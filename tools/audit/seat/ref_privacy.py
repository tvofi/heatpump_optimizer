#!/usr/bin/env python3
"""Name a local path for publication, and refuse a push that would publish the host.

    python3 -I tools/audit/seat/ref_privacy.py slug <path> [--root NAME=DIR]...
    python3 -I tools/audit/seat/ref_privacy.py path <path>      (~/-relative for a posted text)
    python3 -I tools/audit/seat/ref_privacy.py guard --ref <ref> [--message <text>]...
                                                     [--commits <rev> [-C <dir>]]
    python3 -I tools/audit/seat/ref_privacy.py scrub [--write] <file>...  (this host's spans, in place)
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
shell callers' form, and `--commits <rev>` adds the message, and the author
and committer email, of every commit under <rev> that no remote-tracking ref
already holds -- the ones the push publishes for the first time. A refusal
names its class and where, never the matched text. Text is judged as written
and URL-decoded once (`%2FUsers%2F<name>`). The classes, judged against the
host's own identity (`Identity.of_host`: $HOME, its resolved path, the passwd
home; $USER, $LOGNAME, the passwd name, the home's basename; the uid; the
hostname):
  home-directory  a home directory, verbatim (case-folded: macOS paths are);
  account-name    an account name as a whole word -- bounded by characters
                  outside [A-Za-z0-9], so `-Users-<name>-` counts;
  uid             `claude-<uid>`, the session temp root's name;
  scratch-root    `tmp/claude-<digits>`, `/` or `-` separated: ANY host's
                  session temp root, the shape the 70 refs carried;
  host-path       `/Users/<x>` or `/home/<x>`, a macOS per-user temp
                  (`/var/folders/`), or the dash-mangled `Users-<x>` form;
  unpublishable   (ref names and slugs only) a character outside
                  [A-Za-z0-9._/-];
  host-email      (author and committer emails only) a private-use domain
                  (`.local`, `.lan`, `.internal`, ...) or this host's own
                  name -- git's default identity is <user>@<hostname>. A
                  public domain passes, so a noreply address does.
The accounts `root`, `runner` and `user`, and names under three characters, are
not judged: the first three are the fixed accounts of a container, the CI
runner and the cloud seat image, public by construction, and a shorter name
would refuse ordinary words.

THE HOST-PATH GRAMMAR is this module's: `HOME_DIR`, `PUBLIC_ACCOUNTS`,
`CLOUD_ROOTS`. tmp_paths.py imports them. The two apply one grammar to two
questions: here, whether a name PUBLISHES a host (a public account's home does
not); there, whether a tracked script DEPENDS on one machine (any home does,
bar the cloud image's two fixed roots).

CHECK. `--check` is the class rule as a standing registry (fixer.md step 8).
It enumerates every tracked file, at <ref> through `git grep`, holding a push
site -- a non-comment line on which `git` (or `$GIT`/`${GIT}`, a `g`/`rgit`
wrapper, or a Python `git`/`g`/`run`/`sh` call) is followed by the word
`push`; a continuation line opening `push` with a push option, `origin` or a
variable; or a `gh api` call that writes a ref -- `git/refs` or `git/tags`
with a field (`-f`, `-F`, `--field`, `--input`) or a POST/PATCH/PUT method, or
a `createRef`/`updateRef` mutation; or a release that makes a tag --
`gh release create`, or `gh api .../releases` with a field or a write
method -- in `tools/`,
`.claude/workflows/` and `.github/workflows/`, less round evidence and vendored
code. Each such file must have an entry in PUSHERS below: `guarded` (the file
must call this module) or a stated reason it composes nothing a host could leak
into. A file with a site and no entry, a `guarded` entry that does not call this
module, and an entry whose file has no site are each refused, so the registry
cannot rot into an exemption.

CONTENT. `--check` also judges every line a diff adds to a tracked file since
the merge base with origin/main, with the classes above (round 4: the records
under dev/ and the ledger had published the home path in 128 files). A line the same diff
removes elsewhere is a move and is not charged; main's stock is not charged.
`scrub --write <file>...` is the remedy: this host's spans, rewritten in place.

WHAT IT DOES NOT CATCH. A push built across lines whose `push` line opens
with neither a push option, `origin` nor a variable; a `gh api` ref write
whose path and field sit on different lines; a commit written through the
Contents API (`gh api .../contents/<path>` with a `message` field), whose
message the guard never sees; a push through another wrapper
name or a git variable not named GIT; a guarded
file that gains a second, unguarded push (the registry is keyed on the file:
review owns the site); file content a push publishes outside a tracked diff --
a bus ref's evidence tree, a handoff body -- (the guard reads ref names,
messages and commit identities; CONTENT reads tracked diffs); on a runner, an
account name standing alone, since a runner knows only its own; compressed
content (a .gz or .zip blob is judged as its compressed bytes, which spell no
path); text in an encoding neither ASCII-compatible nor UTF-16; base64 (a path
inside an encoded run, as a .har or an HTML report embeds one, is judged as the
encoded text, which spells no path; no decoder is run, since decoding every
base64-looking run is not sound); text encoded twice or JSON-escaped (`\\/Users\\/<x>`);
and another machine's account name, unless it sits in a `/Users/`, `/home/` or
`Users-` shape.
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
#: The fixed accounts of a container (root), the CI runner (runner) and the
#: cloud seat image (user, cloud-setup.sh): public by construction.
PUBLIC_ACCOUNTS = frozenset({"root", "runner", "user"})
MIN_NAME = 3
HASH_HEX = 8

#: THE HOST-PATH GRAMMAR, owned here; tools/audit/seat/tmp_paths.py imports it.
#: HOME_DIR is one account's home directory, `/Users/<name>` or `/home/<name>`
#: (the name is HOME_NAME's characters); tmp_paths.py refuses every one a
#: tracked script depends on, public accounts included, bar the cloud roots.
HOME_NAME = r"[\w.-]+"
HOME_DIR = r"/(?:Users|home)/" + HOME_NAME
#: The cloud seat image's fixed roots under its public account (cloud-setup.sh):
#: the one home a tracked script may name (tmp_paths.py's `cloud` rule).
CLOUD_ACCOUNT = "user"
CLOUD_ROOTS = r"/home/" + CLOUD_ACCOUNT + r"/(?:heatpump_optimizer\b|wt/)"
#: A public account's name as a whole path segment.
_PUBLIC = r"(?:" + "|".join(sorted(PUBLIC_ACCOUNTS)) + r")"
#: What this guard refuses: a home directory that is not a public account's,
#: a macOS per-user temp, or the dash-mangled `Users-<name>` form.
_HOST_PATH = re.compile(
    r"/(?:Users|home)/(?!" + _PUBLIC + r"(?:/|$|[^\w.-]))[\w.-]"
    r"|/var/folders/"
    r"|(?<![A-Za-z0-9])Users-(?!" + _PUBLIC + r"(?:-|$|[^\w.]))[\w.]")
#: Private-use email domains: a git identity under one names a machine
#: (git's own default is <user>@<hostname>, often `.local`).
PRIVATE_EMAIL_SUFFIXES = (".local", ".localdomain", ".lan", ".internal", ".localhost", ".home.arpa")
_SCRATCH_ROOT = re.compile(r"tmp[/-]+claude-\d+(?![0-9])")
_REF_CHARS = re.compile(r"^[A-Za-z0-9._/-]+$")
_SLUG_UNSAFE = re.compile(r"[^A-Za-z0-9_]+")


@dataclass(frozen=True)
class Identity:
    homes: tuple[str, ...]
    names: tuple[str, ...]
    uid: int | None
    hosts: tuple[str, ...] = ()

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
        import socket
        return Identity.made(homes, names, uid, {socket.gethostname()})

    @staticmethod
    def made(homes, names, uid, hosts=()) -> "Identity":
        hs = tuple(sorted({h.rstrip("/") for h in homes if h and h.rstrip("/")}))
        ns = tuple(sorted({n.casefold() for n in names
                           if len(n) >= MIN_NAME and n.casefold() not in PUBLIC_ACCOUNTS}))
        hn = {h.casefold().rstrip(".") for h in hosts if h}
        hn |= {h.split(".", 1)[0] for h in hn}
        return Identity(hs, ns, uid, tuple(sorted(h for h in hn if h and h != "localhost")))


def leaks(text: str, ident: Identity) -> list[str]:
    """The leak classes `text` or its URL-decoded form carries, in a fixed order, each once."""
    from urllib.parse import unquote
    decoded = unquote(text)
    if decoded == text:
        return _leaks(text, ident)
    both = set(_leaks(text, ident)) | set(_leaks(decoded, ident))
    return [c for c in CLASSES if c in both]


CLASSES = ("home-directory", "account-name", "uid", "scratch-root", "host-path")


def email_leaks(email: str, ident: Identity) -> list[str]:
    """`host-email` when a git identity's domain names a machine: a private-use
    suffix, or this host's own name. A public domain (a noreply address) passes."""
    domain = email.rsplit("@", 1)[-1].casefold().rstrip(".>")
    if (domain == "localhost" or domain.endswith(PRIVATE_EMAIL_SUFFIXES)
            or domain in ident.hosts or domain.split(".", 1)[0] in ident.hosts):
        return ["host-email"]
    return []


