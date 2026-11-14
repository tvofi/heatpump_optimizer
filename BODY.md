R10-OUTSIDE-CONTRIBUTOR-CYCLE part 2 of 2: section (E) of the approved design (`design/R10-OUTSIDE-CONTRIBUTOR-CYCLE` `142e70df1b77cf9e7f63d6675b9ad560941e20c9`, approved by `design-verdict/R10-OUTSIDE-CONTRIBUTOR-CYCLE` `fb36c832b6eeb3307bb07502d9a2529b36474535`). Merges with main stay ours on a fork head, and no program of the train turns a contributor's verdict into the owner's approval. No finder harness: the group is an owner report (triage batch 238, P714).

**Repair of the blocked handoff `0d2dfd8b850441a1db42f4c88042dc5b27e88917`** (verdict `Fix review: blocked ... self-test-red`, nonce 763c689d). This head merges part 1's live head `87b116dd7bb0d42b244fcbf9beee8504802873db` (`refs/heads/handoff/r10-outside-contributor-cycle`) and origin/main `870238eb2194c99ae1ad6f1f78e0665e838c70f3` into 0d2dfd8b, then repairs on top. Part 1 is under this branch; the merge order is part 1 and this part together.

What the repair changes, each against the verdict:

1. **Block item 1, `outside-contract`.** The train self-test's `_post_carry` fixture body no longer holds the outside-read words: outside.py's self-test refuses them in any program under tools/ or .github/ but itself, and the fixture needed only some prior review body. Part 1's check is unchanged.
2. **Block item 1, `app-verdict-poster`, `review-carry`, `obligations-ledger`.** Repaired by part 1 at its commit 6538f92df7 (each fixture puts the carried head on a branch of origin), merged here. The reviewer's enumeration rule, every caller of `app_approve.sh --carry` whose self-test runs the real script, returns those three and merge_train.py. The merge left merge_train's carry fixture adding `origin` twice (part 1's line and this part's round-2 line), which killed the self-test with `git remote add` exit 3; part 1's line stays and this part's goes.
3. **Block item 2.** Two rows drive `outside_contract` with `check` exiting 0 beside a line that names the head and does not start with `OUTSIDE: `: a refusal's own words, and the admission's words mid-line. Each must park `[OUTSIDE]` with `admitted a head other than`. A third row is their null control: the same rc 0 beside the line starting `OUTSIDE: ` is admitted.
4. **Block item 3.** origin/main merged; `tools/ci/selftest_closures.json` taken whole from main in the merge commit, then thirteen steps recorded on top by `selftest_scope.py record` (strace): `outside-contract`, new, and the twelve whose entry this diff moved against its former merge base.
5. **The reviewer's finding on `cross_repository`, built here.** `Train.fork_head` and merge_pr.sh's `head_is_ours` call part 1's `cross_repository(facts, repo)`; neither re-types the comparison. The train's `OutsideStub` answers it through the real module's function.

**Round 4 (mechanical repair of #3521's conflict and reds).** This head merges part 1's settled head `99c3c1625923adaae044b8f1940344196a9b30af` (`origin/fix/r10-outside-contributor-cycle`, its handoff `e4b68c37d939` merged into it) and origin/main `9fdba3b8547f9762438dc19b98b310a63d34dcb1` into the previous PR head `396b8caf9e658f0a2449a6738a2d2863eb3b74c4`, then re-records `tools/ci/selftest_closures.json`. No code line is authored in this round:
6. **Part 1's merge** conflicted only in `tools/ci/selftest_closures.json` (`pr-merger`'s read list: part 1 added `tools/audit/seat/pr_args.sh`, this part `tools/pr/outside.py`); resolved as the union, then superseded by item 8. The merge of origin/main after it was automatic: part 1 had already resolved `tools/pr/ci_predict.py` against main.
7. **`tests / closures` (INERT READS UNDER-APPROXIMATED on `docs/CONTRIBUTING.md`)** is repaired by part 1's commit, merged here: `docs/CONTRIBUTING.md` sits in `tests/closure.py`'s `INERT_EXCEPT` and in the recorded closures of `tests/doc_claims.py` and `tests/harness_headers.py` in `tests/closures.json`, not on the INERT list.
8. **`tools/ci/selftest_closures.json`** taken whole from origin/main `9fdba3b854`, then the thirteen steps whose entry the merged diff moves were recorded on top by `selftest_scope.py record` (strace).

