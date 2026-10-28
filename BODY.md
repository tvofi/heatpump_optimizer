Triage batch 57 rules V183 as P269 and V184 as P270 (below), and, as P268, the owner's fourth and fifth amendments to V181 (2026-10-28T19:54:02Z and 19:59:53Z) and the owner's clarification of the fifth, together with the owner's hotfix definition and its sixth amendment, as the owner corrected it. The ruling is ACCEPT narrowed, in three carries. This is the open rolling batch under V182.
- A hotfix is one of five things, under the owner's definition and sixth amendment: a user-submitted bug touching production code; a feature request the owner explicitly calls a hotfix; a critical bug found in the fixing phase; a bug making main red on a required check (the owner's correction); or a CI or machinery bug that deadlocks all merges. `hotfix_by` records which rule applied, with its evidence. Not every "Owner request" brief qualifies.
- An instrument that saves at least 12 h ranks with production.
- Only each group's priority mapping lives in the roster. The tier order may stay in P267's `dev/audit/config/ci_priority.json`.

The default order is main push > CP and hotfix > production plus instruments saving at least 12 h > other instruments by savings. Batch 56 (`86d399b50`) was already pushed, so it does not move. This ruling amends P267.

- **One store per fact.** P267's file held per-group data: a `savings_h` map and `hotfix_prefixes`. Under the clarification, those move to the roster, and the file keeps only the order and its knobs. The plan already has tiers (`tools/plan/replan.py:316` `dispatch_tier`, with production by lane) and a sourceless numeric `savings`. P268 makes `ci_priority.tier()` the one class rule, and it reads each group's mapping only through `roster_lib`.
- **R10-ORCH-ROSTER-SCHEMA: the mapping.**
  - New fields:
    - `source`: `user` means an item submitted by the owner or an end user. It is not a hotfix by itself.
    - `hotfix`: true only under one of the five rules: `user-production-bug`, `owner-called`, `fixing-phase-critical`, `main-red-required` or `merge-deadlock`. `hotfix_by` holds `{rule, evidence}`.
    - `savings_source`: required with `savings`.
    - The existing `class` is kept.
  - New readers `roster_lib.is_hotfix`, `touches_production`, `savings_h` and `group_class`.
  - `append-group` requires `source`. The validated `set-field` op refuses a hotfix with no rule or no evidence, and refuses `user-production-bug` off production.
  - Backfill: "Owner-reported", "User-reported" and "Owner request" briefs get source user.
    - R10-UX-HEALTH is a hotfix: a production UI bug report, with all three files under `custom_components/`.
    - R10-ROUND-PLAYBOOK is not a hotfix.
  - Issue authorship cannot decide `source`, because the orchestrator files issues with the owner's token.
- **R10-FLOW-TOOLKIT-MODEL: the plan calls `ci_priority.tier()`.** It prints every group whose tier changes as production moves from lane to `class`.
- **R10-TRAIN-OVERLAP-GRADE: the setting.**
  - `ci_priority.json` keeps the order only, with no group-keyed data. A setting that holds a group map is refused.
  - `ci_priority.py`'s `tier()` is the one rule. The rest of P267 stands.
- **Re-pointed held texts.** R10-FLOW-WIP and R10-ORCH-LEDGER call `ci_priority.rank`. The R10-FLY-CANCEL-SWEEP brief reads the setting's `never_cancel`, and the mapping from the roster.
- **P269 (V183, owner-directed 2026-10-28T20:20:27Z): ACCEPT narrowed, into a new fly-in, R10-FLY-TRAIN-DEFAULTS.**
  - The recommended train flags are written in three places that disagree today: `standing-merge.md` line 9, `merge_train.py`'s `AUTO_TRAIN_FLAGS` (the sweep-started train), and `train.sh`, which defaults every flag off.
  - One `RECOMMENDED` tuple will hold the set. `train.sh` and the sweep default to it, and each flag gets an explicit `--no-*` switch. The mandate is read from `$STATE_DIR/mandate` and still checked by the gate at every merge.
  - `standing-merge.md` names the set by reference. That line is policy, so the group's PR merges on tvofi's approving review.
  - It is a new group, because `train.sh`'s owners are done and the live `merge_train.py` owner is the M group that already carries P267 and P268.
- **P270 (V184, owner-approved 2026-10-28T20:28:06Z): DEFER, to the orchestrator's measurement seat, whose report amends V184.**
  - `cloud_dispatch.py` `_prompt` (line 107) puts the PR, head and nonce in its first sentence, and repeats the head at lines 120, 123 and 130. No two seats share a prefix past that sentence.
  - Local briefs are already stable-first: the seat preamble's line 13 marks where the variable brief starts.
  - If the numbers clear the bar, the reorder goes to R10-FLOW-DESIGN-STAGES, the one live owner of `cloud_dispatch.py`.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`604d38bf64fa69ec3d34cc772891421f0b80a26d`; the file is the whole diff against `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`. This head fast-forwards the last pushed head `a22006cf4` with three commits: P270, the owner's sixth amendment folded into P268, and the owner's correction to its case (b). Batch 56 (#2931, P267) is unchanged and merges on its own verdict.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P268 and P269 as `ACCEPT`, and P270 as `DEFER`.
- The held R10-FLY-TRAIN-DEFAULTS brief, which cites `#P269`, passes. With P269's verdict rewritten to `REJECT`, it is refused, `#P269 is not an ACCEPT ruling (REJECT)`.
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
  - R10-UX-HEALTH's three files are all under `custom_components/`. R10-ROUND-PLAYBOOK's are `dev/audit/README.md` and `CLAUDE.md`.
- `merge_train.py`: `AUTO_TRAIN_FLAGS = ("--bot-prs", "--approval-carry", "--pre-flight")`; `standing-merge.md:9` names `--overlap --bot-prs --approval-carry --skip-bad --free-holders`; `train.sh` is 398 lines.
- `cloud_dispatch.py` `_prompt`, `sed -n 107,160p | wc -c`: 4872 bytes.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P268 ACCEPT narrowed (V181 fourth and fifth amendments): the per-group mapping lives in the roster. It adds the `source`, `hotfix`, `hotfix_by` and `savings_source` fields, the `roster_lib` readers, `append-group` requiring `source`, a validated `set-field` op and the backfill (`tools/audit/seat/roster_lib.py`). Carry: R10-ORCH-ROSTER-SCHEMA
- P268 ACCEPT narrowed (V181 fourth and fifth amendments): replan's tiers call the setting reader's `tier()` and print every tier change (`tools/plan/replan.py`). Carry: R10-FLOW-TOOLKIT-MODEL
- P268 ACCEPT narrowed (V181 fourth and fifth amendments): P267's setting holds the order only, and its reader's `tier()` is the one rule, reading the mapping from the roster (`tools/audit/seat/merge_train.py`). Carry: R10-TRAIN-OVERLAP-GRADE
- P269 ACCEPT narrowed (V183): a new fly-in, R10-FLY-TRAIN-DEFAULTS, adds one `RECOMMENDED` tuple, defaults it on in `train.sh` and the sweep with `--no-*` switches, reads the mandate from the state dir, and has `standing-merge.md` name the set by reference (`tools/audit/seat/train.sh`). The group does not exist until its held `append-group` op lands after this file is on main. Carry: dismissed: registered by the held append-group op after merge

## Friction

none
