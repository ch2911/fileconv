"""Minimal Tkinter GUI wrapping the same converters as the CLI."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from .cli import ALL_TARGETS, convert_one

_FILETYPES = [
    ("All supported", "*.heic *.heif *.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff "
                      "*.gif *.ico *.mp4 *.mov *.mkv *.webm *.avi *.mp3 *.wav *.flac "
                      "*.aac *.m4a *.ogg *.opus *.docx *.pdf"),
    ("Images", "*.heic *.heif *.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.gif *.ico"),
    ("Video", "*.mp4 *.mov *.mkv *.webm *.avi"),
    ("Audio", "*.mp3 *.wav *.flac *.aac *.m4a *.ogg *.opus"),
    ("Documents", "*.docx *.pdf"),
    ("All files", "*.*"),
]


class _Args:
    """Duck-typed stand-in for the argparse namespace convert_one expects."""

    def __init__(self, outdir: str | None):
        self.outdir = outdir or None
        self.quality = 90
        self.codec = None
        self.crf = None
        self.overwrite = True


class ConverterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("File Converter")
        root.geometry("640x480")
        root.minsize(520, 400)

        top = ttk.Frame(root, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Add files...", command=self.add_files).pack(side="left")
        ttk.Button(top, text="Clear", command=self.clear_files).pack(side="left", padx=(6, 0))
        ttk.Label(top, text="Convert to:").pack(side="left", padx=(18, 4))
        self.target = tk.StringVar(value="jpg")
        ttk.Combobox(top, textvariable=self.target, values=ALL_TARGETS,
                     width=8, state="readonly").pack(side="left")

        mid = ttk.Frame(root, padding=(8, 0))
        mid.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(mid, selectmode="extended")
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(mid, command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)

        out_row = ttk.Frame(root, padding=8)
        out_row.pack(fill="x")
        ttk.Label(out_row, text="Output folder:").pack(side="left")
        self.outdir = tk.StringVar()
        ttk.Entry(out_row, textvariable=self.outdir).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(out_row, text="Browse...", command=self.pick_outdir).pack(side="left")

        bottom = ttk.Frame(root, padding=8)
        bottom.pack(fill="x")
        self.convert_btn = ttk.Button(bottom, text="Convert", command=self.start_convert)
        self.convert_btn.pack(side="left")
        self.status = tk.StringVar(value="Add files to begin. Empty output folder = save next to source.")
        ttk.Label(bottom, textvariable=self.status, anchor="w").pack(side="left", fill="x",
                                                                     expand=True, padx=(10, 0))

        self.log = tk.Text(root, height=7, state="disabled")
        self.log.pack(fill="x", padx=8, pady=(0, 8))

    # ---- UI callbacks -------------------------------------------------
    def add_files(self) -> None:
        for name in filedialog.askopenfilenames(filetypes=_FILETYPES):
            if name not in self.listbox.get(0, "end"):
                self.listbox.insert("end", name)

    def clear_files(self) -> None:
        self.listbox.delete(0, "end")

    def pick_outdir(self) -> None:
        chosen = filedialog.askdirectory()
        if chosen:
            self.outdir.set(chosen)

    def start_convert(self) -> None:
        files = [Path(p) for p in self.listbox.get(0, "end")]
        if not files:
            self.status.set("No files selected.")
            return
        self.convert_btn.config(state="disabled")
        self.status.set("Converting...")
        threading.Thread(target=self._convert_all, args=(files,), daemon=True).start()

    # ---- worker --------------------------------------------------------
    def _convert_all(self, files: list[Path]) -> None:
        args = _Args(self.outdir.get().strip())
        target = self.target.get()
        done = 0
        for src in files:
            try:
                dest = convert_one(src, target, args)
                self._log(f"OK      {src.name}  ->  {dest}")
                done += 1
            except Exception as exc:
                self._log(f"FAILED  {src.name}: {exc}")
        self.root.after(0, self._finish, done, len(files))

    def _finish(self, done: int, total: int) -> None:
        self.status.set(f"Done: {done}/{total} converted.")
        self.convert_btn.config(state="normal")

    def _log(self, line: str) -> None:
        def append() -> None:
            self.log.config(state="normal")
            self.log.insert("end", line + "\n")
            self.log.see("end")
            self.log.config(state="disabled")

        self.root.after(0, append)


def run_gui() -> None:
    root = tk.Tk()
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
