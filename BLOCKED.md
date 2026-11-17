# BLOCKED: r10-gh-read-residue-p3 (repair of #3682, round 3 fire)

Question: body_push's pr-body lint refuses the carry the orchestrator's ruling named (`Carry: R11-PRE-HANDOFF-BOOKKEEPING` is BAD-DEST, stage carries-open): which destination does the ci_predict self-test-reads false positive carry to, or does the orchestrator land R11-PRE-HANDOFF-BOOKKEEPING as a live destination first?

Code: 4b0091b631a2e82950061c7b000bfd14bc51e726, pushed to refs/heads/handoff/r10-gh-read-residue-p3 this fire (fast-forward from 6e7fd991c0). `git merge-tree --write-tree origin/main HEAD` rc 0. No code change.

Body: BODY.md here, as ruled: the predicted `tests / closures` red named under `## Red checks` (inherited from d5ba8b8c, CI green there, its repair a no-op, not re-recorded), and the carry line added under `## Forward-carry`. The refused copy is also kept at handoff-wip/r10-gh-read-residue-p3-body b6f7a31f9d.

## The refusal

`bash tools/audit/seat/body_push.sh r10-gh-read-residue-p3 BODY.md` at 4b0091b631, rc 1:

    REFUSE carry: BAD-DEST body item 49379262: R11-PRE-HANDOFF-BOOKKEEPING: R11-PRE-HANDOFF-BOOKKEEPING is carries-open (resume.stage carries-open); a carry goes to the live group owning the seam, else the producing group keeps the fix; valid targets: unknown (no --pr-group) -- CARRY-AUDIT: 5 finding item(s): 4 routed, 0 unrouted, 1 bad destination(s), at origin/handoff/audit-r10-roster 0c8313fd16
    body_push: REFUSED BODY-LINT

- The predictor arm did not refuse in this run (no REFUSED PREDICTOR); every other arm printed ok (pr-body 0 errors, figures 7 resolved 0 refused, ref_privacy ok).
- Not repaired here: re-targeting or dropping the carry would change what the ruling directed ("No other change"); the destination is the orchestrator's call.