def _leaks(text: str, ident: Identity) -> list[str]:
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


def refusal(ref: str, messages=(), ident: Identity | None = None, emails=()) -> str | None:
    """Why pushing `ref` with these commit messages and identities would publish the host, or None."""
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
    for where, email in emails:
        why = email_leaks(email, ident)
        if why:
            return f"{', '.join(why)} in {where}"
    return None


#: The classes a comment body is judged on: this host's own identity, and any
#: session temp root. A comment may quote another home (a planted fixture's
#: home under another account), so the generic host-path class is a ref-name rule only.
BODY_CLASSES = ("home-directory", "account-name", "uid", "scratch-root")


def body_refusal(text: str, ident: Identity | None = None) -> str | None:
    """Why posting this comment or review body would publish this host, or None."""
    why = [c for c in leaks(text, ident or Identity.of_host()) if c in BODY_CLASSES]
    return f"{', '.join(why)} in the body" if why else None


def home_relative(path: str, home: str | None = None) -> str:
    """A local path as a posted text names it: `~/<rest>` under the home
    directory (as written or resolved), else unchanged. A reader resolves `~`
    against its own $HOME (app_approve.sh's evidence gate)."""
    home = os.environ.get("HOME", "") if home is None else home
    for h in dict.fromkeys((home.rstrip("/"), os.path.realpath(home).rstrip("/") if home else "")):
        if h and (path == h or path.startswith(h + "/")):
            return "~" + path[len(h):]
    return path


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


