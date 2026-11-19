# Handover — the open-issues programme

updated-for: 13cbe48de4236b7979c754640cc5b1a099ef7475

This file is ruled by `dev/governance/rules/writing-for-agents.md` (generated
into `.claude/rules/`, which the harness loads on this path). It holds what a
session starting now must know and cannot derive from the tree in one command.
Delivery status is the frozen table in `dev/programme/plan-2026-09-open-issues.md`
plus one `dev/programme/delivery/<N>.md` per pull request, linked from here and
never restated. **Volatile state is on #3394** (the successor coordination issue,
#201's continuation past its 2,500-comment cap; #201 stays open on the owner's
2026-10-25 sentence below and is wired to R10-CATALOG-PR so that the closeout
exempts it: see the issue set at closure) **and nowhere here**: running seats, open pull requests and heads,
the train queue, today's next action, the open-PR cap in force, the mandate's id
and dates, the v10.0.0 tag sha, the closeout counts and the catalog pull request
number. Chronology this file no longer carries is read at its form before this
rewrite, `git show a77d71fb75:dev/programme/HANDOVER.md` (round 10's closing
days), at the form before round 10's rewrite, `git show b161681af:dev/programme/HANDOVER.md`,
and at its last pre-round-10 form, `git show a77faf30d:dev/programme/HANDOVER.md`.

The reader is the round-11 orchestrator resuming cold. Round scope is that
orchestrator's own (tvofi, 2026-11-13, "You dont need to have an estimate for
round 11, you are round 10"): round 10 queued and named round 11's work, and
neither estimated nor dispatched it apart from the objective-function seat and
the pipeline designer the owner ordered started.

## Round 10 — the outcome

Round 10 opened 2026-10-14 under tvofi's rulings: every dimension under
`dev/governance/dimensions/`, three disjoint finder seats per dimension, one
verifier per dimension whose refute marks a finding **disputed**, one common
judge. Round 9 closed at v7.0.0 and its handoff branches are archived as tags
(`git tag -l 'archive/handoff/audit-r9-*'`). **Round 10 closes at v10.0.0**
(`stamp.py --round-close 10`, decision 0016; versions jump 7.x to 10.0.0 by
rule). Round 10's stamps are read from main's first-parent line
(`git log --first-parent --format='%h %s' v7.0.0..origin/main | grep ' v[0-9]'`);
the closure stamp's window is `git log --first-parent --format='%h %s' v7.1.17..v10.0.0`
and its tag is `git rev-list -n1 v10.0.0`. Each stamp's content is its
`RELEASE_NOTES.md` section; this file does not restate them.

### What closure meant, and which ruling outranks which

Rulings are listed oldest first and **the later outranks the earlier**.

- **2026-10-25** (tvofi, verbatim): "run the full programme to completion (no
  owed handoffs, no deferred findings, no deferred leads, no open roster
  groups, no issues open except 201, nothing deferred to round 11)".
  **Superseded for every non-production group** by the 2026-11-13 ruling below;
  it stands for production code.
- **2026-11-07** (tvofi): closure needs both the v10.0.0 stamp and the catalog
  pull request; its sentence is in `dev/audit/README.md` and not repeated.
- **2026-11-13 ~20:05Z** (tvofi, verbatim): "If these groups cannot be finished
  in round 10 without affecting the closure eta, their remainders are routed to
  round 11 when closure arrives. Closure should happen on 15/11, and only
  production code, the v10.0.0 stamp and the catalog pr may delay it".
- **2026-11-13 ~21:30Z** (tvofi, verbatim): "Please remember what groups may not
  delay round closure. 15/11 is key".
- **2026-11-13 ~22:20Z** (tvofi, verbatim): "you should still keep Everything
  else open moving, even if it may not delay closure": non-gating means
  ordered behind, never parked.
- **2026-11-14 ~00:40Z** (tvofi, verbatim): "Gating groups may move closure if
  absolutely unavoidable, but your should continuously workaround and try to
  hit 15/11 without scoping out gated groups. Also, stamp 7.1.16 much sooner".
- **2026-11-14 ~08:26Z** (tvofi, verbatim): "I want the hotfix merged asap,
  using workarounds to not slow us down more. Your top prio is closure at
  15/11, use workarounds where needed."

**The gating set** is therefore: production code that was in round 10 before the
evening of 2026-11-13 and the open carries of merged production groups
(`custom_components/` and what a production fix needs to merge), the v10.0.0
stamp, and the catalog pull request. Everything else, whatever its kind (policy,
process, instrument, audit, record, the objective function, dimension briefs, the
playbook, every R11-PRE and R11-INTAKE group, the outside-contribution
pipeline), never held a production merge, the stamp or the catalog step, and
never took a seat, reviewer or CI priority from the first list. The plan page's
closure date was not the authority while it priced the second list or lagged
stage words; closure was read from the gating set.

### What merged to form the gating set

Read the merges, not this list, for the final order
(`git log --first-parent --merges --format='%h %cI %s' v7.1.17..v10.0.0`). What
the owner named and what each was:

- **Evening of 2026-11-14** (tvofi, on `#3532`, `#3481`, `#3582`,
  `#3568`): "your main prio is. to land those 4 prs so thhat closure can happen
  15/11". `#3532` merged as `4058469d79`, `#3481` (R10-ADVISOR-STEADY-START)
  as `0a1ef512f4`, `#3582` (R10-ARCH-DOCS-DELTA) as `e901e9ef29` and `#3568`
  (R10-USER-DOCS-VERIFY) as `d7004eaa77`.
- **Product merges after the v7.1.17 tag**, which the soak below does not
  cover: `#3532`, `#3562`, `#3556` (it changed the card), `#3587`, `#3588`
  (enumerator: `git log --first-parent --oneline v7.1.17..origin/main -- custom_components/`),
  and `#3481`.
