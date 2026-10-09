import os
import stat
import subprocess
import sys
from pathlib import Path
from .security import ApiError, scoped_file
from .extractors import SUPPORTED, file_type

FOLDER_PICKER = False


def pick_folder():
    raise ApiError('FOLDER_PICKER_UNAVAILABLE', 'Native folder selection is unavailable. Enter the absolute folder path instead.', 503)


def windows_reveal(path):
    """Native Shell PIDLs avoid Explorer command-line parsing of path punctuation.

    https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shopenfolderandselectitems
    Windows runtime untested on the macOS development machine.
    """
    import ctypes
    from ctypes import wintypes
    shell = ctypes.WinDLL('shell32', use_last_error=True)
    ole = ctypes.WinDLL('ole32', use_last_error=True)
    ole.CoInitializeEx.argtypes = [ctypes.c_void_p, wintypes.DWORD]
    ole.CoInitializeEx.restype = ctypes.c_long
    ole.CoUninitialize.argtypes = []
    ole.CoUninitialize.restype = None
    ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole.CoTaskMemFree.restype = None
    shell.SHParseDisplayName.argtypes = [wintypes.LPCWSTR, ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p), wintypes.DWORD, ctypes.c_void_p]
    shell.SHParseDisplayName.restype = ctypes.c_long
    shell.SHOpenFolderAndSelectItems.argtypes = [ctypes.c_void_p, wintypes.UINT, ctypes.c_void_p, wintypes.DWORD]
    shell.SHOpenFolderAndSelectItems.restype = ctypes.c_long
    hr = ole.CoInitializeEx(None, 2)
    # RPC_E_CHANGED_MODE means this thread already has a different COM apartment.
    initialized = hr >= 0
    if hr < 0 and hr != -2147417850:
        raise OSError(f'COM initialization failed: {hr}')
    pidl = ctypes.c_void_p()
    try:
        hr = shell.SHParseDisplayName(str(path), None, ctypes.byref(pidl), 0, None)
        if hr < 0:
            raise OSError(f'Shell path resolution failed: {hr}')
        hr = shell.SHOpenFolderAndSelectItems(pidl, 0, None, 0)
        if hr < 0:
            raise OSError(f'Shell selection failed: {hr}')
    finally:
        if pidl.value:
            ole.CoTaskMemFree(pidl)
        if initialized:
            ole.CoUninitialize()


def act(path, reveal=False, *, root=None):
    """Revalidate immediately before native dispatch; callers lock active-root changes."""
    path = Path(path)
    if file_type(path) not in SUPPORTED:
        raise ApiError('UNSUPPORTED_FILE', 'Only supported documents and images can be opened or revealed.')
    if root is None:
        raise ApiError('INVALID_ROOT', 'Desktop actions require the active indexed root.')
    try:
        relative = path.relative_to(Path(root)).as_posix()
    except ValueError as exc:
        raise ApiError('FILE_OUTSIDE_ROOT', 'File is outside the selected root.') from exc
    path = scoped_file(root, relative)
    fd = None
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            raise ApiError('UNSUPPORTED_FILE', 'Desktop actions require a regular document file.')
        if sys.platform == 'darwin':
            import fcntl
            # Honor advisory exclusive locks as well as OS read-permission failures.
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        current = path.stat()
        if (current.st_dev, current.st_ino) != (opened.st_dev, opened.st_ino):
            raise ApiError('FILE_CHANGED', 'File changed during the desktop action. Retry after rescanning.', 409, True)
        if sys.platform == 'darwin':
            args = ['/usr/bin/open', '-R', str(path)] if reveal else ['/usr/bin/open', str(path)]
            subprocess.run(args, check=True, timeout=10, capture_output=True, shell=False)
        elif sys.platform == 'win32':
            # Windows share locks can prevent OS read/open; close the validation
            # handle first so it cannot itself obstruct the default application.
            os.close(fd); fd = None
            if reveal:
                windows_reveal(path)
            else:
                os.startfile(str(path), 'open')
        else:
            raise ApiError('PLATFORM_UNSUPPORTED', 'Desktop actions are supported on Windows and macOS only.', 503)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ApiError('DESKTOP_ACTION_FAILED', 'The file is locked, unreadable, or the operating system could not open it.', 503, True) from exc
    finally:
        if fd is not None:
            os.close(fd)
