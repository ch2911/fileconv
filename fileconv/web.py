"""Download from web URLs (YouTube, SoundCloud, and any other site yt-dlp
supports) straight into a chosen audio or video format.

Downloads default to the user's Downloads folder since a URL has no "source
folder". Only download content you have the rights to.
"""

from __future__ import annotations

from pathlib import Path

from .ffmpeg_utils import find_ffmpeg

# fileconv target -> yt-dlp audio codec name
AUDIO_TARGETS = {
    "mp3": "mp3",
    "m4a": "m4a",
    "aac": "aac",
    "flac": "flac",
    "wav": "wav",
    "opus": "opus",
    "ogg": "vorbis",
}
VIDEO_TARGETS = {"mp4", "mkv", "webm", "mov"}


def is_url(value: str) -> bool:
    return value.lower().startswith(("http://", "https://"))


def download_url(url: str, target: str, outdir: str | None, overwrite: bool = False) -> Path:
    """Download a URL and produce a file in the requested format.
    Returns the path of the finished file."""
    import yt_dlp

    directory = Path(outdir) if outdir else Path.home() / "Downloads"
    directory.mkdir(parents=True, exist_ok=True)

    opts: dict = {
        "outtmpl": str(directory / "%(title)s.%(ext)s"),
        "ffmpeg_location": find_ffmpeg(),
        "windowsfilenames": True,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    if overwrite:
        opts["overwrites"] = True

    if target in AUDIO_TARGETS:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": AUDIO_TARGETS[target],
                "preferredquality": "192",
            }
        ]
    elif target in VIDEO_TARGETS:
        opts["format"] = "bv*+ba/b"
        if target == "mov":
            # yt-dlp can't merge directly into mov; merge to mp4 then remux.
            opts["merge_output_format"] = "mp4"
            opts["postprocessors"] = [{"key": "FFmpegVideoRemuxer", "preferedformat": "mov"}]
        else:
            opts["merge_output_format"] = target
    else:
        raise ValueError(
            f"URLs can be saved as audio ({', '.join(sorted(AUDIO_TARGETS))}) "
            f"or video ({', '.join(sorted(VIDEO_TARGETS))}), not {target!r}"
        )

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:
            raise RuntimeError(f"nothing downloadable found at {url}")
        downloads = info.get("requested_downloads") or []
        if downloads and downloads[0].get("filepath"):
            return Path(downloads[0]["filepath"])
        # Fallback: derive the final name from the info dict.
        return Path(ydl.prepare_filename(info)).with_suffix(f".{target}")
