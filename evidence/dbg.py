_src = 'import os\nfrom pathlib import Path\n_P = Path(".") / "dev/nope_xyz/file.py"\n_X = _P.open()\n'
import ast as _a
_tr = _a.parse(_src)
print("binds", {k: [type(x).__name__ for x in v] for k, v in _binds_w(_tr).items()})
print("SP_TOPS has dev:", "dev" in _SP_TOPS, "| has .claude:", ".claude" in _SP_TOPS)
print("arm  ", _sp_literals(_src))
print("wide ", _literals_w(_src))
_c2 = 'import os\nfrom pathlib import Path\n_P = Path(".") / "dev/nope_xyz/file.py"\n_X = _P.read_text()\n'
print("ctrl-read_text arm", _sp_literals(_c2), "wide", _literals_w(_c2))
