"""Resolve immutable application resources independently of the working directory."""

import os
from pathlib import Path
import sys


def resource_root():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        if os.environ.get('RESOURCEPATH'):
            return Path(os.environ['RESOURCEPATH'])
    return Path(__file__).resolve().parents[1]


def mpv_path():
    import shutil
    bundled = resource_root() / 'bin' / ('mpv.exe' if os.name == 'nt' else 'mpv')
    return str(bundled) if bundled.is_file() else shutil.which('mpv') or str(bundled)
