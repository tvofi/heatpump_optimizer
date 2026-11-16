#!/usr/bin/env python3
"""The launcher of an owner-only audit dimension, and the probe that refuses a session able to publish.

    python3 -I owner_only.py launch --private-root DIR --owner-identity DIR [--deploy-key FILE]...
                                    --model-env NAME [--token-fd N | --skip-mirror] -- <session command>
    python3 -I owner_only.py probe --private-root DIR
    python3 -I owner_only.py --self-test [--no-mutants]

A dimension whose dev/audit/config/scopes.json entry carries `owner_only: true`
publishes nothing: its findings go to the owner and to no tree, ref, issue or
comment. The closure is not a filter on what a seat writes. It is that no
process of such a run holds a credential that writes: the seats run under a
SEAT ACCOUNT, an OS account that owns the private root and nothing else, and
this file is the only way a session of that account starts.

`launch`, run by the owner as the seat account:
  1. makes, under the private root (mode 0700, outside every work tree): a
     home, an empty identity directory, a state directory and a bin holding
     the seat gh shim as `gh`; records the owner's key paths in probe.json;
  2. builds the session's environment from an allow-list -- that home,
     HPO_IDENTITY_DIR naming the empty directory, PATH with the bin first,
     HPO_PRIVATE_ROOT, HPO_OWNER_ONLY (the shim's read-only mode),
     HPO_STATE_DIR, and the one model credential named by --model-env -- and
     inherits nothing else;
  3. runs the probe in that environment and stops on any line;
  4. runs tools/audit/seat/corpus_mirror.py, the one process that reads
     GitHub, handing it the read credential on --token-fd; the session never
     sees that descriptor (--skip-mirror reuses a corpus already there);
  5. runs the probe again and replaces itself with the session command.

`probe` exits 0 only when every line below is quiet. A line names a path or a
variable, never a content. It refuses when the running account:
  - has a private root that is not absolute, not mode 0700, inside a git work
    tree, or with no probe.json from the launcher;
  - can read an owner identity directory (where tools/pr/app_mint.sh's
    mint_identity reads the App keys) or a deploy key the launcher was told of;
  - has HPO_IDENTITY_DIR unset, outside the private root, or not empty, or a
    home outside the private root;
  - gets a password from `git credential fill` for github.com;
  - has an agent socket (SSH_AUTH_SOCK) or a private key under its home;
  - has a GitHub token variable set, or a gh further along PATH that reports
    a login;
  - resolves `gh` to anything but the seat shim, or has HPO_OWNER_ONLY unset;
  - runs in a cloud session.
Each workflow driver runs `probe` again in its Prepare step and throws unless
it exits 0.

WHAT THE PROBE CANNOT SEE: a credential in a file it is not told of and that is
not under the account's home; a network route that needs none (an anonymous
write endpoint outside GitHub); and, on a host with one account, the
two-account property itself -- a CI runner is the owner and the seat at once,
so the self-test drives the probe over a fixture view of what an account can
reach, and the real run is proved once on the owner's machine.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHIM = HERE / "shims" / "seat-gh"
MIRROR = HERE / "corpus_mirror.py"
SHIM_MARKER = "# hpo-gh-shim"
ORIGIN_HOST = "github.com"
#: What tools/pr/app_mint.sh, app_comment.sh, app_approve.sh and bus.sh read from an identity directory.
IDENTITY_FILES = ("hpo-author.pem", "hpo-author.appid.txt", "identity-approver.pem", "identity-approver.appid",
                  "hpo-runs.pem", "hpo-runs.appid.txt", "github_known_hosts")
TOKEN_VAR = re.compile(r"(?:GH|GITHUB)_(?:[A-Z0-9]+_)*TOKEN|GH_ENTERPRISE_TOKEN|GITHUB_PAT|HPO_PUSH_URL")
CLOUD_VAR = re.compile(r"CLAUDE_CODE_REMOTE(?:_.*)?|CCR_.*")
PRIVATE_KEY_NAMES = re.compile(r"id_[a-z0-9_]+|.*\.pem|.*_key")
#: The session's PATH after its own bin: the system directories, never the launching user's.
SYSTEM_PATH = "/usr/local/bin:/usr/bin:/bin"
PROBE_FILE = "probe.json"
MANIFEST = "corpus/MANIFEST.json"


class Host:
    """What the running account can reach. The self-test substitutes a fixture view."""

    def __init__(self, env=None):
        self.env = dict(os.environ if env is None else env)

    def mode(self, path: str):
        try:
            return stat.S_IMODE(os.stat(path).st_mode)
        except OSError:
            return None

    def listing(self, path: str):
        """Names in a directory, or None when it cannot be listed."""
        try:
            return sorted(os.listdir(path))
        except OSError:
            return None

    def readable(self, path: str) -> bool:
        return os.access(path, os.R_OK)

    def run(self, argv, stdin: str = "", env=None):
        try:
            p = subprocess.run(argv, input=stdin, capture_output=True, text=True, timeout=30,
                               env=self.env if env is None else env)
        except (OSError, subprocess.TimeoutExpired):
            return 127, ""
        return p.returncode, p.stdout

    def gh_on_path(self):
        """Every executable `gh` on the view's PATH, in order, as (path, is the seat shim)."""
        out = []
        for d in (self.env.get("PATH") or "").split(":"):
            p = os.path.join(d or ".", "gh")
            if os.path.isfile(p) and os.access(p, os.X_OK):
                try:
                    with open(p, errors="replace") as f:
                        f.readline()
                        out.append((p, f.readline().rstrip("\n") == SHIM_MARKER))
                except OSError:
                    out.append((p, False))
        return out


