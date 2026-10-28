# Reviewer demo: which CLI flags does main()'s --group branch accept and never forward?
import importlib.util, io, contextlib, sys
spec = importlib.util.spec_from_file_location("cd", sys.argv[1]); cd = importlib.util.module_from_spec(spec); spec.loader.exec_module(cd)
seen = {}
def fake(role, group, model, **kw): seen.update(role=role, group=group, model=model, **kw); return "dispatch/x"
cd.dispatch_group = fake
argv = ["--role", "fixer", "--group", "G", "--model", "m", "--env-id", "env_OTHER", "--brief", "/nonexistent/brief.md",
        "--topic", "t-other", "--repo", "other/repo", "--out", "/nonexistent/out.json"]
out = io.StringIO()
with contextlib.redirect_stdout(out): rc = cd.main(argv)
print("rc", rc, "stdout", out.getvalue().strip())
print("forwarded", sorted(seen))
vals = set(map(str, seen.values()))
for v in ["env_OTHER", "/nonexistent/brief.md", "t-other", "other/repo", "/nonexistent/out.json"]:
    print("value", v, "forwarded" if v in vals else "DROPPED")
