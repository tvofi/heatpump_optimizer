Fix review: blocked ff6cfdaabc39647855987ae54fed4a3449eb2c47 mutation-vacuous: restore's async_request_refresh reverted to async_update_listeners, and _insight_view handing _scores_view an empty advice, both survive features, entities and finite_boundary

bus-nonce: c6edd5b09341e954f6a0552c0ad06492

PR #2647, group R10-SCORES, fix round 2 (the round-2 fixer on the approved design `design/r10-scores`, `Design review: approve f01e06d24`). This is not the fourth round, so a repair is owed, not a re-cut. I found no round-1 fix verdict for this group on any `probe/rev-*`, `review/*` or `verdict/*` ref, and #2647 has no comments. I read the design verdict (`design-verdict/r10-scores` `7a09f4641`, round 3, approve).

Measured head: `ff6cfdaabc39647855987ae54fed4a3449eb2c47` (`ev/HEAD.txt`), from detached worktrees at that SHA. It was still the PR head at 05:40Z, re-read just before writing this verdict. The code head is `19319cc13`; `ff6cfdaab` adds only `dev/programme/delivery/2647.md`.

- Merge base: `f38f91852`.
- `fix-review.md` is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, at main `a7cf60cfd` and again at `c26499e01`.
- Toolchain: `/opt/hpo/venv-ci/bin/python` (3.14.7), node 22.

## Block

1. **mutation-vacuous (step 1).** I ran two production mutants of lines the body names over the whole Python closure that could kill them: `tests/features.py`, `tests/entities.py` and `tests/finite_boundary.py`. Both survive all three.
   - **R7.** In `async_restore_learned_snapshot`, `await self.async_request_refresh()` becomes `self.async_update_listeners()` (coordinator.py:9525). This is the base behaviour.
     - Result: `ALL 4328 FEATURE CHECKS PASSED`, `ALL 2406 ENTITY CHECKS PASSED`, `ALL 106 FINITE BOUNDARY CHECKS PASSED`.
     - The body's item 3 says "The adopt and restore services now `async_request_refresh()`". The design verdict made both paths a test arm ("Both must refresh … That is a test arm").
     - M11 pins only the adopt path. The restore checks at features.py:17929-17943 assert only the return value, and entities.py:14816 replaces the method with a stub.
     - The ledger cannot see this line: an awaited expression statement draws no generated site. That is why `## Unpinned sites: none` and `ci_predict` are silent. Evidence: `ev/mut-R7_restore_listeners.diff` and `.log`, `ev/c2-R7_restore_listeners-*.log`.
     - Fix wanted: a restore arm like M11's check. After a restore, the cycle that follows re-takes the advice: no refit is offered for the restored scale, and the grade reads the restored scale.
   - **R13.** In `_insight_view`, `"scores": self._scores_view(advice)` becomes `self._scores_view({})` (coordinator.py:10575).
     - Result: `ALL 4328 FEATURE CHECKS PASSED`, `ALL 2406 ENTITY CHECKS PASSED`, `ALL 106 FINITE BOUNDARY CHECKS PASSED`.
     - This is item 3's own claim: "the envelope grade reads the same take" as the advisor. Under R13 the advisor sensor offers a refit while the house grade stays graded, the contradiction item 3 forbids.
     - Every `heat_loss_refit_disagrees` check calls `envelope_score` or `_scores_view(advice)` with a hand-built advice. No check reaches the cycle path, where `insight.model_restart` and `insight.scores` come from one `_insight_view()`.
     - Evidence: `ev/mut-R13_scores_fresh_advice.diff` and `.log`, `ev/c2-R13_scores_fresh_advice-*.log`.
     - Fix wanted: one `_insight_view()` on a coordinator whose refit sits outside its band. Assert that `model_restart.refit` is offered and that `scores.reasons.envelope == "heat_loss_refit_disagrees"`.

2. **carry-missing (step 10): not carried to R10-LEARNER-ETA, R10-UX-HEALTH and R10-ARCH-DOCS.**
   - Three `## Forward-carry` items name no landed SHA. At `origin/handoff/audit-r10-roster` `8de7e22ac` their text is in neither those groups' `carry[]` nor their `brief`:
     - **R10-LEARNER-ETA**: "must read `house_loss_converged`, never a second threshold". This narrows what that stage may do.
     - **R10-UX-HEALTH**, first bullet: the score sensor is `unknown` with `reasons`, and Health's "learned" now means 50 samples. This invalidates an assumption the stage rests on.
     - **R10-ARCH-DOCS**: the `[target: R10-SCORES]` line, with what landed and what did not.
   - All three groups are `not-started`.
   - Only the two "New finding" items (`9a4953627`, `75c891e28`) and the bundle blocker (`c3711a1f0`) are on the roster. Each of those is an ancestor of the branch tip, and I read each one back.
   - `carry_audit.py check --body` reads `7 routed, 0 unrouted` (`ev/carry_audit.txt`). It checks that the marker exists, not that the carry landed, so `pr-contract` green does not settle this. `finding-propagation.md`: "The producing PR does not merge until the carry is in the tree."
   - Fix wanted: land the three carries with their controls, and name the roster SHA in the body.

