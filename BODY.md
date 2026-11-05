R10-BODY-CONTRACT: the body contract at the head (V115), roster ref, review trailers, fold grammar, closed-destination refusal with its consumers, dismissal pointer, refused-body keep, carry control lint, and the orchestrator's pre-merge carry fold. Card 7 (generated figure block) is stopped on measured missing preconditions and stays a Forward-carry item.

## Head

`ed10a06e9ca9c1e5f02831b17d4e7b8531d274f2`, with origin/main `79f765e6b2e0f97e61b57d7b605fc4e70b4bf21e` merged (taken `date -u` 2026-11-05T08:30Z); `tools/pr/prepr.sh` was rerun after that merge.

## Mutation proof

Each arm was red first where it can be red on the unchanged code, and each has a mutant that turns it red:
- V115 tree revision: dropping `BRIEF_LINT_TREE_REV=$head` (the `# mut:contract` line) fails the `treerev` assertion in `body_patch.sh --self-test`.
- Roster ref: removing the argument (`# mut:rosterref`) fails the roster-ref arm.
- Trailers: deleting the new alternation fails `TRAILER reads 'Round: 3'` and `'bus-nonce: abc123'`.
- Dismissal pointer: forcing the pointer branch off fails `Carry: <done group> | dismissed: <reason> routes`.
- Closed destination: testing against `DONE_STAGES` instead of `roster_lib.CARRY_CLOSED`, or listing every live group, turns the closed-group arms red.
- Fold grammar: disabling the unanswered-fold test fails the "(a)-(d) answered, (e) named" arm.
- Keep ref: replacing the `# mut:keep` calls fails all four refusal arms.
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

`none`: `tools/pr/prepr.sh` ran clean on this head. An earlier run, before the budget payment and the INERT classification, refused `closures` (`tests/entities.py` needs `paho` in this sandbox, an environment gap), the two policy-doc budgets, and a classification line for `carry_fold.py`; each was repaired (budget payment, `ci_predict.py --apply-inert`), and CI settles the `closures` table. The cheaper detector for the budget refusals was `policy_lint.mjs --budgets`, run locally.

## Forward-carry

Not built here; each is stated once, and the dispatch seat lands them in the roster:
- Card 7, every body figure from a generated block: the carry's own preconditions are missing, measured above. No workflow edits a body on synchronize; `features_block.py` renders no figure block (it runs test blocks); `figure_lint.mjs` refuses by design to execute body commands, so a renderer would need an owner ruling on running PR-authored commands in `pr-contract`, and a new block format and marker. The carry also touches the PR template and `checkPrBody` (owner review at merge). Carry: R10-BODY-CONTRACT (Carry 11)
- A1, `rosterIssues()` default reading `dev/programme/rosters`: an owner call, because enabling it refuses `carry-1795.json` (issue 1795 is covered by live group R9-UX-6); resolving it moves 1795 into R9-UX-6 and deletes the carry file. Carry: R10-BODY-CONTRACT (Carry 12)
- Fold grammar scope: only the issue body is read, not its comments; `Fold (x): Carry:` is checked for a well-formed destination, not against the roster; wired into `check --body` only, not `pr`. Carry: R10-BODY-CONTRACT (Carry 13)
- Hot files: `body_push.sh` is also edited by open PR 3221 (receipt trailer); this diff adds only new functions and one call per refusal path. Carry: R10-BODY-CONTRACT (Carry 14)
- Carry control lint narrowing: the lint skips the 15 legacy carry files named in `LEGACY_CONTROL_FILES` in `brief_lint.mjs` (their controls name no path or cite unresolvable paths); repairing them rewrites other groups' controls. The set is closed and shrinks as those carries are re-measured. Carry: R10-BODY-CONTRACT (Carry 15)
- Policy files drafted here, merging on the owner's approval: the one sentence in `dev/governance/roles/fix-review.md` and `judge.md` (#2438 (ii)), and the template and contract are untouched. Carry: dismissed: nothing owed beyond the owner's review at merge

## Friction

- finding-propagation: unenforced: a roster-wide default (`rosterIssues()` with no argument) cannot be switched on while a carry collides with a live group, and nothing flags the collision until the default changes. Carry: R10-BODY-CONTRACT (Carry 16)

## Approval

Not yet given. This diff touches two policy files, `dev/governance/roles/fix-review.md` and `dev/governance/roles/judge.md` (one sentence each, #2438 (ii), with spent prose trimmed to stay under the token caps); the owner's approving GitHub review at merge is the approval, and it waits for that review.

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
