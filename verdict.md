Fix review: merge d925d867badb9a3ac12b2a73133174f9a8bc1b4a

bus-nonce: aeb688738f58569e975f980f1ab3fe5f
pending-ci: classify prints `WAIT d925d867badb9a3ac12b2a73133174f9a8bc1b4a pending: gate red: none` (no context named; runner-starved, still queued after repeated polls)

Round 2, delta review b6c080db..d925d867 (head ev/HEAD.txt). The PR's own delta is the harness repair 79c063dc; the rest of the range is main merged in.

## Evidence

- Block answered. The previous block (carry 7 dismissal rested on a null control that could not fail) is repaired: dev/audit/harnesses/prepr_slot_nested.py now cuts the real take_slot out of tools/pr/prepr.sh, runs it against the real tests/gate_lock.py in a private lock dir with a 3/4 pool, and never sets HPO_SLOT_LABEL itself. Outer arm takes the free slot and exports the label; nested arm (pool 4/4) returns at once with "joined prepr-788", no queue ticket. The bare arm now differs by evidence: still waiting at the bound AND slot-status lists `queue=prepr-796`. Head run: rc 0, all ten RESULT rows as wanted (ev/head.out).
- Mutants, each re-run by me at the head (tree restored after each, git status clean):
  - harness's own --mutant (delete `export HPO_SLOT_LABEL`): rc 1, fails outer_exported_label, nested_finished, nested_queue_empty, nested_joined (ev/mutant.out).
  - drop the "joined" branch of take_slot: rc 1, fails nested_finished, nested_queue_empty, nested_joined (ev/mutant_nojoin.out).
  - export the label on the WARN path: rc 1, fails warn_no_label (ev/mutant_warnlabel.out).
  - add a take_slot call to prepr's --self-test branch: rc 1, fails selftest_branch_takes_slot (ev/mutant_selftest.out).
  The null control can now fail; each mutant fails a distinct pin.
- Carry audit at the head: 1 finding item, 1 routed, 0 unrouted. figure_lint: 2 resolved, 0 not verified, 0 refused.
- Merge: `git merge-tree --write-tree origin/main d925d867...` exit 0, no conflict.
- Three-dot diff against main is .gitignore, the harness, delivery/3479.md, tests/closures.json, tests/gitignore_config.py; VERSION and RELEASE_NOTES.md are not in it (the RELEASE_NOTES hunk in the delta is main's v7.1.11 stamp).
- Commit message check: no Claude footer or Co-Authored-By in the head commit.
- CI: classify exits 0 printing WAIT with "gate red: none"; not a red. Not re-derived: the body's PRE-PR run (heavy). tests/closures.json entries not re-derived.

## Findings

- Out of scope: the real outer-prepr step 3h end-to-end path (full prepr run with pool full) is covered only by the cut-function arms plus the static check that the --self-test branch never calls take_slot, not by a whole prepr run. Carry: R10-PREPR-RESIDUE | #3479 | O1 | dismissed: the cut take_slot is the code step 3h calls, the label/join/WARN paths and the self-test branch are each pinned by a mutant that fails, and a full pool-full prepr run is hours of heavy gate for no further discriminating row.
