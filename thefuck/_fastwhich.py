"""`shutil.which` replacement backed by a cached PATH index.

The first lookup scans PATH once (a single `os.scandir` per directory) and
reuses the result, so later lookups are just set membership tests.  Rules
probe for their apps at import time, and each missed probe used to walk the
whole PATH again.
"""

import os
import sys

try:
    from shutil import which as _shutil_which
except ImportError:  # Python 2 has no `shutil.which`
    _shutil_which = None

from .utils import _iter_path_entries

_index = None


def _path_dirs():
    return [d for d in os.environ.get('PATH', '').split(os.pathsep) if d]


def _is_windows():
    return sys.platform == 'win32'


def _build_index():
    global _index
    pathext = [e for e in os.environ.get(
        'PATHEXT', '.COM;.EXE;.BAT;.CMD').split(os.pathsep) if e]
    dirs = _path_dirs()
    if _is_windows():
        # `shutil.which` looks in the current directory first on Windows
        dirs = [os.curdir] + dirs
    windows = _is_windows()
    per_dir = []
    for directory in dirs:
        names = {}
        for name in _iter_path_entries(directory):
            names[name.lower() if windows else name] = name
        per_dir.append((directory, names))
    _index = (per_dir, pathext)
    return _index


def _which_fallback(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ.get('PATH', '').split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def which(program):
    if _shutil_which is None or os.path.dirname(program):
        return _which_fallback(program)

    per_dir, pathext = _index or _build_index()
    if _is_windows():
        program = program.lower()
        if any(program.endswith(ext.lower()) for ext in pathext):
            candidates = [program]
        else:
            candidates = [program + ext.lower() for ext in pathext]
        for directory, names in per_dir:
            for candidate in candidates:
                if candidate in names:
                    return os.path.join(directory, names[candidate])
        return None

    for directory, names in per_dir:
        if program in names:
            path = os.path.join(directory, names[program])
            if os.access(path, os.X_OK) and not os.path.isdir(path):
                return path
    return None
