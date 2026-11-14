Fix review: merge 49afbe9d01564791ae2d37104c03287a4407c954

bus-nonce: bc8c9fdcc1b3db8b073e2aae00d2600a
pending-ci: gate, tests / fast (3.14), tests / coverage, tests / closures, tests / replay, tests / browser, tests / mutation-pins (1), tests / mutation-pins (2), tests / mutation-pins (3), tests / mutation-pins (4), governance / instrument-self-tests

## Scope

Round 2. A delta review from the posted merge verdict at 29370fdbb59aeb18da82ebe9612e7c036e9dc29c, which listed no findings, so none is owed a resolution. `review_carry.py 29370fdb 49afbe9d` prints FRESH-REVIEW (ev/checks.txt). This round covers the four fixer commits bb95b53b50, 8bce59d55b, 2d024b4d16 and b142bcaace, and the resolution in the merge ff45fd27c7 of #3561's head. That merge is the only one in the range whose remerge-diff is not empty: it resolves conflicts in coordinator.py and pump_arbiter.py, and adds `_leg_rule` to optimizer.py (ev/remerge-ff45fd27c7.diff). The merges d07194dd95, 673904aed4 and 49afbe9d01 have no hand resolution; d07194dd95's only change is the closures.json ledger merge-driver union. Following brief (c), the production review is widened to the PR's own custom_components/ diff. That diff is measured against main merged with 30b06950, so it holds this PR's production lines and not #3561's (ev/own-prod.diff). It is compared against the reviewed head's own diff in ev/interdiff.txt.

**Stacking: #3532 lands only after #3561.** 30b069508f194240f90ddd05cb5cfee0613814e1 is an ancestor of #3561's live head ebc8483673e3581e3c06786f689ffc95ed8e366a and of this head. This branch merges it as the same commit object (ff45fd27c7's second parent), so its content is #3561's byte for byte (ev/stack-3561.txt).

## Evidence

- Head: 49afbe9d01564791ae2d37104c03287a4407c954. It is the PR's head at render time and was re-read with `ls-remote refs/pull/3532/head` just before posting (ev/HEAD.txt). The body's `## Head` names the same SHA.
- Merge with main: `git merge-tree --write-tree origin/main 49afbe9d` exits 0, tree 1db224b5fd (ev/checks.txt). The head already contains origin/main 0f37833e21.
- Policy and version files. `dev/governance/roles/` has not changed on main since the merge base (empty diff). VERSION, the manifest and the RELEASE_NOTES heading are untouched (three-dot). Neither claim file is touched, which matches the body's statement that no golden fixture moves.
- Resolution read against both parents. pump_arbiter `_share` keeps #3561's `_lead_mode`/`_step_duty`/`_served` and drops the local `from .duty_legs import both_step_legs`. It delegates to `duty_switch.both_step_duty(rec, start, now, space_kw, dhw_kw, PLAN_STEP_MINUTES, next step's duty)`. coordinator's import line is the union (`supply_hold` from #3561 beside `duty_switch`). The step width now comes from the arbiter (bb95b53b50) and is no longer hard-coded.
- Production read (widened). `DutySwitchLearner.split()` is `duty_legs.leg_rule(*planner_pairs())`, and `planner_fields` hands the solve the same pairs, so the arbiter and the planner read one rule. Its semantics are unchanged from the reviewed `split`:
  - A usable direction has p >= P_OFF > 0, so `p > 0` is equivalent to the old `usable` set.
  - The off time is the median, or 0.
  - The minimum share is SPLIT_MIN_MINUTES.
  - In `leg_ends`, the whole-step branch reads the next step's second circuit from the plan. That matches the arbiter's `next_duty in (second, "both")`.
  - `availability` charges a two-leg step only when hot water leads, which is correct: under space first the inside switch is space to hot water.
  - `switch_ban` under space first bans only the step before heating.
  - The inside weight uses p_sd under space first.
  - In `Direction.book`, `scale = min(1.0, N_CAP / self.n)` follows a +1 booking, so n >= 1 and it cannot divide by zero.
