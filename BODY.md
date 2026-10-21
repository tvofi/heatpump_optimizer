R10-CI-LAYOUT PR G: wire the unwired self-tests, derive the wave-script restore list, and pin the push and merge lines

Part of #201. Closes no filed issue: PR G pays #2444's forward-carries and the #2423 review finding, inside the approved CI-layout design (`probe/design-ci-rev4`, `1371a0a6`, approved by `probe/design-ci-review5`, `afc00bfe`; both archived as `archive/probe/...` tags) and the approved plan addendum's rows 2 and 3.

This is the third of the group's four pull requests (PR 0 merged as #2464). `.github/workflows/governance.yml` is code-owned, so the owner approves at the merged head. The diff adds no required context and renames none: `instrument-self-tests` is not required, and `wave-script` keeps its name. Every change is about a check that could not fail where it was needed:

- **A. The unwired self-tests (#2444).** `tools/audit/seat/selftest_wiring.py` counted only files directly under `tools/audit/seat/`, so self-tests elsewhere under `tools/` were named in no workflow `run:` line. The rule now covers every file under `tools/`, and `governance.yml`'s `instrument-self-tests` runs each file it finds unwired. At this head that is 12 files: the 11 the rule found at the old base, plus `tools/plan/replan.py`, which main added since and the widened rule named on the merge.
- **B. A derived wave-script restore list (#2423).** `wave-script` restores its check source from the base commit, but the list was written by hand and had drifted: it omitted `tests/delivery_status.py`, `tools/release/stamp.py` and five modules under them, so on a head whose readers agreed the job read `divergent=2`. The derivation is now the agreement reader's own precondition: `tools/policy/agreement_py.py` computes its transitive import closure (including its `locate()` loads), and `--out` and `--run` refuse to answer while a pathspec of the job's restore step misses a file in it; `--restore` prints the same check alone and `--self-test` plants its arms. The list gains the seven.
- **C. Offline seams for the four unpinned lines (#2444).** `handoff_push.sh`'s three push calls and `merge_pr.sh`'s merge call are driven end to end by their own `--self-test` over a scratch origin and stubbed `git`/`gh`/`app_push`. Replaced by `true` (or `exit 0`), each line now reddens its self-test. `dev/audit/harnesses/r10_seat_selftests_mutants.py` carries the four as S31-S34.
- **D. A stale self-test the wiring found.** `tools/policy/record-predicate/row_files_replay.py --self-test` read `origin/main` for the plan's old path, which moved under `dev/programme/` in the lift. It now derives the historical commit from the old path's deletion in main's history, so the old-path arm stays a real control.
- **E. The closure recording the head's own re-record exposed.** Re-recording `tests/entities.py` files three `tools/audit/seat/` modules (`merge_train.py`, `queue_pre_flight.py`, `tmp_paths.py`) under `inert_reads` and in the closure, and `closure.py merge` refuses that pair against the INERT prefix (#357). The three move to `INERT_EXCEPT` and into entities' recorded closure, so an edit to one selects the script that reads it.

**What this round changed, and why (returned at `e9d54acd` with three reds).**

1. `policy-docs` refused ``pinned tools/policy/agreement_restore.py` is unregistered``. The previous head put the derivation in a new program beside the agreement reader. `policy-docs` runs the **base's** `field_coverage.mjs`, whose registry cannot name a program this pull request adds, so the red was structural: no edit to the head's `DECLARED` reaches the copy that grades it. `governance.yml`'s own restore note already states the rule ("A program added BESIDE the program it extends rather than inside it is therefore the pull request's own"). The derivation now lives inside `agreement_py.py`, which is already registered and pinned, and the separate program, its `DECLARED` entry and its guard step are gone. The design gained by this: the reader asserts its own precondition, so the lane cannot answer from unrestored readers, and `prepr.sh`'s agreement step enforces it without a line of its own. Alternatives rejected: a new module imported by the reader (codeowners_gap's arm E counts a module beside the importer as pinned, the same red); running the check only in `instrument-self-tests` (that job grades nothing, so the drift would be unguarded); splitting a registry fix into a first pull request (it fixes the next new program, not this one, and the fold is the better design anyway).
2. `instrument-self-tests` stopped on `handoff_push.sh: line 55: i: unbound variable`. The self-test declared its case counter `local ... i` with no value and incremented it with `i=$((i + 1))` under `set -u`. macOS `/bin/bash` 3.2 reads an unset name in arithmetic as 0, so every seat run passed; CI's bash 5 refuses it. The counter is now `i=0` in the declaration. The previous body's answer for this check described `ref_privacy` refusals; that was wrong: the failing log shows `ref_privacy --check at HEAD: ... 0 refused` and one error, the unbound variable.
3. `pr-contract` refused the body for not naming `nightly-status` and `policy-docs`. Both are answered under `## Red checks` below.

## Head

`7dfec2f6bc4641ab1236e7bf15f58390804bd3f4`: the returned head `e9d54acdf`, merged with origin/main `df6ca4bc6` in `663aaa303685ed03e8bc533cbf7cac1ece8d5071` (an automatic merge, no conflict), then one commit, `7dfec2f6b`, carrying the three fixes above. `git merge-base HEAD origin/main` is `df6ca4bc6`; the diff against it is eleven files. Every figure below was taken at this head on this seat (CPython 3.14 seat venv, macOS `/bin/bash` 3.2) unless it says otherwise; `date -u`: 2026-10-21T08:30Z.

Gate mode: item E changes `tests/closure.py`, so `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` prints `MODE: FULL -- every test script runs, nothing is scoped out.` with `reason: tests/closure.py changes the gate itself, so every closure is suspect`. The full suite is CI's (the owner's ruling on heavy scripts); this seat ran the cheap checks named in the Figures.

## Mutation proof

### This round's fixes

- The restore precondition in `agreement_py.py`'s `main` (`if restore_check(root, reader):` replaced by `if False:`): `python3 -I tools/policy/agreement_py.py --self-test` -> rc=1, `agreement_py self-test: 7 checks, 1 failed` (`FAIL and --out refuses to answer on it`). Restored: rc=0, `7 checks, 0 failed`.
- The restore list itself (the `tests/delivery_status.py` pathspec deleted from `wave-script`'s restore step): `python3 -I tools/policy/agreement_py.py --out <file>` -> rc=1, `UNRESTORED tests/delivery_status.py: no wave-script restore pathspec covers it`, `13 closure file(s), 12 covered by the wave-script restore list, 1 missing`, and no JSON written. Restored: rc=0, `13 covered ..., 0 missing`.
- The `policy-docs` red, reproduced and cleared with the job's own restore: a detached worktree of this head, with the `policy-docs` restore pathspecs checked out from the merge base (6 paths), then `node tools/policy/field_coverage.mjs --only registry`. With the previous head's `governance.yml` and `agreement_restore.py` put back: `REFUSED  registry: \`pinned tools/policy/agreement_restore.py\` is unregistered`, `refused=1`, `FIELD COVERAGE REFUSED` (CI's line, verbatim). At this head: `refused=0`, `FIELD COVERAGE ok`.
- The counter: no mutation proof on this seat. The defect only exists under bash 4+, and this seat has only `/bin/bash` 3.2, where the unfixed line passes (`bash -c 'set -u; f(){ local i; i=$((i+1)); echo $i; }; f'` prints `1`, rc=0). CI's `instrument-self-tests` is the only bash 5 run; its log at `e9d54acd` is the before.

### The four lines from the earlier rounds

Each line replaced by the carry's own mutant, then the file's `--self-test` run and the file restored. From the earlier rounds, carried by the harness at this head:

- S31 `push_app 2  # mut:push-update` -> `true`, S32 `out=$(push_app 2)  # mut:push-open` -> `true`, S33 `push_app 1  # mut:push-row` -> `true`: each KILLED, `handoff_push self-test: 2 checks, 1 failed`.
- S34 `gh pr merge … # mut:merge` -> `exit 0`: KILLED, `merge_pr self-test: 14 checks, 2 failed`.
- S08 (the wrapper's dispatch to `delivery_row.sh`), S29 and S30 (`selftest_wiring`), W1-W3 (an unwired file, a step reduced to a comment, a trailing comment): each KILLED.

## Null control

- Unmutated: `agreement_py --self-test` `7 checks, 0 failed`; `agreement_py --restore` `13 closure file(s), 13 covered ..., 0 missing`; `--out` writes its JSON and the lane over it reads `RESULT divergent=0 unregistered=0 dead=0 refused=0`; `handoff_push` `2 checks, 0 failed`; `selftest_wiring --check` `70 self-testing, 70 wired, 0 unwired`.
- The derived closure is unchanged by the move: `agreement_restore.py --print` at the previous head and `closure()` in the folded reader at this head print the same 13 paths (`diff` empty, printed `SAME-CLOSURE` only on a zero exit).
- The required-context set is untouched: the diff edits no `name:` of a required job, and the live ruleset 23698884 still lists the same 17 contexts.

## Figures

- `python3 -I tools/policy/agreement_py.py --self-test` -> `agreement_py self-test: 7 checks, 0 failed`, rc=0; the same under `python3.11` and `python3.13`.
- `python3 -I tools/policy/agreement_py.py --restore` -> `agreement_py restore: 13 closure file(s), 13 covered by the wave-script restore list, 0 missing`, rc=0.
- `python3 -I tools/policy/agreement_py.py --out <file>` then `node tools/policy/agreement.mjs --py-json <file>` -> `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`.
- `node tools/policy/agreement.mjs --self-test` -> `SELF-TEST 27 of 27 probes held`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> before wiring `tools/plan/replan.py`: `UNWIRED tools/plan/replan.py`, `70 self-testing, 69 wired, 1 unwired`, rc=1; after: `70 self-testing, 70 wired, 0 unwired`, rc=0.
- `python3 -I tools/audit/seat/offline_spy.py tools/plan/replan.py` -> `network=0 remote_git=0`, `offline_spy: 1 files, 0 refused`; `python3 -I tools/plan/replan.py --self-test` -> `self-test: 0 failed` under the seat interpreter and `python3.11`.
- `bash tools/audit/seat/handoff_push.sh --self-test` -> `delivery_row self-test: 5 checks, 0 failed`, `handoff_push self-test: 2 checks, 0 failed` (bash 3.2; see the mutation note).
- `node tools/policy/field_coverage.mjs --only registry` at this head -> `RESULT read=3 ignored=0 declared_none=34 blind=0 dead=0 refused=0`, `FIELD COVERAGE ok`.
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` -> `pinned_by_base_restore=81`, `uncovered_files=0`.
- `python3 -I tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 -I tests/layout.py --guard --base df6ca4bc6` -> `layout: GUARD: 0 refusal(s) against df6ca4bc6858`.
- `python3 -I tools/audit/seat/ref_privacy.py --check` -> `18 file(s) with a push site, 9 guarded, ... 0 refused`.
- `python3 tests/throwaway_git.py --check` -> `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
- `node tools/policy/policy_lint.mjs` -> `TOTAL: 0 error(s) across 41 policy file(s)`.
- `python3 tools/pr/ci_predict.py --base origin/main` -> `CI PREDICT: no closures or fast red predicted against df6ca4bc6858`.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` -> `== M0: 0 seat step(s) red`, every S and W mutant `KILLED` except three reported `NOT RUN, the step is red unmutated` (S21 `roster_edit.py`, S24 `seat_venv.sh`, S25 `state_docs.py`, none of them in this diff), so `RESULT survivors=3`, rc=1. That full run overlapped this seat's own commits in the same worktree; re-run alone, `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py S21 S24 S25` -> each `KILLED rc=1`, `RESULT survivors=0`. The three are counted as a contended full run, not as survivors; a reviewer's clean full run decides.
- `env PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` -> `PRE-PR: 7dfec2f6bc4641ab1236e7bf15f58390804bd3f4 0000000000000000000000000000`, rc=0: `MODE: FULL`, `closures` skipped under the env var by the owner's ruling (CI's `closures` and `closures-autofix` own it), `FIGURES: 20 resolved, 0 not verified, 0 refused`.

## Red checks

- `policy-docs` (`field coverage`): `pinned tools/policy/agreement_restore.py` is unregistered. Cause and fix in item 1 above: a program added beside a pinned one is graded by the base's registry, which cannot name it. Cheaper detector: running the base's `field_coverage.mjs --only registry` over the head with the job's restore applied, as in the mutation proof; it took 24.6 s and 20.2 s on two runs on this seat and needs no network, and no instrument does it today (`prepr.sh` runs the head's copy, which carries the entry and passes). Its standing cost would be one restore and one registry run in `prepr.sh`; whether to buy it is carried below.
- `instrument-self-tests`: `handoff_push.sh: line 55: i: unbound variable`. Cause and fix in item 2 above. Cheaper detector: none on this seat. The defect is bash-version behaviour, the seats run macOS `/bin/bash` 3.2, and no bash 4+ is installed here; CI's run is the first that can see it. A seat-side bash 5 (or running `--self-test` steps in the CI container image) would be the detector; carried below.
- `pr-contract`: the previous body did not name `nightly-status` or `policy-docs`. This body names both.
- `nightly-status`: grades `main`, not this diff. Its log reads `NIGHTLY FAILED: slow failed last night.`, scheduled run 39387919507 at `0c298f6`, job 118512165515, and that job's log reads `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): loop_cpu_ratio 0.1114 over its budget 0.111]`, `1 of 93 replay checks FAILED`. `pr-contract` flags it as possibly this PR's own because the diff touches `governance.yml`; `nightly-status` reads the scheduled `tests.yml` run and `tests/nightly_status.py` restored from the base, and the slow lane runs `tests.yml`, which this diff does not touch. The fix is the separate `r10-replay-cap` work. Cheaper detector: none for this PR; the red is main's.
- `ci-ratchet` on main's push runs (carried to this group): run 39548715713 at `739c8369` reads `GREW critical_path_minutes: 56.5 (budget 54.825)`. This pull request does not address it: it edits `governance.yml` and no `tests.yml` job, so it moves neither the `fast (3.14)` critical path nor `script_runs_per_push`. PR 0 (#2464) paid (a)-(c), and the design's window rule (B4) judges `ci-ratchet` on 5 of 8 push runs after PR 0; the remaining grade and any further payment belong to PR 1 and PR 2, which move the jobs. Carried below.

## Forward-carry

- The ruleset step at PR 2's merge (the orchestrator's and tvofi's, not this PR's): ruleset 23698884's `required_status_checks` today lists 17 contexts (read live 2026-10-21): `fast (3.14)`, `browser`, `briefs`, `closure-scope`, `closures`, `typing`, `hassfest`, `validate-hacs`, `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`, `Analyze (actions)`, `Analyze (javascript-typescript)`, `Analyze (python)`, `mutation`, and `budget-raise-gate` (integration 15368). Per the phase 2 design at `archive/probe/design-ci-rev4` (`1371a0a6`, its "required contexts in ruleset 23698884" row), PR 2's step removes all 17 and adds exactly one, `gate` (integration 15368). This PR changes none of them. Carry: R10-CI-LAYOUT
- The `wave-script` agreement lane enforces the restore precondition only once the base carries the folded reader; on this pull request the base's `agreement_py.py` runs without it, and `instrument-self-tests` runs the head's `--restore` as the early signal. The first pull request after this one must show the lane printing `agreement_py restore: ... 0 missing` in `wave-script`; if it does not, the precondition is inert there. Carry: R10-CI-LAYOUT
- PR 1 and PR 2 move jobs under the umbrella: `instrument-self-tests`'s new steps and `wave-script`'s restore pathspecs must move with the jobs they grade, or the drift this PR closes reopens. Carry: R10-CI-LAYOUT
- `ci-ratchet`'s `critical_path_minutes` red on main's push runs (run 39548715713, `56.5` against `54.825`): not paid here; PR 1/PR 2 own the job graph that moves it, under B4's window. Carry: R10-CI-LAYOUT
- Item E's three `INERT_EXCEPT` entries follow the recording, but the call site that reads them is unnamed; if a later seat finds the read is an artefact of the recorder's in-process path, the three go back to INERT with the artefact fixed. Either way the entries only over-select. Carry: R10-CI-LAYOUT

## Friction

- defect-root-cause: unenforced: a program added beside a pinned grader is refused by the base's `field_coverage` registry on the pull request that adds it, and no pre-push instrument runs the base's registry over the head, so the red surfaced only in CI. Carry: R10-CI-LAYOUT
- fixer: cost: the seats run macOS `/bin/bash` 3.2 and CI runs bash 5; a self-test that passes on every seat failed in CI on an unset arithmetic name, and no seat can reproduce the difference. Carry: R10-CI-LAYOUT
