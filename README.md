# fileconv

A local file format converter with a command line and a simple GUI. No cloud
services — everything runs on your machine.

## Supported conversions

| Category  | Formats                                                            |
| --------- | ------------------------------------------------------------------ |
| Images    | HEIC/HEIF ↔ JPEG ↔ PNG ↔ WebP ↔ BMP ↔ TIFF ↔ GIF ↔ ICO             |
| Video     | MP4 ↔ MOV ↔ MKV ↔ WebM ↔ AVI, re-encode to HEVC (H.265), video → GIF |
| Audio     | MP3 ↔ WAV ↔ FLAC ↔ AAC ↔ M4A ↔ OGG ↔ Opus (also extracts audio from video) |
| Documents | DOCX ↔ PDF                                                          |
| Web URLs  | YouTube/SoundCloud/etc. link → MP3 (or any audio format above) or MP4/MKV/WebM/MOV video |

Notes:

- **HEVC** is a codec, not a container. `-t hevc` re-encodes the video stream
  with H.265 (keeping the MP4/MOV container) and tags it `hvc1` so it plays on
  Apple devices. Plain container changes (e.g. `mov -> mp4`) copy the streams
  without re-encoding, which is fast and lossless.
- **DOCX → PDF** works out of the box via a bundled pandoc + typst pipeline
  (pip packages, nothing to install). If Microsoft Word or LibreOffice is
  installed, that is used instead for maximum layout fidelity.
  PDF → DOCX needs no external programs either.
- ffmpeg is bundled via the `imageio-ffmpeg` package — no system install needed.
  If you have ffmpeg on your PATH, that copy is used instead.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```powershell
# Single file
python convert.py photo.heic -t jpg

# Batch: globs and folders work
python convert.py *.heic -t png -o converted/
python convert.py C:\Photos -t jpg

# Video
python convert.py movie.mp4 -t hevc            # H.265 re-encode, smaller file
python convert.py clip.mov -t mp4              # fast remux, no re-encode
python convert.py clip.mov -t mp4 --codec h264 --crf 20
python convert.py demo.mp4 -t gif

# Audio
python convert.py song.wav -t mp3
python convert.py movie.mp4 -t mp3             # extract soundtrack

# Documents
python convert.py report.docx -t pdf
python convert.py scan.pdf -t docx

# Web URLs (saved to ~/Downloads unless -o is given).
# Works for YouTube, SoundCloud, and most sites yt-dlp supports.
# Only download content you have the rights to.
python convert.py "https://www.youtube.com/watch?v=..." -t mp3
python convert.py "https://soundcloud.com/artist/track" -t mp3
python convert.py "https://www.youtube.com/watch?v=..." -t mp4

# GUI (or just run with no arguments)
python convert.py --gui
```

Options:

| Flag          | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `-t, --to`    | Target format                                              |
| `-o, --outdir`| Output folder (default: next to the source file)           |
| `--quality`   | Image quality 1–100 (default 90)                           |
| `--codec`     | Video codec: `copy`, `h264`, `hevc`                        |
| `--crf`       | Video quality; lower = better (h264 default 23, hevc 28)   |
| `--overwrite` | Replace existing output files                              |

You can also install it as a command: `pip install -e .` then use `fileconv`
instead of `python convert.py`.

## Windows app

Build a standalone `FileConverter.exe` (no Python needed to run it):

```powershell
pip install pyinstaller
.\build_app.ps1
```

The app lands in `dist\FileConverter\FileConverter.exe`. Double-clicking opens
the GUI; to get it on the taskbar, launch it and right-click its taskbar icon →
**Pin to taskbar** (or create a Start Menu shortcut and pin from there).
The exe also works from scripts: `FileConverter.exe photo.heic -t jpg` converts
silently with no window.

## macOS app

Apps must be built on the platform they run on, so run this on the Mac itself:

```bash
git clone https://github.com/ch2911/fileconv
cd fileconv
./build_app.sh
```

The script creates its own virtual environment, installs everything, and
produces `dist/File Converter.app`. Drag that into `/Applications`, launch it,
then right-click the Dock icon → **Options → Keep in Dock**. If you use
Homebrew Python, install Tk support first: `brew install python-tk`.

## Tests

```powershell
pip install pytest
pytest
```

The test suite generates its own sample images, videos, and PDFs — no fixtures
needed. The DOCX → PDF test is skipped automatically if neither Word nor
LibreOffice is installed.
