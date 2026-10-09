import os
from pathlib import Path
from urllib.parse import urlparse

class ApiError(Exception):
    def __init__(self, code, message, status=400, retryable=False):
        self.code, self.message, self.status, self.retryable = code, message, status, retryable
        super().__init__(message)

    def body(self):
        return {'error': {'code': self.code, 'message': self.message, 'retryable': self.retryable}}


def has_symlink(path):
    return any(p.is_symlink() for p in (path, *path.parents))

def validate_root(value, data_dir):
    path = Path(value).expanduser()
    if not path.is_absolute() or '..' in path.parts:
        raise ApiError('INVALID_ROOT', 'Choose an absolute folder path without parent traversal.')
    if has_symlink(path):
        raise ApiError('INVALID_ROOT', 'Symlink folders are not supported.')
    try:
        path = path.resolve(strict=True)
    except (OSError, ValueError) as exc:
        raise ApiError('INVALID_ROOT', 'Folder does not exist or is inaccessible.') from exc
    if not path.is_dir() or not os.access(path, os.R_OK | os.X_OK):
        raise ApiError('INVALID_ROOT', 'Choose a readable directory.')
    if path == data_dir or path.is_relative_to(data_dir):
        raise ApiError('INVALID_ROOT', 'Sift cannot index its own data directory.')
    try:
        next(path.iterdir(), None)
    except OSError as exc:
        raise ApiError('INVALID_ROOT', 'Folder cannot be read.') from exc
    return path


def scoped_file(root, relative):
    path = Path(root) / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or has_symlink(path):
        raise ApiError('FILE_OUTSIDE_ROOT', 'File is outside the selected root or is a symlink.')
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ApiError('FILE_NOT_FOUND', 'File no longer exists or is inaccessible.', 404) from exc
    if not resolved.is_relative_to(Path(root)) or not resolved.is_file():
        raise ApiError('FILE_OUTSIDE_ROOT', 'File is not a regular file inside the selected root.')
    return resolved


def check_request(request, config):
    host = request.headers.get('host', '')
    try:
        parsed = urlparse('http://' + host)
        valid_host = parsed.hostname in ('127.0.0.1', 'localhost') and parsed.port in (config.port, 5173)
    except ValueError:
        valid_host = False
    if not valid_host:
        raise ApiError('UNTRUSTED_HOST', 'Request host is not an allowed loopback address.')
    allowed = {f'http://{name}:{port}' for name in ('127.0.0.1', 'localhost') for port in (config.port, 5173)}
    origin = request.headers.get('origin')
    if origin is not None and origin not in allowed:
        raise ApiError('UNTRUSTED_ORIGIN', 'Requests from this origin are not allowed.')
    if request.headers.get('sec-fetch-site') == 'cross-site':
        raise ApiError('UNTRUSTED_ORIGIN', 'Cross-site requests are not allowed.')
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        if request.headers.get('content-type', '').split(';')[0].lower() != 'application/json':
            raise ApiError('INVALID_CONTENT_TYPE', 'Mutations require application/json.')
