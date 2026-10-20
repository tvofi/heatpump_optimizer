Fix review: blocked 202cb8874ef72b82d9db49a6ecd77f28ad22838a carry-missing: the mechanical red is cleared but the finding is still not carried into any destination stage — the re-bodied `Carry:` markers route to groups, yet no roster branch holds countermeasure A, the body cites no `handoff/audit-r10-roster` SHA or carry file, and `git diff origin/main...handoff/audit-r10-roster -- dev/programme/rosters/` prints nothing.
bus-nonce: ffed08738f8420708ca332870a5678a2

Reviewed head: 202cb8874ef72b82d9db49a6ecd77f28ad22838a (live PR head matches; head unchanged since the first review — the body moved, not the tree). Round 2. Diff unchanged: `dev/audit/rca/nightly-ha-pyspy-timeout.md` (new) and `dev/programme/delivery/2479.md` (row).

## RESULT lines

RESULT cleared: the first review's mechanical defect (no `Carry:` markers; `carry_audit` 5 unrouted) is repaired. `tools/audit/carry_audit.py check --body` on the live body reads `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`, and the newest `pr-contract` run at this head (118502573687, started 07:12:17) checked the re-bodied body and concluded success, superseding the 07:06 failure. Every other check's latest conclusion at the head is success or skipped; none is red. Head, tree, gate mode (`MODE: SCOPED -- 0 script(s) run, 33 scoped out.`), files and symbols are unchanged from the first review and still hold.

RESULT blocked carry-missing: countermeasure A changes how a later stage must work, and `finding-propagation.md`'s Enforcement forbids the producing PR from merging until the carry is **in the tree** and the body **names the file, the stage and (a roster carry) the branch SHA**. This body names a group (`R10-CI-LAYOUT`) but no branch SHA and no carry file, and the write has not landed: `handoff/audit-r10-roster` (tip 7e8e5e5) has an empty roster diff against main, no group's `carry` array mentions the py-spy retry, and no `dev/programme/carries/carry-*.json` holds it. `carry_audit.py` only validates the marker's destination; it does not write the carry. This is the "land carries before review" rule: the append and the cited SHA precede dispatch, not the merge.

RESULT blocked carry-destination: the named destination cannot own the fix. Countermeasure A edits `tests/nightly_ha.py` (`LoopHeartbeat.dump`, `_hb_spin`, `check_hb_positive_control`) and its `tests/entities.py` pins; `R10-CI-LAYOUT` lists only `.github/workflows/{tests,governance,ci}.yml` and its brief is CI workflow consolidation, so a fixer there does not touch the check code. The group that lists `tests/nightly_ha.py` is `R10-DIAG-REPLAY`, at `resume.stage: done`. With no live group owning the fix site, `finding-propagation.md` requires its own `dev/programme/carries/carry-<N>.json` (a destination issue), created as part of this finding.

## Remedy (all before the next review, same head is fine — body + roster only)

1. Route countermeasure A to a destination that owns `tests/nightly_ha.py`, or create `dev/programme/carries/carry-<N>.json`. State its control as a precondition: the staged py-spy that hangs on the first call goes red at the base and green at the fix, and the arms that stay red (no cap, no binary, idle rc=0 with no `_hb_spin`).
2. Land it on `handoff/audit-r10-roster` via `roster_edit.py append-carry` (or the carry file on this branch), and put that branch SHA and the destination group/issue in the body, replacing the prose "The orchestrator appends it as a roster carry".
3. Do the same for the `R10-RCA-FRICTION` finding (the cross-run count), which is also absent from the roster branch, or record it as `dismissed: <reason>`.

## Not re-derived (unchanged from round 1)

The local lane reproduction (1 of 60) and the CPU-second / synthetic-dump figures are the seat's own; the container lane is CI-only and no Docker daemon exists in this seat. The CI-side claims were re-derived at the first review and are unaffected by a body-only change: failed jobs 117649075688 / 117731309720 / 117738343906 are `nightly-ha (stable)` failures with two `py-spy did not run: TimeoutExpired` lines each at digest `sha256:33afb0659d78`, and green jobs 117746567958 / 117731855696 are `success`, `Python v3.14.6`, `py-spy rc=0`, same digest.

## Resolved observations from round 1

- The `## Red checks` section now names and answers `pr-contract` (cheaper detector: `carry_audit.py check --body`, seconds). Answered.
- The stale merge-commit line remains: the `## Head` section still lists `93647bfd9b4c2d940bc87b162bf4159ad2dd6b1e`, which is not an ancestor of the head (the head's merge parent is `f81d96c4`), and still says `202cb8874` "merges origin/main" although that commit adds only the delivery row. Non-blocking; re-take the `## Head` lines. Carry: #2479

## Friction

- The dispatch re-bodied the PR without landing the carry, so the reviewer re-opens a block that the body now satisfies mechanically but the tree does not satisfy substantively. `carry_audit.py` green is not propagation. Carry: R10-RCA-FRICTION
