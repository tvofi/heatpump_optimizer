R10-FLOW-BODY-PATCH (Lean flow study K14, expedite). No tool PATCHed a pull request's body alone: `app_push.sh` mints, pushes, then PATCHes, and `update_pr.sh` merges main on every run, so a body `pr-contract` or `carry_audit` refused stayed red or cost a head move (ruling R4 forbids moving a clean head; #2560's 111 to 113 figure is the open case). This adds `tools/audit/seat/body_patch.sh [--dry-run] [--repo O/R] <pr> <expected-head-sha> <body.md>`: it refuses unless the live head is the expected sha, runs the body contract offline at that head (`policy_lint.mjs --pr-body` with pr-contract's own arguments, then `carry_audit.py check --body`), PATCHes `{"body"}` as `hpo-author`, reads the body back (identical modulo one trailing newline, `app_push.sh`'s measured rule) and re-reads the head. The mint is factored out of `app_push.sh` into `tools/pr/app_mint.sh` and sourced by both. One `--once` unit: arguments in, exit code and a last `body_patch: OK|REFUSE` line out, so R10-ORCH-MACHINERY's beat hosts it unchanged. Not run live: no pull request was patched here (the orchestrator runs it).

Code-owned files touched: `.github/workflows/governance.yml` only (`/.github/workflows/` is `@tvofi`), one added step in `instrument-self-tests`. `tools/pr/app_push.sh`, `tools/pr/app_mint.sh`, `tools/audit/seat/body_patch.sh` and `INSTRUMENTS.md` carry no code owner.

## Head

