R10-RELAY-SWEEP: the relay's residue in `tools/audit/seat/cloud_relay.sh`, one owning seam (carries 0-8; part of #201). Levels are written before the serial update loops, a body-only handoff prints a level line, a handoff ahead of its body is held, the relay holder leaves the loop's process group, a delivered verdict is not replayed, and a case-colliding `ev/` is refused early.

## Carries

Carry 0: levels written before the serial update loops, exit 75 and body-sha keying, the body-only path kept a function; bash 3.2 empty-array guards in the self-test. Carry 1: the body-only path stays a function the beat job can call unchanged; the handoff-body ledger disposition is not written, as ledger.py has no beat job at this base. Carry 2: both levels are written before the update loop; the tick prints GAP when no-PR OWED lines have no .level file. Carry 3: handoff-body-unapplied is a registered KIND, printed once per pass; a body older than the head prints nothing. Carry 4: the two-REFUSE stub kills M2, the stderr replay row kills M5, and the guides state the grammar, the Code trailer and handoff-body-stale. Carry 5: the relay holder calls setpgid; tick_loop's self-test sends TERM to the group. Carry 6: relay() skips a probe whose tree review/<pr> already carries, with the RCA at dev/audit/rca/R10-RELAY-REPLAY.md; the state dir and ledger path are printed per pass. Carry 7: HELD-BODY holds a handoff whose body does not name its tip, and the hold file reports MERGED or CLOSED lines as handoff-hold-stale. Carry 8: see Carry 9 below. Carry 9 (the packet counts from 1, so it is the brief's last carry, headed 'Case-insensitive evidence collision'): relay() and bus.sh refuse case-colliding ev/ names, and fix-review.md states the unique-name rule.

## Head

0953e9ce5356da2b08bafc8da32e81b47f4175f9 (the wip tip 46ea96ca5 merged with origin/main 30638cf0c; merge, never rebase). The relay and tick_loop self-tests were re-run at this head.

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
