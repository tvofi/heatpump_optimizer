R10-FLY-CARRY-DOC-CONTEXT: one carry rule, `tools/pr/app_approve.sh` `carry()`, now carries a merge verdict across the four head moves the brief names. The dispatch refusal (`review_carry.py`), the train's admission (`merge_train.py`) and the verdict poster (`app_comment.sh`, reached by `bus.sh confirm`) all ask this one rule.

- **P17, `.md` context.** In a `*.md` file, each context line in `norm()` reads as a bare ` `. A context-only rewrite main made beside the branch's lines therefore carries. The `+`/`-` lines and the hunk's context count still compare. Code files keep their context (the P325 ruling).
- **P123, the delivery row.** `bot_paths`/`bot_author` admit `record: the delivery row for #<N>` as tvofi, with its one path `dev/programme/delivery/<N>.md` bound to the `<N>` in the subject. It goes through the existing confinement and author checks. `app_push.sh` `row_only_verdict` now takes `M` as well as `A` for that row. The `bus.sh` ordering comment no longer says a late row costs a re-review. `orchestrator.md` section 11 gains "other than its own delivery row".
- **Lever L6, the patch rule** (tvofi 2026-10-30). A commit of the branch's own no longer refuses on sight. It carries where the head's tree is git's automatic merge of the reviewed head onto the main it now sits on, outside the files the comparison leaves out, and the branch's own diff still compares equal. That covers a revert and its re-apply, an empty commit, and a side merge that changes nothing. `review_carry.py` drops its own non-merge pre-filter and asks `carry()` alone, so `bus.sh dispatch` stops minting those re-reviews.
- **P264, `app_comment.sh`.** When a merge verdict's head is not the live head, `check_pr` fetches main and the PR head and runs `app_approve.sh --carry`. It posts on `CARRY: yes` with the last body line `carry: <verdict> -> <live>, app_approve.sh --carry: yes`, and prints that line. Otherwise it refuses `head moved` with the carry's reason, as before. Blocked verdicts are unchanged.
- **The driver files' end state** (round 2, the round-1 block). Every comparison in `carry()` leaves main's merge-driver files out (`.gitattributes` `merge=`: the three ledgers, `bugclasses.json` and the two claim files). What each holds at the head is now read on its own. It must be one of:
  - git's automatic merge of the reviewed head onto H's merge base with main;
  - main's own driver output on the two (`driver_wrote`, which generalises `claim_driver_wrote` to `ledgermerge`), for a clone with no drivers configured;
  - for a claim file, the union of both sides;
  - the file as the newest carried, author-checked bot commit left it, and only where the file is one of that subject's own `bot_paths`.

  So a budget, closure or claim line written by a commit of the branch's own, by a bare `ci:` subject, by a merge's hand resolution, or by a bot subject outside its own paths keeps the re-review.

The roster lists #2389 for this group (issues, not fixes), so this body closes nothing.

## Round-2 block, answered

The round-2 review (blocked at 32d880b3dee4e525d16ec270af83d867f7006431, `root-cause-unrecorded: governance / instrument-self-tests`) found the code ready. Its one block is that `## Red checks` still read the round-1 text and did not name a check that is red at this head. This round changes the body only, with no code change, so the review's measurements still describe this tree. Each item in the verdict:

- **The block.** `## Red checks` below now names `governance / instrument-self-tests`, with its cause, the process state and the detector finding. It also names the two checks that are red because of it.
- **The runner-image `unrelated-sleep` defect, shared across PRs.** The verdict dismisses it as not this PR's code. Agreed: this PR answers it by naming it under Red checks, and #3086 owns the fix.
- **Brief item 4, the forged-bot-email residual.** The verdict's dismissal holds, and the Residual below states the same boundary.
- **Round-1 O1 (carry-over-wide).** Answered at this head, by the section below and the reviewer's plants.
- **Round-1 O3 and the "or keep its patch (L6)" clause.** Still raised for the owner under `## Approval`.
- **The P123 row-binding residual.** Unchanged, and dismissed under Residual.
- **Stale figures.** The verdict read app_approve as 316 checks and merge_train as 400 on Linux at this head, where the body said 314 and 381. I re-took every self-test figure at this head on Linux under `env -u BASH_ENV` (Figures). The figures in this body are those re-takes.

## Round-1 block, answered

