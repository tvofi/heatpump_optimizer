R10-OUTSIDE-CONTRIBUTOR-CYCLE part 2 of 2: section (E) of the approved design (`design/R10-OUTSIDE-CONTRIBUTOR-CYCLE` `142e70df1b77cf9e7f63d6675b9ad560941e20c9`, approved by `design-verdict/R10-OUTSIDE-CONTRIBUTOR-CYCLE` `fb36c832b6eeb3307bb07502d9a2529b36474535`). Merges with main stay ours on a fork head, and no program of the train turns a contributor's verdict into the owner's approval. No finder harness: the group is an owner report (triage batch 238, P714).

**Repair of the blocked handoff `40abc1bd0a2cf1fd9524aa824713d6a0207a5d3d`** (verdict `Fix review: blocked ... carry-missing`, nonce 00b0ea32). This head merges origin/main `19baca76181c` and part 1's published head `e216e6c09878b3845ec057ce355ea74fd0ac21bb` (`refs/heads/handoff/r10-outside-contributor-cycle`) into 40abc1bd, then repairs on top. Part 1 is therefore under this branch, and the merge order is: part 1 and this part together, or part 1 first only with the fixture line of item 5 below (see "Part 1 alone").

What the repair changes, each against the verdict:

1. **Block item 1: the calls are part 1's real entry points.** Part 1's `tools/pr/outside.py` has no `cross_repository` and no `contract`; it has `pull_facts(repo, pr, pull)` and `check(repo, pr, ref, ...) -> (rc, lines)`.
   - `Train.fork_head` asks `pull_facts` for the pulls object the train already read, and reads a head repository other than ours as a fork's: the comparison `outside.py`'s own `shape` makes. `pull_facts` also refuses a pulls object of another number; that refusal is a Stop like any other unread head.
   - `Train.outside_contract` runs `check(repo, pr, "origin/main")`. rc 0 admits. rc 1 is a refusal. rc 3 ("not an outside pull request", no allowlist entry) is also a refusal on a fork head. `check` reads the LIVE head, so an admission counts only when its `OUTSIDE:` line names the landing head `<h>`; one naming another head parks with `it admitted a head other than <h>`.
   - merge_pr.sh's `head_is_ours` asks `pull_facts` the same way.
2. **Block item 2: `OUTSIDE_MAIN_COPIES`** names the allowlist at part 1's path, `dev/governance/config/outside_contributors.json`. It also gains the two files part 1's `Rules` opens from the checkout: `tools/policy/policy_lint.mjs` (POLICY_GLOBS, POLICY_DIRS) and `tests/closure.py` (GATE_FILES). A stale copy of either would change the path classes. A self-test reads the real module's source (above its `self_test`) and asserts the list is exactly what it opens under its root plus `ALLOWLIST` and `CODEOWNERS`. A file `outside.py` comes to open or read is then refused here, not at the train.
3. **Block item 3: remerge_main.sh's read-back predicates.** Two fake update-branch answers are added to `remerge_main_selftest.py`:
   - `side`: a 2-parent merge whose second parent carries main's tree but is no first-parent commit of main.
   - `notold`: the automatic merge's tree under a first parent that is not the old head.

   Each fails the read-back. Deleting the `rev-list --first-parent origin/main | grep -qx "$p2"` line kills the first; dropping `[ "$p1" = "$old" ]` kills the second.
4. **The real module in every caller's self-test.**
   - The train's `OutsideStub` answers `pull_facts` through the real module's own function. Its `check` stays stubbed, so the cases that need a scripted answer still have one.
   - Five new cases run the real module's `check` itself (`the real outside.py: ...`), with only its edges answered: `api`, `git` and `show`. They run on this tree's policy_lint.mjs, tests/closure.py and mandate gate.
   - merge_pr.sh's self-test no longer writes a stub. It loads `tools/pr/outside.py` of its own tree, and a new case shows it is the real one: a pulls object of another number is refused with `pull_facts`' own words.
