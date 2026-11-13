#!/usr/bin/env python3
"""The fix reviewer's packet: the facts a review gathers, rendered once at the frozen head.

    review_packet.py render --pr N --head SHA --out FILE [--main REF] [--reviewed-head SHA]
                            [--harness PATH | --harness-file FILE] [--harness-arg A]...
    review_packet.py check FILE --head SHA     (rc 1: the packet names another head)
    review_packet.py handoff --topic T --body FILE [--main REF] [--roster-ref REF]
    review_packet.py --self-test

`bus.sh dispatch` renders it (owner ruling tvofi 2026-10-24, card 8) and names
its path in the reviewer's brief. The packet holds the three-dot diff against
the merge base, a digest of the head's check runs AS READ (pending, green, red
or none, with each run's id: the owner rejected waiting for the gate, card 5, so
the reviewer re-reads the live state before a verdict), `carry_audit.py` and
`figure_lint.mjs` at the head, the finder's harness output at the base and at
the head when one is named (`none named` and `not run` otherwise), and the
mutation-ledger diff. Nothing in it reads a clock, so a second render over the
same facts is byte-identical.

A LATER ROUND IS ITS DELTA (tvofi, 2026-11-09; fix-review.md step 12). With
`--reviewed-head <rh>` (`bus.sh dispatch` passes its own), the packet holds
`git diff <rh> <head>` and the VERDICT.md of the latest verdict/<pr> commit
whose first line names <rh>, in place of the three-dot diff. A first round, an
<rh> that is not an ancestor of the head, or one no verdict names keeps the
three-dot diff and says which (`review_scope`).

WHICH CHECKOUT. Every git read runs in the checkout the WORKING DIRECTORY is in,
never in the directory this module is installed under: `bus.sh dispatch` runs
the renderer where it dispatches (a cloud dispatch does so in a throwaway
clone), and reading the install resolves the head in the wrong repository. A
working directory outside a checkout is refused, never silently redirected.

INDEPENDENCE. The harness run is the finder's: a path present at the merge base
and untouched by the diff, run from the base's bytes at both ends, or a file
outside the tree cited by its sha1 (`fixer.md` step 3's baseline export). A
harness the diff adds or edits is the fixer's, and the render refuses it.

REFUSALS (rc 1, each named by its signal), all mechanical:
  carry-audit      `carry_audit.py check` returns 1 on the body (unrouted or bad);
  head-note        `## Head` does not name the dispatched head;
  figure-lint      `figure_lint.mjs --pr-body` exits non-zero on the body (unverified is
                   not refused, as `fixer.md` step 3 reads it);
  moved-head       the pull request's head is no longer the dispatched head;
  structure        `tests/structure.py` refuses the head merged with main;
  red-unanswered   a CONCLUDED red check the body's `## Red checks` does not name
                   (`policy_lint.mjs --pr-body --red`);
  required-red     a required context's latest run concluded failure and
                   `merge_train.py classify --pr`, which decides, reads it RED or
                   cannot be read; APPROVAL-OWED (P345: only a budget raise's
                   approval, which follows the review) prints `approval-owed`,
                   WAIT or GREEN (a provisional red, P436; #3379) prints
                   `required-wait`/`required-green`, each an advisory instead;
  host-path        the body or an added line names this host (`ref_privacy.py`);
  hot-file         the diff shares a HOT_FILES path with an open pull request
                   whose merge verdict is at its head and not on the train;
  carry-landed     a body line `Carry N ... landed ... <sha>` whose carry is not on the round
                   roster ref at that sha (`landed_cites`, `unlanded_carries`; L5);
  handoff-not-applied  the PR's branch is `fix/<t>` or `fix/<t>-pr`, `handoff/<t>`
                   exists on origin, and its tip is not an ancestor of the head.
A pending check never refuses. Every other finding prints as an advisory.

AT THE HANDOFF (P256). `body_push.sh` runs `handoff` at the code head before
the body is pushed, so a fixer answers before the open what dispatch would
refuse after it: `structure` and `hot-file` as above, and `brief-carries`, each
carry on the group's roster entry (the round roster, `group_for_branch` of
`handoff/<topic>`) not named `Carry N` in the body. Same exit codes as `render`.

EVIDENCE IS NEVER WITHHELD. A refusal that leaves the packet truthful still
WRITES it and then exits 1, so whoever holds a refused dispatch reads the same
facts the reviewer would have: `bus.sh dispatch` dies on the rc and records
nothing, which is the dispatch gate. `host-path` alone writes nothing -- the
packet carries the three-dot diff, so writing it copies the host path into a
file that travels to a reviewer.

UNAVAILABLE (rc 3, nothing written). A seat that cannot READ the packet's
inputs -- its working directory is not a checkout, `git` cannot resolve the
base or the head, `gh` is absent or has no token, a tool the packet runs is
missing, `--out` is unwritable -- is not refusing the head. It prints one
`review_packet: UNAVAILABLE: <why>` line and exits 3, and `bus.sh dispatch`
names no packet, says why, and dispatches anyway. A dispatch must never be
blocked by an aid it could not produce.
`HPO_BUS_GH` replaces `gh` (the self-test's stub); `HPO_BUS_TRAIN_STATE` is the
merge train's state dir, read for what is boarded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
import proof_watch  # noqa: E402  (the one Python reader of the verdict grammar)
import ref_privacy  # noqa: E402

class Unavailable(Exception):
    """The packet's INPUTS are absent in this seat, not its facts bad.

    A refusal (`REFUSE <signal>`) says the dispatched head is not fit to review;
    `UNAVAILABLE` says this seat cannot render the packet at all -- no checkout,
    no `gh`, no token, no network, an unwritable path. The two are different
    worlds, so they get different exit codes: `render` exits 1 for a refusal and
    3 for `UNAVAILABLE`, and `bus.sh dispatch` refuses the dispatch on the first
    but names no packet and proceeds on the second. The packet is an aid to a
    reviewer; a dispatch with no way to render one must still dispatch, and say
    why rather than go silent.
    """


_REPO_ROOT: Path | None = None


def repo() -> Path:
    """The checkout this run reads: the one the working directory is in.

    Never the tool's install. `bus.sh dispatch` runs the renderer in the
    checkout it dispatches for, and that is not always the checkout the tool
    lives in -- cloud_dispatch's self-test dispatches from a throwaway clone.
    Reading the install there resolves the head in the wrong repository, and
    `git merge-base origin/main <head>` dies with `Not a valid commit name
    <head>` although `origin/main` itself is present.
    """
    global _REPO_ROOT
    if _REPO_ROOT is None:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        if r.returncode or not r.stdout.strip():
            raise Unavailable("the working directory is not inside a git checkout")
        _REPO_ROOT = Path(r.stdout.strip())
    return _REPO_ROOT


REPO = os.environ.get("HPO_BUS_REPO", "tvofi/heatpump_optimizer")
#: `gate` is the one required check (`.github/workflows/ci.yml`).
REQUIRED = ("gate",)
#: Files whose concurrent edits have cost a re-review (R10-ORCH-DISPATCH-REG carry [7]).
HOT_FILES = ("tools/audit/seat/pr_args.sh", "tools/audit/seat/update_pr.sh",
             "tools/audit/seat/cloud_relay.sh", "tools/audit/seat/orchestrator_tick.py",
             "dev/audit/harnesses/r10_seat_selftests_mutants.py")
RED = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}
LEDGER = "tests/mutation_ledger"
SIGNALS = ("carry-audit", "figure-lint", "moved-head", "head-note", "structure", "red-unanswered", "required-red", "host-path", "hot-file",
           "handoff-not-applied", "carry-landed", "introduced-red")


def git(*a: str, cwd: Path | None = None, check: bool = True) -> str:
    r = subprocess.run(["git", *a], cwd=cwd or repo(), capture_output=True, text=True)
    if check and r.returncode:
        raise Unavailable(f"git {' '.join(a)}: {r.stderr.strip()[:200]}")
    return r.stdout


def gh(path: str):
    cmd = shlex.split(os.environ.get("HPO_BUS_GH", "gh")) + ["api", path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise Unavailable(f"gh api {path}: no `gh` on PATH")
    if r.returncode:
        raise Unavailable(f"gh api {path}: {(r.stderr or r.stdout).strip()[:200]}")
    try:
        return json.loads(r.stdout or "null")
    except ValueError:
        raise Unavailable(f"gh api {path}: not JSON")


def section(body: str, name: str) -> str:
    m = re.search(rf"^## {re.escape(name)}[ \t]*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


# ------------------------------------------------------------------- the rules
def gate_digest(runs: list[dict]) -> tuple[str, list[str], list[str]]:
    """(state, lines, concluded-red names) of the head's check runs as read: the
    latest run per name decides; pending while any is not completed; `none` when
    the head has no run at all, which is not green."""
    latest: dict[str, dict] = {}
    for r in sorted(runs, key=lambda r: int(r["id"])):
        latest[r["name"]] = r
    lines, reds, pending = [], [], False
    for name in sorted(latest):
        r = latest[name]
        done = r.get("status") == "completed"
        pending |= not done
        c = r.get("conclusion") if done else r.get("status")
        if done and c in RED:
            reds.append(name)
        lines.append(f"{name} id={r['id']} {c}")
    state = "red" if reds else "pending" if pending else "green" if latest else "none"
    return state, lines, reds


#: `merge_train.py classify`'s exit code -> the verdict word its one line starts with.
CLASSIFY_WORD = {0: "GREEN", 1: "RED", 3: "WAIT", 4: "APPROVAL-OWED"}


def required_reading(pr: int, head: str) -> tuple[str, str]:
    """(verdict, rest of the line) of `merge_train.py classify <head> --pr <pr>`,
    the one owner of whether a required red is red (P436: a provisional gate
    red, or one beside a re-running unit, it reads WAIT) and of K15 (d)'s raise
    exception (P345). The packet's own latest-run-per-name digest never decides
    alone: bus.sh dispatches on this same answer, and the two disagreeing is
    #3379's deadlock. A verdict whose word does not match its rc, a line naming
    another head, or a classifier that cannot run is ("RED", why): fail closed.
    HPO_PACKET_CLASSIFY replaces the command (the self-test's stub)."""
    cmd = shlex.split(os.environ.get("HPO_PACKET_CLASSIFY", "")) or [
        sys.executable, str(ROOT / "tools/audit/seat/merge_train.py")]
    try:
        r = subprocess.run([*cmd, "classify", head, "--repo", REPO, "--pr", str(pr)],
                           capture_output=True, text=True)
    except OSError as e:
        return "RED", f"classify could not run: {e}"
    word = CLASSIFY_WORD.get(r.returncode)
    m = word and re.search(rf"^{re.escape(word)} {re.escape(head)}(?: (.*))?$", r.stdout, re.M)
    if m:
        return word, m.group(1) or ""
    last = ([ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()] or [""])[-1]
    return "RED", f"classify unreadable (rc {r.returncode}): {last[:200]}"


def introduced_reading(head: str, base: str, read=None) -> tuple[list[str], str]:
    """(INTRODUCED step names, how read) of the head's instrument-self-tests job
    against the merge base's, by merge_train.introduced_at: the one rule, which
    `classify --pr` reads too: one filtered check-run read per side and one
    job-step read per side through `gh`, and only the head's listing when its
    job is not red. An input with no reading (unreadable, a job-level cancelled,
    a job still running) is ([], "unreadable: ..."), which `build` refuses: fail closed."""
    import merge_train
    read = read or gh

    def get(path):
        try:
            return read(path)
        except Unavailable:
            return None

    def selftest_runs(sha):  # filtered: the head's unfiltered first page can miss the job
        got = get(f"repos/{REPO}/commits/{sha}/{merge_train.SELFTESTS_RUNS}")
        return got.get("check_runs") if isinstance(got, dict) and isinstance(got.get("check_runs"), list) else None

    def job_steps(job):
        got = get(f"repos/{REPO}/actions/jobs/{job}")
        return got.get("steps") if isinstance(got, dict) and isinstance(got.get("steps"), list) else None

    runs = selftest_runs(head)
    if runs is None:
        return [], "unreadable: the head's instrument-self-tests check runs: an introduced red cannot be ruled out (fail closed)"
    try:
        names, how = merge_train.introduced_at(runs, lambda: selftest_runs(base), job_steps)
    except ValueError as e:
        return [], f"unreadable: {e}: an introduced red cannot be ruled out (fail closed)"
    if names is None:
        return [], f"unreadable: {how} has not concluded: an introduced red cannot be ruled out (fail closed)"
    return names, how


def ci_facts(pr: int, head: str, base: str, read=None) -> dict:
    """gather's check-run keys at <head>: the gate digest, classify's reading of
    a required red, and the INTRODUCED reading against <base>; `read` replaces gh."""
    read = read or gh
    gate = gate_digest(read(f"repos/{REPO}/commits/{head}/check-runs?per_page=100").get("check_runs", []))
    return {"gate": gate, "required_read": required_reading(pr, head) if set(gate[2]) & set(REQUIRED) else None,
            "introduced": introduced_reading(head, base, read)}


def head_named(body: str, head: str, base: str) -> bool:
    """Whether `## Head` names the dispatched head as `policy_lint.mjs --pr-body --head` decides
    (P405): the contract accepts a 7-character name and a bot autofix chain on top of a named
    head, so one rule decides and this packet adds none. Only its own `does not name` error
    refuses; a run that stops without reading the head section is Unavailable, not a pass.
    HPO_PACKET_LINT replaces the command (the self-test's stub)."""
    cmd = shlex.split(os.environ.get("HPO_PACKET_LINT", "")) or ["node", "tools/policy/policy_lint.mjs"]
    rc, out = tool([*cmd, "--pr-body", "{BODY}", "--head", head, "--base", base], body)
    if "does not name" in out and "`## Head`" in out:
        return False
    if rc and "[pr-body]" not in out:
        raise Unavailable(f"policy_lint --pr-body did not run: {out[:200]}")
    return True


def head_note_ok(facts: dict) -> bool:
    """The gathered verdict, else the contract's bare floor (the head's full SHA in `## Head`)."""
    named = facts.get("head_named")
    return facts["head"] in section(facts["body"], "Head") if named is None else named


def hot_file_refusals(paths: set[str], open_prs: list[dict], boarded: set[int], this_pr: int) -> list[str]:
    """Each open pull request (`number`, `head`, `files`, `merge_verdict_head`)
    sharing a hot file with this diff while its merge verdict, at its own head,
    is not boarded on the train."""
    out = []
    for p in open_prs:
        shared = sorted(paths & set(HOT_FILES) & set(p.get("files", ())))
        if p["number"] == this_pr or not shared:
            continue
        if p.get("merge_verdict_head") == p["head"] and p["number"] not in boarded:
            out.append(f"#{p['number']} holds an unboarded merge verdict and shares {', '.join(shared)}")
    return out


def own_pr(open_prs: list[dict], topic: str, is_ancestor) -> tuple[int, str | None]:
    """The open pull request a handoff updates (P368): by ancestry -- the one whose head is an
    ancestor of the handoff's HEAD, since a re-cut is built on it -- and only when none is, by
    head branch `fix/<topic>`. (0, None) when none qualifies; two qualifying are excluded
    neither and named in the note, because a guess would hide a real collision."""
    for found in ([p for p in open_prs if is_ancestor(p["head"])],
                  [p for p in open_prs if p.get("branch") == f"fix/{topic}"]):
        if len(found) == 1:
            return found[0]["number"], None
        if found:
            return 0, "own-pr: ambiguous, " + " and ".join(f"#{p['number']}" for p in found) + " both qualify; neither is excluded from the hot-file rule"
    return 0, None


def handoff_hot(touched: set[str], open_prs: list[dict], boarded: set[int], topic: str, is_ancestor) -> list[str]:
    """The handoff's hot-file refusals, the pull request it updates excluded (P368)."""
    this_pr, note = own_pr(open_prs, topic, is_ancestor)  # mut:ownpr
    return hot_file_refusals(touched, open_prs, boarded, this_pr) + ([note] if note else [])


def handoff_topics(branch: str) -> list[str]:
    """The handoff topics a pull request's branch can carry: `fix/<t>` or
    `fix/<t>-pr`, `open_pr.sh`'s two spellings; none for any other shape."""
    t = branch[len("fix/"):] if branch.startswith("fix/") else ""
    return [x for x in ([t, t[:-len("-pr")]] if t.endswith("-pr") else [t]) if x]


def head_note_repair(head: str, branch: str | None) -> str:
    """What repairs a `head-note` refusal (P213): the head the body must name and
    the push that names it, one line. No branch read, no command: a guessed
    branch would send a fixer to push the wrong one."""
    if not branch:
        return ""
    return (f" -- repair: the body's ## Head must name {head}; "
            f"`tools/audit/seat/update_pr.sh {shlex.quote(branch)} - <body-file>` (PR branch {branch})")


#: A body line citing a carry as landed: `Carry 3: landed at 1a2b3c4` (any case, `[3]` too).
LANDED = re.compile(r"\bcarry\s*\[?(\d+)\]?(?![0-9]).*?\blanded\b.*?\b([0-9a-f]{7,40})\b", re.I)


def landed_cites(body: str) -> list[tuple[int, str]]:
    """(carry index, sha) of each carry the body cites as landed, in order."""
    out = []
    for line in body.splitlines():
        m = LANDED.search(line)
        if m:
            out.append((int(m.group(1)), m.group(2).lower()))
    return out


def unlanded_carries(cites: list[tuple[int, str]], carries_at, on_roster) -> list[str]:
    """Each cited carry that is not on the roster ref at its cited sha (L5).
    `on_roster(sha)`: the sha is on the roster ref; `carries_at(sha)`: how many
    carries the group's roster entry holds there (0 when it cannot be read). Both
    must hold: a sha off the ref cites a commit the round never took, and a sha
    on it can predate the carry."""
    out = []
    for n, sha in cites:
        if not on_roster(sha):
            out.append(f"carry-landed: carry {n} is cited as landed at {sha}, which is not on the roster ref")
        elif carries_at(sha) < n:
            out.append(f"carry-landed: carry {n} is cited as landed at {sha}, whose roster entry holds {carries_at(sha)}")
    return out


def roster_carry_reader(topics: list[str], ref: str):
    """(on_roster, carries_at) over the roster ref `ref`, for the group the
    branch's topics name; an unreadable roster at a sha holds no carries."""
    import roster_lib

    def carries_at(sha: str) -> int:
        try:
            roster = roster_lib.show_roster(str(repo()), sha)
        except Exception:  # noqa: BLE001 -- a sha with no roster holds no carry
            return 0
        for t in topics:
            gid = roster_lib.group_for_branch(roster, f"handoff/{t}")
            if gid:
                return len(roster_lib.groups_of(roster)[gid].get("carry") or [])
        return 0
    return (lambda sha: is_ancestor(sha, ref)), carries_at


def fetch_roster_ref(roster_ref: str | None) -> str:
    import roster_lib
    ref = roster_ref or roster_lib.round_ref(roster_lib.git_in(str(repo())))
    if not ref:
        raise Unavailable("roster_lib.round_ref names no round roster branch")
    git("fetch", "-q", "--no-tags", "origin", f"+refs/heads/{ref.removeprefix('origin/')}:refs/remotes/{ref}")
    return ref


def handoff_not_applied(branch: str, head: str, tip_of, is_ancestor, body: str = "",
                        round_topic: str | None = None, behind=None) -> tuple[str | None, str | None]:
    """(refusal, advisory) for `head` lacking its own handoff (P229). `tip_of(topic)`
    is `handoff/<topic>`'s tip on origin or None; the first topic with a ref
    decides. A branch of another shape, or no handoff ref, is never refused.
    For `round_topic` alone (the round roster branch, which takes a commit a
    minute while a landing takes ten) a head holding the snapshot sha its `## Head`
    names is accepted when that sha is an ancestor of the tip; `behind(sha, tip)`
    counts the commits it trails (S14)."""
    for t in handoff_topics(branch):
        tip = tip_of(t)
        if not tip:
            continue
        if is_ancestor(tip, head):
            return None, None
        if t == round_topic:
            for sha in re.findall(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", section(body, "Head")):
                if is_ancestor(sha, head) and is_ancestor(sha, tip):
                    return None, f"roster snapshot {sha}, {behind(sha, tip)} commits behind handoff/{t}; a later landing takes the rest"
        return f"handoff/{t} {tip} is not an ancestor of {head}", None
    return None, None


def origin_handoff_tip(topic: str) -> str | None:
    tip = git("ls-remote", "origin", f"refs/heads/handoff/{topic}").split()
    if not tip:
        return None
    git("fetch", "-q", "origin", f"refs/heads/handoff/{topic}")
    return tip[0]


def is_ancestor(a: str, b: str) -> bool:
    r = subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=repo(), capture_output=True, text=True)
    if r.returncode not in (0, 1):
        raise Unavailable(f"git merge-base --is-ancestor {a} {b}: {r.stderr.strip()[:200]}")
    return r.returncode == 0


def verdict_merge_head(sha: str, read=None) -> str | None:
    """The head a merge verdict names, or None: the first line of `VERDICT.md`
    in the verdict ref's commit, parsed by `proof_watch.parse_verdict`, the one
    Python reader of the grammar (`agreement_py.py` refuses a copy)."""
    read = read or (lambda s: git("show", f"{s}:VERDICT.md", check=False))
    lines = read(sha).splitlines()
    v = proof_watch.parse_verdict(lines[0]) if lines else None
    return v[1] if v and v[0] == "merge" else None


def previous_verdict(pr: int, rh: str, shas=None, read=None) -> str | None:
    """VERDICT.md of the newest verdict/<pr> commit whose first line names <rh>,
    parsed by `proof_watch.parse_verdict`; None when no verdict names it or the
    ref is absent. An unreadable ref is UNAVAILABLE, never read as no verdict."""
    if shas is None:
        r = subprocess.run(["git", "ls-remote", "origin", f"refs/heads/verdict/{pr}"],
                           cwd=repo(), capture_output=True, text=True)
        if r.returncode:
            raise Unavailable(f"git ls-remote verdict/{pr}: {r.stderr.strip()[:200]}")
        tip = r.stdout.split()[:1]
        if not tip:
            return None
        git("fetch", "-q", "origin", f"refs/heads/verdict/{pr}")
        shas = git("log", "--format=%H", tip[0]).split()
    read = read or (lambda s: git("show", f"{s}:VERDICT.md", check=False))
    for sha in shas:
        text = read(sha)
        v = proof_watch.parse_verdict(text.splitlines()[0]) if text.strip() else None
        if v and v[1] == rh:
            return text
    return None


def review_scope(rh: str | None, head: str, verdict: str | None, is_anc) -> tuple[str, str]:
    """("delta" | "full", why): a later round reviews `git diff <rh> <head>`
    beside the verdict at <rh> (fix-review.md step 12); every other round the
    three-dot diff."""
    if not rh:
        return "full", "first round: no --reviewed-head"
    if not is_anc(rh, head):
        return "full", f"the reviewed head {rh} is not an ancestor of {head}, so its delta is no later round's"
    if verdict is None:
        return "full", f"no verdict on verdict/<pr> names the reviewed head {rh}, so there is no finding to confirm resolved"
    return "delta", f"later round over the reviewed head {rh}"


def harness_source(harness: str | None, harness_file: str | None, base: str,
                   touched: set[str], cwd: Path | None = None) -> tuple[str, bytes]:
    """(label, bytes) of the finder's harness; SystemExit on the fixer's."""
    root = (cwd or repo()).resolve()
    if harness_file:
        p = Path(harness_file).resolve()
        if p.is_relative_to(root):
            raise SystemExit("review_packet: REFUSE independence: --harness-file is inside the tree; name it by --harness")
        data = p.read_bytes()
        return f"{p.name} sha1={hashlib.sha1(data).hexdigest()}", data
    if harness in touched:
        raise SystemExit(f"review_packet: REFUSE independence: {harness} is edited by the diff, so it is the fixer's harness")
    r = subprocess.run(["git", "cat-file", "blob", f"{base}:{harness}"], cwd=root, capture_output=True)
    if r.returncode:
        raise SystemExit(f"review_packet: REFUSE independence: {harness} is not at the merge base, so it is not the finder's")
    return f"{harness} at {base}", r.stdout


def run_harness(data: bytes, rev: str, args: list[str]) -> str:
    root = repo()
    with tempfile.TemporaryDirectory() as d:
        tree = Path(d) / "tree"
        tree.mkdir()
        try:
            a = subprocess.run(["git", "archive", rev], cwd=root, capture_output=True, check=True)
            subprocess.run(["tar", "-x", "-C", str(tree)], input=a.stdout, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            raise Unavailable(f"cannot export {rev} for the harness: {e}")
        h = Path(d) / "harness.py"
        h.write_bytes(data)
        r = subprocess.run([sys.executable, str(h), *args], cwd=tree, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": str(tree / "tests" / "hastub")})
        out = (r.stdout + r.stderr).replace(d, "<tmp>")
        return f"rc={r.returncode}\n{out}"


def structure_at_merge(main: str, head: str) -> str | None:
    """Why `tests/structure.py` refuses `head` merged with `main`, or None."""
    root = repo()
    r = subprocess.run(["git", "merge-tree", "--write-tree", main, head], cwd=root, capture_output=True, text=True)
    if r.returncode:
        return f"head does not merge cleanly with {main}: {r.stdout.splitlines()[1:3]}"
    tree = r.stdout.split()[0]
    with tempfile.TemporaryDirectory() as d:
        try:
            a = subprocess.run(["git", "archive", tree], cwd=root, capture_output=True, check=True)
            subprocess.run(["tar", "-x", "-C", d], input=a.stdout, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            raise Unavailable(f"cannot export the merged tree: {e}")
        s = subprocess.run([sys.executable, "tests/structure.py"], cwd=d, capture_output=True, text=True)
        if s.returncode:
            tail = (s.stdout + s.stderr).replace(d, "<tmp>").strip().splitlines()
            return (tail[-1] if tail else f"tests/structure.py exited {s.returncode}")[:300]
    return None


def tool(argv: list[str], body: str) -> tuple[int, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(body)
    try:
        try:
            r = subprocess.run([a.replace("{BODY}", f.name) for a in argv], cwd=repo(),
                               capture_output=True, text=True)
        except FileNotFoundError as e:
            raise Unavailable(f"cannot run {argv[0].rsplit('/', 1)[-1]}: {e}")
        return r.returncode, (r.stdout + r.stderr).replace(f.name, "<body>").strip()
    finally:
        os.unlink(f.name)


def unanswered_reds(body: str, head: str, base: str, reds: list[str],
                    touched: set[str], existing: set[str],
                    required: "list[str] | None" = None) -> list[str]:
    """The concluded reds the body's `## Red checks` leaves unanswered, as
    `policy_lint.mjs --pr-body` decides (cancelled and timed-out reds included,
    RED). Only a red in the required set is owed (owner ruling tvofi 2026-11-07):
    policy_lint reads that set through `merge_train.py owed-reds`, or from
    <required> when given (the self-test's, so it reads no ruleset). Where the
    set cannot be read, the rule as it stood holds: a reporter that grades main
    is owed no answer while the diff leaves its inputs alone (P282), read from
    `--paths-file` and `--existing-file`. Every exemption stays policy_lint's
    alone, as prepr.sh's body_check keeps it."""
    if not reds:
        return []
    with tempfile.TemporaryDirectory() as td:
        pf, ef, rf = Path(td, "paths"), Path(td, "existing"), Path(td, "required")
        pf.write_text("".join(f"{x}\n" for x in sorted(touched)))
        ef.write_text("".join(f"{x}\n" for x in sorted(existing)))
        rf.write_text("".join(f"{x}\n" for x in required or ()))
        rc, out = tool(["node", "tools/policy/policy_lint.mjs", "--pr-body", "{BODY}", "--head", head,
                        "--base", base, "--paths-file", str(pf), "--existing-file", str(ef),
                        *(("--required-file", str(rf)) if required is not None else ()),
                        *[x for n in reds for x in ("--red", n)]], body)
    # A path list policy_lint refuses is not "no unanswered red": the run
    # stopped before any rule read the body, so the outcome is unknown.
    if rc and re.search(r"ERROR +\[pr-body\] --(?:paths|existing)-file ", out):
        raise Unavailable(f"policy_lint refused the diff's path lists: {out[:200]}")
    return sorted(n for n in reds if f"check `{n}` is red and `## Red checks` does not name it" in out)


def diff_paths(base: str, head: str) -> tuple[set[str], set[str]]:
    """(touched, existing): the three-dot diff's paths, and those of them the
    base already had (`--diff-filter=a`), which `unanswered_reds` hands
    policy_lint as `--existing-file`, so a delivery row the diff adds is read as
    the pull request's own and not as an input of main's reporter."""
    span = f"{base}...{head}"
    return (set(git("diff", "--name-only", "--no-renames", span).split()),
            set(git("diff", "--name-only", "--no-renames", "--diff-filter=a", span).split()))


def writes_packet(refusals: list[str]) -> bool:
    """How a render treats its own refusals: written unless it is unpublishable.

    Evidence is never withheld -- a refused dispatch leaves the packet on disk
    for whoever must repair it. `host-path` is the one signal a written packet
    would defeat, because the packet carries the three-dot diff verbatim.
    """
    return not any(r.startswith("host-path:") for r in refusals)


def unnamed_carries(body: str, carries) -> list[int]:
    """The 0-based indexes (`cloud_dispatch.py` renders `Carry {i}` from 0) among
    `carries` -- a count `n` meaning `range(n)`, or the indexes themselves --
    that the body never names as `Carry N` (any case, `[N]` too). A count, not a
    judgement: whether the named carry is answered well is the reviewer's."""
    idx = range(carries) if isinstance(carries, int) else carries
    return [i for i in idx if not re.search(rf"\bcarry\s*\[?{i}\]?(?![0-9])", body, re.I)]


def prompt_carries(prompt: str | None) -> list[int] | None:
    """The `Carry N:` indexes a dispatch PROMPT.md holds, sorted, or None when
    there is no prompt or it holds none: the carries the fixer was dispatched
    with, which a roster appended to afterwards does not change (S14)."""
    found = sorted({int(m) for m in re.findall(r"^Carry (\d+):", prompt or "", re.M)})
    assigned = part_carries(prompt)
    return assigned or found or None


def part_carries(prompt: str | None) -> list[int] | None:
    """The indexes a split part is assigned, or None when the prompt has no part
    line. Two spellings: the hand line `This part: Carries 25, 24, 10 (0-based
    roster indexes` and the generated `Part k of N: build carries 15-17+19-20`
    (`cloud_dispatch.part_split`'s runs). The prompt holds every roster carry
    under the generated line, so the part line, not the `Carry N:` count, scopes it."""
    text = prompt or ""
    hand = re.search(r"^This part: Carries ([0-9, ]+?) \(0-based roster indexes", text, re.M)
    if hand:
        return sorted({int(n) for n in re.findall(r"\d+", hand.group(1))}) or None
    gen = re.search(r"^Part \d+ of \d+: build carries ([0-9+-]+);", text, re.M)
    if not gen:
        return None
    out: set[int] = set()
    for run in gen.group(1).split("+"):
        lo, _, hi = run.partition("-")
        out.update(range(int(lo), int(hi or lo) + 1))
    return sorted(out) or None


def handoff_carries(prompt: str | None, live: int):
    """What `unnamed_carries` checks: the dispatched PROMPT's indexes, else the live roster count."""
    return prompt_carries(prompt) or live


def dispatch_prompt(topic: str) -> str | None:
    """PROMPT.md of `origin`'s `dispatch/fixer-<topic>`, or None when the ref is
    absent here or unreadable (the caller falls back to the live roster)."""
    ref = f"refs/heads/dispatch/fixer-{topic}"
    if not git("ls-remote", "origin", ref, check=False).split():
        return None
    if subprocess.run(["git", "fetch", "-q", "origin", ref], cwd=repo(), capture_output=True).returncode:
        return None
    r = subprocess.run(["git", "show", "FETCH_HEAD:PROMPT.md"], cwd=repo(), capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def handoff_refusals(structure: str | None, hot: list[str], unnamed: list[int],
                     unlanded: list[str] | None = None, base: str = "") -> list[str]:
    """The refusals that need no CI run: the packet's `structure` and `hot-file`,
    and the handoff's `brief-carries` count (P256). One spelling for both callers."""
    out = [f"structure: tests/structure.py refuses the head merged with main: {structure}"] if structure else []
    out += [f"hot-file: {w}" for w in hot]
    out += [f"brief-carries: carry {i} is not named in the body (`Carry N`){base}" for i in unnamed]
    return out + (unlanded or [])


# ------------------------------------------------------------------- the packet
SELF_AUDIT = ("python3 -I tools/audit/carry_audit.py check --body <PR body file> "
              "--comments <file holding [{\"id\": 0, \"body\": <verdict.md text>}]>")


def build(facts: dict) -> tuple[list[str], list[str], str]:
    """(refusals, advisories, packet text) from gathered facts; pure."""
    head, body = facts["head"], facts["body"]
    state, gate_lines, reds = facts["gate"]
    refusals: list[str] = []
    if facts["carry_rc"]:
        refusals.append("carry-audit: carry_audit.py check returned 1 on the body")
    if facts.get("figure_rc"):
        refusals.append("figure-lint: figure_lint.mjs refused the body (its output is in the packet)")
    if facts.get("pr_head") and facts["pr_head"] != head:
        refusals.append(f"moved-head: the pull request's head is {facts['pr_head']}, not the dispatched {head}")
    if not head_note_ok(facts):
        refusals.append(f"head-note: ## Head does not name the dispatched head {head}"
                        + head_note_repair(head, facts.get("branch")))
    refusals += handoff_refusals(facts["structure"], facts["hot"], [])
    (word, why), owed_adv = facts.get("required_read") or ("RED", ""), []
    for n in facts["red_unanswered"]:
        if n in REQUIRED and word in ("WAIT", "GREEN"):
            continue  # classify --pr reads it not red: its required-wait/green advisory names it (S14)
        refusals.append(f"red-unanswered: concluded red check `{n}` is not named in ## Red checks")
    for n in sorted(set(reds) & set(REQUIRED)):
        if word == "APPROVAL-OWED":
            owed_adv.append(
                f"approval-owed: required context `{n}` concluded failure at {head} only on a budget "
                f"raise's owed approval (merge_train.approval_owed): {why}")
        elif word in ("WAIT", "GREEN"):
            owed_adv.append(
                f"required-{word.lower()}: required context `{n}` reads concluded failure at {head} in the "
                f"digest, but merge_train.py classify --pr reads {word} ({why}): classify decides, as "
                "bus.sh's dispatch does, and a pending check never refuses")
        else:
            refusals.append(f"required-red: required context `{n}` concluded failure at {head}"
                            + (f" (merge_train.py classify --pr reads {word} {why})" if why else ""))
    intro, intro_why = facts.get("introduced") or ([], "")
    for n in intro:
        refusals.append(f"introduced-red: INTRODUCED `{n}`: a step of the non-required instrument-self-tests job red at "
                        f"{head} and not at the base ({intro_why}), a finding of this pull request (fix-review.md)")
    if intro_why.startswith("unreadable"):
        refusals.append(f"introduced-red: {intro_why}")
    for w in facts["host"]:
        refusals.append(f"host-path: {w}")
    refusals += facts.get("unlanded", [])
    if facts.get("handoff"):
        refusals.append(f"handoff-not-applied: {facts['handoff']}")
    advisories = [a for a in facts.get("advisories", [])] + owed_adv
    parts = [
        f"# Review packet #{facts['pr']}",
        f"head: {head}", f"base: {facts['base']}", "",
        "Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.",
        "", f"## Gate digest: {state}", *gate_lines, "",
        "## Refusals", *(refusals or ["none"]), "",
        "## Advisories", *(advisories or ["none"]), "",
        "## carry_audit at the head", facts["carry_out"], "",
        "## figure_lint at the head", facts["figure_out"], "",
        f"## Finder's harness: {facts['harness_label']}",
        "### at the base", facts["harness_base"], "### at the head", facts["harness_head"], "",
        "## Mutation-ledger diff", facts["ledger_diff"] or "none", "",
        *scope_parts(facts),
        "## Before you return the verdict (P275)",
        f"Run `{SELF_AUDIT}`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;",
        "an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.",
    ]
    return refusals, advisories, "\n".join(parts) + "\n"


def scope_parts(facts: dict) -> list[str]:
    """The packet's diff sections: the delta and the previous verdict on a later
    round, else the three-dot diff (a facts dict without a scope is a first round)."""
    kind, why = facts.get("scope") or ("full", "first round: no --reviewed-head")
    if kind == "delta":
        rh = facts["reviewed_head"]
        return [f"## Review scope: delta ({why})",
                "Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review "
                "the delta below. Widen only to exactly the already-reviewed code a delta touching production code "
                "(custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, "
                "naming the path and the risk in the verdict; an instrument, test, policy or body delta never "
                "justifies a wider review (fix-review.md step 12).", "",
                f"## Previous verdict at {rh}", facts["previous_verdict"].rstrip("\n"), "",
                f"## Delta diff: git diff {rh} {facts['head']}", facts["diff"]]
    return [f"## Review scope: full ({why})", "", "## Three-dot diff", facts["diff"]]


def gather(a) -> dict:
    import roster_lib
    head, main = a.head, a.main
    base = git("merge-base", main, head).strip()
    touched, existing = diff_paths(base, head)
    label, data = (harness_source(a.harness, a.harness_file, base, touched)
                   if (a.harness or a.harness_file) else ("none named", b""))
    pr = gh(f"repos/{REPO}/pulls/{a.pr}") or {}
    body = pr.get("body") or ""
    branch = (pr.get("head") or {}).get("ref") or ""
    rr = roster_lib.round_ref(roster_lib.git_in(str(repo())))
    handoff, snap_adv = handoff_not_applied(
        branch, head, origin_handoff_tip, is_ancestor, body, rr.removeprefix("origin/handoff/") if rr else None,
        lambda sha, tip: git("rev-list", "--count", f"{sha}..{tip}").strip())
    unlanded: list[str] = []
    cites = landed_cites(body)
    if cites:  # no roster read at all for a body that cites no landed carry
        rref = fetch_roster_ref(None)
        on_roster, carries_at = roster_carry_reader(handoff_topics(branch), rref)
        unlanded = unlanded_carries(cites, carries_at, on_roster)
    ci = ci_facts(a.pr, head, base)
    gate = ci["gate"]
    crc, cout = tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}"], body)
    frc, fout = tool(["node", "tools/policy/figure_lint.mjs", "--pr-body", "{BODY}", "--at", head], body)
    red_unanswered = unanswered_reds(body, head, base, gate[2], touched, existing)
    named = head_named(body, head, base)
    ident = ref_privacy.Identity.of_host()
    host = [w for w in [ref_privacy.body_refusal(body, ident)] if w]
    host += ref_privacy.content_refusals(ref_privacy.added_lines(base, head, repo()), ident)
    open_prs, boarded = hot_prs(touched)
    return {
        "pr": a.pr, "head": head, "base": base, "body": body, **ci,
        "branch": branch, "unlanded": unlanded, "head_named": named,
        "carry_rc": crc, "carry_out": cout, "figure_out": fout, "figure_rc": frc,
        "pr_head": (pr.get("head") or {}).get("sha"),
        "structure": None if a.no_structure else structure_at_merge(main, head),
        "red_unanswered": red_unanswered, "host": host, "handoff": handoff,
        "hot": hot_file_refusals(touched, open_prs, boarded, a.pr),
        "advisories": ([] if os.environ.get("HPO_BUS_TRAIN_STATE") or not open_prs
                       else ["hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded"])
        + ([snap_adv] if snap_adv else []),
        "harness_label": label,
        "harness_base": run_harness(data, base, a.harness_arg) if data else "not run",
        "harness_head": run_harness(data, head, a.harness_arg) if data else "not run",
        "ledger_diff": git("diff", f"{base}...{head}", "--", LEDGER),
        **scope_facts(a.pr, getattr(a, "reviewed_head", None), base, head),
    }


def scope_facts(pr: int, rh: str | None, base: str, head: str, read_verdict=None) -> dict:
    """gather's scope keys: the round's scope, the verdict at <rh> and the diff it reviews."""
    verdict = (read_verdict or previous_verdict)(pr, rh) if rh else None
    scope = review_scope(rh, head, verdict, is_ancestor)
    delta = scope[0] == "delta"
    return {"scope": scope, "reviewed_head": rh, "previous_verdict": verdict,
            "diff": git("diff", rh, head) if delta else git("diff", f"{base}...{head}")}


def hot_prs(touched: set[str]) -> tuple[list[dict], set[int]]:
    """(open pull requests, boarded numbers) the hot-file rule reads; no read
    at all when the diff touches no hot file."""
    open_prs: list[dict] = []
    if not touched & set(HOT_FILES):
        return open_prs, set()
    for p in gh(f"repos/{REPO}/pulls?state=open&per_page=100"):
        files = [f["filename"] for f in gh(f"repos/{REPO}/pulls/{p['number']}/files?per_page=100")]
        tip = git("ls-remote", "origin", f"refs/heads/verdict/{p['number']}", check=False).split()
        merge_head = None
        if tip and not git("fetch", "-q", "origin", f"refs/heads/verdict/{p['number']}", check=False):
            merge_head = verdict_merge_head(tip[0])
        open_prs.append({"number": p["number"], "head": p["head"]["sha"], "branch": p["head"]["ref"], "files": files,
                         "merge_verdict_head": merge_head})
    return open_prs, train_boarded()


def handoff(a) -> int:
    """`handoff`: the refusals a fixer answers before the push (P256), at this
    checkout's HEAD. `head-note` is prepr's own at the same push (`--body-check`
    hands policy_lint `--head HEAD`), and the CI-dependent ones stay at dispatch
    (card 5), so this runs `structure`, `hot-file` and `brief-carries`."""
    import roster_lib
    head = git("rev-parse", "HEAD").strip()
    body = Path(a.body).read_text()
    touched = set(git("diff", "--name-only", "--no-renames", f"{git('merge-base', a.main, head).strip()}...{head}").split())
    ref = fetch_roster_ref(a.roster_ref)
    try:
        roster = roster_lib.show_roster(str(repo()), ref)
    except Exception as e:  # noqa: BLE001 -- an unread roster is not an empty one
        raise Unavailable(f"cannot read the roster at {ref}: {e}")
    gid = roster_lib.group_for_branch(roster, f"handoff/{a.topic}")
    live = len(roster_lib.groups_of(roster)[gid].get("carry") or []) if gid else 0
    prompt = dispatch_prompt(a.topic)
    carries = handoff_carries(prompt, live)
    base = " -- demanded by the dispatch PROMPT's part line" if part_carries(prompt) else ""
    open_prs, boarded = hot_prs(touched)
    anc = lambda sha: subprocess.run(  # noqa: E731
        ["git", "merge-base", "--is-ancestor", sha, head], cwd=repo(), capture_output=True).returncode == 0
    refusals = handoff_refusals(structure_at_merge(a.main, head),
                                handoff_hot(touched, open_prs, boarded, a.topic, anc), unnamed_carries(body, carries),
                                unlanded_carries(landed_cites(body), *reversed(roster_carry_reader([a.topic], ref))), base)
    for x in refusals:
        print(f"review_packet: REFUSE {x}", file=sys.stderr)
    print(f"review-packet handoff: {gid or 'no group'} at {head[:12]}, {live} live, {carries if isinstance(carries, int) else len(carries)} dispatched carries, {len(refusals)} refused")
    return 1 if refusals else 0


def train_boarded() -> set[int]:
    state = os.environ.get("HPO_BUS_TRAIN_STATE")
    if not state:
        return set()
    import merge_train
    st = Path(state)
    spooled, _ = merge_train.spool_read(st)
    try:
        pending = set(json.loads((st / merge_train.QUEUE_PENDING).read_text()))
    except (OSError, ValueError):
        pending = set()
    return {int(e["pr"]) for e in spooled} | {int(x) for x in pending}


def packet_head(text: str) -> str | None:
    m = re.search(r"^head: ([0-9a-f]{40})$", text, re.M)
    return m.group(1) if m else None


# ------------------------------------------------------------------- self-test
def _self_test() -> int:
    passed = failed = 0

    def check(name: str, cond: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + cond, failed + (not cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    H, B = "a" * 40, "b" * 40
    green = [{"id": 1, "name": "gate", "status": "completed", "conclusion": "success"}]
    clean_body = f"## Head\n{H}\n\n## Red checks\nnone\n"
    clean = {"pr": 7, "head": H, "base": B, "body": clean_body, "gate": gate_digest(green),
             "carry_rc": 0, "carry_out": "CARRY-AUDIT: 0", "figure_out": "ok", "structure": None,
             "red_unanswered": [], "host": [], "hot": [], "harness_label": "h.py at " + B,
             "harness_base": "rc=0\nRESULT 1", "harness_head": "rc=0\nRESULT 0", "ledger_diff": "", "diff": "d\n"}
    r0, _, t0 = build(clean)
    check("null control: a clean head dispatches (no refusal)", r0 == [])
    check("the packet is byte-identical on a second render of the same head", build(dict(clean))[2] == t0)
    check("the packet closes on the carry self-audit command (P275)",
          t0.rstrip().splitlines()[-3].startswith("## Before you return the verdict") and SELF_AUDIT in t0
          and "--comments" in SELF_AUDIT)
    check("the packet carries the head's harness output and names the head",
          "RESULT 0" in t0 and packet_head(t0) == H)
    check("check names a stale packet: another head does not match", packet_head(t0) != B)

    def refused(signal: str, **kw) -> bool:
        r, _, _ = build({**clean, **kw})
        return len(r) == 1 and r[0].startswith(signal + ":")

    check("carry-audit: an unrouted body refuses and names it", refused("carry-audit", carry_rc=1))
    check("head-note: a ## Head naming another head refuses", refused("head-note", body=f"## Head\n{B}\n"))
    hn = build({**clean, "body": f"## Head\n{B}\n", "branch": "fix/g"})[0][0]
    check("head-note repair: the refusal names the head and the update_pr.sh push for the PR's branch",
          H in hn and "update_pr.sh fix/g - <body-file>" in hn)
    check("head-note repair null: a branch that cannot be read prints today's refusal, no command",
          build({**clean, "body": f"## Head\n{B}\n"})[0][0] == f"head-note: ## Head does not name the dispatched head {H}")
    with tempfile.TemporaryDirectory() as d:
        stub = Path(d) / "lint.sh"
        stub.write_text('echo "$*" > "$(dirname "$0")/argv"\n'
                        'if [ -n "${PK_NAME:-}" ]; then echo \'  ERROR   [pr-body] `## Head` does not name aaaaaaa, which is the head\'; exit 1; fi\n'
                        'echo \'  ERROR   [pr-body] no `## Figures` section\'; exit 1\n')
        saved = os.environ.get("HPO_PACKET_LINT")
        os.environ["HPO_PACKET_LINT"] = f"bash {stub}"
        try:
            os.environ.pop("PK_NAME", None)
            ok = head_named(clean_body, H, B)
            check("P405 head-note asks policy_lint --pr-body --head (one rule decides); another pr-body error is not its refusal",
                  ok and f"--head {H}" in (Path(d) / "argv").read_text())
            os.environ["PK_NAME"] = "1"
            check("P405 head-note refuses on policy_lint's own `does not name` error, whatever the substring says",
                  not head_named(clean_body, H, B))
            check("P405 gathered verdict decides: a chain policy_lint accepts passes where the substring test refuses",
                  head_note_ok({**clean, "body": f"## Head\n{B}\n", "head_named": True}) is True)
            check("P405 gathered verdict decides: policy_lint's refusal beats a body that contains the head",
                  head_note_ok({**clean, "head_named": False}) is False)
            check("P405 null: with no gathered verdict the floor is the head in ## Head",
                  head_note_ok(clean) and not head_note_ok({**clean, "body": f"## Head\n{B}\n"}))
        finally:
            os.environ.pop("PK_NAME", None)
            if saved is None:
                os.environ.pop("HPO_PACKET_LINT", None)
            else:
                os.environ["HPO_PACKET_LINT"] = saved
    check("P-card3 figure-lint: a figure_lint refusal on the body refuses", refused("figure-lint", figure_rc=1))
    check("P-card3 figure-lint null: figure_lint exit 0 (unverified included) does not refuse", build({**clean, "figure_rc": 0})[0] == [])
    check("P-card3 moved-head: a pull request head other than the dispatched one refuses, naming both",
          refused("moved-head", pr_head=B) and H in build({**clean, "pr_head": B})[0][0])
    check("P-card3 moved-head null: the same head, or a handoff-ref dispatch with no pull request yet, does not refuse",
          build({**clean, "pr_head": H})[0] == [] and build({**clean, "pr_head": None})[0] == [])
    check("structure: a structure refusal at the merge refuses", refused("structure", structure="max_class_loc"))
    check("red-unanswered: an unanswered concluded red refuses", refused("red-unanswered", red_unanswered=["tests / fast"]))
    check("host-path: a host path refuses", refused("host-path", host=["home-directory in the body"]))
    check("hot-file: a shared hot file with an unboarded merge verdict refuses", refused("hot-file", hot=["#9 x"]))
    redgate = [{"id": 1, "name": "gate", "status": "completed", "conclusion": "success"},
               {"id": 2, "name": "gate", "status": "completed", "conclusion": "failure"}]
    check("required-red: the required context's latest run concluded failure refuses",
          refused("required-red", gate=gate_digest(redgate)))
    r_o, adv_o, t_o = build({**clean, "gate": gate_digest(redgate),
                         "required_read": ("APPROVAL-OWED", "1 budget raise(s), planted")})
    check("P345: a required red that is only a raise's owed approval renders: no refusal, an "
          "`approval-owed` advisory naming the reason, in the packet",
          r_o == [] and len(adv_o) == 1 and adv_o[0].startswith("approval-owed: required context `gate`")
          and "1 budget raise(s), planted" in t_o)
    # #3379 at 71b95e42, 00:03Z on 11-10: the gate's latest run concluded failure while the
    # budget-raise-gate re-run was in progress, so classify --pr read WAIT (rc 3) and bus.sh
    # dispatched it, but the packet asked only "is it APPROVAL-OWED?" and refused required-red.
    raise_rerun = [*redgate, {"id": 3, "name": "budget-raise-gate / budget-raise-gate",
                              "status": "in_progress", "conclusion": None}]
    r_w, adv_w, t_w = build({**clean, "gate": gate_digest(raise_rerun),
                             "required_read": ("WAIT", "pending: budget-raise-gate red: none")})
    check("#3379: a required red that classify --pr reads WAIT renders: no refusal, a `required-wait` "
          "advisory naming classify's line (classify decides; a pending check never refuses)",
          r_w == [] and len(adv_w) == 1 and adv_w[0].startswith("required-wait: required context `gate`")
          and "pending: budget-raise-gate" in t_w)
    r_g, adv_g, _ = build({**clean, "gate": gate_digest(redgate), "required_read": ("GREEN", "pending: none red: none")})
    check("a required red that classify --pr reads GREEN renders, with a `required-green` advisory",
          r_g == [] and len(adv_g) == 1 and adv_g[0].startswith("required-green: required context `gate`"))
    r_r, adv_r, _ = build({**clean, "gate": gate_digest(redgate), "required_read": ("RED", "pending: none red: gate")})
    check("null control: a required red that classify --pr reads RED still refuses, naming classify's line",
          len(r_r) == 1 and r_r[0].startswith("required-red: required context `gate`")
          and "RED pending: none red: gate" in r_r[0] and adv_r == [])
    wait_rd = ("WAIT", "pending: gate red: none")
    r_d, adv_d, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"], "required_read": wait_rd})
    check("S14 red-unanswered: a required `gate` red that classify --pr reads WAIT renders one required-wait "
          "advisory and no refusal", r_d == [] and len(adv_d) == 1 and adv_d[0].startswith("required-wait:"))
    r_dg, _, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"], "required_read": ("GREEN", "")})
    check("S14 red-unanswered: the same read GREEN renders", r_dg == [])
    r_dr, _, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"], "required_read": ("RED", "pending: none red: gate")})
    check("S14 red-unanswered null: the same with a RED read refuses red-unanswered and required-red",
          [x.split(":")[0] for x in r_dr] == ["red-unanswered", "required-red"])
    r_da, _, _ = build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"],
                        "required_read": ("APPROVAL-OWED", "1 raise")})
    check("S14 red-unanswered null: an APPROVAL-OWED read and an absent read keep the refusal",
          [x.split(":")[0] for x in r_da] == ["red-unanswered"]
          and "red-unanswered" in [x.split(":")[0] for x in build({**clean, "gate": gate_digest(redgate), "red_unanswered": ["gate"]})[0]])
    check("S14 red-unanswered null: a non-required red (`tests / fast`) beside a WAIT read still refuses",
          refused("red-unanswered", red_unanswered=["tests / fast"], required_read=wait_rd))
    with tempfile.TemporaryDirectory() as d:
        stub = Path(d) / "classify.sh"
        stub.write_text('echo "$*" > "$(dirname "$0")/argv"; echo "${PK_OUT:-}"; exit "${PK_RC:-1}"\n')
        saved = os.environ.get("HPO_PACKET_CLASSIFY")
        os.environ["HPO_PACKET_CLASSIFY"] = f"bash {stub}"
        try:
            os.environ.update(PK_OUT=f"APPROVAL-OWED {H} 1 budget raise(s): why", PK_RC="4")
            got = required_reading(7, H)
            argv = (Path(d) / "argv").read_text().split()
            os.environ.update(PK_OUT=f"RED {H} pending: none red: gate", PK_RC="1")
            red_line = required_reading(7, H)
            os.environ.update(PK_OUT=f"WAIT {H} pending: budget-raise-gate red: none", PK_RC="3")
            wait_line = required_reading(7, H)
            os.environ.update(PK_OUT=f"APPROVAL-OWED {B} 1 budget raise(s): why", PK_RC="4")
            other = required_reading(7, H)
            os.environ.update(PK_OUT=f"APPROVAL-OWED {H} 1 budget raise(s): why", PK_RC="1")
            wrong_rc = required_reading(7, H)
            os.environ.update(PK_OUT=f"REFUSE ci: the check runs at {H[:12]} could not be read", PK_RC="2")
            unread = required_reading(7, H)
        finally:
            os.environ.pop("PK_OUT", None), os.environ.pop("PK_RC", None)
            if saved is None:
                os.environ.pop("HPO_PACKET_CLASSIFY", None)
            else:
                os.environ["HPO_PACKET_CLASSIFY"] = saved
    check("P345: the reason is classify --pr's own APPROVAL-OWED line at rc 4, asked with the pull "
          "request; RED (rc 1), a line naming another head, and the line at any rc but 4 are RED (null controls)",
          got == ("APPROVAL-OWED", "1 budget raise(s): why") and argv[:2] == ["classify", H]
          and argv[-2:] == ["--pr", "7"] and red_line == ("RED", "pending: none red: gate")
          and other[0] == "RED" and wrong_rc[0] == "RED")
    check("#3379: classify's WAIT line at rc 3 is WAIT; a REFUSE at rc 2 (unread) fails closed as RED, naming it",
          wait_line == ("WAIT", "pending: budget-raise-gate red: none")
          and unread[0] == "RED" and "rc 2" in unread[1] and "could not be read" in unread[1])
    check("required-red null: the same head with that run green renders",
          build({**clean, "gate": gate_digest(list(reversed([dict(r, id=3 - r["id"]) for r in redgate])))})[0] == [])
    running = [{"id": 1, "name": "gate", "status": "in_progress", "conclusion": None},
               {"id": 2, "name": "tests / fast", "status": "queued", "conclusion": None}]
    st, lines, reds = gate_digest(running)
    check("a head with checks still running dispatches, digest pending with run ids",
          build({**clean, "gate": (st, lines, reds)})[0] == [] and st == "pending" and "gate id=1 in_progress" in lines)
    est, elines, _ = gate_digest([])
    check("a head with no run read is `none`, never `green`",
          est == "none" and elines == [] and build({**clean, "gate": (est, elines, [])})[0] == [])

    # A LATER ROUND IS ITS DELTA (tvofi, 2026-11-09). Null control first: a
    # first round, with no reviewed head, keeps the three-dot diff.
    check("scope null: a first round renders the three-dot diff and no delta or previous verdict",
          "## Review scope: full (first round" in t0 and "## Three-dot diff\nd\n" in t0
          and "## Delta diff" not in t0 and "## Previous verdict" not in t0)
    RH = "c" * 40
    pv = f"Fix review: blocked {RH} class-open: seam X\n\n## Findings\n\n- seam X is open. Carry: #1\n"
    _, _, td_ = build({**clean, "scope": ("delta", "later round"), "reviewed_head": RH, "previous_verdict": pv,
                       "diff": "delta-only\n"})
    check("scope: a later round renders `git diff <rh> <head>` and the previous verdict's findings, not the three-dot diff",
          f"## Delta diff: git diff {RH} {H}\ndelta-only\n" in td_ and f"## Previous verdict at {RH}" in td_
          and "- seam X is open." in td_ and "## Three-dot diff" not in td_ and "## Review scope: delta" in td_)
    # The exception's wording (tvofi, 2026-11-09): three qualifiers, no wider trigger.
    step12 = (ROOT / "dev/governance/roles/fix-review.md").read_text()
    step12 = step12[step12.index("Else a later round is"):]
    step12 = step12[:step12.index("\n13. ")]
    for label, text in (("the packet's scope line", td_), ("fix-review.md step 12", " ".join(step12.split()))):
        check(f"{label}: the exception names production code, non-obvious risk and CI's blindness, and the wider "
              "trigger wording is absent",
              "custom_components/" in text and "non-obvious" in text and "CI would not" in text
              and "reaches code that review relied on" not in text and "in full" not in text
              and ("never justifies a wider review" in text or "never widen it" in text))
    anc_yes, anc_no = (lambda a, b: True), (lambda a, b: False)
    check("review_scope: delta only with a reviewed head that is an ancestor and a verdict naming it; else full, saying why",
          review_scope(RH, H, pv, anc_yes)[0] == "delta"
          and review_scope(None, H, pv, anc_yes) == ("full", "first round: no --reviewed-head")
          and review_scope(RH, H, pv, anc_no)[0] == "full" and "not an ancestor" in review_scope(RH, H, pv, anc_no)[1]
          and review_scope(RH, H, None, anc_yes)[0] == "full" and "no verdict" in review_scope(RH, H, None, anc_yes)[1])
    vs = {"s3": f"Fix review: merge {H}\n", "s2": pv, "s1": f"Fix review: blocked {RH} old: first\n", "s0": "not a verdict\n"}
    check("previous_verdict: the newest verdict whose first line names <rh>; another head's, an older one and a "
          "malformed line are skipped; none naming it is None",
          previous_verdict(7, RH, ["s3", "s0", "s2", "s1"], vs.get) == pv
          and previous_verdict(7, B, ["s3", "s0", "s2", "s1"], vs.get) is None
          and previous_verdict(7, RH, [], vs.get) is None)

    # EVIDENCE IS NEVER WITHHELD: a refusal still writes the packet, except the
    # one signal a written packet would defeat.
    check("write-on-refusal null: a clean render writes", writes_packet([]))
    check("write-on-refusal: a concluded red still writes its packet", writes_packet(["required-red: gate"]))
    check("write-on-refusal: a host path writes nothing", not writes_packet(["host-path: a home directory"]))
    check("write-on-refusal: one host path beside other refusals still writes nothing",
          not writes_packet(["required-red: gate", "host-path: a home directory"]))

    # P275: #2914's shape -- a verdict note this PR does not settle, with no `Carry:`.
    note = (f"Fix review: merge {H}\n\n## Non-blocking notes\n\n- V149 (FLOW-BOARD): not blocking. "
            "Its ruling is a DEFER in s6-batch47.md and this PR does not settle it.\n")
    audit = lambda v: tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}", "--comments", cf(v)], "## Head\nx\n")[0]  # noqa: E731
    cfs: list[str] = []

    def cf(v: str) -> str:
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump([{"id": 0, "body": v}], f)
        f.close()
        cfs.append(f.name)
        return f.name
    try:
        check("self-audit: a verdict note with no Carry: gives rc 1", audit(note) == 1)
        check("self-audit: the same note with its own `Carry: dismissed:` gives rc 0",
              audit(note.rstrip() + " Carry: dismissed: ruled in s6-batch47, not this PR.\n") == 0)
        check("self-audit null: a verdict with no unrouted note gives rc 0", audit(f"Fix review: merge {H}\n\nNo notes.\n") == 0)
    finally:
        for f in cfs:
            os.unlink(f)

    # brief-carries (P256): every index on the group's roster entry is named.
    six = "".join(f"Carry {i}: answered.\n" for i in range(5))
    check("brief-carries: a body answering carries 0-4 of 6 (0-based, as the dispatch renders) is refused naming carry 5",
          unnamed_carries(six, 6) == [5]
          and handoff_refusals(None, [], unnamed_carries(six, 6)) == ["brief-carries: carry 5 is not named in the body (`Carry N`)"])
    check("brief-carries null: the same body with carry 5 dispositioned passes",
          unnamed_carries(six + "Carry 5: carried to R10-X.\n", 6) == [])
    check("S14 brief-carries: carry 0 is checked, and a one-carry group is not asked for carry 1",
          unnamed_carries("Carry 1: x\n", 1) == [0] and unnamed_carries("Carry 0: x\n", 1) == [])
    prompt21 = "preamble\n" + "".join(f"Carry {i}: text\n" for i in range(21)) + "Carry 21 is mentioned mid-line, not a carry line\n"
    check("S14 brief-carries: the dispatch PROMPT's Carry N: lines decide the set (21), not a live roster of 27",
          prompt_carries(prompt21) == list(range(21))
          and unnamed_carries("".join(f"Carry {i}: a\n" for i in range(21)), prompt_carries(prompt21)) == []
          and unnamed_carries("".join(f"Carry {i}: a\n" for i in range(1, 21)), prompt_carries(prompt21)) == [0])
    check("S14 brief-carries null: no PROMPT (None) falls to the live count, and a body missing a live carry is refused",
          prompt_carries(None) is None and prompt_carries("no carries here") is None
          and handoff_carries(None, 3) == 3 and unnamed_carries("Carry 0: a\nCarry 1: b\n", handoff_carries(None, 3)) == [2])
    check("S14 brief-carries: with a 21-carry PROMPT and 27 live carries the check runs over the PROMPT's 21",
          handoff_carries(prompt21, 27) == list(range(21)))
    full5 = "".join(f"Carry {i}: t\n" for i in range(5))
    hand = full5 + "This part: Carries 3, 2 (0-based roster indexes, texts verbatim below).\n"
    gen = full5 + "Part 2 of 3: build carries 2-3; the others are later parts dispatched at this part's handoff; answer none of them\n"
    gen2 = full5 + "Part 1 of 2: build carries 0-1+4; the others are later parts dispatched at this part's handoff; answer none of them\n"
    two = "Carry 2: a\nCarry 3: b\n"
    check("P593 brief-carries: a part assigned {2,3} (hand line) of a 5-carry prompt demands Carry 2 and Carry 3 only",
          prompt_carries(hand) == [2, 3] and unnamed_carries(two, handoff_carries(hand, 5)) == []
          and unnamed_carries("Carry 2: a\n", handoff_carries(hand, 5)) == [3])
    check("P593 brief-carries: the generated `Part k of N: build carries <runs>` line scopes alike, runs joined by +",
          prompt_carries(gen) == [2, 3] and unnamed_carries(two, handoff_carries(gen, 5)) == []
          and prompt_carries(gen2) == [0, 1, 4] and unnamed_carries("Carry 0: a\nCarry 1: b\n", handoff_carries(gen2, 5)) == [4])
    check("P593 brief-carries: a carry appended after dispatch (live 6, prompt holds 5) is not demanded",
          unnamed_carries(two, handoff_carries(hand, 6)) == [])
    check("P593 brief-carries null: no part line demands all 5 of the prompt; no prompt demands the live count",
          prompt_carries(full5) == list(range(5)) and part_carries(full5) is None
          and unnamed_carries(two, handoff_carries(full5, 5)) == [0, 1, 4] and handoff_carries(None, 5) == 5)
    check("P593 brief-carries: the refusal names its base only when given one",
          handoff_refusals(None, [], [3], None, " -- x") == ["brief-carries: carry 3 is not named in the body (`Carry N`) -- x"]
          and handoff_refusals(None, [], [3]) == ["brief-carries: carry 3 is not named in the body (`Carry N`)"])
    check("brief-carries null: a group with no carries passes", unnamed_carries("", 0) == [])
    check("brief-carries: `carry 1` does not name carry 10, and `Carry [10]` does",
          unnamed_carries("Carry 1: x\n", 11)[-1] == 10 and 10 not in unnamed_carries("Carry [10]: x\n", 11))
    check("handoff: structure and hot-file refuse beside the count, each named",
          [r.split(":")[0] for r in handoff_refusals("max_class_loc", ["#9 x"], [2])]
          == ["structure", "hot-file", "brief-carries"])
    check("handoff null: a clean head refuses nothing", handoff_refusals(None, [], []) == [])

    # carry-landed (L5): a carry cited as landed is on the roster ref at the cited sha.
    S1, S2 = "1" * 7, "2" * 40
    cites = landed_cites(f"Carry 4: landed at {S1} in the roster.\nCarry [5]: dispositioned, not built.\n")
    check("carry-landed: only a line that says landed cites a carry, with its index and sha", cites == [(4, S1)])
    at = {S1: 3}.get
    on = lambda sha: sha == S1  # noqa: E731
    bad = unlanded_carries(cites, lambda sha: at(sha, 0), on)
    check("carry-landed: a carry the roster entry holds too few of at the sha refuses, naming it",
          len(bad) == 1 and bad[0].startswith("carry-landed: carry 4 ") and refused("carry-landed", unlanded=bad))
    check("carry-landed: a sha off the roster ref refuses",
          len(unlanded_carries([(4, S2)], lambda sha: 9, on)) == 1)
    check("carry-landed null: the same body once the carry lands passes",
          unlanded_carries(cites, lambda sha: 4, on) == [])
    check("carry-landed null: a body citing no carry as landed passes",
          unlanded_carries(landed_cites("Carry 1: x\n"), lambda sha: 0, lambda sha: False) == [])
    check("carry-landed: the handoff refuses it beside the count",
          [r.split(":")[0] for r in handoff_refusals(None, [], [], bad)] == ["carry-landed"])

    prs = [{"number": 9, "head": H, "files": [HOT_FILES[0]], "merge_verdict_head": H}]
    check("hot-file arm: an unboarded merge verdict sharing a hot file refuses",
          len(hot_file_refusals({HOT_FILES[0]}, prs, set(), 7)) == 1)
    check("hot-file null: the same verdict boarded passes", hot_file_refusals({HOT_FILES[0]}, prs, {9}, 7) == [])
    # P368: the handoff's own pull request is not a collision with itself.
    own = [{"number": 9, "head": H, "branch": "fix/t-2", "files": [HOT_FILES[0]], "merge_verdict_head": H}]
    n, note = own_pr(own, "t", lambda sha: sha == H)
    check("hot-file own-pr arm (a): the pull request whose head is an ancestor is not refused against itself",
          n == 9 and note is None
          and handoff_hot({HOT_FILES[0]}, own, set(), "t", lambda sha: sha == H) == [])
    n2, _ = own_pr(own, "t-2", lambda sha: False)
    check("own-pr: with no ancestor, the head branch fix/<topic> identifies it", n2 == 9)
    other = [dict(own[0], number=11, head=B, branch="fix/other")]
    n3, _ = own_pr(own + other, "t", lambda sha: sha == H)
    check("hot-file own-pr arm (b) null: a different open pull request holding an unboarded merge verdict still refuses",
          n3 == 9 and len(handoff_hot({HOT_FILES[0]}, own + [dict(other[0], merge_verdict_head=B)], set(), "t",
                                      lambda sha: sha == H)) == 1)
    n4, note4 = own_pr(own + other, "t", lambda sha: True)
    check("hot-file own-pr arm (c): two ancestors are excluded neither and both are named",
          n4 == 0 and note4 and "#9" in note4 and "#11" in note4)
    check("hot-file null: a verdict at a stale head is not a merge verdict at its head",
          hot_file_refusals({HOT_FILES[0]}, [dict(prs[0], merge_verdict_head=B)], set(), 7) == [])
    check("hot-file reader: the verdict's head is the first line of VERDICT.md through proof_watch.parse_verdict",
          verdict_merge_head("d" * 40, read=lambda s: f"Fix review: merge {H}\nevidence: ev/\n") == H)
    check("hot-file reader null: a verdict-ref commit subject is not a verdict",
          verdict_merge_head("d" * 40, read=lambda s: f"verdict 7 {H}\n") is None)

    # red-unanswered, through policy_lint itself. ONLY A REQUIRED RED IS OWED
    # (owner ruling tvofi 2026-11-07): with the train's set given, main's
    # `nightly-status` red goes unnamed even on a diff touching the reporter's
    # own script, and so does a non-required check (a cancelled run is RED and
    # reaches here by name), while a required unit beside them is owed (the arm). The mutant treating every concluded
    # red as required owes all three. `req` is the train's set at the recorded
    # ruleset ([gate]): merge_train's judged(gating_names([gate])).
    import merge_train  # noqa: E402  (the one owner of the required set)
    req = merge_train.judged(merge_train.gating_names([merge_train.GATE]))
    unanswering = f"## Head\n{H}\n\n## Red checks\nnone\n"
    mixed = ["tests / nightly-status", "docs / links", "tests / typing"]
    rs = {"tests/nightly_status.py"}
    check("red-unanswered: with the required set read, only the required unit is owed, on a diff touching "
          "the reporter's own script", unanswered_reds(unanswering, H, B, mixed, rs, rs, req) == ["tests / typing"])
    check("red-unanswered null: a body naming every red is owed nothing",
          unanswered_reds(unanswering.replace("none", "\n".join(f"- `{n}`: answered" for n in mixed)),
                          H, B, mixed, rs, rs, req) == [])
    # Where the set cannot be read (an empty --required-file), the rule as it
    # stood (P282): main's `nightly-status` red is owed no answer by a diff
    # that leaves its inputs alone, `typing` beside it is (the arm); a diff
    # touching the reporter's own script owes both, and so does #2954's,
    # which touched the workflow that schedules it.
    both = ["tests / nightly-status", "typing"]
    check("red-unanswered unread set: main's nightly-status red is not owed by a diff touching only a test file",
          unanswered_reds(unanswering, H, B, both, {"tests/x.py"}, set(), []) == ["typing"])
    check("red-unanswered unread set: a diff touching tests/nightly_status.py owes both",
          unanswered_reds(unanswering, H, B, both, {"tests/nightly_status.py"}, {"tests/nightly_status.py"}, []) == both)
    wf = {".github/workflows/nightly.yml", ".github/workflows/governance.yml"}
    check("red-unanswered unread set: #2954's workflow diff still owes nightly-status",
          unanswered_reds(unanswering, H, B, both, wf, wf, []) == both)
    check("red-unanswered null: no concluded red reads nothing", unanswered_reds(unanswering, H, B, [], {"tests/x.py"}, set()) == [])
    # main's other reporter: every pull request adds its own delivery row, which
    # `--existing-file` keeps from reading as an input of `delivery-status`.
    ds, row = ["governance / delivery-status"], "dev/programme/delivery/9999.md"
    check("red-unanswered unread set: main's delivery-status red is not owed by a diff adding only its own row",
          unanswered_reds(unanswering, H, B, ds, {row}, set(), []) == [])
    check("red-unanswered unread set: a delivery row the base already had owes delivery-status",
          unanswered_reds(unanswering, H, B, ds, {row}, {row}, []) == ds)
    check("red-unanswered: under the train's set, a delivery row the base had owes delivery-status nothing",
          unanswered_reds(unanswering, H, B, ds, {row}, {row}, req) == [])
    try:
        unanswered_reds(unanswering, H, B, both, set(), set(), [])
        ok = False
    except Unavailable:
        ok = True
    check("red-unanswered: a path list policy_lint refuses is UNAVAILABLE, not no unanswered red", ok)

    # The independence arm reads a base blob, so it is driven over a checkout of
    # its own: a self-test must not need the tree it happens to be run in.
    # Built through `tests/throwaway_git.py`, the one way a tracked script
    # makes a throwaway repository: a raw `git init` spawns auto-maintenance
    # against a directory this test then deletes.
    with tempfile.TemporaryDirectory() as td:
        t = Path(td).resolve()
        sys.path.insert(0, str(ROOT / "tests"))
        import throwaway_git  # noqa: E402
        denv = throwaway_git.throwaway_git_init(t, "-q")

        def tgit(*a: str) -> str:
            return subprocess.run(["git", *a], cwd=t, env=denv,
                                  capture_output=True, text=True, check=True).stdout
        (t / "base_harness.py").write_text("# the finder's\n")
        tgit("add", "-A")
        tgit("commit", "-q", "-m", "base")
        base = tgit("rev-parse", "HEAD").strip()
        try:
            harness_source("base_harness.py", None, base, {"base_harness.py"}, t)
            ok = False
        except SystemExit as e:
            ok = "fixer's harness" in str(e)
        check("independence: a harness the diff edits is refused as the fixer's", ok)
        try:
            harness_source("no_such_harness.py", None, base, set(), t)
            ok = False
        except SystemExit as e:
            ok = "not the finder's" in str(e)
        check("independence: a harness absent at the base is refused", ok)
        label, data = harness_source("base_harness.py", None, base, set(), t)
        check("independence null: a base harness the diff leaves alone is the finder's",
              bool(data) and base in label)
        try:
            harness_source(None, str(t / "base_harness.py"), base, set(), t)
            ok = False
        except SystemExit as e:
            ok = "inside the tree" in str(e)
        check("independence: --harness-file inside the checkout is refused", ok)

        # handoff-not-applied (P229), over real ancestry: #2887's shape is the
        # bot's merge of the OLD head with main, the fixer's handoff tip outside it.
        def commit(msg: str, *parents: str) -> str:
            tree = tgit("rev-parse", f"{parents[0]}^{{tree}}").strip()
            return tgit("commit-tree", tree, *[x for p in parents for x in ("-p", p)], "-m", msg).strip()
        old = commit("old head", base)
        tip = commit("handoff tip", old)
        mainc = commit("main moves", base)
        stale, fresh = commit("merge old head + main", old, mainc), commit("merge tip + main", tip, mainc)

        def anc(a: str, b: str) -> bool:
            return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=t, env=denv).returncode == 0
        tips = {"g": tip}.get
        check("handoff-not-applied: #2887's shape (old head merged with main, tip outside) refuses",
              (handoff_not_applied("fix/g", stale, tips, anc)[0] or "").startswith(f"handoff/g {tip} is not an ancestor of {stale}")
              and refused("handoff-not-applied", handoff=handoff_not_applied("fix/g", stale, tips, anc)[0]))
        check("handoff-not-applied: the `fix/<t>-pr` spelling reads handoff/<t>",
              handoff_not_applied("fix/g-pr", stale, tips, anc)[0] is not None)
        check("handoff-not-applied null: a head containing the handoff tip renders",
              handoff_not_applied("fix/g", fresh, tips, anc)[0] is None)
        check("handoff-not-applied null: a pull request with no handoff ref renders",
              handoff_not_applied("fix/nohandoff", stale, tips, anc)[0] is None)
        check("handoff-not-applied null: a branch not spelled fix/<t> renders",
              handoff_not_applied("g", stale, tips, anc)[0] is None and handoff_not_applied("feat/g", stale, tips, anc)[0] is None)

        # S14 roster landing: the round roster branch outruns a landing, so a head
        # holding the snapshot its ## Head names renders (round topic only).
        snap = commit("roster snapshot", base)
        rtip = commit("roster moved on", snap)
        rtip2 = commit("roster moved on again", rtip)
        landing = commit("landing head", snap, mainc)
        side = commit("snapshot off the tip", base)
        side_head = commit("head holding the off-tip snapshot", side)
        rtips = {"g": rtip2}.get
        nbehind = lambda sha, tp: tgit("rev-list", "--count", f"{sha}..{tp}").strip()  # noqa: E731
        hb = lambda sha: f"## Head\n{sha}\n"  # noqa: E731
        ref, adv = handoff_not_applied("fix/g", landing, rtips, anc, hb(snap), "g", nbehind)
        check("S14 roster landing: the 3377 shape (head holds the named snapshot, an ancestor of the tip) renders "
              "with the advisory", ref is None and adv == f"roster snapshot {snap}, 2 commits behind handoff/g; a later landing takes the rest")
        check("S14 roster landing: a named snapshot not in the head is refused",
              handoff_not_applied("fix/g", landing, rtips, anc, hb(side), "g", nbehind)[0] is not None
              and handoff_not_applied("fix/g", landing, rtips, anc, hb(mainc), "g", nbehind)[0] is not None)
        check("S14 roster landing: a named snapshot that is an ancestor of the tip but not of the head is refused",
              handoff_not_applied("fix/g", landing, rtips, anc, hb(rtip), "g", nbehind)[0] is not None)
        check("S14 roster landing: a snapshot in the head but not an ancestor of the tip is refused",
              handoff_not_applied("fix/g", side_head, rtips, anc, hb(side), "g", nbehind)[0] is not None)
        check("S14 roster landing null: a fixer topic (not the round's) with the same shape is refused as today (#2887)",
              handoff_not_applied("fix/g", landing, rtips, anc, hb(snap), "other", nbehind)[0] is not None
              and handoff_not_applied("fix/g", landing, rtips, anc, hb(snap), None, nbehind)[0] is not None)

        # WHICH CHECKOUT, pinned by a read, not by a comment: every git read
        # goes through `repo()`, and `repo()` is the working directory's
        # checkout. Read from this self-test's own checkout instead and the
        # red is the one #2870's first head carried -- `git merge-base
        # origin/main <head>` dying with `Not a valid commit name <head>` on a
        # dispatch from a clone while `origin/main` was there all along.
        global _REPO_ROOT
        here, _REPO_ROOT = os.getcwd(), None
        try:
            os.chdir(t)
            got = git("rev-parse", "--show-toplevel").strip()
        finally:
            os.chdir(here)
            _REPO_ROOT = None
        check("repo(): a git read runs in the checkout the working directory is in, not the tool's install",
              Path(got) == t)

        # gather's path lists, over a real three-dot diff: the delivery row the
        # head adds is touched and not existing, so main's delivery-status red
        # is owed no answer through the same call gather makes.
        (t / "kept.txt").write_text("base\n")
        tgit("add", "-A")
        tgit("commit", "-q", "-m", "kept")
        pbase = tgit("rev-parse", "HEAD").strip()
        (t / "kept.txt").write_text("head\n")
        (t / "dev/programme/delivery").mkdir(parents=True)
        (t / row).write_text("row\n")
        tgit("add", "-A")
        tgit("commit", "-q", "-m", "head")
        phead = tgit("rev-parse", "HEAD").strip()
        here, _REPO_ROOT = os.getcwd(), None
        try:
            os.chdir(t)
            paths = diff_paths(pbase, phead)
        finally:
            os.chdir(here)
            _REPO_ROOT = None
        check("diff_paths: an added delivery row is touched, and only a file the base had is existing",
              paths == ({"kept.txt", row}, {"kept.txt"}))
        check("diff_paths -> red-unanswered: the row the diff adds owes main's delivery-status nothing",
              unanswered_reds(unanswering, H, B, ds, *paths, []) == [])

        # The scope over real commits: <rh> on top of pbase, the head on top of <rh>.
        (t / "kept.txt").write_text("round two\n")
        tgit("add", "-A")
        tgit("commit", "-q", "-m", "round two")
        rhead = tgit("rev-parse", "HEAD").strip()
        here, _REPO_ROOT = os.getcwd(), None
        try:
            os.chdir(t)
            later = scope_facts(7, phead, pbase, rhead, lambda pr, rh: f"Fix review: blocked {rh} x: y\n")
            first = scope_facts(7, None, pbase, rhead, lambda pr, rh: f"Fix review: blocked {rh} x: y\n")
            stray = scope_facts(7, rhead, pbase, phead, lambda pr, rh: f"Fix review: blocked {rh} x: y\n")
        finally:
            os.chdir(here)
            _REPO_ROOT = None
        check("scope_facts: a later round's diff is `git diff <rh> <head>` alone -- the round-one row is not in it",
              later["scope"][0] == "delta" and "+round two" in later["diff"] and row not in later["diff"])
        check("scope_facts null: a first round over the same head reads the three-dot diff, round one's row included",
              first["scope"][0] == "full" and "+round two" in first["diff"] and row in first["diff"])
        check("scope_facts null: a reviewed head that is not the head's ancestor reads the three-dot diff",
              stray["scope"][0] == "full" and row in stray["diff"])

        # UNAVAILABLE is a different outcome from a refusal: a seat that cannot
        # read the inputs reports rc 3 and writes nothing, and `bus.sh dispatch`
        # degrades on it. Driven through main(), the path bus.sh calls.
        import contextlib
        import io
        out = Path(td) / "unavailable.md"
        err = io.StringIO()
        here, _REPO_ROOT = os.getcwd(), None
        try:
            os.chdir(td)  # the temporary root is not itself a checkout
            with contextlib.redirect_stderr(err):
                rc = main(["render", "--pr", "7", "--head", H, "--out", str(out), "--no-structure"])
        finally:
            os.chdir(here)
            _REPO_ROOT = None
        check("UNAVAILABLE: a working directory outside a checkout exits 3, not 1, and writes nothing",
              rc == 3 and not out.exists() and "review_packet: UNAVAILABLE:" in err.getvalue())

    saved = os.environ.get("HPO_BUS_GH")
    os.environ["HPO_BUS_GH"] = "false"
    try:
        gh("repos/x/y")
        ok = False
    except Unavailable:
        ok = True
    finally:
        if saved is None:
            os.environ.pop("HPO_BUS_GH", None)
        else:
            os.environ["HPO_BUS_GH"] = saved
    check("UNAVAILABLE: a failing `gh` is unavailable, never a refusal", ok)

    try:
        git("rev-parse", "--verify", "no-such-ref-for-the-review-packet-self-test")
        ok = False
    except Unavailable:
        ok = True
    check("UNAVAILABLE: a git read that cannot resolve is unavailable, never a refusal", ok)

    # R10-INTRODUCED-REDS-BARRIER: an instrument-self-tests step red at the head
    # and not at the base refuses as INTRODUCED; inherited, no base run, a step
    # skipped by scoping and an unreadable job each read as the rule says.
    import merge_train
    drift = next(iter(merge_train.SELFTESTS_PUSH_ONLY))

    def reader(head_steps, base_steps, base_job=True, broken=(), head_concl=None, base_concl="failure"):
        reads: list[str] = []

        def read(path):
            reads.append(path)
            if any(b in path for b in broken):
                raise Unavailable(f"gh api {path}: HTTP 502")
            if path.endswith(f"commits/{H}/{merge_train.SELFTESTS_RUNS}"):
                return {"check_runs": [{"name": merge_train.SELFTESTS, "id": 1, "status": "completed",
                                        "conclusion": head_concl or ("failure" if head_steps else "success")}]}
            if path.endswith(f"commits/{B}/{merge_train.SELFTESTS_RUNS}"):
                return {"check_runs": [{"name": merge_train.SELFTESTS, "id": 2, "status": "completed",
                                        "conclusion": base_concl}] if base_job else []}
            return {"steps": head_steps if path.endswith("/jobs/1") else base_steps}
        return read, reads

    hs = [{"name": "census", "conclusion": "failure"}, {"name": "render", "conclusion": "failure"},
          {"name": "scoped", "conclusion": "skipped"}, {"name": drift, "conclusion": "failure"}]
    bs = [{"name": "census", "conclusion": "success"}, {"name": "render", "conclusion": "failure"},
          {"name": "scoped", "conclusion": "failure"}, {"name": drift, "conclusion": "failure"}]
    read, reads = reader(hs, bs)
    got = introduced_reading(H, B, read)
    check("introduced: the head's red the base lacks is INTRODUCED, the inherited one is not, by 2 job-step reads",
          got[0] == ["census"] and sum("/actions/jobs/" in p for p in reads) == 2)
    check("no base run: every head red but the push-only drift step counts; skipped is never red",
          introduced_reading(H, B, reader(hs, bs, base_job=False)[0])[0] == ["census", "render"])
    read, reads = reader([], bs)
    check("a head whose job did not conclude failure costs one listing and no job read",
          introduced_reading(H, B, read)[0] == [] and len(reads) == 1)
    for why, broken in (("the head's job", ("/jobs/1",)), ("the base's job", ("/jobs/2",)),
                        ("the base's listing", (f"commits/{B}/",)), ("the head's listing", (f"commits/{H}/",))):
        got = introduced_reading(H, B, reader(hs, bs, broken=broken)[0])
        check(f"fail closed: {why} unreadable refuses introduced-red, never reads clean",
              got[0] == [] and refused("introduced-red", introduced=got))
    r_i = build({**clean, "introduced": (["census"], "head job 1 base job 2")})[0]
    check("build: an INTRODUCED step is an introduced-red refusal naming the step",
          len(r_i) == 1 and r_i[0].startswith("introduced-red: INTRODUCED `census`"))
    check("null: an inherited-only head (nothing introduced) refuses nothing",
          build({**clean, "introduced": introduced_reading(H, B, reader(bs, bs)[0])})[0] == [])
    check("one notion of red: merge_train.RED_CONCLUSIONS is this file's RED", merge_train.RED_CONCLUSIONS == RED)
    hang = [{"name": "census", "conclusion": "cancelled"}, {"name": "render", "conclusion": "skipped"}]
    ok_s = [{"name": "census", "conclusion": "success"}, {"name": "render", "conclusion": "success"}]
    got = introduced_reading(H, B, reader(hang, ok_s, head_concl="timed_out", base_concl="success")[0])
    check("a hang the PR makes (job timed_out, step cancelled) is INTRODUCED: the step and the timeout, refused",
          got[0] == [merge_train.JOB_TIMED_OUT, "census"]
          and [r.split("`")[1] for r in build({**clean, "introduced": got})[0]] == got[0])
    got = introduced_reading(H, B, reader(hang, ok_s, base_concl="success")[0])
    check("a cancelled step inside a failed job is INTRODUCED", got[0] == ["census"])
    for why, concl in (("a job-level cancelled", "cancelled"), ("a job still running", "in_progress")):
        read, reads = reader(hang, ok_s, head_concl=concl)
        if concl == "in_progress":
            def read(path, _r=read):
                got = _r(path)
                for r in got.get("check_runs") or ():
                    r["status"], r["conclusion"] = "in_progress", None
                return got
        got = introduced_reading(H, B, read)
        check(f"fail closed: {why} at the head refuses introduced-red, never reads clean",
              got[0] == [] and refused("introduced-red", introduced=got))
    facts = ci_facts(7, H, B, reader(hs, bs)[0])
    check("gather's ci_facts carries the INTRODUCED reading build refuses (M9: its wiring)",
          facts["introduced"][0] == ["census"] and facts["required_read"] is None
          and refused("introduced-red", introduced=facts["introduced"]))

    print(f"review_packet self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return _self_test()
    p = argparse.ArgumentParser(prog="review_packet.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("--pr", type=int, required=True)
    r.add_argument("--head", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--main", default="origin/main")
    r.add_argument("--reviewed-head", help="the head a previous verdict names: a later round's packet is its delta")
    g = r.add_mutually_exclusive_group()
    g.add_argument("--harness")
    g.add_argument("--harness-file")
    r.add_argument("--harness-arg", action="append", default=[])
    r.add_argument("--no-structure", action="store_true", help="skip the structure merge check (self-test only)")
    h = sub.add_parser("handoff")
    h.add_argument("--topic", required=True)
    h.add_argument("--body", required=True)
    h.add_argument("--main", default="origin/main")
    h.add_argument("--roster-ref")
    c = sub.add_parser("check")
    c.add_argument("packet")
    c.add_argument("--head", required=True)
    a = p.parse_args(argv)
    if a.cmd == "check":
        got = packet_head(Path(a.packet).read_text()) if Path(a.packet).is_file() else None
        if got != a.head:
            print(f"review_packet: REFUSE stale: {a.packet} names head {got}, not {a.head}", file=sys.stderr)
            return 1
        return 0
    if a.cmd == "handoff":
        try:
            return handoff(a)
        except Unavailable as e:
            print(f"review_packet: UNAVAILABLE: {e}", file=sys.stderr)
            return 3
    if not re.fullmatch(r"[0-9a-f]{40}", a.head) or (a.reviewed_head and not re.fullmatch(r"[0-9a-f]{40}", a.reviewed_head)):
        print("review_packet: --head and --reviewed-head take a 40-hex sha", file=sys.stderr)
        return 2
    try:
        refusals, _, text = build(gather(a))
    except Unavailable as e:
        print(f"review_packet: UNAVAILABLE: {e}", file=sys.stderr)
        return 3
    keep = writes_packet(refusals)
    if keep:
        try:
            Path(a.out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.out).write_text(text)
        except OSError as e:
            print(f"review_packet: UNAVAILABLE: cannot write {a.out}: {e}", file=sys.stderr)
            return 3
    for x in refusals:
        print(f"review_packet: REFUSE {x}", file=sys.stderr)
    if keep:
        print(f"review-packet: {ref_privacy.home_relative(str(Path(a.out).resolve()))}")
    return 1 if refusals else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
