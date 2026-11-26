Fix review: merge e4a8523d89c02aa9b4f7c477c6ecfabed09689ec

bus-nonce: 689f1f8cae45711a3ff758c9f729cc1e
pending-ci: gate

Round 4, a delta re-review: `git diff 91cfc89fdade e4a8523d89c0`. Round 2 blocked 91cfc89fdade on `unload-row-written`. Round 3 (`probe/rev-3872-849621cb`, `1495000c9dc5`) returned `merge` at 3c89b84f7bd8 with `pending-ci: gate`. `review_carry.py 3c89b84f7bd8 e4a8523d89c0` prints `FRESH-REVIEW`, so this round reads the range 3c89b84f7bd8..e4a8523d89c0 as new. The 91cfc89fdade..3c89b84f7bd8 half is round 3's, re-confirmed below. I did not widen the scope. The one production conflict in the range is the import line in `pump_arbiter.py`. The only other production change is main's #3879 (`thermal_model.py`, `ledger.py`), which merged with no conflict and touches no fault-hold seam.

## Notes

- Note: round-count: this is the fourth review of this PR. fix-review.md says "from the fourth, a re-cut is owed". The rounds here came from head moves over main merges after a `merge` verdict, not from repeated blocks, so I return no block for it. The orchestrator rules on it. Carry: dismissed: round 3 was `merge`, and rounds 3 and 4 come from main merges, not from blocks on this fix
- Note: body-stale: `## Figures` and `## Unpinned sites` are measured at `0c8d0bd41e6b`, not at the head. The body names the later merges (`21fe7364c3`, `a0ef2a9513`, `21cbf81375`, the automatic `e4a8523d89`) and `c1b0af3c16` only in `## Head`. Below, I re-took every figure that bears on the code at this head. Carry: dismissed: paperwork; each figure re-derived here holds at e4a8523d89c0

## Findings

none

## Evidence

- Round 2's block `unload-row-written` stays resolved. `fault_hold.release` marks a holding entry (`_RELEASED_HOLDING`), `unload_holds` reads the latch or that mark, and `_release_row` gates `reason == "unload"` on it. These lines are unchanged since `fdde1320d3`, which round 3 confirmed. At this head, `fault_hold.py:143-159` reads exactly that.
- Mutation proof, re-run at this head from a detached worktree: `python3 -u dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD` gives `BASELINE 0 failing`, `RESULT mutants=41`, `RESULT survived=0`, EXIT 0 (`ev/mutants.log`). That matches the body's 41/0. It includes the unload-mark mutants (`unload mark set`, `unload mark read`, `unload mark cleared`), and each is killed.
- Production merge resolution in range, `0c8d0bd41e` (`git show --remerge-diff`, `ev/remerge_0c8d0bd4_production.diff`): the only `custom_components/` conflict is the `pump_arbiter.py` import line, resolved as the union `... duty_switch, fault_hold, flow_limit, issues ...`. That is correct for both sides.
- The merges `a0ef2a9513`, `21cbf81375` and `e4a8523d89` have no remerge diff under `custom_components/` (`ev/remerge_later_production.txt`). Their only resolutions are ledger-driver set merges (`tests/closures.json`, `tests/structure_budgets.json`), plus `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt` in `21cbf81375`.
- The only production change since `0c8d0bd41e` is main's own #3879 (`thermal_model.py` `_valve_flow_set` two-zone weighting, `ledger.py` `REFERENCE_BASIS` 4→5). It shares no lines with `fault_hold`, `_write_supply`, `_arbitrate` or `_release_row`, so it puts no reviewed fault-hold behaviour at risk.
- `c1b0af3c16` adds one survivor triage, `fault_hold.py:gate RETURN_DEL da9e8e97`, as `equivalent`. I read it against `fault_hold.py:128-140` at this head: the mutated line is the function's last statement, `return None`. Replacing it with `pass` falls off the end and returns `None` as well, so the triage is sound. It moves no metric beyond the ledger row.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all d9100de781ec` gives `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, EXIT 0 (`ev/env_drift.log`).
- `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`, and `python3 tests/comment_ratchet.py` gives `comment_ratchet: OK` (`ev/structure.log`).
- Body figures at this head: `tests/deployment_shape.py:60` reads "186 of the 561 script pairs", and `git ls-files custom_components/heatpump_optimizer/ | wc -l` reads 123. Both match the body. I did not re-derive the 186 with `tests/entities.py` (about 11 minutes); CI's `tests / fast` is the authority for it.
- `git merge-tree --write-tree origin/main e4a8523d89c0` exits 0, with origin/main at `658fcae30b8d` (`ev/merge_tree.txt`).
- `VERSION`, `manifest.json` and `RELEASE_NOTES.md`: the three-dot diff against the merge base `d9100de781ec` is empty.
- `dev/governance/roles/`: no drift between the merge base and origin/main.
- CI: `merge_train.py classify` read `WAIT ... pending: gate red: none` on all 25 polls from 01:19 to 01:50 UTC, hence `pending-ci: gate`. See `ev/classify.log` for every `merge_train.py classify e4a8523d89c0 --pr 3872` poll. The packet's digest showed `gate` failure, `tests / nightly-ha (2025.2.0)`, `nightly-ha (stable)` and `nightly-status` failure. None of those names is in `merge_train.py owed-reds`, and classify reads `red: none`, so no `## Red checks` answer is owed.
- I did not re-run the gate or the full `tests/features.py`; CI's heavy runs are cited instead.
