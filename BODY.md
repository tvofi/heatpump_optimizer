R10-FLY-CARRY-DOC-CONTEXT: one carry rule, `tools/pr/app_approve.sh` `carry()`, now carries a merge verdict across the four head moves the brief names. The dispatch refusal (`review_carry.py`), the train's admission (`merge_train.py`) and the verdict poster (`app_comment.sh`, reached by `bus.sh confirm`) all ask this one rule.

- **P17, `.md` context.** In a `*.md` file, each context line in `norm()` reads as a bare ` `. A context-only rewrite main made beside the branch's lines therefore carries. The `+`/`-` lines and the hunk's context count still compare. Code files keep their context (the P325 ruling).
- **P123, the delivery row.** `bot_paths`/`bot_author` admit `record: the delivery row for #<N>` as tvofi, with its one path `dev/programme/delivery/<N>.md` bound to the `<N>` in the subject. It goes through the existing confinement and author checks. `app_push.sh` `row_only_verdict` now takes `M` as well as `A` for that row. The `bus.sh` ordering comment no longer says a late row costs a re-review. `orchestrator.md` section 11 gains "other than its own delivery row".
- **Lever L6, the patch rule** (tvofi 2026-10-30). A commit of the branch's own no longer refuses on sight. It carries where the head's tree is git's automatic merge of the reviewed head onto the main it now sits on, outside the files the comparison leaves out, and the branch's own diff still compares equal. That covers a revert and its re-apply, an empty commit, and a side merge that changes nothing. `review_carry.py` drops its own non-merge pre-filter and asks `carry()` alone, so `bus.sh dispatch` stops minting those re-reviews.
- **P264, `app_comment.sh`.** When a merge verdict's head is not the live head, `check_pr` fetches main and the PR head and runs `app_approve.sh --carry`. It posts on `CARRY: yes` with the last body line `carry: <verdict> -> <live>, app_approve.sh --carry: yes`, and prints that line. Otherwise it refuses `head moved` with the carry's reason, as before. Blocked verdicts are unchanged.

The roster lists #2389 for this group (issues, not fixes), so this body closes nothing.

## Carries

- Carry 1 (card 4, the merge-queue hold): moot. Carry 3 resolved it, so the group was built rather than closed.
- Carry 2 (the delivery-row commit): built. `bot_paths`/`bot_author` take the row subject bound to `dev/programme/delivery/<N>.md`, `row_only_verdict` accepts `M`, and the `orchestrator.md` s11 clause and the `bus.sh` comment are changed. Every control the carry names is in the self-test, including the path-binding mutant.
- Carry 3 (merge queue not adopted): the train-path branch was taken.
- Carry 4 (P264, `app_comment.sh` `check_pr`): built, with the pin-only carry, the code-commit refusal, the no-carry-call mutant and the unmoved null.
- Carry 5 (CM-1's hunk vs this group's): the `.md` arm is in `norm()`, the final comparison, and does not touch the merge-parent test. Its reach of 2 of 75 is the RCA's figure, not re-taken here.
- Carry 6 (Lever L6, the patch rule): built in `carry()`, with `review_carry.py` now asking it alone. The policy text is in `fix-review.md` and `standing-dispatch.md`. Controls: absorb carries, content-changing absorb refuses, revert and re-apply carries, and the tree-hash mutant fails the first arm. CI still runs at every head.

## Head

`7d81026f1860170c69f3fc6e9734464b1efe80a3`, measured after merging origin/main `a7dd7f50d67e` (stamped 2026-10-31T18:42:55Z). Every figure below was taken at this head.

## Mutation proof

Each mutant was applied to the in-tree file, its self-test run, and the file restored (driver: a scratch `mut()` that replaces one string and runs the named self-test). All ten are killed:

