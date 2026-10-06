---
status: accepted
supersedes: []
superseded-by: []
---

# 0006 — The policy-merge grant, re-granted to the local session

> **Status note, 2026-09-09.** Ruleset creation, which this record calls
> "deliberately not exercised yet", has been exercised: `main-protect`
> (`22628467`), created as the governance programme's last act once `record` and
> `env-matrix` existed on `main`. This grant has lapsed with its session; ADR
> 0007 states what replaced it.

## Context

Decision 0001 granted policy-merge authority to session
`019DU5u9DvSdWdcqXQnEW3ga` and to that session only. Its "What the grant does
not cover" section is explicit — *"Anything after this session. Policy merges
then revert to owner approval per pull request"* — and its Consequences say the
same. A later session does not inherit it, and reading 0001 as though it did
would be the precise failure this audit was called in to examine: an authority
claimed rather than held.

That session ended with the governance queue built but unmerged: `06-hooks`,
`07-loop`, `08-envmatrix`, `09-verdicts` and `10-adr-corpus`, every one of them
touching `CLAUDE.md`, `.claude/rules/` or `tools/audit/briefs/`. It ended
because the actions the remainder needs — branch deletion, tag creation,
ruleset creation — were refused by the agent proxy rather than by GitHub, so
the work moved to a local session on the owner's own machine.

The owner was asked, before this session merged anything, whether the queue
should run under per-pull-request approval or under a re-grant. **The owner
re-granted**, choosing to carry 0001's preconditions forward unchanged.

This decision does not supersede 0001. 0001 is a true record of an authority
that was held and is now spent; nothing in it becomes wrong when its session
ends, which is what it says would happen. This is a second grant, to a second
session, and both stand.

## Decision

Session `local_aa44f28c-7fa5-4008-9b2f-4e8095607fac` — named rather than called
"this session", because "this session" is not a thing a later reader can
resolve — merges the governance queue's policy pull requests, and performs the
GitHub-account actions that queue needs where they are technically possible.
The second half is stated because this decision exercises it: branch deletion
below is an account action, not a merge, and 0001's own grant was worded the
same way for the same reason.

The six preconditions of 0001 carry forward **unchanged**. Every such merge
satisfies all of them first.

- An adversarial fix-review verdict of `merge`, posted from a detached worktree
  at the head SHA, by a seat that is not the seat that wrote the change. The
  merge authority does not collapse the reviewer and the author into one seat.
- Every check green or skipped.
- The body names the measured head SHA, and it is the head the checks ran on.
- The three-dot diff against the merge base is empty for `VERSION`, the
  integration manifest and the `RELEASE_NOTES.md` heading.
- An `## Approval` section citing this decision.
- One merge at a time, with the unscoped gate on `main` green before the next.

If review seats cannot be kept alive, the queue **stalls** and the owner is
told. It does not proceed unreviewed: the reviewer precondition is the one this
grant most obviously could erode, and so it is the one stated twice.

## What the grant does not cover

Identical to 0001, and restated rather than cross-referenced because a reader
who follows a pointer to find the exclusions is a reader who might not.

- **Release stamps.** `tools/release/stamp.py` assigns versions after a merge
  and this session takes none. That covers everything the stamp writes, not
  only the three files a branch is told never to touch: the bundled card's
  version constant and the `claims-for:` line in both claim files move with it.
  A release tag additionally resets the `record` job's window, which is a second
  reason to take none without the owner.
- **Structural budget raises.** `tests/structure_budgets.json` is the code
  ratchet, not policy. No budget is raised; caps are paid by cutting.
- **Pull requests authored outside this queue.** A second session is closing
  non-policy issues in parallel and its pull requests are not covered here.
- **Anything after this session.** Policy merges revert to owner approval per
  pull request, exactly as 0001 said they would after its own session. The
  mechanical alternative 0001 proposed is unchanged and still unbuilt. O3 —
  whether policy merges after this programme stand on the ruleset plus
  `pr-contract` instead — **was the owner's open question and is now answered**:
  per pull request, with a per-session grant as the option, recorded as decision
  0007. This sentence read "is still the owner's open question" until that
  answer arrived; it is corrected here rather than left to age, because a record
  that describes a settled question as open is the defect this corpus keeps
  finding.

