#!/usr/bin/env python3
"""Replay the five closure incidents against the gate as it is and as #354 makes it.

WHAT IT MEASURES
    For each incident, whether the `closures` job would RUN on the pull
    request, under (a) the rule on main today -- "the diff adds a file under
    custom_components/" -- and (b) the `closure.py affected` predicate this
    branch introduces. The verdict is not reasoned about: the pull request's
    diff is reconstructed from the merge commit against its first parent, the
    new `closure.py` is run against the table AS IT WAS AT THE PULL REQUEST'S
    BASE, and the `if:` expression of the `closures` job is read out of
    `.github/workflows/tests.yml` and evaluated.

    Metric definition, one line: `closures` job fires (yes/no) for a diff,
    per the committed workflow `if:` expression and the committed predicate.

RUN IT
    python3 tools/audit/round3/closures-gate/replay.py

    Add --steps to additionally dry-run the job's own shell (the re-record and
    check steps) with `derive_closures.sh` and `closure.py` stubbed, so the
    scoped/full branch and the `--partial` selection are executed rather than
    read.

EXPECTED
    Ten incident rows. Every row's `new` column is RUN. The `today` column is
    RUN for the four whose diff adds an integration file and SKIP for the six
    that do not -- which is the bug: three of those six are the repair pull
    requests for the incidents above them, checked by nothing.

BASELINE
    Measured against 599f482 (origin/main at the time), on darwin 25.6.0.
    No timing is claimed here; every number is a count or a decision, so the
    thread pin and load the harness contract asks for do not apply.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"

# (label, merge commit, what the incident was)
#
# The issue names five numbers. Three of them -- #214, #320, #332 -- are the
# REPAIR pull requests: the closure was already stale when they were opened,
# and their own diff is the fix. The pull request that had to be caught is the
# one whose merge made main red, so both are replayed: the repair (which must
# be checked before merge, and today is not) and the offender (which must fail
# before merge, and today does not).
INCIDENTS = [
    ("#214 repair",   "f34cb99", "records the closure diagnostics.py already had"),
    ("#209 offender", "430cdb4", "adds custom_components/.../diagnostics.py"),
    ("#320 repair",   "c408dd7", "records the closures icons.json + quality_scale.yaml had"),
    ("#229 offender", "6d83f0b", "adds custom_components/.../quality_scale.yaml"),
    ("#308 offender", "de668be", "adds custom_components/.../icons.json"),
    ("#332 repair",   "5ddea55", "records entity.py, adds the new-integration-file job"),
    ("#316 offender", "890ecbd", "adds custom_components/.../entity.py"),
    ("#340 both",     "ca937da", "adds services.py AND its closure update -- the half that fires today"),
    ("#349 offender", "29f0dc7", "tests/features.py gains tests/run.sh; main red at 599f482"),
    ("#353 repair",   "2a64519", "records the run.sh dependency; its own check said `skipping`"),
]


# ---------------------------------------------------------------------------
# a GitHub expression evaluator, small enough to be obviously right


class Ctx:
    def __init__(self, event_name: str, needs: dict, states: dict | None = None):
        self.event_name = event_name
        self.needs = needs
        # Per-dependency job status. GitHub puts an implicit success() over
        # `needs` on every `if:` that does not itself call a status function,
        # so a job whose dependency was SKIPPED is skipped too, whatever its
        # own condition says. That is what `always()` is there to defeat, and
        # it is the reason `closure-scope` -- which only runs on a pull
        # request -- cannot be allowed to switch the check off on main.
        self.states = states or {}


_TOKEN = re.compile(
    r"\s*(always\(\)|&&|\|\||==|!=|\(|\)|'[^']*'|[A-Za-z_][A-Za-z0-9_.\-]*)")


def _tokens(expr: str) -> list[str]:
    out, i = [], 0
    while i < len(expr):
        m = _TOKEN.match(expr, i)
        if not m:
            if expr[i].isspace():
                i += 1
                continue
            raise ValueError(f"cannot tokenise at {expr[i:][:30]!r}")
        out.append(m.group(1))
        i = m.end()
    return out


def evaluate(expr: str, ctx: Ctx):
    """Evaluate a GitHub `if:` expression: always(), && || == !=, (), literals."""
    toks = _tokens(expr)
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def take():
        nonlocal pos
        t = toks[pos]
        pos += 1
        return t

    def atom():
        t = take()
        if t == "(":
            v = or_()
            assert take() == ")"
            return v
        if t == "always()":
            return True
        if t.startswith("'"):
            return t[1:-1]
        if t == "github.event_name":
            return ctx.event_name
        if t.startswith("needs."):
            _, job, kind, key = t.split(".", 3)
            if kind != "outputs":
                raise ValueError(t)
            # A skipped or failed job has no outputs at all; GitHub yields the
            # empty string, which is exactly the case this gate must not read
            # as "nothing to do".
            return ctx.needs.get(job, {}).get(key, "")
        raise ValueError(f"unknown term {t!r}")

    def cmp_():
        left = atom()
        while peek() in ("==", "!="):
            op = take()
            right = atom()
            left = (left == right) if op == "==" else (left != right)
        return left

    def and_():
        left = cmp_()
        while peek() == "&&":
            take()
            right = cmp_()
            left = right if left else left
        return left

    def or_():
        left = and_()
        while peek() == "||":
            take()
            right = and_()
            left = left if left else right
        return left

    v = or_()
    if pos != len(toks):
        raise ValueError(f"trailing tokens {toks[pos:]}")
    return bool(v)


_STATUS_FN = re.compile(r"\b(always|failure|cancelled)\(\)")


def fires(expr: str, ctx: Ctx) -> bool:
    """Does the job run? The `if:` expression AND GitHub's implicit success()."""
    if not _STATUS_FN.search(expr):
        if any(s != "success" for s in ctx.states.values()):
            return False
    return evaluate(expr, ctx)


