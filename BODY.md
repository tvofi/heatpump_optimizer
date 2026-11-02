Part 1 of R10-SUITE-HOST-DETERMINISM (issues #2726, #2730): the suite's host-zone, gate-lease-timing and coverage-descendant nondeterminism. Parts named under Forward-carry are not built here.

Carries, each named as built, discharged or next part:

- Carry 1 and Carry 4 (0-based 0, 3; features under a non-UTC `HASTUB_TZ`): BUILT. Six checks failed at the merge base under `HASTUB_TZ=Europe/Stockholm` (the four named plus the #2257 cap-tile check and the quiet-off-window check, both zone-dependent the same way). Each now names its instant in the configured zone (aware t0, `dt_util.now()` for the window read, `DEFAULT_TIME_ZONE` for the quiet-window freeze and the tile instants). The `_comparable_ts` docstring said an aware stamp "keeps its own wall clock"; production converts to the configured zone's wall clock, so the docstring is corrected (comment only).
- Carry 2 (0-based 1; gate-lease one-winner flake): BUILT as a test change. The 0.15 s fixed hold is now a wait on a condition (the other waiter's ticket exists and a poll has rewritten it). I could not reproduce the flake (0 bad of 150 under CPU load, before the change), so the cause is not established; the check no longer depends on a window. Planted defect: with `Owner.create` overwriting and `_free_slot` always 0 the case reads red with the CI flake's signature (`overlaps=1 order=['b','a']`).
- Carry 3 (0-based 2; coverage_tree.sh descendants): BUILT. `measure()` waits for processes still carrying the script's own `COVERAGE_PROCESS_START` rcfile path (Linux `/proc`; skipped elsewhere) and refuses, naming the script, after `W5P_DESCENDANT_WAIT` (default 300 s). New entities row drives it under the existing stub interpreter.
- Carry 5 (0-based 4; base-red entities U0c / delivery_status): NEXT PART. Not re-measured here: at this base `tests/entities.py` read ALL PASSED in this seat.
- Carry 6 (0-based 5; scan("HEAD") vs working tree): NEXT PART.
- Carry 7 and Carry 8 (0-based 6, 7; stdlib sampler macOS platform rule, six wrappers): NEXT PART (heartbeat platform rule).
- Carry 9 (0-based 8; nightly respawn): NEXT PART; the `gh run list` count is not available to this seat (no `gh`), so superseded-or-built is undecided and stays open.

## Head

Merged origin/main (8f286293b) into the branch before the handoff (merge-tree was clean); code head 32781595b03cf80ba96ceafa7e30dcf9dac83597. Figures were taken at pre-merge head ba8593ecfe9aea1d6f86c3624df7db45ca67046d. prepr.sh after the merge passed every step except closures, which REFUSED on the base-red typing_ruler (left to CI).

## Mutation proof

- Coverage: replacing `wait_descendants "$s" || return 1` with a no-op fails exactly `a measured script's late-writing descendant is waited for, not recorded as nodata` (entities: 1 of 2593 failed); restored it passes (2593).
- Gate lease: see carry 1; the planted defect reads red.
- Features: the zone fixes are test-side; the null is the base run below.

## Null control

At the merge base, `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 tests/features.py` printed `6 of 4770 FEATURE CHECKS FAILED`. After: `ALL 4770 FEATURE CHECKS PASSED` under Stockholm and `ALL 4777 FEATURE CHECKS PASSED` with the variable unset.

## Figures

- `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 tests/features.py` (before: 6 failed; after: all passed)
- `PYTHONPATH=tests/hastub python3 tests/features.py` (unset zone, all passed)
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (ALL 2593 ENTITY CHECKS PASSED)
- `python3 tests/structure.py` (STRUCTURE RATCHET PASSED)
- `PYTHONPATH=tests/hastub python3 tests/golden.py` (NO UNCLAIMED DRIFT)

## Red checks

none from this diff. Two seat-environment reds read identically at the merge base: `tests/typing_ruler.py` (the pinned `/opt/hpo/venv-ha` census exits 1; also makes `prepr.sh` step `closures` REFUSE, left to CI) and `GOLDEN_MODE=strict` (BLAS drift; the drift-mode gate passes).

## Forward-carry

Carry 5, Carry 6, Carry 7, Carry 8 and Carry 9 above are the next parts, remaining in dev/programme/rosters/wave-r10-groups.json (group R10-SUITE-HOST-DETERMINISM, 0-based carry indices 4-8, on handoff/audit-r10-roster). Carry: R10-SUITE-HOST-DETERMINISM

## Friction

none
