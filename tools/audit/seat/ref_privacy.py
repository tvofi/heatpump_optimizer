#!/usr/bin/env python3
"""Name a local path for publication, and refuse a push that would publish the host.

    python3 -I tools/audit/seat/ref_privacy.py slug <path> [--root NAME=DIR]...
    python3 -I tools/audit/seat/ref_privacy.py guard --ref <ref> [--message <text>]...
                                                     [--commits <rev> [-C <dir>]]
    python3 -I tools/audit/seat/ref_privacy.py --check [--ref <commit>]
    python3 -I tools/audit/seat/ref_privacy.py --self-test

WHY THIS EXISTS (#2310). wt_sync.sh named its `wip-sync/<slug>` refs after the
worktree's absolute path with only a `$HOME/` prefix stripped. A worktree
outside the home directory -- a session scratch under the temp root, whose own
name spells the home path with `/` turned to `-` -- kept the account name, and
the uid in the temp root's name, in 70 remote ref names and their snapshot
commit messages. The owner's ruling: it never recurs. This file is the one
owner of that concern, in three parts.

SLUG. `slug(path, roots)` is the only way an instrument turns a local path into
a ref component. A path under a named root (wt_sync.sh names the repository's
main checkout `repo`) is `<name>-<path below it>`; any other path is
`ext-<leaf>-<hash>`, the leaf directory's name and the first 8 hex digits of
the sha256 of the resolved path -- stable for one path, distinct for two
sharing a leaf, and recoverable to a path only by guessing that path whole. The
result is checked like a ref name below; a candidate that leaks falls back to
`ext-<hash>`, so no input yields a leaking slug. Each run of characters outside
`[A-Za-z0-9_]` becomes one `-`, trimmed at both ends: always a valid ref component.

GUARD. `refusal(ref, messages)` returns why a push would publish the host, or
None. Every instrument that composes a ref name or a commit message from a value
it does not fix itself calls it before `git push`; the `guard` subcommand is the
shell callers' form, and `--commits <rev>` adds the message of every commit
under <rev> that no remote-tracking ref already holds -- the ones the push
publishes for the first time. A refusal names its class and where, never the
matched text. The classes, judged against the host's own identity
(`Identity.of_host`: $HOME, its resolved path, the passwd home; $USER, $LOGNAME,
the passwd name, the home's basename; the uid):
  home-directory  a home directory, verbatim (case-folded: macOS paths are);
  account-name    an account name as a whole word -- bounded by characters
                  outside [A-Za-z0-9], so `-Users-<name>-` counts;
  uid             `claude-<uid>`, the session temp root's name;
  scratch-root    `tmp/claude-<digits>`, `/` or `-` separated: ANY host's
                  session temp root, the shape the 70 refs carried;
  host-path       `/Users/<x>` or `/home/<x>`, a macOS per-user temp
                  (`/var/folders/`), or the dash-mangled `Users-<x>` form;
  unpublishable   (ref names and slugs only) a character outside
                  [A-Za-z0-9._/-].
The accounts `root`, `runner` and `user`, and names under three characters, are
not judged: the first three are the fixed accounts of the CI runner and the
cloud seat image (tmp_paths.py's `cloud` rule), public by construction, and a
shorter name would refuse ordinary words.

CHECK. `--check` is the class rule as a standing registry (fixer.md step 8).
It enumerates every tracked file, at <ref> through `git grep`, holding a push
site -- a non-comment line on which `git` (or a `g`/`rgit` wrapper, or a Python
`git`/`g`/`run`/`sh` call) is followed by the word `push`, or a continuation
line opening `push` with a push option, `origin` or a variable -- in `tools/`,
`.claude/workflows/` and `.github/workflows/`, less round evidence and vendored
code. Each such file must have an entry in PUSHERS below: `guarded` (the file
must call this module) or a stated reason it composes nothing a host could leak
into. A file with a site and no entry, a `guarded` entry that does not call this
module, and an entry whose file has no site are each refused, so the registry
cannot rot into an exemption.

WHAT IT DOES NOT CATCH. A push built across lines whose `push` line opens
with neither a push option, `origin` nor a variable; a push through another wrapper name; a guarded
file that gains a second, unguarded push (the registry is keyed on the file:
review owns the site); file CONTENT a push publishes (the guard reads ref names
and messages only); and another machine's account name, unless it sits in a
`/Users/`, `/home/` or `Users-` shape.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SELF = "tools/audit/seat/ref_privacy.py"
PUBLIC_ACCOUNTS = frozenset({"root", "runner", "user"})
MIN_NAME = 3
HASH_HEX = 8

_HOST_PATH = re.compile(
    r"/(?:Users|home)/(?!(?:root|runner|user)(?:/|$|[^A-Za-z0-9._-]))[A-Za-z0-9._-]"
    r"|/var/folders/"
    r"|(?<![A-Za-z0-9])Users-(?!(?:root|runner|user)(?:-|$|[^A-Za-z0-9._]))[A-Za-z0-9._]")
_SCRATCH_ROOT = re.compile(r"tmp[/-]+claude-\d+(?![0-9])")
_REF_CHARS = re.compile(r"^[A-Za-z0-9._/-]+$")
_SLUG_UNSAFE = re.compile(r"[^A-Za-z0-9_]+")


@dataclass(frozen=True)
class Identity:
    homes: tuple[str, ...]
    names: tuple[str, ...]
    uid: int | None

    @staticmethod
    def of_host() -> "Identity":
        homes, names = set(), set()
        for h in (os.environ.get("HOME", ""),):
            if h:
                homes.update({h, os.path.realpath(h)})
        for n in (os.environ.get("USER", ""), os.environ.get("LOGNAME", "")):
            names.add(n)
        uid = None
        if hasattr(os, "getuid"):
            uid = os.getuid()
            try:
                import pwd
                pw = pwd.getpwuid(uid)
                names.add(pw.pw_name)
                homes.add(pw.pw_dir)
            except (ImportError, KeyError):
                pass
        names.update(os.path.basename(h.rstrip("/")) for h in homes)
        return Identity.made(homes, names, uid)

    @staticmethod
    def made(homes, names, uid) -> "Identity":
        hs = tuple(sorted({h.rstrip("/") for h in homes if h and h.rstrip("/")}))
        ns = tuple(sorted({n.casefold() for n in names
                           if len(n) >= MIN_NAME and n.casefold() not in PUBLIC_ACCOUNTS}))
        return Identity(hs, ns, uid)


def leaks(text: str, ident: Identity) -> list[str]:
    """The leak classes `text` carries, in a fixed order, each once."""
    folded, found = text.casefold(), []
    if any(h.casefold() in folded for h in ident.homes):
        found.append("home-directory")
    if any(re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", folded) for n in ident.names):
        found.append("account-name")
    if ident.uid is not None and re.search(rf"(?<![A-Za-z0-9])claude-{ident.uid}(?![0-9])", text):
        found.append("uid")
    if _SCRATCH_ROOT.search(text):
        found.append("scratch-root")
    if _HOST_PATH.search(text):
        found.append("host-path")
    return found


def refusal(ref: str, messages=(), ident: Identity | None = None) -> str | None:
    """Why pushing `ref` with these commit messages would publish the host, or None."""
    ident = ident or Identity.of_host()
    why = leaks(ref, ident)
    if not _REF_CHARS.match(ref):
        why.append("unpublishable")
    if why:
        return f"{', '.join(why)} in the ref name"
    for where, msg in messages:
        why = leaks(msg, ident)
        if why:
            return f"{', '.join(why)} in {where}"
    return None


def slug(path: str, roots=(), ident: Identity | None = None) -> str:
    """A ref component for a local path that names nothing about the host."""
    ident = ident or Identity.of_host()
    real = os.path.realpath(path)

    def clean(s: str) -> str:
        return _SLUG_UNSAFE.sub("-", s).strip("-")

    digest = hashlib.sha256(real.encode()).hexdigest()[:HASH_HEX]
    cand = None
    for name, root in roots:
        rroot = os.path.realpath(root)
        if real == rroot or real.startswith(rroot.rstrip("/") + "/"):
            cand = clean(f"{name}-{real[len(rroot):]}")
            break
    if cand is None:
        cand = clean(f"ext-{os.path.basename(real)}-{digest}")
    if refusal(cand, (), ident) is not None or not cand:
        cand = f"ext-{digest}"
    return cand


def commit_messages(rev: str, cwd: str | None = None) -> list[tuple[str, str]]:
    """(where, message) for every commit under `rev` no remote-tracking ref holds."""
    out = subprocess.run(["git", "log", "--format=%H%x1f%B%x1e", rev, "--not", "--remotes"],
                         cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git log {rev} --not --remotes exited {out.returncode}")
    pairs = []
    for rec in out.stdout.split("\x1e"):
        rec = rec.strip("\n")
        if rec:
            sha, _, msg = rec.partition("\x1f")
            pairs.append((f"the message of {sha[:12]}", msg))
    return pairs


# ---------------------------------------------------------------------------
# The registry: every tracked file with a push site, and its disposition.

GUARDED = "guarded"
PUSHERS = {
    "tools/audit/seat/wt_sync.sh": (GUARDED, "the #2310 instrument: a slug from slug(), both pushes guarded"),
    "tools/audit/seat/body_push.sh": (GUARDED, "ref from the topic argument, message composed from it"),
    "tools/audit/seat/bus.sh": (GUARDED, "_post's ref from family and number, message from the caller; "
                                "its self-test pushes go to a temp bare repository"),
    "tools/audit/seat/state_docs.py": (GUARDED, "message from --message or the regenerated names; "
                                       "its self-test pushes go to a temp bare repository"),
    "tools/audit/seat/roster_edit.py": (GUARDED, "branch and message composed from arguments; "
                                        "its self-test pushes go to a temp bare repository"),
    "tools/pr/app_push.sh": (GUARDED, "every pull request's push: the branch argument and each commit "
                             "the push publishes; its self-test pushes go to a temp bare repository"),
    "tools/pr/push.sh": (GUARDED, "the retired author path (decision 0011) still pushes a branch"),
    "tools/release/stamp.py": (GUARDED, "the stamp commit's message carries the --title argument"),
    "tools/pr/merge_main_bot.py": ("republishes", "pushes a merge onto a pull request's own branch, "
                                   "a name the remote already holds, under the constant SUBJECT"),
    "tools/audit/seat/merge_train.py": ("republishes", "deletes merged branches the remote already "
                                        "holds; its other push is the self-test's stub"),
    ".github/workflows/tests.yml": ("republishes", "on a runner, constant-message bot commits onto the "
                                    "pull request's own branch, record/autofix or main (nightly kills)"),
    "tools/pr/app_approve.sh": ("fixture", "its pushes are the self-test's, into a temp bare repository"),
    "tools/audit/seat/r9_rc_bus_fetchhead.sh": ("fixture", "a regression harness: every push goes to a "
                                                "temp bare repository"),
    "tools/policy/fragments_sync.mjs": ("fixture", "a `git push` string fed to its own lint as a fixture"),
    ".claude/workflows/audit-find.js": ("prompt", "an agent prompt naming handoff/audit-r<round>-... "
                                        "refs from round and box numbers"),
}

_SITE = re.compile(
    r"\b(?:git|rgit)\b.*?(?<![\w.-])push(?![\w-])"
    r"|(?:^|[;&|(]\s*)g\s+push\b"
    r"|^\s*push\s+(?:--(?:force|set-upstream|no-verify|delete|atomic|push-option)|-[fqu]\b|origin\b|\"?\$)"
    r"|\b(?:git|g|run|runner|sh|_git|_rg)\([^)\n]*[\"']push[\"']")
_COMMENT = re.compile(r"^\s*(?:#|//|\*)")
_GUARD_CALL = (re.compile(r"ref_privacy\.py\b"), re.compile(r"\bguard\s+--ref\b"))
_GUARD_PY = re.compile(r"\bref_privacy\.refusal\(")


def calls_guard(text: str) -> bool:
    """A shell caller names the module and runs `guard --ref`; a Python one calls refusal()."""
    return all(r.search(text) for r in _GUARD_CALL) or bool(_GUARD_PY.search(text))


def scope(path: str) -> bool:
    if path == SELF or re.match(r"tools/audit/(?:round\d+|handoff|w5-[^/]*|archscore/planted)/"
                                r"|tools/policy/vendor/", path):
        return False
    return bool(re.match(r"\.github/workflows/[^/]+\.ya?ml$", path)
                or re.match(r"(?:tools|\.claude/workflows)/.*\.(?:sh|py|mjs|js|cjs)$", path))


def sites(lines) -> dict[str, list[int]]:
    found: dict[str, list[int]] = {}
    for path, n, text in lines:
        if scope(path) and not _COMMENT.match(text) and _SITE.search(text):
            found.setdefault(path, []).append(n)
    return found


def registry_refusals(found: dict[str, list[int]], text_of, registry=PUSHERS) -> list[str]:
    out = []
    for path, ns in sorted(found.items()):
        if path not in registry:
            out.append(f"{path}:{ns[0]}: a push site in a file PUSHERS does not name: guard it "
                       f"(ref_privacy.py guard / ref_privacy.refusal) and register it, or register why not")
        elif registry[path][0] == GUARDED and not calls_guard(text_of(path)):
            out.append(f"{path}: registered {GUARDED} but calls no ref_privacy guard")
    for path in sorted(set(registry) - set(found)):
        out.append(f"{path}: registered in PUSHERS but holds no push site; drop the entry")
    return out


def grep(ref: str) -> list[tuple[str, int, str]]:
    out = subprocess.run(["git", "grep", "-n", "-I", "-E", r"\bpush\b", ref, "--",
                          "tools", ".claude/workflows", ".github/workflows"],
                         cwd=ROOT, capture_output=True, text=True)
    if out.returncode not in (0, 1):
        raise RuntimeError(f"git grep exited {out.returncode}: {out.stderr.strip()}")
    lines = []
    for line in out.stdout.splitlines():
        _, path, n, text = line.split(":", 3)
        lines.append((path, int(n), text))
    return lines


def check(ref: str) -> int:
    found = sites(grep(ref))
    if not found:
        print("ref_privacy: REFUSE: the scan found no push site at all, so it checked nothing", file=sys.stderr)
        return 1

    def text_of(path: str) -> str:
        return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout

    bad = registry_refusals(found, text_of)
    for line in bad:
        print(f"ref_privacy: REFUSE {line}", file=sys.stderr)
    guarded = sum(1 for p in found if PUSHERS.get(p, ("",))[0] == GUARDED)
    print(f"ref_privacy --check at {ref}: {len(found)} file(s) with a push site, {guarded} guarded, "
          f"{len(bad)} refused")
    return 1 if bad else 0


# ---------------------------------------------------------------------------
# Self-test: synthetic identity only; the host's own name is never planted.

def self_test() -> int:
    import tempfile
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_env, throwaway_git_init

    passed = failed = 0

    def ok(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ok   {name}")
        else:
            failed += 1
            print(f"  FAIL {name}{(': ' + detail) if detail else ''}")

    def under(*parts: str) -> str:  # planted paths are built, never spelled (tmp_paths.py)
        return "/" + "/".join(parts)

    fake_name = "exampleuser"
    fake_home = under("Users", fake_name)
    fid = Identity.made({fake_home}, {fake_name}, 4242)
    scratch = under("private", "tmp", "claude-4242", f"-Users-{fake_name}-proj--wt-x", "0a1b", "scratchpad", "fix-1")

    # The defect's own instance: the old rule, `${w#$HOME/}` with non-alnum
    # mapped to '-', over a scratch path outside the home directory.
    old = re.sub(r"[^A-Za-z0-9._-]", "-", scratch.removeprefix(fake_home + "/").lstrip("/"))
    ok("the old wt_sync slug of a scratch path is refused",
       (refusal("wip-sync/" + old, (), fid) or "").startswith("account-name, uid, scratch-root, host-path"),
       str(refusal("wip-sync/" + old, (), fid)))
    s = slug(scratch, (), fid)
    ok("slug() of that path is ext-<leaf>-<hash>", re.fullmatch(r"ext-fix-1-[0-9a-f]{8}", s) is not None, s)
    ok("and passes the guard (the null control)", refusal("wip-sync/" + s, (), fid) is None)
    ok("slug() is stable for one path", slug(scratch, (), fid) == s)
    ok("and distinct for two paths sharing a leaf", slug(scratch.replace("0a1b", "0a1c"), (), fid) != s)
    leafy = f"/srv/{fake_name}-wt"
    ok("a leaf carrying the account name falls back to ext-<hash>",
       re.fullmatch(r"ext-[0-9a-f]{8}", slug(leafy, (), fid)) is not None, slug(leafy, (), fid))
    ok("a leaf named after the temp root falls back too",
       re.fullmatch(r"ext-[0-9a-f]{8}", slug("/srv/claude-4242", (), fid)) is not None)
    with tempfile.TemporaryDirectory() as td:
        real = os.path.realpath(td)
        inside = os.path.join(real, ".claude", "worktrees", "r10-x")
        ok("a path under a named root is <name>-<rest>",
           slug(inside, (("repo", real),), fid) == "repo-claude-worktrees-r10-x",
           slug(inside, (("repo", real),), fid))
    ok("--root naming the home directory still yields no leak",
       refusal(slug(fake_home + "/" + fake_name + "-wt", (("h", fake_home),), fid), (), fid) is None)

    planted = ("wip-sync/private-tmp-claude-4242--Users-exampleuser-proj", "wip-sync " + fake_home + "/proj")
    ok("a planted leaking ref name is refused", refusal(planted[0], (), fid) is not None)
    ok("a planted leaking message is refused, and named as the message",
       (refusal("wip-sync/ext-fix-1-0123abcd", (("the message", planted[1]),), fid) or "")
       .endswith("in the message"))
    ok("the clean name and message pass (the null control)",
       refusal("wip-sync/ext-fix-1-0123abcd", (("the message", "wip-sync ext-fix-1-0123abcd 2026-10-16T00:00:00Z"),),
               fid) is None)
    ok("the account name is judged as a word, not a substring",
       leaks("exampleusers and anexampleuser", fid) == [] and leaks("by EXAMPLEUSER.", fid) == ["account-name"])
    ok("the uid is judged in the temp root's shape only",
       leaks("PR #4242 at claude-42424", fid) == [] and "uid" in leaks("claude-4242", fid))
    ok("a public runner path passes", leaks(under("home", "runner", "w") + " " + under("home", "user", "r"), fid) == [])
    ok("another host's home is refused", leaks("see " + under("home", "someone", "x"), fid) == ["host-path"])
    ok("a per-user macOS temp is refused", leaks(under("private", "var", "folders", "ab", "T"), fid) == ["host-path"])
    ok("an unpublishable ref character is refused", refusal("wip-sync/a b", (), fid) == "unpublishable in the ref name")
    host = Identity.of_host()
    ok("the host identity reads a home, and judges no public account",
       bool(host.homes) and not set(host.names) & PUBLIC_ACCOUNTS)

    # --commits: only the commits no remote-tracking ref holds are judged.
    with tempfile.TemporaryDirectory() as td:
        bare, seat = os.path.join(td, "bare"), os.path.join(td, "seat")
        throwaway_git_init(bare, "-q", "--bare", "-b", "main")
        env = throwaway_git_init(seat, "-q", "-b", "main")

        def g(*a: str) -> str:
            return subprocess.run(["git", *a], cwd=seat, env=env, check=True, capture_output=True,
                                  text=True).stdout.strip()
        g("remote", "add", "origin", bare)
        g("commit", "-q", "--allow-empty", "-m", "base at " + fake_home + "/x")
        g("push", "-q", "origin", "main")
        g("fetch", "-q", "origin")
        g("commit", "-q", "--allow-empty", "-m", "clean local commit")
        msgs = [m for _, m in commit_messages("HEAD", seat)]
        ok("--commits judges the local commit only, not the one origin holds", msgs == ["clean local commit"], str(msgs))
        g("commit", "-q", "--allow-empty", "-m", "notes in " + scratch)
        r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "guard", "--ref", "fix/x",
                            "--commits", "HEAD", "-C", seat], env={**env, "HOME": fake_home, "USER": fake_name},
                           capture_output=True, text=True)
        ok("the guard CLI refuses an unpushed commit naming the scratch path, exit 3",
           r.returncode == 3 and "REFUSE" in r.stderr and scratch not in r.stderr, r.stderr.strip())
        r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "guard", "--ref", "fix/x",
                            "--commits", "HEAD~1", "-C", seat], env={**env, "HOME": fake_home, "USER": fake_name},
                           capture_output=True, text=True)
        ok("and passes the same branch one commit earlier (the null control)", r.returncode == 0, r.stderr.strip())
        r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "guard", "--ref", "fix/x",
                            "--commits", "no-such-rev", "-C", seat], env=env, capture_output=True, text=True)
        ok("an unreadable range refuses (fail closed), exit 2", r.returncode == 2, r.stderr.strip())

    # wt_sync.sh end to end: a worktree under a planted scratch path, pushed to
    # a temp bare origin under a planted HOME and USER.
    with tempfile.TemporaryDirectory() as td:
        td = os.path.realpath(td)
        home = os.path.join(td, "Users", fake_name)
        os.makedirs(home)
        bare, main = os.path.join(td, "origin.git"), os.path.join(home, "repo")
        throwaway_git_init(bare, "-q", "--bare", "-b", "main")
        env = throwaway_git_init(main, "-q", "-b", "main")
        # python3 is this interpreter: a seat shim resolves its venv under $HOME.
        path = os.path.dirname(sys.executable) + os.pathsep + env.get("PATH", "")
        env = {**env, "HOME": home, "USER": fake_name, "LOGNAME": fake_name, "PATH": path}

        def g(*a: str, cwd: str = main) -> str:
            return subprocess.run(["git", *a], cwd=cwd, env=env, check=True, capture_output=True,
                                  text=True).stdout.strip()
        g("remote", "add", "origin", bare)
        Path(main, "f").write_text("f\n")
        g("add", "f")
        g("commit", "-q", "-m", "base")
        g("push", "-q", "origin", "main")
        wt = os.path.join(td, "claude-4242", f"-Users-{fake_name}-repo--wt", "sess", "scratchpad", "fix-9")
        g("worktree", "add", "-q", "-b", "fix-9", wt)
        Path(wt, "dirty").write_text("x\n")
        wt2 = os.path.join(td, "elsewhere", "fix-10")
        g("worktree", "add", "-q", "-b", "fix-10", wt2)
        g("commit", "-q", "--allow-empty", "-m", "notes from " + wt2, cwd=wt2)
        r = subprocess.run(["bash", str(ROOT / "tools/audit/seat/wt_sync.sh")], cwd=main, env=env,
                           capture_output=True, text=True)
        refs = subprocess.run(["git", "--git-dir", bare, "for-each-ref", "refs/heads/wip-sync",
                               "--format=%(refname)%1f%(contents)%1e"], env=env, capture_output=True,
                              text=True).stdout
        pairs = [rec.strip("\n").split("\x1f", 1) for rec in refs.split("\x1e") if rec.strip()]
        wid = Identity.made({home, fake_home}, {fake_name}, 4242)
        ok("wt_sync pushed a snapshot of the dirty scratch worktree", len(pairs) >= 1,
           f"rc={r.returncode} out={r.stdout!r} err={r.stderr[-300:]!r}")
        bad = [(ref, refusal(ref.removeprefix("refs/heads/"), (("the message", msg),), wid)) for ref, msg in pairs]
        ok("no wip-sync ref name or message it pushed leaks the planted host",
           all(b is None for _, b in bad), "; ".join(f"{b}" for _, b in bad if b))
        ok("the worktree whose unpushed commit names its path is refused, not pushed",
           len(pairs) == 1 and "REFUSE" in r.stderr, f"{len(pairs)} ref(s); err={r.stderr[-300:]!r}")

        # body_push.sh, the handoff transport: its topic names the ref and the message.
        Path(td, "BODY.md").write_text("b\n")

        def body(topic: str) -> tuple[int, str]:
            r = subprocess.run(["bash", str(ROOT / "tools/audit/seat/body_push.sh"), topic,
                                os.path.join(td, "BODY.md")], cwd=main, env=env, capture_output=True, text=True)
            return r.returncode, subprocess.run(["git", "--git-dir", bare, "for-each-ref", "refs/heads/handoff-body"],
                                                env=env, capture_output=True, text=True).stdout
        rc, heads = body("Users-" + fake_name + "-notes")
        ok("body_push refuses a topic naming a host path, and pushes nothing", rc != 0 and heads == "", f"rc={rc} {heads}")
        rc, heads = body("r10-clean")
        ok("and pushes a clean topic (the null control)", rc == 0 and "handoff-body/r10-clean" in heads, f"rc={rc}")

    # The registry, over planted lines.
    lines = [("tools/x/new.sh", 3, 'git push -q origin "$c:refs/heads/x/$slug"'),
             ("tools/x/guarded.sh", 9, '  git -C "$w" push -q origin "$ref"'),
             ("tools/x/note.sh", 1, "# git push in a comment"),
             ("tools/x/cont.sh", 4, '     push --force-with-lease=refs/heads/x:"$e" \\'),
             ("tools/x/prose.js", 4, "push the branch after the failing-test commit"),
             ("tools/x/doc.py", 9, "push --json ...`). The window is still open"),
             ("tools/x/js.mjs", 2, "out.push(git)"),
             ("tools/x/py.py", 5, '    run(["git", "push", "-q", "origin", branch])'),
             ("tools/policy/vendor/v.js", 1, "git push"),
             (SELF, 1, "git push")]
    found = sites(lines)
    ok("the site rule finds shell and Python pushes, not comments, .push( or excluded paths",
       sorted(found) == ["tools/x/cont.sh", "tools/x/guarded.sh", "tools/x/new.sh", "tools/x/py.py"],
       str(sorted(found)))
    found.pop("tools/x/cont.sh")
    texts = {"tools/x/guarded.sh": 'RP=ref_privacy.py; "$RP" guard --ref "$ref" && git push',
             "tools/x/py.py": "import ref_privacy\nref_privacy.refusal(ref)\n",
             "tools/x/new.sh": ""}
    reg = {"tools/x/guarded.sh": (GUARDED, "t"), "tools/x/py.py": (GUARDED, "t"), "tools/x/gone.sh": ("fixture", "t")}
    bad = registry_refusals(found, texts.__getitem__, reg)
    ok("an unregistered pusher is refused", any(b.startswith("tools/x/new.sh:3:") for b in bad), str(bad))
    ok("a stale entry is refused", any(b.startswith("tools/x/gone.sh:") for b in bad), str(bad))
    ok("guarded files that call the guard pass (the null control)",
       not any("guarded.sh" in b or "py.py" in b for b in bad), str(bad))
    texts["tools/x/guarded.sh"] = "# ref_privacy.py is named in a comment only\ngit push"
    ok("a guarded entry that calls no guard is refused",
       any("guarded.sh: registered guarded" in b for b in registry_refusals(found, texts.__getitem__, reg)))

    print(f"ref_privacy self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--check"]:
        ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "HEAD"
        return check(ref)
    if argv[:1] == ["slug"] and len(argv) >= 2:
        roots, rest = [], argv[2:]
        while rest[:1] == ["--root"] and len(rest) >= 2 and "=" in rest[1]:
            roots.append(tuple(rest[1].split("=", 1)))
            rest = rest[2:]
        if rest:
            print(f"ref_privacy: unknown argument {rest[0]!r}", file=sys.stderr)
            return 2
        print(slug(argv[1], roots))
        return 0
    if argv[:1] == ["guard"]:
        ref, messages, rev, cwd, rest = None, [], None, None, argv[1:]
        while rest:
            flag = rest[0]
            if flag not in ("--ref", "--message", "--commits", "-C") or len(rest) < 2:
                print(f"ref_privacy: unknown or incomplete argument {flag!r}", file=sys.stderr)
                return 2
            if flag == "--ref":
                ref = rest[1]
            elif flag == "--message":
                messages.append(("the message", rest[1]))
            elif flag == "--commits":
                rev = rest[1]
            else:
                cwd = rest[1]
            rest = rest[2:]
        if ref is None:
            print("ref_privacy: guard needs --ref", file=sys.stderr)
            return 2
        try:
            if rev is not None:
                messages += commit_messages(rev, cwd)
        except RuntimeError as e:
            print(f"ref_privacy: REFUSE: could not read the commits the push publishes ({e}); nothing pushed",
                  file=sys.stderr)
            return 2
        why = refusal(ref, messages)
        if why:
            print(f"ref_privacy: REFUSE: {why} would publish this host; nothing pushed", file=sys.stderr)
            return 3
        return 0
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
