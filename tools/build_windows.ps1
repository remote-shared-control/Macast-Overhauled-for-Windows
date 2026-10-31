param([string]$Python = 'py', [string]$MpvDir = '')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    if ($Python -eq 'py') { & $Python -3.12 -m venv .venv }
    else { & $Python -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.12 venv creation failed' }
}
& .venv\Scripts\python.exe -m pip install -r requirements\windows-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
if ($MpvDir) {
    & .venv\Scripts\python.exe tools\build_windows.py --mpv-dir $MpvDir
} else {
    & .venv\Scripts\python.exe tools\fetch_mpv.py
    if ($LASTEXITCODE -ne 0) { throw 'MPV download failed' }
    & .venv\Scripts\python.exe tools\build_windows.py
}
if ($LASTEXITCODE -ne 0) { throw 'Windows build failed' }