def identity_reach(view, directory: str) -> bool:
    """Whether the account can read anything of an identity directory: its listing, or a key file by name."""
    names = view.listing(directory)
    if names:
        return True
    return any(view.readable(os.path.join(directory, name)) for name in IDENTITY_FILES)


def under(path: str, root: str) -> bool:
    path, root = os.path.normpath(path), os.path.normpath(root)
    return path == root or path.startswith(root + os.sep)


def probe(view, root: str) -> list[str]:
    """Why this account may not run an owner-only session, one line per reason; [] is the only pass."""
    env, why = view.env, []
    if not os.path.isabs(root):
        return [f"the private root {root!r} is not an absolute path"]
    mode = view.mode(root)
    if mode != 0o700:
        why.append(f"the private root {root} is {'absent' if mode is None else f'mode {mode:o}'}, not a directory of mode 700")
    if view.run(["git", "-C", root, "rev-parse", "--is-inside-work-tree"])[0] == 0:
        why.append(f"the private root {root} is inside a git work tree")
    try:
        cfg = json.loads(Path(root, PROBE_FILE).read_text())
        identity_dirs, deploy_keys = list(cfg["identity_dirs"]), list(cfg["deploy_keys"])
    except (OSError, ValueError, KeyError, TypeError):
        return why + [f"{os.path.join(root, PROBE_FILE)} is absent or unreadable: only `owner_only.py launch` starts this session"]
    if not identity_dirs:
        why.append(f"{os.path.join(root, PROBE_FILE)} names no owner identity directory to prove unreadable")
    for d in identity_dirs:
        if identity_reach(view, d):
            why.append(f"this account can read the owner identity directory {d}")
    for k in deploy_keys:
        if view.readable(k):
            why.append(f"this account can read the deploy key {k}")
    idir = env.get("HPO_IDENTITY_DIR") or ""
    if not idir or not under(idir, root) or view.listing(idir) != []:
        why.append("HPO_IDENTITY_DIR is not an empty directory under the private root")
    home = env.get("HOME") or ""
    if not home or not under(home, root):
        why.append("HOME is not under the private root")
    rc, out = view.run(["git", "credential", "fill"], f"protocol=https\nhost={ORIGIN_HOST}\n\n",
                       {**env, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "true", "SSH_ASKPASS": "true"})
    if rc == 0 and re.search(r"^password=.", out, re.M):
        why.append(f"`git credential fill` answers for {ORIGIN_HOST}")
    if env.get("SSH_AUTH_SOCK"):
        why.append("SSH_AUTH_SOCK names an agent socket")
    for sub in (".ssh", ".zcode", ".config/gh"):
        d = os.path.join(home, sub) if home else ""
        for name in (view.listing(d) or []) if d else []:
            if sub == ".config/gh" or PRIVATE_KEY_NAMES.fullmatch(name):
                why.append(f"a credential file is under the home: {os.path.join(d, name)}")
    for name in sorted(env):
        if TOKEN_VAR.fullmatch(name) and env[name]:
            why.append(f"the token variable {name} is set")
        if CLOUD_VAR.fullmatch(name):
            why.append(f"this is a cloud session ({name} is set)")
    ghs = view.gh_on_path()
    if not ghs or not ghs[0][1]:
        why.append("the first `gh` on PATH is not the seat shim (tools/audit/seat/shims/seat-gh)")
    if not env.get("HPO_OWNER_ONLY"):
        why.append("HPO_OWNER_ONLY is unset: the shim would pass a write")
    for path, is_shim in ghs:
        if not is_shim and view.run([path, "auth", "status"])[0] == 0:
            why.append(f"a gh on PATH reports a login: {path}")
    return why


