#!/usr/bin/env python3
"""The one way a tracked script builds a throwaway git repository.

    from throwaway_git import throwaway_git_clone, throwaway_git_env, throwaway_git_init
    env = throwaway_git_init(path, "-q", "-b", "main")   # git init, in path
    subprocess.run(["git", "commit", ...], cwd=path, env=env)
    env = throwaway_git_clone(src, dest, "-q", "--bare")  # git clone, the same two layers

    python3 -I tests/throwaway_git.py --check [--ref <commit>]
    python3 -I tests/throwaway_git.py --self-test

WHY THIS EXISTS (R9-RCA-stamp-race, decision of tvofi 2026-10-08). Git >= 2.54
detaches an auto-maintenance repack after a commit or merge once two loose
objects share the objects/17 shard, so any tiny repository can start one. It
keeps writing into .git/objects/pack while the caller removes the temporary
directory, and the removal fails with `Directory not empty`: a red check that
no diff caused. The suite built about forty such repositories, each with its
own copy of an identity and of what config it shut out. This module is the
shared copy, and `tests/throwaway_git.sh` is its shell twin.

WHAT IT SETS, and how. Two layers, because a site does not control every git
call made in its repository (a production tool the test drives runs its own):

  env    `throwaway_git_env()`: os.environ less every repository-local variable
         git names (`git rev-parse --local-env-vars`: GIT_DIR, GIT_INDEX_FILE,
         GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT, ...) and every inherited
         GIT_CONFIG_KEY_*/GIT_CONFIG_VALUE_*; then a fixed identity, no
         global or system config, and `maintenance.auto=false` plus
         `gc.auto=0` through GIT_CONFIG_COUNT. GIT_CONFIG_PARAMETERS is DROPPED,
         not overridden: git reads it after GIT_CONFIG_COUNT, so an inherited
         `-c maintenance.auto=true` would win over the value set here (the
         #2051 review, measured under git 2.55.0).
  local  `throwaway_git_init()` writes the same two keys into the new
         repository's own config (`throwaway_git_clone()` through `clone -c`), so a git call made WITHOUT this environment
         -- the tool under test -- still reads auto-maintenance as off. The
         one thing that beats it is command-scope config in that caller's own
         environment (GIT_CONFIG_PARAMETERS / GIT_CONFIG_COUNT), which only the
         env layer can remove.

`maintenance.auto=false` is the key git consults before it spawns
auto-maintenance at all (run-command.c prepare_auto_maintenance); `gc.auto=0`
is the fallback it reads while that key is unset, kept as a belt for a git
that predates the first.

THE CHECK (`--check`) refuses a raw `git init` or `git clone` in a tracked
script: every throwaway repository goes through `throwaway_git_init` or
`throwaway_git_clone`, here or in the shell twin. A clone line that itself
carries `maintenance.auto=false` (a `-c` on the clone, which writes it into
the new repository's config) is accepted: it is the local layer, for a
language with no twin.

WHAT IT SCANS, at <ref> through `git grep`: the `.sh .py .mjs .js .cjs` files
under `tools/`, `tests/`, `.claude/` and `dev/audit/harnesses/`, less the round
evidence still kept under `tools/audit/round<n>/`: the instruments a later
seat reruns, and not the records of where things were.

A SITE is a line, not a comment line, that
  - names `git` (any case, as a word, so `"$GIT"` counts) followed later by
    the word `init`;
  - names `git` followed by `clone` as its subcommand, after any global
    options: `git clone`, `"$GIT" clone`, `git -C <dir> clone`,
    `git --no-pager clone`;
  - has the string literal `"clone"` as an argument, followed by `,` or `]`:
    an argv list in any position or with any options, `g(d, "clone", ...)`,
    `execFileSync('git', ['clone', ...])`;
  - or has the string literal `"init"` followed by an init option (`"-q"`,
    `"-b"`, `"--bare"`, ...), the shape of a runner such as
    `g(d, "init", "-q")` that never spells `git`. A bare quoted `"init"` is
    also a config-flow step name, so it alone is not a site.
ALLOW below excuses an exact (file, text) pair with its reason, and an entry
that matches nothing is itself refused.

WHAT IT DOES NOT CATCH: a runner called with `"init"` and no option
(`g("init")`); a git binary held in a variable whose name does not contain
`git` (`"$BIN" clone`, `"$X" init`); a `git worktree add` (it shares its
parent's object store, so its maintenance runs there, not in the temporary
directory); a command assembled across lines; and any repository built
outside the scope above (the round evidence and dev/archive/ are records, not
reruns). Review owns the rest.
"""