`94ef8a7d7bfddda09f1698f75ff06f466a085f69` merges the authored code head `dcb7f980bddc8caed8dfbd9bf033b125fc30d7e8` and then merges origin/main `93e6a63d2` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`dcb7f980bddc8caed8dfbd9bf033b125fc30d7e8` merges origin/main `93e6a63d2855651448a2b8f677b392feddc03c99` (after #2572 and #2557) into the previous head `36ca386d6`, by the fixer seat, with two content conflicts resolved by hand (see `## Conflict resolution`). The PR's own diff against the merge base is unchanged in content apart from those two resolved hunks: 7 files, +534 / -37 (`git diff --stat $(git merge-base origin/main HEAD) HEAD`).

`36ca386d6a830a90096df6821b85abfad0c6a1f9` merges main `1ebc737` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`48cc0918a4ed912d4149d088d0ca6191cf8cf1dc` merges main `57f0c9c` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`3f22a805c7ca335f15a6b218d6aa15a7cec8bb20` merges the authored code head `1554a032ffa9c1d268dd7a83d31e568602ff561f` and then merges origin/main `f2fb1b0e9` (an automatic merge by the orchestrator's script) into this PR's previous head.

`18e7a7c61f2b07691d4d00f49d6a8658eb16d7d6` (code head on `handoff/r10-flow-body-patch`, cut from `e7c664856776542bf60bd770c98aba1eaadb4041`); `ab80640b8` (in `1554a032f`) makes the read-back success a flag only an ok read sets.

Every figure below is measured at `dcb7f980b`, origin/main at `93e6a63d2` (2026-10-22T01:40Z).

## Conflict resolution

`git merge-tree --write-tree origin/main 36ca386d6` reported two content conflicts. Main's side of both is #2529 (`fix/r10-ci-layout-g`, commit `a164f8ec5`), found with `git log origin/main ^1ebc737e7 -- <file>`.

- `.github/workflows/governance.yml`, job `instrument-self-tests`, the region after the `selftest_wiring --check` step: this PR adds the step `Show the body PATCH refusing its own fixtures`; #2529 adds `Show the self-tests outside tools/audit/seat/ refusing their own fixtures` at the same insertion point. Choice: keep both steps, this PR's first, then #2529's, each unchanged byte for byte. They are independent steps (no shared variables, each `if: ${{ !cancelled() }}`), so order changes neither. Both survive: the mutants harness's M0 runs this PR's step green (`body_patch self-test: 62 checks, 0 failed`) and `selftest_wiring --check` counts both files wired; #2529's step, extracted from the merged workflow and run under `bash -e`, exits 0 (all 14 self-tests plus `agreement_py --restore`: `13 closure file(s), 13 covered by the wave-script restore list, 0 missing`).
- `dev/audit/harnesses/r10_seat_selftests_mutants.py`, two hunks. (a) The module docstring's id range: this PR wrote `S01..S34 and the per-file ids (body_patch-1)`, #2529 wrote `S01..S38`. Choice: `S01..S38 and the per-file ids (body_patch-1)`, which is true of the merged list. (b) The `MUTANTS` list tail after `S34`: #2529 adds `S35`..`S38` (handoff_push.sh push lines, merge_pr.sh's `gh pr merge` line); this PR adds `body_patch-1` (the read-back exhaustion). Choice: keep all five, #2529's four then `body_patch-1`, each tuple unchanged. Both survive: the harness run below reports every one of `S35`, `S36`, `S37`, `S38` and `body_patch-1` KILLED, with M0 green on the unmutated tree.

No job, step, mutant or check was dropped from either side: `git diff 36ca386d6 HEAD -- dev/audit/harnesses/r10_seat_selftests_mutants.py` adds only main's lines and the docstring merge, and `git diff origin/main HEAD -- .github/workflows/governance.yml` adds only this PR's step.

## Mutation proof

Predicate lines of the production file are tagged `# mut:<arm>`; the self-test deletes each from a copy and its control must stop refusing. Separately, each of the ten arms the self-test's `mutant` table names (`head`, `prew`, `lint`, `carry`, `rb`, `rbhead`, `rbx`, `eq1`, `exist`, `dot2`) was applied to the production file itself with that table's own sed expression and the whole self-test run, then the file restored from a copy (`git status --short tools/audit/seat/body_patch.sh` empty after). Rule: `sed -n 401,410p tools/audit/seat/body_patch.sh | while read -r _ name expr; do sed -i "$expr" F; bash F --self-test | tail -1; restore; done`, with a `cmp` against the original that would print VACUOUS for an expression that changes nothing (none did). Failed checks of 62 per arm: head 2, prew 2, lint 8, carry 3, rb 4, rbhead 1, rbx 3, eq1 2, exist 1, dot2 1. Ten of ten arms red; restored, `body_patch self-test: 62 checks, 0 failed`.

The harness `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` at this head: `M0: 0 seat step(s) red`, `== body_patch-1 body_patch.sh: KILLED rc=1 | body_patch self-test: 62 checks, 3 failed`, main's `S35`/`S36`/`S37` (`handoff_push self-test: 2 checks, 1 failed`) and `S38` (`merge_pr self-test: 16 checks, 2 failed`) KILLED, `RESULT survivors=0`.

## Null control

The base tree has no body-only tool (`ls tools/audit/seat/body_patch.sh` in a detached worktree at origin/main `93e6a63d2`: `No such file or directory`), and the failing test came first: the self-test was written before the script's predicates, against the stub `gh`/`curl`/`openssl`/`node`. Healthy-arm controls pair every refusal: the passing run PATCHes exactly once and reads back, `--dry-run` leaves the live body untouched, a moved head leaves it untouched with zero curl calls (refused before the mint), and a body the contract refuses makes zero curl calls. For "a refused body is never sent": with `lint-fails`/`carry-fails` set the PATCH count is 0, and with each arm deleted (above) the self-test reddens. The mutants harness's own null control is M0: every seat step runs green on the unmutated tree before any mutant is counted. The mint refactor's control: `app_push.sh --self-test` here and at origin/main read the same count (Figures).

## Figures

- `bash tools/audit/seat/body_patch.sh --self-test` prints `body_patch self-test: 62 checks, 0 failed` (the count is its own rule: one `st` per assertion).
- `bash tools/pr/app_push.sh --self-test` prints `app_push self-test: 182 checks, 0 failed` at this head and in a detached worktree at origin/main `93e6a63d2`: the mint refactor changes no behaviour its 182 checks pin. Instrument: app_push.sh's own self-test.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 74 self-testing, 74 wired, 0 unwired` here, and `73 self-testing, 73 wired, 0 unwired` at origin/main: the new file is the one added and is wired by its governance.yml step. Null control in the harness: W1 (an unwired file) reads `75 self-testing, 74 wired, 1 unwired`.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`: rc=0, `M0: 0 seat step(s) red`, `RESULT survivors=0` (every S/W/per-file mutant KILLED, per the harness's own rule: the step naming the mutated file reddens).
- #2529's step `Show the self-tests outside tools/audit/seat/ refusing their own fixtures`, its `run:` text extracted from this head's governance.yml with PyYAML and run under `bash -e` with a scratch `RUNNER_TEMP`: rc=0.
- Real arms, offline null control (the arms the script calls, outside the stubs): `node tools/policy/policy_lint.mjs --pr-body <"hello"> --head <sha> --title t --author hpo-author --paths-file F --existing-file F` exits 1; `python3 -I tools/audit/carry_audit.py check --body <"## Forward-carry / - a real finding with no owner">` exits 1 and prints `CARRY-AUDIT: 1 finding item(s): 0 routed, 1 unrouted, 0 bad destination(s)`; the same with `## Forward-carry` = `none` exits 0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, changed files (7). The two named run green with PYTHONPATH=tests/hastub on a python3.13 venv built from `tests/requirements-ci.txt` with `--require-hashes` (`seat_venv.sh` refused here: `No download found for request: cpython-3.14.7-linux-x86_64-gnu`): `tests/entities.py` prints `ALL 2382 ENTITY CHECKS PASSED`, `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget touched, no raise.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL` (shell, workflow and harness only).
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py`, arm `none`: `uncovered_files=0`, `enforcement_surface_files=135` here and `134` at origin/main (the one added file, `body_patch.sh`, pinned, run by no PR job as every sibling seat script); its `unpin` perturbation arm reads `uncovered_files=18`, the script's own null control. Seams the class enumerates (every minter of an App token): `grep -rn "POST.*access_tokens" tools/pr tools/audit/seat | grep -v "STUB\|printf"` returns three — `tools/pr/app_mint.sh` (the one author-App mint, shared in this diff by `app_push.sh` and `body_patch.sh`); `tools/pr/app_approve.sh` and `tools/pr/app_comment.sh` mint the distinct `hpo-approver` identity and are left alone. No other author-App minter exists.

Alternatives and why each lost: a `--body-only` flag on `app_push.sh` (it requires a clean worktree at the branch tip, runs the whole prepr and the ref-privacy guard against a push that never happens, and is R10-FLOW-BODY-ONLY's scope); copying the mint into the new script (the brief forbids it; two mints drift on how a token is held and revoked); `gh api --method PATCH` as the caller (the author must be `hpo-author`, decision 0011).

## Red checks

From the check-runs API (`repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`), per commit:

- `36ca386d6`: 49 check runs, one failure, `nightly-status`.
- `48cc0918a`: 49 check runs, one failure, `nightly-status`.
- `3f22a805c`: 49 check runs, one failure, `nightly-status`.
- `1554a032f`, `ab80640b8`, `18e7a7c61`: 0 check runs (handoff heads, never a PR head).
- `dcb7f980b`: not yet run (this push).

`nightly-status` (tests.yml, `if: github.event_name == 'pull_request'`) grades the scheduled lanes' runs on `main`, which are Actions metadata, not this branch's content: the scheduled `tests.yml` runs on main concluded `failure` on 2026-10-19, -20 and -21, and the same check is red at the heads of #2557 (`a9f187ea9`) and #2572 (`e5845f90c`), which share no file with this diff. It is not caused or fixable by this change; the cheaper detector for the class it reports is the nightly lane itself, already running. No other check went red on any commit of this PR.

## Forward-carry

- The beat's job table should list `body_patch.sh` as a hosted one-shot (arguments pr, sha, body; success = exit 0 and a last `body_patch: OK` line). Carry: R10-ORCH-MACHINERY
- The read-back equality (one trailing newline) is now stated in two scripts (`app_push.sh` `read_once` and `body_patch.sh` `verdict`); a third reader would justify one shared function. Carry: dismissed: two readers only, merging them couples the push path to a body-only tool.

## Friction

- finding-propagation: unclear: a seam note for FLOW-BODY-PATCH in STUDY K17 names the beat but not the argument shape a hosted job takes, so this seat chose positional arguments and an `OK|REFUSE` last line. Carry: R10-ORCH-MACHINERY