def session_env(root: str, model_env: str, parent: dict) -> dict:
    """The allow-list, and nothing inherited: every key is named here."""
    env = {
        "HOME": os.path.join(root, "home"),
        "HPO_IDENTITY_DIR": os.path.join(root, "identity"),
        "HPO_STATE_DIR": os.path.join(root, "state"),
        "HPO_PRIVATE_ROOT": root,
        "HPO_OWNER_ONLY": "1",
        "PATH": os.path.join(root, "bin") + ":" + SYSTEM_PATH,
        "LANG": "C.UTF-8",
    }
    if model_env in env or TOKEN_VAR.fullmatch(model_env) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", model_env):
        raise ValueError(f"--model-env {model_env!r} is not a model credential's name")
    if not parent.get(model_env):
        raise ValueError(f"--model-env {model_env} is unset in the launching environment")
    env[model_env] = parent[model_env]
    return env


def prepare(root: str, identity_dirs, deploy_keys) -> None:
    """The directories and files the session's environment names, each owner-only."""
    old = os.umask(0o077)
    try:
        for sub in ("home", "identity", "state", "bin", "corpus"):
            os.makedirs(os.path.join(root, sub), mode=0o700, exist_ok=True)
        gh = os.path.join(root, "bin", "gh")
        Path(gh).write_text(SHIM.read_text())
        os.chmod(gh, 0o700)
        Path(root, PROBE_FILE).write_text(json.dumps(
            {"identity_dirs": [os.path.abspath(d) for d in identity_dirs],
             "deploy_keys": [os.path.abspath(k) for k in deploy_keys]}, indent=1) + "\n")
    finally:
        os.umask(old)


def launch(a, parent_env, view_of=Host, run_mirror=None, exec_=os.execvpe, say=print) -> int:
    root = a.private_root
    if not os.path.isabs(root) or not os.path.isdir(root):
        say(f"owner_only: REFUSED the private root {root!r} is not an existing absolute directory")
        return 2
    if not a.session:
        say("owner_only: REFUSED no session command after `--`")
        return 2
    if (a.token_fd is None) == (not a.skip_mirror):
        say("owner_only: REFUSED give exactly one of --token-fd (the mirror reads GitHub first) and --skip-mirror")
        return 2
    try:
        env = session_env(root, a.model_env, parent_env)
    except ValueError as e:
        say(f"owner_only: REFUSED {e}")
        return 2
    prepare(root, a.owner_identity, a.deploy_key)

    def refused(stage: str) -> bool:
        lines = probe(view_of(env), root)
        for ln in lines:
            say(f"owner_only: REFUSED ({stage}) {ln}")
        return bool(lines)

    if refused("before the mirror"):
        return 1
    if a.skip_mirror:
        if not os.path.isfile(os.path.join(root, MANIFEST)):
            say(f"owner_only: REFUSED --skip-mirror and no {os.path.join(root, MANIFEST)}")
            return 1
    else:
        rc = (run_mirror or _run_mirror)(root, a.token_fd, env)
        if rc != 0:
            say(f"owner_only: REFUSED the corpus mirror exited {rc}; no session started")
            return 1
    if refused("before the session"):
        return 1
    say(f"owner_only: starting the session as an owner-only seat, private root {root}")
    exec_(a.session[0], a.session, env)
    return 0


