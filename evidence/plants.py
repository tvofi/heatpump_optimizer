o = repr(_sp_old)
plants = {
 "control one-hop name (body's shape)": f"_P = {o}\n_X = open(_P)\n",
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
}
print("old =", _sp_old)
for k, p in plants.items():
    f = _sp_faults(_sp_unit, _sp_unit_src + "\nimport os\nfrom pathlib import Path\n" + p)
    # an actual run of the planted program: does it really open a missing file?
    print(("REFUSED " if f else "ESCAPES ") + k)
