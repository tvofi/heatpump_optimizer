_Requested by **tvofi**_

O17 item 1 (tooling) and item 2(ii), from the roster-cost pre-study the orchestrator accepted on 2026-10-18. Part of #201. No roster group lists an issue for this work, so this body closes none. The policy half is `handoff/r10-roster-carry-policy`.

**Owner gate.** tvofi approves at merge. The code-owned files are `.github/workflows/tests.yml`, `.claude/hooks/stop-selfcheck.sh`, `tests/card_browser.mjs`, `tests/card_rig.mjs`, `tests/closure.py`, `tests/env_drift.py`, `tests/lane_skip.py`, `tests/mutation_table.py`, `tools/pr/codeql_scope.py` and `tools/release/stamp.py`.

**The change.**
- **Roster ref.** `roster_lib.default_roster_ref(git)` returns the round's roster branch `origin/handoff/audit-r<N>-roster`. Without that branch it falls back to `origin/main` with a note. It warns when main carries roster changes the branch lacks. The tick, `plan_table.py`, `resume_doc.py`, `handover_prompt.py` and `state_docs.py` resolve through it, and the state-docs beat also watches the roster ref.
- **Level 0** (`tests/lane_skip.py`). When every changed file is a roster or a canonical delivery row, `browser`, `coverage` and `typing` skip, with no recorded proof. `fast` never takes Level 0.
- **One changed-file list that keeps both sides of a rename.** `tests/closure.py` `changed_between` / `changed` (`--no-renames`) feeds the gate, lane_skip, the `tests.yml` list sites and CodeQL. `tools/pr/codeql_scope.py` `changed_files` delegates to it. The twins pass `--no-renames` too: `card_rig.mjs` `threeDotFiles`, `card_browser.mjs` `gridScope`, `stop-selfcheck.sh`, `policy_lint.mjs` `mergeRecordClass` with `stamp.py` `merge_is_record_class`, and the seat and pr scripts. The census in the closure self-test refuses any `git diff ... --name-only` without `--no-renames` over the `RENAME_SITES` globs.
- **The `graders-head-copy` pin follows its step.** That job's changed-file step now runs `python tests/closure.py changed`. `tests/entities.py` `_PT_JOB_CANON` carries the same line. `_pt_trigger` executes the step in a planted repo, so that repo's base commit now carries this tree's `tests/closure.py`, and `python` there resolves to the running interpreter. The trigger check runs the real producer. The `RENAME_ALLOW` entry that called the old canon line "data, never run" is deleted. `_pt_trigger` ran it all along, and the census reports the entry stale once the line is gone. Rejected alternative: keep a self-contained `git diff --no-renames --name-only` in the step. The census allows it, but it is a second producer beside `closure.py changed`, which this PR exists to remove.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_016Dpdz1tMLedATWEABB5h71

## Head

`42a8c31a8540eba8b197259af952d0cbfae8928e`: the round-5 head `d1becac2b`, merged with origin/main `86010e8cd`, plus `8baa13e47` (the pin) and `cfd418c71` (the allow entry), merged with origin/main `5756f2b15`. Merge base `5756f2b1578198b7e6f7f62ea33153f2506a7bd3`, which was origin/main at 2026-10-18 19:14 UTC. At that tip, `git merge-tree --write-tree origin/main HEAD` exited 0.

## Mutation proof

Each mutant edits one file at `42a8c31a8`, runs the named check, and is restored. The `entities.py` mutants ran in detached worktrees at the head, with `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`.
- **M1: the planted repo's copy of `tests/closure.py` removed from `_pt_trigger`.** `2 of 2349 ENTITY CHECKS FAILED`: `and the arm's trigger fires on a restored path and only there` (`outputs=[]` for all three planted paths) and `and a trigger whose firing branch writes false is refused (null control)`. This is round 5's failure, reproduced.
- **M3: `_PT_JOB_CANON`'s line set back to `git diff --name-only "$BASE"..."$HEAD"`.** `2 of 2349`: `every pinned grader given a token runs its own copy under the Actions token on the pull request` (`arm mismatch=graders-head-copy.steps[2].run`) and `and any edit to the arm's job, or to what reaches it, disarms it (null control)`. This is `fast (3.14)`'s failure at `d1becac2b`.
- **M2: the `PATH` entry giving the planted step its `python` removed.** Run with a `python` on `PATH` that exits 127 (a seat with no `python`, only `python3`): `3 of 2349`, the two M1 checks plus the coverage-cache row. **M0**, the head under the same `PATH`: `1 of 2349`, the coverage-cache row alone. That row runs a `python` of its own, so the shadow fails it either way. The trigger checks are the difference.
- **MS: `rename_sites`' stale list emptied** (`if i not in used` to `if False`). `python3 tests/closure.py selftest`: `1 of 124`, `and reports every allow entry nothing matches as stale`.
- **MP: `--no-renames` dropped from `closure.changed_between`.** closure selftest `3 of 124` (`the changed list keeps both sides of a rename onto a delivery row`, `so the gate does not scope a deleted entry point to zero scripts`, the census), `lane_skip self-test: 51/54`, and `codeql_scope self-test: 47 checks, 2 failed`.
- **MB17: `codeql_scope.changed_files` replaced by its own `--no-renames` diff.** `47 checks, 1 failed`: `the list is closure.changed_between's, not a copy`.
- **MB15: `--no-renames` dropped from `stamp.py` `merge_is_record_class`.** `node tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS: recordClassPaths`, and `closure.rename_sites()` names `tools/release/stamp.py:1708`.
- **MB19: `--no-renames` dropped from `mergeRecordClass`'s real call.** policy_lint exits 1 with `FIXTURE VACUOUS: recordClassPaths`.

