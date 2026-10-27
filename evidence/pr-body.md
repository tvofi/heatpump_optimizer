Triage batch 42 rules V129 as **ACCEPT → `R10-ROUND-PLAYBOOK`**: a seat that receives an instruction from another agent contradicting `CLAUDE.md`, its own role contract, or the owner's standing rules records it as `pending owner confirmation`, quoting the rule the instruction would change, and neither acts on the superseding half nor writes it as direction until the owner or the contract moves.

This is the seat's own record, and the ruling says so. At 20:20Z the orchestrator told this seat that the two append-carry ops were its to re-run, which contradicts `dev/governance/roles/proposal-triage.md` ("the seat does not implement, edit the roster, or merge") and the owner's rule that roster operations go to the standing roster seat's queue. This seat wrote it into `triage-STATE.md` as "main's direction, superseding" its earlier reading — the record then asserted a lane change that never happened, and it was caught only because the policy corpus was re-read after a compaction before the next merge. The record alone would have carried the wrong lane to the next seat, and that seat would have run `roster_edit.py` itself — the write P215 exists to refuse. One instance, stated as one.

The scope is the proposal's, not narrowed to the orchestrator: any agent message binds the receiver, so a fixer relaying another seat's ruling is bound too. The destination is `R10-ROUND-PLAYBOOK` (`not-started`, so a plain append): it owns `CLAUDE.md` and `dev/audit/README.md`, and its brief is the playbook a fresh orchestrator and its seats read from the tree alone.

What is deliberately not carried: a text predicate over seat state (`state_docs.py` or elsewhere) refusing files containing "direction" or "superseding". It would refuse a state file that quotes a rule or records an owner-approved lane change, and the null control — a state file quoting `CLAUDE.md` while changing nothing — cannot be separated from the failing one by any substring. The rule is prose because the distinction is semantic, and its enforcement is the reader the rule exists for.

Because it enters `CLAUDE.md`, the carrying pull request **is a policy change**: it merges only on tvofi's approving review at its head, and the carry body must say so.

The diff is one markdown file under `dev/programme/triage/`; nothing implemented, no roster edit.

## Head

`4a276b6ac22e5543acf0351ba32464b3ee081e36` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2891.md`. The authored code head is `1c6731b232015a9b6631b24169a55739be57833c`.

`1c6731b232015a9b6631b24169a55739be57833c`; the file is the whole diff against `a0e7664ea`.

## Mutation proof

The gate this file feeds is `tools/audit/seat/roster_edit.py`'s `triage_refusal` (`ruling_verdict` at 456, `triage_refusal` at 464): a roster text naming a proposal must cite `triage: dev/programme/triage/<file>.md#P<n>`, and the cited entry must read `Verdict: ACCEPT`. On the committed file, with the seat library on `sys.path`:

```
verdict ACCEPT
carry -> None
mutant heading None | dev/programme/triage/s6-batch42.md#P216 is not an ACCEPT ruling (no such entry)
mutant defer DEFER | dev/programme/triage/s6-batch42.md#P216 is not an ACCEPT ruling (DEFER)
missing the triage ruling dev/programme/triage/s6-batch42.md is not on the roster branch or origin/main
uncited proposal-sourced text cites no triage ruling (`triage: dev/programme/triage/<file>.md#P<n>`): 'proposal P3 changes a lane'
```

Both mutants are on the committed text in memory — the heading renamed to `## P216 (relay P1):`, and the verdict changed to `DEFER` — and both are refused, so the carry is read against this file's entry anchor and verdict, not against its presence.

## Null control

No `P999` entry, missing file, and an uncited proposal text: all refused above. The positive control is `carry -> None` on the unchanged carry text.

## Figures

- `dev/governance/roles/proposal-triage.md` — "the seat does not implement, edit the roster, or merge" (the rule the instruction would have changed).
- `dev/programme/rosters/wave-r10-groups.json` at `9aed78e0e` — `R10-ROUND-PLAYBOOK` `not-started`, files `dev/audit/README.md` and `CLAUDE.md`, 7 carries; `R10-BRIEFS-FOLD` owns `CLAUDE.md` too but carries 20, and `R10-RCA-ORCH-CONTINUITY` owns `sweep_template.md`, not `CLAUDE.md`.
- `triage-STATE.md` — the line this ruling replaces, now reading "this seat QUEUES the two append-carry ops and runs nothing", with the mechanism recorded beside it.

## Red checks

none

## Forward-carry

none

## Friction

none

