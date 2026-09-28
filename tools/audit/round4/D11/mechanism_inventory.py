#!/usr/bin/env python3
"""D11 / round 4 -- one row per refusal a seat can meet, and whether its control fires.

METRIC. Two numbers and a table:
  mechanisms          -- rows, DERIVED from the tree and the API rather than
                         carried from any document: ruleset rules + required
                         contexts + policy_lint check classes + brief_lint carry
                         classes + structure.py budget metrics + wired hooks +
                         self-testing scripts. The derivation is printed beside
                         the count so a reader can re-add it.
  controls_fired      -- rows whose positive control this harness DROVE BY HAND
                         and saw refuse. A green self-test that was never driven
                         is not a control; every arm below runs the program.
  controls_inert_in_ci-- rows whose control fires when driven directly and does
                         NOT fire through the argument list CI passes. This is
                         the interesting column: `pr-body`'s `--red` arm is one.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/mechanism_inventory.py

EXPECTED at baseline 7dd68dd (tolerance: exact counts):
  mechanisms=73 controls_driven=9 controls_fired=9 controls_inert_in_ci=1
  policy_lint_classes=14 policy_lint_classes_without_fixture_entry=3
  unwired_hook_scripts=1 mutation_lane_functions=12
MACHINE: any. Node 20+ and `gh` on PATH; ~60 s wall, no timing claim.

PERTURBATION. Delete one entry from `tests/structure_budgets.json` and
`mechanisms` must fall by one; pass `--red 'fast (3.14)'` in governance.yml's
pr-contract step and `controls_inert_in_ci` must fall to 0.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
NODE = os.environ.get("D11_NODE", "node")
ZERO = "0" * 40


def run(cmd, cwd=ROOT):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str))
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    rows = []          # (family, name, refuses_where, control_driven, control_fired)
    driven = []        # (name, arm, rc, fired)

    # ---- 1. the ruleset on main -------------------------------------------
    rs = L.api(f"repos/{L.REPO}/rulesets/{L.RULESET_ID}") or {}
    rule_types = [r["type"] for r in rs.get("rules", [])]
    ctx = sorted(L.required_contexts(rs))
    for t in rule_types:
        rows.append(("ruleset", t, "main (push and merge)", False, False))
    for c in ctx:
        rows.append(("required-check", c, "pull request head", False, False))

    # ---- 2. policy_lint check classes -------------------------------------
    src = open(os.path.join(ROOT, ".claude/workflows/policy_lint.mjs"), encoding="utf-8").read()
    block = re.search(r"const CHECKS = \[(.*?)\n\]", src, re.S)
    classes = re.findall(r"name: '([a-z-]+)'", block.group(1)) if block else []
    rot = re.search(r"const REQUIRED_ROT = \{(.*?)\n\}\n", src, re.S)
    rot_keys = set(re.findall(r"^  '?([a-z-]+)'?: ", rot.group(1), re.M)) if rot else set()
    for c in classes:
        rows.append(("policy_lint", c, "PR + push to main (policy-docs)", False, False))

    # ---- 3. brief_lint carry classes ---------------------------------------
    fx = os.path.join(ROOT, ".claude/workflows/fixtures")
    carry = sorted(f for f in os.listdir(fx) if f.startswith("carry-99"))
    for f in carry:
        rows.append(("brief_lint", f, "PR (briefs job)", False, False))

    # ---- 4. the structural ratchet -----------------------------------------
    bud = json.load(open(os.path.join(ROOT, "tests/structure_budgets.json")))
    metrics = [k for k in bud if k != "recorded_at"]
    for m in metrics:
        rows.append(("structure.py", m, "PR (fast) + push to main", False, False))

    # ---- 5. hooks ----------------------------------------------------------
    settings = json.load(open(os.path.join(ROOT, ".claude/settings.json")))
    wired = [h["hooks"][0]["command"] for k, v in settings["hooks"].items() for h in v]
    for k in settings["hooks"]:
        rows.append(("hook", k, "the seat's own session", False, False))
    hookdir = os.path.join(ROOT, ".claude/hooks")
    unwired = [
        f for f in sorted(os.listdir(hookdir))
        if f.endswith(".sh") and not any(f in w for w in wired)
    ]

    # ---- 6. self-testing scripts, each DRIVEN ------------------------------
    arms = [
        ("rules_sync", [NODE, ".claude/workflows/rules_sync.mjs", "--check"], 0),
        ("policy_lint corpus", [NODE, ".claude/workflows/policy_lint.mjs"], 0),
        ("policy_lint mutants", [NODE, ".claude/workflows/policy_lint_mutants.mjs"], 0),
        ("fragments_sync", [NODE, ".claude/workflows/fragments_sync.mjs", "--self-test"], 0),
        ("policy_lint --hooks", [NODE, ".claude/workflows/policy_lint.mjs", "--hooks"], 0),
        ("gh_comment", ["python3", ".claude/workflows/gh_comment.py", "self-test"], 0),
        ("prepr.sh", ["bash", "tools/audit/prepr.sh", "--self-test"], 0),
        ("push.sh", ["bash", "tools/audit/push.sh", "--self-test"], 0),
        ("check-wave-script", [NODE, ".claude/workflows/check-wave-script.mjs"], 0),
    ]
    for name, cmd, want in arms:
        rc, out = run(cmd)
        fired = rc == want
        driven.append((name, " ".join(cmd), rc, fired))
        rows.append(("self-test", name, "PR (policy-docs / pr-contract)", True, fired))

    # ---- 7. the `pr-body --red` arm, BOTH WAYS -----------------------------
    # Drive the refusal by hand first, then through the exact argument list
    # `.github/workflows/governance.yml` passes. A control that only fires on
    # the first is a mechanism CI cannot reach.
    body = ".claude/workflows/fixtures/policy-rot/prepr/unnamed-red.md"
    paths = os.path.join(os.environ.get("TMPDIR", "/tmp"), "d11-paths.txt")
    open(paths, "w").write("README.md\n")
    base = [NODE, ".claude/workflows/policy_lint.mjs", "--pr-body", body,
            "--head", ZERO, "--title", "t", "--paths-file", paths]
    rc_red, _ = run(base + ["--red", "fast (3.14)"])
    rc_ci, _ = run(base)
    gov = open(os.path.join(ROOT, ".github/workflows/governance.yml"), encoding="utf-8").read()
    ci_passes_red = "--red" in gov
    inert = int(rc_red == 1 and rc_ci == 0 and not ci_passes_red)
    print("PR-BODY `--red` ARM, DRIVEN BY HAND:")
    print(f"  with --red 'fast (3.14)' : rc={rc_red}  (1 = the refusal fires)")
    print(f"  governance.yml's arg list: rc={rc_ci}  (0 = the same body passes)")
    print(f"  governance.yml passes --red: {ci_passes_red}")

    # ---- report -------------------------------------------------------------
    print()
    print("MECHANISM COUNT, DERIVED:")
    print(f"  ruleset rules on main                {len(rule_types):3d}")
    print(f"  required status-check contexts       {len(ctx):3d}")
    print(f"  policy_lint check classes            {len(classes):3d}")
    print(f"  brief_lint carry fixtures            {len(carry):3d}")
    print(f"  structure_budgets.json metrics       {len(metrics):3d}   (keys less recorded_at)")
    print(f"  wired hook events                    {len(settings['hooks']):3d}")
    print(f"  self-testing scripts driven here     {len(arms):3d}")
    print(f"  ----------------------------------------")
    print(f"  mechanisms                           {len(rows):3d}")
    print()
    print("SELF-TESTS DRIVEN:")
    for name, cmd, rc, fired in driven:
        print(f"  {'ok  ' if fired else 'FAIL'} {name:<22} rc={rc}  {cmd}")
    print()
    no_mut = sorted(set(classes) - rot_keys)
    print(f"policy_lint classes with no REQUIRED_ROT fixture entry: {no_mut}")
    print(f"policy_lint classes in REQUIRED_ROT but not in CHECKS:  {sorted(rot_keys - set(classes))}")
    rc_m, out_m = run([NODE, ".claude/workflows/policy_lint_mutants.mjs"])
    mutated = set(re.findall(r"PIN\s+\w+\s+(\w+)", out_m))
    print(f"functions the mutation lane empties:                    {len(mutated)}")
    print(f"hook scripts present but not wired in settings.json:    {unwired}")

    print()
    L.result("mechanisms", len(rows))
    L.result("ruleset_rules", len(rule_types))
    L.result("required_contexts", len(ctx))
    L.result("policy_lint_classes", len(classes))
    L.result("policy_lint_classes_without_fixture_entry", len(no_mut))
    L.result("brief_lint_carry_fixtures", len(carry))
    L.result("structure_metrics", len(metrics))
    L.result("wired_hook_events", len(settings["hooks"]))
    L.result("unwired_hook_scripts", len(unwired))
    L.result("controls_driven", len(driven))
    L.result("controls_fired", sum(1 for _, _, _, f in driven if f))
    L.result("controls_inert_in_ci", inert)
    L.result("mutation_lane_functions", len(mutated))
    L.footer()


if __name__ == "__main__":
    main()
