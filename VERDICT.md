Fix review: blocked 411932cae18926136f04692026a5be881b4c6e70 class-open: hours_until_next_window autumn repeated hour unguarded (fold=1 now at 02:30, 02:45 window returns -0.75 h, base 0.25)

bus-nonce: 580cd535511637c3b5f77d1b973a29ce

Round 1 (no prior reviewed head).

## Block

The claim is "the next-window countdown is the zone's real hours across a DST change". Its autumn domain has an unguarded part: a `now` in the second pass of the repeated hour (`fold=1`). The fix builds the opening instant with `datetime.combine(..., now.tzinfo)`, which always gives `fold=0`. So a window whose wall start lies later in the same repeated hour resolves to the first pass, an hour in the past.

- Probe (`ev/fold_probe_head.txt`), Europe/Stockholm, 2026-10-25, window (02:45, 03:30):
  - `now` 02:30+02:00 (fold 0): `hours_until_next_window` returns 0.25, and `vvc_should_run` pre-heats.
  - `now` 02:30+01:00 (fold 1): it returns **-0.75**, and `vvc_should_run` returns `(False, 'outside every demand window')`. The pre-heat the lead exists for is lost.
- At the base (`ev/fold_probe_base.txt`) the wall arithmetic returns 0.25 and pre-heats, which is the real answer for the second pass. This diff introduces the regression.
- Production reach: the coordinator publishes `dt_util.now()`, which is fold-aware under zoneinfo, so it publishes a negative countdown. `vvc_should_run_at` is an actuator path and skips the pre-heat. `next_window_in_hours` reads `h.start_time`, which is an instant converted from UTC and so carries `fold=1` in the second pass.
- The body's harness (`r11_wallclock_dst.py`) probes only 00:30 to 04:00, which straddles the transition and never lands inside the repeated hour. Its Rule A and Rule B enumerate the sites, but they do not reach the domain of the new predicate.
- Repair direction (the fixer's to choose): resolve `opens` with the fold that keeps it at or after `now`, e.g. retry with `fold=1` when the elapsed time is negative. Add a check that drives `now` at `fold=1` inside the repeated hour, with the plain day as its null.

## Findings

- Note: stale-body: `## Raise justification` and the `budget-raise-gate` red-check entry describe `name_kept_members` 38 -> 39. At this head the three-dot diff leaves `name_kept_members` at 38 and only lowers `class_excess_loc` (17220 -> 17209) and `module_excess_loc` (21646 -> 21639). The `observed` property removal (3e618a5f60) appears to be the payment, so the body no longer describes the budget move. Carry: dismissed: body paperwork, rewritten by the fixer in the re-cut round this block opens

## Evidence

- RESULT: head reviewed 411932cae18926136f04692026a5be881b4c6e70 (`ev/HEAD.txt`); the PR's head matches it. Merge base 46d0a521befa01ff62cf647e04d3a2b783ea2fc1.
- RESULT: `git merge-tree --write-tree origin/main <head>` exits 0 (`LEDGER-MERGE: resolved tests/closures.json`), so it merges cleanly.
- RESULT: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- RESULT: the finder harness `dev/audit/harnesses/r11_wallclock_dst.py` was run at both ends for all four instances and three days (`ev/harness_both_ends.txt`).
  - Base: 3.5 against 2.5 and 4.5, then 88/84, 88/84 and 176/168 slips. The plain day reads 0 slips and 3.5.
  - Head: every cell agrees.
  - This matches the body's table. The base was the current merge base 46d0a521be, not dbdc71faea, and the readings are the same. The rc column in that file is the pipe's tail rc, not the harness's.
- RESULT: VERSION, the manifest and the release-notes heading are not in the diff. The structure budgets only move down. `closures.json` adds the new harness.
- Not re-run: the per-mutant proofs. One attempt ran with features.py driven directly, and features.py failed in 1.2 s for an environment reason (rc 1, see `ev/mutant_dhw_return.txt`). The frugal guard then refused further inline discovery of the runner. The mutation proof is unverified by this seat, which does not change the block.
- CI: the classify waiter was still running at return. Its last line is in `ev/classify_tail.txt`, and a block verdict does not turn on it.
