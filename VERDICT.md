Fix review: merge f6e26053c165f43a2f65f87a9b9777b198db9b05

bus-nonce: f89c2f2b6216f3e2ad43600a56c497d2
pending-ci: gate

## Round

First round (full review; review_packet `Review scope: full`). Roles at the merge base are current (`git diff <mb>...origin/main -- dev/governance/roles/` empty).

## Findings

- Follow-up: the health signal is job-queued age of the run to cancel (`ci_pause.queued_minutes` >= `pause_queued_min` 5), and it cannot tell "GitHub is not granting runners" from "this account's concurrent-job limit is full". Measured on main at 16:39 UTC: the in-progress main run 45632212603 had all 30 jobs created at 16:01:46 and its last two started at 16:26:29 and 16:27:59, a 25-minute queue under saturation while the next push's run 45652073996 sat `pending` in `CI-main` (ev/run45632212603_jobs.tsv). Under that load the gate refuses the cancel exactly when it would free runners for the held run, so the body's "about 740 job-minutes (about 13%)" saving, taken from the brief before the gate existed, is an upper bound that the gate can shrink. The direction is fail-safe: a refusal leaves the pre-PR behaviour (no cancel), never a lost verdict, so I judge it acceptable as a conservative first cut and do not block. The control a follow-up needs: count, over main pushes, the cancels `main` would have made with the gate and without it, splitting queued time into saturation (other repository jobs in progress at the limit) and no-grant (none in progress). Carry: #3885
- Follow-up: own mutant `next((w for ... ) if w), "")` -> `next((w for ...), "")` (check only the first run in `p["cancel"]`) survives the self-test (87 checks, 0 failed): every #3885 case has one run to cancel. Under ci.yml's `CI-main` group at most one older run is active, so the push path does not reach it; a by-hand run over another `--workflow` can. One self-test case with two cancellable runs, the second unhealthy, would kill it. Carry: #3885
- Residual: own mutants `age >= setting` -> `age > setting` (the boundary at exactly `pause_queued_min`) and the `mine` filter dropped to every listed run (the API listing is already `branch=main&event=push`) both survive; the first is a boundary on a continuous age and the second is equivalent under the listing's own filter. Carry: dismissed: equivalent or boundary-only mutants, no reachable behaviour change

## Evidence

- RESULT self-test at head: `cancel_superseded self-test: 87 checks, 0 failed` (ev/selftest.txt), matching the body.
- RESULT mutation proof at head: `python3 dev/audit/harnesses/r11_main_cancel_mutants.py` -> M0 null-ok, mutants=18, survived=0; each of the seven #3885 mutants killed by 1 to 4 checks (ev/mutants.txt), matching the body.
- RESULT own mutants: 3 run, 3 survived, dispositioned under Findings (ev/own_mutants.txt).
- Null control: the base `main_arm` takes no `sleep`/`now`/`setting` keywords (the diff adds them), so the head's self-test against base production raises the `TypeError` the body quotes; I read this from the diff and did not splice-run it.
- Design question (1), the health signal: judged above (Findings, first item) as acceptable, fail-safe, carried.
- prelude scope in main-cancel.yml: the job provides every variable `prelude.py` reads on a push (GITHUB_EVENT_PATH/NAME, GITHUB_SHA, token, full history). It differs from ci.yml's prelude in `GITHUB_RUN_ID` (main-cancel's own) and in timing: it runs while the older run is still active, so `push_range` skips it and measures from the last completed run. When the cancel happens, the older run ends `cancelled`, which `push_range` also skips, so ci.yml's prelude later measures the same range and grades the push `full` as well. When nothing is cancelled, the difference changes nothing. An unreadable prelude (rate-limit exit 3, a traceback) yields `unknown`, which cancels nothing (self-test case).
- Finder's harness: none named (CI workflow change from the #3885 brief); the 26-push basis is describe-only with no enumerator in the tree, as the body states, and I did not re-derive it.
- Merge with main: `git merge-tree --write-tree origin/main f6e26053c1` exits 0 (tree 27e610c0749e3bc0cf8b6bc2f66224b592f2ecce).
- VERSION, manifest, RELEASE_NOTES.md and both claim files are untouched (three-dot diff empty).
- Closures: `.github/workflows/main-cancel.yml` was added to the two recorded closures that list every workflow; earned by the new file.
- Scoped gate (question 2): `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=d2128054db ./tests/run.sh` at the head on this host: `MODE: SCOPED -- 3 script(s) run, 31 scoped out`, `6 TEST SCRIPT(S) PASSED`, exit 0 (ev/gate.log). `tests/entities.py` ran in full and passed in 693 s, with no timing failure; `harness_headers.py` passed in 174 s. The fixer's prepr timeout and the one-off entities.py timing failure did not recur here. The `FAIL hb:positive_control` / `hb:changed_save` lines in the log are retried sampler probes inside a passing script (exit 0), not a gate failure.
- CI at this head: `merge_train.py classify f6e26053c165f43a2f65f87a9b9777b198db9b05 --pr 3899` printed `WAIT f6e26053c165f43a2f65f87a9b9777b198db9b05 pending: gate red: none` (rc 3) on every run from 16:38 to 17:08 UTC (ev/classify.log), so this verdict carries `pending-ci: gate` for the relay. Own CI is waived for #3885 PRs per the dispatch.
- Red checks: none at the head (classify `red: none`); the body's `## Red checks: none` agrees. Owed-reds set saved in ev/owed-reds.txt.
