Fix review: merge b163dc32376e1f448ea408c4de4c53645850a392

bus-nonce: f17fa2392995ec7818ab354d34b46114

Round 2: the second `Fix review:` on #3402, after round 1's `blocked b10beaad55c9 config-attack`. Scope follows the owner's 2026-11-09 ruling: the delta `git diff b10beaad55c9fdb50ec8446bb3593c3ca11d8bd0 b163dc32376e1f448ea408c4de4c53645850a392`, round 1's findings, and the live required checks. I measured head `b163dc32376e1f448ea408c4de4c53645850a392`. It is a merge of `ae769072d` into `b10beaad5` and has the same tree as `ae769072d` (`git diff --stat` is empty), so the body's code head and this head are one tree (step 7).

## Findings

None open. Round 1's block is resolved, and so is its budget-1 residual. Its R21 follow-up was already carried as roster carry 10 of R10-ARBITER-OFF-RESTORE.

## Evidence

- Round 1 block (unbounded adopted baseline), resolved. `write_persistent` now adopts `_within_range(reading.value - (state["written"] - baseline), reading)`. `_within_range` is the clamp `persistent_target` already applied: its four lines moved into one helper that both sites call, with the same semantics (step 15: no breach). Inside the range the adoption is unchanged, so the bound adds no behaviour there. Afterwards `state["written"] = reading.value` keeps a re-classification idempotent: at the edge a second adoption gives the same clamped value. When the entity declares no range, behaviour is as before. The delta's production change reaches no code outside these two call sites, so the review was not extended (`ev/delta_production.diff`).
- The body's departure from P6 is stated, and it holds. With range 20..35, 22 is displaced +3 to 25, and a hand edit to 21 adopts 20, not 18. The +3 then writes 23, and off restores 20. At the edge the plan therefore moves the user's setting by `b + d - reading`, 2 K here. Displace 0 writes 20, the same value the arm and off restore hold. The checks pin the floor, ceiling and neutral cases with their null controls, and I re-ran them. The body weighs the two alternatives, refusal and bounding at restore, and both lose on stated grounds. I judge the departure an architecturally sound resolution of the note's internal P6-versus-I1 conflict, not a step-17 breach. The arbiter's side is carried: roster carry 11 of R10-ARBITER-OFF-RESTORE on `origin/handoff/audit-r10-roster` at `f769963686cc` states "an adopted baseline must be a value the entity holds" with its control (M21) (step 10).
- Round 1 residual (budget 1 writes nothing), resolved by the docs: `docs/configuration.md`, `docs/ecl110.md`, `strings.json` and the en/de/sv translations now say "0 or 1 writes nothing". The widened check drives budgets 0 and 1. My M26 (reserve `+2` -> `+1`) fails it.
- Mutation proof (step 1): `ev/mut.py` drives `ev/mcmd.sh`. That is my own block runner: `tests/features.py`'s prologue, its imports, the helper definitions the block names, then the two R10-GENERIC-HEAT-CURVE sections. Unmutated it prints `ALL 106 FEATURES BLOCK PASSED` at this head and `ALL 103` at `b10beaad5` (`ev/block_head.log`, `ev/block_base.log`). The delta is exactly +3 checks plus the widened budget check. My runner counts one more check than the body's 105/102 because its extraction differs; the delta agrees. All 7 mutants are killed (`ev/mutants.log`):
  - M21, adoption bound removed: the 3 range-edge checks fail, matching the body.
  - M22, the helper's ceiling side removed: 2 checks fail ("max 23 sends 23" and the ceiling check), matching the body.
  - M23, the floor side removed: 3 fail.
  - M24, the adoption bounded on the floor only: the ceiling check fails.
  - M25, the plan target unbounded: 2 fail.
  - M26, the reserve +1: 4 fail, including the budget-1 check.
  - M27, the adoption clamp dropped: 3 fail.
- Finder's harness (steps 2, 9): none exists. This is the owner-ruled build, as round 1 recorded. The mutant runner above is my own and lives in `ev/`.
- Claims (step 4): `GOLDEN_MODE=drift tests/env_drift.py --all origin/main` prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, rc=0 (`ev/env_drift.log`).
- Versions (step 5): `git diff <merge-base>...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is empty.
- Ratchet and ledger (step 14): `tests/structure.py` prints STRUCTURE RATCHET PASSED (`ev/structure.log`). The ledger drops four `persistent_target` CLAMP_DROP/GUARD_OFF pins and adds five `_within_range` pins. They are the same clamp lines, moved. M22, M23 and M25 show the sites are killed by `tests/features.py`, so the pins are earned.
- Merge (step 13): `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main `0362916ac7c1`, with `LEDGER-MERGE: resolved tests/closures.json` in stderr (`ev/merge_tree.stderr`). No conflict. Main has since moved to `5d09dedf69eb`; the train re-proves the merge there.
- CI (step 11): `merge_train.py classify b163dc32376e1f448ea408c4de4c53645850a392 --pr 3402` returned WAIT until 06:22:49Z, then rc=2 `REFUSE ci: the check runs at b163dc32376e could not be read` on every poll to 08:15:49Z (`ev/ci_classify.log`). The cause is environmental. The head has 126 check runs, and `gh api --paginate` follows a `repositories/{id}` Link URL that this cloud seat's proxy refuses with HTTP 403. I read pages 1 and 2 explicitly and took the latest run of each of the 23 required contexts that `merge_train.py owed-reds` lists. All 23 are completed success or skipped, including `gate` success (id 129687971835, 07:18:11Z) and `pr-contract / pr-contract` success (id 129687160630, 07:14:54Z) (`ev/ci_required_manual.txt`). No non-required context is red at its latest run either. So no red check is owed a `## Red checks` answer. The orchestrator should re-confirm with classify from a seat whose `gh` can paginate.
- Head re-read before return (step 12): `refs/pull/3402/head` is `b163dc32376e1f448ea408c4de4c53645850a392`, unchanged.

## Friction

- `merge_train.py classify` cannot read more than 100 check runs from a cloud seat, because `--paginate` follows numeric-ID repository links the agent proxy blocks. Once a head passes 100 runs, every cloud review returns rc=2 for good. Requesting `&page=N` explicitly works.
