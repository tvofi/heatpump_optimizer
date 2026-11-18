# `loop_ledger.py`

- `loop_ledger.py` — the convergence record's enumerator (R11-PRE-ROUND-METRICS
  part 2; decision 0018 sections 2 and 4; process cards P7 and L1). Report-only.
  Its rules and null controls are the script's docstring. It reads seven
  roster fields, each written only through `roster_edit.py set-field`, which
  refuses a word outside its vocabulary (`roster_lib.convergence_why`):
  - `found_by` — a finder dimension `D<n>`, `reviewer`, `ci-main`, `owner` or `outside`;
  - `owned_by` — the owning dimension `D<n>`, or `none`;
  - `caused_by` — `{"cause": "#<pr>" | <group> | "external" | "original", "rca": <id>}`,
    the id a record under `dev/audit/rca/` that is one of the group's own `rca`
    records or declares the group its subject in its title and opening paragraph,
    table rows aside (`roster_lib.rca_lists`, `rca_subjects`), so the cause is the
    root-cause seat's, never the fixer's; a group with no `rca` of its own takes
    `caused_by` once a record declares it so, and until then that read stays `unread`;
    a group a record names only later, as a status row or a sibling, is refused;
  - `family` — a class of `dev/audit/config/bugclasses.json`;
  - `cm_kind` — `delete`, `self-heal`, `narrow`, `widen`, `new-refusal` or `policy-text`;
  - `parent` — the roster group this one descends from;
  - `follows` — the fix a re-report follows (a fix that did not fix).

  Every outside group and every hotfix or bug group touching the product owes
  `found_by`, `owned_by` and `caused_by`; any other hotfix group `found_by` and
  `caused_by`; a group with an `rca` record `caused_by`, `family` and
  `cm_kind`. When: the orchestrator sets them at intake and at the RCA's
  landing, and runs

      python3 -I tools/audit/seat/loop_ledger.py [--roster-ref REF]

  at a round's close and weekly; it prints, per round (each roster) and per
  ISO week of roster entry, `escapes` by found_by and owned_by, `injected`,
  `refix` and `loop` (countermeasures by family and cm_kind, k, generations).
  A read whose owing groups are not all recorded prints `unread (k of n ...)`.
  `scorecard.py`'s `E` line prints the owning-dimension split through
  `owned_split`. `--self-test`: the null controls (an empty directory, one
  dropped field per read), the vocabulary refusals, a two-commit history and
  a planted run directory per clearing event of the read below.

  **A cause per red run** (card E11-N-GATE-CAUSE), from the directory
  `round_metrics.py produce` writes, with no API call:

      python3 -I tools/audit/seat/loop_ledger.py --runs <state>/scorecard

  prints `gate_reds`, then one row per run attempt whose `gate` job concluded
  failure, on main's push or on a pull-request head. The cause is derived from
  what cleared the red and is held to the vocabulary a written
  `caused_by.cause` passes (`roster_lib.is_cause`): `external` (a later attempt,
  or a later run at the same `head_sha`, went green) or `#<n>` (main was red:
  the pull request merged at main's first red push run after its last green;
  else the row's own pull request, once a later run of it went green). `unread`
  (a run with no job listing at its latest attempt, a merge subject naming no
  pull request, a head naming none) and `uncleared` (no later green) are read
  states beside them. A derived row is never written to a roster and feeds no
  other read. The order of the tests and the null controls are the script's
  docstring. Each row ends with the attempt's failed jobs and a
  product/machinery column: on a push run, `tools/ci/gate.py`'s `status` over
  that attempt's jobs (`product <v>, machinery <v>`, each green, red or
  unread); on any other run `unread`, because `status` takes an event class
  and `pr` or `pr-cc` is not derivable from a cached run row. Limits: a red
  cleared by a body edit or a review at the same head reads `external`, as a
  re-run does; a fork's run whose `pull_requests[]` is empty at every run of
  its sha reads `unread`; a main red spell already open at the first main run
  in the directory reads `unread` on every row it reaches until a green main
  run is read, because the run that opened it is before the window `produce`
  lists.