def published(rev: str, cwd: str | None = None) -> tuple[list, list]:
    """(messages, emails), each a list of (where, text), for every commit under
    `rev` that no remote-tracking ref holds: what the push publishes first."""
    out = subprocess.run(["git", "log", "--format=%H%x1f%ae%x1f%ce%x1f%B%x1e", rev, "--not", "--remotes"],
                         cwd=cwd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git log {rev} --not --remotes exited {out.returncode}")
    messages, emails = [], []
    for rec in out.stdout.split("\x1e"):
        rec = rec.strip("\n")
        if rec:
            sha, ae, ce, msg = rec.split("\x1f", 3)
            messages.append((f"the message of {sha[:12]}", msg))
            emails += [(f"the author email of {sha[:12]}", ae), (f"the committer email of {sha[:12]}", ce)]
    return messages, emails


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
    "tools/audit/seat/prune_refs.py": (GUARDED, "writes archive/<branch> tags through gh api git/refs: "
                                       "a permanent name from a branch it does not fix (round 2)"),
    "tools/pr/merge_main_bot.py": ("republishes", "pushes a merge onto a pull request's own branch, "
                                   "a name the remote already holds, under the constant SUBJECT"),
    "tools/audit/seat/merge_train.py": ("republishes", "deletes merged branches the remote already "
                                        "holds; its other push is the self-test's stub"),
    ".github/workflows/tests.yml": ("republishes", "on a runner, constant-message bot commits onto the "
                                    "pull request's own branch, record/autofix or main (nightly kills)"),
    "tools/pr/app_approve.sh": ("fixture", "its pushes are the self-test's, into a temp bare repository"),
    "tools/audit/seat/pr_args.sh": ("fixture", "its self-test's stub app_push.sh pushes the branch it is given "
                                    "into a scratch origin repository; the file pushes nothing else"),
    "tools/audit/seat/r9_rc_bus_fetchhead.sh": ("fixture", "a regression harness: every push goes to a "
                                                "temp bare repository"),
    ".github/workflows/release.yml": ("shape-checked", "`gh release create` makes the tag on origin, and the "
                                      "step before refuses any TAG not matching ^v[0-9]+\\.[0-9]+\\.[0-9]+$, "
                                      "so no host text reaches the name (round 3)"),
    "tools/policy/fragments_sync.mjs": ("fixture", "a `git push` string fed to its own lint as a fixture"),
    "tools/audit/seat/cloud_dispatch.py": ("prompt", "a cloud reviewer's prompt naming probe/rev-<pr>-<nonce8> "
                                           "from a PR number and 8 hex digits, under a constant seat identity; "
                                           "the script itself pushes nothing"),
    ".claude/workflows/audit-find.js": ("prompt", "an agent prompt naming handoff/audit-r<round>-... "
                                        "refs from round and box numbers"),
}

_GH_WRITE = (r"(?:(?<![\w-])-[fF](?![\w-])|--(?:raw-)?field\b|--input\b"
             r"|(?:-X|--method)[\"',\s=]*(?:POST|PATCH|PUT)\b)")
