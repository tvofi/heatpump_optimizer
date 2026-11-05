R10-BODY-CONTRACT: the body contract at the head (V115), roster ref, review trailers, fold grammar, closed-destination refusal with its consumers, dismissal pointer, refused-body keep, carry control lint, and the orchestrator's pre-merge carry fold. Card 7 (generated figure block) is stopped on measured missing preconditions and stays a Forward-carry item.

## Head

`ec14238f0d0c2491d30950b78c1539815bc3b693`, with origin/main `b707d89329c746c870d07e0b1725e644874078dc` merged (it had not moved since the previous merge; `git log HEAD..origin/main` is empty, so the `tools/pr/prepr.sh` run at this head is the only one needed). Repair round 2 of #3227 after a blocking review at `a52354e6`.

Carry 11 to Carry 16 are the roster's carries of this group from the previous body (the Forward-carry items of that body); the new items under Forward-carry are the review findings this round did not fix.

## Mutation proof

Each arm was red first where it can be red on the unchanged code, and each has a mutant that turns it red:
- V115 tree revision: dropping `BRIEF_LINT_TREE_REV=$head` (the `# mut:contract` line) fails the `treerev` assertion in `body_patch.sh --self-test`.
- Roster ref: removing the argument (`# mut:rosterref`) fails the roster-ref arm.
- Trailers: deleting the new alternation fails `TRAILER reads 'Round: 3'` and `'bus-nonce: abc123'`.
- Dismissal pointer: forcing the pointer branch off fails `Carry: <done group> | dismissed: <reason> routes`.
- Closed destination: testing against `DONE_STAGES` instead of `roster_lib.CARRY_CLOSED`, or listing every live group, turns the closed-group arms red.
- Fold grammar: disabling the unanswered-fold test fails the "(a)-(d) answered, (e) named" arm.
- Keep ref: replacing the `# mut:keep` calls fails all four refusal arms.
- Repair 1 (bare array): the merged marker comment is above `policy_lint`; `python3 -I tools/audit/seat/bare_array.py --check` was red at `a52354e6` (names `body_patch.sh:146`, rc 1) and is rc 0 now. The pre-existing `bare_array.py` self-test already holds the mutant of the same shape (a comment between the marker and the line).
- Repair 2 (closing keywords): thirteen new arms in the carry_audit self-test, one per form (the nine keywords close/closes/closed, fix/fixes/fixed, resolve/resolves/resolved; the colon spelling; the issue-URL, owner/repo and GH- reference shapes), were ten red on the old two-keyword `CLOSES` before the regex change (failing test first). Mutants, each run: back to the two keywords (10 failed); dropping fix (5), resolve (4), closed (1), the URL shape (1), the owner/repo shape (1), the GH- shape (1).
- Pins for the review's surviving mutants, each run red against its mutant: `fold_rc = 0` in `check` (2 failed), dropping `| fold_rc` on the roster path (1) and on the empty path (1) through three end-to-end `check --body` arms; `dests.pr_group = pr_group_of(...)  # mut:branch` replaced by `pass` (1 failed, an end-to-end `check --branch` arm); `carry_fold.py` `if bad:` to `if False:` (1 failed, a body with one good and one done destination writes nothing); `treeListing(process.env.BRIEF_LINT_TREE_REV, cwd)` to `treeListing(undefined, cwd)` (`TREEREV VACUOUS`, through `trackedFiles(dir)` with the variable set and unset); stripping `<!--.*?-->` from `fold_problems` (1 failed).
- Carry 6 (`--branch`): making `pr_group_of` return None fails `branch fix/r10-pr resolves to the PR group R10-PR` and the `-pr` suffix arm (2 failed, run this pass).
- Carry 9 (control lint): changing `if (!names) {` to `if (false) {` makes `assertCarryControl` print `CONTROL VACUOUS` for both `the FUTURE-STATE section 2 figures` and the bare statistic (run this pass).
- Carry 8 A2 (`carry_fold.py`): replacing the post-fold `landed` call (`# mut:postfold`) with `[]` fails `an op that returned 0 but wrote nothing fails after the fold, naming the id` (1 failed, run this pass).

## Null control