5. **The combined tree's train self-test (found here, not in the verdict).** Part 1's `app_approve.sh --carry` asks `git ls-remote --heads origin` whether a head is a branch tip of ours. The train self-test's throwaway repository (`add, a train live` / its null control) had no `origin`, so both cases read `origin's branch heads could not be listed` and failed. The fixture now makes the throwaway repository its own origin. The null control still refuses by the carry rule proper, because the listing now succeeds.
6. **Carry 1, built here:** `tools/ci/selftest_closures.json`'s `pr-merger` step is re-recorded by `selftest_scope.py record --step pr-merger` (strace). Its self-test now opens `tools/pr/outside.py`.

Unchanged from 40abc1bd, and pinned as before: `approve` reads the contract on every cross-repository head at every step 6, before the already-approved shortcuts. `_approve` returns `owner` on a code-owned fork head with class O standing. The three writers Stop `[OUTSIDE]` before a post (`no_fork_post`). `recarry` detaches a fork head's worktree at `refs/remotes/pull/<pr>/head` and passes `--head-repo`. remerge_main.sh moves the fork by GitHub's `update-branch` at `expected_head_sha` as the hpo-author App. merge_pr.sh owner mode refuses in `gates` on a cross-repository or unread head.

Alternatives, and why each lost (`fixer.md` step 17):
- **Add `cross_repository` and `contract` to part 1's module.** That edits part 1's file to fit this part's guess. `pull_facts` and `check` already are the one owner's facts and contract; a wrapper there would be a second entry point for the same thing.
- **Run `check` on the pulls object (`pull=`).** That form is pr-contract's early signal. It reads neither the reviews nor the other pull requests at the head, and refuses unless `early`. The train needs the gate's form.
- **Pass the head to `check`.** It takes none, and reads the live head itself. The train compares the head the admission names with its own instead of changing part 1's signature.
- **Keep the stubs and test the real module in a separate check.** Then a stub could still pass a call the real module does not have, which is exactly how 40abc1bd went green.

Carries of earlier rounds answered (each names a file of this part): 23 (step 6 reads the contract every time; self-test "an unowned class-O path ... PARKS at the next step 6 once the mandate is revoked"); 14, round 2; 16 and 26; 24; 11; 16, round 3. Their wording is unchanged from 40abc1bd's body, which the roster at `c161476814b0` holds.

## Head

`0d2dfd8b850441a1db42f4c88042dc5b27e88917`, measured against origin/main `19baca76181cb019d9b1cfd93ee6bc0a08e20047` (read 2026-11-12T15:45Z). Its parents are 40abc1bd, origin/main `19baca76181c` and part 1's `e216e6c09878`; the repair commits sit on top. `git merge-tree --write-tree origin/main HEAD` exits 0 with no conflict.

## Mutation proof

By hand at this head: each one predicate replaced in the committed tree, the owning self-test run, the file restored. The instrument is the self-test named; a kill is its `FAIL` lines (count by `grep -cE '^ *FAIL'`).

merge_train.py, `python3 -I tools/audit/seat/merge_train.py --self-test` (710 checks at the head):
- `fork_head`'s `cross = facts["head_repo"] != self.repo` to `cross = False`: 27 FAIL, among them every `fork head recarry:` case.
- `fork_head` reading the raw pulls object instead of `pull_facts` (the pre-repair shape, real `pull_facts` unasked): 4 FAIL, among them `FAIL fork head: a pulls object read for another pull request is a Stop saying so ...`.
- `outside_contract`'s ` and f" at {h}: " in str(ln)` deleted: `FAIL the real outside.py: an admission of another head parks the fork head [OUTSIDE] ...`.
- `outside_contract`'s `ok = rc == 0 and` to `ok = rc in (0, 3) and`: `FAIL fork head: \`check\` exiting 3 parks [OUTSIDE] even beside an admission-shaped line -- only rc 0 admits`. This case was added because the mutant first survived.
- The allowlist entry of `OUTSIDE_MAIN_COPIES` back at `dev/governance/outside_contributors.json`: 2 FAIL (`... the files the contract must hold as origin/main's own ...` and `... exactly what the real outside.py opens ...`).
- The reviewer's named mutants of 40abc1bd's lines, re-run here:
  - `no_fork_post`'s `if fork is not None:` to `if False:`: 3 FAIL.
  - `outside_contract`'s `if ok is not True:` to `if False:`: 11.
  - `outside_is_mains`' blob comparison to `if False:`: 2.
  - `self.contracted.pop(pr, None)` dropped: 1.
  - The unnamed-fork refusal to `if False:`: 1.

  The rest of the reviewer's sixteen (`ev/train_mutants.txt`) mutate lines this repair does not change (`git diff 329e8043a4 HEAD -- tools/audit/seat/merge_train.py` touches only `fork_head`, `outside_contract`, `OUTSIDE_MAIN_COPIES` and the self-test). They were reported killed at 40abc1bd and are not re-run here.

