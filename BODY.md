Group: R10-FLOW-MAIN-GATE (registration pending: roster PR-B)

Spec: the pack group file `dev/programme/flow-study/roster/groups/R10-FLOW-MAIN-GATE.json` at pin ff1beba2a24cab268cca5426cc390dbf21185cc0 (brief revision 7, (a) to (d) in one pull request: no fixer had started (a)), with STUDY.md K15 and its revision-7 table at the same pin.

The train's `--overlap` main gate (`Train.main_green`) counted every required context whose latest run had no green conclusion as red, so contexts still in flight were logged "is not green ... revert it first". Replayed on main e7c66485's live runs, the base logs exactly that line for three in-flight required contexts; this head logs "still running ... a wait, not red".

The fix gives `merge_train.py` one module-level state classifier, which the train, `merge_pr.sh` and the orchestrator tick all use (K15: "one owner"):

- (a) `latest_runs`, `run_state` and `classify(latest, required)` judge the latest run of each required context. A queued or in-progress run is `wait`, never red. A context with no run yet is `wait`. Red outranks wait. `NOT_GATING` (`record`, `record-autofix`, `nightly-status`, `delivery-status`) never counts, even if a ruleset lists it. `required` None raises: an unreadable ruleset is a refusal, never green. The `--overlap` gate logs RED (with the revert text) only on red, and logs a wait otherwise. `wait_ci(only=...)` judges through the same `classify`.
- (b) `stale(cr, run_status)`: a check-run that is queued or in progress while its workflow run (from `details_url`) has completed is stale. `Train.unstale(h)` runs in `land()` before the first merge attempt. It re-runs each stale run once, logs `STALE <context> at <h> ... run <id>`, and re-reads until the context concludes. If the context is still red or unconcluded, the train stops. `merge_train.py unstale <sha>` is the same step, and `merge_pr.sh` calls it (`unstale_head`) before its CI wait.
- (c) `conflicts(run, base, head)` reads the conflicted paths from `git merge-tree --write-tree --name-only --no-messages`. `dirty_repair(files, claim_files)` offers the claimnotes repair only when every conflicted file is a claim file. Anything else is a content conflict: it goes back to the owning fixer, and its verdict does not carry. The tick's DIRTY line now names those files first (#2569's shape: `roster_edit.py`).
- (d) A head is reviewable exactly when `classify(...)[2]` is empty. The tick prints `#N: NOT REVIEWABLE at <head>` when a required context (PR_ONLY included) has concluded red. `merge_train.py classify <sha>` gives a dispatcher the same verdict: GREEN rc 0, RED rc 1, WAIT rc 3, unreadable rc 2. With `--main`, PR_ONLY contexts are dropped.

#2570's tick classifier (`Tick.latest`, `Tick.judge`) now delegates to `latest_runs` and `run_state`, and the MAIN section takes its REQUIRED-red list from `classify`. #2570's `superseded()` stays where it is: it acts on non-required lanes only, which `classify` never reads. The tick's own `GREEN` constant is removed, because nothing reads it anymore.

Alternatives considered and rejected:
- A new `ci_state.py` module would mean a second import path for `queue_pre_flight.py`, which already imports the train for its words, and a new self-testing file to wire.
- Keeping `Tick.judge` and adding a train-side copy would be the second rule the brief forbids.
- Re-running every non-completed check before a merge would be a guess where the workflow run's own status is the fact.
- In (c), parsing GitHub's `mergeStateStatus` alone cannot name the files.

Root cause: process state (d) for (a). R9-ADMIT-REQ made the overlap read one pass instead of a completion wait, and kept the completed-only red test, whose precondition (every run concluded) no longer held. No `defect-root-cause.md` trigger fires: no release, no red pull request.

## Head

