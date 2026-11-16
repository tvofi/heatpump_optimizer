# R10-RCA-SETPOINT-LATCH-DEADLOCK: the off restore's own-write refusal held the space write with no release

This is the root-cause seat for R10-HOTFIX-FLOW-SETPOINT-STUCK. It follows
`dev/governance/roles/root-cause.md` and `dev/governance/rules/defect-root-cause.md`.
It ran beside that fixer, never inside it, and edits nothing under
`custom_components/` or `tests/`.

- **Trigger:** 1. The defect reached released versions: v7.1.12 (`4596f721f6`,
  stamped 2026-11-12T10:48Z) and every later tag, since the code is unchanged at
  `origin/main` `154dbb4c61` (2026-11-13T16:30Z).
- **Introduced by:** PR #3404 (R10-ARBITER-OFF-RESTORE), merge `1aeaf273a4`. The
  hold is in its first commit, `413cbb3c90` (2026-11-10).
- **The fix:** not read. The fixer's branch had not been pushed when this
  analysis was written. Section 5 says what its head still owes.
- **Reproduction:** `dev/audit/harnesses/r10_rca_setpoint_latch.py`.

## Result

- **Cause.** The off restore must not take the optimizer's own last write as
  the person's baseline. `_arm_space` enforces that by refusing the write
  itself, not only the capture. On an install upgraded from a version without
  the restore, the persisted record (`ArbiterState.written`, restored by
  `_load`) equals what the pump reads, usually the idle gate `FLOW_GATE_C`
  (25). So every space set-point write is refused, boost's included. Only a
  person can release it: an edit at the pump, or Optimizer active turned off
  and on again. A restart does not release it.
- **Process state: (a).** No contract asks that a refusal on an actuator write
  have a release that needs no person. The upgrade path was not missed: the
  fixer drove it, tested it, documented it and disclosed it, and the reviewer
  named it in a verdict. Every seat judged the hold against the stated intent,
  and the stated intent included the hold. No person accepted the consequence:
  both owner-account approvals were agent approvals under mandate.
- **Cost test.** The proposed detector costs about 1 s per run. The policy
  line costs about 20 min of reviewer time per 30 days. The defect costs at
  least about 6 h of programme time per occurrence (estimate), plus a house
  without heat until someone acts. One escape in 30 days of the round. Both
  countermeasures pass.
- **Countermeasure.**
  - Built: the detector, as a hand-run harness. It exits 1 at v7.1.12, at
    main and at #3404's first commit. It exits 0 at v7.1.11 (the null
    control) and on a candidate fix. It exits 2 on a tree that writes nothing.
    6 of 6 hand mutants are killed.
  - Proposed: the same invariant inside `tests/features.py`, which is the
    fixer's or main's to land.
  - Proposed to the owner (policy): one line in `fix-review.md` and one in
    `fixer.md`.
  - Recorded refusal: a stamp-time rule for release notes about user action.
- **Audit class.** No class in `dev/audit/config/bugclasses.json` matches.
  This is the first instance of the shape, so no class barrier is owed.

## 1. The cause, verified

### The code

At v7.1.12, `custom_components/heatpump_optimizer/pump_arbiter.py`:

- `_write` (`:1464-1488`) calls `_held_back` before any service call (`:1473`).
- `_held_back` (`:1506-1515`) ends with
  `return slot == "space_setpoint" and not await _arm_space(...)`.
- `_arm_space` (`:1518-1541`) computes `own`:
  - the key is not armed, or it is armed on another entity;
  - and the last record, `written["space_setpoint"]` or else
    `dropped["space_setpoint"]`, exists;
  - and the reading does not differ from it.
- When `own` is true, `_arm_space` logs once through `log_held` with "not
  writing it until it is set at the controller", then `return False`. That
  return is the hold.

At `origin/main` `154dbb4c61`, the same functions are at `:1596-1631`, with the
same logic. `git diff v7.1.12 origin/main -- pump_arbiter.py` changes 257 lines
of the file, none of them in `own` or its return.

### Why it bites on upgrade

- `_load` (`:1922-1942`) restores `written` from the store, filtered only by
  `_writable`. The record from before v7.1.12 is therefore present.
- Since v7.1.12, `armed` comes from `off_restore`'s store, so it is None on
  every upgraded install.
- `hold` (`:1388-1409`) rewrites any reading that differs from the record.
  That makes reading equal to record the steady state of every Control
  install. On an install that was idle at upgrade, the value is the gate,
  25 °C.

### What releases the hold

All four exits were checked against the code. Only the first two release it,
and both need a person.

