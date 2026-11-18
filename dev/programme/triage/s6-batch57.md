# Proposal triage, session s7, batch 57 (P268-P270)

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

- **The hotfix definition (owner, relayed by the orchestrator).** An owner request is a hotfix
  only if it is a bug touching production code, or a feature request the owner explicitly calls a
  hotfix. Not every "Owner request" brief qualifies, so R10-ROUND-PLAYBOOK is not a hotfix. A
  user-submitted bug in production code is a hotfix.
- **Sixth amendment (owner, 2026-10-28T20:28:56Z).** "hotfix also covers (a) a critical bug
  found by the programme during the fixing phase, (b) any bug on main, (c) a CI- or
  programme-machinery bug that deadlocks all merges. hotfix_by records which rule applied."
  The owner then corrected case (b): it is "any bug making main red on a required check", not
  "any bug on main". Cases (a) and (c) stand.

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
2026-10-28T19:54:02Z, 19:59:53Z and the clarification after it), and the owner's hotfix
definition.

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
   - `source` is one of `"user"`, `"audit"` or `"programme"`. `"user"` means an item submitted
     by the owner or an end user, either a report or a request. It does not make the group a
     hotfix by itself.
   - `hotfix` is an optional boolean, set at intake under the owner's definition. It is
     `true` only under one of five rules, and `hotfix_by` records which rule applied as
     `{rule, evidence}`:
     - `user-production-bug`: a user-submitted bug touching production code (`source: "user"`,
       a bug report, and a group that `touches_production`). The evidence is the report, an issue
       or brief line.
     - `owner-called`: a feature request the owner explicitly calls a hotfix. The evidence is the
       owner's words, cited.
     - `fixing-phase-critical`: a critical bug the programme finds during the fixing phase. The
       evidence is the finding or verdict that names it critical.
     - `main-red-required`: a bug that makes main red on a **required** check, as the owner
       corrected it. The evidence is the red required check-run on a main SHA, by its run id and
       context name. A bug on main that turns no required check red is not a hotfix under this
       rule.
     - `merge-deadlock`: a CI or programme-machinery bug that deadlocks all merges. The evidence
       is the stop that shows no merge can land, for example the train's stop line, or a required
       check red on every open head.
     - Anything else is not a hotfix. That includes an owner request for a document or an
       instrument, such as R10-ROUND-PLAYBOOK.
   - `savings_source` cites the ruling or cost test, for example
     `dev/programme/triage/<batch>.md#P<n>`. It is required whenever the existing numeric
     `savings` is set.
   - The existing `class` is kept, and `"production"` marks production code.
2. **`roster_lib` readers, the one place any instrument gets a group's mapping:**
   - `is_hotfix(g)`: `hotfix is True`, or a `R10-HOTFIX-` name (the existing convention);
   - `touches_production(g)`: `class == "production"`, or any of its `files` under
     `custom_components/`;
   - `savings_h(g)`: the number, or `None`;
   - `group_class(g)`: `class`, or for a group with no `class`, `"production"` if its lane is one
     of replan's production lanes.
3. **Intake.**
   - `roster_edit.py append-group` **refuses** a group JSON without `source`.
   - A new op, `set-field <group> source|hotfix|hotfix_by|savings|savings_source|class <value>`,
     is restricted to those six fields and validated. It refuses:
     - a `savings` with no `savings_source`;
     - `hotfix true` without a `hotfix_by` whose `rule` is one of the five and whose `evidence`
       is non-empty;
     - `rule: user-production-bug` unless `source` is `"user"` and the group
       `touches_production`.
4. **Backfill.**
   - Briefs that open "Owner-reported", "User-reported" or "Owner request" get `source: "user"`.
   - Those that report a bug and touch production also get `hotfix: true`. On the live roster that
     is R10-UX-HEALTH: "Owner-reported Health tab", a list of UI defects, with all three of its
     files under `custom_components/`.
   - R10-ROUND-PLAYBOOK ("Owner request"; files `dev/audit/README.md` and `CLAUDE.md`) gets
     `source: "user"` and is **not** a hotfix, as the owner ruled.
   - R10-HOTFIX-BATCH-ERREXIT keeps its prefix, and `is_hotfix` still reads the prefix. This
     carry sets no `hotfix_by` for it, because no rule's evidence is recorded for it here.
   - The three programme rules (`fixing-phase-critical`, `main-red-required` and `merge-deadlock`) are
     applied by the orchestrator at intake as they arise. They are not backfilled from brief
     text.
