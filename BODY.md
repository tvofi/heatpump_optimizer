R10-PROCESS-SLIM: cards C4, C5, C8 and C6 (a) of the slip study, plus the merge train's two defects (the post-merge docs step and the carry-ancestry park). Content approved by tvofi in chat 2026-11-05. C6 (a) is folded in by the main seat's ruling. Its half (b), the wake stream, is out of tree and not here.

**This round's change, by the orchestrator's ruling of 2026-11-08: C5 no longer deletes Nightly's `record-autofix` beat.** `tools/release/stamp.py` (code-owned) still depends on that beat in two places:
- its flush (rules 3-4) dispatches nightly.yml so that the beat merges a record pull request;
- its rule 5 (`--require-rows`) refuses a merged PR without the row the beat writes.

R10-FLY-STAMP-FLUSH-COST (#3296) is changing that flush now, so the beat's deletion is forward-carried to it (Forward-carry). `.github/workflows/nightly.yml` is byte-identical to origin/main again (`git diff --quiet origin/main HEAD -- .github/workflows/nightly.yml` exits 0).

Deletion over machinery throughout: 39 files changed, 578 insertions, 761 deletions (`git diff --shortstat 0a8033305d7b03494eb63453e6181a13ffa55c05...HEAD` at the head below). The diff writes 0 files under `custom_components/` (`git diff --name-only 0a8033305d7b03494eb63453e6181a13ffa55c05...HEAD -- custom_components` is empty). One cap pair is removed, for a deleted file (Raise justification). Claim files, `VERSION`, the manifest version and the notes heading are byte-identical to the merge base (prepr steps `no version edit` and `claim files`).

### What changes, per card

- **C4 (verdict carry):** when `bus.sh dispatch` is given no `--reviewed-head`, it derives one from `verdict/<pr>`'s latest `Fix review: merge <sha>` (`last_merge_verdict`).
  - The existing `review_carry.py` refusal therefore applies by default, and a second reviewer at the very head that a merge verdict names is refused.
  - The carry predicate is unchanged (`app_approve.sh --carry`).
  - `fix-review.md` step 12 states it.
- **C5 (paperwork is a note):** `fix-review.md` blocks only on code, tests and harness. `carry-missing` and `root-cause-*` become `Note:` lines, and a note on `custom_components/` is still a block. No seat writes a per-PR delivery row:
  - `bus.sh dispatch` no longer demands a row;
  - `handoff_push.sh` no longer writes one;
  - `governance / delivery-status` and `delivery-status-publish` are deleted;
  - `governance / record`'s refusal step is report-only;
  - **kept, unlike the earlier rounds:** Nightly's `record-autofix` beat, its `push:` trigger and `HOLD_MAX_AGE_S`. The beat still rows each merge from API facts. `record_row.py`'s plan covers both a rowless merge and a merged PR whose row reads `**open**`, so a PR that `handoff_push.sh` no longer rows is still rowed for rule 5.
- **C8 (review after the cheap checks):** `bus.sh dispatch` on a WAIT head refuses while any of `CHEAP_CHECKS` is still in flight. `bus.sh post` refuses a `merge` verdict at a head that `merge_train.py classify` calls RED, or whose classification it cannot read.
- **C6 (a):** `dev/governance/roles/proposal-triage.md` is deleted. Its two cap keys and its phantom `tests/closures.json` entry go with it. The triage-bar clauses main added to it since (R10-FLY-TRIAGE-BAR) now live in `orchestrator.md` section 5's proposal bullet (Merge resolution, origin/main 6457496a).
- **Train docs step: removed** from `postmerge.py`. `release_worktrees` logs `released <wt> (already collected)` for a worktree that `worktree_gc.sh` already collected.
- **Train carry ancestry: fixed** in `app_approve.sh carry()`.
- **Carry 2, superseded by main:** main's R10-HOTFIX-SELFTEST-TIMEOUT now starts the slow self-tests detached (timeout 30), so this branch's timeout-40 hunk and its `open_pr.sh`/`update_pr.sh` change are dropped in favour of main's (Merge resolution).

### This round's commits

- 0712679bfda0da7f7445ee191da94bcc049a4eee: merges origin/main 0a8033305d7b03494eb63453e6181a13ffa55c05 into f5af5b513b1978d732fd41902c203890e3a0247b, the PR head holding the merge verdict. `git merge-tree --write-tree origin/main f5af5b51` exits 1 with `CONFLICT (content)` in `.claude/rules/defect-root-cause.md`, `.cursor/rules/defect-root-cause.mdc`, `dev/governance/roles/fix-review.md` and `dev/governance/rules/defect-root-cause.md`, so the merge was owed (`fixer.md` step 6).
- 0aa9d4f2fba26e5ec93c42bec570f5faddbaa19b: the cap payment for the union (Merge resolution, origin/main 0a803330).
- c09a9acb7a7d5806c5db8881404ebd808a23daf0: merges origin/main 806e952ca, which moved during prepr and then conflicted (Merge resolution, origin/main 806e952c).
- After both, `git merge-tree --write-tree origin/main HEAD` exits 0 and prints no `CONFLICT` (the null control).

### Merge resolution (origin/main 806e952c)

- **`.github/workflows/governance.yml`, the `handoff_push.sh` self-test step (hand-written):** main's #3337-range scope gating (`id: handoff-push`, `if: ${{ !cancelled() && steps.scope.outputs.handoff-push == 'true' }}`) is kept; this branch's step name "Show the handoff push refusing its own fixtures" is kept, and main's `delivery_row self-test` grep stays out, as this branch already removed it (84be4038d: `handoff_push.sh` no longer runs the row writer, card C5).
- `python3 -I tools/ci/selftest_scope.py --self-test`: `90 checks, 0 failed` (incl. "the live job parses (114 steps) and its gating is consistent"); every `steps.scope.outputs.<id>` the merged file uses is a key of `tools/ci/selftest_closures.json` and the reverse (106 each, both differences empty). `bash tools/audit/seat/handoff_push.sh --self-test`: `6 checks, 0 failed`. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `git merge-tree --write-tree origin/main HEAD`: exit 0 at origin/main 806e952ca.

### Merge resolution (origin/main 0a803330): main merged, conflicts resolved by union

Re-check only these hunks; every other file auto-merged. The conflict is with #3305 (R10-HOTFIX-NONREQUIRED-REDS, merge 5e1ffb34), which replaced the base's `nightly-status`/`delivery-status` exemption paragraph with the required-reds ruling, where this branch had dropped `delivery-status` from the same paragraph (card C5 deletes that grader).
- **`dev/governance/rules/defect-root-cause.md`, Enforcement, the paragraph after "The reviewer reads the PR's checks" (hand-written):**
  - From main, kept: "Only a red on a required check is owed an answer (tvofi, 2026-11-07)"; the set `merge_train.py owed-reds` prints, read by `policy_lint.mjs --pr-body`; "A red outside it, an alert apart, blocks nothing"; `nightly-status` grades `main` and its red is the orchestrator's there; "fix the nightly lane and dispatch Nightly (`web-fragments.md`)"; "An unreadable set keeps the pre-ruling rule"; "A cause outside this repository is named with its owner."
  - From this branch, kept: the `nightly-status` exemption "unless the diff touches what it reads", now stated as the content of the pre-ruling rule an unreadable set keeps. That is what `policy_lint.mjs` does: `requiredFromTrain`'s unreadable arm leaves every red owed, `MAIN_STATE_REPORTERS`' exemption included, voided by `reporterInputsTouched`. The list of inputs is named by `REPORTER_INPUTS` instead of spelled out (the cap payment).
  - Not kept, from main: "`delivery-status`" in "`nightly-status` and `delivery-status` grade `main`", and "or drain the overdue rows". This is this branch's own delta to the same base sentence: card C5 deletes the `governance / delivery-status` job (`git grep -c delivery-status HEAD -- .github/workflows/governance.yml` finds it only in two comments, no job), so a rule naming it as a live grader would be false (`fixer.md` step 9).
- **`dev/governance/roles/fix-review.md` step 11, the nightly-status sentence (hand-written):** "**A red `nightly-status` is not this pull request's**: it is not required." Main's "neither is required" is kept for `nightly-status`; `delivery-status` is dropped as above. This branch's "unless its diff reaches what it reads" is carried by `defect-root-cause.md`'s Enforcement, which the same step already cites (main's "(`defect-root-cause.md`'s Enforcement)", auto-merged two lines above), so the sentence's own citation is dropped to pay the cap.
- **`.claude/rules/defect-root-cause.md` and `.cursor/rules/defect-root-cause.mdc`:** not hand-edited; regenerated by `node tools/policy/rules_sync.mjs`, and `--check` prints `RULES-SYNC ok`.
- **The cap payment (0aa9d4f2fba26e5ec93c42bec570f5faddbaa19b).** The first union put `.claude/rules/defect-root-cause.md` at 156 lines / about 1930 tokens (caps 153 / 1887) and `fix-review.md` at about 2479 tokens (cap 2451); `node tools/policy/policy_lint.mjs` printed 3 errors. Paid inside the two hunks above, no budget change. `node tools/policy/policy_lint.mjs --budgets` now prints 153/153 lines, 1880/1887 tokens and 133/140 lines, 2449/2451 tokens; `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 49 policy file(s)`. At origin/main 0a803330 the same command prints `TOTAL: 0 error(s) across 50 policy file(s)` (the 50th is the deleted `proposal-triage.md`).
- **The PR's budget raise survives:** `grep -c proposal-triage dev/governance/config/policy_budgets.json` prints 0 at this head and 2 at origin/main.
- **Step ref:** `handoff-wip/r10-process-slim` was fast-forwarded by a step commit whose parents are the stale 6b1472f52 and this seat's head (tree equal to the head), so no delete was needed (Friction r10-process-slim-5).

