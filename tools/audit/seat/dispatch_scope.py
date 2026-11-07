#!/usr/bin/env python3
"""Refuse a workflow dispatch that runs more jobs than the caller wants.

    python3 -I tools/audit/seat/dispatch_scope.py --check
    python3 -I tools/audit/seat/dispatch_scope.py --self-test

WHY. `workflow_dispatch` is a whole-workflow trigger. The stamp's record flush
POSTed `nightly.yml/dispatches` to run the one-minute `record-autofix` job, and
every other job of that file whose `if:` admits a dispatch ran with it:
mutation-nightly, four mutation-ledger shards, slow and two nightly-ha lanes,
about 950 runner-minutes a dispatch (dev/audit/rca/r10-rca-flush-dispatch.md).
The cost was written in a code comment and no check read it.

THE RULE. Every dispatch call site under tools/ and .github/ (a
`workflows/<file>/dispatches` URL or a `gh workflow run <file>`; comment lines
are not call sites) is registered in WANTS with the jobs it wants, `"*"` for
the whole workflow by design, and the `inputs` it sends. The target's jobs are
then evaluated under `github.event_name == 'workflow_dispatch'` on main: a job
runs when its `if:` is absent or true, an unresolvable term (`needs` of a job
that runs, anything not modelled) counting as true, so the evaluation
over-approximates and never hides a lane. A call site is refused when

  * it is not registered (a new dispatch must say what it runs);
  * the target runs a job the entry did not want;
  * a wanted job does not run on a dispatch (the dispatch does nothing);
  * a registered entry matches no call site (a stale entry pins nothing);
  * a declared input is not a string literal in the call site's file.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]

#: (call-site file, target workflow) -> jobs wanted ("*": the whole workflow, by
#: design) and the inputs the call site sends, which the target's `if:`s read.
WANTS: dict[tuple[str, str], dict] = {
    ("tools/release/stamp.py", "nightly.yml"): {
        "jobs": ["record-autofix"], "inputs": {},
        "why": "the record flush wants the record beat, not the nightly lanes"},
    (".github/workflows/tests.yml", "ci.yml"): {
        "jobs": "*", "inputs": {}, "why": "re-dispatching the umbrella for a pull request"},
    (".github/workflows/merge-main.yml", "ci.yml"): {
        "jobs": "*", "inputs": {}, "why": "re-dispatching the umbrella for a pull request"},
    ("tools/audit/seat/ci_probe.py", "<dynamic>"): {
        "jobs": "*", "inputs": {}, "why": "a probe; its target is a parameter"},
    ("tools/audit/seat/ci_probe.py", "tests.yml"): {
        "jobs": "*", "inputs": {}, "why": "the probe's self-test names a workflow it never runs"},
}

URL = re.compile(r"workflows/([\w.${}-]+?\.ya?ml|\{\w+\})/dispatches")
GHRUN = re.compile(r"gh workflow run\s+([\w.-]+\.ya?ml)")
CONST = re.compile(r"^(\w+)\s*=\s*[\"']([\w.-]+\.ya?ml)[\"']", re.M)


class _U:
    """An unresolvable term: it compares true to anything and is truthy."""
    def __eq__(self, o): return True
    def __ne__(self, o): return True
    def __bool__(self): return True
    __hash__ = None


def _evaluate(expr, event: str, ref: str, ran: dict, inputs: dict) -> bool:
    text = str(expr).strip()
    text = re.sub(r"^\$\{\{\s*(.*?)\s*\}\}$", r"\1", text, flags=re.S)
    text = text.replace("&&", " and ").replace("||", " or ")
    text = re.sub(r"!\s*(cancelled|failure)\(\)", "U", text)  # a status check is no filter
    text = re.sub(r"!(?!=)", " not ", text)
    text = re.sub(r"\b(always|success|cancelled|failure)\(\)", "U", text)
    text = re.sub(r"needs\.([\w-]+)\.result",
                  lambda m: repr("success" if ran.get(m[1], True) else "skipped"), text)
    text = re.sub(r"(?:github\.event\.inputs|inputs)\.([\w-]+)",
                  lambda m: repr(inputs[m[1]]) if m[1] in inputs else "U", text)
    text = text.replace("github.event_name", repr(event)).replace("github.ref", repr(ref))
    text = re.sub(r"\b(contains|startsWith|endsWith)\(([^()]*)\)",
                  lambda m: f"{m[1]}({m[2]})", text)
    env = {"U": _U(), "contains": lambda a, b: a is not None and (b in a if isinstance(a, str) else True),
           "startsWith": lambda a, b: isinstance(a, str) and a.startswith(b) or isinstance(a, _U),
           "endsWith": lambda a, b: isinstance(a, str) and a.endswith(b) or isinstance(a, _U)}
    try:
        return bool(eval(text, {"__builtins__": {}}, env))  # noqa: S307 -- own workflow files
    except Exception:  # an expression this model cannot read over-approximates
        return True


def dispatch_jobs(workflow: dict, inputs: dict | None = None) -> list[str]:
    """The jobs of a parsed workflow that run on a main dispatch."""
    jobs = workflow.get("jobs") or {}
    ran: dict[str, bool] = {}
    pending = dict(jobs)
    while pending:
        progressed = False
        for name, job in list(pending.items()):
            needs = job.get("needs") or []
            needs = [needs] if isinstance(needs, str) else needs
            if any(n in pending for n in needs):
                continue
            cond = job.get("if")
            ran[name] = True if cond is None else _evaluate(
                cond, "workflow_dispatch", "refs/heads/main", ran, inputs or {})
            del pending[name]
            progressed = True
        if not progressed:  # a needs cycle: the file is invalid, count every job
            for name in pending:
                ran[name] = True
            break
    return [n for n in jobs if ran.get(n)]


def call_sites(root: Path) -> list[tuple[str, str, str]]:
    """(file, target workflow, source text) of each dispatch call site."""
    found = []
    files = [p for d in ("tools", ".github") for p in sorted((root / d).rglob("*"))
             if p.is_file() and p.suffix in (".py", ".sh", ".yml", ".yaml")]
    for path in files:
        rel = path.relative_to(root).as_posix()
        if rel == "tools/audit/seat/dispatch_scope.py":
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        consts = dict(CONST.findall(text))
        code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
        for m in URL.finditer(code):
            target = m[1]
            if target.startswith("{") and target.endswith("}"):
                target = consts.get(target[1:-1], "<dynamic>")
            found.append((rel, target, text))
        for m in GHRUN.finditer(code):
            found.append((rel, m[1], text))
    return found


def check(root: Path, wants: dict | None = None) -> list[str]:
    wants = WANTS if wants is None else wants
    problems, seen = [], set()
    for rel, target, text in call_sites(root):
        key = (rel, target)
        seen.add(key)
        entry = wants.get(key)
        if entry is None:
            problems.append(f"{rel}: dispatches {target} and is not registered in WANTS "
                            f"(say which jobs it wants)")
            continue
        for name in entry["inputs"]:
            if f'"{name}"' not in text and f"'{name}'" not in text and f"-f {name}=" not in text:
                problems.append(f"{rel}: declares input {name!r} for {target} but never sends it")
        wf = root / ".github/workflows" / target
        if target == "<dynamic>" or not wf.is_file():
            continue
        runs = dispatch_jobs(yaml.safe_load(wf.read_text()) or {}, entry["inputs"])
        if entry["jobs"] == "*":
            continue
        extra = [j for j in runs if j not in entry["jobs"]]
        missing = [j for j in entry["jobs"] if j not in runs]
        if extra:
            problems.append(f"{rel}: dispatching {target} wants {entry['jobs']} but also runs "
                            f"{extra}")
        if missing:
            problems.append(f"{rel}: dispatching {target} never runs wanted {missing}")
    for key in wants:
        if key not in seen:
            problems.append(f"WANTS entry {key} matches no call site (stale)")
    return problems


# --- self-test ---------------------------------------------------------------

_DEFECT = """on: {push: {}, workflow_dispatch: {}, schedule: [{cron: '1 0 * * *'}]}
jobs:
  slow: {if: "github.event_name != 'push'", runs-on: x}
  ledger: {if: "github.ref == 'refs/heads/main' && github.event_name != 'push'", runs-on: x}
  ledger-push:
    needs: [ledger]
    if: "!cancelled() && (github.event_name == 'schedule' || github.event_name == 'workflow_dispatch') && needs.ledger.result == 'success'"
    runs-on: x
  record-autofix:
    if: "!cancelled() && github.ref == 'refs/heads/main' && (github.event_name == 'push' || github.event_name == 'workflow_dispatch')"
    runs-on: x