**carry-over-wide: a commit of the branch's own that edits main's merge-driver files carries under L6.** Taken, and widened from this instance to its whole class. The seams of that class are the sites in `carry()` that apply the driver-file exclusion `x`: `awk '/^carry\(\) \{/{on=1} on && /\$\{x\[@\]/ {print NR} on && /^}/{exit}' tools/pr/app_approve.sh`. At the head it returns five sites. Each one's disposition:

- The merge check (`git diff --quiet "$t" "$c"`): a merge's hand resolution of a ledger was never read. **Closed** by the end-state check. Twin: "NO CARRY: a merge from main whose merge-driver file is resolved by hand".
- The bare `ci:` confinement (`git diff --quiet "$c^" "$c"`): any author could rewrite a driver file under any `ci:` subject. **Closed.** Twin: "NO CARRY: a ci: subject by a seat that edits a merge-driver file".
- The bot-subject confinement (`y=(...)`): a bot subject could rewrite any driver file, not only its own. **Closed** by keying the bot exemption on `bot_paths`. Twin: "NO CARRY: the same bot subject rewriting a merge-driver file outside its own paths (#3077)". Control: "CARRY: a bot commit that rewrites only its own merge-driver file".
- The own-commit tree check (`git diff --quiet "$t" "$h"`), the block itself. **Closed.** Twins: "NO CARRY: a commit of the branch's own that edits a merge-driver file (a budget raise)", "NO CARRY: a commit of the branch's own that adds a claim line after main's driver resolved the merge", "NO CARRY: the same ledger with one value then changed by a commit of the branch's own", and "NO CARRY: a commit of the branch's own that edits the driver file a carried bot commit wrote".
- `norm()`, the branch's own diff comparison. It is left as it was: it compares the branch's patch, and a driver file main stamps would differ there at every main move. The end-state check now covers those files at the head instead.

The reviewer's replay was re-driven on this repository from a detached worktree at d843403626ee923fe1fbde4428f3a0b2eb734b06. Each move was a `fix:` commit by `t@t`, and `bash <app_approve.sh> --carry d843403626ee923fe1fbde4428f3a0b2eb734b06 <h> origin/main` ran at both ends:

| move on d84340362 | round-1 script | this head |
|---|---|---|
| one digit appended to the first value of `tests/structure_budgets.json` | `CARRY: yes` | `CARRY: no ... tests/structure_budgets.json at <h> is not ...` |
| one line appended to `tests/golden/claimed_drift.txt` (alone) | `CARRY: yes` | `CARRY: no ... tests/golden/claimed_drift.txt at <h> is not ...` |
| an empty commit (null control) | `CARRY: yes` | `CARRY: yes` |

The null row shows the check does not refuse when nothing moved, on the real merge history of this pull request's own head (1be5d4d44, a main merge). Real merged PRs beyond this one were not replayed. The round-2 review re-ran these plants and more at both verdict heads, with the same results (its verdict's Evidence).

## Carries

- Carry 1 (card 4, the merge-queue hold): moot. Carry 3 resolved it, so the group was built rather than closed.
- Carry 2 (the delivery-row commit): built. `bot_paths`/`bot_author` take the row subject bound to `dev/programme/delivery/<N>.md`, `row_only_verdict` accepts `M`, and the `orchestrator.md` s11 clause and the `bus.sh` comment are changed. Every control the carry names is in the self-test, including the path-binding mutant.
- Carry 3 (merge queue not adopted): the train-path branch was taken.
- Carry 4 (P264, `app_comment.sh` `check_pr`): built, with the pin-only carry, the code-commit refusal, the no-carry-call mutant and the unmoved null.
- Carry 5 (CM-1's hunk vs this group's): the `.md` arm is in `norm()`, the final comparison, and does not touch the merge-parent test. Its reach of 2 of 75 is the RCA's figure, not re-taken here.
- Carry 6 (Lever L6, the patch rule): built in `carry()`, with `review_carry.py` now asking it alone. The policy text is in `fix-review.md` and `standing-dispatch.md`. Controls: an absorb carries, an absorb that changes content refuses, a revert and its re-apply carries, and the tree-hash mutant fails the first arm. CI still runs at every head.

## Head

