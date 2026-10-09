$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$backend = Join-Path $repoRoot 'backend'
$frontend = Join-Path $repoRoot 'frontend'
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
foreach ($path in @($python, (Join-Path $backend 'app\main.py'), (Join-Path $frontend 'node_modules'))) {
  if (-not (Test-Path -LiteralPath $path)) { Write-Error "Sift is not set up yet. Run scripts\setup.ps1 first."; exit 1 }
}
$port = if ($env:SIFT_PORT) { $env:SIFT_PORT } else { '8765' }
$url = 'http://127.0.0.1:5173'
$occupied = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq 5173 -or $_.LocalPort -eq [int]$port })
if ($occupied.Count -gt 0) { Write-Error "A required Sift port (5173 or $port) is already in use. Stop the owning app or choose a different SIFT_PORT; Sift did not stop it."; exit 1 }
$logs = Join-Path $env:LOCALAPPDATA 'Sift\logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$node = (Get-Command node -ErrorAction Stop).Source
$vite = Join-Path $frontend 'node_modules\vite\bin\vite.js'
$frontendProc = Start-Process -FilePath $node -ArgumentList @(('"{0}"' -f $vite), '--host', '127.0.0.1', '--port', '5173', '--strictPort') -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logs 'frontend.log') -RedirectStandardError (Join-Path $logs 'frontend-error.log')
Start-Process $url
Write-Host "Sift UI: $url (Vite development server)"
Write-Host 'Backend startup and model activity will appear here. Press Ctrl+C to stop the backend.'
try { & $python -m uvicorn app.main:app --app-dir $backend --host 127.0.0.1 --port $port }
finally { if (-not $frontendProc.HasExited) { Stop-Process -Id $frontendProc.Id -ErrorAction SilentlyContinue } }
