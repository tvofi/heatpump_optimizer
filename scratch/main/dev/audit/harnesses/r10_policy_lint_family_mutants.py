"""R10-POLICY-LINT-FAMILY: does each fix line have a check that dies without it?

    python3 dev/audit/harnesses/r10_policy_lint_family_mutants.py [--agreement-json FILE]

Applies one mutant at a time to the working tree, runs the check that owns
it, prints the refusals, and restores the file byte for byte (refusing to
continue if it cannot). Metric, one block per mutant:
    MUTANT <name> rc=<n>      -- the owning check's exit status under the mutant
        <refusal line>        -- each FIXTURE VACUOUS / FAIL / DIVERGENT line it printed
    RESTORED <n> file(s)      -- every mutated file is back to its bytes
M1 drops the family's exclusion of filed members, M2 the four synonyms, M3
the pr-body call to the gate, M4 the gate's own verdict in --check-body, M5
restores the JS line split and trim in the heading test (needs
--agreement-json, the output of `python3 -I tools/policy/agreement_py.py
--out FILE`). M6-M12 are round 2's (dev/audit/rca/R10-RCA-RAISE-GATE-GRAMMAR.md
C2, C3): the gate's refusal of a raise with no section, the lint's budget-path
trigger, its refusal when no base is named, its forwarding of the base, and
the base passed by pr-contract, prepr's body_check and body_patch.sh. The #2408
shadowing mutant is policy_lint_mutants.mjs's own record-known-bad arm, run by
that lane.
"""
import subprocess
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
PL, GATE = "tools/policy/policy_lint.mjs", "tools/policy/budget_raise_gate.py"
PRC, PREPR, PATCH = ".github/workflows/pr-contract.yml", "tools/pr/prepr.sh", "tools/audit/seat/body_patch.sh"
MUTANTS = [
    ("M1-no-exclusion", PL, "const taken = new Set(filed.flatMap((m) => [...hist.get(m).prs]))", "const taken = new Set()"),
    ("M2-no-synonyms", PL, ", 'test-vacuous', 'vacuous-test', 'vacuous-check', 'mutant-survives']", "]"),
    ("M3-no-raise-call", PL, "  const raise = raiseJustification(bodyPath, body, { base, head, paths })\n", "  const raise = null\n"),
    ("M4-check-body-ok", GATE, "        ok, why = check_body(body, raises)\n", "        ok, why = True, check_body(body, raises)[1]\n"),
    ("M5-js-heading-test", PL,
     "body.split(PY_LINE_BREAK_RE).some((ln) => ln.replace(PY_STRIP_RE, '') === '## Raise justification')",
     "body.split('\\n').some((ln) => ln.trim() === '## Raise justification')"),
    ("M6-gate-no-diff-raise", GATE, "    if raises:\n        return False, (f\"the diff raises", "    if False:\n        return False, (f\"the diff raises"),
    ("M7-no-budget-trigger", PL, "if (!heading && !budgets.length) return null", "if (!heading) return null"),
    ("M8-no-base-refusal", PL, "if (budgets.length && !diff) return", "if (false) return"),
    ("M9-no-base-forward", PL, "...(diff ? ['--base', base, '--head', head] : [])", "...([])"),
    ("M10-pr-contract-no-base", PRC, '--head "$PR_HEAD" --base "$PR_BASE" --title', '--head "$PR_HEAD" --title', 2),
    ("M11-prepr-no-base", PREPR, '  [ -n "${BASE:-}" ] && args+=(--base "$BASE")\n', ""),
    ("M12-body-patch-no-base", PATCH, '--head "$head" --base "$base" --title', '--head "$head" --title'),
]
MARKERS = ("FIXTURE VACUOUS", "  FAIL ", "DIVERGENT", "RESULT divergent", "FAIL ")


def owner(name, path, agreement):
    if name.startswith("M5"):
        return ["node", "tools/policy/agreement.mjs", "--py-json", agreement]
    if path.endswith(".sh"):
        return ["bash", path, "--self-test"]
    return ["python3", path, "--self-test"] if path.endswith(".py") else ["node", PL if path.endswith(".yml") else path]


def main(argv):
    agreement = argv[argv.index("--agreement-json") + 1] if "--agreement-json" in argv else None
    restored = 0
    for name, path, old, new, *count in MUTANTS:
        if name.startswith("M5") and not agreement:
            print(f"MUTANT {name} not run: no --agreement-json")
            continue
        f = ROOT / path
        src = f.read_bytes()
        text = src.decode()
        if text.count(old) != (count[0] if count else 1):
            print(f"MUTANT {name} not applied: its anchor appears {text.count(old)} time(s) in {path}")
            return 1
        f.write_text(text.replace(old, new))
        try:
            r = subprocess.run(owner(name, path, agreement), cwd=ROOT, capture_output=True, text=True)
        finally:
            f.write_bytes(src)
        if f.read_bytes() != src:
            print(f"RESTORE FAILED for {path}")
            return 1
        restored += 1
        print(f"MUTANT {name} rc={r.returncode}")
        for ln in r.stdout.splitlines():
            if any(m in ln for m in MARKERS):
                print("   ", ln.strip()[:160])
    print(f"RESTORED {restored} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
