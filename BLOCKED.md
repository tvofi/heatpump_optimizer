# BLOCKED: R10-HOTFIX-GATE-STALE-JOBS, body push

Code is handed off: refs/heads/handoff/r10-hotfix-gate-stale-jobs = 5e1e16a64f65fa2b7760902fdf316f9c45d760d0 (prepr rc=0, self-test 49 checks 0 failed, ABSENT-bound pin added and its mutant killed).
body_push.sh refuses with CARRY-MISSING R10-FLY-GH-READ-RETRY, items 0290a23c and da72de94 (the two Forward-carry items in BODY.md). Landing them is a write to the round-10 roster branch, which this seat may not push to, and I did not dismiss them to pass.
Question: will the orchestrator land the two ops (BODY.md Forward-carry text; same ops as the earlier BLOCKED note), or name another destination? Then `bash tools/audit/seat/body_push.sh r10-hotfix-gate-stale-jobs BODY.md` pushes the body unchanged.
