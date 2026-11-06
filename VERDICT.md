Fix review: blocked 009edde68dbcedd611b622d6c6a0c4c44b443bd0 class-open: ref46/ref53 border, CI job 127046649273 (ref_ms 50.94, cpu_ratio 2.256) is red at this head on ref53's 2.081

bus-nonce: c9b474cadaf6621da788bba05c0f6fdc

## Block

The body's diagnosis is that CI draws `ref_ms` as a continuum, so bands cannot separate runner classes. The diff applies that only below ref24 and between bands. It leaves the ref46/ref53 border (49.51 | 49.60) as it was, and the CI data show the same failure there.

- CI job 127046649273 (run 41966183843, PR 3219, 2026-11-05T04:10Z) is in the body's own window. Its synthetic clean replay read `ref_ms 50.94, cpu_ratio 2.2558`. The job log says `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.256 over its budget 2.081]`.
- At this head, `class_budget` + `cost_offenders` grade that draw the same way: `cpu_ratio 2.256 over its budget 2.081` (`ev/window-offenders.txt`).
- The draw comes from a ref46-population runner. Its own doubled arms ran at ref_ms 47.28 and 48.13, inside ref46. Its memory arm read cpu_ratio 2.366 at 47.28, inside ref46's population of 2.275-2.476. Every true ref53 draw on record is 1.444-1.493, and all of them predate 2026-11-02 (`ev/window.txt`).
- So a ref46 runner whose ruler drifts over 49.60 is graded on ref53's budget and turns the lane red on CI. On the body's own rule, the in-window ref53 population forces a budget in (2.256, 4.512]. The committed 2.081 lies outside that window (`ev/rule-null-control.txt`).
- The body says "ref53 has no new draw in this window and is unchanged" and "offend on 0 of 51". Both are contradicted by this draw.

The class rule the body implies is "every CI draw graded on a budget its population holds". Run over the window, it returns two seams. The diff covers neither and the body dispositions neither: this one, and the loop item in Findings.

## Findings

- The ref46/ref53 border: a ref46 runner drawing ref_ms ≥ 49.60 is graded on ref53's cpu 2.081 and goes red (job 127046649273, above). This is the block. A fix has to hold that draw: re-band, re-centre ref53 on its live population, or fall back when a draw lies over its own class's budget band. The fix must show the draw passing clean and its doubled arm still red. Carry: R10-REPLAY-COST-BUDGET
- A loop-ruler outlier turns the lane red at this head. Job 127310664875 (run 42046303116, PR 3198, 2026-11-05) read clean loop_cpu_ratio 0.0594 with `loop_ref_ms 279.78`, against 131-176 on every other ref46 draw. The lane refused it: `loop_cpu_ratio 0.0594: budget 0.1278 cannot see a 2x cycle`. That refusal reproduces at this head and on main. The diff did not cause it, but it is the same class of runner-induced red in the same window, and the body counts it nowhere. It can be settled here or routed with a reason. Carry: R10-REPLAY-COST-BUDGET
- The body's figures do not reproduce. I re-derived the window by the body's stated rule: the 800 most recent ci.yml runs listed to the end of 2026-11-05, which span 2026-11-02T10:31Z to 2026-11-05T23:58Z.
  - It holds 78 `tests / replay` jobs that ran with a synthetic clean line, not 51.
  - By class: ref24 14 (body 10+1), ref30 18 (body 11), ref46 40 (body 27), ref53 1 (body 0), unbanded 5 (body 3; 34.61 twice and 37.73 are extra).
  - Main refuses 13 in-window draws, not 8. The head offends on 2, not 0.
  - What does reproduce: the owner fixture's range 224.3-269.8 exactly, the 10 new ref24 rows, the 3 fallback rows, and PR 3220's `4 of 194 replay checks FAILED`. One run's job listing (41831302984, page 2) returned HTTP 502 on every retry and is not in my set.

  The table needs re-deriving with its job ids committed or cited. Carry: R10-REPLAY-COST-BUDGET
- The ref24 raise from 3.630 to 4.167 is the centring rule's value, not one the draws force. Every ref24 reading, in the table and on CI, is at most 3.597, which is under 3.630. Twice the minimum is 4.828, so the old 3.630 also held every clean draw and refused every doubled one. The body says "the 3.402-3.597 readings the old budget left no room for", which is false (3.597 is 99.1 % of 3.630). My mutant restoring 3.630 survives every control. The real fix for the 20.5-22.3 draws was the band edge, 22.64 → 19.51.
  - The rule itself is applied correctly: sqrt(2)·sqrt(2.414·3.597) = 4.167.
  - It costs 1.5x detection on four banded ref24 draws that main would see (2.495-2.635 × 1.5 = 3.74-3.95, red under 3.630 and passing under 4.167).
  - Nothing in the tree ties the literal to the rule: a hand-set 3.630 or 4.5 passes the controls.

  The body should state the rule as the reason, not headroom. A control should pin each class budget to the rule over `COST_CLASS_READINGS`. Carry: R10-REPLAY-COST-BUDGET
