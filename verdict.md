Fix review: merge 815ebab2a5398507fc2cc3df6ef8791ad74c3c89

bus-nonce: d6ec0bf935c214123ad62bff02e8def4
pending-ci: gate

## Scope

Round 2 of this PR's review: round 1 returned `merge` at `95eae2dd6f` (probe `probe/rev-3678-8ee69eac`). `69dc1cd4f2`, the bot's pin commit on top of it, went red on `tests / mutation`; no verdict naming it is on a probe ref or on the PR. Delta review against `69dc1cd4f2`, as dispatched. The packet's `Review scope` line reads `full` only because no verdict names `69dc1cd4f2`. The delta is the round-1 finding set plus `git diff 69dc1cd4f2 815ebab2a5`. `review_carry.py 69dc1cd4f2 815ebab2a5` prints `FRESH-REVIEW` because `7f7bbc5cb4` is a hand-resolved merge (ev/review_carry.txt). The branch's own commits in the range are `e78cd86ab` (three checks in `tests/features.py`), `846a1e10f` (three `killed_by` ledger rows), `7f7bbc5cb4` (main merged; conflicts in `dev/audit/rounds/round4/D6/claims.py` and `tests/deployment_shape.py`), and `59047cf34` and `3a16b7a93` (counts in `docs/architecture.md` and the D6 register). None of them touches `custom_components/`. `diff` of the `-U0` changed lines under `custom_components/` at `69dc1cd4f2` against its merge base and at `815ebab2a5` against its merge base prints nothing. With no production delta, the scope does not widen. Policy copy is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` prints 0 lines.

## Evidence

- Step 1, the mutation proof for the repaired red, re-run on a git-archive copy of `815ebab2a5` by my own driver (ev/mut5.sh, ev/mut5.log). Each mutant is applied in place, then the rooms blocks run through `features_block.py` from the `#3616 R11-OUTSIDE-ROOMS-P1` marker with the emitted prelude. Each runs once against `69dc1cd4f2`'s `tests/features.py` ("old") and once against the head's ("new"):
  - unmutated: old `ALL 38 FEATURES BLOCK PASSED`, new `ALL 41 FEATURES BLOCK PASSED`
  - `inputs.py` `_scaled`, min-end clamp dropped: old 38 passed, new `1 of 41 FEATURES BLOCK FAILED`
  - `inputs.py` `_scaled`, max-end clamp dropped: old 38 passed, new `1 of 41 FEATURES BLOCK FAILED`
  - `rooms.py` `_margins`, `np.clip` dropped: old 38 passed, new `1 of 41 FEATURES BLOCK FAILED`
  - `rooms.py` `resolve`, `max(..., 0.0)` floor dropped: old 38 passed, new `1 of 41 FEATURES BLOCK FAILED`
  - `rooms.py` `resolve`, `ROOM_LIFT_CAP_C` cap dropped: old `6 of 38 FEATURES BLOCK FAILED`, new `6 of 41 FEATURES BLOCK FAILED`

  Each row matches the body's table, and the files were restored byte-identical (`RESTORED`). Four new checks each kill a mutant the old file let survive; the cap was already killed, and now has a ledger row. Each new check carries a control against absolute values, not against `max_age_for`, which calls `_scaled`. The values are `[180, 180, 3600, 3600]` for base 360 and scales 0, 0.5, 10 and 1e9; a room 0.5 K shorter than the house holds 0.5; a margin of -0.5 equals no margin.
- The ledger rows: `rooms.py/resolve.CLAMP_DROP.1af0ce3c.json` names `killed_by: tests/features.py`, and its `old` line is the head's `rooms.py:274` text. The two other files are as the body lists them.
- Merge with main: `git merge-tree --write-tree origin/main 815ebab2a5` exits 0 (ev/merge_tree.txt). origin/main is `38bf516bdd`, the head's own merge base. No claim-file driver ran.
- Merge resolution `7f7bbc5cb4` (`git show --remerge-diff`): both conflicts are the same count, which main's `runs.py` and this branch's `rooms.py` each raised by one. They resolve to 96, keeping both histories in the parenthetical. Re-derived at the head: `ls custom_components/heatpump_optimizer/*.py | wc -l` gives 96, and `git ls-tree -r --name-only 815ebab2a5 custom_components/heatpump_optimizer | wc -l` gives 115. Both match the register and `tests/deployment_shape.py`. The 167 closure pairs and the HA-free 62 are not re-derived under their own predicates here (`tests/entities.py`'s `_d308_pairs`, and its homeassistant rule). A plain `grep -l homeassistant` over the modules returns 36, which is my definition and not the test's. Those two figures rest on CI's `tests / fast` and the gate at this head, which run `tests/entities.py`, `tests/doc_claims.py` and `tests/deployment_shape.py`.
- Step 4, claims: against the merge base, `tests/golden/claimed_drift.txt` differs only by the `config_flow` line, phase 1's claim extended for the toggle. `card_claimed_drift.txt` is untouched. No solve fixture moved in the delta (no production change).
- Step 5: `git diff --stat <mb>...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is empty (ev/static.txt).
- Step 14: the only `*_budgets.json` change against the merge base is in `tests/structure_budgets.json`. There, `class_excess_loc` goes 17407 -> 17385 (down) and `recorded_at` changes, both written by the ledger merge driver (ev/static.txt). No metric rises, and `budget-raise-gate` is green.
- Round-1 finding (M15, `rooms.lifted` identity on the all-clipped path) was dismissed there as plan-equivalent. The delta does not touch `rooms.lifted`, so it stands as recorded.
- Step 11: `69dc1cd4f2`'s reds were `tests / mutation`, `pr-contract / pr-contract` and `gate`, each in `merge_train.py owed-reds` (ev/owed_reds.txt). The body's `## Red checks` answers all three: mutation names a cheaper detector (prepr step 6d and `ci_predict.py`); pr-contract records that none exists; gate is a consequence. `tests / nightly-status` was red in the packet's digest; it is outside the owed set and is neither answered nor a block.
- CI at this head: `merge_train.py classify 815ebab2a5 --pr 3678` printed `WAIT 815ebab2a5398507fc2cc3df6ef8791ad74c3c89 pending: gate red: none` (rc 3) at every poll from 02:43 to 03:12 UTC (ev/classify.txt). The packet's `introduced-red: unreadable` refusal was `instrument-self-tests` still in progress at render, and classify decides. The heavy runs are CI's and were not re-run here.
- Step 12: `git ls-remote origin refs/pull/3678/head` prints `815ebab2a5398507fc2cc3df6ef8791ad74c3c89`, the head measured.
- Step 16: N/A; the delta adds no production path.

## Notes

- Note: body-figure: `## Figures` says the ledger merge driver "kept the older `recorded_at`". The kept `4ce615b5e6` (committed 2026-11-16) is newer than main's `a39627da59` (2026-11-15). Paperwork only, no metric is affected. Carry: dismissed: a wording slip in a body figure, no later stage reads it
