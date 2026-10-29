R10-FLY-NIGHTLY-HB. `hb:positive_control` (tests/nightly_ha.py `check_hb_positive_control`) failed every try on the 2026-10-29 schedule run 40806276912, job `nightly-ha (stable)`: "a 600 ms spin read as 5308.8 ms; dump names the spin: True; py-spy rc=0 names it: False; try 3 of 3", which also failed `run:exit_status` and turned the nightly red.

**What the failure measured.** The control's spin is held until its sample returns or is cut (`HB_CONTROL_HOLD_S = HB_DUMP_S + timeout + 1.0`). The CI gap is 5308.8 ms = `HB_DUMP_S` 250 ms + the 5000 ms sample timeout + 58.8 ms: every one of the three samples ran to its cut. That separates the three candidate causes the brief names. A late sample on a contended runner returns rc=0 inside the cut (gap under 5250 ms, the sampler section present); a sampling-window miss returns rc=0 without `_hb_spin` at a gap near 600 ms; only a sampler that does not return reads 5250 ms plus overhead, three times out of three. The harness reproduces that number with a py-spy that never returns (5292.5 to 5330.9 ms over 9 base tries) against 600.3 to 600.8 ms with the real py-spy (the null), so the bound was not wrong and widening it, or retrying, would not have rescued it: the retry already ran three fresh spins.

**Why py-spy did not return** is the previous fixer seat's container measurement (py-spy 0.4.2 past "Found interpreter" spinning in its stack walk on some CPython 3.14 HA processes, for the process's life; the stdlib unwinder reading those processes). This seat could not re-take it: `docker pull` of the HA image is refused here (Docker Hub 429; the ghcr blob host 403 through the proxy). It is recorded as that seat's finding, not as a figure of this body, and the PR's own `nightly-ha (stable)` arm in `tests.yml` is the real-HA run of this head.

**The fix.** `sample_command()` makes the stall sampler CPython's own `_remote_debugging.RemoteUnwinder` wherever the interpreter ships it (3.14+, the `stable` arm), run in a child with the same 5 s cut, and the staged `py-spy dump --nonblocking` only where it does not (the 3.13 floor, where #2479 measured no hang). The check is unchanged in what it asserts: in one try the gap is seen, the in-process dump names the spin, and the out-of-process section (now `sampler rc=0:`) names it. Alternatives: a longer timeout or more retries (refused by the brief, and by the measurement above: the sample never returns); a container respawn (R10-NIGHTLY-HB-RESPAWN's option (b), which costs a second HA boot per red and keeps the sampler that fails); an inconclusive verdict on timeout (changes what the control asserts). The sampler swap removes the failing component instead of working around it.

This seat added one commit on 877f4addb: `--inproc real|hung` in the group's harness, so every figure below re-runs without the HA image.

## Head

