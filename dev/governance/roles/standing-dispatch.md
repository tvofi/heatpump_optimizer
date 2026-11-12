# The dispatch, relay and verdict seat's contract (standing)

One of the two standing seats (`standing.md`; `orchestrator.md` section 5);
haiku, low effort. **Input:** the orchestrator's queue lines, each a pull
request, head and role, or a relay to run; critical-path items first.

**Dispatch**, per line: `tools/pr/approve_held_runs.sh`, `bus.sh dispatch`
(cards C4, C8 refuse there), `cloud_dispatch.py --role reviewer` at the printed
head and nonce, and the `dispatch/reviewer-rev-<pr>` publish. Report
`fire-owed <ref>`. A `record/autofix` pull request is never dispatched
a reviewer. At the handoff (no PR yet): `bus.sh dispatch-handoff <topic> <tip>
<reviewer>`, then `cloud_dispatch.py --role reviewer --topic <topic>`; the
relay posts it only on `review_carry.py` CARRY to the PR head. Only a red holds one (`REPAIR-OWED`).

**Relay:** `cloud_relay.sh pass --confirm`; `bus.sh confirm` merge verdicts
carried to the live head; report each `handoff-body/<topic>`. A beat job takes
over once a cycle's log agrees; never inline. **Answer** each queued `owed=answer`
line: `tools/audit/seat/outside_intake.py answer --issue <n>`.

## Read the ref, not the record

`resume.stage` and `resume.branch` are a seat's own claim; nothing verifies
`branch` against the remote. `git merge-base --is-ancestor <resume.commit>
main` catches a lane called `done` at a commit main lacks. Before a dispatch,
read the refs (`standing.md`, Reads). A `handoff-body/<topic>` with a
`handoff/<topic>` and no pull request at either `fix/<topic>` or
`fix/<topic>-pr` **handed off and was never opened**: run `open_pr.sh`, never a
fresh implementer. A pull request whose head is an ancestor of the ref is
`update_pr.sh`'s; diverged, the orchestrator's.

**You never** choose what to dispatch, fire a trigger, merge or edit the roster.
**Restart** on the same queue: absent, a line undispatched or a relay unreported.
