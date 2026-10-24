Root-cause seat, topic r10-rca-codescan-wait. Start from origin/main; read dev/governance/roles/root-cause.md and dev/governance/rules/defect-root-cause.md first. This runs beside the countermeasure fix and never inside it.

DEFECT. pr-contract goes red at tools/ci/codescan_wait.py exit 1 while codeql Analyze is in progress on a fresh head, and the gate fails with "still being judged". Three instances on 2026-10-24: #2698 at 3383fb2a, #2704 at 04860ee0, #2706 at ea459c0b. Each needed a hand rerun, and the tick read each as owed to the fixer (a false "back to fixer").

OWED (root-cause.md): (1) a named cause; (2) the process state, one of (a)-(d), with its reason; (3) a cost test with numbers (count the instances, reruns and tick misreads from the check-runs API, not from memory; print the failure count beside each figure); (4) a countermeasure, or a recorded refusal.

MEASURE FIRST. Read the pr-contract log of one instance and say which exit path of codescan_wait.py fired. Read the check-runs API for the three heads, not gh pr checks.

COUNTERMEASURE. The fix itself is carried to R10-CI-LAYOUT-P2 (triage P62, dev/programme/triage/s6-batch4.md#P62). Do not implement it here. Record the carry with a Carry: line and cite the roster branch SHA beside it if the destination is not on main's roster.

RECORD. Write dev/audit/rca/R10-RCA-CODESCAN-WAIT.md, following the shape of dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md. Push refs/heads/handoff/r10-rca-codescan-wait and body_push.sh refs/heads/handoff-body/r10-rca-codescan-wait. Re-run prepr to a pass at your head first; do not touch VERSION, RELEASE_NOTES or either claim file. Write a literal n/a: <reason> for any carry that is none.
