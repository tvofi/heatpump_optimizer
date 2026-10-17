# REVIEWER'S OWN enumerator (not the finder's, not the fixer's): the class is
# "shapes by which a module names the path it opens", which the round-1 plant
# list is a sample of. Each shape is planted in the cited unit and the arm's own
# _sp_literals is asked whether it reads the literal as an open.
def _arm_opens(src, lit):
    return any(l == lit for _, l, _ in _sp_literals(src))

o = repr(_sp_old)
S = _sp_unit_src + "\nimport os, subprocess\nfrom pathlib import Path\n"
SHAPES = {
 # --- the 13 the arm/plant list carries (population, not class) ---
 "one-hop name": f"_P = {o}\n_X = open(_P)\n",
 "two-hop alias": f"_A = {o}\n_B = _A\n_X = open(_B)\n",
 "two-hop alias via join": f"_A = {o}\n_B = _A\n_X = os.path.join('.', _B)\n",
 "pathlib / in open": f"_X = open(Path('.') / {o})\n",
 "pathlib / then read_text": f"_X = (Path('.') / {o}).read_text()\n",
 "pathlib / via name then read_text": f"_P = Path('.') / {o}\n_X = _P.read_text()\n",
 "f-string root prefix": f"_X = open(f\"{{os.getcwd()}}/{_sp_old}\")\n",
 "f-string bare": f"_X = open(f\"{_sp_old}\")\n",
 "dict value then subscript": f"_C = {{'k': {o}}}\n_X = open(_C['k'])\n",
 "tuple-unpack assign": f"_A, _B = {o}, 'x'\n_X = open(_A)\n",
 "annotated assign": f"_A: str = {o}\n_X = open(_A)\n",
 "str concat": f"_X = open('./' + {o})\n",
 "read via json.loads(Path.read_text)": f"_X = Path({o}).read_text()\n",
 # --- extra shapes in the same class ---
 "three-hop alias": f"_A = {o}\n_B = _A\n_C = _B\n_X = open(_C)\n",
 "chained assign": f"_A = _B = {o}\n_X = open(_B)\n",
 "walrus bind": f"_A = None\nif (_A := {o}):\n    _X = open(_A)\n",
 "for-target bind": f"for _P in ({o},):\n    _X = open(_P)\n",
 "func-param default": f"def f(_p={o}):\n    return open(_p)\n_X = f()\n",
 "list index": f"_L = [{o}]\n_X = open(_L[0])\n",
 "tuple index": f"_T = ({o},)\n_X = open(_T[0])\n",
 "dict key by name": f"_C = {{'k': {o}}}\n_K = 'k'\n_X = open(_C[_K])\n",
 "attr bind (ns)": f"class C: p = {o}\n_X = open(C.p)\n",
 "augassign": f"_A = ''\n_A += {o}\n_X = open(_A)\n",
 "percent-format": f"_X = open('%s' % {o})\n",
 "pathlib joinpath": f"_X = Path('.').joinpath({o})\n",
 "conditional expr": f"_X = open({o} if os.name else 'x')\n",
 "os.path.join first arg": f"_X = open(os.path.join({o}, 'x'))\n",
 "Path receiver .open()": f"_X = (Path('.') / {o}).open()\n",
 "named receiver .open()": f"_P = Path('.') / {o}\n_X = _P.open()\n",
 "named receiver .read_bytes()": f"_P = Path('.') / {o}\n_X = _P.read_bytes()\n",
 "receiver .open() in with": f"with (Path('.') / {o}).open() as _f:\n    pass\n",
 "star-unpack": f"_A, *_R = {o}, 'x'\n_X = open(_A)\n",
 "global-in-func": f"def f():\n    global _G\n    _G = {o}\n_X = open(_G)\n",
 "nested f-string attr": f"_R = os.getcwd()\n_X = open(f\"{{_R}}/{_sp_old}\")\n",
}
esc = []
for k, p in SHAPES.items():
    ok = _arm_opens(S + p, _sp_old)
    print(("READS  " if ok else "ESCAPES") + " " + k)
    if not ok:
        esc.append(k)
# null control: a held literal with NO open must not read as an open
held = _arm_opens(S + f"_X = ({o},)\n", _sp_old)
print("NULL held-literal (must be READS=False):", held)
print("ESCAPE_COUNT", len(esc), "OF", len(SHAPES))
print("ESCAPES", esc)
