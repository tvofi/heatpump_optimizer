#!/usr/bin/env python3
"""The fast lane's shards (R11-CI-CASE-SELECT P2, #3885): how many, and which script runs where.

    python3 -I tools/ci/shards.py plan [--ref REF] [--changed FILE]   print fast_shards= and fast_plan=
    python3 -I tools/ci/shards.py route --shard K/N                   the plan in $HPO_FAST_PLAN, checked, one
                                                                      `script<TAB>shard` line each
    python3 -I tools/ci/shards.py --self-test

The prelude calls `outputs()`. Every script `tests/run.sh` names on a `run` or `run_always`
line is assigned to exactly one shard, so the assignment is a function over the suite: a script
runs in its shard, and run.sh skips it by name in every other one. A script the plan does not name
runs in shard 1. Each shard intersects its scripts with run.sh's own GATE_SCOPE plan, so the
union of what the shards run is exactly what one unsharded run would run, whatever the estimate
below got wrong.

Seconds: `tests/closures.json`'s `recorded` table at REF, the span sums of
`tests/case_closures.json` for the scripts it splits, both committed and so pinned: a re-run of
the same event reads the same files and draws the same plan. A recording with a nonzero `rc`,
a non-positive or non-finite figure, or one the table's own comment discloses as a stub (the two
differential guards, #934) is no timing; such a script, and any script without one, is priced at
the upper quartile of the timings that remain. Bad timings only unbalance the shards.

Count: ceil(estimated seconds / TARGET_S), clamped to [MIN_SHARDS, MAX_SHARDS]. The estimate is
over the scripts the diff selects (closure.select over the prelude's changed list) plus the
`run_always` lines, else over every script. Packing: closure.lane_plan, longest group first into
the least-loaded shard, each PRODUCERS group (a payload's writer and its readers) kept together.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN_SH = ROOT / "tests" / "run.sh"
TARGET_S = 12 * 60      # seconds of recorded script work one shard is sized for
MIN_SHARDS, MAX_SHARDS = 2, 4   # the account's concurrent-job cap prices every extra runner
# closure.CLOSURES_COMMENT names these as timed by a stub invocation, not a real run (#934).
STUB_TIMED = ("tests/golden.py", "tests/env_drift.py")
# Named by run.sh but skipped by name in CI's fast job: the architecture pair (RUN_PART=fast; the
# arch-instrument job runs it), rolling.py (SLOW=1 only) and golden.py (GOLDEN_MODE=drift). They
# are assigned like every script and weigh nothing; were this list wrong, only the balance moves.
FAST_SKIPS = ("tests/arch_score.py", "tests/arch_score_head.py", "tests/rolling.py", "tests/golden.py")
_RUN_LINE = re.compile(r'^\s*(run|run_always)\s.*?\b(tests/[\w.-]+\.(?:py|mjs))\b')
_SHARD = re.compile(r"^([1-9][0-9]*)/([1-9][0-9]*)$")
# The fast lane's job: one `fast (3.14)` unsharded, else one `fast (3.14, K/N)` per shard, each
# with the caller's `tests / ` prefix when a run's job listing names it. Every reader of the job
# name reads it through FAST, is_fast or owed_fast; READERS is the census of the files that name it.
FAST = "fast (3.14)"
_FAST_JOB = re.compile(r"^(tests / )?fast \(3\.14(?:, ([1-9][0-9]*)/([1-9][0-9]*))?\)$")


def is_fast(name: str) -> bool:
    """Whether a job name is the fast lane's: unsharded or one shard, with or without `tests / `."""
    return bool(_FAST_JOB.match(name or ""))


def owed_fast(listed, prefix: str = "tests / ") -> list[str]:
    """The fast job names a run owes, from the names its listing holds: every `K/N` of the one N
    its shards name, else the unsharded name. Fail closed: shards of two different counts owe the
    unsharded name, which such a run never lists, so it is never read as finished."""
    counts = set()
    for x in listed:
        m = _FAST_JOB.match(x or "")
        if m and m.group(3) and (m.group(1) or "") == prefix:
            counts.add(int(m.group(3)))
    if len(counts) != 1:
        return [prefix + FAST]
    n = counts.pop()
    return [f"{prefix}fast (3.14, {k}/{n})" for k in range(1, n + 1)]


