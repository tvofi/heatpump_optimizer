Fix review: merge 234e6df8739b8403a5bc295cd9c8006f7af8dc7b

bus-nonce: aff7e9fa8341212de54eddc3af9d5be0

Round 1, record PR (triage s8 batch 81, P318). Head measured: 234e6df8739b8403a5bc295cd9c8006f7af8dc7b.

## Findings

- The ruling puts the P318 carry on R10-NIGHTLY-HB-RESPAWN, whose own roster carry on main says to close that group as superseded unless a nightly red recurs. The batch text says the new carry may be dispatched alone, but nothing says what happens to it if the group is closed, so the orchestrator must dispatch the carry (or re-home it) before any such closure. Carry: R10-NIGHTLY-HB-RESPAWN

## Evidence

- Three-dot diff touches only dev/programme/triage/s6-batch81.md and dev/programme/delivery/3026.md; no production, claim, VERSION or budget file moved, so steps 1-6 and 14 have nothing to mutate.
- origin/main 2376d3f9e: tests/entities.py:18368 is def _hb_stdlib_reads and :18392 is the find_spec("_remote_debugging") arm with no handler, as cited. The docstring wording about the privilege matches.
- git log -S: the arm arrived in 120cd1bb6 (2026-10-29), as cited.
- The four handoff-body tips (r10-cop-partload-p2, r10-fly-beat-fetch-race, r10-hotfix-learner-inputs, r10-ux-health-p2) each record the task-port PermissionError; quotes match, including the 44 FAIL lines at the merge base.
- Roster on main: R10-NIGHTLY-PYSPY-RETRY is done, R10-NIGHTLY-HB-RESPAWN is queued (S, after PYSPY-RETRY), as the batch states.
- The held op b81-P318.txt and the "about 6 min" local-run figure are not in the tree or the PR, so I could not re-derive them; the ruling stands on the cited code and bodies without them.
- git merge-tree --write-tree origin/main: rc=0, no conflict.
- merge_train.py classify: GREEN (after polling WAIT; ev/classify.txt). Packet carry_audit: 0 findings; no refusals.
- VERSION, manifest and notes heading untouched.
