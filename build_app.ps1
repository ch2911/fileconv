# Build FileConverter.exe (windowed app) into dist\FileConverter\.
# Run from the project root with the venv's Python available at .venv.
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

& $py (Join-Path $PSScriptRoot "scripts\make_icon.py")

& $py -m PyInstaller `
    --noconfirm `
    --windowed `
    --name FileConverter `
    --icon (Join-Path $PSScriptRoot "assets\icon.ico") `
    --collect-all pypandoc `
    --collect-all imageio_ffmpeg `
    --collect-data docx `
    --collect-data pdf2docx `
    (Join-Path $PSScriptRoot "app.py")

Write-Host "`nBuilt: $(Join-Path $PSScriptRoot 'dist\FileConverter\FileConverter.exe')"
