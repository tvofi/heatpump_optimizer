R10-FLOW-BODY-PATCH (Lean flow study K14, expedite). No tool PATCHed a pull request's body alone: `app_push.sh` mints, pushes, then PATCHes, and `update_pr.sh` merges main on every run, so a body `pr-contract` or `carry_audit` refused stayed red or cost a head move (ruling R4 forbids moving a clean head; #2560's 111 to 113 figure is the open case). This adds `tools/audit/seat/body_patch.sh [--dry-run] [--repo O/R] <pr> <expected-head-sha> <body.md>`: it refuses unless the live head is the expected sha, runs the body contract offline at that head (`policy_lint.mjs --pr-body` with pr-contract's own arguments, then `carry_audit.py check --body`), PATCHes `{"body"}` as `hpo-author`, reads the body back (identical modulo one trailing newline, `app_push.sh`'s measured rule) and re-reads the head. The mint is factored out of `app_push.sh` into `tools/pr/app_mint.sh` and sourced by both. One `--once` unit: arguments in, exit code and a last `body_patch: OK|REFUSE` line out, so R10-ORCH-MACHINERY's beat hosts it unchanged. Not run live: no pull request was patched here (the orchestrator runs it).

Code-owned files touched: `.github/workflows/governance.yml` only (`/.github/workflows/` is `@tvofi`), one added step in `instrument-self-tests`. `tools/pr/app_push.sh`, `tools/pr/app_mint.sh`, `tools/audit/seat/body_patch.sh` and `INSTRUMENTS.md` carry no code owner.

## Head

`18e7a7c61f2b07691d4d00f49d6a8658eb16d7d6` (code head on `handoff/r10-flow-body-patch`, cut from `e7c664856776542bf60bd770c98aba1eaadb4041`; `origin/main` had moved to `929275e8a3f79ad5e118a82f94ec6ecee306e7c0` at 2026-10-21T15:20Z and is not merged in).

## Mutation proof

Predicate lines of the production file are tagged `# mut:<arm>`; the self-test deletes each from a copy and its control must stop refusing. Separately, each arm was deleted from the production file itself and the whole self-test run (script: `sed '/# mut:<arm>$/s/.*/:/'` into a scratch copy beside `app_mint.sh`, readback/rbhead arms replaced by a `break`): every deletion turns checks red. head: `naming the reason`, `no curl, no contract: refused before any write or mint`; prewrite: `REFUSE: the head moves between the check and the write`, `no PATCH was sent`; contract: `policy_lint gets pr-contract's arguments`, `REFUSE: policy_lint refuses the body`, `never sent, never minted`, `its paths are what the head changes against the base`; carry: `carry_audit check --body runs on the same body`, `REFUSE: carry_audit refuses the body`; readback: `REFUSE: the body read back is not the body sent`, `and no OK line`; rbhead: `REFUSE: the head is found moved on the read-back`. Six of six arms red. Restored; `body_patch self-test` green again.

## Null control

The unmodified tree has no body-only tool (`ls tools/audit/seat/body_patch.sh` at `e7c664856` is absent), and the failing test came first: the self-test was written before the script's predicates, against the stub `gh`/`curl`/`openssl`/`node`. Healthy-arm controls pair every refusal: the passing run PATCHes exactly once and reads back, `--dry-run` leaves the live body `the old body, 111` untouched, a moved head leaves it untouched with zero curl calls (refused before the mint), and a body the contract refuses makes zero curl calls. For the quantified claim "a refused body is never sent": with `lint-fails`/`carry-fails` set the PATCH count is 0, and with each arm deleted (mutants above) it is 1. The mint refactor's control: `app_push.sh --self-test` before and after reads the same count (see Figures).

## Figures

- `bash tools/audit/seat/body_patch.sh --self-test` prints `body_patch self-test: 51 checks, 0 failed` (the new instrument; the count is its own rule: one `st` per assertion).
- `bash tools/pr/app_push.sh --self-test` prints `app_push self-test: 135 checks, 0 failed` at this head and at `e7c664856` (stashed, same command): the mint refactor changes no behaviour its 135 checks pin. Instrument: app_push.sh's own self-test.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints `selftest_wiring: 38 self-testing, 38 wired, 0 unwired` (the new file is wired by the governance.yml step; before it, 37 self-testing and 37 wired).
- Real arms, offline null control (the arms the script calls, outside the stubs): `node tools/policy/policy_lint.mjs --pr-body <"hello"> --head <sha> --title t --author hpo-author --paths-file F --existing-file F` exits 1; `python3 -I tools/audit/carry_audit.py check --body <"## Forward-carry / - a real finding with no owner">` exits 1 and prints `CARRY-AUDIT: 1 finding item(s): 0 routed, 1 unrouted`; the same with `## Forward-carry` = `none` exits 0.
- `python3 tests/closure.py select --diff e7c664856776542bf60bd770c98aba1eaadb4041 --workdir D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (tools/pr/ and tools/audit/ are INERT); the two named, `tests/entities.py` (`ALL 2375 ENTITY CHECKS PASSED`) and `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), run green with PYTHONPATH=tests/hastub on the venv-ci python.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`; no budget touched, no raise.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL` (shell and workflow only).
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py`: `uncovered_files=0` at this head and at `e7c664856`; the surface grows by one file (`body_patch.sh`, pinned, run by no PR job as every sibling seat script). Seams the class enumerates (every minter of the author App's token): `grep -rln "access_tokens" tools/ | grep -v self` is not a clean rule (app_push.sh and body_patch.sh match only on their self-test stubs), so the rule is `grep -rn "POST.*access_tokens" tools/pr tools/audit/seat | grep -v "STUB\|printf"` — dispositions: `tools/pr/app_mint.sh` (the one author-App mint, shared in this diff); `app_approve.sh` and `app_comment.sh` mint the distinct `hpo-approver` identity and are left alone. No other author-App minter exists.

Alternatives and why each lost: a `--body-only` flag on `app_push.sh` (it requires a clean worktree at the branch tip, runs the whole prepr and the ref-privacy guard against a push that never happens, and is R10-FLOW-BODY-ONLY's scope); copying the mint into the new script (the brief forbids it; two mints drift on how a token is held and revoked); `gh api --method PATCH` as the caller (the author must be `hpo-author`, decision 0011).

## Red checks

`nightly-status` grades `main`, not this branch: this diff touches none of its inputs, and the cheaper detector for the class it reports is the one already running nightly; it is named here only because it stands red on main and is not caused or fixable by this change. No other check has run: this is a handoff head with no pull request yet.

## Forward-carry

- The beat's job table should list `body_patch.sh` as a hosted one-shot (arguments pr, sha, body; success = exit 0 and a last `body_patch: OK` line). Carry: R10-ORCH-MACHINERY
- The read-back equality (one trailing newline) is now stated in two scripts (`app_push.sh` `read_once` and `body_patch.sh` `verdict`); a third reader would justify one shared function. Carry: dismissed: two readers only, merging them couples the push path to a body-only tool.

## Friction

- finding-propagation: unclear: a seam note for FLOW-BODY-PATCH in STUDY K17 names the beat but not the argument shape a hosted job takes, so this seat chose positional arguments and an `OK|REFUSE` last line. Carry: R10-ORCH-MACHINERY
