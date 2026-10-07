# 0009 — Agent identities for author and approver: no separate human approval, and the approver exists before the rule does

Status: recorded 2026-09-14 from the repository owner's in-session instruction
(#201 comment 5670207248, the D11 wave's decision on #954). **Every GitHub-side
step in this record is the owner's and none had happened then**, and the status
notes below supersede this paragraph: no machine account
exists, the seats still authorize as the owner, and ruleset `main-protect`
(`22628467`) still carries no `pull_request` rule with `bypass_actors` =
`[{RepositoryRole 5, always}]` (re-verified 2026-09-14 at `2e9a4d8` by the
pre-staging card on #954). Effective once the checklist's verification step has
been executed and written into this record's status line; until then this
record is a plan with its checks written down — the shape 0008 landed in — and
#954 stays open.

> **Status note, 2026-09-16.** Landed, measured at `5ffe0d9`:
> `GET repos/tvofi/heatpump_optimizer/collaborators` lists `tvofi-seat-author`
> with role `write` (step 2's author half); the write deploy key `hpo-stamp`
> (id 163516584) exists; and the bypass probes passed both arms on throwaway
> branches and rulesets (#201 comments 5701766255 and 5701850207). The approver
> is the GitHub App `hpo-approver` (id 4968222), reported installed with
> pull-request write on 2026-09-16; `GET .../installation` needs the App's own
> token, so the seat recording this note could not re-read it. Step 3b landed
> with #1071 (`059f047`): the `delivery-status-publish` lane pushes as
> `tvofi-seat-author` (#1065's force-push at 19:37:11Z, #201 comment
> 5703429662). **Not landed** at that note (steps 3 to 6 since, in the notes
> below): the rest of step 3 — seats still authenticate as
> `tvofi` (`gh api user --jq .login`), so the author half of step 4 is
> unverified, and the App has not yet approved a pull request the machine
> account authored (its APPROVED review 5227837364 on #1065, authored by
> `github-actions[bot]`, is not the demonstration: #201 comment 5703923412); step 5,
> `main-protect`'s `bypass_actors` still `[{RepositoryRole 5, always}]`; and
> step 6, no `pull_request` rule. The code-owner half is amended below.

> **Status note, 2026-09-16 22:30Z.** Supersedes the "not landed" list above
> for steps 3, 4 and 5.
>
> - **Step 5 landed at 21:18Z** (#201 comment 5704665628), after #1077 merged
>   (`698041b`). One `PUT` on `rulesets/22628467` changed `bypass_actors` from
>   `[{RepositoryRole 5, always}]` to `[{RepositoryRole 5, pull_request},
>   {DeployKey, always}]`; every rule read back identical to the saved rollback
>   body. The probe, on a throwaway branch under a throwaway ruleset with the
>   same bypass list: an API ref update as `tvofi` (admin) was refused, the
>   same as `tvofi-seat-author` (write) was refused, and a push over the deploy
>   key landed. Both throwaways were deleted. The owner then revoked the PAT
>   behind `~/.zcode/stamp.token`; `GET /user` with it returns 401 (comment
>   5704702814). A stamp now pushes only over the deploy key. Pull requests
>   merge under the new bypass: #1080 (21:30Z), #1082 and #1081 were merged by
>   `tvofi` after it, and the ruleset's `updated_at` still reads 21:18:10Z.
> - **Step 3 is demonstrated.** GitHub shows `tvofi-seat-author` as the
>   author of #1083, a ledger cycle, and of #1084, this record's own pull
>   request, which a seat opened and not the ledger lane. Before #1084 was
>   opened, with the seat's token:
>   `gh api user --jq .login` printed `tvofi-seat-author`, and
>   `gh api repos/tvofi/heatpump_optimizer/collaborators/tvofi-seat-author/permission --jq .permission`
>   printed `write`.
> - **Step 4 is demonstrated.** `hpo-approver[bot]` posted APPROVED review
>   5228959633 on #1083 at head `a149cb4` (22:23:03Z), a pull request the
>   machine account authored; #1083 merged as `9b462d7` at 22:23:06Z (#201
>   comment 5705424893).
> - **Step 6** is pre-authorised for one session (comment 5704795223): a
>   `pull_request` rule with the code-owner review, and `bypass_actors` reduced
>   to the DeployKey alone. It had **not** landed at this note; superseded by
>   the next note.

> **Status note, 2026-09-17.** **Steps 1 to 6 have all landed.** This note
> supersedes both notes above, the status paragraph and "#954 stays open"
> under Consequences wherever they differ: #954 closes with the pull request
> that carries this note.
>
> - **Step 6's first attempt was rolled back**, 2026-09-16 23:47–23:52Z (#201
>   comment 5706235238). The App's APPROVED review 5229528092 on throwaway
>   #1088 did not count while its installation had `contents: read`:
>   `reviewDecision` stayed `REVIEW_REQUIRED`, so the saved body was `PUT`
>   back. The owner then granted the App `contents: write` and widened the
>   author PAT to `repo, workflow`.
> - **Step 6 landed at 2026-09-17 04:58Z** (comment 5708908916), under the
>   mandate in comment 5704795223, with no pull request open. One `PUT` on
>   `rulesets/22628467` kept the deletion, non-fast-forward and
>   required-checks rules byte-identical, added a `pull_request` rule with
>   `required_approving_review_count: 1` and `require_code_owner_review: true`,
>   and cut `bypass_actors` to `[{DeployKey, always}]`. The probe, on
>   throwaway #1096: an unapproved merge as `tvofi` (admin) was refused; after
>   `hpo-approver[bot]`'s review 5231247704, `reviewDecision` read `APPROVED`.
>   #1096 was closed unmerged.
> - **The first merges under the rule.** #1098, a policy pull request, merged
>   as `b4a3a3c` at 05:48:34Z with one review, the owner's approval at
>   `f4c178f`, although it also changed the unowned `brief_lint.mjs`. #1100
>   merged as `1fd1b3d` at 06:04:57Z on the App's review 5231824699, and #1099
>   as `db3e095` at 06:17:25Z on its review 5231919413.
> - **A stamp pushes over the deploy key alone**: v6.6.0 was stamped that way
>   (comment 5708985902).
> - **The `SEAT_AUTHOR_TOKEN` Actions secret** is held by no workflow step since
>   #1086. On the owner's instruction (comment 5708947495) it was deleted on
>   2026-09-17, leaving the repository no Actions secret (comment 5710361737).

## Context

0008 accepted the two-identity design in principle, in the order that cannot
lock the repository, and deferred its step 4 — the approving identity — as "a
second step, deferred and not declined". The round-4 D11-01 finding measured
what stands while it is deferred: no version of `main-protect` in its entire
history has carried a `pull_request` rule, administrator bypass is always, and
**0 of 651 merged pull requests carry an approving review by anyone** (census
re-walked 2026-09-14; 592 at the audit, 602 at the deferral). The same finding
measured that 0008's ordered plan had **no instrument that would notice if it
stalled** — 0008's own effective-when condition, a seat verifying step 3(c) and
writing a status line, was the only progress signal the record had.

The owner took the decision in session on 2026-09-14, correcting 0008's staged
shape.

## Decision

The owner's words, #201 comment 5670207248: **the author identity is the fixer
seats' machine account; the approver identity is the reviewer seats and/or the
orchestrator, as appropriate; no separate human approval is required.**

This revises 0008 step 2 — the code owner is an agent identity, not `@tvofi` —
and promotes 0008 step 4's third identity into the plan's **first move**. The
order is 0008's, kept; only what sits inside it moves.

**Separation of duties is preserved, not relaxed, by removing the human.** The
approver of a pull request is never its author. The orchestrator approves only
work it did not author; the orchestrator's own authored record pull requests
are approved by a reviewer seat. The approval the rule counts is a seat's —
that is the whole content of "no separate human approval is required".

## The checklist, in the order that cannot lock the repository

1. **The owner creates the identities.** A machine account for authorship, and
   for approval a second machine account or a GitHub App — an App can approve
   and has no password, which is 0008 step 4's reason for naming it.
2. **Both are added as collaborators with write, never admin.** The bypass
   actor in `main-protect` is the administrator role; an identity outside it is
   bound by the rules it merges under (0008 step 1's reason).
3. **The seats' GitHub authorization is switched** to the author machine
   account. Account-wide, so every repository the seats reach must be shared
   with it (0008 step 3(b)'s cost, unchanged).
4. **A seat verifies, and writes into this record's status line**, in 0008's
   verification shape: `gh api user --jq .login` prints the machine account,
   and
   `gh api repos/tvofi/heatpump_optimizer/collaborators/<login>/permission --jq .permission`
   prints `write` — once per write identity. For the App form, the approving
   identity is verified by the approving review it posts: GitHub refuses an
   author's approval of their own pull request, so a review from it on a pull
   request the machine account authored is the demonstration that the approver
   exists and can act.
5. **`bypass_actors` is scoped down from `always`** — before the rule, so the
   rule binds the merging identity too. The instruction names the direction;
   the owner's flip sets the value.
6. **Only then, at a quiet moment with no open pull requests, the rule is
   added**: `GET repos/tvofi/heatpump_optimizer/rulesets/22628467` saved as the
   rollback body first, then one `PUT` on the same path carrying the existing
   rules plus the `pull_request` rule with
   `required_approving_review_count: 1` — 0008 step 3(d)'s parameter shape
   with the count 0008 step 4 deferred. Rollback is the saved body `PUT` back.

## Why the approver is the first move

The order is not stylistic. **Enabling the rule before the approver identity
exists deadlocks every open pull request**, including, until #1086 retired
it, the `ci/delivery-ledger` cycle pull request the #1017 delivery-ledger design
kept open and which had to be approved and merged every cycle. With one
identity, GitHub refuses the only approval available — the author's own — so
the lock is total; that is the measurement behind 0005's original refusal and
#954's deferral (0 approving reviews in the repository's entire merge history,
because none was possible). The approver identity is therefore the first move,
not the last. This is 0008's own deadlock argument with one change: the
identity whose absence made the rule a lock is created before the rule instead
of after it.

## CODEOWNERS does not land in this change

> **Amended 2026-09-16** (see "Amendment: the code owner is the owner, for
> policy only", below). Two sentences of this section are superseded: the file
> had already landed, at #756 under 0008, naming `@tvofi`; and its code owner is
> not the approver identity.

The approver handle a code-owner line must name does not exist yet. CODEOWNERS
is the change that **follows identity verification**, per 0008's own order —
0008 step 3(d): the file may merge before the rule, because without the rule
GitHub only auto-requests a review, which claims nothing. The code owner it
will carry is **the approver identity, not `@tvofi`** — this revises 0008 step
2. The paths are 0008's, unchanged: `CLAUDE.md`, `.claude/rules/`,
`.cursor/rules/`, `tools/audit/briefs/` (less `COMMON.md`, which `CLAUDE.md`
says is not policy), `docs/decisions/`, and the file itself.

## The observer

Each step of this checklist lands on GitHub, not in this tree, and a step that
lands invisibly is a plan that stalls unobserved — which is what the D11-01
finding measured about 0008. The W4D-G1 derivation instrument (#957, this
wave's first pull request) reads the ruleset and reports each GitHub-side step
landing, including the rule itself or its continued absence. 0008's own
effective-when condition — a seat must verify and write the status line —
warned of exactly this stall by making a manual write the only signal; the
derivation is the instrument that closes it, and this record's verification
step writes into a tree the instrument watches.

## The boundary this record does not cross

> **Amended 2026-09-16:** the owner has rewritten that sentence, in the pull
> request carrying the amendment below.

`CLAUDE.md`'s sentence — "The owner's approval is required before merging a
change to any of it" (its "Where the policy is" section) — is a separate text.
Tonight's instruction covers the **GitHub review mechanism**; the in-session
approval practice for policy merges stands until the owner rewrites that
sentence. This record changes who approves on GitHub once its checklist lands;
it does not change what `CLAUDE.md` says, and a later edit to `CLAUDE.md` is
the owner's act, not a consequence of this file.

## The session grant

The session grant of 2026-09-14 (#201 comment 5670246622) is recorded here
because this record is one of the pull requests it covers (W4D-G9): full
approval for any **policy changes or budget raises during that session only**,
a raise remaining the last resort with pruning tried first (the
`ratchet-budgets.md` order, restated by the owner with the grant). **It
expires when the session ends**, where decision 0007's per-pull-request owner
approval resumes; the permanent rule is unchanged — human approval for policy
changes and budget raises after the session. Same shape as decisions
0001/0006, and like them it names its session so no later session inherits it.

## Consequences

- 0005 is superseded when this checklist's verification lands, and stands
  until then; 0008's status note tracks this record, and its step-2 shape and
  step-4 deferral are revised here while its order and rollback are kept.
- **#954 stays open.** The identity creation, the authorization switch and the
  rule flip are owner-side GitHub steps that have not happened; this record is
  the decision, not the flip, and the issue closes when the steps land and the
  observer reports them — not before. *(Superseded 2026-09-17: every step
  landed, in the status note of that date, and #954 closes with it.)*
- The `--author` every seat pins on its commits changes with the account
  switch, in the change that follows verification; no policy file in the tree
  carries the string (0008's consequence, kept).
- `pr-contract`'s `## Approval` section and the verdict comment stay: they
  carry what GitHub's review event does not — the SHA measured and the
  finder's harness (0008's consequence, kept).
- What changes from 0008's design once the rule is live: 0007's
  "owner approval per pull request" is satisfied for GitHub by an approving
  seat rather than the owner, on the mechanism this checklist builds; the
  sentence-level practice keeps its own boundary until `CLAUDE.md` is
  rewritten, as above. *(Amended 2026-09-16: for a policy path it is satisfied
  by the owner's code-owner review, below.)*

## Amendment: the code owner is the owner, for policy only (2026-09-16)

The owner approved this in session (#201 comments 5702359298, *"Approved"*,
and 5702401684, *"Add all but HANDOVER.md"*).

**An App cannot be the code owner.** GitHub's CODEOWNERS documentation lists
users and teams with explicit `write` access as code owners and names no App
form, and a personal repository has no teams. The approver this record creates
is an App, so "the approver identity, not `@tvofi`" cannot be written in the
file. The revision of 0008 step 2 is withdrawn: **the code owner is `@tvofi`**.

**`.github/CODEOWNERS` already exists**, since #756 under 0008. It now names
`@tvofi` on `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, `.cursor/rules/`,
`tools/audit/briefs/` with `COMMON.md` unowned, `tests/README.md`,
`tools/audit/README.md`, `tools/audit/harnesses/README.md`,
`.github/PULL_REQUEST_TEMPLATE.md`, `.claude/skills/steward/SKILL.md`,
`.claude/workflows/web-fragments.md`, `docs/decisions/` and itself. Every other
path has no code owner. `docs/HANDOVER.md` is left out and leaves the policy
set: it carries state, not rules.

**Step 6's rule carries both parameters**: `required_approving_review_count: 1`
and `require_code_owner_review: true`. A pull request touching no owned path is
satisfied by the App's approving review, given for the reviewer seats. One
touching an owned path additionally needs the owner's approving review, which
is how the owner's approval of a policy change is given; `CLAUDE.md`'s sentence
says so. "No separate human approval is required" above holds for every other
path. How the code-owner requirement treats the unowned files of a mixed pull
request is not stated in GitHub's documentation and was not probed before step
6; #1098, a mixed pull request, merged on the owner's review alone.

> **Status note, 2026-09-22 (R6-D11-01, #1402).** The list above is the policy
> set, and it was the whole surface: 0 of the 37 tracked files that produce or
> implement the checks `main-protect-checks` requires carried a code owner, so
> `require_code_owner_review` could not demand the owner for a change to the
> checks themselves. `.github/CODEOWNERS` now names `@tvofi` on them too — the
> six `.github/workflows/*.yml`, the hooks and their wiring, and the scripts
> those workflows execute with an interpreter — and its header carries the
> derivation. `tools/audit/round6/D11/fix/codeowners_gap.py` prints the surface
> size and how many of its files an owner-carrying pattern matches: against the
> pre-#1402 file that count was zero, and against the file this note describes
> it is the surface size.
