Fix review: merge d47fd1dfbc72bc5f0c2e80304a92ce5ffd7b2d71

bus-nonce: dff866b81fd3c2c2e3a7960f63f6854a

## Head and round

Measured head `d47fd1dfbc72bc5f0c2e80304a92ce5ffd7b2d71`. It is the head the PR body names, and the PR's live head when this verdict was written. First review of #2948. Topic `fix/r10-fly-owed-levels-r2`; I did not count rounds on any earlier PR. The roles diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` was empty, so the contract read is current. Reviewed from a detached worktree at the head.

## Findings

- `sweep_template.md` step (5) and `owed_unactioned.py` now disagree on the owed family. Step (5) still tells the sweep to read "every `OWED`, `REVIEW OWED`, `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:` line ... and give each an action this sweep". The tool now also counts `MERGE-READY:` and `BLOCKED-UNFIXED:`. Triage P277 scoped the template out on the premise that step (5) "names no family of its own", and that premise is false at this head. The two do not contradict each other: step (5) runs the tool and obeys its exit 1, so a level line still owes an action or an `OWED-ACK` by its second sweep. What is lost is the inline read-and-act list, which no longer names two of the seven. #2935, the open sweep_template PR, does not touch that list: I grepped its diff for `DESIGN-BUILD`/`MERGE-READY` and found nothing. Carry: R10-FLY-SWEEP-DEFAULTS
- One mutant survives: dropping the `$` anchor from `key_of`'s level regex leaves the self-test at 37 checks, 0 failed. So the body's claim "a verdict-level line of any other shape falls through to the existing Unreadable (exit 2)" holds at the head but nothing pins it. I checked it by CLI: `-> MERGE-READY: #2896 5f3a5dd6 extra` gives `UNREADABLE`, rc 2 (ev/harness.txt). The tick prints only `f"MERGE-READY: #{n} {head[:8]}"` and `f"BLOCKED-UNFIXED: #{n} {head[:8]}"` (orchestrator_tick.py:690, :696), so the unpinned shape cannot be reached from the producer. Carry: dismissed: the producer never prints that shape, and the mutant's only effect would be to key a trailing-text line rather than refuse it, which is no worse an outcome.
- The body names a class rule (`grep -n 'flag=True' tools/audit/seat/orchestrator_tick.py`, which gives 69 flagged prints) and leaves the census to the orchestrator as one group. The finding's own seam, `verdict_levels` (tick :653-702), emits three line kinds: `MERGE-READY`, `BLOCKED-UNFIXED` and `REVIEW OWED`. All three are now in `FAMILY`, so within that seam the class is closed. The other flagged lines are outside the owed family as R10-RCA-OWED-UNACTIONED defines it (lines 173-174), and the self-test deliberately keeps `#N: mergeable state DIRTY` out. Carry: dismissed: the finding's seam is fully covered, and widening the owed family to every flagged line is a design question with no finding behind it.

## Evidence

- Mutation proof, re-run (ev/mutation.txt). Head self-test: `37 checks, 0 failed`. Each of the three mutants below was applied with sed, run, then restored, and `git status` was clean afterwards:
  - `FAMILY` without `MERGE-READY:`: 4 failed (the three MERGE-READY arms and the shared-key arm).
  - `FAMILY` without `BLOCKED-UNFIXED:`: 3 failed.
  - The level branch replaced by `pass`: six arms fail, then `Unreadable`.
  These match the body's mutation figures exactly.
- Extra mutant (ev/mutation-extra.txt): with `return m.group(1), shas` in place of `[m.group(2)]`, 7 fail, so the head8-as-id choice is pinned. The `$`-anchor mutant survives; see Findings.
- Finder's harness. Triage P277 committed no harness: its measurement is verdict-ref times plus the shape of the FAMILY regex. Per fix-review step 9, I built my own instrument and name it as mine (ev/harness.txt). It is two boards in the tick's own `render()` shape, ten minutes apart, holding `-> MERGE-READY: #2896 5f3a5dd6`, `-> BLOCKED-UNFIXED: #2933 1a2b3c4d`, a non-owed `-> #2887: mergeable state DIRTY` and an unflagged line. I ran the base file (merge base `d074b94b0626d2a66014e0629946c850ab283e05`) and the head file:
  - RESULT base sweep1 rc=0, `0 key(s)`; base sweep2 rc=0, `0 unactioned`. This is the defect.
  - RESULT head sweep1 rc=0, `2 key(s) ... 0 unactioned`; head sweep2 rc=1, `2 unactioned`, with `#2896 sweeps=2` and `#2933 sweeps=2`. So both are owed after the same `--after` 2 sweeps as the existing family.
  - RESULT head sweep3: an `OWED-ACK ... #2896 5f3a5dd6` covers #2896, which shows `1 acknowledged`, while #2933 stays unactioned, rc 1.
  - The non-owed `#2887` line never keys, at either end.
  I did not re-take the 5-11 h stall figures from triage; the body itself marks them "not re-taken here".
- Null control (ev/harness.txt). A board without the levels (`#2887 DIRTY` plus `REVIEW OWED: #2920`) gives byte-identical output at the base and the head over two sweeps: rc 0 then 1, with `#2920` unactioned on both. So no non-level line is newly owed.
- The body's figures: 37 checks against 30 before is consistent with 7 added `check()` calls in the diff (I counted them). I did not re-run the closure select, structure, or prepr figures; CI's `tests / closures`, `closure-scope` and `gate` are green on this head, and the packet's figure_lint shows `9 resolved, 0 not verified`.
- Merge: `git merge-tree --write-tree origin/main d47fd1dfbc72bc5f0c2e80304a92ce5ffd7b2d71` gives rc 0 and tree f2de8712 against origin/main d24ee8ab (ev/merge-tree.txt).
- VERSION, RELEASE_NOTES.md and the manifest are untouched three-dot (ev/version.txt). The diff contains no claim file or budget file. No golden fixture or budget moves, so there is no metric movement to earn.
- CI on the head, from the check-runs API and re-read live before writing this:
  - `gate` success in all three runs (40867481837, 40862171276, 40862172832).
  - `pr-contract` success, last started 11:44:30Z, after the only red.
  - `governance / instrument-self-tests`, `tests / closures`, `tests / mutation`, `tests / fast (3.14)`, `typing` and `coverage` are all success.
  - The only failure is `tests / nightly-status`. It grades main's scheduled Nightly, and this diff touches none of what it reads (defect-root-cause.md). The body names and answers it under `## Red checks`, so the root-cause trigger is answered.
- Code and docs agree: the docstring, `instruments/owed_unactioned.py.md` and `FAMILY` all name the same seven-kind family.
- Forward-carry: the body states none. The template mismatch above is mine, carried here.
