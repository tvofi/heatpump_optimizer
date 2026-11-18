# reviewer: compare the check's derived claim set with a case-insensitive / wider spelling set
import runpy, re, pathlib
g = runpy.run_path("tests/doc_claims.py", run_name="x")
pkg = pathlib.Path("custom_components/heatpump_optimizer")
rx = g["_HA_FREE_CLAIM"]
wide = re.compile(r"free of\s+(?:any\s+)?(?:#\s*)?Home\s+(?:#\s*)?Assistant|no Home\s+Assistant|HA-free|imports no Home", re.S | re.I)
narrow = sorted(p.stem for p in pkg.glob("*.py") if rx.search(p.read_text()))
widened = sorted(p.stem for p in pkg.glob("*.py") if wide.search(p.read_text()))
print("narrow", len(narrow), narrow)
print("missed by narrow", sorted(set(widened) - set(narrow)))
own = {p.stem for p in pkg.glob("*.py") if p.stem != "__init__" and not g["_imports_ha_itself"](p)}
miss = sorted(set(widened) - set(narrow))
got = g["_imports_without_ha"](miss)
for m in miss: print(m, "own-HA-free" if m in own else "imports-HA-itself", got.get(m))
