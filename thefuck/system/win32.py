import os
import sys
import msvcrt
from .. import const


def _enable_utf8_output():
    """Switches redirected standard streams to utf-8.

    Python 3.6+ already prints unicode to the Windows console through
    `WriteConsoleW`, so only streams redirected to a file or a pipe still
    use the locale encoding. Reconfiguring them keeps the output
    consistent with `PYTHONIOENCODING=utf-8`, which both `fuck.bat` and
    `fuck.ps1` set, and can never fail the execution.

    """
    for stream in (sys.stdout, sys.stderr):
        if stream is None:
            continue

        encoding = (getattr(stream, 'encoding', None) or '')
        if encoding.lower().replace('-', '') == 'utf8':
            continue

        reconfigure = getattr(stream, 'reconfigure', None)
        if reconfigure is None:
            continue

        try:
            reconfigure(encoding='utf-8')
        except (AttributeError, OSError, ValueError):
            pass


def init_output():
    import colorama
    _enable_utf8_output()
    colorama.init()


def get_key():
    ch = msvcrt.getwch()
    if ch in ('\x00', '\xe0'):  # arrow or function key prefix?
        ch = msvcrt.getwch()  # second call returns the actual key code

    if ch in const.KEY_MAPPING:
        return const.KEY_MAPPING[ch]
    if ch == 'H':
        return const.KEY_UP
    if ch == 'P':
        return const.KEY_DOWN

    return ch


def open_command(arg):
    return 'cmd /c start ' + arg


try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


def _expanduser(self):
    return self.__class__(os.path.expanduser(str(self)))


# pathlib's expanduser fails on windows, see http://bugs.python.org/issue19776
Path.expanduser = _expanduser
