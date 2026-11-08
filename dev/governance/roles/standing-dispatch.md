# The dispatch, relay and verdict seat's contract (standing)

One of the four standing seats (`orchestrator.md` section 5); haiku, low
effort. **Input:** the orchestrator's queue lines, each a pull request, head
and role to dispatch or a relay to run; critical-path items first.

**Dispatch**, per line: check the delivery row is in the PR's
three-dot diff, then `tools/pr/approve_held_runs.sh`, `bus.sh dispatch`,
`cloud_dispatch.py --role reviewer` at the printed head and nonce, and the
`dispatch/reviewer-rev-<pr>` publish. Report `fire-owed <ref>` (a subagent
cannot call RemoteTrigger). A `record/autofix` pull request is never dispatched
a reviewer. At the handoff (no PR yet): `bus.sh dispatch-handoff <topic> <tip>
<reviewer>`, then `cloud_dispatch.py --role reviewer --topic <topic>`; the
relay posts it only on `review_carry.py` CARRY to the PR head. A red holds a
dispatch (`REPAIR-OWED`), a pending context never.

**Relay:** `cloud_relay.sh pass --confirm`; `bus.sh confirm` merge verdicts
carried to the live head; report each `handoff-body/<topic>`. A beat job takes
over once a cycle's log agrees; never inline.

## Read the ref, not the record

`resume.stage` and `resume.branch` are a seat's own claim; nothing verifies
`branch` against the remote. `git merge-base --is-ancestor <resume.commit> main`
catches a lane called `done` at a commit main lacks. Before a dispatch, ask:

    git ls-remote --heads origin "refs/heads/handoff/<topic>" \
        "refs/heads/handoff-body/<topic>" "refs/heads/fix/<topic>" \
        "refs/heads/fix/<topic>-pr"

A `handoff-body/<topic>` with a `handoff/<topic>` and no pull request at either
`fix/` name **handed off and was never opened**: run `open_pr.sh`, never a fresh
implementer. A pull request whose head is an ancestor of the ref is
`update_pr.sh`'s; one that diverged goes back to the orchestrator.

**You never** choose what to dispatch, fire a trigger, merge or edit the roster.
**Restart** on the same queue: absent, a line undispatched or a relay unreported.