_SITE = re.compile(
    r"(?:\b(?:git|rgit)\b|\$\{?(?i:git)\}?(?![\w]))[^\n]*?(?<![\w.-])push(?![\w-])"
    r"|\bgh\b[^\n]*?\bapi\b(?=[^\n]*git/(?:refs|tags)\b)(?=[^\n]*" + _GH_WRITE + r")"
    r"|\bgh\b[^\n]*?\bapi\b[^\n]*\b(?:createRef|updateRef)\b"
    r"|\bgh\s+release\s+create\b"
    r"|\bgh\b[^\n]*?\bapi\b(?=[^\n]*/releases\b)(?=[^\n]*" + _GH_WRITE + r")"
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
    """tmp_paths.py's instrument scope (its one owner), narrowed to the pushing trees."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import tmp_paths
    if path == SELF or re.match(r"tools/audit/archscore/planted/|tools/policy/vendor/", path):
        return False
    return path.startswith(("tools/", ".claude/workflows/", ".github/workflows/")) and tmp_paths.scope(path)


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
    out = subprocess.run(["git", "grep", "-n", "-I", "-E", r"\bpush\b|git/(refs|tags)|createRef|updateRef|release +create|/releases", ref, "--",
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
    base, added, refused = content_check(ref)
    bad += refused
    for line in bad:
        print(f"ref_privacy: REFUSE {line}", file=sys.stderr)
    guarded = sum(1 for p in found if PUSHERS.get(p, ("",))[0] == GUARDED)
    print(f"ref_privacy --check at {ref}: {len(found)} file(s) with a push site, {guarded} guarded, "
          f"{len(added)} line(s) added since {(base or 'nothing')[:12]} judged, {len(bad)} refused")
    return 1 if bad else 0


# ---------------------------------------------------------------------------
# Tracked content: what a diff adds is judged like a ref name (#2310's third
# part). A tracked record publishes on every clone, so a home path in an
# evidence log is the 70 refs' leak with a longer life. Only lines a diff ADDS
# are judged, against the merge base with origin/main (tmp_paths.ledger_base,
# its one owner): main's stock is not charged to every branch, and a line the
# same diff removes is a move, not an addition. The classes are CLASSES: on a
# runner the identity is a public account, so the host-path and scratch-root
# shapes are what judge there; on a seat its own home, name and uid join them.
# The remedy is `scrub`, which rewrites only this host's spans.

def content_check(ref: str, root: Path = ROOT, ident: Identity | None = None):
    """(base, added lines, refusals) for `ref` against tmp_paths.ledger_base: what --check runs."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import tmp_paths
    base = tmp_paths.ledger_base(ref, root)
    if base is None:
        print(f"ref_privacy: content SKIP -- no merge base with origin/main and no parent of {ref}")
        return None, [], []
    added = added_lines(base, ref, root)
    return base, added, name_refusals(added_names(base, ref, root), ident) + content_refusals(added, ident)


def added_names(base: str, ref: str, cwd: Path = ROOT) -> list[str]:
    """Every path `ref` holds that `base` did not: an added, renamed or copied file's name
    (round 3). A name publishes on every clone as surely as content: #2310 began as the
    dash-mangled home of a project directory, `-Users-<name>-...`, in a ref name."""
    got = subprocess.run(["git", "diff", "--no-renames", "--name-only", "--diff-filter=A", "-z", base, ref],
                         cwd=cwd, capture_output=True)
    if got.returncode != 0:
        raise RuntimeError(f"git diff --diff-filter=A {base[:12]} {ref} exited {got.returncode}")
    return [p for p in got.stdout.decode("utf-8", "replace").split("\0") if p]


def name_refusals(paths, ident: Identity | None = None) -> list[str]:
    """One refusal per added path whose NAME would publish a host, judged like a ref name."""
    ident = ident or Identity.of_host()
    out = []
    for i, path in enumerate(paths, 1):
        why = leaks(path, ident)
        if why:
            out.append(f"added path #{i} of `git diff --name-only --diff-filter=A`: {', '.join(why)} in the name of a file the diff adds; rename it")
    return out


def blob_text(data: bytes) -> str:
    """A blob as the content check reads it. Text is UTF-8 (undecodable bytes
    replaced). A blob holding a NUL byte has its NULs dropped and every other
    byte kept one-for-one (Latin-1), so the ASCII a binary carries -- a path in
    an image's metadata, or UTF-16 text, whose ASCII is every other byte -- reads
    as the guard's classes see it. A segment between two newlines is a "line"."""
    if b"\0" in data:
        return data.replace(b"\0", b"").decode("latin-1")
    return data.decode("utf-8", "replace")


def added_lines(base: str, ref: str, cwd: Path = ROOT) -> list[tuple[str, int, str]]:
    """(path, line, text) for every line of a file `base..ref` changes whose text the
    file did not hold at `base`, less any text another changed file gave up (a move).
    Judged by line text per file, not by hunk: a reordered line is not charged, and
    no diff grammar is parsed here (the hunk header is mutation_table.py's to read).
    A blob holding a NUL byte (an image, a UTF-16 capture, any binary) is judged
    too, as `blob_text` renders it: binary content is not skipped (round 2)."""
    def run(*a: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *a], cwd=cwd, capture_output=True)

    names = run("diff", "--no-renames", "--name-only", "-z", base, ref)
    if names.returncode != 0:
        raise RuntimeError(f"git diff {base[:12]} {ref} exited {names.returncode}")

    def lines(rev: str, path: str) -> list[str]:
        got = run("show", f"{rev}:{path}")
        return blob_text(got.stdout).splitlines() if got.returncode == 0 else []  # absent: added or deleted whole

    added, removed = [], set()
    for path in filter(None, names.stdout.decode("utf-8", "replace").split("\0")):
        old, new = lines(base, path), lines(ref, path)
        was, now = {t.strip() for t in old}, {t.strip() for t in new}
        removed |= was - now
        added += [(path, n, t) for n, t in enumerate(new, 1) if t.strip() not in was]
    return [(p, n, t) for p, n, t in added if t.strip() not in removed]


