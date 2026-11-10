Fix review: merge daa6e203b1ae894799e62b56cd3c8d879beb2359

bus-nonce: efd93fc897b85bc7840adebab1578111

## Evidence

- Round 1 of review. Measured head daa6e203b1ae894799e62b56cd3c8d879beb2359 (authored code head 7d6540509c884772cfbf0739ed876a6a619f9669 plus the delivery row only), in a detached worktree. The role-contract diff merge-base...origin/main under dev/governance/roles/ is empty, so the contract is current.
- RESULT selftest head: `open_driver.py --self-test` 91 checks, 0 failed; `beat_jobs.py --self-test` 185 checks, 0 failed (ev/selftest-head.txt). Both figures in the body re-derived.
- RESULT mutant 1 (BOARD_RE reverted to bare `^OWED`): FAIL "parse_board: the tick board's flagged `-> OWED: ` line is read", 91 checks, 1 failed. Killed.
- RESULT mutant 2 (overbroad prefix `^.*?OWED`): FAIL "null: an unflagged board line is not owed", 91 checks, 1 failed. Killed, so the null has teeth.
- RESULT null control: the head self-test against the merge base's open_driver.py gives exactly the new flagged check FAIL (91, 1 failed); the base self-test against the base driver gives 89 checks, 0 failed (ev/selftest-base-driver.txt). This matches the body's "89 pass at origin/main, the new check fails".
- Writer side confirmed: orchestrator_tick.py:1137 emits `OWED: {row}` flagged for level rows that start with `OWED `, and line 2649 renders a flagged line as `"-> " + text`. beat_jobs.py:528 passes `--board` (overlay tick_log) to open_driver. The new prefix is therefore the shape the producer writes.
- Class: open_driver.BOARD_RE is the only parser in tools/ that reads `handoff-no-pr` board lines (a grep for `^OWED` regexes and `startswith("OWED`) finds no other reader of the tick board's handoff lines). The class is one seam. The `refs/heads/handoff/` anchor still excludes `handoff-body/` and `handoff-update`.
- The finding's harness is the committed self-test check (no separate finder's harness; hotfix). The review packet runs no finder's harness.
- `git merge-tree --write-tree origin/main daa6e203` exits 0 (tree 21b9404b), so the head merges cleanly. No claim files touched, and no conflict.
- VERSION, the manifest and RELEASE_NOTES are untouched: the three-dot diff touches only open_driver.py, open_driver_selftest.py and dev/programme/delivery/3396.md. No budgets, closures or goldens move.
- CI: `merge_train.py classify` gives `GREEN daa6e203b1ae894799e62b56cd3c8d879beb2359 pending: none red: none`, rc=0 (ev/classify.txt). No red required check, so the body's "Red checks: none" is correct. Mutation lane green; per contract its baseline was not inferred from that.
- Forward-carry: none named, and none needed.
- Architecture: a two-line regex widening plus a comment, inside the owning module. No breach.

## Findings

none
