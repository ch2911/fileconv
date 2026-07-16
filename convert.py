"""Entry point: python convert.py <files> -t <format>  (or no args for the GUI)."""

from fileconv.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
