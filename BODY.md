Group: R10-FLOW-MAIN-GATE (registration pending: roster PR-B)

Spec: the pack group file `dev/programme/flow-study/roster/groups/R10-FLOW-MAIN-GATE.json` at pin ff1beba2a24cab268cca5426cc390dbf21185cc0 (brief revision 7, (a) to (d) in one pull request: no fixer had started (a)), with STUDY.md K15 and its revision-7 table at the same pin.

The train's `--overlap` main gate (`Train.main_green`) counted every required context whose latest run had no green conclusion as red, so contexts still in flight were logged "is not green ... revert it first". Replayed on main e7c66485's live runs, the base logs exactly that line for three in-flight required contexts; this head logs "still running ... a wait, not red".

The fix gives `merge_train.py` one module-level state classifier, which the train, `merge_pr.sh` and the orchestrator tick all use (K15: "one owner"):

- (a) `latest_runs`, `run_state` and `classify(latest, required)` judge the latest run of each required context. A queued or in-progress run is `wait`, never red. A context with no run yet is `wait`. Red outranks wait. `NOT_GATING` (`record`, `record-autofix`, `nightly-status`, `delivery-status`) never counts, even if a ruleset lists it. `required` None raises: an unreadable ruleset is a refusal, never green. The `--overlap` gate logs RED (with the revert text) only on red, a wait otherwise, and "check runs unreadable" when the read failed. `wait_ci(only=...)` judges through the same `classify`.
- (b) `stale(cr, run_status)`: a check-run that is queued or in progress while its workflow run (from `details_url`) has completed is stale. `Train.unstale(h)` runs in `land()` before the first merge attempt. It re-runs each stale workflow run once (two stale check-runs of one run re-run it once), logs `STALE <context> at <h> ... run <id>`, and re-reads until the context concludes. If the context is still red or unconcluded, the train stops. `merge_train.py unstale <sha>` is the same step, and `merge_pr.sh` calls it (`unstale_head`) before its CI wait.
- (c) `conflicts(run, base, head)` reads the conflicted paths from `git merge-tree --write-tree --name-only --no-messages` under GitHub's merge: `text_merge(run)` puts git's own text merge in place of every merge driver the clone's config defines (`git config --get-regexp '^merge\..+\.driver$'`), because GitHub runs none. So a claim file the local claimnotes driver would resolve is still listed: GitHub reports that head DIRTY, and the driver is its repair. An unreadable config is no answer (None). `build()` uses the same `text_merge`. `dirty_repair(files, claim_files)` offers the claimnotes repair only when every conflicted file is a claim file. Anything else is a content conflict: it goes back to the owning fixer, and its verdict does not carry. The tick's DIRTY line names those files first (#2569's shape: `roster_edit.py`).
- (d) A head is reviewable exactly when `classify(...)[2]` is empty. The tick prints `#N: NOT REVIEWABLE at <head>` when a required context (PR_ONLY included, read live from the ruleset) has concluded red. `merge_train.py classify <sha>` gives a dispatcher the same verdict: GREEN rc 0, RED rc 1, WAIT rc 3, unreadable rc 2. With `--main`, PR_ONLY contexts are dropped.

#2570's tick classifier (`Tick.latest`, `Tick.judge`) now delegates to `latest_runs` and `run_state`, and the MAIN section takes its REQUIRED-red list from `classify`. #2570's `superseded()` stays where it is: it acts on non-required lanes only, which `classify` never reads. The tick's own `GREEN` constant is removed, because nothing reads it anymore.

Round 2 repairs the review of 957df90af (`review/2584`, the verdict's blocking item). The claimnotes driver every clone installs (`claim-files.md`) ran inside `git merge-tree`, resolved a notes-only claim conflict and printed `MERGE-CLAIM: resolved <path>` to stderr, and `Tick.git` returns stdout plus stderr. A claim-only DIRTY read "could not answer", and a content-plus-claim conflict listed the MERGE-CLAIM line as a file. Now no driver runs, which is what GitHub does.

Alternatives considered and rejected:
- A new `ci_state.py` module would mean a second import path for `queue_pre_flight.py`, which already imports the train for its words, and a new self-testing file to wire.
- Keeping `Tick.judge` and adding a train-side copy would be the second rule the brief forbids.
- Re-running every non-completed check before a merge would be a guess where the workflow run's own status is the fact.
- In (c), parsing GitHub's `mergeStateStatus` alone cannot name the files.
- In (c), reading stdout alone in the tick: it removes the symptom and leaves the driver running, so a claim-only conflict would still read clean locally (`[]`, "re-read GitHub's state") while GitHub reports it DIRTY. With no driver run, the driver's stderr has no producer. The strict parse stays as the backstop: a clean exit with a second line, or a conflict exit with none, is None. A stdout-only runner would also be a site no arm can kill, because a neutralized merge-tree writes nothing to stderr.
- In (c), neutralizing only the drivers base's `.gitattributes` names, as `build()` did: a driver named only in the head's attributes, or set in `.git/info/attributes`, would still run. Only a configured driver can run (an attribute naming none falls back to the text merge), so the config is the complete set. `build()` and `conflicts()` share that one rule.

Root cause: process state (d) for (a). R9-ADMIT-REQ made the overlap read one pass instead of a completion wait, and kept the completed-only red test, whose precondition (every run concluded) no longer held. No `defect-root-cause.md` trigger fires: no release, and the only red at the head is nightly-status (below). Carry: dismissed: no trigger fires here (item bf9a641a)

## Head

`b07e9e9d85b795e220715183d90b13a79d2cf107` is two commits on PR head `957df90af06717cd38127f7edf6623b9ff248989`, which already contains origin/main `57f0c9c77cfd5958e0a2443e158bea8326bedae2`. Main had not moved at 2026-10-21T18:52Z (`git merge-base --is-ancestor origin/main HEAD` exit 0), so no merge was owed. Every figure below was taken at `b07e9e9d8` against `57f0c9c77`, between 2026-10-21T18:52Z and 19:10Z. Carry: dismissed: head statement, nothing owed (item 7bf8a818)

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 merge_train-1 ... merge_train-18 merge_pr-1 orchestrator_tick-1 ... orchestrator_tick-4` (23 per-file mutants, each run under the governance step that names its file, each after the same step passed unmutated) printed `M0: 0 seat step(s) red` and `RESULT survivors=0`. The 18 merge_train ids were re-run at `b07e9e9d8` (`RESULT survivors=0`) after its self-test-only commit; merge_pr-1 and orchestrator_tick-1..4 were run at `8328b0283`, whose `merge_pr.sh`, `orchestrator_tick.py` and production `merge_train.py` lines equal the head's (`git diff 8328b0283 b07e9e9d8 -- tools/audit/seat/merge_pr.sh tools/audit/seat/orchestrator_tick.py` is empty; the one commit between them edits `_state_self_test` alone). The per-file ids are in the harness's own `MUTANTS` block. Round 1's 15:

- merge_train-1 NOT_GATING filter removed: KILLED, 6 failed.
- merge_train-2 pending reads red: KILLED, 12 failed.
- merge_train-3 wait outranks red: KILLED, 1 failed.
- merge_train-4 unreadable ruleset returns green: KILLED, 1 failed.
- merge_train-5 overlap logs RED for a wait: KILLED, 2 failed.
- merge_train-6 stale without the run-completed test: KILLED, 2 failed.
- merge_train-7 `self.unstale(h)` removed from `land`: KILLED, 3 failed.
- merge_train-8 no re-read after the re-run: KILLED, 1 failed.
- merge_train-9 `all` to `any` in the claimnotes test: KILLED, 1 failed.
- merge_train-10 the tree line kept in `conflicts`: KILLED, 4 failed.
- merge_train-11 `classify` CLI drops PR_ONLY on a PR head: KILLED, 1 failed.
- merge_pr-1 `unstale_head` runs `true`: KILLED, 1 failed.
- orchestrator_tick-1 `req_bad = red`: KILLED, 3 failed.
- orchestrator_tick-2 NOT REVIEWABLE line suppressed: KILLED, 2 failed.
- orchestrator_tick-3 the old claimnotes hint for every DIRTY: KILLED, 3 failed.

Round 2's 8, one per new behaviour and one per reviewer survivor:

- merge_train-12 `conflicts()` without `text_merge` (the round-1 shape): KILLED, 2 failed.
- merge_train-13 `text_merge` returns no `-c` arguments: KILLED, 2 failed.
- merge_train-14 R1: the exit-code/line-count guard dropped: KILLED, 1 failed.
- merge_train-15 R3: a shared workflow run re-run once per check-run name: KILLED, 1 failed.
- merge_train-16 R4: the `runs is None` unreadable arm in the overlap gate removed: KILLED, 1 failed.
- merge_train-17 `text_merge` reads an unreadable config as no driver: KILLED, 1 failed.
- merge_train-18 `build()` runs on an unreadable config: KILLED, 1 failed.
- orchestrator_tick-4 R2: `getattr(self, "_req_pr", None) or required` to `required`: KILLED, 1 failed.

Failing first: merge_train-12 restores the round-1 `conflicts()` (no `text_merge`). Under it the new driver-installed arm fails in the train's self-test (the harness line above), and, applied by hand, the tick's real-git arm fails 3 checks (Null control). Carry: dismissed: mutation proof, nothing owed (item bcd1f644)

## Null control

- The base self-tests are 198/168/14 checks with 0 failed (`merge_train.py`, `orchestrator_tick.py`, `merge_pr.sh --self-test` at origin/main). The head's are 219/186/16 checks with 0 failed, under python3.11. Carry: dismissed: counts at both ends, nothing owed (item 9108e8a9)
- The driver-installed arm carries its own control: in the same clone the bare `git merge-tree` (no `text_merge`) resolves the claim, exits 0 and prints `MERGE-CLAIM: resolved`; in the clone without the driver it exits 1 with no MERGE-CLAIM. So the arm's clone really runs the driver, and `conflicts()` gives the same answer in both clones. Carry: dismissed: control in the arm, nothing owed (item 001fa1aa)
- The tick's real-git arm (no stub, the tick's own `Tick.git`) classifies a claim-only DIRTY as the claimnotes repair and a content-plus-claim DIRTY as a content conflict naming `roster_edit.py` and the claim file, with no MERGE-CLAIM text in the line. With merge_train-12 applied by hand at the head, `orchestrator_tick.py --self-test` fails exactly these 3 checks, which reproduces both shapes the review named. Carry: dismissed: reviewer defect closed in this diff (item 0aadbe87)
- The R2 arm reads `pr-contract` from the stubbed ruleset: a red `pr-contract` gives one NOT REVIEWABLE line naming it, while the main-graded list is `["tests"]`. The null control is the same head with `pr-contract` green, which gives no line. Carry: dismissed: reviewer survivor pinned in this diff (item c26f6948)
- R1: `conflicts()` on a clean exit with a second line and on a conflict exit with only the tree line is None. The null control is each agreeing shape (`[]`, `[claim]`). R3: two stale check-runs of one workflow run give exactly one POST and one STALE line, and the merge proceeds. R4: a failed check-runs read logs one "check runs unreadable" line and no "still running"; the null control is the two readable arms beside it. Carry: dismissed: reviewer survivors pinned in this diff (item 1869ae66)
- Each round-1 arm carries its own null control: a non-required red stays green, a check-run whose run is still in progress is not re-run, a clean merge-tree is `[]` and an unknown head is `None`, and a non-required red is still reviewable. Carry: dismissed: controls in the arms, nothing owed (item 7356f69d)
- Finder's harness at both ends: `dev/audit/harnesses/r10_main_gate_replay.py` (sha1 266e441f0062fd71721fd8b225f185d28ff2aaba) reads e7c66485's live check runs and main's required contexts through the public API. It was run against a `git archive origin/main` export and against the head.
  - With no `--pending` (the settled tip, where no required context is red), base and head both print only `END`.
  - With `--pending mutation typing closures` the base logs `OVERLAP: batch/replay at e7c664856776 is not green (closures, mutation, typing) after #N's unproved merge: revert it first; --overlap logs it and does not wait`. The head logs `OVERLAP: batch/replay at e7c664856776 is still running (closures, mutation, typing): a wait, not red; --overlap does not wait`.
  - The in-flight moment has passed live, so `--pending` re-creates it. The red arm is the self-test's, because no required context is red at e7c66485. Carry: dismissed: finder harness at both ends, nothing owed (item 5de22e1c)

## Figures

- `python3 dev/audit/harnesses/r10_main_gate_replay.py <merge_train.py> [--pending mutation typing closures]`: run at the `git archive origin/main` export and at the head. The lines are quoted under Null control. Carry: dismissed: figure command, nothing owed (item fb96e327)
- Self-test counts: `python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/audit/seat/orchestrator_tick.py --self-test`, `bash tools/audit/seat/merge_pr.sh --self-test`, at each tree. Carry: dismissed: figure command, nothing owed (item 90f49a86)
- Mutants: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0` followed by the 23 ids above. Carry: dismissed: figure command, nothing owed (item 59e8ccae)
- Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and `scope.run` names `tests/entities.py`. Carry: dismissed: figure command, nothing owed (item a7db2ab7)
  - `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py`: `ALL 2382 ENTITY CHECKS PASSED`.
  - run_always: `tests/env_drift.py --claims-only 57f0c9c77` printed `claims hygiene: 57f0c9c77 ok`, `tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`, `tests/layout.py` printed `layout self-test: ok`, and `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget was raised. Carry: dismissed: figure command, nothing owed (item df2391bb)
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`. Carry: dismissed: figure command, nothing owed (item 147fd5f9)
- `python3 -I tests/throwaway_git.py --check`: 0 sites refused. Both new real-git arms build their repository through `throwaway_git_init`. Carry: dismissed: figure command, nothing owed (item 04af1a9b)
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 38 self-testing, 38 wired. `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused. Carry: dismissed: figure command, nothing owed (item 85769ef8)
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at `b07e9e9d8`: `no closures or fast red predicted against 57f0c9c77cfd`. Carry: dismissed: figure command, nothing owed (item 81151266)

Class seams. Rule: `git grep -lE "check-runs|check_runs" HEAD -- tools ':!*.md' ':!tools/audit/round*'`, each file read for the head it judges and its red rule. The property is a reader that decides whether a head is red, pending or green. Carry: dismissed: class rule stated, seams below (item 3374c33a)

- `merge_train.py` (`main_green`, `wait_ci(only=...)`, `land`) and `orchestrator_tick.py` (`judge`, MAIN, PRS): closed in this diff. Carry: dismissed: closed in this diff (item 8f7f80bf)
- `merge_pr.sh`: stale check-runs are closed in this diff (`unstale_head`). Its own red judgement defers to GitHub's `mergeStateStatus`, which reads the ruleset itself, so it is already guarded. Carry: dismissed: already guarded by GitHub (item ee521cf1)
- `record_row.py` `failed_required`/`not_green` (the record beat's automerge guard) and `ci-watch.sh` (the watcher's failure-only red): these are distinct readers that keep their own rule. They are carried under Forward-carry to the beat that hosts them. Carry: R10-ORCH-MACHINERY (item b93f1f35)
- `proof_watch.py`: judges one named check on a proof branch, not a required set. This is a distinct finding, carried with the other two. Carry: R10-ORCH-MACHINERY (item ca61d005)
- `failure_logs.sh`, `codeql-triage-poll.sh`, `ci_predict_replay.sh`, `tools/plan/replan.py`, `tools/pr/prepr.sh`, `tools/pr/push.sh`, `tools/pr/preflight.sh`, `policy_lint.mjs`: they fetch failure logs, triage CodeQL, read timings or check a branch's own ancestry. None judges whether a head is mergeable, so they are not this class. Carry: dismissed: not this class (item 87ed9b4c)
- `cloud_dispatch.py` and the `tools/policy/fixtures/red-ancestry/*`, `tools/plan/durations.json` files: prompt text and recorded data. Carry: dismissed: not this class (item efc2803f)

Class seams for (c)'s round-2 property, a local merge that runs a driver GitHub does not. Rule: `git grep -nE "merge-tree|git[\"', ]+merge[\"' ]" HEAD -- tools tests ':!*.md' ':!tools/audit/round*'`, each site read for whether it predicts GitHub's merge. Carry: dismissed: class rule stated, seams below (item 086ef8e7)

- `merge_train.py` `conflicts()` and `build()`: closed in this diff (`text_merge`). Carry: dismissed: closed in this diff (item 9b0702f3)
- `tools/pr/merge_main_bot.py` `merge_tree(text_only=...)`: already guarded. It predicts GitHub's merge with every driver `main`'s `.gitattributes` names replaced by `git merge-file --quiet`, and runs in CI from `main`'s copies, where no driver is configured outside the ones it names. It is a second copy of the same replacement, in another closure; folding it into `text_merge` would widen this PR into `tools/pr/`. Carry: dismissed: already guarded, separate CI tool (item 938d66a1)
- `tools/merge/ledger_merge.py --replay` (`--attr-source`), `tools/policy/record-predicate/row_files_replay.py`: replays that measure what a driver does or did, so a driver running is the point. Carry: dismissed: measures the driver itself (item 8c06ccd5)
- `tools/pr/app_push.sh` (step (b)), `tools/pr/app_approve.sh`, `tools/policy/policy_lint.mjs` (the merge-commit tree check): they re-derive a seat's own local merge commit, which a seat makes with its drivers, so running them is correct. Carry: dismissed: re-derives a local merge (item 3ec1d4b6)
- `tools/audit/seat/remerge_main.sh`, `handoff_push.sh`, and the `git merge` lines in `tests/entities.py`, `tools/pr/prepr.sh`, `tools/pr/app_push.sh` and `tools/release/stamp.py` self-tests: they perform a merge rather than predict GitHub's, or build fixtures. `tools/audit/seat/cloud_dispatch.py`, `tests/env_drift.py`, `tests/mutation_table.py` and `tools/policy/agreement.mjs` name merges in prompt text or comments. Carry: dismissed: not this class (item d560ebf5)

## Unpinned sites

none: `prepr.sh` step 6d prints `the diff adds no unpinned mutation site`.

## Red checks

- nightly-status: red at the PR head because it grades main's nightly, not this head. The latest scheduled `tests.yml` run, 39563978649 on main c77f89dc6 (2026-10-21T07:43Z), concluded failure in two jobs: `slow` (step "Replay recorded days through the real coordinator") and `mutation-nightly` (step "Drive the table over the whole package"). This diff touches neither the coordinator nor the package, only `tools/audit/seat/`, two harnesses, `INSTRUMENTS.md` and the closures entry, and `NOT_GATING` keeps nightly-status out of every head's verdict. No cheaper detector is owed here: the red is main's. Carry: dismissed: grades main, not this PR (item 00d4fe3a)

## Forward-carry

- The beat's sweep, `record_row.py`'s automerge guard (`failed_required`, `not_green`), `ci-watch.sh`'s failure-only red and `proof_watch.py` each still carry their own red rule. Per this group's seam note, the beat and the sweep read `merge_train.classify` (and `merge_train.py classify <sha>` from shell). No third rule is written. The control is the e7c66485 replay (`dev/audit/harnesses/r10_main_gate_replay.py`, `--pending` against no `--pending`). Carry: R10-ORCH-MACHINERY (item c2b007d6)
- K15 (d)'s pre-dispatch check (rule E) has a command now: a reviewer is fired only when `merge_train.py classify <head>` exits 0 or 3, never 1 (RED) or 2 (unreadable). R10-FLOW-DISPATCH is not on the roster yet (registration pending: roster PR-B), so this lands with the dispatch seam R10-ORCH-MACHINERY owns (`bus.sh dispatch`, the `reviewer-fire` close). Carry: R10-ORCH-MACHINERY (item 7f7f3da4)

## Friction

none
