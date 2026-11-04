R10-HOTFIX-CI-CRITPATH-4: main red at 8e90d8144, `tests / ci-ratchet` GREW critical_path_minutes 29.067 on 21.983 + 1.3 (CI run 41818271680), hours after #3180 re-based the grade. No work grew and no queue moved. The window lost its one fast-host draw of `tests / fast (3.14)`. #3180 priced each job at its fastest run in the 16-run window. Run 41491607650 (d40e377e5, `tests / fast (3.14)` 1223 s) aged out between the two newest windows, and the job repriced at its next-fastest draw, 1640 s, on the same work. The lane's 13 heaviest scripts, timed in the same runner, put its work flat across all 60 push runs (wall over its own scripts' speed: sd 2.9 %, against 17.5 % raw). The fleet's mix moved: the fast class (factors 0.50-0.61) was drawn in 10 of 60 runs and in 1 of the newest 26.

The fix changes what the grade measures, so runner draw cannot redden main:

- **A host probe in every heavy job.** `tests/host_probe.py` is fixed pure-Python work that refuses on its own checksum. It runs as a step of its own, `Probe the runner's speed (python X.Y)`, in `fast`, `arch-instrument`, `coverage` and `closures`, under the job's matrix interpreter. The jobs API already carries step timestamps into `runs.json`.
- **Probed pricing (`job_price`).** A probed job's work in reference-host seconds is its wall × `PROBE_REFERENCE_S[python]` / its probe's seconds, priced at the median over the window. A job with no probe step is priced as before.
- **Pricing over the window's observed needs**, not each run's last-ending chain.
- **The reference is measured on the fleet, and pinned.** Repair round 2: `PROBE_REFERENCE_S` is now `{"3.13": 22.12, "3.14": 22.40}`, derived by `tools/audit/seat/probe_bridge.py`'s stated rule from this PR's own probed CI runs, committed as `dev/audit/harnesses/r10_hotfix_ci_critpath_4/fleet.json`. Round 1's 17.50 / 18.92 came from a one-machine bridge, and the fleet refutes it by 22 % (review of 10e05b94f). `probe_bridge.py --self-test` runs in governance's `instrument-self-tests` on every pull request, re-derives the constant from the committed record, and refuses any tree value that differs by more than the rounding. `tests/ci_ratchet.py`, `probe_bridge.py` and `fleet.json` are now CODEOWNERS-owned beside `tests/host_probe.py`.

**What this does not do: it does not turn main green.** On the fleet-measured unit the pushes after the merge are predicted to keep reading GREW, at 25.644 and 25.993 against 23.283 (replay.py section 6). The cause is that `tests / closures` prices about 1400 reference-host seconds probed. The budget's window priced it at its fastest draw, 1117 s, which sits below the fleet's fast-class host. Round 1's predicted post-merge green came from the 21 %-low constant (the same windows read 22.252 / 22.633 under it). The budget is unchanged. The decision is the owner's under CLAUDE.md rule 2: re-record `critical_path_minutes` in the probed unit (reason in the commit message), or pay it with work cut on the closures / ci-ratchet path. No constant may be moved to clear it.

