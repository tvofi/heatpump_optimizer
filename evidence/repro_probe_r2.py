"""Reviewer's reproduction, round 2 (the reviewer's instrument): owner_only.probe through the real Host,
over a sound synthetic account (owner paths that exist and are closed), one perturbation per line."""
import importlib, os, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
m = importlib.import_module("owner_only")
PY = sys.executable
td = tempfile.mkdtemp()

class Sealed(m.Host):
    """As root every mode reads; stand in for the kernel's refusal of the owner paths (the body's own device)."""

def fresh(name, in_git=False):
    base = os.path.join(td, name); os.makedirs(base)
    if in_git:
        subprocess.run(["git", "init", "-q", base], check=True)
    ident = os.path.join(td, name + "-owner-id"); os.makedirs(ident); Path(ident, "hpo-author.pem").write_text("k")
    root = os.path.join(base, "root"); os.makedirs(root, mode=0o700)
    m.prepare(root, [ident], [], "MODEL_KEY")
    return root, ident

def probe(root, ident, path=None, extra=None, ghdir=None):
    env = {"HOME": os.path.join(root, "home"), "HPO_IDENTITY_DIR": os.path.join(root, "identity"), "HPO_OWNER_ONLY": "1",
           "PATH": path or (os.path.join(root, "bin") + (":" + ghdir if ghdir else "") + ":/usr/local/bin:/usr/bin:/bin"), **(extra or {})}
    v = m.Host(env)
    closed = lambda p: p == ident or p.startswith(ident + os.sep)
    real_stat, real_access, real_listdir = os.stat, os.access, os.listdir
    def _access(p, mode): return False if closed(p) else real_access(p, mode)
    def _listdir(p):
        if closed(p): raise PermissionError(p)
        return real_listdir(p)
    v._access, v._listdir = _access, _listdir
    lines = [ln.replace(td, "<td>") for ln in m.probe(v, root)]
    return ("probe OK" if not lines else "REFUSED " + " | ".join(lines))

r, i = fresh("null")
print("null control (sound account, real git):", probe(r, i))
r, i = fresh("ingit", in_git=True)
print("control: root inside a git work tree:", probe(r, i))
print("same root, GIT_DIR names a path that is no repository:", probe(r, i, extra={"GIT_DIR": os.path.join(td, "nowhere")}))
print("same root, GIT_CEILING_DIRECTORIES names the work tree:", probe(r, i, extra={"GIT_CEILING_DIRECTORIES": os.path.dirname(r)}))
for label, body in (("exits 0 (control)", "exit 0"), ("exits 1", "exit 1"), ("exits 2", "exit 2"), ("is killed by a signal", "kill -9 $$"), ("exits 127 (its interpreter missing a command)", "nonexistent-cmd-xyz")):
    r, i = fresh("gh" + label[:9].replace(" ", ""))
    g = os.path.join(td, "ghbin" + label[:9].replace(" ", "")); os.makedirs(g)
    Path(g, "gh").write_text("#!/bin/sh\n" + body + "\n"); os.chmod(os.path.join(g, "gh"), 0o755)
    print(f"a second gh on PATH that {label}:", probe(r, i, ghdir=g))
r, i = fresh("names")
for name in ("PUSH_AUTH", "DEPLOYKEY", "SSHKEY", "PRIVATEKEY", "ACCESS_TOKENS", "PUSH_SECRETS", "SIGNING_KEYS", "GH_PASS", "PUSH_BEARER", "SESSION_COOKIE", "PUSH_JWT", "PUSH_AUTHORIZATION", "NETRC", "GIT_CONFIG_COUNT", "MODEL_KEY"):
    print(f"variable {name} set:", probe(r, i, extra={name: "x"}))
shutil.rmtree(td)
