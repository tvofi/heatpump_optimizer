The pull-request `tests / replay` job is cancelled at its 30-minute cap on most runs that reach it, returning no verdict. This raises the cap to 60 minutes, sized from the lane's own cost budget on the slowest runner on record, and makes the lane check its own wall time against that cap every night, so the next growth is reported before the pull-request job times out. These are rungs 1 and 2 of P-R11-REPLAY-TIMEOUT, flow card FG-4. The owner approved FG-4 on 2026-11-26 with a tooling-freeze exception. `.github/` is code-owned, so the owner reviews this. Leaves #3885 open.

- Rung 1: `.github/workflows/tests.yml` sets `replay`'s `timeout-minutes` from 30 to 60. The size comes from the budget on the slowest runner on record: this PR's own replay job 139918878679 (run 45821055133) landed on a `ref47` runner (`ref_ms` 46.75) and read the owner fixture's 16 cycles in 2424.3 s at `cpu_ratio` 532.0, 4.56 s per unit, where the nightly `ref31` runs read 3.4-3.8. Scaled to the `COST_BUDGETS` `cpu_ratio` of 589.7, plus the rest of the lane's 81.0 s, the lane at budget is 2768.1 s (`budget_wall_s`, `REPLAY_SIZING_DRAW`), so the check below needs at least 59 min; 60 is that plus one. The first cut sized 45 from the nightly runs only, and that job's own headroom check went red at 2505.3 s (see `## Red checks`).
- Rung 2: `tests/replay.py`'s `main()` adds one check, `lane wall time within the pull-request replay job's headroom`. `replay_timeout_minutes` reads the cap from tests.yml's text, and `headroom_offenders` goes red when the wall time is over `REPLAY_HEADROOM_SHARE` (0.8) x (cap x 60 - `REPLAY_JOB_SETUP_S`, 20 s). It names the cap to raise, and a cap it cannot read is red. On the nightly `slow` job (150-min cap) it fires while the pull-request arm still finishes. Three `controls()` pairs pin the predicate, the unread cap and the job reader.
- `COST_ARMS_SKIPPED`'s "about 12 CPU-minutes a replay" is false now: the lane's own `cycles over` line reads 1426.5-1738.5 s. The figure is replaced by a pointer to that line, so the text cannot go stale again. The `COST_CUTS` evidence string that says "about 12 CPU-minutes a run" is a dated measurement record, so it stays as written (`fixer.md` step 10).
- Alternatives: P-R11-REPLAY-TIMEOUT rules out dropping the owner fixture from the pull-request arm, because that is a coverage loss and the owner's call. It also rules out sharding, because one fixture is about 97% of the lane and its cycles feed one cost mean. Seconds per `cpu_ratio` vary with the runner class, so the cap is checked against the budget only at the slowest draw on record (`control:headroom:cap_covers_the_budget`), and a slower class is caught by the wall-time check, not predicted. Wall time against the cap measures the failure itself.
- No runner is added, and the required check set is unchanged: `replay` is in no `REQUIRED` set (`tools/ci/gate.py`, `tools/ci/prelude.py` `UNITS`). The diff adds no new file, touches no production code and leaves every `*_budgets.json` unchanged.

## Head

`bbb99796c9b249495ac3b45484713a3af0924f45` is this PR's code head: the repair commit over `8e0391b08fa316937564766964e3e13c3a1fb97d`, which raises the cap to 60 and adds `control:headroom:cap_covers_the_budget` after the replay job's red on run 45821055133.

Merge base with `origin/main` 1d3077736d, measured 2026-11-26T13:52Z.

## Mutation proof

- Predicate `if wall_s <= limit:` -> `if True:` in `headroom_offenders`, then `controls()` (`PYTHONPATH=tests/hastub python3 tests/replay.py` section "controls"): `control:headroom:over_the_cap` FAIL (`bad=[] good=[]`). The other 39 controls stay ok. Restored.
- Job reader regex `(?:    .*\n|[ \t]*\n)*?` -> `(?:.*\n)*?`, which lets the scan run into the next job: `control:headroom:reads_the_replay_job` FAIL (`read 45`). Restored. This mutant survived the first cut of the controls, which had no next job carrying a cap. The second commit adds that case.
- The check in `main()`, driven end to end (`main(["--fixture", "tests/replay/synthetic-dhw-only.json"])`) with `REPLAY_HEADROOM_SHARE` set to 0.0001: `FAIL lane wall time within the pull-request replay job's headroom [lane wall time 614.0 s > 0.0001 x (45 min - 20 s) = 0.3 s; raise the replay job's timeout-minutes to at least 102328]`. At 0.8: `ok   lane wall time within the pull-request replay job's headroom` (749.1 s).

- Repair (commit `bbb99796c9`), controls run by `MUTANT_CMD` (`controls()` with exit 1 on any failing control), 8 of 8 hand mutants killed, each restored: cap 60 -> 45 (the base of this repair) and 60 -> 58; `budget_wall_s` without the budget scaling and without `rest_s`; `owner_s` 2424.3 -> 2224.3; `rest_s` -> 0.0; `owner_cpu_ratio` -> the budget; the control's bad cap 57 -> 60. Before the cap moved, the new control failed at 45 (`good=["lane wall time 2768.1 s > 0.8 x (45 min - 20 s) = 2144.0 s; ... at least 59"]`).
- `diff mutants`: `tools/audit/seat/mutant_run.py --diff ... --max-mutants 40 --report-only` lists no site and exits 0: its `SKIP_PREFIXES` excludes `tests/`, and the diff touches no other Python. The hand mutants above are the measured proof.

