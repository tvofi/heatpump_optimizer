Fix review: merge bcaf7d61e237c800fc3678047bffeb6ef9714017

bus-nonce: c9edbefc5888e44c79a54942abc38857

This review covers the resolution delta only (fix-review.md step 12). My round-2 merge verdict stood at `a0c0f8665`. The resolution merge is `3ca9f1943` (parents `a0c0f8665` and main `42e6dedb2`). It is followed by `4ba98387c` and `bcaf7d61e`, and each of those two equals its own `git merge-tree --write-tree` auto-merge tree byte for byte, so neither carries a resolution of its own. I re-read the head before posting and it had not moved.

## The resolution, judged against the conflicted tree `ed35e4e14`
`git merge-tree a0c0f8665 42e6dedb2` reports conflicts in four files: coordinator.py, dev/audit/rounds/round4/D6/claims.py, tests/deployment_shape.py and tests/dst_checks.py. `tests/closures.json` was resolved by the LEDGER-MERGE driver. Beyond the conflict hunks, the resolution touches only claims.json, claims.md and docs/architecture.md.

- **coordinator.py.** The resolution keeps this PR's `FORECAST_STEP = timedelta(minutes=PLAN_STEP_MINUTES)` and takes main's comment, which names `drift.utc_step_starts`. Main's reintroduced `FORECAST_STEP_MINUTES = 15` is dropped. A `git grep` at the head for `FORECAST_STEP_MINUTES|_solve_anchor|_step_start` over custom_components, tests and tools finds only `plan_step` users. Main brought in no new reader of the deleted names.
- **tests/dst_checks.py.** It takes main's `utc_step_starts as _utc_step_starts`, which coordinator.py imports from drift on line 270, and drops main's `_solve_anchor` import. `HASTUB_TZ=Europe/Stockholm` dst_checks.py prints `ALL 134 DST / QUARTER-GRID CHECKS PASSED` here, and CI fast prints the same.
- **Module counts.** On disk at the head I count 79 `.py` modules and 97 tracked package files. Of the modules, 28 import homeassistant at module level, 1 imports it inside a function and 50 are free of it. claims.py now reads 79/79 with history 78 -> 79 (plan_step.py) and 77 -> 78 (log_latch.py). deployment_shape.py reads 97 with both history entries. architecture.md reads 79, 28 of 79, and 50. All of these match my counts.
- **Regenerated claims.json and claims.md.** I re-ran `claims.py` from a head export: `claims_false=0`, `arch_modules_on_disk=79`, `arch_map_listed=79`, `arch_map_missing=0`, and both output files are byte-identical to the committed ones.
- **Mutants.**
  - The fixer's mutant (architecture.md back to 78) reproduces: `claims_false=1`, `FALSE C32`.
  - My own mutant (architecture.md "The other 50 modules" changed to 49) gives `claims_false=0`. Nothing checks that sentence. The resolution's 50 is correct by my count, so this is not a block. It is a D6 claims-harness gap that predates this PR. It needs a fold or a dispatch to the D6 harness owner, not just this note.
- The PR's features block in a head export prints `ALL 6 FEATURES BLOCK PASSED`.

## CI at the head, latest run per name
30 success, 15 skipped, 0 failure or cancelled.
- `fast (3.14)` (job 117665586836) prints:
  - `MODE: SCOPED -- 28 script(s) run, 5 scoped out`
  - `ALL 4171 FEATURE CHECKS PASSED`
  - `ALL 2347 ENTITY CHECKS PASSED`
  - `ALL 134 DST / QUARTER-GRID CHECKS PASSED`
  - `ALL 109 HARNESS HEADER CHECKS PASSED`
  - `STRUCTURE RATCHET PASSED`
  - `ALL 50 GUARD PIN CHECKS PASSED`
  - `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`
- `mutation` (job 117665520777) prints `MUTATION TABLE PASSED`.
- `closures` (job 117669544241) is success.

Nothing went red at this head.

`git merge-tree --write-tree origin/main HEAD` against main at `63816b857` exits 0. The only conflict is `tests/closures.json`, which the LEDGER-MERGE driver resolved. VERSION, the manifest, the notes heading, the claim files and the budgets are untouched by the resolution.

Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-pump-model/evidence3/
