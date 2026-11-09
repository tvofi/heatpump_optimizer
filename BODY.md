R10-DISPATCH-AT-HANDOFF: a reviewer is dispatched at the handoff, keyed by topic, with the carries the branch already held (bus.sh dispatch-handoff and rekey, open_pr.sh re-key, the relay's held handoff verdict arm, policy text, review_packet refusals). This repair merges origin/main into the handoff, which the opener had refused over one content conflict in tools/audit/seat/cloud_dispatch.py.

## Head note

Repair merge: origin/main (6457496aba7b1076b1ed60c374c5badafdf66fc1, read at 2026-11-09T02:39Z) is merged into the handoff by e27484ffc9fb1f282974a35f02a470f657795e57, which is the head measured below. The one conflict, cloud_dispatch.py, was resolved by union: main's frugal-routing line, role-pack setup and merge-tree-only block rule (#3338 and its earlier commits) and this branch's handoff reviewer (topic-keyed revt ref, no packet, no CI wait) are all present. The previous merge's tip was 089f1da017e98a697a24e70c308f79beee9b8607. `git merge-tree --write-tree origin/main HEAD` exits 0 and origin/main is an ancestor of the head.

## Head

e27484ffc9fb1f282974a35f02a470f657795e57

## Mutation proof

Two mutants of the merged tools/audit/seat/cloud_dispatch.py, each run against `python3 tools/audit/seat/cloud_dispatch.py --self-test` and restored after:
- Branch side: `ref_key = f"revt-{topic}" if at_handoff else f"rev-{pr}"` changed to `if False else`. Fails "a reviewer at the handoff returns on probe/revt-<topic>-<nonce8> with the subject `verdict <topic> <head>`" (146 checks, 1 failed).
- Main side: the reviewer's "block on main only when that reports a conflict" text changed to "block on main whenever main moved, or a". Fails "the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main" (146 checks, 1 failed).

## Null control

The unmutated merged file: `python3 tools/audit/seat/cloud_dispatch.py --self-test` prints "146 checks, 0 failed". The other instruments the merge touched pass their own self-tests at this head: closeout, machinery_ratchet, roster_edit, roster_lib, roster_queue, roster_sync, prune_refs, postmerge, orchestrator_tick, r10_mandate_guard_mutants and r10_roster_ops_mutants, each 0 failed.

## Figures

- `python3 tools/audit/seat/cloud_dispatch.py --self-test`: 146 checks, 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`: run at this head, origin/main unmoved since the merge; every step before the closures skip printed ok.
- `git merge-tree --write-tree origin/main HEAD`: exit 0.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Pending, not granted: this diff touches policy files (dev/governance/roles/standing-dispatch.md and dev/governance/roles/fix-review.md, both carried unchanged from the earlier handoff and main), which the owner approves by an approving review before merge (CLAUDE.md, policy section). No approval has been given; none is claimed here.
