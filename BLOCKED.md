# BLOCKED: r10-round-playbook body re-take, body_push refused

The body is re-taken at PR head 8d4ff2f2 as BODY.md beside this file; `prepr.sh --body-check` on it prints `pr-body ok: PR-BODY: 0 error(s)`, carry ok, figures ok, ref_privacy ok. No red is caused by code in this diff: `budget-raise-gate / budget-raise-gate` is the deliberate raise (named and answered), `gate` rolls it up (one run also hit the API rate-limit stop), and `pr-contract / pr-contract` failed on the old body naming the check bare.

`bash tools/audit/seat/body_push.sh r10-round-playbook BODY.md`, run from a worktree at 8d4ff2f2, refused:

    body_push: handoff/r10-round-playbook is at 73929b827531, this checkout at 8d4ff2f25...; push the code, then the body

The code ref handoff/r10-round-playbook is at 73929b82, and the PR head 8d4ff2f2 (a main merge plus the app's delivery-row commit) is ahead of it. This seat was told not to touch code and not to override a refusal, so it did not move the handoff ref.

Needed from the orchestrator: fast-forward handoff/r10-round-playbook to 8d4ff2f2 (or run body_push.sh from a seat allowed to), then `bash tools/audit/seat/body_push.sh r10-round-playbook BODY.md`. The earlier landed-carry arm (`CARRY-LANDED: 13 missing`) may still refuse after that and needs the roster ops named in the previous BLOCKED.md.
