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
  dropped field per read), the vocabulary refusals and a two-commit history.