### Previous round's commit (origin/main 6457496a)

- b5ddb2a577cfffcc1569103ed4d1aa1b6021a2e2: merges origin/main 6457496aba7b1076b1ed60c374c5badafdf66fc1 into 491177c4b361a6a75a18e1e9e1d0f1533d630dc6. `git merge-tree --write-tree origin/main 491177c4` exits 1, so the merge was owed (`fixer.md` step 6). After it, `git merge-tree --write-tree origin/main HEAD` exits 0.

### Merge resolution (origin/main 6457496a)

- **One conflict, `dev/governance/roles/proposal-triage.md` (modify/delete).** This branch deletes it (card C6 (a)). Main modified it in c7f4535dc, eda3592e3 and 546513323 (the triage bar). The deletion stays. Every clause those commits added is carried, word for word except the two marked, into `orchestrator.md` section 5's "A proposal is ruled directly" bullet, the place this branch folded the triage gate into:
  - "A countermeasure policy requires (root cause, red-check carry, finding fix; see Machinery) keeps its route." Main reads "see below"; the pointer names the paragraph it points to.
  - "An exemption ACCEPT (over 20% on a `ratchet-budgets.md` measure) says so; its PR records it." The 20% threshold in `ratchet-budgets.md` itself (and its generated `.claude`/`.cursor` copies), `machinery_ratchet.py` and its instrument page auto-merged and are byte-identical to origin/main (`git diff --quiet origin/main HEAD -- <those five files>` exits 0).
  - "**Machinery:** a planned instrument/machinery group, or existing non-production CI lane or seat, stays only on a measured gain of at least 10% on them." Main reads "**Machinery.** A planned".
  - "Repair of such code (outside `custom_components/`) with roster `severity` `low` or `normal` meets both (over 20% to add);"
  - "`medium`, `high`, `major`, `critical`, root-cause countermeasure, closeout, owner directive skip them;"
  - "unset is classified first, never assumed major."
  - Main's remaining text in that file restates the base's obligations (the Bar's cost list, verdicts, ruling format, the "you never" line) that card C6 (a) already retired with the seat; it is not re-added.
- **`orchestrator.md` and `INSTRUMENTS.md` do not conflict at this base.** `git diff --quiet fdc8d21a origin/main -- dev/governance/roles/orchestrator.md tools/audit/seat/INSTRUMENTS.md` exits 0: main has not touched either since 491177c4's merge base, so the merge takes this branch's side unchanged and no union is owed. The brief's two content conflicts were measured against `origin/fix/r10-process-slim` (565f9f2b), whose resolution 97c49a85 already holds (previous Head note below).
- **The fold's cap payment.** The fold took `orchestrator.md` to 301 lines and about 4386 tokens, over its caps of 295 and 4251 (`node tools/policy/policy_lint.mjs`: 2 errors). Paid inside the file, no budget change, by deleting motivation-only text (`fixer.md` step 9): the "(empty means identical)" anecdote in section 1 (the rule stays, citing `fixer.md` step 3); section 2's duty list, which the contract's opening already states; the relative-scratch anecdote in section 5; section 6's word-level-diff anecdote; section 3's "three symptoms recorded separately are worth less than one analysis" clause; "restated three times" in the critical-path bullet; and a shorter wording of section 4's GitHub-tool-surface clause, same fact. Result: 294/295 lines, 4248/4251 tokens, `0 error(s) across 49 policy file(s)`.
- **Not in this head:** `refs/heads/handoff-wip/r10-process-slim` holds 6b1472f52, a previous seat's step ref left undeleted, whose tree equals 491177c4's (`git log -1 --format=%T` prints 3c428084 for both). This head does not descend from it, so it could not be fast-forwarded; replacing it was refused by this container's permission guard, so this seat pushed no step ref and left that ref untouched (Friction r10-process-slim-5).

### Earlier round's commits

- 5fa6b6a9c: merges origin/main 17e1157925908bd69addb58ed824c1ac22bfa82f. `git merge-tree --write-tree origin/main b2381acd` reported a conflict (rc 1), so the merge was owed under the 2026-11-07 ruling.
- d70186a59: restores main's pins on the beat, unchanged, failing first:
  - `tests/entities.py`: the record-autofix wiring, the train hold, the batch gate, the rate-limit and the push-trigger checks;
  - `merge_train.py`: the batch self-test's guard read;
  - `orchestrator_tick.py`: the MAIN D-1 push-run pin.
- a210a9cec: `nightly.yml` restored to origin/main.
- 2600a6b28: the record text corrected. `delivery-status-tracking.md` item 1, CLAUDE.md's index row, `orchestrator.md` section 9 and `dev/README.md` said that no row is written and that merged rows gate nothing. Both claims are false while the beat runs. They now say that no seat writes a row and that the beat does, which the stamp reads.
- e6a4a7dd3: a test-only repair of a semantic merge interaction in `merge_train.py`'s unwind self-test (Merge resolution).

### Previous merge resolution (origin/main 17e11579)

- **`.github/workflows/governance.yml` (three hunks).** Main's R10-HOTFIX-SELFTEST-TIMEOUT runs `open_pr.sh`, `pr_args.sh` and `update_pr.sh`'s self-tests detached, and its read steps grep `pr_args self-test` in the output of `open_pr.sh` and `update_pr.sh`.
  - Kept: main's timeout comment and `timeout-minutes: 30`, and main's removal of the in-line open-pr and update-pr steps.
  - Because main's steps read the `pr_args` tally, `open_pr.sh`, `update_pr.sh` and the harness's S12/S27 wrapper mutants take main's text. This branch's carry 2 is superseded.
- **`dev/governance/roles/fix-review.md` (one hunk):** union, with main's "Evidence names differ beyond case." inside the branch's paragraph.
  - The union was 9 tokens over the file's `files_tokens` cap.
  - Paid by dropping two attribution dates from the branch's own added lines (C4's and C5's).
  - `node tools/policy/policy_lint.mjs`: `0 error(s) across 49 policy file(s)`.
- **The semantic interaction, repaired in a test only (e6a4a7dd3).**
  - The interaction: main's new batch-seam arm, "a first TERM in batch 1's closing release stops the train", waits for a stubbed `git worktree remove`. This branch's `release_worktrees` skips a worktree that git does not list and that does not exist. The driver's stub listed none, so `/x` was skipped and the arm failed.
  - The repair: the stub now lists `/x`, as in life. Production is unchanged.

## Head

25bc7471a0386ad028b02db9feb0b6c89f80210d (`handoff/r10-process-slim-p2`).

**Head note (25bc7471): main merged, one conflict resolved by union** (`fixer.md` step 6; no re-cut, a resolution delta for the same reviewer). 25bc7471a0386ad028b02db9feb0b6c89f80210d merges origin/main 7bdc8aa2ec92934b96b77d3fd8d331b1c23d3769 into e24d9e408c6c2f6053faa66a14e305a29f747c37. Before it, `git merge-tree --write-tree origin/main e24d9e40` exits 1 with `CONFLICT (content)` in `dev/governance/roles/fix-review.md`; after it, `git merge-tree --write-tree origin/main HEAD` exits 0 (the null control; origin/main 7bdc8aa2, 2026-11-09T15:28:00Z). `git merge-base origin/main HEAD` is now 7bdc8aa2ec92934b96b77d3fd8d331b1c23d3769; `git diff --shortstat 7bdc8aa2...HEAD`: `39 files changed, 578 insertions(+), 761 deletions(-)`. Every other file auto-merged, `tests/closures.json` through the `ledgermerge` driver.
- **The one hand-resolved hunk, `dev/governance/roles/fix-review.md` step 10, the carry-missing sentence.** The conflict is with #3330 (R10-FLY-NO-SELF-CARRY, merge 6d660061d), which appended an own-group verdict after the same base line that this branch had turned into a `Note:` line (card C5).
  - Kept from this branch: "One only in this PR's comments is `Note: carry-missing: not carried to <stage>`."
  - Kept from main, word for word: "An own-group `Carry:` naming neither `fixer.md` exception is `blocked <sha> carry-missing: own-group`."
  - Decision for the reviewer: main's own-group arm stays a block, not a `Note:`. It is main's newer rule (`fixer.md`: "A finding in your own group's seam is built in this PR, not carried" means code left unbuilt, not paperwork), and demoting it would loosen a rule this branch never saw. Re-check this hunk.
  - Read-back against both parents: `git diff HEAD^1 HEAD -- dev/governance/roles/fix-review.md` shows only main's #3330 lines and main's other auto-merged edits; `git diff origin/main HEAD -- dev/governance/roles/fix-review.md` shows only this branch's own delta (C5's `Note:` paragraph, step 11's `Note:` wording, step 12's carry wording) and the `Note:` line above.
  - Caps: `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 49 policy file(s)`; `--budgets` prints `tools/audit/briefs/fix-review.md 133 140 2451 2451`, at its token cap, not over. `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- **Re-run at 25bc7471 (fixer.md steps 2-8).** `python3 tests/closure.py select --diff 7bdc8aa2` prints `MODE: FULL` (reason: `.github/workflows/tests.yml changes the gate itself`), so the suite is CI's (step 5). The `run_always` lines, with `PYTHONPATH=tests/hastub`: `tests/env_drift.py --claims-only 7bdc8aa2` (`claims hygiene: ... ok`), `tests/closure.py selftest` (`ALL 118 closure shrink pins PASSED`), `tests/layout.py` (`layout self-test: ok`), `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`). `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. The merge moves no mutation anchor: the one hand-written hunk is policy prose, so no pin is re-taken.
