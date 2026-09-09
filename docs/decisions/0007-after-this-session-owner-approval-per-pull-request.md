# 0007 — After this session: owner approval per pull request, with a session grant as the option

Status: accepted, 2026-09-09, by the repository owner.

## Context

The governance audit left three questions with the owner because no seat could
answer them from inside the container. Two are settled and recorded: O1, a
second GitHub identity, was declined (`0005`); O2, code-scanning default setup,
answered itself once the endpoint read `configured`. **O3 is the third**, and it
is the only one about what happens *after* the programme: do policy merges
revert to owner approval per pull request, or stand on the ruleset plus
`pr-contract`?

Both `0001` and `0006` said in their own text that their grant covers one
session and reverts afterwards. Neither said what "afterwards" is, and a rule
that exists only as the absence of a grant is the state this corpus keeps
finding: a requirement everybody believes and nothing states.

## Decision

**A policy merge after this session needs the repository owner's approval on
that pull request.** The owner may instead grant a session, in the shape `0001`
and `0006` already used: a decision record naming the session, carrying the six
preconditions unchanged, covering that session's queue and reverting when it
ends.

The six preconditions are not restated here because they are not new; they are
`0001`'s, carried by `0006`, and any grant citing this decision carries them
too. What is new is only the default: **absent a grant, per pull request.**

**The ruleset and `pr-contract` are the floor, not the substitute.** They were
the other half of the question, and the answer is that they were never the
alternative to approval: `pr-contract` refuses a body without an `## Approval`
section, a head that moved, a missing verdict — mechanically, on every pull
request, whether or not a human is in the loop. A grant rides on top of them.
Removing approval and keeping only the checks would leave the corpus with no
reader who is not also its author.

`pr-contract` runs today. **When this decision was taken the ruleset did not
exist**: `main` carried no repository or inherited ruleset, so every check was
advisory at the merge boundary, and creating one was this programme's last
remaining act — deliberately last, because a required context that never reports
blocks every merge permanently, and two of its eighteen contexts only began
reporting when the pull requests that added them landed. Written in the past
tense on purpose: a decision is dated, and this one must not go false the hour
the ruleset is created. This decision does not wait on it. What the floor is made of
can change; that a policy merge needs a reader who is not its author cannot.

## What this does not decide

- **Non-policy pull requests.** Unchanged: they need no approval and never did.
  The file class is `CLAUDE.md`'s, not this record's, and is stated there.
- **Release stamps.** Excluded by `0001` and `0006` alike, and still excluded.
- **Whether a mechanical form could ever replace the human.** `0001` sketched
  one — a `Policy-Approved-By:` trailer with CODEOWNERS and required review.
  `0005` measured why it cannot bind today: one identity authors and approves,
  and GitHub refuses self-approval, so the rule would be a lock rather than
  enforcement. If O1 is ever revisited, this decision is revisited with it.

## Consequences

The cost is one message per session rather than one per pull request, which is
what made the queue tractable, and it is paid by the owner rather than by the
programme. The benefit is that the file class an agent could most usefully
loosen on itself is the one class an agent does not merge alone.

The failure mode this closes is specific and was nearly hit at the start of this
session: a session inheriting a previous session's grant by reading its record
and assuming it carried. `0001` named its session by id and said so; the
inheriting session asked instead of assuming, and was re-granted. **Asking is
the protocol, and it belongs at the start of a session, before the first policy
pull request is merged, not when one is reached.**
