R10-CI-LAYOUT PR G: wire the unwired self-tests, derive the wave-script restore list, and pin the push and merge lines

Part of #201. Closes no filed issue: PR G pays #2444's forward-carries and the #2423 review finding, inside the approved CI-layout design (`probe/design-ci-rev4`, `1371a0a6`, approved by `probe/design-ci-review5`, `afc00bfe`) and the approved plan addendum's rows 2 and 3.

This is the third of the group's four pull requests (PR 0 merged as #2464). `.github/workflows/governance.yml` is code-owned, so the owner approves at the merged head. The diff adds no required context: `instrument-self-tests` is not one, and `wave-script` keeps its name. Every change is about a check that could not fail where it was needed:

- **A. The unwired self-tests (#2444).** `tools/audit/seat/selftest_wiring.py` counted only files directly under `tools/audit/seat/`, so seven self-tests outside it were named in no workflow `run:` line, and a fourth line set (`merge_pr.sh`'s `gh pr merge`) was named but never reached by its own self-test. The rule now covers every file under `tools/`, and `governance.yml`'s `instrument-self-tests` runs each of the 11 it finds unwired at the base.
- **B. A derived wave-script restore list (#2423).** `wave-script` restores its check source from the base commit, but the list was written by hand and had drifted: it omitted `tests/delivery_status.py`, `tools/release/stamp.py` and five modules under them, so on a head whose readers agreed the job read `divergent=2`. `tools/policy/agreement_restore.py` derives the list from the agreement reader's transitive import closure (including its `locate()` loads) and `--check` refuses a list that misses one; the list gains the seven. Because the tool becomes a PINNED program in `wave-script` (it is restored by `tools/policy/*.py` and run below that restore), two registries follow it in the same diff: `field_coverage.mjs`'s `DECLARED` names the new grader with its reason, and `prepr.sh`'s agreement-lane step runs `agreement_restore.py --check` locally, so the pre-push gate has a path to it.
- **C. Offline seams for the four unpinned lines (#2444).** `handoff_push.sh`'s three push calls and `merge_pr.sh`'s merge call are now driven end to end by their own `--self-test` over a scratch origin and stubbed `git`/`gh`/`app_push`. Each was unpinned: replaced by `true` (or `exit 0`) its self-test stayed rc=0; each now reddens it. `dev/audit/harnesses/r10_seat_selftests_mutants.py` carries the four as S31-S34.
- **D. A stale self-test the wiring found.** `tools/policy/record-predicate/row_files_replay.py`'s `--self-test` read `origin/main` for the plan's old path; the path moved under `dev/programme/` in the lift, and the self-test has been red since. It now derives the historical commit from the old path's deletion in main's history, so the old-path arm stays a real control and no longer describes a state main left.
- **E. The closure recording the head's own re-record exposed.** Re-recording `tests/entities.py` at this head files three `tools/audit/seat/` modules (`merge_train.py`, `queue_pre_flight.py`, `tmp_paths.py`) under `inert_reads` and in the closure, and `closure.py merge` refuses that pair against the INERT prefix (#357) — the same refusal the `tools/policy/agreement.mjs` block records. The three move to `INERT_EXCEPT` and into entities' recorded closure, so an edit to one selects the script that reads it. `ci_predict` names a fourth, an inert read rather than a dependency: the changed `tools/audit/seat/selftest_wiring.py` is opened as text, and `--apply-inert` writes its `inert_reads` entry. The same recording at the base is clean; the arm that opens the three is not named, and that is carried below.

Scope note. The roster carry names seven files and says to widen the rule "to their directories"; the approved plan addendum (row 2) widens the same rule to all of `tools/`. I took the plan's wider scope: the carry's seven are all inside it, and the widened rule found four more that the carry's weaker substring rule had counted as wired because a run line named the file without its self-test (`--install`, `--report`/`--hooks`, a variable's value, or a comment). All 11 are wired rather than allow-listed; `tests/entities.py` already runs two of them (`tools/merge/ledger_merge.py` and `tools/release/stamp.py`), and the workflow step now drives each on the pull request's own copy in the job that grades nothing.

## Head

`2fd3fd459e6a8dd6eaf02a938ffa16b8554918e8` is three commits on origin/main `990e90af9`: `a164f8ec5` (the authored code head), merged with main in `5ab1ea80eab4e949658d4a6cc176ccde7ed6a014` (an automatic merge, no resolution); `430560cc677322efda5eab1f4f91ea93174e7286`, which lands the push self-test's stub at the live `tools/pr/app_push.sh` and stops the restore tool's reader arm citing the pre-move reader alone, because the guard refuses a changed file's new citation of a landed retired path; and `2fd3fd459e6a8dd6eaf02a938ffa16b8554918e8`, which records the reads entities takes in the seat instruments (item E). The branch was cut from origin/main `2dadcdc8`; the merges since are main's own (record rows and `record_row.py`, `tests/card.mjs`, the requirements files, `r10_deeplink_mutants.py` and a roster edit), none of which this diff touches. `git merge-base HEAD origin/main` is `990e90af9`, and the diff against it is the twelve files below. Every figure below was taken at this head on this seat (CPython 3.14.7, the seat interpreter); `date -u`: 2026-10-20T17:36Z.

`prepr.sh` ran with `PREPR_SKIP_CLOSURES=1` by the owner's ruling for this wave: CI's `closures` context is required on every pull request and `closures-autofix` repairs an under-scoped result, so a local re-record duplicates the required check and serialises handoffs on the shared box. Everything else in prepr ran and passed. What the closures lane would have recorded is measured here directly instead (`closure.py check --in-dir`, in the Figures and item E), and CI's `closures` context remains the authority for the committed table.

Gate mode: because item E changes `tests/closure.py`, the gate's own rule scopes nothing — `python3 tests/closure.py affected --files-from <the diff>` prints `CASE: FULL -- tests/closure.py changes the gate itself, so every closure is suspect`, and `prepr.sh` runs `MODE: FULL`. That is the price of repairing the classification in this pull request; the alternative, leaving the INERT pair for the closures job, is a check `closures-autofix` cannot merge (its own message: "check refuses this pair on CI").

## Mutation proof

### The four lines, at both ends (#2444's control, re-taken)

Each line replaced by the carry's own mutant, then the file's `--self-test` run and the file restored (`git status` clean after). The base tree is a detached worktree of `4e5801eb5`.

| line (head) | mutant | base `4e5801eb5` (#2444's head) | head |
|---|---|---|---|
| `handoff_push.sh` update-path push | `true` | rc=0, `delivery_row self-test: 5 checks, 0 failed` | rc=1, `handoff_push self-test: 2 checks, 1 failed` |
| `handoff_push.sh` open-path push | `true` | rc=0, `delivery_row self-test: 5 checks, 0 failed` | rc=1, `handoff_push self-test: 2 checks, 1 failed` |
| `handoff_push.sh` row push | `true` | rc=0, `delivery_row self-test: 5 checks, 0 failed` | rc=1, `handoff_push self-test: 2 checks, 1 failed` |
| `merge_pr.sh` `gh pr merge …` | `exit 0` | rc=0, `merge_pr self-test: 12 checks, 0 failed` | rc=1, `merge_pr self-test: 14 checks, 2 failed` |

Commands: `bash tools/audit/seat/handoff_push.sh --self-test` and `bash tools/audit/seat/merge_pr.sh --self-test`. The base `handoff_push.sh --self-test` delegates to `delivery_row.sh`, which is why the base arms cannot see the pushes; the head's script runs its own two-arm harness as well as `delivery_row`'s.

`dev/audit/harnesses/r10_seat_selftests_mutants.py` (the #2444 harness, updated) carries the same four as S31-S34 and the changed wrapper dispatch as S08. At the head it prints `RESULT survivors=1`, and that one is the pre-existing M0 red below, not a mutant:

- S31 `push_app 2  # mut:push-update` -> `true`: KILLED rc=1, `handoff_push self-test: 2 checks, 1 failed`.
- S32 `out=$(push_app 2)  # mut:push-open` -> `true`: KILLED rc=1, the same tally.
- S33 `push_app 1  # mut:push-row` -> `true`: KILLED rc=1, the same tally.
- S34 `gh pr merge … # mut:merge` -> `exit 0`: KILLED rc=1, `merge_pr self-test: 14 checks, 2 failed`.
- S08, the wrapper's dispatch to `delivery_row.sh`: KILLED rc=1 (its tally line never prints).
- S29 (comments kept in a `run:` line) and S30 (`return 0` for the wiring refusal): KILLED rc=1, `selftest_wiring self-test: 18 checks, 2 failed` / `1 failed`.
- W1 (an unwired self-testing file) KILLED: `selftest_wiring: 70 self-testing, 69 wired, 1 unwired`; W2 (a step reduced to a comment) and W3 (a trailing comment) each KILLED: `69 self-testing, 68 wired, 1 unwired`.

### The derivation and the check

- `python3 -I tools/policy/agreement_restore.py --self-test` -> `agreement_restore self-test: 7 checks, 0 failed`; its arms include "a list missing one transitive reader exits 1 and names it", "a wildcard pathspec that would cover tests/ does not cover a nested file", and a workflow with no `wave-script` job refused rather than read as covered.
- `python3 -I tools/audit/seat/selftest_wiring.py --self-test` -> `selftest_wiring self-test: 18 checks, 0 failed`; the harness's S29 (comments kept) and S30 (`return 0` for the refusal) are killed.
- The widened rule's planted failing case is the harness's W1 (a self-testing file under `tools/audit/seat/` with no run line) and the new file-level case: a `--self-test` file under `tools/pr/` with no mention reads `UNWIRED` and makes `--check` exit 1 (the base figure below).
- The restore list's own control is the planted-divergence table below: a divergence in a reader the merge-base list does not restore turns the job red (`divergent=830`, rc=1), the same plant is restored away by this PR's list (`divergent=0`), and a divergence planted in the restored copy of each added file reddens the lane (`delivery` 830, `stamp` 830, `train` 36; rc=1 each).

## Null control

- Unmutated files: `handoff_push` `2 checks, 0 failed`; `merge_pr` `14 checks, 0 failed`; `selftest_wiring --check` `69 self-testing, 69 wired, 0 unwired`; `agreement_restore --check` `13 closure file(s), 13 covered ... 0 missing`; `row_files_replay --self-test` rc=0.
- The 24 files the carry's weak loop reads `wired` stay wired: the head's 69 self-testing files include all of them, no existing step is renamed, and `instrument-self-tests` keeps its name. `wave-script` keeps its name and stays the one required context among the two jobs; the required set is still the 17 contexts in `tools/policy/fixtures/required-contexts.json`.
- The unplanted head reads `divergent=0` in the agreement lane, with and without the restore.
- The layout guard at the head reads 0 refusals: the new self-test's stub is at the live `tools/pr/app_push.sh`, and the restore tool's fallback arm names the pre-move reader on a line that also names the live one.
- The widened check on the base tree is the only "before": 11 unwired; the head wires exactly those 11 and adds the new tool, so 69/69.

## Figures

Every command below was run at the head unless it names the base tree (a detached worktree of `4e5801eb5`).

- The carry's weak loop at the base (its own control): `git grep -lE -e '--self-test|self-test\)' -- tools/ ':!tools/audit/seat/' ':!*.md' ':!*.json' | while read f; do grep -rqF "$f" .github/workflows/ && echo "wired $f" || echo "unwired $f"; done | awk '{print $1}' | sort | uniq -c` -> `7 unwired`, `24 wired`.
- The widened rule on the base tree (the head's `selftest_wiring.py`, copied over the base's): `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `68 self-testing, 57 wired, 11 unwired`, naming `tools/audit/archscore/gate.py`, `tools/audit/check_scopes.py`, `tools/audit/merge_throughput.py`, `tools/audit/worktree_gc.sh`, `tools/coverage/partition.py`, `tools/merge/ledger_merge.py`, `tools/policy/policy_lint.mjs`, `tools/policy/record-predicate/row_files_replay.py`, `tools/pr/approve_held_runs.sh`, `tools/pr/head_note.py`, `tools/release/stamp.py`; rc=1.
- The widened rule at the head: `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `69 self-testing, 69 wired, 0 unwired` (the 69th is the new `agreement_restore.py`).
- The derived list: `python3 -I tools/policy/agreement_restore.py --print` -> 13 paths: `tests/delivery_status.py`, `tests/layout.py`, `tests/structure.py`, `tests/throwaway_git.py`, `tools/audit/round4/D11/d11lib.py`, `tools/audit/round4/D11/governance_cost.py`, `tools/audit/seat/merge_train.py`, `tools/audit/seat/queue_pre_flight.py`, `tools/audit/seat/ref_privacy.py`, `tools/audit/seat/tmp_paths.py`, `tools/policy/agreement_py.py`, `tools/policy/budget_raise_gate.py`, `tools/release/stamp.py`.
- The list against the merge-base `governance.yml` (the head's tool): `python3 -I tools/policy/agreement_restore.py --check` -> `13 closure file(s), 6 covered by the wave-script restore list, 7 missing`; rc=1.
- `python3 tools/pr/ci_predict.py --base origin/main` -> at `6f3bd6fa5`, `PREDICT closures INERT READS tests/entities.py: tools/audit/seat/selftest_wiring.py (a new file beside 5 it lists)`; `--apply-inert` writes that entry, and the same command at this head prints `CI PREDICT: no closures or fast red predicted against 990e90af9bcd`.
- The list at the head: `python3 -I tools/policy/agreement_restore.py --check` -> `13 closure file(s), 13 covered by the wave-script restore list, 0 missing`; rc=0.
- The recording behind item E: `python3 tests/closure.py record tests/entities.py --out-dir ~/hpo-seats/r10s3/ci-layout-g/exp/rec-entities` (the run the closures lane performs), then `python3 tests/closure.py check --in-dir ~/hpo-seats/r10s3/ci-layout-g/exp/rec-entities --partial` -> `closure: committed closures cover every file this run touched`, rc=0, beside the safe note `tests/entities.py lists 3 file(s) this run did not touch (safe: over-scoped)`. The same pair recorded at the base `990e90af9` (a detached worktree) covered with no INERT read at all. Before the classification change, `python3 tests/closure.py merge --in-dir <that recording> --partial --out <copy of the table>` refused: `files on the INERT list are actually read by tests: tools/audit/seat/merge_train.py`, `... queue_pre_flight.py`, `... tmp_paths.py` -- the pair item E repairs.
- The four restore scenarios, `~/hpo-seats/r10s3/ci-layout-g/exp/sim_restore.sh` (sha1 `b762f9c777f0dc4fad7e3de16a1003c1bc0a8e42`), which performs the job's own restore over a head worktree and runs its two agreement commands:
  - merge-base list, no plant: `divergent=0`, rc=0.
  - merge-base list, `tests/delivery_status.py` answering null: `divergent=830`, rc=1.
  - this PR's list, no plant: `divergent=0`, rc=0.
  - this PR's list, the same plant: `divergent=0`, rc=0 (restored from the base before the lane runs).
- Divergence planted in the restored copy, `~/hpo-seats/r10s3/ci-layout-g/exp/sim_after.sh` (sha1 `619be173bfcf3b64ecb76746d130422b452cab48`): `none` -> `divergent=0` rc=0; `delivery` -> `divergent=830` rc=1; `stamp` -> `divergent=830` rc=1; `train` -> `divergent=36` rc=1.
- The agreement lane at the head: `python3 -I tools/policy/agreement_py.py --out /tmp/ag.json && node tools/policy/agreement.mjs --py-json /tmp/ag.json` -> `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- `bash tools/audit/seat/handoff_push.sh --self-test` -> `delivery_row self-test: 5 checks, 0 failed` and `handoff_push self-test: 2 checks, 0 failed`.
- `bash tools/audit/seat/merge_pr.sh --self-test` -> `merge_pr self-test: 14 checks, 0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -> `ALL 2359 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 -I tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 -I tests/layout.py --guard --base 990e90af9` -> `layout: GUARD: 0 refusal(s) against 990e90af9bcd`, rc=0 (the follow-up commit's reason).
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` -> `enforcement_surface_files=131`, `covered_by_an_owner=50`, `pinned_by_base_restore=81`, `uncovered_files=0`.
- `node tools/policy/policy_lint.mjs` -> `TOTAL: 0 error(s) across 41 policy file(s)`.
- `node tools/policy/field_coverage.mjs --only registry` -> `RESULT read=3 ignored=0 declared_none=35 blind=0 dead=0 refused=0`, `FIELD COVERAGE ok` (the new pinned grader is declared with its reason).
- The new `instrument-self-tests` step runs offline: `python3 -I tools/audit/seat/offline_spy.py tools/audit/archscore/gate.py tools/audit/merge_throughput.py tools/audit/worktree_gc.sh tools/coverage/partition.py tools/merge/ledger_merge.py tools/policy/record-predicate/row_files_replay.py tools/pr/approve_held_runs.sh tools/pr/head_note.py tools/release/stamp.py tools/policy/agreement_restore.py` -> `offline_spy: 10 files, 0 refused`, every line `network=0 remote_git=0` under backstop `sandbox-exec`. The step's two remaining programs it cannot drive as-is (one is node, one needs its `--repo` argument) run under the same deny-network sandbox: `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network-outbound (remote ip))' python3 -I tools/audit/check_scopes.py --self-test --repo .` -> `SELF-TEST passed (both perturbed scopes refused)`, rc=0, and the same sandbox around `node tools/policy/policy_lint.mjs --self-test` -> `FIXTURE ok: 92 error(s) hold 246 pins across 12 check classes on fixtures/policy-rot/ and fixtures/policy-loop/`, rc=0.
- `bash tools/pr/prepr.sh --self-test` -> `303 passed, 0 failed` (the new agreement-lane line is in prepr's own run and its pinned-grader reader).
- `env PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` -> `PRE-PR: 2fd3fd459e6a8dd6eaf02a938ffa16b8554918e8 0000000000000000000000000000`, rc=0: every step `ok` or `skip`, `MODE: FULL`, `closures` skipped under the env var by the owner's ruling, `ci predict: no closures or fast red predicted`, `layout guard: 0 refusal(s)`, `pr-body: 0 error(s)`, `figures: 47 resolved, 1 not verified, 0 refused`.
- The r10 harness: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` -> `RESULT survivors=1` (the pre-existing M0 `ref_privacy` red; S01-S34, S04U, S08, S12, S27 and W1-W3 all `KILLED`).

## Red checks

- `instrument-self-tests`'s step "Refuse a push that names the host, and an unregistered pusher" is red at the base and at this head with the same 16 refusals: `ref_privacy --check` prints `REFUSE <path>: registered in PUSHERS but holds no push site; drop the entry` for 16 entries, `tools/release/stamp.py`, `tools/pr/push.sh` and `tools/audit/seat/bus.sh` among them. Set-compared at both ends (`python3 -I tools/audit/seat/ref_privacy.py --check` at the head and at a detached `4e5801eb5`), the only difference is the diff-window figure (`605` vs `92 line(s) added since`); no file this diff touches is named, so it adds no refusal. The failing command is its own cheapest detector (seconds, no network); the standing cost is that step's seconds on every pull request, and the answer is a registry decision about which files may push, outside this group's brief. Carry: R10-CI-LAYOUT.
- The r10 harness's M0 is red on that same step at the base and at the head (`== M0 rc=1 Refuse a push that names the host, and an unregistered pusher | ref_privacy: REFUSE tools/release/stamp.py: ...`), so its `RESULT survivors=1` carries the one pre-existing red; every S mutant this PR adds or changes is killed and no other seat step is red.

## Forward-carry

- The restore-closure guard in `wave-script` prints "the base does not carry the derivation; skipped" on this pull request by construction (the base cannot carry the tool it adds). The first pull request after this one must confirm it runs; if it still skips, the guard is inert. Carry: R10-CI-LAYOUT.
- Item E's classification follows the recording (the three files are read by `tests/entities.py` at this head), but the call site that reads them is not named: the base's recording is clean, and an in-process re-run of entities under an import tracer named none of them. If a later seat finds the read is an artifact of the recorder's in-process path, the three go back to INERT with the artifact fixed; if it is a real read, they stand. Either way the entries only over-select. Carry: R10-CI-LAYOUT.
- PR 1 and PR 2 of this group move `tests.yml` under the umbrella and may move jobs: `instrument-self-tests`'s new step, the `wave-script` restore pathspecs and its new guard must move with the jobs they grade, or the drift this PR closes reopens silently. Carry: R10-CI-LAYOUT.
- `ref_privacy`'s stale `PUSHERS` registry: the 16 refusals are recorded in `## Red checks`; the cleanup is a registry decision. Carry: R10-CI-LAYOUT.

## Friction

- finding-propagation: unclear: the roster carry names seven unwired files and "their directories"; the approved plan addendum (row 2) widens the same rule to all of `tools/`. I took the plan's scope, wired 11, and the carry's seven are inside it, so the outcome is the same but the two texts read differently. Carry: R10-CI-LAYOUT.
