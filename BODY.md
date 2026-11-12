Builds carry 1 (P447, STAMP-HOLD) of R10-TRAIN-RESIDUE-P2 in `tools/audit/seat/merge_train.py` and `tools/release/stamp.py`: a stamp pushes main's tags and release commit while a train may merge into it, so a merge landing mid-stamp fails `guard()` or recarries. The stamp now publishes `refs/heads/stamp-hold` for its run (`stamp_hold`/`stamp_run` split in `stamp.py`); `Train.stamp_hold_wait` waits before each merge attempt while the hold stands, and takes over a hold at or past `STAMP_HOLD_MAX_AGE_S` (7200 s) as a dead holder's. Carries 17 and 18 merged in the first part; this part also answers the review's open pins on them (below).

Repair round 1, after `Fix review: blocked d0c9eb66 hold-unrefreshed`:
- The wait calls `self.hold_refresh()` before every sleep. The record beat treats `train-hold` older than `HOLD_MAX_AGE_S` (3600 s) as stale and merges record PRs, and this wait runs to 7200 s.
- A future-dated hold (the train's clock behind the stamp's) is live, not absent: `stamp_hold_age` returns the negative age and the wait bounds it by its own elapsed poll time (`max(age, waited)`), so it is taken over after 7200 s of waiting instead of never. Decision: this hold guards main against a merge, so unknowable-as-young fails closed, bounded; the beat's convention (stale) is for a bookkeeping beat.
- Tests that pin carries 17/18, which survived before: equal-stamp pair in both orders (X10), two valid stamps (X14), `context`-keyed entry (X16), `record_drafts` with `real` false (X17).

This merge stays behind the barrier PR 3499 (it touches `tools/audit/seat/merge_train.py`).

- Carry 1: built here (P447, STAMP-HOLD: `stamp_hold_wait`, `stamp_hold_age`, the `stamp.py` `stamp_hold`/`stamp_run` split).
- Carry 2: left for a later part; it stays on the roster.
- Carry 3: left for a later part; it stays on the roster.
- Carry 4: left for a later part; it stays on the roster.
- Carry 5: left for a later part; it stays on the roster.
- Carry 6: left for a later part; it stays on the roster.
- Carry 7: left for a later part; it stays on the roster.
- Carry 8: left for a later part; it stays on the roster.
- Carry 9: left for a later part; it stays on the roster.
- Carry 10: left for a later part; it stays on the roster.
- Carry 11: left for a later part; it stays on the roster.
- Carry 12: left for a later part; it stays on the roster.
- Carry 13: left for a later part; it stays on the roster.
- Carry 14: left for a later part; it stays on the roster (P567 fix 2, newest-wins red rule versus GitHub's any-red rule).
- Carry 15: left for a later part; it stays on the roster.
- Carry 16: left for a later part; it stays on the roster.
- Carry 17: built in the merged first part; this part adds the pins its review owed (X10, X14, X16, X17).
- Carry 18: built in the merged first part; this part adds the pins its review owed (X10, X14, X16, X17).
- Carry 19: left for a later part; it stays on the roster.
- Carry 20: left for a later part; it stays on the roster.
- Carry 21: left for a later part; it stays on the roster.
- Carry 22: left for a later part; it stays on the roster.
- Carry 0: left for a later part; it stays on the roster.

## Head

1012ff4440889a24bf3bcd2f66eff2bfefeddb19, on top of d0c9eb66497bfd1cb2931bae2c7bddcfa3271e71 (the reviewed head), measured on origin/main 14f227c5bd0eb80855b21055cc668857a5f820b4's descendant; merge-tree reports no conflict.

## Mutation proof

Each mutant of `merge_train.py` run through `python3 tools/audit/seat/merge_train.py --self-test` (669 checks, 0 failed unplanted); the reviewer's drivers `ev/mut.py` and `ev/mut_prior.py` adapted to the new code:
- A drop `self.stamp_hold_wait()` in `land`: KILLED (5 FAIL, "stamp hold:" cases).
- B drop `if not self.real: return`: KILLED ("a rehearsal batch ... does not wait").
- D take-over without `return`: KILLED (hang, timeout).
- E negative age -> None (the old fail-open): KILLED ("a future-dated hold ... is live", and the poll-count take-over case).
- K drop `self.hold_refresh()` in the wait: KILLED ("every poll of a held wait refreshes train-hold").
- L drop `waited += ...`: KILLED (hang); M `max(age, waited)` -> `age`: KILLED (hang); F drop the poll sleep: KILLED (4 FAIL).
- `return None` on an unparseable commit date dropped (mutant_run.py:3201 RETURN_DEL, survived before): now KILLED by "an unreadable commit date is no wait".
- J negative age -> 0.0: survives, equivalent (live, bounded by the same `waited` count, differs only in the logged age). C `>=` -> `>`: equivalent (an age of exactly 7200.0 from a whole-second date is unreachable). mutant_run.py:3210 `waited = 1`: equivalent (take-over after 240 polls either way).
- Prior survivors X10-X17 (`rollup_states`, `record_drafts`, via ev/mut_prior.py): X14 `stamps[0]`->`stamps[-1]` KILLED ("two valid stamps"), X16 drop the `context` fallback KILLED ("status-context entry"), X17 drop `if not self.real` in `record_drafts` KILLED ("record_drafts on a rehearsal ... reads nothing"), M4/M7/M8/M9 KILLED. X10 `>=` -> `>` survives and is equivalent: the key is `(stamp, i)` and `i` is unique per entry, so a tie cannot occur; the equal-stamp pair is pinned in both list orders regardless.

`stamp.py` mutants are the reviewer's S1-S5, all KILLED at d0c9eb66; `stamp.py` is unchanged in this round.

## Null control

No hold: `stamp hold: null control, no hold runs the merge as today with no wait` (0 polls, merge runs); a rehearsal batch does not wait; all-SUCCESS rollups and a recorded `draft: False` are unchanged; the unplanted tree passes every new case.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test`: rc 0, 669 checks, 0 failed (was 661 at d0c9eb66; eight new cases).
- `python3 tools/release/stamp.py --self-test`: rc 0.
- `bash tools/pr/prepr.sh /home/user/body.md`: every step ok except `self-test` (`tools/pr/prepr.sh --self-test`, case 6b "skips a diff that reaches no selectable script", 539 passed, 3 failed). The same three cases fail at the reviewed head d0c9eb66 in this clone, so they are not from this diff; the branch changes neither `tools/pr/prepr.sh` nor `dev/governance/`.
- `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py`: exit 0, `tests/closures.json` re-recorded for `tests/entities.py` (874 files).

## Red checks

none

## Forward-carry

none

## Friction

none

## Architecture score

n/a: no budget or gate rise.
