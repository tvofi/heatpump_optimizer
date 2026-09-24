# 0013 — Fix-review verdicts post as the `hpo-approver` App; policy and budget files are the owner's

Status: recorded 2026-09-24 from the repository owner's ruling of that date,
given by `tvofi` to the orchestrator and relayed in this record's dispatch.
Amends 0011's three-identity model in one role; 0011 stands otherwise.

## Context

0011 made verdicts, merges and closes `tvofi`'s: the reviewer seat hands its
verdict text to the orchestrator, who posts it as `tvofi`, and
`tools/audit/app_approve.sh` approves only on a `Fix review: merge <sha>` from
that login. So the owner's account carried two voices — its own approving
review on a code-owned path, and every seat's verdict on every other one —
and a reader could not tell from the login which it was.

## Decision

The owner's ruling of 2026-09-24, in two parts:

1. **Review verdicts and approvals come from the approver identity, the
   `hpo-approver` App, not from `tvofi`.** The orchestrator still holds the
   credential — seats stay LOCAL-ONLY (0011) — and posts the reviewer seat's
   verdict with `tools/audit/app_comment.sh`, which reads it back
   byte-identical through `.claude/workflows/gh_comment.py verify` and
   refuses a post that lands as anyone but `hpo-approver[bot]`.
   `app_approve.sh`'s allowlist becomes that App alone.
2. **Only policy and budget files belong to the code owner `tvofi`.** The
   ratchet caps (`*_budgets.json`, named one by one) join the policy set in
   `.github/CODEOWNERS`.

What stays from 0011:

- **A verdict never posts as the author App** (#1233's defect: GitHub refuses
  an author's approval of its own pull request, and an author-App verdict
  blurs which identity owes the review). `app_comment.sh` reads only the
  approver's key files; both scripts' self-tests refuse the author App.
- **Merges and closes stay `tvofi`'s.** The ruling names verdicts and
  approvals only, and nothing in the record moves the merge: the
  orchestrator merges with `--match-head-commit` as `tvofi` (orchestrator.md
  section 11), and the approver App is not on the ruleset's bypass list.
- The owner's approving review is still the only one that satisfies
  `require_code_owner_review`; an App cannot be a code owner.

Measured, 2026-09-24: the App's login is `hpo-approver[bot]`, type `Bot`,
id `330097732` (`GET /users/hpo-approver%5Bbot%5D`); its ten reviews on
#1489-#1557 all carry `author_association` `NONE`. So the old allowlist's
association guard (OWNER, MEMBER or COLLABORATOR) would refuse every App
verdict; `app_approve.sh` pins the login, the `Bot` type and the numeric id
instead, which no user account can hold.

## The enforcement surface: kept owned

Part 2 read literally would drop `@tvofi` from the required-check
enforcement surface (#1402, #1515, #1558): the workflows, the scripts they
execute, the hooks. This record **keeps it owned** and asks the owner to rule
on it separately, because dropping it re-opens #1515's hole with nothing in
its place: a pull request editing `pr-contract.yml`, or a script it runs,
grades itself, and the approving review on an un-owned path is the App's —
issued on a verdict the orchestrator posts, from a seat the orchestrator
dispatched. The restore-from-base step (#1403) covers only
`.claude/workflows/*.mjs` and `*.py`, and a workflow edit can remove it.
Measured over the 54 first-parent merges since 2026-09-20 whose base carried
the surface block, 17 were owner-reviewed only because of it.

## Consequences

- The reviewer seat hands verdict text to the orchestrator, who posts it
  with `tools/audit/app_comment.sh` (`fix-review.md`); `orchestrator.md`
  section 5's identity line names the App for verdicts.
- `app_approve.sh` refuses a `tvofi` verdict. A pull request whose only
  verdict is `tvofi`'s is re-verdicted by re-posting the same text through
  `app_comment.sh`; nothing else changes about it.
- A path not in the web session's reach: `.claude/workflows/web-fix-wave.js`
  has the reviewer post its own verdict through the MCP identity, which is
  not the App, so such a verdict is re-posted the same way before approval.
- Owning the budget files puts the owner's review on every pull request that
  re-records one — including `tests/mutation_budgets.json`'s line pins after
  a line shift. Measured over the 104 first-parent merges since 2026-09-20,
  12 touched a budget file and no owned path.
- `docs/decisions/` is `@tvofi`'s; this record needs the owner's approving
  review before it merges.
