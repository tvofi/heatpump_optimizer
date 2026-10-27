Triage batch 37 rules V125, the STOP result body that reads as an orphan handoff on every pass. The verdict is **ACCEPT narrowed**: `tools/audit/seat/ledger.py`'s `level()` exempts a `handoff-body/` ref whose body commit's first non-blank line is a STOP marker, matched with an optional markdown heading, and counts it as a result body rather than owed. Two arms are REJECTED with their binding cost named: renaming result bodies (the seat that needs it did not read its brief) and suppressing the line in the tick (the strike belongs where the line is computed; the tick prints what the ledger hands it). The ruling also records the zero-code remedy for the instance itself, `ledger.py dispose <ref> <sha40>`, which the orchestrator applied and read back after the ruling. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

The measurement that changes the proposal's own arm: the motivating body's first line is an H1, `# STOP: …`, so a test for a line that *begins* `STOP:` would not match the one ref the proposal was written for. The ruling carries the byte-exact first line and requires the heading form.

## Head

`10ecdefa658330e6ad0f7ab0d157ff1ba4dc27d8`; the file is the whole diff against `524c1896b6943b3da03d6cad61420ced31e14c9c`.

## Mutation proof

`tools/audit/seat/roster_edit.py`'s triage gate is this file's only in-tree consumer, and an ACCEPT is what lets a carry cite it. On the committed file, with `PYTHONPATH=tools/audit/seat`:

```
P205 verdict: ACCEPT
refusal on committed file: None
```

Flipping the verdict line to `DEFER` in an out-of-tree copy prints `mutant verdict: DEFER` and `mutant refusal: dev/programme/triage/s6-batch37.md#P205 is not an ACCEPT ruling (DEFER)`: the gate reads this file's verdict, so an ACCEPT here is what a carry depends on and a DEFER could not be laundered into one.

## Null control

An entry that does not exist (`P999`) prints `dev/programme/triage/s6-batch37.md#P999 is not an ACCEPT ruling (no such entry)`; a missing file prints `the triage ruling dev/programme/triage/s6-batch37.md is not on the roster branch or origin/main`.

## Figures

One line per figure, with the command that printed it.

- `b9b690afb9830a20e046b3515bd18858757d2047 refs/heads/handoff-body/r10-flow-jidoka-p2-body`: `git ls-remote origin 'refs/heads/handoff-body/r10-flow-jidoka*'`.
- the body's first line begins `# S T O P :` (an H1): `git show b9b690afb:BODY.md | sed -n '1p' | od -c`.
- three board lines per pass for that ref — `OWED … handoff-no-pr … ct=1793007293`, `DISPATCH: ? … (25.6h)`, `OWNER FLAG: ? … stranded 25.6h (threshold 12h)` — at 11:09:39Z: the board log `tick.txt` in the orchestrator state directory (instrument output, not re-derived here).
- the manual route applied and read back: `ledger.py disposed <ref> <sha40>` exits 0 for that ref after the orchestrator's dispose at 11:28:57Z, and a `grep` of the relay state directory's `dispositions.tsv` still prints 0 because the store is written beside the ledger's log path, not in the repository or the relay directory — a trap for anyone verifying a dispose.
- the ref-prefix classifier and the exemption list: `grep -n 'ARMS = ' tools/audit/seat/ledger.py` and the `level()` docstring above it.

## Red checks

none

## Forward-carry

- P205 ACCEPT (V125): the STOP result-body exemption in `tools/audit/seat/ledger.py`'s `level()`, with the heading form and its two self-test arms; the owning group is in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-ORCH-LEDGER

## Friction

none
