_Requested by **tvofi**_

O17 item 1 (tooling) and item 2(ii), from the roster-cost pre-study the orchestrator accepted on 2026-10-18. Part of #201. No roster group lists an issue for this work, so this body closes none. The policy half is `handoff/r10-roster-carry-policy`.

**Owner gate.** tvofi approves at merge. The code-owned files are `.github/workflows/tests.yml`, `.claude/hooks/stop-selfcheck.sh`, `tests/lane_skip.py`, `tests/closure.py`, `tests/card_rig.mjs`, `tests/card_browser.mjs` and `tools/pr/codeql_scope.py`.

**The change.**
- **Roster ref.** `roster_lib.default_roster_ref(git)` returns the round's roster branch `origin/handoff/audit-r<N>-roster`. Without that branch it falls back to `origin/main` with a note. It warns when main carries roster changes the branch lacks. The tick, `plan_table.py`, `resume_doc.py`, `handover_prompt.py` and `state_docs.py` resolve through it, and the state-docs beat also watches the roster ref.
- **Level 0** (`tests/lane_skip.py`). When every changed file is a roster or a canonical delivery row, `browser`, `coverage` and `typing` skip, with no recorded proof. `fast` never takes Level 0.
- **One changed-file list that keeps both sides of a rename.** `tests/closure.py` `changed_between` / `changed` (`--no-renames`) feeds the gate, lane_skip, the `tests.yml` list sites and CodeQL; `tools/pr/codeql_scope.py` `changed_files` delegates to it. Its twins pass `--no-renames` too: `card_rig.mjs` `threeDotFiles`, `card_browser.mjs` `gridScope`, `stop-selfcheck.sh`, `policy_lint.mjs` `mergeRecordClass` with `stamp.py` `merge_is_record_class`, and the seat and pr scripts. The census in the closure self-test refuses any `git diff ... --name-only` without `--no-renames` over the workflow, tests, tools/pr, tools/policy, seat, release and hook globs. It exempts empty-tree diffs, comment lines, lines marked `# rename-null-control`, four exact allow entries, and `--cached`, where a new list site would pass unseen.

## Head

`a9a26cc41`: `ddb2725f5` merged with `origin/fix/r10-roster-fastpath` at `f95578604` (the closures-autofix commit `ci: re-record closures`, `tests/closures.json` only), because prepr's push-order step refused the handoff as diverged. Merge base `211c8290e`. At 2026-10-18 17:31 UTC origin/main was `c8cc75ea9`, and `git merge-tree --write-tree origin/main HEAD` exited 0.

## Mutation proof

Each mutant edits one file in place at `a9a26cc41`, runs the named check, and is restored with `git checkout --`. These four were re-run in this pass:
- **MB15: `--no-renames` dropped from `stamp.py` `merge_is_record_class`.** `node tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS: recordClassPaths`, and `closure.rename_sites()` names `tools/release/stamp.py:1708`.
- **MB17: `codeql_scope.changed_files` replaced by its own porcelain `git diff --name-only`.** `python3 -I tools/pr/codeql_scope.py --self-test` fails `a rename lists its source too`, `so the python leg analyzes the rename` and `the list is closure.changed_between's, not a copy`.
- **MB19: `--no-renames` dropped from `mergeRecordClass`'s real call.** `node tools/policy/policy_lint.mjs` prints `FIXTURE VACUOUS: recordClassPaths`.
- **MB20: `recordDiffParity` searching the whole of `policy_lint.mjs`.** `node tools/policy/policy_lint.mjs` prints `FIXTURE VACUOUS: recordClassPaths ["recordDiffParity passes mergeRecordClass with --no-renames dropped from its own call (the needle found itself)"]`.

**Disclosed self-correction.** Round 4's parity check searched all of `policy_lint.mjs` for the needle, and found the needle's own spelling. `recordDiffParity` now reads only the bodies of `mergeRecordClass` and `merge_is_record_class`. MB20 is that shape, and policy_lint's fixture arm drives it on every run.

## Null control

