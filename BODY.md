Lands **(iv)** of the owner's pick from the measured pre-study
`dev/audit/rounds/round9/prestudy/coverage-fast-scoping-prestudy.md`
(handoff `r9-covfast-scoping-prestudy` @ `69e374393`, body `87f5145ca`), and
**refuses (vi-a) by that same pre-study's own acceptance rule** -- the
measurement that refuses it is in this body, below, so the next seat does not
re-derive it.

**(iv) -- landed.** `tools/coverage/coverage_tree.sh` splits its measurement
into a third lane: `features` alone, `boost_drift_replay` alone, everything
else in between (`W5P_LANES=3`, the new default; `1` stays the serial
reference, `2` stays for two-lane comparisons). Scheduling only: every script
still runs with the same arguments under its own coveragerc, the per-script
data files and the final combine are unchanged, so `coverage.json` is the
union it was serially -- the R9-F10.15 argument, re-proven here on the
#1890(a) stand-in shape. One file changed; no check, lane, budget or
workflow is touched.

**(vi-a) -- refused, not widened** ("If the line sets differ, the knob is
refused, not widened" -- the pre-study's section 6). The knob was built
(`--short-replay`: a 4-day schedule, one pre-boost day, the two boost days,
one recovery; assertions skipped; unit checks and the two-zone prefix kept)
and measured against the full invocation **in the same tree, under the same
tracer** (macOS, coverage 7.13.1, both arms in parallel). The compressed
schedule executes **7399 lines against the full replay's 7700 -- 301 lines
short, across 14 files, uniformly only-full** (the table is under ##
Figures; `defrost.py`'s missing 59 are its derate-confidence branches that
need `DERATE_CONFIDENCE_SAMPLES` observations, `snapshots.py`'s 24 include
the store round-trip the daily drift watch drives, and the learners'
missing lines are their multi-day adaptation). And the residual cost cannot
be cut byte-identically either: the full invocation's cost is almost all
real `optimize()` solves -- shared prefix 254 + three arms x 178 + two-zone
prefix 254 = 1042 solve-cycles, while `check_fork`'s 762 guard cycles reuse
one cached `_OneSolve` and are cheap -- so a short replay that keeps the
line set keeps the solves. The lever left is the pre-study's own (vi-b):
make the solves cheaper, and the brief that commissions (vi-b) must carry
this refusal section whole. The refused work (knob, the `RECORDED_ARGV`
closure rule built for it, the identity instrument) is preserved on the
local branch `fix/covfast-scoping-refused-local` and in
`/Users/timmalmstrom/hpo-seats/r9fix-covfast/refusal-evidence/` for the
reviewer; none of it is in this tree.

## Head

`ae47d8ca06c56102e92461279183ffd611dcae15`, branched from
`origin/main = 6918cb4b213de25c5d6a560578127beef14f0e43` (2026-10-10; the
five files this work touches are byte-identical between that tip and the
pre-study's baseline `6be88834e`, verified by `git diff --stat
6be88834e 6918cb4b2 -- <those files>` being empty, so the pre-study's
measurements and this body's refusal measurement describe this tree).

## Mutation proof

- **Failing-first arm** (the feature did not exist): `origin/main`'s
  instrument, `W5P_LANES=3 W5P_WORK=$(mktemp -d) PYTHON=<python>
  tools/coverage/coverage_tree.sh fast` -> `W5P_LANES must be 1 or 2`,
  exit 2. Green at the head with the same command: the stage runs, three
  lanes, exit 0.
- **Mutant (the #1890(a) shape)**: the boost lane's measure call mutated to
  `measure ""` (a lane that measures nothing, exit 0) in the scratch tree
  -- the stand-in stage's `coverage.json` **differs** from the serial
  reference: `services.py` loses 63 lines and `debugger.py` 72, the two
  files only the boost lane's script reaches (the stand-in stub imports
  were chosen for that, measured not assumed). Killed, restored with
  `git checkout --`.
- **The refused knob's own proofs** (on `fix/covfast-scoping-refused-local`,
  for the reviewer, not in this tree): its recorded-argv rule had a
  failing-first arm (three selftest pins red at the arms-first commit
  `4444d9a67`, green at `89de32e2d`, red again under a pin-deletion mutant)
  -- sound work, withdrawn with the knob it guarded.

## Null control

The serial run is the control: `W5P_LANES=1` twice, `2` twice, `3` twice
and the new default (unset) once produce seven `coverage.json` equal as
parsed JSON with `meta.timestamp` removed -- the lanes move nothing but
when a script runs. The CI null control is the job's own log: the
`coverage` job's `Measure the tree` step must print the three lanes'
`ran tests/... wall=Ns` lines interleaved (parallel, not summed), and its
step wall must fall from the 3623 s class toward the longest single lane;
this pull request changes no package line, so `coverage-ratchet`'s output
must equal the base push run's.

## Figures

- pre-study measurements, carried (their rule: durations read from the
  GitHub jobs API of push run `38076804408`, `origin/main = 6be88834e`,
  2026-10-10, x2 runner band is their section 1.5): `coverage` job 61 m 01
  s; the measurement stage's rest lane 3623 s with `boost_drift_replay`
  traced 2925 s (81 % of it) beside `features.py` 995 s and ~700 s of
  everything else; `fast (3.14)` 52 m 17 s.
- failing-first arm: command above -> `W5P_LANES must be 1 or 2`, `origin-main
  exit=2`.
- lane-equality harness: `bash
  /Users/timmalmstrom/hpo-seats/r9fix-covfast/lane-proof.sh` (stand-in
  worktree `/Users/timmalmstrom/hpo-seats/r9fix-covfast/lanewt`, its own
  stubbed `tests/run.sh` and stub scripts) -> `EQUALITY: 1 distinct
  coverage.json across 7 runs`, `75 package files, 5159 lines`, and the
  mutant line -> `differs from serial = True`, `{'debugger.py': 72,
  'services.py': 63}`.
- the refusal measurement (macOS, cov-venv 3.14.7, coverage 7.13.1, both
  arms in parallel, tree = baseline plus the refused-knob commits): full
  arm `exit=0 wall=2125s`, short arm `exit=0 wall=1011s`, then the
  comparator over the two `coverage.json` outputs (rule: per-file
  `executed_lines` sets, union and difference) -> `full: 75 files, 7700
  executed lines / short: 75 files, 7399 / files that differ: 14`, every
  difference only-full; the full table is
  `/Users/timmalmstrom/hpo-seats/r9fix-covfast/refusal-evidence/divergence.txt`
  (beside both `coverage.*.json`, both arms' logs, and the instrument).
  Per-file only-full counts: coordinator 99, defrost 59, price_model 25,
  snapshots 24, dhw_learning 22, comfort_learning 17, accuracy 13,
  curve_learning 13, dhw_draws 11, flow_lift 8, freq_control 4, optimizer
  4, draw_range 1, drift 1.
- cost-structure rule (why no byte-identical short exists): solve-cycles =
  `fork_cycle() + 3 x (DAYS*48 - fork_cycle()) + fork_cycle()` = 254 + 534
  + 254 = 1042, and `check_fork`'s cycles run on the one cached `_OneSolve`
  plan (the guard exists to avoid paying three prefixes' solves), so
  cutting the guard saves no solve. Walls fit the rule: 1042 solve-cycles
  -> 2125 s and 514 -> 1011 s, both ~2.0 s per solve-cycle.
- gate scope of this diff: `python3 tests/closure.py select --diff
  origin/main --workdir <tmp>` -> `MODE: SCOPED -- 0 script(s) run, 33
  scoped out` (an INERT instrument file; the run_always set ran below,
  CI's `coverage` job still measures every script because the per-script
  cache key hashes `coverage_tree.sh`).
- at the head: `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`;
  `tests/entities.py` -> `ALL 2250 ENTITY CHECKS PASSED`;
  `tests/closure.py selftest` -> `ALL 57 closure shrink pins PASSED`;
  `tests/env_drift.py --claims-only origin/main` -> `claims hygiene:
  origin/main ok`; `tests/layout.py` -> `layout self-test: ok`;
  `tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED`;
  `tools/audit/archscore/score.py --diff origin/main` ->
  `Architecture score: dS +0.0000 NULL`.
- **wall-time prediction, a prediction and CI's to measure** (rule: the
  stage costs its longest lane; carried walls above): the measurement step
  falls from the 3623 s class to `max(2925, 995, ~700)` ~= 2960 s --
  **~11 min per `coverage` run**, on pushes and reach-PRs alike, with the
  first post-merge PR a cache miss that measures everything (the key
  hashes the instrument). Read the oracle off the landed run's own
  `ran tests/<s>.py exit=<rc> wall=<n>s` lines and the step timing.

## Architecture score

`dS +0.0000 NULL` -- no production module is touched; the one changed file
is a measurement instrument under the INERT prefix `tools/coverage/`.

## Red checks

none at the head. The CI oracle to read on the landed run is the
`coverage` job's measure step (three interleaved lanes, wall at the
longest lane) and `coverage-ratchet` unchanged against the base push run.

## Forward-carry

none

## Friction

none
