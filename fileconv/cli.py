"""Command-line interface for fileconv.

Examples:
    fileconv photo.heic -t jpg
    fileconv *.heic -t png -o converted/
    fileconv movie.mp4 -t hevc
    fileconv clip.mov -t mp4 --codec h264 --crf 20
    fileconv report.docx -t pdf
    fileconv song.wav -t mp3
    fileconv --gui
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

from . import __version__
from .docs import DOC_FORMATS, docx_to_pdf, pdf_to_docx
from .images import IMAGE_FORMATS, convert_image
from .video import (
    AUDIO_FORMATS,
    VIDEO_CONTAINERS,
    VIDEO_TARGETS,
    convert_audio,
    convert_video,
    resolve_video_target,
)

ALL_TARGETS = sorted(set(IMAGE_FORMATS) | VIDEO_TARGETS | AUDIO_FORMATS | DOC_FORMATS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fileconv",
        description="Convert images (HEIC/JPEG/PNG/...), video (MP4/HEVC/MOV/...), "
        "audio (MP3/WAV/...) and documents (DOCX/PDF).",
        epilog="Supported targets: " + ", ".join(ALL_TARGETS),
    )
    parser.add_argument("inputs", nargs="*", help="Files, globs, or folders to convert")
    parser.add_argument("-t", "--to", metavar="FORMAT", help="Target format (e.g. jpg, hevc, pdf)")
    parser.add_argument("-o", "--outdir", metavar="DIR", help="Output folder (default: next to source)")
    parser.add_argument("--quality", type=int, default=90, help="Image quality 1-100 (default 90)")
    parser.add_argument(
        "--codec",
        choices=["copy", "h264", "hevc"],
        help="Video codec (default: copy streams when the container allows it)",
    )
    parser.add_argument("--crf", type=int, help="Video quality, lower = better (h264 default 23, hevc 28)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    parser.add_argument("--gui", action="store_true", help="Launch the graphical interface")
    parser.add_argument("--version", action="version", version=f"fileconv {__version__}")
    return parser


def collect_inputs(raw_inputs: list[str]) -> list[Path]:
    """Expand globs (PowerShell/cmd don't) and folder arguments into file lists."""
    known_exts = {f".{ext}" for ext in set(IMAGE_FORMATS) | VIDEO_CONTAINERS | AUDIO_FORMATS | DOC_FORMATS}
    files: list[Path] = []
    for raw in raw_inputs:
        if any(char in raw for char in "*?["):
            matches = [Path(m) for m in glob.glob(raw)]
            if not matches:
                print(f"warning: no files match {raw!r}", file=sys.stderr)
            files.extend(m for m in matches if m.is_file())
            continue
        path = Path(raw)
        if path.is_dir():
            found = sorted(p for p in path.iterdir() if p.is_file() and p.suffix.lower() in known_exts)
            if not found:
                print(f"warning: no convertible files in folder {raw!r}", file=sys.stderr)
            files.extend(found)
        elif path.is_file():
            files.append(path)
        else:
            print(f"warning: {raw!r} not found, skipping", file=sys.stderr)
    return files


def output_path(src: Path, target_ext: str, outdir: str | None) -> Path:
    directory = Path(outdir) if outdir else src.parent
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / f"{src.stem}.{target_ext}"
    if dest.resolve() == src.resolve():
        dest = directory / f"{src.stem}_converted.{target_ext}"
    return dest


def convert_one(src: Path, target: str, args: argparse.Namespace) -> Path:
    """Dispatch a single file to the right converter. Returns the output path."""
    src_ext = src.suffix.lstrip(".").lower()

    if target in IMAGE_FORMATS and src_ext in IMAGE_FORMATS:
        dest = output_path(src, target, args.outdir)
        _check_overwrite(dest, args.overwrite)
        return convert_image(src, dest, quality=args.quality)

    if target in VIDEO_TARGETS and src_ext in VIDEO_CONTAINERS:
        real_ext = resolve_video_target(src, target)
        dest = output_path(src, real_ext, args.outdir)
        _check_overwrite(dest, args.overwrite)
        codec = "hevc" if target == "hevc" else args.codec
        return convert_video(src, dest, codec=codec, crf=args.crf)

    if target in AUDIO_FORMATS and (src_ext in AUDIO_FORMATS or src_ext in VIDEO_CONTAINERS):
        dest = output_path(src, target, args.outdir)
        _check_overwrite(dest, args.overwrite)
        return convert_audio(src, dest)

    if src_ext == "docx" and target == "pdf":
        dest = output_path(src, "pdf", args.outdir)
        _check_overwrite(dest, args.overwrite)
        return docx_to_pdf(src, dest)

    if src_ext == "pdf" and target == "docx":
        dest = output_path(src, "docx", args.outdir)
        _check_overwrite(dest, args.overwrite)
        return pdf_to_docx(src, dest)

    raise ValueError(f"No converter for .{src_ext} -> .{target}")


def _check_overwrite(dest: Path, overwrite: bool) -> None:
    if dest.exists() and not overwrite:
        raise FileExistsError(f"{dest} already exists (use --overwrite to replace it)")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui or (not args.inputs and not args.to):
        from .gui import run_gui

        run_gui()
        return 0

    if not args.inputs:
        parser.error("no input files given")
    if not args.to:
        parser.error("missing -t/--to target format")

    target = args.to.lower().lstrip(".")
    if target not in ALL_TARGETS:
        parser.error(f"unknown target {args.to!r}. Supported: {', '.join(ALL_TARGETS)}")

    files = collect_inputs(args.inputs)
    if not files:
        print("error: nothing to convert", file=sys.stderr)
        return 1

    failures = 0
    for src in files:
        try:
            dest = convert_one(src, target, args)
            print(f"  {src}  ->  {dest}")
        except Exception as exc:
            failures += 1
            print(f"  {src}  FAILED: {exc}", file=sys.stderr)

    total = len(files)
    print(f"Done: {total - failures}/{total} converted.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
