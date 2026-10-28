Fix review: merge 583219fa8a44c79e038ae091ce907dafa3e847d0

bus-nonce: 4fff0b41f588c5ca0029da5a4a9d2c9b

Round 1. Reviewed head `583219fa8a44c79e038ae091ce907dafa3e847d0` (still the head when this was written), merge base origin/main `50af6174f`. The PR adds one INERT ruling record (`dev/programme/triage/s6-batch2.md`, P45-P52) and its delivery row. It changes no code, check, budget, claim file, closure or version.

## Evidence

- RESULT roles-current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so this review used the current contract.
- RESULT merge: `git merge-tree --write-tree` exits 0 against `50af6174f` and against the newer origin/main `0c3640761`. No conflict and no claim-file involvement.
- RESULT version: `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (three-dot diff).
- RESULT mutation (step 1): there is no production line, so the step does not apply as written. I tested the consumer instead. `roster_edit.ruling_verdict` at the head returns P45 ACCEPT, P46 ACCEPT, P47 DEFER, P48 DEFER, P49 ACCEPT, P50 REJECT, P51 ACCEPT, P52 REJECT and P53 None. `triage_refusal` passes carries citing #P45, #P46, #P49 and #P51, and refuses #P47 (DEFER), #P50 (REJECT) and #P53 (no such entry). Mutant: changing P45's verdict to REJECT makes the refusal fire for #P45. The body's null control reproduces (`ev/nullcontrol.txt`). The harness is mine, built from the body's description; no committed harness exists for a ruling record.
- RESULT figures, all re-derived at `50af6174f`:
  - Verdict counts: 4 ACCEPT, 2 DEFER, 2 REJECT; 8 entries.
  - P49: 14 of 48 merges, and the chain #2676-#2686 each add only their own `delivery/<N>.md`.
  - P52: the five commit times match in UTC.
  - `N-postreview-merge-red`: kind instrument, total 0, 15 non_round_instances, rca R9-RC-POSTREVIEW-MERGE, barrier null, `trigger` with per_round, cross_round and barriered_any false and class_rca_on_record true.
  - RCA `776d37392` is an ancestor of `handoff/r10-rca-ci-ratchet-run-name`. Its numbers (129 s/day, 21 600 s, 167 days, state (d) "not (c)", section 5 not registering) are as quoted.
  - Code citations: `sweep_template.md:61` names `train.sh`, last edited in `b16084794`. `pulse.py` 49-53 is the queue format and `STANDING` is at line 91. `roster_sync.py` 84-92 is `DERIVABLE_STAGES`, which excludes `carries-open`. `replan.py` ~205 is `touches_coordinator`. `standing-tick.md:8` is the only wait/background line. `orchestrator.md:109` is the "Four standing seats" line.
  - Roster at `4c54758d7` (an ancestor of the current roster head): R10-ORCH-BEATD, R10-FLOW-RECORD-PITCH, R10-ORCH-ROSTER-SCHEMA, R10-FLOW-TOOLKIT-MODEL and R10-FLY-PRUNE-REFS are not-started. R10-FLY-INERT-LOAD-TIME is in-progress. R10-FLY-RELAY-REVIEW-FF and R10-CI-LAYOUT-P2 are carries-open. This matches the file.
- RESULT ref_privacy: `ref_privacy.py --check` at the head prints `0 refused`. The body's red `instrument-self-tests` at `44ee0e5f` is answered (bypassed detector named, 0.5 s), and that job is now green at this head.
- RESULT CI on the head (`ev/ci.txt`): every workflow has concluded.
  - The final `gate` 120841072885 is success.
  - `pr-contract` 120840986826 started after the last red check and passed.
  - The two red `gate` runs at this head (120838763234 and 120840541163) each print only "run(s) ... at this head are still being judged; their gate decides". That is a deferral to a later run, not a defect, so no root-cause answer is owed.
  - The mutation lane is green but drew no mutant (no production code line).
- RESULT class (step 6): no enumeration rule applies, because the PR is a ruling record and not a fix of a seam.
- RESULT forward-carry (step 10): the carry texts for P45/P46/P51 and P49 are in the tree file, and each states its controls. They are not yet on the roster branch (`717f7e582` has 0 lines citing s6-batch2). By design `roster_edit` refuses them until this file is on main or the roster branch, so the ops are owed after the merge (findings below).

## Findings

- After the merge, append the shared standing-seat carry (P45, P46, P51; text in `s6-batch2.md` "One destination") to R10-ORCH-BEATD with `roster_edit.py append-carry`, citing `triage: dev/programme/triage/s6-batch2.md#P45` (#P46, #P51). This cannot land before the merge. Carry: R10-ORCH-BEATD
- After the merge, append P49's record-chain carry (measure first) to R10-FLOW-RECORD-PITCH, citing `#P49`. Carry: R10-FLOW-RECORD-PITCH
- P52's derivation command is inaccurate. `TZ=UTC git log -1 --format=%cI <sha>` prints the committer's +02:00 offset, not UTC; `--date=iso-strict-local --format=%cd` with `TZ=UTC` prints UTC. All five quoted UTC times are correct after conversion (`ev/checks.txt`), so no figure is wrong. Carry: dismissed: wording of a derivation command in a ruling record; every figure it supports re-derives correctly
- The delivery row's title still reads "(P45-P51)", but the PR title and file cover P45-P52. `delivery-status` is green at this head. Carry: dismissed: cosmetic title drift in a record row that no check reads as a figure
- P52 asks the RCA seat (R10-RCA-CI-RATCHET-RUN-NAME) to add a `bugclasses.json` row on its own PR before that PR merges. No live roster group owns that RCA, so the ruling routes it as an orchestrator ask rather than a carry. Carry: dismissed: routed by the ruling to the RCA seat's own pull request; no roster group to carry to
