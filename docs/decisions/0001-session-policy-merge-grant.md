---
status: accepted
supersedes: []
superseded-by: []
---

# 0001 — The session policy-merge grant

> **Status note, 2026-09-09.** The two `200 []` answers below are spent. Ruleset
> `main-protect` (`22628467`) has since been created and the merge boundary is
> enforced: deletion, non-fast-forward and 18 required status checks. The grant
> this record describes has also lapsed with its session; ADR 0007 states what
> replaced it. Nothing else here changes — the record stands as what was true
> when the decision was taken.

## Context

`CLAUDE.md` "Changing any of it" requires the owner's approval before **merging**
a change to policy: `CLAUDE.md` itself, every `.cursor/rules/*.mdc`, and
everything under `tools/audit/briefs/`. The approval is required before the
merge, not before the draft, so a seat opens the pull request and surfaces it.

The 2026-09 governance audit rewrites most of that corpus. Serialising a dozen
policy pull requests behind individual owner approvals would have stretched the
audit across days and left the corpus half-converted in between, which is the
worst of the three states: the old rules no longer describe the tree and the new
ones do not yet bind.

The owner granted this session complete and unconditional authority to merge
policy changes and to perform GitHub-account actions where they are technically
possible, scoped to this audit and to this session — session
`019DU5u9DvSdWdcqXQnEW3ga`, named here because "this session" is not a thing a
later reader can resolve.

## Decision

The audit merges its own policy pull requests, under the repository's own
preconditions rather than instead of them.

Every such merge satisfies all of the following first.

- An adversarial fix-review verdict of `merge`, posted from a detached worktree
  at the head SHA, by a seat that is not the seat that wrote the change. The
  merge authority does not collapse the reviewer and the author into one seat.
- Every check green or skipped.
- The body names the measured head SHA, and it is the head the checks ran on.
- The three-dot diff against the merge base is empty for `VERSION`, the
  integration manifest and the `RELEASE_NOTES.md` heading.
- An `## Approval` section citing this decision.
- One merge at a time, with the unscoped gate on `main` green before the next.

## What the grant does not cover

- **Release stamps.** `tools/release/stamp.py` assigns versions after a merge and
  the audit takes no stamp. That covers everything the stamp writes, not only
  the three files a branch is told never to touch: the bundled card's version
  constant and the `claims-for:` line in both claim files move with it.
- **Structural budget raises.** `tests/structure_budgets.json` is the code
  ratchet, not policy. The audit raises no budget.
- **Pull requests authored outside the audit**, except where landing or
  superseding one is needed to unblock an audit rewrite of the same file.
- **Anything after this session.** Policy merges then revert to owner approval
  per pull request, or to a mechanical form the audit proposes: a `policy:`
  title prefix, an `## Approval` section, a `Policy-Approved-By:` trailer
  checked on push to `main`, and CODEOWNERS with required code-owner review
  once cloud seats have a GitHub identity distinct from the owner's.

## Consequences

The corpus converts in one session rather than across several, and every
converted rule is either mechanically enforced or labelled honour with a reason.

The cost is that the paper trail is the enforcement for one session. That is
honest rather than hidden: the identity that would make CODEOWNERS bind does not
exist, because an author cannot approve their own pull request under one
identity, and every organisation and installation path the container can reach
returns 403. The audit records that as a measured blocker rather than as an open
question.

## Evidence

    # no ruleset, repository or inherited, applies to main
    GET /repos/tvofi/heatpump_optimizer/rulesets?includes_parents=true   -> 200 []
    GET /repos/tvofi/heatpump_optimizer/rules/branches/main              -> 200 []

    # the paths that would let the audit close the gap itself. Two different
    # refusals, and the difference decides who can lift them:
    GET .../branches/main/protection   -> 403 GitHub: "Resource not accessible
                                                by integration" — a token scope
    GET .../actions/permissions        -> 403 the agent proxy: "not permitted
                                                through this proxy" — this
                                                execution environment
    GET .../hooks                      -> 403 the agent proxy, same

The two `200 []` answers are what the legacy `protected: false` flag could not
give: they close the "the flag may not reflect a modern ruleset" caveat, and
they are why the audit treats the merge boundary as unguarded rather than as
unknown.

The 403s are recorded with their source because reading a proxy refusal as
GitHub's would send a later reader to change a token scope that was never the
obstacle. Only the first is a permissions answer about this repository; the
other two say this container cannot ask.
