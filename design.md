# R10-OUTSIDE-CONTRIBUTOR-CYCLE design note, round 2: adoption on our machine is the gate; a fork changes no grader unread

- **Base:** 14f227c5bd0eb80855b21055cc668857a5f820b4 (the dispatch's base, `origin/main` when written). Every line number below is read at that commit. No predecessor (`after` is empty). Roster read at origin/handoff/audit-r10-roster c90f06340a.
- **Revises** 79ffef7edb4a5ef1d80c29cc4ac18043c878f729 against the verdict at fbfe6a13 (which read dca53dc6; tools/audit/seat/merge_train.py moved again since, so its numbers are re-read here, not copied). The seam is unchanged.
- **No finder harness: owner report.** The owner's ruling of 2026-11-12 (triage batch 238, entry P714): "Implement a mechanism that allow baikanfans PRs to be accepted as is as long as they follow all our conventions and rules and have a valid merge verdict (the reviewer may also be run by bankaifan). Merges with main and codeowner approvals remain in our machinery even for such PRs." It supersedes the retired group R10-PR-CONTRACT-OUTSIDE; decision 0017 says so.
- **Built whole in round 10.** Section 6's parts are a build order. Nothing is deferred to a later round.

| verdict point | answered in |
|---|---|
| 1. a fork controls its own workflow files | section 2 (A): adoption runs the whole contract from `origin/main`; pr-contract is the early signal |
| 2. unowned graders | section 2 (B): the three-class rule, what it returns at the base, the failing test's route |
| 3. `carry` admits forgeable bot subjects | section 2 (C): on a head no branch of ours holds, only an automatic merge of main carries |
| 4. citations and the pinned pathspec | every section re-anchored; tools/audit/seat/remerge_main.sh by path; pathspec mechanism in section 2 (D) |

## 1. Owning seam

tests/seam_map.json names no file under tools/, so `fixer.md` step 17 decides: the module that computes a fact owns it. "Is this an admitted outside pull request, and which class is each path it changes" is one concept with three readers. It keeps **one owner: a new module outside.py under tools/pr/**, with the allowlist beside the policy as data. Callers, hunk only: tools/policy/policy_lint.mjs (`checkPrBody`'s author arm, :7131-7133), .github/workflows/pr-contract.yml (one step), tools/audit/seat/bus.sh (one new subcommand ending in `push_verdict`, :277), and in part 2 tools/audit/seat/merge_train.py. **tools/pr/app_approve.sh is edited, in `carry` only** (:289-495): what carries is that file's own fact, and the edit asks git which heads are ours, not outside.py who the author is. `VERDICT_AUTHORS` (:116) stays the approver App alone, so `posted_verdict` (merge_train.py:3384), `build_queue` (:3314), `add_verdict` (:4181), orchestrator_tick.py:647 and proof_watch.py:88 learn no new author.

## 2. Shape

```
contributor (fork)             our dispatch seat (our machine)              unchanged machinery
push head H; body; row   --->  ci.yml on H: early signal only
comment: Fix review: merge H
         review-commit: C --->  bus.sh adopt <pr> <comment id>
                                (A) outside.py + allowlist + CODEOWNERS read
                                    with git show origin/main:<path>;
                                    full contract over merge-base(origin/main,H)...H
                                (B) class R -> refuse; class O -> owner's
                                    APPROVED review at H, else refuse
                                fetch C from the fork URL the pulls API names
                                push_verdict gates -> review/<pr> on origin
                                bus.sh confirm  ------------------------->  hpo-approver comment
                                                                            app_approve.sh (C), train, ruleset
```

**(A) Adoption is the authoritative gate (point 1).** .github/workflows/ci.yml:34-35 triggers on `pull_request`, so a fork head runs the workflow files of its own merge ref, and pr-contract's base pin is a step inside one of them (.github/workflows/pr-contract.yml:100-136). Green there proves nothing about a head that edited .github/. So the adopt subcommand, on our machine, materialises outside.py, the allowlist, .github/CODEOWNERS and tools/audit/carry_audit.py from `origin/main` with `git show` into a throwaway directory, never from the seat's checkout and never from the head, and runs the **whole** outside contract before `push_verdict`:
1. allowlist: the pull request's author and the comment's author match one entry by login, numeric id and type `User`, both read from the API;
2. the head repository's full name differs from ours (cross-repository);
3. the path rule (B) over `git diff --no-renames --name-only $(git merge-base origin/main H)...H`, three-dot, with H fetched from refs/pull/<pr>/head;
4. the verdict binding and the bus gates of round 1, unchanged: first line passes `verdict_sha` (bus.sh:186), verb `merge`, SHA equal to the live head; VERDICT.md's first line byte-equal to the comment's; C fetched from the clone URL the pulls API reports, read with plumbing only, regular files under a size cap; evidence names the head (bus.sh:286-288); `ref_privacy.py body-lines` (:299); `carry_gate` (:247) from main's copy; `survivor_list.py check` (:304).

No fork code is executed on our machine: every step reads git objects or the API. pr-contract runs the same outside.py as an **early signal** for the contributor; it gates nothing we rely on. **Consequence:** policy and budget paths are class R, so `policy_approval_due` (merge_train.py:2602) is never due on an adopted head and `policy_approve` (:2644) never posts there.

**(B) The grader rule (point 2): default deny, three classes.** A fork changes no path the gate executes or reads unless the owner read that change at the head. outside.py classifies every changed path, first match wins:

| class | paths | consequence |
|---|---|---|
| **F** free | custom_components/, blueprints/, README.md, docs/ outside a CODEOWNERS line, and the one row dev/programme/delivery/<its own number>.md | CI at the head plus the contributor's review. **No owner read**: decision 0017 states this limit in those words |
| **R** refused | .github/, tools/, .claude/, .cursor/, `POLICY_GLOBS` and `POLICY_DIRS` (policy_lint.mjs:240, :305; includes the allowlist), any `*_budgets.json`, tests/closures.json, tests/golden/ (fixtures and both claim files), tests/mutation_ledger/, every `GATE_FILES` entry (tests/closure.py:470), every root file but README.md, and **any path in no class** | adoption refuses; the fix stays with our fixer as today |
| **O** owner-read | every other path under tests/, and any CODEOWNERS-matched path not in R | adoption refuses unless the reviews API shows an APPROVED review by the owner's numeric id with `commit_id` equal to H |

What the rule returns at the base: `git ls-files tests` is the grader population; R takes tests/closures.json, the budget files, tests/golden/ and tests/mutation_ledger/; the rest is O, which holds all of `closure.selectable_scripts()`, tests/structure.py and tests/entities.py included, owned or not. .github/CODEOWNERS:151-195 owns only part of it and has no line for custom_components/, tools/pr/, tools/audit/seat/ or policy_lint.mjs; the rule does not depend on that file being complete. No recorded closure separates a product test from a repository grader (tests/structure.py's closure in tests/closures.json reads only tests/ and custom_components/, like tests/edge.py's), and added lines can lower a script as well as deleted ones, so no mechanical filter is offered in place of a read.

**How a fork fix adds its failing test:** as an edit to an existing selectable script, class O. The owner reads that test diff and approves at H; adoption checks the review, GitHub keeps it across the later main merge (the ruleset fixture tools/ci/fixtures/ruleset/ruleset_23698884.json has `dismiss_stale_reviews_on_push` false), and (C) keeps any later commit from riding on it. This is the owner's "codeowner approvals remain in our machinery", extended on a fork head from the CODEOWNERS lines to every grader. Cost, stated: one owner read of the test diff per outside fix. Not acceptable as is, and said so in the guide: a fix that adds a tracked file outside docs/ (tests/entities.py wants it classified in tests/closures.json or tests/closure.py, both R), moves a golden, or needs a budget edit.

**(C) Carry on a head that is not ours (point 3).** tools/pr/app_approve.sh's `carry` admits, between the verdict SHA and the head, a merge (:313), a branch commit of unchanged content (:360-363) and a commit under a bot subject (:364-420, `bot_author` :237, `bot_paths` :245), and :233-236 says of subject and author "git metadata anyone can write". Sound while only our identities push the head; a fork pusher writes both, and the four autofix jobs skip on a fork (tests.yml:1142, :2404, :2676, :2935), so no legitimate bot commit exists there. Change: `carry` asks `git ls-remote --heads origin` whether the head is the tip of a branch of our repository. If it is not, every non-merge commit in the range refuses, bot and `ci:` subjects included, and only the existing merge arm (automatic, driver output only) carries. One function, read by both callers: `approve` (:549-558) and the `--carry` arm (:741) that `admit_verdict` calls (merge_train.py:3359). The train is not edited for this and cannot skip it. This is what binds the verdict to the head: the ruleset keeps approvals across a push (`require_last_push_approval` false), so only `--match-head-commit` (merge_train.py:2935, in `land`) and `admit_verdict` (:3341) hold the line. remerge_main.sh:42's claims-drop commit never arises on a fork head: claim files are R, so the branch claims nothing.

**(D) Carriage, the allowlist, the pin (point 4).** The contributor's only signature is GitHub's authentication of the comment's author; no key, no nonce. The allowlist is a JSON file, outside_contributors.json under dev/governance/ (policy by `POLICY_DIRS`, plus a new CODEOWNERS line): login, numeric id, date, decision number. **It merges empty; the owner adds the entry once every part is on main**, so no build order opens a window. pr-contract.yml:111-133's pinned pathspec already holds `tools/pr/*.py`, so outside.py is restored from the base with no pathspec growth; the pathspec matches programs, not data, so outside.py reads the allowlist and CODEOWNERS with `git show <pinned sha>:<path>`, the same call adoption makes with `origin/main`. pr-contract's API step (:206) adds the author's id and type and the head repository's name; on admission it passes one flag to policy_lint.mjs that relaxes the author arm and nothing else.

**(E) Merges with main stay ours (part 2).** `recarry` (merge_train.py:2690) builds its worktree from `origin/{br}` (:2726) and runs tools/audit/seat/remerge_main.sh (:2735), which fetches and resets to `origin/$BR` (:33-34) and pushes to a hard-coded repository (:49); `freeable` (:1866) reads `origin/{br}` too (:1879). For a head outside.py reports cross-repository, the worktree comes from refs/pull/<pr>/head and the push target (head repository, head branch) from the pulls API. The merge is automatic or the train parks naming the fork; it never resolves. Part 2 also makes `_post_agent_approval` (:2576, the `gh pr review --approve` at :2588) refuse on a cross-repository head.

**Documents.** Decision 0017 under dev/governance/decisions/ (highest at the base is 0016; re-derive at the merge base): the three classes, the F limit, the validity limit (form, binding and CI are checked; the review's honesty rests on the allowlist). docs/CONTRIBUTING.md (absent at the base; tests/closure.py:275 classifies docs/). dev/governance/roles/fix-review.md gains one section for an outside reviewer: steps unchanged; publication is the fork branch and the two-line comment; a head that moves by anything but our main merge voids the verdict.

**Invariants kept.** No secret reaches a fork run. `app_approve.sh --self-test` still prints "REFUSE: a merge verdict from a CONTRIBUTOR outside the allowlist" (:1110). Held fork runs are approved by hpo-runs after a read of the diff, unchanged.

## 3. Alternatives

- **Trust pr-contract's base pin** (round 1). Lost: the pin is a step in a file the fork's merge ref supplies; one caller (CI) would hold a rule the bus must hold.
- **A base-graders CI job** restoring tests/ from the base and re-running the suite. Lost: it proves the product passes main's graders at this head and says nothing of the lowered copy that merges; it needs a second full run per push; and its result is again reported by fork-supplied workflow files.
- **Additions-only edits to test scripts, no read.** Lost: an appended early exit or rebinding lowers a grader with no deleted line; `git diff --numstat` cannot tell.
- **A CODEOWNERS line for tests/.** Lost: it would demand the owner's review on every pull request of ours; the class-O check binds fork heads only, in the one module that knows them.
- **Pass a strict flag from the train to `--carry`.** Lost: two callers must remember it, one in a hot file; a git fact read inside `carry` cannot be forgotten.
- **Add the contributor to `VERDICT_AUTHORS`, or issue a key.** Lost as in round 1: five readers assume one Bot id, and the evidence gate (app_approve.sh:563-661) wants a path on our machine.

## 4. Sibling sites

`git grep -n -E "bot_paths|bot_author" -- tools`: the carry arms of (C) and policy_lint.mjs's `AUTOFIX_BOT_COMMITS`, which grades our own heads and is unchanged. `git grep -n -E "VERDICT_AUTHORS|verdict_allowlist\(" -- tools`: the readers of section 1, none changes. `git grep -n -F 'origin/{br}' -- tools/audit/seat` and `git grep -n -F 'origin/$BR' -- tools/audit/seat`: `freeable`, `recarry` and remerge_main.sh, all part 2. `git grep -c -E "hpo-author\[bot\]|app/hpo-author" -- tools .github tests`: author gates are policy_lint.mjs (changed), tools/pr/cancel_superseded.py (ci.yml:148 skips it on a fork) and tools/audit/seat/pr_cap.py (the fixer states what an outside author gets); tools/audit/seat/outside_intake.py classifies and is not a gate; the rest name the App as our pusher. `git grep -n "pull_request_target" -- .github`: no new one is added.

## 5. Evidence, by file

- **outside.py self-test** (new; a step of governance.yml's `instrument-self-tests`, registered in tools/ci/selftest_closures.json): admitted for login+id on a cross-repository head; refused for another id, a same-repository head, type Bot; one fixture per R line of (B) and one unclassified path, each refused; an O path refused without the owner's review, refused with a review at another commit or by another id, admitted with it at H; every `closure.GATE_FILES` entry and every `*_budgets.json` in `git ls-files` classifies R (pins the rule to the enumeration, so a new gate file cannot fall into F). **Null control:** remove the allowlist entry and the admitted case flips. Mutation targets: the id comparison, the cross-repository comparison, the default-deny fall-through, the `commit_id` comparison.
- **bus.sh self-test** (`self_test`, :1017): an adopted-form verdict on a head touching each R class refuses, with a working tree whose own outside.py is stubbed permissive (proves main's copy ran); plus round 1's cases (unlisted commenter, SHA not the head, `blocked`, VERDICT.md differing, symlink entry, carry-gate and survivor failures) and the success case writing `review/<pr>` with the provenance line and a dispatch record under the reviewer name outside:<login>. Mutation targets: the `git show origin/main` source, the three-dot range, the two first-line comparisons.
- **app_approve.sh self-test** (fixture at :874-1000, origin a local bare repository): a `ci: re-record closures` commit by the bot's email over tests/closures.json, and a `ci: pin killed mutants` commit, each **carry** when the head is also a branch tip and **refuse** when it is only refs/pull/7/head; an automatic merge of main carries both ways. The failing-first case is the refusal, red at the base. Mutation target: the branch-tip test and each non-merge arm's refusal under it.
- **policy_lint.mjs** in-file tests beside :3982-3991: the outside author without the flag keeps today's message.
- **Part 2:** `merge_train.py --self-test` cases beside :5541-5584 for a fork head (worktree from the pull ref, push target from the API, park on conflict, agent approval refused); remerge_main.sh's `mut:` lines keep their kills.
- **Goldens:** none move; both claim files stay byte-identical. **Live check before handoff**, in the body: the item-8 run below, and which of our identities GitHub lets push a main merge to a maintainer-editable fork branch.

## 6. Build order, hot files, rulings

| part | content | files | order |
|---|---|---|---|
| 1 | outside.py, the empty allowlist, CODEOWNERS line, policy_lint flag, pr-contract step, the adopt subcommand, the `carry` edit, decision 0017, the guide, the fix-review.md section | bus.sh, app_approve.sh, policy_lint.mjs, pr-contract.yml; none hot | one pull request (1a and 1b of round 1 shared outside.py and cannot run beside each other) |
| 2 | (E): fork-head main merge, park reason, agent approval refused | merge_train.py (hot), remerge_main.sh | starts after R10-GATE-DEFER-BARRIER merges; shares no file with part 1 and may be built beside it |

The mechanism is live when the owner adds the allowlist entry, after both parts merge.

- **decision: owner.** Class O is read by the owner. The cheaper variant is a read by our fix-review seat scoped to the test diff; it changes who reads, not the mechanism.
- **decision: owner.** Whether an agent-posted owner approval may ever land on a cross-repository head; (E) builds "never" until ruled otherwise.
- **decision: owner.** Round 1 listed four further features (a budget lowering against a raise for a fork, automatic approval of held runs, sampled re-execution of adopted evidence, per-contributor scopes). None is needed for the requirement to hold whole and none is built; the owner names any that belong to the mechanism.
- **decision: orchestrator.** Ordering against designs sharing bus.sh and policy_lint.mjs (R10-STANDING-CONTRACTS-P2, r10-fly-standing-contracts) and governance.yml (r10-machinery-ratchets).

## 7. Carries

None received. Owed: part 2's roster entry behind R10-GATE-DEFER-BARRIER, written by the roster seat before part 1 merges (`finding-propagation.md`).

## Notes for the fixer

- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 1) - the allowlist id comes from the users API and is recorded as data; contributor text is data throughout.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 2) - read the fetched review commit with `ls-tree` and `cat-file` only; never check it out.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 3) - pr-contract.yml, CODEOWNERS, governance.yml, tools/ci/ and dev/governance/ are code-owned or policy: the body's Approval section and the owner's review at the head.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 4) - measure tests/structure.py and the machinery budgets before the first edit; a raise is asked of the owner before the push.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 5) - app_approve.sh's existing bot-carry fixtures push only refs/pull/7/head (`setpr`, :1000); they need a branch ref to stay carried, and that edit is the proof the new test reads the ref.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 6) - a failed or unreadable `ls-remote` refuses the carry; retry it through `retry_with` (:171) as the carry's fetch is.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 7) - adopt reads the comment by id through the API and refuses one that is not an issue comment of that pull request.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 8) - the evidence gate (app_approve.sh:563-661) wants a directory on our machine naming the head: adopt unpacks the evidence locally, and the live check shows app_approve.sh approving an adopted verdict end to end.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 9) - `checkPrBody` reads commits only in its Dependabot branch (:7125); confirm before claiming the flag relaxes the author arm alone.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 10) - the mandate approval and the owner's own review post from one account; class O's check reads the review at H, and R keeps `policy_approval_due` from ever posting there. State both in the self-test.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 11) - remerge_main.sh:49's push target comes from the pull request in part 2; if no identity of ours can push to the fork, try the update-branch API with the expected head SHA, and report to the owner before using a personal token.
- Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 12) - decision 0011 still cites tools/audit/app_approve.sh; 0017 corrects the citation, not 0011's history.
