# Reviewer's own instrument (disclosed): the replay's two readings, offline,
# with the PR heads fetched over git because gh is unauthenticated here.
import subprocess, sys
sys.path.insert(0, "tools/policy"); import budget_raise_gate as g
def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    if r.returncode: raise SystemExit(f"git {' '.join(a)} failed: {r.stderr}")
    return r.stdout
for arg in sys.argv[1:]:
    pr, _, at = arg.partition(":")
    h = git("rev-parse", f"refs/rev/pr{pr}").strip()
    base = git("merge-base", at or "origin/main", h).strip()
    files = git("diff", "--no-renames", "--name-only", base, h).split()
    path = [f for f in files if f.endswith(g.SUFFIX)]
    trees = {}
    def ls(s):
        trees[s] = set(git("ls-tree", "-r", "--name-only", s).splitlines()); return sorted(trees[s])
    def show(s, p): return git("show", f"{s}:{p}") if p in trees[s] else None
    paths, raises = g.raises_between(base, h, ls, show)
    print(f"#{pr} head {h[:12]} base {base[:12]}\n  path : {'RAISE' if path else 'none'} ({', '.join(path)})\n  gate : {len(raises)} raise(s): {'; '.join(raises)[:300]}")