- V115: a path the head deletes refuses with the revision set; the checkout listing differs from the head listing.
- Folds: all five answered is accepted; no `Fold (x):` line is accepted unchanged; `Fold (e): dismissed:` with no reason is refused.
- Dismissal: `Carry: <done group>` alone is still refused; an unknown token with `| dismissed:` is refused.
- Closed destination: a live after-edged group and a not-yet-started group are accepted as before; branch `fix/r10-nothing` resolves to no group (the refusal then says so).
- Control lint: a control naming `dev/audit/harnesses/agreement_two_pr.mjs` passes; a control in a legacy carry file (`carry-201.json`) with no path passes (the narrowing).
- carry_fold: the same body folded twice writes nothing the second time; a done destination is refused before any write.
- Keep ref: a successful push leaves no keep ref.
- Closing keywords: `Mentions #7`, `Fixing #7` and `unfixes #7` close nothing and owe no fold answer; `check --body` with the fold answered is accepted; `check` without `--branch` still prints `valid targets: unknown`.

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test | tail -1` (carry_audit self-test; the count is its own line)
- `python3 -I tools/audit/seat/carry_fold.py --self-test | tail -1`
- `bash tools/audit/seat/body_patch.sh --self-test | tail -1`
- `bash tools/audit/seat/body_push.sh --self-test | tail -1`
- `node tools/policy/brief_lint.mjs | tail -3` (the `CONTROL ok` line and `TOTAL: 0 error(s)`)
- `python3 tests/structure.py | tail -1` (ratchet passed; no budget raised)
- `node tools/policy/policy_lint.mjs --budgets | grep briefs/` : `fix-review.md` and `judge.md` sit under their token caps; the added sentence was paid for by trimming spent prose (one motivation sentence in `fix-review.md` step 2, shorter wording in `judge.md`), no cap raised.
- Card 7 precondition measurements: `grep -nE "pulls/.*PATCH|gh pr edit|update_pull_request|body_patch" .github/workflows/*.yml` finds only governance.yml's self-test steps, so no workflow rewrites a PR body on synchronize (pr-contract.yml is `workflow_call` only); `grep -nE "^def " tools/audit/seat/features_block.py` lists block/through/run, a runner of `tests/features.py` blocks, not a figure renderer; `sed -n 14,20p tools/policy/figure_lint.mjs` states it "does not execute one character of the body".
- Closed-destination consumers: `grep -n "HEAD_REF" .github/workflows/pr-contract.yml` shows the step now passes `--branch "$HEAD_REF"`.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` OK. No golden was touched; claim files are byte-identical to origin/main (prepr step).

## Red checks

Read against the check runs of the PR head `a52354e6e441236ec0b63fa49fd303900c64f6cf`, the last head CI graded (the final head below has no run until it is pushed; CI is the authority for it). Merge base: `b707d89329c746c870d07e0b1725e644874078dc` (`git merge-base origin/main HEAD`). Every concluded red, all pages:

- `governance / instrument-self-tests` (job 127227661299), step 27 `Refuse a bare array expansion in a set -u script`: this diff. `body_patch.sh:146` carried a comment between the `# never-empty:` marker and the `policy_lint` line, which `bare_array.py` does not accept. Repaired here (marker and reason on one comment line directly above the line); `bare_array.py --check` rc 0 at this head.
- `tests / fast (3.14)` (job 127227966145), step `Run the suite`: this diff, the same line, read by `tests/entities.py` (`no tracked tools/**/*.sh script expands a bare "${array[@]}"`). `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head: `ALL 2631 ENTITY CHECKS PASSED`.
- `pr-contract / pr-contract` (jobs 127240182833, 127241211745, 127242351411), step 10 `Check the body against the contract`: this body, which said `none` and answered neither red above. Answered here.
- `gate` (jobs 127240629116, 127241637011, 127242766124): the aggregate of the two required reds above; it follows them.
- `governance / delivery-status` (job 127227661367): inherited. It grades main's ledger, red on the base ancestry (merge base `b707d89329c746c870d07e0b1725e644874078dc`): overdue delivery rows of other merged PRs, not this diff's. This diff touches `.github/workflows/governance.yml` for self-test steps only.
- `tests / nightly-status` (job 127227661278): inherited. It reads last night's run of main (merge base `b707d89329c746c870d07e0b1725e644874078dc`): the nightly slow-job replay cost-band failure, carried by R10-REPLAY-COST-BUDGET. This diff does not touch that lane.

Root cause of the two own reds (`defect-root-cause.md`, red-check trigger): the last edit to `body_patch.sh` (the inserted comment line) was made after the prepr run that the previous body cited, and `tools/pr/prepr.sh` did not run `bare_array.py --check` at all. The cheaper detector was `python3 -I tools/audit/seat/bare_array.py --check` (seconds). Countermeasure built: `privacy_line` in `prepr.sh`, step 3f7, now runs it first (one added command in an existing step) and refuses with its last line.

## Forward-carry

