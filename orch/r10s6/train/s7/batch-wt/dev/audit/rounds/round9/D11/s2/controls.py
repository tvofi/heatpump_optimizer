"""D11-s2 harness: positive controls for the refusals CLAUDE.md and .claude/rules/ name.

Metric: of K refusals my cells (CLAUDE.md, AGENTS.md, .claude/rules/*.md,
  .cursor/rules/*.mdc) say a mechanism enforces, how many fire when the defect
  they name is planted in a throwaway clone (count; want K).
Count key: the mechanism's own output -- rules_sync.mjs --check exit status, or a
  policy_lint.mjs `[<class>]` ERROR line naming the planted file -- never the
  harness's own diff.
Controls (claim -> planted defect -> the mechanism that must fire):
  C1 CLAUDE.md "--check refuses drift"              one byte in a .mdc     rules_sync --check rc!=0
  C2 CLAUDE.md "... and an orphan .mdc"             an extra .mdc          rules_sync --check rc!=0
  C3 ratchet-budgets.md "a stated cap is checked by `counts`"  `AGENTS.md` stated at 14 lines  [counts]
  C4 policy_lint rule-binding ("every paths: glob matches a tracked file")  a dead glob  [rule-binding]
  C5 CLAUDE.md index "names every policy file"      the row of a rule named once deleted [index]
  C6 ratchet-budgets.md per-file cap                +1 line on a zero-headroom rule  [budgets]
Null: the unmodified clone (rules_sync rc 0, policy_lint TOTAL 0).
Perturbation: none of the six should move under a no-op; the judge's perturbation
  is any one plant reverted -> that control's fired count drops by 1.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s2/controls.py
Expected: RESULT controls_fired=6 of 6 (exact); null_errors=0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: B3.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import temp_root, clone, node, tail  # noqa: E402
import re

LINT = ".claude/workflows/policy_lint.mjs"
SYNC = ".claude/workflows/rules_sync.mjs"


def edit(d, rel, fn):
    p = os.path.join(d, rel)
    old = open(p, encoding="utf-8").read()
    new = fn(old)
    assert new != old, f"plant did not apply to {rel}"
    open(p, "w", encoding="utf-8").write(new)


def lint_fired(out, cls, where, needle=""):
    return any(f"[{cls}]" in l and where in l and "ERROR" in l and needle in l for l in out.splitlines())


CONTROLS = [
    ("C1-mdc-drift", lambda d: edit(d, ".cursor/rules/gate-scoping.mdc", lambda t: t.replace("Running the gate", "Running the gat3", 1)),
     lambda d: node(d, SYNC, "--check")[0] != 0),
    ("C2-mdc-orphan", lambda d: open(os.path.join(d, ".cursor/rules/orphan-rule.mdc"), "w").write("---\ndescription: x\nalwaysApply: true\n---\nx\n"),
     lambda d: node(d, SYNC, "--check")[0] != 0),
    ("C3-stated-cap", lambda d: edit(d, ".claude/rules/claim-files.md", lambda t: t.replace("Two limits, both measured.", "`AGENTS.md` is capped at 14 lines. Two limits, both measured.", 1)),
     lambda d: lint_fired(node(d, LINT)[1], "counts", "claim-files.md", "AGENTS.md")),
    ("C4-dead-glob", lambda d: edit(d, ".claude/rules/claim-files.md", lambda t: t.replace('  - "tests/golden/**"', '  - "tests/golden/**"\n  - "no/such/dir/**"', 1)),
     lambda d: lint_fired(node(d, LINT)[1], "rule-binding", "claim-files.md", "no/such/dir")),
    ("C5-index-row", lambda d: edit(d, "CLAUDE.md", lambda t: re.sub(r"\n\| `comment-readback\.md` \|[^\n]*", "", t, count=1)),
     lambda d: lint_fired(node(d, LINT)[1], "index", "comment-readback.md")),
    ("C6-line-cap", lambda d: edit(d, ".claude/rules/gate-scoping.md", lambda t: t + "one more line of prose\n"),
     lambda d: lint_fired(node(d, LINT)[1], "budgets", "gate-scoping.md", "lines exceeds its cap")),
]


def main():
    tmp = temp_root("controls")
    n0 = os.path.join(tmp, "null")
    head = clone(n0)
    rs, _ = node(n0, SYNC, "--check")
    rc, out = node(n0, LINT)
    m = re.search(r"TOTAL: (\d+) error", out)
    print(f"# head {head}; null rules_sync rc={rs}; policy_lint rc={rc} TOTAL={m and m.group(1)}")
    fired = 0
    for name, plant, check in CONTROLS:
        d = os.path.join(tmp, name)
        clone(d)
        plant(d)
        ok = bool(check(d))
        fired += ok
        print(f"CONTROL {name:16s} fired={ok}")
    print(f"RESULT controls={len(CONTROLS)} count")
    print(f"RESULT null_errors={int(m.group(1)) if m else -1} count")
    print(f"RESULT null_rules_sync_rc={rs}")
    print(f"RESULT controls_fired={fired} count")
    tail()


if __name__ == "__main__":
    main()
