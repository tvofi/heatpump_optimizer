Part of #3885 (carry 2 of `dev/programme/carries/carry-3885.json`): a pull request forked at a light main commit looked its drift baseline up under that commit's key alone. A light push stands `tests/env_drift.py` down, so it never warms an entry, and every such fork captured its baseline cold.

The lookup now resolves the fork point to the nearest first-parent ancestor that warmed one. `env_drift.baseline_candidates` walks back from the fork point, nearest first, for as long as `env_drift.capture_reaches` says the files changed since then do not reach the capture. `capture_reaches` is `tests/closure.py`'s own `select`, given the older commit's closures the way `run.sh` gives them, which is the same rule that stood env_drift down on those pushes. `env_drift.cache_resolve` takes the nearest candidate whose entry loads, under the key that push wrote. `env_drift.py --cache-keys` prints the candidates' keys, and `tests.yml` passes them as `restore-keys`. The walk stops after `BASELINE_KEYS_MAX` (10) commits, the most keys actions/cache accepts in one restore. It does not start when the checkout's closure entry for env_drift differs from the fork point's.

What env_drift asserts is unchanged. On a hit, the baseline it compares against is a capture the gate already treats as equal to the fork point's, and on a miss it captures the fork point and stores it under that commit's own key, as before. Warm-side and push-side behaviour are untouched.

Alternatives considered. Carrying the range base's entry forward on each light push (the carry's suggestion) would need a restore, a re-key and a save on every light push, and it would write entries whose recorded commit is not the commit they were captured from. Resolving on the reading side writes nothing new, keeps `cache_load`'s key re-check strict, and needs no change on the push side.

## Head

984536019dc8c707a56d0d7c434308e29fedbd52, origin/main a59a1b0d9ac7 merged in (one conflict: both sides appended to the end of tests/entities.py, both kept). Measured at merge base ac9045c22372 on 2026-11-28T17:40Z; the walk below is over origin/main ac9045c22372.

## Mutation proof

Each mutant was applied in place to `tests/env_drift.py` and the new `tests/entities.py` block was run alone (from `# #3885 carry 2:` to the script's close). The file was restored after each one (`cmp` against the saved copy printed nothing). The production lines are under `tests/`, so prepr's `MUTANT_CMD` draws none of them.
- M1 `out.append(sha)` → `pass`: FAIL `a light fork point resolves through its light ancestors to the heavy commit, nearest first (#3885)`, FAIL `a heavy fork point resolves to itself alone, and the walk stops at its limit (#3885 null control)`
- M2 the walk's `files and reaches(...)` predicate → `False`: the same two FAILs
- M3 the closure guard `if (here ...) != (there ...)` → `if False`: FAIL `a checkout whose closure for env_drift differs from the fork point's never walks (#3885)`
- M4 `for sha in candidates` → `candidates[:1]`: FAIL `the lookup takes the entry the heavy push warmed, under the key that push wrote; the fork point alone misses and keeps its own key (#3885)`
- M5 `capture_reaches` drops `or DRIFT_SELF in plan["run"]`: FAIL `the default rule is tests/closure.py's selection: a file outside the capture's closure does not reach it, one inside does (#3885)`
- The test builds its repository with `throwaway_git_init`. At the merge base, the block fails at once with `AttributeError: module 'env_drift' has no attribute 'baseline_candidates'` (the failing test was written first).

## Null control

- A fork at a recording commit resolves to itself first, so its key and lookup are the same as before. `walk` checks this for every recording commit it lists and exits 1 if one does not resolve to itself; it passed. At heavy 7b0ddc205f25, `--cache-keys` prints exactly one key, equal to `--cache-key`.
- The resolved baseline is the fork point's own capture: the entry captured at 265e061f65e4 (before run) and the one warmed at 7b0ddc205f25 hold identical payloads, 56 scenarios, compared by `json.loads` equality.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/ci3885_drift_fork.py walk --count 60` (sha1 c69cd6dff579538357a377658e3cf42f8e804569) over origin/main ac9045c22372: of the last 60 first-parent commits, 18 recorded no baseline. A fork there hits 42/60 before and 60/60 after, and every recording commit resolves to itself. Rule: a commit recorded when its first-parent diff is not `prelude.light`, or when `capture_reaches` with its parent's closures says it reaches the capture. The nightly's warm of main's tip is not counted, so "before" is a lower bound. fd93aa3e9b, the fork the carry measured missing (run 45907841043), is classified `recorded=no` and resolves to 46d0a521befa.
- Timing, one host with 4 cores and OPENBLAS_CORETYPE=Haswell, fork point 265e061f65e4 (light), its recording ancestor 7b0ddc205f25 warmed by `ci3885_drift_fork.py warm 7b0ddc205f25 DIR`, then `tests/env_drift.py --all 265e061f65e4` from a one-commit fork with `DRIFT_CACHE_DIR=DIR`:
  - base code: 347 s, `DRIFT BASELINE CACHE MISS`, two captures
  - this head: 179 s, `DRIFT BASELINE CACHE HIT`, `ref 265e061f65e4 -> 7b0ddc205f25`
  - saving per light fork: 168 s here (CI's cold run in the carry was 262 s)
  - null control: at a recording fork the key is unchanged, so the time is unchanged (above).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No budget is raised, and no payment was owed: the change touches only `tests/`, `dev/` and `.github/`, none of which the ratchet measures.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL`, because `.github/workflows/tests.yml` changes the gate, so CI runs the full suite. Run locally: the full `tests/entities.py`, the new block alone, and `tests/env_drift.py --all` (the timing runs above, both `NO UNCLAIMED DRIFT`, `NO STALE FIXTURE`).

## Red checks

none

## Forward-carry

none

## Friction

none
