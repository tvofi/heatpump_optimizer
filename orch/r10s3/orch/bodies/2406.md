_Requested by **tvofi**_

O17 item 1 (tooling) and item 2(ii), from the roster-cost pre-study the orchestrator accepted on 2026-10-18. Part of #201. No roster group lists an issue for this work, so this body closes none. The policy half is `handoff/r10-roster-carry-policy`.

**Owner gate.** tvofi approves at merge. The code-owned files are `.github/workflows/tests.yml`, `.claude/hooks/stop-selfcheck.sh`, `tests/card_browser.mjs`, `tests/card_rig.mjs`, `tests/closure.py`, `tests/env_drift.py`, `tests/lane_skip.py`, `tests/mutation_table.py`, `tools/pr/codeql_scope.py` and `tools/release/stamp.py`.

**The change.**
- **Roster ref.** `roster_lib.default_roster_ref(git)` returns the round's roster branch `origin/handoff/audit-r<N>-roster`. Without that branch it falls back to `origin/main` with a note. It warns when main carries roster changes the branch lacks. The tick, `plan_table.py`, `resume_doc.py`, `handover_prompt.py` and `state_docs.py` resolve through it, and the state-docs beat also watches the roster ref.
- **Level 0** (`tests/lane_skip.py`). When every changed file is a roster or a canonical delivery row, `browser`, `coverage` and `typing` skip, with no recorded proof. `fast` never takes Level 0.
- **One changed-file list that keeps both sides of a rename.** `tests/closure.py` `changed_between` / `changed` (`--no-renames`) feeds the gate, lane_skip, the `tests.yml` list sites and CodeQL. `tools/pr/codeql_scope.py` `changed_files` delegates to it. The twins pass `--no-renames` too: `card_rig.mjs` `threeDotFiles`, `card_browser.mjs` `gridScope`, `stop-selfcheck.sh`, `policy_lint.mjs` `mergeRecordClass` with `stamp.py` `merge_is_record_class`, and the seat and pr scripts. The census in the closure self-test refuses any `git diff ... --name-only` without `--no-renames` over the `RENAME_SITES` globs.
- **The `graders-head-copy` pin follows its step.** That job's changed-file step runs `python tests/closure.py changed`. `tests/entities.py` `_PT_JOB_CANON` carries the same line. `_pt_trigger` executes the step in a planted repo, so that repo's base commit carries this tree's `tests/closure.py`, and `python` there resolves to the running interpreter. The trigger check runs the real producer. The `RENAME_ALLOW` entry that called the old canon line "data, never run" is deleted, because `_pt_trigger` ran it all along. Rejected alternative: keep a self-contained `git diff --no-renames --name-only` in the step. The census allows it, but it is a second producer beside `closure.py changed`, which this PR exists to remove.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`22803f99bd8be29012a668ef22140dd12ae3aa5e`: the orchestrator's merge of origin/main `06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b` over `82095a68d` (which has the tree of `26b148e5b6f2114803da0c571c33c55d217232ce`, the head every figure below was taken at). Merge base `06c6f3cf2`, which is origin/main. This pass changed no code: round 7's block was a missing carry destination, and the fix is a roster edit. The reviewer re-derived the main merge's delta and found it clean (round 7 verdict: `closure.rename_sites()` `([], [])`, `prepr.sh --self-test` `290 passed, 0 failed`, `git merge-tree` rc 0). The figures and mutants below were measured at `26b148e5b` on 2026-10-19.

## Mutation proof

Each mutant edits one file in a detached worktree at `26b148e5b`, runs the named check, and is discarded. The `entities.py` mutants ran `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`.
- **M1: the planted repo's copy of `tests/closure.py` removed from `_pt_trigger`** (the `Path(_td, "tests", "closure.py").write_text(...)` line deleted). `2 of 2349 ENTITY CHECKS FAILED`: `and the arm's trigger fires on a restored path and only there` (`outputs=[]` for all three planted paths) and `and a trigger whose firing branch writes false is refused (null control)`.
- **M3: `_PT_JOB_CANON`'s changed-file line set back to `git diff --name-only "$BASE"..."$HEAD"`.** `2 of 2349`: `every pinned grader given a token runs its own copy under the Actions token on the pull request` (`arm mismatch=graders-head-copy.steps[2].run`) and `and any edit to the arm's job, or to what reaches it, disarms it (null control)`.
- **MS: `rename_sites`' stale list emptied** (`if i not in used` to `if False`). `python3 tests/closure.py selftest`: `1 of 124`, `and reports every allow entry nothing matches as stale`.
- **MP: `--no-renames` dropped from `closure.changed_between`.** closure selftest `3 of 124` (`the changed list keeps both sides of a rename onto a delivery row`, `so the gate does not scope a deleted entry point to zero scripts`, `no rename-detecting --name-only diff under RENAME_SITES`), `lane_skip self-test: 51/54 pins passed`, and `codeql_scope self-test: 47 checks, 2 failed`.
- **MB17: `codeql_scope.changed_files` replaced by its own `--no-renames` diff.** `47 checks, 1 failed`: `the list is closure.changed_between's, not a copy (#2406)`.
- **MB15: `--no-renames` dropped from `stamp.py` `merge_is_record_class`.** `node tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS: recordClassPaths`, and `closure.rename_sites()` names `tools/release/stamp.py:1708`.
- **MB19: `--no-renames` dropped from `mergeRecordClass`'s real call.** policy_lint exits 1 with `FIXTURE VACUOUS: recordClassPaths`, and `closure.rename_sites()` names `tools/policy/policy_lint.mjs:2356`.
- **M2 (the `PATH` entry giving the planted step its `python`) was not re-run.** It needs a box whose `PATH` has no `python`, and this seat's shims provide one. The body claims nothing from it. `## Unpinned sites` says what that entry is.

