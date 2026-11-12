R10-DUTY-SWITCH-RESTART-LEARNING-PR-B, first pull request: the carries part A (#3461) left to the part that first reads its estimate. With thanks to Bankaifan, whose pull request 3420 found the duty-switch restart this group learns; the split-order rule that adopts its split function is part B's later pull request, and this one changes no plan and no write.

- **`N_ON` is a decayed weight, not a count** (Carry 2, item ef5d3875). Each booking ages the earlier episodes first, so five stops ten hours apart weigh under five and a sixth latches. The approved note's "n >= 5" already reads as a weight, so the code is unchanged; the module docstring now says so, and the section pins it.
- **The starts sensor's attributes move with observations, not with age** (Carry 3, item c7d068a1). `published` gives `p` to two places, which decay does not move, and `n` as the whole episodes still weighing, rounded down so a published 5 means the latch's weight is reached; `k` is dropped, being `p` times `n`. Age alone now steps only `n`, once per whole episode lost.

Alternatives: keeping `k` and `n` at a coarser decimal still moves them with age alone, only less often; publishing the weights as of the last booking needs a booking instant the record does not store. Dropping `n` entirely hides why a latch falls off.

## Head

6b9e873394a02ec82ec24d23dc454a99418e2366, on `handoff/r10-duty-switch-restart-learning-pr-b`, cut from main 005eed2573da9e946fa4838de147401d0ff36cc1.

## Mutation proof

Each mutant applied to `published` alone, then `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`, restored after:

- `n` back to the reading-time weight to two places (`round(d.weights(when)[1], 2)`, the old resolution): 3 of 61 checks fail, "p publishes to two places, n as whole episodes (down, never up) …", "the published n is aged to the reading's time, p and the tallies are not", "age alone moves no published attribute within a day …".
- `n` rounded to nearest instead of down (`float(round(...))`): the same 3 fail.
- `p` from the decayed `k` (`round(d.weights(when)[0], 2)`): the same 3 fail.
- The whole base `duty_switch.py` under the new section: the section stops at `KeyError: 'duty_switch_dhw_space_p'`.

The `N_ON` check pins an unchanged constant: it fails under any `N_ON` at or under the five spread stops' weight, and passes at the base, by design.

## Null control

- Churn: in the new check, the decayed weight read to two places, the resolution the base published, moves within the same day's 96 quarter-hour reads in which no attribute moves at the head.
- `N_ON`: the existing check where a stop taking an undecayed `n` from 4 to 5 switches a direction on still passes, so the weight reaches five at one instant.
- Empty learner: `published` still returns `{}` with no observation (the section's "attributes are the counter's alone until a direction has an observation" check).
- No golden moves: no file under `tests/golden/` names a `duty_switch_` key (the publication is conditional), and neither claim file is touched.

## Figures

<!-- figure-block: scope-line mb=005eed2573da9e946fa4838de147401d0ff36cc1 head=6b9e873394a02ec82ec24d23dc454a99418e2366 -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py`: all section checks pass at the head; the mutants above as listed.
- `python3 tests/structure.py`: the ratchet passes.

## Red checks

none

## Forward-carry

The carries this pull request does not build land in `docs/design/2026-11-10-duty-switch-restart-learning/design.md`, section "Part B, first pull request", each owed to part B's later pull request, which first reads the estimate:

- Carry 0: the module-level reader is added with its first caller, the arbiter's split; a reader with no caller turns `dead_top_level_symbols` red. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B (items 1b22f416)
- Carry 1: factory reset keeps the duty-switch store; the owner rules before the reader merges. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B (items 3c666f5b)
- Carry 4: a reader takes `span_days` 0 beside non-zero tallies as "nothing recent", and an absent key as no observation. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B (items 90bc5153)
- Carry 5: evidence accrues at different rates per set-point unit; a reader of `n` must not assume otherwise. Carry: R10-DUTY-SWITCH-RESTART-LEARNING-PR-B (items d088605d)

## Friction

none
