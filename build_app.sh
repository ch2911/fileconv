#!/usr/bin/env bash
# Build "File Converter.app" into dist/ on macOS. Sets up everything itself:
#   git clone https://github.com/ch2911/fileconv && cd fileconv && ./build_app.sh
# Requires python3 with tkinter (the python.org installer includes it; for
# Homebrew python run: brew install python-tk).
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
.venv/bin/python -m pip install --quiet -r requirements.txt pyinstaller
.venv/bin/python scripts/make_icon.py

.venv/bin/python -m PyInstaller \
    --noconfirm \
    --windowed \
    --name "File Converter" \
    --icon assets/icon.icns \
    --collect-all pypandoc \
    --collect-all imageio_ffmpeg \
    --collect-data docx \
    --collect-data pdf2docx \
    app.py

echo
echo 'Built: dist/File Converter.app'
echo 'Drag it into /Applications, launch it, then right-click its Dock icon'
echo 'and choose Options > Keep in Dock.'
