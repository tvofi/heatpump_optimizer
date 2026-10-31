#!/usr/bin/env python3
"""D11 / round 4 -- the merge boundary, read with BOTH arms, against the tree's account of it.

METRIC. Three numbers about the enforcement boundary on `main`:
  (1) pull_request_rules      -- rules of type `pull_request` in the live
                                 ruleset. This is the only rule that can require
                                 an approving review; 0 means a merge to `main`
                                 needs none.
  (2) bypass_actors_always    -- actors with bypass_mode `always`, and whether
                                 the identity that performs the merges is one.
  (3) tree_claim_mismatches   -- assertions in the TREE about the required-check
                                 set (a count, or `record` being in it) that the
                                 live ruleset contradicts.

BOTH ARMS, because they disagree by construction. Arm A is
`GET /repos/:r/rules/branches/main`, which lists the rules that apply to the
branch and says nothing about who may bypass them. Arm B is
`GET /repos/:r/rulesets/:id`, which carries `bypass_actors`. A seat that reads
only arm A concludes "16 required checks, enforced" and is wrong about its own
merges.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/ruleset_probe.py

EXPECTED at baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (tolerance: exact;
these are counts from the API, not timings):
  pull_request_rules=0, bypass_actors_always=1, bypass_applies_to_merger=1,
  required_contexts=16, tree_claim_mismatches=8, api_failures=0
MACHINE: any; network-bound, no CPU claim.

PERTURBATION. Change one digit in a tree assertion -- e.g. `18` in
tests/record_status.py:13 -> `16` -- and `tree_claim_mismatches` must fall by
one. Nothing in CI derives that number from the API, which is the finding.
"""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d11lib as L  # noqa: E402

ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()

# Files that assert something about the required-check set. Each entry is
# (path, regex, what the regex captures). Derived by grepping the tree for
# `main-protect` and `required context`; the harness re-greps so a new
# assertion is caught rather than carried.
CLAIM_GLOBS = [
    "tests/record_status.py",
    "tests/entities.py",
    "tests/nightly_status.py",
    ".github/workflows/governance.yml",
    ".github/workflows/tests.yml",
    "docs/HANDOVER.md",
    "docs/plan-2026-09-open-issues.md",
    ".github/CODEOWNERS",
    "RELEASE_NOTES.md",
]
# `\d+` alone matches the ruleset ID in "main-protect 22628467 required contexts".
# A required-check set has at most two digits here; the bound is what separates
# a count from an identifier, and it is the difference between 8 and 10.
COUNT_RE = re.compile(r"\b(\d{1,2})\s+required (?:status check|context)")
RECORD_RE = re.compile(r"`record` is one of `main-protect`'s")


def main():
    # ---- arm A: the branch-rules endpoint (not bypass-aware) ----------------
    armA = L.api(f"repos/{L.REPO}/rules/branches/main") or []
    a_types = sorted(r["type"] for r in armA)
    a_ctx = set()
    for r in armA:
        if r["type"] == "required_status_checks":
            a_ctx = {c["context"] for c in r["parameters"]["required_status_checks"]}
    print(f"ARM A  rules/branches/main -> {a_types}")
    print(f"ARM A  required contexts: {len(a_ctx)}")
    print(f"ARM A  bypass information: (none -- this endpoint carries no bypass field)")

    # ---- arm B: the ruleset object -----------------------------------------
    rs = L.api(f"repos/{L.REPO}/rulesets/{L.RULESET_ID}") or {}
    b_types = sorted(r["type"] for r in rs.get("rules", []))
    b_ctx = L.required_contexts(rs)
    bypass = rs.get("bypass_actors", [])
    print(f"ARM B  rulesets/{L.RULESET_ID} -> {b_types}  enforcement={rs.get('enforcement')}")
    print(f"ARM B  required contexts: {len(b_ctx)}")
    print(f"ARM B  bypass_actors: {bypass}")

    # Who merges? The repository's own permission block for the authenticated
    # identity, which is the identity every merge in this repository is made by.
    repo = L.api(f"repos/{L.REPO}") or {}
    perms = repo.get("permissions", {})
    is_admin = bool(perms.get("admin"))
    always = [b for b in bypass if b.get("bypass_mode") == "always"]
    # RepositoryRole actor_id 5 is `admin` in GitHub's built-in role table.
    admin_always = any(
        b.get("actor_type") == "RepositoryRole" and b.get("actor_id") == 5
        for b in always
    )

    print()
    print(f"ARM DISAGREEMENT: arm A lists {len(a_ctx)} enforced context(s) and no bypass;")
    print(f"                  arm B shows {len(always)} actor(s) with bypass_mode=always.")
    print(f"                  authenticated identity admin={is_admin}")

    pr_rules = [r for r in rs.get("rules", []) if r["type"] == "pull_request"]

    # ---- the tree's account of the boundary --------------------------------
    mism = []
    for rel in CLAIM_GLOBS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            for m in COUNT_RE.finditer(line):
                n = int(m.group(1))
                if n != len(b_ctx):
                    mism.append((rel, i, f"claims {n} required contexts, live set is {len(b_ctx)}"))
            if RECORD_RE.search(line) and "record" not in b_ctx:
                mism.append((rel, i, "claims `record` is a required context; it is not"))
    print()
    print("TREE ASSERTIONS THE LIVE RULESET CONTRADICTS:")
    for rel, i, why in mism:
        print(f"  {rel}:{i}  {why}")

    # ---- history: the set is not a constant --------------------------------
    vers = L.ruleset_versions()
    print()
    print("RULESET VERSION HISTORY (utc, n_required, has pull_request rule, bypass_always):")
    for ts, st in vers:
        ctx = L.required_contexts(st)
        prr = any(r["type"] == "pull_request" for r in st.get("rules", []))
        ba = len([b for b in st.get("bypass_actors", []) if b.get("bypass_mode") == "always"])
        print(f"  {ts}  n={len(ctx):2d}  pull_request_rule={prr}  bypass_always={ba}")

    print()
    L.result("required_contexts", len(b_ctx))
    L.result("arm_a_required_contexts", len(a_ctx))
    L.result("pull_request_rules", len(pr_rules))
    L.result("bypass_actors_always", len(always))
    L.result("bypass_applies_to_merger", int(admin_always and is_admin))
    L.result("ruleset_versions", len(vers))
    L.result(
        "ruleset_versions_with_pull_request_rule",
        sum(1 for _, st in vers if any(r["type"] == "pull_request" for r in st.get("rules", []))),
    )
    L.result("tree_claim_mismatches", len(mism))
    L.footer()


if __name__ == "__main__":
    main()