- **Carry marker.** The Forward-carry marker for item ada60feb stays `Carry: R10-CLOSEOUT-INSTRUMENTS`. The previous seat's BLOCKED note says it re-routed it to R10-HOTFIX-RECORD-ATTRIB, but that edit never reached BODY.md (`git diff c4a2af87b 4b068b494 -- BODY.md` is empty). At `handoff/audit-r10-roster` c53b399c3, R10-HOTFIX-RECORD-ATTRIB is `resume.stage: done` and R10-CLOSEOUT-INSTRUMENTS is `carries-open`. `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body BODY.md --branch handoff/r10-process-slim-p2` prints `6 routed, 0 unrouted, 0 bad destination(s)`. With the marker set to R10-HOTFIX-RECORD-ATTRIB, the same command prints `BAD-DEST ... is done` (the null control).
- `python3 tools/audit/seat/ref_privacy.py guard --ref refs/heads/handoff/r10-process-slim-p2 --commits HEAD --over origin/main -C .` exits 0.

**Previous head note (e24d9e40):** e24d9e408c6c2f6053faa66a14e305a29f747c37.

**Head note: supersedes PR #3245, same patch, history re-authored.** This head carries the patch of #3245 (handoff/r10-process-slim at c09a9acb7a7d5806c5db8881404ebd808a23daf0) unchanged. Its history is re-authored from the legacy unnumbered seat identity: in the 59 commits of origin/main..c09a9acb, 21 were authored and committed `seat@users.noreply.github.com`, which body_push's push guard refuses (`unnumbered-email`). Only those author and committer emails were rewritten, to `70032254+tvofi@users.noreply.github.com` (`git filter-branch --env-filter ... -- origin/main..HEAD` at main f365ce75); names, dates, messages and merge structure are unchanged, and every tree is identical. Proof:
- (a) old and new ranges both hold 59 commits; paired by `git rev-list --reverse --topo-order`, each pair's `^{tree}` is identical, as are author and committer names and dates, the message, and the parents (mapped through the rewrite).
- (b) `git log --format='%ae%n%ce' origin/main..HEAD | grep -c seat@` prints 0.
- (c) `python3 tools/audit/seat/ref_privacy.py guard --ref refs/heads/handoff/r10-process-slim-p2 --commits HEAD --over origin/main -C .` exits 0.
- (d) the final tree is 8e0ef08cc212bdefe8c05fecbb98d6cfbbaae026 at both e24d9e40 and c09a9acb.