def _run_mirror(root: str, token_fd: int, env: dict) -> int:
    """The mirror holds the read credential on a descriptor; the descriptor is closed before the session starts."""
    try:
        return subprocess.run([sys.executable, "-I", str(MIRROR), "run", "--private-root", root, "--token-fd", str(token_fd)],
                              env=env, pass_fds=(token_fd,)).returncode
    finally:
        try:
            os.close(token_fd)
        except OSError:
            pass


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test(Path(__file__), mutants="--no-mutants" not in argv)
    session = []
    if "--" in argv:
        k = argv.index("--")
        argv, session = argv[:k], argv[k + 1:]
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("cmd", choices=["launch", "probe"])
    ap.add_argument("--private-root", required=True)
    ap.add_argument("--owner-identity", action="append", default=[])
    ap.add_argument("--deploy-key", action="append", default=[])
    ap.add_argument("--model-env", default="")
    ap.add_argument("--token-fd", type=int)
    ap.add_argument("--skip-mirror", action="store_true")
    a = ap.parse_args(argv)
    a.session = session
    if a.cmd == "probe":
        lines = probe(Host(), a.private_root)
        for ln in lines:
            print(f"owner_only: REFUSED {ln}")
        if not lines:
            print("owner_only: probe OK")
        return 1 if lines else 0
    if not a.owner_identity:
        print("owner_only: REFUSED --owner-identity names the directory the App keys live in, so the probe can prove it unreadable")
        return 2
    return launch(a, dict(os.environ))


SELF_TEST_MARK = "# ---" + "--- self-test: mutants edit only the code above this line"
# ------ self-test: mutants edit only the code above this line


class Fixture(Host):
    """A view of an account as the probe must find it; each case perturbs one fact."""

    def __init__(self, root: str, env=None):
        self.root = root
        self.env = dict(env or {})
        self.modes = {root: 0o700}
        self.dirs = {os.path.join(root, "identity"): []}
        self.files: set[str] = set()
        self.work_tree = False
        self.credential = ""
        self.ghs = [(os.path.join(root, "bin", "gh"), True)]
        self.logins: set[str] = set()
        self.ran: list[list[str]] = []

    def mode(self, path):
        return self.modes.get(path)

    def listing(self, path):
        return self.dirs.get(path)

    def readable(self, path):
        return path in self.files

    def run(self, argv, stdin="", env=None):
        self.ran.append(list(argv))
        if argv[:1] == ["git"] and "rev-parse" in argv:
            return (0, "true\n") if self.work_tree else (128, "")
        if argv[:3] == ["git", "credential", "fill"]:
            return 0, stdin.strip() + ("\n" + self.credential if self.credential else "") + "\n"
        if argv[1:] == ["auth", "status"]:
            return (0, "") if argv[0] in self.logins else (1, "")
        return 127, ""

    def gh_on_path(self):
        return list(self.ghs)


