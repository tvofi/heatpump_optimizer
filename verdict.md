Fix review: blocked 2d58f010bcc3393898a2f66680cf20e4d9cb048d swap-void-undone: a zone-sensor swap in the same options change as a nameplate edit past the gate writes the pre-void ratio back over the void

bus-nonce: e7260a7675a71353994b5cb2df629c2f

## Round

Round 1. Reviewed at head 2d58f010bcc3393898a2f66680cf20e4d9cb048d. The authored code is 18a66328950debff47f245bc25d8cd2af4bfdd73, merged with origin/main 5d4e0bcf by 8d8570f40. The merge base is now 5d4e0bcfb88413ddf9ca7f0884c36bbec9235447; the brief's cc930cdd is the pre-merge base. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Block

`_reanchor_house_heat_loss_scale` (coordinator.py, around lines 5241-5285) reads `live, ratio = self._heat_loss_anchors(), self._lower_floor_loss_ratio` before it calls `_void_heat_loss_learners(heat_loss_entity_voids(stored, live), ...)`. When the same load also crosses the nameplate gate (`heat_loss_anchor_pair` is not None), `reanchor_heat_loss` receives the stale pre-void `ratio`. Its `l_now <= 0` branch, which the pair takes on a total-only edit, then hands that ratio back unchanged, and `self._apply_lower_floor_loss_ratio(new_ratio)` overwrites the void. The live house anchor fed to the pair is also computed with the pre-void ratio.

Measured through the production coordinator: the owner's nameplates, a store written with indoor=sensor.t6, lower=sensor.floor_old, 1.2356/1.943, n=400, reloaded with upper 0.13->0.2 and lower 0.2->0.3 in the same change as the swap (ev/attack_head.txt, ev/attack_mechanism.txt):

- lower swap + edit: scale 0.8185, **ratio 1.9430, n_ratio 0**. The swap's void is gone, and the stale ratio now has zero confidence.
- both sensors swapped + edit (the finder's move together with a nameplate correction, which is the owner's actual history): scale 1.0, **ratio 1.9430, n=(0,0)**.
- control, the same two changes in two loads (swap, then edit): ratio 1.0000, n_ratio 0, which is correct. The result is path-dependent.
- mechanism trace: `heat_loss_anchor_pair(...) -> ((0.5186, 0.0), (0.7829, 0.0))` (lower 0, so the ratio is passed through), `reanchor_heat_loss(..., 1.2356, 1.943, (0.9997, 0.0)) -> (0.8185, 1.943, ...)`.

The PR claims "A changed id voids that learner alone ... Voiding sets the value to 1.0", and that is false on this configuration, which the harness's input domain accepts (fix-review.md step 6). A likely repair: void before reading `ratio` and the live anchors, plus a test with a swap and an above-gate nameplate edit in one load. The same path serves snapshot restore (`_apply_learner_payloads`).

## Findings

- The swap void is undone when the same options change carries a nameplate edit past `HOUSE_LOSS_MAX_STEP` (## Block). Carry: R10-HOTFIX-LEARNER-INPUTS
- Surviving reviewer mutant M8: `if key in was and (was[key] or None) != now.get(key)` -> `if (was.get(key) or None) != now.get(key)` passes all 1036 checks of the cut run. The docstring's "a key it does not hold, voids nothing" branch is unpinned. Every save writes both keys, so only a hand-edited or partial store reaches it. Carry: dismissed: unreachable from any store the integration writes; pin it with the round-2 repair if cheap
- The new section alone does not kill the button's await mutant (M10, `off_the_action(...)` -> `await ...`); only the RC2 row in the full `tests/features.py` does. That is the designed pin, so it is not a gap. Carry: dismissed: the RC2 row is the intended detector and it fails as required
- review_packet refuses `red-unanswered: tests / mutation`, but the body does answer `mutation` under `## Red checks` ("red by construction on the 7 sites"). This is a name-matching mismatch between the packet's `tests / mutation` and the body's `mutation`, so the fixer should name the check exactly as CI does in round 2. Carry: R10-HOTFIX-LEARNER-INPUTS

- CI at this head went red on `tests / fast (3.14)`, which printed `1 TEST SCRIPT(S) FAILED`; the API log tail did not name the script, and it was not reproduced here. The body says "No CI check has run" and answers only `mutation` and `arch-score`. `tests / mutation-autofix`, `pr-contract` and `gate` are also red. The round-2 body owes each red check its answer (fix-review step 11), which is not judged here because the head is blocked on the defect. Carry: R10-HOTFIX-LEARNER-INPUTS

## Evidence

- Finder's harness (handoff-body/r10-live-plan-energy 7c4e639e, probe.py, the owner's two-zone nameplates and SE3 prices), driven through my own swap driver over the production coordinator (ev/scripts/swap_energy.py; the driver is mine, disclosed per step 9). ev/swap_energy_base_head.txt:
  - RESULT base 5d4e0bcf, finder swap indoor=bthome, lower=t6: scale 1.2356 ratio 1.9430 n=(400,400) plan 51.67 kWh UA 0.641. This reproduces the finder's arm 1.
  - RESULT head, finder swap: scale 1.0 ratio 1.0 n=(0,0) saves=1 plan 24.00 kWh UA 0.330. This equals the finder's arm 4.
  - RESULT head, indoor only: (1.0, 1.943, 0, 400), plan 40.78 kWh. Lower only: (1.2356, 1.0, 400, 0), plan 30.72 kWh. Lower sensor removed: voids the ratio.
  - RESULT head, null controls (outdoor sensor, comfort_weight): (1.2356, 1.943, 400, 400), saves=0, 51.67 kWh. These match base, and nothing is written.
