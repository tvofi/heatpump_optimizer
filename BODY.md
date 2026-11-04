R10-HOTFIX-CI-CRITPATH-4: main red at 8e90d8144, `tests / ci-ratchet` GREW critical_path_minutes 29.067 on 21.983 + 1.3 (CI run 41818271680), hours after #3180 re-based the grade. No work grew and no queue moved. The window lost its one fast-host draw of `tests / fast (3.14)`. #3180 priced each job at its fastest run in the 16-run window. Run 41491607650 (d40e377e5, `tests / fast (3.14)` 1223 s) aged out between the two newest windows, and the job repriced at its next-fastest draw, 1640 s, on the same work. The lane's 13 heaviest scripts, timed in the same runner, put its work flat across all 60 push runs (wall over its own scripts' speed: sd 2.9 %, against 17.5 % raw). The fleet's mix moved: the fast class (factors 0.50-0.61) was drawn in 10 of 60 runs and in 1 of the newest 26. #3180's reviewer predicted 22.35 at the second push, and the miss is that draw.

The fix changes what the grade measures, so runner draw cannot redden main:

- **A host probe in every heavy job.** `tests/host_probe.py` is fixed pure-Python work that refuses on its own checksum. It runs as a step of its own, `Probe the runner's speed (python X.Y)`, in `fast`, `arch-instrument`, `coverage` and `closures`. The jobs API already carries step timestamps into `runs.json`, so no new data channel is needed.
- **Probed pricing (`job_price`).** A probed job's work in reference-host seconds is its wall × `PROBE_REFERENCE_S[python]` / its probe's seconds, and the job is priced at the median of that over the window. The median replaces the minimum because host speed is already divided out: a hung run does not move it, and growth reads at half the window instead of after every fast draw has aged out. A job with no probe step is priced as before.
- **Pricing over the window's observed needs, not each run's last-ending chain.** Which job ends last is itself a draw (a lane queued behind a slow sibling hides a longer one), so the old per-run chain read the host draw a second way. The grade is now the longest path through every need edge the window observed.
- **The unit is kept.** `PROBE_REFERENCE_S` is the probe's seconds on the fleet's fast class, the host the shipped grade priced each lane on. So 21.983 + 1.3 keeps its meaning and nothing is re-recorded.

Alternatives considered and why each lost:
- Re-record the budget at 29.x: re-records merely to pass, and the next fast draw would make it slack.
- A longer window: fast draws ran at about 1 in 26, and a longer window only delays the same red while lengthening the growth lag.
- In-runner per-script timings as the host factor: these are proven on 60 runs for `fast (3.14)`. But `closures` logs no per-script seconds and `arch-instrument` is one script, so this cannot cover every lane.
- `actions/checkout` as a free historical probe: measured sd 10.8 % against 2.9 %.

## Head

