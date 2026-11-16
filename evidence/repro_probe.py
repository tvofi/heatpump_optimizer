"""Reviewer's reproduction (the reviewer's instrument): owner_only.probe through the real Host view."""
import importlib, os, subprocess, sys, tempfile, shutil
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
m = importlib.import_module("owner_only")
PY = sys.executable
def run(root, path, extra=None):
    env = {"HOME": os.path.join(root, "home"), "HPO_IDENTITY_DIR": os.path.join(root, "identity"), "HPO_OWNER_ONLY": "1",
           "PATH": path, **(extra or {})}
    p = subprocess.run([PY, "-I", "tools/audit/seat/owner_only.py", "probe", "--private-root", root], env=env, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()
td = tempfile.mkdtemp()
# an owner identity directory this account CAN read, to prove the control sees
ident = os.path.join(td, "owner-id"); os.makedirs(ident); Path(ident, "hpo-author.pem").write_text("k")
def fresh(name, in_git, identity_dirs):
    base = os.path.join(td, name); os.makedirs(base)
    if in_git: subprocess.run(["git", "init", "-q", base], check=True)
    root = os.path.join(base, "root"); os.makedirs(root, mode=0o700)
    m.prepare(root, identity_dirs, [])
    for d in ("home", "identity"):
        os.makedirs(os.path.join(root, d), mode=0o700, exist_ok=True)
    return root
full = os.path.join("%s", "bin") + ":/usr/local/bin:/usr/bin:/bin"
r = fresh("null", False, [os.path.join(td, "absent-typo")])
print("baseline (root outside a tree, git on PATH, identity path ABSENT):", *run(r, full % r))
r = fresh("readable", False, [ident])
print("control (identity directory readable):", *run(r, full % r))
r = fresh("ingit", True, [os.path.join(td, "absent-typo")])
print("root inside a git work tree, git on PATH:", *run(r, full % r))
print("same root, PATH = the root's bin only (no git resolves):", *run(r, os.path.join(r, "bin")))
r = fresh("pushauth", False, [os.path.join(td, "absent-typo")])
print("PUSH_AUTH set (tools/pr/merge_main_bot.py:293 pushes with it):", *run(r, full % r, {"PUSH_AUTH": "eA=="}))
print("control GH_TOKEN set:", *run(r, full % r, {"GH_TOKEN": "x"}))
shutil.rmtree(td)