"""
_FIX_SPLIT = _DEFECT.replace("github.event_name != 'push'\"", "github.event_name == 'schedule'\"")
_FIX_INPUT = _DEFECT.replace(
    "github.event_name != 'push'\"",
    "github.event_name != 'push' && (github.event_name != 'workflow_dispatch' || inputs.lanes == 'all')\"")
_CALLER = 'import json\nURL = "x/actions/workflows/{NIGHTLY}/dispatches"\nNIGHTLY = "nightly.yml"\n{extra}\n'


def _tree(workflow: str, caller_extra: str = "") -> Path:
    root = Path(tempfile.mkdtemp(prefix="dispatch_scope_"))
    (root / ".github/workflows").mkdir(parents=True)
    (root / "tools/release").mkdir(parents=True)
    (root / ".github/workflows/nightly.yml").write_text(workflow)
    (root / "tools/release/stamp.py").write_text(_CALLER.replace("{extra}", caller_extra))
    return root


def self_test() -> int:
    stamp = ("tools/release/stamp.py", "nightly.yml")
    want = {stamp: {"jobs": ["record-autofix"], "inputs": {}, "why": "t"}}
    want_in = {stamp: {"jobs": ["record-autofix"], "inputs": {"lanes": "none"}, "why": "t"}}
    cases = [
        ("defect: a dispatch also runs slow and the ledger lanes (red)",
         check(_tree(_DEFECT), want), True),
        ("the split fix: dispatch runs record-autofix only (green)",
         check(_tree(_FIX_SPLIT), want), False),
        ("the input fix, input declared and sent (green)",
         check(_tree(_FIX_INPUT, 'PAYLOAD = {"inputs": {"lanes": "none"}}'), want_in), False),
        ("the input fix, input declared but never sent (red)",
         check(_tree(_FIX_INPUT), want_in), True),
        ("the input fix registered without its input still runs the lanes (red)",
         check(_tree(_FIX_INPUT, 'PAYLOAD = {"inputs": {"lanes": "none"}}'), want), True),
        ("an unregistered dispatch call site (red)", check(_tree(_FIX_SPLIT), {}), True),
        ("a stale registry entry (red)",
         check(_tree(_FIX_SPLIT, ""), {**want, ("tools/x.py", "y.yml"):
                                       {"jobs": "*", "inputs": {}, "why": "t"}}), True),
        ("a wanted job that a dispatch never runs (red)",
         check(_tree(_FIX_SPLIT.replace("(github.event_name == 'push' || github.event_name == 'workflow_dispatch')",
                                        "github.event_name == 'push'")), want), True),
        ("a comment mentioning the dispatch is not a call site (green)",
         check(_tree(_FIX_SPLIT, "# gh workflow run other.yml --ref main"), want), False),
    ]
    failed = 0
    for name, problems, expect_red in cases:
        ok = bool(problems) == expect_red
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": {problems}"))
    print(f"dispatch_scope self-test: {len(cases)} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--check" in argv:
        problems = check(ROOT)
        for p in problems:
            print(f"REFUSE: {p}")
        print(f"dispatch_scope: {'REFUSED' if problems else 'OK'} "
              f"({len(call_sites(ROOT))} dispatch call site(s))")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
