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
    mint_identity reads the App keys) or a deploy key the launcher was told of,
    or was told of one that does not exist: an absent path proves nothing;
  - has HPO_IDENTITY_DIR unset, outside the private root, or not empty, or a
    home outside the private root;
  - gets a password from `git credential fill` for github.com;
  - has an agent socket (SSH_AUTH_SOCK) or a private key under its home;
  - has a variable set whose name is a credential's (CREDENTIAL_WORD: a
    segment ending TOKEN, AUTH, SECRET, KEY, PASS, ..., or one that is PEM,
    PAT or NETRC, singular or plural, or one of TOKEN_VAR), other than
    the one model credential the launcher recorded, or a gh further along PATH
    that reports a login;
  - gets NO ANSWER to a question it asks: git or a gh that cannot be run or
    does not return in time, an exit that is not the command's stated no
    (git: 128 naming no repository, or no username or password to read; gh:
    1 saying it is logged into no host), a path whose state the host does
    not report. Each of the three commands it runs passes only on that no;
  - resolves `gh` to anything but the seat shim, or has HPO_OWNER_ONLY unset;
  - runs in a cloud session.
Each workflow driver runs `probe` again in its Prepare step and throws unless
it exits 0.

WHAT THE PROBE CANNOT SEE: a credential in a file it is not told of and that is
not under the account's home; a credential in a variable whose name says
nothing of it; an owner path mistyped below a directory this account cannot
enter, which reads as closed exactly as the real one does (what is proved
then is that nothing under that directory is reachable); a network route that needs none (an anonymous
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
#: A name segment that says the variable holds a credential. TOKEN_VAR names GitHub's; this names the class,
#: which a list of the tree's own push variables (PUSH_AUTH, tools/pr/merge_main_bot.py) only samples. A
#: segment that ENDS with a word of the first group, or IS one of the second, in the singular or the plural.
#: It errs to refusing: MONKEY, COMPASS and BYPASS end with a word and are refused; unset the variable.
CREDENTIAL_WORD = re.compile(r"(?:.*(?:TOKEN|SECRET|PASSWORD|PASSWD|PASSPHRASE|PASS|CREDENTIAL|AUTH|AUTHORIZATION|KEY|BEARER|COOKIE|JWT)|PAT|PEM|NETRC)S?")
CLOUD_VAR = re.compile(r"CLAUDE_CODE_REMOTE(?:_.*)?|CCR_.*")
PRIVATE_KEY_NAMES = re.compile(r"id_[a-z0-9_]+|.*\.pem|.*_key")
#: The session's PATH after its own bin: the system directories, never the launching user's.
SYSTEM_PATH = "/usr/local/bin:/usr/bin:/bin"
PROBE_FILE = "probe.json"
#: What a path the account must not read is to it. UNKNOWN is the host giving no answer, and refuses.
ABSENT, DENIED, OPEN, UNKNOWN = "absent", "denied", "open", "unknown"
#: git's two answers that are a "no" (LC_ALL=C): any other non-zero exit is no answer.
NOT_A_REPOSITORY = "not a git repository"
NO_CREDENTIAL = re.compile(r"could not read (?:Username|Password)")
#: gh's answer that is a "no": `gh auth status` exits 1 saying this. Exit 1 is also what it answers for a login
#: whose token it could not validate, so the exit alone is no answer.
NO_LOGIN = "not logged into any"
MANIFEST = "corpus/MANIFEST.json"


class Host:
    """What the running account can reach. The self-test substitutes a fixture view."""

    _stat, _access, _listdir = staticmethod(os.stat), staticmethod(os.access), staticmethod(os.listdir)

    def __init__(self, env=None, timeout_s: float = 30):
        self.env = dict(os.environ if env is None else env)
        self.timeout_s = timeout_s

    def mode(self, path: str):
        try:
            return stat.S_IMODE(os.stat(path).st_mode)
        except OSError:
            return None

    def listing(self, path: str):
        """Names in a directory, or None when it cannot be listed."""
        try:
            return sorted(self._listdir(path))
        except OSError:
            return None

    def reach(self, path: str) -> str:
        """ABSENT, DENIED or OPEN; UNKNOWN when the host reports neither that the path is missing nor that it is closed."""
        try:
            self._stat(path)
        except (FileNotFoundError, NotADirectoryError):
            return ABSENT
        except PermissionError:
            return DENIED
        except OSError:
            return UNKNOWN
        return OPEN if self._access(path, os.R_OK) else DENIED

    def run(self, argv, stdin: str = "", env=None):
        """-> (exit, stdout, stderr); the exit is None when the command could not be run or did not return in time."""
        try:
            p = subprocess.run(argv, input=stdin, capture_output=True, text=True, timeout=self.timeout_s,
                               env=self.env if env is None else env)
        except (OSError, subprocess.TimeoutExpired):
            return None, "", ""
        return p.returncode, p.stdout, p.stderr

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


def owner_path_refusal(view, path: str, kind: str, names=()) -> str:
    """Why an owner path proves nothing, or is readable; "" only when it exists and is closed to this account."""
    state = view.reach(path)
    if state == ABSENT:
        return f"the {kind} {path} does not exist: an absent path proves nothing about the owner's keys"
    if state == UNKNOWN:
        return f"the host did not answer whether this account can read the {kind} {path}"
    if state == OPEN or view.listing(path) is not None:
        return f"this account can read the {kind} {path}"
    if any(view.reach(os.path.join(path, name)) == OPEN for name in names):
        return f"this account can read the {kind} {path}"
    return ""


def credential_named(name: str) -> bool:
    """Whether a variable's name says it holds a credential: a GitHub one, or any segment of the class."""
    return bool(TOKEN_VAR.fullmatch(name)) or any(CREDENTIAL_WORD.fullmatch(seg) for seg in re.split(r"[^A-Z0-9]+", name.upper()))


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
    why += work_tree_refusal(view, root)
    try:
        cfg = json.loads(Path(root, PROBE_FILE).read_text())
        identity_dirs, deploy_keys = list(cfg["identity_dirs"]), list(cfg["deploy_keys"])
        model_env = str(cfg.get("model_env") or "")
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return why + [f"{os.path.join(root, PROBE_FILE)} is absent or unreadable: only `owner_only.py launch` starts this session"]
    if not identity_dirs:
        why.append(f"{os.path.join(root, PROBE_FILE)} names no owner identity directory to prove unreadable")
    for kind, paths, names in (("owner identity directory", identity_dirs, IDENTITY_FILES), ("deploy key", deploy_keys, ())):
        for path in paths:
            refusal = owner_path_refusal(view, path, kind, names)
            if refusal:
                why.append(refusal)
    idir = env.get("HPO_IDENTITY_DIR") or ""
    if not idir or not under(idir, root) or view.listing(idir) != []:
        why.append("HPO_IDENTITY_DIR is not an empty directory under the private root")
    home = env.get("HOME") or ""
    if not home or not under(home, root):
        why.append("HOME is not under the private root")
    rc, out, err = view.run(["git", "credential", "fill"], f"protocol=https\nhost={ORIGIN_HOST}\n\n",
                            {**env, "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "true", "SSH_ASKPASS": "true"})
    if rc == 0 and re.search(r"^password=.", out, re.M):
        why.append(f"`git credential fill` answers for {ORIGIN_HOST}")
    elif rc != 0 and not NO_CREDENTIAL.search(err):
        why.append(f"`git credential fill` did not answer for {ORIGIN_HOST} ({unanswered(rc)})")
    if env.get("SSH_AUTH_SOCK"):
        why.append("SSH_AUTH_SOCK names an agent socket")
    for sub in (".ssh", ".zcode", ".config/gh"):
        d = os.path.join(home, sub) if home else ""
        names = view.listing(d) if d else []
        if names is None and view.reach(d) != ABSENT:
            why.append(f"a directory under the home that may hold a credential cannot be listed: {d}")
        for name in names or []:
            if sub == ".config/gh" or PRIVATE_KEY_NAMES.fullmatch(name):
                why.append(f"a credential file is under the home: {os.path.join(d, name)}")
    for name in sorted(env):
        if env[name] and (TOKEN_VAR.fullmatch(name) or (name not in (model_env, "SSH_AUTH_SOCK") and credential_named(name))):
            why.append(f"the credential variable {name} is set")
        if CLOUD_VAR.fullmatch(name):
            why.append(f"this is a cloud session ({name} is set)")
    ghs = view.gh_on_path()
    if not ghs or not ghs[0][1]:
        why.append("the first `gh` on PATH is not the seat shim (tools/audit/seat/shims/seat-gh)")
    if not env.get("HPO_OWNER_ONLY"):
        why.append("HPO_OWNER_ONLY is unset: the shim would pass a write")
    for path, is_shim in ghs:
        if is_shim:
            continue
        rc, out, err = view.run([path, "auth", "status"])
        if rc == 0:
            why.append(f"a gh on PATH reports a login: {path}")
        elif rc != 1 or NO_LOGIN not in out + err:
            why.append(f"a gh on PATH did not answer whether it holds a login: {path} ({unanswered(rc)})")
    return why


def work_tree_refusal(view, root: str) -> list[str]:
    """Why the private root may be inside a work tree; [] only when git says, each time it is asked, that it is in none.

    Asked first with none of git's own variables in the environment: GIT_DIR or GIT_CEILING_DIRECTORIES there
    makes git answer for another place, and the prefix names them all. A file-system boundary does not end the
    search. Asked again as the session's git is configured, where those variables can only add a work tree.
    """
    plain = {k: v for k, v in view.env.items() if not k.startswith("GIT_")}
    for asked in ([plain] if plain == view.env else [plain, view.env]):
        rc, _, err = view.run(["git", "-C", root, "rev-parse", "--is-inside-work-tree"],
                              env={**asked, "LC_ALL": "C", "GIT_DISCOVERY_ACROSS_FILESYSTEM": "1"})
        if rc == 0:
            return [f"the private root {root} is inside a git work tree"]
        if rc != 128 or NOT_A_REPOSITORY not in err:
            return [f"git did not answer whether the private root {root} is inside a work tree ({unanswered(rc)})"]
    return []


def unanswered(rc) -> str:
    return "it could not be run, or did not return in time" if rc is None else f"exit {rc} is neither answer"


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


def prepare(root: str, identity_dirs, deploy_keys, model_env: str = "") -> None:
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
             "deploy_keys": [os.path.abspath(k) for k in deploy_keys], "model_env": model_env}, indent=1) + "\n")
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
    prepare(root, a.owner_identity, a.deploy_key, a.model_env)

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

    def __init__(self, root: str, env=None, closed=()):
        self.root = root
        self.env = dict(env or {})
        self.modes = {root: 0o700}
        self.dirs = {os.path.join(root, "identity"): []}
        self.files: set[str] = set()
        self.states = {path: DENIED for path in closed}   # the owner's paths: there, and closed
        self.work_tree = False
        self.tree_answer = (128, "", "fatal: " + NOT_A_REPOSITORY + " (or any of the parent directories): .git\n")
        self.credential = ""
        self.fill_answer = None   # what `git credential fill` answers instead of a filled description
        self.unrunnable: set[str] = set()   # a gh that cannot be run, or does not return
        self.gh_answers: dict[str, tuple] = {}   # what a gh answers `auth status` instead of saying it holds no login
        self.asked: list[tuple[list[str], dict]] = []   # each question with the environment it was asked in
        self.ghs = [(os.path.join(root, "bin", "gh"), True)]
        self.logins: set[str] = set()
        self.ran: list[list[str]] = []

    def mode(self, path):
        return self.modes.get(path)

    def listing(self, path):
        return self.dirs.get(path)

    def reach(self, path):
        return OPEN if path in self.files else self.states.get(path, ABSENT)

    def run(self, argv, stdin="", env=None):
        self.ran.append(list(argv))
        self.asked.append((list(argv), dict(self.env if env is None else env)))
        if argv[:1] == ["git"] and "rev-parse" in argv:
            return (0, "true\n", "") if self.work_tree else self.tree_answer
        if argv[:3] == ["git", "credential", "fill"]:
            return self.fill_answer or (0, stdin.strip() + ("\n" + self.credential if self.credential else "") + "\n", "")
        if argv[1:] == ["auth", "status"]:
            if argv[0] in self.unrunnable:
                return None, "", ""
            return self.gh_answers.get(argv[0]) or ((0, "", "") if argv[0] in self.logins else (1, "", GH_SAYS_NO))
        return None, "", ""

    def gh_on_path(self):
        return list(self.ghs)


