R10-DIMENSIONS-FULL-COVERAGE is split in two by decision 0013's Consequences (a pinned grader that pins the shape of the artifact it grades is two pull requests).

**p1, handed off here:** `handoff/r10-dimensions-full-coverage` is `origin/main` plus one file, `tools/policy/check-wave-script.mjs`, the wave-script grader made to pass over both the tree on main and the tree p2 brings. It changes no policy and no artifact.

**p2, not handed off:** `handoff-wip/r10-dimensions-full-coverage` holds everything the brief owes (A to F), on a history that does not contain p1's commit but carries the byte-identical grader file. It is a WIP handoff until p1 is on main (`fixer.md` step 5, BOOTSTRAP). The step ref is therefore NOT deleted. Its drafted body is `P2-BODY.md` on `handoff-wip/r10-dimensions-full-coverage-body`.

What p2 still owes before its own handoff, in order:

0. The roster group's two dispatched carries, which the dispatch payload did not snapshot and this seat read only at the handoff (`jq` of the group on `origin/handoff/audit-r10-roster`):
   - Carry 0: add to the defect group's `cause` what FOUND the defect (a finder dimension, a reviewer, CI on main, the owner, an outside user) beside what caused it, in `tools/audit/convergence.py` (`check`, `report`, self-test), `root-cause.md` section 6 and `orchestrator.md` section 13; and make `tools/audit/seat/scorecard.py`'s `E` line split escapes by `cause.dimension` from that one field, not a second mechanism. Evidence the carry cites: the process convergence audit at d5d7ff8187, findings Q-E1 and Q-E2.
   - Carry 1: in `dev/audit/README.md`'s playbook, a pointer at the finder phase (phase 2) to `COMMON.md`'s "The denominator" and `tools/audit/enumerate.py`, beside the phase 13 pointer already there; and a dry read in the body: from the playbook alone a new orchestrator reaches the step and the instrument that enforces it. If R10-ROUND-PLAYBOOK-FINAL has not merged, carry the pointer to it. The same instruction says outside and owner-filed findings fold into the running round unless explicitly deferred; `orchestrator.md` section 2 still says a round's scope freezes at its register, which this group has not edited.
   Both raise per-file caps again (`policy_budgets.json`).

1. p1 merged to main. Then `git merge origin/main` into the WIP head (the grader file is identical on both sides) and `node tools/policy/check-wave-script.mjs` at the merged head.
2. `tools/pr/prepr.sh <P2-BODY.md>` clean. Its last run, before the split, predicted these reds; the state of each:
   - `GRADER check-wave-script.mjs REFUSED by the base's copy` (BOOTSTRAP): answered by p1. Re-check after step 1; it must be gone.
   - `LAYOUT placement` for `tools/audit/enumerate.py` and `tools/audit/convergence.py`: repaired in the WIP head (`tests/layout.json`; `python3 tests/layout.py --guard --base origin/main` prints 0 refusals).
   - `UNCLASSIFIED dev/governance/dimensions/D16.md` and `D17.md`: a brief is classified by a measured closure (`tests/closure.py` `_CITATION_POLICY`), and `tests/entities.py`'s closure lists D0 to D15. Repair: `./tests/derive_closures.sh --single tests/entities.py` on Linux (the script's header puts it near 25 minutes), then commit `tests/closures.json`. See the note at the end of this file for whether that ran.
   - `tools/ci/selftest_closures.json`, step `self-tests-outside-seat`: the step gained two commands, so its measured entry is stale and the drift check on a push to main would name it. Repair: `python3 -I tools/ci/selftest_scope.py record --step self-tests-outside-seat` (Linux, strace). See the note at the end.
3. The body's `## Head`, figures and mutation table re-taken at the final head (`fixer.md` step 6).
4. Owner decisions the body flags: the wording of `D16.md` and `D17.md`; the three rotation bounds in `rotation.json` (D0.M4, D3.M1, D14.M2); the budget raise in `policy_budgets.json`.
5. Overlap with R10-D5-D6-FULL-SCOPE, for whoever merges second: the `CADENCE` line of `audit-find.js`, `D6.md` step 2, the cadence test of the grader (p1 already derives it from the table, so either order passes), and `_territory_pending` in `scopes.json`, which `check_scopes.py` refuses once D5 or D6 carries a `ledger` key: that merge declares their `territory`.

A choice made late that a resumer should not undo without reading why: D1 and D16 are NOT isolated dimensions. An isolated dimension is listed in both `audit-find.js` and `tools/audit/prepare_baseline.sh`, the second is pinned to the base in CI, and D1 has a brief, so the base's grader refuses the pair. The Prepare step of `audit-find.js` instead exports earlier releases' packages under `old-releases/<tag>/`, which gives both dimensions the old writers with no `.git`.

State of the two re-records at this push (2026-11-13):

- `tools/ci/selftest_closures.json`: re-recorded and committed on the WIP head (`selftest_scope.py record --step self-tests-outside-seat`, exit 0).
- `tests/closures.json` for `tests/entities.py`: NOT yet merged. `./tests/derive_closures.sh --single tests/entities.py` ran to the end and refused to merge, because `tests/entities.py` exits 1 on this tree with exactly two failing checks, both the classification this record exists to repair: "every tracked file is either measured or deliberately classified" and "every carry and every policy file this arm reads for citations selects this script", each naming only `D16.md` and `D17.md`. The script's own remedy is the two-step `./tests/derive_closures.sh --record-only --out-dir D` then `python3 tests/closure.py merge --in-dir D --partial --allow-failures`, legitimate here because the run reached its final tally line (all checks executed).