- `carry()` re-merge tree check off (`if [ -n "$own" ]` → `if false`): `app_approve.sh --self-test` FAIL "NO CARRY: a commit of the branch's own that moves its change to another function with the same context (L6)", plus four "refused naming that commit".
- Row path binding dropped (any `dev/programme/delivery`): FAIL "NO CARRY: a row commit for #7 writing another pull request's row", "refused on the path its subject binds", and "CARRY: a verdict head holding its row plus a row-edit commit".
- Row author dropped from `bot_author`: FAIL "CARRY: the verdict head plus its delivery-row add", the edit arm, "the add and the edit in one range", and two naming checks.
- `.md` mask removed: FAIL "CARRY: main rewrote a context line beside the branch's lines in a .md file (P17)".
- Mask applied to every file: FAIL "NO CARRY: the same context rewrite in a .py file (code stays strict)", "NO CARRY: a merge from main that changed a context line of the branch's hunk", and two more.
- Tree hashes compared instead of the patch: 20 FAIL, the first "CARRY: a merge from main that leaves the branch's own diff byte-identical" (L6's first arm).
- `app_comment.sh` posting without the carry call: FAIL "REFUSE: a merge verdict at a head moved by a commit of the branch's own changing code", "refused 'head moved', with the carry's reason", "and nothing was minted or posted" (got 4 calls).
- `app_comment.sh` without the carry body line: FAIL "with the carry as the body's last line".
- `review_carry.py` with its non-merge pre-filter restored: FAIL "a revert and its re-apply answers CARRY (L6)", "and counts its two non-merge commits".
- `app_push.sh` without the `M` arm: FAIL "--row-only: one commit editing only its own row is pushed with prepr skipped (P123)", "... prepr skipped for the edit", "real git: commit_row's edit of a row the live head carries skips prepr (P123)".

## Null control

- A verdict head with no commit after it carries trivially: "CARRY: the verdict head itself, no commit after it (null control)".
- An unmoved head posts with no carry line: "an unmoved head posts with no carry line (null control)", "and prints none".
- Each carry arm has a refusing twin one field away: a row commit plus one other file, one authored by anyone but tvofi, one naming another PR's row, and ordinary commits changing one code line, one test line or one budget value (each refusal names its commit). There is a re-apply one byte away, the `.py` twin of the `.md` context arm, a `.md` `+`-line difference, and a `.md` context-count change.
- `--row-only`: an edit plus one more file runs prepr (stub and real git).
- Two of the old tree's assertions flip by design, under L6: "CARRY: an empty commit of the branch's own (L6)" and "CARRY: a merge of a side branch whose one commit is empty". Each has a new refusing twin ("its one commit changing a line"). Two existing fixtures whose "code" commit changed nothing were given a code line: `bus.sh`'s dispatch null control (`h2c`), and `merge_train.py`'s add refusal, whose expected reason is now `own commits <sha> change its content`.

## Figures

- app_approve self-test: 296 checks, 0 failed — `bash tools/pr/app_approve.sh --self-test` (271 at origin/main 7539d1675d7f, 2 of them flipped by L6).
- app_comment self-test: 67 checks, 0 failed — `bash tools/pr/app_comment.sh --self-test`.
- review_carry self-test: 29 checks, 0 failed — `python3 tools/audit/seat/review_carry.py --self-test`.
- app_push self-test: 204 checks, 0 failed — `bash tools/pr/app_push.sh --self-test`.
- bus self-test: 110 checks, 0 failed — `bash tools/audit/seat/bus.sh --self-test`.
- merge_train self-test: 381 checks, 0 failed — `python3 tools/audit/seat/merge_train.py --self-test`.
- Why `norm()` and not `git patch-id --stable`: on one Python line re-indented by 2 and by 4 extra spaces, `--stable` printed the same id (d476a2066751) for both, while `--verbatim` printed two (af7484f96384, 1c97eed918f5). That was a scratch repository, git 2.43.0, `git diff | git patch-id --stable` and `--verbatim`. `norm()` is the verbatim reading.
- The scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED`, RUN `tests/doc_claims.py` (ALL 255 checks PASSED) and `tests/entities.py`. run_always: `tests/harness_headers.py` (ALL 112 HARNESS HEADER CHECKS PASSED), `tests/layout.py`, `tests/closure.py selftest` (ALL 117), `tests/env_drift.py --claims-only` (ok).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs`: TOTAL 0 error(s), with the policy text cut to fit each file's cap rather than raising one. `python3 tools/pr/ci_predict.py`: no red predicted.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: Architecture score: dS +0.0000 NULL. The change stays inside the carry seam's own files. The patch rule extends `carry()` rather than adding a second predicate beside it, and `review_carry.py` loses its copy.

## Unpinned sites

`tools/` shell and Python only, which mutation-autofix does not mutate. Each new predicate is pinned by the in-tree self-test mutants listed under Mutation proof.

## Red checks

none

## Approval

Awaiting the owner's approving review. The three policy files are `dev/governance/roles/orchestrator.md` (section 11), `dev/governance/roles/fix-review.md` (step 12) and `dev/governance/roles/standing-dispatch.md` (Relay). Section 11 gains the brief's "other than its own delivery row" and also "or keep its patch (L6)": without the second clause, the section's file clause would refuse the L6 carries `--carry` now reports. That clause goes beyond the P123 wording and is raised here for the owner rather than made silently.

## Residual

- Residual of the row binding: the row path is bound to the subject's `#<N>`, not to the pull request, because `carry()` takes no PR number. A tvofi-authored row commit naming another PR's number and writing that PR's row would carry here. Carry: dismissed: the brief binds the row path to its subject's number, and a row is no code a review measures

## Forward-carry

none

## Friction

fixer.md-preamble: cost: a group sized S in the roster carried four briefs (P17, P123, P264, L6) across eleven files, three of them policy. Carry: dismissed: a sizing note for the orchestrator, no later stage owns it