## Null control

The check is demonstrated failing at the base's cap and passing at the head's, on every nightly lane wall time the proposal measured. `replay_timeout_minutes` reads 30 from `git show origin/main:.github/workflows/tests.yml` and 45 from the head:

- 2026-11-09 772.0 s: ok at 30, ok at 45
- 2026-11-16 836.1 s: ok at 30, ok at 45 (the null control: the lane before #3602's step doubled)
- 2026-11-19 1518.1 s: red at 30 (> 1424.0 s), ok at 45
- 2026-11-24 1476.4 s: red at 30, ok at 45
- 2026-11-25 1798.0 s: red at 30, ok at 45
- 2026-11-26 1751.8 s: red at 30, ok at 45

At 30 the check fires on every night from 2026-11-19. At 45 it fires on none (limit 2144.0 s).

At 60 the check also holds on the slow-runner draw: 2505.3 s is under the 2864.0 s limit, and the lane at budget on that runner, 2768.1 s, is under it too. At 45 both are red. Other pull requests' replay jobs on main's 30-minute cap, 2026-11-26 07:07Z-13:31Z: of 20 besides this one, 9 were cancelled at the cap (30m12s-30m16s), 7 were green in 19m31s-29m44s and 4 were cancelled before they started, so the 30-minute cap is the failure this PR removes.

## Figures

- Controls 41, 0 failing: `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path[:0]=['tests']; import replay as r; c=r.controls(); print(len(c), sum(not x[1] for x in c))"`
- Cap read at head 45 and at base 30, the two agreeing with PyYAML at the head: `python3 -c "import sys,yaml; sys.path[:0]=['tests']; import replay as r; t=open('.github/workflows/tests.yml').read(); print(r.replay_timeout_minutes(t), yaml.safe_load(t)['jobs']['replay']['timeout-minutes'])"`
- Null-control table above: `python3 -c "import sys,subprocess; sys.path[:0]=['tests']; import replay as r; b=r.replay_timeout_minutes(subprocess.run(['git','show','origin/main:.github/workflows/tests.yml'],capture_output=True,text=True).stdout); h=r.replay_timeout_minutes(open('.github/workflows/tests.yml').read()); [print(w, b, r.headroom_offenders(w,b) or 'ok', h, r.headroom_offenders(w,h) or 'ok') for w in (772.0,836.1,1518.1,1476.4,1798.0,1751.8)]"`. The wall times are the `replay lane wall time` lines of nightly `slow` runs 42542424086, 43783271327, 44432094532, 45300031206, 45521325964 and 45731557683.
- Gate scope `MODE: FULL` (tests.yml changes the gate itself): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. CI runs the full suite.
- Instrument self-test scope `MODE: SCOPED -- 31 step(s) run`: `python3 -I tools/ci/selftest_scope.py select --base $(git merge-base origin/main HEAD)`. Each named step's `run:` text from governance.yml ran at the head on this macOS host, which carried a load average of 30-54 from other seats. 25 were green, and `beatd` and `self-tests-outside-seat` were green on a direct run. Four steps fail with the same FAIL lines at the head and at `origin/main` dbdc71faea, so the host causes them, not this diff: `verdict-bus` (`bash tools/audit/seat/bus.sh --self-test`, 28 of 245, case-insensitive filesystem among them), `app-push` (`bash tools/pr/app_push.sh --self-test`, 2 of 235), `ci-predictor` (`python3 -I tools/pr/ci_predict.py --self-test`, 5) and `owner-only-channel` (`python3 -I dev/audit/harnesses/owner_only_channel.py`, the SCOPES arm's 120 s subprocess timeout). `prepr` (`bash tools/pr/prepr.sh --self-test`) is 569 passed, 2 failed at the head, both in the ancestry-reds fixture ("an ancestry no commit of which carries any check run skips, never refuses" and its skip line). A tree without this diff, 03697934d5, fails the same two plus two more of the same fixture's arms, and prepr.sh reads nothing this diff changes. CI's governance job is the authority for all of them.
- `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`
- No workflow linter (actionlint, zizmor) is in the tree or on this host. The workflow lint was the PyYAML parse above plus `tests/entities.py`'s workflow pins, which CI's full scope runs.
- Local lane run on a loaded macOS host, not CI's runner class: `synthetic-dhw-only.json: cycle_cost [cpu_ratio 2.376 over its budget 2.119]`. This is off-CI cost with a self-test run on the same host, and the replay job on this pull request grades it on CI.

## Red checks

- `tests / replay`, run 45821055133, job 139918878679, red after 42m10s: caused by this PR, and repaired. 201 of 202 checks passed; the one red was this PR's own `lane wall time within the pull-request replay job's headroom` (`lane wall time 2505.3 s > 0.8 x (45 min - 20 s) = 2144.0 s; raise the replay job's timeout-minutes to at least 53`). The job landed on a `ref47` runner (`ref_ms` 46.75 against the nightly's 30.9), where the owner fixture costs 4.56 s per `cpu_ratio` unit; the 45 was sized from `ref31` nightlies only. The owner fixture's `cpu_ratio` was 532.0, inside its 589.7 budget, so no cost regression. The null control is main: no `tests / replay` ran on main (each main CI run skips it, it is pull-request only), and on other pull requests the job is cancelled at main's 30-minute cap. The repair raises the cap to 60, sized on this draw at budget, and adds `control:headroom:cap_covers_the_budget`, which refuses 45 and 58.

## Forward-carry

none

## Friction

none