The head is `900364b18d16a8edba39397f76d42c44b14415fc`: a merge of origin/main `56630e7e6d229d960cf1b4db304d488ee20873e6` into the verdicted head `aa6148d4ff35c457e83310337760e075cb823a14` (verdict `Fix review: merge aa6148d4ff35c457e83310337760e075cb823a14`), plus one trim commit. Everything else in this body describes aa6148d4f; the reviewer reviews only this delta against that verdict. `git merge-tree --write-tree origin/main aa6148d4f` reported one conflict, `tools/audit/seat/bus.sh`.

**Resolution delta.**
1. `tools/audit/seat/bus.sh`, one hunk in the `--self-test` review-carry block, resolved as a union. Merge base 6421fe135.
   - This PR contributed: the `h2c` commit (one code line on `h2`, because `h2` alone is an empty commit and now carries under L6) and the final null control dispatching at `$h2c`.
   - Main contributed: the P348 arms (`vc`, with its merge-verdict null control, the blocked, latest-verdict, no-verdict and unreadable-ref arms C3 to C6).
   - Order in the merged file: main's arms, then this PR's `h2c` setup, then the dispatch at `$h2c`. The `h2` checkout comes after main's arms, which never move the work tree.
   - The header comment and the `dispatch` code auto-merged: this PR's ordering sentence and main's "latest verdict is merge" sentence both stand.
2. `dev/governance/roles/orchestrator.md`, commit 900364b18: the merge put the file at 17024 bytes, over its 4251-token cap (`policy_lint` `files_tokens`: 1 error; 0 at main and at aa6148d4f). Two sentences were shortened with no change of meaning: this PR's section-11 clause now reads "bar its delivery row, or keep its patch (L6); else a resolution delta for the same reviewer", and main's "a reviewed head whose verdict was merge" now reads "a merge-verdict reviewed head". This is a policy file. No cap was raised.
3. `fix-review.md` and `standing-dispatch.md` auto-merged. I read the merged text against main's changes (a dropped judge-ruling sentence, `carry_audit.py check` before a verdict, "head-moved" wording). They do not touch the sentences this PR adds, and the two texts agree.

## Hunk proof

For `bus.sh`, each parent's added lines against the merge base are all present in the merge, and the merge adds no line of its own: `B=6421fe135d9f5a9e65433a4433f000d2419486bf; for p in aa6148d4f origin/main; do git diff $B $p -- tools/audit/seat/bus.sh | grep '^+[^+]' | sort -u | comm -23 - <(git diff $B HEAD -- tools/audit/seat/bus.sh | grep '^+[^+]' | sort -u) | wc -l; done` printed 0 and 0, and the merge's lines in neither parent's added set number 0.

## Mutation proof

Failing tests first. The round-2 rows were added before each production change and run against the unfixed `carry()`:
- At d84340362: 10 failed, every twin above plus its "refused naming" row. The three new null controls were green.
- Before 25c2038d0: 2 failed, the out-of-paths bot twin and its naming row.

Round-2 mutants of `carry()` and `driver_wrote`. Each was applied in place, `bash tools/pr/app_approve.sh --self-test` was run, and the file was restored, confirmed by `git diff --quiet -- <file>`. All eight are killed:
- M1, the end-state refusal replaced by `:`: 12 failed (every twin and its naming row).
- M2, no bot commit recorded: 2 failed, "CARRY: a bot commit that rewrites only its own merge-driver file" and "CARRY: an empty commit of the branch's own after a carried bot commit's driver-file write (null control)".
- M3, `driver_wrote` dropped from the end state: 2 failed, "CARRY: the same in a clone with no claim driver configured, read by main's own driver" and "CARRY: a ledger main's driver resolved, in a clone with no ledger driver configured".
- M4, the `ledgermerge` arm of `driver_wrote` deleted: 1 failed, the ledger row of M3.
- M5, the claim-union arm dropped: 1 failed, "CARRY: a claim file resolved to the pure union of both sides".
- M6, the automatic-merge arm dropped: 24 failed, the first being "CARRY: a merge from main that leaves the branch's own diff byte-identical".
- M7, the bot exemption taking any content (`[ -n "$lb" ] && continue`): 2 failed, "NO CARRY: a commit of the branch's own that edits the driver file a carried bot commit wrote" and its naming row.
- M8, the bot exemption ignoring the path (`[ "$e" = "$p" ] || continue` replaced by `:`): 2 failed, "NO CARRY: the same bot subject rewriting a merge-driver file outside its own paths (#3077)" and its naming row.