## Null control

- The unmodified head: `ALL 2349 ENTITY CHECKS PASSED`. Each mutant above fails on the named checks only, and the two `entities.py` mutants fail two checks each out of 2349.
- The rename probes (`closure._rename_probe_lists`, and codeql_scope's `git mv lib.py lib.md`) read one commit both ways. Porcelain lists only the destination, and the producer lists both sides.
- The census's planted root refuses the porcelain line in `x.py`, `y.mjs` and a split `z.sh`, and passes the `--no-renames` twin beside each one. With an empty `tools/policy/policy_lint.mjs` planted, every allow entry reads stale.
- Each red below was read at the CI run that produced it, and the same command was re-run on this head. A check that read red for a main-side cause must read green here, and the command in `## Figures` prints the opposite string when it does not.

## Figures

All taken at `26b148e5b` on 2026-10-19, merge base `b87e8f19b`:
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` (Python 3.14): `ALL 2349 ENTITY CHECKS PASSED`.
- `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
- `closure.rename_sites()` (`python3 -c "import sys; sys.path.insert(0,'tests'); import closure; print(closure.rename_sites())"`): `([], [])`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <tmp>`: `MODE: FULL`, because `.github/workflows/tests.yml` changes the gate itself. The `run_always` scripts were run as listed here, and `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`.
- `python3 tests/lane_skip.py self-test`: `54/54 pins passed`.
- `python3 -I tools/pr/codeql_scope.py --self-test`: `47 checks, 0 failed`.
- `python3 tools/audit/seat/roster_lib.py --self-test`: `18 checks, 0 failed`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `104 checks, 0 failed`.
- `python3 tools/audit/seat/state_docs.py --self-test`: `all checks passed`.
- `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`, with no `VACUOUS`.
- `python3 tests/layout.py --guard --base origin/main`: `GUARD: 0 refusal(s)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `RESULT uncovered_files=0`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/policy/agreement_py.py --out <tmp>/agreement.json`, then `node tools/policy/agreement.mjs --py-json <tmp>/agreement.json`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`. This is `wave-script`'s own command. The failing run printed `divergent=2` for the `merge-subject-pr` pair.
- `git fetch --no-tags origin main; python3 -I -S tests/delivery_status.py --check`: `DELIVERY STATUS OK -- 136 rowed, 2 pending, 0 overdue`. This is `delivery-status`'s own command. The failing run printed `3 overdue` (`#2413`, `#2412`, `#2407`).

## Unpinned sites

- **The `tests.yml` wiring** (`typing`'s `needs` and `if:`) and **the CodeQL scope job's import of `tests/closure.py`**. No local check drives a workflow. CI on this head runs every lane and the `scope` job. The first record-only head after merge should show three `skipped`.
- **The `PATH` entry in `_pt_trigger`** survives a mutant on any box that has `python` on `PATH`, CI included. It is kept so the check holds on a seat that has only `python3`.

## Red checks

Read from the check-runs API (`repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`, conclusion `failure`). At the PR head `2d9f20009`'s latest CI, four runs are red: `wave-script`, `delivery-status` and two `pr-contract` runs. The last three entries of this list are red on earlier commits of the branch and were answered in earlier rounds.

- **`wave-script`** (at `2d9f20009`, job 117830442120): `AGREEMENT REFUSED`, `merge-subject-pr` divergent on `Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)` and `#2379`, where `policy_lint.mjs` `resolvePrFromCommit` and `enumerateMerges` read `null` and `stamp.py` and `delivery_status.py` read the number. Not this PR's: this diff changes neither `agreement.mjs` nor `agreement_py.py`, and in `policy_lint.mjs` it changes `mergeRecordClass` and the record-class parity arm, not `resolvePrFromCommit` or `enumerateMerges`. Main itself was red on this check from `5756f2b1`. Cleared by the merge of origin/main `b87e8f19b`, which carries `#2423` and `#2424` (the one merge-subject grammar and its guard): the command above prints `divergent=0` on this head. Cheaper detector: the check itself, on main's push, which is how main's red was seen. Standing cost: one `node` and one `python3` run of about a second.
- **`delivery-status`** (at `2d9f20009`, job 117830442352): `DELIVERY STATUS OVERDUE`, 3 overdue rows (`#2413`, `#2412`, `#2407`). It grades `main`, not this branch, and `pr-contract` flags it because this diff touches `.github/workflows/tests.yml`. This diff does not touch `tests/delivery_status.py`, the file the check restores and runs. Cleared by the merge of origin/main `b87e8f19b`, whose `#2420` wrote the missing rows for `#2407`, `#2412`, `#2413` and `#2423`: the command above prints `0 overdue` on this head. The check is not a required context. Cheaper detector: the check itself, whose standing cost is one `git`-only script run. It already fires on main, so none cheaper is owed.
- **`pr-contract`** (two runs at `2d9f20009`, jobs 117830438954 and 117830750613): the body did not name `delivery-status` and then `wave-script`, both red at the head. Answered by the two entries above. The check is the cheaper detector: `tools/pr/prepr.sh` runs the same rule on the seat before the push, at a cost of seconds, and ran on this body (below).
- **`fast (3.14)`** (at `b965c4ab9` and `d1becac2b`, job 117746495595): `2 of 2347 ENTITY CHECKS FAILED`, the two M3 checks. This PR's own: it changed `graders-head-copy`'s step without the `_PT_JOB_CANON` literal and the planted repo the step needs. Fixed at the earlier head, reproduced by M1 and M3 above. Cheaper detector: `tests/entities.py` on the seat, at a standing cost of about 270 s (that job's timing line, `FAILED python3 tests/entities.py (269s)`). It existed already, but fixer.md step 5 leaves a `MODE: FULL` diff to CI. Answered in `## Friction`.
- **`closures`** (at `b965c4ab9`, job 117725439310): `UNDER-SCOPED: tests/card.mjs really reads 1 file(s) the committed closure does not list: tests/env_drift.py`. Bot-repaired by `closures-autofix` (commit `f95578604`, `ci: re-record closures`). The cheaper detector is `ci-autofix.md`'s, already running.
- **`nightly-ha (stable)`** (at `f95578604`, job 117731309720): `hb:positive_control` failed on its py-spy leg (`py-spy dump` timed out after 30 seconds), and `run:exit_status` is the container's exit from that failure. `nightly-ha (2025.2.0)` passed on the same commit. No cheaper detector exists: only this container lane runs py-spy inside the `homeassistant/home-assistant:stable` image.

- **`pr-contract` reading main's roster.** `pr-contract` and `carry_audit` read the roster on `origin/main`, not the roster branch. R10-STAMP lands on main with roster PR #2417. Until then a `BAD-DEST` red there is that lag, not this PR: the destination named in `## Forward-carry` exists on `origin/handoff/audit-r10-roster` and resolves there.

## Forward-carry

- Carry: R10-STAMP (`dev/programme/rosters/wave-r10-groups.json`, on `origin/handoff/audit-r10-roster` at `73bb15fe8f5bf05ec3568927118a8d678dd8b99f`). R10-STAMP is the post-drain stamp group, `resume.stage: not-started`, so it runs after this PR merges and is a destination a later seat reads. The beat restart was moved there from R10-TICK-DRIVERS, which is `done` (#2390), with its control unchanged: after this PR merges, restart the state-docs beat on main's code with no `--roster-ref` and no `--watch-ref refs/heads/main`. Check: the memo holds two SHAs, main's and the roster branch's, and a roster-only commit regenerates the plan within one beat. Read back from the roster branch: it is the last entry of R10-STAMP's `carry`.
- The CodeQL delegation carry is done in this PR, so it needs no destination. `roster_edit.py` has no verb that removes a carry entry, so both #2406 entries remain in R10-TICK-DRIVERS' `carry` (a `done` group, which nothing dispatches or lints). The orchestrator removes them by hand if it wants them gone. Carry: dismissed: the CodeQL delegation is done in this diff, and the beat-restart entry is carried to R10-STAMP above; the stale entries in a done group are inert.


## Friction

- fixer-step-5: unenforced: under `MODE: FULL`, step 5 leaves every script to CI, so a `tests.yml` edit that breaks `tests/entities.py`'s `_PT_JOB_CANON` pin went red only on CI (`fast (3.14)` at `b965c4ab9` and `d1becac2b`). Running `tests/entities.py` locally whenever a diff touches `.github/workflows/tests.yml` would catch it at push time. Carry: dismissed: a change to fixer.md step 5 is a policy edit that needs tvofi's approval and is not this PR's scope; this entry is the record of the event.