The commit names in the notes below are the pre-rewrite SHAs of #3245's history.

**Previous head note (c09a9acb): main merged, conflicts resolved by union** (`fixer.md` step 6; no re-cut, for the same reviewer). This handoff changes no code from c09a9acb: only the Forward-carry marker for item ada60feb moves to R10-CLOSEOUT-INSTRUMENTS (orchestrator re-route; R10-FLY-STAMP-FLUSH-COST is done and the stamp still reads the rows: `git grep -c -- '--require-rows' origin/main -- tools/release/stamp.py` prints 8 at main f365ce75). c09a9acb7a7d5806c5db8881404ebd808a23daf0 merges origin/main 806e952ca into 0aa9d4f2fba26e5ec93c42bec570f5faddbaa19b (one conflict, `governance.yml`: Merge resolution, origin/main 806e952c). 0712679bfda0da7f7445ee191da94bcc049a4eee merges origin/main 0a8033305d7b03494eb63453e6181a13ffa55c05 into f5af5b513b1978d732fd41902c203890e3a0247b, the PR head holding the merge verdict, with two hand-written hunks; 0aa9d4f2fba26e5ec93c42bec570f5faddbaa19b pays their caps (Merge resolution, origin/main 0a803330). f5af5b51 and b5ddb2a5 are ancestors of this head. The previous head notes follow unchanged.

