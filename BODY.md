The pull-request `tests / replay` job is cancelled at its 30-minute cap on most runs that reach it, returning no verdict. This raises the cap to 45 minutes, sized from the lane's own cost budget, and makes the lane check its own wall time against that cap every night, so the next growth is reported before the pull-request job times out. These are rungs 1 and 2 of P-R11-REPLAY-TIMEOUT, flow card FG-4. The owner approved FG-4 on 2026-11-26 with a tooling-freeze exception. `.github/` is code-owned, so the owner reviews this. Leaves #3885 open.

- Rung 1: `.github/workflows/tests.yml` sets `replay`'s `timeout-minutes` from 30 to 45. The size comes from the budget: the owner fixture's `COST_BUDGETS` `cpu_ratio` of 589.7, times the worst measured 3.83 s per unit (1738.5 s / 454.26 on the 2026-11-25 nightly), is 2258 s. Add about 1 min for setup and the synthetic fixture, and the budget allows 38.6 min. The uncensored observed maximum is 34.2 min (the 2026-11-17 nightly).
- Rung 2: `tests/replay.py`'s `main()` adds one check, `lane wall time within the pull-request replay job's headroom`. `replay_timeout_minutes` reads the cap from tests.yml's text, and `headroom_offenders` goes red when the wall time is over `REPLAY_HEADROOM_SHARE` (0.8) x (cap x 60 - `REPLAY_JOB_SETUP_S`, 20 s). It names the cap to raise, and a cap it cannot read is red. On the nightly `slow` job (150-min cap) it fires while the pull-request arm still finishes. Three `controls()` pairs pin the predicate, the unread cap and the job reader.
- `COST_ARMS_SKIPPED`'s "about 12 CPU-minutes a replay" is false now: the lane's own `cycles over` line reads 1426.5-1738.5 s. The figure is replaced by a pointer to that line, so the text cannot go stale again. The `COST_CUTS` evidence string that says "about 12 CPU-minutes a run" is a dated measurement record, so it stays as written (`fixer.md` step 10).
- Alternatives: P-R11-REPLAY-TIMEOUT rules out dropping the owner fixture from the pull-request arm, because that is a coverage loss and the owner's call. It also rules out sharding, because one fixture is about 97% of the lane and its cycles feed one cost mean. A check that compared the cap with `COST_BUDGETS` directly would need seconds per `cpu_ratio`, which the runner varies. Wall time against the cap measures the failure itself.
- No runner is added, and the required check set is unchanged: `replay` is in no `REQUIRED` set (`tools/ci/gate.py`, `tools/ci/prelude.py` `UNITS`). The diff adds no new file, touches no production code and leaves every `*_budgets.json` unchanged.

## Head

8b4cd6657c1aee2cf1d7be2cf9d00be830cc8784, merge base and `origin/main` dbdc71faea358a95a7b33840ed252b0d8a646a31, measured 2026-11-26T08:35Z.

## Mutation proof

- Predicate `if wall_s <= limit:` -> `if True:` in `headroom_offenders`, then `controls()` (`PYTHONPATH=tests/hastub python3 tests/replay.py` section "controls"): `control:headroom:over_the_cap` FAIL (`bad=[] good=[]`). The other 39 controls stay ok. Restored.
- Job reader regex `(?:    .*\n|[ \t]*\n)*?` -> `(?:.*\n)*?`, which lets the scan run into the next job: `control:headroom:reads_the_replay_job` FAIL (`read 45`). Restored. This mutant survived the first cut of the controls, which had no next job carrying a cap. The second commit adds that case.
- The check in `main()`, driven end to end (`main(["--fixture", "tests/replay/synthetic-dhw-only.json"])`) with `REPLAY_HEADROOM_SHARE` set to 0.0001: `FAIL lane wall time within the pull-request replay job's headroom [lane wall time 614.0 s > 0.0001 x (45 min - 20 s) = 0.3 s; raise the replay job's timeout-minutes to at least 102328]`. At 0.8: `ok   lane wall time within the pull-request replay job's headroom` (749.1 s).

