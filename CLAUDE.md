# fileconv

Local file format converter (images / video / audio / documents / web URLs)
with a CLI and a Tkinter GUI. GitHub: https://github.com/ch2911/fileconv

## Layout

- `fileconv/cli.py` — argument parsing and dispatch. `convert_one()` routes a
  (source, target) pair to the right converter; both the CLI and GUI call it.
- `fileconv/images.py` — Pillow + pillow-heif. Importing it registers the HEIF
  codec globally.
- `fileconv/video.py` — video/audio via ffmpeg subprocess. "hevc" is treated
  as a pseudo-target (H.265 re-encode keeping the container), because HEVC is
  a codec, not a container. Plain container changes remux with `-c copy`.
- `fileconv/ffmpeg_utils.py` — finds ffmpeg: system PATH first, else the
  binary bundled in the imageio-ffmpeg wheel. Note: no ffprobe is available.
- `fileconv/docs.py` — DOCX→PDF tries three engines in fidelity order:
  Word (docx2pdf) → LibreOffice headless → pandoc+typst (pure pip, always
  available). PDF→DOCX uses pdf2docx.
- `fileconv/web.py` — yt-dlp wrapper: URL → audio/video file. URL downloads
  default to ~/Downloads (a URL has no source folder).
- `fileconv/gui.py` — thin Tkinter wrapper around `convert_one`/`download_url`.
- `app.py` — PyInstaller entry point (GUI when no args, silent CLI with args;
  stubs stdout/stderr because windowed apps have none).
- `convert.py` — dev entry point: `python convert.py <files-or-urls> -t <fmt>`.

## Dev commands

```bash
python -m venv .venv                      # python3 on mac; needs tkinter
.venv/bin/pip install -r requirements.txt pytest
.venv/bin/python -m pytest                # all fixtures are generated, no media in repo
FILECONV_NETWORK_TESTS=1 .venv/bin/python -m pytest tests/test_web.py  # live yt-dlp download
.venv/bin/python convert.py --gui         # run the GUI from source
./build_app.sh                            # mac: build dist/"File Converter.app"
./build_app.ps1                           # windows: build dist/FileConverter.exe
git tag v0.2.0 && git push origin v0.2.0  # release: CI tests 3 OSes, builds both apps, publishes
```

## Gotchas

- Homebrew Python lacks Tk: `brew install python-tk` before running the GUI.
- On Windows the built exe is pinned to the user's taskbar via a Start Menu
  shortcut that points at `dist\FileConverter\FileConverter.exe` — rebuild in
  place, don't move/rename that folder.
- If YouTube/SoundCloud downloads start failing, bump yt-dlp and rebuild;
  extractors rot quickly.
- The Windows dev machine has no Word/LibreOffice, so DOCX→PDF exercises the
  pandoc+typst tier there; on a machine with Word, docx2pdf runs instead
  (slower, opens Word, higher fidelity).
- Line endings are pinned in .gitattributes (`.sh` LF, `.ps1` CRLF).
- CI: `tests.yml` runs the suite on Linux/Windows/macOS; `release.yml` (on
  `v*` tags) reuses it, then builds both apps and publishes a GitHub release.
  The asset names `FileConverter-windows.zip` / `FileConverter-macos.zip` are
  load-bearing — README links use `/releases/latest/download/<name>`.
- The released macOS app is Apple Silicon-only (`macos-latest` runners are
  arm64); Intel Macs build from source.
- LibreOffice headless can exit 0 *without* writing the PDF (broken profile
  prints "source file could not be loaded", still returns 0). `docx_to_pdf`
  checks the output file exists and falls back to pandoc+typst.