- `fallback_budget`'s docstring says "the largest class budget measured for each keyed metric". For loop_cpu_ratio it returns COST_BUDGETS' 0.1278, not ref24's 0.1813, because a metric already in COST_BUDGETS is excluded from the max. The body states this (loop 0.1278), so the behaviour is disclosed. But a ref24-population runner (CI loop up to 0.1331) drawing an unbanded ruler, e.g. 25.6-28.7, would be graded on 0.1278 and go red. Either the docstring or the code should change, and the choice should be stated. Carry: R10-REPLAY-COST-BUDGET
- The comment above `COST_CLASS_BUDGETS` still reads "every reading 69-72 % of its class's budget". For ref24 the readings are now 58-86 %. Carry: R10-REPLAY-COST-BUDGET
- The body routes the AWAY_COVERED pin and the export.py credential-refusal pin to "R10-REPLAY-COST-BUDGET round 3". No round-3 entry states them. The group's roster carry is on `origin/handoff/audit-r10-roster` wave-r10-groups.json:15340. Both pins already run at this head: `ok control:away:covered_names_are_committed`, `ok AWAY_COVERED names committed fixtures`, and `ok recorder:unsupported_scheme_refusal_prints_none_of_the_url` (`ev/replay-head-synthetic.txt`). The body should say they are built and name the checks, rather than route them to a stage that does not exist. Carry: R10-REPLAY-COST-BUDGET
- Mutation gap, minor: three mutants survive `replay.controls()`.
  - Band edges `lo <= x <= hi` changed to `<`.
  - ref24 band edge set back to 22.64. It is masked because the fallback then also yields 4.167.
  - The `print(out['notice'])` line in `main()` dropped, so no control proves the lane prints the WARNING.

  The new production branches (fallback return, max, isfinite, notice) are each killed. Carry: R10-REPLAY-COST-BUDGET

## Evidence