Alternatives, and why each lost (`fixer.md` step 17):
- **Scope part 1's outside-read check off self-test text.** That weakens the check that no other program writes the line to fit a fixture that never needed the words.
- **Keep this part's `git remote add origin <path>` and drop part 1's `.`.** Either lists the fixture's own branches; part 1's is the sibling's published line, and a re-applied delta is diffed against the sibling's head (`fixer.md` step 6).
- **Pin the `OUTSIDE: ` conjunct through the real module only.** The real `check` never prints a head-naming line beside rc 0 that is not the admission, so no real-module row can separate the conjunct; the stubbed answer is the only driver of that shape.

**Round 5 (mechanical merge repair of #3521's conflict).** The handoff tip `c50eee3303f7` was complete. `handoff-wip/r10-outside-contributor-cycle-p2` `8a263ed22f6f` adds only `BLOCKED.md` over it, recording the CARRY-LANDED refusal, and no code. That tip conflicted with origin/main in one file (`git merge-tree --write-tree origin/main HEAD` rc 1), so origin/main was merged into it twice: `d7004eaa775d`, then `23cc7b8e1d00` once main had moved under the first prepr run. Main's second move changed only delivery records and the same table. Part 1 (`handoff/r10-outside-contributor-cycle`) is on main now, so the diff against main is this part's own six files. No code line is authored in this round:
9. **`tools/ci/selftest_closures.json`** (the one conflict, at both merges) is resolved per step, three-way. Steps this part moved are the thirteen whose entry differs between `c50eee33` and its original merge base `9fdba3b854`. Every other step takes main's entry byte-for-byte. A moved step takes the union of both sides: lists unioned, `index`/`objects` OR'd, `run_sha` the merged workflow's. That is `selftest_scope.py`'s `union_entries` rule, which its docstring names for combining measurements. Main has since re-measured and unioned twelve of the thirteen into its own entries (#3595's table), so the merged table differs from origin/main `23cc7b8e1d00`'s in one step only, `pr-merger`. There it adds this part's `tools/pr/outside.py` file and `tools/pr` probe: the step's self-test loads the real `outside.py`. Each of `c50eee33`'s 115 entries is a subset of the merged entry, except `beat-job-rows`, which this part never moved and which keeps main's newer measurement. `selftest_scope.stale()` returns `''` on the merged table against the merged workflow. There was no `strace` re-record, because the host is macOS. Main's push re-measures every step (`check`).
10. Every other file merged without a conflict. `tools/audit/seat/merge_train.py`'s patch against main changed only by part 1's lines, which are now main's own: for example the fixture's single `git("remote", "add", "origin", ".")`, present once in the merged file and once on main.

## Head

`d5c42d1cfa22087033364e1b1a38bfda45912966` merges origin/main `23cc7b8e1d004279d99bd59f3d2bd2a8f885b426` into `0c66a3df1087`, which merges origin/main `d7004eaa775dd7b42aa392df0eb53aeec198b2b0` into the handoff tip `c50eee3303f750d670fbe74c598f88cd8306e868` (round 5, item 9). The handoff tip and the PR head `396b8caf9e65` are both its ancestors.

Previous head: `c50eee3303f750d670fbe74c598f88cd8306e868`, measured against origin/main `9fdba3b8547f9762438dc19b98b310a63d34dcb1` (its merge base) and re-checked against origin/main `6858b4abc1941f8f69fe8eebc5a1101527733dff` at 2026-11-14T17:08Z: `git merge-tree --write-tree origin/main HEAD` exits 0 there, so no further merge was taken. The parents of the code are part 1's `99c3c1625923` and the previous PR head `396b8caf9e65`; the round adds two merge commits and the closures commit.

## Mutation proof

By hand at `c50eee3303f750d670fbe74c598f88cd8306e868`'s code (the commit before it, the same code tree; the closures commit changes only `tools/ci/selftest_closures.json`): one predicate replaced in the committed tree, the owning self-test run, the file restored by `git checkout`. A kill is the self-test's `FAIL` lines.

merge_train.py, `python3 -I tools/audit/seat/merge_train.py --self-test`:
- `outside_contract`'s `str(ln).startswith("OUTSIDE: ") and ` deleted (the reviewer's survivor t15): `merge_train self-test: 811 checks, 2 failed`, both new rows: `FAIL fork head: \`check\` exiting 0 beside a refusal's own words naming the head parks [OUTSIDE] ...` and `FAIL fork head: \`check\` exiting 0 beside the admission's words mid-line naming the head parks [OUTSIDE] ...`.
- `fork_head`'s `cross = _outside_gate().cross_repository(facts, self.repo)` to `cross = False`: `merge_train self-test: 811 checks, 31 failed`, among them every `fork head recarry:` case; the count is this run's.

merge_pr.sh, `bash tools/audit/seat/merge_pr.sh --self-test`:
- `head_is_ours`' `cross = mod.cross_repository(facts, repo)` to `cross = False`: `merge_pr self-test: 35 checks, 2 failed`: `FAIL owner mode on a cross-repository head refuses, naming the fork (decision 0017)` and `FAIL ... having read the pull request and neither the mandate nor a post`.

The mutants of the lines this round does not change were run by the reviewer at 0d2dfd8b (22 run, 21 killed; the survivor is the first bullet) and are not re-run here.

## Null control

- **The four steps at both ends.** At 0d2dfd8b the reviewer measured `outside self-test: 208 checks, 1 failed`, `app_comment` `67 checks, 6 failed`, `review_carry` `29 checks, 4 failed`, `ledger` `102 checks, 1 failed`. At this head the same commands print 0 failed (Figures).
- **The admission row.** With the conjunct in place, rc 0 beside the line starting `OUTSIDE: ` at the head is admitted (`ok ... null control: the same rc 0 beside the line starting \`OUTSIDE: \` at the head is admitted`), so the two new rows refuse on the line's start and not on rc 0.
- **The doubled remote.** With both `git remote add origin` lines, as the merge left them, `merge_train.py --self-test` dies in `_add_self_test` with `CalledProcessError ... 'git', 'remote', 'add', 'origin' ... exit status 3` and prints no summary line; with one it prints the summary line `merge_train self-test: ... 0 failed` (Figures).
- **The closures table.** Against origin/main `9fdba3b854`'s table, the recorded one adds the step `outside-contract` and changes twelve entries; the other 102 of main's 114 are byte-equal (compared by loading both files with `json.load` and comparing each step's entry; a step that differs is listed, so a 0-difference table would print an empty list).

## Figures

At `0c66a3df1087276324abb4c5f00b305ea9e2f8d2`, origin/main `d7004eaa775dd7b42aa392df0eb53aeec198b2b0`, 2026-11-14T21:53Z (macOS host). The round-5 head `d5c42d1cfa22` differs from it only by main's delivery records and `tools/ci/selftest_closures.json` (`git diff --stat 0c66a3df d5c42d1c`), so no program these self-tests run changed. Each line is the tool's own last line:
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 815 checks, 0 failed`.
- `bash tools/audit/seat/merge_pr.sh --self-test`: `merge_pr self-test: 35 checks, 0 failed`.
- `python3 -I tools/audit/seat/remerge_main_selftest.py`: `remerge_main self-test: 13 checks, 0 failed`.
- `python3 -I tools/pr/outside.py --self-test`: `outside self-test: 266 checks, 0 failed`.
- `python3 -I tools/ci/selftest_scope.py --self-test`: `selftest_scope self-test: 110 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)`. `node tools/policy/brief_lint.mjs`: rc 0, last line `PLAYBOOK ok: ...`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL`, reason `tools/ci/selftest_closures.json changes the gate itself`. The suite is CI's.
- `git merge-tree --write-tree origin/main HEAD` at d5c42d1c against origin/main 23cc7b8e1d00: rc 0. It was rc 1 at c50eee33 and at 0c66a3df, each time on `tools/ci/selftest_closures.json`.

The figures below this line were measured at the previous head c50eee33 and are kept as that round's record:

At `c50eee3303f750d670fbe74c598f88cd8306e868`'s code tree, origin/main `9fdba3b8547f9762438dc19b98b310a63d34dcb1`, 2026-11-14 (16:00Z to 17:08Z):
- `python3 -I tools/pr/outside.py --self-test`: `outside self-test: 266 checks, 0 failed`.
- `bash tools/pr/app_comment.sh --self-test`: `app_comment self-test: 70 checks, 0 failed`.
- `python3 -I tools/audit/seat/review_carry.py --self-test`: `review_carry self-test: 32 checks, 0 failed`.
- `python3 -I tools/audit/seat/ledger.py --self-test`: `ledger self-test: 104 checks, 0 failed`.
- `python3 -I tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 811 checks, 0 failed`.
- `bash tools/audit/seat/merge_pr.sh --self-test`: `merge_pr self-test: 35 checks, 0 failed`.
- `python3 -I tools/audit/seat/remerge_main_selftest.py`: `remerge_main self-test: 13 checks, 0 failed`.
- `bash tools/audit/seat/bus.sh --self-test`: `bus self-test: 230 checks, 0 failed`.
- `bash tools/pr/app_approve.sh --self-test`: `app_approve self-test: 350 checks, 0 failed`.
- `python3 -I tools/pr/ci_predict.py --self-test`: `ci_predict self-test: 0 failed`.
- `node tools/policy/field_coverage.mjs --self-test`: `FIELD COVERAGE SELF-TEST ok`. `node tools/policy/policy_lint_mutants.mjs`: rc 0.
- `python3 -I tools/audit/seat/selftest_wiring.py --self-test`: `selftest_wiring self-test: 26 checks, 0 failed`; `--check`: rc 0, `selftest_wiring: 0 index gap(s)`.
- `bash tools/audit/seat/open_pr.sh --self-test`, `pr_args.sh --self-test`, `update_pr.sh --self-test`: each ends `pr_args self-test: 261 checks, 0 failed`, rc 0.
- `python3 -I tools/ci/selftest_scope.py record --step <each of the thirteen>`: `selftest_scope: recorded 13 step(s) ...; 1 failed ['verdict-bus'], 0 broken trace(s)`. `verdict-bus` (bus.sh's self-test) then passed under `strace -f -qq -o /dev/null bash tools/audit/seat/bus.sh --self-test` (`bus self-test: 230 checks, 0 failed`) and untraced (above), and `python3 -I tools/ci/selftest_scope.py record --step verdict-bus` recorded it: `recorded 1 step(s) ...; 0 failed [], 0 broken trace(s)`. The one traced failure did not reproduce in two runs; its FAIL line was not captured (the record prints the step's tail only).
- `python3 -I tools/ci/selftest_scope.py static`: `selftest_scope static: 115 gated step(s), 0 problem(s)`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: FULL -- every test script runs, nothing is scoped out.`, `reason: .github/workflows/tests.yml changes the gate itself`. That file is part 1's. Under `MODE: FULL` there is no scope to run locally; the suite is CI's.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `git diff --stat $(git merge-base origin/main HEAD)...HEAD`, at c50eee33: 31 files, part 1's and this part's (at the round-5 head: 6 files, this part's own, since part 1 is on main). `VERSION`, `RELEASE_NOTES.md`, the manifest and both claim files are outside it; `dev/governance/config/policy_budgets.json` is in it, from part 1.

## Red checks

CI ran at the previous head `396b8caf9e65` on 2026-11-12 (21:10Z to 21:53Z); its required reds are answered below. None of them is built by this part's code.

- `budget-raise-gate / budget-raise-gate` at 396b8caf, job 131494044713: `RAISE .claude/workflows/policy_budgets.json: files_tokens.tools/audit/briefs/fix-review.md: 2546 -> 2775 (a pinned value the gate cannot sign as routine)`, then `REFUSED: no decisive review by tvofi (id 70032254) on this pull request`. Cause: part 1's raise carried in by the merge, with no approving review at the head. No cheaper detector exists for a missing approval: the gate is the check that reads it, and it clears only on the owner's (or a mandate's) approving review at the head (`## Approval`). It stays red at this head until that review; prepr named it before any pull request existed.
- `tests / closures` at 396b8caf, job 131494487808: `INERT READS UNDER-APPROXIMATED`, naming `tests/doc_claims.py: docs/CONTRIBUTING.md` and `tests/harness_headers.py: docs/CONTRIBUTING.md`. Cause: part 1 added `docs/CONTRIBUTING.md` under the INERT `docs/` prefix while two measured scripts read it. Repaired by part 1's commit merged here (item 7). Cheaper detector: `./tests/derive_closures.sh --single <script>` for the two scripts on the author's Linux machine before the push, which is part 1's seam; its standing cost was not measured here, and no countermeasure is built in this part.
- `pr-contract / pr-contract` at 396b8caf, job 131517308122: `PR-BODY: 2 error(s)`, `check \`budget-raise-gate / budget-raise-gate\` is red and \`## Red checks\` does not name it` and the same for `tests / closures`. Cause: the body then current had not been updated for that CI run. Cheaper detector: none beyond the one that already exists, `prepr.sh`'s pr-body step, which reads the PR's reds only once a PR has run CI; the body is now re-written with both named (above).
- `tests / briefs` at part 1's merge commit `21b69d9a97d8b4b2072546d8adb4b67865f8c11d` (under this branch through part 1), job 131905563323: `LEGACY-CONTROL VACUOUS: carry-1412.json: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`. Not at this head: CI's step command `node tools/policy/brief_lint.mjs`, run here, exits 0 and prints no `VACUOUS` line (its last line `PLAYBOOK ok: ...`). Cause: a stale exemption at that tree, gone by part 1's later commits and main. Cheaper detector: the same command, which prepr's `brief_lint` step already runs locally in seconds; it was part 1's head to run, and no countermeasure is built here.
- `governance / instrument-self-tests` at 396b8caf, job 131494044297 (not in the `merge_train.py owed-reds` set, answered because a self-test red at the head is a block): the API's log tail does not reach the failing step. Every self-test the merged diff reaches passes at this head (Figures), and the closures table is re-recorded on the merged tree (item 8), so the table's entries match this tree's reads.

## Raise justification

This repair raises nothing: `git diff 87b116dd7b HEAD` names no `*_budgets.json`. The one raise in the diff against main is part 1's, carried by the merge of `87b116dd7bb0`: `files_tokens` for `dev/governance/roles/fix-review.md` (`tools/audit/briefs/fix-review.md` in the budget file), `2546 -> 2775`. That is the value `node tools/policy/policy_lint.mjs --budgets` measures.

What the raise buys, in part 1's words (`handoff-body/r10-outside-contributor-cycle`, section `## Raise justification`): the class-O read seat's rule in the contract that seat reads, which the design verdict's item 27 requires there.

Payments tried: four, by part 1, none taken. Each reason is part 1's:
- cutting spent prose (every sentence is a verdict rule another seat is graded by);
- a pointer-only text (no headroom, and it drops item 27's sentence);
- moving the paragraphs to the instrument guide or `docs/CONTRIBUTING.md` (outside the measured corpus, the escape `ratchet-budgets.md` names);
- a new role contract (more corpus tokens, a new cap, and a `CLAUDE.md` row with `CLAUDE.md` at its own cap).

This part tried no payment of its own, because it adds no token to the file.

Architecture score: dS +0.0000 NULL


## Unpinned sites

none: prepr's unpinned-sites step reported `the diff adds no unpinned mutation site`. Its diff-mutant draw was not taken: the first 40 added `.py` lines of this diff against main are part 1's `tools/pr/outside.py`, which merge_train's self-test does not own. This round's production predicates were mutated by hand (Mutation proof).

## Approval

This round adds no policy file: against part 1's head and main it changes merge_train.py, merge_pr.sh and `tools/ci/selftest_closures.json`. The last is code-owned.

The diff against main also carries part 1's policy and code-owned files, by the merge of `87b116dd7bb0`:
- decision 0017, `dev/governance/roles/fix-review.md`, `dev/governance/config/outside_contributors.json`, `dev/governance/config/policy_budgets.json`;
- `.github/workflows/`, `.github/CODEOWNERS`.

Their approval record is part 1's `## Approval` (`handoff-body/r10-outside-contributor-cycle`). All of them merge on the owner's approving review at this head. Under the owner's ruling of 2026-11-12 quoted in the design note ("a mandate made by me is valid for my machinery"), that review may be the programme's mandate approval.

## Forward-carry

<!-- Carries 0 to 6 keep the numbering of 40abc1bd's body, whose seven items the relay folded onto the roster. Each line says where it now stands. -->

- Carry 0: **The interface to part 1's module.** Built in this diff (items 1 and 4): `fork_head`, `outside_contract` and `head_is_ours` call part 1's `pull_facts` and `check`, and each caller has a self-test on the real file. Carry: dismissed: built here, the verdict's block item 1
- Carry 1: **`tools/ci/selftest_closures.json` re-record.** Built in this diff (items 4 and 8), for `pr-merger`, the one step whose self-test newly opens part 1's module. `merge-train` records `objects: true` and is selected on every diff. Carry: dismissed: built here, re-recorded with strace
- Carry 2: **The live checks the design owes are not run.** This seat has no `gh`, no App key and no fork pull request. Three are owed:
  - (a) whether GitHub lets the hpo-author installation token of our repository call `update-branch` on a maintainer-editable fork pull request, and which identity the resulting merge commit carries (carry 11);
  - (b) app_approve.sh approving an adopted verdict end to end after that merge (carry 8);
  - (c) which `commit_id` a class-O approval reports before and after it (carries 20, 25).

  remerge_main.sh's fork arm is proved against a fake `curl` and a fake mint only. Run all three on a test fork before the owner adds the allowlist entry. If (a) is refused, the train parks `[OUTSIDE] ... no personal token is tried without the owner`, the designed stop. R10-CI-PRIORITY-PAUSE, which held the merge train's run control, is done and receives no carry. R11-INTAKE-R10-RESIDUE is the live consumer of this group. It shares merge_train.py and holds round-10 residuals that no live round-10 group owns, for the round-11 architect to re-home. Carry: R11-INTAKE-R10-RESIDUE
- Carry 3: **The three instruments' guides and decision 0017 owe this part's surface:** remerge_main.sh's `--head-repo`, the `[OUTSIDE]` block class, and carry 29's sentence that no tool of ours pushes a fork head to a branch of origin. That sentence is true of this part: the fork head is fetched to `refs/remotes/pull/<pr>/head` only. The decision is policy, an owner-approved text, and not written by a fixer. Carry: R10-PROCESS-SLIM
- Carry 4: **Carry 14, round 3:** `_post_agent_approval`'s body under a bare `--mandate` id reads "under <id>", which `MANDATE_CITE` does not read as a citation. Whether it should say "mandate comment <id>" for our own heads is the train's wording, unchanged here. R10-GATE-DEFER-BARRIER, which last held merge_train.py's approval path, is `carries-open` and receives no carry; R11-INTAKE-R10-RESIDUE is the live consumer of this group (it shares merge_train.py) that holds round-10 residuals no live round-10 group owns, for the round-11 architect to re-home. Carry: R11-INTAKE-R10-RESIDUE
- Carry 7: **merge_pr.sh app mode merges a cross-repository head without asking outside.py's contract** (the verdict at 763c689d, first finding): `gates` returns before `head_is_ours` unless the mode is owner, and nothing calls `check`. Established by the reviewer's read and the file's own passing case `null control: app mode on a cross-repository head passes the gates`; not run end to end, no fork pull request exists. Not built in this round, which the dispatch scopes to the repair; it is this group's seam and waits on the orchestrator's cut of a further part. Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE
- Carry 8: **`Train.fork_head` executes the checkout's tools/pr/outside.py before `outside_is_mains` compares it with origin/main's blob** (the verdict's second finding, by reading, no perturbation run). A checkout whose copy answered "ours" never reaches the comparison. Same standing as carry 7. Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE
- Carry 9: **`Train.land` asks the outside contract only when the base is main** (`if self.real:`); on a `batch/` base the pinned merge runs without it (the verdict's third finding, read, not run). Same standing as carry 7. Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE

## Friction

- prepr-ci-predict: unenforced: Carry 5: `tools/pr/ci_predict.py` runs the base's `carry_audit.py` in a `--shared` clone that holds no `origin/handoff/audit-r<N>-roster`. A `Carry:` to a group that lives only on the round's roster branch therefore reads as a bad destination, while `pr-contract.yml` fetches that ref before the same check. It reproduced at this head: the prediction refused two destinations that main's own `carry_audit.py`, run on a main worktree with `--branch`, routes (`7 routed, 0 unrouted, 0 bad destination(s)`). As the last seat did, this seat gave the clone the ref CI fetches: a local branch `handoff/audit-r10-roster` at `origin/handoff/audit-r10-roster`, pushed nowhere. The predictor owes the fetch. R10-SEAT-SCRIPT-OUTPUT is done and receives no carry; R11-PRE-HANDOFF-BOOKKEEPING is the live consumer that owns the handoff's carry decision (`tools/audit/carry_audit.py` is in its files). Carry: R11-PRE-HANDOFF-BOOKKEEPING
- brief: cost: Carry 6: the first dispatch asked for code against an interface part 1 had not published. That made the two calls a guess and cost this repair round. Read from part 1's published head here. Carry: dismissed: resolved in this round, the interface is read from e216e6c09878
- fixer-step-6: cost: Carry 10: a sibling part merged under this branch brought four self-test steps red that this part's body never ran, because its Figures listed only the files this part edits. One review round. This round ran every step the closures diff names. Carry: dismissed: answered in this body's Red checks; the round's brief now states the rule