`14ce015949c34a34586eae8b570b4d5cebbf6da6` merges origin/main `57f0c9c77cfd5958e0a2443e158bea8326bedae2` (no conflict; main's delta is R10-FREQ-DEFROST and record rows, none of this diff's files) into the authored head `9e64287f9367a390e69612119b9eed0c0b9c7e61`, which was measured against `f2fb1b0e950ecd047b7f08b3adef93776a622540`. Every figure below was re-taken at `14ce01594` against `57f0c9c77` at 2026-10-21T18:19Z, except the mutants and the e7c66485 replay: the merge changed none of `merge_train.py`, `merge_pr.sh` or `orchestrator_tick.py` (`git diff 9e64287f9 14ce01594 -- tools/audit/seat/` is empty), so those still describe the head. `git merge-tree --write-tree origin/main 14ce01594` is clean (a tree id, rc 0).

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py merge_train-1 ... orchestrator_tick-3` (15 per-file mutants, each run under the governance step that names its file) printed `RESULT survivors=0`:

- merge_train-1 NOT_GATING filter removed: KILLED, 6 failed (K15 (a) e7c66485 shape).
- merge_train-2 pending reads red: KILLED, 11 failed.
- merge_train-3 wait outranks red: KILLED, 1 failed.
- merge_train-4 unreadable ruleset returns green: KILLED, 1 failed.
- merge_train-5 overlap logs RED for a wait: KILLED, 2 failed.
- merge_train-6 stale without the run-completed test: KILLED, 2 failed.
- merge_train-7 `self.unstale(h)` removed from `land`: KILLED, 2 failed.
- merge_train-8 no re-read after the re-run: KILLED, 1 failed.
- merge_train-9 `all` to `any` in the claimnotes test: KILLED, 1 failed.
- merge_train-10 the tree line kept in `conflicts`: KILLED, 2 failed.
- merge_train-11 `classify` CLI drops PR_ONLY on a PR head: KILLED, 1 failed.
- merge_pr-1 `unstale_head` runs `true`: KILLED, 1 failed.
- orchestrator_tick-1 `req_bad = red`: KILLED, 3 failed.
- orchestrator_tick-2 NOT REVIEWABLE line suppressed: KILLED, 1 failed.
- orchestrator_tick-3 the old claimnotes hint for every DIRTY: KILLED, 2 failed.

Failing first: commit da6c45b45 adds the train's K15 arms before any production line, and `python3 tools/audit/seat/merge_train.py --self-test` there stops with `NameError: name 'latest_runs' is not defined`.

## Null control

- The base self-tests are 198/168/14 checks with 0 failed (`merge_train.py`, `orchestrator_tick.py`, `merge_pr.sh --self-test` at origin/main). The head's are 214/178/16 checks with 0 failed, under python3.11, and the train and tick also under 3.13.
- Each arm carries its own null control: a non-required red stays green, a check-run whose run is still in progress is not re-run, a clean merge-tree is `[]` and an unknown head is `None`, and a non-required red is still reviewable.
- Finder's harness at both ends: `dev/audit/harnesses/r10_main_gate_replay.py` reads e7c66485's live check runs and main's required contexts through the public API.
  - With no `--pending` (the settled tip, where only `ci-ratchet`, `record` and `record-autofix` concluded failure, none required), base and head both log nothing.
  - With `--pending mutation typing closures` the base logs `OVERLAP: batch/replay at e7c664856776 is not green (closures, mutation, typing) after #N's unproved merge: revert it first; --overlap logs it and does not wait`. The head logs `OVERLAP: batch/replay at e7c664856776 is still running (closures, mutation, typing): a wait, not red; --overlap does not wait`.
  - The in-flight moment itself has passed live, so `--pending` re-creates it. The red arm (a failed required context logs RED with the revert text) is the self-test's, because no required context is red at e7c66485.

## Figures