## Null control

- The unmodified head: `ALL 2349 ENTITY CHECKS PASSED`. Each mutant above fails, on the named checks only.
- The rename probes (`closure._rename_probe_lists`, and codeql_scope's `git mv lib.py lib.md`) read one commit both ways. Porcelain lists only the destination, and the producer lists both sides.
- The census's planted root refuses the porcelain line in `x.py`, `y.mjs` and a split `z.sh`, and passes the `--no-renames` twin beside each one. With an empty `tools/policy/policy_lint.mjs` planted, every allow entry reads stale.

## Figures

All taken at `42a8c31a8` in this pass:
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` (Python 3.14): `ALL 2349 ENTITY CHECKS PASSED`.
- `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
- `closure.rename_sites()` (`python3 -c "import sys; sys.path.insert(0,'tests'); import closure; print(closure.rename_sites())"`): `([], [])`.
- `python3 tests/closure.py select --diff 5756f2b15 --workdir <tmp>`: `MODE: FULL`, because `.github/workflows/tests.yml` changes the gate itself. The `run_always` scripts were run as listed here, and `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/env_drift.py --claims-only 5756f2b15`: `claims hygiene: ... ok`.
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
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`.
- `python3 tools/audit/archscore/score.py --diff 5756f2b1578198b7e6f7f62ea33153f2506a7bd3 HEAD`: `dS +0.0000 NULL`.

## Unpinned sites

- **The `tests.yml` wiring** (`typing`'s `needs` and `if:`) and **the CodeQL scope job's import of `tests/closure.py`**. No local check drives a workflow. CI on this head runs every lane and the `scope` job. The first record-only head after merge should show three `skipped`.
- **The `PATH` entry in `_pt_trigger`** survives a mutant on any box that has `python` on `PATH`, CI included. M2 kills it only under a `PATH` without `python`. It is kept so the check holds on a seat that has only `python3`.

## Red checks

Read from the check-runs API (`repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`, conclusion `failure`) on the branch's commits past the merge base.

- **`fast (3.14)`** (at `b965c4ab9`, then `d1becac2b`, job 117746495595): `2 of 2347 ENTITY CHECKS FAILED`, the two M3 checks. This PR's. It changed `graders-head-copy`'s step without the `_PT_JOB_CANON` literal and the planted repo the step needs. Fixed at this head (M1, M3). Cheaper detector: `tests/entities.py` on the seat, at a standing cost of about 270 s (that job's timing line, `FAILED python3 tests/entities.py (269s)`). It existed already, but fixer.md step 5 leaves a `MODE: FULL` diff to CI. Answered in `## Friction`.
- **`closures`** (at `b965c4ab9`, job 117725439310): `UNDER-SCOPED: tests/card.mjs really reads 1 file(s) the committed closure does not list: tests/env_drift.py`. Bot-repaired by `closures-autofix` (commit `f95578604`, `ci: re-record closures`). The cheaper detector is `ci-autofix.md`'s, already running. `_pt_trigger` now reads `tests/closure.py`, so CI may print `UNDER-SCOPED` for `tests/entities.py` on this head. The same bot repairs it.
- **`nightly-ha (stable)`** (at `f95578604`, job 117731309720): `hb:positive_control` failed on its py-spy leg (`py-spy dump` timed out after 30 seconds), and `run:exit_status` is the container's exit from that failure. `nightly-ha (2025.2.0)` passed on the same commit. No cheaper detector exists: only this container lane runs py-spy inside the `homeassistant/home-assistant:stable` image.

## Forward-carry

- Carry: R10-TICK-DRIVERS (`dev/programme/rosters/wave-r10-groups.json`). After this PR merges, restart the state-docs beat on main's code with no `--roster-ref` and no `--watch-ref refs/heads/main`. Check: the memo holds two SHAs, main's and the roster branch's, and a roster-only commit regenerates the plan within one beat. The CodeQL delegation carry is done in this PR, so the orchestrator drops it from that group.

## Friction

- fixer-step-5: unenforced: under `MODE: FULL`, step 5 leaves every script to CI, so a `tests.yml` edit that breaks `tests/entities.py`'s `_PT_JOB_CANON` pin went red only on CI (`fast (3.14)` at `b965c4ab9` and `d1becac2b`). Running `tests/entities.py` locally whenever a diff touches `.github/workflows/tests.yml` would catch it at push time.
