# whole-tree over-fire control: every repo-path literal each tracked .py OPENs,
# with whether it resolves. Diffed across the two heads by the caller.
import subprocess
from pathlib import Path
files = subprocess.run(["git","ls-files","*.py"],capture_output=True,text=True).stdout.split()
for f in files:
    try: src = Path(f).read_text(encoding="utf-8")
    except Exception: continue
    try: res = _sp_literals(src)
    except Exception: continue
    for line, lit, got in res:
        print("%s\t%d\t%s\t%d" % (f, line, lit, 1 if Path(got.rstrip("/")).exists() else 0))