- `python3 dev/audit/harnesses/r10_main_gate_replay.py <merge_train.py> [--pending mutation typing closures]`: run at `git show origin/main:tools/audit/seat/merge_train.py` and at the head. The lines are quoted under Null control.
- Self-test counts: `python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/audit/seat/orchestrator_tick.py --self-test`, `bash tools/audit/seat/merge_pr.sh --self-test`, at each tree.
- Mutants: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py merge_train-1 merge_train-2 merge_train-3 merge_train-4 merge_train-5 merge_train-6 merge_train-7 merge_train-8 merge_train-9 merge_train-10 merge_train-11 merge_pr-1 orchestrator_tick-1 orchestrator_tick-2 orchestrator_tick-3`.
- Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, with `RUN tests/entities.py`.
  - `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py` (3.14.7): `ALL 2382 ENTITY CHECKS PASSED`.
  - run_always: `tests/env_drift.py --claims-only 57f0c9c77` ok, `tests/closure.py selftest` `ALL 124 closure shrink pins PASSED`, `tests/layout.py` ok, `tests/harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget was raised.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tests/throwaway_git.py --check`: 0 sites refused. The (c) arm builds its repository through `throwaway_git_init`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 38 self-testing, 38 wired.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: it predicted one closures INERT READS entry, for the new harness under `tests/harness_headers.py`. `--apply-inert` wrote it (commit 9e64287f9), and a re-run at `14ce01594` printed `no closures or fast red predicted against 57f0c9c77cfd`.

Class seams. Rule: `git grep -lE "check-runs|check_runs" HEAD -- tools ':!*.md' ':!tools/audit/round*'`, each file read for the head it judges and its red rule. The property is a reader that decides whether a head is red, pending or green.

- `merge_train.py` (`main_green`, `wait_ci(only=...)`, `land`) and `orchestrator_tick.py` (`judge`, MAIN, PRS): closed in this diff.
- `merge_pr.sh`: stale check-runs are closed in this diff (`unstale_head`). Its own red judgement defers to GitHub's `mergeStateStatus`, which reads the ruleset itself, so it is already guarded.
- `record_row.py` `failed_required`/`not_green` (the record beat's automerge guard) and `ci-watch.sh` (the watcher's failure-only red): these are distinct readers that keep their own rule. They are carried below to the beat that hosts them.
- `proof_watch.py`: judges one named check on a proof branch, not a required set. This is a distinct finding, carried below with the other two.
- `failure_logs.sh`, `codeql-triage-poll.sh`, `ci_predict_replay.sh`, `tools/plan/replan.py`, `tools/pr/prepr.sh`, `tools/pr/push.sh`, `tools/pr/preflight.sh`, `policy_lint.mjs`: they fetch failure logs, triage CodeQL, read timings or check a branch's own ancestry. None judges whether a head is mergeable, so they are not this class.
- `cloud_dispatch.py` and the `tools/policy/fixtures/red-ancestry/*`, `tools/plan/durations.json` files: prompt text and recorded data.

## Unpinned sites

none: `prepr.sh` step 6d prints `the diff adds no unpinned mutation site`.

## Red checks

none

## Forward-carry

- The beat's sweep, `record_row.py`'s automerge guard (`failed_required`, `not_green`), `ci-watch.sh`'s failure-only red and `proof_watch.py` each still carry their own red rule. Per this group's seam note, the beat and the sweep read `merge_train.classify` (and `merge_train.py classify <sha>` from shell). No third rule is written. The control is the e7c66485 replay (`dev/audit/harnesses/r10_main_gate_replay.py`, `--pending` against no `--pending`). Carry: R10-ORCH-MACHINERY
- K15 (d)'s pre-dispatch check (rule E) has a command now: a reviewer is fired only when `merge_train.py classify <head>` exits 0 or 3, never 1 (RED) or 2 (unreadable). R10-FLOW-DISPATCH is not on the roster yet (registration pending: roster PR-B), so this lands with the dispatch seam R10-ORCH-MACHINERY owns (`bus.sh dispatch`, the `reviewer-fire` close). Carry: R10-ORCH-MACHINERY

## Friction

none