- Delta mutation proof, by this reviewer. Each mutant was applied alone to a copy of the head and the full `PYTHONPATH=tests/hastub python3 tests/features.py` was run (ev/mutants.txt, ev/mutant-results.txt, ev/mutant-maker.sh). All 13 are killed:

  | Mutant | Change | rc | FAILs |
  |---|---|---|---|
  | M1 | `leg_rule` first is always dhw | 1 | 7 |
  | M2 | `into` is always 0 | 1 | 3 |
  | M3 | whole-step merge in `both_step_legs` disabled | 1 | 8 |
  | M4 | `whole` never set in `leg_ends` | 1 | 2 |
  | M5 | inside weight always p_ds | 1 | 3 |
  | M6 | `availability` charges every two-leg step | 1 | 5 |
  | M7 | `switch_ban` ignores the rule | 1 | 3 |
  | M8 | `both_step_duty` uses DEFAULT_RULE instead of `learner.split()` | 1 | 9 |
  | M9 | `next_duty=None` | 1 | 7 |
  | M10 | the latch is decided on every read | 1 | 3 |
  | M11 | optimizer's ban call without the rule | 1 | 3 |
  | M12 | optimizer's availability call without the rule | 1 | 4 |
  | M13 | optimizer's switch-cost call without the rule | 1 | 1 |

  Unmutated, the head gives rc=0 with 0 FAIL lines (ev/features-head.log). The decay and booking CLAMP_DROP, decay CMP_BOUND and both `both_step_duty` GUARD_OFF sites are pinned killed in the head's mutation ledger by `mutation_table.py --pin-killed` (review packet ledger diff).
- Finder's harness: the review packet names none, and this is a fix-protocol feature group under the approved design note. The body's section harnesses were not re-run separately: the full features.py run above includes their sections.
- Figures. `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` is not re-derived by this reviewer (figure_lint: unverified). The arch-score `dS +0.0000 NULL` is not re-derived either; the CI `arch-score / arch-score` check is green at this head.
- Red checks. Live check runs were read through get_check_runs at about 04:45Z.
  - `tests / mutation` is red, and it is in the `owed-reds` set. The body answers it under `## Red checks`: these are new killed sites that are not yet pinned, and `mutation-autofix` pins them (`ci-autofix.md`). The lane log shows `count=4 shards=[1, 2, 3, 4]`, and the four `mutation-pins` jobs are queued or running. My 13 mutants are all killed, which is consistent with the red being "unpinned killed", not survivors.
  - `tests / nightly-status` is red. It is outside the owed set and grades main, so it is not this PR's.
  - `gate` (run 43554607758) is red as the aggregate. A newer `gate` run is queued.
  - The body's predicted `tests / fast (3.14)` red, main's charge-start clock check, does not reproduce at this head: features.py rc=0 locally. main's #3578 ("Pin the charge-start block's clock to a fixed Monday") is in the head. The CI run is still in progress.
  - `tests / typing`, `validate / validate-hacs`, `arch-score` and `budget-raise-gate` are green.
- CI wait. `merge_train.py classify 49afbe9d --pr 3532` printed `WAIT 49afbe9d01564791ae2d37104c03287a4407c954 pending: gate red: none` (rc 3) on every poll from about 04:08Z to 04:52Z (ev/classify.log). It names no pending context, so the `pending-ci:` line above lists the incomplete contexts read from the live check runs.
- The PR body's `## Head` SHA matches the measured head.

## Findings

- The PR body contains a splice. Right after `## Unpinned sites`' survivors list, a stray `## Red checks`).` line is followed by a second copy of `## Mutation proof`, `## Null control`, `## Figures` and an older `## Unpinned sites`. That copy names stale reviewed-head lines (duty_switch.py:193, 223, 403, 406, 551-558, which no longer hold those sites), and it appears before the real `## Red checks`. Carry: dismissed: body-text duplication with no code or ledger effect; the first copy of each section is current at this head, and the stale line numbers are superseded by the ledger pins mutation-autofix records.

## Friction

none
