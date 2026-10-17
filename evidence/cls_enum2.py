# REVIEWER'S OWN round-2 variants: the same class, with the realistic forms of
# the two shapes that still escape.
def _arm_opens(src, lit):
    return any(l == lit for _, l, _ in _sp_literals(src))
o = repr(_sp_old)
S = _sp_unit_src + "\nimport os\nfrom pathlib import Path\n"
SH = {
 "for-target (fixed r2)": f"for _P in ({o},):\n    _X = open(_P)\n",
 "walrus (fixed r2)": f"_A = None\nif (_A := {o}):\n    _X = open(_A)\n",
 ".open() receiver (fixed r2)": f"_X = (Path('.') / {o}).open()\n",
 "class attr, read as C.P": f"class C:\n    P = {o}\n_X = open(C.P)\n",
 "class attr, read via instance": f"class C:\n    P = {o}\n_X = open(C().P)\n",
 "self.attr set in __init__, read in another method":
   f"class C:\n    def __init__(self):\n        self._p = {o}\n    def run(self):\n        return open(self._p)\n",
 "self.attr set and read in the SAME method":
   f"class C:\n    def run(self):\n        self._p = {o}\n        return open(self._p)\n",
 "global set in a function, read at module level":
   f"_G = None\ndef f():\n    global _G\n    _G = {o}\n_X = open(_G)\n",
 "global set in a function, read in ANOTHER function":
   f"_G = None\ndef f():\n    global _G\n    _G = {o}\ndef g():\n    return open(_G)\n",
 "nonlocal in a nested function":
   f"def outer():\n    _N = None\n    def inner():\n        nonlocal _N\n        _N = {o}\n    inner()\n    return open(_N)\n",
 "module constant read through a function": f"_M = {o}\ndef f():\n    return open(_M)\n",
}
esc = []
for k, p in SH.items():
    ok = _arm_opens(S + p, _sp_old)
    print(("READS  " if ok else "ESCAPES") + " " + k)
    if not ok: esc.append(k)
print("NULL held-literal (must be False):", _arm_opens(S + f"_X = ({o},)\n", _sp_old))
print("ESCAPE_COUNT", len(esc), "OF", len(SH)); print("ESCAPES", esc)
