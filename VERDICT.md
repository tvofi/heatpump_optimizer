Fix review: merge 134d25cbce3e369577b7b4c1951ff656ba82ced2

bus-nonce: e0de51d62bfaa4e2e348637f8ac8e812

Round 1. Docs-only triage record: one file under dev/programme/triage/ plus its delivery row. No production code, so no mutation proof of production lines applies.

## Evidence
- RESULT head: measured 134d25cbce3e369577b7b4c1951ff656ba82ced2; the PR head at read time.
- RESULT merge-tree origin/main 134d25cbce3e369577b7b4c1951ff656ba82ced2: rc=0, clean tree 0a7eb9d5.
- RESULT classify: GREEN (pending: none, red: none), rc 0. Packet gate digest green; no refusals; carry_audit 0 findings.
- RESULT diffstat: 2 files (the triage file and delivery/3381.md); the body says "one file", and the delivery row is the standard companion. VERSION, manifest and RELEASE_NOTES untouched. No claim files touched.
- RESULT spot re-derivation at origin/main 0a8033305d: review_packet.py LANDED regex accepts all-digit strings while brief_lint SHA_RE requires an a-f letter (P466); cloud_relay.sh handoff arm runs bus.sh dispatch and never cloud_dispatch --publish, which exists (P467); merge_train latest_runs keeps the worst gate suite and READMIT_SAME_VERDICT is HOLDER, BRANCH_POLICY, PREFLIGHT_PARK (P468, P470); open_driver.resolve and names_group exist (P474); tools/ci/sweep.py with settle commits 34b98bbdb and 6158186e1 on main (P465); reconcile.py absent from the tree (P464). Session-local logs, run listings and verdict-ref counts (46 re-runs, 58/26 blocked verdicts, 35 open bodies) are not in the tree; not re-derived.
- RESULT policy: P473 and P475 are ACCEPT with owning groups, and they carry the bar-skip route (owner directive, medium root-cause class). The rejects state the percentage against the 20 % bar. The ruling text matches the brief's restatement of the 2026-11-08 rulings.
- Red checks: none on the head; body answers none. Forward-carry: none claimed; each ACCEPT/DEFER names its group in its Carry line.

## Findings
- Follow-up: P475's pending-ci exit needs a statement of whether a CI-only block counts toward the three-round rule. That is fix-review.md text, which is policy, and the entry says the owner approves it at the merge. Carry: R10-DISPATCH-AT-HANDOFF
- Follow-up: P465 hands the orchestrator the decision to re-enable gate-sweep.yml after #3327; the cost is about 46 hand re-runs and 9 review rounds a night. The orchestrator decides and records it. Carry: dismissed: orchestrator action named in the PR, not a tracked-code defect