Method of the reference (`probe_bridge.py`'s docstring):
- **3.14**: each probed `tests / fast (3.14)` job's host factor is the median, over its scripts of >= 20 s, of seconds / that script's 60-run median (`fast_scripts.json`). The job implies reference = probe × UNIT / factor, where UNIT is 0.5645, the fast class's median factor. The tree's value is the median over jobs: 22.40, 22.43 and 20.72, giving 22.40. The 22.43 job ran on a fast-class host itself (factor 0.604, probe 24 s).
- **3.13**: no 3.13 job logs scripts with a 60-run history, so 3.13 is 3.14's value times the interpreters' probe ratio on the fleet. That ratio is the median ratio of the 3.13 and 3.14 heavy jobs' probe seconds paired by rank: 0.9875, giving 22.12. Rank pairing keeps the fleet's two-class mix (probes 22-24 s and 38-40 s) from landing a median in the gap. The ratio of medians (38 / 35.5 = 1.070, giving 23.98) is the alternative, and it lost on that ground; the self-test pins both readings.

Alternatives considered and why each lost:
- Re-record the budget at 29.x, or move the constant until main is green: both re-record merely to pass. The constant one is what round 1 did by accident and what this round pins against.
- A local bridge, re-measured: it does not transfer. The probe is pure Python while the scripts are solver-heavy, so the ratio is per machine (17.50 here, 18.29 on the reviewer's machine, 22.4 on the fleet).
- Computing `PROBE_REFERENCE_S` at import from `fleet.json`: this would put a harness data file in the grader's runtime path. A literal constant, pinned by a gate that re-derives it, keeps the grader's inputs explicit and its change reviewable.
- A longer window; in-runner script timings as the host factor; `actions/checkout` as a probe: as in round 1.

## Head

`ae7fa1331e5dec7c022909199f5b241e8df2addc`: the merge of origin/main d7582ed40 into this round's code head d02aeb9bb (by way of the earlier merge 3aaa204fe of 3583448e1), which sits on the bot head abf21ae34. Main's commits since 8e90d8144 touch none of this diff's files. Figures were taken at 3aaa204fe and d02aeb9bb (stamped `2026-11-04T16:44Z`); `tools/pr/prepr.sh` was rerun at this head after the merge.

## Mutation proof

Each mutant was applied in place on the committed tree, run through `python3 tools/audit/seat/probe_bridge.py --self-test` with `PYTHONDONTWRITEBYTECODE=1`, then restored with `git checkout`. The baseline and the restored tree each read 8 checks, 0 failed.
- `PROBE_REFERENCE_S["3.14"]` 22.40 -> 17.70 (-21 %): 1 failed, `FAIL the committed fleet record (3 probed fast (3.14) runs) re-derives ... -- 3.14: tree 17.7 derived 22.4`.
- 22.40 -> 27.10 (+21 %): 1 failed, `-- 3.14: tree 27.1 derived 22.4`.
- `["3.13"]` 22.12 -> 17.48 (-21 %): 1 failed, `-- 3.13: tree 17.48 derived 22.12`.
- 22.40 -> 22.42 (one rounding step past): 1 failed, `-- 3.14: tree 22.42 derived 22.4`.
- rank pairing -> ratio of medians: 2 failed, the two-class check and `-- 3.13: tree 22.12 derived 23.98`.
- the wall-clock table row never read: 1 failed, `FAIL a log tail holding only the wall-clock table reads the same seconds`.
- the host factor not divided out: 2 failed, the 40 s / 20 s check and `-- 3.13: tree 22.12 derived 21.74; 3.14: tree 22.4 derived 22.02`.

Failing test first: the new pin, written before the constant moved (round 1's 17.50 / 18.92 in place), read `FAIL ... -- 3.13: tree 18.92 derived 22.12; 3.14: tree 17.5 derived 22.4` (8 checks, 1 failed). Round 1's mutants of `tests/ci_ratchet.py` and the entities.py probe pins are untouched by this round: `ci_ratchet.py --self-test` reads every probe fixture through the symbol `PROBE_REFERENCE_S`.

## Null control

- In the self-test, round 1's one-machine 17.50 / 18.92 is refused by the same comparison that accepts the tree's value (`the one-machine bridge's 17.50 / 18.92 is refused`).
- In replay.py section 6, with each fully green fleet run as the merge run: every probed job 1.9x slower (wall and probe) moves the grade within the probe's 1 s rounding, while 300 s more `tests / closures` work moves it by all of it (300 × 22.12 / 22 / 60 = 5.03). Under the 21 %-moved constant, the same windows read 3.4 lower. That is the control showing the constant is load-bearing.
- replay.py sections 1-4 synthesise each run's probe from the reference itself, so they read the same at either constant: the grade there is wall × UNIT / factor.

## Figures

- `python3 dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py` -> `RESULT holds=1`, sections as listed in its docstring:
  - 1: at main, the newest window reads 29.067 and one run earlier 22.117; 41491607650 at 1223 s ages out.
  - 2: wall sd 17.5 %, wall over host factor sd 2.9 %, UNIT 0.565.
  - 3: newest window probed 20.35.
  - 4: every job probed (grade 19.118), slow fleet +0.026 (bound 0.624), hung run +0.000, +300 s at k=9 +2.30 and at k=12 +2.46, against +0.00 at main until 16.
  - 5: fleet.json, `3 probed fast (3.14) jobs imply 3.14 [22.4, 22.43, 20.72] -> 22.4; heavy-job probes {'3.13': [22.0, 22.0, 38.0, 38.0, 39.0, 39.0], '3.14': [22.0, 24.0, 32.0, 39.0, 39.0, 40.0]}; 3.13/3.14 rank ratio 0.9875 -> 3.13 22.12; in the tree ... agree`; the one-machine bridge reads 17.50, 22 % under the fleet.
  - 6: the merge push reads 29.067 against 23.283. Fleet run 41854976917 is not a stand-in (`tests / closures` failed). As the merge run, 41862133797 reads 25.644 (GREW), 22.252 under 17.50 / 18.92, 1.9x slower +0.456 (rounding 1.166), +300 s closures +5.027. 41862145105 reads 25.993 (GREW), 22.633, +0.949 (rounding 1.181), +5.144.
- `fleet.json` is the jobs API listing (`list_workflow_jobs`) of CI runs 41854976917, 41862133797 and 41862145105, cut to `tests/ci_ratchet.py`'s run fields. For each `tests / fast (3.14)` job, its `scripts_s` comes from the job log's tests/run.sh wall-clock table (the last 5000 lines; jobs 126662136647, 126687075621, 126687214067; 13 of 13 heavy scripts matched each).
- `python3 tools/audit/seat/probe_bridge.py --self-test` -> 8 checks, 0 failed.
- `python3 -I tests/ci_ratchet.py --self-test` -> 65 checks, 0 failed.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `112 self-testing, 112 wired, 0 unwired`, 0 index gaps
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> `ALL 112 HARNESS HEADER CHECKS PASSED`
- `python3 tools/pr/ci_predict.py` -> `no closures, fast, governance or instrument red predicted against 8e90d8144331 (a data-file read is not seen)`. `tests/harness_headers.py` reads replay.py's path, which `tests/closures.json`'s `inert_reads` already lists (abf21ae34). The new reads are `fleet.json`, by probe_bridge.py and replay.py, neither of them a suite script.
- `python3 tests/closure.py select --diff 8e90d8144` -> `MODE: FULL` (`.github/workflows/tests.yml changes the gate itself`), so the full suite is CI's.

## Red checks

- `tests / ci-ratchet` on main at 8e90d8144 (CI run 41818271680), GREW critical_path_minutes 29.067. This is the red this PR answers, and Carry 1 of the group's roster entry: the cause is the host-draw pricing above. The cheaper detector now exists: the probe makes the statistic draw-independent, and `replay.py` reproduces the miss offline. Its standing cost is one probe step per heavy job, 22-40 s per job on the fleet. This PR does not clear the red. On the fleet-measured unit the pushes after the merge are predicted GREW at 25.6-26.0 (above): a budget decision for the owner, carried below.
- Predicted: the merge commit's own `tests / ci-ratchet` reads GREW 29.067 (its window holds no probed run), and the pushes after it keep reading GREW until the owner's budget decision.
- `tests / closures` red at 10e05b94f (job 126662136815, `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/r10_hotfix_ci_critpath_4/replay.py`): UNDER-SCOPED, repaired by the `closures-autofix` bot's `abf21ae34 ci: re-record closures`. `tests / closures` concluded success at abf21ae34 in CI runs 41862133797 and 41862145105. The cheaper detector is `./tests/derive_closures.sh --single tests/harness_headers.py`; `ci_predict.py` does not see a data-file read and says so.
- `pr-contract / pr-contract` red at 10e05b94f (job 126686675448): `## Red checks` did not name `tests / nightly-status`. That is answered by the next line.
- `tests / nightly-status` (red or about to be; this diff touches `.github/workflows/tests.yml` and `.github/workflows/governance.yml`, both in `policy_lint.mjs`'s `REPORTER_INPUTS`, so the main-state exemption is void here and an answer is owed). It reports the last concluded scheduled Nightly run: run 41749544997 (2026-11-04T00:48Z, at c3a279e32), job `slow`, `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 3.382 over its budget 2.173]`, `1 of 176 replay checks FAILED`. That is main's inherited red (the cycle_cost cpu_ratio budget, runner noise, re-centred by #3174), not this branch's. This diff cannot reach it: it is a past scheduled run's conclusion, `nightly.yml` and `tests/nightly_status.py` are untouched, and the diff's edits to tests.yml and governance.yml add a probe step, a ci-ratchet pricing change and a self-test comment, none of which alters what the reporter reads. The repair is the orchestrator's, on main: fix the nightly lane and dispatch Nightly on the default branch.

## Review findings (10e05b94f)

- PROBE_REFERENCE_S 21 % low: re-derived on the fleet from this PR's probed CI runs (`fleet.json`, the rule in probe_bridge.py), now 22.40 / 22.12. The post-merge prediction is re-run under it and reads GREW, stated above and carried. Carry: R10-HOTFIX-CI-CRITPATH-4
- No gate checked the constant's value: `probe_bridge.py --self-test` (governance, every PR) now refuses a constant that the committed fleet record does not re-derive, and the reviewer's 17.50 -> 21.0 class of mutant is killed (Mutation proof). `tests/ci_ratchet.py`, `probe_bridge.py` and `fleet.json` are now owned in `.github/CODEOWNERS`, so a PR moving the constant and the record together needs the owner's review. Carry: R10-HOTFIX-CI-CRITPATH-4
- host_probe.py's docstring: it now says the probe runs after setup-python under the job's matrix interpreter, and it names `reference_work`. Carry: R10-HOTFIX-CI-CRITPATH-4
- `tests / nightly-status` unnamed: named in Red checks with its cause and owner. Carry: R10-HOTFIX-CI-CRITPATH-4
- `tests / closures` red: repaired by the bot at abf21ae34 and green there (Red checks). Carry: R10-HOTFIX-CI-CRITPATH-4
- Timing-inferred need edges unioned across the window: not built here. replay.py section 6's paths show it (`budget-raise-gate` or `validate-hacs`, about 30 s, ahead of `tests / closures`). It is carried to #201 with the declared-`needs:` guard as its remedy. Carry: R10-HOTFIX-CI-CRITPATH-4

## Forward-carry

- The post-merge GREW (25.6-26.0 predicted on the fleet unit) and the owner's budget decision under CLAUDE.md rule 2; re-deriving `PROBE_REFERENCE_S` from probed push runs once eight exist (`probe_bridge.py --repo`, a new `fleet.json` and the constant in one PR); and the need-edge guard. Carry: #201 (`dev/programme/carries/carry-201.json`, the entry `from` R10-HOTFIX-CI-CRITPATH-4)

## Friction

none
