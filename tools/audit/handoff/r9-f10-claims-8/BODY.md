<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJV4exbLBp3nfo2UJV5DJuBG6)_

🤖 Generated with [Claude Code](https://claude.com/claude-code) · https://claude.ai/code/session_01CVE4ENK8xD5ECXpZC2JsWg

Before: a branch that never edited either claim file, merged with a `main` that had just landed a claiming PR, was refused `INHERITED CLAIMS`. Its only remedy (`--drop-inherited`, or the `claims-autofix` bot) deleted the claiming PR's lines, and the branch's merge then removed them from `main`. This happened on #608 (#569's claims), on #635 (#633's), and on 2026-10-01 to #1808 and #1809 (F6.4's, #1806). Every such drop is an edit to a claim file, and that edit makes the next claiming merge conflict on GitHub, where PRs go `DIRTY` and cannot run (#570).

After: a claim file whose bytes equal its fork point's is the no-claim state that `claim-files.md` already prescribes. It is not refused, the autofix does not empty it, and its lines excuse no drift. Only lines a branch wrote may excuse drift or go stale, on both lanes: `env_drift.py`'s `excusing_claims`, which `main()` applies before `judge_drift`, and `card_drift.mjs` through `judgeCardClaims`. A merged-in line excusing by name was #213's hole, so the authored-only rule keeps that hole closed on both lanes. A branch that edited the file and kept the baseline's list is still refused `INHERITED CLAIMS`. That message now says an untouched file passes.

How: `claims_hygiene_verdict` takes `carried`, which lists the claim files whose bytes at `CLAIM_HEAD` (or in the working tree) equal those at the claim base. Those files skip both rules. `drop_inherited_claim_lines` returns None on identical text. `apply_inherited_claims` reads its baseline at `fork_point` (the merge base with `ref`), as the guard does. `authored_claims` / `authoredClaims` keep each scenario whose reason list differs from the fork point's (#1255's parse). This branch was re-cut on `main` at `dc6c97e4`, after R9-F10.3 lifted the drift loop into a pure `judge_drift` (#1810). That function is kept unchanged: `main()` now passes it `excusing_claims(repo, ref, claims)`, and the staleness rule reads the same rebound map. The card verdict moved into `card_rig.mjs`'s `judgeCardClaims`, so each consumer can be tested. The root-cause seat's write-up is `root-cause.md` on `handoff/r9-f10-claims-baseline-rca`. Its round 2 endorses this design on the condition that both excusal sites are ported and tested, which this PR does.

Policy: `.claude/rules/claim-files.md` (and its generated `.cursor` twin) now states the lifecycle: a line excuses only the diff that wrote it, and lines `main` carries are inert until the stamp empties them. The prose was paid for in the same paragraph, and the file is still within its cap (`node .claude/workflows/policy_lint.mjs --budgets`).

## Approval

tvofi's approving review is owed: this changes `.claude/rules/claim-files.md`.

## Head

`f338f15f54d118bd6af9246f0b61fac8a8eac31e` (code head), on merge base `dc6c97e4` (main after #1810). It replaces round 2's `d7c7b55e`, which was cut on `f67f598a` and now conflicts with R9-F10.3's `judge_drift` in `tests/env_drift.py`. Rounds 1 and 2 are re-applied here as two commits: `dbe33db1` holds the tests and `f338f15f` the fix. Every figure below was taken at `f338f15f`.

## Mutation proof

Each mutant was applied to the head tree, its closure was run, and the tree was restored (`mut3.py` in the seat's scratch). Every one was killed:

- M1: `claims_hygiene_verdict` ignores `carried`. `tests/entities.py` fails "a branch that only merged a claiming main passes claims hygiene" and "CLAIM_HEAD pointing at a byte-identical file is the no-claim state (R9-F10.8)".
- M2: the `text == baseline_text` guard in `drop_inherited_claim_lines` is deleted. Fails "the autofix leaves a claim file the branch never edited byte-identical" and "an untouched claim file is not an inherited-claims rewrite".
- M3: `excusing_claims` returns every line. Fails "a carried claim line does not excuse a moved fixture".
- M4: `apply_inherited_claims` reads the baseline at `ref` instead of `fork_point`. Fails "the autofix judges an untouched file against the fork point, not main's tip".
- M5: `judgeCardClaims` excuses with every line. `tests/card.mjs` fails "a carried card claim line excuses no moved state", "a card claim line the branch wrote excuses its moved state" and "an edited card file that kept the baseline's list is still inherited".
- M6: `judgeCardClaims` treats nothing as untouched. Fails "a card claim file the branch never edited is not refused".
- M7: `main()`'s `claims = excusing_claims(repo, ref, claims)` line is deleted, so `judge_drift` gets the raw map. Fails "main() judges drift and staleness with excusing_claims, not the raw file".

M1 to M4 and M7 are #213's excusal hole on the solver lane, and M5 and M6 on the card lane. `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --scope changed --base dc6c97e4` reports no production code line added or modified within its scope, so there is nothing to pin: every changed line is under `tests/`, and the mutants above are its proof.

Failing tests came first. With the head's tests on `dc6c97e4`'s code, `tests/entities.py` fails 7 checks: the six named above for M1 to M4 and M7, plus "an untouched claim file is not an inherited-claims rewrite". `tests/card.mjs` fails 4 and `prepr.sh --self-test` fails arm 6a's untouched branch ("got 1:--drop-inherited, wanted 0:"). The logs are in the project's `audit-r9/fix/evidence/F10.8-v3/`.

## Null control

At `dc6c97e4`, with its own tests, `tests/entities.py` and `tests/card.mjs` pass. On that code the new tests fail exactly as listed above. The touched controls stay red at the head (`prepr.sh --self-test` arm 6a's edited branch included), which shows that only the untouched shape changed: an edited file that kept `main`'s list still gets `INHERITED CLAIMS`, both from the working tree and through `CLAIM_HEAD`, and the card lane still refuses it as inherited. An authored line beside a carried one still excuses its moved fixture or state, so the port did not disable excusal. Five existing checks encoded "byte-identical is inherited" and were rewritten to the touched shape: two drop/apply fixtures, the `_ac2` card autofix positive, and the two `_merge_hygiene_git` arms. A sixth check was added for the byte-identical arm.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: all checks pass. With the head's tests on `dc6c97e4`'s code: 7 fail.
- `node tests/card.mjs` at the head: ALL CARD CHECKS PASSED. On `dc6c97e4`'s code: 4 fail.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=dc6c97e4 ./tests/run.sh`: `MODE: SCOPED -- 7 script(s) run, 21 scoped out`, with "9 TEST SCRIPT(S) PASSED" and rc 0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/audit/prepr.sh --self-test` at the head: 129 passed, 0 failed. On `dc6c97e4`'s code: 128 passed, 1 failed (6a's untouched arm).
- `node .claude/workflows/policy_lint.mjs` and `--budgets`: rc 0, with `claim-files.md` at its cap. `node .claude/workflows/rules_sync.mjs --check`: ok. `node .claude/workflows/brief_lint.mjs`: rc 0.
- `mypy --strict tests/env_drift.py`: 221 errors at the head and 221 with `dc6c97e4`'s file, so no new error was added (most come from imported modules).
- Not run, because cloud seats lack Python 3.14.2: `typing_ruler` and real-HA `ha_contract`. Neither reads the changed files' behaviour; CI or the Mac runs them.

## Red checks

These are from #1811's round 1, at PR head `34dde3d9`:

- `instrument-self-tests`: `bash tools/audit/prepr.sh --self-test` failed arm 6a. That arm built a branch that inherits main's claim list and never edits the file, and expected it to be refused; this PR makes exactly that shape pass. The fix makes the refused arm edit a note while keeping main's list, which is still refused naming `--drop-inherited`, and adds an untouched arm that asserts it passes. A cheaper detector exists: `prepr.sh --self-test` runs locally in seconds, but this seat's round-1 pre-handoff run used `prepr.sh <body>`, which does not run the self-test. The standing cost of also running `--self-test` before handoff is seconds, so a seat that changes a gate script should run it. This head runs it green (129/0).
- `pr-contract`: red only because this section did not name `instrument-self-tests`. It clears once that check is green.

## Forward-carry

none: no stage that has yet to start is told to drop carried claims. The R9-F10.8 roster entry on the fixplan handoff branch is updated by the orchestrator.

## Friction

claim-files: contradiction: `claim-files.md` told a branch that claims nothing to leave both files byte-identical, while `inherited_claims_error` refused exactly that shape after any claiming merge. 47 drop commits since 2026-09-17 (root-cause.md §1); fixed here.
