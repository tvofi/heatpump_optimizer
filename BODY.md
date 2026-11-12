Builds carry 1 (P447, STAMP-HOLD) of R10-TRAIN-RESIDUE-P2 in `tools/audit/seat/merge_train.py` and `tools/release/stamp.py`: a stamp pushes main's tags and release commit while a train may merge into it, so a merge landing mid-stamp fails `guard()` or recarries. The stamp publishes `refs/heads/stamp-hold` for its run (`stamp_hold`/`stamp_run` split in `stamp.py`); `Train.stamp_hold_wait` waits before each merge attempt while the hold stands, refreshes `train-hold` at every poll (the record beat reads it stale at `HOLD_MAX_AGE_S`), reads a future-dated hold as live and bounds it by its own poll count, and takes over a hold at or past `STAMP_HOLD_MAX_AGE_S` as a dead holder's. Decision: this hold guards main against a merge, so an age that is unknowable-as-young fails closed, bounded; an unreadable ref or commit date is no wait.

## Re-cut

Fourth round. This body replaces the earlier ones; every figure below was re-taken at the head named under `## Head`.

Disclosed self-correction: the handoff 1012ff4440889a24bf3bcd2f66eff2bfefeddb19 committed a re-recording of `tests/entities.py` in `tests/closures.json` that was over-wide, and its body called the three `prepr.sh --self-test` failures inherited. Both were wrong. Measured against the handoff's merge base 14f227c5bd0eb80855b21055cc668857a5f820b4, that recording moved exactly one script's closure, `tests/entities.py`: 567 to 874 members and 75 to 4023 inert reads, 4289 lines added to `tests/closures.json` by `git diff --stat`. The inert reads then held `dev/governance/` files, so `closure.py affected` answered `scoped` for the self-test's skip fixture (one new file under `dev/governance/rules/`) and three rows failed at that head and at neither `origin/main` nor the merge base.

Repair: `origin/main` is merged and `tests/closures.json` is taken from it byte-identical; this pull request no longer changes that file (0 lines). Nothing is re-recorded, because the committed recording already covers what the script reads (`## Figures`).

Cause of the wide recording, with its control: the cloud container's `/proc/sys/kernel/pid_max` is 32768 and a recording of `tests/entities.py` spawns enough processes to wrap it. `strace_files` in `tests/closure.py` keeps the set of Python pids and drops one only on a non-Python `execve`, never on exit, so a recycled pid's opens (a `git` or `node` thread that never execs) are counted as Python reads. Same tree, same command, only `pid_max` changed: at 32768 the recording holds 926 members and 4516 inert reads; at 4194304 it holds 570 and 8, every one inside the committed 572 and 75.

