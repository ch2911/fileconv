"""Video and audio conversions driven by ffmpeg.

Note on HEVC: HEVC (H.265) is a codec, not a container. Converting "to hevc"
re-encodes the video stream with libx265, keeping an MP4/MOV container. The
`hvc1` tag is applied so the result plays on Apple devices.
"""

from __future__ import annotations

from pathlib import Path

from .ffmpeg_utils import run_ffmpeg

VIDEO_CONTAINERS = {"mp4", "mov", "mkv", "webm", "avi"}
# "hevc" is accepted as a target meaning: re-encode to H.265 (see module docstring).
VIDEO_TARGETS = VIDEO_CONTAINERS | {"hevc", "gif"}
AUDIO_FORMATS = {"mp3", "wav", "flac", "aac", "m4a", "ogg", "opus"}

_AUDIO_CODECS = {
    "mp3": ["-c:a", "libmp3lame", "-q:a", "2"],
    "wav": ["-c:a", "pcm_s16le"],
    "flac": ["-c:a", "flac"],
    "aac": ["-c:a", "aac", "-b:a", "192k"],
    "m4a": ["-c:a", "aac", "-b:a", "192k"],
    "ogg": ["-c:a", "libvorbis", "-q:a", "5"],
    "opus": ["-c:a", "libopus", "-b:a", "128k"],
}


def is_media_ext(ext: str) -> bool:
    ext = ext.lower().lstrip(".")
    return ext in VIDEO_CONTAINERS or ext in AUDIO_FORMATS


def resolve_video_target(src: Path, target: str) -> str:
    """Map a requested target to the actual output extension."""
    if target == "hevc":
        # Keep the source container when it can hold HEVC, otherwise use mp4.
        src_ext = src.suffix.lstrip(".").lower()
        return src_ext if src_ext in {"mp4", "mov", "mkv"} else "mp4"
    return target


def convert_video(src: Path, dest: Path, codec: str | None = None, crf: int | None = None) -> Path:
    """Convert/remux a video file.

    codec: "copy" (remux only), "h264", or "hevc". Defaults to "copy" for
    mp4/mov/mkv container changes and a sensible re-encode elsewhere.
    """
    dest_ext = dest.suffix.lstrip(".").lower()

    if dest_ext == "gif":
        return _video_to_gif(src, dest)

    if codec is None:
        codec = "copy" if dest_ext in {"mp4", "mov", "mkv"} else "h264"
    if dest_ext == "webm":
        # webm only allows VP8/VP9/AV1 + Vorbis/Opus; always re-encode.
        args = [
            "-i", str(src),
            "-c:v", "libvpx-vp9", "-crf", str(crf if crf is not None else 32), "-b:v", "0",
            "-c:a", "libopus", "-b:a", "128k",
            str(dest),
        ]
        run_ffmpeg(args)
        return dest

    if codec == "copy":
        args = ["-i", str(src), "-c", "copy"]
        if dest_ext in {"mp4", "mov"}:
            args += ["-movflags", "+faststart"]
        args.append(str(dest))
        run_ffmpeg(args)
        return dest

    if codec == "h264":
        vcodec = ["-c:v", "libx264", "-crf", str(crf if crf is not None else 23), "-preset", "medium"]
    elif codec == "hevc":
        vcodec = [
            "-c:v", "libx265", "-crf", str(crf if crf is not None else 28),
            "-preset", "medium", "-tag:v", "hvc1",
        ]
    else:
        raise ValueError(f"Unknown codec: {codec}")

    args = [
        "-i", str(src),
        *vcodec,
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
    ]
    if dest_ext in {"mp4", "mov"}:
        args += ["-movflags", "+faststart"]
    args.append(str(dest))
    run_ffmpeg(args)
    return dest


def convert_audio(src: Path, dest: Path) -> Path:
    """Convert to an audio format. Works for audio sources and for extracting
    the audio track from a video file."""
    dest_ext = dest.suffix.lstrip(".").lower()
    codec_args = _AUDIO_CODECS[dest_ext]
    run_ffmpeg(["-i", str(src), "-vn", *codec_args, str(dest)])
    return dest


def _video_to_gif(src: Path, dest: Path, fps: int = 12, width: int = 480) -> Path:
    """Video -> animated GIF using a generated palette for decent colors."""
    filters = (
        f"fps={fps},scale={width}:-1:flags=lanczos,"
        "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    )
    run_ffmpeg(["-i", str(src), "-vf", filters, "-loop", "0", str(dest)])
    return dest