M1 to M6 ran before 25c2038d0, which changes only the bot exemption's two lines. M2, M7 and M8 are the mutants of those lines, run at the code head. The round-2 review re-ran all eight at this head, each in its own detached worktree, and all were killed (M1 14 failed, M6 27: the rows 25c2038d0 added account for the difference from 12 and 24).

Round 1's ten mutants (Mutation proof at d84340362, the round-1 body) are of lines this round does not change. The round-1 review re-ran five of them, all killed.

## Null control

- Round 2: an empty commit of the branch's own after a merge from main carries ("CARRY: an empty commit of the branch's own after a merge from main (null control)"). So does one after a carried bot commit's driver-file write, and one after main's claim driver resolved the merge. A ledger main's driver resolved carries in a clone with no driver configured. Its twin, the same ledger with one value then changed by a commit of the branch's own, refuses. On this repository, the empty-commit row of the replay table carries at both ends.
- A verdict head with no commit after it carries trivially: "CARRY: the verdict head itself, no commit after it (null control)".
- An unmoved head posts with no carry line: "an unmoved head posts with no carry line (null control)", "and prints none".
- Each round-1 carry arm has a refusing twin one field away: a row commit plus one other file, one authored by anyone but tvofi, one naming another PR's row, and ordinary commits changing one code line, one test line or one budget value. There is also a re-apply one byte away, the `.py` twin of the `.md` context arm, a `.md` `+`-line difference, and a `.md` context-count change.
- The fixture's bot commit "ci: re-record closures" now rewrites its own `tests/closures.json` (a driver file in the fixture's `.gitattributes`) and carries. Its round-1 shape, the same subject rewriting `led.json`, now refuses. That shape is the out-of-paths twin, and its flip is the design change of 25c2038d0.

## Figures

