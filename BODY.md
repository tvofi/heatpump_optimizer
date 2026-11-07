Root-cause record for the recurring-friction key `ci-red` (#3156), the one `R10-RCA-FRICTION-SWEEP.md` section 4b left to its own group. It re-derives the count at this merge base, names each of the 18 entries' PR and red check, and finds one verdict word covering four mechanisms. It lands a record, its evidence and one reader script, and changes neither the keying rule nor the gate. Disposes #3156

## Head

`e3094246142cdfa6028f8c92bf9a42b0d548f2c7` (PR head: code `809d977725797d0eae4339a9b5507eec41f0a159` plus the delivery row `dev/programme/delivery/3295.md`; `origin/main` `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76` merged in; every figure below re-taken at this head, 2026-11-07).

## Mutation proof

n/a: no production line changes; the diff is one record, its evidence under `dev/audit/rca/ci-red/` and `entries.py`, a reader. The reader's own control: asked for the misspelt key `ci-redd` it prints `ENTRIES 0 PRS 0`, against `ENTRIES 18 PRS 14` for `ci-red`.

## Null control

The unmodified tree has no `ci-red` record. The histogram row (14 / 18) is the control for the reader: `entries.py` returns the same two numbers independently, and its (PR, head, gap) columns were identical across two runs at `b4ec2f332` and `4b5d771bd`.

## Figures

- `node tools/policy/policy_lint.mjs --stats --since v7.1.2`: 93 merged PRs, `ci-red` 14 PRs / 18 entries (`dev/audit/rca/ci-red/stats_v7.1.2.txt`).
- `python3 -I dev/audit/rca/ci-red/entries.py W.json ci-red`, W.json written by the `--window-cache` flag of the command above: `ENTRIES 18 PRS 14` (`dev/audit/rca/ci-red/entries_v7.1.2.tsv`).
- Four causes (8 / 4 / 4 / 2 entries) are read from the verdict first lines in that table; groups and their mean minutes (212, 110, 297) are sums of its fourth column.
- `python3 -c "import sys; sys.path.insert(0,'tests'); import harness_headers as h; print(h.inline_scan())"` with `PYTHONPATH=tests/hastub`: prints `0`, 0.55 s; `python3 tests/harness_headers.py`: 1m59s, "ALL 112 HARNESS HEADER CHECKS PASSED".
- `bash tools/pr/prepr.sh` on a committed tree: `rc=0` at `49141f365`; main then moved by a triage-only merge (`git diff --stat b4ec2f332..origin/main`: delivery and triage notes), so it was merged in and prepr is rerun with this body.
- `git diff --shortstat origin/main...HEAD` at `e3094246`: 5 files changed, 347 insertions(+), 0 deletions; paths `dev/audit/rca/R10-RCA-CI-RED.md`, `dev/audit/rca/ci-red/{entries.py,entries_v7.1.2.tsv,stats_v7.1.2.txt}`, `dev/programme/delivery/3295.md`. Nothing under `.github/`, `tools/`, `tests/` or production code.
- `grep -c '^#[0-9]' dev/audit/rca/ci-red/entries_v7.1.2.tsv`: 18, and the file's last line reads `ENTRIES 18 PRS 14`.

## Red checks

The diff adds an RCA record, its evidence and the delivery row, and no file any workflow executes; the `dev/audit/rca` and `dev/programme/delivery` strings in `.github/workflows/*.yml` are comments, and `nightly.yml` writes delivery rows only on its own record run. So no red below is caused by this diff, each answered from the job logs. Check-runs read from `get_check_runs` and `list_workflow_jobs` (filter all) on run 42395767077 at the head.

- `tests / nightly-status` (jobs 128472881028 attempt 1, 128483785307 attempt 2, 128486658442 attempt 3; concluded failure each time). Class: nightly status reading a verdict older than this PR, unrequired on `main-protect`. Cause: the log prints `NIGHTLY FAILED: mutation-ledger (1), mutation-ledger (2), mutation-ledger (3), mutation-ledger (4), mutation-ledger-push, mutation-nightly, slow failed in the last verification dispatch`, all seven jobs `cancelled`, from dispatched run 42369836867 (2026-11-07T11:50:04Z, head `08fd676`, conclusion `cancelled`; run 42382408131 was still in flight). That run predates this branch and tests a different head, and the diff touches nothing the nightly reads, so it cannot have caused or can clear it. No verification dispatch run exists for this head and none is owed: the lanes are untouched. Answer: external to this change; owned by the nightly lane. The cause of the cancelled dispatch is not established here. Carry: #3156.
- `governance / instrument-self-tests` (job 128472881084 attempt 1, 128483761614 attempt 2; both concluded cancelled at 2026-11-07T17:45:13Z, started 17:20:39Z; attempt 3 job 128486658258 started 18:15:40Z and was still in progress at this read). Class: cancelled, not a failing self-test. The attempt-1 log shows the last self-test step finish `SELF-TEST: 55 probe(s), 15 null(s), 0 wrong` and the preceding step `13 passed, 0 failed` at 17:45:11Z, two seconds before the job was cancelled; no self-test failed. The `gate` job 128478979568 of the same run was cancelled at the same second, 17:45:13Z, so the run was cancelled externally, not by a job's own result. The diff touches no self-tested instrument. Whether attempt 3 clears it is not known at this read.
- `gate` (job 128478979568, concluded cancelled at 17:45:13Z, same second as the above). Class: the gate's edit/code deferral race, cleared by a later run: the edit-kind gate in run 42397799719 (job 128481636534, KIND edit, WORKSET `arch-score budget-raise-gate pr-contract`) concluded success at 17:57:13Z with `PASS`, and the gate in run 42395769305 (job 128483764621, KIND edit, WORKSET `arch-score budget-raise-gate`) concluded success at 18:08:35Z with `PASS`. Neither gate log shows a "still being judged" line, so I cannot show the deferral message itself, only that the cancelled gate was superseded by two passing ones across the two runs.
- Skipped jobs (`kernel-points`, `codeql`, `validate`, `hassfest`, `pr-contract`, `governance`, `tests` in run 42395769305, and the scoped-out jobs of run 42395767077) are `skipped`, not red.

## Forward-carry


- B, a `prepr.sh` step running `harness_headers.inline_scan()` (0.55 s) when the diff touches `dev/audit/harnesses/`, with the red/green demonstration the root-cause rule requires. Carry: #3156 (the carrier for all three until the orchestrator opens their groups; not to close on this record)
- C, teach `ci-cancelled` and route unnamed-red blocks to `root-cause-detectable` / `-unrecorded` in the reviewer vocabulary (`.claude/workflows/web-fix-wave.js` `VERDICT_CLASSES`): policy, waits for the owner's approving review. Carry: #3156
- The cause of the cross-run gate deferral (#3240, #3244) is not established. Carry: #3156

## Friction

none
