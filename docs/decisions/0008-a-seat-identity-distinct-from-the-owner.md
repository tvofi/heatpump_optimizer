# 0008 — A seat identity distinct from the owner, in the order that cannot lock the repository

Status: accepted in principle by the repository owner on 2026-09-10 ("fix #680");
**effective, and 0005's decision superseded, only once step 3(c) below has been
verified by a seat.** Until then the file this record adds is inert by
construction, and this record is a plan with its checks written down. 0005's
order is the part of that record this one keeps; its reason is restated below
because it is the whole safety argument.

## Context

#680 re-put O1 — a second GitHub identity — to the owner with the live ruleset
as new evidence, and the owner accepted. What 0005 and #680 measured still
holds, re-measured at `ae36eff` for this record:

- `GET /repos/tvofi/heatpump_optimizer/collaborators` → 1.
- Ruleset `main-protect` (`22628467`, `enforcement: active`, target the default
  branch): rules `deletion`, `non_fast_forward`, `required_status_checks`
  (`strict_required_status_checks_policy: false`); **no `pull_request` rule**;
  `bypass_actors` = one entry, `RepositoryRole` 5 — administrators — with
  `bypass_mode: always`.
- No `CODEOWNERS` at `.github/`, the root, or `docs/`.

Every seat of this programme authenticates as the owner's own account, which is
the repository's administrator. So two facts hold at once today, and 0005 named
only the first: no rule can require a reviewer other than the author, because
there is no other identity; and every rule that does exist is one the seats'
identity is a bypass actor for.

## Decision

Two identities, one of them new, and one order.

1. **The author identity becomes a machine account.** A second GitHub user,
   added as a collaborator with **write** and not admin; the Claude account's
   GitHub authorization is switched to it, so every seat authors, pushes and
   merges as that account. Its merges are then bound by `main-protect` like
   anyone's: the bypass actor is the administrator role and the machine
   account is not in it, so the required contexts stop being discipline and
   become a rule.

2. **The code owner is the owner.** `.github/CODEOWNERS` names `@tvofi` for
   `CLAUDE.md`, `.claude/rules/`, `.cursor/rules/`, `tools/audit/briefs/`
   (less `COMMON.md`, which `CLAUDE.md` says is not policy), `docs/decisions/`,
   and itself. With the rule below, a pull request touching those paths needs
   the owner's approval on GitHub and no other pull request needs any: 0007's
   "owner approval per pull request" becomes a check rather than a sentence,
   and the session grant of 0001/0006 stops being needed because it stops
   being possible.

3. **The order is 0005's.** (a) The owner creates the machine account and adds
   it as a write collaborator. (b) The owner switches the Claude account's
   GitHub authorization to it — account-wide, so every repository the seats
   reach must be shared with it. (c) A seat verifies, and writes into this
   record's status line: `gh api user --jq .login` prints the machine account,
   and `gh api repos/tvofi/heatpump_optimizer/collaborators/<login>/permission
   --jq .permission` prints `write`. (d) Only then the ruleset rule is added:
   `GET repos/tvofi/heatpump_optimizer/rulesets/22628467` saved as the
   rollback, then one `PUT` on the same path carrying the three existing rules
   plus

   ```json
   {"type": "pull_request",
    "parameters": {"required_approving_review_count": 0,
                   "require_code_owner_review": true,
                   "dismiss_stale_reviews_on_push": true,
                   "require_last_push_approval": false,
                   "required_review_thread_resolution": false}}
   ```

   Rollback is the saved body `PUT` back. `dismiss_stale_reviews_on_push` is
   `fix-review.md` step 12's head-moved rule, enforced by GitHub for the
   owner's approvals. The `CODEOWNERS` file may merge before (d): without the
   rule GitHub only auto-requests a review, which claims nothing. The rule
   before (c) locks every policy pull request, because the author would still
   be the owner and GitHub does not count an author's approval of their own
   pull request.

4. **The review seat's own identity is a second step, deferred and not
   declined.** #680's first item — `required_approving_review_count: 1`, so
   every merge carries an approval from an identity that is not the author —
   needs a third identity for the fix-review seat (a GitHub App installation,
   which can approve and has no password), its token reachable by that seat and
   by no other, and the record job reading the review event, which is #541
   class 4. Nothing in this record is worth less without it, and adding it is
   one more identity and one more parameter in the same order. Recorded so it
   is a decision and not a forgotten item.

## Consequences

- `pr-contract`'s `## Approval` section and the verdict comment stay: they
  carry what GitHub's review event does not — the SHA measured and the
  finder's harness.
- The `--author` every seat pins on its commits changes with the account, in
  the change that follows (c); no policy file in the tree carries the string,
  so that change is to the seats' instructions rather than to the corpus.
- What stays honour after (d): for a non-policy pull request the fix-review
  seat is still another seat of the same kind and not a human gate. That is
  step 4's gap, and this record accepts it rather than closes it.
- 0005 is superseded from (c) on and stands until then; its status note says
  so, and this record is the one that names the steps.
