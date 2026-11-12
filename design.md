# R10-OUTSIDE-CONTRIBUTOR-CYCLE design note: an outside verdict is adopted onto our bus, never trusted in place

- **Base:** 289c9b996832e50da330335deb3432836759ad2c (the dispatch's base). `origin/main` when written: 26072317b5556a2baa1ff562d8fbbc9588e2ba5c, which adds 311 lines to tools/audit/seat/merge_train.py and touches no other file this note cites. No predecessor (`after` is empty). Roster read at origin/handoff/audit-r10-roster 2eadb4e258.
- **No finder harness: owner report.** The evidence is the owner's ruling of 2026-11-12 (triage batch 238, entry P714): "Implement a mechanism that allow baikanfans PRs to be accepted as is as long as they follow all our conventions and rules and have a valid merge verdict (the reviewer may also be run by bankaifan). Merges with main and codeowner approvals remain in our machinery even for such PRs. The difference from today is that baikanfan may run the fixer-reviewer cycles themselves." The contributor's own reviewer is decided and not reopened here.
- **It supersedes** the retired group R10-PR-CONTRACT-OUTSIDE (ruling of 2026-11-06, "outside fixes merge via our own PR"); decision 0017 says so.
- **Two points the owner rules on** (section 6): what "merges with main" covers for a stale fork head, and whether a fork may edit tools/.

## 1. Owning seam

tests/seam_map.json names no file under tools/, so `fixer.md` step 17 decides: the module that computes a fact owns it. "Is this pull request an admitted outside pull request, and what may it not touch" is one new concept with three readers (the body contract, the bus, later the train). It gets **one small new owner: a module outside.py under tools/pr/**, with the allowlist beside it as data. Callers, hunk only: tools/policy/policy_lint.mjs (the author arm of `checkPrBody`, :7131), .github/workflows/pr-contract.yml (one step), tools/audit/seat/bus.sh (one subcommand that ends in the existing `push_verdict`). **tools/pr/app_approve.sh is not edited**, against the brief's expected files: its allowlist stays the approver App alone (`VERDICT_AUTHORS`, :116-117), which is what keeps tools/audit/seat/merge_train.py's `posted_verdict` (:3362) and proof_watch.py's `verdict_allowlist` (:88) unchanged.

## 2. Shape

**Today.** `checkPrBody` refuses any author but the App; a verdict exists only as a `review/<pr>` commit on our origin, pushed by `bus.sh push-verdict`, signed by `confirm` with the approver key and posted as hpo-approver; `app_approve.sh` and the train read only that App's comment.

**After.** The contributor's verdict is an *input* to our bus, checked by the same gates as ours, then re-issued by our approver identity. Nothing downstream of `confirm` learns a new author.

```
contributor (fork)            our dispatch seat                     unchanged machinery
push head; body + row  ---->  ci.yml: pr-contract (base-pinned)
                              outside.py contract: allowlist,
                              cross-repo, refused paths  -> green/red
push review/<pr> to fork
comment: Fix review: merge H
         review-commit: C --> bus.sh adopt <pr> <comment id>
                              outside.py verdict (binding)
                              fetch C from the fork URL, read as data
                              push_verdict gates -> review/<pr> on origin
                              bus.sh confirm  -------------------->  hpo-approver comment
                                                                     app_approve.sh, train, owner review
```

**(1) Carriage without keys.** GitHub's authentication of the comment author is the only signature the contributor has, and it suffices: the comment is by a numeric account id on the allowlist. The comment's first line is `Fix review: merge <head40>`, its second `review-commit: <40hex>`, naming a commit reachable from a branch of the fork whose tree is the bus's own shape (VERDICT.md plus evidence/, as `push_verdict` stages it, bus.sh:306-307). No nonce: a nonce binds a verdict to a reviewer we dispatched, and here the binding is the account id. A comment edited later changes nothing, because adoption pins the commit and the head by SHA.

**(2) "Valid", mechanically.** `bus.sh adopt` refuses unless all hold, each with its existing instrument:
- comment author's login, id and type `User` match an allowlist entry read from origin/main, and so do the pull request author's; the pull request is cross-repository (outside.py);
- first line passes `verdict_sha` (bus.sh:186), verb `merge`, SHA equal to the live head; VERDICT.md's first line is byte-equal to the comment's;
- the commit is fetched from the clone URL the pulls API reports for the head repository, never from text in the comment, into a throwaway repository; its tree holds only regular files (a symlink or submodule entry refuses) under a size cap;
- evidence names the head (bus.sh:286-288); `ref_privacy.py body-lines`; `carry_gate` (tools/audit/carry_audit.py `check`: every finding ends in a `Carry:` marker with a live destination); `survivor_list.py check`.

Then adopt mints the dispatch record with reviewer `outside:<login>`, appends the minted `bus-nonce:` line and one provenance line (login, id, comment id, commit) to VERDICT.md, and calls `push_verdict`. `confirm` runs as today, so the posted approver comment shows who reviewed. **What validity does not establish:** that the evidence is true. Form, binding and our own CI at the head are checked; the review's honesty rests on the allowlist, which is the ruling's content. Decision 0017 states this limit in those words.

**(3) The allowlist** is a JSON file, outside_contributors.json under dev/governance/: entries of login, numeric id, date and decision number. The id is load-bearing (a login can be renamed or re-registered). Only the owner edits it, by three independent locks: a new .github/CODEOWNERS line; `POLICY_DIRS` (policy_lint.mjs:305) already makes dev/governance/ policy; and both readers take it from the base (pr-contract's pinned check source, adopt's origin/main), so a pull request cannot add its own author. Removal reds the contributor's open pull requests at their next run.

**(4) pr-contract and the train.** pr-contract.yml's API step (:206) also reads the author's id and type and the head repository's full name; a new step runs outside.py from the pinned source and, on admission only, passes one new flag to `policy_lint.mjs`, which relaxes the author arm and nothing else. Every other body rule, `carry_audit.py` and the gate run exactly as for ours. The train needs **no edit to admit**: its verdict filter still sees the approver App. What it cannot do for a fork head is the main merge: `recarry` (merge_train.py:2668) and remerge_main.sh:33-49 assume `origin/<branch>` and push to our repository. Part 1 leaves that as a named park; part 2 fixes it.

**(5) Refused from a fork**, by outside.py over the changed-path list pr-contract already builds (:231): any `*_budgets.json` (part 1 refuses every edit, not only a raise); `POLICY_GLOBS` and `POLICY_DIRS` paths, which include the allowlist; .github/; tests/golden/claimed_drift.txt and card_claimed_drift.txt (a fork cannot record in the canonical environment, so a fix that moves a golden stays with our fixer); and, the designer's addition, tools/, .claude/ and .cursor/, because graders run from the base only until the merge, after which an unreviewed instrument edit is live. Version files are already refused for everyone (:441). Code-owned product and test paths stay allowed: the owner's review covers them, as the ruling says.

**(6) and (7) Documents.** Decision 0017 under dev/governance/decisions/ (the next free number at the base; re-derive at the merge base). A contributor guide at docs/CONTRIBUTING.md, which GitHub surfaces and tests/closure.py's `INERT` already classifies by prefix, so no closure edit. dev/governance/roles/fix-review.md gains one section: steps 1-15 bind an outside reviewer unchanged; publication is the fork branch and the two-line comment in place of `push-verdict`; no nonce; our dispatch seat runs `adopt` then `confirm`; a head that moves after the comment voids it. Also owed by the contributor, stated in the guide: the delivery row dev/programme/delivery/<N>.md in their own diff, a green tools/pr/prepr.sh before each push (the four autofix jobs skip on a fork: tests.yml:1142, :2404, :2676, :2935), and "allow edits by maintainers".

**Invariants kept.** No secret reaches a fork run. `app_approve.sh --self-test` still prints "REFUSE: a merge verdict from a CONTRIBUTOR outside the allowlist" (:1109): a contributor's comment alone never approves. Held fork runs are still approved by hpo-runs after a read of the diff (ruling of 2026-11-06, unchanged).

## 3. Alternatives

- **Add the contributor to `VERDICT_AUTHORS`.** Lost: that constant has five readers (merge_train.py:3292, :4169; orchestrator_tick.py:644; proof_watch.py:88; app_approve.sh:539), two in hot files, each assuming one Bot id and a `bus:` line; and app_approve's evidence gate (:563-661) wants a path on our machine, which a contributor's comment cannot name.
- **Give the contributor a signing key.** Lost: a second key ring and its revocation, against the brief's "none of our keys", for a signature that says no more than the account id already does.
- **A workflow on `pull_request_target` that validates and posts the verdict.** Lost: it runs base code with secrets on an event a fork triggers, a class this repository holds to one file (dependabot-automerge.yml); adopt on a seat's machine has the same checks with no new trigger.
- **The author rule inside policy_lint.mjs with its own allowlist reader.** Lost: bus.sh would need a second reader of the same rule; two implementations of one match is the duplicated shape `D7.md` asks to name one owner for.

## 4. Sibling sites

`git grep -c -E "hpo-author\[bot\]|app/hpo-author" -- tools .github tests` returns 14 files. Gates on a pull request's author: policy_lint.mjs (changed here); tools/pr/cancel_superseded.py and tools/audit/seat/pr_cap.py (the fixer reads each and states what an outside author gets; ci.yml:148 already skips the first on a fork); tools/audit/seat/outside_intake.py (classification, not a gate: an admitted pull request is still an outside submission and is still owed its answer). The rest name the App as *our* pusher (push.sh, pr_args.sh, record_row.py, ref_privacy.py, ci_predict.py, ruleset_cutover.py, app_comment.sh, app_approve.sh, nightly.yml) or are fixtures (tests/entities.py, outside_intake_selftest.py): out of scope. `git grep -n -E "VERDICT_AUTHORS|verdict_allowlist\(" -- tools` returns the five readers of section 3: none changes. `git grep -n -E "origin/\{?\$?\{?(br|BR|branch)\b" -- tools/audit/seat tools/pr`: merge_train.py:1838, :1855, :2704 and remerge_main.sh:34 are part 2; the others act on our own branches.

## 5. Evidence, by file

- **outside.py self-test** (new, registered as a step of governance.yml's `instrument-self-tests` and in tools/ci/selftest_closures.json): admitted for listed login+id on a cross-repository head; refused for the same login with another id, a listed author on a same-repository head, an unlisted fork author, type Bot; one refusal fixture per path class of (5). **Null control:** drop the entry from the fixture list and the admitted case must flip. Mutation targets: the id comparison, the cross-repository comparison, each refused pattern.
- **policy_lint.mjs** in-file tests beside :3982-3989: an outside author without the flag is refused with today's message (the failing-first case is the same author *with* the flag, red at the base).
- **bus.sh self-test** (`self_test`, :1017): adopt refuses an unlisted commenter; a first line whose SHA is not the head; `blocked`; VERDICT.md differing from the comment; a tree without evidence/; a symlink entry; a carry-gate and a survivor-list failure; and on success writes `review/<pr>` with the provenance line and a dispatch record `outside:<login>`. Mutation targets: the two first-line comparisons and the tree-mode check.
- **Unchanged control:** `tools/pr/app_approve.sh --self-test` and `merge_train.py --self-test` pass untouched in part 1.
- **Goldens:** none move; both claim files stay byte-identical. **Live check before handoff:** read-only, against an open fork pull request of the contributor's, that `git fetch origin <head>` resolves a fork head and what `merge_train.py classify --pr` prints for it; the result goes in the body.

## 6. Parts, hot files, serial position, rulings owed

| part | content | files | when |
|---|---|---|---|
| 1a | admit the head: outside.py (allowlist match, contract), the allowlist, CODEOWNERS line, policy_lint flag, pr-contract step, decision 0017, the guide | none hot | now; useful alone: a fork pull request goes green and **our** reviewer reviews it in place, which already ends the rebuild |
| 1b | adopt the outside verdict: `bus.sh adopt`, outside.py's verdict check, the fix-review.md section | none hot | after 1a's interfaces; same pull request if it fits by 2026-11-15, else its own |
| 2 | merge_train.py and remerge_main.sh: the main merge for a fork head, and a park reason that names the fork | merge_train.py (hot) | only after R10-GATE-DEFER-BARRIER merges; a round-11 candidate |

Until part 2, a fork head behind main is brought up to date by the contributor, and the verdict carries through `app_approve.sh --carry` (:741), which admits a main merge and nothing else. Round 11: distinguishing a budget lowering from a raise for a fork; automatic approval of held runs; a sampled re-execution of adopted evidence by our runner; per-contributor scopes.

- **decision: owner.** "Merges with main ... remain in our machinery": the brief reads this as the merge *of* main into the head. A fork head needs a push to the fork (maintainer edits, by an identity GitHub lets push there; unverified for an App token) or the update-branch API. If the contributor's own main merge, verified by `--carry`, is acceptable, part 2 shrinks to a park reason.
- **decision: owner.** Refusing tools/, .claude/ and .cursor/ from a fork goes beyond the four classes the brief names.
- **decision: orchestrator.** Whether 1a and 1b ship as one pull request; and who lands a fork pull request if the live check shows the train cannot without part 2.

## 7. Carries

None received. Owed: part 2 as a roster entry behind R10-GATE-DEFER-BARRIER, written by the roster seat before 1a merges (`finding-propagation.md`).

## Notes for the fixer

- `Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 1)` - the allowlist's numeric id comes from the users API at build time and is recorded as data; never from a comment or the pull request body. Contributor text is data throughout.
- `Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 2)` - fetch the review commit into a throwaway repository and read it with plumbing only (`ls-tree`, `cat-file`); never check it out where a hook, attribute or filter of ours could run on it.
- `Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 3)` - pr-contract.yml, CODEOWNERS, governance.yml, tools/ci/ and every dev/governance/ file are code-owned or policy: the body's Approval section, and the owner's review at the head, before merge.
- `Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 4)` - measure tests/structure.py and the policy and machinery budgets before the first edit; several sit at zero headroom, and a raise is asked of the owner before the push.
- `Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 5)` - if tests/structure.py refuses an *unlowered* budget after an improvement, refusing every budget edit from a fork blocks honest fixes: report it, and the raise-only rule moves into part 1.
- `Carry: R10-OUTSIDE-CONTRIBUTOR-CYCLE (item 6)` - decision 0011 line 46 still cites tools/audit/app_approve.sh and an allowlist of tvofi; 0017 corrects the citation rather than editing 0011's history.