- The rename probes (`closure._rename_probe_lists`, and codeql_scope's `git mv lib.py lib.md`) read one commit both ways. Porcelain lists the destination alone, and the producer lists both sides.
- The census's planted root refuses the porcelain line in `x.py`, `y.mjs` and a split `z.sh`, and passes the `--no-renames` twin beside each one.
- policy_lint's fixture arm also drops the flag from its own copy of the call, outside `mergeRecordClass`. `recordDiffParity` must still pass there, and at the head it does.

## Figures

All taken at `a9a26cc41` in this pass:
- `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
- `closure.rename_sites()` (`python3 -c "import sys; sys.path.insert(0,'tests'); import closure; print(closure.rename_sites())"`): `([], [])`.
- `python3 tests/lane_skip.py self-test`: `54/54 pins passed`.
- `python3 -I tools/pr/codeql_scope.py --self-test`: `47 checks, 0 failed`.
- `python3 tools/audit/seat/roster_lib.py --self-test`: `18 checks, 0 failed`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `104 checks, 0 failed`.
- `python3 tools/audit/seat/state_docs.py --self-test`: `all checks passed`.
- `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)` and `FIXTURE ok`, with no `VACUOUS`.
- `python3 tests/layout.py --guard --base origin/main`: `GUARD: 0 refusal(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`.
- `python3 tools/audit/archscore/score.py --diff 211c8290eda31038fcfe70cd526ab912cf92b103 HEAD`: `dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at `ddb2725f5` (Python 3.14.7): `3 of 2347 ENTITY CHECKS FAILED`, the graders-head-copy rows under `## Red checks`.

## Unpinned sites

- **The `tests.yml` wiring** (`typing`'s `needs` and `if:`) and **the CodeQL scope job's import of `tests/closure.py`**. No local check drives a workflow. CI on this head runs every lane and the `scope` job. The first record-only head after merge must show three `skipped`.

## Red checks

Read from the check-runs API on every commit of `fix/r10-roster-fastpath` past the merge base (`repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`, conclusion `failure`, `pr-contract` excluded).

- **`closures`** (at `b965c4ab9`, job 117725439310): `UNDER-SCOPED: tests/card.mjs really reads 1 file(s) the committed closure does not list: tests/env_drift.py`. This PR's card parity pin makes `card.mjs` read `env_drift.py`. Bot-repaired: `closures-autofix: changed -- nothing owed to a human.` (job 117731170063), commit `f95578604` `ci: re-record closures`, merged into this head. The cheaper detector is `ci-autofix.md`'s, already running.
- **`fast (3.14)`** (at `b965c4ab9`, job 117720932505): `>>> FAILED: python3 tests/entities.py`, `2 of 2347 ENTITY CHECKS FAILED`. **This PR's, and still red at the head.** This PR changed `graders-head-copy`'s changed-file step in `tests.yml` from `git diff --name-only "$BASE"..."$HEAD"` to `python tests/closure.py changed --base "$BASE" --head "$HEAD"`. `tests/entities.py` `_PT_JOB_CANON` holds that job's literal text, so two of its checks now fail at `ddb2725f5`: `every pinned grader given a token runs its own copy under the Actions token on the pull request` (`arm mismatch=graders-head-copy.steps[2].run`) and `and any edit to the arm's job, or to what reaches it, disarms it (null control)`. A third local failure is the `delivery_status` step-case row, which reads a step of the same job. The fix is the one-line canonical literal in `_PT_JOB_CANON`. This pass's brief allows a code change only where prepr shows one owed, and prepr does not run `entities.py`, so the fix is left to the orchestrator. Cheaper detector: run `PYTHONPATH=tests/hastub python3 tests/entities.py` on the seat whenever a diff touches `.github/workflows/tests.yml`, at a standing cost of 224 s of CI wall (this job's own timing table). Today it is skipped because the diff scopes `MODE: FULL` and fixer.md step 5 leaves FULL to CI. Making prepr run `tests/entities.py` on a `tests.yml` diff would move this detector to push time.
- **`nightly-ha (stable)`** (at `f95578604`, job 117731309720): `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`. `hb:positive_control` failed only on its py-spy leg: `py-spy did not run: TimeoutExpired: Command '['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid', '1']' timed out after 30 seconds`. The heartbeat read the 600 ms spin as 600.2 ms and the in-process dump named it. `run:exit_status` is the container's exit 1 from that red. `nightly-ha (2025.2.0)` passed on the same commit. No cheaper detector exists: the failure is py-spy attaching inside the `homeassistant/home-assistant:stable` image, which only this container lane runs.

## Forward-carry

- Carry: R10-TICK-DRIVERS (`dev/programme/rosters/wave-r10-groups.json`). After this merges, restart the state-docs beat on main's code with no `--roster-ref` and no `--watch-ref refs/heads/main`. Check it: the memo holds two SHAs, main's and the roster branch's, and a roster-only commit regenerates the plan within one beat. The CodeQL delegation carry is done in this PR, so the orchestrator drops it from that group.

## Friction

- fixer-step-5: unenforced: under `MODE: FULL` the seat leaves every script to CI, so the `tests/entities.py` pin on `graders-head-copy`'s literal went red only on CI (`fast (3.14)` at `b965c4ab9`) and was never run locally.
