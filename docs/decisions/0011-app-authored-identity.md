# 0011 — Pull requests are authored by the `hpo-author` App; the retired account never writes again

Status: recorded 2026-09-19 from the repository owner's decision, #201
comment 5744682317. Amended by 0013 (2026-09-24): verdicts post as the
`hpo-approver` App, not `tvofi`.

## Context

The author identity 0009 built the programme on — the seat user account
`tvofi-seat-author` — is spam-flagged by GitHub. Measured on 2026-09-18/19:

- its pull request **#1256** returned `201 Created` and then `404` within
  about sixty seconds, and the branch it pushed (`fix/d11-gov`) was left
  wedged;
- **about eleven of its merged pull requests now return 404 retroactively** —
  the conversations vanished after the merges, with no event to read;
- the in-tree `docs/delivery/` rows for those pull requests survive, which is
  how the purge is enumerable at all.

A second measured fact shapes the model beside it: **a verdict must never
post as an author App** (#1233's defect — GitHub refuses an author's approval
of their own pull request, so an author-App verdict cannot carry, and one
posted anywhere near that role blurs which identity owes the review). The
approver side of 0009 needs no repair: `hpo-approver` has approved pull
requests since 0009's step 6 landed.

## Decision

The owner's words, #201 comment 5744682317 — **the three-identity model**:

- **author** = the `hpo-author` App (orchestrator-centralized minting — seats
  stay LOCAL-ONLY, hand off, orchestrator pushes);
- **approver** = the `hpo-approver` App;
- **verdicts/merges/closes = `tvofi`.** (Verdicts: `hpo-approver` since 0013.)

Measured properties of the App this rests on: slug `hpo-author`, id `5003531`,
owner `tvofi`, installation `163073454`; the repository is readable through
its installation token, which carries `contents`, `pull_requests` and
`workflows` read & write. The tool is `tools/audit/app_push.sh` (branch
`fix/app-push-tool`): it runs `tools/audit/prepr.sh` on the body before
anything is minted (#678's ordering), pushes over https through a file-fed
credential helper so the token never sits on a command line, opens or re-bodies
the pull request as the App, and reads the body back byte-identical. Seats hold
no App credential: the id file and private key live with the orchestrator and
are never printed. `tools/audit/app_approve.sh`'s verdict allowlist narrows to
`tvofi` (the approver App since 0013) and requires a `merge` verdict to cite an evidence directory that
exists, is non-empty, and names the head SHA.

**The retired account makes no GitHub write.** Its writes can vanish (phantom)
and its artifacts purge retroactively, so nothing may depend on one landing.

## What does not change

0005/0009's machinery is untouched: the approving review is still required
before a merge, and the owner is still the sole code-owner reviewer — an App
cannot be a code owner (0009's amendment of 2026-09-16), so neither
`hpo-approver` nor `hpo-author` can satisfy an owner review.

## Consequences

- **Apps are never code owners**: only `@tvofi`'s approving review satisfies
  `require_code_owner_review` on an owned path, which `.github/CODEOWNERS` and
  its header now state outright.
- **The retired account stays retired even if support restores it.** The
  support ticket seeks restoration of the **purged pull-request
  conversations**, not the account's write role; no tool, brief or brief
  change re-grants it one.
- The reviewer seat hands verdict text to the orchestrator, who posts it as
  `tvofi` — as `hpo-approver` since 0013 (`tools/audit/briefs/fix-review.md`); the fixer hands the branch and
  body off locally (`tools/audit/briefs/fixer.md` step 5); every brief names
  the three-identity model (`tools/audit/briefs/orchestrator.md` section 5).
- `tools/audit/push.sh` remains in the tree for a seat that legitimately
  pushes with its own `GH_TOKEN`; it is no longer the fixer's path to a pull
  request.
