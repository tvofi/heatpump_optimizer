import json, sys, shutil, tempfile, pathlib, importlib.util
tree, rec_src, closures, checktxt = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("closure", tree + "/tests/closure.py")
sys.path.insert(0, tree + "/tests")
closure = importlib.util.module_from_spec(spec); spec.loader.exec_module(closure)
td = pathlib.Path(tempfile.mkdtemp()); p = td / "closures.json"; shutil.copy(closures, p)
r = td / "rec"; shutil.copytree(rec_src, r)
if checktxt != "-": shutil.copy(checktxt, r / "check.txt")
closure.CLOSURES = p; closure.ROOT = pathlib.Path(sys.argv[5]) if len(sys.argv) > 5 else closure.ROOT
st = closure.apply_under_scoped_recordings(r, partial=True)
print(f"status={st} red={closure.autofix_repair_failed('closures-autofix', st)} unchanged={p.read_text()==open(closures).read()}")