def cases(m) -> dict[str, bool]:
    import secrets
    import tempfile
    r: dict[str, bool] = {}
    secret = secrets.token_hex(12)
    with tempfile.TemporaryDirectory() as td:
        root = os.path.join(td, "private")
        os.mkdir(root, 0o700)
        owner_id, deploy = os.path.join(td, "owner", ".zcode"), os.path.join(td, "owner", "stamp_key")
        m.prepare(root, [owner_id], [deploy])
        env = m.session_env(root, "MODEL_KEY", {"MODEL_KEY": "k", "GH_TOKEN": secret, "SSH_AUTH_SOCK": "/s", "HOME": "/owner",
                                                 "PATH": "/owner/bin", "HPO_IDENTITY_DIR": owner_id, "AWS_SECRET": secret})

        def view(**change):
            v = Fixture(root, env)
            for k, val in change.items():
                setattr(v, k, val)
            return v

        def lines(**change):
            return m.probe(view(**change), root)

        r["probe null: the account the launcher builds is refused nothing"] = lines() == []
        r["env: the session inherits nothing but the named model credential"] = \
            sorted(env) == ["HOME", "HPO_IDENTITY_DIR", "HPO_OWNER_ONLY", "HPO_PRIVATE_ROOT", "HPO_STATE_DIR", "LANG", "MODEL_KEY", "PATH"] \
            and secret not in json.dumps(env) and env["HOME"] == os.path.join(root, "home") \
            and env["HPO_IDENTITY_DIR"] == os.path.join(root, "identity") and env["PATH"].split(":")[0] == os.path.join(root, "bin") \
            and "/owner" not in env["PATH"]

        def refused_env(name, parent):
            try:
                m.session_env(root, name, parent)
            except ValueError:
                return True
            return False
        r["env: a token variable, an allow-list name, an unset name or a malformed one is no model credential"] = \
            all(refused_env(n, {n: "x"}) for n in ("GH_TOKEN", "GITHUB_TOKEN", "HOME", "PATH", "lower", "A B")) \
            and refused_env("MODEL_KEY", {}) and not refused_env("MODEL_KEY", {"MODEL_KEY": "k"})
        r["prepare: the root's files are owner-only, the shim is installed as gh, and probe.json holds the owner's paths"] = \
            all(stat.S_IMODE(os.stat(os.path.join(root, s)).st_mode) == 0o700 for s in ("home", "identity", "state", "bin", "bin/gh")) \
            and stat.S_IMODE(os.stat(os.path.join(root, m.PROBE_FILE)).st_mode) == 0o600 \
            and Path(root, "bin", "gh").read_text().splitlines()[1] == m.SHIM_MARKER \
            and json.loads(Path(root, m.PROBE_FILE).read_text()) == {"identity_dirs": [owner_id], "deploy_keys": [deploy]}
        one = lambda got, word: len(got) == 1 and word in got[0] and secret not in got[0]  # noqa: E731
        r["probe: a readable identity directory is refused by its path"] = one(lines(dirs={os.path.join(root, "identity"): [], owner_id: ["hpo-author.pem"]}), owner_id)
        r["probe: an unlistable identity directory whose key file is readable by name is refused"] = \
            one(lines(files={os.path.join(owner_id, "identity-approver.pem")}), owner_id) \
            and one(lines(files={os.path.join(owner_id, "hpo-author.appid.txt")}), owner_id)
        r["probe: a readable deploy key is refused by its path"] = one(lines(files={deploy}), deploy)
        r["probe: a git credential for the origin host is refused, and its value is not printed"] = \
            one(lines(credential="username=x\npassword=" + secret), "git credential fill")
        r["probe null: a credential helper that answers no password is not one"] = lines(credential="username=x") == []
        r["probe: an agent socket is refused"] = one(m.probe(Fixture(root, {**env, "SSH_AUTH_SOCK": "/run/agent.sock"}), root), "SSH_AUTH_SOCK")
        home = env["HOME"]
        r["probe: a private key, or a gh login file, under the home is refused by its path"] = \
            one(lines(dirs={os.path.join(root, "identity"): [], os.path.join(home, ".ssh"): ["id_ed25519", "known_hosts", "id_ed25519.pub"]}), "id_ed25519") \
            and one(lines(dirs={os.path.join(root, "identity"): [], os.path.join(home, ".config/gh"): ["hosts.yml"]}), "hosts.yml")
        r["probe null: a known_hosts and a public key under the home are not credentials"] = \
            lines(dirs={os.path.join(root, "identity"): [], os.path.join(home, ".ssh"): ["known_hosts", "id_ed25519.pub"]}) == []
        for name in ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_APP_INSTALL_TOKEN", "HPO_PUSH_URL"):
            r[f"probe: the token variable {name} is refused by name, never by value"] = \
                one(m.probe(Fixture(root, {**env, name: secret}), root), name)
        r["probe null: an empty token variable and the model credential are not refused"] = \
            m.probe(Fixture(root, {**env, "GH_TOKEN": "", "TOKENIZER": "x"}), root) == []
        for name in ("CLAUDE_CODE_REMOTE", "CCR_SESSION_PROFILE"):
            r[f"probe: a cloud session is refused ({name})"] = one(m.probe(Fixture(root, {**env, name: "1"}), root), "cloud session")
        r["probe: a gh that is not the shim first on PATH is refused"] = \
            one(lines(ghs=[("/usr/bin/gh", False), (os.path.join(root, "bin", "gh"), True)]), "not the seat shim") \
            and one(lines(ghs=[]), "not the seat shim")
        r["probe: a real gh behind the shim that reports a login is refused by its path"] = \
            one(lines(ghs=[(os.path.join(root, "bin", "gh"), True), ("/usr/bin/gh", False)], logins={"/usr/bin/gh"}), "/usr/bin/gh")
        r["probe null: a real gh behind the shim with no login passes, and the shim itself is never asked"] = \
            lines(ghs=[(os.path.join(root, "bin", "gh"), True), ("/usr/bin/gh", False)]) == [] \
            and [os.path.join(root, "bin", "gh"), "auth", "status"] not in (lambda v: (m.probe(v, root), v.ran)[1])(view(logins={os.path.join(root, "bin", "gh")}))
        no_mode = {k: v for k, v in env.items() if k != "HPO_OWNER_ONLY"}
        r["probe: HPO_OWNER_ONLY unset is refused"] = one(m.probe(Fixture(root, no_mode), root), "HPO_OWNER_ONLY")
        r["probe: a private root that is not mode 700, absent, or inside a work tree is refused"] = \
            one(lines(modes={root: 0o755}), "mode 755") and one(lines(modes={}), "absent") and one(lines(work_tree=True), "work tree")
        r["probe: a relative private root is refused before anything is read"] = one(m.probe(view(), "private"), "not an absolute path")
        r["probe: an identity directory that is unset, outside the root, absent or not empty is refused"] = \
            all(one(got, "HPO_IDENTITY_DIR") for got in (
                m.probe(Fixture(root, {k: v for k, v in env.items() if k != "HPO_IDENTITY_DIR"}), root),
                (lambda v: (v.dirs.update({owner_id + "x": []}), m.probe(v, root))[1])(Fixture(root, {**env, "HPO_IDENTITY_DIR": owner_id + "x"})),
                lines(dirs={}), lines(dirs={os.path.join(root, "identity"): ["hpo-author.pem"]})))
        r["probe: a home outside the private root is refused"] = one(m.probe(Fixture(root, {**env, "HOME": td}), root), "HOME")
        os.rename(os.path.join(root, m.PROBE_FILE), os.path.join(root, "gone"))
        r["probe: a root the launcher did not prepare (no probe.json) is refused"] = one(lines(), m.PROBE_FILE)
        os.rename(os.path.join(root, "gone"), os.path.join(root, m.PROBE_FILE))
        Path(root, m.PROBE_FILE).write_text(json.dumps({"identity_dirs": [], "deploy_keys": []}))
        r["probe: a probe.json naming no identity directory proves nothing and is refused"] = one(lines(), "names no owner identity")
        m.prepare(root, [owner_id], [deploy])

        # launch, with the mirror, the view and the exec injected: the order is the property.
        def run_launch(view_change=None, mirror_rc=0, **over):
            trace, said = [], []
            a = argparse.Namespace(private_root=root, owner_identity=[owner_id], deploy_key=[deploy], model_env="MODEL_KEY",
                                   token_fd=7, skip_mirror=False, session=["session", "--flag"])
            for k, val in over.items():
                setattr(a, k, val)

            def view_of(e):
                trace.append("probe")
                v = Fixture(root, e)
                for k, val in (view_change or {}).items():
                    setattr(v, k, val)
                return v

            def mirror(rt, fd, e):
                trace.append(("mirror", fd, sorted(e)))
                return mirror_rc

            def exec_(prog, argv_, e):
                trace.append(("exec", prog, list(argv_), dict(e)))
            rc = m.launch(a, {"MODEL_KEY": "k", "GH_TOKEN": secret, "HOME": "/owner", "PATH": "/owner/bin"}, view_of, mirror, exec_, said.append)
            return rc, trace, "\n".join(said)

        rc, trace, said = run_launch()
        r["launch: probe, mirror with the descriptor, probe again, then the session under the allow-listed environment"] = \
            rc == 0 and [t if isinstance(t, str) else t[0] for t in trace] == ["probe", "mirror", "probe", "exec"] \
            and trace[1][1] == 7 and trace[3][1:3] == ("session", ["session", "--flag"]) and trace[3][3] == env \
            and "GH_TOKEN" not in trace[3][3] and secret not in said
        rc, trace, said = run_launch(view_change={"files": {deploy}})
        r["launch: a red probe starts neither the mirror nor the session"] = rc == 1 and trace == ["probe"] and "REFUSED" in said
        rc, trace, said = run_launch(mirror_rc=3)
        r["launch: a mirror that fails starts no session"] = rc == 1 and [t if isinstance(t, str) else t[0] for t in trace] == ["probe", "mirror"]
        rc, trace, said = run_launch(token_fd=None, skip_mirror=True)
        r["launch: --skip-mirror with no corpus manifest starts no session"] = rc == 1 and trace == ["probe"]
        os.makedirs(os.path.join(root, "corpus"), exist_ok=True)
        Path(root, m.MANIFEST).write_text("{}")
        rc, trace, said = run_launch(token_fd=None, skip_mirror=True)
        r["launch null: --skip-mirror over an existing manifest runs no mirror and starts the session"] = \
            rc == 0 and [t if isinstance(t, str) else t[0] for t in trace] == ["probe", "probe", "exec"]
        r["launch: both or neither of --token-fd and --skip-mirror, no session command, or a root that does not exist is refused before any probe"] = \
            all(run_launch(**o)[:2] == (2, []) for o in ({"skip_mirror": True}, {"token_fd": None}, {"session": []},
                                                         {"private_root": os.path.join(td, "absent")}, {"model_env": "GH_TOKEN"}))
    return r


