# 0009 — Agent identities for author and approver: no separate human approval, and the approver exists before the rule does

Status: recorded 2026-09-14 from the repository owner's in-session instruction
(#201 comment 5670207248, the D11 wave's decision on #954). **Every GitHub-side
step in this record is the owner's and none has happened**: no machine account
exists, the seats still authorize as the owner, and ruleset `main-protect`
(`22628467`) still carries no `pull_request` rule with `bypass_actors` =
`[{RepositoryRole 5, always}]` (re-verified 2026-09-14 at `2e9a4d8` by the
pre-staging card on #954). Effective once the checklist's verification step has
been executed and written into this record's status line; until then this
record is a plan with its checks written down — the shape 0008 landed in — and
#954 stays open.

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
exists deadlocks every open pull request**, including the standing
`ci/delivery-ledger` cycle pull request the #1017 delivery-ledger design keeps
open by design and which must be approved and merged every cycle. With one
identity, GitHub refuses the only approval available — the author's own — so
the lock is total; that is the measurement behind 0005's original refusal and
#954's deferral (0 approving reviews in the repository's entire merge history,
because none was possible). The approver identity is therefore the first move,
not the last. This is 0008's own deadlock argument with one change: the
identity whose absence made the rule a lock is created before the rule instead
of after it.

## CODEOWNERS does not land in this change

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
  observer reports them — not before.
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
  rewritten, as above.