- **Four more gating items followed the four**: the savings-valuation docs
  pass `#3596` (below), the self-test scope hotfix `#3595` (R10-HOTFIX-MAIN-SELFTEST-SCOPE-2:
  `governance / instrument-self-tests` was red on main after `#3532`, not part of
  the required `gate`, but the owner's gating list names "main red"), the
  production hotfix `#3599` (R10-HOTFIX-REFERENCE-BASIS, below), and the
  closure record pull requests (R10-CLOSEOUT-CLEANUP's: `#3601`, merged as
  `29b3e5a74c`, its follow-up `#3604`, merged as `946eb6d255`, and a third,
  `r10-closure-record-3`, which carries this file after the stamp).
  **`#3599` was the last gating item and merged as `57fa260451`**
  (2026-11-15T03:49Z, after `#3491`, merged as `099d4fa3f2` at 03:48Z): its
  first-round merge verdict (probe `94f29ddb`) was never posted, because the
  mutation-autofix pin commit moved the head under its pending-ci draft, and a
  delta review of the pin commit alone, at `b58c6ca368`, returned merge (probe
  `996b06f9`). `#3605` (the delivery rows for `#3491`, `#3599`, `#3600` and
  `#3604`) merged as `2d0b1c7594`, and **v10.0.0 was stamped at `13cbe48de4`**
  (2026-11-15T05:22Z; the stamp's own record is `RELEASE_NOTES.md`'s
  `## v10.0.0`).
  `#3592` (a carry-tip SIGPIPE hotfix) was an instrument for landing the four
  and gated nothing.
- **`#3595` landed through a 7-second release of ruleset 23698884** (22:09:33Z
  to 22:09:40Z on 2026-11-14, read back active after). The approving review
  itself re-triggered `gate`: four `gate` runs started after the review although
  `merge_train.py classify` had read the head GREEN before it, so `gate` was
  pending at the merge and every re-run concluded success after it. The cause is
  in the clarifying comment 6885005206 on `#3595`, which replaced the landing
  script's default cause text. `#3596` raced the same way and merged as
  `6abf88e617` through a ruleset window of 23:04:44Z to 23:04:52Z (clarifying
  comment 6885662574 on `#3596`). **The landing chain now settles 240 s after
  the approving review and merges only on two GREEN reads with no `gate` run
  active**, so an approval-triggered `gate` run is no longer a reason to
  release the ruleset.
- **The savings reference changed without a basis bump** (R10-HOTFIX-REFERENCE-BASIS,
  `#3599`). `#3587` changed the booked `savings_baseline` for one install class (a
  two-zone house behind a throttling valve whose curve is the bound, the owner's
  own install among them): the first-step reference power rose 1.12 to 1.15 % at
  +5 to -15 C with no sun, and sunny steps, unvalved, single-zone and plain
  houses read bit-identical (a read-only verification seat called
  `_compute_baseline_power` at `931970141c^1` and `931970141c`). The rule
  "Bump when the booked reference changes" sits as a comment on `REFERENCE_BASIS`
  in `ledger.py`, a file `#3587`'s diff never touched, so neither its fixer nor
  its reviewer met it, and `docs/dashboard-card.md` promises the old-basis
  behaviour. `#3599` raises `REFERENCE_BASIS` from 2 to 3, mirroring
  `194625754d`: a month first booked on v7.1.17 that is still open at the
  upgrade reads "old basis" (both cost columns kept, no saving stated), and its
  release-notes line says so. Process state (b): the rule existed and nothing
  enforces it. The countermeasure its body routes is a features check pinning a
  digest of `_compute_baseline_power` over fixed installs beside the basis
  literal; its reproducibility across BLAS builds is unmeasured and must be
  measured before it is built.
- **R10-SAV-VALUATION-RESIDUE** was split because two carries were unbuilt when
  its second part merged: part 3 (`#3588`, carry 10: the combi hot-water kWh
  tile and the savings attribution read the store charge as one channel; its
  harness is `dev/audit/harnesses/r10_combi_tank.py`) and part 4 (`#3587`, carry
  9: the valved two-zone reference below the set-point, whose fix edits
  `thermal_model.py`). Both merged on 2026-11-14.

### The docs pass nobody had dispatched

`#3582` and `#3568` each state in their merged body that the savings-valuation
parts `#3587` and `#3588` are "outside this pass; a short later pass covers
them", and no `handoff*/` or `dispatch/` ref held that pass. R10-USER-DOCS-VERIFY
carry 17 (the late user-docs delta) therefore stayed pending and the closeout's
roster refusal held. It is gating under the owner's list ("the three user-text
verification groups ... the architecture docs delta"), so it was dispatched as
one size-S pull request (topic `r10-user-docs-verify-sav`, group
R10-USER-DOCS-VERIFY) re-reading README.md, the seven user pages and
`docs/architecture.md` against the two parts' diffs, and was never routed to
round 11 (overnight decision, 2026-11-14 ~21:20Z). R10-ARCH-DOCS-DELTA carries 0
and 1 had been marked `implemented e901e9ef29` by `#3582` before that pass; the
record of the architecture half of the re-read is the docs pass's own body,
`#3596`. **`updated-for:` of this file names the v10.0.0 stamp commit,
`13cbe48de4`**;
it must be reachable from the record pull request's head (`tests/entities.py`).

### Delivered, and the stamp

v10.0.0 is stamped at `13cbe48de4` (2026-11-15T05:22Z), after the gating items
above. Measure the closure outcome from the tree and the tag, not from this file:
the tag and date (`git rev-list -n1 v10.0.0`, `git log -1 --format=%cI v10.0.0`),
the stamp's flags and the cause of each (`--allow-red`, `--allow-rowless`,
`--no-flush`: the release commit and `RELEASE_NOTES.md`'s `## v10.0.0`), the
stamp's `gate` read (`gh run list --workflow ci.yml --branch main --limit 3`), the
closeout report's counts (the `--report-dir` of `tools/audit/seat/closeout.py
--apply`) and the archive tags it made (`git tag -l 'archive/handoff/audit-r10-*'`),
the ratchet state (`python3 tests/structure.py`, and `head -3
tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` reading
`claims-for: 10.0.0` with no claim line after a stamp). The stamp's window starts at
v7.1.17, not at round 9's close. The v7.1.16 and v7.1.17 stamps both ran with
`--allow-rowless --no-flush`, and v7.1.17 also with `--allow-red` (main's run was
still in progress at the stamp, 15 jobs green and none failed at the last read).

After closeout the roster branch `handoff/audit-r10-roster` and the plan branch
`handoff/audit-r10-plan` are archived; the plan of record is
`dev/programme/rosters/wave-r10-groups.json` **on `main`** (the record pull
request landed the final roster there; before that the tracked copy lagged the
branch), and the state documents are mirrored under `dev/programme/round10/state/`.
`#3601` landed the roster at `00e3c2f8c0`; the follow-up record
`#3604` re-landed it at `f8d3342d50`, because the closeout dry plan
at `#3601`'s merge printed `step in-main: BLOCKED` on one bare citation
(`handoff/r10-arch-docs-delta`, in the round-10 roster) and the roster branch
had moved since (the #201 wire, and carries folded for `#3575`, `#3553`,
`#3521`, `#3600` and draw-map part B). The third record,
`r10-closure-record-3`, re-landed it at `89acffb1ab`, because the closeout dry plan
at the stamp printed `step in-main: BLOCKED` on four bare citations
(`handoff/r10-cop-learner-draw-floor`, `handoff/r10-hotfix-main-selftest-scope-2`,
`handoff/r10-hotfix-reference-basis` and `review/3481`, all in the round-10
roster) and the roster branch had moved again (two carries appended to
R11-INTAKE-R10-RESIDUE, and stage edits after the merges). A roster edit after
`89acffb1ab` is on the branch only, and after closeout on its tag
`archive/handoff/audit-r10-roster`.
`closeout.py --apply` also clears the orchestrator's state directory unless told
otherwise: see the trap on `--orch-root`.

The catalog pull request (issue #2965, group R10-CATALOG-PR) opens after the
stamp, as tvofi; `python3 tools/audit/check_scopes.py --repo . --ref HEAD` on the
v10.0.0 tree must exit 0 before it (the group's carry 1). Its number and state
are on #3394.

**The soak.** tvofi, 2026-11-12 ~17:00Z (verbatim): "It should not hold up the
chain, so I will submit it when it needs to be submitted", restated
2026-11-13 ~11:00Z: "Nothing should be held up for the soak, it will run for
the period it has time to. I told you to tell me directly when the results are
needed and I will send them immediately". So: no soak duration in any plan; patch
releases are stamped promptly so the soak has something to run on; and at the
moment a stamp needs the result the orchestrator tells tvofi directly.
`dev/audit/README.md`'s closure paragraph still states the 2026-11-11 form
("v10.0.0 is stamped only after tvofi says they opened the card's tabs on it,
never without"); the 2026-11-12 and 2026-11-13 rulings outrank it, and the
sentence is owed an amendment (see Owed).

**Release notes lead with the human action** (tvofi, 2026-11-13 ~16:40Z,
verbatim): "Every release requiring extra steps should either be shipped with an
automated migration script or very clearly describe the human action needed at
the beginning of the release notes." At every stamp ask of each merged pull
request whether upgrading needs a user action; if so a migration, else the action
first in that version's notes. The policy and the stamp mechanism that enforce it
are not built (see Owed), so until they are the stamping seat checks by hand.

**What the soak measured** (the read is out of tree at
`$HPO_STATE_DIR/s14/seat/soak-read/SOAK.md`, derived facts only; its scripts sit
beside it and run as `python3 -I <script> <bundle>`). The owner's diagnostics
download, taken 2026-11-14 ~18:42Z, shows v7.1.17 healthy over 3.4 h of rows on his
install (Home Assistant 2026.11.1): no solve failure, input health `ok`, every
duty write delivered. His words on the card half, before the stamp, were "Card
looks fine"; he did not state which version he ran or whether both themes were
opened. Not covered by that soak: the product merges after the tag (list under
"What merged"), and the card changed after the tag (`#3556`), so a check of the
card on 7.1.17 does not cover the card at main's tip. The soak never gated.

**A soak defect candidate goes to round-11 intake as a D1 item** (SOAK.md, C1; the
owner was asked to look at the room sensor and his answer is not recorded). One
install, not a regression of v7.1.17: the age rule is older and the restart was
the 7.1.17 upgrade. A Home Assistant restart re-stamps an on-change sensor's entity, so
`INPUT_MAX_AGE_MINUTES`'s staleness rule did not fire for an indoor sensor that
had been silent about 557 min; the product read its age as 211 min against the
360 min limit. The control is the lower-floor sensor, which moved over the same
hours, and the forecast bias on that version was the week's most negative; what the
bundle cannot separate is an upstairs zone that genuinely did not warm. It is a live D1
(robustness) and D8 (sensor) lead, to be re-measured on a second install
before it is called a production defect.

### What round 10 did not deliver

- Every non-gating group and pull request not merged at the stamp is
  re-routed to round 11 and listed below with its refs; none was closed or
  deleted by the programme (the owner ruled to keep the 12 re-routed pull
  requests open: "Keep them open", 2026-11-14 ~11:20Z). Open and non-gating at
  this record, and routed to round 11 if unmerged at the handover: `#3602`,
  `#3598`, `#3593`, `#3521`, `#3551` and `#3566`. `#3606`
  (R10-HOTFIX-SELFTEST-SCOPE-RERECORD part 3, the self-test scope re-record 3)
  is open in review; its carry (body item `ca87a555`) is on
  R11-INTAKE-R10-RESIDUE.
- The findings round 10 did not fix are carries on the roster, not issues. A
  group's carry count is the length of its `carry` list;
  R11-INTAKE-R10-RESIDUE holds the ones no live group owns, and the carries
  stranded on deferred or refused groups are the `CARRY-ROSTER:` summary line of
  `python3 tools/audit/carry_audit.py roster` (one `STRANDED` line per carry).
- The round's dimension coverage and judgements are under
  `dev/audit/rounds/round10/`; the roster header's `struck`, `refused` and
  `unreproduced` keys hold the refuted and unreproduced findings
  (`python3 -c "import json;r=json.load(open('dev/programme/rosters/wave-r10-groups.json'));print({k:len(v) for k,v in r.items() if k in ('struck','refused','unreproduced')})"`).
- **A planted-defect audit dispatch is held to the round-end pass** (overnight
  decision, 2026-11-14 ~21:01Z): the review-strength guardrail tripped on the
  cut 2026-11-14T00:09Z to 20:21Z and the dispatch, arm `claude-opus-5-5`, waited
  because it is non-gating and CI and seats went to closure first. Fire it in the
  round-end consolidation, not after.
- **Known red at closure, not part of the required `gate`:**
  `governance / instrument-self-tests` was red on main's pushes after `#3532`,
  at the step that refuses a self-test read set the committed table misses (the
  table `tools/ci/selftest_closures.json` drifts when a push to main adds an
  unrecorded read). Its repair for the table is `#3595` (how it landed is under
  "What merged"); the guard against the
  drift is R10-SELFTEST-SCOPE-UNION-GUARD (`#3551`, below), and card L9 would
  make both unnecessary by generating the table. The stamp reads `gate` only, and
  tvofi ruled on 2026-11-13 ~23:51Z (verbatim) "Instrument self test also in
  scope" for merging over the strace `PTRACE_LISTEN` red of that job.
  Whether it is still red at the tip is read from the stamp's push run
  (`gh run view <ci.yml run id> --json jobs --jq '.jobs[]|select(.conclusion=="failure")|.name'`).
- **The nightly-ha `a4` failure of 2026-11-12/13**: `tests/nightly_ha.py`'s `a4`
  step assumed a failed update while `#3454` bridges a price outage when cached
  prices still cover now; a test defect with no product change, repaired by
  `#3540` (merged 2026-11-13). The 11-12 failure stood 18 h with no fixer
  dispatched (logged as a slip). A recurrence of an `a4` failure after `#3540`
  owes a fixer the same turn, never a diagnosis seat first. The 2026-11-14
  nightly red was a different cause (one `features` check keyed on the weekday,
  repaired by `#3578`); `nightly-status` grades only the newest concluded
  scheduled run, so the next scheduled run is the green.

### The closing night, 2026-11-14 to 15

tvofi went to sleep ~20:32Z (verbatim): "Continue the programme without my input to
closure ASAP proactively, using workarounds where needed. No scoping out of gating
work. If your fable credits run out during the night, switch from fable to Opus
5.5", and ~20:34Z that the switch includes the orchestrator's own session. The
standing rule that follows: a Fable seat or cloud fire that fails for credit or
quota is re-fired on `claude-opus-5-5` with the same brief and the switch noted;
the rule expires when round 10 closes. What the decisions of that night were
(each logged `OVERNIGHT-DECISION` in the orchestrator's sweep log, out of tree):
every default Q1 to Q10 of the closure runbook was accepted (successor #3394
with #201 wired to R10-CATALOG-PR; the closeout's `--orch-root` pointed at a path
that does not exist so no scratch is cleared; scratch `retarget.py` used with
closeout step 1 as its check; #2728 closed after prune pass 2; the record pull
request under R10-CLOSEOUT-CLEANUP); the docs pass above is gating; `#3553`
(closeout-prep part 2) need not merge for closure, because R10-CLOSEOUT-PREP is
done once its one carry moves to round 11, and its review continues non-gating;
the draw-floor repair body for `#3593` is held until that pull request can be
updated after the gating merges; `#3551` and `#3566` were released from the CI
hold once the runners freed, and both were then held for round 11 with no
further fixer that night (their rows below carry the evidence); a design ruling
on honest starts was left to the owner (its row below).

**Round 11 does not start until four playbook-shaping changes merge** (owner,
2026-11-14 ~21:40Z, as logged in the sweep): `#3575` (decision 0018, the
objective function), `#3491`, `#3451` (which keeps `proposal-triage.md` in its
once-per-round shape, owner ~21:42Z: no deletion) and the playbook round-start
section (R10-PLAYBOOK-ROUND-START, `#3600`). They never delayed the
stamp; any of them unmerged at the stamp is run by round 10's orchestrator as a
post-closure item before the round-11 orchestrator starts. This gate sits in
front of sequence (a) below. `#3575` merged first, as `4eea986a62` on
2026-11-15 (decision 0018 and the evaluator contract
`dev/governance/roles/evaluator.md`; `corpus_tokens` raised from 68618 to 69333
under the mandate), and `#3600` second, as `2a257fce08` (its round-1 review was
`blocked evidence-cut`, repaired at handoff `76aca12e6f`). At the stamp `#3491` had merged as `099d4fa3f2` (its macOS `ps_start` repair
included) and `#3451` had not: it is open, its head `7f4a9be89c` holds a merge
verdict (`verdict/3451`, 2026-11-15T04:02Z) and the pull request is CONFLICTING,
so a merge-repair handoff, `archive/handoff/r10-process-slim-p2` at `c314960799`
(a live ref until the closeout archives it; a merge of main into `7f4a9be89c`), awaits a delta review of
`git diff 7f4a9be89c c314960799`. `#3451` is the one of the four that was not
merged at the stamp.

## Round 11 — what it starts from

### The start gate and the order the pre-finder work must land in

**Sequence.** (a) The pre-finder groups merge first, R11-PRE-MACHINERY-LIMITER
before the other instrument groups (item 5): every R11-PRE group
except the pipeline's later stages, plus the D5/D6 CADENCE carry and
R10-DIMENSIONS-FULL-COVERAGE part 2 (both carried on R11-INTAKE-R10-RESIDUE). (b) Only then is the round-11 baseline cut and
the finders started, because finders work from a pinned baseline and the
dimension, scope, objective-function and instrument changes must be inside it.
(c) The pipeline's day 1 must be merged before round 11's fixers start, so it
may run while the finders, verifiers and the planner work and does not hold the
finders. (d) The pipeline's shadow day runs beside the fix wave as a
measurement and gates nothing. (a) and (b) are the owner's 2026-11-13 ruling
quoted below; (c) and (d) are the orchestrator's reading of the owner's
2026-11-14 instruction (verbatim: "The design should be planned and built (if
it will save significand wall clock time in a programme) before the fixers in
round 11 start.") and of the 2026-11-14 ruling "Day 1 plus shadow" in item 1.

tvofi, 2026-11-13 ~18:06Z (verbatim): "Do all the necessary changes, including
yes on both my decisions, before round 11." The same evening, on six of the
process-audit items: "They should be fixed in the beginning of round 11 before
the finders run". **Round 11's finders do not start until the R11-PRE groups
below, the D5/D6 CADENCE carry and R10-DIMENSIONS-FULL-COVERAGE part 2 are merged**
(each group's brief says it must merge, or be built, before round 11's finders;
R10-D5-D6-FULL-SCOPE and part 1 of the dimension pair merged in round 10 as `#3571`
and `#3572`). Every R11-PRE group is `after R10-CATALOG-PR` except
R11-PRE-PARALLEL-PIPELINE, and the two the owner ordered started early
(R11-PRE-OBJECTIVE-FUNCTION and the pipeline design) ran before it; list them from the roster, not from here:
`python3 -c "import json;[print(g['group'],g['resume']['stage'],g.get('size')) for g in json.load(open('dev/programme/rosters/wave-r10-groups.json'))['groups'] if g['group'].startswith('R11-PRE')]"`.

The roster has no after-edges among the R11-PRE groups, so the order below is
derived from the one thing the roster does state, `files` (compare them with
the enumerator `python3 -c "import itertools,json;g={x['group']:set(x['files']) for x in json.load(open('dev/programme/rosters/wave-r10-groups.json'))['groups'] if x['group'].startswith('R11-PRE')};[print(a,b,sorted(g[a]&g[b])) for a,b in itertools.combinations(g,2) if g[a]&g[b]]"`)
and from each brief's own statement. Treat it as the constraints the round-11
orchestrator plans against, not as a schedule (round scope is that
orchestrator's):

1. **Decisions that change how the others merge go first.**
   R11-PRE-PARALLEL-PIPELINE (design stage, XL). Its design is on
   `design/R11-PRE-PARALLEL-PIPELINE` (appendix `design-wip/r11-pre-parallel-pipeline`)
   and its review on `design-verdict/R11-PRE-PARALLEL-PIPELINE`: round 1 returned
   `revise ... evidence-missing` at `80fbf6319f`, round 2 returned
   `Design review: approve 22fdbabafb30647a27332d6096df1feb02fc8fb7`. **The approval
   is of day 1 as a dispatchable design and of the shadow as a measurement that
   gates nothing; the switch (moving main by promotion, the appendix's SWITCH.md)
   is neither approved by the owner nor by the reviewer.** The reviewer's
   enumerators reproduced the counts (215 merges, 826 merges of main into a
   head, 682 of the 826 answering no conflict under GitHub's driver-free
   merge; `main_moves.py` and `absorb_nodriver.py` in the appendix). Owner
   rulings, 2026-11-14, verbatim: "remerge_main.sh definitely needs to be scoped
   down aggressively. Speculative gating could be done by running the scripts
   in cloud seats."; "If cloud seats for speculative gating is feasible, they
   should run haiku"; and, asked whether to build day 1 plus the shadow day as a
   measurement beside round 11 or day 1 only: "Day 1 plus shadow". What follows:
   day 1 (main is merged into a head only on a real conflict or a driver-only
   unmergeable head: `open_pr.sh`, `handoff_push.sh`, `remerge_main.sh`, the
   train's serial recarry; a proof input to `ci.yml` judged as a push) is built
   before the fixers start, as three groups: PROOF-INPUT first, TRAIN-ROUTING
   after it, NO-ABSORB independent but needing the same after-edge unless its
   reason argument defaults to today's behaviour (the verdict's carry o1, the
   orchestrator's decision); all of part 2 and part 3's policy text need the
   owner's review; the verdict's file-list carries n-a to n-d go to those
   groups' fixers (n-a: `inputs.recheck` at `tests.yml`'s `lane-proofs` and
   `laneskip` steps and `ci.yml`'s pass-through, which part 3 would stop feeding).
   The machinery ratchet charges day 1 as three non-production merges with no
   exemption, in a window the R11-PRE groups already fill; its headroom is
   unmeasured, so measure it first. The shadow day measures beside the fix
   wave; the integration branch is the owner's decision after the shadow
   result; six GitHub behaviours are unprobed, and no probe ran before the
   v10.0.0 stamp.
2. **The scope chain, strictly serial** because all three edit
   `tools/audit/check_scopes.py`: R10-D5-D6-FULL-SCOPE (merged as `#3571`), then
   R10-DIMENSIONS-FULL-COVERAGE (part 1 merged as `#3572`; its part 2, WIP ref
   `6f760d9fff`, owes four carries that were moved together to
   R11-INTAKE-R10-RESIDUE because carry 0 says "build it once"; it also edits
   `dev/audit/config/scopes.json` and `dev/governance/roles/COMMON.md`), then
   R11-PRE-OBJECTIVE-FUNCTION (`#3575`, merged as `4eea986a62`; it
   evaluates the dimensions as they stand, so the dimensions land first). Each
   is a policy change for the owner's review.
3. **`CLAUDE.md` and `dev/governance/roles/orchestrator.md`** are edited by
   R11-PRE-OBJECTIVE-FUNCTION, R11-PRE-RULINGS-FILE and (`CLAUDE.md` only)
   R10-DIMENSIONS-FULL-COVERAGE, and `orchestrator.md` by R11-PRE-TOOLCHAIN-PIN: land them one at a time, each rebased on the last.
4. **`tools/audit/seat/beat_jobs.py`** is edited by R11-PRE-TOOLCHAIN-PIN,
   R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER and R11-PRE-PLAN-RENDER, and
   **`tools/audit/seat/cloud_dispatch.py`** by R11-PRE-TOKEN-LEDGER and
   R11-PRE-STANDING-SCRIPTS: serial inside each set.
5. **R11-PRE-MACHINERY-LIMITER lands first among the instrument groups.**
   Owner, 2026-11-14 ~11:45Z, on the orchestrator's recommendation to land it
   first (verbatim): "limiter first, write that in". It lands before
   R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER, R11-PRE-RELAY-REBUILD,
   R11-PRE-ACK-COMPLETION, R11-PRE-STANDING-SCRIPTS and R11-PRE-PLAN-RENDER, so
   each of those is built under one-in-one-out and names what it retires;
   landed after, the largest intake of new machinery goes in unmetered and sets
   the limiter's baseline. The limiter sets "a new gate enters only when one
   leaves". The orchestrator's recommendation, not the owner's words: purely
   additive groups the owner ordered on 2026-11-13 are covered by one recorded
   exemption written into the limiter itself, if its rule allows an exemption
   as the machinery ratchet's does; the round-11 orchestrator checks the
   group's brief for that.
6. **R11-PRE-SHARED-FILES** (design first) generates `tests/closures.json`,
   `tests/structure_budgets.json` and the instruments index after merge instead
   of editing them in pull requests, which removes the coupling every other
   group pays in main-absorb rounds; the design owes how the two rules reading
   those files stay enforced.

What each R11-PRE group is, in the owner's own cards (decision cards answered
2026-11-13 ~18:43Z, verbatim: "P1: Yes · P2: Declining cap, one in one out,
severity route narrowed · P3: Yes · P4: Yes, local and cloud · P5: Keep and do
the rest · P6: Yes · P7: Yes, fold in · P8: Yes · P9: Yes, design first in
round 11 · P10: Yes · P11: Freeze, except production defects, owner orders and
red main · P12: Yes, during round 11 · P13: Yes · P14: Yes · R1: Yes, keep one
exception seat · R2: Yes, render on change · R3: "Full for CLAUDE.md,
orchestrator contract and rulings; changes only for instrument pages" · X1: No,
mandate stays as is · X2: Yes, trial"). The evidence for every card is the
process-convergence audit on the ref `handoff-wip/r10-process-convergence-audit`
at commit d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7, sections named in each
group's brief.

| group | card | what it builds | review route |
|---|---|---|---|
| R11-PRE-TOOLCHAIN-PIN | P1 | seats and the beat run tools from a promoted stable ref; product and machinery status reported apart; no stamp on a red product status | design first (L) |
| R11-PRE-MACHINERY-LIMITER | P2, P11 | declining machinery ratchet, one in one out, severity route narrowed; carries the freeze text below | policy, owner review |
| R11-PRE-ROUND-METRICS | P3, P8 | scorecard producer, lead-time percentiles, time-to-restore, token line, bottleneck alert; empty input prints unread | null control: empty input prints unread |
| R11-PRE-TOKEN-LEDGER | P4 | dispatch header and a daily per-header token sum; measure first whether cloud usage is readable per session | measure first |
| R11-PRE-RULINGS-FILE | P6, R3 | the owner's rulings verbatim in the tree, re-read by the compaction hook; interim carrier is the rulings list below | policy, owner review |
| R11-PRE-OBJECTIVE-FUNCTION | owner order | the objective function and a round-start evaluation step | policy, owner review; Fable |
| R11-PRE-SHARED-FILES | P9 | shared files generated after merge; features test script split by module | design first (L) |
| R11-PRE-HANDOFF-BOOKKEEPING | P10 | carry, body and red-check items decided mechanically at handoff; includes PC-1113-01 | policy, owner review |
| R11-PRE-RELAY-REBUILD | P12 | verdict posting never queues behind a pull-request update; retires the local detached watch-mode relay | |
| R11-PRE-ACK-COMPLETION | P14 | an acknowledgement names the event that closes it and is renewed at most twice; a gantt accept expires; a proposal candidate has an id; includes PC-1113-02 | |
| R11-PRE-STANDING-SCRIPTS | R1 | merge, rendering and watching as beat scripts, one exception seat | policy, owner review |
| R11-PRE-PLAN-RENDER | R2 | plan page rendered on change; closure history as data; round-10-only view and a future-rounds tab with its own preliminary gantt (owner, 2026-11-13 ~19:59Z and ~20:00Z, below) | |
| R11-PRE-PARALLEL-PIPELINE | owner order 2026-11-14 | day 1: heads stop moving, built before the fixers; shadow day beside the fix wave; switch not approved | Fable; design approved round 2 for day 1 and the shadow |

**The objective function** (owner's words, 2026-11-13): "have a fable seat define
that function and add it in the audit process, so that everything can be
evaluated against that objective when a new round is started, and any changes
needed is made before the finders start"; "the objective function should be such
that a "perfect" model that reads it, should be able to improve the dimensions,
process and machinery so that that round is completed "perfectly" against all
dimensions, in a "perfect" way"; "Running that perfect audit round should result
in perfect production code"; "In the definition of "perfect" production code
should also be that the integration is "perfecty" generic and can run every
install in a "perfect" way, resulting in "perfect" savings". The
carries on R11-PRE-OBJECTIVE-FUNCTION restate these; the install population and
comfort bounds are the orchestrator's to set (owner, 2026-11-13 ~20:28Z: "this
is yours to set using your best judgement"), and a carry holds the values and
basis. Convergence is the standing aim: "for objective bugs, I want the codebase
to converge towards 0 bugs with infinite number of audit rounds" (2026-11-13
~17:46Z), and every dimension covers its whole scope every round, never a
sample (2026-11-13 ~17:40Z, "I want future rounds to always check everything in
their dimension, not only small samples").

### R11-INTAKE-R10-RESIDUE and the carries

R11-INTAKE-R10-RESIDUE (issues #2731, #3314, #3369) is a holding group, not a
work unit: the round-11 architect (`architect-planner.md`) triages each carry and
re-homes it to the group owning its seam, or refuses it with a reason, and the
group closes when it holds no carry. Every `moved R11-INTAKE-R10-RESIDUE` mark
adds to it (a carry bound for a `carries-open` group was re-routed here under the
2026-11-12 ruling that self-fed work which would move closure goes to round 11). It holds, besides unplaced residue: the three text-verification
carries (see rulings), the card items P11, P13 and X2 that no R11-PRE group
builds, the Darwin self-test reds with no owning group (`cloud-setup.sh`'s
`mapfile` under bash 3.2, `gh_calls.py`, `heartbeat.sh`, `hooks_setup.py`,
`train.sh`, and unverified `bus.sh`, `open_pr.sh`, `pr_args.sh`, `update_pr.sh`,
from the macOS-lane seat's logs, which are out of tree), the entries of the
five carry files closeout-prep part 2 deleted (`#3553`, merged as `a72ae19952`
on its round-4 merge verdict at `aeb5f761cb`: `carry-201`, `carry-1922`,
`carry-2065`, `carry-2066` and `carry-2075` are gone from
`dev/programme/carries/`, and `carry-1645` records its answer `16e8fef927`;
each removed entry is a carry headed `From r10-closeout-prep-p2`, on this group
or on the group owning its seam), and carry 18
(segmented hot-water LP, conditional on `r10_partload_pricing.py`), whose
placement is the orchestrator's, not the owner's.

### What the intake group also holds from closure

Beyond the residue named above, these were routed to R11-INTAKE-R10-RESIDUE or to
the round-end pass at closure, each with its source:

- **The carry-file entries `#3553` re-homed** (stated above).
- **The soak defect candidate** above, as a D1 item.
- **R10-CI-PRIORITY-PAUSE's forward carries** (`priority_cancel`, `is_hotfix`,
  backfill; the group's own work merged as `#3560`).
- **R10-ARCH-DOCS-DELTA carries 8 and 14**: the re-read of `dev/audit/README.md`
  (playbook) and `dev/README.md` against `#3451` and `#3491`, see the next item.
- **The D5/D6 CADENCE carry** (`CADENCE` D5:1, D6:1 in the code-owned
  `audit-find.js`): owed **before round 11's finders**.
- **Tooling friction is counted by family, not analysed per event** (card L8
  below). Counts at closure, from the orchestrator's sweep log
  (`$HPO_STATE_DIR/s14/sweep.md`, out of tree; grep it for `FRICTION` and
  `family`), each the last count the log states:
  - `hung-instrument` 2: a `preflight.sh` run blocked 7 min in a background job
    with no stdin guard; a tick pass stood 24 min in `bus.sh` orphans.
  - `generated-block-stale` 3 (`#3532` twice, `#3568`): `update_pr.sh`'s
    body-only refresh renders a figure block without the pull request's base sha,
    so after main moves it writes `MODE: FULL` where `pr-contract` renders
    `SCOPED`; repaired by hand with `figure_block.py refresh --base <pulls
    base.sha> --head <head>`; card L9 covers it.
  - `pipefail-sigpipe` 3 sites: the `app_approve.sh` carry-tip regression from
    `#3514`, the flaky `gh_transient` census row it also caused, and
    `open_pr.sh` line 125; the class (`printf | grep -q` under `pipefail`, 8+
    instances) owes a lint barrier proposal and a carry on R11-INTAKE-R10-RESIDUE.
    The same incident is also logged once as `fail-closed-on-unseen-state`.
  - `flaky-selftest` 3: the bus self-test's concurrent-confirm check (P354),
    which failed `#3566` twice in CI and never locally, counted with `#3532`'s
    `gh_transient` row.
  - `roster-drain-refusal-unlogged` 1: the drain digest keeps only the last
    pass's refusal reason.
  - `relay-handoff` 1: a recycled dispatch seat's relay monitor died with the
    seat and left a merge verdict unposted; the landing chain now carries the
    verdict nonce itself.

  - `carry-fold` 2: `carry_audit.landed` reads an item landed when its
    destination already holds any carry of the same topic or pull request, so
    `carry_fold` folds nothing for a later item of a topic folded before
    (`#3553` round 3 stopped on it); cure: `roster_edit append-carry` by hand.
    The other instance was a remote rejection mid-fold, cured by a rerun.
  - `relay-serial-update` 1: a relay pass is serial inside one `update_pr.sh`
    full prepr (about 35 minutes for `#3491`), so every other handoff's relay
    waits behind it; cure: gating relays go through the landing chains, and the
    push holder is never killed.
  - `relay-ev-case`: `cloud_relay.sh` refuses a verdict whose `ev/` holds names
    differing only in case (a case-insensitive checkout keeps one); cure: rename
    them apart and re-publish the verdict ref.
  - `approval-retriggers-gate` 2 (`#3595`, `#3596`): the cure is under "What
    merged".

  Counts from now on go on #3394. Per-family RCA runs once at round end.

### Re-routed groups and pull requests, with the next step

Rerouting is a roster edit, not a closure: `set-after <group> …,R10-CATALOG-PR`
(which replaces the whole after-list, so read it first and keep only afters that
are neither done nor gating; the way `roster_lib.closeout_exempt` exempts a group
from the closeout refusal; a `deferred` stage alone is not exempt, and no
`roster_edit` op writes `resume.host`) plus a `next_step` pointer holding the open
pull request, the refs and the carry count. **The refs a group names survive the
prune** (closeout keeps the head ref of an open pull request and a not-done group's
design refs, and any ref younger than six hours); a `handoff-wip` ref of a re-routed
group that is older is deleted unless tagged, so read a missing one at
`archive/handoff-wip/<topic>` (`git tag -l 'archive/handoff*/<topic>'`). Each
group's exact refs, stage and carry count are in its `resume.next_step` on the
roster at the final sha and are not copied here. The extra prune pass after the
catalog pull request (owner, 2026-11-14 ~11:20Z, "Keep them open") leaves main,
every open pull request's head, `handoff/audit-r10-plan`,
`handoff/audit-r10-roster` and `heartbeat/orchestrator` and tags the rest;
**restore design refs from their tags before an L or XL dispatch**:
`git push origin refs/tags/archive/design/<g>:refs/heads/design/<g> refs/tags/archive/design-verdict/<g>:refs/heads/design-verdict/<g>`.

The groups below were routed to round 11 at closure; a group that merged first is
`done` on the roster and its row is moot (list the survivors with `python3 -c`
over `groups` for every group whose `resume.stage` is not `done`, `absorbed` or
`refused`). The judgement the roster does not hold:

| group | pull request | next step |
|---|---|---|
| R10-PROCESS-SLIM | `#3451` | an earlier verdict `Fix review: blocked 467f58500d introduced-red` (`tests/doc_claims.py`: `dev/README.md`'s machinery figure still cites the `postmerge.py` `state_docs.py` call the diff deletes) was repaired, and `Fix review: merge 7f4a9be89c` followed (2026-11-15T04:02Z); the pull request is CONFLICTING at that head, and the merge-repair handoff `archive/handoff/r10-process-slim-p2` at `c314960799` (a live ref until the closeout archives it) awaits a delta review; stays held while it deletes `proposal-triage.md` (owner, 2026-11-14: the contract is kept, once-per-round shape); part of the pre-round-11 gate |
| R10-SEAT-IDENTITY-P5 | `#3491` (owns issue #3134), merged as `099d4fa3f2` (2026-11-15T03:48Z) | merge verdict at `a720d3ed63`; then a Darwin-only defect (`seat_gen`'s `ps_start` reads `ps` `etimes`, which macOS lacks) was built in the pull request by a local fixer (overnight decision 2026-11-14 ~23:02Z), repair handoff `handoff/r10-seat-identity-p5` at `75d6b5fe82`; moot; its delta re-read is under the delta re-read section below |
| R10-OUTSIDE-CONTRIBUTOR-CYCLE | `#3521` (part 2; part 1 merged as `#3514`) | contributor-cycle build; carry 2 (three live fork checks) is the orchestrator's: a test fork under the mandate's admin rights, each admin write read back and logged |
| R10-SELFTEST-SCOPE-UNION-GUARD, R11-SELFTEST-SCOPE-MAIN-UNION-RERECORD | `#3551` | last verdict `Fix review: blocked 00a470f7b7 mutation-vacuous`: two mutants survive, M3 (the `shrink_gaps` deletion exemption widened from status D to every path the diff touches) and M1 (`table_base`'s merge-base replaced by the bare ref); no repair fixer was dispatched (overnight decision 2026-11-14 ~22:22Z) because card L9, ruled yes, generates the table and replaces what this pull request builds: round 11 decides repair or close; the guard (C) was round 10's, the bot re-record (A) is round 11's and edits the code-owned `.github/workflows/governance.yml`; the analysis lands as `dev/audit/rca` with a `bugclasses.json` entry |
| R10-CLOSEOUT-PREP part 2 | `#3553` | merged as `a72ae19952` (2026-11-14 ~23:46Z); its removed carry-file entries are under R11-INTAKE below; moot |
| R10-NUDGE-RETIRE | `#3566` | `nudge.md` binds Cursor and ZCode sessions only; retire it as written. Held on a CI-only flake its diff does not reach: `governance / instrument-self-tests` failed at head `3487296ce9` on the bus self-test's concurrent-confirm check (P354) twice, the second time as job 132606865401, while the repair fixer measured 0 failed at the head, the merge base and head plus main and 8 of 8 concurrent runs locally; the body answers the red as that flake. Next: one more run on a quiet runner, then the delta review |
| R10-COP-LEARNER-DRAW-FLOOR | `#3593` (owns issue #3106) | L, design first (design ref `design/R10-COP-LEARNER-DRAW-FLOOR`); carries 84e73ec4, 35931f4b, the duty-gate-to-ceiling gain measurement and carry 2 (#3106's linearity measurement on the owner's install: the linear set-point-to-draw map fails there, with a floor-end excess and a ceiling-end shortfall); `mutation-autofix` had left two added sites alive at an earlier head (`accuracy.py:1004` and `coordinator.py:962`, both `CMP_BOUND`), and the head now carries a later `ci: pin killed mutants` commit (`5cf3425240`); non-gating, round 11 if unmerged; owner, 2026-11-13 ~20:25Z: "Yes, design can be prepared now." |
| R10-DRAW-MAP-EVIDENCE | none when this file was written (`#3597`, part 1, was closed by `open_pr.sh` when its row push was refused as a non-fast-forward); part B is handed off at `handoff/r10-draw-map-evidence-b` `8c1508d9c1` with its body on `handoff-body/r10-draw-map-evidence-b`, and opens after `#3593` | owner order 2026-11-14, by name, non-gating, to round 11 if unbuilt at the stamp: build the correction the data supports and improve the data collection and the experiment mode so a later round can correct the set-point-to-draw map; part 1 found the ceiling store empty because the ceiling probe never armed on the owner's install; part 2 is a design review; his diagnostics file stays local |
| R10-START-COUNTER-EDGES | `#3598` (the build), `#3420` (the contributor's design, held open) | round-2 design approved 2026-11-14 (`Design review: approve 18655c84b679af92a83bdccbd4c1a2e88faec8ec`, carries v0 to v5 in that verdict); the reviewer measured one size-L pull request of about 15 files reaching 30 of 33 closures (design ref `design/R10-START-COUNTER-EDGES`); the build opened as `#3598`, non-gating, and goes to round 11 if unmerged at the stamp; owner, 2026-11-13 ~20:18Z, verbatim: "Fire it now, and if it is not merged when the stamp is ready, it goes to round 11 rather than holding closure" |
| R11-OUTSIDE-HONEST-STARTS-RUNS | `#3529` (contributor's, stacked on `#3481` and `#3532`, both merged); the build is `#3602` | design round 2 approved (`Design review: approve 0c692c86d2ff28fef984db5833219514fff52d77`, ref `design-verdict/R11-OUTSIDE-HONEST-STARTS-RUNS` at `caab288c05`; the roster's `next_step` still says round 2 is in flight, which is stale); the handoff review returned `blocked architecture-unsound` (probe `04e5bcfca3`); departures 1 and 3 went to a design amendment, approved at `a63a2ca6cd` (`design-verdict/R11-OUTSIDE-HONEST-STARTS-RUNS` at `6e5cc74429`), and blocks 2 and 3 to a repair fixer. **Design ruling c1 (a priced start engages on a modulating install too) is the owner's and undecided**: the head builds the recommended arm, the body says pending owner confirmation, and it is not merged on that ruling without tvofi; the other arm is one predicate, and the reviewer measured that both claimed fixtures still move under the `_engaged` predicate alone (`cycling_cost` 44.96 to 46.39 kWh, `everything_on` predicted cost 60.27 to 64.88). Non-gating (owner, 2026-11-14 ~19:18Z: "the honest fix is non gating") |
| R10-PLAYBOOK-ROUND-START | `#3600`, merged as `2a257fce08` (round-1 review `blocked evidence-cut` at `e3df1f1ca6`, repaired at handoff `76aca12e6f`); moot | the round-start step: the playbook must keep working with the objective function and the improved dimensions, and make the round orchestrator pick up the previous round's carries and pre-finder groups (owner, 2026-11-13 ~19:26Z); one section of `dev/audit/README.md` that fits the existing caps; part of the pre-round-11 gate above |
| R10-GH-READ-RESIDUE-P3, R10-RELAY-NOBODY-STALL, R10-FLY-OPENER-STALE-ENV, R10-TICK-RESIDUE-P3, R10-TRAIN-REVIEW-PRESETTLE, R10-UPDATE-PR-SEAT-WORKTREE, R10-PREPR-DARWIN-SELFTEST-LANE | none | the seven deferred instrument groups reopen as written, brief and carries kept; under the freeze shape below each is a proposal first |
| R11-PRE-* | `#3575` (the objective function) merged as `4eea986a62` | the start gate above |
| R11-INTAKE-R10-RESIDUE | none | holding group, below |

Merged first, carries open (the carries stay on those groups; build or mark
each): R10-GATE-DEFER-BARRIER, R10-PREPR-RESIDUE, R10-REVIEW-DISPATCH-RESIDUE,
R10-STANDING-CONTRACTS-P2, R10-SUITE-ENV-RESIDUE. `R10-REVIEW-DISPATCH-RESIDUE`'s
part-6 handoff ref (`handoff/r10-review-dispatch-residue-p6`) had no open pull
request at closure.

### Outside contributions

Outside work is ordered first in every queue and the rule since 2026-11-13
~19:35Z is that it **always folds into the ongoing round unless the owner or the
outsider explicitly defers it** (tvofi, verbatim: "outside and owner filed
findings and requests should always fold into the ongoing round if not
explicitly deferred by the owner or outsider"). For two items the test was the
closure date (2026-11-13 ~19:45Z, verbatim: "Fold the two outside PRs in if they
do not change the closure eta, round 11 if they do. Design can be prepared in
parallel in any case"); the ruling of ~20:05Z then fixed the meaning: whatever
is unmerged at closure goes to round 11. **The contributor of `#3529`, `#3420`,
`#3434` and `#3437` is Bankaifan.** On 2026-11-14 ~19:18Z tvofi ruled "the honest
fix is non gating", taking R11-OUTSIDE-HONEST-STARTS-RUNS off the closure path.

- `#3529` (honest starts and runs): R11-OUTSIDE-HONEST-STARTS-RUNS, design round
  2 approved, built on `handoff/r11-outside-honest-starts-runs` and open as `#3602`, ruling c1
  open for the owner (row above). **A decisions post with the plan link is owed on the pull request**
  (the outside-intake ruling: a decisions post first, then
  `python3 tools/audit/seat/outside_intake.py answer`); read `outside_intake.py
  list` for which outside pull requests have been answered.
- `#3420` (the contributor's design for duty-switch restart learning, with an
  implementation pushed onto it): held open; its round-11 group is
  R10-START-COUNTER-EDGES. The planner pricing it asked for merged as
  R10-DUTY-SWITCH-PLANNER-PRICE (`#3526`), and `#3569` is that group's carries
  part.
- `#3439` (disinfection step notice) was adopted and merged as
  R10-DISINFECTION-STEP-NOTICE (`#3581`).
- `#3440` was closed on 2026-11-14 with the reasons posted (comment
  6868429012) after the owner's order (~00:21Z, verbatim: "Would the planner be
  more accurate if it priced the lift? If yes, start a group for it (non gated),
  else, close it and tell them why") and an analysis that read NO: the COP
  default depends on the outdoor temperature only and the power-feedback loop
  absorbs the lift.
- `#3456` was closed with thanks on 2026-11-13 (delivered by `#3512`).
- Short status posts went to the contributor on `#3529`, `#3439` and `#3420`
  after the replan (owner order, 2026-11-13 ~20:18Z). The contributor's own
  fixer and reviewer cycle is the permanent shape (R10-OUTSIDE-CONTRIBUTOR-CYCLE).

### The pipeline design group

R11-PRE-PARALLEL-PIPELINE is the owner's order of 2026-11-14 ~10:10Z, verbatim:
"Have a fable seat with web access and sendmessage capability study and design a
high throughput pipeline, using a branch parallel with main. Study publicly
available designs and standards. The design should be planned and built (if it
will save significand wall clock time in a programme) before the fixers in round
11 start." Design first (decision 0014); build only on `Design review: approve`
and a cost test (wall-clock hours per programme against a measured baseline,
with its null control) that shows a significant saving; a design that does not
pay records that and builds nothing. Constraints already ruled: no CI capacity
widening by billing, runners, plan or second account (owner, 2026-11-13 ~07:31Z,
verbatim "No." on the billing raise); `main`'s protection and the required gate
are not loosened; policy changes go to the owner's review; nothing of the group
started a CI run before the closure stamp without the orchestrator's word; and
it never took a seat, reviewer or CI priority from round-10 production. Fable
seats for designer, design review and build (owner ruling for L and XL work,
2026-11-11).

The owner's answers to the designer's questions, 2026-11-14 ~10:20Z (verbatim:
"1. Ruled out. 2. Every change must not stay its own PR. 3. Yes. 4. Three days
is fine but about maximum."), which the orchestrator read and relayed to the
designer as: an organization transfer and the native merge queue are dropped;
reviewed work lands on the integration branch on its verdict and scoped checks,
with the FULL suite per batch (a change to `orchestrator.md` section 11, which
is the owner's review). Answer 4 preceded the design review's five-to-six-day
estimate and the later rulings, so it is not the plan; the state and the
current rulings are in constraint 1 above. The answers are on the group's
`resume.note`, because a design-stage group with no files is a receiver only
and the roster refused them as a carry. **They supersede the first item of
`dev/audit/README.md`'s "Round 11's opening plan carries"** (the
organization-transfer decision), which that file still lists as open and which
is owed an amendment (see Owed), and make the held groups that item names moot
only if the integration branch is built; the roster's note, not the README,
says which. The designer's baseline (a handoff-to-merge decomposition over the
window 2026-11-07 to 2026-11-14) and harness are out of the tree: **the
orchestrator holding the design must put the harness on the design ref**
(`design/R11-PRE-PARALLEL-PIPELINE`) or the cost test has no enumerator and its
figures are not figures (`writing-for-agents.md`).

### Rulings that bind round 11

Until R11-PRE-RULINGS-FILE merges these exist in the tree only here (the
orchestrator's notes are not in it). Each is verbatim and dated.

- **The instrument freeze shape** (tvofi, 2026-11-13 ~19:17Z, verbatim): "Under
  the round 11 instrument freeze, my intension is that all instrument fixes
  should be done locally, all proposals consolidated and triaged at round end,
  and those with good cost/benefit fixed in the beginning of round 12". And
  ~20:04Z: "This should be the shape for instrument fixes, prototype local fixes
  in-round, file proposal permanent fixes for consolidation and cost/benefit
  that is carried to the start of next round". So an instrument fault gets a
  local prototype, kept runnable and named, and a numbered proposal citing it;
  no instrument group or repair fixer opens mid-round; the exceptions are
  production defects, owner orders and a red required check on main (card P11).
  Applied to round 10 from ~19:42Z (verbatim: "For the rest of the round, apply
  instrument fixes locally and file as proposals to be triaged for round 11. The
  exceptions (main red etc. applies)"); in-flight instrument pull requests
  finished.
- **Fixer carry limit by kind** (tvofi, 2026-11-13 ~20:51Z, verbatim: "you may
  have a fixer have more carries based on their kind, locally for now and filed
  as a permanent proposal"): light text carries may exceed five per part;
  findings owing their own proof keep five (PC-1113-08).
- **Text verification** (tvofi, 2026-11-13 ~17:29Z, verbatim): "Do 1 in round 10,
  and 2 and 3 in round 11 sequenced as you recommend. Code comments in
  instruments and the documents that describe the instruments, developer and
  other non-static documentation also in scope for 3." where 1 is all
  user-facing text in production, 2 every sentence in all documentation, 3 all
  code comments. ~17:31Z: "The test suite comments are in scope. Also, since
  1-2 is done before 3, they may not trust code comments, only the actual code
  behaviour". Method: judge every sentence against the code that decides the
  behaviour, never a comment or docstring (a reviewer blocks a row whose
  evidence is one); pin every mechanically checkable claim with a test;
  documentation first, one part per document, then comments by module after the
  round's production pull requests on hot files merged; frozen round records are
  static and out. The three carries are on R11-INTAKE-R10-RESIDUE. The reason:
  a false config-flow sentence ("never writes a recommended space set-point")
  misled the owner while the house sat at 16 C behind a stuck set-point (v7.1.12
  to v7.1.15); his words, 2026-11-13 ~16:26Z: "the incorrect conflict flow text
  and the release notes omission are defects in themselves" ("conflict flow"
  read as config flow).
- **Process convergence** (tvofi, 2026-11-13 ~18:06Z): the agentic process
  converges "against optimal quality, lead time and token effectiveness, both with
  the number of audit rounds, and also within the rounds by the self-feeding
  mechanisms", including the machinery's support of the orchestrator's
  long-horizon stability (no slipped tasks, no lost objective, adaptation to
  roadblocks) and of following the plan (roster, Gantt, replanning).
- **Plan page** (tvofi, 2026-11-13 ~19:59Z to ~20:01Z, verbatim): "The plan html
  for round 10 should also not show the round 11 groups"; "for the permanent fix,
  future round items should be possible to view on a separate tab with a
  separate preliminary gantt"; "The copy you send me tonight is the prototype of
  the permanent one, future round tab included". The prototype's builder is
  session scratch only.
- **Production share and the open-PR cap** stay as `dev/audit/README.md` states
  them; the owner's 2026-11-13 ~07:38Z ruling (verbatim: "All production groups
  now goes above the cap"); the caps in force are volatile and are on the
  successor issue.
- **Hotfix checks** (tvofi, 2026-11-09): a hotfix runs
  `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` or none; CI is the
  authority. A non-required red never blocks a merge and never briefs a fixer
  (2026-11-07, restated 2026-11-09): only a red the tick's owed-reds line names
  does.
- **Records** merge near a stamp as batches (tvofi, 2026-11-04): triage and
  roster records ride their own branches, and a cancelled record run is
  cancelled, never closed.

### Loop-study rulings L1 to L9

tvofi, 2026-11-14 ~17:12Z: **all nine yes** (L6 all three parts; L7 at k 0.8 and
15 % machinery hotfix share; L8 once per family at round end), **built at round
11's start under the instrument freeze**. The study is out of tree at
`$HPO_STATE_DIR/s14/seat/loop-study-1114/REPORT.md` (its scripts under `data/`).
Its answers: the loops prevent recurrence partly (65 % of bug classes that had a
barrier still produced instances), introduce almost one follow-up per closed
machinery item (0.74; 0.95 in the last week), and the product queue converges
while the machinery queue does not. The cards, one line each:

- **L1** a loop ledger: `caused_by`, `family`, `cm_kind` on every RCA and
  triage ACCEPT, `parent` on a roster group, one enumerator for recurrence per
  family and the loop's growth rate k; fits R11-PRE-ROUND-METRICS.
- **L2** countermeasures in order delete, self-repair, narrow, new refusal last,
  a new refusal printing its own repair command and a shadow run on the last 20
  healthy heads.
- **L3** a machinery check that cannot read its input (a cancelled run, a job
  still running, a spent API budget, a stale checkout) reports "unread", not red;
  three in a row escalate; product checks keep failing closed.
- **L4** price induced work in the cost test: expected follow-up items and the
  generated artefacts the change stales in open branches.
- **L5** triage by instrument at round end, not by proposal; the third accepted
  change to one instrument in a round owes a retire, simplify, redesign or leave
  decision.
- **L6** probation and retirement: at round start list each countermeasure of the
  previous round with its family's recurrence and children; a machinery check
  whose last ten reds include no true defect becomes advisory; when main reddens
  on a machinery check within ten merges of a machinery change, revert that
  change first.
- **L7** a kill criterion: k at or above 0.8, or machinery hotfixes above 15 % of
  code merges, for two consecutive weeks stops RCA building and proposals until
  the next round start; product defects are exempt.
- **L8** root-cause analysis of machinery friction by family at round end; a
  product defect, a release defect or an outage keeps its own RCA seat at once.
  **This reverses part of the "RCA dispatch immediately" ruling and the
  third-instance rule, for machinery only, and already binds.**
- **L9** extend "generated after merge" to four artefacts today's reds came from:
  the self-test scope table, figure blocks in pull-request bodies, brief line
  pins, and the stamp line of the claim files; it makes R10-SELFTEST-SCOPE-UNION-GUARD
  and its round-11 sibling unnecessary and extends R11-PRE-SHARED-FILES.

The study's own known error, left as written: case study 2 and card L3 say the
owner's 2026-11-11 "advisory on push" ruling was not built; it was built by `#3500`
(the push report-only set in `tools/ci/gate.py`).

### The delta re-read owed for `#3451` and `#3491`

Owner, 2026-11-12 (verbatim in the sweep log): the residue after-edges were
removed from R10-ROUND-PLAYBOOK-FINAL and R10-CLOSEOUT-PREP in exchange for one
delta re-read before the stamp. `#3491` merged as `099d4fa3f2` before the stamp
and `#3451` did not, so only `#3451`'s line is "not merged at stamp"; `#3491`'s
re-read is owed now (the roster marks ARCH-DOCS-DELTA carry 14 implemented at
`e901e9ef29`, which predates `#3491`'s merge, and carry 8 is moved to
R11-INTAKE-R10-RESIDUE). The re-read is owed when each lands:
read the merged diff three-dot against `dev/audit/README.md` (phase table,
lessons, closure and round-11 sections) and `dev/README.md`, one line each, in
this file. The carry-42 re-read of the instrument residue groups is done and its
roster carry is marked implemented; `#3451` stays held while it deletes
`proposal-triage.md`.

### Local prototype inventory

The owner's rule (2026-11-13: prototype instrument fixes locally in-round, file
the permanent fix for round-end consolidation, decision 0013 forbids a reusable
instrument living only in scratch) left these scratch instruments, all under
`$HPO_STATE_DIR/s14/` out of tree, each owing a ref or a tree home and the
proposal named:

- `seat/closure-runbook/`: `make_queue.py`, `sim_queue.py`, `fill_shas.py`,
  `retarget.py`, `extra_retarget_lines.py`, `main_only_roster_delta.py`,
  `groups_now.py` and `RUNBOOK.md` (the 18-step closure order). Owes: a
  `retarget` arm in `closeout.py` (the bare-citation rewrite is a file rewrite,
  see the trap below) and `roster_queue` handling for a carry whose text a
  `--match` cannot quote (an index-keyed mark such as `R10-CI-PRIORITY-PAUSE` carry 12 is a by-hand
  op, which `roster_queue.replay_unsafe` refuses in a queue).
- `seat/closeout-prune-1114/`: the pass-2 refs-file procedure
  (`heads-minus-keepers.txt`, `PRUNE-TO-4.md`, `DECISION.md`). Owes:
  `prune_refs.py --no-age-keeps` and `--claude-sessions prune`.
- `seat/replan-*/build_tabs.py`: the two-tab plan page (round-10 view and a
  future-rounds tab with its own preliminary Gantt). Spec for R11-PRE-PLAN-RENDER.
- `plan-proto/` with the local ref `refs/proto/plan-gating`: a gating-only
  costing of the plan on a fixture roster, never pushed.
- `seat/pipeline-design/` (`design.md`, the baseline harness, `group.json`):
  **put the harness on `design/R11-PRE-PARALLEL-PIPELINE`** or the cost test has
  no enumerator.
- `seat/loop-study-1114/data/`: L1's prototype; `seat/soak-read/`: the D15
  bundle-read scripts.
- Proposal owed besides: **a closeout default `--orch-root` that cannot delete
  `HPO_STATE_DIR`** (trap below).

### The issue set at closure

#3394 is the successor (#201 is capped at 2,500 comments). `closeout.py --apply
--successor 3394` refuses on any open issue not wired to a post-closure group
and not in its exempt list; #201 is wired to R10-CATALOG-PR so the owner's
sentence holds. `brief_lint.mjs` refuses an issue that has both a carry file
and a live roster group, so `#3601` landed a roster with #201 unwired; `#3553`
deleted `dev/programme/carries/carry-201.json`, #201 was re-wired on the roster
branch, and the follow-up record landed that roster. Closeout pass A's issue
exemption reads the `--roster-file` copy. The catalog step ends #2965; #2728 is closed after prune pass 2
(so its target holds when it closes); #3139 closes with the docs pass; #2257
with `#3481`. The mapping of the open issues at 2026-11-14: #2731, #3314 and
#3369 to R11-INTAKE-R10-RESIDUE; #2999, #2389 and #3313 (recurring-friction
families) to R11-INTAKE-R10-RESIDUE; #3106 to R10-COP-LEARNER-DRAW-FLOOR; #3134
to R10-SEAT-IDENTITY-P5; #2965 to R10-CATALOG-PR. The live list is
`gh issue list --state open --json number,title`; every open issue has a
scheduled, deferred or refused disposition (`delivery-status-tracking.md` item
5).

## The seats and who may do what


- **Identity** (decisions 0011, 0013; `CLAUDE.md`). Pull requests are authored
  by `hpo-author` through `tools/pr/app_push.sh`; verdicts post as
  `hpo-approver`; only the orchestrator writes to GitHub. A seat pushes refs
  only: a fixer `handoff/<topic>` and `handoff-body/<topic>`
  (`tools/audit/seat/body_push.sh`), a reviewer its verdict on the probe ref its
  brief names. **Commits take the author from the environment**: set
  `GIT_AUTHOR_*` and `GIT_COMMITTER_*` to `hpo-fixer` and the noreply address
  in every shell that commits, because the session environment pre-sets them to
  the owner and beats `git config` and `-c`. Check `git log -1
  --format='%an <%ae>'` after each commit.
- **Standing seats**, each on its own contract in `dev/governance/roles/`:
  `standing-merge.md` (operates the train, never chooses what merges) and
  `standing-dispatch.md` (dispatch, relay, verdict confirm), plus
  `proposal-triage.md` (opus; a proposal gets a ruling before it is routed).
  The tick and roster seats are retired into the `tick-digest` and
  `roster-drain` beat rows (`standing-tick.md`, `standing-roster.md`): read the
  digest, queue roster ops for the job. The orchestrator sends queue lines and acts on
  reports; `tools/audit/seat/pulse.py` and the sweep's liveness step restart an
  absent one. **The orchestrator never runs `train.sh add`, a roster op or a
  dispatch inline** (tvofi, 2026-10-21 and 2026-10-27): it confirms a verdict on
  the bus and hands the merge seat the PR head, the verdict's reviewed head and
  any carry judgement.
- **Seat placement** (tvofi, 2026-10-24, 2026-10-28, 2026-10-30, 2026-11-01,
  2026-11-08, 2026-11-11). Cloud seats are uncapped and fire through
  `tools/audit/seat/cloud_dispatch.py` and a remote trigger; a cloud run is
  one-way, nothing comes back on SendMessage, and new fixers and repair rounds
  go to the cloud. Local seats carry the work the orchestrator must steer
  (M-and-larger, critical-path, repeatedly blocked), at most seven counting
  fixers, reviewers and the standing ones (2026-11-08); **when the local
  1-minute load is far above the core count (the ruling's own figure was about
  50 on 8 cores), L, XL and critical-path fixers go to the cloud too.** A cloud
  seat silent past about 2.5 hours with no ref pushed, or a prompt that fails
  twice on the cloud, is re-run locally after an `ls-remote` guard against a
  late push. Fixers run at medium effort; a mechanical turn takes sonnet or
  haiku; model routing is under the decisions section. A Fable seat or fire
  that fails for credit or quota is re-fired on `claude-opus-5-5` (owner,
  2026-11-14; expires when round 10 closes).
- **The open-PR cap** is the owner's, restated on #3394 each time it moves, and
  it is a count of open pull requests that gates only starting a new roster
  group. `pr_cap.py dispatch-gate` counts in-progress roster groups against
  `HPO_WIP_CAP` instead, which is not the owner's rule: never quote its `WIP
  n/6` as the cap.
- **Record pull requests** (this file, delivery rows, roster batches) are
  reviewed by sonnet. A record seat's checks are `tools/pr/prepr.sh` with no
  closures skip, its CI-predict step, and `python3 tests/structure.py`.

## The instruments in daily use

`tools/audit/seat/INSTRUMENTS.md` is the operator's guide and the only
inventory; look an instrument up there before writing a loop, relay or helper
(`orchestrator.md` section 13). The ones a session reaches for first are the
tick driver (`tick_loop.sh`, `orchestrator_tick.py`), the verdict path
(`bus.sh`, `cloud_dispatch.py`, `cloud_relay.sh`, `review_packet.py`,
`review_carry.py`), the handoff path (`open_pr.sh`, `update_pr.sh`,
`body_push.sh`, `body_patch.sh`), the merge path (`train.sh`, `merge_train.py`,
`tools/pr/app_approve.sh`), the roster (`roster_edit.py`, `roster_sync.py`,
`state_docs.py`), the sweep (`sweep_render.py`, `sweep_template.md`), and
`tools/audit/worktree_gc.sh` after each merge. The critical path is whatever
`roster_lib.critical_path(roster)` returns over the open groups of the roster
(`tools/audit/seat/roster_lib.py`; load the JSON and call it), never the plan
page's date alone. Comments on #3394 and on pull
requests are posted with `tools/pr/gh_comment.py` and read back
(`comment-readback.md`).

- **The seat interpreter.** Put the seat venv's `bin` and the repository's
  `tools/audit/seat/shims` first on `PATH`, and set `PYTHON` to that venv's
  `python3`; bare `python3` is 3.11 and `prepr.sh` dies on a PEP 701
  f-string. `tools/audit/seat/seat_venv.sh` builds it and prints where. A seat venv's `BASH_ENV`
  can make an instrument self-test pass vacuously: reproduce a red with
  `env -u BASH_ENV`. A cloud container may not put the toolchain on `PATH`
  either: prepend `/opt/hpo/venv-ci/bin`, run with `env -u BASH_ENV
  PYTHONPATH=tests/hastub`, and through the agent proxy loop
  `?per_page=100&page=N` on the `repos/<owner>/<repo>` path, because `gh api
  --paginate` follows GitHub's numeric-id `Link` URL and gets 403 after page one.
- **Anything over about 60 seconds runs detached** through
  `tools/audit/seat/daemonize.py --log <file>`; read the log when it exits and
  do not block a foreground turn on it (tvofi, 2026-10-30).
- **Never `git stash`**: every worktree shares one stash list and a pop can take
  another seat's work. Commit to a scratch branch or copy the files.
- **No `pkill -f` or kill by pattern**; stop only a PID you started. A wait loop
  that `pgrep`s its own pattern matches itself.
- **A GitHub poll is no faster than every 300 s**; prefer `git ls-remote` and
  `git fetch` to REST. Heads of moving refs are read with `ls-remote`, never
  from `FETCH_HEAD` in a shared worktree.

## The mandate

The authority to approve as the owner is a record, read from the API at the
moment of use and trusted nowhere in the tree: the newest comment by `tvofi`
on #201 or #3394 whose first line is `MANDATE: agents may approve as tvofi, scope
<code-owned|budget-raise|all>, from <ISO> until <ISO>`. Its id, scope and
dates are on #201 and in the sweep prompt; decision 0013 and its 2026-10-02
and 2026-10-14 amendments are the rule. After `until`, decision 0007's
per-pull-request owner review is the rule again.

- **Under scope `all`, the orchestrator approves code-owned, policy and
  budget-raise merges itself** (tvofi, 2026-10-20 and 2026-10-27, "my approval
  is still not required during your valid mandate to act as me"). Do not park a
  group as waiting on the owner's review. Cite the mandate in the review and
  merge body in the grammar `MANDATE_CITE` reads (`mandate #<id>` or a bare
  `issuecomment-<id>`, never backticked), exactly one id per review.
- **A raise is still searched for.** A budget raise under the mandate owes
  `## Raise justification`: each payment tried and the `Architecture score: dS`
  line `tools/audit/archscore/score.py --diff` printed. The mandate waives the
  owner's signature and not the search (`CLAUDE.md` rule 2). A raise the only
  sound payment calls for is the orchestrator's to rule (tvofi, 2026-10-23); a
  seat's classifier denial of it is not laundered through the mandate, the seat
  is re-briefed or the work runs where the action is allowed.
- **The kill switch is deliberately loose.** `budget_raise_gate.py` voids a
  mandate on any later comment by the owner's account on #201 or #3394 that contains the
  stem of the verb "to revoke", in any case, on any line, beside that
  mandate's id. **An identifier counts**: a roster group whose name contains
  that stem voided it a second time (2026-10-31) and refused a pull request's
  `budget-raise-gate`. The first time (2026-10-21) a decision's text did. In any
  comment posted as `tvofi`, never write the stem next to a mandate id and
  grep the text for it first; say "withdrawn", or cite the mandate in a
  separate comment. The repair for a voided mandate is the owner posting a
  fresh one, or, as on 2026-10-31, editing the offending comment and
  re-running the failed jobs after a local gate PASS. The barrier is the
  mandate-guard roster group's carry (`gh_comment.py` refusing the pairing).
- **What the mandate does not cover**: anything past its `until`, and a change
  to what a seat must do that has no review verdict behind it. While
  `tvofi`'s own latest decisive review is CHANGES_REQUESTED the gate refuses.
- **While the owner is away** (tvofi, 2026-10-28): decide by the recommendation,
  record the decision and its reason, never stall on an owner flag.

## Merge, train and stamp

1. **Evidence.** `gate` passed at the head, and a `Fix review: merge <sha>`
   verdict from a reviewer who measured this head, or a carry
   (`tools/pr/app_approve.sh --carry <verdict> <head>`; `review_carry.py` says
   whether a moved head needs its own review). `orchestrator.md` section 11 is
   the list. Read check-runs from `/repos/<owner>/<repo>/commits/<sha>/check-runs`
   and not `gh pr checks`, which shows the latest run per check and hides a
   red behind a later green; a context with no run at a head is "not yet",
   never green, and a `CANCELLED` required context is not a verdict (rerun it).
2. **Queue.** The orchestrator picks membership and order, critical path first,
   and hands the merge seat each PR, its reviewed head and the mandate. The
   queue entry's `verdict` is the **reviewed PR head** from the verdict's first
   line, an ancestor of the live head, never the commit `bus.sh confirm` prints
   (that one is never an ancestor, and a wrong value reads as
   `STALE-VERDICT-CARRY`). `verdict_comment` is the comment id read back from
   the API.
3. **Train.** The merge seat runs `tools/audit/seat/train.sh` on its
   `RECOMMENDED` defaults, `batch`, one live train, detached; `train.sh add`
   loads a late verdict into the batch already running. **No merge outside the
   train** (tvofi, 2026-10-26): not a budget head, a policy head or a hotfix;
   those are reasons to batch. The one standing exception is a blocked critical
   path or a deadlock, merged by the merge seat with
   `tools/audit/seat/merge_pr.sh --mandate` (tvofi, 2026-11-11; used on
   2026-11-13 ~05:55Z when a serial entry's CI wait held green critical-path
   entries behind it). A refusal is reported and the head fixed, never
   landed another way. `--overlap` means the train does not wait on `main`'s
   gate between merges and each car's own CI must have run on its current
   head; batching is the `batch` subcommand, not that flag. Never a second
   train on the same state dir, and never `--allow-red`.
4. **The merge message** is a closing surface (`orchestrator.md` section 4):
   no negated closing keyword, never a custom `--subject`, `preflight.sh` as a
   filter with the intended issues as arguments, then read which issues the
   merge actually closed.
5. **After each merge**: `state_docs.py --push`, the merge's #3394 comment, the
   delivery row (the beat writes it; a frozen PR's own row costs a record pull
   request), the roster `set-stage` through the roster seat, and
   `tools/audit/worktree_gc.sh`. This file is updated in the same record pull
   request as the merge it records, and `updated-for:` names a merge that
   `origin/main` contains (`tests/entities.py` refuses a branch-local SHA, which
   a squash orphans).
6. **If a merge reddens `main`**: a behaviour change in the merged diff is
   reverted first and diagnosed after; a failure the diff cannot reach is
   established as such and is its own issue.
7. **Stamp.** The orchestrator stamps, `stamp.py --push --push-key <deploy
   key> --known-hosts <file>` (the stamping host holds both; the stamp seat's
   brief names them), never by hand and never in a branch; the closure stamp is
   `--round-close 10` with no `--bump`, and `--bump major` always refuses
   (decision 0016). It refuses a `main` whose `ci.yml` push run's `gate` is not
   green (`--allow-red` takes the cause in the release notes and on the
   coordination issue, and per the owner's standing ruling only while main's gate
   is still pending, never over a concluded red), a window with a merged PR
   lacking its row (`--allow-rowless`, with `--no-flush` to skip the record
   flush and the record beat dispatched after the stamp; every stamp from
   v7.1.12 to v7.1.17 needed both, because a merge's row waits for the record
   beat), and notes omitting a merged PR. `--dry-run` runs rules 1 to 6 and the
   register generator on a temporary copy; rule 7 (claims) is checked by
   `python3 tests/env_drift.py --claims-only <last tag>`. The deploy key's SSH
   on port 22 can time out from the stamping host: route `github.com` to
   `ssh.github.com:443` and verify the host key against GitHub's published
   fingerprints. A stamp empties both claim files (`claims-for:` becomes the new
   version), so a gating branch that added a claim line has it wiped, expected;
   and it strands every pre-stamp handoff on the claim file (PC-1113-18).

## Decisions taken — do not relitigate

- **`main` is guarded by three rulesets**, read from
  `/repos/<owner>/<repo>/rulesets/<id>` and never from here: `main-protect`
  (22628467), `main-protect-checks` (23698884; the required checks, one
  approving review, the code owner's review per 0009 step 6) and
  `release-tags-protect` (23937752). Rollback is one DELETE per ruleset.
  **Before adding a required context** confirm it reports on a pull-request
  head and not only on a push to `main`: one that never reports blocks every
  merge, a matrix change is a required-set change, `skipped` and `neutral`
  satisfy the rule, and a scheduled context made required blocks the merge that
  would repair it. `GET /repos/.../rules/branches/<branch>` is not
  bypass-aware: test a bypass on a probe branch with its own ruleset, both arms.
- **CI is one umbrella with one required check.** `.github/workflows/ci.yml`
  calls one file per unit, each check reading `<stem> / <job>`; `gate` is the
  only required context (`tools/policy/fixtures/required-contexts.json`),
  moved by `tools/ci/ruleset_cutover.py`. Autofix jobs dispatch `ci.yml -f pr
  -f base` once; the stamp precondition is the latest `ci.yml` push run's
  `gate` on `origin/main`. The approve steps and `approve_held_runs.sh` stay
  until M-3 decides (design `archive/probe/design-ci-rev4`, review
  `archive/probe/design-ci-review5`).
- **Model routing is Claude seats, per roster group** (`fixerModel`,
  `reviewerModel`, the `model` object). tvofi, 2026-09-09: Opus for
  orchestration, architectural fixes and review, survey, judge and production
  fixes; Sonnet for tests, tooling, docs, records and read-only reporting.
  **Superseded for L and XL groups** (2026-11-11 and 2026-11-12): L and XL work
  runs on Fable seats and nothing else does, and a reviewer's model is at least
  the fixer's. A model trailer on a merge or a stamp is the session's model, not
  a routing event. Effort and the mechanical-turn models are under the seats
  section above.
- **Merges land as merge commits** (0010); the merge body defaults to the pull
  request's title, so a closing keyword in a title reaches `main`. A closing
  keyword in a branch's commit message links an issue just as a pull-request
  body does (#503 acquired a false link to #457 that way).
- **Never re-gate an unchanged head.** A terminal CI result at that head is the
  gate evidence. Local runs exist for what CI cannot produce: the mutation
  proof, the failing test at the merge base, the finder's harness at both ends.
- **`_helper(self, ...)` is refused** as a decomposition: it erases moved
  references at zero cost, a measurement artefact.
- **#387 was fixed with the `env_drift` shape**, not by growing `alt_basins`
  nor lowering the coverage floor: tree and merge base in one run, computed to
  computed. The coverage floor is a literal, not an environment override.
- **The #1058 tie-break: a body long from disclosed self-corrections is
  re-cut by relocating them here.** `fixer.md`'s re-cut and *cutting evidence
  is never compliance* pointed opposite ways; a disclosed self-correction is a
  correction to the record, so it moves into this file and nothing is cut.
- **A pull-request body carries `## Figures`** (#676). The detector resolves a
  file name to an artefact; the looser one, any number near a file name, was
  refused for reading a date and a line count as caps. The body is one live
  object: every head's contract job reads the current body, so a red at a
  superseded head is the instrument, not the commit.
- **A coverage ratio over an open set of mutation carriers is not a figure**;
  the denominator is unbounded, so state the class. A figure about the
  document it lives in is derived beside it, at the head.
- **A generalised vacuous-acceptance-arm detector is refused on cost** (#201
  comment 5720829142): three classes (a harness decoupled from the mutated
  code, an under-specified environment precondition, a false prose claim no
  mutation proof addresses) needing different logic per class, against a defect
  costing about one review round. The refusal owes its qualifier: the catch
  rate rests on an attentive seat. The instance found after it, #1126: a check
  carried a retyped copy of `VERDICT_RE` that diverged from
  `web-fix-wave.js`'s and its null control passed on either regex; the fix
  executes the source's own literal. Do not re-propose without new information.
- **Wave 1067's three deferrals stand** (plan
  `dev/archive/plans/plan-1067-rotenso-inputs.md`): the new option keys stay
  options-page slots out of `topology._SLOTS`; no zone-2 supply slot, since the
  two-zone model carries one flow temperature and no per-zone emitter law; the
  flow-lift bias stays one-sided so the scalar and batch COP paths agree.
  **W1067-POST1** (offer the pre-fill when a heat-pump device is added) gets
  its own issue when started, none before.
- **dp 107 is read two ways and stays unresolved without a reading from the
  owner's install**: make-all/tuya-local (`4551357`,
  `devices/fisher_water_heatpump.yaml`) reads it as the tank's current
  temperature, tvofi/tuya_heat_pump (`fda9bed`, `models/000004k4z6.py`) as the
  wired controller, tank on dp 26; both readings are pinned in
  `tests/features.py`. A DP-keyed localtuya table is refused for the same
  reason, a DP number is not identity, unless a firmware signature proves the
  device.
- **R10-FLY-CLOUD-FRUGAL-OFF is refused.** The owner dropped it and a roster
  line naming it is disposed, never raised again.
- **R10-RCA-CARD-HEALTH-TEXT is refused** (tvofi, 2026-11-13 ~19:15Z, verbatim:
  "drop the card-health root-cause, no longer relevant"); its handoff-body ref is
  left for the closeout prune.
- **A mold floor outranks away** (tvofi, 2026-11-01): the precedence stays and
  the away status and the savings view say when the floor limits away savings;
  the failing-test shape is in `dev/audit/README.md`'s round-11 carries.

## Corrections to the record

- **This file is not policy and no budget reads its text.** It sits outside
  `POLICY_GLOBS` (owner, 2026-09-16, #201 comment 5702401684), so a record pull
  request touching only it owes no `## Approval` and no code-owner review.
  `policy_budgets.json` names it in `roles.record.opens`, which charges the
  rules that path loads, not the file. The residual is a reviewer's: prose
  moved here leaves the corpus.
- **The "34-key `data` payload" is wrong**, as is any count of it; the freeze
  is enforced by `tests/features.py`'s symmetry check and the `coord_*` goldens.
- **The `hpo-ledger` bypass on `main-protect` is gone**: a read of that ruleset
  on 2026-10-21 returns no bypass actor; 0011 still records the decision as the
  owner's.
- **Leave both claim files exactly as you found them** (#662). "Always
  byte-identical" was refused (#600 rightly carries claim lines), then "empty
  on a branch that claims nothing": a squash applies that deletion to `main`
  and carries another lane's claims off, measured four times.
- **A file reported missing was there**: the seat listed a checkout on a stale
  branch. Check existence with `git show origin/main:<path>`.
- **The subject enumerator missed merges and invented them, and the errors hid
  each other.** Compare sets, never totals; the API enumerator is the default.
- **An empty diff over `tests/` and `custom_components/` does not mean no gate
  is owed** (#1122): derive scope from `closure.py select`, never from
  top-level directories.
- **Wave 1067's merged bodies carry figures their reviewers could not
  re-derive**; the bodies stay, this is the correction. #1150's "22 other
  configs" is 21, and its empty-signature predicate returns `True` on
  `all(())`, unreachable today and a trap for a future table. #1152's "253.3 µs
  per drive" measured 72.4 µs on the reviewer's driver; the verdict holds at
  both. #1153's "256 production lines" is 281 under the body's own rule, and
  its "0 `mypy --strict` errors" is unavailable, not true or false; CI's
  `typing` check is the answer.

## Traps that cost a session

A trap that has acquired a mechanical detector is a one-line pointer to it:
promotion, not cutting. The detector must fire when the trap would bite, in that trap's mode, and each
graduation owes a mutation proof in its own pull request.

Round 10's closing days added the traps below. None has an instrument yet
unless it says so; where its fix is routed is stated, and **"unrouted" means no
roster group, carry or proposal id holds it** (checked by searching the roster's
groups and carries for the trap's distinguishing words) and the next
orchestrator files it.

- **`closeout.py --apply` with its default `--orch-root` deletes the
  orchestrator's whole state directory** (found 2026-11-14, before the apply).
  `step_local` (lines 318 to 325, defaults in `main()` lines 776 to 792) runs
  `shutil.rmtree` on every entry of `--orch-root` whose name does not start
  with a `--keep-orch` prefix; the defaults are `~/hpo-orch` and `ledger,state`,
  and the round's state directory (`HPO_STATE_DIR`, 22 GB and 802 entries, holding
  the sweep log, the roster queue, the merge-train state, every seat directory
  and the closure runbook) starts with neither. Passing `--orch-root
  $HPO_STATE_DIR` is equally destructive. The workaround is a path that does not
  exist (`--orch-root ~/hpo-orch/NO-SCRATCH-CLEAR-r10`), which
  `step_local` skips because it checks `c.orch.is_dir()`. **The scratch under
  `~/hpo-orch` was not cleared; the owner decides** (clearing it is irreversible
  and outside the closure runbook's own prune). Next round's closeout re-meets
  this: fix the default (proposal owed, above) before running it.
- **A merged body that defers a part to "a later pass" holds nothing.** Both
  docs gating pull requests (`#3582`, `#3568`) left the savings-valuation parts to
  a short later pass that no ref, roster carry or dispatch held; the closeout's
  roster refusal on a pending carry was the only thing that surfaced it. Before a
  closure, for every merged body that says "outside this pass", find the ref or
  carry that holds the remainder, or dispatch it.
- **A restart refreshes a silent sensor's timestamp, so staleness is
  under-read** (the soak candidate above, one install): any age-based guard on an
  on-change feed that reads `last_updated` is reset by a Home Assistant restart.
  Read how the product derives the age (`INPUT_MAX_AGE_MINUTES` and its consumer)
  before choosing the fix.
- **A reboot leaves dead seats' worktrees holding pull-request branches**
  (2026-11-14, host rebooted about 09:36Z). Measured at takeover: the live train,
  the merge seat, the dispatch seat and the watch scripts were gone; the beat
  daemon, `beat_extras.sh` and `tick_loop.sh` came back through the session
  start hook. `update_pr.sh` then refused `BUSY` for four pull-request
  branches because the dead dispatch seat's worktrees still had them checked
  out, and `update_pr.sh` frees only a worktree owned by another instrument.
  Detach such a worktree only after reading it: `git -C <worktree> status
  --porcelain` empty, its HEAD on `origin`, and no process whose cwd is in it.
  Unrouted: the repair is for `update_pr.sh` to free a worktree whose owning seat
  has no live process, clean and on origin, and the fix is a proposal under the
  freeze shape. Cost when it happened: one local seat for the minutes it took.
- **The cloud environment id is not stable.** On 2026-11-14 at 10:00Z a remote
  trigger create returned HTTP 400 `environment_not_found` for the environment
  the fires of 08:47Z and 09:07Z had used; the start-target listing (the remote
  trigger tool's `list_start_targets`) showed a new `Default` id and the
  repository's seats environment. Fires moved to the seats environment and the
  dispatch overlay and the seat env lines (state, not tree) were updated; the
  first fix fired there read `cloud-setup` OK in its session log and began work.
  Read the start targets before a fire batch and after any outage; an id held in
  state is a claim, and a fire with no sources dies in about 20 seconds reading
  "succeeded". Unrouted.
- **The gate-deferral defect** (2026-11-14; proposal PC-1113-23; hotfix
  R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH). A body edit or review event at an
  unchanged head made `ci.yml`'s refresh re-run green gates, they failed as
  deferrals (the gate instrument was busy), and `stale_pin()` and `fresh()` in
  `tools/ci/sweep.py` (from commit a5ee73e39f, 2026-11-08) then dispatched a
  full `ci.yml` run for every open pull request whose base predated a change
  to `tools/ci/*.py`, true of every open pull request once #3557 and #3573
  merged. Per-event cost: `gh run view 43563862488 --json createdAt,updatedAt`
  (the figure is under Figures); the train entries #3570 and #3544 each
  refused merges and waited after being GREEN. Root-cause process state (c) with
  (d); it is not caused by #3573's own logic. Local workaround that held until
  the hotfix: pre-post the train's approvals so review cycles run in parallel
  and `--approval-carry` posts nothing at train time, no body edit on a
  green, WAIT or queued pull request, one patch per red body. The hotfix
  (#3584, owner-ordered front of the train) went through option B (structural
  deferral) and then option (b): the first predicate read a real red as a
  deferral whenever another run's job finished after the gate started, so the
  predicate is now derived from what `tools/ci/gate.py`'s `busy()` could have
  read.
`#3584` merged as `1791869fdb` (sweep self-test count at main: `python3 tools/ci/sweep_selftest.py | tail -3`). The earlier shape of the same class, a gate red standing after the awaited run went green (#3377, #3516, #3513, #3530, #3490, #3441 and #3533 among them, on 2026-11-13), is what R10-GATE-DEFER-BARRIER (#3573) was built to close.
  Where a stale deferral red stands against a green code run, re-run the
  deferral run's failed jobs (never delete a run) and read `classify` after.
- **Parallel text groups rewrite the same keys, and a clean merge hides it**
  (2026-11-14). #3564 (config-flow text) and #3580 and #3576 (docs and strings
  residue) each reworded the same eight `data_description` keys in
  `strings.json` and `translations/{en,de,sv}.json` (`name`,
  `space_setpoint_unit`, `pv_production_entity`, `away_dhw_min_temperature`,
  `dhw_free_disinfection_enabled`, `vvc_pump_entity`, `main_fuse_amperes`,
  `open_window_relax_enabled`) plus one hunk of `tests/doc_claims.py`; the
  reviewer of the later one had recorded only adjacent lines. The rule that
  resolved it is semantic and so the fixer's, not a merge tool's: for each key
  **the `git merge-tree` of the two heads is the oracle for keys a pull request
  does not own, and the wording that is true of the code wins, the merged
  train's unless the later one adds a needed fact** (seven keys took the train's
  wording, `space_setpoint_unit` one merged sentence stating also what Control
  writes; no train sentence was found false). **Open for the owner:** he may
  prefer #3564's `dhw_free_disinfection_enabled` wording, which states the 1 C
  tolerance. The stack was hand-merged (#3561, #3562, #3532, #3564 each
  reconciled onto the heads under them and sent a delta review). Routed:
  round 11's documentation-verification parts are **one per document and never
  parallel on one file** for this reason; no instrument lists the keys two open
  pull requests both change.
- **A carries-open group does not read done at merge, and the plan prices it as
  work.** `roster_edit`'s `hold_done` turns `set-stage done` into a byte-identical
  no-op while any carry is unmarked or while the group owns an open issue no
  other live group owns; a no-op is printed as "no change" and the roster stays
  `carries-open`. The plan priced every carries-open group at one fixed large
  cost whatever was left open (proposal PC-1113-05's family; on 2026-11-14 the
  tool's closure date was held by a carries-open group whose carries the ledger
  read as delivered). On 2026-11-13 a reconciliation found a large unmarked tail
  (the `carry` lists of the `carries-open` groups on the roster), and idle
  carries-open groups went unnoticed for the duration under Figures because the tick had no
  line for a merged group with pending carries and no seat. What worked: a
  `marks-after-<pr>` queue per gating pull request, its `MERGESHA` replaced at
  the merge and appended to the roster drain queue, each carry marked
  `implemented <sha>`, `dismissed` or `moved <group>`, then `set-stage done`
  (`--at-sha <full sha>` where the group's `resume.commit` is stale), read back
  with `roster_queue.py show <group>`. A mark's `--match` takes the exact
  carry text. A carry cannot be moved to a `carries-open` group, and a
  design-stage group with no files is a receiver only. Routed: the tick line
  (`IDLE-CARRIES <group> <pending> <hours since last ref>`) is
  R11-PRE-ACK-COMPLETION's, from PC-1113-02.
- **Closeout refuses bare citations of refs it will delete, and the retarget is
  a file rewrite, not a roster op.** `tools/audit/seat/closeout.py` step 1 greps
  `.claude`, `.github`, `dev/governance`, `dev/programme/rosters`, `CLAUDE.md`,
  `AGENTS.md` and `README.md` at main for a bare `handoff/`, `handoff-body/`,
  `fix/`, `design/`, `design-verdict/`, `review/`, `probe/`, `claim/`,
  `dispatch/`, `record/`, `verdict/`, `ci-probe/`, `wip-sync/` or `brief/`
  ref (the count at the dry run is under Figures) and refuses each hit whose ref
  is in the delete plan. Rewriting a citation to `archive/<ref>` satisfies it (the
  lookbehind excludes `/`) and `node tools/policy/brief_lint.mjs` exits 0 whether
  or not the tag exists. `roster_edit.write_roster` refuses the rewrite at the
  triage gate (a rewritten carry that mentions a triage item without a
  `triage:` citation reads as text the write adds), so it was applied to the
  files inside the roster-landing record pull request; two passes reach a fixpoint.
  The doomed set moves with time (a ref younger than six hours is kept, a
  not-done group's design refs are kept), so derive it immediately before
  `--apply` and re-run if a citation was added after. It moved under `#3601`:
  `handoff/r10-arch-docs-delta` (tip committed 2026-11-14 17:29Z) was not
  reported at that record's last dry pass and was cited bare at its merge, so a
  follow-up record retargeted it. A dry pass also keeps a ref whose tip the
  checkout lacks, and `prune_refs.tip_ages` reads 500 tips per
  `git log --no-walk`, which exits 128 and prints nothing when any one of them
  is missing, so one unfetched tip leaves its whole batch kept as young (one
  dry pass of the follow-up record read `keep-young-tip=698` against 207 a pass
  earlier). It moved again after `#3604`: the dry plan at the stamp named four
  bare citations (`handoff/r10-cop-learner-draw-floor`,
  `handoff/r10-hotfix-main-selftest-scope-2`, `handoff/r10-hotfix-reference-basis`
  and `review/3481`), and a third record retargeted them. Fetch every head
  (`git fetch origin '+refs/heads/*:refs/remotes/origin/*'`) immediately
  before each dry pass, and read the `rules:` line's `keep-young-tip` before
  trusting `step in-main: ok`. One line is outside the
  roster and code-owned: a comment in `.claude/hooks/pre-bash.sh` citing a
  `verdict/` ref, reworded to name no ref in its own comment-only pull
  request. The retarget script is session scratch.
  The retarget script is `retarget.py` in the closure runbook directory (inventory above); the pre-bash comment pull request: `git log --first-parent --grep=prebash v7.1.17..v10.0.0`.
- **The plan page's closure date is not the closure date.** It counted the
  post-closure R11-PRE groups, showed running groups as `not started` by stage
  words alone, and priced a serial after-edge as a sum of parallel work
  (PC-1113-05; at the 2026-11-14 ~10:06Z render the tool's closure date was past
  15 November and every gating row it put past that date was one whose marks
  were already queued, no work owed). Read closure from the gating set. The owner's copy was rendered
  from a roster filtered of `R11-` groups until R11-PRE-PLAN-RENDER builds it.
- **A cloud seat's liveness is not in `list_runs`.** `last_event_at` equals
  `created_at` for live sessions, so no rule can key on it, and a dead session
  showed `active/running` for 1 h 45 min; only the last timestamp of the run log
  tells. A cloud command has a bound near two minutes (a long chained `sleep`
  ends exit 137): a cloud brief should say so. Unrouted.
- **Four instrument or lane flakes read as reds on unrelated pull requests in
  two days** (2026-11-13 and 2026-11-14): the `tests/entities.py` diagnostics
  redaction check matching a clock field by chance (fixed by #3579), the
  `PTRACE_LISTEN` I/O error that fails `governance / instrument-self-tests` after
  a clean child exit (PC-1113-12; frequency over earlier runs not established),
  the bus self-test's concurrent-confirm check (PC-1113-21) and the beat daemon's
  deferred-restart case (PC-1113-21 addendum). `defect-root-cause.md`'s
  recurrence trigger has fired; the answer is a root-cause seat, not a fifth
  workaround. Unrouted; owed to round 11.

Older traps, still live:

- **A killed agent never writes its own `state at stop:` comment**, and a
  subagent does not survive a session restart though its report does
  (`tasks/<agentId>.output`; `ListAgents` goes empty without notice). On
  resume walk the session's branches and open pull requests, post the owed
  notes, and read the report before re-dispatching. **No detached loop survives
  a host reboot** (train, tick loop, state-docs beat, `wt_sync.sh` were all dead
  at one takeover): restart each from the tree and re-read the queue (the 2026-11-14 reboot and
  its worktree consequence are in the closing-days list below).
- **A daemonized instrument with a silent log is not a dead one.** The
  wrapper's `dup2` makes stdout a block-buffered file; an 8-minute healthy FULL
  train was read as dead and killed. The entry now line-buffers and announces
  itself first; rehearse a launch fix under the incident's exact wrapper.
- **A stand-down note and a committed roster can disagree; origin is the
  tiebreak**, the pull request's own comments. A roster's `resume.stage` and
  `resume.branch` are a seat's claim: read the ref (`standing-dispatch.md`).
- **A gate cannot be its own witness.** When the subject is the selection
  machinery, the selection that runs is chosen by what is under test (#356).
  A check whose failure is visible and one whose failure is blocking look
  identical in a passing run.
- **A figure from another artefact is not measured until you run the thing
  that produced it**, and a figure in prose whose referent is a function of
  `origin/main` is stale by construction: it was the largest source of blocked
  rounds under the 2026-09-09 grant. Derive it (scrape `Fix review: blocked
  <sha> <class>:`); `COUNT_RULES` in `tools/policy/counts.mjs` refuses
  prose disagreeing with the artefact, `brief_lint.mjs` runs it over briefs.
  A bare figure is not refused by a rule (a rule was built and reported three
  wrong per right one): write `58.6 % at 4b6e0765`. The same rule: a body's
  count of its own diff comes from the diff, by mutating the artefact and
  reading the detector.
- **A fix is verified against the instance demonstrated, not the property
  stated.** The verification is built from the instance's form and a sibling
  carrying the property in another form survives, including one the same
  commit creates. `tools/pr/preflight.sh` catches none of the instances
  measured (root-cause analysis over #531, #569, #591). A production fix is
  accepted by standing property-quantified instruments; a record or policy
  artifact has none, so a reviewer of one measures the property.
- **A repair that makes a window, set or diff empty by construction passes for
  the wrong reason.** Force the precondition back to false and check the arm
  reddens (#1115: the window `mainRef()..mainRef()`; reverting to `HEAD` inside
  a shallow clone had to reproduce the original red).
- **A branch can be stale against main invisibly in its own diff**: a move
  reverting a fix that landed inside the moved lines, or a stale claim or
  budget table; and a citation and its referent can live on two branches with
  nothing shared (`configuration_url`: a brief cited it, another branch deleted
  its only occurrence, `main` went red). Only a three-dot comparison against
  current `main` catches the first; `CLAUDE.md` rule 1's forced `full` push run
  caught the second. **Prose is not a pin**: restoring the sentence would have
  greened the gate and reproduced the defect, so re-anchor.
- **A clean merge is evidence of no textual overlap and nothing else.** Two
  sides appending at one insertion point shared a trailing bracket, and
  `--ours` would have dropped a block silently; a sibling merge silently
  reverts its sibling (#2120 was cut before #2119 merged, and its side of a
  shared region was empty). Verify by parsing the result, sweeping every shared
  file for main's lost lines (0 lost, named budget cells excepted) and, for
  add/add conflicts in `tests/features.py`, proving the union keeps every `R.check` name of
  main.
- **A main-only ratchet red hides behind per-PR grading, and two such reds
  deadlock each other.** A red that exists only on `main` reddens every open
  pull request's required verdict while its own checks stay green, and no pull
  request fixes it alone: round 9's closure lane-balance pin and
  `archscore.coord_footprint` row each needed the other's re-record in their
  merge commit. The resolution was cherry-picking one re-record verbatim onto
  the other and closing the first as superseded (`dev/audit/rca/R9-RCA-TRAIN-WEDGE.md`).
- **Rate-limit 403s arrive disguised as red lanes and missing runs.** At
  saturation the repository's `GITHUB_TOKEN` bucket (`dev/audit/rca/install-ratelimit.md`;
  Governance's `record` log prints `RATE_LIMIT before:`/`after:`) turns
  arch-score, env-matrix and validate-hacs into reds that are not verdicts and
  drops workflow events, leaving required contexts without a run. The fix is a
  **recarry**, a new merge commit at the live head that re-fires the events
  with the verdict carried (`--approval-carry`), not a rerun of the failed
  lane. The automated recovery is session-only and does not fire while turns
  are active. **The recarry treadmill prices every queue move**: each move of
  `main` re-prices every queued entry; merge fast after lanes conclude, up-front
  recarries, machinery-touching heads held to a final pass that runs the fixed
  code.
- **`merge_pr.sh` stops on `UNSTABLE` when only an optional context is red**
  (#2465); `nightly-status` reports the last scheduled run, not the pull
  request. Read the required set from the ruleset and merge at the exact head.
- **"The pull request is open" is not a handoff.** The freeze starts at
  handoff and only the orchestrator moves the head; a head moved under a live
  review costs it (`orchestrator.md` section 7). A record pull request cannot
  converge while the merge queue runs (#531 stayed open 20 hours over 31
  merges), so one record per merge, and live state on #3394.
- **`prepr.sh` gates `## Head` against the LOCAL head and `pr-contract` gates
  the REMOTE tip**, so a pull request that writes its own record file pushes
  twice and one `pr-contract` run necessarily fails on the commit being
  replaced (#1116, #1121). A red-then-green at a superseded head, answered in
  the body by naming that head. **A named recurrence at two; at a third
  `defect-root-cause.md`'s recurrence trigger fires and the answer is a
  root-cause seat.** No countermeasure at two is the decision: a check
  suppressing it would stop reporting a body genuinely stale at the head.
- **`body_push.sh`'s predictor does not run the layout guard.**
  `tools/pr/ci_predict.py` passed a head that `prepr.sh` then refused on
  `new-reference` (a retired path cited in prose). Before `body_push.sh` run
  `python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)`;
  rc=0 and `0 refusal(s)` is the pass.
- **`policy_lint.mjs --budgets` exits 0 whatever it prints**; the bare
  `node tools/policy/policy_lint.mjs` refuses. A mutation proof driven against
  `--budgets` proves nothing (#1123).
- **A verdict that does not parse loses its routing class.** `web-fix-wave.js`'s
  `VERDICT_RE` anchors on `^Fix review:`, reads the first line only and takes
  `<class>` from the closed `VERDICT_CLASSES`: backticks around the line or an
  invented class (`revise` is not one) make the dispatcher record an
  undifferentiated non-merge. Post the first line bare; read the class list from
  the file.
- **A coverage check can run a guard's line and pin nothing.** Shapes found by
  mutation: an earlier guard rejected the input, the exception escapes and ends
  the script, an eager f-string detail aborts, the value the mutation leaves
  untouched equals the asserted one, and a mutant that cannot parse reports a
  pass. Assert the mutation's occurrence count before applying it (a control
  reported NOT CAUGHT because the replacement hit a comment), use only-arm
  inputs, and never assert equality against a production structure.
  **A mutator restores only on a clean exit**: a harness killed by a timeout
  leaves production mutated, so check `git status --porcelain` when you stop
  one (`R10-FLY-MUTANT-RESTORE` owes the shared helper).
- **A sectioned config-flow field resolves its label only at
  `step.<id>.sections.<s>.data.<field>` and `data_description`**, with no
  fallback to step level; every check had read the step-level map and confirmed
  the defect (#1111 restored the labels). The class is a check and the
  production code agreeing about the wrong location.
- **A worktree shares the repository's config and refs with every other
  worktree.** `git remote remove origin` inside one repointed the main
  checkout. A throwaway git experiment goes in a standalone clone under
  `mktemp -d`. `worktree_gc.sh <owner/repo>` (`--dry-run` previews) collects a detached, clean worktree
  over an hour old that is not an open pull request's head: claim a root-cause
  or audit seat's with `git worktree lock`, not an untracked marker at the root
  (`closure.py select` turns `MODE: SCOPED` into `MODE: FULL` naming it). The
  main checkout stays clean; `handoff_push` runs `prepr`.
- **A leftover sweep reads part of a row.** In a table row every cell, in a
  bullet the leading verdict, both dropping quoted and backticked text first
  (#690, #678). A blank line ends a markdown table; ground truth for a render
  question is GitHub's `/markdown` endpoint.
- **zsh**: assigning to a variable named `path` destroys `PATH`; `${PIPESTATUS}`
  is empty (use `pipestatus`); `date -jf '%Y-%m-%dT%H:%M:%SZ'` parses UTC as
  local, so compute ages with `datetime.fromisoformat` and an explicit UTC now;
  backticks inside a double-quoted string are command substitution (write a
  comment body to a file with a quoted heredoc and pass `--body-file`).
- **A replacement that matches a prefix leaves both halves in one line, and an
  anchor that matches the first occurrence lands an insertion in the wrong
  section.** Assert the whole construct to be replaced and anchor on a string
  you have counted.
- **A comment bumps a pull request's `updated_at`**; the body-edit clock is the
  `Governance` run list, which fires on `[edited]`.
- **A record's own fields are checked by almost nothing** (#687): a dead path
  in a roster `resume.note` is invisible to `brief_lint.mjs` while the same path
  in `brief` is an error.
- **Re-pointing a branch chain by position after a rebase drops a commit.** Map
  by commit subject and verify the tip's pin count: by index once shifted eight
  branches by one, and only that count noticed.
- **Six of this project's own instruments reported rather than measured**
  (#341, #347, #354, #350, #357, #510), each found by someone chasing something
  else: the pattern is the finding, not the individual bugs.

Graduated, one line each:

- **One CI runner is not the fleet** (#387): `tools/policy/policy_lint_envmatrix.mjs`.
- **The machinery a handover depends on is code nobody ran** (`.claude/` is
  `INERT`): `tools/policy/check-wave-script.mjs` and `policy_lint --hooks`.
- **A shallow checkout fails a driver on the clone, not the tree** (#901):
  `tests/entities.py` refuses a history-reading driver at depth 1.
- **A shallow clone turns "commits ahead" into fiction**:
  `.claude/hooks/session-start.sh`.
- **A one-sided cap and a growing document collide across branches** (#608,
  #607): `policy-docs`'s `[budgets]`.
- **A citation repointed to a commit that resolves but lacks the file is worse
  than a dead one**: `policy_lint`'s `citations` for the corpus and rosters;
  elsewhere `git cat-file -e <sha>:<path>`, not per directory.
- **A blank line ends a markdown table**: `policy_lint --record`'s `table` check
  over both disposition documents.
- **A sectioned config-flow field's label**: the schema-derived, no-fallback
  assertion in `tests/entities.py`, which walks the built schema.
- **A new option key derives into `config_flow._ABSENT_FALLBACKS`**, or every
  options-page visit writes it (#1107): `tests/config_flow_steps.py`'s
  "_ABSENT_FALLBACKS is exactly the proven set".

## Owed

**Owed to round 11, with the owner's ruling behind each:**

- **The release rule's policy and mechanism** (tvofi, 2026-11-13 ~16:35Z; see
  the release-notes paragraph above): a pull-request-body heading the stamp lifts
  into the notes and a `stamp.py` refusal, plus the root-cause document
  `dev/audit/rca/R10-RCA-SETPOINT-LATCH-DEADLOCK.md`, which is only on the ref
  `handoff-wip/r10-rca-setpoint-latch-deadlock` at `2e20aa5d4e` (its harness
  `r10_rca_setpoint_latch.py` ships with the set-point hotfix pull requests).
  The RCA's countermeasure sections (a `fix-review.md` step and a `fixer.md`
  step-3 sentence) and the owner's rule overriding its refusal (iv) have **no roster
  group, carry or pull request** that carries them. `fix-review.md`'s
  `files_tokens` budget has no headroom (a raise was pending on #3514 when
  written), so pay by cutting or sequence after that pull request. Until it
  exists the stamping seat asks of each merged pull request whether upgrading
  needs a user action. The v7.1.12 GitHub Release body equals its `RELEASE_NOTES.md` section (diffed at write time).
- **Two sentences of `dev/audit/README.md` are stale against later rulings** and
  are R10-PLAYBOOK-ROUND-START's to amend (R10-ROUND-PLAYBOOK-FINAL is done): the soak step (the 2026-11-12 and 2026-11-13
  rulings above) and the first item of "Round 11's opening plan carries" (the
  organization transfer, ruled out 2026-11-14). The README is not a policy file;
  no owner review is owed for it.
- **Out-of-tree artefacts that must land in the tree or be named by ref**
  (decision 0013: a reusable instrument is never only in scratch): the scratch
  instruments of the prototype inventory above, the proposals list (defined
  below until a file in the tree replaces it), the local detached watch-mode
  relay that R11-PRE-RELAY-REBUILD retires, and the macOS-lane seat's logs for the
  Darwin self-test reds.
- **Policy edits not landed because they are policy**, re-judged against the
  tree at closure (each still true): `fix-review.md` has no step for an
  ABSENT check (a pull request whose workflows never queued shows no red); the
  mutation proof runs twice, fixer and reviewer, landing only in prose where no
  later seat can re-run it; `fixer.md` owes the finding that a probe that builds
  its own input can build the complement of production's (#591's seat);
  `finding-propagation.md` holds a producing pull request until its carry is in
  the tree, so two branches owing a carry to the same contract cannot both comply
  under concurrency (raised on #201; round 10 met it as `CARRY-LANDED` stops of
  cloud fixers that may not write the roster, PC-1113-01). Dropped as resolved:
  `standing-merge.md` no longer names `merge_pr.sh` for budget and policy heads.
- **Post-hoc reviews from 2026-09-07**: #591, #592, #596, #602, #603, #605 and
  #569 merged without an independent verdict at their final head, and #606 with
  none as a red-`main` repair. **#603** is policy whose approved form changed
  twice after approval; **#596** introduced `tests/typing_budgets.json`, the
  baseline every typing tranche ratchets against. No round-10 record in the tree
  reviews them (`grep -rln 'typing_budgets' dev/audit/rounds/round10` prints
  nothing), so they stay owed.
- **An instrument over the plan's open-issue dispositions, or a decision not to
  build one.** `recordRegion` reads the plan's `## Delivery status`, the
  delivery rows and this file; `## Open friction issues — dispositions` is read
  by no check. A detector must not disposition an issue by mere mention, the
  shape #658 narrowed the region to escape.
- **A stale-pin sweep** (cited from `.github/workflows/codeql.yml`): #960
  SHA-pinned every mutable `uses:`; no lane reads a workflow ref for staleness.
- **`tools/policy/policy_lint_envmatrix.mjs`'s `okRef` row still drives
  `--record --since HEAD`**, assuming `HEAD..origin/main` is empty in its clone,
  the defect #1115 fixed for `--record`'s acceptance arm.
- **`tests/typing_ruler.py`'s docstring still says the pinned toolchain is one
  "which no gate lane has"** (grep that phrase); #1122 established it false:
  `HPO_TYPING_PYTHON` re-execs the pinned mypy half through `run.sh`.

## Proposals filed, not built

Under the freeze shape each is a numbered proposal with the local handling used
in round 10, consolidated and triaged once at round 11's end against the 20 %
bar (`dev/governance/rules/ratchet-budgets.md`); an item marked built or owned
needs no triage. The list lived in session state and is defined here until a
file in the tree replaces it.

| id | defect | local handling in round 10 |
|---|---|---|
| PC-1113-01 | a cloud fixer that may not write the roster stops on `CARRY-LANDED` | a seat folds the carries and re-pushes the body; **owned by R11-PRE-HANDOFF-BOOKKEEPING** |
| PC-1113-02 | no tick line for a merged group with pending carries and no seat | dispatch seat enumerates by hand; **owned by R11-PRE-ACK-COMPLETION** |
| PC-1113-03 | one slow `update_pr.sh` holds every other handoff update in the relay | a second detached watch-mode relay; **owned by R11-PRE-RELAY-REBUILD** |
| PC-1113-04 | a handoff accepted with predicted reds (`doc_claims` history phrase, unpinned sites) reached CI after merge verdicts | none |
| PC-1113-05 | plan closure counts post-closure groups, shows running groups as not started, prices a serial edge as a sum | the owner's copy rendered from a filtered roster; partly R11-PRE-PLAN-RENDER |
| PC-1113-06 | run the per-group pipeline and the sweep fan-outs as deterministic workflow scripts, not orchestrator turns plus standing seats (the owner asked 2026-11-13 whether workflows would make a round more effective) | no prototype; evidence is the orchestrator's token and compaction counts, out of tree |
| PC-1113-07 | `cloud_dispatch.py --group --part` refuses with and without `--topic`, so a part of a group with over five carries cannot render | a flag-path render with a This-part line (local script) |
| PC-1113-08 | the fixer size rule weighs every carry alike | **allowed locally by the owner**; R10-DOCS-STRINGS-RESIDUE part 2 carried carries 5 to 13 |
| PC-1113-09 | `cloud_dispatch.py` refuses designer roles for a size-M group even when a fixer raised a design departure | the brief handed over by hand |
| PC-1113-10, -19 | a recarry or the `merge-main` bot commit moves the head and leaves the body's figure block and `## Head` naming the old head, so `pr-contract` reds | `update_pr.sh` body-only refresh after the recarry; the real gap is that nothing refuses a train or relay launched from a checkout far behind main |
| PC-1113-11 | the train fails 8 merges on a draft pull request | `gh pr ready` by the orchestrator after reading verdict and `classify` |
| PC-1113-12 | `governance / instrument-self-tests` reddens on a `PTRACE_LISTEN` I/O error after a clean exit | re-run the job; owner allowed merging over it (2026-11-13 ~23:51Z) |
| PC-1113-13 | the shared REST core bucket empties under a full wave of seats | slow the merge seat's watches; the refusals retry after the reset |
| PC-1113-14 | `cloud_dispatch.py` refuses a review packet whose diff quotes a generic `/home/<word>/` path | the packet published from a copy with the prefix replaced |
| PC-1113-15 | the introduced-red guard holds reviewer dispatch until the self-test job concludes at every new head | wait for the job |
| PC-1113-16 | a second train starts in the default state dir beside a live one (the pidfile is per state dir) | one stop by hand; no wrong merge |
| PC-1113-17 | `body_push.sh` publishes a body it refused for privacy | none |
| PC-1113-18 | a stamp strands every pre-stamp handoff on the claim file in `update_pr.sh`'s order | hand merges by a local seat |
| PC-1113-20 | a red inherited from main must be answered in every open pull request body | one body patch per pull request |
| PC-1113-21 | timing-sensitive self-test cases read as an introduced red on unrelated pull requests | one authorised re-run, a second failure on the same check is real |
| PC-1113-22 | no tracked instrument prints "GREEN at the live head with a posted merge verdict that names or carries to it" | a scratch watch |
| PC-1113-23 | the gate-deferral defect above | **built as #3584** |

## Figures

- Gate-deferral dispatch, per event: 1 h 45 min 30 s (run 43563862488, 2026-11-14;
  `gh run view 43563862488 --json createdAt,updatedAt`).
- Bare citations of doomed refs at the closeout dry plan, `origin/main`
  `a77d71fb75`, 2026-11-14: 285 (283 in the round-10 roster, 1 in the round-9
  roster, 1 in `.claude/hooks/pre-bash.sh`); enumerator: the `cited bare` lines of
  `python3 tools/audit/seat/closeout.py --roster-file <roster> --repo
  tvofi/heatpump_optimizer --report-dir <dir> --verdicts-drained --successor <N>`
  (dry, without `--apply`).
- Idle carries-open groups, longest idle: 61 h against the 2026-11-13 19:08Z
  enumeration (last ref age of each group, `git ls-remote origin 'refs/heads/handoff*/<topic>'`).
- The reboot: about 09:36Z on 2026-11-14, four worktrees detached by hand
  (`wt-3481`, `wt-3562`, `wt-3563`, `wt-3564`).

## The machine this runs on — measure it, do not read it

A seat's box is not the owner's. Measure your own (`nproc`, `command -v gh`,
`python3 -V`); `tests.yml` matrixes both declared interpreters, CI is the
authority for the browser lane, and `git branch --show-current` beats trusting a
path. **A 403 is not always the repository's answer**: "Resource not accessible
by integration" is a token scope; "not permitted through this proxy" is the
environment. Recording the second as the first sends a reader to change what was
never the obstacle.
