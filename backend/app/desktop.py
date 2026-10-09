import os
import subprocess
import sys
from .security import ApiError
from .extractors import SUPPORTED, file_type

# No dependable Tk installation on the tested Python; never pretend a picker exists.
FOLDER_PICKER = False

def pick_folder():
    raise ApiError('FOLDER_PICKER_UNAVAILABLE', 'Native folder selection is unavailable. Enter the absolute folder path instead.', 503)

def act(path, reveal=False):
    if file_type(path) not in SUPPORTED:
        raise ApiError('UNSUPPORTED_FILE', 'Only supported documents and images can be opened or revealed.')
    try:
        if sys.platform == 'darwin':
            args = ['/usr/bin/open', '-R', str(path)] if reveal else ['/usr/bin/open', str(path)]
            subprocess.run(args, check=True, timeout=10, capture_output=True)
        elif sys.platform == 'win32':
            if reveal:
                subprocess.Popen(['explorer.exe', '/select,', str(path)])
            else:
                os.startfile(str(path))
        else:
            raise ApiError('PLATFORM_UNSUPPORTED', 'Desktop actions are supported on Windows and macOS only.', 503)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ApiError('DESKTOP_ACTION_FAILED', 'The operating system could not open this file or folder.', 503, True) from exc
