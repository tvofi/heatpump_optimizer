HOTFIX: Nightly `nightly-ha` (stable and 2025.2.0) has been red since #3454, which reddens `tests / nightly-status` on every code PR. Run 43358851739 (main e4ca2d940e) prints `FAIL a4:failed`, `a4:unavailable`, `a4:buttons`, `a4:no_stale` and `run:exit_status`. Cause: #3454 made a failed Tibber fetch raise `UpdateFailed` only once the last published prices no longer cover now (`issues.note_price_outage`, `_known_prices_for`); otherwise it bridges with a warning and the `price_feed_stale` repair. `_async_check_a4` broke the fake Tibber right after a fetch of a curve covering now, so the update was bridged and every check presuming `UpdateFailed` failed. A harness defect against an accepted product change; nothing under `custom_components/` changes and #3454 is not reverted.

Fix, `tests/nightly_ha.py` plus its self-tests in `tests/entities.py`: A4 is two real-boundary phases. (1) New `a4:bridged`: with HTTP 500 while published prices cover now, `last_update_success` stays True, `price_feed_stale` is in HA's issue registry, nothing published went unavailable. (2) The fake server gains an ended-curve mode (200 with `_hourly_prices(now - 3 days)`); one refresh takes it, `before_failure` records are taken, then the 500 runs the unchanged `a4:failed/unavailable/buttons/no_stale`, then restore and `a4:recovered`. The harness never sets `last_update_success` or the coordinator's price cache. Docstrings updated; `_a4_update_failed_traceback` kept valid (phase 2 still ends in `UpdateFailed` from `_tibber_fetch_failed`).

Product check before relying on the ended curve: `pull_prices` -> `prices_from_tibber_payload` applies no expiry filter (only unparsable rows and an empty result are refused), so an ended curve is `ok` and replaces the cache; `_known_prices_for` then covers nothing (`_covering_index`, one-hour tolerance; the last row of a 3-day-old curve ends 2 h before now), so `note_price_outage` gets a falsy `covering` and the next 500 raises.

## Head

94e45e79312352005bd46af581fa286bd3583342 (code head, measured at this SHA; base bc58019d01b3072e02bfd30cdf052dd715f2945c).

## Mutation proof

No Docker in this cloud environment (`docker info` fails), so the live Nightly is the remaining proof and nothing below was run in a container. Run instead: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` (all checks passed, including the new A4 pins), and a driver that runs the real `_async_check_a4` against a modelled coordinator implementing #3454's rule (500 raises only when no covering curve was taken):
- normal: `a4:bridged`, `a4:failed`, `a4:unavailable`, `a4:buttons`, `a4:no_stale`, `a4:recovered` all True.
- bridging disabled (the model's `note_price_outage` forced to not bridge): `a4:bridged` False, `a4:failed` True.
- ended-curve step skipped (`end_price_curve` made a no-op): `a4:failed`, `a4:unavailable`, `a4:buttons`, `a4:no_stale` False (bridged, so `last_update_success=True`).
Predicate mutation of `check_a4_bridged` is pinned by the new entities.py self-test with four negative cases (failed update, missing repair, entity unavailable, empty before-set) beside the positive one.

## Null control

On main, the unmodified harness prints the five FAIL lines of run 43358851739. The ended-curve-skipped run above is the null control for the premise: with the source broken while prices still cover now, `a4:failed` reads `last_update_success=True`, as on main. The unmodified `_async_check_a4` itself was not driven against the modelled coordinator. The reviewer-facing live proof is a dispatched Nightly on this branch (`gh workflow run nightly.yml --ref <branch>`) with 0 FAIL lines in both `nightly-ha` jobs; not run here.

## Figures

- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2711 ENTITY CHECKS PASSED` at the code head before the final docstring-only commit's re-run; the re-run after it also passed.
- `bash tools/pr/prepr.sh` (no body) at 94e45e79312352005bd46af581fa286bd3583342: `PRE-PR ... rc=0`, every step ok, `diff mutants` skipped (MUTANT_CMD unset; the change adds no `.py` line outside `tests/`).
- the count of checks is whatever `tests/nightly_ha.py` roster prints; no count is claimed.

## Red checks

`tests / nightly-status` and Nightly `nightly-ha` (graded on main; the orchestrator's per `defect-root-cause.md`, not owed an answer here). Root-cause answer anyway. State (d): the process was sound and its precondition changed underneath it. #3454's lane did not run `nightly-ha` because it runs only on schedule or dispatch, so the product change and its harness premise were never co-tested. Cheaper detector considered: (1) a pull-request rule dispatching `nightly-ha` when a diff touches `_tibber_fetch_failed` or `_fetch_tibber_prices`: standing cost one container Nightly (many minutes) per matching PR plus a path list that must track the A4 path; (2) an offline `entities.py` self-test driving `_async_check_a4`'s premise against the real coordinator: needs HA, which the stub does not satisfy for this path (`ha_contract.py` fidelity), so it would pin the stub. Recorded: neither is worth building now. Frequency is one occurrence in a release cycle, the loss is a red Nightly caught within a day, and the present change makes A4 name both contracts. Revisit at a third instance.

## Forward-carry

none

## Friction

none
