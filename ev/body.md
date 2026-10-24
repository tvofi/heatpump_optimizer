Adds `dev/programme/triage/s6-batch15.md`: one ruling, P84 (S6-V19, parallel record and policy merges run through hand-rolled shell), under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdict: P84 ACCEPT NARROWED -> R10-TRAIN-UPGRADE, the owner-ordered group, already dispatched. Re-scoped before merge: the first ruling at cf58e6a8 named a new group, R10-FLY-TRAIN-POLICY-APPROVE, which is withdrawn, and the accepted change folds into the owner's train-upgrade order. Under a numeric `--mandate` in force for policy, `merge_train.py` posts the citing owner approval that its own `policy_gate` already requires, so policy heads land on-train. A separate `merge_par.py` lane stays REJECTED. Triage and record heads need no change, because `policy_lint.mjs --corpus-filter` classes them as non-policy and `--bot-prs` already carries record PRs. The owner's order sets the group's wider scope (sequenced batches, loading a running train), which this ruling does not rule.

## Head

`feb44bd885e566535671469ee95c2b0556676290`, on merge base `a260e5630`.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the one entry (P84 -> ACCEPT).

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P99`) returns None. The carry text was linted by `node tools/policy/brief_lint.mjs` as the brief and carry of a not-started R10-TRAIN-UPGRADE in a scratch copy of the roster: 0 errors. The same copy with the carry's `merge_train.py` path replaced by an unresolvable one gave 1 error, so the linter does read that text.

## Figures

- Entries and verdicts: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch15.md | sort | uniq -c` (1 ACCEPT).

## Red checks

none

## Forward-carry

n/a: once this file is on main, the orchestrator routes the carry through `roster_edit.py`, citing this file.

## Friction

none