## Findings

- **Non-blocking (step 2/9, the harness).**
  - The design names the finder's harness for item 2: `dev/audit/rounds/round10/study-reseed/live_store.py --ratio-override 1.0`. It needs the owner's bundle, which this container does not have. It reads the seams `_space_demand_kw` and `adoption_decision`, never the envelope grade, so it cannot measure this fix at either end.
  - `dev/audit/harnesses/r10_scores_envelope.py` is the fixer's own instrument. Its header says so ("This harness drives …"), but the body presents it as "Item 2's harness" without the words "this PR's instrument, not the finder's".
  - I ran it at both ends, and I built my own probe (`ev/probe_env.py`). It calls `envelope_score` directly against RATIO-SITES' formula, tau = mass / ((U + L·r)·s).
  - Both agree with the body (Evidence). The bundle-dependent arms stay carried to R10-PARAMS-OWNER (`c3711a1f0`). Carry: dismissed: the fixer's instrument is in the tree with its own header, and the finder's harness needs the bundle R10-PARAMS-OWNER holds
- **Non-blocking (step 11).** `tests/entities.py` at the head reads `ALL 2406 ENTITY CHECKS PASSED` here (`ev/c2-head-entities.log`). The body says `4 of 2402 ENTITY CHECKS FAILED` for the `hb:positive_control` py-spy retry arm, on its own machine. The arm depends on the environment, and CI `fast` was still running when I read it, so `fast` decides this one. Carry: dismissed: environment-dependent heartbeat arm, CI fast is the arbiter

## Brief items

- **(a) Owner items 1-3 and C3: answered.**
  - Item 1: `readNumber` is byte-identical to C3's patch at `3930b421a`. The sub-scores read through it in `scoreParts`. The headline reads through `statNumber`, which handles `unknown` and `unavailable`, and its state is a string, never `null`. The two `finiteScore` sites are gone.
  - Item 2: the loss is `_effective_house_heat_loss`, with the convergence dash and the refit dash.
  - Item 3: one advice per cycle, `insight.model_restart`. There is a card census over every score input, and a backend sweep `learned == house_loss_converged(samples)`, as the design review's carry asked.
  - The `Number(attrs.*)` census re-derives as the body says: 4 sites at the head outside scores, all in the Advisor rows and carried. The grep also matches the `readNumber(attrs[key])` line itself, which is benign.
  - Item 3 is **not pinned** at the two wiring points in Block 1.
- **(b) The six ledger score sites (`a9099faf3`): each mutated back, each red** (`ev/mutants.txt`):

  | site | mutant | result |
  |---|---|---|
  | `_watched_cop_buckets` CMP_BOUND 5235f6e3 | `>=` -> `>` | 1 of 4328 failed: `a COP bucket at exactly the minimum sample count is watched…` |
  | `_refit_disagrees` CMP_BOUND fcdeb271 | `>` -> `>=` | 1 failed |
  | `envelope_score` CMP_BOUND 88c2835d, loss site | `<= 0.0` -> `< 0.0` | ZeroDivisionError |
  | `envelope_score` CMP_BOUND 88c2835d, mass site | `<= 0` -> `< 0` | 1 failed |
  | `envelope_score` GUARD_OFF 88c2835d | guard -> `if False:` | ZeroDivisionError |
  | `machine_score` CLAMP_DROP 4fe0081d | clip dropped | 1 failed |

  My own mutants are all red too, except R7 and R13:

  | mutant | change | result |
  |---|---|---|
  | R1 | M2's configured loss | 1 failed: the two-zone check |
  | R2 | M9 | 2 failed |
  | R3 | M7's precedence swap | 1 failed |
  | R4 | band measured on the fitted scale | 1 failed |
  | R5 | a reason for every grade | 4 failed |
  | R6 | M11 | 1 failed |
  | R8 | operation reason constant | 1 failed |
  | R9 | convergence at half a time constant | 2 failed |
  | R10 | M6 | ValueError |
  | R11 | sensor pre-cycle fallback scale -> None | 1 failed |
  | R12 | a missing refit disagrees | TypeError |
  | C1 | M1 (card) | 8 CARD CHECK(S) FAILED |
  | C2 | M12 (card) | 1 failed |
  | C3 | generic reason text | 8 failed |

