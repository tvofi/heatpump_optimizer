Part of #2495. R10-CI-LAYOUT-P2a, unit U6-lib (code-scanning alert lister). Head c90a9b15b6ebaa45c6d83619b12596b0df9eac47 on base 738d950aa981efbdf866ff369942a69c5ae7d205.

## Unit
U6-lib. New: `tools/ci/alert_list.py` (291 lines, about 140 production, the rest self-test), `tools/ci/alert_list_mutants.sh` (28). `tests/closure.py` +6 (two INERT lines for my own files; U0a's `tools/ci/` GATE_FILES entry supersedes them on assembly). `git diff --stat origin/main...HEAD`: 3 files, 325 insertions. Not touched: ghapi.py, workflows, entities.py, governance.yml, VERSION.

## Interface
- `reds(get, ref, sha, legs, base, base_repeats) -> (ok, [red lines] | reason)`; `main(argv, get)`; `title_sha(display_title)` (the `sha=` token); `PINS = {sort: created, direction: desc}`; `python3 -I tools/ci/alert_list.py --pins` prints `code-scanning/analyses sort=created direction=desc` for the entities row; `--self-test` prints `alert_list self-test: N checks, 0 failed`.
- Output: one `code-scanning alert <n> (<rule id>)` line per alert; failure prints `FAIL closed: <reason>` and exits 1. `RateLimited` is never caught (propagates; verified at the analysis and the alert read).
- Flow: analyses matched by `ref=`/`commit_sha` (no `sha=` parameter, no `LAG_MAX`); each matched analysis read by id with `Accept: application/sarif+json`; base subtraction when `base_repeats`; then each remaining alert read by number (no ref), dropped if dismissed (N5-2). Never `alerts?ref=` open listings.
- **Contract gap for the glue / P2b:** the contract's `get(path, params=None)` cannot carry `Accept`. The module calls `get(path, params, headers)` for the SARIF read only; `ghapi.get` (or the binding) must accept an optional `headers` and the JSON parse must tolerate the `sarif+json` content type. Paths are relative to `repos/{repo}/`. The `__main__` entry imports `ghapi.get` lazily (absent until U0a lands).
- **Not done:** mutants are in `alert_list_mutants.sh`, not in `r10_seat_selftests_mutants.py`: that harness resolves a mutant through a `governance.yml` `instrument-self-tests` step, which the glue adds. Registering `alert_list-1..` there is the glue's.

## Controls
- Self-test: `python3 -I tools/ci/alert_list.py --self-test` -> `alert_list self-test: 24 checks, 0 failed`.
- Null: no-alert fixture lists `[]`. Plant: alert 7 dismissed (alert-level) lists `[]`; X2 drops only the dismissed one of two.
- Rejected-reading control (A): the `alerts?ref` reading lists nothing where the analysis reading lists alert 7.
- Mutants: `sh tools/ci/alert_list_mutants.sh` -> 8 of 8 refused (alert-level read skipped; base exclusion off; missing alert number skipped; unmatched leg unrefused; sort/direction unpinned; Accept dropped; RateLimited swallowed; failed alert read tolerated), ending `ALERT-LIST MUTANTS: every mutant refused`. The unmutated self-test is run first inside the script.
- `python3.13 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. `PYTHONPATH=tests/hastub python3.13 tests/entities.py` -> `ALL 2388 ENTITY CHECKS PASSED`. `tests/harness_headers.py` rc 0; `tests/throwaway_git.py --check` 0 refused. The full scoped gate and closures were not run (PREPR_SKIP_CLOSURES=1; CI owns them).
- No GitHub API calls were made.

## Red checks
nightly-status: not examined (no API reads, per the brief). This diff adds no workflow and changes no code a gate script reads, so it cannot cause or cure that check; the orchestrator should answer it from the live record.
