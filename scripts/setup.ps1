$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$requirements = Join-Path $repoRoot 'backend\requirements.txt'
$frontend = Join-Path $repoRoot 'frontend'

function Stop-WithHelp([string]$message) {
  Write-Error "$message`nSee README.md and docs/SIFT_BUILDER_A_BACKEND.md for the missing project dependency or agreed model details."
  exit 1
}

if (-not (Test-Path -LiteralPath $requirements)) { Stop-WithHelp 'Backend requirements are not available yet. Setup cannot complete until Builder A provides backend/requirements.txt.' }
if (-not (Test-Path -LiteralPath (Join-Path $frontend 'package-lock.json'))) { Stop-WithHelp 'Frontend lockfile is missing. Run npm install in frontend/ first.' }

$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
  & $python.Source -3.11 --version *> $null
  if ($LASTEXITCODE -eq 0) { $pythonExe = 'py'; $pythonPrefix = @('-3.11') }
}
if (-not $pythonExe) {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    $version = & $python.Source --version 2>&1
    if ($version -match '^Python 3\.(1[1-9]|[2-9][0-9])\.') { $pythonExe = $python.Source; $pythonPrefix = @() }
  }
}
if (-not $pythonExe) { Stop-WithHelp 'Python 3.11 or newer is required. Install it for your user, then run setup.ps1 again.' }
foreach ($name in @('node', 'npm', 'ollama')) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { Stop-WithHelp "$name is not installed or is not on PATH." }
}
$nodeVersionText = (node --version).TrimStart('v')
$nodeVersion = [version]$nodeVersionText
if (-not (($nodeVersion.Major -eq 20 -and $nodeVersion.Minor -ge 19) -or ($nodeVersion.Major -ge 22 -and ($nodeVersion.Major -gt 22 -or $nodeVersion.Minor -ge 12)))) {
  Stop-WithHelp "Node.js $nodeVersionText is too old for the frontend. Install Node.js 20.19+ or 22.12+."
}

$venv = Join-Path $repoRoot '.venv'
if (-not (Test-Path -LiteralPath $venv)) { & $pythonExe @pythonPrefix -m venv $venv; if ($LASTEXITCODE -ne 0) { Stop-WithHelp 'Could not create the project virtual environment.' } }
$venvPython = Join-Path $venv 'Scripts\python.exe'
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { Stop-WithHelp 'Could not prepare pip in .venv.' }
& $venvPython -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) { Stop-WithHelp 'Backend dependency installation failed.' }
Push-Location $frontend
try { & npm ci; if ($LASTEXITCODE -ne 0) { Stop-WithHelp 'Frontend dependency installation failed.' }; & npm run build; if ($LASTEXITCODE -ne 0) { Stop-WithHelp 'Frontend build failed.' } }
finally { Pop-Location }

Write-Host ''
Write-Host 'Setup complete. No model was downloaded.'
Write-Host 'The embedding model is still being benchmarked with Builder A. Follow the exact model and prefix instructions they publish before indexing.'
& ollama list
if ($LASTEXITCODE -ne 0) { Write-Warning 'Ollama is installed but not responding. Start it with: ollama serve' }
Write-Host 'Ollama is installed. Start it with: ollama serve'
Write-Host 'Once Builder A confirms the model, install it explicitly with: ollama pull <confirmed-model-tag>'