5. **Controls:**
   - an append-group without `source` is refused;
   - `set-field X savings 14` without a source is refused;
   - `is_hotfix` is true for a `hotfix: true` fixture and for a `R10-HOTFIX-` fixture, and false
     for a `source: "user"` request that touches only `dev/`;
   - `set-field X hotfix true` with no `hotfix_by`, or with an unknown rule, is refused;
   - `rule: user-production-bug` is refused on a `source: "audit"` group and on a user group that
     touches no production file;
   - each of `fixing-phase-critical`, `main-red-required` and `merge-deadlock` is accepted with
     evidence, and refused without it;
   - `main-red-required` whose evidence names a context outside the ruleset's required checks is
     refused;
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
- making every `source: "user"` group a hotfix, because the owner's definition excludes requests
  that are not production bugs unless the owner says so;
- any group-keyed data outside the roster.

Cost: about 50 lines in `roster_lib` and `roster_edit` plus five controls; about 15 lines in
`replan.py` plus the tier-change report; and a `ci_priority.py` smaller than P267 priced, since
it holds no mapping. `append-group` gets one required key, which every future intake op must
supply.

Binding: the owner directs the outcome. This ruling's job is that each group's priority has
exactly one store, the roster, and that the tier rule exists once and is read by all six
consumers. User-submitted bugs need fields, because nothing in the tree marks them today. `hotfix` is
validated against the owner's definition at intake, not guessed from the brief text.

### Owed to the owner from P268

- Whether superseded CI runs on CP and hotfix PRs should also be kept rather than cancelled by
  P266's sweep. That is a one-key change in the setting's `never_cancel` reading.

## P269: train.sh and the merge sweep default to the recommended flag set, each switchable off

Verdict: ACCEPT, narrowed, into a new fly-in, **R10-FLY-TRAIN-DEFAULTS** (size S). Its fixer edits
`tools/audit/seat/train.sh`, `tools/audit/seat/merge_train.py`'s argument defaults, and one
sentence of `dev/governance/roles/standing-merge.md`.

Source: `proposals.md` V183 (owner-directed, 2026-10-28T20:20:27Z). The owner has decided the
outcome; this ruling sets the shape and the owner group. It enters the open rolling batch under
V182, because #2932 has no verdict.

Instances (read at origin/main `b6f6ceca4`):
- **The set is in three places today, and they disagree.**
  - `dev/governance/roles/standing-merge.md` line 9 names `--overlap --bot-prs --approval-carry
    --skip-bad --free-holders`.
  - `merge_train.py`'s `AUTO_TRAIN_FLAGS` (the train a sweep or an event `add` starts, near line
    2862) is `("--bot-prs", "--approval-carry", "--pre-flight")`.
  - `train.sh` itself defaults every flag off, and only passes through what it is given (its
    header, lines 27-33).
  - So a sweep-started train runs without `--overlap`, `--skip-bad` or `--free-holders`. A hand
    launch that follows the role contract runs without `--pre-flight`.
- **Mandate.** `--mandate` takes a comment id. The train reads and checks a mandate only through
  `budget_raise_gate.py` (`_mandate_gate`, near line 630): its window, revocation and the owner's
  pinned identity. A stale or revoked id is therefore a policy stop at the merge, not a silent
  approval. No mandate file exists in the tree.
- **The owners of `train.sh` are done.** R10-FLOW-AUTOTRAIN and R10-TRAIN-UPGRADE both list it,
  and both are at stage `done`. The one live owner of `merge_train.py`, R10-TRAIN-OVERLAP-GRADE
  (M, `carries-open`), already holds P267's pause and P268's tier rule. Adding a policy sentence
  there would put tvofi's review gate on the whole M group. A small fly-in on a distinct seam
  (argument defaults, not the pause) avoids that, and the two seams share `merge_train.py` the
  way the hot-file ruling allows.

Brief (the new group):
1. **One tuple holds the set.** `merge_train.py` defines `RECOMMENDED = ("--overlap",
   "--approval-carry", "--skip-bad", "--free-holders", "--bot-prs", "--pre-flight")`. These are
   the owner's set, in the owner's order. `AUTO_TRAIN_FLAGS` is replaced by it.
2. **`train.sh` with no subcommand runs `batch` with the set on.** Each flag gets an explicit off
   switch: `--no-overlap`, `--no-approval-carry`, `--no-skip-bad`, `--no-free-holders`,
   `--no-bot-prs` and `--no-pre-flight`. The old `--<flag>` spellings stay accepted as no-ops, so
   existing launch lines keep working. The launch line prints the effective set.
