Adds ROADMAP.md, a short undated long-term roadmap (zone groups; one zone per room), linked from the README. Documentation only; no production code. Ruled by tvofi 2026-11-15 on #3616.

Repair: `dev/audit/config/scopes.json` classifies ROADMAP.md in D6's `universe` and seat `s1`, beside README.md and DISCLAIMER.md (s1 holds the top-level user documents; SECURITY.md is in s5 with the developer documents).

## Head

`05b21ff0042f93444894ed205b6c7a5b6fb5db7e`, measured on origin/main `e352724335c136b65562cd3e71f728549ad04a82` at 2026-11-16T14:30Z; `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

n/a: documentation and a scope-config entry, no production line. The scopes entry's mutation is its removal, which the null control runs.

## Null control

At `57ccfef48d3ee990176bb672515ab12c8d1315f4` (the scopes.json edit stashed), `python3 -I tools/audit/check_scopes.py --repo . --self-test` prints `FAIL D6 ...` and `classified in neither universe nor static: ROADMAP.md`; at the head it prints `SELF-TEST passed (every perturbed scope refused)`.

## Figures

- `python3 -I tools/audit/check_scopes.py --repo . --self-test`: `SELF-TEST passed` at the head; FAIL on D6 naming ROADMAP.md at `57ccfef48d`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL`, reason `tests/closure.py changes the gate itself` (the PR's INERT entry), left to CI.
- Self-test wall time, `date +%s.%N` around the command above: 98.6 s on this container.

## Red checks

- `governance / instrument-self-tests` (step `check_scopes.py --self-test`): cause, ROADMAP.md is a new top-level tracked `**.md` file, which D6's `classify` globs require to sit in D6's `universe` or `static`; the PR added it to `tests/closure.py`'s INERT list and `tests/layout.json` but not to scopes.json. Cheaper detector: `python3 -I tools/audit/check_scopes.py --repo . --self-test` in `prepr.sh` when the diff adds a tracked file matching a dimension's `classify` globs; standing cost 98.6 s per prepr run on such a diff only (a new top-level doc is rare), against one CI round plus a repair seat per miss. Not built in this PR (a governance-instrument change, the root-cause seat's). Carry: dismissed: recorded here for the root-cause seat; PR #3628 (CODE_OF_CONDUCT.md) is a second instance of the same miss.

## Forward-carry

none

## Friction

none
