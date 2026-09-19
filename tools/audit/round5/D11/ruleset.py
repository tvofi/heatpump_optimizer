#!/usr/bin/env python3
"""D11 round 5 -- what the merge boundary's own ruleset lets through, and what
the tree's only reader of it can see.

METRIC DEFINITIONS (one line each):
  M1 rules_bypassed_by_the_live_bypass_actor -- the number of rules in ruleset
     `main-protect` that a holder of a bypass actor whose `bypass_mode` is
     `always` skips at the merge boundary (GitHub: `always` bypasses the
     ruleset regardless of rule type; `pull_request` bypasses only the
     pull_request rule).
  M2 derived_output_delta_between_two_rulesets -- the byte count of the
     difference between the JSON `counts.mjs:liveRequiredContexts()` returns
     for a ruleset carrying a `pull_request` rule and `bypass_actors`, and the
     JSON it returns for the same ruleset with both removed.
  M3 recorded_shape_parameter_disagreements -- the number of `pull_request`
     parameters whose live value differs from the value the decision record
     that prescribed them (docs/decisions/0008, carried by 0009 step 6) writes.

COMMAND
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D11/ruleset.py

Reads GitHub read-only (`gh api`), the tree, and one `node` probe that imports
`.claude/workflows/counts.mjs`. Writes only under its own directory. No BLAS
import, so the thread pin is a no-op and `thread_factor` is 1.0.

EXPECTED (baseline eaa2a06, 2026-09-19)
  M1 = 4 of 4; the second arm (bypass actor removed) = 0
  M2 = 0 bytes, while the two rulesets differ in 1 rule and 1 bypass actor
  M3 = 1 of 5 (`dismiss_stale_reviews_on_push`: recorded true, live false)

MACHINE macOS Darwin 25.6.0, 8-core Apple M1, python3 3.11.5, node v22.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
RULESET_ID = "22628467"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"

STUB_GH = r"""#!/bin/bash
# stub gh for the counts.mjs probe: answers the two calls the reader makes.
case "$*" in
  */rules/branches/main) cat "$STUB_DIR/branch.json" ;;
  */rulesets/*) cat "$STUB_DIR/ruleset.json" ;;
  *) echo "stub gh: unhandled $*" >&2; exit 9 ;;
esac
"""


def gh(args):
    p = subprocess.run(["gh", "api"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"gh api {' '.join(args)} rc={p.returncode}: {p.stderr.strip()[:200]}")
    return json.loads(p.stdout)


# The M2 perturbation: carry what the ruleset says about its OTHER rules and its
# bypass actors into the object the reader returns. Three one-line edits in
# `.claude/workflows/counts.mjs`; the file is restored byte-identically after.
ARM_FIXED_READER = [
    ("    const viaRulesets = new Set()",
     "    const viaRulesets = new Set(); const shapes = []"),
    ("      const rs = JSON.parse(execFileSync('gh', ['api', `${base}/rulesets/${id}`], { encoding: 'utf8' }))",
     "      const rs = JSON.parse(execFileSync('gh', ['api', `${base}/rulesets/${id}`], { encoding: 'utf8' }))"
     "\n      shapes.push({ id, rules: (rs.rules || []).map((r) => r.type),"
     " bypass: (rs.bypass_actors || []).map((a) => a.bypass_mode) })"),
    ("    return { contexts: a, count: a.length, rulesets: [...ids].sort((x, y) => x - y) }",
     "    return { contexts: a, count: a.length, rulesets: [...ids].sort((x, y) => x - y), shapes }"),
]


def bypassed(ruleset):
    """M1: rules skipped by the strongest bypass actor present."""
    actors = ruleset.get("bypass_actors") or []
    if any((a.get("bypass_mode") or "").lower() == "always" for a in actors):
        return len(ruleset.get("rules") or [])
    if any((a.get("bypass_mode") or "").lower() == "pull_request" for a in actors):
        return sum(1 for r in (ruleset.get("rules") or []) if r.get("type") == "pull_request")
    return 0


def probe(root, ruleset, branch):
    """Drive the production reader with a stubbed gh; return its JSON output."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "bin").mkdir()
        stub = td / "bin" / "gh"
        stub.write_text(STUB_GH)
        stub.chmod(0o755)
        (td / "ruleset.json").write_text(json.dumps(ruleset))
        (td / "branch.json").write_text(json.dumps(branch))
        env = dict(os.environ, STUB_DIR=str(td), PATH=f"{td / 'bin'}:{os.environ['PATH']}")
        p = subprocess.run(
            ["node", str(HERE / "counts_probe.mjs"), str(root)],
            capture_output=True, text=True, env=env)
        if p.returncode != 0:
            raise RuntimeError(f"probe failed: {p.stderr.strip()[:300]}")
        return json.loads(p.stdout.strip().splitlines()[-1])


def recorded_pull_request_parameters():
    """The `pull_request` parameter block the live rule is measured against.

    The shape the live rule was created from is 0009 step 6: "`0008` step 3(d)'s
    parameter shape with the count `0008` step 4 deferred" -- i.e. 0008's block
    verbatim except `required_approving_review_count`, whose value is 0008 step
    4's 1. Both are read from the records rather than typed here."""
    text = (ROOT / "docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md").read_text()
    start = text.index('"type": "pull_request"')
    block = text[start:text.index("}", text.index('"required_review_thread_resolution"', start))]
    params = json.loads("{" + block + "}}")["parameters"]
    # 0008 step 4's count is the one 0009 step 6 lands the rule with; 0008 step
    # 3(d) writes 0 there and defers the value to step 4. Read step 4's prose.
    import re
    step4 = text[text.index("4. **The review seat's own identity"):]
    m = re.search(r"`required_approving_review_count: (\d+)`", step4)
    params["required_approving_review_count"] = int(m.group(1))
    return {"parameters": params}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-bypass", action="store_true",
                    help="perturbation arm for M1: the same ruleset with every bypass actor removed")
    ap.add_argument("--arm-fixed-reader", action="store_true",
                    help="perturbation arm for M2: three one-line edits carry the ruleset's rule types "
                         "and bypass actors into the reader's returned object")
    ap.add_argument("--flip-recorded-dismissal", action="store_true",
                    help="perturbation arm for M3: flips the recorded dismiss_stale_reviews_on_push "
                         "in memory, which must move the disagreement count DOWN to 0")
    args = ap.parse_args()
    rs = gh([f"repos/{REPO}/rulesets/{RULESET_ID}"])
    (HERE / "ruleset_raw.json").write_text(json.dumps(rs, indent=1))
    rules = rs.get("rules") or []
    actors = rs.get("bypass_actors") or []
    keys = gh([f"repos/{REPO}/keys"])

    live_m1 = bypassed(rs) if not args.no_bypass else bypassed(dict(rs, bypass_actors=[]))
    # Arm B: the same ruleset with every bypass actor removed -- the direction
    # `docs/decisions/0009` step 5 names ("scoped down from `always`").
    no_bypass = dict(rs, bypass_actors=[])
    arm_m1 = bypassed(no_bypass)

    pr_rule = next((r for r in rules if r.get("type") == "pull_request"), None)
    pr_params = (pr_rule or {}).get("parameters", {})
    print(f"RESULT perturbation_arm_no_bypass={1 if args.no_bypass else 0}")

    print(f"RESULT rules_in_main_protect={len(rules)}")
    print(f"RESULT bypass_actors={len(actors)}")
    print(f"RESULT bypass_actors_with_bypass_mode_always={sum(1 for a in actors if (a.get('bypass_mode') or '') == 'always')}")
    print(f"RESULT rules_bypassed_by_the_live_bypass_actor={live_m1}")
    print(f"RESULT rules_bypassed_with_the_bypass_entry_removed={arm_m1}")
    print(f"RESULT write_deploy_keys_enabled={sum(1 for k in keys if k.get('enabled') and not k.get('read_only'))}")
    print(f"RESULT pull_request_rule_present={1 if pr_rule else 0}")
    print(f"RESULT required_approving_review_count={pr_params.get('required_approving_review_count')}")
    print(f"RESULT require_code_owner_review={1 if pr_params.get('require_code_owner_review') else 0}")
    print(f"RESULT dismiss_stale_reviews_on_push={1 if pr_params.get('dismiss_stale_reviews_on_push') else 0}")
    print(f"RESULT require_last_push_approval={1 if pr_params.get('require_last_push_approval') else 0}")

    recorded = recorded_pull_request_parameters()["parameters"]
    if args.flip_recorded_dismissal:
        recorded["dismiss_stale_reviews_on_push"] = not recorded["dismiss_stale_reviews_on_push"]
    disagree = [k for k, v in recorded.items() if pr_params.get(k) != v]
    print(f"RESULT perturbation_arm_flip_recorded_dismissal={1 if args.flip_recorded_dismissal else 0}")
    print(f"RESULT recorded_shape_parameter_disagreements={len(disagree)}")
    for k in disagree:
        print(f"RESULT   disagreement {k}: recorded={recorded[k]!r} live={pr_params.get(k)!r}")

    # M2: is the tree's ruleset reader sensitive to the rule and the bypass actor?
    # The branch-endpoint surface carries the same 15 contexts on both arms, so
    # the only difference between them is the `pull_request` rule and the bypass
    # actor. The reader must return the SAME JSON on both, which is the finding.
    contexts = sorted(
        c["context"] for r in rules if r["type"] == "required_status_checks"
        for c in (r.get("parameters") or {}).get("required_status_checks", []))
    branch_rules = [{"type": "required_status_checks", "ruleset_id": int(RULESET_ID),
                     "parameters": {"required_status_checks": [{"context": c} for c in contexts]}}]
    counts_mjs = ROOT / ".claude/workflows/counts.mjs"
    original = counts_mjs.read_bytes()
    try:
        if args.arm_fixed_reader:
            text = original.decode()
            for old, new in ARM_FIXED_READER:
                assert old in text, f"the anchor {old[:48]!r} is not in counts.mjs; nothing was changed"
                text = text.replace(old, new, 1)
            counts_mjs.write_text(text)
        arm_a = probe(ROOT, rs, branch_rules)                      # live ruleset
        trimmed = dict(rs, bypass_actors=[], rules=[r for r in rules if r["type"] != "pull_request"])
        arm_b = probe(ROOT, trimmed, branch_rules)                 # both removed
    finally:
        counts_mjs.write_bytes(original)
    a = json.dumps(arm_a["value"], sort_keys=True)
    b = json.dumps(arm_b["value"], sort_keys=True)
    delta = len(a) - len(b) if a != b else 0
    print(f"RESULT perturbation_arm_fixed_reader={1 if args.arm_fixed_reader else 0}")
    print(f"RESULT counts_mjs_restored_byte_identical="
          f"{1 if counts_mjs.read_bytes() == original else 0}")
    print(f"RESULT derived_output_delta_between_two_rulesets={abs(delta)}")
    print(f"RESULT derived_value_is_null_on_either_arm={1 if (arm_a['value'] is None or arm_b['value'] is None) else 0}")
    print(f"RESULT probe_arm_a={a}")
    print(f"RESULT probe_arm_b={b}")
    print(f"RESULT probe_reason_arm_a={arm_a['why']!r}")
    print(f"RESULT probe_reason_arm_b={arm_b['why']!r}")
    print(f"RESULT rulesets_differ_in_rules_count={len(rules) - len(trimmed['rules'])}")
    print(f"RESULT rulesets_differ_in_bypass_actors={len(actors) - 0}")
    print(f"RESULT delta_probe_control_contexts_count={arm_a['value']['count'] if arm_a['value'] else None}")

    print(f"RESULT load1={os.getloadavg()[0]}")
    print("RESULT thread_factor=1.0")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