**Previous head note (b5ddb2a5):** b5ddb2a577cfffcc1569103ed4d1aa1b6021a2e2 merges origin/main 6457496aba7b1076b1ed60c374c5badafdf66fc1 into 491177c4b361a6a75a18e1e9e1d0f1533d630dc6, with one hand resolution (Merge resolution, origin/main 6457496a).

**Previous head note (491177c4):**
- 491177c4b361a6a75a18e1e9e1d0f1533d630dc6 merges origin/main fdc8d21adaa50a7feee534f08ee5edde9bda81ed into f30fb9a9f0c7e54587844adda6a2d75a37da3280 (no conflict), which merged origin/main 425b858495432c8dceb89d8d13866550352ba54f into 53ceaf58b04d110386afbb334e08bb471037a168 (no conflict), which merged origin/main daf8b349fd30cc60786eeca333a426b693aa4c5f (no conflict) into 97c49a85813a4971a5ba6bc537ef4481f51e15fd, the previous resolution head, which merged origin/main bb7dfb9b into the PR head 565f9f2b8a5efd9de1d260c241ee657aedc52576. The PR head is an ancestor of this head.
- The conflict, confirmed first: `git merge-tree --write-tree origin/main 565f9f2b` exits 1 with `CONFLICT (content)` in `dev/governance/roles/orchestrator.md` and `tools/audit/seat/INSTRUMENTS.md`; `git merge-tree --write-tree origin/main 97c49a85` exits 0, so none of this seat's three merges needed a hand edit (main moved to 425b8584, then fdc8d21a, while prepr ran, so it was merged again each time and prepr re-run). The resolution is 97c49a85's union, re-verified in this seat:
  - `orchestrator.md`: main's section-5 bullet "Each outside submission reaches a disposition" (tvofi 2026-11-06) is kept, followed by this branch's "A proposal is ruled directly" bullet, which replaces main's unchanged proposal-triage bullet (card C6 deletes `proposal-triage.md`). Main's two trims (the 2026-09-07 sentences in the preamble, the Round-10 sentences under "Look the instrument up") are kept; this branch's section-9 and L6 rewordings are kept.
  - `INSTRUMENTS.md`: main's `plan_public.py`, `outside_intake.py` and `hooks_setup.py` lines are kept, with this branch's `postmerge.py` wording.
- `git merge-base origin/main HEAD` is fdc8d21adaa50a7feee534f08ee5edde9bda81ed, the base of every three-dot figure here. `git diff --shortstat fdc8d21adaa50a7feee534f08ee5edde9bda81ed...HEAD`: `39 files changed, 557 insertions(+), 743 deletions(-)`, the same as at 97c49a85 against bb7dfb9b.
- Not in this head: the earlier step ref's 747e9065b, which moved `HOLD_MAX_AGE_S` into merge_train.py. With the beat kept, the constant stays in nightly.yml, as on main.

## Mutation proof

Each changed line was mutated by hand. A mutant was graded by the self-test or check named, and the file was restored after.
- **The beat (a210a9cec), whose deletion is the mutant.** At d70186a59, with the restored pins and without the beat:
  - `python3 -I tools/release/stamp.py --self-test` prints `FAIL hold: the bound is nightly.yml's own HOLD_MAX_AGE_S by source read` and `RESULT stamp_self_test=fail`;
  - `python3 tools/audit/seat/orchestrator_tick.py --self-test` prints `283 checks, 2 failed` (`FAIL MAIN D-1: nightly.yml's push-run jobs are exactly the record beat`, and its red-named pair);
  - `python3 tools/audit/seat/merge_train.py --self-test` prints `FAIL record_row.py takes every option the bot sweep passes, and the record beat merges behind the same --automerge-check ... --head ... --require-green guard`;
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` stops with `ValueError: substring not found` at `_RAF_JOB_RAW = _workflow_job(_NIGHTLY_YML, "record-autofix")`.
  - At a210a9cec and at this head, the first three print `RESULT stamp_self_test=pass`, `283 checks, 0 failed` and `475 checks, 0 failed`. entities.py runs to its end, and its only reds are this container's two (Null control).
- **The fixture repair (e6a4a7dd3).** Without the two stub lines, `merge_train.py --self-test` prints `475 checks, 1 failed` (`FAIL a first TERM in batch 1's closing release stops the train`), three runs of three. With them it prints `0 failed`, three runs of three. The arm's own mutants (the old `SIG_IGN`, and a defer that never re-raises) still print `ok`, so the arm still separates them.
- **The policy text (2600a6b28)** has no executable line. `node tools/policy/rules_sync.mjs --check` exits 0, and `node tools/policy/policy_lint.mjs` prints `0 error(s)`.
- **The cards' own mutants are the earlier rounds'**, in `dev/audit/harnesses/r10_seat_selftests_mutants.py`. Their planted files are not changed by this round except the S12/S27 wrappers, which are back to main's text. MUTANT_CMD was left unset (prepr's diff-mutant step is report-only).

## Null control

- **origin/main 17e11579, the same container:**
  - `stamp.py --self-test` prints `pass`;
  - `merge_train.py --self-test` prints `472 checks, 0 failed`;
  - `entities.py` prints `2 of 2656 ENTITY CHECKS FAILED`. The two are "the coverage job reuses only an entry main's push run saved" and "the release ZIP holds the integration folder at its root". This head prints the same two, as `2 of 2648`; the 8 fewer checks are C5's delivery-status pins.