merge_pr.sh, `bash tools/audit/seat/merge_pr.sh --self-test` (29 checks):
- `head_is_ours`' `cross = facts["head_repo"] != repo` to `cross = False`: `FAIL owner mode on a cross-repository head refuses, naming the fork (decision 0017)` and `FAIL ... having read the pull request and neither the mandate nor a post`.
- The pre-repair call `cross = bool(mod.cross_repository(pull, repo))` restored: 7 FAIL, every owner-mode case that reaches `head_is_ours` (`OUTSIDE REFUSE: .../tools/pr/outside.py could not say whether #7's head is cross-repository`). That is the verdict's measurement, now red in this file's own self-test.

remerge_main.sh, `python3 -I tools/audit/seat/remerge_main_selftest.py` (13 checks):
- The `rev-list --first-parent origin/main | grep -qx "$p2"` line deleted: `FAIL a new head with a second parent that is no first-parent commit of main (its tree is main's) fails the read-back: not PUSHED, non-zero` (13 checks, 1 failed).
- ` && [ "$p1" = "$old" ]` dropped: `FAIL a new head with a first parent that is not the old head (the tree is the automatic merge) fails the read-back ...` (13 checks, 1 failed).

Failing test first: the five `the real outside.py:` cases and the `read for another pull request` case fail on the pre-repair production code (Null control below).

## Null control

- **The pre-repair tree is red on the combined tree.** Take 40abc1bd's production text of `fork_head`, `outside_contract` and `OUTSIDE_MAIN_COPIES` (the three hunks of the first repair commit, reversed by content), with this head's self-test, on the merge with part 1. The train's self-test prints 10 `FAIL` lines and then dies with a `TypeError` (rc 1). Among the FAILs: `FAIL fork head null control: a head of ours, read by the same reader, is asked of outside.py and never put to the outside contract` and `FAIL the real outside.py null control: a head of ours is read by its \`pull_facts\` as ours, merged, and never put to \`check\``. So a same-repository head is refused alongside the fork heads, which is the verdict's "stops the train on every pull request".
- **At this head, both kinds of head are admitted where the contract allows.** With the real module's `check`:
  - `ok the real outside.py: a fork head of an allowlisted author changing class-F paths only is ADMITTED by its own \`check\` at the landing head, and the train merges it on the App's approval`
  - `ok the real outside.py null control: a head of ours is read by its \`pull_facts\` as ours, merged, and never put to \`check\``

  Its refusals keep the contract's own words: a class-R path, an author on no allowlist entry (rc 3), an admission of another head.
- merge_pr.sh: `null control: app mode on a cross-repository head passes the gates`. The owner-mode cases pass on a head of ours through the real module.
- remerge_main.sh: the `ok` fork case (`a fork head is merged by update-branch at the expected head and reads back PUSHED`) is the twin of `side` and `notold`, on the same fixture.
- selftest closures: with the recorded table before the re-record, `selftest_scope.py select --change M:tools/pr/outside.py` selects no `pr-merger` step (0 `run pr-merger` lines); at this head it does (`MODE: SCOPED`, `run pr-merger`).
- Part 1 alone: `merge_train.py --self-test` at `e216e6c09878` prints `656 checks, 2 failed` (the two `add, a train live` cases). The same at origin/main `19baca76181c` prints `656 checks, 0 failed`, and at 40abc1bd `701 checks, 0 failed`. This head prints `710 checks, 0 failed` with the fixture line of item 5.

## Figures