from __future__ import annotations

import contextlib
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = "tests/throwaway_git.py"
SHELL_TWIN = "tests/throwaway_git.sh"

IDENTITY = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
#: (key, value) set both through the environment and in the repository's config.
CONFIG = (("maintenance.auto", "false"), ("gc.auto", "0"))
#: `git rev-parse --local-env-vars` at git 2.55.0, plus GIT_INTERNAL_SUPER_PREFIX
#: from older gits: what git itself treats as belonging to one repository.
LOCAL_ENV = ("GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS",
             "GIT_CONFIG_COUNT", "GIT_OBJECT_DIRECTORY", "GIT_DIR", "GIT_WORK_TREE",
             "GIT_IMPLICIT_WORK_TREE", "GIT_GRAFT_FILE", "GIT_INDEX_FILE",
             "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_PREFIX",
             "GIT_INTERNAL_SUPER_PREFIX", "GIT_SHALLOW_FILE", "GIT_COMMON_DIR")
_INHERITED_PAIR = re.compile(r"GIT_CONFIG_(?:KEY|VALUE)_")


def throwaway_git_env(base: dict | None = None) -> dict:
    """The environment for every git call into a throwaway repository."""
    env = {k: v for k, v in (os.environ if base is None else base).items()
           if k not in LOCAL_ENV and not _INHERITED_PAIR.match(k)}
    env.update(IDENTITY, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_COUNT=str(len(CONFIG)))
    for i, (key, value) in enumerate(CONFIG):
        env[f"GIT_CONFIG_KEY_{i}"], env[f"GIT_CONFIG_VALUE_{i}"] = key, value
    return env


@contextlib.contextmanager
def throwaway_git_environ():
    """os.environ replaced by throwaway_git_env() for the block, then restored:
    for a self-test whose every git call -- its own runner's and the
    production code's under test -- works in throwaway repositories. A call
    that passes no env= then inherits the env layer too, which the repository
    layer alone cannot replace: an inherited GIT_CONFIG_PARAMETERS outranks a
    repository's own config (the #2054 review, round 1)."""
    saved = dict(os.environ)
    os.environ.clear()
    os.environ.update(throwaway_git_env(saved))
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


