import typing, collections.abc
if not hasattr(typing, "ByteString"):
    class _BS(bytes): pass
    typing.ByteString = _BS
import sys as _s
_vp = "/home/claude/venv/lib/python3.14/site-packages"
if _vp not in _s.path:
    _s.path.append(_vp)