Carries are numbered as the roster numbers them, from 0 (`handoff/audit-r10-roster`, the group's `carry` list, 23 entries). Disclosed self-correction: the earlier bodies listed 1 to 23, so carry 0 was never named, a carry 23 that does not exist was, and the two carries of the first part were named 17 and 18; they are 16 and 17, read from the first part's commit 0c55662763.

- Carry 0: left for a later part; it stays on the roster.
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
- Carry 14: left for a later part; it stays on the roster.
- Carry 15: left for a later part; it stays on the roster.
- Carry 16: built in the merged first part (P608, the rollup read by newest entry); this part adds the pins its review owed (equal-stamp pair in both orders, two valid stamps, a `context`-keyed entry).
- Carry 17: built in the merged first part (P609, a draft is a state on every route); this part adds the pin its review owed (`record_drafts` with `real` false).
- Carry 18: left for a later part; it stays on the roster.
- Carry 19: left for a later part; it stays on the roster.
- Carry 20: left for a later part; it stays on the roster.
- Carry 21: left for a later part; it stays on the roster.
- Carry 22: left for a later part; it stays on the roster.

This merge stays behind the barrier PR 3499 (it touches `tools/audit/seat/merge_train.py`).

## Head

a98c71de318ebdd7ba7eb6e5219866436152035c: the handoff 1012ff4440889a24bf3bcd2f66eff2bfefeddb19 merged with origin/main 43e95474559ca8e2188830f8775c1ddf52df964a (70ecfa6a3fca8720d14b881160bafc602872c576, where the self-tests, mutants and recordings below ran) plus one commit adding the carry entry to `dev/programme/carries/carry-201.json`; measured 2026-11-12T17:53Z on Linux x86_64 with `pid_max` raised to 4194304 for every recording. The diff against origin/main is `tools/audit/seat/merge_train.py`, `tools/release/stamp.py`, `dev/programme/delivery/3498.md` and `dev/programme/carries/carry-201.json`.

## Mutation proof

Each mutant is one exact text replacement in `tools/audit/seat/merge_train.py`, applied in a detached worktree of the head and run through `python3 tools/audit/seat/merge_train.py --self-test` under a 2 GiB address-space cap and a 200 s timeout (a scratch driver, not in the tree). Nine mutants, nine killed; the unplanted tree passes (rc 0, 0 FAIL).

- A, the `self.stamp_hold_wait()` call in `land` replaced by `pass`: KILLED, 5 FAIL (`stamp hold: a live hold logs STAMP-HOLD and waits, and the merge runs only after it clears`, the refresh case, both future-dated cases, the past-the-bound case).
- B, `if not self.real: return` removed: KILLED, `stamp hold: a rehearsal batch (merges nothing into main) does not wait`.
- E, a negative age returned as `None` (fail open): KILLED, `stamp hold: a future-dated hold (this clock behind the stamp's) is live, not absent` and `... is taken over by the wait's own poll count`.
- K, `self.hold_refresh()` in the wait replaced by `pass`: KILLED, `stamp hold: every poll of a held wait refreshes train-hold (the record beat reads it stale at 3600 s)`.
- R, an unreadable commit date returned as 60.0 instead of `None`: KILLED, `stamp hold: an unreadable commit date is no wait (the age is unknowable), and the merge runs`.
- L (`waited += STAMP_HOLD_POLL_S` removed), M (`max(age, waited)` replaced by `age` in the bound) and T (the bound replaced by `if False`): KILLED, each does not terminate; the self-test dies with `MemoryError` under the cap, rc 1.

`tools/release/stamp.py` is unchanged since the reviewed head d0c9eb66497bfd1cb2931bae2c7bddcfa3271e71 and was not re-mutated in this pass.

## Null control

No hold: `stamp hold: null control, no hold runs the merge as today with no wait` passes with 0 polls and the merge runs; a rehearsal batch does not wait. For the closure repair the null control is the recording itself: at `pid_max` 32768 the same command on the same tree prints the wide set, and `tools/pr/prepr.sh --self-test` prints the three 6b FAIL rows at 1012ff44 and none at 14f227c5, 43e95474 or this head.

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test`: rc 0, 669 checks, 0 failed.
- `python3 tools/release/stamp.py --self-test`: rc 0, `RESULT stamp_self_test=pass`.
- `bash tools/pr/prepr.sh --self-test` at 1012ff4440889a24bf3bcd2f66eff2bfefeddb19: exit 2, 539 passed, 3 failed (`6b skips a diff that reaches no selectable script, recording nothing`, `and a skip-case diff still skips`, `and the skip case's line is byte-identical too`).
- `bash tools/pr/prepr.sh --self-test` at 14f227c5bd0eb80855b21055cc668857a5f820b4, at 43e95474559ca8e2188830f8775c1ddf52df964a and at this head: exit 0, 542 passed, 0 failed, each.
- `env -u BASH_ENV ./tests/derive_closures.sh --single tests/entities.py --record-only --out-dir <dir>` at this head with `pid_max` 32768: exit 0, 926 files, 4516 inert reads; 354 files and 4463 inert reads are outside the committed recording.
- The same command at this head with `pid_max` 4194304: exit 0, 570 files, 8 inert reads; 0 outside the committed recording (rule: set difference of the record's `files` and `inert_reads` against `closures` and `inert_reads` of `tests/entities.py` in `tests/closures.json`).
- `git diff origin/main...HEAD --stat -- tests/closures.json`: empty.

## Red checks

none

## Forward-carry

- `tests/closure.py` `strace_files` never drops a pid from its Python set when the process exits, so on a host whose `pid_max` is 32768 (the cloud seat container) any Linux closures recording long enough to wrap the pid space is void: it comes out wider than the read set and, committed, turns scoped diffs into recordings (the three 6b rows above). Precondition for a cloud seat until the parser is fixed: record only with `pid_max` raised (`echo 4194304 > /proc/sys/kernel/pid_max`, root in the container) and refuse a recording whose inert reads grow by more than the diff explains. Control: the two recordings under `## Figures`. Re-measure with `cat /proc/sys/kernel/pid_max` and one `--single --record-only` recording of `tests/entities.py` compared against the committed file. `tools/audit/seat/cloud-setup.sh --check` reads no `/proc/sys` value today. Not built here: `tests/closure.py` is a gate file outside this group's seam and no live roster group owns it, so the finding is the newest entry of `dev/programme/carries/carry-201.json`, whose stage now names any later seat that records a closure on a cloud seat. Carry: #201

## Friction

- gate-scoping.md: unclear: step 6b's Linux recording is trusted on any Linux host, and the cloud seat's pid space makes it over-wide; the rule names off-Linux hosts only. Carry: #201

## Architecture score

n/a: no budget or gate rise.