## Consequences

The queue runs to completion in one session rather than across days of
per-pull-request approvals, and the corpus does not sit half-converted, which
0001 identified as the worst of the three available states.

The cost is unchanged from 0001 and is stated rather than hidden: the paper
trail is the enforcement, because the identity that would make CODEOWNERS bind
does not exist: there is one collaborator, every seat authenticates as that
same identity, and GitHub refuses to let an author approve their own pull
request. A required-approval rule today would therefore be a **lock** rather
than weak enforcement. That measurement is recorded in its own decision later
in this queue; it is deliberately not cited by number here, because the
decisions numbered above 0003 do not exist on `main` yet and a citation that
resolves to nothing is the defect this corpus keeps finding.

One thing has changed, and it narrows the gap 0001 recorded. 0001's evidence
listed three refusals and separated them by source: one from GitHub's token
scope, two from the agent proxy. This session runs outside that proxy, so the
second class no longer applies to it. Branch deletion was the cheapest of the
three to exercise and is therefore the one this decision measures:

    git push --delete origin audit/queue-01-readmes audit/queue-02-fragments \
      audit/queue-03-record2 audit/queue-04-claims-fiction   -> rc=0
    git ls-remote --heads origin 'refs/heads/audit/*'        -> all four absent

Each branch's content was confirmed present on `main` before its ref was
deleted, by comparing the branch tip against `main` over exactly the files the
branch's own three-dot diff touched. `ls-remote` is the witness rather than the
push's own output, because a `git push --delete` has printed success while
failing in this programme before.

### What a decision record costs the corpus

Written here because the next seat to add one will otherwise re-derive it, and
because this file is the evidence for it.

A file under `docs/decisions/` is matched by no `POLICY_GLOBS` pattern, so it is
**free until a policy document names it**. The check that fires is `named-docs`:

    docs/decisions/<new>.md added, cited by nothing   -> rc=0, 35 policy files
    ... then cited from docs/HANDOVER.md              -> rc=1
        ERROR [named-docs] is named by docs/HANDOVER.md but has no cap in
        .claude/workflows/policy_budgets.json
    ... then cited from docs/plan-2026-09-open-issues.md instead -> rc=0

`docs/plan-2026-09-open-issues.md` is corpus-excluded, which is why decision
0001 is already cited from it — in #610's disposition row — and cost nothing.
So a new decision is cited from the plan of record, not from the handover,
unless someone is willing to pay a cap for it.

This corrects the outgoing programme handover, which said a sixth decision
record costs a line in `CORPUS_EXCLUDED`. Driven at both `main` and the chain
tip, it does not: the exclusion list matters only for a file the corpus has
already pulled in, and an uncited decision is never pulled in.

Ruleset creation, the third refusal, is deliberately **not** exercised yet. A
required check that does not exist on `main` blocks every merge permanently,
and the `env-matrix` and `record` checks do not exist there until `08` and `07`
land. It is the last action of the programme, not an early proof of capability.

Tag creation is not exercised at all, because the only tag worth creating is a
release tag and this grant excludes release stamps.

## Evidence

The re-grant is a decision the owner took in this session's own transcript,
which is exactly the thing 0001 was written to stop relying on. What survives
the session is this file, the `## Approval` section each merge carries, and the
disposition row in the plan of record.

The queue this grant covers was verified intact before any of it was used, at
the chain tip `audit/queue-10-adr-corpus`:

    node .claude/workflows/policy_lint.mjs
      -> 0 errors across 35 policy files
      -> FIXTURE ok: 54 errors hold 76 pins across 10 check classes

    node .claude/workflows/policy_lint_envmatrix.mjs "$PWD" <tmp> "$(git rev-parse HEAD)"
      -> 13 declared outcomes held, 0 did not, across 5 environment shapes

**76 pins across 10 check classes is the mis-rebase detector**, and it is the
only thing in this programme that has ever caught one. It read 76 here, so the
chain is pointed where it claims to be.