- **(c) "Part of #2238 and part of #2258": right.**
  - The roster's `fixes` is `[]` for R10-SCORES.
  - The body and all 17 commit messages hold no closing keyword (`close|fix|resolve #N`).
  - Both issues are open, with `closed_by_pull_requests: 0`.
  - #2258's bundle arms are carried to R10-PARAMS-OWNER, so #2258 must stay open.
- **(d) `## Red checks`.**
  - The reds on the head are `budget-raise-gate` ×2 and `nightly-status`. `budget-raise-gate` is answered. `nightly-status` grades main, and the diff touches nothing it reads.
  - `mutation` and `fast` were still running when I read CI (~05:15Z). The body pre-answers both: mutation at `04ab79356`, and entities' heartbeat arm.
  - The second `pr-contract` run, started 04:36:08Z, began after the last red to conclude (`budget-raise-gate` at 04:35:49Z) and is green.
  - My block does not rest on CI (`ev/checks.txt`).
- **(e) The raise.**
  - `seam_cut_total` 708 -> 714 reproduces: main learning 281, grid 158, views 106; head 283, 159, 109 (`ev/structure-*.log`).
  - archscore `--diff origin/main` reproduces `dS +0.0105 IMPROVES`, `coord_footprint 2489 -> 2471` (`ev/archscore.log`).
  - The four payments taken are sound:
    - envelope out of the class;
    - `restart_advice` made pure;
    - `async_request_refresh` over an in-place write;
    - the pure composition functions.
  - Each moves code to pure module functions or reuses an existing mechanism, and none games the instrument.
  - The `class_excess_loc` and `max_class_loc` falls are real: 18244 and 8480 at the head.
  - Untried payments: I hunted one. The advice could be taken in the learning seam (`_async_watch_learning_drift`), stored, and read once from views. That needs a new coordinator attribute, and `coordinator_attrs` sits at 147 of 147 with zero headroom, so it trades one raise for another and is not a free payment.
  - Re-seating (5) and the dict-smuggling of (7) were correctly refused as moving the charge.
  - I found no untried payment that improves the code.

## Evidence

- RESULT head `tests/features.py`: `ALL 4328 FEATURE CHECKS PASSED`, rc 0. That is 4325 plus the three new checks (`ev/features-head.log`).
- RESULT head `node tests/card.mjs`, after `tests/plan_view.py`: `ALL CARD CHECKS PASSED`, rc 0 (`ev/card-head.log`).
- RESULT head `tests/entities.py`: `ALL 2406 ENTITY CHECKS PASSED`. `tests/finite_boundary.py`: `ALL 106 FINITE BOUNDARY CHECKS PASSED` (`ev/closure2.txt`).
- RESULT fixer harness `r10_scores_envelope.py`, sha1 `272d5175…`:
  - head: `split_max_abs_gap=0.0`; ends arm at 0 samples `None heat_loss_learning`; at 2000 samples 79.2 / 0.0 (`ev/harness-head.log`);
  - origin/main, production identical to the merge base: `split_max_abs_gap=10.5` (split 0.5, scale 1.0: 6.2 against 16.7); ends arm at 0 samples 79.2 / 0.0;
  - `--ratio-override 1.0` at the base: `0.0` (`ev/harness-base*.log`).
  - These match the body.
- RESULT my probe at the head (`ev/probe-env-head.log`):
  - `probe_max_gap=0.00e+00` over 40 cells (single- and two-zone, r ∈ {0.5, 0.8, 1, 1.25, 2}, s ∈ {0.3, 1, 2.6, 3});
  - 49 samples gives `(None, heat_loss_learning)`, 50 samples a grade;
  - refit edge at scale 2.0, band 25 %: 2.5 / 2.51 / 1.5 / 1.49 give False / True / False / True.
- RESULT `tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- RESULT step 13: `git merge-tree --write-tree` against origin/main `a7cf60cfd` and `c26499e01` exits 0 both times, with no conflict and no claim driver invoked (`ev/merge_tree.txt`).
- RESULT steps 4-5: `VERSION` 7.0.4, the manifest and `RELEASE_NOTES.md` are untouched. Both `claims-for:` lines read 7.0.4. The claimed set is exactly the five `coord_*` fixtures plus card `score_open`, matching the body. I did not re-run `env_drift --all` or `card_drift` myself; CI `fast` carries them.
- RESULT step 6: the body's two census rules re-derive.
  - Card: 4 `Number(attrs.*)` sites at the head, 4 plus 3 `finiteScore` at the base.
  - UA grep: the envelope site is gone.
  - The remaining hits are split-aware (`_space_demand_kw`, optimizer.py:2197, thermal_model.py:2283), single-zone branches, the lower-floor learner's own base, or tanks.
