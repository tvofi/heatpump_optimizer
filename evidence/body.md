Adds `dev/programme/triage/s6-batch14.md`: one ruling, P83 (S6-V18, a cloud pool run ends its turn while a background job is pending), under `dev/governance/roles/proposal-triage.md`. The file is under `dev/programme/`, which `tests/closure.py` lists as INERT, the route the earlier batches took.

Verdict: P83 REJECT, re-ruled before merge. The first ruling (ACCEPT NARROWED to R10-FLY-CLOUD-WAIT at fe155d28) is withdrawn. The run log of cse_01SeVeYCKsQwZTCi9e1C7Vv4 shows that a cloud run is resumed by its own background-task notifications, so the setup line in `cloud_dispatch.py` is correct, and the one real cost (a duplicate reviewer) came from the sweep reading `worker_status` idle as ended. The idle-reclaim candidate stays REJECTED (P55's race). A run-log liveness instrument is DEFERRED until the #2750 run log is re-checked or a further duplicate refire is found. No group and no carry.

## Head

`06cb984bdc0172bdd8eceda1ba55de0e67b4830e`, on merge base `87ecf385b`. That is the ruling commit `c130c242` plus one commit holding only this PR's own delivery row, `dev/programme/delivery/2755.md`.

## Mutation proof

n/a: no code or check changes; the file is a ruling record. Its consumer is the triage gate: `roster_edit.ruling_verdict` reads the one entry (P83 -> REJECT).

## Null control

`roster_edit.ruling_verdict` on a pid the file lacks (`P99`) returns None. The ruling carries no carry text, so there is nothing for brief_lint to check.

## Figures

- Entries and verdicts: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch14.md | sort | uniq -c` (1 REJECT).

## Red checks

none at the body's head. At 06cb984 before this body re-take, `pr-contract` (job 120962100585) and `gate` (job 120962222537) were red only because `## Head` named c130c242. That is settled by this body edit; the tree is unchanged.

## Forward-carry

n/a: REJECT and DEFER rulings route nothing to the roster.

## Friction

none
