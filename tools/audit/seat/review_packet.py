#!/usr/bin/env python3
"""The fix reviewer's packet: the facts a review gathers, rendered once at the frozen head.

    review_packet.py render --pr N --head SHA --out FILE [--main REF]
                            [--harness PATH | --harness-file FILE] [--harness-arg A]...
    review_packet.py check FILE --head SHA     (rc 1: the packet names another head)
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
  structure        `tests/structure.py` refuses the head merged with main;
  red-unanswered   a CONCLUDED red check the body's `## Red checks` does not name
                   (`policy_lint.mjs --pr-body --red`);
  required-red     a required context's latest run concluded failure;
  host-path        the body or an added line names this host (`ref_privacy.py`);
  hot-file         the diff shares a HOT_FILES path with an open pull request
                   whose merge verdict is at its head and not on the train.
A pending check never refuses. Every other finding prints as an advisory.

EVIDENCE IS NEVER WITHHELD. A refusal that leaves the packet truthful still
WRITES it and then exits 1, so whoever holds a refused dispatch reads the same
facts the reviewer would have: `bus.sh dispatch` dies on the rc and records
nothing, which is the dispatch gate. `host-path` alone writes nothing -- the
packet carries the three-dot diff, so writing it copies the host path into a
file that travels to a reviewer.
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
            raise SystemExit("review_packet: REFUSED repo: the working directory is not inside a git checkout")
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
SIGNALS = ("carry-audit", "head-note", "structure", "red-unanswered", "required-red", "host-path", "hot-file")


def git(*a: str, cwd: Path | None = None, check: bool = True) -> str:
    r = subprocess.run(["git", *a], cwd=cwd or repo(), capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"review_packet: REFUSED git {' '.join(a)}: {r.stderr.strip()[:200]}")
    return r.stdout


def gh(path: str):
    cmd = shlex.split(os.environ.get("HPO_BUS_GH", "gh")) + ["api", path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"review_packet: REFUSED gh api {path}: {(r.stderr or r.stdout).strip()[:200]}")
    return json.loads(r.stdout or "null")


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


def head_note_ok(body: str, head: str) -> bool:
    return head in section(body, "Head")


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


def verdict_merge_head(sha: str, read=None) -> str | None:
    """The head a merge verdict names, or None: the first line of `VERDICT.md`
    in the verdict ref's commit, parsed by `proof_watch.parse_verdict`, the one
    Python reader of the grammar (`agreement_py.py` refuses a copy)."""
    read = read or (lambda s: git("show", f"{s}:VERDICT.md", check=False))
    lines = read(sha).splitlines()
    v = proof_watch.parse_verdict(lines[0]) if lines else None
    return v[1] if v and v[0] == "merge" else None


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
        a = subprocess.run(["git", "archive", rev], cwd=root, capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(tree)], input=a.stdout, check=True)
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
        a = subprocess.run(["git", "archive", tree], cwd=root, capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", d], input=a.stdout, check=True)
        s = subprocess.run([sys.executable, "tests/structure.py"], cwd=d, capture_output=True, text=True)
        if s.returncode:
            return (s.stdout + s.stderr).replace(d, "<tmp>").strip().splitlines()[-1][:300]
    return None


def tool(argv: list[str], body: str) -> tuple[int, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(body)
    try:
        r = subprocess.run([a.replace("{BODY}", f.name) for a in argv], cwd=repo(), capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).replace(f.name, "<body>").strip()
    finally:
        os.unlink(f.name)


def writes_packet(refusals: list[str]) -> bool:
    """How a render treats its own refusals: written unless it is unpublishable.

    Evidence is never withheld -- a refused dispatch leaves the packet on disk
    for whoever must repair it. `host-path` is the one signal a written packet
    would defeat, because the packet carries the three-dot diff verbatim.
    """
    return not any(r.startswith("host-path:") for r in refusals)


# ------------------------------------------------------------------- the packet
def build(facts: dict) -> tuple[list[str], list[str], str]:
    """(refusals, advisories, packet text) from gathered facts; pure."""
    head, body = facts["head"], facts["body"]
    state, gate_lines, reds = facts["gate"]
    refusals: list[str] = []
    if facts["carry_rc"]:
        refusals.append("carry-audit: carry_audit.py check returned 1 on the body")
    if not head_note_ok(body, head):
        refusals.append(f"head-note: ## Head does not name the dispatched head {head}")
    if facts["structure"]:
        refusals.append(f"structure: tests/structure.py refuses the head merged with main: {facts['structure']}")
    for n in facts["red_unanswered"]:
        refusals.append(f"red-unanswered: concluded red check `{n}` is not named in ## Red checks")
    for n in sorted(set(reds) & set(REQUIRED)):
        refusals.append(f"required-red: required context `{n}` concluded failure at {head}")
    for w in facts["host"]:
        refusals.append(f"host-path: {w}")
    for w in facts["hot"]:
        refusals.append(f"hot-file: {w}")
    advisories = [a for a in facts.get("advisories", [])]
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
        "## Three-dot diff", facts["diff"],
    ]
    return refusals, advisories, "\n".join(parts) + "\n"


def gather(a) -> dict:
    head, main = a.head, a.main
    base = git("merge-base", main, head).strip()
    touched = set(git("diff", "--name-only", "--no-renames", f"{base}...{head}").split())
    label, data = (harness_source(a.harness, a.harness_file, base, touched)
                   if (a.harness or a.harness_file) else ("none named", b""))
    body = gh(f"repos/{REPO}/pulls/{a.pr}").get("body") or ""
    runs = gh(f"repos/{REPO}/commits/{head}/check-runs?per_page=100").get("check_runs", [])
    gate = gate_digest(runs)
    crc, cout = tool([sys.executable, "-I", "tools/audit/carry_audit.py", "check", "--body", "{BODY}"], body)
    _, fout = tool(["node", "tools/policy/figure_lint.mjs", "--pr-body", "{BODY}", "--at", head], body)
    red_unanswered = []
    if gate[2]:
        _, pout = tool(["node", "tools/policy/policy_lint.mjs", "--pr-body", "{BODY}", "--head", head,
                        *[x for n in gate[2] for x in ("--red", n)]], body)
        red_unanswered = sorted(n for n in gate[2] if f"check `{n}` is red and `## Red checks` does not name it" in pout)
    ident = ref_privacy.Identity.of_host()
    host = [w for w in [ref_privacy.body_refusal(body, ident)] if w]
    host += ref_privacy.content_refusals(ref_privacy.added_lines(base, head, repo()), ident)
    open_prs, boarded = [], set()
    if touched & set(HOT_FILES):
        for p in gh(f"repos/{REPO}/pulls?state=open&per_page=100"):
            files = [f["filename"] for f in gh(f"repos/{REPO}/pulls/{p['number']}/files?per_page=100")]
            tip = git("ls-remote", "origin", f"refs/heads/verdict/{p['number']}", check=False).split()
            merge_head = None
            if tip and not git("fetch", "-q", "origin", f"refs/heads/verdict/{p['number']}", check=False):
                merge_head = verdict_merge_head(tip[0])
            open_prs.append({"number": p["number"], "head": p["head"]["sha"], "files": files,
                             "merge_verdict_head": merge_head})
        boarded = train_boarded()
    return {
        "pr": a.pr, "head": head, "base": base, "body": body, "gate": gate,
        "carry_rc": crc, "carry_out": cout, "figure_out": fout,
        "structure": None if a.no_structure else structure_at_merge(main, head),
        "red_unanswered": red_unanswered, "host": host,
        "hot": hot_file_refusals(touched, open_prs, boarded, a.pr),
        "advisories": [] if os.environ.get("HPO_BUS_TRAIN_STATE") or not open_prs
        else ["hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded"],
        "harness_label": label,
        "harness_base": run_harness(data, base, a.harness_arg) if data else "not run",
        "harness_head": run_harness(data, head, a.harness_arg) if data else "not run",
        "ledger_diff": git("diff", f"{base}...{head}", "--", LEDGER),
        "diff": git("diff", f"{base}...{head}"),
    }


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
    check("the packet carries the head's harness output and names the head",
          "RESULT 0" in t0 and packet_head(t0) == H)
    check("check names a stale packet: another head does not match", packet_head(t0) != B)

    def refused(signal: str, **kw) -> bool:
        r, _, _ = build({**clean, **kw})
        return len(r) == 1 and r[0].startswith(signal + ":")

    check("carry-audit: an unrouted body refuses and names it", refused("carry-audit", carry_rc=1))
    check("head-note: a ## Head naming another head refuses", refused("head-note", body=f"## Head\n{B}\n"))
    check("structure: a structure refusal at the merge refuses", refused("structure", structure="max_class_loc"))
    check("red-unanswered: an unanswered concluded red refuses", refused("red-unanswered", red_unanswered=["tests / fast"]))
    check("host-path: a host path refuses", refused("host-path", host=["home-directory in the body"]))
    check("hot-file: a shared hot file with an unboarded merge verdict refuses", refused("hot-file", hot=["#9 x"]))
    redgate = [{"id": 1, "name": "gate", "status": "completed", "conclusion": "success"},
               {"id": 2, "name": "gate", "status": "completed", "conclusion": "failure"}]
    check("required-red: the required context's latest run concluded failure refuses",
          refused("required-red", gate=gate_digest(redgate)))
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

    # EVIDENCE IS NEVER WITHHELD: a refusal still writes the packet, except the
    # one signal a written packet would defeat.
    check("write-on-refusal null: a clean render writes", writes_packet([]))
    check("write-on-refusal: a concluded red still writes its packet", writes_packet(["required-red: gate"]))
    check("write-on-refusal: a host path writes nothing", not writes_packet(["host-path: a home directory"]))
    check("write-on-refusal: one host path beside other refusals still writes nothing",
          not writes_packet(["required-red: gate", "host-path: a home directory"]))

    prs = [{"number": 9, "head": H, "files": [HOT_FILES[0]], "merge_verdict_head": H}]
    check("hot-file arm: an unboarded merge verdict sharing a hot file refuses",
          len(hot_file_refusals({HOT_FILES[0]}, prs, set(), 7)) == 1)
    check("hot-file null: the same verdict boarded passes", hot_file_refusals({HOT_FILES[0]}, prs, {9}, 7) == [])
    check("hot-file null: a verdict at a stale head is not a merge verdict at its head",
          hot_file_refusals({HOT_FILES[0]}, [dict(prs[0], merge_verdict_head=B)], set(), 7) == [])
    check("hot-file reader: the verdict's head is the first line of VERDICT.md through proof_watch.parse_verdict",
          verdict_merge_head("d" * 40, read=lambda s: f"Fix review: merge {H}\nevidence: ev/\n") == H)
    check("hot-file reader null: a verdict-ref commit subject is not a verdict",
          verdict_merge_head("d" * 40, read=lambda s: f"verdict 7 {H}\n") is None)

    # The independence arm reads a base blob, so it is driven over a checkout of
    # its own: a self-test must not need the tree it happens to be run in.
    with tempfile.TemporaryDirectory() as td:
        t = Path(td).resolve()

        def tgit(*a: str) -> str:
            return subprocess.run(["git", "-C", str(t), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                  capture_output=True, text=True, check=True).stdout

        tgit("init", "-q")
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
    g = r.add_mutually_exclusive_group()
    g.add_argument("--harness")
    g.add_argument("--harness-file")
    r.add_argument("--harness-arg", action="append", default=[])
    r.add_argument("--no-structure", action="store_true", help="skip the structure merge check (self-test only)")
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
    if not re.fullmatch(r"[0-9a-f]{40}", a.head):
        print("review_packet: --head takes a 40-hex sha", file=sys.stderr)
        return 2
    refusals, _, text = build(gather(a))
    keep = writes_packet(refusals)
    if keep:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text)
    for x in refusals:
        print(f"review_packet: REFUSE {x}", file=sys.stderr)
    if keep:
        print(f"review-packet: {ref_privacy.home_relative(str(Path(a.out).resolve()))}")
    return 1 if refusals else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