- **The container's, not the branch's:**
  - `bus.sh --self-test` prints `FAIL an ordinary append with no intervening fetch is the same commit object as before`, and `ref_privacy.py --self-test` prints `113 checks, 1 failed` (the machine-email author arm). Both fail identically at origin/main here, with or without the seat's `GIT_AUTHOR_*` variables, so they are left to CI.
  - `ci_predict.py --self-test` printed `1 failed` until `/opt/hpo/runner-temp`, the `RUNNER_TEMP` that this container's `BASH_ENV` sets, existed. It then printed `0 failed`.
- **The merge commit 5fa6b6a9c, before the restoration:** `stamp.py --self-test` prints `RESULT stamp_self_test=fail`, the red the previous seat measured on CI (`tests / fast (3.14)`, `governance / instrument-self-tests`).

## Figures

**This round, re-taken at 0aa9d4f2fba26e5ec93c42bec570f5faddbaa19b, origin/main 0a8033305d7b03494eb63453e6181a13ffa55c05 (the merge base):**
- `git merge-tree --write-tree origin/main f5af5b513b1978d732fd41902c203890e3a0247b`: exit 1, four `CONFLICT (content)` lines (the control). `git merge-tree --write-tree origin/main HEAD`: exit 0, no `CONFLICT` line.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok: every generated rule is the generated form of its source`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 49 policy file(s)`; control, the unpaid union at 0712679bfda0da7f7445ee191da94bcc049a4eee: `TOTAL: 3 error(s)` (the three caps under Merge resolution).
- `node tools/policy/policy_lint.mjs --budgets`: `.claude/rules/defect-root-cause.md` 153/153 lines, 1880/1887 tokens; `tools/audit/briefs/fix-review.md` (the key for `dev/governance/roles/fix-review.md`) 133/140 lines, 2449/2451 tokens.
- `node tools/policy/brief_lint.mjs`: exit 0.
- `python3 tools/policy/role_pack.py --self-test`: `35 passed, 0 failed`.
- `python3 tools/audit/seat/review_packet.py --self-test`: `72 checks, 0 failed`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `292 checks, 0 failed`.
- `python3 tools/audit/archscore/score.py --diff 0a8033305d7b03494eb63453e6181a13ffa55c05 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `git diff --shortstat 0a8033305d7b03494eb63453e6181a13ffa55c05...HEAD`: `39 files changed, 578 insertions(+), 761 deletions(-)`. `git diff --quiet origin/main HEAD -- .github/workflows/nightly.yml` exits 0.
- `python3 tests/closure.py select --diff 0a8033305d7b03494eb63453e6181a13ffa55c05`: `MODE: FULL` (`.github/workflows/tests.yml changes the gate itself`), so CI runs the suite.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2662 ENTITY CHECKS PASSED`, exit 0.
- `python3 tools/audit/seat/merge_train.py --self-test`: `570 checks, 0 failed`.
- `python3 tools/pr/ci_predict.py --self-test`: `0 failed`.
- `bash tools/audit/seat/body_push.sh --self-test`: `39 checks, 0 failed`.


**Previous round, at b5ddb2a577cfffcc1569103ed4d1aa1b6021a2e2, origin/main 6457496aba7b1076b1ed60c374c5badafdf66fc1 (read 2026-11-09T01:27:29Z), not re-taken except where this round lists them above:**
- `python3 -I tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `292 checks, 0 failed` (main's count grew from 283).
- `python3 tools/audit/seat/merge_train.py --self-test`: `567 checks, 0 failed`.
- `bash tools/audit/seat/handoff_push.sh --self-test`: `6 checks, 0 failed`.
- `bash tools/audit/seat/body_push.sh --self-test`: `35 checks, 0 failed`.
- `python3 tools/audit/seat/postmerge.py --self-test`: `18 checks, 0 failed`.
- `python3 tools/audit/seat/roster_edit.py --self-test`: `257 checks, 0 failed`.
- `python3 tools/audit/machinery_ratchet.py --self-test`: `54 checks, 0 failed` (main's 20% threshold, auto-merged).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs --budgets`: exit 0, `dev/governance/roles/orchestrator.md` (budget key `tools/audit/briefs/orchestrator.md`) at 294/295 lines, 4248/4251 tokens. `node tools/policy/policy_lint.mjs`: `0 error(s) across 49 policy file(s)`. Control: the unpaid fold printed `2 error(s)` (301 > 295 lines, 4386 > 4251 tokens).
- `python3 tools/audit/seat/selftest_wiring.py --check`: `124 self-testing, 124 wired, 0 unwired`, `0 index gap(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `node tools/policy/brief_lint.mjs`: exit 0.
- `python3 tools/audit/archscore/score.py --diff 6457496aba7b1076b1ed60c374c5badafdf66fc1 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff 6457496aba7b1076b1ed60c374c5badafdf66fc1`: `MODE: FULL` (`.github/workflows/tests.yml changes the gate itself`), so CI runs the suite.
- `git merge-tree --write-tree origin/main HEAD`: exit 0.
- **Triage-bar clause check (the null-controlled check for this merge).** Rule: `clause_check.py <file> <clauses>` collapses whitespace in `<file>` and prints `MISSING n` and exits 1 unless every line of `<clauses>` (the seven clause fragments quoted under Merge resolution, one per line: the countermeasure-route sentence split at "see", "keeps its route.", and the five others) is a substring. The script is three lines of Python: `t=re.sub(r"\s+"," ",open(f).read()); miss=[c for c in clauses if re.sub(r"\s+"," ",c) not in t]; sys.exit(1 if miss else 0)`; a one-off probe kept in scratch (`fixer.md` step 18).
  - merged `dev/governance/roles/orchestrator.md`: `ALL-PRESENT`, rc 0;
  - main's `proposal-triage.md` (`git show origin/main:...`), the source: `ALL-PRESENT`, rc 0, so every fragment is main's text;
  - null control 1, 491177c4's `orchestrator.md`: `MISSING 7`, rc 1;
  - null control 2, the merged file with "unset is classified" perturbed to "unset is assumed": `MISSING 1: ['unset is classified first, never assumed major.']`, rc 1. A tree dropping any one clause fails it.
- **The merge carries the branch's delta unchanged except the resolution.** Rule: `git diff --name-only origin/main HEAD` equals `git diff --name-only fdc8d21a 491177c4` (39 files each, `diff` exits 0), and per file the `+`/`-` lines of `origin/main..HEAD` are compared by sha1 with those of `fdc8d21a..491177c4`: `same` for 37 of 39; `DELTA DIFFERS` for exactly `orchestrator.md` (the fold and its payment) and `proposal-triage.md` (the deleted text is now main's version).
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>`: clean at this head, `PRE-PR: b5ddb2a577cfffcc1569103ed4d1aa1b6021a2e2 000000000000000000000000000000000 rc=0` (gate mode `MODE: FULL`; `closures` skipped, closures-autofix is the only check left). origin/main read again at 2026-11-09T02:07:09Z: 6457496aba7b; unmoved since that run, so no second run is owed.

