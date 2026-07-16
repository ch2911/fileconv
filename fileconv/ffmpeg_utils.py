"""Locate and run ffmpeg. Uses the system binary when available, otherwise
falls back to the binary bundled with the imageio-ffmpeg package."""

from __future__ import annotations

import shutil
import subprocess
from functools import lru_cache


@lru_cache(maxsize=1)
def find_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "ffmpeg not found. Install ffmpeg or `pip install imageio-ffmpeg`."
        ) from exc


def run_ffmpeg(args: list[str]) -> None:
    """Run ffmpeg with the given arguments, raising with stderr on failure."""
    cmd = [find_ffmpeg(), "-hide_banner", "-y", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-8:])
        raise RuntimeError(f"ffmpeg failed (exit {result.returncode}):\n{tail}")
