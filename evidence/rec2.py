import sys, types, shutil
from pathlib import Path
root=Path(sys.argv[1]).resolve(); keep=Path(sys.argv[2])
sys.path.insert(0,str(root/"tools/ci")); import selftest_scope as s
shim=types.SimpleNamespace(**{k:getattr(shutil,k) for k in dir(shutil) if not k.startswith("__")})
def rmtree(p,*a,**k): keep.write_text(str(p)); print("KEPT traces at",p,flush=True)
shim.rmtree=rmtree; s.shutil=shim
sys.exit(s.record(root, sys.argv[4].split(","), Path(sys.argv[3])))