Retaken at `900364b18d16a8edba39397f76d42c44b14415fc` on Linux under `env -u BASH_ENV`, origin/main 56630e7e6d22 (checked 2026-11-01), each from its summary line:
- `bash tools/audit/seat/bus.sh --self-test`: `bus self-test: 115 checks, 0 failed` (110 at aa6148d4f, plus main's 5 P348 arms).
- `bash tools/pr/app_approve.sh --self-test`: `app_approve self-test: 316 checks, 0 failed`.
- `bash tools/pr/app_comment.sh --self-test`: `app_comment self-test: 67 checks, 0 failed`.
- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 204 checks, 0 failed`.
- `python3 -I tools/audit/seat/review_carry.py --self-test`: `review_carry self-test: 29 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 417 checks, 0 failed` (400 at aa6148d4f; main added arms).
- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `ref_privacy self-test: 97 checks, 0 failed`.
- `bash -n tools/audit/seat/bus.sh` printed no error.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)` at this head. Before the trim commit it printed 1 error (`files_tokens` for `orchestrator.md`, 4256 against 4251). The control: the same command at origin/main printed 0.
- `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, naming `tests/doc_claims.py` and `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed ALL 296 checks PASSED.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed no red predicted.
- `tools/pr/prepr.sh <body>` at this head: printed `PRE-PR: 900364b18d16a8edba39397f76d42c44b14415fc 0000000000000000000000000000 rc=0` (origin/main 56630e7e6, unmoved since; the closures step left tests/harness_headers.py to CI). Claim files are byte-identical to origin/main (`git diff origin/main HEAD --quiet -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt`).

The figures of the original body, taken at aa6148d4f's ancestors, are unchanged by this delta except where listed above.

### Earlier figures (aa6148d4f's ancestors, kept as recorded)


Self-tests at 32d880b3dee4e525d16ec270af83d867f7006431, on Linux under `env -u BASH_ENV`, each read from its SUMMARY line:
- `bash tools/pr/app_approve.sh --self-test`: `app_approve self-test: 316 checks, 0 failed`. The earlier body said 314, read on a Mac. app_approve.sh is byte-identical between 25c2038d0 and this head and has no platform branch. I did not re-establish the Mac figure, so it is withdrawn, not explained.
- `bash tools/pr/app_comment.sh --self-test`: `app_comment self-test: 67 checks, 0 failed`.
- `bash tools/pr/app_push.sh --self-test`: `app_push self-test: 204 checks, 0 failed`.
- `python3 -I tools/audit/seat/review_carry.py --self-test`: `review_carry self-test: 29 checks, 0 failed`.
- `bash tools/audit/seat/bus.sh --self-test`: `bus self-test: 110 checks, 0 failed`. The earlier Mac run failed 14 here, all `orphans` rows from the bash 3.2 defect #3055 fixes. Linux does not have that defect.
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 400 checks, 0 failed`. The earlier 381 was read before main's `merge_train.py` changes were merged in at 32d880b3d.

These match the round-2 reviewer's Linux reading at this head.

The scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, naming `tests/doc_claims.py` and `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed ALL 296 checks PASSED. `PYTHONPATH=tests/hastub python3 tests/entities.py` printed ALL 2497 ENTITY CHECKS PASSED. This is a Linux run at this head, so the earlier Mac stop at `_hb_stdlib_reads` no longer applies.

Other gates: `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs` printed TOTAL: 0 error(s) across 50 policy file(s). `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed CI PREDICT: no closures, fast, governance or instrument red predicted against 92588d581fde (a data-file read is not seen). That is a static read, and it cannot see the runner-image red under Red checks. `tools/pr/prepr.sh <body>` at this head, with this body, on a committed tree, printed `PRE-PR: 32d880b3dee4e525d16ec270af83d867f7006431 0000000000000000000000000000 rc=0` (2026-11-01, origin/main 6421fe135).

Why `norm()` and not `git patch-id --stable` (round 1): one Python line was re-indented by 2 and by 4 extra spaces. `--stable` printed one id for both, and `--verbatim` printed two (scratch repository, git 2.43.0).

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: Architecture score: dS +0.0000 NULL. CI's `arch-score / arch-score` is green at this head. The end-state check is one loop inside `carry()`. It reuses the existing driver runner, generalised from claim files to both of main's drivers rather than copied. It keys the bot exemption on the existing `bot_paths`/`bot_author` table rather than a second list.

## Unpinned sites

The changes are in `tools/` shell and Python only, which mutation-autofix does not mutate. The in-tree self-test mutants listed under Mutation proof pin each new predicate.

## Red checks

none. The check-runs of the pull request, all 94 on one page, read at aa6148d4f, include no concluded `failure`: the earlier `governance / instrument-self-tests` red was #3086's runner-image defect and is green there (run 41308039685). The new head has no runs yet; the code-scanning alerts list is empty to my knowledge, not queried.

## Approval

Awaiting the owner's approving review. The three policy files are `dev/governance/roles/orchestrator.md` (section 11), `dev/governance/roles/fix-review.md` (step 12) and `dev/governance/roles/standing-dispatch.md` (Relay). Section 11 gains the brief's "other than its own delivery row", and also "or keep its patch (L6)". Without the second clause, the section's file clause would refuse the L6 carries that `--carry` now reports. That clause goes beyond the P123 wording, so it is raised here for the owner rather than added silently. Round 2 changes no policy file. The round-1 review's O3, that the `.md` context mask also covers instruction files (CLAUDE.md, `dev/governance/**`, `.claude/**`), is the owner's decision, flagged in its verdict and here.

## Residual

- The row binding: the row path is bound to the subject's `#<N>`, not to the pull request, because `carry()` takes no PR number. Carry: dismissed: the brief binds the row path to its subject's number, a row is no code a review measures, and the round-1 review (O2) found no use beyond a row
- The bot exemption trusts the author email `bot_author` names, and any pusher can set it. A forged commit under a bot's exact subject can therefore still write that bot's own paths, for example `tests/closures.json` under `ci: re-record closures`. Carry: dismissed: this is the trust boundary the confinement check has always used. Round 2 narrows it from every driver file to each subject's own paths. At every head, a required check that does not read the carry grades each of those paths (`budget-raise-gate`, `tests / closures`, the claim hygiene), and the round-2 review upheld this dismissal

## Forward-carry

none

## Friction

- fixer.md-preamble: cost: a group sized S in the roster carried four briefs (P17, P123, P264, L6) across eleven files, three of them policy. Round 2 added a fifth seam family. Carry: dismissed: a sizing note for the orchestrator, no later stage owns it
- fixer.md-step-5: cost: `bash tools/audit/seat/bus.sh --self-test` cannot read green on a Mac until #3055 merges (Figures). Carry: dismissed: #3055 is its fix
