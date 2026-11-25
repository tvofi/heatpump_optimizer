Fix review: merge a45822062eea60500c87f5804206455e7405d6d1

bus-nonce: c12a068a57e21c0cee0b8f70bc33d490
pending-ci: gate

Round 2, delta review, at head a45822062eea60500c87f5804206455e7405d6d1. The review covers the repair `git diff 0d345358c4 34cefdc55b` and the main merges up to the head (f6cf4ccae6, then a45822062e merging 7588328188, which merges main 0e1eba2b). Cloud seat, Linux, CI venv, `OPENBLAS_CORETYPE` Haswell. Worktrees at the head and at 0d345358c4.

## Findings

- Note: carry-missing: the `## Forward-carry` item s2 (direct slab: the radiator curve leaves the upper floor 0.232/0.451/0.670 K short) is still routed to #3713, which this merge closes, as it was at 0d345358c4. As in round 1, the orchestrator files the sibling issue before the merge or rules otherwise. Carry: #3713
- Note: stale-body: the body's round-2 paragraph says "merges cleanly, so no merge was made". Two main merges have been made since then (f6cf4ccae6, and a45822062e merging 7588328188 into main 0e1eba2b). The body's `## Head` line does name a45822062e and 7588328188 correctly. This is paperwork, not production. Carry: dismissed: a stale body sentence, the `## Head` line is current

## Evidence

- Prior finding resolved. The round-1 block at 0d345358c4 was `test-gap`: the valve-fed law's zone weighting was unpinned off r = 0.5 and M9 survived. The reviewer drove M9 itself with `ev/m9_drive.sh`. The edit is in `thermal_model.py`'s `_valve_flow_set`, `free_heat_kw = (w_upper * (1.0 - r) + w_lower * r) * p.internal_gains / w_sum` (`ev/head.M9.diff.txt`, `ev/prev.M9.diff.txt`), on the block `features_block.py "# R11-SEAM-two-zone-slab (#3713): ..." "# R11-VALVE-REFERENCE (carries 0, 1): ..."`. Results (`ev/m9.summary.txt`):
  - head, unmutated: rc 0 (`ev/head.unmutated.txt`).
  - head, M9: rc 1, 2 of 4 FAIL (`ev/head.M9.txt`). (a) fails with split 0.3/0.7 at 21.0713, scalar and batch, at +5/-5/-15 C. (b) fails with split 0.7/0.3 at 21.0401. The install's 0.5 rows read 21.0000.
  - 0d345358c4, unmutated: rc 0 (`ev/prev.unmutated.txt`).
  - 0d345358c4, M9: rc 0, no FAIL (`ev/prev.M9.txt`). M9 survives there and is killed at the head. Its figures match round 1's split probe and the body's.
  - Both worktrees were restored clean after each run.
- Delta content. `tests/features.py` adds `_TZ_SPLITS` (install, 0.3/0.7, 0.7/0.3) and `_tz_split`. (a), (b) and (d) now loop over all three splits. (d)'s previous two-split loop now reads `_TZ_SPLITS`, a superset. The (a)/(b) gate check still asserts `two_zone_enabled`, valve-fed and target 21.0 on the base install. Other changes in the delta:
  - `carry-3881.json` is new. It is byte-identical to origin/main, which landed it via #3892 (`git diff --quiet origin/main <head>` on that path). It states its control as a precondition: the 35 C start, four kernel classes, the base's +1.500, and the single-zone null arm. That resolves round 1's carry-missing note on R9-F2.1 P3.
  - `tests/closures.json` adds the carry to the entities closure.
  - Four ledger pins by 34cefdc55b and three by `mutation-autofix`'s 3e2dc1b603. These are bot and `--pin-killed` rows, and CI's mutation-pins lane re-checks them.
- Production. `custom_components/` is unchanged between 0d345358c4 and 34cefdc55b. The PR's own three-dot production diff at the head is identical to the one at 0d345358c4: `diff` of `git diff <merge-base> <sha> -- custom_components` with index lines dropped, merge bases 24e3f37620 and 0e1eba2b. The production delta against 0d345358c4 comes from main's merges alone, so it does not widen the review.
- Merge: `git merge-tree --write-tree origin/main a45822062e` exits 0. Roles are current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff.
- carry_audit: the packet's run on the body at the head reads `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`. The verdict's own items were checked with `carry_audit.py check` (`ev/carry_audit.txt`).
- CI: `merge_train.py classify a45822062eea60500c87f5804206455e7405d6d1 --pr 3879` (`ev/classify.log`, last output `ev/classify.last.txt`). The state is recorded below.
  - Every poll from 14:30Z to 14:59:37Z printed `WAIT a45822062eea60500c87f5804206455e7405d6d1 pending: gate red: none`, rc 3, 19 runs at intervals of 60 s or more.
  - The verdict is therefore returned with `pending-ci: gate`, and the relay posts it only once CI is green at this head.
  - No red was read, so no `## Red checks` answer is owed at this head.
- carry_audit on this verdict: `carry_audit.py check` exits 0 (`ev/carry_audit.txt`).
- Not re-run, following the delta scope and fix-review.md step 11: the eight-edit proof M1 to M8 and M10 to M15 (round 1 ran them and production is unchanged), `env_drift.py --all`, the gate, and the mutation table. The four new ledger pins are left to CI's `tests / mutation-pins` lane.
