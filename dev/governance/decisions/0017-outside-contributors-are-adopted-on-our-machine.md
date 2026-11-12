# 0017 — An outside contributor's pull request is adopted on our machine

Status: recorded 2026-11-12 from the repository owner's rulings of that day.
Lands as roster group R10-OUTSIDE-CONTRIBUTOR-CYCLE in two parts (part 2 is
the merge train's side) and supersedes the retired group
R10-PR-CONTRACT-OUTSIDE. It amends 0011 (who may author) and 0013 (whose
verdict is confirmed) for allowlisted contributors only. Where 0011 cites
`tools/audit/app_approve.sh`, the file is `tools/pr/app_approve.sh`.

## Context

Decision 0011 refuses every pull request not authored by the `hpo-author` App,
and 0013 confirms only a verdict our own reviewer wrote. A contributor outside
the programme could therefore land nothing as written: each fix was re-cut by a
seat of ours.

## Decision

The owner, verbatim (tvofi, 2026-11-12, triage batch 238, entry P714):
*"Implement a mechanism that allow baikanfans PRs to be accepted as is as long
as they follow all our conventions and rules and have a valid merge verdict
(the reviewer may also be run by bankaifan). Merges with main and codeowner
approvals remain in our machinery even for such PRs."*

1. **Adoption on our machine is the gate.** A fork head runs the workflow
   files of its own merge ref, so a green `pr-contract` there is an early
   signal and proves nothing we rely on. `bus.sh adopt <pr> <comment id>`
   fetches main, checks it out to a throwaway worktree and runs the whole
   contract from that copy. Nothing of the fork is checked out or executed on
   our machine: git objects and the API only.
2. **The allowlist** is `dev/governance/config/outside_contributors.json`: login,
   numeric id (from the users API), date, decision. The pull request's author
   and the verdict comment's author must be one entry, by login, id and type
   `User`. It merges empty; the owner adds an entry once both parts are on main.
3. **A fork changes no grader unapproved.** `tools/pr/outside.py` classes
   every changed path, default deny:
   - **F, free:** `custom_components/`, `blueprints/`, `README.md`, a `*.md`,
     `*.png` or `*.svg` under `docs/` outside `docs/site/` and outside every
     CODEOWNERS line, and the pull request's own delivery row. **Class F has
     no owner read**: CI at the head and the contributor's own review are all
     that judge it.
   - **R, refused:** `.github/`, `tools/`, `.claude/`, `.cursor/`, the policy
     set, any `*_budgets.json`, `tests/closures.json`, `tests/golden/`,
     `tests/mutation_ledger/`, every gate file, every root file but
     `README.md`, and any path in no class. Such a fix stays with our fixer.
   - **O, owner-read:** every other path under `tests/` and `docs/`
     (`docs/index.html` and `docs/site/`, which the pages workflow publishes,
     and the scripts and data files under `docs/img/`), and any other
     CODEOWNERS-matched path.
   A diff to the manifest's `version` key refuses, as does a head that is also
   another pull request's head, of any state.
4. **A fork names no branch a shell expands.** The head ref name matches,
   whole, `[A-Za-z0-9][A-Za-z0-9._/-]{0,99}` and is not `main`. No workflow
   expands a contributor-named value inside a `run:` block; `outside.py`'s
   self-test refuses one.
5. **Class O is the owner's review or his machinery's under his mandate.**
   The owner, verbatim (tvofi, 2026-11-12, on who reads the owner-only paths
   of a contributor's fork pull request): *"They don't need to be read by me,
   a mandate made by me is valid for my machinery."* It resolves to one check
   on the owner account's **latest** decisive review of the pull request: it is
   APPROVED; its body carries, on a line of its own, `Outside read: <sha40>`
   naming the head or a commit that reaches the head by automatic merges of
   main only; it sits on that commit, on the head, or on a commit that carries
   between them; and its body is one of **two forms**:
   - **the owner's own:** it declares no agent and cites no mandate. The gate's
     agent pattern matches the words seat, mandate and orchestrator anywhere,
     so the owner writes exactly `Outside read: <head sha>` and nothing that
     names those;
   - **the machinery's:** it declares an agent and cites exactly one mandate,
     in force **now** with scope `all`, and the owner's own latest decisive
     review is not a change request. A mandate lets an agent approve, never
     overrule him; his revocation voids it until the merge.
   **Three reads** tell his machinery from a contributor, none taking a byte
   the contributor writes as authority: the **account** (GitHub's reading of
   the posting credential, pinned by login, id and type); the **mandate**
   (the owner's unedited comment on a record issue of this repository, read by
   id from the API at the instant of the check); the **head** (the line and
   the carry). One writer emits the machinery's form:
   `outside.py approve`, run by our class-O read seat. The train's three
   verdict-driven approval writers refuse a fork head (part 2).
6. **After adoption only our automatic merge of main moves the head.** On a
   head that is no branch tip of this repository, `app_approve.sh --carry`
   refuses every non-merge commit, whatever its subject or author says, and a
   merge whose merge-driver files are not main's. **No tool of ours pushes a
   fork's head to a branch of this repository**: that test would read it as
   ours.
7. **Unchanged:** verdicts post as `hpo-approver` (0013); merges with main and
   code-owner approvals stay ours; no secret reaches a fork run (the three
   autofix jobs and `mutation-pins` require a same-repository head); a held
   fork run is approved by `hpo-runs` after a read of the diff.

## Before the first allowlist entry

Two checks need the owner's credential and a fork, which the building seat did
not hold. Neither changes the code; both are owed before an entry is added:

- **The live check.** Post one mandated class-O approval on a test fork head
  with `outside.py approve`, read from the API which `commit_id` it reports
  before and after our main merge, and take one adopted verdict through
  `bus.sh adopt`, `confirm` and `app_approve.sh` end to end. The class-O check
  admits the review on the commit it read, on the head, and on a commit that
  carries between them, so every answer GitHub can give is covered; the check
  records which one it gave.
- **The account behind `secrets.CLOSURES_PUSH_TOKEN`.** It is the one workflow
  secret that is neither an App credential nor the Actions token. The tree
  shows where it goes: the three autofix jobs (same-repository heads only),
  `merge-main.yml` (main only), and the reusable Tests call, where GitHub
  withholds secrets from a fork's run. If it authenticates the owner's
  account, class O's account read rests on that withholding; the owner names
  the account.

## Owner defaults this record takes

His approving review of this record is his ruling on each:

- `docs/index.html` and `docs/site/` are class O; the `*.png` and `*.svg`
  under `docs/` that the same workflow publishes stay class F.
- The covering mandate scope is `all` (the gate's policy scope set); `code-owned`
  does not cover a contributor's grader change.
- Not built: a budget lowering against a raise for a fork, automatic approval
  of held runs, sampled re-execution of adopted evidence, per-contributor scopes.

## Consequences

- **What is checked, and what is not.** Form, binding to the head, the path
  rule and CI are checked. The honesty of a contributor's own review is not:
  it rests on the allowlist, which is the owner's choice of whom to trust.
- A fork fix adds its failing test by editing an existing test script (class
  O, one seat read). A fix that adds a tracked file outside `docs/`, moves a
  golden or needs a budget edit is not acceptable as is.
- The lane-skip arm is off for a fork head: every lane runs on every push.
- `dev/governance/` and `tools/pr/outside.py` are `@tvofi`'s in
  `.github/CODEOWNERS`: this record merges on the owner's approving review, or
  under a mandate in force with scope all.