def content_refusals(lines, ident: Identity | None = None) -> list[str]:
    """One refusal per added line that would publish a host: where and which class, never the text."""
    ident = ident or Identity.of_host()
    out = []
    for path, n, text in lines:
        why = leaks(text, ident)
        if why:
            out.append(f"{path}:{n}: {', '.join(why)} in an added line of a tracked file; "
                       f"rewrite it with `ref_privacy.py scrub --write {path}` or drop the path")
    return out


#: macOS's per-user temp root, built rather than spelled: the content check
#: reads this file like any other, and a spelled path is what it refuses.
MAC_TEMP = "/".join(("", "var", "folders"))
TMP_ROOT = "/".join(("", "tmp"))


def scrub(text: str, ident: Identity) -> str:
    """`text` with this host's spans rewritten in place, each to a fixed placeholder:
    a session scratchpad under the host's temp root to `<scratchpad>`, any other
    path under that root to `<session-tmp>`, a macOS per-user temp to `<tmp>`, the
    home directory to `~`, and a remaining account name to `<owner-home>`. Line
    breaks are untouched, so a line count and every line number survive."""
    if ident.uid is not None:
        root = rf"(?:/private)?{TMP_ROOT}/claude-{ident.uid}(?![0-9])"
        text = re.sub(root + r"/[^/\s\"'`]+/[^/\s\"'`]+/scratchpad(?![\w-])", "<scratchpad>", text)
        text = re.sub(root, "<session-tmp>", text)
    text = re.sub(r"(?:/private)?" + MAC_TEMP + r"/[\w-]+/[\w-]+/T(?![\w-])", "<tmp>", text)
    for h in sorted(ident.homes, key=len, reverse=True):
        text = re.sub(re.escape(h) + r"(?![\w.-])", "~", text, flags=re.IGNORECASE)
    for nm in ident.names:
        text = re.sub(r"(?<![A-Za-z0-9])" + re.escape(nm) + r"(?![A-Za-z0-9])", "<owner-home>", text,
                      flags=re.IGNORECASE)
    return text


# ---------------------------------------------------------------------------
# Self-test: synthetic identity only; the host's own name is never planted.

