Triage batch 57 rules, as P268, the owner's fourth and fifth amendments to V181 (2026-10-28T19:54:02Z and 19:59:53Z) and the owner's clarification of the fifth. The ruling is ACCEPT narrowed, in three carries.
- Every user-submitted finding is a hotfix.
- An instrument that saves at least 12 h ranks with production.
- Only each group's priority mapping lives in the roster. The tier order may stay in P267's `dev/audit/config/ci_priority.json`.

The default order is main push > CP and hotfix > production plus instruments saving at least 12 h > other instruments by savings. Batch 56 (`86d399b50`) was already pushed, so it does not move. This ruling amends P267.

- **One store per fact.** P267's file held per-group data: a `savings_h` map and `hotfix_prefixes`. Under the clarification, those move to the roster, and the file keeps only the order and its knobs. The plan already has tiers (`tools/plan/replan.py:316` `dispatch_tier`, with production by lane) and a sourceless numeric `savings`. P268 makes `ci_priority.tier()` the one class rule, and it reads each group's mapping only through `roster_lib`.
- **R10-ORCH-ROSTER-SCHEMA: the mapping.**
  - New fields: `source` (`user` means a finding submitted by the owner or an end user, which makes the group a hotfix) and `savings_source`, which is required with `savings`. The existing `class` is kept.
  - New readers `roster_lib.is_hotfix`, `savings_h` and `group_class`.
  - `append-group` requires `source`, and a restricted `set-field` op is added.
  - Backfill marks "Owner-reported" and "User-reported" briefs as source user; the live one is R10-UX-HEALTH. Issue authorship cannot decide this, because the orchestrator files issues with the owner's token.
- **R10-FLOW-TOOLKIT-MODEL: the plan calls `ci_priority.tier()`.** It prints every group whose tier changes as production moves from lane to `class`.
- **R10-TRAIN-OVERLAP-GRADE: the setting.**
  - `ci_priority.json` keeps the order only, with no group-keyed data. A setting that holds a group map is refused.
  - `ci_priority.py`'s `tier()` is the one rule. The rest of P267 stands.
- **Re-pointed held texts.** R10-FLOW-WIP and R10-ORCH-LEDGER call `ci_priority.rank`. The R10-FLY-CANCEL-SWEEP brief reads the setting's `never_cancel`, and the mapping from the roster.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`9051091b67d051a6782ec665b412bf5f5974e670`; the file is the whole diff against `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`. This head fast-forwards the first pushed cut `d3ae03989` (fourth amendment only), and no pull request carried that ref.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P268 as `ACCEPT`.
- The gate passes all seven held texts citing `#P268`: the three carries, the re-pointed R10-TRAIN-OVERLAP-GRADE, R10-FLOW-WIP and R10-ORCH-LEDGER carries (which also cite `#P267`), and the R10-FLY-CANCEL-SWEEP brief (`#P266`, `#P267` and `#P268`).
- Mutant (the verdict rewritten to `DEFER` in a copy): the R10-ORCH-ROSTER-SCHEMA carry is refused, `#P268 is not an ACCEPT ruling (DEFER)`, so the gate reads this line.

## Null control

With the file absent, the same carry returns `the triage ruling dev/programme/triage/s6-batch57.md is not on the roster branch or origin/main`.

## Figures

- `tools/plan/replan.py`: `dispatch_tier` at line 316, `dispatch_key` at line 327, the `savings` read at line 395, and `PRODUCTION` at line 100.
- Roster `be898eaef`:
  - `class` counts: instrument 95, owner 14, production 13, rca 12, policy 9, study 7, process 7, and none 7.
  - No group has a `source` or `hotfix` key.
  - 11 briefs open "Owner-reported", "Owner request" or "User-reported"; 2 of them are live.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P268 ACCEPT narrowed (V181 fourth and fifth amendments): the per-group mapping lives in the roster. It adds the `source` and `savings_source` fields, the `roster_lib.is_hotfix`, `savings_h` and `group_class` readers, `append-group` requiring `source`, a restricted `set-field` op and the backfill (`tools/audit/seat/roster_lib.py`). Carry: R10-ORCH-ROSTER-SCHEMA
- P268 ACCEPT narrowed (V181 fourth and fifth amendments): replan's tiers call the setting reader's `tier()` and print every tier change (`tools/plan/replan.py`). Carry: R10-FLOW-TOOLKIT-MODEL
- P268 ACCEPT narrowed (V181 fourth and fifth amendments): P267's setting holds the order only, and its reader's `tier()` is the one rule, reading the mapping from the roster (`tools/audit/seat/merge_train.py`). Carry: R10-TRAIN-OVERLAP-GRADE

## Friction

none
