Fix review: merge 1d114ed62a582faeb04211104ebb118ec30bd6c9

bus-nonce: dc878c5b1636c3c9e7d88bee4994a75f

## Scope

Round 2 (delta round) of the fix review of #3220, R10-HOTFIX-SAV-ESTIMATE. Reviewed head 1d114ed62a582faeb04211104ebb118ec30bd6c9, from a detached worktree at that SHA. Previous verdict blocked 6dcd1abb85eca7b53bfe390c5b934907f38419f8 (ratchet-grown, typing). `review_carry.py 6dcd1abb8 1d114ed62` prints FRESH-REVIEW, because the branch's own commits e76b0d7dc, bf628b2ec, 539995fa5 and 70f0c46f5 change its content. So this round re-reviews those four and re-takes the measurements the brief names. The roles diff from merge base to origin/main touches only `standing-dispatch.md`, so this contract is current.

## Evidence

- RESULT typing: `.venv-typing` built from `tests/requirements-typing.txt` with `--require-hashes --no-deps`, the way `tests.yml` builds it. `tests/typing_ruler.py --mypy` at the head gives `ALL 9 typing-ruler checks PASSED`, rc 0, 0 errors (ev/typing_head.log). Null control: the head with `class LedgerStore(QuarantiningStore):` (the line before e76b0d7dc) gives `FAIL errors did not grow [recorded 0, measured 2 (+2)]` and `FAIL by_code[type-arg] did not grow [recorded 0, measured 2 (+2)]`, rc 1 (ev/typing_null.log). The block is repaired. `tests/typing_budgets.json` is untouched.
- RESULT features: `PYTHONPATH=tests/hastub python3 tests/features.py` ran in full at the head and printed `ALL 4832 FEATURE CHECKS PASSED`, rc 0 (ev/features_head.log, OPENBLAS_CORETYPE=Haswell).
- RESULT entities: `PYTHONPATH=tests/hastub python3 tests/entities.py` ran in full at the head and printed `ALL 2622 ENTITY CHECKS PASSED`, rc 0 (ev/entities_head.log). Both were runnable on this Linux host, so nothing was skipped.
- RESULT census (the finder's harness, `dev/audit/harnesses/r10_rca_sav_estimate.py`, sha1 04b644563c84d26378cad42a603dc050e7e5fd88, identical at d8eeae8f8, the merge base and the head):
  - At merge base 6125b263d: single 1.00, unvalved 0.92, valve-at-curve 0.00, valve-charged 0.00, wood-warm 0.00, wood-hot 0.00. That is `6 of 6 cells ran, 4 out of band`, rc 1.
  - At the head: 1.00, 0.92, 1.00, 1.00, 1.00, 1.00. That is `6 of 6 cells ran, 0 out of band`, rc 0 (ev/census_base.log, ev/census_wt.log).
  - The null cells (single, unvalved) are in band at both ends. Booked over horizon mean is 1.00 on five cells and 0.92 on unvalved, as the body says.
  - The `ledger` and `attrib` arms need the owner's export, which this host does not have, so they were not run.
- RESULT mutants: each mutant ran the full `tests/features.py` on a copy of the head tree (ev/make.py, ev/run.sh, ev/mutants_features.txt). The copies have no `.git`, so the null copy (a comment-only change) fails exactly one check, `and the path that proceeds still stamps a resolvable recorded_at (#363)`. That failure is discounted in every row below.
  - `null`: only that recorded_at check fails. The null is clean.
  - `wood0` (`_wood_covered_share` returns 0): KILLED by `a wood tank's usable heat, at the pump's COP, is the share of the solve's starts it covers ...`, which reads `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`.
  - `wood1` (it returns 1): KILLED by the same check, which reads `(1.0, 1.0, 1.0, 0.0, 0.0, 0.0)`.
  - `floordel` (the `max(0.0, ...)` on `required_thermal` is deleted): KILLED by `a thermostat on a warm plain house buys no heat and sells none: not one reference step is negative` (min -0.679) and by `a summer house holding passive warmth reads its hot-water saving, not a loss`.
  - `floorlate` (no demand floor, `np.maximum(baseline_power, 0.0)` at the return): KILLED by `a thermostat's end state is the house its booked power heats: a replay of the kW lands on it, warm day and swinging day`. The gaps are room/slab 3.473/6.074 C on the warm day and 0.294/0.516 C on the swinging day, the body's figures exactly. The head passes this check with gap 0.
  - `floorpower` (no demand floor, the floor put on the booked step `baseline_power[i] = max(0.0, power)` while the negative power is still simulated): KILLED by the replay check and by `two-zone: a valved reference costs the unvalved one plus the tank's loss`.
  - `migguard` (the `"savings_baseline" in lines` condition dropped from `migrate_ledger_v1`): KILLED by `a v1 month with no savings booked at the upgrade books its first saving on the new reference`.
  - No mutant of mine survived.
- RESULT P3: at the head, in the suite, `RESULT f21_p3_two_zone=1 j_plain=107.039134 j_continuation_off=107.903727 continuation_gain=+0.864593`. This equals the body under Haswell.
  - The body's other kernel classes (Sandybridge, Prescott, SkylakeX) were not re-derived on this host. CI's `tests / fast` on the head is the SkylakeX-class evidence.
  - 539995fa5 moves the pin's tank start from 30 to 35 C and keeps its claim, a strictly positive gain. The comment states why. No golden fixture is touched.
- RESULT figures (`dev/audit/harnesses/r10_sav_wood_reference.py`, the fixer's harness, sha1 0f98bbb397a62d65a07448e934e0e100e49359da, at the head; ev/wood_reference_head.log):
  - `first: SOUND`
  - `valve-flat: SOUND`, pct +4.18, residual -3.90 %
  - `valve-vary: SOUND`, pct +28.50, residual -8.02 %
  - wood-cold: pct 7.47, plan 66.89, residual -3.22 %
  - wood-full: pct 87.88, plan 8.76, residual +88.64 %
  - wood-unforeseen: pct 49.10, plan 40.63, calibration 1.0
  - Each equals the body.
  - wood-stale, wood-coast and wood-fire were not re-run, so their body figures are quoted, not verified.
  - The three-row calibration check (50 / 75 / 87.5 % with wood, 50 / 50 / 50 % without) was not re-derived as numbers here. Its mechanism is pinned by the calibration checks, which pass at the head, and round 1's reviewer killed its floor mutant.
- RESULT structure: `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED` (ev/structure_head.log). The only budget move in the three-dot diff is `class_excess_loc` 17618 -> 17590, downward, plus `recorded_at`. No raise.
- RESULT merge: `git merge-tree --write-tree origin/main 1d114ed62` against origin/main 6777ec333 exits 0 with tree 3ecb430eaac77c02e38ce39dce227eac047bfe0e. There is no conflict and no claim-driver marker, so #3195's overlap does not conflict at this main.
- RESULT version: the three-dot diff touches none of `VERSION`, `manifest.json` or `RELEASE_NOTES.md`. `VERSION` is 7.1.1, and `claims-for: 7.1.1` in both claim files.
- RESULT claims:
  - The three-dot diff changes `tests/golden/claimed_drift.txt` only. It adds 9 R10-HOTFIX-SAV-ESTIMATE claims (the valve_storage family, valve_upper_direct_slab, wood_coil, wood_two_tank and its smart_write) and suspends their may-drift lines as comments. So no fixture is both claimed and may-drift.
  - `card_claimed_drift.txt` is unchanged.
  - This round's commits touch no `tests/golden/` file.
  - `env_drift.py --all` was not re-run by me. The fixer's gate at 893f4940d reads `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE`, and CI's gate at the head decides.
- RESULT migration (bf628b2ec): every writer of `savings_baseline` is `add_savings_settlement` (ledger.py:296-306), which stamps a month's REFERENCE_BASIS on its first savings booking (ledger.py:292-293). `savings_months` skips a month with no `savings_baseline` (ledger.py:443). So stamping only months that hold `savings_baseline` loses no old-basis month. A month booked on v1 keeps the dash, and its totals are not rewritten.
- RESULT owner's rulings (judged on the diff and the passing pins, not re-litigated from round 1):
  - The no-wood reference is checked in the space and the hot-water reference (`the reference has no wood ...`, `the reference's hot water has no refill coil ...`).
  - The disclaimer has no firewood line.
  - The old-basis dash is pinned (`a v1 ledger migrates to v2 ...`, and the new unbooked-month check).
  - The option-A calibration floor applies only when wood is configured (`if wood_configured and calibration is not None`, pinned by the mutation-ledger records).
  - The percent is unclipped (`savings_pct` returns the raw ratio).
  - Positive rows on the wood arms are wood's heat under the owner's no-wood-reference ruling, not a defect. Actuals stay metered.
- RESULT scope note: the replay check runs an unvalved house. Behind a valve, `_apportion_by_steady_demand` respreads the booked kW by design, so a replay could not land there. On the valved path, the floor's place is held by `two-zone: a valved reference costs the unvalved one plus the tank's loss`, which killed `floorpower`. This is a limit of the pin's domain, not a gap.
- RESULT head: the PR body's `## Head` names 1d114ed62a582faeb04211104ebb118ec30bd6c9, the head I measured.
- RESULT forward-carry: on `origin/handoff/audit-r10-roster` (cfe7c09), R10-SAV-COMFORT's carry holds the body's two items "From PR 3220": the residual -3.90 % / -8.02 %, and `_apportion_by_steady_demand` with no pump cap, 4.98 of 6.0 kW. R10-FLY-REPLAY-MASK holds the empty-replay item 31ee5e06. `carry_audit` at the head: 3 routed, 0 unrouted.
- RESULT CI at 1d114ed62: `merge_train.py classify 1d114ed62... --pr 3220` exited 1, `RED ... pending: none red: gate`.
  - The run at this head, 41979321879 (CI code, merge ref 196a0f5b), was cancelled at 08:28 UTC. That happened when the orchestrator pushed 6f8dfe831, a merge of origin/main 79f765e6b with no branch-only non-merge commit; `review_carry.py 1d114ed62 6f8dfe831` prints CARRY. So `gate` and `mutation-autofix` were cancelled, `mutation-pins (3)` was cancelled, and `pr-contract` was skipped. CI on this head never concluded, and it cannot now.
  - Jobs at this head (ev/ci_jobs_1d114ed6_run41979321879.txt):
    - Success: `tests / typing` (the round-1 block, now green), `tests / fast (3.14)` (the SkylakeX-class runner that was red in round 1, now green), coverage, browser, closures, arch-instrument, lane-proofs, graders-head-copy, coverage-ratchet, mutation-pins 1, 2 and 4, arch-score, budget-raise-gate, policy-docs, instrument-self-tests and env-matrix.
    - `tests / mutation`: red with `MUTATION TABLE REFUSED -- 3111 unpinned site(s) against 3097 ... 16 of them added by this diff`. These are exactly the 16 sites in the body's `## Unpinned sites`, which `mutation-autofix` pins (`ci-autofix.md`). The body names this red, and the pin lane was cancelled before it ran.
    - `tests / replay`: red, `4 of 186 replay checks FAILED`. All four are `synthetic-dhw-only.json: cycle_cost` and its three doubled arms, `runner class unknown: ref_ms 37.8 lies in no band of COST_RUNNER_CLASSES`. The body answers the same red at c3992a14 (ref_ms 22) as a runner the class table does not cover. This diff touches neither the table nor the reference benchmark. Every other replay invariant passes.
    - `governance / delivery-status` and `tests / nightly-status`: red, and named in the body as inherited.
  - Under step 11, the `pr-contract` run that checks the body after the last red never started on this head. So I have not verified that the reds are answered by the pr-contract run; I verified it only from the body text.
  - The move to 6f8dfe831, checked under steps 12 and 13: `git merge-tree --write-tree 79f765e6b 1d114ed62` exits 0. The claim and ledger drivers print `LEDGER-MERGE: resolved tests/structure_budgets.json` (class_excess_loc 17618 + both deltas = 17589) and `LEDGER-MERGE: resolved tests/closures.json`. They print no `refused` marker. The resulting tree a82ee2b40 is identical to 6f8dfe831's tree (`git diff --stat` empty; ev/mergetree_79f765e.txt). So the move adds no resolution of its own, and the reviewed patch is unchanged.
  - This `merge` verdict asserts the patch reviewed at 1d114ed62. It does not assert a green CI there. A red CI never carries, so the train must see a concluded green at the carry target 6f8dfe831 (run 41994531832, in progress when this verdict was written).

- RESULT self-audit: `carry_audit.py check` was run with this verdict as the comment, and the body side was taken from the packet's own run at the head (3 routed, 0 unrouted). It printed `CARRY-AUDIT: 0 finding item(s)`, rc 0.

## Findings

none

## Friction

- The frugal-routing hook capped inline read-only searches at 5 per prompt. I delegated two locate batches to a scout instead of overriding it. No result depended on the scout's judgement, and every figure above is from my own runs.
- The CI waiter was stopped once by the 30-minute background limit and was re-armed.
