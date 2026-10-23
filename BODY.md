Session s4 kept its proposals and 25 draft triage rulings out of the tree, which `dev/governance/roles/proposal-triage.md` does not allow: a ruling lives in a batch file under `dev/programme/triage/`, and `tools/audit/seat/roster_edit.py`'s triage gate reads it from there. `dev/programme/triage/s4-batch1.md` recorded P1-P4. This adds `dev/programme/triage/s5-batch1.md`: every other s4 proposal, plus the assessor's #2569 proposal, re-ruled from the contract as P5-P33, each `Source:` line naming its s4 label. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route `s4-batch1.md` took.

Rulings re-derived, not copied. Verdicts that differ from s4's drafts: P13 (s4 P-A, ACCEPT) is DEFER, because the s4 log records the `--group` path with a 3-line trigger already taking the token saving; P26 (s4 P-N), P28 (s4 P-P), P21 (s4 P-I) and P25 (s4 P-M) are ACCEPT where s4 drafted DEFER, because each now has measured instances (opener logs, a third stale-tools instance, a measured 3.5 h loss, a phantom slot still live at the base). P33 (an undrained approved record PR) had no s4 ruling; #2653 is a live second instance.

## Head

`9cfd290c2a6f7703154baaa6bac9c499d9579561`, on origin/main `27b59c9f7`; roster read at origin/handoff/audit-r10-roster `e4c92864f`.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its one consumer is the triage gate: `roster_edit.ruling_verdict` reads all 29 entries (P5 to P33) with the verdict each states, and `roster_edit.triage_refusal` passes the three ACCEPT carry texts this ruling routes.

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P34`) returns None, and `triage_refusal` refuses a carry citing a DEFER entry (`#P13`), so the gate distinguishes the verdicts this file states.

## Figures

- Verdicts per class: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s5-batch1.md | sort | uniq -c`.
- Entries: `rg -c '^## P' dev/programme/triage/s5-batch1.md`.
- s4's draft rulings: `rg -c '^## ' triage.md`, run in the s4 orchestrator's scratch directory (out of tree; the file is not tracked).
- Lettered-label carries citing no ruling: `git show e4c92864f:dev/programme/rosters/wave-r10-groups.json | jq -r '.groups[].carry[]? | strings' | rg -c -i '\btriage\b[^.]{0,40}\bP-[A-Q]\b|^P-[A-Q] \(triage'`.

## Red checks

none

## Forward-carry

- P14's reconciling text for carries 2 and 5 (tick_loop.sh restart), to append with `roster_edit.py append-carry`, cites `dev/programme/triage/s5-batch1.md#P14`. Carry: R10-FLY-RELAY-REVIEW-FF
- P21's deletion rule for the handoff-wip step-push prefix (closes carry 5's open decision), cites `#P21`. Carry: R10-FLOW-DESIGN-STAGES
- P33's ledger entry for an approved record or autofix pull request open past 30 minutes, cites `#P33`. Carry: R10-ORCH-LEDGER
- The triage gate in `tools/audit/seat/roster_edit.py` matches only numbered labels with `PROPOSAL_RE`, so 19 carries at roster `e4c92864f` naming a lettered s4 label (P-A to P-Q) landed with no ruling cited, most after decision 0015 (`b16084794`); 'Triage P5' matches the regex and 'Triage P-A' does not. Carry: R10-ORCH-ROSTER-SCHEMA

## Friction

none
