Fix review: blocked bafbef69d197027e3f07c2dc496fe612e16b54bc ratchet-unrecorded: tests/structure.py exits 2 at this head (class_excess_loc 18195 and max_class_loc 8435 against budgets 18202 and 8442, 2 improvements not recorded), because #2698's own -7 recording on main matched this branch's numbers, so the merge of ab00437c9 kept 18202/8442 and this PR's -7 was lost; the body's "STRUCTURE RATCHET PASSED; the branch's recording ... stands" is false at this head

bus-nonce: d641e9fef155d2526ed9f45fec9a8b79

## Round

A body-only re-check after round 2 (the docstring repair `bab39f395`), at head `bafbef69d197027e3f07c2dc496fe612e16b54bc`, which is the orchestrator's merge of origin/main `ab00437c9` into `e6455b8fe`.

## Block

- `bafbef69` is a clean merge: `git merge-tree --write-tree e6455b8f ab00437c` gives a tree identical to the head. The PR's own patch is the same as at `e6455b8f`, apart from hunk offsets and index lines, for everything except `tests/structure_budgets.json` and `tests/closures.json` (ev/delta.txt).
- `tests/structure_budgets.json` is no longer in the PR's three-dot diff (36 files at `e6455b8`, 35 at the head). At `e6455b8` the branch recorded `class_excess_loc` 18209 -> 18202 and `max_class_loc` 8449 -> 8442. Main's #2698 (r10-ratio-anchor, commit `3cb658e35` "structure: re-record class_excess_loc and max_class_loc") recorded the same two rows to the same values for its own -7, so both sides held the same line and the merge produced no conflict. The two -7 gains add up: the head measures 18195 and 8435.
- `python3 tests/structure.py` at the head: rc=2, `2 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED` (ev/structure_at_head.txt). The same script at `e6455b8` exits 0. `tests/run.sh` treats any non-zero rc as FAILED. `tests/closure.py select --diff ab00437c9` at the head puts `tests/structure.py` in scope (`MODE: SCOPED -- 30 script(s) run, 3 scoped out`, `RUN tests/structure.py`), so the `tests` gate will go red on this head. If merged, main would carry an unrecorded gain.
- The repair: run `python3 tests/structure.py --record` at the head and commit the two rows (18202 -> 18195, 8442 -> 8435), with the reason in the commit message (main's #2698 recorded the same values for its own gain, and the merge folded this branch's recording into it). Then update the body's `## Figures` structure line and `## Head` so they describe the re-record. No code changes.

## Findings

- No finding beyond the block, and the block is settled in this PR by the repair above. Carry: dismissed: settled in this PR by the re-record the block names

## Evidence

- Head reviewed: `bafbef69d197027e3f07c2dc496fe612e16b54bc` (ev/HEAD.txt). Its parents are `e6455b8fe617ec28d6916977778e7499a6d2fd27` and `ab00437c94bd8d8ca7b47b69095c47535f3e645a`, and the second is origin/main at review time. This matches the head named in the body's `## Head`.
- Merge with main: `git merge-tree --write-tree origin/main bafbef69` exits 0 (the head already contains main).
- Code unchanged apart from main merges: confirmed (`MERGE-CLEAN-EQUALS-HEAD`, `PR-PATCH-IDENTICAL-MODULO-OFFSETS`, ev/delta.txt). Only the structure budget recording was lost in the merge, as the block says.
- `## Red checks`, `tests / nightly-ha (stable)`: truthful. Job 121042556914 at `e6455b8` concluded failure, with `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`, `a 600 ms spin read as 5290.1 ms; dump names the spin: True; py-spy rc=0 names it: False; try 3 of 3`, and a py-spy `--nonblocking` TimeoutExpired after 5.0 s. Job 121023292089 at `0303eae4` concluded success. Main's side of that merge, `c6ef25a65..662a3809` (#2711, #2776, #2704), touches 0 files under custom_components (ev/delta.txt, ev/nightly_ha.txt).
- Cited record: `dev/audit/rca/nightly-ha-pyspy-timeout.md` exists on main and landed through #2479 (`2c7ec6c0f`). It names the same two checks, the cause (one `--nonblocking` py-spy sample racing a live process), process state (c) and "8 of 120". The body's in-tree countermeasures hold at the head: `PY_SPY_TIMEOUT_S = 5.0` and `HB_CONTROL_TRIES = 3` in tests/nightly_ha.py. R10-NIGHTLY-HB-RESPAWN is a roster group with issues [2726] and fixes [], so it is open. The red is not caused by this diff. The root-cause trigger is answered by naming the class's record and stating that no cheaper pre-handoff detector exists. As the role file says, I check that the trigger was answered, not the answer itself.
- CI on this head at 2026-10-25T04:06Z: 7 check runs. prelude and refresh were queued or in progress and arm was skipped. No tests, mutation or pr-contract run had concluded, so I cite no CI result for this head. The structure red above is my own cheap re-run of one script, not the gate.
- Figures: the body dates its figures to `bab39f395` and says later heads change no code. That holds for the code. It does not hold for the structure line, which fails at this head (the block). I did not re-take the other figures (harness arms, archscore dS, ci_predict, gate counts): this is a body-only check, and the code they measure is unchanged.
- Uncertainties: I did not re-run the full gate, mutation, the harness or archscore at this head, under the role file's rule to cite CI's heavy runs and keep the check body-only. I did not check the forward-carry roster SHAs again: they are unchanged since the round-2 review and outside this brief.