#: gh's own sentence for an account with no login (gh 2.89.0, exit 1, on stderr).
GH_SAYS_NO = "You are not logged into any GitHub hosts. To log in, run: gh auth login\n"
#: The words CREDENTIAL_WORD names: those a segment may END with, and those a segment must EQUAL; each also in its plural.
ENDING = ("TOKEN", "SECRET", "PASSWORD", "PASSWD", "PASSPHRASE", "PASS", "CREDENTIAL", "AUTH", "AUTHORIZATION", "KEY", "BEARER", "COOKIE", "JWT")
WHOLE = ("PAT", "PEM", "NETRC")


def name_corpus() -> tuple[list[str], list[str]]:
    """(names that say credential, names that do not): every word in every position, delimiter, case and gluing."""
    # first the variables this tree's own writers read a credential from (merge_main_bot.py, the workflows' env blocks)
    yes, no = ["PUSH_AUTH", "PUSH_TOKEN", "CLOSURES_PUSH_TOKEN", "HPO_RUNS_PEM", "RUNS_PEM", "HPO_LEDGER_PEM", "HPO_RECORD_PEM", "HPO_APPROVER_PEM"], ["PATH", "HOME", "LANG", "TOKENIZER", "AUTHOR_NAME", "KEYBOARD_LAYOUT", "COMPAT_MODE", "SECRETARY",
                              "HPO_IDENTITY_DIR", "HPO_PRIVATE_ROOT", "HPO_STATE_DIR", "HPO_OWNER_ONLY", "SSH_AUTH_SOCK", "PASSAGE_ID", "STATUS", "ACCESS_MODE"]
    # then the spellings the round-2 review found passing (its ev/repro_probe_r2.txt): plurals, a word glued behind another, five more words
    yes += ["DEPLOYKEY", "SSHKEY", "PRIVATEKEY", "ACCESS_TOKENS", "PUSH_SECRETS", "SIGNING_KEYS", "GH_PASS", "PUSH_BEARER", "SESSION_COOKIE", "PUSH_JWT",
            "PUSH_AUTHORIZATION", "NETRC"]
    for word in ENDING + WHOLE:
        for form in (word, word + "S"):
            for name in [form] + [shape.format(w=form, d=d) for d in ("_", ".", "-") for shape in ("XA{d}{w}", "{w}{d}YB", "XA{d}{w}{d}YB")]:
                yes += [name, name.lower(), name.title()]
            (yes if word in ENDING else no).append("XA" + form)     # glued behind a prefix: GHTOKEN and DEPLOYKEYS are one, COMPAT is not
        no += [word + "X", "XA_" + word + "X", word + "X_YB", word + "SX"]   # the word running on into a longer one
    return sorted(set(yes)), sorted(set(no))


