Test-only hotfix. The charge-start block in `tests/features.py` (helper `_chg_seq`) started its clock at `dt_util.now()`, the real calendar day, and the check "a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked" expects the weekday count `[1, 0]`. On a Saturday or Sunday the real clock books the weekend count, so `tests / fast` is red on every PR and on main for the whole weekend. The helper now starts from a fixed Monday (2026-11-09), so its own `saturday=True` shift still lands on a Saturday. Production code is unchanged.

## Head

ed82d6a78f2fb7897cf8264f92ae0bc205d1cca4 (merge base with origin/main fdb526895c31c430b31325718f8af768807ffbfb, measured 2026-11-14T01:23:39Z).

## Mutation proof

Mutant: swap the day-type booking in `custom_components/heatpump_optimizer/dhw_learning.py` (`idx = 1 if weekend else 0` in the EWMA fold becomes `idx = 0 if weekend else 1`), run with `tools/audit/seat/mutant_run.py --spec` over the block (`features_block.py` from `def _chg_seq(` to the cooling-learner comment): `SURVIVED NULL`, `KILLED swap-daytype-booking`.

## Null control

Unfixed origin/main, same block, clock moved by a prelude (`FAKE_WD`=weekday number): Wednesday rc=0, Saturday rc=1, Sunday rc=1. Fixed head, same block, all seven days (Mon..Sun): rc=0 each. The unfixed run on the real Saturday clock fails with weekday count [0, 1]. The mutant run above also passes its NULL arm on the fixed head, so the kill is the mutant's.

## Figures

- `python3 tools/audit/seat/features_block.py --prelude ... 'def _chg_seq(' '# The cooling learner reads the same flag'`: Saturday real clock, origin/main: rc=1, one FAIL (the check named above); fixed head under the fake clock on each of the seven weekdays: rc=0.
- `python3 tools/audit/seat/mutant_run.py --spec <swap-daytype-booking> --cmd <the features_block call>`: SURVIVED NULL, KILLED swap-daytype-booking.
- Sweep rule: `grep -nE 'dt_util\.now|datetime\.now|date\.today|utcnow|weekday\(\)' tests/features.py` on the merge base, 122 lines. Disposition: pinned 1 (`_chg_seq` start, the only line whose asserted value is a day-type count compared with a literal), immune 121. Immune because: about 105 sites use `now` only as an offset anchor (`now +- timedelta`) and assert relative values; the weekday readers (`_pd_*` at the `.weekday()` calls, `_bo_factor`, and the `_r9egb1_*` blend checks) read the day of an argument or compute the oracle from the same `now` as production; `_r9egb1_sat` and `_r9egb1_mon` are fixed dates. Evidence beyond reading: CI's Saturday run of the whole script (job.log of run 3551 diagnosis) printed `1 of 5571 FEATURE CHECKS FAILED`, this one; and the `_r9egb1_h3 .. _lc_exp_now` block (the only one reading `dt_util.now().weekday()`) passes 34 of 34 with the clock on Saturday, Sunday and Monday (`features_block.py --emit-prelude` plus the clock prelude).
- Sunday was not run for the whole script (hotfix owner ruling: no whole run); no site in the file separates Saturday from Sunday except the fixed-date ones.

## Red checks

none. Root cause (red-check trigger, `defect-root-cause.md`): state (c): the process (a fast lane that runs features on push) was followed and could not produce the result, because a lane that runs on weekdays only ever sees weekday clocks; PR 3444 passed on the day it merged. Cheaper detector: run the block under a faked Saturday clock in the fast lane, or a lint refusing an unpinned `dt_util.now()` in a block that asserts a day-type count; standing cost not measured here. Root-cause seat dispatched by the orchestrator; this PR builds nothing for it.

## Forward-carry

none

## Friction

none