Not built here; each is stated once, and the dispatch seat lands them in the roster:
- Card 7, every body figure from a generated block: the carry's own preconditions are missing, measured above. No workflow edits a body on synchronize; `features_block.py` renders no figure block (it runs test blocks); `figure_lint.mjs` refuses by design to execute body commands, so a renderer would need an owner ruling on running PR-authored commands in `pr-contract`, and a new block format and marker. The carry also touches the PR template and `checkPrBody` (owner review at merge). Carry: R10-BODY-CONTRACT (Carry 11)
- A1, `rosterIssues()` default reading `dev/programme/rosters`: an owner call, because enabling it refuses `carry-1795.json` (issue 1795 is covered by live group R9-UX-6); resolving it moves 1795 into R9-UX-6 and deletes the carry file. Carry: R10-BODY-CONTRACT (Carry 12)
- Fold grammar scope: only the issue body is read, not its comments; `Fold (x): Carry:` is checked for a well-formed destination, not against the roster; wired into `check --body` only, not `pr`. Carry: R10-BODY-CONTRACT (Carry 13)
- Hot files: `body_push.sh` is also edited by open PR 3221 (receipt trailer); this diff adds only new functions and one call per refusal path. Carry: R10-BODY-CONTRACT (Carry 14)
- Carry control lint narrowing: the lint skips the 15 legacy carry files named in `LEGACY_CONTROL_FILES` in `brief_lint.mjs` (their controls name no path or cite unresolvable paths); repairing them rewrites other groups' controls. The set is closed and shrinks as those carries are re-measured. Carry: R10-BODY-CONTRACT (Carry 15)
- Issue-side fold spellings: `FOLD_LINE` reads `Fold (x):` with a lowercase letter and the colon straight after the parenthesis, so an owner's `**Fold (a)**:` or `Fold (A):` gets no fold read; the live spelling could not be confirmed. Carry: R10-BODY-CONTRACT
- Dismissal pointer grammar: `seg_dests` accepts `,` and `;` as well as `|` after the group, wider than the documented `Carry: <GROUP> | dismissed:`; align the docs or narrow the regex. Carry: R10-BODY-CONTRACT
- The `Round:\s*\d` trailer reads any item line opening `Round: <digit>`, so a finding written that way is read as a trailer; the null control covers only `Round:` with no number. Carry: R10-BODY-CONTRACT
- Dropping `--branch "$HEAD_REF"` from `pr-contract.yml` is unpinned: nothing tests the workflow text, and the effect is only the refusal printing `valid targets: unknown`. Carry: R10-BODY-CONTRACT
- Policy files drafted here, merging on the owner's approval: the one sentence in `dev/governance/roles/fix-review.md` and `judge.md` (#2438 (ii)), and the template and contract are untouched. Carry: dismissed: nothing owed beyond the owner's review at merge

## Friction

- finding-propagation: unenforced: a roster-wide default (`rosterIssues()` with no argument) cannot be switched on while a carry collides with a live group, and nothing flags the collision until the default changes. Carry: R10-BODY-CONTRACT (Carry 16)

## Approval

Not yet given. This diff touches two policy files; the owner's approving GitHub review at merge is the approval, and it waits for that review. The three-dot diff changes three places in `dev/governance/roles/fix-review.md` and five in `dev/governance/roles/judge.md` (#2438 (ii)); each, old to new:
- `fix-review.md` step 2: removed "A fixer who measures with a harness they wrote is measuring themselves." (token-cap payment; the rule "Measure with the finder's harness" stays).
- `fix-review.md` step 14: "On a raise, judge each payment the body lists and hunt one it missed" became "On a raise, judge each listed payment and hunt one it missed" (token-cap payment).
- `fix-review.md` closing: "from the fourth, `fixer.md` owes a re-cut, not a repair." became "from the fourth, `fixer.md` owes a re-cut." (token-cap payment).
- `fix-review.md` closing, ADDED (the policy change): "A ruling naming a destination stage states it as a `Carry:` marker."
- `judge.md` opening: "You do not trust the finders or the verifiers; you re-measure." became "You trust neither finders nor verifiers; you re-measure." (token-cap payment).
- `judge.md` step 3: "Compare the metric definitions the finder and the verifiers wrote. Where they measured different things, mark the votes `not comparable` and decide on your own measurement." became "Compare the metric definitions; where they differ, mark the votes `not comparable` and decide on your own measurement." (token-cap payment).
- `judge.md` step 7: "`unreproduced` is no kill and no pass: the round is not dry until it is re-measured or refuted." became "`unreproduced` is no kill, no pass: re-measure or refute it before the round is dry." (token-cap payment).
- `judge.md` closing, ADDED (the policy change): "A ruling naming a destination stage states it as a `Carry:` marker."
No `*budget*` file changed; no cap was raised (`fix-review.md` 137/140 lines, 2440/2451 tokens; `judge.md` 29/30, 467/469).

## Brief carries by number

- Carry 1 (`--roster-ref` on the contract arm): built.
- Carry 2 (card 7): stopped, preconditions missing; under Forward-carry.
- Carry 3 (V115): built.
- Carry 4 (`bus-nonce:`, `Round:`): built.
- Carry 5 (`Fold (x):`): built, scope limits under Forward-carry.
- Carry 6 (closed destination): built, `pr-contract.yml` passes `--branch "$HEAD_REF"`, resolved to the group by `pr_group_of`.
- Carry 7 (`Carry: G | dismissed:`): built.
- Carry 8: A2 built as `tools/audit/seat/carry_fold.py` (indexed in INSTRUMENTS.md, self-test wired in governance.yml); A1 kept as a Forward-carry item.
- Carry 9: built with the narrowing above; sentence (ii) drafted.
- Carry 10 (keep ref): built.