## Red checks

At 25bc7471a0386ad028b02db9feb0b6c89f80210d no check has run: no pull request is open for it, and a handoff ref runs no workflow. Owed answers are only for reds in the set `python3 tools/audit/seat/merge_train.py owed-reds --repo tvofi/heatpump_optimizer` prints (owner ruling 2026-11-09).

The superseded PR #3245's head is f5af5b513b1978d732fd41902c203890e3a0247b, an ancestor of this head. Its check-runs (`pull_request_read get_check_runs`, read 2026-11-09: 66 runs, one page):
- `budget-raise-gate / budget-raise-gate` (128968794644, run 42555968032; 128970652152, run 42555968038) failed with `REFUSED: tvofi's approval is on 565f9f2b8a5e, not this head f5af5b513b19: an approval covers only the commit it was given on`; 129024905382 in run 42556058045 passed at 07:09Z. Root-cause trigger: no cheaper detector exists — the refusal is the gate's designed answer to a moved head (`budget-raise-gate`, decision 0013), not a defect of this diff. **This head is predicted the same red** until the raise is approved at it (the proposal-triage cap removal, Raise justification).
- `gate` (128978623669, run 42555968038) failed with `FAIL run(s) [42555968032, 42556058045] at this head are still being judged; their gate decides`, and `gate` (128995014829, run 42555968032) with `FAIL budget-raise-gate / budget-raise-gate: failure`. Both are the umbrella gate reporting the two states above; `gate` 129028330496 in run 42556058045 passed at 07:13Z. Root-cause trigger: none of its own — it relays the budget-raise-gate answer above.
- Every other concluded check is success or skipped, including `tests / fast (3.14)` (128979578350), `governance / instrument-self-tests` (128968794869), `pr-contract / pr-contract` (128994276179), `tests / mutation` (128968794805) and `tests / nightly-status` (128968794817).
- The PR is `DIRTY` against main at f5af5b51: GitHub cannot build the merge ref. This head resolves that.
- Earlier heads' reds are answered in the previous rounds' text, kept in this section's history: at 565f9f2b the `gate` wait answer (128732022666), and at b2381acd5004e85a8b85a4643bc0939d25a3bf75 `tests / fast (3.14)` and `governance / instrument-self-tests` (`stamp.py --self-test`'s hold check), fixed by keeping the beat (Mutation proof).

## Unpinned sites

n/a: the diff writes no line under `custom_components/`. This round's executable change is the restored nightly.yml, pinned by the restored checks, and one self-test fixture line, which its own arm and mutants grade.

## Approval