# Every file under tools/, tests/ and .github/ whose text names the fast job (`fast (3.14`), and
# why sharding leaves it correct. The self-test greps the tree and refuses a file missing here or
# listed here and no longer naming it: a new reader is routed before it merges (#3902 review).
#   sharded  reads job names through is_fast/owed_fast/FAST, or emits the shard names itself
#   ruleset  reads the required set from the ruleset, which requires `gate` alone; its own lines
#            naming the job are self-test fixtures
#   generic  reads every job name alike (prefix, matrix pattern or listing), so a shard is a job
#   label    names the lane in text it prints; it never matches a job listing
#   fixture  self-test data or recorded API shapes only
#   prose    comments or documentation
READERS = {
    ".github/workflows/ci.yml": "sharded",
    ".github/workflows/tests.yml": "sharded",
    "tests/README.md": "prose",
    "tests/ci_ratchet.py": "generic",
    "tests/doc_claims.py": "fixture",
    "tests/entities.py": "fixture",
    "tests/features.py": "prose",
    "tests/host_probe.py": "prose",
    "tests/run.sh": "prose",
    "tests/stress.py": "prose",
    "tools/audit/seat/ancestry_calls.sh": "fixture",
    "tools/audit/seat/body_patch.sh": "fixture",
    "tools/audit/seat/ci-watch.sh": "ruleset",
    "tools/audit/seat/ci_critpath.py": "generic",
    "tools/audit/seat/cloud_relay.sh": "fixture",
    "tools/audit/seat/fixtures/ci_critpath/jobs_39619839750.json": "fixture",
    "tools/audit/seat/fixtures/ci_critpath/jobs_39625218966.json": "fixture",
    "tools/audit/seat/fixtures/ci_rerun/pr3836/jobs-44944866503.json": "fixture",
    "tools/audit/seat/instruments/cloud-setup.sh.md": "prose",
    "tools/audit/seat/instruments/probe_bridge.py.md": "prose",
    "tools/audit/seat/merge_train.py": "ruleset",
    "tools/audit/seat/orchestrator_tick.py": "ruleset",
    "tools/audit/seat/probe_bridge.py": "sharded",
    "tools/audit/seat/record_row.py": "ruleset",
    "tools/ci/fixtures/gate_busy_defer_runs.json": "fixture",
    "tools/ci/fixtures/gate_requeued_needs_runs.json": "fixture",
    "tools/ci/fixtures/ruleset/ruleset_23698884.json": "fixture",
    "tools/ci/gate.py": "sharded",
    "tools/ci/prelude.py": "sharded",
    "tools/ci/ruleset_cutover.py": "fixture",
    "tools/ci/shards.py": "sharded",
    "tools/ci/sweep.py": "sharded",
    "tools/ci/sweep_selftest.py": "fixture",
    "tools/plan/durations.json": "fixture",
    "tools/plan/replan.py": "sharded",
    "tools/policy/fixtures/policy-rot/prepr/red-answered.md": "fixture",
    "tools/policy/fixtures/red-ancestry/green/d01ba036aa210b8c6f2660c8e2985f65c764a779.json": "fixture",
    "tools/policy/fixtures/red-ancestry/red/12f5d8775e1ebff95b15e4f8ac34a3df86c984fb.json": "fixture",
    "tools/policy/fixtures/red-ancestry/red/d01ba036aa210b8c6f2660c8e2985f65c764a779.json": "fixture",
    "tools/policy/fixtures/required-contexts.json": "fixture",
    "tools/policy/policy_lint.mjs": "generic",
    "tools/pr/ci_predict.py": "label",
    "tools/pr/merge_main_bot.py": "fixture",
    "tools/pr/prepr.sh": "fixture",
    "tools/release/stamp.py": "fixture",
}


