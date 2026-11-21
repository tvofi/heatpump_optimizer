Fix review: merge ef62eaecaffa0e0b81e1a2b4b5718d78fdd52e6c

bus-nonce: dfde3aa1b0569a3dfa22b563bb626cb2
pending-ci: gate

## Findings

none

## Evidence

- Round: second review of this PR. This is a delta round over the reviewed head 007e7be48d0fcfe5c01c9bafb920f0c34c67d12a. `review_carry.py 007e7be4 ef62eaec` prints `FRESH-REVIEW`.
- Head: `ef62eaecaffa0e0b81e1a2b4b5718d78fdd52e6c` is still `refs/pull/3737/head` (`git ls-remote`). The body's `## Head` section names it.
- Delta scope: the PR's own commits in `007e7be4..ef62eaec` that are not on main are these five:
  - adf0a38ba1 and d4e133dc1f, which change `tests/features.py`;
  - dbc6569df2 and 247ce3b6da, which add mutation-ledger `killed_by` pins;
  - 7b9204eb3a, which deletes the stale pin `HeatPumpOptimizerCoordinator._dhw_current_hour.RETURN_DEL.a653dd5d`. The method is now the module function `_dhw_current_hour` (`coordinator.py:908`), and that function's own pin a2025997 is present.
  - The rest of the delta is main merges.
- The PR's production diff is unchanged across the round. `git diff <merge-base> <head> -- custom_components` at 007e7be4 (base 9fe63d00) and at ef62eaec (base e698fc8a) differ only in hunk offsets and index lines. Nothing in `custom_components/` widens the scope.
- The previous block (mutation-vacuous, `draw_range.fold`'s `commit_runs(keep=not (frozen or distorted))`) is resolved. adf0a38ba1 adds the check "fold commits a closed space run as a row only when the interval is neither frozen nor distorted ...", which drives `fold` with each flag alone, both flags and neither. I ran each mutant on block A at the head (ev/mutants_delta.txt):
  - unmutated: `ALL 33 FEATURES BLOCK PASSED`
  - `keep=True`: 1 of 33 FAIL (new check)
  - `keep=not distorted`: 1 of 33 FAIL (new check)
  - `keep=not frozen`: 1 of 33 FAIL (new check)
  - `keep=False`: 2 of 33 FAIL (new check and the window null)
  - `keep=not (frozen and distorted)` (my own extra mutant): 1 of 33 FAIL
  - These match the body's mutation-proof figures.
- d4e133dc1f's check, "the heating floor is capped by the ceiling before the entity's minimum decides", kills main's mislabelled-equivalent CLAMP_DROP at `pump_arbiter.py:972`. I ran it in the R10-SETPOINT-BOOST block (ev/mutants_delta.txt, ev/blockB_head.txt):
  - unmutated: the check is `ok`, with no FAIL in the block.
  - `lo=(m.floor_c)`: the check FAILs with `[45.0, 45.0, 45.0] 30.0 50.0`. These are the body's figures: 45 under the mutant, against 35 at the head; nulls 30 and 50.
  - `lo=None`: killed by 2 existing checks.
  - `lo=(m.heat_c)`: killed by 7 existing checks.
  - main's triage `survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json` is absent at the head, and the killed pin `_flow_target.CLAMP_DROP.6dfae9cd` is present.
- Instrument limit: `features_block.py` run over the R10-SETPOINT-BOOST span to part A stops later with `NameError: name '_s5_effective' is not defined`. This is a gap in the emitted prelude across an 18k-line span, which `--emit-prelude` exited 1 on. It is after the CLAMP check. 169 checks ran `ok` and none FAILed before it. CI's `tests / fast` runs the whole script.
- `tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, `seam_cut_total 413 <= 413` (ev/structure_head.txt).
- `git diff $(merge-base)...head` leaves `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files untouched.
- Merge with main: `git merge-tree --write-tree origin/main ef62eaec` exits 0 (ev/merge_tree.txt).
- carry_audit at the head (review packet): `14 finding item(s): 14 routed, 0 unrouted, 0 bad destination(s)`. All name R11-CARRY-DRAWMAP's split parts B and F, under the approved note's split-part exception. I did not re-verify this beyond the previous round's reading.
- Red checks: owed-reds is {`tests / mutation`, `tests / typing`, `validate / validate-hacs`}. The body's `## Red checks` answers the earlier `tests / mutation` reds (at 007e7be4, adf0a38b and 212e7976). CI state at this head is given by the classify line in the next item.
- CI: `merge_train.py classify ef62eaec --pr 3737` read `WAIT ef62eaecaffa0e0b81e1a2b4b5718d78fdd52e6c pending: gate red: none` on every run from 15:28 to 16:00 UTC (ev/classify_poll.log). The review is otherwise complete, so the verdict carries `pending-ci: gate`. Head re-read at 16:00 UTC: still ef62eaec.