Content approved by tvofi in chat 2026-11-05 (cards C2-C9 accepted; C4, C5, C8 and C6 (a) are this group's). tvofi posts the approving review at the head.

**Policy sentences this round changes**, beyond the round-2 list the verdict holds:
- `delivery-status-tracking.md` item 1 changes. It read "There is no per-PR `dev/programme/delivery/<N>.md` row and no record pull request ... the rows already merged stay as history, read by nothing that gates". It now reads "No seat writes a per-PR ... row (card C5 ...). Nightly's `record-autofix` beat still rows each merge from API facts, because `tools/release/stamp.py`'s flush and `--require-rows` read those rows (orchestrator ruling 2026-11-08, until R10-FLY-STAMP-FLUSH-COST retires them)."
- CLAUDE.md's `delivery-status-tracking.md` row: "no per-PR row" becomes "no seat writes a per-PR row".
- `orchestrator.md` section 9: "no per-PR row (card C5)" becomes "no per-PR row from you (card C5)".
- `fix-review.md`: main's "Evidence names differ beyond case." is unioned in, and "(card C5, tvofi 2026-11-05)" and "(card C4, tvofi 2026-11-05; #1667, 2026-10-27)" lose their dates. That is the cap payment.

- **This round, `orchestrator.md` section 5's proposal bullet** gains main's triage-bar clauses (Merge resolution, origin/main 6457496a): the countermeasure route, the over-20% exemption ACCEPT, the 10% Machinery keep test and the roster-severity mapping. These change what a ruler of proposals must do, as main's R10-FLY-TRIAGE-BAR already did in the deleted contract.
- **This round's cap payment deletes text from `orchestrator.md`**: the "(empty means identical)" anecdote (section 1), the duty list in section 2 ("— sequencing, merging, the record, the freeze, stamps, and speaking to the owner"), "A relative one resolves against the seat's cwd, which was yours for three seats." (section 5), "A word-level diff licensed a union that silently dropped a clause, in a commit claiming nothing was dropped." (section 6), "three symptoms recorded separately are worth less than one analysis of why they were possible" (section 3) and "restated three times" (section 5); section 4's "no method on the GitHub tool surface here exposes them at all" reads "no GitHub tool method here exposes them". No obligation is among them; each is motivation for a rule that stays.

- **This round (merge of origin/main 0a803330), `defect-root-cause.md` Enforcement and `fix-review.md` step 11** change against main's #3305 text: `delivery-status` leaves "`nightly-status` and `delivery-status` grade `main`" and "or drain the overdue rows" goes (card C5 deletes that grader); the pre-ruling rule an unreadable required set keeps is stated (`nightly-status` exempt unless the diff touches its `REPORTER_INPUTS`); fix-review's sentence reads "A red `nightly-status` is not this pull request's: it is not required." (Merge resolution, origin/main 0a803330.)

The round-2 sentences that said the beat is deleted are no longer in the diff.

## Raise justification

Raise approved under mandate (comment 6624093439, scope all) by the orchestrator 2026-11-06 14:4xZ: cap removal for a deleted file, no payment possible.
- **What moves:** no cap rises in substance. The two caps removed belong to `dev/governance/roles/proposal-triage.md` (`files` 36, `files_tokens` 489, in `dev/governance/config/policy_budgets.json`), and card C6 (a) deletes that file.
- **Why a cap must go:** `policy_lint.mjs --budgets` refuses a cap on a missing file, so keeping them is refused too.

Payments tried: keeping the caps (refused by `policy_lint.mjs --budgets`); keeping the file as an on-demand contract (rejected, because card C6 retires the seat and an unread contract is spent prose).

- **The other policy files:** each one this diff touches is paid inside its own cap. The previous round's `fix-review.md` union is paid by the two dates; this round's `orchestrator.md` fold by the deletions listed under Approval. Payment considered and not taken: carrying the 489-token cap of the deleted file to `orchestrator.md` (a per-file raise, owner-confirmed before the push under rule 2, which this unattended seat could not obtain, and unneeded once the motivation text paid it).
- **The score:** re-run in this seat at 0aa9d4f2fba26e5ec93c42bec570f5faddbaa19b (`python3 tools/audit/archscore/score.py --diff 0a8033305d7b03494eb63453e6181a13ffa55c05 HEAD`). This round's union is paid inside its own two caps (Merge resolution), no budget change.
Architecture score: dS +0.0000 NULL

## Forward-carry

- Delete Nightly's `record-autofix` beat once no stamp rule reads it. That deletion covers:
  - its `push:` trigger and `HOLD_MAX_AGE_S`;
  - `merge_train.py`'s train hold (`hold_refresh`, `HOLD_REF`) and the stamp's `hold_bound_s`/`train_hold`/`record_flush` arms;
  - `record_row.py`'s `governance / delivery-status` red name (that job is deleted by this PR);
  - the pins this PR restored in `tests/entities.py`, `merge_train.py` and `orchestrator_tick.py`.

  The stamp's flush (rules 3-4) and rule 5 (`--require-rows`) still read the beat, and that group is changing the flush now (orchestrator ruling 2026-11-08). Carry: R10-CLOSEOUT-INSTRUMENTS

## Carries

- **Carry 1** is the roster's carry on R10-PROCESS-SLIM: a repair body's `## Head` named the previous handoff. `tools/audit/seat/body_push.sh` now refuses `head-stale` when `## Head` does not name `handoff/<topic>`'s code sha. The check runs after the identity guard (round 3) and pushes nothing. It is unchanged by this round, and `body_push.sh --self-test` prints `35 checks, 0 failed`.
- **Carry 2** is the instrument-self-tests timeout. Main's R10-HOTFIX-SELFTEST-TIMEOUT answers it now, by running the slow self-tests detached under the 30-minute timeout. This branch's own answer (`open_pr.sh` and `update_pr.sh` no longer re-running `pr_args.sh`'s self-test, and a 40-minute timeout) is dropped in the merge in favour of main's (Merge resolution).

## Friction

- r10-process-slim-1: cost: with the record stream retired, `merge_train.py --bot-prs` (`sweep_bots`) likely has nothing left to merge; this was not measured here. Carry: dismissed: unmeasured, and deleting a live train path is beyond the cards' scope.
- r10-process-slim-2: unenforced: `bus.sh`'s C8 gate cannot see a cheap check GitHub has not yet created. Carry: dismissed: the card's risk line accepts review starting early, never a merge at red.
- r10-process-slim-3: unenforced: the container's `BASH_ENV` sets a `RUNNER_TEMP` it does not create, so `ci_predict.py`'s STEP REPLAY self-test reads red in a fresh cloud seat until the directory exists. Carry: dismissed: environment setup, not this diff's code; the measured fix is one `mkdir`.
- r10-process-slim-4: unenforced: `tools/pr/ci_predict.py`'s grader replay clones the local repository with `--shared`, so a carry to a group that lives only on the round's roster branch reads `BAD-DEST` there unless the seat holds a local `handoff/audit-r<N>-roster` branch, while pr-contract's own step fetches that ref and routes it (Figures, prepr). Carry: dismissed: a predictor false red with a one-command local remedy, outside this group's cards; the orchestrator may route it.
- r10-process-slim-5: unenforced: a repair seat's step ref `handoff-wip/r10-process-slim` (6b1472f52, tree-identical to 491177c4) outlived its handoff, so the next seat's step push is not a fast-forward and replacing it needs a delete this container's guard refuses; this seat pushed no step ref. The seat that pushed it owed the ref's deletion after its body push (brief's Output step). This round fast-forwarded it with a step commit whose parents are 6b1472f52 and the seat's head, so no delete was needed. Carry: dismissed: a fast-forward step commit over the stale ref needs neither a delete nor a guard exception.