## Null control

The check is demonstrated failing at the base's cap and passing at the head's, on every nightly lane wall time the proposal measured. `replay_timeout_minutes` reads 30 from `git show origin/main:.github/workflows/tests.yml` and 45 from the head:

- 2026-11-09 772.0 s: ok at 30, ok at 45
- 2026-11-16 836.1 s: ok at 30, ok at 45 (the null control: the lane before #3602's step doubled)
- 2026-11-19 1518.1 s: red at 30 (> 1424.0 s), ok at 45
- 2026-11-24 1476.4 s: red at 30, ok at 45
- 2026-11-25 1798.0 s: red at 30, ok at 45
- 2026-11-26 1751.8 s: red at 30, ok at 45

At 30 the check fires on every night from 2026-11-19. At 45 it fires on none (limit 2144.0 s).

## Figures

- Controls 40, 0 failing: `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path[:0]=['tests']; import replay as r; c=r.controls(); print(len(c), sum(not x[1] for x in c))"`
- Cap read at head 45 and at base 30, the two agreeing with PyYAML at the head: `python3 -c "import sys,yaml; sys.path[:0]=['tests']; import replay as r; t=open('.github/workflows/tests.yml').read(); print(r.replay_timeout_minutes(t), yaml.safe_load(t)['jobs']['replay']['timeout-minutes'])"`
- Null-control table above: `python3 -c "import sys,subprocess; sys.path[:0]=['tests']; import replay as r; b=r.replay_timeout_minutes(subprocess.run(['git','show','origin/main:.github/workflows/tests.yml'],capture_output=True,text=True).stdout); h=r.replay_timeout_minutes(open('.github/workflows/tests.yml').read()); [print(w, b, r.headroom_offenders(w,b) or 'ok', h, r.headroom_offenders(w,h) or 'ok') for w in (772.0,836.1,1518.1,1476.4,1798.0,1751.8)]"`. The wall times are the `replay lane wall time` lines of nightly `slow` runs 42542424086, 43783271327, 44432094532, 45300031206, 45521325964 and 45731557683.
- Gate scope `MODE: FULL` (tests.yml changes the gate itself): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. CI runs the full suite.
- Instrument self-test scope `MODE: SCOPED -- 31 step(s) run`: `python3 -I tools/ci/selftest_scope.py select --base $(git merge-base origin/main HEAD)`. Each named step's `run:` text from governance.yml ran at the head on this macOS host, which carried a load average of 30-54 from other seats. 25 were green, and `beatd` and `self-tests-outside-seat` were green on a direct run. Four steps fail with the same FAIL lines at the head and at `origin/main` dbdc71faea, so the host causes them, not this diff: `verdict-bus` (`bash tools/audit/seat/bus.sh --self-test`, 28 of 245, case-insensitive filesystem among them), `app-push` (`bash tools/pr/app_push.sh --self-test`, 2 of 235), `ci-predictor` (`python3 -I tools/pr/ci_predict.py --self-test`, 5) and `owner-only-channel` (`python3 -I dev/audit/harnesses/owner_only_channel.py`, the SCOPES arm's 120 s subprocess timeout). `prepr` (`bash tools/pr/prepr.sh --self-test`) is 569 passed, 2 failed at the head, both in the ancestry-reds fixture ("an ancestry no commit of which carries any check run skips, never refuses" and its skip line). A tree without this diff, 03697934d5, fails the same two plus two more of the same fixture's arms, and prepr.sh reads nothing this diff changes. CI's governance job is the authority for all of them.
- `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`
- No workflow linter (actionlint, zizmor) is in the tree or on this host. The workflow lint was the PyYAML parse above plus `tests/entities.py`'s workflow pins, which CI's full scope runs.
- Local lane run on a loaded macOS host, not CI's runner class: `synthetic-dhw-only.json: cycle_cost [cpu_ratio 2.376 over its budget 2.119]`. This is off-CI cost with a self-test run on the same host, and the replay job on this pull request grades it on CI.

## Red checks

none

## Forward-carry

none

## Friction

none
