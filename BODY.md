Triage batch 57 rules the owner's fourth amendment to V181 (2026-10-28T19:54:02Z) as P268: ACCEPT narrowed, in three carries. Every user-submitted finding is a hotfix at intake. An instrument PR that is critical, or saves at least 12 h, ranks with production. The default order becomes main push > CP and hotfix > production plus instruments saving at least 12 h > other instruments by savings. Batch 56 (`86d399b50`) was already pushed, so this is a separate ruling and batch 56's head does not move.

- **One tier rule, not two.** `tools/plan/replan.py:316` `dispatch_tier` already has the owner's tiers (0 the critical path, 1 production, 2 the rest), and it ranks tier 2 by the roster's numeric `savings` (line 395). P267's setting had defined its own classes. P268 makes `dispatch_tier` the single rule, and `ci_priority.py` imports it.
- **R10-ORCH-ROSTER-SCHEMA: the fields.**
  - New fields `source` (`user`, `audit` or `programme`) and `savings_source`, which is required whenever `savings` is set.
  - New readers `roster_lib.is_hotfix`, true for source user or an `R10-HOTFIX-` name, and `savings_h`.
  - `append-group` refuses a group without `source`, and a restricted, validated `set-field` op is added.
  - Backfill marks "Owner-reported" and "User-reported" briefs as source user. The live one is R10-UX-HEALTH. Issue authorship cannot decide this, because the orchestrator files issues with the owner's token.
- **R10-FLOW-TOOLKIT-MODEL: the plan.**
  - Tier 0 adds hotfix.
  - Tier 1 adds groups whose savings reach `major_savings_h`, which defaults to 12 and is read from `dev/audit/config/ci_priority.json`.
- **R10-TRAIN-OVERLAP-GRADE: P267's setting, amended.**
  - The order becomes `main-push`, `cp-hotfix`, `tier1`, `instrument`, mapped to replan's tiers.
  - The config-local `savings_h` map and `hotfix_prefixes` are dropped.
  - Everything else in P267 stands.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`d3ae0398983beb27f9fb98265c155c545c980975`; the file is the whole diff against `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P268 as `ACCEPT`.
- The three queued carries citing `#P268` pass the gate.
- Mutant (the verdict rewritten to `REJECT` in a copy): the R10-ORCH-ROSTER-SCHEMA carry is refused, `#P268 is not an ACCEPT ruling (REJECT)`, so the gate reads this line.

## Null control

With the file absent, the same carry returns `the triage ruling dev/programme/triage/s6-batch57.md is not on the roster branch or origin/main`.

## Figures

- `tools/plan/replan.py`: `dispatch_tier` at line 316, `dispatch_key` at line 327, the `savings` read at line 395, and `TIER_CRITICAL, TIER_PRODUCTION, TIER_OTHER = 0, 1, 2` at line 105.
- The roster at `be898eaef` has no `source` or `hotfix` key. 11 briefs open "Owner-reported", "Owner request" or "User-reported". Of those, 2 are live: R10-UX-HEALTH and R10-ROUND-PLAYBOOK.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P268 ACCEPT narrowed (V181 fourth amendment): the roster fields `source` and `savings_source`, `roster_lib.is_hotfix` and `savings_h`, `append-group` requiring `source`, a restricted `set-field` op, and the backfill (`tools/audit/seat/roster_lib.py`). Carry: R10-ORCH-ROSTER-SCHEMA
- P268 ACCEPT narrowed (V181 fourth amendment): `dispatch_tier`'s tier 0 adds hotfix, and tier 1 adds instruments saving at least 12 h. It becomes the one tier rule (`tools/plan/replan.py`). Carry: R10-FLOW-TOOLKIT-MODEL
- P268 ACCEPT narrowed (V181 fourth amendment): P267's setting order becomes main push, cp-hotfix, tier1, instrument, from replan's tiers, and its config-local savings and prefixes are dropped (`tools/audit/seat/merge_train.py`). Carry: R10-TRAIN-OVERLAP-GRADE

## Friction

none
