#!/usr/bin/env python3
"""Stamp a release on main. This is the only way a version number is assigned.

    python tools/release/stamp.py --bump patch|minor --title "<what shipped>" [--push] [--dry-run]
    python tools/release/stamp.py --self-test

Versions are assigned at merge time, never in a branch: four branches each
picking "the next version" once cost real cycles, and a stamp that skipped a
claim file turned main red. So every rule below is a refusal, not a warning:

  1. The working tree is a checkout of origin/main (fetched), clean except for
     RELEASE_NOTES.md -- the stamper writes the notes section by hand first.
  2. The Tests workflow for HEAD has completed and succeeded (fast + closures),
     so a release never publishes ahead of the unscoped gate. --allow-red
     overrides, loudly, for a red main whose cause is already understood.
     Read through `gh run list` when gh is installed and through the REST
     API when it is not; both paths reduce to one verdict, so the refusal
     is the same sentence with the same override either way. A source that
     cannot answer at all -- no gh and no network -- is a not-green verdict
     with its reason, never an exception: rule 2 is a refusal, and a
     refusal that crashes instead cannot be overridden.
  3. The next version is greater than VERSION and than every existing tag, and
     its tag exists neither locally nor on origin.
  4. RELEASE_NOTES.md opens with a '## v<next>' section whose body mentions
     every PR merged since the last tag -- a stamp covers everything
     unstamped, whoever merged it. The merges are read off main's own
     --first-parent line, in both subject shapes main has produced
     ('Merge pull request #N from ...' and a trailing '(#N)'), and a window
     the rule could not attribute refuses instead of enumerating empty: an
     enumerator that silently finds nothing cannot reject notes that omit
     everything.
  5. (rule "rows") Every merged pull request in the window this tag is about to
     close has a disposition -- `record`'s own predicate, re-applied before the
     tag moves the anchor past it. The window is the one rule 4 reads
     (`<last v* tag>..HEAD`, first-parent) and the instrument is
     `tests/delivery_status.py --require-rows`, which answers it from git alone
     so a stamp needs no token. This is the countermeasure to #1301 (D11-02):
     the deploy-key tag push is main-protect's only bypass, so a stamp was the
     one event that could close a window over rowless merges and make them
     unreachable -- the next window starts after the merge, and no later run
     ever sees it again. Three consecutive stamps did exactly that (v6.6.7 over
     4/4, v6.6.6 over 9/16, v6.6.5 over 7/9) while the instrument, asked only
     for what was OVERDUE, read zero. --allow-rowless overrides, loudly, for a
     window whose rows are owed and knowingly deferred, and it prints the
     instrument's own pending list, so the merges a stamp orphans are named in
     its log rather than only in a later window that cannot see them.

  6. manifest.json's version equals VERSION before the stamp (a botched
     earlier stamp is fixed by hand, not papered over here).
  7. (rule "claims") The stamp commit passes `tests/env_drift.py --claims-only
     HEAD^1` -- the claims check main's own push run applies to it -- before
     anything is pushed, with or without --push. v6.6.0's commit failed that
     check and only main's push run found out. A refusal deletes the local
     tag, resets to the pre-stamp HEAD keeping RELEASE_NOTES.md, prints the
     check's output and exits 2. --dry-run makes no commit, so it never runs.

  8. (rule "register") The D6 register (tools/audit/round4/D6/) is
     re-recorded through its own generator, claims.py, from the tree being
     stamped. One row of it -- C42, "manifest version equals VERSION" -- is a
     snapshot of VERSION, and tests/harness_headers.py re-runs that generator
     on every push and fails when the committed register is not what it
     produces, so a stamp that moves VERSION and leaves the register behind is
     RED at the stamped head. A generator that fails refuses before the commit,
     with every file this stamp wrote put back. --dry-run writes nothing, so it
     never runs.

--push-key PATH pushes the commit and the tag over a deploy key to the SSH URL
instead of to origin (#954): main-protect's only bypass is that key (decision
0009 steps 5 and 6), so a direct push to main lands over it and nothing else. The
key and its pinned host file are checked before rule 1, and a key push that is
refused is never retried as origin.

What it writes: VERSION, the manifest version, CARD_VERSION in the bundled
card (console banner only -- card_drift.mjs is unchanged), both claim files
(the `claims-for:` stamp moves to the new version, the reason block is
rewritten, and every bare claim line is deleted -- a stamp empties the list,
the next branch restates its own footprint), and the D6 register re-recorded
from that tree by its own generator (rule "register"), then one commit and one
tag, which rule 7 checks before any push. Nothing is pushed without --push.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import re
import shlex
import shutil
import stat
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = ROOT / "VERSION"
MANIFEST = ROOT / "custom_components" / "heatpump_optimizer" / "manifest.json"
CARD_JS = (
    ROOT / "custom_components" / "heatpump_optimizer" / "www" / "heatpump-optimizer-card.js"
)
NOTES = ROOT / "RELEASE_NOTES.md"
CARD_VERSION_RE = re.compile(r'const CARD_VERSION = "\d+\.\d+\.\d+";')
CLAIM_FILES = (
    ROOT / "tests" / "golden" / "claimed_drift.txt",
    ROOT / "tests" / "golden" / "card_claimed_drift.txt",
)
# The D6 register: the committed output of claims.py, which tests/
# harness_headers.py re-runs (it declares `live-header`) and requires
# byte-identical to the committed files. One of its rows -- C42, "manifest
# version equals VERSION" -- is a snapshot of VERSION, so a stamp that moves
# VERSION and leaves the register behind is RED at the stamped head. The stamp
# re-records it through the generator itself, rather than editing the version
# row by hand, so a register that acquires another version-bearing row cannot
# silently drift behind the stamp that wrote it.
REGISTER_DIR = ROOT / "tools" / "audit" / "round4" / "D6"
REGISTER_GENERATOR = REGISTER_DIR / "claims.py"
REGISTER_FILES = (REGISTER_DIR / "claims.json", REGISTER_DIR / "claims.md")
# claims.py runs from ROOT (its ROOT = Path(".")), inserts tests/ and
# custom_components/ onto sys.path itself, and needs only the Home Assistant
# stub a stamp's checkout cannot be assumed to import.
REGISTER_PYTHONPATH = "tests/hastub"
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
# Rule 4's population: the pull requests merged into main since the last tag.
# It is read off main's OWN first-parent line (window_log_args below), and a
# subject there has taken two shapes, so both are matched. The squash form is
# END-ANCHORED on purpose: `fix(#960): ...` is a branch commit naming an
# ISSUE, and an unanchored search over branch commits read seven of those as
# merged pull requests, one of them still open.
PR_RE = re.compile(r"\(#(\d+)\)\s*$")
MERGE_SUBJECT_RE = re.compile(r"^Merge pull request #(\d+)\b")
# The stamper's own commit. It carries no pull request by construction, and it
# lands inside a later window whenever a tag push failed (the rc=3 fallback
# leaves the commit behind), so it is excluded before the blindness alarm
# below counts what it could not attribute.
STAMP_SUBJECT_RE = re.compile(r"^v\d+\.\d+\.\d+: stamp\b")
# %h/%p/%s, unit-separated. The parent count is how a merge is recognised as
# one -- git says so, where a subject regex only guesses.
WINDOW_FORMAT = "%h%x1f%p%x1f%s"
# Rule 2's gate. gh answers it when gh is installed; when it is not, the same
# question goes straight to the REST API, which needs the repository spelled
# out: a stamp is taken from a checkout of this repository by definition, and
# reading the slug back off `git remote` would make the gate depend on how the
# checkout was cloned rather than on which repository it is.
GITHUB_API = "https://api.github.com"
REPO = "tvofi/heatpump_optimizer"
TESTS_WORKFLOW = "Tests"
TESTS_WORKFLOW_FILE = "tests.yml"
GATE_RUN_LIMIT = 5
GATE_TIMEOUT_S = 30.0
# The deploy-key push. The URL is derived from REPO, never read off or written
# to `origin`: worktrees share one repository config, so `git remote set-url`
# or a `-c` override there would re-point every sibling checkout's push. The
# key reaches ssh through the subprocess environment only.
KEY_PUSH_URL = f"git@github.com:{REPO}.git"
DEFAULT_KNOWN_HOSTS = "~/.zcode/github_known_hosts"
# A key push that cannot reach port 22 fails instead of hanging after the stamp
# commit and tag exist locally.
SSH_CONNECT_TIMEOUT_S = 30


class Refuse(SystemExit):
    def __init__(self, rule: int | str, why: str) -> None:
        super().__init__(f"stamp refused (rule {rule}): {why}")


def sh(*args: str, check: bool = True, env: dict | None = None) -> str:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=check,
                          env=env).stdout


# --- the push, to origin or over the deploy key -------------------------------

def push_key_problem(key: str, known_hosts: str) -> str | None:
    """Why the deploy key cannot be used, or None.

    The key must be a file of mode exactly 600: ssh refuses a looser one at
    push time, which is after the stamp commit and tag exist locally. The
    pinned host file must exist and be writable by its owner only, because a
    host file anyone can rewrite pins nothing. Neither path may be empty or
    carry whitespace, a quote or `%`: ssh re-parses `-o UserKnownHostsFile=` on
    its own and expands `%` tokens in both paths, so such a path fails at push
    time even though the shell quoting holds.
    """
    if not key or not known_hosts:
        return "the deploy key and the known_hosts path must both be non-empty"
    key_path, hosts_path = Path(key).expanduser(), Path(known_hosts).expanduser()
    for label, path in (("deploy key", key_path), ("known_hosts file", hosts_path)):
        if any(ch.isspace() or ch in "'\"%" for ch in str(path)):
            return (f"{label} path {str(path)!r} carries whitespace, a quote or %, "
                    "which ssh re-splits or expands")
    if not key_path.is_file():
        return f"deploy key {key_path} does not exist or is not a file"
    if not hosts_path.is_file():
        return f"known_hosts file {hosts_path} does not exist or is not a file"
    key_mode = stat.S_IMODE(key_path.stat().st_mode)
    if key_mode != 0o600:
        return f"deploy key {key_path} is mode {key_mode:o}, not 600"
    hosts_mode = stat.S_IMODE(hosts_path.stat().st_mode)
    if hosts_mode & 0o022:
        return f"known_hosts file {hosts_path} is mode {hosts_mode:o}; group or others can rewrite it"
    return None


def key_ssh_command(key: str, known_hosts: str) -> str:
    """The GIT_SSH_COMMAND the deploy-key push runs under, as measured on #201."""
    return (f"ssh -i {shlex.quote(str(Path(key).expanduser()))} -o IdentitiesOnly=yes "
            f"-o UserKnownHostsFile={shlex.quote(str(Path(known_hosts).expanduser()))} "
            f"-o StrictHostKeyChecking=yes -o ConnectTimeout={SSH_CONNECT_TIMEOUT_S}")


