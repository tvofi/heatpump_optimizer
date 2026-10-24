Adds `dev/programme/triage/s6-batch3.md`: the s6 orchestrator's proposal S6-T (the opener re-runs prepr under the gate lease) ruled as P53 under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdict: P53 ACCEPT narrowed to `R10-FLY-OPENPR-ATOMIC` (the opener's second push takes `--row-only`); the stamp (a) and cloud-prepr (b) candidates are DEFERRED pending a measured queue wait.

## Head

`6cab77593df6e32cf2e44b8b240e8a0050a130de`, on origin/main `50af6174f`; roster read at origin/main.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the one entry.

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P54`) returns None.

## Figures

- Entries and verdicts: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch3.md | sort | uniq -c` (1 ACCEPT).
- The two opener pushes: `rg -n 'app_push|_push' tools/audit/seat/open_pr.sh`; the row-only precedent: `rg -n 'row-only' tools/audit/seat/update_pr.sh`.

## Red checks

none

## Forward-carry

- P53's carry (`open_pr.sh`'s second push passes `--row-only`, with a self-test row and null control), cites `dev/programme/triage/s6-batch3.md#P53`. Carry: R10-FLY-OPENPR-ATOMIC

## Friction

none
