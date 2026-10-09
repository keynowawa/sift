import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

MODEL = 'nomic-embed-text:v1.5'

def default_data_dir():
    if sys.platform == 'win32':
        return Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local')) / 'Sift'
    if sys.platform == 'darwin':
        return Path.home() / 'Library/Application Support/Sift'
    return Path.home() / '.local/share/Sift'

@dataclass
class Config:
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get('SIFT_DATA_DIR', default_data_dir())).expanduser().resolve())
    model: str = MODEL
    port: int = field(default_factory=lambda: int(os.environ.get('SIFT_PORT', '8765')))
    semantic_threshold: float = 0.53
    max_file_bytes: int = 25 * 1024 * 1024
    max_text_chars: int = 200000
    chunk_chars: int = 1000
    chunk_overlap: int = 150
    frontend_dist: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2] / 'frontend/dist')

    @property
    def platform(self):
        return {'darwin': 'macos', 'win32': 'windows'}.get(sys.platform, 'other')

    @property
    def signature(self):
        return f'{self.model}:extraction-v1:chunks-{self.chunk_chars}-{self.chunk_overlap}:ctx2048'
