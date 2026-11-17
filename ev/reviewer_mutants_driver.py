"""Reviewer mutants for #3670 delta 95e70c96 (run from the worktree root)."""
import subprocess, sys, pathlib
W = sys.argv[1]
ST = pathlib.Path("custom_components/heatpump_optimizer/store.py")
DR = pathlib.Path("custom_components/heatpump_optimizer/draw_range.py")
M = "# -- R11-OUTSIDE-HONEST-METERED-FLOOR: the learned floor moves the plan"
MUT = {
 "M1 floor_kw re-declared whole=_DRAW_KEY": (ST, '"draw/floor_kw": Domain("real", _POS),', '"draw/floor_kw": Domain("real", _POS, whole=_DRAW_KEY),'),
 "M2 floor_since re-declared whole=_DRAW_KEY": (ST, '"draw/floor_since": _COUNT,', '"draw/floor_since": Domain("int", 0, whole=_DRAW_KEY),'),
 "M3 loader drops samples on a bad floor_kw cell (declaration left cell)": (DR,
   '        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n',
   '        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n        if out.floor_kw is None and data.get("floor_kw") is not None and not (isinstance(data.get("floor_kw"), (int, float)) and not isinstance(data.get("floor_kw"), bool) and data.get("floor_kw") > 0):\n            out.samples.clear()\n'),
 "M4 loader zeroes engaged on a bad floor_since cell": (DR,
   '        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n',
   '        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n        if data.get("floor_since") is not None and type(data.get("floor_since")) is not int:\n            out.config = None\n'),
 "N0 null control: comment-only edit": (ST, '"draw/floor_since": _COUNT,', '"draw/floor_since": _COUNT,  # null'),
}
for name, (p, old, new) in MUT.items():
    src = p.read_text()
    assert src.count(old) == 1, (name, src.count(old))
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f"exec(open('{W}/prelude.py').read())", M],
                           capture_output=True, text=True, env={**__import__("os").environ, "PYTHONPATH": "tests/hastub"})
        fails = [l for l in r.stdout.splitlines() if l.startswith("  FAIL") or "FAIL" in l[:8]]
        tail = (r.stdout.strip().splitlines() or ["<none>"])[-1]
        print(f"{name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {tail}")
        for f in fails: print("    " + f[:220])
        if r.stderr.strip(): print("    stderr: " + r.stderr.strip().splitlines()[-1][:220])
    finally:
        p.write_text(src)
