# Cross-platform verification

Windows and macOS require separate real-machine checks. A shared codebase or frontend build does not establish support for both platforms.

| Check | Windows | macOS |
| --- | --- | --- |
| Setup and local model readiness | Not run | Not run |
| Folder paths with spaces and Unicode | Not run | Not run |
| Index, search, preview, open, reveal | Not run | Not run |
| Reload during indexing and reconnect | Not run | Not run |
| Changed/deleted files and incremental scan | Not run | Not run |
| Model-off errors and offline runtime | Not run | Not run |

The frontend build was checked on a Windows development environment, but the app has no backend in this checkout and the frontend itself is browser-based. This is not a Windows product smoke test. macOS is unverified. Record actual OS versions, hardware, test date, failures, and the teammate who ran each machine check before making support claims.
