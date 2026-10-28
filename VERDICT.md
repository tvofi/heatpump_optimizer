Fix review: blocked fbbd3e61fe312f94b6c4c579b64236fcf9699248 policy-loosened: severity critical narrowed from a merge that can happen to one that happened, and step 4 departs from the owner's quoted words

bus-nonce: 349bfe5d53c6482114137e4323361dbc

Round 1 of PR #2736 (policy(D11): mechanise-first). Reviewed at head fbbd3e61fe312f94b6c4c579b64236fcf9699248 in a detached worktree; that SHA was still the PR head and origin/main was still e97f5749b when I wrote this. Role contract: origin/main's fix-review.md. `git diff $(merge-base)...origin/main -- dev/governance/roles/` prints nothing, so my copy of the contract is current. I reviewed this as a policy change: the owner's wording governs, and every sentence the diff adds, cuts or rewrites was checked for a binding it adds, drops or loosens.

## Block

1. **The critical severity class is loosened, and the body does not say so.** Before: "`critical` — a merge to `main` *can happen* with no review or with a red required check". After: "`critical` — a merge to `main` with no review or a red required check". The old text made a latent gap critical, meaning a mechanism that *permits* an unreviewed or red merge. The new text reads as an actual merge that took place. Under it, a ruleset gap with no merge through it yet becomes `high` or lower. The body's list of cuts gives a reason for every other cut but not this one. Restore "can happen", or get the owner to approve the change explicitly.
2. **Step 4 departs from the owner's quoted words in ways that loosen what they bind.** The quote is *"each operation or shape that is not clearly a one shot and could be mechanical should be mechanical and wired into the machinery ... only policy if no robust script could be built at a reasonable cost"*.
   - Non-finding: "a policy kept because no robust script *exists*". The owner's test is whether one *could be built at a reasonable cost*. Read literally, the new text clears exactly the case the owner wants found: a policy that stands only because nobody has written the script yet.
   - Finding: "an operation recurring by hand ... its recurrence count from a command run alone". The owner sets the burden the other way: anything *not clearly a one shot*. Requiring a counted recurrence leaves a gap. An operation seen once that is plainly repeatable is neither a finding (no recurrence count) nor a non-finding (not a true one-shot).
   - "or shape" is dropped (the finding names only operations and prose steps). "and wired into the machinery" is dropped too: an instrument that exists but is unwired is filed only as "a conformance row", and is never a finding against the owner's "wired" requirement.
3. **The source scope is narrowed, and the body does not say so.** "the repository's history" became "`main`'s history". D11 also audits branch-side mechanisms: claim, dispatch, probe and handoff refs, and the pre-merge heads that step 3's conformance sample reads, such as the first `pr-contract` run at the merged head. The cut list does not mention this.

## Findings

- The owner quote in step 4 cannot be traced to any GitHub record. tvofi's #201 comments since 2026-10-24T07:00Z contain no such text (saved in `ev/owner_201_comments.txt`). No repo issue comment since 2026-10-24T00:00Z (68 comments, one page) and no issue or PR body updated since then contains "could be mechanical". The PR has no comments and no reviews. The body cites the quote as "tvofi 2026-10-24" with no link. I could not verify the quoted words against a source; the owner's approving review at the head is the only check left. Carry: dismissed: settled by the owner's approving review that this policy PR already owes before merge
- Two of the body's "already stated elsewhere" justifications rely on files a D11 finder is not told to read. The #677 merge-enumerator trap is stated at `D13.md:74`, but a D11 seat reads D11.md and COMMON.md, and D11's own conformance sample enumerates merged PRs. The "derive the row count" rule is pointed to `writing-for-agents.md`, which the D11 brief never cites. The rules do exist in the tree, so this is a reach gap, not a falsehood. Carry: dismissed: the fixer can keep a one-clause pointer (`D13.md`'s fooled-before list) within the same cap when re-cutting for the Block
- Step 3's detector-health bullet lost "name any that is dead". Step 1's "a mechanism whose control you cannot make fire is a finding" still covers it, so this is not a loosening. Carry: dismissed: covered by step 1's sentence at this head
- `policy_lint.mjs --budgets` labels D11's row `tools/audit/briefs/D11.md`, a path that does not exist at this head. The file is `dev/governance/dimensions/D11.md`. This comes from the instrument, not from this PR. Carry: dismissed: pre-existing instrument label, not moved by this diff; outside this PR

## Evidence

- Head reviewed: fbbd3e61fe312f94b6c4c579b64236fcf9699248 (`ev/HEAD.txt`). The body's first `## Head` line names it. The bare SHA cf212c29e that follows is the previous code head, and the body says the head merges main into it.
- Merge with origin/main e97f5749b: `git merge-tree --write-tree` gives tree 6bd067797b, rc=0, no conflict (`ev/merge_tree.txt`).
- VERSION, the manifest and `RELEASE_NOTES.md` are untouched by the three-dot diff (`ev/diff_three_dot.txt`).
- Figures re-derived with `node tools/policy/policy_lint.mjs --budgets`, at origin/main 9586fce08 and at the head (`ev/budgets_9586fce08.txt`, `ev/budgets_head.txt`):
  - D11 lines: 99 → 100, cap 103.
  - D11 tokens: 1497 → 1493, cap 1499.
  - Corpus tokens: 66415 → 66411, cap 66434.
  - Role policy: 10016, cap 9958 + band 500.
  - All four match the body.
  - The first-draft size of 6576 bytes is the drafter's own out-of-tree measurement and I could not re-derive it. The limit of 5997 bytes is consistent with 1499 × 4.
- `node tools/policy/policy_lint.mjs` at the head: 0 errors across 50 policy files (`ev/policy_lint_head.txt`).
- Mutation proof reproduced. Changing step 4 to name `tools/audit/seat/INSTRUMENTS.md` makes the lint exit with rc=1 and `ERROR [named-docs] tools/audit/seat/INSTRUMENTS.md: is named by tools/audit/briefs/D11.md but has no cap` (`ev/mutant_instruments_md.txt`). I restored the file afterwards.
- Cut justifications I confirmed:
  - `COMMON.md:20-22` states the earlier-findings wall and the D11 `exposure` record.
  - Step 3's check-runs parenthetical survives, covering the checks-summary trap.
  - `COMMON.md` item 3 defines a perturbation.
  - The branch-rules fooled-before item keeps "probe it with both arms".
  - The dropped "You get a worktree with `.git`" is supplied by `.claude/workflows/audit-find.js:53`.
- CI on the head (`ev/check_runs.txt`, commit check-runs API): no run is red. arch-score and budget-raise-gate succeeded, prelude and refresh succeeded, and the lanes the diff does not reach were skipped. `pr-contract` was still queued, so the step 11 body check had not run. No red check was owed an answer.
- Round: 1.
