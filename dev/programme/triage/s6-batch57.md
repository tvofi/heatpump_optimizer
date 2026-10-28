# Proposal triage, session s7, batch 57 (P268)

One entry: the owner's fourth amendment to V181 (2026-10-28T19:54:02Z), quoted from `proposals.md`
as it stands. The amendment does two things:
- **User-submitted findings are hotfixes.** Any finding submitted by the owner or an end user (an
  issue or report, not an audit seat's) is marked hotfix at intake and takes the hotfix tier.
- **A correction to the third amendment.** An instrument PR that is critical, or saves at least
  12 h, ranks *with* production code, not below it.

The default order becomes: main push > CP and hotfix (every user-submitted finding included) >
production together with instruments saving at least 12 h > other instruments by savings. The
amendment also requires roster fields set at intake and read by `replan.py` and the CI priority
setting.

Batch 56 (P267) had already been pushed as `handoff/triage-s7-batch56` `86d399b50` when this
arrived, so this is a separate ruling, as the orchestrator directed, and batch 56's head does not
move. Facts were read at origin/main `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa` and at the live
roster `origin/handoff/audit-r10-roster` `be898eaef54a6ba1f996b4ca9b11c6f93ce94ea4`.

## P268: user-submitted findings take the hotfix tier, and an instrument saving at least 12 h ranks with production: one tier rule for the plan and every queue

Verdict: ACCEPT, narrowed, in three carries:
- **R10-ORCH-ROSTER-SCHEMA** (`carries-open`; owns `roster_lib.py`, `roster_sync.py` and
  `roster_edit.py`) takes the roster fields.
- **R10-FLOW-TOOLKIT-MODEL** (`not-started`; owns `tools/plan/replan.py`) takes the plan's tiers.
- **R10-TRAIN-OVERLAP-GRADE** (`carries-open`) takes P267's setting. This ruling supersedes the
  parts of P267 that it names.

Source: `proposals.md` V181, fourth amendment (owner, 2026-10-28T19:54:02Z).

Instances:
- **The plan already has the owner's tiers, so this amends them rather than adding a second
  rule.** `tools/plan/replan.py:316` (`dispatch_tier`): "0 the critical path, 1 production, else
  2". `dispatch_key` (line 327) ranks only tier 2 by the roster's `savings`, and line 395 reads that
  field as a number. Production is decided by lane (`lane[n] in PRODUCTION`). So:
  - the "savings field" the amendment asks for already exists as a bare number;
  - "hotfix" does not exist;
  - tier 1 does not admit an instrument at any savings.
- **P267's setting (batch 56) made a second copy of those tiers.** It gave the setting its own
  classes (`production` by diff path, a `savings_h` map inside the config, `hotfix_prefixes`). Two
  tier rules would drift, so one rule is used below.
- **No roster field marks a user-submitted finding.** The roster's top-level keys at the ref above
  are after, architect_note, brief, carry, class, effort, files, findings, fixerModel, fixes,
  fixture, group, hot_files, issues, kind, lane, model, owner_gate, priority, rca, resume,
  reviewerModel, role, severity, size, stage and wave. There is no `source` and no `hotfix`.
  Issue authorship cannot stand in for it, because the orchestrator files issues with the owner's
  own token.
- **What the brief text shows.** 11 groups' briefs open "Owner-reported", "Owner request" or
  "User-reported". Two of them are live: R10-UX-HEALTH ("Owner-reported Health tab", not-started)
  and R10-ROUND-PLAYBOOK ("Owner request", not-started). One hotfix-prefixed group exists:
  R10-HOTFIX-BATCH-ERREXIT.

Carry 1, to R10-ORCH-ROSTER-SCHEMA (the fields, set at intake):
1. Two optional top-level fields:
   - `source`, one of `"user"`, `"audit"` or `"programme"`. `"user"` means a finding submitted by
     the owner or an end user.
   - `savings_source`, a citation such as `dev/programme/triage/<batch>.md#P<n>`. It is required
     whenever the existing numeric `savings` is set.
2. `roster_lib` gains:
   - `is_hotfix(g)`: `source == "user"`, or a `R10-HOTFIX-` name, the one existing convention;
   - `savings_h(g)`: the number, or `None`.
3. `roster_edit.py append-group` **refuses** a group JSON without `source`, so intake decides it
   every time.
4. A new op, `set-field <group> source|savings|savings_source <value>`, is restricted to those
   three fields and validated: a `savings` with no `savings_source` is refused.
5. Backfill. A brief that opens "Owner-reported" or "User-reported" is `source: "user"`, and that
   includes the live R10-UX-HEALTH. A brief that opens "Owner request" is a request, not a
   finding, so it stays unmarked unless the owner says otherwise.
6. Controls:
   - an append-group without `source` is refused;
   - `set-field X savings 14` without a source is refused;
   - `is_hotfix` is true for a `source: "user"` fixture and for a `R10-HOTFIX-` fixture, and false
     for a plain one;
   - null: today's roster with no new fields loads unchanged.

Carry 2, to R10-FLOW-TOOLKIT-MODEL (the plan reads them):
- `dispatch_tier` becomes:
  - tier 0: the critical path, or `roster_lib.is_hotfix`;
  - tier 1: a production lane, or `savings_h >= major_savings_h`;
  - tier 2: the rest, ranked by savings as today.
- `major_savings_h` is read from `dev/audit/config/ci_priority.json` (default 12), and an absent
  file means 12.
- This function becomes the one tier rule. `tools/audit/seat/ci_priority.py` (P267) imports it
  rather than defining classes of its own.
- Controls, in replan's existing tier mutant set (from line 1319):
  - a `source: "user"` group off the critical path is scheduled in tier 0;
  - an instrument with savings 14 is tier 1, and one with savings 3 is tier 2;
  - setting `major_savings_h` to 20 moves the 14 h group to tier 2;
  - mutant: dropping the hotfix arm puts the user group in tier 2, and fails;
  - null: a roster with no `source` and no `savings` reproduces today's plan.

Carry 3, to R10-TRAIN-OVERLAP-GRADE (P267's setting, amended):
- The `order` default becomes `["main-push", "cp-hotfix", "tier1", "instrument"]`.
- `cp-hotfix`, `tier1` and `instrument` are replan's tiers 0, 1 and 2, taken from the imported
  `dispatch_tier`. A PR maps to its group by branch. A PR with no group falls back: `tier1` if its
  three-dot diff touches `custom_components/`, else `instrument`.
- P267's config-local `savings_h` map and `hotfix_prefixes` are **dropped**. Savings and hotfix
  come from the roster, through `roster_lib`.
- `train-head` stays a structural `never_pause` guard, not an `order` class.
- Everything else in P267 stands: `never_pause`, `never_cancel`, the floor refusals, the
  `tiebreak` and the readers.
- Changed controls:
  - a `source: "user"` PR off the critical path is never paused;
  - with the default file an instrument PR saving 14 h ranks with a production PR and above a 3 h
    instrument PR;
  - null: `rank()` over the default file reproduces the owner's corrected order.

Not carried: deriving "user-submitted" from issue authorship (see the third instance); a separate
`hotfix: true` field, because `source: "user"` and the existing prefix already decide it.

Cost: about 40 lines in `roster_lib` and `roster_edit` plus five controls; about 15 lines in
`replan.py` plus five tier mutants; and a smaller `ci_priority.py`, because it now imports its
classes instead of defining them. `append-group` gets one required key, which every future intake
op must supply.

Binding: the owner directs the order. The ruling's job is to keep one tier rule: replan already
had one, and P267 had started a second. User-submitted findings need a field, because nothing in
the tree marks them today, and the orchestrator files issues under the owner's account, so
authorship cannot tell them apart.

### Owed to the owner from P268

- Whether an "Owner request" brief (a requested feature or document, such as R10-ROUND-PLAYBOOK)
  counts as a user-submitted finding. This ruling reads "finding" as a reported defect or issue,
  so requests stay unmarked. Marking one is a single `set-field <group> source user` op.