| exit | releases? | evidence |
|---|---|---|
| a person sets a different value at the pump | yes | `hold` deletes the record when the reading differs (`:1405`). The next `_arm_space` sees no own value and arms with the person's value. This is the only release `docs/configuration.md:876-879` names ("set it on the pump once"). |
| Optimizer active Off, then on again (or duty mode away from Control) | yes | `_arbitrate` (`:1649`) → `_forget` (`:1655-1658`, `:1446-1447`) clears `written` and `dropped`. **Code-read, not measured:** the next arm then captures the reading, 25, as the person's baseline. That is the exact capture the refusal exists to prevent. Undocumented. |
| restart or reload | no | `_load` restores the same record |
| time, retry, repair issue | no | `_arm_space` has no clock. `log_held` logs once per transition. No issue is raised. |

### Reproduction

`python3 -I dev/audit/harnesses/r10_rca_setpoint_latch.py --check <root>`. The
harness drives `pump_arbiter.apply` through the same stub shape as
`tests/features.py`'s arbiter section (`_PaCoord`): a flow set-point install,
Control on, a plan that heats the house on every step, 0 °C outdoors, and a
device that takes every write. All runs below were made from cwd `/tmp`. The
harness exits 3 if the package loads from outside the named root, and no run
exited 3.

| tree | rc | states | failed |
|---|---|---|---|
| v7.1.11 `50e4b1aa25` (before the hold; null control) | 0 | 9 | 0 |
| #3404 first commit `413cbb3c90` | 1 | 18 | 1 |
| v7.1.12 `4596f721f6` | 1 | 36 | 4 |
| origin/main `154dbb4c61` | 1 | 36 | 4 |
| main + candidate fix (`_arm_space`'s `return False` → `return True`: refuse the capture, not the write) | 0 | 36 | 0 |
| main + skip control (`_write` returns first) | 2 | – | – |

The state count differs by tree because two axes depend on the tree:
`dropped` exists only from `da4ecec213`, and `CONSUMER` only from #3404.

Each failure ends with the entity reading 25 after 10 passes, against a
demanded 55. The failing states at v7.1.12 and main:

- `written=25 dropped=None reading=25 armed=False`: the upgrade case;
- `written=None dropped=25 reading=25 armed=False`;
- `written=25 dropped=25 reading=25 armed=False`;
- `written=55 dropped=25 reading=25 armed=False`. Here `hold` drops the 55
  record against the 25 reading, and the dropped 25 then holds. Whether a live
  install reaches this state was not verified.

The scratch run behind the first report to the orchestrator used the same
upgrade state with longer horizons:

- 600 one-minute passes at the gate: `space_writes=0 entity_now=25`;
- the null control (reading 31): `space_writes=1 first=[55]`;
- a fresh coordinator on the same entry id after 5 passes, which loads the
  record from the store: `space_writes=0 record=(25.0, ...)`;
- Off then Auto: `[55, 55]`.

Not verified:

- the boost ceiling path. Boost's write goes through the same `_write` →
  `_held_back` (`:1502` at main), so the same refusal reaches it, but no boost
  was driven;
- the owner's install itself.

### Which side moved

The tests did not drift into the hold. They were written with it, as its
specification:

- `tests/features.py:63599` `_pa_upgraded` (blamed to `413cbb3c90`) starts
  from a persisted record of 30 and runs 2 passes. It asserts
  `_pa_up_first == []`, so the write is refused.
- Its title says the write "waits". No check asserts that the wait ends.

The fix must invert this check.

## 2. The process state: (a)

**(a) The process did not exist.** No contract asks for the property the
defect broke: a refusal on an actuator write path must have a release that
needs no person.

What each seat had, and did:

1. **The brief.** It was written by roster op `fac0e80098` (2026-11-07,
   "roster_edit batch of 6") and says: "Refuse to capture a value equal to the
   arbiter's own last write." It refuses the capture and says nothing on
   whether the write proceeds.
   - The owner's ruling (#201 comment 6708225978) is only "Arbiter too", and
     leaves the baseline to "the building group's work". The refusal line is
     the brief writer's, not the owner's.
   - `architect_note` is empty and the group is size M, so no designer ran.
2. **The fixer drove the upgrade state and chose the hold knowingly.**
   - PR #3404's body, line 5: "`_arm_space` refuses a first capture whose
     reading equals the arbiter's own last write ..., latched once per entity,
     and holds the write until the controller reads anything else."
   - `docs/configuration.md:876-879`: "after an upgrade from a version
     without this, the set-point is not written until it reads anything else,
     so set it on the pump once."
   - `fixer.md:54-56` ("A learner or guard change is measured at both ends of
     its input range") was obeyed: `_pa_upgraded` is the upgraded end.
   - Neither the body nor the docs state what the pump does meanwhile. It
     stays at the last write, the idle gate on an idle install.
3. **The fix reviewer saw it and pushed the other way.**
   - The blocked verdict `e76038aacc` (`review/3404`, VERDICT.md:14) says: "on
     an upgrade with the loop active ... The write stays held until a person
     changes the controller."
   - The review blocked because the hold could leak, letting the optimizer's
     own value be captured. Repair round 3 (`da4ecec213`, `4831cb404f`) made
     the latch survive run ends (`ArbiterState.dropped`). That widened the set
     of states that enter it: three of the four failing states above need
     `dropped`.
   - The final verdict, `5b85bdeaa0`, was "Fix review: merge" at `aa70efdd`.
4. **No person accepted it.**
   - Both approvals by the owner's account (2026-11-11T03:35Z at `561edf4c`,
     19:59Z at `212e3fc7`) read "Agent approval (the orchestrator, not tvofi
     in person) ... under mandate 6715477401".
   - The two `hpo-approver` approvals are bot approvals on the verdict.