def self_test() -> int:
    import inspect
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
    fid = Identity.made({fake_home}, {fake_name}, 4242, {"example-mbp.local"})
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
    esc = "see %2FUsers%2F" + fake_name + "%2Fproj"
    ok("a URL-escaped home path is refused, judged decoded (round 2)",
       leaks(esc, fid) == ["home-directory", "account-name", "host-path"], str(leaks(esc, fid)))
    ok("and an escape that decodes to nothing private passes (the null control)",
       leaks("100%25 done, see %2Fsrv%2Fbuild", fid) == [])
    ok("a git identity at a private-use domain is refused (round 2)",
       email_leaks("t@" + fake_name + "s-mbp.local", fid) == ["host-email"]
       and email_leaks("t@seat.lan", fid) == ["host-email"])
    ok("and one at this host's own name, short or full",
       email_leaks("t@example-mbp", fid) == ["host-email"] and email_leaks("t@EXAMPLE-MBP.local", fid) == ["host-email"])
    ok("a noreply address passes, even naming the account (the null control)",
       email_leaks("123+" + fake_name + "@users.noreply.github.com", fid) == []
       and email_leaks("noreply@anthropic.com", fid) == [])
    bodyleak = "evidence: " + fake_home + "/.zcode/bus/verdicts/7/abc/evidence"
    ok("a comment body naming this host's home is refused (the bus evidence line)",
       (body_refusal(bodyleak, fid) or "").startswith("home-directory, account-name"), str(body_refusal(bodyleak, fid)))
    ok("and the same line home-relative passes, as does a quoted other home (the null control)",
       body_refusal("evidence: ~/.zcode/bus/verdicts/7/abc/evidence", fid) is None
       and body_refusal("planted " + under("Users", "someone", "y"), fid) is None)
    ok("home_relative: under the home is ~/<rest>; outside it, or a sibling sharing its prefix, unchanged",
       home_relative(fake_home + "/.zcode/bus/x", fake_home) == "~/.zcode/bus/x"
       and home_relative("/srv/x", fake_home) == "/srv/x" and home_relative(fake_home + "s/x", fake_home) == fake_home + "s/x")
    host = Identity.of_host()
    ok("the host identity reads a home and a hostname, and judges no public account",
       bool(host.homes) and bool(host.hosts) and not set(host.names) & PUBLIC_ACCOUNTS)

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
        msgs = [m for _, m in published("HEAD", seat)[0]]
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
        # round 2: the identity a published commit carries is judged too
        g("reset", "-q", "--hard", "HEAD~1")
        r = subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "clean"], cwd=seat, capture_output=True,
                           env={**env, "GIT_AUTHOR_EMAIL": "t@" + fake_name + "s-mbp.local"})
        r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "guard", "--ref", "fix/x",
                            "--commits", "HEAD", "-C", seat], env=env, capture_output=True, text=True)
        ok("the guard CLI refuses an unpushed commit whose author email names a machine, exit 3",
           r.returncode == 3 and "host-email in the author email of" in r.stderr, r.stderr.strip())
        g("commit", "-q", "--amend", "--allow-empty", "--no-edit", "--reset-author")
        r = subprocess.run([sys.executable, "-I", str(Path(__file__).resolve()), "guard", "--ref", "fix/x",
                            "--commits", "HEAD", "-C", seat], env=env, capture_output=True, text=True)
        ok("and passes it re-authored to the fixture identity (the null control)", r.returncode == 0, r.stderr.strip())

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
        # The plant leaks by construction on every host: it names the planted
        # home, never the temp root, which is a host path on macOS
        # (/var/folders) and none on Linux (/tmp) -- the #2316 CI red.
        wt2 = os.path.join(home, "elsewhere", "fix-10")
        g("worktree", "add", "-q", "-b", "fix-10", wt2)
        planted_msg = "notes from " + wt2
        g("commit", "-q", "--allow-empty", "-m", planted_msg, cwd=wt2)
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
        ok("the planted message is itself a leak under the planted identity (the plant's precondition)",
           (refusal("fix-10", (("the message", planted_msg),), wid) or "").startswith("home-directory"),
           str(refusal("fix-10", (("the message", planted_msg),), wid)))
        ok("the worktree whose unpushed commit names its path is refused, not pushed",
           len(pairs) == 1 and "REFUSE" in r.stderr, f"{len(pairs)} ref(s); err={r.stderr[-300:]!r}")

        # body_push.sh, the handoff transport: its topic names the ref and the message.
        # It runs the checkout's ci_predict.py first (R10-HANDOFF-PREPR-BOUNCE M2);
        # the planted repository is no code head, so a stub predictor passes it.
        Path(main, "tools/pr").mkdir(parents=True)
        Path(main, "tools/pr/ci_predict.py").write_text("print('CI PREDICT: planted stub')\n")
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
             ("tools/x/gfn.py", 7, '    code, o = g(wt, "push", "-q", "origin", f"HEAD:refs/heads/{br}")'),
             ("tools/x/var.sh", 2, '"$GIT" -C "$w" push -q origin "$ref"'),
             ("tools/x/var2.sh", 2, '${GIT} push origin x'),
             ("tools/x/gitdir.sh", 2, 'cd "$GIT_DIR" && echo push done'),
             ("tools/x/ghsh.sh", 3, 'gh api "repos/$r/git/refs" -f ref="refs/tags/$t" -f sha="$s"'),
             ("tools/x/ghpy.py", 3, '["gh", "api", f"repos/{repo}/git/refs", "-f", f"ref={ref}",'),
             ("tools/x/ghpatch.sh", 3, 'gh api -X PATCH "repos/$r/git/refs/heads/$b" -F force=true'),
             ("tools/x/ghgql.sh", 3, 'gh api graphql -f query="mutation { createRef(input: $i) { ref { name } } }"'),
             ("tools/x/ghread.sh", 3, 'gh api "repos/$r/git/refs/heads/$b" --jq .object.sha'),
             ("tools/x/ghdel.sh", 3, 'gh api -X DELETE "repos/$r/git/refs/heads/$b"'),
             (".github/workflows/x-rel.yml", 9, '          gh release create "${TAG}" \\'),
             ("tools/x/relapi.sh", 3, 'gh api "repos/$r/releases" -f tag_name="$t" -f target_commitish="$s"'),
             ("tools/x/relview.sh", 3, 'gh release view "$t" --json tagName'),
             ("tools/x/relget.sh", 3, 'gh api "repos/$r/releases/latest" --jq .tag_name'),
             ("tools/policy/vendor/v.js", 1, "git push"),
             (SELF, 1, "git push")]
    found = sites(lines)
    ok("the site rule finds shell and Python pushes, not comments, .push( or excluded paths",
       {"tools/x/cont.sh", "tools/x/guarded.sh", "tools/x/new.sh", "tools/x/py.py"} <= set(found),
       str(sorted(found)))
    ok("a Python wrapper call with no `git` word is a site (the g(...) arm alone: merge_train.py's shape)",
       "tools/x/gfn.py" in found)
    ok("git spelled through a variable is a site, and $GIT_DIR is not (round 2)",
       {"tools/x/var.sh", "tools/x/var2.sh"} <= set(found) and "tools/x/gitdir.sh" not in found)
    ok("a gh api ref write is a site: -f, -F, -X PATCH, a createRef mutation (round 2)",
       {"tools/x/ghsh.sh", "tools/x/ghpy.py", "tools/x/ghpatch.sh", "tools/x/ghgql.sh"} <= set(found))
    ok("and a gh api ref read or DELETE is not (the null control)",
       not {"tools/x/ghread.sh", "tools/x/ghdel.sh"} & set(found))
    ok("a release that makes a tag is a site: gh release create, gh api .../releases with a field (round 3)",
       {".github/workflows/x-rel.yml", "tools/x/relapi.sh"} <= set(found))
    ok("and a release read is not (the null control)",
       not {"tools/x/relview.sh", "tools/x/relget.sh"} & set(found))
    for extra in (".github/workflows/x-rel.yml", "tools/x/relapi.sh", "tools/x/cont.sh", "tools/x/gfn.py", "tools/x/var.sh", "tools/x/var2.sh", "tools/x/ghsh.sh",
                  "tools/x/ghpy.py", "tools/x/ghpatch.sh", "tools/x/ghgql.sh"):
        found.pop(extra, None)
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

    # Tracked content (round 4): a diff adding a line that names a host is
    # refused, by where and class; the planted text is built, never spelled.
    with tempfile.TemporaryDirectory() as td:
        env = throwaway_git_init(td, "-q", "-b", "main")

        def g(*a: str) -> str:
            return subprocess.run(["git", *a], cwd=td, env=env, check=True, capture_output=True,
                                  text=True).stdout.strip()
        stock = "stock log line from " + fake_home + "/old\n"
        Path(td, "rec.log").write_text("clean\n" + stock)
        kept = "kept stock line from " + fake_home + "/kept\n"  # no other file gives it up
        Path(td, "keep.log").write_text(kept)
        g("add", "-A"); g("commit", "-q", "-m", "base")
        base = g("rev-parse", "HEAD")
        Path(td, "rec.log").write_text("clean\n" + "File " + scratch + "/x.py\n")
        Path(td, "moved.log").write_text(stock)  # moved out of rec.log, not added
        Path(td, "other.log").write_text("ran at " + under("home", "someone", "w") + "\n")
        Path(td, "keep.log").write_text(kept + "edited\n")  # a changed file keeping main's stock line
        Path(td, "nul.bin").write_bytes(b"bin\0\nran at " + under("Users", "someone", "w").encode() + b"\n")
        Path(td, "u16.txt").write_bytes(("ran at " + under("Users", "someone", "w") + "\n").encode("utf-16-le"))
        Path(td, "clean.bin").write_bytes(b"\x89PNG\0\0\x01ran at ~/w\n\0")
        os.makedirs(Path(td, "rounds", f"-Users-{fake_name}-proj"))
        Path(td, "rounds", f"-Users-{fake_name}-proj", "x.log").write_text("ok\n")  # the leak is the NAME
        os.makedirs(Path(td, "fresh"))
        Path(td, "fresh", "ok.log").write_text("ok\n")
        g("add", "-A"); g("commit", "-q", "-m", "plant")
        g("update-ref", "refs/remotes/origin/main", base)
        got_base, _, bad = content_check("HEAD", Path(td), fid)
        ok("--check's content arm judges the diff from the merge base with origin/main", got_base == base)
        ok("and check() runs it (a pin by text: check() itself needs the real tree's pushers)",
           "content_check(ref)" in inspect.getsource(check))
        ok("a diff adding a line naming the host's scratch path is refused, by line and class",
           any(b.startswith("rec.log:2: account-name, uid, scratch-root, host-path") for b in bad), str(bad))
        ok("and one naming another machine's home, by the host-path shape a runner can see",
           any(b.startswith("other.log:1: host-path") for b in bad), str(bad))
        ok("the refusal never echoes the planted text", not any(fake_name in b for b in bad), str(bad))
        ok("a line the diff moves from another file is not charged (the null control)",
           not any(b.startswith("moved.log:") for b in bad), str(bad))
        ok("main's stock line in a changed file is not charged (the null control)",
           not any(b.startswith("keep.log:") for b in bad), str(bad))
        ok("a NUL-bearing file adding a host line is refused: binary content is judged (round 2)",
           any(b.startswith("nul.bin:") for b in bad), str(bad))
        ok("and so is UTF-16 text naming one, its NULs dropped",
           any(b.startswith("u16.txt:") for b in bad), str(bad))
        ok("a file added under a dash-mangled home is refused by its name, never echoing it (round 3)",
           any(b.startswith("added path #") and "account-name, host-path in the name" in b
               and fake_name not in b for b in bad), str(bad))
        ok("an ordinary new path passes by name and content (the null control)",
           not any(b.startswith("fresh/") for b in bad) and sum("in the name" in b for b in bad) == 1, str(bad))
        ok("a NUL-bearing file naming no host passes (the null control), and nothing else is charged",
           not any(b.startswith("clean.bin:") for b in bad) and len(bad) == 5, str(bad))
        Path(td, "rec.log").write_text("clean\n" + scrub(stock + "File " + scratch + "/x.py\n", fid))
        for f in ("moved.log", "other.log", "nul.bin", "u16.txt", f"rounds/-Users-{fake_name}-proj/x.log"):
            Path(td, f).unlink()
        g("add", "-A"); g("commit", "-q", "-m", "scrubbed")
        ok("the scrubbed tree's diff is refused nothing (scrub is the remedy)",
           content_refusals(added_lines(base, "HEAD", Path(td)), fid) == [],
           str(content_refusals(added_lines(base, "HEAD", Path(td)), fid)))
    planted = (scratch + "/a.log and " + fake_home + "/x and EXAMPLEUSER and "
               + under("private", "var", "folders", "ab", "cd0", "T", "t1") + " and "
               + under("tmp", "claude-4242", "d13", "w.json") + "\n")
    clean = scrub(planted, fid)
    ok("scrub leaves no leak class under the planted identity, and keeps the line count",
       leaks(clean, fid) == [] and clean.count("\n") == planted.count("\n"), clean)
    ok("scrub's placeholders, in order: scratchpad, home, account, temp, session temp",
       clean == "<scratchpad>/fix-1/a.log and ~/x and <owner-home> and <tmp>/t1 and <session-tmp>/d13/w.json\n", clean)
    ok("scrub leaves another account's home and a public one alone (the null control)",
       scrub(under("home", "runner", "w") + " " + under("Users", "someone"), fid)
       == under("home", "runner", "w") + " " + under("Users", "someone"))

    print(f"ref_privacy self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--check"]:
        ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "HEAD"
        return check(ref)
    if argv[:1] == ["scrub"] and len(argv) >= 2:
        write, paths = "--write" in argv[1:], [a for a in argv[1:] if a != "--write"]
        ident, changed = Identity.of_host(), 0
        for f in paths:
            text = Path(f).read_text(encoding="utf-8", errors="surrogateescape")
            new = scrub(text, ident)
            if new != text:
                changed += 1
                if write:
                    Path(f).write_text(new, encoding="utf-8", errors="surrogateescape")
        print(f"ref_privacy scrub: {changed} of {len(paths)} file(s) {'rewritten' if write else 'would change'}")
        return 0
    if argv[:1] == ["path"] and len(argv) == 2:
        print(home_relative(argv[1]))
        return 0
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
        ref, messages, emails, rev, cwd, rest = None, [], [], None, None, argv[1:]
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
                ms, emails = published(rev, cwd)
                messages += ms
        except RuntimeError as e:
            print(f"ref_privacy: REFUSE: could not read the commits the push publishes ({e}); nothing pushed",
                  file=sys.stderr)
            return 2
        why = refusal(ref, messages, None, emails)
        if why:
            print(f"ref_privacy: REFUSE: {why} would publish this host; nothing pushed", file=sys.stderr)
            return 3
        return 0
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
