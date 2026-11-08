# The dispatch, relay and verdict seat's contract (standing)

One of the four standing seats (`orchestrator.md` section 5); haiku, low
effort. **Input:** the orchestrator's queue lines, each a pull request, head
and role to dispatch or a relay to run; critical-path items first.

**Dispatch**, per line: check the delivery row is in the PR's
three-dot diff, then `tools/pr/approve_held_runs.sh`, `tools/audit/seat/bus.sh
dispatch`, `tools/audit/seat/cloud_dispatch.py --role reviewer` at the printed
head and nonce, and the `dispatch/reviewer-rev-<pr>` publish. Report
`fire-owed <ref>`: a subagent cannot call RemoteTrigger; the orchestrator
fires. A `record/autofix` pull request is never dispatched a reviewer.

**Dispatch at the handoff** (R10-DISPATCH-AT-HANDOFF): once `handoff/<topic>` and
`handoff-body/<topic>` land, `bus.sh dispatch-handoff <topic> <tip> <reviewer>`,
then `cloud_dispatch.py --role reviewer --topic <topic> --head <tip> --nonce <it>`
(no `--pr`). `open_pr.sh` re-keys the record to the pull request; the relay
posts the verdict only when `review_carry.py` answers CARRY for tip..PR head,
else it prints `HELD-STALE` and `bus.sh dispatch <pr> <head>` starts a fresh
review. A topic that never opens a PR is reported, never posted. A pending
required context never holds a dispatch; only a red does (`REPAIR-OWED`).

**Relay:** `cloud_relay.sh pass --confirm`; `bus.sh confirm` merge verdicts
carried to the live head; report each `handoff-body/<topic>`. A beat job takes
over once a cycle's log agrees; never inline.

## Read the ref, not the record

The roster's `resume.stage` and `resume.branch` are a seat's own claim;
`roster_edit.py set-stage` refuses unknown stages; nothing verifies
`branch` against the remote. Where `resume.commit` is set,
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
**Restart** on the same queue: absent, a line undispatched or a relay unreported.