def push_via(refspec: str, key: str | None = None, known_hosts: str | None = None,
             runner=None, environ=None) -> str:
    """Push one refspec: to origin with no key, exactly as before; over the key
    to KEY_PUSH_URL otherwise. There is no fallback between the two -- after
    the bypass narrows, an origin retry is a refused push mid-release."""
    runner = runner or sh
    if key is None:
        return runner("git", "push", "origin", refspec)
    env = dict(os.environ if environ is None else environ)
    env["GIT_SSH_COMMAND"] = key_ssh_command(key, known_hosts or DEFAULT_KNOWN_HOSTS)
    return runner("git", "push", KEY_PUSH_URL, refspec, env=env)


def refresh_origin(runner=None) -> str | None:
    """Fetch origin after a key push. A push to origin updates origin/main as it
    goes; a push to a URL does not, so without this the checkout still reads
    main as the pre-stamp commit. Returns a warning rather than raising: the
    stamp is already public when this runs."""
    try:
        (runner or sh)("git", "fetch", "origin", "--quiet")
    except subprocess.CalledProcessError as exc:
        why = (exc.stderr or "").strip().splitlines()
        return "could not refresh origin after the key push: " + (why[-1] if why else "git fetch failed")
    return None


# --- pure pieces (covered by --self-test) -----------------------------------

def bump(version: str, part: str) -> str:
    major, minor, patch = (int(x) for x in version.strip().split("."))
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    raise ValueError(part)


def version_tuple(v: str) -> tuple[int, int, int]:
    a, b, c = (int(x) for x in v.strip().lstrip("v").split("."))
    return a, b, c


