"""Entry point for the packaged Windows app (PyInstaller, windowed mode).

Double-clicking launches the GUI. Passing arguments runs the CLI silently,
which also lets the built exe be used from scripts:
    FileConverter.exe photo.heic -t jpg
"""

import io
import sys

# In a windowed (no-console) PyInstaller app, stdout/stderr may be None;
# the CLI's print() calls need a real writable stream.
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

from fileconv.cli import main

if __name__ == "__main__":
    sys.exit(main())