3. **Mandate default.** With no `--mandate`, `train.sh` reads `$STATE_DIR/mandate` (one line, a
   comment id) if it exists, and prints `mandate: <id> (from <state-dir>/mandate)`. With no file it
   prints `mandate: none (owner reviews only)`, and `--no-mandate` turns it off. The gate still
   checks the id at every merge. No id is guessed or carried in code.
4. **`merge_train.py sweep`** starts `train.sh` with the same defaults, so the sweep and a hand
   launch can no longer differ.
5. **`standing-merge.md` line 9 names the set by reference.** It says "train.sh's recommended
   defaults (`RECOMMENDED` in `merge_train.py`)", not a flag list, so the contract cannot drift
   from the code. POLICY: that file is policy, so this group's PR merges only on tvofi's
   approving review.
6. **Controls:**
   - a bare `train.sh --queue Q ... --self-test` prints all six flags in its effective set;
   - `--no-skip-bad` removes exactly that one;
   - the sweep's started argv equals a bare hand launch's;
   - a state dir with a `mandate` file passes `--mandate <id>`, and one without passes none;
   - a mutant that drops a flag from `RECOMMENDED` fails the effective-set arm;
   - null: an explicit old-style `--overlap` launch is byte-identical in effect to a bare one.
   - Classify nothing new: no file is added.

Not carried: a mandate id in code or in the tree, because a mandate is a dated, revocable comment;
or turning a flag on that the owner's set does not name.

Cost: about 40 lines across `train.sh` and `merge_train.py`, six controls, and one policy
sentence. It saves the per-launch flag list that the orchestrator and the sweep today write
differently.

Binding: owner-directed. The shape keeps one definition of the set, read by both launch paths and
named by the contract, and it keeps the mandate under the gate's existing checks.

## P270: prompt-cache and context efficiency: stable text first, variables last

Verdict: DEFER. The measurement that decides it is already being taken. The owner approved the
card, and the orchestrator has a measurement seat quantifying it, which will amend V184. Until
that amendment arrives, the benefit is unmeasured.

Source: `proposals.md` V184 (owner-approved, 2026-10-28T20:28:06Z).

Instances (read at origin/main `b6f6ceca4`):
- **(1) The cloud prompt does put variables early.** `tools/audit/seat/cloud_dispatch.py`
  `_prompt` (line 107) builds its first sentence from the subject, which names the PR, the repo
  and the 40-hex head (line 109), and appends the bus nonce at line 112. The head reappears
  inside fixed instructions at lines 120, 123 and 130, and the nonce at line 132. So no two
  seats share a prefix past the first sentence. The function's text is about 4.9 kB
  (`sed -n 107,160p | wc -c` gives 4872).
- **(2) A RemoteTrigger run-body override is untested.** The card itself says "if the API
  supports a run-body override (test first)".
- **(3) Local briefs are already stable-first.** This seat's own brief opens with a fixed SEAT
  PREAMBLE. Its line 13 reads "--- SEAT BRIEF (everything below this line varies per seat;
  nothing above it may change mid-session) ---". So the local half is the practice already. Only
  the cloud prompt departs from it.
- **The owner groups.** `cloud_dispatch.py` is in the `files` of R10-FLOW-DESIGN-STAGES (M,
  `not-started`), R10-FLOW-DISPATCH (`done`) and R10-FLY-POOL-INSTRUMENT (`absorbed`). The one
  live owner is R10-FLOW-DESIGN-STAGES.

What would change the answer: the measurement seat's numbers. Two of them decide it:
- cache-read against uncached input tokens for a burst of cloud seats, dispatched within the
  cache window with today's prompt, then with a reordered render;
- whether RemoteTrigger accepts a per-run body.

If the reorder shows a clear saving, (1) goes to R10-FLOW-DESIGN-STAGES as a carry. The fixed role
text comes first, then one variable block (PR, head, nonce, brief path), and commands read
`$SEAT` or the environment. A render self-test would assert that two seats' prompts share every
byte before that block. (2) would join it only if the API test passes. (3) needs nothing.

Cost of the carry, when ruled: about 30 lines of template reordering and one prefix-identity
check in a 4.9 kB prompt builder. The reviewer prompt's own wording must not change, because
`cloud_relay.sh` and the verdict grammar read what it asks for.

Binding: an unmeasured benefit, against a measurement already in flight. The ruling waits for the
amendment and does not pre-empt it.