At `0d2dfd8b850441a1db42f4c88042dc5b27e88917`, origin/main `19baca76181c`:
- `python3 -I tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 710 checks, 0 failed` (40abc1bd: 701; the base fc2a7edcf2be: 656).
- `bash tools/audit/seat/merge_pr.sh --self-test`: `merge_pr self-test: 29 checks, 0 failed` (40abc1bd: 28).
- `python3 -I tools/audit/seat/remerge_main_selftest.py`: `remerge_main self-test: 13 checks, 0 failed` (40abc1bd: 11).
- `bash tools/audit/seat/pr_args.sh --self-test`: `pr_args self-test: 205 checks, 0 failed`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: FULL -- every test script runs, nothing is scoped out.`, `reason: .github/workflows/tests.yml changes the gate itself`. That file is part 1's (`git diff 329e8043a4 HEAD --stat` names this repair's four files only: merge_train.py, merge_pr.sh, remerge_main_selftest.py, tools/ci/selftest_closures.json). Under `MODE: FULL` there is no scope to run locally; the suite is CI's.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/ci/selftest_scope.py record --step pr-merger`: `recorded 1 step(s) ...; 0 failed [], 0 broken trace(s)`. Against the recorded table, the step's files gain `tools/pr/outside.py`, its probes gain `tools/pr`, and every other step is equal (113 of 114 untouched).
- `git diff --stat $(git merge-base origin/main HEAD)...HEAD`: 23 files, part 1's and this part's. `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are outside it. `dev/governance/config/policy_budgets.json` is in it, from part 1 (`git diff 329e8043a4 HEAD` does not name it).

## Red checks

No CI run exists at this head. Predicted by prepr's ci-predict:

- `budget-raise-gate`: inherited from part 1, not built here.
  - The cause: the diff against main carries part 1's raise of `.claude/workflows/policy_budgets.json` (`files_tokens.tools/audit/briefs/fix-review.md: 2546 -> 2775`). `git diff 329e8043a4 HEAD` names no `*_budgets.json`.
  - It is red by design until tvofi approves at the head (CLAUDE.md rule 2, `budget-raise-gate`, 0013); that approval is the owner's and is answered in part 1's body.
  - The cheaper detector already ran: prepr's ci-predict named it before any pull request existed. It costs nothing extra, because it runs on every prepr.
- pr-contract's policy_lint arm: the same raise read by the base's copy (`BOOTSTRAP`). Its answer is the owner's approval above, not a change here.

## Raise justification

This repair raises nothing: `git diff 329e8043a4 HEAD` names no `*_budgets.json`. The one raise in the diff against main is part 1's, carried by the merge of `e216e6c09878`: `files_tokens` for `dev/governance/roles/fix-review.md` (`tools/audit/briefs/fix-review.md` in the budget file), `2546 -> 2775`. That is the value `node tools/policy/policy_lint.mjs --budgets` measures.

What the raise buys, in part 1's words (`handoff-body/r10-outside-contributor-cycle`, section `## Raise justification`): the class-O read seat's rule in the contract that seat reads, which the design verdict's item 27 requires there.

