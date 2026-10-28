# Proposal triage, session s7, batch 57 (P268)

One entry, covering the owner's fourth and fifth amendments to V181 and the owner's
clarification of the fifth. All three are quoted from `proposals.md` as it stands.

- **Fourth amendment (2026-10-28T19:54:02Z).** Every user-submitted finding (an issue or report
  from the owner or end users, not an audit seat's) is a hotfix and takes the hotfix tier.
  Correcting the third amendment, an instrument PR that is critical, or saves at least 12 h, ranks
  *with* production. The default order is main push > CP and hotfix > production together with
  instruments saving at least 12 h > other instruments by savings.
- **Fifth amendment (19:59:53Z), as clarified.** "Only the group<->priority mapping must live in
  the roster; tier definitions/order may stay in a separate file such as ci_priority.json. All
  instruments read the mapping from the roster."

Batch 56 (P267) was already pushed as `handoff/triage-s7-batch56` `86d399b50` when the fourth
amendment arrived. All three are therefore ruled here, and batch 56's head does not move. This
ruling amends P267 where it says so. Facts were read at origin/main
`b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa` and at the live roster
`origin/handoff/audit-r10-roster` `be898eaef54a6ba1f996b4ca9b11c6f93ce94ea4`.

## P268: each group's priority mapping lives in the roster, the tier order stays in P267's setting, and one tier rule serves the plan and every queue; user-submitted findings are hotfixes, and an instrument saving at least 12 h ranks with production

Verdict: ACCEPT, narrowed, in three carries:
- **R10-ORCH-ROSTER-SCHEMA** (`carries-open`; owns `roster_lib.py`, `roster_sync.py` and
  `roster_edit.py`) takes the per-group mapping.
- **R10-FLOW-TOOLKIT-MODEL** (`not-started`; owns `tools/plan/replan.py`) makes the plan use the
  one tier rule.
- **R10-TRAIN-OVERLAP-GRADE** (`carries-open`) amends P267's setting and reader.

Source: `proposals.md` V181, the fourth and fifth amendments and the clarification (owner,
2026-10-28T19:54:02Z, 19:59:53Z and the clarification after it).

Instances:
- **P267's setting held per-group data that belongs to the roster.**
  - P267 kept the tier order and knobs in `dev/audit/config/ci_priority.json`. Under the
    clarification those may stay there.
  - P267 also put a group-to-savings map (`savings_h`) and a name list (`hotfix_prefixes`) in the
    same file. Those are the group<->priority mapping, and under the clarification they belong in
    the roster.
  - P267 classified production by diff path, which is a per-PR guess at what the roster's `class`
    already says.
- **The plan already has tiers and a per-group savings field.** `tools/plan/replan.py:316`
  (`dispatch_tier`) reads "0 the critical path, 1 production, else 2". Production is decided by
  lane: `PRODUCTION = ("Learners", "Core model", "Product UX")`, line 100. `dispatch_key` (line
  327) ranks tier 2 by the roster's numeric `savings` (read at line 395), which has no source.
  Tier 1 admits no instrument at any savings. Hotfix does not exist.
- **The roster already carries `class`.** The values at the ref above are instrument 95, owner
  14, production 13, rca 12, policy 9, study 7 and process 7, with 7 groups having none.
- **No roster field marks a user-submitted finding.** The groups' keys are after,
  architect_note, brief, carry, class, effort, files, findings, fixerModel, fixes, fixture, group,
  hot_files, issues, kind, lane, model, owner_gate, priority, rca, resume, reviewerModel, role,
  severity, size, stage and wave. Issue authorship cannot stand in for it, because the
  orchestrator files issues with the owner's token.
- **What the briefs show.** 11 briefs open "Owner-reported", "Owner request" or "User-reported".
  The live ones are R10-UX-HEALTH ("Owner-reported Health tab", not-started) and
  R10-ROUND-PLAYBOOK ("Owner request", not-started). One hotfix-prefixed group exists:
  R10-HOTFIX-BATCH-ERREXIT.

Carry 1, to R10-ORCH-ROSTER-SCHEMA (the mapping, set at intake):
1. **Per-group fields.**
   - `source` is one of `"user"`, `"audit"` or `"programme"`. `"user"` means a finding submitted
     by the owner or an end user, and it makes the group a hotfix.
   - `savings_source` cites the ruling or cost test, for example
     `dev/programme/triage/<batch>.md#P<n>`. It is required whenever the existing numeric
     `savings` is set.
   - The existing `class` is kept, and `"production"` marks production code.
2. **`roster_lib` readers, the one place any instrument gets a group's mapping:**
   - `is_hotfix(g)`: `source == "user"`, or a `R10-HOTFIX-` name (the existing convention);
   - `savings_h(g)`: the number, or `None`;
   - `group_class(g)`: `class`, or for a group with no `class`, `"production"` if its lane is one
     of replan's production lanes.
3. **Intake.**
   - `roster_edit.py append-group` **refuses** a group JSON without `source`.
   - A new op, `set-field <group> source|savings|savings_source|class <value>`, is restricted to
     those four fields and validated: a `savings` with no `savings_source` is refused.
4. **Backfill.** A brief that opens "Owner-reported" or "User-reported" is `source: "user"`, and
   that includes the live R10-UX-HEALTH. "Owner request" briefs stay unmarked unless the owner says
   otherwise.
5. **Controls:**
   - an append-group without `source` is refused;
   - `set-field X savings 14` without a source is refused;
   - `is_hotfix` is true for a `source: "user"` fixture and for a `R10-HOTFIX-` fixture, and false
     for a plain one;
   - `group_class` falls back to lane only when `class` is absent;
   - null: today's roster with no new fields loads unchanged.

Carry 2, to R10-FLOW-TOOLKIT-MODEL (the plan uses the one rule):
- `replan.py`'s `dispatch_tier` and `dispatch_key` call `ci_priority.tier()` and its `tiebreak`
  (carry 3) instead of their own lane rule.
- Production now comes from `roster_lib.group_class`, not lane. That change is reported, not
  hidden: the replan prints each group whose tier changed against today's rule.
- Controls:
  - a `source: "user"` group off the critical path is scheduled first among the ready groups;
  - a 14 h instrument is scheduled with production;
  - null: with no `source`, no `savings` and the default setting, the plan equals today's except
    for the groups the tier-change report names.

Carry 3, to R10-TRAIN-OVERLAP-GRADE (P267's setting and reader, amended):
- `dev/audit/config/ci_priority.json` keeps the **tier definitions and order only**:
  - `order` is `["main-push", "cp-hotfix", "tier1", "instrument"]`;
  - `major_savings_h` is `12`;
  - `tiebreak` is `["cp-rank", "savings-desc", "train-position", "age"]`;
  - `never_pause` is `["main-push", "cp-hotfix", "train-head"]`;
  - `never_cancel` is `["main-push", "cp-hotfix"]`.
- **Removed from the file:** P267's `savings_h` map and `hotfix_prefixes`. The mapping comes from
  the roster.
- `tools/audit/seat/ci_priority.py` keeps P267's floor refusals. Its classes are defined in one
  function, `tier(group, crit, roster, setting)`, which reads the mapping only through
  `roster_lib.is_hotfix`, `savings_h` and `group_class`:
  - `cp-hotfix` is the critical path, or `is_hotfix`;
  - `tier1` is `group_class == "production"`, or `savings_h >= major_savings_h`;
  - `instrument` is the rest.

  A PR maps to its group by branch. A group-less PR is `tier1` if its three-dot diff touches
  `custom_components/`, else `instrument`.
- `train-head` stays a structural `never_pause` guard, not an order class.
- Everything else in P267 stands: the trigger, one victim per pass, `paused.json`,
  `rerun-failed-jobs` on every exit, resume at start, and the readers.
- Changed controls:
  - a `source: "user"` PR off the critical path is never paused;
  - a 14 h instrument PR ranks with a production PR and above a 3 h instrument PR;
  - a setting file that still holds a group-keyed map is refused, naming the key, so the mapping
    cannot drift back out of the roster;
  - null: `rank()` over the default setting and today's roster reproduces the owner's order.

Re-pointed, not re-ruled (the held texts are updated before release):
- R10-FLOW-WIP's ranked dispatch list calls `ci_priority.rank`.
- R10-ORCH-LEDGER's owed-PR order calls `ci_priority.rank`. Its "paused CI never resumed"
  bucket stands.
- R10-FLY-CANCEL-SWEEP (P266) honours the setting's `never_cancel` `main-push`. A superseded run
  is dead work, so CP and hotfix superseded runs stay cancellable unless the owner widens this.

Not carried:
- deriving "user-submitted" from issue authorship (see the fourth instance);
- a separate `hotfix: true` field, because `source: "user"` and the existing prefix decide it;
- any group-keyed data outside the roster.

Cost: about 50 lines in `roster_lib` and `roster_edit` plus five controls; about 15 lines in
`replan.py` plus the tier-change report; and a `ci_priority.py` smaller than P267 priced, since
it holds no mapping. `append-group` gets one required key, which every future intake op must
supply.

Binding: the owner directs the outcome. This ruling's job is that each group's priority has
exactly one store, the roster, and that the tier rule exists once and is read by all six
consumers. User-submitted findings need a field, because nothing in the tree marks them today.

### Owed to the owner from P268

- Whether an "Owner request" brief, such as R10-ROUND-PLAYBOOK, counts as a user-submitted
  finding. This ruling reads "finding" as a reported defect or issue. Marking a request is one
  `set-field <group> source user` op.
- Whether superseded CI runs on CP and hotfix PRs should also be kept rather than cancelled by
  P266's sweep. That is a one-key change in the setting's `never_cancel` reading.
