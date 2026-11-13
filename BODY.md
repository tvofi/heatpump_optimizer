No code change: carries 5 and 6 of R10-SUITE-ENV-RESIDUE are already landed on main, and carries 0-4 are dispositioned in the brief.

## Head

e23124ff6e45bac1d48b4a775dad555a37965355 (origin/main; the handoff ref is that same commit, no diff).

## Mutation proof

n/a: no code change.

## Null control

On origin/main e23124ff6e45bac1d48b4a775dad555a37965355 the two faults named in carries 5 and 6 are gone: `bash .claude/hooks/stop-selfcheck.sh --self-test` prints 29 passed, 0 failed; `python3 -I tests/throwaway_git.py --self-test` prints 49 checks, 0 failed; `PYTHONPATH=tests/hastub python3 tests/entities.py` prints ALL 2711 ENTITY CHECKS PASSED, no git init CalledProcessError. Landed by 6f594e459c, 7d55d16d97, 2b97dcb098 and c3fa2b58fd (throwaway git: an emptied temp file, per-process empty global config, ENOTDIR file for the global config). The earlier handoff-wip ref 7215e37c71 is an ancestor of main.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
