# 0005 — No CODEOWNERS while one identity authors and approves

Status: accepted. Revisit when O1 is answered. "The plan", "PR-T4", "4.9" and
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

When **O1** is answered — a GitHub identity for cloud seats distinct from the
owner, which every organisation and installation path in this environment
refuses with 403 — this decision should be revisited in the same change that
creates the identity, because the two are worth nothing apart. A CODEOWNERS
file added before then buys a false signal; the identity added without
CODEOWNERS leaves the reviewer requirement unstated.

Nothing in the tree cites this file by name, deliberately: a capped policy file
naming a document under `docs/decisions/` is refused by `named-docs` until that
directory's corpus classification is decided, which is the owner's call and is
not decided here.
