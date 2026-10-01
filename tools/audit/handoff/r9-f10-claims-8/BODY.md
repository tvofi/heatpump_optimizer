<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJV4exbLBp3nfo2UJV5DJuBG6)_

🤖 Generated with [Claude Code](https://claude.com/claude-code) · https://claude.ai/code/session_01CVE4ENK8xD5ECXpZC2JsWg

Before: a branch that never edited either claim file, merged with a `main` that had just landed a claiming PR, was refused `INHERITED CLAIMS`. Its only remedy (`--drop-inherited`, or the `claims-autofix` bot) deleted the claiming PR's lines, and the branch's merge then removed them from `main`. This happened on #608 (#569's claims), on #635 (#633's), and on 2026-10-01 to #1808 and #1809 (F6.4's, #1806). Every such drop is an edit to a claim file, and that edit makes the next claiming merge conflict on GitHub, where PRs go `DIRTY` and cannot run (#570).

After: a claim file whose bytes equal its fork point's is the no-claim state that `claim-files.md` already prescribes. It is not refused, the autofix does not empty it, and its lines excuse no drift. Only lines a branch wrote may excuse drift or go stale, on both lanes: `env_drift.py`'s `judge_drift` and `card_drift.mjs` through `judgeCardClaims`. A merged-in line excusing by name was #213's hole, so the authored-only rule keeps that hole closed on both lanes. A branch that edited the file and kept the baseline's list is still refused `INHERITED CLAIMS`. That message now says an untouched file passes.

How: `claims_hygiene_verdict` takes `carried`, which lists the claim files whose bytes at `CLAIM_HEAD` (or in the working tree) equal those at the claim base. Those files skip both rules. `drop_inherited_claim_lines` returns None on identical text. `apply_inherited_claims` reads its baseline at `fork_point` (the merge base with `ref`), as the guard does. `authored_claims` / `authoredClaims` keep each scenario whose reason list differs from the fork point's (#1255's parse). The drift loop moved, unchanged, out of `main()` into `judge_drift`, and the card verdict moved into `card_rig.mjs`'s `judgeCardClaims`, so each consumer can be tested. The root-cause seat's write-up is `root-cause.md` on `handoff/r9-f10-claims-baseline-rca`. Its round 2 endorses this design on the condition that both excusal sites are ported and tested, which this PR does.

Policy: `.claude/rules/claim-files.md` (and its generated `.cursor` twin) now states the lifecycle: a line excuses only the diff that wrote it, and lines `main` carries are inert until the stamp empties them. The prose was paid for in the same paragraph, and the file is still within its cap (`node .claude/workflows/policy_lint.mjs --budgets`).

## Approval

tvofi's approving review is owed: this changes `.claude/rules/claim-files.md`.

## Head

`d7c7b55e66429d27d7f9fb41bb91a29636a9c9c9` (code head), on merge base `f67f598afcd3f72c0b36d43724cd7e0a4d30a607`. The scoped gate ran at `cfc93ab2`. The commits after it add one `tests/entities.py` check, a type annotation, and round 2's `tools/audit/prepr.sh` self-test fix. `tests/entities.py` and `bash tools/audit/prepr.sh --self-test` were re-run green at the head.

## Mutation proof

Each mutant was applied to the head tree, its closure was run, and the tree was restored (`mut.py` in the seat's scratch). Every one was killed:

- M1: `claims_hygiene_verdict` ignores `carried`. `tests/entities.py` fails "a branch that only merged a claiming main passes claims hygiene" and "CLAIM_HEAD pointing at a byte-identical file is the no-claim state (R9-F10.8)".
- M2: the `text == baseline_text` guard in `drop_inherited_claim_lines` is deleted. Fails "the autofix leaves a claim file the branch never edited byte-identical" and "an untouched claim file is not an inherited-claims rewrite".
- M3: `judge_drift` excuses with every line (`excusing = claims`). Fails "a carried claim line does not excuse a moved fixture".
- M4: `apply_inherited_claims` reads the baseline at `ref` instead of `fork_point`. Fails "the autofix judges an untouched file against the fork point, not main's tip".
- M5: `judgeCardClaims` excuses with every line. `tests/card.mjs` fails "a carried card claim line excuses no moved state", "a card claim line the branch wrote excuses its moved state" and "an edited card file that kept the baseline's list is still inherited".
- M6: `judgeCardClaims` treats nothing as untouched. Fails "a card claim file the branch never edited is not refused".

Failing tests came first. Commit `d156fac5` holds the tests plus the behaviour-preserving extraction. There, `tests/entities.py` fails 4 of the new checks, including "a carried claim line does not excuse a moved fixture", and `tests/card.mjs` fails 4. The pre-existing PR-template arm check was also red in that run; it is green at the head.

## Null control

At `f67f598a`, `tests/entities.py` passes all of its checks and `tests/card.mjs` passes. On that tree the new tests fail exactly as listed above. The touched controls stay red at the head (`prepr.sh --self-test` arm 6a's edited branch included), which shows that only the untouched shape changed: an edited file that kept `main`'s list still gets `INHERITED CLAIMS`, both from the working tree and through `CLAIM_HEAD`, and the card lane still refuses it as inherited. An authored line beside a carried one still excuses its moved fixture or state, so the port did not disable excusal. Five existing checks encoded "byte-identical is inherited" and were rewritten to the touched shape: two drop/apply fixtures, the `_ac2` card autofix positive, and the two `_merge_hygiene_git` arms. A sixth check was added for the byte-identical arm.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: all checks pass. At `d156fac5`: 5 fail (4 new plus the template arm).
- `node tests/card.mjs` at the head: all checks pass. At `d156fac5`: 4 fail.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at `cfc93ab2`: `MODE: SCOPED`, with every selected script passing, `env_drift.py --all` included ("NO UNCLAIMED DRIFT").
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/audit/prepr.sh --self-test` at the head: 129 passed, 0 failed.
- `node .claude/workflows/policy_lint.mjs`: 0 errors. `node .claude/workflows/rules_sync.mjs --check`: ok. `node .claude/workflows/brief_lint.mjs`: rc 0.
- `python3 -m mypy --strict --ignore-missing-imports tests/env_drift.py`: the line-stripped error set equals `origin/main`'s (a `diff` of the two sorted lists is empty).
- Not run, because cloud seats lack Python 3.14.2: `typing_ruler` and real-HA `ha_contract`. Neither reads the changed files' behaviour; CI or the Mac runs them.

## Red checks

- `instrument-self-tests`, at PR head `34dde3d9`: `bash tools/audit/prepr.sh --self-test` failed arm 6a. That arm built a branch that inherits main's claim list and never edits the file, and expected it to be refused; this PR makes exactly that shape pass. Round 2 (`d7c7b55e`) makes the refused arm edit a note while keeping main's list, which is still refused naming `--drop-inherited`, and adds an untouched arm that asserts it passes. A cheaper detector exists: `prepr.sh --self-test` runs locally in seconds, but this seat's pre-handoff run used `prepr.sh <body>`, which does not run the self-test. The standing cost of also running `--self-test` before handoff is seconds, so a seat that changes a gate script should run it.
- `pr-contract`: red only because this section did not name `instrument-self-tests`. It clears once that check is green.

## Forward-carry

none: no stage that has yet to start is told to drop carried claims. The R9-F10.8 roster entry on the fixplan handoff branch is updated by the orchestrator.

## Friction

claim-files: contradiction: `claim-files.md` told a branch that claims nothing to leave both files byte-identical, while `inherited_claims_error` refused exactly that shape after any claiming merge. 47 drop commits since 2026-09-17 (root-cause.md §1); fixed here.