def job_ifs() -> dict:
    import yaml

    wf = yaml.safe_load(WORKFLOW.read_text())
    return {name: (j.get("if") or "true") for name, j in wf["jobs"].items()}


def job_step(job: str, step_name: str) -> str:
    import yaml

    wf = yaml.safe_load(WORKFLOW.read_text())
    for st in wf["jobs"][job]["steps"]:
        if st.get("name") == step_name:
            return st["run"]
    raise KeyError(f"{job}: no step named {step_name!r}")


# ---------------------------------------------------------------------------
# the incidents


def git(*args, cwd=ROOT) -> str:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def diff_of(sha: str) -> tuple[str, list[str]]:
    """The pull request's change: the merge commit against its first parent."""
    base = git("rev-parse", f"{sha}^1").strip()
    files = [l for l in git("diff", "--name-only", base, sha).splitlines() if l]
    return base, files


def today_rule(base: str, sha: str) -> bool:
    """main's rule as of 599f482: does the diff ADD a file under custom_components/?"""
    out = git("diff", "--diff-filter=A", "--name-only", base, sha,
              "--", "custom_components/**")
    return bool([l for l in out.splitlines() if l.strip()])


def _new_rule_source() -> str:
    """The three functions this branch adds, lifted out of tests/closure.py.

    The replay must not copy the whole file into the historical tree: INERT,
    GATE_FILES, NOT_A_TEST and the rest are the tables OF THE DAY, and
    overwriting them with today's answers the wrong question. So only the new
    rule travels; every table it consults is the one that shipped at that base.
    """
    src = (ROOT / "tests" / "closure.py").read_text()
    start = src.index("def affected(files: list[str]) -> dict:")
    end = src.index("def main() -> int:")
    return src[start:end]


NEW_RULE = None


