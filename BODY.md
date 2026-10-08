R9-CI-2. When `mutation-pins` ran a single shard, `mutation-autofix` printed `shards merged: skip-no-measurement` and pushed nothing, even though that shard had measured pins. On #2025 at `de81043a`, shard job 113265218115 printed `PIN KILLED: 4 pinned` and uploaded `mutation-pins-1` with status `measured`. Autofix job 113280999308 then skipped, and the four pins were hand-applied in `c5e00ae3`. Part of #201.

**Cause.** `actions/download-artifact` at the pinned `37930b1c` extracts into `path` itself, not into `path/<artifact name>`, whenever exactly one artifact matches (`artifacts.length === 1`, `src/download-artifact.ts`). The autofix log shows `Total of 1 artifact(s) downloaded` to `.../_temp/mutation-pins-shards`. `merge_pin_shards` iterated the subdirectories of that root, found only the files `status`, `pins.json` and `head`, and returned `skip-no-measurement`. Its `tests/entities.py` fixture built `mutation-pins-1..4` by hand, so it pinned the assumed layout, not the action's.

**Fix.** `merge_pin_shards` treats a `root` that holds `status` as the one shard. Multi-shard roots are read as before. `mutation-autofix` runs the base's copy of `tests/mutation_table.py`, so the fix takes effect for pull requests whose base contains this merge.

**Reach.** The seat took every `pull_request` run of tests.yml from #2049's merge (06:40Z) to 12:01Z. 9 runs reached `mutation-autofix` after a pin run. All 6 single-shard runs printed `skip-no-measurement`, and all 3 multi-shard runs (7, 2 and 10 shards) succeeded. Of the six:

- **#2025 `de81043a`**: 4 pins were lost and then hand-applied.
- **#2024 `c13216ce`** (run 37769767377, autofix 113300382416): 1 measured pin was lost, and it is **still unapplied at #2024's head**.
- **#2025 `0864a8d2`**: 4 pins were measured, but the autofix had already checked out `de81043a`, which closures-autofix pushed. That run would have been `skip-head-moved` anyway.
- **#2024 at `e575850b`, `c1cae32d` and `8fb1b717`**: the shards said `skip-nothing-killed` (survivors only). The runs were mislabelled, and nothing was lost.

The root-cause analysis is `dev/audit/rca/R9-CI-2.md`. It records process state (c): R9-CI-1's eight proof runs all had 3, 4 or 10 shards, and none had 1. It also gives the cost test, and it records the decision not to add a policy line.

## Head

`cef15d6352e970806dc9a3e32b4c23c92e212e95` (code head). Merge base `dcc77dd0` is origin/main at the time of measurement. The code is in `e7e6f0ef` and the RCA in `9e181f5e`. `cef15d63` takes back a comment-only edit to `.github/workflows/tests.yml`, which would have forced the FULL gate.

## Mutation proof

- **Failing test first.** The fixture of the real one-artifact layout, run against main's `merge_pin_shards` with `PYTHONPATH=tests/hastub python3 tests/entities.py`, gave `1 of 2212 ENTITY CHECKS FAILED`:
  - `FAIL the pin shards are disjoint, cover the pool and keep an anchor's twins together; their merge is measured when any shard measured, one shard too  [... one-artifact=skip-no-measurement,[]]`
- **Mutant** `shards = [r] if False else ...` at the fix: `1 of 2212 ENTITY CHECKS FAILED`, the same check and the same `one-artifact=skip-no-measurement,[]`. After restoring: `ALL 2212 ENTITY CHECKS PASSED`.
- **The finder's harness at both ends.** The seat downloaded the real `mutation-pins-1` artifacts with `gh run download <run> -p 'mutation-pins*'` and flattened each one the way the action delivers a lone match. It then called `merge_pin_shards(<root>, <tmp>)`:
  - origin/main: run 37763212023 `skip-no-measurement`, run 37769767377 `skip-no-measurement`, run 37756428662 `skip-no-measurement`.
  - this branch: run 37763212023 `measured` with 4 pins, run 37769767377 `measured` with 1 pin, run 37756428662 `skip-nothing-killed`.

## Null control

- The existing multi-shard cases are unchanged: a 4-subdirectory root still merges to `measured` with `["p:a", "p:c"]`, to `skip-nothing-killed` when it holds only survivors, and to `skip-measure-failed`. All of them pass in the same check.
- Run 37756428662, the flattened lone shard whose status is `skip-nothing-killed`, still returns `skip-nothing-killed` and not `measured`. So the root-as-shard path reports the shard's own status and invents nothing.

## Figures

- `python3 tests/closure.py select --files tests/mutation_table.py tests/entities.py dev/audit/rca/R9-CI-2.md`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2212 ENTITY CHECKS PASSED` (Python 3.14, seat venv).
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- The run census comes from `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?per_page=100&created=>=2026-10-07'`, filtered to `pull_request` runs created at or after 06:40Z. For each run, `/actions/runs/<id>/jobs` gave the `mutation-pins (k)` and `mutation-autofix` jobs, and each autofix job's log gave its `shards merged:` line. All API calls succeeded (0 failures).

## Red checks

none

## Forward-carry

- The comment in `.github/workflows/tests.yml` above `Download the pins the mutation-pins shards measured` ("each in its own subdirectory") is false for one shard. It was left alone because a comment-only edit forces FULL. The next PR that touches tests.yml should correct it; R9-CI-2b (`fix/r9-ci-2b`) touches it.
- #2024's one lost pin, `custom_components/heatpump_optimizer/inputs.py:InputReader.read_flow_kg_s RETURN_DEL 69557675#2` from run 37769767377 (artifact `mutation-pins-1`), needs a hand-apply or a pin re-run once this merges.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
