import json, os, subprocess, sys, tempfile, importlib.util
from pathlib import Path
src = sys.argv[1]
spec = importlib.util.spec_from_file_location("ss", src); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
    r = Path(td); env = {**os.environ, "GIT_AUTHOR_NAME": "x", "GIT_AUTHOR_EMAIL": "x@x", "GIT_COMMITTER_NAME": "x", "GIT_COMMITTER_EMAIL": "x@x"}
    g = lambda *a: subprocess.run(["git", *a], cwd=r, env=env, check=True, capture_output=True, text=True).stdout.strip()
    g("init", "-q")
    e = lambda files: {"run_sha": "s", "files": files, "probes": [], "dirs": [], "git": [], "index": False, "objects": False}
    (r / m.TABLE).parent.mkdir(parents=True, exist_ok=True)
    (r / "tools/x.py").write_text("a\n"); (r / m.TABLE).write_text(json.dumps({"steps": {"s": e(["tools/x.py"])}}))
    g("add", "-A"); g("commit", "-qm", "b"); b = g("rev-parse", "HEAD")
    (r / "tools/x.py").write_text("b\n"); (r / m.TABLE).write_text(json.dumps({"steps": {"s": e([])}}))
    g("add", "-A"); g("commit", "-qm", "h")
    print("RESULT shrink_gaps on a diff that MODIFIES tools/x.py and drops its read:", m.shrink_gaps(r, b))