RESULT roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty; the merge base equals origin/main 750a6001a.
RESULT merge: `git merge-tree --write-tree origin/main 009edde6` gives 449537967d39, exit 0, with no conflict.
RESULT untouched: the three-dot diff is only `tests/replay.py` and `dev/programme/delivery/3234.md`. No claim file, VERSION, manifest, RELEASE_NOTES or `*_budgets.json` is touched. No budget-file raise, so no tvofi review is owed for one. The raises are the in-code replay budgets: ref24 cpu 3.630 → 4.167 and the ref24 band low edge 22.64 → 19.51.
RESULT mutation proof (fixer's): `return fallback_budget(name), []` mutated to the old refusal fails `control:cycle_cost:runner_class_fallback`, as the body says. My further mutants (`ev/mutants.txt`): max → min fails 2 controls, notice→None fails 1, isfinite dropped fails 1; band `<`, ref24 3.630, band 22.64 and notice-print dropped all survive.
RESULT controls: 34 controls at the head, none failing.
RESULT finder's harness (the CI log population): I parsed 110 tests/replay and nightly slow jobs (535 rows) from 1200 ci.yml runs and 200 nightly.yml runs, all pages (`ev/draws.tsv`, `ev/fetch.sh`, `ev/logs.sh`, `ev/parse.py`). This instrument is mine, built from the body's description; no committed harness exists for it. That absence is itself an instrument gap, and it is the cause of Findings O3. In the reproduced window, head offends on 2 of 78 synthetic clean draws and main on 13 of 78 (`ev/window-offenders.txt`). The PR does repair the runner-class-unknown red (11 of the 13).
RESULT margins, budget against the max in-window clean draw (`ev/rule-null-control.txt`):

| class | budget | max clean | budget / max |
|---|---|---|---|
| ref24 | 4.167 | 3.597 | 1.158 |
| ref30 | 3.934 | 2.903 | 1.355 |
| ref46 | 3.357 | 2.476 | 1.356 |
| ref53 | 2.081 | 2.256 | 0.923 (red) |
| fallback | 4.167 | 3.069 | 1.358 |

Body rule over the same draws: fallback 3.852, ref30 3.979, ref46 3.356.
RESULT plants, real `--one` replays in a planted copy (`ev/plant-override.diff`, `ev/plant.sh`, `ev/plants-real-replay.txt`; rc = 1 iff cycle_cost offends, which is what makes `tests/replay.py` exit 1):
- Probes: 18 in all, at the low, mid and high point of each of the four bands, the fallback at 15, 27, 35, 40.1 and 80, and a fallback floor case at cpu 2.09. Each probe's base was its class's lowest in-window passing clean reading.
- 2x plants: doubled cpu, memory and loop each give rc=1 at all 18 probes (54 of 54). No planted doubling survives at any class or at the fallback.
- 1.5x cpu passes (rc=0) at ref24 and at every fallback probe; it is red at ref30, ref46 and ref53.
- 1.5x loop passes at ref24, ref46 and the fallback; it is red at ref30 and ref53.
- 1.5x memory is red everywhere.
- Every clean run gives rc=0.
RESULT plants over all 110 CI draws (`ev/analyse-head.txt`, `ev/detail-head.txt`): no 2x plant survives on a clean draw that passes. 1.5x cpu survives on 11 passing draws at head (ref24 6, fallback 4, ref30 1), against 3 on main. 1.5x loop survives on 8 at head, against 5 on main.
RESULT measured CI doubled arms graded at the head: 322 of 330 are over budget. The 8 that are not all sit in jobs whose clean draw is already red (`cannot see a 2x cycle`), so the lane was red there anyway. None silently passes.
RESULT local loop failure (adversarial point 2): it is an artefact of non-CI boxes, but `ref_ms` does not separate it.
- This box at the head: ref_ms 26.61 (unbanded, fallback), loop 0.1426, loop_ref_ms 82.3, giving `1 of 182 replay checks FAILED`, rc=1.
- On origin/main it drew ref_ms 30.20, inside ref30, and failed the same way, loop 0.1551 over 0.1278, rc=1 (`ev/replay-main-synthetic.txt`). The failure is not this PR's.
- No CI draw outside ref24 ever exceeds 0.1278. Maxima: fallback 0.1183, ref30 0.1194, ref46 0.1082, ref53 0.1046. ref24 reaches 0.1331 against its own 0.1813.
- What separates boxes like this one is the loop figure at a given loop_ref_ms, not ref_ms: CI reads at most 0.133 at loop_ref 75-101, these boxes 0.143-0.155 at loop_ref 82-97.
- The check does refuse such a box: the lane goes red rather than silently passing, and the unbanded cpu grade prints `WARNING runner class unknown`. The loop budget is flat except for ref24, which matches the draws. The O5 fallback-loop gap is the one place it may not.
RESULT flat input: the owner fixture is not class-keyed, its budget is unchanged at 337.8 / 3740.0 / 0.249, and its 78 in-window CI readings are 224.3-269.8.
RESULT suite at the head: `tests/structure.py` passes at head and at main (STRUCTURE RATCHET PASSED). `tests/replay.py` on the synthetic fixture fails here at head and at main on the loop figure above. `tests/entities.py`: see CI below.
RESULT CI: the head's check runs (`ev/check-runs-head.tsv`, all pages) show `tests / replay` success. Its log drew ref_ms 30.47 (ref30), cpu 2.9908, all 195 replay checks passing, and all three doubled arms seen. The one red is `tests / nightly-status`. Its log names the 2026-11-05 nightly `slow` job 126971378040, which is main's ref_ms 40.1 refusal that this PR repairs. It is not a required context, and the body names that cause. `merge_train.py classify` still exits 3, `WAIT 009edde6... pending: gate red: none`, at the last read (`ev/classify.txt`), about 70 minutes after the gate's last required job concluded. Both `pr-contract / pr-contract` runs (127672200014, 127672980563) are green, and so is every gate job. The only checks still in progress are the two `prelude` runs, which the ruleset does not require. So the head's CI has no red, and I did not wait on prelude. This block rests on the CI job logs, not on this head's checks. `tests/entities.py` did not finish here (it stalls after `the CI ratchet refuses a non-finite, mistyped or unknown budget row` at both head and main); this head's `tests / fast` and `tests / closures` are green.
RESULT head: 009edde68dbcedd611b622d6c6a0c4c44b443bd0 is the head I measured and the head the body names.
Round: first review of #3234, which is the group's fix round 2.

## Friction

The frugal inline-search hook capped Bash reads per prompt, so log inspection went through script files and scout lookups. GitHub returned HTTP 502 on one run's jobs page 2 on every retry.
