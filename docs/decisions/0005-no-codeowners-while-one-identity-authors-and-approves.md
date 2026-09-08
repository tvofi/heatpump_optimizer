# 0005 — No CODEOWNERS while one identity authors and approves

Status: accepted; O1 was answered — declined — so this stands rather than waits
(Consequences, below). "The plan", "PR-T4", "4.9" and
"O1" below are the governance-audit plan's — `docs/plan-2026-09-governance-audit.md`,
which is not on `main`: it is archived on `audit/session-evidence-2026-09-08`.

## Context

The plan's PR-T4 pairs `.github/PULL_REQUEST_TEMPLATE.md` with
`.github/CODEOWNERS`. The template landed and is enforced: `policy_lint` lints
it as if it were a pull-request body, so deleting a heading turns the
acceptance red on the change that deletes it. The second file was never
written, and an audit of the plan found it reading as forgotten rather than
declined — which is worse than either.

**What CODEOWNERS would do here, measured.** The proxied credential
authenticates as the repository owner and carries
`permissions: {admin: false, maintain: false, push: false}`.
`GET /repos/tvofi/heatpump_optimizer/rulesets?includes_parents=true` and
`GET .../rules/branches/main` both return `200 []`: no repository ruleset and
no inherited ruleset applies to `main`. So a code-owner rule cannot be
required, because there is nothing to require it in — and `POST /rulesets` is
refused through this environment's proxy.

**And if it could, it would bind nobody.** Every seat in this programme acts as
one GitHub identity. GitHub does not let an author satisfy their own code-owner
review, so the rule would either block every pull request or be bypassed by the
same identity that wrote it. The plan says this in section 4.9 —
*"a required-approval or code-owner rule is not requested while one identity
authors and approves, which would make it honor with extra steps"* — and then
lists the file anyway.

## Decision

**Do not add `.github/CODEOWNERS` in this programme.** A file that names owners
no check consults is a claim of enforcement the repository cannot honour, and
this audit's whole subject is prose that is stricter than the machinery under
it.

**The enforcement CODEOWNERS was meant to provide is provided by the paper
trail instead**, and that half is mechanical: `pr-contract` requires the body's
`## Approval` section, the head SHA it names must equal the head CI ran, and
policy merges under the session grant cite `docs/decisions/0001`. What stays
honor is *who* approved, and that is honor because a second identity does not
exist, not because nobody thought about it.

**This is recorded rather than left undone.** An item that is declined and an
item that was forgotten look identical in a tree; only one of them is a
decision.

## Consequences

**O1 was put to the owner and declined**, so this decision stands rather than
waiting on one. The measurement that settled it: the repository has exactly one
collaborator — `tvofi`, role `admin` — and cloud seats authenticate as that same
identity, so every pull request in this programme is authored by the owner. And
GitHub refuses a self-approval. A required-approval rule today would therefore
not be weak enforcement; it would be a **lock**, with the only eligible approver
ineligible on every pull request. That, and not the 403s, is why the ruleset in
this programme requests no approval rule.

The alternative was costed rather than assumed impossible. A machine account is
two clicks; what it does not buy on its own is the separation, because these
seats take their credential from the Claude account's own GitHub authorization,
which is account-wide — so switching it means every repository those seats reach
must be shared with the machine account. The failure mode is silent in the worst
direction: CODEOWNERS plus a required-approval rule added *before* the switch is
verified locks the repository rather than guarding it. The order that avoids
that: create the account, switch the authorization, **verify the authenticated
login is the machine account**, and only then add CODEOWNERS and the rule.

Revisit when that identity exists, in the same change that creates it, because
the two are worth nothing apart: a CODEOWNERS file added before then buys a
false signal, and the identity added without CODEOWNERS leaves the reviewer
requirement unstated.

What stays honour meanwhile is *who* reviews. The adversarial fix-review seat is
not the author and does refuse — two of the three pull requests before this one
were blocked on real defects, one of them a false claim that would otherwise
have shipped permanently into a code comment. But it is another seat of the same
kind rather than a human gate, and that is the gap this decision accepts rather
than closes.

This file may now be cited by name from a capped policy file. It could not be
when it was written: `named-docs` refuses a document a capped file names but
nothing measures, and `docs/decisions/` was then neither measured nor excluded.
The commit carrying this edit settles that, by naming the ADRs in
`CORPUS_EXCLUDED` one by one.
