import os

# Local-only runtime: opt out before any native ONNX initialization. The Python
# API alone can be too late for the minimal initialization event on macOS.
# https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md
os.environ['ORT_DISABLE_TELEMETRY'] = '1'

from pathlib import Path
import threading
import importlib.util
import numpy as np
from PIL import Image, ImageOps
from pypdf import PdfReader

SUPPORTED = {'txt', 'md', 'pdf', 'png', 'jpg'}

def file_type(path):
    ext = path.suffix.lower().lstrip('.')
    return 'jpg' if ext == 'jpeg' else ext

class Unsupported(Exception):
    pass

class Extractor:
    def __init__(self):
        self.ocr_files = 0
        self.lock = threading.Lock()
        self.engine = None

    def ocr_ready(self):
        try:
            import rapidocr
            base = Path(rapidocr.__file__).parent / 'models'
            return importlib.util.find_spec('onnxruntime') is not None and all((base / n).is_file() for n in (
                'PP-OCRv6_det_small.onnx', 'ch_ppocr_mobile_v2.0_cls_mobile.onnx', 'PP-OCRv6_rec_small.onnx'))
        except ImportError:
            return False

    def ocr(self, path):
        if not self.ocr_ready():
            raise Unsupported('Local OCR dependencies/models unavailable')
        with self.lock:
            if self.engine is None:
                import onnxruntime
                onnxruntime.disable_telemetry_events()
                import rapidocr
                base = Path(rapidocr.__file__).parent / 'models'
                # Explicit bundled paths prevent runtime model downloads.
                self.engine = rapidocr.RapidOCR(params={
                    'Det.model_path': str(base / 'PP-OCRv6_det_small.onnx'),
                    'Cls.model_path': str(base / 'ch_ppocr_mobile_v2.0_cls_mobile.onnx'),
                    'Rec.model_path': str(base / 'PP-OCRv6_rec_small.onnx'),
                    'Global.log_level': 'error',
                    'EngineConfig.onnxruntime.intra_op_num_threads': 2,
                    'EngineConfig.onnxruntime.inter_op_num_threads': 1})
            with Image.open(path) as image:
                image = ImageOps.exif_transpose(image).convert('RGB')
                image.thumbnail((1600, 1600))
                result = self.engine(np.asarray(image))
            self.ocr_files += 1
            return '\n'.join(result.txts or [])

    def extract(self, path, max_chars=200000):
        kind = file_type(path)
        if kind in ('txt', 'md'):
            raw = path.read_bytes()
            text = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
            pages = [(None, text)]
        elif kind == 'pdf':
            reader = PdfReader(path)
            if reader.is_encrypted:
                raise Unsupported('Encrypted PDF is unsupported')
            pages = []
            remaining = max_chars
            for i, page in enumerate(reader.pages):
                text = (page.extract_text() or '')[:remaining]
                pages.append((i + 1, text))
                remaining -= len(text)
                if remaining <= 0:
                    break
        elif kind in ('png', 'jpg'):
            pages = [(None, self.ocr(path))]
        else:
            raise Unsupported('Unsupported file type')
        bounded = []
        remaining = max_chars
        for page, text in pages:
            bounded.append((page, text[:remaining]))
            remaining -= len(bounded[-1][1])
            if remaining <= 0:
                break
        if not any(t.strip() for _, t in bounded):
            raise Unsupported('No extractable text; scanned PDFs and textless photos are unsupported')
        return bounded

def chunks(pages, size=1000, overlap=150):
    for page, text in pages:
        for offset in range(0, len(text), size - overlap):
            piece = text[offset:offset+size]
            if piece.strip():
                yield page, piece
            if offset + size >= len(text):
                break
