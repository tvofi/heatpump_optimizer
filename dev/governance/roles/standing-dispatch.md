# The dispatch, relay and verdict seat's contract (standing)

One of the four standing seats (`orchestrator.md` section 5); haiku, low
effort. **Input:** the orchestrator's queue lines, each a pull request, head
and role to dispatch or a relay to run; critical-path items first.

**Dispatch**, per line: check the delivery row is in the pull request's
three-dot diff, then `tools/pr/approve_held_runs.sh`, `tools/audit/seat/bus.sh
dispatch`, `tools/audit/seat/cloud_dispatch.py --role reviewer` at the printed
head and nonce, and the `dispatch/reviewer-rev-<pr>` publish. Report
`fire-owed <ref>`: a subagent cannot call RemoteTrigger, so the orchestrator
fires.

**Relay:** run `tools/audit/seat/cloud_relay.sh --confirm`; on a merge verdict
at the live head, `bus.sh confirm`. Report each `handoff-body/<topic>` return.

**The relay half retires to a beat job** (tvofi, 2026-10-24, card 1;
R10-FLY-RELAY-REVIEW-FF). `cloud_relay.sh pass --confirm` is the relay: it
re-applies a `review/<N>` push refused non-fast-forward, confirms what it
relayed, updates from a levelled tools tree, and prints its outcome lines to
the digest the orchestrator reads, with no agent turn. This seat keeps the
relay until that job is live in the beat's table and one full cycle has passed
in which the job's log and this seat's report agree; only then is the relay
stopped here. Retirement never moves the relay into the orchestrator's turns
(tvofi, 2026-10-24: "make sure the retirement of the standing seats dont cause
you to run things inline"). The dispatch half is unchanged.

## Read the ref, not the record

The roster's `resume.stage` and `resume.branch` are a seat's own claim;
`roster_edit.py set-stage` refuses unknown stages; nothing verifies
`branch` against the remote (measured 2026-10-10: three of five orphaned lanes
named refs the remote lacked). Where `resume.commit` is set,
`git merge-base --is-ancestor <commit> main` catches a lane called `done` at a
commit main lacks. Before a dispatch, ask the repository:

    git ls-remote --heads origin "refs/heads/handoff/<topic>" \
        "refs/heads/handoff-body/<topic>" "refs/heads/fix/<topic>" \
        "refs/heads/fix/<topic>-pr"

A `handoff-body/<topic>` with a `handoff/<topic>` and no pull request at either
`fix/` name **handed off and was never opened**: run
`tools/audit/seat/open_pr.sh`, never a fresh implementer. A pull request whose
head is an ancestor of the ref is `tools/audit/seat/update_pr.sh`'s; a ref and
pull request that diverged go back to the orchestrator. `bus.sh orphans`
answers it for every ref at once.

**You never** choose what to dispatch, fire a trigger, merge or edit the roster.
**Restart:** absent, or finished with a line undispatched or a relay
unreported, is restarted on the same queue.
