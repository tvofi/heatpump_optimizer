"""Spike: every line the V3 enumerator prints, in exactly one class; refuses an unclassified line.

    git grep -n 'features\\.py' -- ':!dev/audit/rounds' ':!tests/mutation_ledger' ':!tests/features.py' \\
      | python3 refclass.py
"""
import re
import sys
from collections import Counter, defaultdict

# (class, disposition, rule) in order; the first rule a line matches is its class.
DATED = re.compile(
    r"^(dev/archive/|dev/audit/rca/|dev/audit/waves/|dev/audit/harnesses/r10_(hotfix_ci_critpath_4|mutant_skip|rca_ci_critpath_3)/"
    r"|dev/programme/(delivery|triage|register|round9|round10)/|dev/programme/plan-2026-09-open-issues\.md"
    r"|dev/programme/rosters/wave-r(9|10)-groups\.json|dev/governance/decisions/|docs/design/20\d\d-"
    r"|dev/audit/config/rotation\.json|tests/golden/card_claimed_drift\.txt|tools/policy/fixtures/)")
HARNESS_EXEC = {  # dev/audit/harnesses/*.py whose code opens, execs or runs the script (scout, at the base)
    "host_zone_features.py": "R-run", "r10_heat_meter_mutants.py": "H-dated",
    "r10_advisor_steady_bracket.py": "H-dated", "r10_advisor_steady_carrier.py": "H-dated",
    "r10_duty_switch_price_section.py": "H-dated", "r10_duty_switch_section.py": "H-dated",
    "r10_i1_action_guards.py": "H-dated", "r10_i1_sweep_guards.py": "H-dated",
    "r10_sav_baseline_mutants.py": "H-dated", "r10_store_races_census.py": "H-dated",
    "r11_honest_starts_runs.py": "H-dated", "ux10_flow_into_model.py": "H-dated", "ux9_flow_unit_guard.py": "H-dated",
    "boost_tail_mutants.py": "H-block", "learner_freeze_mutants.py": "H-block",
    "r10_arbiter_off_restore_mutants.py": "H-block", "start_counter_edges_mutants.py": "H-block",
}
RUN = {("tests/run.sh", 580), (".github/workflows/nightly.yml", 543), ("tests/README.md", 346),
       ("tools/audit/seat/verify_eight.py", 92), ("tools/audit/seat/features_block.py", 156),
       ("tools/audit/seat/features_block.py", 195), ("tools/pr/prepr.sh", 2848), ("tools/pr/prepr.sh", 2870),
       ("tools/ci/shards.py", 339), ("tools/ci/shards.py", 340)}
TABLE = {"tests/closures.json", "tests/case_closures.json", "tools/ci/selftest_closures.json"}
TABLE_LINES = {("tests/case_select.py", 55), ("tests/closure.py", 220), ("tools/ci/shards.py", 93),
               ("tests/entities.py", 22931), ("tests/entities.py", 23794)}
LIVE_TEXT = re.compile(r"^(custom_components/|docs/architecture\.md|tests/README\.md|dev/audit/README\.md"
                       r"|dev/governance/dimensions/|dev/programme/HANDOVER\.md|dev/programme/carries/"
                       r"|dev/programme/rosters/wave-r11-groups\.json|dev/audit/config/bugclasses\.json"
                       r"|\.github/workflows/|tools/audit/seat/INSTRUMENTS\.md|tools/audit/seat/instruments/"
                       r"|tools/coverage/)")
CODE = re.compile(r"^(tests/|tools/|dev/audit/harnesses/)")


_PROSE = {}


def _prose(path, num):
    """A comment or a docstring line (tokenize/ast); for a shell or JS file a #/'//' comment line."""
    if path not in _PROSE:
        lines = set()
        if path.endswith(".py"):
            import ast, io, tokenize
            src = open(path, encoding="utf-8").read()
            for t in tokenize.generate_tokens(io.StringIO(src).readline):
                if t.type == tokenize.COMMENT:
                    lines.add(t.start[0])
            for n in ast.walk(ast.parse(src)):
                body = getattr(n, "body", None)
                if isinstance(body, list) and body and isinstance(body[0], ast.Expr) \
                        and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
                    lines.update(range(body[0].lineno, body[0].end_lineno + 1))
        else:
            for i, t in enumerate(open(path, encoding="utf-8"), 1):
                if t.lstrip().startswith(("#", "//")):
                    lines.add(i)
        _PROSE[path] = lines
    return num in _PROSE[path]

counts, files, unclassified = Counter(), defaultdict(set), []
for ln in sys.stdin:
    path, num, text = ln.split(":", 2)
    num = int(num)
    base = path.rsplit("/", 1)[-1]
    if DATED.match(path):
        c = "D dated record: left, excluded from the enumerator"
    elif path.startswith("dev/audit/harnesses/") and HARNESS_EXEC.get(base) == "R-run":
        c = "R runner/opener: retargeted"
    elif path.startswith("dev/audit/harnesses/") and HARNESS_EXEC.get(base) == "H-block":
        c = "B runs through features_block.py: unchanged, works once features_block resolves the marker"
    elif path.startswith("dev/audit/harnesses/") and base in HARNESS_EXEC:
        c = "H closed-group harness reading the file: left, pinned to its group's SHA"
    elif path.startswith("dev/audit/harnesses/"):
        c = "P prose in a harness: left (comment, no read)"
    elif (path, num) in RUN:
        c = "R runner/opener: retargeted"
    elif path.startswith("tests/entities.py") and 4390 <= num <= 4480:
        c = "R runner/opener: retargeted"  # _P2_CENSUSES reads the named script's text
    elif path in TABLE or (path, num) in TABLE_LINES:
        c = "T table or census row: re-recorded / follows the parts"
    elif LIVE_TEXT.match(path):
        c = "L live citation: rewritten one-for-one to the owning part"
    elif CODE.match(path) and _prose(path, num):
        c = "L live citation: rewritten one-for-one to the owning part"
    elif CODE.match(path):
        c = "S data in code (a literal a self-test or message carries): left; the split head is its check"
    else:
        unclassified.append(ln.rstrip())
        continue
    counts[c] += 1
    files[c].add(path)
for c in sorted(counts):
    print(f"{counts[c]:5d} lines {len(files[c]):4d} files  {c}")
print(f"{sum(counts.values()):5d} lines {len({p for s in files.values() for p in s}):4d} files  total")
for u in unclassified:
    print("UNCLASSIFIED", u[:200])
sys.exit(1 if unclassified else 0)
