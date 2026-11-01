#!/usr/bin/env python3
"""closeout.py -- the round's final act: archive, prune and clean up after itself.

    python3 tools/audit/seat/closeout.py --roster-file FILE [--repo OWNER/REPO]
        [--remote origin] [--main origin/main] [--seats-root DIR ...]
        [--orch-root DIR] [--keep-orch NAME ...] [--report-dir DIR]
        [--issues-file FILE] [--successor N] [--verdicts-drained]
        [--apply] [--json]
    python3 tools/audit/seat/closeout.py --self-test

WHY THIS EXISTS (owner request, tvofi 2026-10-24). The programme must contain a
group that cleans up after itself and drives the open branches to the owner's
1-3 target: main plus at most two development branches, remote and local,
every other ref archived as a tag first. A session-local loop does this once
in a scratch directory and no later session can test it (decision 0013), so
this is the loop, with its ordering written as code. It COMPOSES the existing
instruments and owns none of their logic: `prune_refs.py` plans and writes the
refs, `worktree_gc.sh` does the final worktree collection, `state_docs.py`
names the state docs that must already be in main, `brief_lint.mjs` proves the
citations.

A DRY PLAN BY DEFAULT. Without `--apply` the run reads and prints; it writes
nothing, local or remote (the self-test asserts the remote's refs, the working
tree and the report directory are byte-equal after a dry run).

`--apply` REFUSES FIRST, ON THE ROSTER. It reads `--roster-file` and refuses,
naming each group, while any group other than R10-CLOSEOUT-CLEANUP (`--self-
group`) is not done -- R10-ARCH-DOCS and R10-ROUND-PLAYBOOK included. The run is
the round's last act, so the instrument enforces that itself. The dry plan
runs at any time and prints what the refusal would name.

THE STEPS, each gated by the one before (STEPS below is the order):
  1 in-main    the roster and the four state docs are in main (the roster
               branch and the state ref are read at run time and must not be
               deleted while a workflow or citation reads them), no policy file
               still cites a ref about to go (retarget it to the archive tag at
               the same sha), and `node tools/policy/brief_lint.mjs` passes.
  2 refs       prune_refs' plan over every remote branch, written by batched
               `git push`: every archive tag first, read back, then the
               deletes; a ref to delete without its tag at its own sha refuses
               the whole step before any delete.
  3 local      seat worktrees under the seat roots removed (one holding an
               unpushed commit, or uncommitted work, is reported and KEPT);
               scratch under the orchestrator root cleared except the ledger
               and state; `git worktree prune`; local branches reduced to what
               a kept worktree holds or what no remote or tag has; a final
               worktree_gc.
  4 issues     every open issue but the coordination issue's successor
               (`--successor`) is dispositioned. This step REFUSES to pass,
               and says how many are open; it closes nothing, because a
               disposition needs the number that closes it or the re-scope
               that keeps it, which is a judgement. Archiving merged cloud
               sessions is the orchestrator's (archive_session); the report
               says so rather than pretending to do it.
  5 report     counts before and after (refs by family, archive tags, worktrees,
               local branches, open issues, open pull requests) and every ref
               left with the rule that kept it, written under `--report-dir`.
               It is written on every `--apply` run, blocked or complete.

The remaining-branches target is REPORTED, never forced: an open-PR head, a live
`claude/*` session branch and a not-done group's `design/` ref are kept by
prune_refs' rules, and the report names each.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prune_refs  # noqa: E402
import roster_lib  # noqa: E402

SELF_GROUP = "R10-CLOSEOUT-CLEANUP"
MAX_BRANCHES = 2
ROOT = HERE.parents[2]
#: Where a bare citation of a ref about to go would break a reader (fixtures under
#: tools/ and tests/ name refs as data; `brief_lint` is their arbiter).
CITATION_PATHS = (".claude", ".github", "dev/governance", "dev/programme/rosters",
                  "CLAUDE.md", "AGENTS.md", "README.md")
CITED_RE = re.compile(r"(?<![\w./-])((?:handoff|handoff-body|fix|design|design-verdict|"
                      r"review|probe|claim|dispatch|record|verdict|ci-probe|wip-sync|brief)"
                      r"/[A-Za-z0-9._/-]*[A-Za-z0-9_])")
CITED_GREP = ("(handoff|handoff-body|fix|design|design-verdict|review|probe|claim|dispatch|"
              "record|verdict|ci-probe|wip-sync|brief)/[A-Za-z0-9._/-]+")
STEPS = ("in-main", "refs", "local", "issues", "report")   # the order is the gate


def roster_blockers(roster: dict, self_group: str = SELF_GROUP) -> list:
    """Every group other than `self_group` whose stage is not done, sorted."""
    return sorted(g for g in roster_lib.open_groups(roster) if g != self_group)


class Ctx:
    """The checkout, the roots and the readers. A test overrides the reads."""

    def __init__(self, a, roster: dict):
        self.repo, self.remote, self.main = a.repo, a.remote, a.main
        self.roster, self.roster_path = roster, a.roster_file
        self.seats = [Path(p).expanduser() for p in a.seats_root]
        self.orch = Path(a.orch_root).expanduser()
        self.keep_orch = tuple(a.keep_orch)
        self.report_dir = Path(a.report_dir)
        self.successor = a.successor
        self.issues_file = a.issues_file
        self.verdicts_drained = a.verdicts_drained
        self.now = time.time()
        self.checkout = Path(a.checkout)

    def git(self, *argv, cwd=None, check=False):
        r = subprocess.run(["git", *argv], cwd=cwd or self.checkout,
                           capture_output=True, text=True)
        if check and r.returncode:
            raise RuntimeError(f"git {' '.join(argv)}: {r.stderr.strip()[:200]}")
        return r

    def run_git(self, argv, **kw):          # the prune_refs `git=` runner
        return subprocess.run(argv, cwd=self.checkout, **kw)

    def heads(self) -> dict:
        """{branch: sha} on the remote, read in the checkout."""
        out = self.git("ls-remote", "--heads", self.remote, check=True).stdout
        return {ln.split()[1].split("refs/heads/", 1)[1]: ln.split()[0]
                for ln in out.splitlines() if "refs/heads/" in ln}

    # -- reads that a test replaces --------------------------------------
    def gh_json(self, *args):
        r = subprocess.run(["gh", *args], capture_output=True, text=True)
        return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None

    def open_issues(self):
        if self.issues_file:
            return json.load(open(self.issues_file, encoding="utf-8"))
        return self.gh_json("issue", "list", "--repo", self.repo, "--state", "open",
                            "--limit", "1000", "--json", "number,title")

    def open_prs(self):
        return self.gh_json("pr", "list", "--repo", self.repo, "--state", "all",
                            "--limit", "3000", "--json", "number,state,headRefName")

    def brief_lint(self):
        r = subprocess.run(["node", "tools/policy/brief_lint.mjs"], cwd=self.checkout,
                           capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr)[-400:]

    def worktree_gc(self):
        r = subprocess.run(["bash", "tools/audit/worktree_gc.sh", self.repo],
                           cwd=self.checkout, capture_output=True, text=True)
        return r.returncode, r.stdout.strip().splitlines()[-1:] or [""]


# -- snapshots -------------------------------------------------------------

def family_histogram(refs) -> dict:
    h: dict = {}
    for n in refs:
        h[prune_refs.family_of(n)] = h.get(prune_refs.family_of(n), 0) + 1
    return dict(sorted(h.items()))


def snapshot(c: Ctx) -> dict:
    """Counts at one moment. A count that cannot be read is None, never 0."""
    heads = c.heads()
    tags = c.git("ls-remote", "--tags", c.remote, "refs/tags/archive/*").stdout
    wts = [ln for ln in c.git("worktree", "list", "--porcelain").stdout.splitlines()
           if ln.startswith("worktree ")]
    local = c.git("for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split()
    issues, prs = c.open_issues(), c.open_prs()
    return {"heads": heads, "heads_by_family": family_histogram(heads),
            "archive_tags": len([ln for ln in tags.splitlines() if not ln.endswith("^{}")]),
            "worktrees": len(wts), "local_branches": sorted(local),
            "open_issues": None if issues is None else len(issues),
            "open_prs": None if prs is None else
            len([p for p in prs if p.get("state") == "OPEN"])}


# -- the steps -------------------------------------------------------------

def cited_refs(c: Ctx, doomed) -> dict:
    """{ref: [paths]} for each doomed ref a live policy path still names bare."""
    doomed = set(doomed)
    out: dict = {}
    r = c.git("grep", "-I", "-n", "-E", CITED_GREP, c.main, "--", *CITATION_PATHS)
    for line in r.stdout.splitlines():
        _, _, rest = line.partition(":")
        path, _, text = rest.partition(":")
        for m in CITED_RE.finditer(text.partition(":")[2] or text):
            if m.group(1) in doomed and path not in out.get(m.group(1), []):
                out.setdefault(m.group(1), []).append(path)
    return out


def step_in_main(c: Ctx, doomed, apply: bool) -> list:
    problems = []
    rel = f"dev/programme/rosters/{os.path.basename(c.roster_path)}"
    if c.git("cat-file", "-e", f"{c.main}:{rel}").returncode:
        problems.append(f"the roster {rel} is not in {c.main}")
    n = roster_lib.roster_round(rel)
    import state_docs
    for doc in state_docs.DOC_NAMES:
        p = f"dev/programme/round{n}/state/{doc}"
        if c.git("cat-file", "-e", f"{c.main}:{p}").returncode:
            problems.append(f"state doc {p} is not in {c.main}")
    for ref, paths in sorted(cited_refs(c, doomed).items()):
        problems.append(f"{ref} is cited bare by {paths[0]}"
                        + (f" (+{len(paths) - 1})" if len(paths) > 1 else "")
                        + f"; retarget it to {prune_refs.archive_tag(ref)}")
    rc, text = c.brief_lint()
    if rc:
        problems.append("brief_lint refuses: " + " ".join(text.split())[-160:])
    return problems


def plan_refs(c: Ctx, refs=None, prs=None) -> dict:
    refs = c.heads() if refs is None else refs
    prs = c.open_prs() if prs is None else prs
    if prs is None:
        raise ValueError("the pull requests cannot be read; a plan without them could "
                         "delete an open head")
    reach = set(c.git("rev-list", c.main, check=True).stdout.split())
    return prune_refs.plan(
        refs, prune_refs.index_prs(prs), reach, archive_scope="all",
        keep_residue=False, verdicts_drained=c.verdicts_drained,
        done_branches=prune_refs.done_group_branches(c.roster_path),
        open_groups=prune_refs.open_group_ids(c.roster_path),
        ages=prune_refs.tip_ages(refs.values(), c.now, git=c.run_git))


def step_refs(c: Ctx, p: dict, apply: bool) -> list:
    done = prune_refs.apply_plan_push(c.remote, p["actions"], not apply,
                                      untagged=p["untagged"], git=c.run_git)
    return [f"{v}: {d}" for v, d in done if v.endswith("FAILED")]


def _unpushed(c: Ctx, wt: Path) -> str:
    """Why a worktree holds work no remote ref or tag has; empty when it holds none."""
    st = c.git("-C", str(wt), "status", "--porcelain")
    if st.returncode or st.stdout.strip():
        return "dirty"
    n = c.git("-C", str(wt), "rev-list", "--count", "HEAD", "--not", "--remotes", "--tags")
    if n.returncode or not n.stdout.strip().isdigit():
        return "unreadable"
    return "unpushed" if int(n.stdout) else ""


def step_local(c: Ctx, apply: bool) -> dict:
    """Returns {"kept": [(path, why)], "removed": [...], "problems": [...]}."""
    kept, removed = [], []
    roots = [r.resolve() for r in c.seats if r.exists()]
    listing = c.git("worktree", "list", "--porcelain").stdout.split("\n\n")
    main_wt = os.path.realpath(c.checkout)
    for block in listing:
        path = next((ln[9:] for ln in block.splitlines() if ln.startswith("worktree ")), "")
        if not path or os.path.realpath(path) == main_wt:
            continue
        real = Path(os.path.realpath(path))
        if not any(r == real or r in real.parents for r in roots):
            continue
        why = _unpushed(c, real) if real.exists() else ""
        if why:
            kept.append((str(path), why))
        elif apply:
            r = c.git("worktree", "remove", "--force", str(path))
            (removed if r.returncode == 0 else kept).append(
                str(path) if r.returncode == 0 else (str(path), "remove-failed"))
        else:
            removed.append(str(path))
    if apply:
        c.git("worktree", "prune")
    # scratch under the orchestrator root, less the ledger and state
    if c.orch.is_dir():
        for e in sorted(c.orch.iterdir()):
            if e.name.startswith(c.keep_orch):
                continue
            removed.append(str(e))
            if apply:
                shutil.rmtree(e, ignore_errors=True) if e.is_dir() and not e.is_symlink() \
                    else e.unlink()
    # local branches: main and what a kept worktree has checked out stay
    held = {ln.split("refs/heads/", 1)[1] for ln in
            c.git("worktree", "list", "--porcelain").stdout.splitlines()
            if "refs/heads/" in ln and ln.startswith("branch ")}
    cur = c.git("symbolic-ref", "--short", "-q", "HEAD").stdout.strip()
    for b in c.git("for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split():
        if b in ("main", cur) or b in held:
            continue
        lost = c.git("rev-list", "--count", f"refs/heads/{b}", "--not", "--remotes", "--tags")
        if not lost.stdout.strip().isdigit() or int(lost.stdout):
            kept.append((f"branch {b}", "unpushed"))
        elif apply:
            c.git("branch", "-D", b)
            removed.append(f"branch {b}")
        else:
            removed.append(f"branch {b}")
    gc = ("not run (dry)", [""])
    if apply:
        gc = c.worktree_gc()
    return {"kept": kept, "removed": removed, "gc": gc, "problems": []}


def step_issues(c: Ctx) -> list:
    issues = c.open_issues()
    if issues is None:
        return ["the open issues cannot be read; nothing is dispositioned unseen"]
    rest = sorted(i["number"] for i in issues if i["number"] != c.successor)
    if rest:
        return [f"{len(rest)} open issue(s) beyond the successor "
                f"{'#' + str(c.successor) if c.successor else '(none named)'} "
                f"await a disposition, first #{rest[0]}"]
    return []


def render_report(before: dict, after: dict, p: dict, local: dict, status: str,
                  problems: list) -> str:
    def row(label, b, a):
        return f"| {label} | {b} | {a} |"
    fams = sorted(set(before["heads_by_family"]) | set(after["heads_by_family"]))
    lines = [f"# Round closeout report ({status})", "",
             "| count | before | after |", "|---|---|---|",
             row("remote branches", len(before["heads"]), len(after["heads"]))]
    lines += [row(f"  family `{f}`", before["heads_by_family"].get(f, 0),
                  after["heads_by_family"].get(f, 0)) for f in fams]
    lines += [row("archive tags", before["archive_tags"], after["archive_tags"]),
              row("archive tags added by this run", "", p["tags"]),
              row("worktrees", before["worktrees"], after["worktrees"]),
              row("local branches", len(before["local_branches"]),
                  len(after["local_branches"])),
              row("open issues", before["open_issues"], after["open_issues"]),
              row("open pull requests", before["open_prs"], after["open_prs"]), ""]
    kept = [(n, s, r) for n, s, _f, r, a in p["rows"] if a == "keep"]
    lines += [f"## Refs left ({len(kept)}) and the rule that kept each", ""]
    lines += [f"- `{n}` @ {s[:12]} -- {r}" for n, s, r in kept] or ["- none"]
    lines += ["", "## Worktrees and local branches kept", ""]
    lines += [f"- {w} -- {why}" for w, why in local["kept"]] or ["- none"]
    if problems:
        lines += ["", "## Blocked", ""] + [f"- {x}" for x in problems]
    lines += ["", "Merged cloud sessions are archived by the orchestrator "
              "(`archive_session`); this instrument does not."]
    return "\n".join(lines) + "\n"


def run(c: Ctx, apply: bool, out=print) -> int:
    """0 complete; 2 refused before writing; 3 stopped at a step (partial, reported)."""
    blockers = roster_blockers(c.roster)
    if blockers:
        out(("REFUSED" if apply else "DRY: --apply would REFUSE")
            + f": {len(blockers)} group(s) other than {SELF_GROUP} not done: "
            + ", ".join(blockers))
        if apply:
            return 2
    if apply:   # tip ages need the objects; an unread age keeps the ref (a dry run keeps them too)
        c.git("fetch", "--quiet", "--no-tags", c.remote, "+refs/heads/*:refs/remotes/origin/*")
    before = snapshot(c)
    p = plan_refs(c, before["heads"])
    by_rule: dict = {}
    for _n, _s, _f, rule, _a in p["rows"]:
        by_rule[rule] = by_rule.get(rule, 0) + 1
    out("rules: " + ", ".join(f"{k}={v}" for k, v in sorted(by_rule.items())))
    doomed = [a for v, a, _s in p["actions"] if v == "delete"]
    out(f"plan: {p['tags']} tag(s), {p['deletes']} delete(s), "
        f"{sum(1 for r in p['rows'] if r[4] == 'keep')} kept")
    problems: list = []
    local = {"kept": [], "removed": [], "gc": ("", [""]), "problems": []}
    for step in STEPS[:-1]:
        if step == "in-main":
            problems = step_in_main(c, doomed, apply)
        elif step == "refs":
            problems = step_refs(c, p, apply)
        elif step == "local":
            local = step_local(c, apply)
            problems = local["problems"]
            out(f"local: {len(local['removed'])} to remove, {len(local['kept'])} kept")
        else:
            problems = step_issues(c)
        out(f"step {step}: " + ("ok" if not problems else "BLOCKED"))
        for x in problems:
            out(f"  - {x}")
        if problems and apply:
            break
    if not apply:
        return 0
    after = snapshot(c)
    status = "COMPLETE" if not problems else "BLOCKED"
    c.report_dir.mkdir(parents=True, exist_ok=True)
    (c.report_dir / "CLOSEOUT-REPORT.md").write_text(
        render_report(before, after, p, local, status, problems), encoding="utf-8")
    left = len([n for n in after["heads"] if n != "main"])
    out(f"report: {c.report_dir / 'CLOSEOUT-REPORT.md'} ({status}); "
        f"{left} branch(es) beside main"
        + ("" if left <= MAX_BRANCHES else f" -- OVER the target of {MAX_BRANCHES}"))
    return 0 if not problems else 3


# -- self-test: a throwaway remote, every control ----------------------------

def self_test() -> int:
    import tempfile
    sys.path.insert(0, str(ROOT / "tests"))
    from throwaway_git import throwaway_git_init
    res: list = []

    def check(tag, cond):
        res.append((tag, bool(cond)))

    tmp = Path(tempfile.mkdtemp(prefix="closeout_selftest."))
    try:
        origin, seat = tmp / "origin.git", tmp / "seat"
        throwaway_git_init(origin, "-q", "--bare")
        env = throwaway_git_init(seat, "-q", "-b", "main")

        def g(*a, cwd=seat, ok=True):
            r = subprocess.run(["git", *a], cwd=cwd, env=env, capture_output=True, text=True)
            assert r.returncode == 0 or not ok, r.stderr
            return r.stdout.strip()

        def commit(f, text):
            (seat / f).parent.mkdir(parents=True, exist_ok=True)
            (seat / f).write_text(text)
            g("add", f)
            g("commit", "-q", "-m", f"add {f}")
            return g("rev-parse", "HEAD")

        def roster(stages):
            return {"groups": [{"group": k, "resume": {"stage": v}} for k, v in stages.items()]}

        g("remote", "add", "origin", str(origin))
        rp = "dev/programme/rosters/wave-r10-groups.json"
        (seat / "dev/programme/rosters").mkdir(parents=True)
        (seat / rp).write_text(json.dumps(roster({"A": "done", SELF_GROUP: "not-started"})))
        for d in ("PLAN-TABLE.md", "FLOW-BOARD.md", "RESUME-CURRENT.md", "NEXT-SESSION-PROMPT.md"):
            (seat / "dev/programme/round10/state").mkdir(parents=True, exist_ok=True)
            (seat / "dev/programme/round10/state" / d).write_text("x\n")
        g("add", "-A")
        g("commit", "-q", "-m", "base")
        base = commit("f", "0\n")
        g("checkout", "-q", "-b", "side", base)
        side = commit("side", "1\n")
        g("checkout", "-q", "main")
        g("push", "-q", "origin", "main", f"{side}:refs/heads/handoff/old-topic",
          f"{side}:refs/heads/handoff-body/old-topic", f"{side}:refs/heads/fix/open-pr",
          f"{base}:refs/heads/probe/merged")
        g("fetch", "-q", "origin")

        class A:
            repo, remote, main = "o/r", "origin", "origin/main"
            roster_file = rp
            seats_root = [str(tmp / "hpo-seats")]
            orch_root = str(tmp / "hpo-orch")
            keep_orch = ["ledger", "state"]
            report_dir = str(tmp / "report")
            issues_file = ""
            successor = 7
            verdicts_drained = False
            checkout = str(seat)

        class T(Ctx):
            lint_rc = 0
            issues = [{"number": 7, "title": "successor"}]
            prs = [{"number": 1, "state": "OPEN", "headRefName": "fix/open-pr"}]
            gc_calls = 0

            def git(self, *argv, cwd=None, check=False):
                r = subprocess.run(["git", *argv], cwd=cwd or self.checkout, env=env,
                                   capture_output=True, text=True)
                if check and r.returncode:
                    raise RuntimeError(r.stderr)
                return r

            def run_git(self, argv, **kw):
                return subprocess.run(argv, cwd=self.checkout, env=env, **kw)

            def open_issues(self):
                return self.issues

            def open_prs(self):
                return self.prs

            def brief_lint(self):
                return self.lint_rc, "lint says no" if self.lint_rc else "ok"

            def worktree_gc(self):
                T.gc_calls += 1
                return 0, ["gc ran"]

        def mk(stages, **kw):
            rj = tmp / "wave-r10-groups.json"
            rj.write_text(json.dumps(roster(stages)))
            a = A()
            a.roster_file = rj
            c = T(a, roster(stages))
            c.roster_path = str(rj)
            c.now = time.time() + 30 * 3600          # every tip older than the age guards
            for k, v in kw.items():
                setattr(c, k, v)
            return c

        def remote_state():
            return g("for-each-ref", "--format=%(refname) %(objectname)", cwd=origin)

        def tree_state():
            return g("status", "--porcelain") + g("for-each-ref", "refs/heads")

        quiet = lambda *_a: None  # noqa: E731
        open_one = {"A": "done", "B": "in-progress", SELF_GROUP: "not-started"}
        all_done = {"A": "done", "B": "done", SELF_GROUP: "not-started"}

        # dry run with a group open: prints the plan, names the refusal, writes nothing
        lines: list = []
        before_r, before_t = remote_state(), tree_state()
        rc = run(mk(open_one), False, lines.append)
        check("a dry run with a group open exits 0 and says --apply would refuse B",
              rc == 0 and any("would REFUSE" in x and "B" in x for x in lines))
        check("a dry run prints the plan",
              any(x.startswith("plan: ") for x in lines))
        check("a dry run writes nothing (remote refs, tree, report dir)",
              remote_state() == before_r and tree_state() == before_t
              and not (tmp / "report").exists())
        # --apply with a group open refuses, names the group, writes nothing
        lines = []
        rc = run(mk(open_one), True, lines.append)
        check("--apply with a group open refuses (rc 2) naming it",
              rc == 2 and any("REFUSED" in x and "B" in x for x in lines))
        check("...and wrote nothing", remote_state() == before_r
              and not (tmp / "report").exists())
        check("roster_blockers names every other open group and skips this one",
              roster_blockers(roster({"X": "not-started", "Y": "done", SELF_GROUP: "not-started"}))
              == ["X"])
        # null control: every other group done -> it proceeds into the steps
        lines = []
        c = mk(all_done, lint_rc=1)
        rc = run(c, True, lines.append)
        check("null: with every other group done, --apply gets past the roster to step 1",
              any(x.startswith("step in-main") for x in lines))
        check("step 1 blocks on a failing brief_lint and nothing is written after it",
              rc == 3 and any("brief_lint refuses" in x for x in lines)
              and remote_state() == before_r)
        check("a blocked run still writes the report, marked BLOCKED",
              "BLOCKED" in (tmp / "report/CLOSEOUT-REPORT.md").read_text())
        # a missing state doc blocks step 1
        lines = []
        mv = "dev/programme/round10/state/FLOW-BOARD.md"
        g("rm", "-q", mv)
        g("commit", "-q", "-m", "drop a state doc")
        g("push", "-q", "origin", "main")
        g("fetch", "-q", "origin")
        rc = run(mk(all_done), True, lines.append)
        check("a state doc missing from main blocks step 1",
              rc == 3 and any("FLOW-BOARD.md is not in" in x for x in lines))
        g("revert", "--no-edit", "HEAD")
        g("push", "-q", "origin", "main")
        g("fetch", "-q", "origin")

        # a policy file citing a ref about to go blocks step 1; its archive tag does not
        (seat / "dev/governance").mkdir(parents=True, exist_ok=True)
        (seat / "dev/governance/cites.md").write_text("see handoff/old-topic for the evidence\n")
        g("add", "-A")
        g("commit", "-q", "-m", "cite")
        g("push", "-q", "origin", "main")
        g("fetch", "-q", "origin")
        lines = []
        rc = run(mk(all_done), True, lines.append)
        check("a policy file still citing a doomed ref blocks step 1, naming the retarget",
              rc == 3 and any("handoff/old-topic is cited bare" in x
                              and "archive/handoff/old-topic" in x for x in lines))
        (seat / "dev/governance/cites.md").write_text("see archive/handoff/old-topic for the evidence\n")
        g("commit", "-q", "-am", "retarget")
        g("push", "-q", "origin", "main")
        g("fetch", "-q", "origin")

        # a worktree with an unpushed commit, and one clean at a pushed head
        for d in (tmp / "hpo-seats").glob("*"):
            shutil.rmtree(d)
        (tmp / "hpo-seats").mkdir()
        g("worktree", "add", "-q", "-b", "wip", str(tmp / "hpo-seats/unpushed"), "main")
        g("-C", str(tmp / "hpo-seats/unpushed"), "commit", "-q", "--allow-empty", "-m", "local only")
        g("worktree", "add", "-q", "--detach", str(tmp / "hpo-seats/clean"), "origin/main")
        (tmp / "hpo-orch").mkdir()
        (tmp / "hpo-orch/ledger.jsonl").write_text("{}\n")
        (tmp / "hpo-orch/scratch").mkdir()
        (tmp / "hpo-orch/scratch/junk").write_text("j\n")

        lines = []
        rc = run(mk(all_done), True, lines.append)
        after = remote_state()
        check("--apply with every other group done runs steps 1-3; step 4 passes with only the successor",
              rc == 0 and any(x.startswith("step issues: ok") for x in lines))
        check("every tag precedes every delete: the archive tags exist at the old shas",
              all(f"refs/tags/archive/{n} {side}" in after
                  for n in ("handoff/old-topic", "handoff-body/old-topic")))
        check("the deleted refs are gone from the remote",
              "refs/heads/handoff/old-topic" not in after
              and "refs/heads/probe/merged" not in after)
        check("null control: main and the open-PR head are kept",
              "refs/heads/main" in after and "refs/heads/fix/open-pr" in after)
        check("a worktree holding an unpushed commit survives",
              (tmp / "hpo-seats/unpushed").is_dir())
        check("null: the clean seat worktree at a pushed head is removed",
              not (tmp / "hpo-seats/clean").exists())
        check("scratch under the orchestrator root goes, the ledger stays",
              not (tmp / "hpo-orch/scratch").exists() and (tmp / "hpo-orch/ledger.jsonl").exists())
        check("the unpushed branch is not deleted, and the final worktree_gc ran once",
              g("rev-parse", "--verify", "-q", "refs/heads/wip") != "" and T.gc_calls == 1)
        rep = (tmp / "report/CLOSEOUT-REPORT.md").read_text()
        check("the report states COMPLETE, the left refs with their rule, and the kept worktree",
              "(COMPLETE)" in rep and "`fix/open-pr`" in rep and "keep" in rep
              and "unpushed" in rep and "Merged cloud sessions" in rep)

        # step 4 refuses while an issue beyond the successor is open
        lines = []
        rc = run(mk(all_done, issues=[{"number": 7, "title": "s"}, {"number": 9, "title": "x"}]),
                 True, lines.append)
        check("an open issue beyond the successor blocks step 4 and the report says BLOCKED",
              rc == 3 and any("await a disposition, first #9" in x for x in lines)
              and "BLOCKED" in (tmp / "report/CLOSEOUT-REPORT.md").read_text())
        check("unreadable issues block step 4 (never read as zero)",
              step_issues(mk(all_done, issues=None)) != [])

        # every tag precedes every delete: a delete lacking its tag refuses the whole step
        refs = mk(all_done).heads()
        g("push", "-q", "origin", f"{side}:refs/heads/fix/late")
        bad = [("delete", "fix/late", side)]
        try:
            prune_refs.apply_plan_push("origin", bad, False, git=mk(all_done).run_git)
            refused = False
        except prune_refs.ApplyRefused:
            refused = True
        check("a ref to be deleted that lacks its archive tag refuses",
              refused and "refs/heads/fix/late" in remote_state() and refs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for _t, v in res if v)
    for tag, v in res:
        print(f"  {'PASS' if v else 'FAIL'}  {tag}")
    print(f"closeout self-test: {len(res)} checks, {len(res) - ok} failed")
    return 0 if ok == len(res) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--main", default="origin/main")
    ap.add_argument("--checkout", default=".")
    ap.add_argument("--roster-file", default="")
    ap.add_argument("--seats-root", action="append",
                    default=None, help="repeatable; default ~/hpo-seats and ~/.local/state/hpo/pr")
    ap.add_argument("--orch-root", default="~/hpo-orch")
    ap.add_argument("--keep-orch", action="append", default=None,
                    help="name prefixes kept under --orch-root (default ledger, state)")
    ap.add_argument("--report-dir", default="dev/audit/rounds/round10")
    ap.add_argument("--issues-file", default="")
    ap.add_argument("--successor", type=int, default=0)
    ap.add_argument("--verdicts-drained", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not a.roster_file:
        print("closeout: REFUSE: --roster-file is required (the gate reads it)", file=sys.stderr)
        return 2
    a.seats_root = a.seats_root or ["~/hpo-seats", "~/.local/state/hpo/pr"]
    a.keep_orch = a.keep_orch or ["ledger", "state"]
    roster = json.load(open(a.roster_file, encoding="utf-8"))
    try:
        return run(Ctx(a, roster), a.apply)
    except (ValueError, prune_refs.ApplyRefused) as e:
        print(f"closeout: REFUSED: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