def census() -> tuple[list[str], list[str]]:
    """(files naming the fast job that READERS does not route, READERS files that no longer name it)."""
    p = subprocess.run(["git", "grep", "-l", "-F", "fast (3.14", "--", "tools", "tests", ".github"],
                       cwd=ROOT, capture_output=True, text=True)
    if p.returncode not in (0, 1):
        return [f"git grep failed: {p.stderr.strip()[:120]}"], []
    found = set(p.stdout.split())
    return sorted(found - set(READERS)), sorted(set(READERS) - found)


def _closure():
    sys.path.insert(0, str(ROOT / "tests"))
    import closure  # noqa: PLC0415  (tests/closure.py: lane_plan, select, the edges)
    return closure


def suite_scripts(text: str) -> tuple[list[str], set[str]]:
    """(every script a run/run_always line of run.sh names, in file order; those run_always names)."""
    seen: dict[str, None] = {}
    always: set[str] = set()
    for line in text.splitlines():
        m = _RUN_LINE.match(line)
        if m:
            seen.setdefault(m.group(2))
            if m.group(1) == "run_always":
                always.add(m.group(2))
    return list(seen), always


def _show(ref: str, rel: str) -> dict | None:
    p = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except ValueError:
        return None


def timings(closures: dict | None, cases: dict | None) -> dict[str, float]:
    """Seconds per script from the two committed tables; only figures that can be a timing."""
    out: dict[str, float] = {}
    for script, rec in ((closures or {}).get("recorded") or {}).items():
        if not isinstance(rec, dict) or rec.get("rc", 0) != 0 or script in STUB_TIMED:
            continue
        s = rec.get("seconds")
        if isinstance(s, (int, float)) and not isinstance(s, bool) and math.isfinite(s) and s > 0:
            out[script] = float(s)
    for script, entry in ((cases or {}).get("scripts") or {}).items():
        spans = (entry or {}).get("spans") or {}
        secs = [v.get("seconds") for v in spans.values() if isinstance(v, dict)]
        if secs and all(isinstance(s, (int, float)) and not isinstance(s, bool) and math.isfinite(s)
                        and s >= 0 for s in secs) and sum(secs) > 0:
            out[script] = float(sum(secs))
    return out