#: (needle, replacement, the case that must fail). One per predicate.
MUTANTS = {
    "root mode": ("if mode != 0o700:", "if mode is None:", "not mode 700"),
    "work tree": ('rev-parse", "--is-inside-work-tree"])[0] == 0:', 'rev-parse", "--is-inside-work-tree"])[0] == 99:', "inside a work tree"),
    "probe file": ('        return why + [f"{os.path.join(root, PROBE_FILE)} is absent or unreadable: only `owner_only.py launch` starts this session"]',
                   '        identity_dirs, deploy_keys = ["/x"], []', "no probe.json"),
    "no identity named": ("    if not identity_dirs:\n", "    if False:\n", "naming no identity directory"),
    "identity dir": ("        if identity_reach(view, d):\n", "        if False:\n", "readable identity directory"),
    "identity by name": ("    return any(view.readable(os.path.join(directory, name)) for name in IDENTITY_FILES)", "    return False", "readable by name"),
    "deploy key": ("        if view.readable(k):\n", "        if False:\n", "readable deploy key"),
    "identity env": ("if not idir or not under(idir, root) or view.listing(idir) != []:", "if not idir:", "outside the root, absent or not empty"),
    "home": ("    if not home or not under(home, root):\n", "    if not home:\n", "home outside the private root"),
    "credential": ('if rc == 0 and re.search(r"^password=.", out, re.M):', "if False:", "git credential for the origin host"),
    "agent": ('    if env.get("SSH_AUTH_SOCK"):\n', "    if False:\n", "agent socket"),
    "home keys": ('if sub == ".config/gh" or PRIVATE_KEY_NAMES.fullmatch(name):', "if False:", "under the home is refused"),
    "public key": ('PRIVATE_KEY_NAMES = re.compile(r"id_[a-z0-9_]+|.*\\.pem|.*_key")', 'PRIVATE_KEY_NAMES = re.compile(r"id_.*|.*\\.pem|.*_key|known_hosts")', "public key under the home"),
    "token var": ("        if TOKEN_VAR.fullmatch(name) and env[name]:\n", "        if False:\n", "token variable GH_TOKEN"),
    "push url": ("|GH_ENTERPRISE_TOKEN|GITHUB_PAT|HPO_PUSH_URL", "|GH_ENTERPRISE_TOKEN|GITHUB_PAT", "HPO_PUSH_URL"),
    "cloud": ("        if CLOUD_VAR.fullmatch(name):\n", "        if False:\n", "cloud session is refused (CCR_"),
    "shim first": ("    if not ghs or not ghs[0][1]:\n", "    if not ghs:\n", "not the shim first on PATH"),
    "mode var": ('    if not env.get("HPO_OWNER_ONLY"):\n', "    if False:\n", "HPO_OWNER_ONLY unset"),
    "gh login": ('if not is_shim and view.run([path, "auth", "status"])[0] == 0:', "if False:", "reports a login"),
    "shim not asked": ('if not is_shim and view.run([path, "auth", "status"])[0] == 0:', 'if view.run([path, "auth", "status"])[0] == 0:', "shim itself is never asked"),
    "inherit": ('    env[model_env] = parent[model_env]\n', '    env[model_env] = parent[model_env]\n    env.update({k: v for k, v in parent.items() if k not in env})\n', "inherits nothing"),
    "model name": ("if model_env in env or TOKEN_VAR.fullmatch(model_env) or not", "if not", "is no model credential"),
    "first probe": ('    if refused("before the mirror"):\n        return 1\n', "", "red probe starts neither"),
    "second probe": ('    if refused("before the session"):\n        return 1\n', "", "probe, mirror with the descriptor, probe again"),
    "mirror rc": ("        if rc != 0:\n", "        if False:\n", "mirror that fails"),
    "manifest": ("        if not os.path.isfile(os.path.join(root, MANIFEST)):\n", "        if False:\n", "no corpus manifest"),
    "one of": ("    if (a.token_fd is None) == (not a.skip_mirror):\n", "    if False:\n", "both or neither"),
    "umask": ("    old = os.umask(0o077)\n", "    old = os.umask(0o022)\n", "owner-only, the shim is installed"),
}


def self_test(path: Path, mutants: bool = True) -> int:
    import importlib.util
    import shutil
    import tempfile
    bad = []

    def load(p: Path):
        spec = importlib.util.spec_from_file_location("owner_only_under_test", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    for name, ok in cases(load(path)).items():
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            bad.append(name)
    if mutants:
        code, sep, tail = path.read_text().partition(SELF_TEST_MARK)
        for name, (old, new, case) in MUTANTS.items():
            if code.count(old) != 1:
                print(f"FAIL mutant {name}: needle found {code.count(old)} times in the code")
                bad.append("mutant " + name)
                continue
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / "shims").mkdir()
                shutil.copy(SHIM, Path(td) / "shims" / "seat-gh")
                mp = Path(td) / path.name
                mp.write_text(code.replace(old, new) + sep + tail)
                p = subprocess.run([sys.executable, "-I", str(mp), "--self-test", "--no-mutants"],
                                   capture_output=True, text=True, timeout=120)
            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
            if not killed:
                bad.append("mutant " + name)
    print("owner_only self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