- (b) Migration (ev/attack_head.txt): a legacy store with no record keeps both learners on first load, saves once and adopts `{'indoor_temp_entity': 'sensor.t6', 'lower_floor_temp_entity': 'sensor.floor_old'}`. A later lower swap then voids the ratio (1.2356, 1.0, 400, 0), and a reload voids nothing more with 0 saves. The swap rule stays live after migration. The legacy-store arms of the swap driver show no void on first load at the head, as the body states.
- (c) The reset `async_reset_heat_loss_learners()` gives (1.0, 1.0, 0, 0) with 1 save, and the finder's solve on the result is 24.00 kWh. The button and the service both call the one void path; diff read. The comfort, COP, DHW and defrost learners are untouched per the PR's `_li_others` check, which passes on the cut run baseline (1036/1036).
- (d) The structure, VERSION, manifest, RELEASE_NOTES, structure_budgets and both claim files are untouched in the three-dot diff (ev/untouched.txt). I read the dedup of the re-anchor prose: #86 and #2239 and the law still stand in the docstring. Lost are the history-only pointers ("v5.7.0", "four prior attempts recorded in dev/archive/backlog.md", "Round 1"). I judge no operative information lost. coord_footprint 2381->2387 is not re-derived here; the body's argument (the learner state is coordinator attributes, and the pure rule is in thermal_model) is honest, and the sounder seam, a learner object, is R10-ARCH's.
- (e) Mutation, cut tests/features.py run before "Runtime parameter updates", by my delegated worker (ev/mutants/). The kills were M1 swap gate -> `if False`: 4 FAIL. M2 drop `_lower_floor_loss_samples = 0`: 8 FAIL. M3 drop the scale reset: 5 FAIL. M4 `return swapped` -> `return False`: 2 FAIL. M5 drop the reset save: 1 FAIL. M6 drop the record from `_heat_loss_anchors`: 7 FAIL. M9 drop the record from `_HEAT_LOSS_ANCHOR_KEYS`: 1 FAIL. M10 button awaits: killed by the RC2 row in the full run. M7 (`was[key]` without `or None`) survives and is equivalent on written stores. M8 survives (## Findings).
- (f) The forward-carry reads back on origin/handoff/audit-r10-roster at 1b03aeccf31a32d28961e3a087160eeb47d10c35, in R10-FACTORY-RESET carry[0]. It names `async_reset_heat_loss_learners`, `_void_heat_loss_learners` and `const.HEAT_LOSS_LEARNERS`, and states the precondition "Any snapshot taken before the reset must be taken before this call". 1b03aecc is an ancestor of the roster branch. Both dismissals carry reasons (carry_audit: 3 routed, 0 unrouted).
- `git merge-tree --write-tree origin/main 2d58f010` (origin/main 18b788ac) exits 0, with the ledger driver merging the closure sets (ev/merge_tree.txt).
- The figures I could not re-derive are coord_footprint 2381->2387, the body's 21-line class payment, and the local gate counts. CI's heavy runs are cited, not re-run.
- CI: `merge_train.py classify 2d58f010...` exited 1: `RED 2d58f010bcc3393898a2f66680cf20e4d9cb048d pending: none red: gate` (ev/classify.txt, ev/classify.log). The check runs at the head, read live: `tests / fast (3.14)` failure (job 124391176216); `tests / mutation` failure; `tests / mutation-autofix` failure; `pr-contract / pr-contract` failure (its carry_audit step prints `3 routed, 0 unrouted`); `gate` failure. Green: closures, coverage, arch-instrument, replay, typing, browser, nightly-ha x2, mutation-pins x2, arch-score, budget-raise-gate, hassfest, validate-hacs, codeql x3, and the governance jobs.
- The head was re-read at post time: origin/fix/r10-hotfix-learner-inputs = 2d58f010bcc3393898a2f66680cf20e4d9cb048d (ev/head_at_post.txt).
