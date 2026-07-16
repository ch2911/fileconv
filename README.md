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

Notes:

- **HEVC** is a codec, not a container. `-t hevc` re-encodes the video stream
  with H.265 (keeping the MP4/MOV container) and tags it `hvc1` so it plays on
  Apple devices. Plain container changes (e.g. `mov -> mp4`) copy the streams
  without re-encoding, which is fast and lossless.
- **DOCX → PDF** uses Microsoft Word if installed, otherwise LibreOffice.
  PDF → DOCX needs neither.
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

## Tests

```powershell
pip install pytest
pytest
```

The test suite generates its own sample images, videos, and PDFs — no fixtures
needed. The DOCX → PDF test is skipped automatically if neither Word nor
LibreOffice is installed.
