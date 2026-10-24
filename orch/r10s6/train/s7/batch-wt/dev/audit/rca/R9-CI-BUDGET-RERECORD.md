# R9-CI-BUDGET-RERECORD: three deliberate re-records of `tests/ci_budgets.json` in two days, and the refusal the class now owes

**Instances.** #2160 (2026-10-12/13): the cold-start baseline plus the
gather fix (`run_id` → `workflow_run.id` after the artifacts-list API stopped
returning `run_id`; the broken window admitted the run's own lanes and
double-counted 96 vs a true 63). #2173 at `4d6d329e5` (cherry-picked verbatim
from superseded #2175): `archscore.coord_footprint` 2587 → 2592, grown by
#2118 without re-recording. #2179: `script_runs_per_push` and
`script_runs_full_case_pr` 63 → 68, the lane machinery's own measured cost
with the morning's gather fix already in.

**The question the third instance owed the record:** is this a defect class,
or the ratchet's designed payment? **The recorded refusal:** for
`script_runs_*`, no countermeasure is taken — the budgets were analytic
fail-closed estimates written before any run had emitted artifacts (#2132's
reason field says so), the growth is the lane machinery's own measured cost,
and each re-record's proof is the grade itself (with the committed table the
ratchet rc=1 GREW; with the recorded rows rc=0, everything else held or
tightened — `critical_path_minutes` 61.0 → 54.825 → 45.03). What the refusal
does **not** cover is a fourth instance: the countermeasure that would retire
the class is deriving the `script_runs` rows from a trailing window at
re-record time rather than pinning a point value, which changes what the
budget measures and is the owner's call, not a seat's. Recorded here so the
fourth occurrence triggers that decision instead of a fourth body saying
"designed cost".

**Process state: (d)** for the gather half (the process was sound; its
precondition — the API returning `run_id` — changed underneath it; the
countermeasure is the gather reading the field that still exists), and (a)
for the baseline half (no honest baseline existed to grade against; the
cold-start `--record` pays it once). Each re-record merges only on the
owner's approving review at its head (budget-raise-gate, 0013) — that gate
is the class's standing control, and it held all three times.