def notes_section(text: str, version: str) -> str | None:
    """Body of the '## v<version>' section, which must be the first section."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if line.strip() != f"## v{version}":
                return None
            body: list[str] = []
            for rest in lines[i + 1:]:
                if rest.startswith("## v"):
                    break
                body.append(rest)
            return "\n".join(body).strip()
    return None


def pr_from_subject(subject: str) -> str | None:
    """The pull request a first-parent commit on main carries, or None.

    Two shapes, because main has produced both: GitHub's merge commit
    (`Merge pull request #N from ...`) and the squash subject (`... (#N)`).
    Which one is in force is a per-merge choice nothing in this repository
    pins, so rule 4 reads both rather than the one that was current when it
    was written.
    """
    merge = MERGE_SUBJECT_RE.match(subject)
    if merge:
        return merge.group(1)
    squash = PR_RE.search(subject)
    return squash.group(1) if squash else None


def merged_prs(subjects: list[str]) -> set[str]:
    return {pr for pr in (pr_from_subject(s) for s in subjects) if pr}


def window_log_args(last_tag: str, head: str = "HEAD") -> list[str]:
    """Rule 4's window: main's own commits, never the merged branches'.

    Without --first-parent the log walks into every merged branch, so the
    subjects read are the branch author's rather than main's merges -- which
    both loses the merges (a merge subject is not in the branch) and invents
    pull requests out of issue references in branch commit messages.
    """
    return ["git", "log", f"{last_tag}..{head}", "--first-parent",
            f"--format={WINDOW_FORMAT}"]


def parse_window(raw: str) -> list[tuple[str, int, str]]:
    """(abbreviated sha, parent count, subject) per first-parent commit.

    A non-empty line that does not carry WINDOW_FORMAT's three fields is
    REFUSED, not skipped. Skipping it returns the same empty list a clean
    empty window returns, and that is the failure path this whole change
    exists to close (#1041 comment 5693093076): the derivation that produces
    the population a check quantifies over must not answer "nothing merged"
    when it means "I could not read this". The first version of this function
    had the bare `continue`, written by a seat that had just read that
    analysis, which is how durable the shape is.
    """
    rows = []
    for line in raw.splitlines():
        if not line:
            continue
        parts = line.split("\x1f", 2)
        if len(parts) != 3:
            raise Refuse(4, f"git log --first-parent returned a line rule 4 cannot read: "
                            f"{line!r}. A window that cannot be read is not an empty one.")
        sha, parents, subject = parts
        rows.append((sha, len(parents.split()), subject))
    return rows


def blind_merges(window: list[tuple[str, int, str]]) -> list[tuple[str, str]]:
    """(sha, subject) for window merges no pull request could be read from.

    A commit with two or more parents on main's first-parent line is a merge
    by git's own account, so one whose subject yields no number is a merge
    this rule cannot quantify over. It is named and refused rather than
    dropped from the population, which is how the enumerator went blind in
    the first place.
    """
    return [(sha, subject) for sha, parents, subject in window
            if parents >= 2 and pr_from_subject(subject) is None]


def enumeration_went_blind(window: list[tuple[str, int, str]],
                           prs: set[str], blind: list[tuple[str, str]]) -> bool:
    """True when the window holds commits and the rule attributed nothing.

    Zero pull requests means either `nothing merged` or `the subject shapes
    above no longer describe main`, and a rule that cannot tell those apart
    passes notes that omit everything. Stamp commits are excluded because
    they carry no pull request by construction; `blind` is excluded because
    those are already refused by name, with their own message.

    The one shape that fires this honestly-but-unhelpfully is a window whose
    every commit was pushed to main directly with no pull request at all.
    That is a release worth a human look, so it refuses rather than guessing.
    """
    unstamped = [row for row in window if not STAMP_SUBJECT_RE.match(row[2])]
    return bool(unstamped) and not prs and not blind


def rule4_problem(window: list[tuple[str, int, str]], body: str,
                  last_tag: str, nxt: str) -> str | None:
    """Rule 4's whole verdict on one window and one notes body.

    Returns the refusal's reason, or None. It is a function rather than a run
    of statements inside main() because rule 4 had no way to be exercised
    without taking a release: the enumerator underneath it read the wrong
    commits for twenty-five merges and nothing could run it to find out.
    """
    prs = merged_prs([subject for _, _, subject in window])
    blind = blind_merges(window)
    if enumeration_went_blind(window, prs, blind):
        return (f"read no merged pull request from any of the {len(window)} commit(s) on main "
                f"since {last_tag}; rule 4 cannot reject notes that omit a merge it never saw, "
                f"so it refuses rather than pass. Newest subject: {window[0][2]!r}")
    unnamed = [(sha, subject) for sha, subject in blind if sha not in body]
    if unnamed:
        return (f"merged into main since {last_tag} with no pull request in the subject, and not "
                f"named by sha in the v{nxt} notes: "
                + "; ".join(f"{sha} {subject!r}" for sha, subject in unnamed))
    missing = sorted((pr for pr in prs if not re.search(rf"#{pr}(?!\d)", body)), key=int)
    if missing:
        return f"merged since {last_tag} but not mentioned in the v{nxt} notes: #{', #'.join(missing)}"
    return None


def rewrite_card_version(text: str, new_version: str) -> tuple[str, str | None]:
    """Replace CARD_VERSION in the bundled card. Returns (new_text, old_version)."""
    match = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', text)
    if not match:
        raise ValueError("no CARD_VERSION constant in card")
    old = match.group(1)
    new_text, n = CARD_VERSION_RE.subn(
        f'const CARD_VERSION = "{new_version}";', text, count=1
    )
    if n != 1:
        raise ValueError("could not rewrite CARD_VERSION")
    return new_text, old


def rewrite_claims(text: str, new_version: str, title: str) -> tuple[str, str | None, int]:
    """Move the stamp, rewrite the reason block, delete every bare claim.

    Returns (new_text, old_stamp, deleted_claims). The reason block is the run
    of comment lines that follows `# claims-for:` up to the first blank line;
    `# may-drift:` lines sit after a blank line and are never touched.
    """
    lines = text.splitlines()
    out: list[str] = []
    old_stamp = None
    deleted = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^# claims-for:\s*(\S+)", line)
        if m:
            old_stamp = m.group(1)
            out.append(f"# claims-for: {new_version}")
            out.append("#")
            out.append(f"# v{new_version}: {title}. The stamp empties the list; the")
            out.append("# next branch restates its own footprint, claims included.")
            out.append("#")
            i += 1
            while i < len(lines) and lines[i].startswith("#") and not lines[i].startswith("# may-drift:"):
                i += 1
            continue
        if line.strip() and not line.startswith("#"):
            deleted += 1
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out) + "\n", old_stamp, deleted


def runs_url(head: str, repo: str = REPO, api: str = GITHUB_API) -> str:
    """The REST query rule 2 asks: this commit's push runs, newest first."""
    return f"{api}/repos/{repo}/actions/runs?head_sha={head}&event=push"


def rest_headers(token: str | None) -> dict[str, str]:
    """The repository is public, so the unauthenticated query works too; a
    GH_TOKEN only buys the higher rate limit."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "heatpump-optimizer-stamp",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def is_tests_run(run: dict) -> bool:
    """gh selects the gate by workflow name; so do we, and by the workflow
    file as well, so a renamed `name:` does not silently select nothing."""
    return ((run.get("name") or "").strip() == TESTS_WORKFLOW
            or (run.get("path") or "").rsplit("/", 1)[-1] == TESTS_WORKFLOW_FILE)


def runs_from_payload(payload: dict, limit: int = GATE_RUN_LIMIT) -> list[dict]:
    """Reduce a /actions/runs payload to exactly what `gh run list --json
    status,conclusion,databaseId --limit 5` returns, so the verdict below
    cannot tell the two paths apart. The API answers newest first."""
    runs = [{"status": r.get("status"), "conclusion": r.get("conclusion"), "databaseId": r.get("id")}
            for r in (payload.get("workflow_runs") or []) if is_tests_run(r)]
    return runs[:limit]


def gate_verdict(runs: list[dict]) -> tuple[bool, str]:
    """(green, why) for rule 2, from either path's runs."""
    done = [r for r in runs if r["status"] == "completed"]
    green = any(r["conclusion"] == "success" for r in done)
    pending = [r for r in runs if r["status"] != "completed"]
    why = ("no completed Tests run for HEAD yet" if not done else
           f"Tests for HEAD concluded {[r['conclusion'] for r in done]}")
    if pending:
        why += f"; {len(pending)} run(s) still in progress"
    return green, why


def gate_source(which=shutil.which) -> str:
    """Which path rule 2 takes. gh when it is on PATH, REST when it is not --
    decided here rather than by a subprocess raising FileNotFoundError from
    under the check, which is how a missing binary used to outrank
    --allow-red."""
    return "gh" if which("gh") else "rest"


def self_test() -> int:
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        ok &= cond
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    check("bump patch", bump("6.2.12", "patch") == "6.2.13")
    check("bump minor", bump("6.2.12", "minor") == "6.3.0")
    check("tag order", version_tuple("v6.2.12") > version_tuple("v6.2.9"))
    notes = "# Notes\n\n## v6.2.13\n\n### T\n\nB (#170) and (#171).\n\n## v6.2.12\n\nold\n"
    check("notes: first section found", notes_section(notes, "6.2.13") == "### T\n\nB (#170) and (#171).")
    check("notes: wrong version is None", notes_section(notes, "6.2.14") is None)
    check("merged prs", merged_prs(["A (#170)", "B (#171)", "stamp"]) == {"170", "171"})

    # Rule 4's enumeration. Both halves of the defect it replaces are pinned:
    # the merges it did not see, and the issue numbers it invented. A window
    # in the shape main produces today -- GitHub merge commits -- plus one
    # squash subject, one branch-style subject naming an issue, and the
    # stamper's own commit.
    check("subjects: a merge commit names its pull request",
          pr_from_subject("Merge pull request #1052 from tvofi/fix/d11-pins") == "1052")
    check("subjects: a squash subject names its pull request",
          pr_from_subject("fix: read the entity unit (#969)") == "969")
    check("subjects: an issue reference is not a merged pull request",
          pr_from_subject("fix(#960): cap the fallback") is None)
    check("subjects: a trailing issue list is not read as one number",
          pr_from_subject("W1-G15: judge may-drift keys (#254, W1-G15)") is None)
    check("subjects: the stamper's own commit carries none",
          pr_from_subject("v6.5.0: stamp the wave-4 close") is None)
    check("subjects: #16 is not read out of (#165)",
          pr_from_subject("something (#165)") == "165")
    mixed = ["Merge pull request #1052 from tvofi/fix/d11-pins",
             "fix: read the entity unit (#969)",
             "fix(#960): cap the fallback",
             "v6.4.4: stamp the round"]
    check("merged prs: both shapes, and nothing invented",
          merged_prs(mixed) == {"1052", "969"})

    # The window is main's own first-parent line. Reading every commit of
    # every merged branch is what produced both halves of the defect, so the
    # flag is pinned here rather than left to the call site's spelling.
    check("window: the log is first-parent",
          "--first-parent" in window_log_args("v6.5.0"))
    check("window: the log spans last tag to head",
          "v6.5.0..HEAD" in window_log_args("v6.5.0"))
    check("window: the format carries sha, parents and subject",
          f"--format={WINDOW_FORMAT}" in window_log_args("v6.5.0")
          and WINDOW_FORMAT.count("%x1f") == 2)
    parsed = parse_window("abc1234\x1fdef5678 9012345\x1fMerge pull request #7 from x/y\n"
                          "bbb2222\x1faaa1111\x1ffix: a thing (#8)\n")
    check("window: a merge is recognised by its parent count",
          parsed == [("abc1234", 2, "Merge pull request #7 from x/y"),
                     ("bbb2222", 1, "fix: a thing (#8)")])
    check("window: a subject carrying the separator keeps it",
          parse_window("abc1234\x1faaa1111\x1ffix: a\x1fb") == [("abc1234", 1, "fix: a\x1fb")])
    check("window: an empty log is an empty window", parse_window("") == [])
    try:
        parse_window("abc1234\x1fdef5678 9012345\x1fMerge pull request #7 from x/y\n"
                     "a-line-with-no-separators\n")
        check("window: an unreadable line refuses, it is not dropped", False)
    except Refuse as _pw:
        # Dropping it would return the list a clean run returns, minus a
        # commit -- the silent-zero shape this change exists to close.
        check("window: an unreadable line refuses, it is not dropped",
              "cannot read" in str(_pw) and "rule 4" in str(_pw))
    try:
        parse_window("every-line-unreadable\nand-this-one-too\n")
        check("window: an all-unreadable log refuses rather than reading empty", False)
    except Refuse:
        check("window: an all-unreadable log refuses rather than reading empty", True)

    # The blindness alarm. Its own null control is the healthy window: a rule
    # whose alarm never fires is the failure it exists to catch.
    healthy = [("aaa1111", 2, "Merge pull request #1052 from tvofi/a"),
               ("bbb2222", 2, "Merge pull request #1051 from tvofi/b")]
    blind_window = [("aaa1111", 2, "Landed the D11 pins"),
                    ("bbb2222", 2, "Landed the ledger fix")]
    check("blind: a healthy window raises no alarm",
          not enumeration_went_blind(healthy, merged_prs([s for _, _, s in healthy]),
                                     blind_merges(healthy)))
    check("blind: a healthy window names no unattributable merge",
          blind_merges(healthy) == [])
    check("blind: a merge with no number in its subject is named, not dropped",
          blind_merges(blind_window) == [("aaa1111", "Landed the D11 pins"),
                                         ("bbb2222", "Landed the ledger fix")])
    check("blind: a named merge is refused by name, not by the empty-set alarm",
          not enumeration_went_blind(blind_window, set(), blind_merges(blind_window)))
    squashed_away = [("aaa1111", 1, "landed the D11 pins"),
                     ("bbb2222", 1, "landed the ledger fix")]
    check("blind: a window that attributed nothing at all refuses",
          enumeration_went_blind(squashed_away,
                                 merged_prs([s for _, _, s in squashed_away]),
                                 blind_merges(squashed_away)))
    check("blind: an empty window is not blind, it is empty",
          not enumeration_went_blind([], set(), []))
    stamp_only = [("aaa1111", 1, "v6.5.0: stamp the wave-4 close")]
    check("blind: a window holding only the stamper's own commit is not blind",
          not enumeration_went_blind(stamp_only, set(), []))

    # Rule 4's verdict itself, on one window, both ways round. These are the
    # arms the defect had backwards: notes that omit a real merge passed, and
    # honest notes were refused until they mentioned issue numbers that never
    # merged.
    _w = [("aaa1111", 2, "Merge pull request #1052 from tvofi/fix/d11-pins"),
          ("bbb2222", 2, "Merge pull request #1051 from tvofi/record"),
          ("ccc3333", 1, "fix(#960): a branch commit that never merged alone")]
    check("rule 4: complete notes pass",
          rule4_problem(_w, "Shipped #1052 and #1051.", "v6.5.0", "6.5.1") is None)
    check("rule 4: notes omitting a merge are refused, naming it",
          "#1051" in (rule4_problem(_w, "Shipped #1052.", "v6.5.0", "6.5.1") or ""))
    check("rule 4: an issue number is never demanded of the notes",
          "#960" not in (rule4_problem(_w, "Shipped #1052 and #1051.", "v6.5.0", "6.5.1") or ""))
    _blindw = [("aaa1111", 2, "Landed the D11 pins")]
    check("rule 4: an unattributable merge refuses, naming its sha",
          "aaa1111" in (rule4_problem(_blindw, "Shipped things.", "v6.5.0", "6.5.1") or ""))
    check("rule 4: naming that sha in the notes clears it",
          rule4_problem(_blindw, "Shipped aaa1111, a merge with no pull request.",
                        "v6.5.0", "6.5.1") is None)
    check("rule 4: a window it could attribute nothing in refuses",
          "no merged pull request" in
          (rule4_problem([("aaa1111", 1, "landed the pins")], "anything", "v6.5.0", "6.5.1") or ""))
    check("rule 4: an empty window passes, as it did before",
          rule4_problem([], "anything", "v6.5.0", "6.5.1") is None)

    # Where the window comes from. Every pure piece above is correct while the
    # caller still hand-rolls its own `git log` without the flag -- which is
    # exactly the tree this replaced -- so rule 4's region is read.
    # rindex for the same reason the tag-push contract below uses it: the
    # literal occurs in this check's own source, earlier in the file.
    _r4_src = pathlib.Path(__file__).read_text()
    _r4 = _r4_src[_r4_src.rindex("# Rule 4: the notes section"):]
    _r4 = _r4[:_r4.index("# Rule 5:")]
    check("rule 4: the window comes from window_log_args", "window_log_args(" in _r4)
    check("rule 4: the call site builds no log of its own", '"git", "log"' not in _r4)
    check("rule 4: the verdict comes from rule4_problem", "rule4_problem(" in _r4)
    claims = (
        "# header\n#\n# claims-for: 6.2.12\n#\n# The old reason.\n#\n\n"
        "# may-drift: wood_coil -- machine-sensitive\n"
        "capacity_tariff_15min  # moved\n"
    )
    new, old, deleted = rewrite_claims(claims, "6.2.13", "the test")
    check("claims: old stamp read", old == "6.2.12")
    check("claims: one bare claim deleted", deleted == 1)
    check("claims: new stamp present", "# claims-for: 6.2.13" in new)
    check("claims: may-drift kept", "# may-drift: wood_coil" in new)
    check("claims: old reason gone", "old reason" not in new)
    check("claims: no bare lines", all(not l.strip() or l.startswith("#") for l in new.splitlines()))
    tight = "# claims-for: 6.2.12\n# reason\n# may-drift: wood_coil -- x\nfoo  # claim\n"
    new2, _, deleted2 = rewrite_claims(tight, "6.2.13", "t")
    check("claims: may-drift survives without a blank line", "# may-drift: wood_coil" in new2 and deleted2 == 1)
    card = 'const CARD_VERSION = "5.4.20";\n'
    card_new, card_old = rewrite_card_version(card, "6.3.13")
    check("card: old version read", card_old == "5.4.20")
    check("card: new version written", 'const CARD_VERSION = "6.3.13";' in card_new)
    try:
        rewrite_card_version("no version here", "6.3.13")
        check("card: missing constant refuses", False)
    except ValueError:
        check("card: missing constant refuses", True)
    check("notes: #16 is not covered by #165", not re.search(r"#16(?!\d)", "fixed in #165"))
    check("tags: pre-release tags are ignored", not TAG_RE.match("v6.2.15-rc1") and bool(TAG_RE.match("v6.2.15")))

    # Rule 2's evidence, on both paths. gh is not installed everywhere a
    # release is taken from, and rule 2 used to call it before --allow-red
    # was read -- a missing binary raised FileNotFoundError instead of
    # refusing. These cover the pure pieces of the fallback: the URL, the
    # reduction of a runs payload to a verdict, and which path is taken.
    check("rule 2: the rest query", runs_url("abc123") ==
          "https://api.github.com/repos/tvofi/heatpump_optimizer/actions/runs?head_sha=abc123&event=push")
    check("rule 2: a token becomes a bearer header", rest_headers("t123")["Authorization"] == "Bearer t123")
    check("rule 2: no token, no header (the repository is public)", "Authorization" not in rest_headers(None))
    payload = {"total_count": 3, "workflow_runs": [
        {"id": 11, "name": "Tests", "path": ".github/workflows/tests.yml",
         "status": "completed", "conclusion": "success"},
        {"id": 12, "name": "Card", "path": ".github/workflows/card.yml",
         "status": "completed", "conclusion": "failure"},
        {"id": 13, "name": "Tests", "path": ".github/workflows/tests.yml",
         "status": "in_progress", "conclusion": None},
    ]}
    reduced = runs_from_payload(payload)
    check("rule 2: the payload reduces to gh's shape", reduced == [
        {"status": "completed", "conclusion": "success", "databaseId": 11},
        {"status": "in_progress", "conclusion": None, "databaseId": 13}])
    check("rule 2: another workflow's run is not the gate", all(r["databaseId"] != 12 for r in reduced))
    check("rule 2: a completed success is green", gate_verdict(reduced)[0])
    red = runs_from_payload({"workflow_runs": [
        {"id": 21, "name": "Tests", "status": "completed", "conclusion": "failure"}]})
    red_green, red_why = gate_verdict(red)
    check("rule 2: a red run refuses, naming the conclusion", not red_green and "failure" in red_why)
    queued = runs_from_payload({"workflow_runs": [
        {"id": 31, "name": "Tests", "status": "queued", "conclusion": None}]})
    check("rule 2: a run still going is counted, not awaited", gate_verdict(queued) ==
          (False, "no completed Tests run for HEAD yet; 1 run(s) still in progress"))
    check("rule 2: no run at all", gate_verdict([]) == (False, "no completed Tests run for HEAD yet"))
    check("rule 2: gh's shape and rest's reduce to one verdict",
          gate_verdict([{"status": "completed", "conclusion": "failure", "databaseId": 21}]) == gate_verdict(red))
    check("rule 2: the five newest Tests runs, as gh's --limit", len(runs_from_payload(
        {"workflow_runs": [{"id": i, "name": "Tests", "status": "completed", "conclusion": "success"}
                           for i in range(9)]})) == 5)
    check("rule 2: gh is used when it is installed", gate_source(lambda name: "/usr/bin/gh") == "gh")
    check("rule 2: rest is used when gh is absent", gate_source(lambda name: None) == "rest")

    def _no_gh(head: str) -> list[dict]:
        raise FileNotFoundError(2, "No such file or directory: 'gh'")

    unreadable = tests_gate("deadbee", which=lambda name: None, fetchers={"rest": _no_gh})
    check("rule 2: a source that cannot answer refuses, it does not raise",
          not unreadable[0] and "could not read the Tests gate" in unreadable[1])

    # The tag-push fallback is a control-flow contract, so it is pinned by
    # reading this file: a failed tag push must not raise past the caller,
    # must not roll the commit back, and must leave an exit code the caller
    # can tell apart from success.
    # rindex, not index: the literal searched for also occurs in this very
    # check, so a forward search matches the check's own source and pins
    # nothing -- the exact failure tests/README.md describes as a test
    # asserting against its own copy. The last occurrence is the real one.
    src = pathlib.Path(__file__).read_text()
    tail = src[src.rindex('push_via(f"v{nxt}"'):]
    guarded = tail[:tail.index("RESULT stamped=")]
    check("tag push: the failure is caught, not raised",
          "except subprocess.CalledProcessError" in guarded)
    check("tag push: a failed tag push does not roll the commit back",
          "reset" not in guarded)
    check("tag push: the caller can tell it apart from success", "return 3" in tail)
    check("tag push: the recovery names the Release workflow",
          "Dispatch the Release" in tail and "creates the tag" in tail)
    # The deploy-key push (#954, decision 0009 step 5). Once main-protect's
    # admin bypass is narrowed to pull requests, a direct push to main lands
    # only over the deploy key, so these pin the three things that failure
    # would be silent about: the key reaches ssh through the subprocess
    # environment and nowhere else, the push targets the SSH URL rather than
    # origin, and a refused key push is never retried as origin.
    calls: list[tuple[tuple, dict]] = []

    def _record(*a, **kw):
        calls.append((a, kw))
        return ""

    push_via("HEAD:main", runner=_record)
    check("push: --push alone is today's command, unchanged",
          calls == [(("git", "push", "origin", "HEAD:main"), {})])
    calls.clear()
    push_via("HEAD:main", "/k/stamp.key", "/k/hosts", runner=_record, environ={"PATH": "/bin"})
    (_argv, _kw), = calls
    check("push: over the key, the target is the SSH URL",
          _argv == ("git", "push", "git@github.com:tvofi/heatpump_optimizer.git", "HEAD:main"))
    check("push: over the key, origin is never named", "origin" not in _argv)
    check("push: over the key, no config is written or overridden",
          not any(a in ("-c", "config", "remote") for a in _argv))
    _env = _kw.get("env") or {}
    check("push: the ssh command reaches the subprocess environment",
          _env.get("GIT_SSH_COMMAND") == key_ssh_command("/k/stamp.key", "/k/hosts"))
    check("push: the caller's environment is kept beside it", _env.get("PATH") == "/bin")
    _ssh = key_ssh_command("/k/stamp.key", "/k/hosts")
    check("push: the ssh command pins the key, the host file and strict checking",
          all(part in _ssh for part in ("-i /k/stamp.key", "IdentitiesOnly=yes",
                                         "UserKnownHostsFile=/k/hosts",
                                         "StrictHostKeyChecking=yes")))
    # ssh keeps the FIRST value of an option, in any of its spellings (`-oKey=v`,
    # `-o 'Key v'`), so no parse of the options pins them: the whole string is.
    check("push: the ssh command is exactly the measured one, options in order",
          _ssh == "ssh -i /k/stamp.key -o IdentitiesOnly=yes -o UserKnownHostsFile=/k/hosts "
                  "-o StrictHostKeyChecking=yes -o ConnectTimeout=30")
    check("push: a path with a space is quoted, not split",
          "-i '/k/my key'" in key_ssh_command("/k/my key", "/k/hosts"))
    calls.clear()

    def _refused(*a, **kw):
        calls.append((a, kw))
        raise subprocess.CalledProcessError(1, a, "", "remote: Cannot update this protected ref")

    try:
        push_via("HEAD:main", "/k/stamp.key", "/k/hosts", runner=_refused, environ={})
        check("push: a refused key push raises", False)
    except subprocess.CalledProcessError:
        check("push: a refused key push raises", True)
    check("push: a refused key push is never retried as origin",
          len(calls) == 1 and all("origin" not in a for a, _ in calls))
    calls.clear()
    check("push: after a key push, origin is fetched so origin/main shows the stamp",
          refresh_origin(runner=_record) is None
          and calls == [(("git", "fetch", "origin", "--quiet"), {})])
    check("push: a failed refresh is reported, not raised",
          "could not refresh" in (refresh_origin(runner=_refused) or ""))

    import tempfile
    with tempfile.TemporaryDirectory() as _d:
        _key, _hosts = Path(_d) / "stamp.key", Path(_d) / "hosts"
        _key.write_text("k")
        _hosts.write_text("h")
        _key.chmod(0o600)
        _hosts.chmod(0o644)
        check("key: a 600 key and a pinned host file pass",
              push_key_problem(str(_key), str(_hosts)) is None)
        check("key: a missing key refuses, naming it",
              "does not exist" in (push_key_problem(str(Path(_d) / "nope"), str(_hosts)) or ""))
        check("key: a missing known_hosts refuses, naming it",
              "known_hosts" in (push_key_problem(str(_key), str(Path(_d) / "nope")) or ""))
        _key.chmod(0o644)
        check("key: a key readable by others refuses, naming the mode",
              "644" in (push_key_problem(str(_key), str(_hosts)) or ""))
        _key.chmod(0o400)
        check("key: a key that is not exactly 600 refuses",
              "400" in (push_key_problem(str(_key), str(_hosts)) or ""))
        _key.chmod(0o600)
        _hosts.chmod(0o666)
        check("key: a host file others can rewrite refuses",
              "666" in (push_key_problem(str(_key), str(_hosts)) or ""))
        _hosts.chmod(0o644)
        check("key: an empty key path refuses",
              "non-empty" in (push_key_problem("", str(_hosts)) or ""))
        for _bad in ("sp ace", "quo'te", 'dq"te', "tab\tbed", "pct%h"):
            _odd = Path(_d) / _bad
            _odd.write_text("h")
            _odd.chmod(0o600)
            check(f"key: a known_hosts path with {_bad!r} refuses before push time",
                  "whitespace, a quote or %" in (push_key_problem(str(_key), str(_odd)) or ""))
            check(f"key: a key path with {_bad!r} refuses before push time",
                  "whitespace, a quote or %" in (push_key_problem(str(_odd), str(_hosts)) or ""))

    # Where main() pushes from. Every pure piece above is correct while the
    # call site still builds its own `git push origin` -- so the region is read.
    _push_src = pathlib.Path(__file__).read_text()
    _pr = _push_src[_push_src.rindex("    if args.push:"):]
    _pr = _pr[:_pr.index("RESULT stamped=v{nxt} tag_pushed={")]
    check("push: main pushes the branch and the tag only through push_via",
          _pr.count("push_via(") == 2 and '"git", "push"' not in _pr)
    check("push: both pushes carry the key arguments",
          _pr.count("args.push_key, args.known_hosts") == 2)
    # rindex: main() is the last function, and these literals also occur in
    # this check's own source above it.
    _pre = _push_src[_push_src.rindex("    args = ap.parse_args()"):]
    _pre = _pre[:_pre.index("    # Rule 1: a fetched, clean checkout")]
    check("push: the key is checked before rule 1, and a problem refuses",
          "problem = push_key_problem(args.push_key, args.known_hosts)" in _pre
          and "if problem:" in _pre and 'raise Refuse("push-key"' in _pre)
    check("push: an empty --push-key is checked, not skipped as falsy",
          "    if args.push_key is not None:\n        problem = push_key_problem" in _pre)
    check("push: main refreshes origin after a key push",
          "        if args.push_key is not None:\n            warning = refresh_origin()" in _pr)
    # Before the tag push: that push may fail and `return 3`, and origin/main
    # must show the stamp commit either way.
    check("push: the refresh runs before the tag push",
          -1 < _pr.find("warning = refresh_origin()") < _pr.find('push_via(f"v{nxt}"'))

    # The claims self-check (after v6.6.0). main's push run refused that
    # stamp's commit with `env_drift.py --claims-only HEAD^1`; the stamp now
    # runs the same check on its own commit before anything is pushed.
    check("claims self-check: the command is main's push-run check against HEAD^1",
          claims_selfcheck_argv("py") == ["py", "tests/env_drift.py", "--claims-only", "HEAD^1"])

    class _Proc:
        def __init__(self, rc: int, out: str) -> None:
            self.returncode, self.stdout, self.stderr = rc, out, ""

    check("claims self-check: exit 0 passes",
          claims_selfcheck(lambda argv: _Proc(0, "claims hygiene: HEAD^1 ok\n"))
          == (True, "claims hygiene: HEAD^1 ok"))
    check("claims self-check: exit 1 refuses, carrying the refusal",
          claims_selfcheck(lambda argv: _Proc(1, "RECORD PR CLAIMS: no\n")) == (False, "RECORD PR CLAIMS: no"))
    check("claims self-check: a crash is not a pass",
          not claims_selfcheck(lambda argv: _Proc(2, ""))[0])

    def _unstartable(argv):
        raise FileNotFoundError(2, "No such file")

    check("claims self-check: a check that cannot start refuses",
          not claims_selfcheck(_unstartable)[0])

    # The disposition gate, rule "rows" (#1301/D11-02). The stamp is the one
    # writer whose push MOVES the window `record` reads -- `<last v* tag>`
    # ..origin/main, over the deploy-key bypass -- so it re-applies record's
    # own predicate before it writes anything. The instrument is the ledger
    # this repository already builds, read under `--require-rows` (PENDING
    # refuses), which answers from git and needs no token.
    check("rows gate: the command is the token-free disposition instrument, over this window",
          disposition_gate_argv("v6.6.1", "py")
          == ["py", "tests/delivery_status.py", "--require-rows", "--since", "v6.6.1"])
    check("rows gate: with no tag yet it asks over the whole of origin/main",
          disposition_gate_argv(None, "py")
          == ["py", "tests/delivery_status.py", "--require-rows"])
    _rows_rowless = ("DELIVERY STATUS OK -- 0 rowed, 1 pending, 0 overdue "
                     "(overdue at 12 commits)\n  pending  #1301 0abc123 the merge")
    check("rows gate: a rowless window refuses, carrying the instrument's own list",
          disposition_gate("v6.6.1", lambda argv: _Proc(1, _rows_rowless))
          == (False, _rows_rowless))
    check("rows gate: a fully rowed window clears",
          disposition_gate("v6.6.1",
                           lambda argv: _Proc(0, "DELIVERY STATUS OK -- 3 rowed, 0 pending, 0 overdue"))
          == (True, "DELIVERY STATUS OK -- 3 rowed, 0 pending, 0 overdue"))
    check("rows gate: a crash is not a pass",
          not disposition_gate("v6.6.1", lambda argv: _Proc(2, ""))[0])
    check("rows gate: a check that cannot start refuses",
          not disposition_gate("v6.6.1", _unstartable)[0])

    # Where main() runs it. Every pure piece above is correct while the call
    # site never runs the gate -- which is exactly the tree before this change
    # -- so rule 5's region is read: the gate must run before the manifest
    # rule, and the one way past it must be the explicit, named override.
    _r5 = _r4_src[_r4_src.rindex("# Rule 5: the window"):]
    _r5 = _r5[:_r5.index("# Rule 6:")]
    check("rows gate: main() runs the disposition gate, before the manifest rule",
          "disposition_gate(last_tag)" in _r5)
    check("rows gate: the override is explicit, and only --allow-rowless takes it",
          "--allow-rowless" in _r5 and 'raise Refuse("rows"' in _r5)

    # Rule "register". The stamp re-records the D6 register through its own
    # generator -- the header's command, from ROOT, with the stub on
    # PYTHONPATH -- and a generator that fails refuses rather than ship the
    # stale register the rule exists to prevent.
    check("register: the generator is claims.py, run from ROOT",
          register_argv("py") == ["py", "tools/audit/round4/D6/claims.py"])
    check("register: the stub is put on PYTHONPATH, the caller's kept after it",
          register_env({"PATH": "/bin"})["PYTHONPATH"] == "tests/hastub"
          and register_env({"PYTHONPATH": "/x"})["PYTHONPATH"]
          == "tests/hastub" + os.pathsep + "/x")
    check("register: a generator that exits 0 passes",
          regenerate_register(
              lambda a: _Proc(0, "RESULT claims_extracted=125 claims\n")) is None)
    try:
        regenerate_register(lambda a: _Proc(1, "FALSE        C105  docs\n  the last line"))
        check("register: a generator that fails refuses, naming its last line", False)
    except Refuse as _reg:
        check("register: a generator that fails refuses, naming its last line",
              "register" in str(_reg) and "the last line" in str(_reg) and "exit 1" in str(_reg))

    def _unstartable_register(argv):
        raise FileNotFoundError(2, "No such file")

    try:
        regenerate_register(_unstartable_register)
        check("register: a generator that cannot start refuses", False)
    except Refuse as _reg2:
        check("register: a generator that cannot start refuses", "could not run" in str(_reg2))

    # publish_stamp with doubles for every collaborator, so both arms run the
    # real control flow and nothing is pushed. `events` is the order things
    # happened in: the self-check must come before any push.
    class _Args:
        push, push_key, known_hosts = True, "/k/stamp.key", "/k/hosts"

    def _publish(selfcheck_result, args=_Args):
        events: list = []

        def _push(refspec, key=None, hosts=None):
            events.append(("push", refspec, key, hosts))
            return ""

        def _check():
            events.append(("selfcheck",))
            return selfcheck_result

        def _undo(nxt, pre_head):
            events.append(("undo", nxt, pre_head))

        def _refresh():
            events.append(("refresh",))
            return None

        try:
            # Its RESULT line is a real stamp's, so it is kept out of this output.
            with contextlib.redirect_stdout(io.StringIO()):
                rc = publish_stamp(args, "6.6.2", "pre1234", push_via=_push, refresh_origin=_refresh,
                                   claims_selfcheck=_check, undo_local_stamp=_undo,
                                   sh=lambda *a, **kw: events.append(("sh",) + a) or "")
        except Refuse as exc:
            return events, str(exc)
        return events, rc

    _ev, _res = _publish((False, "RECORD PR CLAIMS: refused"))
    check("claims self-check: a refused stamp commit pushes nothing",
          not any(e[0] == "push" for e in _ev))
    check("claims self-check: a refused stamp commit is undone to the pre-stamp head",
          ("undo", "6.6.2", "pre1234") in _ev)
    check("claims self-check: a refused stamp exits non-zero, printing the refusal",
          isinstance(_res, str) and "rule claims" in _res and "RECORD PR CLAIMS: refused" in _res)
    _ev, _res = _publish((True, "claims hygiene: HEAD^1 ok"))
    check("claims self-check: a good stamp still pushes the branch, then the tag, over the key",
          _res == 0 and [e for e in _ev if e[0] == "push"] ==
          [("push", "HEAD:main", "/k/stamp.key", "/k/hosts"), ("push", "v6.6.2", "/k/stamp.key", "/k/hosts")])
    check("claims self-check: a good stamp is not undone", not any(e[0] == "undo" for e in _ev))
    check("claims self-check: it runs before the first push",
          ("selfcheck",) in _ev and _ev.index(("selfcheck",)) < next(
              i for i, e in enumerate(_ev) if e[0] == "push"))

    class _NoPush:
        push, push_key, known_hosts = False, None, "/k/hosts"

    _ev, _res = _publish((False, "refused"), _NoPush)
    check("claims self-check: a local stamp without --push is checked and undone too",
          ("undo", "6.6.2", "pre1234") in _ev and isinstance(_res, str))

    # The undo, on a real throwaway repository: no tag, no stamp commit, and
    # the hand-written notes kept, uncommitted, over the pre-stamp tree.
    with tempfile.TemporaryDirectory() as _gd:
        _genv = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                 "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
                 "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        for _k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            _genv.pop(_k, None)

        def _git(*a, **kw):
            return subprocess.run(a, cwd=_gd, text=True, capture_output=True, check=True, env=_genv).stdout

        _notes, _ver = Path(_gd) / "RELEASE_NOTES.md", Path(_gd) / "VERSION"
        _git("git", "init", "-q")
        _notes.write_text("# Notes\n")
        _ver.write_text("6.6.1\n")
        _git("git", "add", "-A")
        _git("git", "commit", "-q", "-m", "base")
        _pre = _git("git", "rev-parse", "HEAD").strip()
        _notes.write_bytes(b"# Notes\r\n\r\n## v6.6.2\r\n\r\nShipped #1.\r\n")
        _ver.write_text("6.6.2\n")
        _git("git", "add", "-A")
        _git("git", "commit", "-q", "-m", "v6.6.2: stamp t")
        _git("git", "tag", "v6.6.2")
        undo_local_stamp("6.6.2", _pre, runner=_git, notes=_notes)
        check("undo: the local tag is gone", _git("git", "tag", "--list").strip() == "")
        check("undo: HEAD is the pre-stamp commit", _git("git", "rev-parse", "HEAD").strip() == _pre)
        check("undo: the stamp's other writes are reverted", _ver.read_text() == "6.6.1\n")
        check("undo: the notes are kept, uncommitted",
              _notes.read_bytes() == b"# Notes\r\n\r\n## v6.6.2\r\n\r\nShipped #1.\r\n"
              and _git("git", "status", "--porcelain").strip() == "M RELEASE_NOTES.md")

    # Where main() calls it, and the null control: --dry-run returns before
    # the commit, so it writes nothing and never reaches the self-check.
    _main_src = _push_src[_push_src.rindex("    args = ap.parse_args()"):]
    check("claims self-check: main publishes only through publish_stamp, after the tag",
          -1 < _main_src.find('sh("git", "tag", f"v{nxt}")')
          < _main_src.find("return publish_stamp(args, nxt, head)")
          and "push_via(" not in _main_src)
    _dry_help = _push_src[_push_src.rindex('    ap.add_argument("--dry-run"'):].split("\n", 2)
    _dry_help = _dry_help[0] + _dry_help[1]
    check("claims self-check: --dry-run's help says it skips the claims check",
          "every check" not in _dry_help and "no claims check" in _dry_help)
    check("claims self-check: --dry-run returns before the commit and the self-check",
          -1 < _main_src.find("if args.dry_run:") < _main_src.find('sh("git", "commit"')
          < _main_src.find("return publish_stamp("))

    # Rule "register", at its call site. Every pure piece above is correct while
    # main() stops calling the generator -- which is the stale register exactly
    # as it was -- so the region between the version writes and the commit is
    # read: it must re-record the register, stage it, and put the stamp's own
    # writes back (never the notes) when the generator fails.
    _wrote = _main_src[_main_src.index("    VERSION_FILE.write_text(nxt"):]
    _wrote = _wrote[:_wrote.index('sh("git", "commit"')]
    check("register: main re-records the register before it commits, and stages it",
          "regenerate_register()" in _wrote and "REGISTER_FILES" in _wrote)
    _recover = (_wrote[_wrote.index('sh("git", "checkout"'):_wrote.index('sh("git", "add"')]
                if 'sh("git", "checkout"' in _wrote else "")
    check("register: its failure path restores the stamp's writes and keeps the notes",
          "REGISTER_FILES" in _recover and "NOTES" not in _recover)
    print(f"RESULT stamp_self_test={'pass' if ok else 'fail'}")
    return 0 if ok else 1


# --- rule 2's two sources ----------------------------------------------------

def fetch_runs_gh(head: str) -> list[dict]:
    return json.loads(sh("gh", "run", "list", "--workflow", TESTS_WORKFLOW, "--commit", head,
                         "--event", "push", "--json", "status,conclusion,databaseId",
                         "--limit", str(GATE_RUN_LIMIT)))


def fetch_runs_rest(head: str) -> list[dict]:
    request = urllib.request.Request(runs_url(head), headers=rest_headers(os.environ.get("GH_TOKEN")))
    with urllib.request.urlopen(request, timeout=GATE_TIMEOUT_S) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return runs_from_payload(payload)


def tests_gate(head: str, which=shutil.which, fetchers: dict | None = None) -> tuple[bool, str]:
    """Rule 2's evidence, from gh or from REST. Never raises: a source that
    cannot answer is a not-green verdict carrying its reason, so --allow-red
    governs 'the gate says red' and 'nothing here can read the gate' alike."""
    source = gate_source(which)
    fetch = (fetchers or {"gh": fetch_runs_gh, "rest": fetch_runs_rest})[source]
    try:
        runs = fetch(head)
    except Exception as exc:  # every failure to read is a verdict, never a crash
        stderr = getattr(exc, "stderr", None)  # gh's own complaint, when it is gh
        detail = stderr.strip().splitlines()[-1] if stderr else f"{type(exc).__name__}: {exc}"
        return False, f"could not read the Tests gate for HEAD via {source}: {detail}"
    return gate_verdict(runs)


# --- the D6 register, re-recorded before the commit (rule "register") --------

def register_argv(python: str = sys.executable) -> list[str]:
    """claims.py's own command, spelled from ROOT.

    The path is relative on purpose: claims.py sets ``ROOT = pathlib.Path(".")``
    and refuses the ``__file__`` route (tools/audit/README.md, "A harness at the
    evidence tag may measure the tag, not your tree"), so it is correct only
    when its working directory is the checkout being stamped.
    """
    return [python, str(REGISTER_GENERATOR.relative_to(ROOT))]


def register_env(environ: dict | None = None) -> dict:
    """The environment claims.py runs under: tests/hastub on PYTHONPATH.

    Its own header runs it that way, and its ``sys.path`` inserts supply the
    other two entries. Any PYTHONPATH the caller already has is kept after it,
    so the stamp neither depends on nor discards the caller's environment.
    """
    env = dict(os.environ if environ is None else environ)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = REGISTER_PYTHONPATH + (os.pathsep + existing if existing else "")
    return env


def regenerate_register(runner=None, python: str | None = None) -> None:
    """Re-record the D6 register from the tree this stamp is about to commit.

    It runs after VERSION, the manifest and the card are written and before the
    commit, so the register it produces records the version being stamped. Any
    exit other than 0 refuses: a register the stamp could not regenerate is the
    stale register this step exists to prevent, and committing it would put
    main back where the rule exists to take it from. A generator that cannot be
    started refuses the same way -- a stamp nothing re-recorded is the failure,
    not a warning.
    """
    argv = register_argv(python or sys.executable)
    run = runner or (lambda a: subprocess.run(a, cwd=ROOT, text=True,
                                             capture_output=True, env=register_env()))
    try:
        proc = run(argv)
    except OSError as exc:
        raise Refuse("register", f"could not run the D6 register generator: {exc}") from exc
    if proc.returncode != 0:
        tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
        raise Refuse("register",
                     f"{REGISTER_GENERATOR.relative_to(ROOT)} failed with exit "
                     f"{proc.returncode}: " + (tail[-1] if tail else "no output"))


# --- after the commit: the claims self-check, then the push ------------------

# The check main's own push run applies to a stamp: tests/run.sh always runs
# `env_drift.py --claims-only "$GOLDEN_REF"`, and tests.yml sets GOLDEN_REF to
# HEAD^1 on a push to main. Run against the freshly made stamp commit, HEAD^1
# is the origin/main this stamp was taken on, so the verdict is the one that
# push run would print -- before the push instead of after it. v6.6.0 was
# refused by exactly this check, and only main's push run found out.
CLAIMS_SELFCHECK_REF = "HEAD^1"


def claims_selfcheck_argv(python: str = sys.executable) -> list[str]:
    return [python, "tests/env_drift.py", "--claims-only", CLAIMS_SELFCHECK_REF]


def claims_selfcheck(runner=None) -> tuple[bool, str]:
    """(passed, what it printed) for the stamp commit at HEAD.

    Any exit other than 0 is a refusal: env_drift returns 1 for a claims
    refusal, and a crash is not a pass. A check that cannot be started at
    all is a refusal too -- a stamp nothing verified is the failure this
    exists to stop."""
    run = runner or (lambda argv: subprocess.run(argv, cwd=ROOT, text=True, capture_output=True))
    try:
        proc = run(claims_selfcheck_argv())
    except OSError as exc:
        return False, f"could not run the claims check: {exc}"
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output or f"exit {proc.returncode}, no output"


# Rule "rows": the disposition gate (#1301/D11-02). The same predicate the
# `record` job applies to `main`, re-run here -- before the stamp commit is
# made -- because this tool is the one writer whose push can MOVE the window
# `record` reads. `<last v* tag>..origin/main` is `record`'s window, the
# deploy-key tag push is main-protect's only bypass, so a stamp taken over a
# rowless merge is the one event that can make that merge unreachable: the
# next window starts after the merge, and no later run ever sees it. That is
# not hypothetical -- v6.6.7 closed over 4/4 rowless merges, v6.6.6 over 9/16,
# v6.6.5 over 7/9, and the instrument, asked only what was OVERDUE, read zero
# each time, because at stamp time every merge in the window is minutes old
# and therefore PENDING.
#
# The instrument is `tests/delivery_status.py --require-rows`: the ledger this
# repository already builds, read under `record`'s bar instead of the
# delivery-status lane's. It answers from git (the merge log and the row
# files) and needs no token, so a stamp -- which runs with a deploy key and
# no API credential -- can run it. `--allow-rowless` is the deliberate
# override, in the same shape as `--allow-red`: for a window whose rows are
# owed and knowingly deferred, it prints what it is deferring and stamps.
DISPOSITION_GATE_SCRIPT = "tests/delivery_status.py"


def disposition_gate_argv(last_tag: str | None, python: str = sys.executable) -> list[str]:
    argv = [python, DISPOSITION_GATE_SCRIPT, "--require-rows"]
    if last_tag:
        argv += ["--since", last_tag]
    return argv


def disposition_gate(last_tag: str | None, runner=None) -> tuple[bool, str]:
    """(cleared, what it printed) for the window the tag is about to close.

    `record`'s predicate, asked from git alone: every merged pull request in
    `<last tag>..origin/main` carries a disposition. With no tag yet the whole
    of origin/main is asked, which is the same window `record` would have read.
    Any exit other than 0 is a refusal -- the predicate returns 1 for a window
    with an unrowed merge, and a crash is not a pass. A gate that cannot be
    started at all is a refusal too: a stamp nothing checked is the failure
    this exists to stop."""
    run = runner or (lambda argv: subprocess.run(argv, cwd=ROOT, text=True, capture_output=True))
    try:
        proc = run(disposition_gate_argv(last_tag))
    except OSError as exc:
        return False, f"could not run the disposition check: {exc}"
    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, output or f"exit {proc.returncode}, no output"


def undo_local_stamp(nxt: str, pre_head: str, runner=None, notes: Path = NOTES) -> None:
    """Discard the local stamp commit and tag, keeping the hand-written notes.

    The tree returns to `pre_head` -- the origin/main the stamp was taken on --
    with RELEASE_NOTES.md as the stamper left it before running, uncommitted,
    so a corrected run starts from what rule 1 accepts."""
    runner = runner or sh
    kept = notes.read_bytes()  # bytes, so line endings come back exactly as written
    runner("git", "tag", "-d", f"v{nxt}")
    runner("git", "reset", "-q", "--hard", pre_head)
    notes.write_bytes(kept)


def publish_stamp(args, nxt: str, head: str, push_via=push_via, refresh_origin=refresh_origin,
                  claims_selfcheck=claims_selfcheck, undo_local_stamp=undo_local_stamp,
                  sh=sh) -> int:
    """Everything after the stamp commit and tag exist locally.

    The collaborators are parameters so --self-test can drive this path with
    doubles and never push; their defaults are the real functions, under the
    same names, so main's call is the production path unchanged."""
    # The claims self-check runs first, on every stamp that made a commit and
    # before anything leaves this checkout. A refused commit is discarded here,
    # while it is still local, rather than found by main's push run.
    passed, output = claims_selfcheck()
    if not passed:
        undo_local_stamp(nxt, head)
        raise Refuse("claims", "the stamp commit fails `env_drift.py --claims-only "
                               f"{CLAIMS_SELFCHECK_REF}`, the check main's push run applies; "
                               f"nothing was pushed, the commit and tag v{nxt} were discarded "
                               "and RELEASE_NOTES.md is kept. The check said:\n" + output)
    print(f"claims self-check: {output.splitlines()[-1]}")
    if args.push:
        # main moves between fetch and push when another session is merging.
        # A rejected push must leave nothing behind: no local tag that would
        # make the retry refuse under rule 3, no stamp commit off main.
        try:
            push_via("HEAD:main", args.push_key, args.known_hosts)
        except subprocess.CalledProcessError as exc:
            sh("git", "tag", "-d", f"v{nxt}")
            sh("git", "reset", "--hard", "origin/main")
            raise Refuse(1, "push to main was rejected (main moved, or the pushing identity was "
                            "refused); the stamp commit and tag were "
                            "discarded -- fetch, rewrite the notes for the new HEAD, run again: "
                            + exc.stderr.strip().splitlines()[-1]) from exc
        if args.push_key is not None:
            warning = refresh_origin()
            if warning:
                print(f"WARNING: {warning}", file=sys.stderr)
        # The tag push is the one step that can fail AFTER the commit is
        # already public, and in some environments it always does: push
        # credentials scoped to branches get 403 on refs/tags while
        # refs/heads succeeds. Raising here left the stamp half-done and
        # quiet -- the version commit on main, the tag local only, and so
        # no GitHub Release at all, because release.yml triggers on the tag
        # push. v6.3.10 and v6.3.11 both went missing exactly that way
        # before anyone thought to look at the releases page.
        #
        # So this failure is reported rather than raised, and the caller is
        # pointed at the recovery release.yml already documents for the
        # branch-scoped case: dispatch it with the tag name and it creates
        # the tag at the commit it runs on. Nothing is rolled back -- the
        # commit belongs on main either way, and rule 3 refuses a second
        # stamp of a version that is already there.
        try:
            push_via(f"v{nxt}", args.push_key, args.known_hosts)
        except subprocess.CalledProcessError as exc:
            why = (exc.stderr or "").strip().splitlines()
            print(f"RESULT stamped=v{nxt} tag_pushed=false")
            print(f"WARNING: v{nxt} is committed on main but its tag was NOT pushed: "
                  + (why[-1] if why else "git push failed"), file=sys.stderr)
            print(f"         There is no GitHub Release yet. Dispatch the Release "
                  f"workflow with tag=v{nxt} at this commit -- it creates the tag "
                  f"itself -- or push refs/tags/v{nxt} from a checkout whose "
                  f"credentials allow it.", file=sys.stderr)
            return 3
    print(f"RESULT stamped=v{nxt} tag_pushed={'true' if args.push else 'false'}")
    return 0


# --- the stamp ---------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bump", choices=("patch", "minor"))
    ap.add_argument("--title", help="what shipped, for the commit subject and the claim files")
    ap.add_argument("--push", action="store_true", help="push the commit and the tag to origin")
    ap.add_argument("--push-key", metavar="PATH",
                    help="with --push: push over this deploy key to the SSH URL, never to origin")
    ap.add_argument("--known-hosts", metavar="PATH", default=DEFAULT_KNOWN_HOSTS,
                    help="the pinned GitHub host key file for --push-key (default: %(default)s)")
    ap.add_argument("--dry-run", action="store_true",
                    help="run rules 1-6 and print the plan; write nothing, so no commit and no claims check")
    ap.add_argument("--allow-red", action="store_true", help="stamp even though HEAD's gate is not green")
    ap.add_argument("--allow-rowless", action="store_true",
                    help="stamp even though the window the tag closes holds a merge with no "
                         "disposition row; the instrument's own list is printed as the warning")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.bump or not args.title:
        ap.error("--bump and --title are required (or --self-test)")
    if args.push_key is not None and not args.push:
        ap.error("--push-key only means something with --push")
    if args.push_key is not None:
        problem = push_key_problem(args.push_key, args.known_hosts)
        if problem:
            raise Refuse("push-key", problem + "; nothing was written, and origin is not a fallback")

    # Rule 1: a fetched, clean checkout of origin/main.
    sh("git", "fetch", "origin", "--quiet", "--tags")
    head = sh("git", "rev-parse", "HEAD").strip()
    main = sh("git", "rev-parse", "origin/main").strip()
    if head != main:
        raise Refuse(1, f"HEAD {head[:7]} is not origin/main {main[:7]}; stamps go on main only")
    dirty = [l for l in sh("git", "status", "--porcelain").splitlines() if l.strip()]
    if any(not l.endswith("RELEASE_NOTES.md") for l in dirty):
        raise Refuse(1, f"working tree has changes beyond RELEASE_NOTES.md: {dirty}")

    # Rule 2: HEAD's unscoped gate is green, read through gh or through REST.
    # One verdict, one refusal, one override, whichever source answered.
    green, why = tests_gate(head)
    if not green:
        if not args.allow_red:
            raise Refuse(2, why + " (wait, or --allow-red with the cause understood)")
        print(f"WARNING: stamping a main whose gate is not green: {why}")

    # Rule 3: the next version is new, and above every tag.
    current = VERSION_FILE.read_text().strip()
    nxt = bump(current, args.bump)
    tags = [t for t in sh("git", "tag", "--list").split() if TAG_RE.match(t)]
    remote = [t for t in (l.split("refs/tags/")[1] for l in sh("git", "ls-remote", "--tags", "origin").splitlines()
                            if "refs/tags/v" in l and not l.endswith("^{}")) if TAG_RE.match(t)]
    if f"v{nxt}" in tags or f"v{nxt}" in remote:
        raise Refuse(3, f"tag v{nxt} already exists")
    top = max((version_tuple(t) for t in tags + remote), default=(0, 0, 0))
    if version_tuple(nxt) <= top:
        raise Refuse(3, f"next version {nxt} is not above the highest tag {'.'.join(map(str, top))}")
    last_tag = "v" + ".".join(map(str, top)) if top != (0, 0, 0) else None

    # Rule 4: the notes section exists and covers every merged PR.
    body = notes_section(NOTES.read_text(), nxt)
    if not body:
        raise Refuse(4, f"RELEASE_NOTES.md must open with a non-empty '## v{nxt}' section")
    window = parse_window(sh(*window_log_args(last_tag))) if last_tag else []
    why = rule4_problem(window, body, last_tag or "the first commit", nxt)
    if why:
        raise Refuse(4, why)

    # Rule 5: the window this tag closes holds no merged pull request without
    # a disposition. Rules 1-4 ask whether the NOTES are ready; this asks
    # about the WINDOW. `<last v* tag>..origin/main` is the window `record`
    # reads, and the tag push below is main-protect's only bypass, so this run
    # is the one writer that can carry a rowless merge out of every future
    # window at once (#1301/D11-02: three consecutive stamps did, while the
    # instrument, asked only what was OVERDUE, read zero). `record`'s own
    # predicate is re-applied here, before anything is written, so the refusal
    # costs a stamp rather than a permanent hole in the ledger. It reads git
    # and the row files and needs no token, so it runs under --dry-run too --
    # a dry run says whether the stamp would be refused, which is most of what
    # a dry run is for.
    cleared, why = disposition_gate(last_tag)
    if not cleared:
        if not args.allow_rowless:
            raise Refuse("rows",
                         "the window this tag would close holds a merged pull request "
                         "with no disposition. Tagging moves "
                         f"{last_tag or 'the first commit'}..origin/main past it, no later "
                         "window can see it again, and `record` would never report it. Row it "
                         "(the merge commit's body names the pull request), or pass "
                         "--allow-rowless to defer the rows knowingly. Nothing was written; "
                         "the instrument said:\n" + why)
        print(f"WARNING: stamping over a window with undispositioned merges "
              f"(--allow-rowless): {why}")
    else:
        print(f"disposition gate: {why.splitlines()[0] if why.splitlines() else why}")

    # Rule 6: the manifest agrees with VERSION before we move both.
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("version") != current:
        raise Refuse(6, f"manifest version {manifest.get('version')} != VERSION {current}; fix by hand first")

    card_before = CARD_JS.read_text()
    card_match = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', card_before)
    if not card_match:
        raise Refuse(6, "could not read CARD_VERSION from the bundled card")
    card_current = card_match.group(1)

    plan = [
        f"VERSION {current} -> {nxt}",
        f"manifest version -> {nxt}",
        f"CARD_VERSION {card_current} -> {nxt}",
    ]
    claim_edits = []
    for path in CLAIM_FILES:
        new, old, deleted = rewrite_claims(path.read_text(), nxt, args.title)
        if old != current:
            print(f"WARNING: {path.name} was stamped {old}, not {current}; restamping anyway")
        claim_edits.append((path, new))
        plan.append(f"{path.relative_to(ROOT)}: claims-for {old} -> {nxt}, {deleted} claim(s) deleted")
    plan.append(f"{REGISTER_DIR.relative_to(ROOT)}: re-recorded from the stamped tree "
                f"by {REGISTER_GENERATOR.name}")
    plan.append(f"commit 'v{nxt}: stamp {args.title}' and tag v{nxt}" + (" (pushed)" if args.push else " (not pushed)"))
    print("stamp plan:")
    for p in plan:
        print(f"  - {p}")
    if args.dry_run:
        print("dry run: nothing written")
        return 0

    VERSION_FILE.write_text(nxt + "\n")
    text = MANIFEST.read_text()
    text, n = re.subn(r'"version":\s*"[^"]+"', f'"version": "{nxt}"', text, count=1)
    if n != 1:
        raise Refuse(6, "could not rewrite the manifest version")
    MANIFEST.write_text(text)
    card_text, _ = rewrite_card_version(card_before, nxt)
    CARD_JS.write_text(card_text)
    for path, new in claim_edits:
        path.write_text(new)
    try:
        regenerate_register()
    except Refuse:
        # Nothing is committed yet, so a failed regeneration is one checkout
        # away from the pre-stamp tree: put back every file this stamp wrote
        # (the generator may have left a partial write of its own) and keep the
        # hand-written notes, so a corrected run starts from what rule 1
        # accepts.
        sh("git", "checkout", "--", str(VERSION_FILE), str(MANIFEST), str(CARD_JS),
           *map(str, CLAIM_FILES), *map(str, REGISTER_FILES))
        raise
    sh("git", "add", str(VERSION_FILE), str(MANIFEST), str(CARD_JS), str(NOTES),
       *map(str, CLAIM_FILES), *map(str, REGISTER_FILES))
    sh("git", "commit", "-q", "-m",
       f"v{nxt}: stamp {args.title}\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>")
    sh("git", "tag", f"v{nxt}")
    return publish_stamp(args, nxt, head)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refuse as e:
        print(e, file=sys.stderr)
        sys.exit(2)