def affected_at(base: str, files: list[str], tmp: Path, at_head: bool = False) -> dict:
    """Run the NEW rule against the tables as they were at `base` (or at HEAD)."""
    global NEW_RULE
    if NEW_RULE is None:
        NEW_RULE = _new_rule_source()
    import importlib.util

    if at_head:
        path = ROOT / "tests" / "closure.py"
        tag = "head"
    else:
        wt = tmp / f"wt-{base[:8]}"
        if not wt.exists():
            git("worktree", "add", "--detach", str(wt), base)
        path = wt / "tests" / "closure.py"
        tag = base[:8]
    spec = importlib.util.spec_from_file_location(f"closure_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not at_head:
        exec(NEW_RULE, mod.__dict__)
    return mod.affected(files)


# ---------------------------------------------------------------------------
# the job's own shell, executed against stubs


STUB = """#!/usr/bin/env bash
echo "$(basename "$0") $*" >> "$STUB_LOG"
"""


def dry_run_steps() -> None:
    """Execute the closures job's two shell steps with the tools stubbed."""
    record = job_step("closures", "Re-record the closures")
    checker = job_step("closures", "Fail if tests/closures.json under-approximates")
    for case, scripts in (("scoped", "tests/open_meteo.py\ntests/frontend.py"),
                          ("full", ""),
                          ("", "")):
        with tempfile.TemporaryDirectory() as td:
            sand = Path(td) / "sandbox"
            (sand / "tests").mkdir(parents=True)
            for name in ("derive_closures.sh",):
                p = sand / "tests" / name
                p.write_text(STUB)
                p.chmod(0o755)
            log = Path(td) / "log"
            log.write_text("")
            env = dict(os.environ,
                       STUB_LOG=str(log),
                       RUNNER_TEMP=str(Path(td) / "runner"),
                       SCOPE_CASE=case, SCOPE_SCRIPTS=scripts,
                       PATH=f"{Path(td)}/bin:{os.environ['PATH']}")
            (Path(td) / "bin").mkdir()
            py = Path(td) / "bin" / "python"
            py.write_text(STUB)
            py.chmod(0o755)
            (Path(td) / "runner").mkdir()
            for body in (record, checker):
                r = subprocess.run(["bash", "-e", "-c", body], cwd=sand,
                                   env=env, capture_output=True, text=True)
                if r.returncode != 0:
                    print(f"  STEP FAILED (case={case!r}): {r.stderr.strip()}")
            shown = case or "(empty: closure-scope failed)"
            print(f"  case={shown}")
            for line in log.read_text().splitlines():
                print(f"      {line}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", action="store_true")
    a = ap.parse_args()

    ifs = job_ifs()
    print(f"workflow: {WORKFLOW.relative_to(ROOT)}")
    print(f"  closures.if = {ifs['closures'].strip()}")
    print()

    # The safety property the whole gate rests on, checked first: a push to
    # main runs the closures job even though closure-scope is skipped there
    # and contributes no outputs.
    # On a push and on the nightly, closure-scope does not run at all: its
    # `if:` is pull_request-only, so it is SKIPPED and contributes no outputs.
    skipped = {"closure-scope": "skipped"}
    push = fires(ifs["closures"], Ctx("push", {}, skipped))
    sched = fires(ifs["closures"], Ctx("schedule", {}, skipped))
    broke = fires(ifs["closures"],
                  Ctx("pull_request", {}, {"closure-scope": "failure"}))
    print(f"RESULT push_to_main_runs_closures={push}")
    print(f"RESULT nightly_runs_closures={sched}")
    print(f"RESULT closure_scope_failed_runs_closures={broke}")
    print()

    rows = []
    with tempfile.TemporaryDirectory(prefix="hpo-replay-") as td:
        tmp = Path(td)
        for label, sha, note in INCIDENTS:
            base, files = diff_of(sha)
            plan = affected_at(base, files, tmp)
            head = affected_at(base, files, tmp, at_head=True)
            ok = {"closure-scope": "success"}
            needs = {"closure-scope": {"case": plan["case"],
                                       "scripts": "\n".join(plan["rederive"])}}
            new_runs = fires(ifs["closures"], Ctx("pull_request", needs, ok))
            old_needs = {"new-integration-file":
                         {"added": "1" if today_rule(base, sha) else "0"}}
            old_if = ("always() && ( github.event_name == 'push' || "
                      "github.event_name == 'schedule' || "
                      "needs.new-integration-file.outputs.added != '0' )")
            old_runs = fires(old_if, Ctx("pull_request", old_needs,
                                         {"new-integration-file": "success"}))
            rows.append((label, sha, len(files), old_runs, new_runs,
                         plan["case"], len(plan["rederive"]), plan["reason"],
                         note, head["case"], head["reason"]))
        for wt in tmp.glob("wt-*"):
            git("worktree", "remove", "--force", str(wt))

    print(f"{'incident':16s} {'merge':9s} {'files':>5s} "
          f"{'today':6s} {'new':6s} {'case':7s} {'rederive':>8s}  {'case@head':9s}")
    print("-" * 84)
    for (label, sha, n, old, new, case, k, reason, note,
         hcase, hreason) in rows:
        print(f"{label:16s} {sha:9s} {n:5d} "
              f"{'RUN' if old else 'SKIP':6s} {'RUN' if new else 'SKIP':6s} "
              f"{case:7s} {k:8d}  {hcase:9s}")
    print()
    print("  case      = the new rule against the tables committed AT THAT BASE")
    print("  case@head = the same diff against today's tables, for contrast only")
    print()
    for (label, sha, n, old, new, case, k, reason, note,
         hcase, hreason) in rows:
        print(f"{label}: {note}")
        print(f"    {case}: {reason}")
        if hcase != case:
            print(f"    @head it would be {hcase}: {hreason}")
    print()
    print(f"RESULT incidents={len(rows)}")
    print(f"RESULT run_today={sum(1 for r in rows if r[3])}")
    print(f"RESULT run_with_change={sum(1 for r in rows if r[4])}")
    print(f"RESULT missed_today={sum(1 for r in rows if not r[3])}")
    print(f"RESULT missed_with_change={sum(1 for r in rows if not r[4])}")

    if a.steps:
        print()
        print("the closures job's own shell, run against stubs:")
        dry_run_steps()

    # This is a check, not a report. The three properties below are the ones
    # #354 is about; a workflow edit that breaks any of them fails here.
    bad = []
    if not push:
        bad.append("a push to main no longer runs the closures job -- "
                   "always() has gone, or the push term has")
    if not broke:
        bad.append("a failed closure-scope no longer runs the closures job: "
                   "an empty case must fail closed")
    for r in rows:
        if not r[4]:
            bad.append(f"{r[0]} would still be merged unchecked ({r[5]})")
    if bad:
        print()
        for b in bad:
            print(f"FAIL: {b}")
        return 1
    print("OK: every incident is checked before merge, and main still is too")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
