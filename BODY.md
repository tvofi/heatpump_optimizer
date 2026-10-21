Group: R10-FLOW-BODY-PATCH (registration pending: roster PR-B), `dev/programme/flow-study/roster/groups/R10-FLOW-BODY-PATCH.json` at pack commit 78117030 on branch claude/dazzling-gauss-7l3u2b.

R10-FLOW-BODY-PATCH (Lean flow study K14, expedite, size S). No tool PATCHed a pull request's body alone: `app_push.sh` mints, pushes, then PATCHes, and `update_pr.sh` merges main on every run, so a body `pr-contract` or `carry_audit` refused stayed red or cost a head move (ruling R4 forbids moving a clean head). This adds `tools/audit/seat/body_patch.sh [--dry-run] [--repo O/R] <pr> <expected-head-sha> <body.md>`: it refuses unless the live head is the expected sha, runs the body contract offline at that head (`policy_lint.mjs --pr-body` with pr-contract's own arguments, then `carry_audit.py check --body`), PATCHes `{"body"}` as `hpo-author`, reads the body back (identical modulo one trailing newline, `app_push.sh`'s measured rule) and re-reads the head. The mint is factored out of `app_push.sh` into `tools/pr/app_mint.sh` and sourced by both. One `--once` unit: arguments in, exit code and a last `body_patch: OK|REFUSE` line out, so R10-ORCH-MACHINERY's beat hosts it unchanged. Not run live: no pull request was patched here (the orchestrator runs it).

Round 2 (fix review `blocked 50c4a681`): the read-back's retry exhaustion could report success. Its `die` was the only thing between the exhausted loop and the `OK` line, so `|| die` -> `|| break` printed `OK` for a body never read back. The loop now exits success only through `rbok=1`, set by an `ok` verdict alone, and the `OK` line sits past a guard on `rbok`; no loop exit but a good read reaches it. The reviewer's other three survivors (equality relaxed to `strip()`, `--diff-filter=a` dropped, two-dot diff) are killed by new fixtures, and the offline-versus-pr-contract divergence is documented in the script header and `INSTRUMENTS.md`. The round-1 sentence citing "#2560's 111 to 113 figure" as the open case is removed: STUDY K14 revision 4 at the pack pin states it was not a live case.

Code-owned files touched: `.github/workflows/governance.yml` only (`/.github/workflows/` is `@tvofi`), one added step in `instrument-self-tests`. `tools/pr/app_push.sh`, `tools/pr/app_mint.sh`, `tools/audit/seat/body_patch.sh`, `INSTRUMENTS.md` and the harness file carry no code owner.

## Head

`1554a032ffa9c1d268dd7a83d31e568602ff561f` (code head on `handoff/r10-flow-body-patch`: the round-1 PR head `50c4a681d` plus one fix commit plus a merge of `origin/main` `290712ec0d342e3fa9b96e4533615024bc4c05b7`, fetched 2026-10-21T17:05Z; `git merge-tree --write-tree origin/main 1554a032f` exits 0). Every figure below was taken at this head; those that are a function of `origin/main` carry that tip.

## Mutation proof

Predicate lines of the production file are tagged `# mut:<arm>`; the self-test deletes each from a copy and its control must stop refusing. Separately each arm was deleted from the production file itself, the whole self-test run, and the file restored (`git status --short` empty afterwards; `sed '/# mut:<arm>$/s/.*/:/'`, with the replacement stated where it is not a deletion). Every deletion turns named checks red:

- head: `naming the reason`, `no curl, no contract: refused before any write or mint`;
- prewrite: `REFUSE: the head moves between the check and the write`, `no PATCH was sent`;
- contract: `policy_lint gets pr-contract's arguments`, `REFUSE: policy_lint refuses the body`, `never sent, never minted`, `its paths are what the head changes against the base`;
- carry: `carry_audit check --body runs on the same body`, `REFUSE: carry_audit refuses the body`;
- readback (replaced by `rbok=1; break`): `REFUSE: the body read back is not the body sent`, `and no OK line`;
- rbhead (replaced by `rbok=1; break`): `REFUSE: the head is found moved on the read-back`;
- **rbexhaust (new, the blocking item)**: the guard line deleted, and separately `|| die ...` replaced by `|| break` (the reviewer's mutant): `REFUSE: no read-back can be performed (retry exhaustion)`, `and no OK line: a body never read back is not reported patched`, `naming the reason`;
- eq1 (new, equality relaxed to `a.strip() == b.strip()`): `REFUSE: the body read back differs only in trailing whitespace beyond the one newline`, `and no OK line`;
- existing (new, `--diff-filter=a` dropped): `its existing paths are the files the base already had`;
- threedot (new, two-dot `git diff base head`): `its paths are what the head changes against the base (three-dot)`.

Eleven of eleven runs red. Failing test first for the blocking item: with the new fixtures added and production unchanged, the old-form mutant (`|| break` on the exhaustion `die`) turned exactly `REFUSE: no read-back can be performed`, `and no OK line` and `naming the reason` red, 3 failed of 58 (the unmutated production passed 58/0 against the same fixtures: the round-1 defect was that the mutant was expressible and unkilled, so the production change removes the shared loop exit rather than correcting a wrong output). The harness `dev/audit/harnesses/r10_seat_selftests_mutants.py body_patch-1` (per-file id, assessor ruling P6) plants the guard's mutant in the committed file and runs governance.yml's `body_patch.sh --self-test` step: `KILLED rc=1 | body_patch self-test: 62 checks, 3 failed`; its M0 baseline step is `body_patch self-test: 62 checks, 0 failed`.

## Null control

At the merge base the tool is absent (`ls tools/audit/seat/body_patch.sh` at `290712ec0` fails). Healthy-arm controls pair every refusal: the passing run PATCHes exactly once and reads back; `--dry-run` leaves the live body `the old body, 111` untouched; a moved head leaves it untouched with zero curl calls; a body the contract refuses makes zero curl calls. For the new arm: the healthy `ok` run reads back on the first attempt (2 GETs total, 1 PATCH, one `OK` line), against the `rbfail` run's 4 GETs (the pre-write read plus exactly 3 read-back attempts), 0 `OK` lines, rc 1. The whitespace fixture's twin is the healthy run, whose one-newline read-back is accepted. The moved-base fixture is a repository where the base is not an ancestor of the head (round 1's was), so two-dot and three-dot paths differ (`d.txt`): with the mutant the `paths` file holds `a.txt b.txt d.txt`, unmutated `a.txt b.txt`. For "a refused body is never sent": with `lint-fails`/`carry-fails` set the PATCH count is 0, and with each arm deleted it is 1.

## Figures

- `bash tools/audit/seat/body_patch.sh --self-test` prints `body_patch self-test: 62 checks, 0 failed` at this head (51 at `50c4a681d`; +11 assertions: existing-list 1, whitespace fixture 2, exhaustion fixture 4, four mutant arms 4). Rule: one `st` per assertion.
- `bash tools/pr/app_push.sh --self-test` prints `app_push self-test: 135 checks, 0 failed` at this head and at `origin/main` `290712ec0` (same command in a worktree there): the mint refactor changes no behaviour its checks pin.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 39 self-testing, 39 wired, 0 unwired` at this head and `38 self-testing, 38 wired, 0 unwired` at `290712ec0`: the +1 is `body_patch.sh`, wired by the governance.yml step.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 body_patch-1` prints `== M0: 0 seat step(s) red` and `RESULT survivors=0`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`; the two named, run at this head with PYTHONPATH=tests/hastub on the venv-ci python: `tests/entities.py` prints `ALL 2381 ENTITY CHECKS PASSED`, `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget touched, no raise.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`.
- Real arms, offline null control (the arms the script calls, outside the stubs): `node tools/policy/policy_lint.mjs --pr-body <"hello"> --head <sha> --title t --author hpo-author --paths-file F --existing-file F` exits 1; `python3 -I tools/audit/carry_audit.py check --body <"## Forward-carry / - a real finding with no owner">` exits 1 and prints `CARRY-AUDIT: 1 finding item(s): 0 routed, 1 unrouted`; with `## Forward-carry` = `none` it exits 0.
- Class, every minter of the author App's token: rule `grep -rn "POST.*access_tokens" tools/pr tools/audit/seat | grep -v "STUB\|printf"`; dispositions: `tools/pr/app_mint.sh` (the one author-App mint, shared in this diff); `app_approve.sh` and `app_comment.sh` mint the distinct `hpo-approver` identity and are left alone. No open seam.
- Class, every loop in `body_patch.sh` that can leave without its success condition: `grep -n 'while\|until\|break' tools/audit/seat/body_patch.sh` outside the self-test is the one read-back loop, guarded by `rbok`.
- Offline contract versus pr-contract: `carry_audit.py check --body` and `policy_lint` here run the caller's checkout, and `policy_lint`'s red-history walk reads only when `GITHUB_TOKEN` or `GH_TOKEN` is set; pr-contract runs the base's `policy_lint` on the PR tree's `carry_audit`. Stated once in the script header and `INSTRUMENTS.md`.

Alternatives and why each lost: a `--body-only` flag on `app_push.sh` (it requires a clean worktree at the branch tip and runs the whole prepr and the ref-privacy guard against a push that never happens; R10-FLOW-BODY-ONLY's scope); copying the mint into the new script (two mints drift on how a token is held and revoked); `gh api --method PATCH` as the caller (the author must be `hpo-author`, decision 0011); for the exhaustion defect, keeping the `die` and adding only a fixture (the `|| break` edit would stay a one-token mutant of a shared exit, and exhaustion should be unable to report success).

## Red checks

`nightly-status` grades `main`, not this branch: this diff touches none of its inputs, and the cheaper detector for the class it reports is the one already running nightly; named here because it stands red on main and is not caused or fixable by this change. This head has not run in CI.

## Forward-carry

- The beat's job table should list `body_patch.sh` as a hosted one-shot (arguments pr, sha, body; success = exit 0 and a last `body_patch: OK` line). Carry: R10-ORCH-MACHINERY
- The read-back equality (one trailing newline) is now stated in two scripts (`app_push.sh` `read_once` and `body_patch.sh` `verdict`); a third reader would justify one shared function. Carry: dismissed: two readers only, merging them couples the push path to a body-only tool.

## Friction

- finding-propagation: unclear: a seam note for FLOW-BODY-PATCH in STUDY K17 names the beat but not the argument shape a hosted job takes, so this seat chose positional arguments and an `OK|REFUSE` last line. Carry: R10-ORCH-MACHINERY

## Approval

`.github/workflows/` is code-owned by tvofi (`.github/CODEOWNERS`). This diff merges only on tvofi's approving review at its head, or under tvofi's mandate on #201 whose scope covers it. No bound or budget is raised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01DRcTYfN1Z4dArTmGgW5fwn