5. **The release note did not carry it.** The v7.1.12 entry for #3404
   (`RELEASE_NOTES.md`, "Turning the optimizer off restores the pump's space
   set-point") has no line about the upgrade. The config-flow help at
   v7.1.12 (`strings.json:595`, `translations/en.json:595`) still reads "Used
   only to notice when the entity cannot be read. The optimizer never writes a
   recommended space set-point."
6. **The contracts.** `git grep -n -i -E "liveness|latch|deadlock|upgrade|actuator"`
   over `fix-review.md` and `designer.md` returns nothing. In `fixer.md` the
   only match is `:231` (actuator writes belong in the coordinator or
   `pump_arbiter.py`, a layering rule).
   - `D1.md` hunts "turns a corrupt input into a permanent failure". Its store
     fuzz (step 2) mutates corrupt payloads, not a valid payload from a
     previous version.
   - Round 10's D1 audit predates this PR in any case.

**Why not (b).** No rule was disobeyed. The guard edge was measured, the body
disclosed the hold, and the docs named the person's action.

**Why not (c).** The processes that ran (guard-edge measurement, adversarial
review) work against the fix's stated intent, and here they produced what
that intent asked for. The missing piece is the criterion: a refusal must
end without a person. No process holds that criterion, so a firmer version of
any existing step would have been obeyed with the same outcome. The nearest
existing control has the right property in another unit: P5's barrier, "the
#1524 liveness checks refusing a gate that refuses everything", covers sysid
adoption gates. Nothing extended it to actuator writes. That is an absent
process for this unit, not a misfiring one.

**Why not (d).** No precondition changed. The hold was born with its
human-only release in `413cbb3c90`.

## 3. How far the class reaches

**Rule.** Every hold condition on an actuator write in the three write-owning
modules this round touched: each `log_held(` site whose true branch skips a
write. For each, ask what ends it on a valid configuration.

- Enumerator: `git grep -n 'log_held(' -- custom_components/heatpump_optimizer/pump_arbiter.py custom_components/heatpump_optimizer/heat_curve.py custom_components/heatpump_optimizer/off_restore.py`.
- It prints 17 lines at `154dbb4c61` and none at v7.0.0.
- `_held_back`'s two non-`log_held` refusals were read too.

| site (main) | refusal | release |
|---|---|---|
| `pump_arbiter.py:1625` `_arm_space` | the record equals the reading, key not armed | **a person only: this defect** |
| `pump_arbiter.py` `_held_back` retry | retry not due | time (`RETRY_MINUTES`) |
| `pump_arbiter.py` `_held_back` mode domain | mode entity of a read-only domain | configuration; intended, the slot cannot be written |
| `pump_arbiter.py:644` | indoor set-point whose minimum exceeds the room target | configuration fault, warned |
| `heat_curve.py:366`, `:504` | entity not a number, no target | configuration fault, warned |
| `heat_curve.py:376`, `:551` | "not resent until the target changes" | automatic: the plan moves the target |
| `heat_curve.py:383` | 24 h write cap | time (the deque drains) |
| `off_restore.py:185` | no readable baseline | automatic: the entity becomes readable |
| `off_restore.py:215`, `:248` | a restore not sent | retried on the next restore |

**Reach.** One site in about ten holds an actuator write on a valid
configuration until a person acts, and that site is this defect.

**Escape record.** `RELEASE_NOTES.md` v7.1.0 to v7.1.15 (16 stamps) has no
other escape of this shape. The nearest is #3497's "no longer refused", which
was a wrong value, not a held write.

**Register.** No class in `dev/audit/config/bugclasses.json` (61 entries)
has this mechanism. The nearest are:

- P5, whose barrier carries the liveness check for gates;
- R9-ROW-STALE, "a record guard refuses the exact rewrite the record beat
  exists to perform", an instrument class.

As a single instance, it owes no barrier under `defect-root-cause.md`'s
audit-class clause. Minting a class is the judge's call, not this seat's.

## 4. The cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

Units are wall-clock, per occurrence, over 30 days (the round's span from
v7.0.0, 2026-10-14, to now).

**cost(defect).**

| measure | value | basis |
|---|---|---|
| released exposure | v7.1.12 stamp (2026-11-12T10:48Z) to 2026-11-13T16:30Z, about 30 h and counting; the fix is not released | tag date, `date -u` |
| affected installs | every Control install with a space set-point entity, upgraded with reading equal to record, which is the steady state `hold` enforces | code-read; the install count is not known |
| user harm | the pump holds the last write, the gate on an idle install: the owner's house at 16 °C at 0 °C outdoors | the brief's report; not re-measured |
| programme cost | a hotfix fixer, its review, this seat, a stamp: at least about 6 h | estimate; no fix PR existed to time |

**P(recurrence).** No measured class frequency exists. The round's record
holds one escape:

- about 30 actuator-module merges in 30 days
  (`git log --first-parent origin/main --since=2026-10-14 -- pump_arbiter.py heat_curve.py off_restore.py boost.py supply_hold.py | wc -l` = 30);
- about 10 new hold sites in those modules (section 3).

The estimate is 0.3 to 1 per 30 days.

**Expected defect cost:** 0.3 × 6 h = 1.8 h, up to 6 h, per 30 days, before
any user harm.

**cost(countermeasure, recurring).**

- **The invariant in `tests/features.py`.**
  - Measured: the harness's 36 states × 10 passes take 0.8 to 0.9 s of CPU
    end to end, imports included (`time`, single tree). Inside
    `features.py` the imports are already paid.
  - At 100 selected runs a day, that is under 50 min of CI time per 30 days,
    with no seat time. It **passes**.
- **One review line** (section 5).
  - About 2 min per pull request that adds a refusal on an actuator write.
  - Of about 30 actuator-module merges per 30 days, an estimated third add one:
    about 20 min per 30 days. It **passes**.
- **A stamp-time release-note rule.**
  - `stamp.py` would refuse a note that omits a PR's declared user action.
  - Upkeep: a new PR-body field and a parser.
  - Benefit: none here. The hold was disclosed in the docs and the body, and a
    note saying "set it on the pump once" would still have left every
    upgraded house unheated until someone read it. The defect is the
    behaviour, not its announcement.
  - It **fails** on benefit, and is refused (section 5).
- **An upgrade-path fixture** (a previous release's store loaded and run). Its
  states are a subset of the invariant's. It adds nothing.

## 5. Countermeasures

### Built: the detector, shown failing and passing

`dev/audit/harnesses/r10_rca_setpoint_latch.py --check <root>` is the detector.
Its results are the table in section 1:

- rc 1 on the defect: v7.1.12, main and `413cbb3c90`;
- rc 0 on the null control (v7.1.11) and on a candidate fix;
- rc 2 on a skip tree that writes nothing;
- rc 3 on a provenance refusal.

The candidate fix shows that the detector turns green on a fix. It is not
offered as the fix. It drops the refusal of the write and keeps the refusal of
the capture. The fixer's design may differ, and the detector is owed a run on
the fixer's head before merge: the fix review's to run.

**Mutation proof.** The harness is under `dev/` and outside `mutant_run.py`,
so it was mutated by hand. The scored command requires all of:

- rc 1 at v7.1.12, run from the candidate-fix tree;
- rc 0 at the candidate fix, run from the v7.1.12 tree;
- rc 2 on the skip tree;
- rc 0 at v7.1.11;
- rc 1 at `413cbb3c90`.

Unmutated, it passes. 6 of 6 mutants are killed:

| mutant | edit | scored rcs (tag, fix, skip, v7.1.11, r1) |
|---|---|---|
| Ma | the verdict becomes `return 0` | 0 0 2 0 0 |
| Mb | the gate dropped from the `written` axis | 1 0 2 0 0 (killed by `413cbb3c90`, which has no `dropped` axis) |
| Mc | the skip guard becomes `if False:` | 1 0 1 0 1 |
| Md | the comparison becomes `final != final` | 0 0 2 0 0 |
| Me | the gate dropped from the reading axis | 0 0 2 0 0 |
| Mf | `os.chdir(root)` removed | 1 0 2 1 1 (v7.1.11 reads package data relative to the cwd) |

Mb survived until `413cbb3c90` was added to the score. On trees with
`dropped`, the dropped-gate state covers the same latch.

### Proposed: the invariant in `tests/features.py`

The harness's loop belongs beside the arbiter section's off-restore checks.
For the fixer of R10-HOTFIX-FLOW-SETPOINT-STUCK, or main:

- **The invariant:** from every persisted state, the entity reads the
  demanded target within N passes, with no person acting.
- **Its null control:** the reference install is written.
- **It replaces** `_pa_upgraded`'s "the write waits" assertion, which pins the
  defect.

It addresses the seam, not the state. It is a test and needs no owner
approval.

### Proposed to the owner (policy): the missing process, state (a)

These are policy changes, owner-gated, or under a mandate scoped `all`. They
are drafted here and not landed.

- **`fix-review.md`, a new step:**
  > **A new refusal on an actuator write names its release.** Where the diff
  > adds a path that skips a write the plan demands (a hold, a latch, a
  > refusal that returns before the service call), the body names what ends
  > it on a valid configuration, and a check drives the refusal's entry state
  > (persisted state from the previous release included) to that end. A
  > release that needs a person to act at the pump, or to toggle the
  > optimizer, is `blocked` unless the owner, in person, accepted it on the
  > pull request.
- **`fixer.md` step 3, one sentence after "measured at both ends of its input
  range":**
  > A guard that refuses an actuator write is also driven from the previous
  > release's persisted state, and its release needs no person.

Together these supply the criterion that every seat lacked in section 2. The
"in person" clause addresses item 4 there: mandate approvals carried the hold
without a person seeing it.

### Recorded refusal

The stamp-time release-note rule is refused (section 4). Its benefit is not
in this defect's causal path.

## 6. Carries

These are findings outside this seat's edit scope, routed by
`finding-propagation.md`, for the orchestrator to place in
R10-HOTFIX-FLOW-SETPOINT-STUCK's brief (a live group):

- **`_pa_upgraded` pins the defect.** `tests/features.py:63599-63622` asserts
  that the write waits, and the fix must invert it.
  Carry: R10-HOTFIX-FLOW-SETPOINT-STUCK
- **The Off-and-on release captures the optimizer's own value.** `_forget`
  clears the record, so the next arm takes the reading (the gate) as the
  baseline. This was found by code-read and not measured. A fix that keeps any
  hold should close it; one that drops the hold should say what the restore
  writes on an install armed with the gate.
  Carry: R10-HOTFIX-FLOW-SETPOINT-STUCK
- **A second entry into the latch.** `written=55 dropped=25 reading=25`:
  `hold` drops the 55 record, and the dropped 25 then holds (section 1).
  Reachability on a live install was not verified.
  Carry: R10-HOTFIX-FLOW-SETPOINT-STUCK
- **The config-flow help text.** `strings.json:595` and the translations still
  say "Used only to notice when the entity cannot be read. The optimizer never
  writes a recommended space set-point." `pump_duty_mode`'s help (`:1274`)
  says Control writes the entity. Class I5.
  Carry: R10-HOTFIX-FLOW-SETPOINT-STUCK
- **Docs.** `docs/configuration.md:876-879` ("set it on the pump once")
  describes the defect as behaviour.
  Carry: R10-HOTFIX-FLOW-SETPOINT-STUCK
- **The defect's issue.** `defect-root-cause.md` asks for a short **Root
  cause** section on the defect's own issue. No issue is on record, and this
  seat makes no GitHub write. Placing that section is the orchestrator's: state
  (a), the cost-test verdict and this path.

## Reproduce

    git worktree add --detach /tmp/v7111 v7.1.11
    git worktree add --detach /tmp/v7112 v7.1.12
    git worktree add --detach /tmp/r1 413cbb3c90
    H="$PWD/dev/audit/harnesses/r10_rca_setpoint_latch.py"
    (cd /tmp && python3 -I "$H" --check /tmp/v7111)   # rc 0, 9 states
    (cd /tmp && python3 -I "$H" --check /tmp/r1)      # rc 1, 1 of 18
    (cd /tmp && python3 -I "$H" --check /tmp/v7112)   # rc 1, 4 of 36
    (cd /tmp && python3 -I "$H" --check "$PWD")       # rc 1 at main until the fix