`990f6948fef6afa2f0d109a486e76b072c24049f`, measured against main 8e90d8144 (origin/main unmoved since this seat's base; stamped `2026-11-04T13:56Z`).

## Mutation proof

Each mutant was applied in place to `tests/ci_ratchet.py`, run through `python3 tests/ci_ratchet.py --self-test`, then restored with `git checkout`:
- `seen = reference or walls` -> `seen = walls` (probed price ignored): 3 failed, e.g. `FAIL a fleet 1.9x slower on the same work does not move the grade -- 32.15 -> 60.817`.
- `reference_work` returns `None`: 5 failed, e.g. `FAIL losing the window's one fast draw moves a probed grade by under 1 % ... -- 19.417 -> 32.15`.
- the need edge never recorded (`needs[...].add(...)` -> `pass`): 15 failed, e.g. `FAIL a longer path that never ended its run still sets the grade (30.5, not 21.5) ... -- 30.0, 20.0`.
- probed price at the minimum, not the median: 1 failed, `FAIL 300 s more work in 9 of 16 runs grows the grade by all of it ... -- 28.169 -> 28.169`.

Each tests/entities.py probe pin was mutated in place, its block run (the pin's own lines, executed by a driver over the tree), then restored:
- `arch-instrument`'s step renamed `(python 3.15)`: `FAIL arch-instrument: probe steps ['3.15'], python ['3.14']`.
- `coverage`'s probe step deleted: `FAIL coverage: probe steps [], python ['3.13']`.
- the probe's work changed (`range(60_000)` -> `range(60_001)`): the one-round checksum pin `FAIL got 4289037`, and `python3 tests/host_probe.py` refuses with exit 1 (`checksum ... is not the recorded ...`).

## Null control

- At main the same 60 runs read 29.067 in the newest window and 22.117 one run earlier (replay.py section 1). This tree reads the same window identically while no run carries a probe ("this tree unprobed", section 3), so the change moves nothing until a probe step exists.
- In the self-test, the fixture that reproduces the red unprobed (`the same windows unprobed reproduce the red ... moves over 30 %`) is the control for the probed check beside it.
- In the DAG check, shortening the longer lane to 10 minutes returns the last job's path (21.5).
- In entities.py, the probe-step rule finds no step in `ci-ratchet`.

## Figures

- `python3 dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py` -> `RESULT holds=1`. It replays tests/ci_ratchet.py's own statistic over the 60 completed ci.yml push runs 41331759691..41818271680 in `runs.json`, with `fast_scripts.json` holding each run's fast-lane script seconds from its job log. It reads:
  - Section 1: the newest window at main reads 29.067; one run earlier it read 22.117; the run ageing out is 41491607650 at 1223 s.
  - Section 2: wall sd 17.5 %, wall over host factor sd 2.9 %, UNIT 0.565.
  - Section 3: newest window probed 20.35 against 29.067.
  - Section 4, every job probed: slow fleet 1.9x reads -0.108 (1 s rounding bound 0.802), one hung run +0.000, and +300 s of growth reads +2.23 at 9 of 16 runs and +2.56 at 12, where main reads +0.00 until 16.
  - Section 5: the bridge derives 17.50 / 18.92, equal to the tree's.
  The other lanes carry no host history, so section 3 leaves them at their fastest draw. That is why its window maximum stays 29.783, the same as at main.
- `python3 tests/ci_ratchet.py --self-test` -> 65 checks, 0 failed.
- `python3 tools/audit/seat/probe_bridge.py --self-test` -> 4 checks, 0 failed.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> 112 self-testing, 112 wired.
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> ALL 112 HARNESS HEADER CHECKS PASSED.
- `./tests/derive_closures.sh --single tests/entities.py` -> entities.py recorded at rc 0 (its `tests/closures.json` timing entry), with `tests/host_probe.py` in its closure; at the commit before it, the run's one failure was `every tracked file is either measured or deliberately classified [... tests/host_probe.py]`.
- `python3 tools/pr/ci_predict.py` -> no closures, fast, governance or instrument red predicted against 8e90d8144331.
- The bridge (`dev/audit/harnesses/r10_hotfix_ci_critpath_4/bridge.json`) uses the two scripts tests/run.sh runs alone on the box, as CI runs the probe step. Timed alone here, they read this machine at 0.87 and 0.72 of the fleet's factor-1 host, so the grade's level carries about 9 % uncertainty. The three-wide parallel arm spans 0.58..1.27 and is disclosed, not used. `tools/audit/seat/probe_bridge.py --repo tvofi/heatpump_optimizer` re-derives the value on the fleet itself once probed runs exist (see Forward-carry).

## Red checks

- `tests / ci-ratchet` on main at 8e90d8144 (CI run 41818271680), GREW critical_path_minutes 29.067. This is the red this PR answers, and Carry 1 of the group's roster entry: the cause is the host-draw pricing above. The cheaper detector exists now: the probe makes the statistic draw-independent, and `replay.py` reproduces the miss offline. Its standing cost is one probe step per heavy job: PROBE_REFERENCE_S's 17.5 s on the fast class, about 31 s (17.5 / UNIT 0.565) on a factor-1 host.
- Predicted: the merge commit's own `tests / ci-ratchet` reads GREW once more, because the grade never sees its own in-progress run and the window holds no probed run yet. This is not a regression. The next push clears it without a re-record (carried, below).


## Forward-carry

- The merge push's predicted ci-ratchet red, and replacing the one-machine bridge with `probe_bridge.py`'s fleet measurement once eight or more probed runs exist. Carry: #201 (`dev/programme/carries/carry-201.json`, the entry `from` R10-HOTFIX-CI-CRITPATH-4).

## Friction

none
