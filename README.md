# fileconv

A local file format converter with a command line and a simple GUI. No cloud
services — everything runs on your machine. Works as a Python tool on
Windows/macOS/Linux, as a packaged desktop app on Windows and macOS, and the
URL-download feature has an on-device iPhone recipe too.

## What it converts

| Category  | Formats                                                            |
| --------- | ------------------------------------------------------------------ |
| Images    | HEIC/HEIF ↔ JPEG ↔ PNG ↔ WebP ↔ BMP ↔ TIFF ↔ GIF ↔ ICO             |
| Video     | MP4 ↔ MOV ↔ MKV ↔ WebM ↔ AVI, re-encode to HEVC (H.265), video → GIF |
| Audio     | MP3 ↔ WAV ↔ FLAC ↔ AAC ↔ M4A ↔ OGG ↔ Opus (also extracts audio from video) |
| Documents | DOCX ↔ PDF                                                          |
| Web URLs  | YouTube/SoundCloud/etc. link → MP3 (or any audio format above) or MP4/MKV/WebM/MOV video |

Good to know:

- **HEVC** is a codec, not a container. `-t hevc` re-encodes the video stream
  with H.265 (keeping the MP4/MOV container) and tags it `hvc1` so it plays on
  Apple devices. Plain container changes (e.g. `mov -> mp4`) copy the streams
  without re-encoding, which is fast and lossless.
- **DOCX → PDF** works out of the box via a bundled pandoc + typst pipeline
  (pip packages, nothing to install). If Microsoft Word or LibreOffice is
  installed, that is used instead for maximum layout fidelity.
  PDF → DOCX needs no external programs either.
- **ffmpeg is bundled** via the `imageio-ffmpeg` package — no system install
  needed. If you have ffmpeg on your PATH, that copy is used instead.
- **URL downloads** save to `~/Downloads` by default (override with `-o`).
  Only download content you have the rights to. To play the results in Spotify,
  see [Playing the results in Spotify](#playing-the-results-in-spotify).

## Quick start (Windows / macOS / Linux)

Requires Python 3.10+ ([python.org](https://www.python.org/downloads/) builds
include everything needed).

```bash
git clone https://github.com/ch2911/fileconv
cd fileconv
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Then convert away:

```bash
# Images
python convert.py photo.heic -t jpg
python convert.py *.heic -t png -o converted/     # globs work
python convert.py C:\Photos -t jpg                # so do folders (Windows)
python convert.py ~/Pictures -t jpg               # (macOS/Linux)

# Video
python convert.py movie.mp4 -t hevc               # H.265 re-encode, smaller file
python convert.py clip.mov -t mp4                 # fast remux, no re-encode
python convert.py clip.mov -t mp4 --codec h264 --crf 20
python convert.py demo.mp4 -t gif

# Audio
python convert.py song.wav -t mp3
python convert.py movie.mp4 -t mp3                # extract the soundtrack

# Documents
python convert.py report.docx -t pdf
python convert.py scan.pdf -t docx

# Web URLs (YouTube, SoundCloud, and most sites yt-dlp supports)
python convert.py "https://www.youtube.com/watch?v=..." -t mp3
python convert.py "https://soundcloud.com/artist/track" -t mp3
python convert.py "https://www.youtube.com/watch?v=..." -t mp4

# GUI (or just run with no arguments)
python convert.py --gui
```

| Flag          | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `-t, --to`    | Target format                                              |
| `-o, --outdir`| Output folder (default: next to the source file)           |
| `--quality`   | Image quality 1–100 (default 90)                           |
| `--codec`     | Video codec: `copy`, `h264`, `hevc`                        |
| `--crf`       | Video quality; lower = better (h264 default 23, hevc 28)   |
| `--overwrite` | Replace existing output files                              |

Prefer a real command? `pip install -e .` installs `fileconv`, so you can run
`fileconv photo.heic -t jpg` from anywhere the venv is active.

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
then right-click the Dock icon → **Options → Keep in Dock**.

Notes:

- If you use Homebrew Python, install Tk support first: `brew install python-tk`
  (the python.org installer already includes it).
- The app is ad-hoc signed, which is fine for the machine it was built on.
  Don't copy the built app to another Mac — build it there instead.

## iPhone / iPad

iOS can't run fileconv itself (no Python desktop apps, and Apple doesn't allow
downloader apps in the App Store). But the feature you'd want on the go —
saving a SoundCloud/YouTube link as an MP3 — works fully on-device using the
same engine fileconv uses (yt-dlp + ffmpeg), wired into the Share menu:

**One-time setup (~10 minutes):**

1. Install **a-Shell** (free, App Store) — a terminal app with ffmpeg built in.
2. In a-Shell, run: `pip install yt-dlp`
3. In the **Shortcuts** app, create a shortcut named "SoundCloud → MP3" with
   three actions, in this order:
   1. **Get URLs from Input** — sharing from the SoundCloud app sends
      "Track title by artist" text with the link buried inside; this extracts
      the actual link.
   2. **Get Item from List** — set to **First Item**.
   3. **a-Shell: Execute Command** — paste:

      ```
      yt-dlp -x --audio-format mp3 --audio-quality 0 --embed-metadata --embed-thumbnail --no-playlist -P ~/Documents/Music -o "%(title)s.%(ext)s" "URL"
      ```

      then replace the word `URL` with the magic variable **Item from List**,
      keeping the quotes around it (links contain `&`, which breaks the
      command unquoted).
4. In the shortcut's settings (ⓘ): turn on **Show in Share Sheet**, set
   **Receive** to URLs and Text, and set **If there's no input** to
   **Get Clipboard**. Optionally: long-press the shortcut → **Share** →
   **Add to Home Screen** for a one-tap icon.

**Using it:** tap **Share** on any track → **SoundCloud → MP3** (or copy a link
and tap the Home Screen icon). MP3s arrive with cover art and metadata in the
Files app under **On My iPhone → a-Shell → Music**. For video instead of audio,
swap `-x --audio-format mp3 --audio-quality 0` for
`-f "bv*+ba/b" --merge-output-format mp4`.

If downloads stop working after a while, sites changed something — update the
downloader in a-Shell: `pip install -U yt-dlp` (the desktop version needs the
same occasional bump).

### Playing the results in Spotify

Useful if the tracks you want aren't on Spotify at all — live versions, remixes,
DJ edits, or artists who only release on SoundCloud. Spotify reads local files,
so converted MP3s sit in your library alongside everything else.

**On iPhone/iPad**, no computer needed: in the Files app, move the MP3s into
**On My iPhone → Spotify** (create the folder if it isn't there). They appear
under **Your Library → Local Files** in the Spotify app.

**On desktop**, enable **Settings → Local Files → Show Local Files**, then
**Add a source** and pick your output folder. To get those tracks onto a phone
this way you need Premium, both devices on the same Wi-Fi, and the playlist
downloaded for offline use — the Files app route above avoids all three.

Spotify only accepts MP3, M4P, and MP4 for local files, so convert FLAC, WAV,
and OGG first (`python convert.py track.flac -t mp3`). Keep filenames simple;
special characters are a common reason a track doesn't show up.

## Tests

```bash
pip install pytest
pytest
```

The test suite generates its own sample images, videos, and PDFs — no fixtures
in the repo. The DOCX → PDF test is skipped automatically if no conversion
engine is available. One test downloads a real (19-second) YouTube video and is
skipped unless you opt in: `FILECONV_NETWORK_TESTS=1 pytest tests/test_web.py`.
