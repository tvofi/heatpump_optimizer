# R10-RCA-FAMILY-SCRATCH-INSTRUMENTS: reusable instruments that lived only in session scratch

Round-end family analysis (loop card L8). The family is a process one: decision 0013 says a
reusable instrument lands in the tree, never only in scratch, and round 10 closed on several
that never did. Measured at `origin/main` `a39627da59` on 2026-11-15. Lands no code.

## 1. Instances

The prototype inventory in `dev/programme/HANDOVER.md` ("Local prototype inventory") and the
sweep log name, among others: the landing chains `chain_one.sh`, `chain_one_v2.sh`,
`chain_after_green.sh` and the ruleset-release `land.sh` (`$HPO_STATE_DIR/s14/bypass/`); the wake
filter `wake_filtered.sh`; the dispatch seats' `disp.sh`, `verify.sh`, `relayc.sh`, `watch4.sh`
and their siblings (`seat/dispatch-s15-*`); the closure runbook's eleven scripts; `build_tabs.py`;
`train_guard.sh`; `pubfix.sh` and `partline_fix.sh`; the detached watch-mode relay. More than
twenty, each used for days; the gating merges of 2026-11-15 (#3593, #3451) landed through two of
them (sweep lines 2603, 2612).

## 2. Named cause

Two rulings meet: tvofi's 2026-11-13 freeze shape ("prototype local fixes in-round, file
proposal permanent fixes for consolidation and cost/benefit that is carried to the start of next
round") and decision 0013. The freeze keeps a fix out of the tree during the round by design;
0013 forbids the instrument living only in scratch. No step said where a prototype lives between
the two, or who disposes of it at round end.

## 3. Process state: (d)

0013 was sound when instrument fixes merged in-round; its precondition (that a reusable
instrument has a path into the tree during the round) changed with the freeze. Not (b): seats
followed the freeze.

## 4. Class reach

Every round from 11 on, by the same freeze.

## 5. Cost test

- cost(defect): a prototype that dies with its session (the chains carry a session scratch path
  in their first lines) is rebuilt or lost; an undisposed one is a second instrument beside the
  tracked one.
- cost(countermeasure, recurring): none beyond what is already owed.

## 6. Countermeasure: none new, recorded

R11-PRE-MACHINERY-LIMITER's carry 2 already owes the sentence: "State where the proposals file
and the prototypes live so the next orchestrator finds them from the playbook". This round-end
batch rules on every prototype round 10 left (triage
`dev/programme/triage/r10-round-end.md#P789` to `#P794`); tvofi kept one set session-local on
purpose (card C9: the landing chains and `land.sh` stay local until a benchmark against the
merge train reads), so "in scratch" is a ruled state for them, with an owner and an end. Building a separate check would add a
refusal for a disposal that the round-end triage now does once a round; L2 orders that last.
