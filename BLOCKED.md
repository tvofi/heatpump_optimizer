# BLOCKED: r10-advisor-steady-start, round 4 resumed

The ruled merge is made and the fixer steps are re-run at 815f99a3faea7305d5ef9c85ef801d740bd54bb0 (this ref's tip is that tree with this file added). tools/pr/prepr.sh still refuses it, on two steps whose repairs are not this seat's to choose, so nothing was pushed to handoff/r10-advisor-steady-start or handoff-body/r10-advisor-steady-start.

## Questions

1. `tests / briefs` cannot be repaired without editing a pinned grader, and prepr reads that as BOOTSTRAP. Who lands the grader part, and in what order?
2. Two Forward-carry items name groups that are now `carries-open`. Which live group takes each, or does this group keep them?

## 1. The briefs red and the BOOTSTRAP

- Cause, measured: the first control of dev/archive/carries/carry-1412.json cites `p_dhw_run = max(0.1, min(p_max * 0.8, p_max))` at a line number of optimizer.py; the line now lives in custom_components/heatpump_optimizer/dhw_planner.py. That stale citation was the carry's one control error, which is what kept it in `LEGACY_CONTROL_FILES`. This branch's optimizer.py delta merged with main's puts an unrelated `p_max` within one line of the cited number, so the citation resolves by accident. The carry linted with `legacy: new Set()`: 1 error on main (2b4515dc5), 1 on the unmerged round-4 tree, 0 at 143279b4f and on the merged tree.
- Repair made, commit 815f99a3f (two files, nothing else): the control names dhw_planner.py with no line number (0 errors on the unmerged tree as well, the control), carry-1412.json leaves `LEGACY_CONTROL_FILES`, `LEGACY_CONTROL_CAP` 14 to 13. `node tools/policy/brief_lint.mjs` exits 0 at the head with `LEGACY-CONTROL ok`.
- The refusal, verbatim: `PREDICT briefs   GRADER brief_lint.mjs REFUSED by the base's copy, over tools/policy/brief_lint.mjs: ERROR   [W1-G2] counts: states 22 for metrics in tests/structure_budgets.json; derived 18. Derive the count, do not carry one. (brief line 5) -- BOOTSTRAP: no change in this pull request reaches the base's copy; move the registration to unpinned data the grader reads, or split p1 grader / p2 artifact`. The `[W1-G2] counts` line is the base copy's and was not traced by this seat; the head's copy does not print it.
- Why this seat did not split: every exit from the red needs the set to shrink, and the set is a literal in the grader. Without commit 815f99a3f the head's copy is the base's and the red stays as CI printed it. With the grader hunk alone on main, carry-1412 loses its exemption while its citation is still stale there, which this seat expects to read as a lint error on main (not run). With the carry edit beside it, the base's copy reads the carry as clean and still listed. So p1 is commit 815f99a3f as it stands, and its own pull request is predicted red on `briefs` by the base's copy; landing it is an owner or orchestrator act, and this seat may write to no branch that could carry it.
- If the ruling is the other way (leave the grader alone and answer the red by name only), reverting 815f99a3f is one commit; the red then stays on the pull request's head.

## 2. Carry destinations

`REFUSE   carry   BAD-DEST body item 55dd448f: R10-SAV-VALUATION-RESIDUE: R10-SAV-VALUATION-RESIDUE is carries-open (resume.stage carries-open); a carry goes to the live group owning the seam, else the producing group keeps the fix`, and the same for item 00444e5b, R10-BODY-CONTRACT, in the ci predict step. prepr's valid targets: R10-ARCH-DOCS-DELTA, R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID, R10-ECL110-MQTT-OFF-NEUTRAL, R10-OUTSIDE-DHW-START-HYSTERESIS, R10-OUTSIDE-SUPPLY-STALE-STEP, R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE, R10-OUTSIDE-LEARNER-ROBUSTNESS-P2, R10-OUTSIDE-LEARNER-ROBUSTNESS-P3. None owns either seam.
- 55dd448f is rounds-old (the thermostat reference behind a throttling valve, `_compute_baseline_power`); its destination closed since the round-4 draft passed the body check.
- 00444e5b is new this pass: the thirteen files left in `LEGACY_CONTROL_FILES` were not surveyed for the shape that turned this check red.

## What was run at 815f99a3f, and what was not

- prepr: `PRE-PR: 815f99a3faea7305d5ef9c85ef801d740bd54bb0 ... rc=1`. Refusals: `ci predict` and `carry`, above. `pr-body` 0 errors, `figures` 18 resolved, `ancestry reds` answered (code-scanning alerts not read: HTTP 403), `push order` now a warning only, `merged structure` passed on HEAD merged with origin/main.
- `diff mutants` is a WARN, 28 survivors, and it measures this seat's choice of `MUTANT_CMD`, not the diff: the command was the round's one block of tests/features.py, and the draw's first 40 mutants fall mostly on lines of rounds 1 to 3 that block does not run. tests/features.py whole was not set as the command (about ten minutes a mutant here). Not dispositioned in the body.
- Scoped gate: `MODE: SCOPED -- 31 script(s) run, 2 scoped out`, an `ok` line for each of the 31 and no FAIL line; the run was stopped by the seat's background time limit inside tests/stress.py and printed no closing line. tests/stress.py (`ALL 116 STRESS CHECKS PASSED`) and tests/harness_headers.py (`ALL 112 HARNESS HEADER CHECKS PASSED`) were then run by hand. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Replay, two whole runs: owner fixture `cpu_ratio` 266.7 then 258.4 against 332.8; the first run failed that fixture on `loop_cpu_ratio` alone (0.2165 over 0.2154), the second passed it. The synthetic fixture, which this diff does not reach, was red in both and on `cpu_ratio` too.
- The seven pins: nine hand mutants over the seven sites, each killed by the round's block, a comment-only null surviving. `tests/mutation_table.py --pin-killed` was not re-run.
- origin/main moved during the pass (2b4515dc5 to 19baca761); `git merge-tree --write-tree origin/main HEAD` reports no conflict and main is not merged in.
- Body: the draft for 815f99a3f is BODY.md on refs/heads/handoff-wip/r10-advisor-steady-start-body. body_push.sh was not run.
