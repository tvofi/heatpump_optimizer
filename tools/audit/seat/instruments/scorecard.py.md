# `scorecard.py`

- `scorecard.py` — the convergence scorecard (R10-MACH-SCORECARD): ten
  report-only lines, one per signal, the baseline from which thresholds can
  later be set. No line sets an exit code or holds a merge. It is read-only on
  every input and makes no GitHub call; an input it cannot read prints
  `<line>  unread (<why>)`, never a guessed value. The lines:
  - `A_gate` — the share of the last 20 concluded main `CI` runs whose job
    `gate` succeeded (a run with no cached job listing is `unread`).
  - `A_run` — the share of the same runs whose run conclusion is success.
  - `Y_rev` — over the last 50 pull requests, the share whose first review
    verdict (the earliest by `t`, whatever the order of `verdicts.json`) is `merge`.
  - `M_first` — over the same 50, the share whose first verdict is `blocked`
    in a machinery family (carry, body, CI state, merge state, root-cause
    form, ruling or roster).
  - `Y_train` — over the last 50 merges the merge train named, the share
    never on a `SKIP #n` or `PARK` line.
  - `H` — hotfix-token merges among the last 50 code merges (production or
    instrument), with the production merges among them beside it. It has no
    null control: it is a naming measure, a branch token, read with that caveat.
  - `S` — size: `machinery_ratchet.py --measure` (non-production merges per
    window, churn per 1 000 product lines) and machinery lines over product lines.
  - `E` — roster groups whose source is `outside` and hotfix or bug groups
    touching the product, and how many of both are still open.
  - `C` — the longest run of consecutive cancelled main runs in the last 50.
  - `K` — `recycle` lines of the standing dispatch and triage seats in the
    day's sweep record.

  Every line but `H` is held in `--self-test` to a null control (a case whose
  right answer is the quiet one). Inputs sit under `<state>/scorecard/`
  (`runs.json`, `jobs/jobs_<id>.json`, `verdicts.json`, `merges.tsv`,
  `roster.json`) beside the overlay's `train_log` and the optional
  `sweep_record`. When: the beat's `scorecard` row runs `report --dir
  <state>/scorecard --train-log <train_log> --repo <checkout>` (plus
  `--sweep-record` when the overlay names one) once a day and writes the
  output to `S/beatd/scorecard.txt`; the digest hears only
  `scorecard: UNREADABLE rc=<n>: <why>` when the run fails. `--self-test`:
  planted and null cases per line, and one mutant per predicate.
