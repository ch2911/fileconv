import os
from pathlib import Path

import pytest

from fileconv.web import download_url, is_url


def test_is_url():
    assert is_url("https://www.youtube.com/watch?v=abc")
    assert is_url("HTTP://soundcloud.com/artist/track")
    assert not is_url("photo.heic")
    assert not is_url(r"C:\music\https-notes.txt")


def test_unknown_target_rejected(tmp_path: Path):
    with pytest.raises(ValueError, match="URLs can be saved as"):
        download_url("https://example.com/video", "docx", str(tmp_path))


@pytest.mark.skipif(
    not os.environ.get("FILECONV_NETWORK_TESTS"),
    reason="network test; set FILECONV_NETWORK_TESTS=1 to run",
)
def test_youtube_to_mp3(tmp_path: Path):
    # "Me at the zoo" - the first video on YouTube, 19s, not going anywhere.
    dest = download_url(
        "https://www.youtube.com/watch?v=jNQXAC9IVRw", "mp3", str(tmp_path)
    )
    assert dest.exists() and dest.suffix == ".mp3" and dest.stat().st_size > 0