Payments tried: four, by part 1, none taken. Each reason is part 1's:
- cutting spent prose (every sentence is a verdict rule another seat is graded by);
- a pointer-only text (no headroom, and it drops item 27's sentence);
- moving the paragraphs to the instrument guide or `docs/CONTRIBUTING.md` (outside the measured corpus, the escape `ratchet-budgets.md` names);
- a new role contract (more corpus tokens, a new cap, and a `CLAUDE.md` row with `CLAUDE.md` at its own cap).

This part tried no payment of its own, because it adds no token to the file.

Architecture score: dS +0.0000 NULL

## Unpinned sites

none: prepr's unpinned-sites step reported `the diff adds no unpinned mutation site`. Its diff-mutant draw was not taken. The first 40 added `.py` lines of this diff against main are part 1's `tools/pr/outside.py`, which merge_train's self-test does not own. This repair's own production predicates were mutated by hand (Mutation proof).

## Approval

This repair adds no policy file: `git diff 329e8043a4 HEAD` names merge_train.py, merge_pr.sh, remerge_main_selftest.py and `tools/ci/selftest_closures.json`. The last is code-owned.

The diff against main also carries part 1's policy and code-owned files, by the merge of `e216e6c09878`:
- decision 0017, `dev/governance/roles/fix-review.md`, `dev/governance/config/outside_contributors.json`, `dev/governance/config/policy_budgets.json`;
- `.github/workflows/`, `.github/CODEOWNERS`.

Their approval record is part 1's `## Approval` (`handoff-body/r10-outside-contributor-cycle`). All of them merge on the owner's approving review at this head. Under the owner's ruling of 2026-11-12 quoted in the design note ("a mandate made by me is valid for my machinery"), that review may be the programme's mandate approval.

## Forward-carry

<!-- Carries 0 to 6 keep the numbering of 40abc1bd's body, whose seven items the relay folded onto the roster. Each line says where it now stands. -->

- Carry 0: **The interface to part 1's module.** Built in this diff (items 1 and 4): `fork_head`, `outside_contract` and `head_is_ours` call part 1's `pull_facts` and `check`, and each caller has a self-test on the real file. Carry: dismissed: built here, the verdict's block item 1
- Carry 1: **`tools/ci/selftest_closures.json` re-record.** Built in this diff (item 6), for `pr-merger`, the one step whose self-test newly opens part 1's module. `merge-train` records `objects: true` and is selected on every diff. Carry: dismissed: built here, re-recorded with strace
- Carry 2: **The live checks the design owes are not run.** This seat has no `gh`, no App key and no fork pull request. Three are owed:
  - (a) whether GitHub lets the hpo-author installation token of our repository call `update-branch` on a maintainer-editable fork pull request, and which identity the resulting merge commit carries (carry 11);
  - (b) app_approve.sh approving an adopted verdict end to end after that merge (carry 8);
  - (c) which `commit_id` a class-O approval reports before and after it (carries 20, 25).

  remerge_main.sh's fork arm is proved against a fake `curl` and a fake mint only. Run all three on a test fork before the owner adds the allowlist entry. If (a) is refused, the train parks `[OUTSIDE] ... no personal token is tried without the owner`, the designed stop. R10-CI-PRIORITY-PAUSE is the live group on the merge train's run control, and shares this part's files. Carry: R10-CI-PRIORITY-PAUSE
- Carry 3: **The three instruments' guides and decision 0017 owe this part's surface:** remerge_main.sh's `--head-repo`, the `[OUTSIDE]` block class, and carry 29's sentence that no tool of ours pushes a fork head to a branch of origin. That sentence is true of this part: the fork head is fetched to `refs/remotes/pull/<pr>/head` only. The decision is policy, an owner-approved text, and not written by a fixer. Carry: R10-PROCESS-SLIM
- Carry 4: **Carry 14, round 3:** `_post_agent_approval`'s body under a bare `--mandate` id reads "under <id>", which `MANDATE_CITE` does not read as a citation. Whether it should say "mandate comment <id>" for our own heads is the train's wording, unchanged here. R10-GATE-DEFER-BARRIER is the live group on merge_train.py's approval path. Carry: R10-GATE-DEFER-BARRIER

## Friction

- prepr-ci-predict: unenforced: Carry 5: `tools/pr/ci_predict.py` runs the base's `carry_audit.py` in a `--shared` clone that holds no `origin/handoff/audit-r<N>-roster`. A `Carry:` to a group that lives only on the round's roster branch therefore reads as a bad destination, while `pr-contract.yml` fetches that ref before the same check. It reproduced at this head: the prediction refused two destinations that main's own `carry_audit.py`, run on a main worktree with `--branch`, routes (`7 routed, 0 unrouted, 0 bad destination(s)`). As the last seat did, this seat gave the clone the ref CI fetches: a local branch `handoff/audit-r10-roster` at `origin/handoff/audit-r10-roster`, pushed nowhere. The predictor owes the fetch. Carry: R10-SEAT-SCRIPT-OUTPUT
- brief: cost: Carry 6: the first dispatch asked for code against an interface part 1 had not published. That made the two calls a guess and cost this repair round. Read from part 1's published head here. Carry: dismissed: resolved in this round, the interface is read from e216e6c09878
