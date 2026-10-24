Adds `dev/programme/triage/s6-batch2.md`: eight proposals from the s6 orchestrator's `proposals.md` (the s5 items I-M that `s5-batch2.md` never ruled, and s6's Q, R and S6-S) ruled as P45-P52 under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdicts: P45 ACCEPT, P46 ACCEPT narrowed, P51 ACCEPT narrowed (all three to the existing `R10-ORCH-BEATD`; the file says the work may later be split into its own group); P49 ACCEPT (measure first) to `R10-FLOW-RECORD-PITCH`; P47 and P48 DEFER; P50 and P52 REJECT.

## Head

`e06c58981e10fae40a077294c8af41f4485dadaf`, on origin/main `50af6174f`; roster read at origin/handoff/audit-r10-roster `4c54758d7`.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the eight entries.

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P52`) returns None, and a carry citing a DEFER entry (`#P47`) is refused, so the gate distinguishes the verdicts this file states.

## Figures

- Verdicts per class: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch2.md | sort | uniq -c`.
- Entries: `rg -c '^## P' dev/programme/triage/s6-batch2.md`.
- P49 share of record merges: the `git log ... | grep -c record/autofix` line in P49's `Instances:`, run at origin/main `50af6174f`.

## Red checks

none

## Forward-carry

- P45, P46 and P51 (the standing seats' sweep template, `pulse.py --seat-alive` arm and Wait paragraph), cite `dev/programme/triage/s6-batch2.md#P45`. Carry: R10-ORCH-BEATD
- P49's carry (record chain: measure whether a record-only merge owes a row, then end the chain), cites `#P49`. Carry: R10-FLOW-RECORD-PITCH

## Friction

none
