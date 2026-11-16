"""Reviewer mutants for #3670 round 2: each applies one textual edit, runs the
declared-cost check (tests/_fb2.py, the head's floor block cut before its
application section), records rc and the summary line, and restores."""
import pathlib, subprocess, sys, os
ROOT = pathlib.Path(sys.argv[1])
S = "custom_components/heatpump_optimizer/store.py"
D = "custom_components/heatpump_optimizer/draw_range.py"
MUT = [
 ("R1 floor_kw whole restored", S, '"draw/floor_kw": Domain("real", _POS),', '"draw/floor_kw": Domain("real", _POS, whole=_DRAW_KEY),'),
 ("R2 floor_since whole restored", S, '"draw/floor_since": _COUNT,', '"draw/floor_since": Domain("int", 0, whole=_DRAW_KEY),'),
 ("R3 loader drops record on a bad floor_kw", D,
  "        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n",
  "        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n"
  "        if data.get('floor_kw') is not None and out.floor_kw is None:\n            out.samples = []\n"),
 ("R4 loader drops record on a bad floor_since", D,
  "        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n",
  "        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n"
  "        if 'floor_since' in data and type(data['floor_since']) is not int:\n            out.samples = []\n"),
]
env = {**os.environ, "PYTHONPATH": "tests/hastub:tests"}
for name, path, old, new in MUT:
    p = ROOT / path; src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tests/_fb2.py"], cwd=ROOT, env=env, capture_output=True, text=True, timeout=200)
        tail = [l for l in r.stdout.splitlines() if "FEATURES BLOCK" in l or l.startswith("  FAIL")]
        print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}")
        for l in tail: print("   ", l[:400])
    finally:
        p.write_text(src)
