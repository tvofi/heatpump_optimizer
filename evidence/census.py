import ast as _cr_ast, pathlib, sys
_CR_PKG = pathlib.Path(sys.argv[1]) / "custom_components/heatpump_optimizer"
src = (pathlib.Path(sys.argv[1]) / "tests/features.py").read_text()
start = src.index("def _cr_save_sites():"); end = src.index("_cr_sites = _cr_save_sites()")
exec(src[start:end])
sites = _cr_save_sites()
by = {h: [s for s in sites if s[2] == h] for h in ("held", "propagates", "swallowed")}
ok = by["swallowed"] == [] and len(by["held"]) >= 18
print("swallowed", by["swallowed"]); print("held", len(by["held"]), "dhw:", [s for s in by["held"] if s[0]=="dhw_learning.py"])
print("CENSUS", "PASS" if ok else "FAIL")