2f033a59af4fed89f681cf9d5edcfb89cc714d78 (877f4addb plus the harness's `--inproc` arm). Merge base 486e65cbd9c8451c01624f13b773feb6d722ad9b; `git merge-tree --write-tree origin/main HEAD` reports no conflict at origin/main e5ddba1fad5e6eccfeceaeaaa249bc459963405b (2026-10-29T19:46Z).

## Mutation proof

Mutant: delete the fix's predicate, the two lines `if importlib.util.find_spec("_remote_debugging") is not None:` / `return [sys.executable, "-c", _STDLIB_SAMPLE]` in `sample_command`, so the sampler is py-spy wherever it is staged.

- `tests/entities.py` (the closure's script for `tests/nightly_ha.py`), under 3.14.6 and under 3.13.17: red under both. 3.13.17: `1 of 2472 ENTITY CHECKS FAILED`, the one being `the stall sampler is the interpreter's own unwinder where it ships one, staged or not; else the staged py-spy, nonblocking; else none` (`['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid'] / ['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid'] / None`). 3.14.6: `2 of 2472 ENTITY CHECKS FAILED`, the same check, plus `the lease has one winner, a dead gate is stolen, a live one is not, and run.sh runs unleased`, a gate-lease timing check this diff does not reach, run while three entities.py processes and prepr.sh shared the host; the unmutated head under 3.14.6 passed it in the same window (`ALL 2472 ENTITY CHECKS PASSED`), so it is load, not the mutant, and it is not claimed as a kill.
- The harness's N4 edit, which is the same predicate: `--mode N4 --inproc hung` under 3.14.6, 2 runs, `ok=0 fail=2`, readings `(True, True, False)` on every try, gaps 5298.3 to 5320.7 ms: the base's failure, back.

Restored: the mutant ran in a separate worktree; the head is unchanged.

## Null control

The unmodified base 486e65cbd, under the same harness and the same CPython 3.14.6:

- `--mode plain --inproc hung`: 3 runs, `ok=0 fail=3`, every try `(True, True, False)`, gaps 5292.5 to 5330.9 ms: the CI failure's signature (failing test first, at the base).
- `--mode plain --inproc real`: 10 runs, `ok=10 fail=0`, gaps 600.4 to 600.8 ms: the base passes on a py-spy that answers, so the hung arm, not the harness, is what reddens it.

At the head, the control still fails on a heartbeat that does not see a real spin (null controls of the control's power, `--inproc real`, 3.14.6, 2 runs each): N1 the spin stalls nothing, `ok=0 fail=2`, readings `(False, False, False)`; N2 the watcher never dumps, `ok=0 fail=2`, `(True, False, False)`; N3 the sampler reads a pid that does not exist, `ok=0 fail=2`, `(True, True, False)`.

## Figures

- Nightly history, stamped origin/main e5ddba1 at 2026-10-29T19:46Z. Enumerator: `gh run list --workflow nightly.yml -e schedule -L 100` and `-e workflow_dispatch -L 100` (push runs skip `nightly-ha`: `if: github.event_name != 'push'`), then per run `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs` for the two `nightly-ha (<image>)` jobs, and for a failed job its `FAILED: N of M checks: [...]` line (the lane exits 1 on any failed check). The brief's `gh run list --workflow nightly.yml -L 30` returns 30 runs of which 2 are non-push; the enumerator above returns every non-push run that exists, 14, the oldest 39890399205 (2026-10-23). Result: `hb:positive_control` failed in 1 of 14 runs (40806276912, `nightly-ha (stable)`), 1 of 14 `stable` jobs, 0 of 14 `2025.2.0` jobs. Null control of the enumerator: on the one run it counts, the job's own log line is `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`, so it does see the key when it fails; the 27 other jobs concluded `success`.
- Fix tree, `python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <head> --mode plain --inproc hung --runs 3 --out <dir>` under 3.14.6: `ok=3 fail=0`, one try each at 600.3 to 600.6 ms, sampler the interpreter: the py-spy that hangs is no longer the sampler. Null: the same command on the base, `ok=0 fail=3` (## Null control).
- Fix tree, `--mode plain --inproc real --runs 10` under 3.14.6: `ok=10 fail=0`. Null: the base, same command, `ok=10 fail=0`; the fix costs nothing on a healthy sampler.
- Fix tree under 3.13.17 (the floor, no `_remote_debugging`): `--inproc real --runs 3` `ok=3 fail=0`, `--inproc hung --runs 2` `ok=0 fail=2`, sampler py-spy: the floor keeps py-spy, and a py-spy hang there would still redden, as it should.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` prints `MODE: SCOPED -- 5 script(s) run, 28 scoped out.`; each of the five (`config_flow_steps.py`, `debug_collect.py`, `doc_claims.py`, `entities.py`, `harness_headers.py`) and the `run_always` lines (`layout.py`, `closure.py selftest`, `env_drift.py --claims-only <merge-base>`) exit 0 under 3.13 with `PYTHONPATH=tests/hastub`; `tests/entities.py` ends `ALL 2472 ENTITY CHECKS PASSED`. Under 3.14.6, where its unwinder arm runs instead of the 3.13 `else`: `ALL 2472 ENTITY CHECKS PASSED`, its unwinder check reading a real spinning child as `(True, True, True)` and the same child outside the spin as `(True, True, False)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`tests / nightly-status`: this diff touches none of what it reads (`policy_lint.mjs` `REPORTER_INPUTS`: `tests/nightly_status.py`, `tests/delivery_status.py`, `ci.yml`, `tests.yml`, `nightly.yml`, `governance.yml`, the plan, `HANDOVER.md`; it reads nightly.yml run and job records over the API, never `tests/nightly_ha.py` or the roster). Its red grades `main`. Two runs feed it: schedule 40806276912, red on `nightly-ha (stable)` `hb:positive_control`, which is this PR's subject; and the later main dispatch 40835853528, red on `slow`, step `Closed-loop simulation`, while its `nightly-ha (stable)` passed, a lane this diff does not touch and the orchestrator's on `main`. The cheaper detector for the `hb:positive_control` red: none deterministic exists. The hang is per HA process and was seen on 1 of 14 runs; the pull-request arm of `nightly-ha` in `tests.yml` runs the same control but catches a per-process hang only by chance, at the cost of one HA boot it already pays. The cause is upstream, py-spy 0.4.2 against CPython 3.14 (owner: the py-spy project); the fix stops depending on it where the interpreter ships its own unwinder. After merge, `gh workflow run nightly.yml --ref main` re-grades `main`.

## Forward-carry

- R10-NIGHTLY-HB-RESPAWN's premise (a respawn rescues a py-spy hang) is changed by this fix: its build is owed only if a `stable` nightly on a main carrying this fix again fails `hb:positive_control` with every try's sampler timed out or rc!=0. Carry: `dev/programme/rosters/wave-r10-groups.json` (R10-NIGHTLY-HB-RESPAWN `carry`, commit d63e5544d on this head). Its figures (4 processes, 24 of 24 probes) are the previous seat's and were not re-taken here. Carry: R10-NIGHTLY-HB-RESPAWN

## Friction

- environment.network: cost: `docker pull homeassistant/home-assistant:stable` returned 429 and `ghcr.io/home-assistant/home-assistant:stable` 403 on the blob host, so the group's container harness modes cannot run in a cloud seat; `--inproc` is the workaround that landed in the group's harness. Carry: dismissed: the harness now runs without the image, and the real HA run is the pull request's own nightly-ha arm
- fixer.md: unclear: `gh api .../actions/jobs/<id>/logs` is refused here (blob host 403), so job logs came through the MCP `get_job_logs`; the per-job count therefore keys on job conclusion plus the failed job's `FAILED:` line rather than on a `hb:positive_control` line in every log (step 3). Carry: dismissed: the count's rule is written in Figures and the enumerator sees the one failure it counts