def throwaway_git_init(path, *init_args: str, git=("git",)) -> dict:
    """`git init <init_args>` run IN `path` (created if missing; never an argv
    path, which a closure recording would attribute to this repository), then
    the two keys written into its own config. Returns throwaway_git_env()."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    env = throwaway_git_env()
    subprocess.run([*git, "init", *init_args], cwd=path, env=env, check=True, capture_output=True)
    for key, value in CONFIG:
        subprocess.run([*git, "config", key, value], cwd=path, env=env, check=True, capture_output=True)
    return env


def throwaway_git_clone(src, dest, *clone_args: str, git=("git",), cwd=None) -> dict:
    """`git clone -c <both keys> <clone_args> <src> <dest>` under
    throwaway_git_env(); `clone -c` writes the keys into the new repository's
    own config. Returns throwaway_git_env()."""
    env = throwaway_git_env()
    config = [a for key, value in CONFIG for a in ("-c", f"{key}={value}")]
    subprocess.run([*git, "clone", *config, *clone_args, str(src), str(dest)], cwd=cwd, env=env,
                   check=True, capture_output=True)
    return env


# ---------------------------------------------------------------------------
# The check: no raw `git init` in a tracked script.

_SITE = (re.compile(r"(?i:\bgit\b).*\binit\b"),
         re.compile(r"(?i:\bgit\b)[\"'}]?(?:\s+(?:-[Cc]\s+\S+|--?[A-Za-z][\w-]*(?:=\S+)?))*\s+clone\b"),
         re.compile(r"[\"']clone[\"']\s*[,\]]"),
         re.compile(r"[\"']init[\"']\s*,\s*[\"'](?:-q|--quiet|-b|--bare|--initial-branch|--template"
                    r"|--object-format)"))
_LOCAL_LAYER_INLINE = "maintenance.auto=false"

# (file, text the line must contain, reason). Exact and per file.
ALLOW = (
    (SELF, "", "this file spells the shape in its patterns, docstring and fixtures"),
    (SHELL_TWIN, "git init \"$@\"", "the shell twin's own init, the one the shell sites call"),
)


def scope(path: str) -> bool:
    if re.match(r"tools/audit/round\d+/", path):
        return False
    return bool(re.match(r"(?:tools|tests|\.claude|dev/audit/harnesses)/.*\.(?:sh|py|mjs|js|cjs)$", path))


def is_site(text: str) -> bool:
    s = text.strip()
    if s.startswith(("#", "//")):
        return False
    if re.search(r"\bclone\b", text) and _LOCAL_LAYER_INLINE in text and not re.search(r"\binit\b", text):
        return False  # a clone that writes the local layer itself
    return any(rx.search(text) for rx in _SITE)


def classify(lines, allow=ALLOW) -> tuple[list[str], list[str]]:
    """(refusals, stale allow entries) for (path, line, text) hits."""
    used, bad = set(), []
    for path, n, text in lines:
        if not scope(path) or not is_site(text):
            continue
        hit = [i for i, (f, t, _) in enumerate(allow) if f == path and t in text]
        if hit:
            used.update(hit)
            continue
        bad.append(f"{path}:{n}: {text.strip()[:140]}")
    stale = [f"{f}: {t!r} ({why})" for i, (f, t, why) in enumerate(allow) if i not in used]
    return bad, stale


def grep(ref: str) -> list[tuple[str, int, str]]:
    r = subprocess.run(["git", "grep", "-n", "-I", "-i", "-E", r"init|clone", ref, "--",
                        "tools", "tests", ".claude", "dev/audit/harnesses"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise SystemExit(f"throwaway_git: git grep failed: {r.stderr.strip()}")
    out = []
    for line in r.stdout.splitlines():
        _, path, n, text = line.split(":", 3)  # "<ref>:<path>:<n>:<text>"
        out.append((path, int(n), text))
    return out


def self_test() -> int:
    import tempfile
    passed = failed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}" + (f" -- {detail}" if detail and not cond else ""))

    def one(path: str, text: str, allow=()) -> list[str]:
        return classify([(path, 1, text)], allow)[0]

    py, sh = "tests/x.py", "tools/pr/x.sh"
    for name, path, text in (
            ("a subprocess git init", py, 'subprocess.run(["git", "init", "-q"], cwd=d, check=True)'),
            ("a runner that never spells git", py, 'g(d, "init", "-q", "-b", "trunk")'),
            ("a runner over a command list", py, 'for cmd in (["init", "-q"], ["add", "-A"]):'),
            ("a bare init", py, 'git("init", "-q", "--bare", bare, cwd=root)'),
            ("a shell init", sh, 'git init -q -b main "$R"'),
            ("a shell init through -C", ".claude/hooks/x.sh", 'if git -C "$T" init -q; then'),
            ("a git binary in a variable", sh, '"$GIT" init -q r'),
            ("an init in a dev/audit harness", "dev/audit/harnesses/x.py", 'git("init", "-q")'),
            ("a subprocess clone", py, 'run(["git", "clone", "-q", "--bare", str(seed), str(origin)])'),
            ("a runner clone that never spells git", py, 'g(d, "clone", "-q", str(R), str(L))'),
            ("a shell clone", sh, '(git clone -q --shared . "$CLM/r" && cd "$CLM/r"'),
            ("a JS clone", "tools/policy/x.mjs", "const c = sh('git', ['clone', '-q', '--no-checkout', SRC, dir])"),
            ("a positional list clone (the #2054 review's K2)", py, 'run(["git", "clone", str(origin), str(stale)])'),
            ("a list clone with --depth", py, 'subprocess.run(["git", "clone", "--depth", "1", a, b])'),
            ("execFileSync clone", "tools/policy/x.mjs", "execFileSync('git', ['clone', src, dir])"),
            ("a shell clone through a git variable", sh, '"$GIT" clone -q "$a" "$b"'),
            ("a shell clone after a global option", sh, 'git --no-pager clone -q "$a" "$b"'),
            ("a list clone after -c options", py, 'run(["git", "-c", "x=y", "clone", a, b])')):
        check(f"refused: {name}", one(path, text) != [])
    for name, path, text in (
            ("the helper call", py, 'env = throwaway_git_init(d, "-q", "-b", "trunk")'),
            ("the shell helper call", sh, 'throwaway_git_init "$R" -q -b main'),
            ("a comment naming git init", sh, "  # A box without a working `git init` cannot drive these."),
            ("a config-flow step named init", py, 'shows_menu(result, "init")'),
            ("a dunder init", py, "def __init__(self, git):"),
            ("the clone helper call", py, 'throwaway_git_clone(seed, origin, "-q", "--bare")'),
            ("prose about a clone", "tools/policy/x.mjs", "console.log(`this clone is shallow; git answers`)"),
            ("a directory named clone", sh, 'g() { git -C "$W/clone" -c push.negotiate=false "$@"; }'),
            ("a clone carrying the local layer inline", "tools/policy/x.mjs",
             "sh('git', ['clone', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', '-q', SRC, dir])"),
            ("round evidence", "dev/audit/rounds/round9/x.py", 'git("init", "-q")'),
            ("the archive", "dev/archive/x.py", 'git("init", "-q")')):
        check(f"passes: {name}", one(path, text) == [])
    allow = ((py, "git init", "why"),)
    check("an allow entry excuses only its own file",
          one(py, "git init", allow) == [] and one("tests/y.py", "git init", allow) != [])
    check("an allow entry that matches nothing is reported stale",
          classify([(py, 1, "nothing")], allow)[1] != [] and classify([(py, 1, "git init")], allow)[1] == [])

    # The env layer: a hostile inherited environment, and what survives it.
    hostile = {"PATH": os.environ.get("PATH", ""), "GIT_DIR": "/elsewhere/.git", "GIT_INDEX_FILE": "/x",
               "GIT_CONFIG_PARAMETERS": "'maintenance.auto'='true'", "GIT_CONFIG_COUNT": "3",
               "GIT_CONFIG_KEY_2": "maintenance.auto", "GIT_CONFIG_VALUE_2": "true", "HPO_KEEP": "1"}
    env = throwaway_git_env(hostile)
    check("the env drops every repository-local variable and every inherited config pair",
          not ({"GIT_DIR", "GIT_INDEX_FILE", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_KEY_2"} & set(env)),
          str(sorted(k for k in env if k.startswith("GIT_"))))
    check("the env keeps what is not git's", env.get("HPO_KEEP") == "1")
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "r"
        got_env = throwaway_git_init(repo, "-q")

        def read(key: str, environ: dict) -> str:
            return subprocess.run(["git", "config", "--get", key], cwd=repo, env=environ,
                                  capture_output=True, text=True).stdout.strip()

        check("init returns the env", got_env == throwaway_git_env())
        check("git reads auto-maintenance off, and gc.auto 0, through the env",
              read("maintenance.auto", got_env) == "false" and read("gc.auto", got_env) == "0")
        bare = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        check("a caller WITHOUT the env still reads both off: the repository's own config",
              read("maintenance.auto", bare) == "false" and read("gc.auto", bare) == "0")
        forced = dict(throwaway_git_env(), GIT_CONFIG_PARAMETERS="'maintenance.auto'='true'")
        check("null control: an inherited -c maintenance.auto=true outranks both layers, "
              "which is why the env drops it",
              read("maintenance.auto", forced) == "true")
        check("the env survives the same hostile parameters, once rebuilt from them",
              read("maintenance.auto", throwaway_git_env(forced)) == "false")
        clone = Path(td) / "c.git"
        got_env = throwaway_git_clone(repo, clone, "-q", "--bare")
        r2 = {k: subprocess.run(["git", "config", "--get", k], cwd=clone, env=bare, capture_output=True,
                                text=True).stdout.strip() for k, _ in CONFIG}
        check("a clone writes both keys into its own config, and returns the env",
              r2 == dict(CONFIG) and got_env == throwaway_git_env(), str(r2))
        before = dict(os.environ)
        os.environ["GIT_CONFIG_PARAMETERS"] = "'maintenance.auto'='true'"
        try:
            with throwaway_git_environ():
                inside = dict(os.environ)
                no_env = subprocess.run(["git", "config", "--get", "maintenance.auto"], cwd=repo,
                                        capture_output=True, text=True).stdout.strip()
            hostile_after = os.environ.get("GIT_CONFIG_PARAMETERS")
        finally:
            os.environ.clear()
            os.environ.update(before)
        check("throwaway_git_environ: a call passing no env= reads auto-maintenance off under an "
              "inherited -c maintenance.auto=true, and os.environ is restored after the block",
              no_env == "false" and "GIT_CONFIG_PARAMETERS" not in inside
              and hostile_after == "'maintenance.auto'='true'", f"no_env={no_env!r}")
        # The shell twin sets the same variables to the same values.
        twin = ROOT / SHELL_TWIN
        r = subprocess.run(["bash", "-c", '. "$1"; throwaway_git_env; env -0', "_", str(twin)],
                           env=hostile, capture_output=True, text=True)
        sh_env = dict(kv.split("=", 1) for kv in r.stdout.split("\0") if "=" in kv)
        mine = {k: v for k, v in throwaway_git_env(hostile).items() if k.startswith("GIT_")}
        theirs = {k: v for k, v in sh_env.items() if k.startswith("GIT_")}
        check("the shell twin's throwaway_git_env sets exactly the same GIT_ variables",
              r.returncode == 0 and mine == theirs, f"py-only {set(mine.items()) - set(theirs.items())}, "
              f"sh-only {set(theirs.items()) - set(mine.items())}")
        r = subprocess.run(["bash", "-c", '. "$1"; throwaway_git_init "$2" -q --bare && '
                            'git -C "$2" config --get maintenance.auto && git -C "$2" config --get gc.auto '
                            '&& test -z "${GIT_CONFIG_GLOBAL:-}"', "_", str(twin), str(Path(td) / "b.git")],
                           env=bare, capture_output=True, text=True)
        check("the shell twin's init writes both keys and leaves the caller's shell untouched",
              r.returncode == 0 and r.stdout.split() == ["false", "0"], r.stdout + r.stderr)
        r = subprocess.run(["bash", "-c", '. "$1"; throwaway_git_clone -q --bare "$2" "$3" && '
                            'git -C "$3" config --get maintenance.auto && git -C "$3" config --get gc.auto '
                            '&& test -z "${GIT_CONFIG_GLOBAL:-}"', "_", str(twin), str(repo), str(Path(td) / "s.git")],
                           env=bare, capture_output=True, text=True)
        check("the shell twin's clone writes both keys and leaves the caller's shell untouched",
              r.returncode == 0 and r.stdout.split() == ["false", "0"], r.stdout + r.stderr)
    print(f"throwaway_git self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] != ["--check"]:
        print(__doc__)
        return 2
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "HEAD"
    bad, stale = classify(grep(ref))
    for b in bad:
        print("REFUSE", b)
    for s in stale:
        print("STALE ALLOW", s)
    print(f"throwaway_git: {len(bad)} raw git init or clone site(s) refused, {len(stale)} stale allow "
          f"entr{'y' if len(stale) == 1 else 'ies'} at {ref}")
    return 1 if bad or stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
