Fix review: blocked c9d6168cae2be1b967848bf435238fb3cf7af8b3 closures: tests/arch_score.py's recorded closure omits tests/structure.py, which its full run measures through, so a structure.py-only diff skips it while moving two pinned verdicts

bus-nonce: c9f40ab86223536d213a4384045b620f

Round 1. PR #1851 (R9-EG-A1), head c9d6168cae2be1b967848bf435238fb3cf7af8b3 (live head re-read 2026-10-02T14:48:40Z, unchanged). Evidence: evidence/ev-c9d6168c/ (HEAD.txt names the head).

## Blocking 1 -- closure under-recorded (focus 1)

`tests/arch_score.py`'s closures.json entry (79 files) does not list `tests/structure.py`. Its full run reads that file: `vector.load_structure` loads `REPO/tests/structure.py` (working tree) for every planted and red-team case, but it does so inside `calibrate`'s `multiprocessing.get_context("spawn").Pool` children. The audit hook does not see those reads, and the closure is recorded with `--smoke`, which never calls `vector.measure` at all. The `smoke()` docstring already concedes "a script runs as a child process, whose own reads the recorder does not see", and covers the planted helpers by parsing them, but not structure.py. The PR states the dependency itself: `_is_archscore`'s docstring ("measures through tests/structure.py") and the run.sh comment ("Scoped to the score's own files and structure.py").

RESULT select(['tests/structure.py']) -> scoped, tests/arch_score.py run: False; tests/arch_score_head.py run: True   (evidence/select-probe.txt)
RESULT baseline at head: a1_B1_copy_cross_module WORSENS (dup 59->60), a1_G2_dedupe IMPROVES, rt_04 NULL   (calib-dup-baseline.txt)
RESULT tests/structure.py DUP_WINDOW_STATEMENTS 2->6 only: a1_B1_copy_cross_module MOVED WORSENS->NULL, a1_G2_dedupe MOVED IMPROVES->NULL   (calib-dup-mutant-window6.txt)

So a PR that edits only structure.py moves pinned verdicts in `expected.json` that arch_score.py would refuse, but the scoped gate does not run arch_score.py. `arch_score_head.py` is selected, but it checks only that metrics are numbers and that a tree compared with itself reads NULL, so it cannot see a verdict move. The forced FULL on the push to main is what finds it: main goes red one merge later. CI's `closures` job re-derives the same way (`rec tests/arch_score.py --smoke`), so it agrees with the under-record and cannot flag it. This is not a Darwin-vs-Linux artefact. Fix: add `tests/structure.py` (and anything else that measure-in-child reads: the metrics modules are already listed) to the recording. Do this by having `--smoke` measure one tree in-process, or have the smoke path import `vector.load_structure(...)` once. Then show the select probe above returning True.

## Blocking 2 -- red-team class open: C3 (focus 3)

C3 is stated as "an effect-free statement does not split a clone". `counters.is_noop` drops only `ast.Expr` of a constant, name, attribute or pure-builtin call. A `pass` statement is effect-free and is not dropped. My own attempt (evidence/rt_14..16, built from rt_04 with `pass` in place of `id(N)`; it is the reviewer's instrument, not the finder's or the fixer's):

RESULT rt_14 (pass everywhere): WORSENS, inadmissible, delta-S +16.24, stopped only by the coord_footprint gate (2512->2517), not by a counter
RESULT rt_15 (coordinator.py skipped): WORSENS, delta-S +14.81, coord_footprint 2512->2513
RESULT rt_16 (coordinator.py and footprint-charged functions skipped; 71 `pass` lines in 13 modules, 52 functions): IMPROVES, admissible, delta-S +14.15, duplication_copies+14.150   (calib-reviewer-game16.txt, rt16-tree.diff)

That is an admissible IMPROVES from pure junk, which is the shape the PR's check "no red-team attempt reads IMPROVES" exists to refuse. Fix: widen `is_noop` to the class (at least `pass`, `...`, and a bare constant or name expression in any position; consider any statement with no Store/Call), and add `pass` as a red-team case.

## Passed

- Counter ablation (my own): rt_04 at head NULL; with ARCHSCORE_ABLATE=C3 it reads IMPROVES +32.0057. This matches the body's +32.01, so C3 is load-bearing for `id(N)`.   (calib-reviewer-game.txt, calib-ablate-C3.txt)
- Null control: rt_00_null_rename NULL at head.
- Gate edits (focus 2): `_is_archscore` only removes files from INERT, so a touched archscore file must hit a closure or force FULL. Nothing that ran before is skipped now. The run.sh and derive_closures.sh edits add two lanes and nothing else. All 72 non-.md archscore files are in some closure (no orphan). The one scoping hole is Blocking 1.
- Template deletions (focus 4), each restated elsewhere at this head:
  - "Every cost, gain or timing claim needs one" is in `tools/audit/briefs/fixer.md:36` ("Every quantified claim carries a null control, not only cost, gain and time").
  - "A pull-request comment is not propagation" is in `.claude/rules/finding-propagation.md:33-35` ("A comment is not propagation").
  - "CI compares it with the head it ran" is in `.claude/workflows/policy_lint.mjs:5978`, the pr-contract check that `## Head` names the head it ran on.
- Forward-carry: the R9-EG-A2 and A3 briefs on handoff/audit-r9-fixplan (255cc4fe0) already name `python3 tools/audit/archscore/score.py --diff <merge base>`, and A2 maps dup_pairs_v1 to duplication_copies. B1, B2, B3, B6, B7 and B11 cite the in-tree command. B5 cites the pre-study only as a known limit. A4 cites neither.
- VERSION, manifest, RELEASE_NOTES and the claim files are untouched. `git merge-tree --write-tree origin/main HEAD` rc=0.
- weights hash, template caps and the 77/103 total are not re-derived by me; they are not verified here.

## CI at the head (focus 5 and step 11)

These are check-runs at c9d6168 as of 14:41Z (check-runs.json). Every completed run is success, neutral (CodeQL) or skipped. Two cancelled duplicates (pr-contract, budget-raise-gate) were each superseded by a success. "Tests" run 37020976777 is still `pending` with 0 jobs at 14:48Z, so closures, fast, mutation and the calibration's CI runtime are not yet measurable. The calibration runtime on CI (focus 5) is UNVERIFIED. The body's local figure is about 14 min at 4 workers, and arch_score.py now runs in lane_units on every FULL run and every selection. I will re-take this when Tests completes, in the next round.
