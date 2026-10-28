# Proposal triage, session s7, batch 57 (P268)

One entry, covering the owner's fourth and fifth amendments to V181, quoted from `proposals.md`
as it stands.

The fourth amendment (2026-10-28T19:54:02Z):
- Every user-submitted finding (an issue or report from the owner or end users, not an audit
  seat's) is a hotfix and takes the hotfix tier.
- Correcting the third amendment, an instrument PR that is critical, or saves at least 12 h, ranks
  *with* production.
- Default order: main push > CP and hotfix > production together with instruments saving at least
  12 h > other instruments by savings.

The fifth amendment (19:59:53Z):
- Group priority lives in one central place, the roster. That covers the per-group fields
  (hotfix or source user, savings with its ruling, class) and the tier order itself.
- There is no separate `dev/audit/config/ci_priority.json`.
- `replan.py`, the merge train, the CI pause and cancel sweep, fixer dispatch and the ledger all
  read priority from the roster.

Batch 56 (P267) was already pushed as `handoff/triage-s7-batch56` `86d399b50` when the fourth
amendment arrived, so both amendments are ruled here and batch 56's head does not move. This
ruling supersedes P267 where it says so. Facts were read at origin/main
`b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa` and at the live roster
`origin/handoff/audit-r10-roster` `be898eaef54a6ba1f996b4ca9b11c6f93ce94ea4`.

## P268: group priority lives in the roster, with one tier rule read by the plan and every queue; user-submitted findings are hotfixes, and an instrument saving at least 12 h ranks with production

Verdict: ACCEPT, narrowed, in three carries:
- **R10-ORCH-ROSTER-SCHEMA** (`carries-open`; owns `roster_lib.py`, `roster_sync.py` and
  `roster_edit.py`) holds the schema, the reader and the one tier rule.
- **R10-FLOW-TOOLKIT-MODEL** (`not-started`; owns `tools/plan/replan.py`) makes the plan call it.
- **R10-TRAIN-OVERLAP-GRADE** (`carries-open`) makes the train's pause and queue order call it.

P267's tracked config file and its `ci_priority.py` parser are **withdrawn**. P267's held carries
for R10-FLOW-WIP and R10-ORCH-LEDGER, and the held R10-FLY-CANCEL-SWEEP brief, are re-pointed at
the roster reader before release. Their texts cite both rulings.

Source: `proposals.md` V181, fourth and fifth amendments (owner, 2026-10-28T19:54:02Z and
19:59:53Z).

Instances:
- **The plan already has the owner's tiers.** `tools/plan/replan.py:316` (`dispatch_tier`) reads
  "0 the critical path, 1 production, else 2". Production is decided there by lane:
  `PRODUCTION = ("Learners", "Core model", "Product UX")`, line 100. `dispatch_key` (line 327)
  ranks only tier 2 by the roster's numeric `savings`, which line 395 reads. So the savings field
  exists, with no source. Hotfix does not exist. Tier 1 admits no instrument at any savings.
- **The roster already carries `class`.** The values at the ref above are instrument 95, owner
  14, production 13, rca 12, policy 9, study 7, process 7, with 7 groups having none. That is the
  per-group class the owner names. Today the plan reads lane, not class.
- **No roster field marks a user-submitted finding.** The groups' keys are after, architect_note,
  brief, carry, class, effort, files, findings, fixerModel, fixes, fixture, group, hot_files,
  issues, kind, lane, model, owner_gate, priority, rca, resume, reviewerModel, role, severity,
  size, stage and wave. Issue authorship cannot stand in for it, because the orchestrator files
  issues with the owner's token.
- **The roster's top level holds no priority block today.** Its keys are `_comment`, `fork`,
  `fork_note`, `session`, `repo`, `serial`, `struck`, `refused` and `unreproduced`.
- **What the briefs show.** 11 briefs open "Owner-reported", "Owner request" or "User-reported".
  The live ones are R10-UX-HEALTH ("Owner-reported Health tab", not-started) and
  R10-ROUND-PLAYBOOK ("Owner request", not-started). One hotfix-prefixed group exists:
  R10-HOTFIX-BATCH-ERREXIT.

Carry 1, to R10-ORCH-ROSTER-SCHEMA (the one central place):
1. **The tier order and its knobs.** The roster file gains a top-level `priority` block. Its
   defaults are the owner's:
   - `order` is `["main-push", "cp-hotfix", "tier1", "instrument"]`.
   - `major_savings_h` is `12`.
   - `tiebreak` is `["cp-rank", "savings-desc", "train-position", "age"]`.
   - `never_pause` is `["main-push", "cp-hotfix", "train-head"]`. `train-head` is a structural
     guard, not an order class.
   - `never_cancel` is `["main-push", "cp-hotfix"]`.
   - An absent block means these defaults.
2. **Per-group fields, set at intake.**
   - `source` is one of `"user"`, `"audit"` or `"programme"`. `"user"` means a finding submitted
     by the owner or an end user.
   - `savings_source` cites the ruling or cost test, for example
     `dev/programme/triage/<batch>.md#P<n>`. It is required whenever the existing numeric
     `savings` is set.
   - The existing `class` is kept, and `"production"` marks production code.
3. **The reader and the one tier rule live in `roster_lib`.**
   - `priority(roster)` returns the block with defaults. It **refuses**, naming the key, a block
     that drops `main-push` or `cp-hotfix` from `never_pause`, drops `main-push` from
     `never_cancel`, puts anything above `main-push`, or names an unknown class or omits one.
   - `is_hotfix(g)` is true for `source == "user"` or a `R10-HOTFIX-` name.
   - `savings_h(g)` returns the number, or `None`.
   - `tier(g, crit, roster)`: `cp-hotfix` if the group is on the critical path or `is_hotfix`;
     `tier1` if `class == "production"`, or (for a group with no `class`) its lane is one of
     replan's production lanes, or `savings_h >= major_savings_h`; else `instrument`.
   - `rank(items, roster, train)` orders items by `order`, then `tiebreak`.
   - A PR maps to its group by branch. A PR with no group is `tier1` if its three-dot diff touches
     `custom_components/`, else `instrument`.
4. **Intake.** `roster_edit.py append-group` **refuses** a group JSON without `source`. A new op,
   `set-field <group> source|savings|savings_source|class <value>`, is restricted to those four
   fields and validated: a `savings` with no `savings_source` is refused. The `priority` block is
   edited only through a `set-priority <key> <json>` op that runs `priority()`'s refusals first.
5. **Backfill.** A brief that opens "Owner-reported" or "User-reported" is `source: "user"`, and
   that includes the live R10-UX-HEALTH. "Owner request" briefs stay unmarked unless the owner
   says otherwise.
6. **Controls:**
   - an append-group without `source` is refused;
   - `set-field X savings 14` without a source is refused;
   - `set-priority never_pause '["train-head"]'` is refused naming `never_pause`;
   - `tier` gives `cp-hotfix` for a `source: "user"` group off the critical path, `tier1` for an
     instrument with savings 14, and `instrument` for one with savings 3;
   - `major_savings_h` 20 moves the 14 h group to `instrument`;
   - mutant: dropping the hotfix arm puts the user group in `instrument`, and fails;
   - null: today's roster, with no new fields and no block, loads unchanged.

Carry 2, to R10-FLOW-TOOLKIT-MODEL (the plan reads it):
- `replan.py`'s `dispatch_tier` and `dispatch_key` call `roster_lib.tier` and the block's
  `tiebreak`, instead of their own lane rule.
- The switch from lane to `class` for production is reported, not hidden. The replan prints each
  group whose tier changed against today's rule.
- Controls:
  - a `source: "user"` group off the critical path is scheduled first among the ready groups;
  - a 14 h instrument is scheduled with production;
  - null: with no `source`, no `savings` and no block, the plan equals today's except for the
    groups the tier-change report names.

Carry 3, to R10-TRAIN-OVERLAP-GRADE (P267's pause, re-pointed):
- The victim choice and the queue order call `roster_lib.rank`, with `priority()`'s
  `never_pause`.
- **Withdrawn from P267:** `dev/audit/config/ci_priority.json`, `tools/audit/seat/ci_priority.py`,
  the config-local `savings_h` map and `hotfix_prefixes`.
- Everything else in P267 stands: the trigger, one victim per pass, `paused.json`,
  `rerun-failed-jobs` on every exit, and resume at start.
- Changed controls:
  - a `source: "user"` PR off the critical path is never paused;
  - a 14 h instrument PR ranks with a production PR and above a 3 h instrument PR;
  - null: `rank()` over a roster with the default block reproduces the owner's order.

Re-pointed, not re-ruled (the held texts are updated before release):
- R10-FLOW-WIP's ranked dispatch list calls `roster_lib.rank`.
- R10-ORCH-LEDGER's owed-PR order calls `roster_lib.rank`. Its "paused CI never resumed" bucket
  stands.
- R10-FLY-CANCEL-SWEEP (P266) reads `priority()`'s `never_cancel` and honours `main-push` from it.
  A superseded run is dead work, so CP and hotfix superseded runs remain cancellable unless the
  owner widens this.

Not carried: deriving "user-submitted" from issue authorship (see the third instance); a separate
`hotfix: true` field, because `source: "user"` and the existing prefix decide it; and any second
store of the order.

Cost:
- About 70 lines in `roster_lib` and `roster_edit`, plus seven controls.
- About 15 lines in `replan.py`, plus the tier-change report.
- Fewer lines in `merge_train.py` than P267 priced, because it now imports the rule.
- One required key on every future `append-group`.

Binding: the owner directs the outcome. The ruling's job is to leave one store and one rule. The
plan already had a tier rule, and P267 had started a second, in a second file. One reader in
`roster_lib` serves the six consumers the owner names. User-submitted findings need a field,
because nothing in the tree marks them today.

### Owed to the owner from P268

- Whether an "Owner request" brief, such as R10-ROUND-PLAYBOOK, counts as a user-submitted
  finding. This ruling reads "finding" as a reported defect or issue. Marking a request is one
  `set-field <group> source user` op.
- Whether superseded CI runs on CP and hotfix PRs should also be kept, not cancelled by P266's
  sweep. That is a one-key change in the roster's `priority.never_cancel` reading.