def cases(m) -> dict[str, bool]:
    import secrets
    import shutil
    import tempfile
    r: dict[str, bool] = {}
    secret = secrets.token_hex(12)
    with tempfile.TemporaryDirectory() as td:
        root = os.path.join(td, "private")
        os.mkdir(root, 0o700)
        owner_id, deploy = os.path.join(td, "owner", ".zcode"), os.path.join(td, "owner", "stamp_key")
        m.prepare(root, [owner_id], [deploy], "MODEL_KEY")
        env = m.session_env(root, "MODEL_KEY", {"MODEL_KEY": "k", "GH_TOKEN": secret, "SSH_AUTH_SOCK": "/s", "HOME": "/owner",
                                                 "PATH": "/owner/bin", "HPO_IDENTITY_DIR": owner_id, "AWS_SECRET": secret})

        def fx(e):
            return Fixture(root, e, closed=(owner_id, deploy))

        def view(**change):
            v = fx(env)
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
            and json.loads(Path(root, m.PROBE_FILE).read_text()) == {"identity_dirs": [owner_id], "deploy_keys": [deploy], "model_env": "MODEL_KEY"}
        one = lambda got, word: len(got) == 1 and word in got[0] and secret not in got[0]  # noqa: E731
        idir = os.path.join(root, "identity")
        r["probe: a readable identity directory is refused by its path"] = one(lines(dirs={idir: [], owner_id: ["hpo-author.pem"]}), owner_id)
        r["probe: an identity directory that lists, even empty, is refused: a listing is a read"] = \
            one(lines(dirs={idir: [], owner_id: []}), "can read the owner identity directory " + owner_id)
        r["probe: an owner path the account can open is refused"] = \
            one(lines(states={owner_id: m.OPEN, deploy: m.DENIED}), "can read the owner identity directory " + owner_id)
        r["probe: an owner identity directory or deploy key that does not exist proves nothing and is refused"] = \
            one(lines(states={deploy: m.DENIED}), f"owner identity directory {owner_id} does not exist") \
            and one(lines(states={owner_id: m.DENIED}), f"deploy key {deploy} does not exist")
        r["probe: an owner path whose state the host does not report is refused"] = \
            one(lines(states={owner_id: m.UNKNOWN, deploy: m.DENIED}), "did not answer whether this account can read the owner identity directory") \
            and one(lines(states={owner_id: m.DENIED, deploy: m.UNKNOWN}), "did not answer whether this account can read the deploy key")
        r["probe: an unlistable identity directory whose key file is readable by name is refused"] = \
            one(lines(files={os.path.join(owner_id, "identity-approver.pem")}), owner_id) \
            and one(lines(files={os.path.join(owner_id, "hpo-author.appid.txt")}), owner_id)
        r["probe: a readable deploy key is refused by its path"] = one(lines(files={deploy}), deploy)
        r["probe: a git credential for the origin host is refused, and its value is not printed"] = \
            one(lines(credential="username=x\npassword=" + secret), "git credential fill")
        r["probe null: a credential helper that answers no password is not one"] = lines(credential="username=x") == []
        no_git = (None, "", "")
        r["probe: git that cannot be run, or exits with neither answer, leaves the work-tree question unanswered and is refused"] = \
            all(one(lines(tree_answer=ans), "git did not answer whether the private root") for ans in (
                no_git, (128, "", "fatal: detected dubious ownership in repository\n"), (1, "", ""), (127, "", ""), (129, "", m.NOT_A_REPOSITORY)))
        r["probe: a `git credential fill` that cannot be run, or fails without saying it has no credential, is refused"] = \
            all(one(lines(fill_answer=ans), "`git credential fill` did not answer") for ans in (
                no_git, (128, "", "fatal: credential helper died\n"), (1, "", ""), (127, "", "")))
        r["probe null: git saying it could read no username or password has answered, with no credential"] = \
            lines(fill_answer=(128, "", "fatal: could not read Username for 'https://github.com': terminal prompts disabled\n")) == [] \
            and lines(fill_answer=(128, "", "fatal: could not read Password for 'https://x@github.com': terminal prompts disabled\n")) == []
        r["probe: an agent socket is refused"] = one(m.probe(fx({**env, "SSH_AUTH_SOCK": "/run/agent.sock"}), root), "SSH_AUTH_SOCK")
        home = env["HOME"]
        r["probe: a private key, or a gh login file, under the home is refused by its path"] = \
            one(lines(dirs={os.path.join(root, "identity"): [], os.path.join(home, ".ssh"): ["id_ed25519", "known_hosts", "id_ed25519.pub"]}), "id_ed25519") \
            and one(lines(dirs={os.path.join(root, "identity"): [], os.path.join(home, ".config/gh"): ["hosts.yml"]}), "hosts.yml")
        r["probe: a directory under the home that is there and cannot be listed is refused"] = \
            one(lines(states={owner_id: m.DENIED, deploy: m.DENIED, os.path.join(home, ".ssh"): m.DENIED}), "cannot be listed: " + os.path.join(home, ".ssh"))
        r["probe null: a known_hosts and a public key under the home are not credentials"] = \
            lines(dirs={os.path.join(root, "identity"): [], os.path.join(home, ".ssh"): ["known_hosts", "id_ed25519.pub"]}) == []
        for name in ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_APP_INSTALL_TOKEN", "HPO_PUSH_URL"):
            r[f"probe: the token variable {name} is refused by name, never by value"] = \
                one(m.probe(fx({**env, name: secret}), root), name)
        named, unnamed = name_corpus()
        missed = [n for n in named if not one(m.probe(fx({**env, n: secret}), root), f"the credential variable {n} is set")]
        r["probe: every credential-named variable of the corpus is refused by name (PUSH_AUTH among them)" + (f"; missed {missed}" if missed else "")] = \
            not missed and "PUSH_AUTH" in named and all(any(w.lower() in n.lower() for n in named) for w in ENDING + WHOLE)
        caught = [n for n in unnamed if m.probe(fx({"SSH_AUTH_SOCK": "/s", n: "v", **env}), root) not in ([], ["SSH_AUTH_SOCK names an agent socket"])]
        r["probe null: a name where the word runs on into a longer one, or the launcher's own variables, is not a credential's" + (f"; caught {caught}" if caught else "")] = \
            not caught and len(unnamed) > len(ENDING + WHOLE)
        Path(root, m.PROBE_FILE).write_text(json.dumps({"identity_dirs": [owner_id], "deploy_keys": [deploy]}))
        r["probe: the model credential is exempt only by the launcher's record of its name"] = one(lines(), "the credential variable MODEL_KEY is set")
        Path(root, m.PROBE_FILE).write_text(json.dumps({"identity_dirs": [owner_id], "deploy_keys": [deploy], "model_env": "GH_TOKEN"}))
        r["probe: a GitHub token variable is refused even when the record names it the model credential"] = \
            sorted(m.probe(fx({**env, "GH_TOKEN": secret}), root)) == ["the credential variable GH_TOKEN is set", "the credential variable MODEL_KEY is set"]
        m.prepare(root, [owner_id], [deploy], "MODEL_KEY")
        r["probe null: an empty token variable and the model credential are not refused"] = \
            m.probe(fx({**env, "GH_TOKEN": "", "TOKENIZER": "x"}), root) == []
        for name in ("CLAUDE_CODE_REMOTE", "CCR_SESSION_PROFILE"):
            r[f"probe: a cloud session is refused ({name})"] = one(m.probe(fx({**env, name: "1"}), root), "cloud session")
        r["probe: a gh that is not the shim first on PATH is refused"] = \
            one(lines(ghs=[("/usr/bin/gh", False), (os.path.join(root, "bin", "gh"), True)]), "not the seat shim") \
            and one(lines(ghs=[]), "not the seat shim")
        r["probe: a real gh behind the shim that reports a login is refused by its path"] = \
            one(lines(ghs=[(os.path.join(root, "bin", "gh"), True), ("/usr/bin/gh", False)], logins={"/usr/bin/gh"}), "reports a login: /usr/bin/gh")
        r["probe: a real gh behind the shim that cannot be run, or does not return, is refused by its path"] = \
            one(lines(ghs=[(os.path.join(root, "bin", "gh"), True), ("/usr/bin/gh", False)], unrunnable={"/usr/bin/gh"}), "did not answer whether it holds a login: /usr/bin/gh")
        behind = [(os.path.join(root, "bin", "gh"), True), ("/usr/bin/gh", False)]
        not_a_no = {"exit 1 and silent": (1, "", ""), "exit 1 saying its token is invalid": (1, "", "X Failed to log in to github.com account x (default)\n"),
                    "exit 2": (2, "", ""), "exit 4": (4, "", GH_SAYS_NO), "exit 127": (127, "", "sh: 1: nonexistent: not found\n"),
                    "killed by a signal": (-9, "", ""), "exit 128": (128, "", "")}
        for label, answer in not_a_no.items():
            r[f"probe: a real gh behind the shim that answers {label} has not said it holds no login and is refused by its path"] = \
                one(lines(ghs=behind, gh_answers={"/usr/bin/gh": answer}), "did not answer whether it holds a login: /usr/bin/gh")
        r["probe null: a real gh that says it holds no login, on either stream, passes"] = \
            lines(ghs=behind, gh_answers={"/usr/bin/gh": (1, "", GH_SAYS_NO)}) == [] and lines(ghs=behind, gh_answers={"/usr/bin/gh": (1, GH_SAYS_NO, "")}) == []
        tree_env = lambda v: [e for argv, e in (m.probe(v, root), v.asked)[1] if "rev-parse" in argv]  # noqa: E731
        plain_q, both_q = tree_env(view()), tree_env(fx({**env, "GIT_DIR": "/nowhere", "GIT_CEILING_DIRECTORIES": td}))
        r["probe: the work-tree question is asked with none of git's variables but the two the probe sets, and again as the session's git is configured"] = \
            [sorted(k for k in e if k.startswith("GIT_")) for e in plain_q] == [["GIT_DISCOVERY_ACROSS_FILESYSTEM"]] \
            and [sorted(k for k in e if k.startswith("GIT_")) for e in both_q] == [["GIT_DISCOVERY_ACROSS_FILESYSTEM"], ["GIT_CEILING_DIRECTORIES", "GIT_DIR", "GIT_DISCOVERY_ACROSS_FILESYSTEM"]] \
            and all(e.get("GIT_DISCOVERY_ACROSS_FILESYSTEM") == "1" and e.get("LC_ALL") == "C" for e in plain_q + both_q)

        def second_yes(v):
            v.run = lambda argv, stdin="", env=None, _run=v.run: (0, "true\n", "") if "rev-parse" in argv and "GIT_DIR" in (env or {}) else _run(argv, stdin, env)
            return v
        r["probe: a root that only the session's own git configuration makes a work tree is refused"] = \
            one(m.probe(second_yes(fx({**env, "GIT_DIR": "/elsewhere", "GIT_WORK_TREE": root})), root), "is inside a git work tree")
        r["probe null: a real gh behind the shim with no login passes, and the shim itself is never asked"] = \
            lines(ghs=[(os.path.join(root, "bin", "gh"), True), ("/usr/bin/gh", False)]) == [] \
            and [os.path.join(root, "bin", "gh"), "auth", "status"] not in (lambda v: (m.probe(v, root), v.ran)[1])(view(logins={os.path.join(root, "bin", "gh")}))
        no_mode = {k: v for k, v in env.items() if k != "HPO_OWNER_ONLY"}
        r["probe: HPO_OWNER_ONLY unset is refused"] = one(m.probe(fx(no_mode), root), "HPO_OWNER_ONLY")
        r["probe: a private root that is not mode 700, absent, or inside a work tree is refused"] = \
            one(lines(modes={root: 0o755}), "mode 755") and one(lines(modes={}), "absent") and one(lines(work_tree=True), "is inside a git work tree")
        r["probe: a relative private root is refused before anything is read"] = one(m.probe(view(), "private"), "not an absolute path")
        r["probe: an identity directory that is unset, outside the root, absent or not empty is refused"] = \
            all(one(got, "HPO_IDENTITY_DIR") for got in (
                m.probe(fx({k: v for k, v in env.items() if k != "HPO_IDENTITY_DIR"}), root),
                (lambda v: (v.dirs.update({owner_id + "x": []}), m.probe(v, root))[1])(fx({**env, "HPO_IDENTITY_DIR": owner_id + "x"})),
                lines(dirs={}), lines(dirs={os.path.join(root, "identity"): ["hpo-author.pem"]})))
        r["probe: a home outside the private root is refused"] = one(m.probe(fx({**env, "HOME": td}), root), "HOME")
        os.rename(os.path.join(root, m.PROBE_FILE), os.path.join(root, "gone"))
        r["probe: a root the launcher did not prepare (no probe.json) is refused"] = one(lines(), m.PROBE_FILE)
        os.rename(os.path.join(root, "gone"), os.path.join(root, m.PROBE_FILE))
        Path(root, m.PROBE_FILE).write_text(json.dumps({"identity_dirs": [], "deploy_keys": [], "model_env": "MODEL_KEY"}))
        r["probe: a probe.json naming no identity directory proves nothing and is refused"] = one(lines(), "names no owner identity")
        m.prepare(root, [owner_id], [deploy], "MODEL_KEY")

        # The real Host, over a real directory tree and the real git: the fixture view above cannot show what Host itself answers.
        tools, stalled, broken, empty = (os.path.join(td, d) for d in ("tools", "stalled", "broken", "empty"))
        for d in (tools, stalled, broken, empty):
            os.mkdir(d)
        for prog in ("git", "true"):
            os.symlink(shutil.which(prog), os.path.join(tools, prog))
        Path(stalled, "git").write_text("#!/bin/sh\nexec /bin/sleep 2\n")
        Path(broken, "gh").write_text("#!/nonexistent/interpreter\n")
        for prog in (os.path.join(stalled, "git"), os.path.join(broken, "gh")):
            os.chmod(prog, 0o700)
        os.makedirs(owner_id)
        Path(owner_id, "hpo-author.pem").write_text("synthetic")
        Path(deploy).write_text("synthetic")
        closed = (owner_id, os.path.join(owner_id, "hpo-author.pem"), deploy)
        for path in reversed(closed):
            os.chmod(path, 0)

        class Sealed(m.Host):
            """A CI runner is the owner and the seat at once, and root reads through any mode: where the kernel
            would not refuse the owner's paths, its three refusals are the one thing stood in for."""
            if os.geteuid() == 0:
                _access = staticmethod(lambda path, mode: path not in closed and os.access(path, mode))

                @staticmethod
                def _listdir(path):
                    if path in closed:
                        raise PermissionError(path)
                    return os.listdir(path)

        def host(path=None, timeout_s=30, cls=Sealed, **more):
            e = {**env, "GIT_CONFIG_NOSYSTEM": "1", "PATH": os.path.join(root, "bin") + ":" + (tools if path is None else path), **more}
            return m.probe(cls(e, timeout_s), root)

        every = lambda got, n, word: len(got) == n and all(word in ln for ln in got)  # noqa: E731
        r["host null: a sound account through the real Host and the real git is refused nothing"] = host() == []
        r["host: with no git on PATH both git questions are unanswered and refused"] = \
            sorted(ln.split(" did not answer")[0] for ln in host(path=empty)) == ["`git credential fill`", "git"] \
            and every(host(path=empty), 2, "it could not be run, or did not return in time")
        r["host: a git that does not return in time is refused on both questions"] = \
            every(host(path=stalled, timeout_s=0.3), 2, "it could not be run, or did not return in time")
        r["host: a gh behind the shim that cannot be run is refused"] = \
            one(host(path=tools + ":" + broken), "did not answer whether it holds a login: " + os.path.join(broken, "gh"))
        scripts = {"exit0": "exit 0", "exit1": "exit 1", "exit2": "exit 2", "exit127": "nonexistent-command-of-the-fixture", "signal": "kill -9 $$",
                   "says-no": "echo 'You are not logged into any GitHub hosts. To log in, run: gh auth login' >&2; exit 1"}
        got = {}
        for label, body in scripts.items():
            os.mkdir(os.path.join(td, "gh-" + label))
            Path(td, "gh-" + label, "gh").write_text("#!/bin/sh\n" + body + "\n")
            os.chmod(os.path.join(td, "gh-" + label, "gh"), 0o700)
            got[label] = [ln.split(":")[0] for ln in host(path=tools + ":" + os.path.join(td, "gh-" + label))]
        r["host: a real gh behind the shim passes only by saying it holds no login: exit 0 is a login, and exit 1 unsaid, 2, 127 or a signal is no answer"
          + ("" if got.get("says-no") == [] else f"; got {got}")] = \
            got == {"exit0": ["a gh on PATH reports a login"], "says-no": [], **{k: ["a gh on PATH did not answer whether it holds a login"] for k in ("exit1", "exit2", "exit127", "signal")}}
        tree = os.path.join(td, "tree")
        for sub in (".git/objects", ".git/refs", "private"):   # a work tree by hand: what git's discovery looks for
            os.makedirs(os.path.join(tree, sub))
        Path(tree, ".git", "HEAD").write_text("ref: refs/heads/main\n")
        inner = os.path.join(tree, "private")
        os.chmod(inner, 0o700)
        m.prepare(inner, [owner_id], [deploy], "MODEL_KEY")
        inner_env = m.session_env(inner, "MODEL_KEY", {"MODEL_KEY": "k"})

        def in_tree(**more):
            return m.probe(Sealed({**inner_env, "GIT_CONFIG_NOSYSTEM": "1", "PATH": os.path.join(inner, "bin") + ":" + tools, **more}), inner)
        r["host: a private root inside a work tree is refused, and no variable of git's in the environment hides the tree"
          + ("" if one(in_tree(), "inside") else f"; control {in_tree()}")] = \
            all(one(got_, f"the private root {inner} is inside a git work tree") for got_ in (
                in_tree(), in_tree(GIT_DIR=os.path.join(td, "nowhere")), in_tree(GIT_CEILING_DIRECTORIES=tree),
                in_tree(GIT_DIR=os.path.join(td, "nowhere"), GIT_CEILING_DIRECTORIES=tree, GIT_WORK_TREE=empty)))
        r["host null: the same variables over a root outside every work tree are refused nothing"] = \
            host(GIT_CEILING_DIRECTORIES=tree) == [] and host(GIT_DISCOVERY_ACROSS_FILESYSTEM="0") == []

        def stat_raising(error):
            class Raising(m.Host):
                _stat = staticmethod(lambda path: (_ for _ in ()).throw(error))
            return Raising({})
        import errno
        r["host: reach reads a stat the kernel refuses as denied, and one that fails any other way as no answer"] = \
            (stat_raising(PermissionError(errno.EACCES, "x")).reach(deploy), stat_raising(OSError(errno.EIO, "x")).reach(deploy),
             stat_raising(OSError(errno.ELOOP, "x")).reach(deploy)) == (m.DENIED, m.UNKNOWN, m.UNKNOWN)
        r["host: PUSH_AUTH set in the real environment is refused by name"] = one(host(PUSH_AUTH=secret), "the credential variable PUSH_AUTH is set")
        gone = os.path.join(td, "owner", "absent-typo")
        m.prepare(root, [gone], [gone + "-key"], "MODEL_KEY")
        r["host: owner paths that do not exist are refused, each by its path"] = \
            sorted(host()) == [f"the deploy key {gone}-key does not exist: an absent path proves nothing about the owner's keys",
                               f"the owner identity directory {gone} does not exist: an absent path proves nothing about the owner's keys"]
        m.prepare(root, [owner_id], [deploy], "MODEL_KEY")
        h = m.Host({})
        r["host: reach tells an absent path, one under a file, and an open one apart; a closed one is denied"] = \
            (h.reach(gone), h.reach(os.path.join(root, m.PROBE_FILE, "x")), h.reach(root), Sealed({}).reach(deploy)) == (m.ABSENT, m.ABSENT, m.OPEN, m.DENIED)
        r["host: run reports an exit, both streams, and None for a program that is not there"] = \
            h.run([sys.executable, "-c", "import sys; print('o'); print('e', file=sys.stderr); sys.exit(3)"]) == (3, "o\n", "e\n") \
            and h.run([os.path.join(td, "no-such-program")]) == (None, "", "")
        for path in closed:
            os.chmod(path, 0o700)

        # launch, with the mirror, the view and the exec injected: the order is the property.
        def run_launch(view_change=None, mirror_rc=0, **over):
            trace, said = [], []
            a = argparse.Namespace(private_root=root, owner_identity=[owner_id], deploy_key=[deploy], model_env="MODEL_KEY",
                                   token_fd=7, skip_mirror=False, session=["session", "--flag"])
            for k, val in over.items():
                setattr(a, k, val)

            def view_of(e):
                trace.append("probe")
                v = fx(e)
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
    "work tree": ('        if rc == 0:\n            return [f"the private root {root} is inside a git work tree"]', '        if rc == 99:\n            return [f"the private root {root} is inside a git work tree"]', "inside a work tree"),
    "work tree unanswered": ("        if rc != 128 or NOT_A_REPOSITORY not in err:\n", "        if False:\n", "leaves the work-tree question unanswered"),
    "work tree any 128": ("        if rc != 128 or NOT_A_REPOSITORY not in err:\n", "        if rc != 128:\n", "leaves the work-tree question unanswered"),
    "work tree either half": ("        if rc != 128 or NOT_A_REPOSITORY not in err:\n", "        if rc != 128 and NOT_A_REPOSITORY not in err:\n", "leaves the work-tree question unanswered"),
    "work tree any exit": ("        if rc != 128 or NOT_A_REPOSITORY not in err:\n", "        if rc is None:\n", "leaves the work-tree question unanswered"),
    "git variables out of the question": ('if not k.startswith("GIT_")}', "if True}", "no variable of git's in the environment hides the tree"),
    "git variables, two named": ('if not k.startswith("GIT_")}', 'if k not in ("GIT_DIR", "GIT_WORK_TREE")}', "no variable of git's in the environment hides the tree"),
    "asked without them first": ("    for asked in ([plain] if plain == view.env else [plain, view.env]):\n", "    for asked in [view.env]:\n", "no variable of git's in the environment hides the tree"),
    "asked as configured too": ("    for asked in ([plain] if plain == view.env else [plain, view.env]):\n", "    for asked in [plain]:\n", "only the session's own git configuration"),
    "across file systems": ('"LC_ALL": "C", "GIT_DISCOVERY_ACROSS_FILESYSTEM": "1"}', '"LC_ALL": "C"}', "asked with none of git's variables"),
    "stat denied": ("        except PermissionError:\n            return DENIED\n", "        except PermissionError:\n            return ABSENT\n", "a stat the kernel refuses as denied"),
    "stat unanswered": ("        except OSError:\n            return UNKNOWN\n", "        except OSError:\n            return DENIED\n", "a stat the kernel refuses as denied"),
    "run unanswered": ('            return None, "", ""\n        return p.returncode, p.stdout, p.stderr', '            return 128, "", NOT_A_REPOSITORY + NO_CREDENTIAL.pattern[:14] + "Username"\n        return p.returncode, p.stdout, p.stderr', "with no git on PATH"),
    "run timeout": ("timeout=self.timeout_s,", "timeout=None,", "does not return in time"),
    "run stderr": ("        return p.returncode, p.stdout, p.stderr", '        return p.returncode, p.stdout, ""', "host null"),
    "probe file": ('        return why + [f"{os.path.join(root, PROBE_FILE)} is absent or unreadable: only `owner_only.py launch` starts this session"]',
                   '        identity_dirs, deploy_keys, model_env = ["/x"], [], "MODEL_KEY"', "no probe.json"),
    "no identity named": ("    if not identity_dirs:\n", "    if False:\n", "naming no identity directory"),
    "identity dir": ("            if refusal:\n", "            if False:\n", "readable identity directory"),
    "identity by name": ("    if any(view.reach(os.path.join(path, name)) == OPEN for name in names):\n", "    if False:\n", "readable by name"),
    "deploy key": ('("deploy key", deploy_keys, ())', '("deploy key", [], ())', "readable deploy key"),
    "absent owner path": ("    if state == ABSENT:\n", "    if False:\n", "does not exist proves nothing"),
    "absent owner path, real": ("        except (FileNotFoundError, NotADirectoryError):\n            return ABSENT\n", "        except (FileNotFoundError, NotADirectoryError):\n            return DENIED\n", "owner paths that do not exist"),
    "unreported state": ("    if state == UNKNOWN:\n", "    if False:\n", "whose state the host does not report"),
    "a listing is a read": ("    if state == OPEN or view.listing(path) is not None:\n", "    if state == OPEN or view.listing(path):\n", "that lists, even empty"),
    "open path": ("    if state == OPEN or view.listing(path) is not None:\n", "    if view.listing(path) is not None:\n", "the account can open"),
    "denied is not open": ("        return OPEN if self._access(path, os.R_OK) else DENIED", "        return OPEN", "host null"),
    "identity env": ("if not idir or not under(idir, root) or view.listing(idir) != []:", "if not idir:", "outside the root, absent or not empty"),
    "home": ("    if not home or not under(home, root):\n", "    if not home:\n", "home outside the private root"),
    "credential": ('if rc == 0 and re.search(r"^password=.", out, re.M):', "if False:", "git credential for the origin host"),
    "credential unanswered": ("    elif rc != 0 and not NO_CREDENTIAL.search(err):\n", "    elif False:\n", "fails without saying it has no credential"),
    "credential said no": ("    elif rc != 0 and not NO_CREDENTIAL.search(err):\n", "    elif rc != 0:\n", "saying it could read no username"),
    "credential any exit": ("    elif rc != 0 and not NO_CREDENTIAL.search(err):\n", "    elif rc is None:\n", "fails without saying it has no credential"),
    "home dir unlistable": ("        if names is None and view.reach(d) != ABSENT:\n", "        if False:\n", "there and cannot be listed"),
    "agent": ('    if env.get("SSH_AUTH_SOCK"):\n', "    if False:\n", "agent socket"),
    "home keys": ('if sub == ".config/gh" or PRIVATE_KEY_NAMES.fullmatch(name):', "if False:", "under the home is refused"),
    "public key": ('PRIVATE_KEY_NAMES = re.compile(r"id_[a-z0-9_]+|.*\\.pem|.*_key")', 'PRIVATE_KEY_NAMES = re.compile(r"id_.*|.*\\.pem|.*_key|known_hosts")', "public key under the home"),
    "credential class": (' or (name not in (model_env, "SSH_AUTH_SOCK") and credential_named(name))):', "):", "every credential-named variable"),
    "token var": ("        if env[name] and (TOKEN_VAR.fullmatch(name) or (", "        if env[name] and ((", "even when the record names it"),
    "model exempt": ('(name not in (model_env, "SSH_AUTH_SOCK") and', '(name != "SSH_AUTH_SOCK" and', "probe null: the account the launcher builds"),
    "model by record": ('        model_env = str(cfg.get("model_env") or "")\n', '        model_env = "MODEL_KEY"\n', "exempt only by the launcher's record"),
    "record written": ('"model_env": model_env}', '"model_env": ""}', "probe.json holds the owner's paths"),
    "record passed": ("    prepare(root, a.owner_identity, a.deploy_key, a.model_env)\n", "    prepare(root, a.owner_identity, a.deploy_key)\n", "launch null"),
    "auth word": ("|CREDENTIAL|AUTH|AUTHORIZATION|", "|CREDENTIAL|AUTHORIZATION|", "every credential-named variable"),
    "key ends a segment": ("|AUTHORIZATION|KEY|BEARER|", "|AUTHORIZATION|BEARER|", "every credential-named variable"),
    "plural": (')|PAT|PEM|NETRC)S?")', ')|PAT|PEM|NETRC)")', "every credential-named variable"),
    "whole words stay whole": ("|JWT)|PAT|PEM|NETRC)S?", "|JWT|PAT|PEM|NETRC))S?", "runs on into a longer one"),
    "word ends a segment": ("any(CREDENTIAL_WORD.fullmatch(seg)", "any(CREDENTIAL_WORD.search(seg)", "runs on into a longer one"),
    "segments": ('re.split(r"[^A-Z0-9]+", name.upper())', "[name.upper()]", "every credential-named variable"),
    "any case": ('re.split(r"[^A-Z0-9]+", name.upper())', 're.split(r"[^A-Za-z0-9]+", name)', "every credential-named variable"),
    "push url": ("|GH_ENTERPRISE_TOKEN|GITHUB_PAT|HPO_PUSH_URL", "|GH_ENTERPRISE_TOKEN|GITHUB_PAT", "HPO_PUSH_URL"),
    "cloud": ("        if CLOUD_VAR.fullmatch(name):\n", "        if False:\n", "cloud session is refused (CCR_"),
    "shim first": ("    if not ghs or not ghs[0][1]:\n", "    if not ghs:\n", "not the shim first on PATH"),
    "mode var": ('    if not env.get("HPO_OWNER_ONLY"):\n', "    if False:\n", "HPO_OWNER_ONLY unset"),
    "gh login": ('        if rc == 0:\n            why.append(f"a gh on PATH reports a login: {path}")', '        if False:\n            why.append(f"a gh on PATH reports a login: {path}")', "reports a login"),
    "gh unanswered": ("        elif rc != 1 or NO_LOGIN not in out + err:\n", "        elif False:\n", "cannot be run, or does not return"),
    "gh any exit": ("        elif rc != 1 or NO_LOGIN not in out + err:\n", "        elif rc is None:\n", "answers exit 2 has not said"),
    "gh exit 1 unsaid": ("        elif rc != 1 or NO_LOGIN not in out + err:\n", "        elif rc != 1:\n", "answers exit 1 and silent"),
    "gh said under another exit": ("        elif rc != 1 or NO_LOGIN not in out + err:\n", "        elif NO_LOGIN not in out + err:\n", "answers exit 4 has not said"),
    "gh said on stdout": ("NO_LOGIN not in out + err:", "NO_LOGIN not in err:", "on either stream"),
    "gh real exits": ("        elif rc != 1 or NO_LOGIN not in out + err:\n", "        elif rc is None or rc > 100:\n", "passes only by saying it holds no login"),
    "shim not asked": ("        if is_shim:\n            continue\n", "", "shim itself is never asked"),
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
