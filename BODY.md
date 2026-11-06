R10-RELAY-SWEEP: the relay's residue in `tools/audit/seat/cloud_relay.sh`, one owning seam (carries 0-8; part of #201). Levels are written before the serial update loops, a body-only handoff prints a level line, a handoff ahead of its body is held, the relay holder leaves the loop's process group, a delivered verdict is not replayed, and a case-colliding `ev/` is refused early.

## Head

1aabe264a9288492a83a85cd46bc9a14824e7b70 (the wip tip 46ea96ca5 merged with origin/main b36679cea; merge, never rebase).

## Mutation proof

The relay self-test pins each carry with a planted control and a null control: `bash tools/audit/seat/cloud_relay.sh --self-test` reads 367 checks, 0 failed, at this head. The carry-4 mutants M2 (`tail -n 1` to `head -n 1`) and M5 (the `cat update.out` replay) are now killed by the two-REFUSE stub and the "whole output reaches the relay's stderr" rows. The tick_loop self-test row for the group TERM reads 27 checks, 0 failed. I did not re-run the mutants by deleting lines in this session; the prior seat's rows carry that proof.

## Null control

A body tip older than the head prints nothing, a body naming the new tip updates, distinct `ev/` names relay, a new tree is pushed, and a relay finishing inside HPO_TICK_RELAY_WAIT is reaped as before; all are self-test rows. The 93-probe replay origin was not re-run in this session.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

This diff edits `dev/governance/roles/fix-review.md`, which is policy; the owner's approving review at the head is pending.