def priced(scripts: list[str], known: dict[str, float]) -> dict[str, float]:
    """Every script's seconds: its timing, else the upper quartile of the timings (never below the median)."""
    vals = sorted(known.values())
    default = vals[min(len(vals) - 1, (3 * len(vals)) // 4)] if vals else float(TARGET_S)
    return {s: known.get(s, default) for s in scripts}


def shard_count(seconds: float) -> int:
    return max(MIN_SHARDS, min(MAX_SHARDS, math.ceil(seconds / TARGET_S)))


def plan(scripts: list[str], always: set[str], seconds: dict[str, float],
         selected: list[str] | None) -> dict:
    """{"n": N, "s": {script: shard}}: every script assigned, packed by the selected load."""
    closure = _closure()
    load = [s for s in scripts if s not in FAST_SKIPS
            and (selected is None or s in set(selected) | always)]
    n = shard_count(sum(seconds[s] for s in load))
    # The selected scripts are packed by their seconds; the rest ride at zero, so they still
    # get a shard (run.sh's own scope may select them) without moving the balance.
    weight = {s: {"seconds": seconds[s] if s in load else 0.0} for s in scripts}
    # lane_plan moves each closure.lane_edges group (a payload's writer and its readers) whole,
    # and returns no empty lane, so n is the count of shards that hold a script.
    lanes = closure.lane_plan(scripts, weight, n)
    return {"n": len(lanes), "s": {s: i for i, ln in enumerate(lanes, 1) for s in ln}}


def outputs(changed: list[str] | None, ref: str) -> dict[str, str]:
    """The prelude's two outputs; empty strings (one unsharded `fast (3.14)` job) on any failure."""
    try:
        scripts, always = suite_scripts(RUN_SH.read_text())
        known = timings(_show(ref, "tests/closures.json"), _show(ref, "tests/case_closures.json"))
        selected = None
        if changed:
            got = _closure().select(changed)
            if got.get("mode") == "scoped":
                selected = list(got["run"])
        p = plan(scripts, always, priced(scripts, known), selected)
        if not check(p):
            return {"fast_shards": "", "fast_plan": ""}
        return {"fast_shards": json.dumps([f"{k}/{p['n']}" for k in range(1, p["n"] + 1)],
                                          separators=(",", ":")),
                "fast_plan": json.dumps(p, separators=(",", ":"), sort_keys=True)}
    except Exception as e:  # noqa: BLE001 -- the fallback is the unsharded job, never a dropped test
        print(f"shards: no plan ({type(e).__name__}: {e}); fast runs unsharded", file=sys.stderr)
        return {"fast_shards": "", "fast_plan": ""}


def check(p) -> bool:
    """A plan is {"n": N >= 1, "s": {tests/<script>: k in 1..N}} and every shard holds a script."""
    if not isinstance(p, dict) or set(p) != {"n", "s"}:
        return False
    n, s = p["n"], p["s"]
    if not isinstance(n, int) or isinstance(n, bool) or n < 1 or not isinstance(s, dict):
        return False
    if not all(isinstance(k, str) and k.startswith("tests/") and isinstance(v, int)
               and not isinstance(v, bool) and 1 <= v <= n for k, v in s.items()):
        return False
    return set(s.values()) == set(range(1, n + 1))


def route(plan_text: str, shard: str) -> tuple[list[str], str]:
    """(`script<TAB>k` lines, '' or why the plan or shard is refused). Fail closed: a refusal is red."""
    m = _SHARD.match(shard or "")
    if not m:
        return [], f"shard {shard!r} is not K/N"
    k, n = int(m.group(1)), int(m.group(2))
    try:
        p = json.loads(plan_text or "")
    except ValueError:
        return [], "the plan is not JSON"
    if not check(p):
        return [], "the plan is not a partition of its scripts over 1..n"
    if p["n"] != n or not 1 <= k <= n:
        return [], f"shard {shard} does not belong to a plan of {p['n']} shard(s)"
    return [f"{s}\t{v}" for s, v in sorted(p["s"].items())], ""


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if argv[:1] == ["route"] and len(argv) == 3 and argv[1] == "--shard":
        import os  # noqa: PLC0415
        lines, why = route(os.environ.get("HPO_FAST_PLAN", ""), argv[2])
        if why:
            print(f"shards: REFUSE {why}", file=sys.stderr)
            return 2
        print("\n".join(lines))
        return 0
    if argv[:1] == ["plan"]:
        ref, changed = "HEAD", None
        rest = argv[1:]
        while rest:
            if rest[0] == "--ref" and len(rest) > 1:
                ref, rest = rest[1], rest[2:]
            elif rest[0] == "--changed" and len(rest) > 1:
                changed, rest = Path(rest[1]).read_text().split(), rest[2:]
            else:
                break
        if not rest:
            for k, v in outputs(changed, ref).items():
                print(f"{k}={v}")
            return 0
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


def run_sh_routes(p: dict, shard: str, scripts: list[str]) -> tuple[int, list[str]]:
    """(exit status, the scripts that ran) when tests/run.sh's own shard_setup, shard_of, run_always
    and skip, sourced from the file, route `scripts` under plan `p` as shard `shard` ('' unsharded).
    Each script is a `true` stand-in; the lease is stubbed to run the command."""
    import os  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    fns = "".join(re.findall(r"(?ms)^(?:shard_setup|shard_of|scope_script|run_always|skip)\(\) \{.*?^\}\n",
                             RUN_SH.read_text()))
    with tempfile.TemporaryDirectory() as td:
        drive = Path(td) / "drive.sh"
        drive.write_text("PYTHON=%s; WORKDIR=%s; JOBS=1; LANE=x; step=0; WAIT_UNRUN=; SHARD_TABLE=\n"
                         'FAST_SHARD="$1"; shift\nleased() { "$@"; }\n%s\nshard_setup || exit 1\n'
                         'for s in "$@"; do run_always true "$s"; done\n' % (sys.executable, td, fns))
        env = {**os.environ, "HPO_FAST_PLAN": json.dumps(p)}
        r = subprocess.run(["bash", str(drive), shard, *scripts], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=60)
        man = Path(td) / "x.manifest"
        rows = man.read_text().splitlines() if man.is_file() else []
    ran = [row.split("\t")[3].split()[-1] for row in rows if not row.split("\t")[3].startswith("#skip")]
    return r.returncode, ran


def self_test() -> int:
    fails, n = 0, 0

    def ck(name, got, want):
        nonlocal fails, n
        n += 1
        ok = got == want
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": got {got!r}, want {want!r}"))

    text = ('  run_always "$PYTHON" tests/env_drift.py --claims-only "$GOLDEN_REF"\n'
            '  run "$PYTHON" tests/features.py\n  # run "$PYTHON" tests/commented.py\n'
            '    run node tests/card.mjs\n  run "$PYTHON" tests/env_drift.py --all "$GOLDEN_REF"\n'
            '  run_always "$@"\n  run "$PYTHON" tests/plan_view.py\n')
    ck("run.sh's run lines, a comment and `$@` named by none",
       suite_scripts(text), (["tests/env_drift.py", "tests/features.py", "tests/card.mjs",
                              "tests/plan_view.py"], {"tests/env_drift.py"}))
    real, real_always = suite_scripts(RUN_SH.read_text())
    ck("the tree's run.sh names features.py, stress.py and the setup render",
       all(s in real for s in ("tests/features.py", "tests/stress.py", "tests/setup_qa_render.mjs")), True)
    ck("the tree's run_always lines include harness_headers.py", "tests/harness_headers.py" in real_always, True)
    cl = {"recorded": {"tests/a.py": {"seconds": 100.0, "rc": 0}, "tests/b.py": {"seconds": 5.0, "rc": 1},
                       "tests/env_drift.py": {"seconds": 1.0, "rc": 0}, "tests/c.py": {"seconds": float("nan")},
                       "tests/d.py": {"seconds": 0}, "tests/e.py": {"seconds": 40.0}}}
    cs = {"scripts": {"tests/f.py": {"spans": {"x": {"seconds": 30.0}, "y": {"seconds": 20.0}}}}}
    ck("timings drop a failed run, a stub, a NaN and a zero; span sums stand for their script",
       timings(cl, cs), {"tests/a.py": 100.0, "tests/e.py": 40.0, "tests/f.py": 50.0})
    ck("an untimed script is priced at the upper quartile, never dropped",
       priced(["tests/a.py", "tests/new.py"], {"tests/a.py": 10.0, "x": 20.0, "y": 30.0, "z": 40.0}),
       {"tests/a.py": 10.0, "tests/new.py": 40.0})
    ck("count: clamped below", shard_count(60.0), MIN_SHARDS)
    ck("count: ceil(seconds / target)", shard_count(2.5 * TARGET_S), 3)
    ck("count: clamped above", shard_count(40.0 * TARGET_S), MAX_SHARDS)
    scripts = ["tests/features.py", "tests/entities.py", "tests/stress.py", "tests/plan_view.py",
               "tests/card.mjs", "tests/card_drift.mjs", "tests/setup_qa_render.mjs", "tests/x.py"]
    sec = {"tests/features.py": 1600.0, "tests/entities.py": 1300.0, "tests/stress.py": 900.0,
           "tests/plan_view.py": 2.0, "tests/card.mjs": 160.0, "tests/card_drift.mjs": 6.0,
           "tests/setup_qa_render.mjs": 1500.0, "tests/x.py": 30.0}
    p = plan(scripts, set(), sec, None)
    ck("a full plan is a partition of every script", (check(p), sorted(p["s"])), (True, sorted(scripts)))
    ck("a full plan's count is the estimate's", p["n"], shard_count(sum(sec.values())))
    ck("the two longest scripts land in different shards",
       p["s"]["tests/features.py"] != p["s"]["tests/entities.py"], True)
    ck("every payload reader shares the writer's shard",
       {p["s"][c] for c in ("tests/card.mjs", "tests/card_drift.mjs", "tests/setup_qa_render.mjs")},
       {p["s"]["tests/plan_view.py"]})
    q = plan(scripts, {"tests/x.py"}, sec, ["tests/card.mjs"])
    ck("a scoped plan still assigns every script, sized by the selection",
       (check(q), sorted(q["s"]), q["n"]), (True, sorted(scripts), MIN_SHARDS))
    good = json.dumps(p)
    ck("route: the plan's lines for a shard of it",
       len(route(good, f"1/{p['n']}")[0]), len(scripts))
    for name, txt, sh in (("a shard of another count", good, f"1/{p['n'] + 1}"),
                          ("a shard past n", good, f"{p['n'] + 1}/{p['n']}"),
                          ("a malformed shard", good, "1"),
                          ("no plan", "", "1/2"),
                          ("a script mapped past n", json.dumps({"n": 2, "s": {"tests/a.py": 3, "tests/b.py": 1}}), "1/2"),
                          ("an empty shard", json.dumps({"n": 2, "s": {"tests/a.py": 1}}), "1/2"),
                          ("a non-test key", json.dumps({"n": 1, "s": {"x.py": 1}}), "1/1")):
        ck(f"route refuses {name}", bool(route(txt, sh)[1]), True)
    missing, stale = census()
    ck("#3902: every file naming the fast job is routed in READERS, and every READERS file names it",
       (missing, stale), ([], []))
    ck("#3902: is_fast reads the unsharded job, a shard and their caller-prefixed names, and nothing else",
       [is_fast(x) for x in ("fast (3.14)", "tests / fast (3.14, 2/3)", "fast (3.14, 0/3)",
                             "fast (3.13)", "tests / fast (3.14, 1/2) x", "fast-lane")],
       [True, True, False, False, False, False])
    ck("#3902: owed_fast owes every shard of the one listed count, else the unsharded name",
       [owed_fast(["tests / fast (3.14, 2/3)", "gate"]), owed_fast(["gate"]),
        owed_fast(["tests / fast (3.14, 1/2)", "tests / fast (3.14, 1/3)"])],
       [[f"tests / fast (3.14, {k}/3)" for k in (1, 2, 3)], ["tests / fast (3.14)"], ["tests / fast (3.14)"]])
    four = ["tests/a.py", "tests/b.py", "tests/c.py", "tests/d.mjs"]
    two = {"n": 2, "s": {"tests/a.py": 1, "tests/b.py": 2, "tests/c.py": 1}}    # d: unnamed, so shard 1
    ran = {k: run_sh_routes(two, f"{k}/2", four) for k in (1, 2)}
    ck("#3902: run.sh's routing over a 2-shard plan runs every script once across the shards, an unnamed "
       "one in shard 1", (ran[1], ran[2]), ((0, ["tests/a.py", "tests/c.py", "tests/d.mjs"]), (0, ["tests/b.py"])))
    three = {"n": 3, "s": {"tests/a.py": 3, "tests/b.py": 1, "tests/c.py": 2, "tests/d.mjs": 3}}
    got3 = [run_sh_routes(three, f"{k}/3", four) for k in (1, 2, 3)]
    ck("#3902: ... and over a 3-shard plan, each shard exactly its own",
       got3, [(0, ["tests/b.py"]), (0, ["tests/c.py"]), (0, ["tests/a.py", "tests/d.mjs"])])
    ck("#3902: run.sh with no shard runs every script (the unsharded job; null control)",
       run_sh_routes(two, "", four), (0, four))
    ck("#3902: run.sh refuses a shard its plan does not hold, and runs nothing",
       run_sh_routes(two, "3/2", four), (1, []))
    print(f"shards self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
