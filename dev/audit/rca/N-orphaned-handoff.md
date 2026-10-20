# RCA — N-orphaned-handoff: a level that never ages, and an arm that read its finding as failure

A round-10 root-cause seat (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`) ran beside no fix; this change is the
record and nothing else. Class `N-orphaned-handoff`
(`dev/audit/config/bugclasses.json`). Round 10 measured 12 stranded refs — 11 genuine,
one content-covered — five of them aged 41.9–96.6 h at 2026-10-20T18:00Z. The per-round
trigger (three or more instances) is met for the second consecutive round: R9 recorded 7.

## 1. Named cause

An obligation was recorded as a **level over append-only history**. `cloud_relay.sh`
appends `OWED handoff-no-pr <ref> <sha>` on every pass. `orchestrator_tick.py`'s
`relay_owed` reads the whole log and keys each row on `f[2]` — the literal kind token for
this grammar, not the ref — while a `POSTED` row keys on a PR number. No `POSTED` can ever
clear a `handoff-no-pr` row. The board therefore printed **31,303 `-> OWED:` lines over
236 refs** at 18:18Z, of which **179 refs already had a pull request**; a merged and
disposed ref (`r10-trust-relative`, #2435) still printed 144. The live obligation was 12.
The orchestrator could not read a queue in a level that grows by a pass's worth of history
every pass.

The second cause is an **availability defect**: `orchestrator_tick.py`'s earlier `orphans`
arm treated `bus.sh orphans`' exit 1 — the instrument's contract for "a stranded ref
exists" — as instrument unavailability. For **143 consecutive passes**, 2026-10-18
15:50:52Z to 2026-10-19 06:06:12Z, `tick.log` printed

    -> bus.sh orphans unavailable (exit 1): the subcommand depends on #2112, unmerged -- fold its refs when it lands

and discarded the `ORPHAN` lines it had already read. `d4f47f040` (2026-10-19 01:03Z)
repaired the reading; the fixed arm first ran at 06:06Z. A detector that reports a finding
as "no answer" is worse than one that is absent: it states the level was checked and
empty.

The third cause is the **absence of age and of a closer**. `orchestrator.md` §5b states
the duty and the orchestrator did read and queue — see §3. Nothing made an obligation old,
and nothing recorded an opening attempt, so a queued obligation neither escalated nor
closed.

## 2. What was re-measured, with the commands

Measured by this seat at origin/main `4a8c89d` (the tick's own provenance at 18:18Z; the
checkout `origin/main` moved to `efc0e6733` while the record was written).

`bash tools/audit/seat/bus.sh orphans --min-age-h 0`:

    ORPHAN r10-earlycutoff-coverage  ecaf178cbd4e 96.6h uncovered=1 repair=opener
    ORPHAN r10-i5-docs              7a7102eb844c 44.3h uncovered=7 repair=opener
    ORPHAN r10-merge-pr-mandate     6219325ca209 48.9h uncovered=3 repair=opener
    ORPHAN r10-rca-harness-friction d1611efe6b7d 41.9h uncovered=9 repair=opener
    ORPHAN r10-roster-ops           9969e3ca80bd 47.5h uncovered=1 repair=opener
    orphans: 12 stranded, 1 superseded; skipped no-body=26 named=1 ancestor=91 young=0

`gh pr list --state all --head fix/<topic>` and `--head fix/<topic>-pr` returned `[]` for
all five. `git ls-remote --heads origin refs/heads/handoff/<topic>
refs/heads/handoff-body/<topic>` returned both refs for each.

**Correction 1: earlycutoff is not owed.** Its one uncovered commit adds 52 lines to
`tests/features.py`. `git cherry origin/main <ref>` prints `-` for that commit
(equivalent), and `git grep -c` finds all three of the block's distinctive strings on
`origin/main:tests/features.py`. `gh pr view 2397` shows PR #2397 (`fix/r10-test-orphans`,
merged 2026-10-18T13:53:10Z) carrying `tests/features.py`. The work landed by another
pull request. `content_superseded`'s M arm demands a byte-identical file and so cannot see
a hunk re-applied into a file main has since changed; the ref reads stranded forever.
Genuine instances this round: **11 of 12**, four aged.

**Correction 2: the detector was not never-blind.**
`grep -c 'bus.sh orphans unavailable (exit 1)' tick.log` → 143. The first and last are
bounded by `grep -n '^##### PASS'`: the first pass in the log is 2026-10-18T15:50:52Z and
the last unavailable line sits before the pass at 2026-10-19T06:06:12Z. The first
`OWED handoff: r10-earlycutoff-coverage` line is at the 06:06Z pass. The gap is 14.25 h,
during which the arm answered "unavailable" every pass instead of naming any ref.

**Correction 3: the board.** `wc -c -l` on the tick's output file →
**4,073,591 bytes, 31,413 lines**; `grep -c '^-> OWED:'` → **31,303**;
`grep -o 'handoff-no-pr refs/heads/[^ ]*' | sort -u | wc -l` → **236**;
`grep -c '^BOARD'` → 1; last line `DISPATCH LIST: 31343 finding(s)`. The machinery
design §S1 measured the same defect at 12:20Z as 3,901,380 B, 30,079 lines, 30,014
findings, 29,976 OWED lines over 229 subjects — it grew by 1,327 OWED lines in six hours.
`grep -c 'handoff-no-pr refs/heads/handoff/r10-earlycutoff-coverage'
$HPO_STATE_DIR/cloud-relay.log` → 200 in the 24 h the log retains (it starts
2026-10-19T18:11:37Z); the current tick loop ran **198 passes in 24 h** (8.25/h).

**The roster contradicts the refs.** In `dev/programme/rosters/wave-r10-groups.json`:
`R10-I5-DOCS` and `R10-RCA-FRICTION` read `not-started`, so PLAN prints "UNBLOCKED, not
started -- start a fixer on handoff/<topic>" — the fresh-implementer dispatch §5b forbids
for a lane that already handed off. `R10-ROSTER-OPS` reads `in-progress / next_step
open_pr`; `R10-MERGE-PR-MANDATE` reads `in-progress / next_step recarry`. The record and
the instrument disagree for four of four.

## 3. Process state: (c), followed, with the wrong result

Quoted process, `dev/governance/roles/orchestrator.md` §5b:

> A `handoff-body/<topic>` ref with a `handoff/<topic>` ref and no pull request at either
> `fix/` name is a lane that **handed off and was never opened**: dispatch an opener
> (`tools/audit/seat/open_pr.sh`), never a fresh implementer.

The process ran. The orchestrator read the OWED lines and acted on them as a queue behind
the open-PR cap and the wave order; `SEATS.md` records it:

- 2026-10-18 20:02Z: "R10-RCA-FRICTION handoff CODE 4cfac180 BODY 91382d21 ...
  PARKED under soft cap (13 open > 6); opens in CP order at <=4."
- 2026-10-19 01:52Z: "Owed openers rca-harness-friction/nightly-pyspy/roster-ops held:
  prepr 4/4 + open PRs 5; wave-2 after drain."
- 2026-10-20 07:10Z: "Owed openers remain (no PR carries them): r10-roster-ops 9969e3ca,
  r10-merge-pr-mandate 6219325c, r10-follower-debounce f210e78b,
  r10-rca-harness-friction d1611efe, r10-i5-docs 7a7102eb, r10-earlycutoff-coverage
  ecaf178c. Open-PR cap 6; 5 open now."

The result did not follow. The cap explains part of the delay but not the whole: counted
open PRs under `pr_cap.py`'s rule were 2 when earlycutoff was pushed on 2026-10-16
17:33Z, 14–17 at the four later pushes on 2026-10-18/19, and 0–5 through 2026-10-20, so
on the final day there was headroom and still no opening. On 2026-10-20 the orchestrator
did dispatch openers: `$HPO_STATE_DIR/pr/r10-i5-docs/p1.log` and
`.../r10-earlycutoff-coverage/p1.log` record a prepr run at 11:33Z whose last line is
`Terminated: 15` at 11:50Z, after 11 checks passed; no pull request was minted and no
retry is recorded. The attempt is a second failure mode, not a missing instruction.

This is **(c)**: the process was followed and did not produce the intended result. It is
not (a) — the detector, the opener and the duty all exist and ran. It is not (b) — the
orchestrator read and queued the lines, citing the cap in its own log, and two openers
were dispatched. A firmer instruction was obeyed and wrong. It is not (d) for the primary
defect — nothing the process relied on changed; the append-only derivation and the
missing closer were true when the process was written. Two observations in the brief are
different states and are not averaged in:

- **A design deliverable with no body ref** (`handoff/orch-machinery` at `09174d94`,
  approved by `review/orch-machinery-design` at `0bd5d12f`) is **(a)** for the obligation
  it needs. No kind maps "an approved design with a review ref and no body ref" to a
  build dispatch; `bus.sh orphans` skips it as `no-body` and the relay's
  `handoff-no-pr` line names it among the 31,303, but nothing closes it by a builder
  being dispatched. The orchestrator has since added group `R10-ORCH-MACHINERY`
  (`next_step`: dispatch at the approved design), gated on `R10-ROSTER-OPS` — the record
  now exists, the kind still does not.
- **A brief that grew after its seat finished** (`R10-ROSTER-OPS`, handed off at
  `9969e3ca` on 2026-10-18T18:37:44Z; brief gained the `state_docs.py beat --apply`
  deliverable at `541868d6f` on 2026-10-20T11:35:54Z, 41 h later) is **(d)**. The
  process — handoff freezes the branch, the roster records the deliverable — was sound,
  and its precondition (the brief the handoff answers) changed underneath it. The
  countermeasure is to notice the change (a brief hash pinned at handoff), not a new
  rule; it extends the machinery design's §6.4 reconciler.

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- `cost(countermeasure, recurring)`: the machinery design §6.8 prices the obligations
  ledger at **~5 s per pass** (~300 lines). At the tick's 300 s nominal cadence that is
  5 s x 12/h = 60 s/h, or **2.4 h over a six-day round**; at the measured achieved
  cadence (198 passes/24 h) it is **1.65 h**. It also replaces the 4,073,591-byte board
  write each pass: 4.07 MB x 8.25/h ≈ 34 MB/h, about 0.81 GB/day.
- `cost(defect)`: **5.13 seat-hours** is measured, not estimated — the R9 RCA
  (`dev/audit/rca/R9-ORPHAN-HANDOFF.md`) records that a fresh opus seat spent 5.13 hours
  re-implementing `r9-ux-10` before finding the orphan. This round adds a 47.5 h median
  delay across four deliverables (41.9, 44.3, 47.5, 48.9), which the 5.13 h does not
  include.
- `P(recurrence)` = **1.0**, measured. `dev/audit/config/bugclasses.json`'s
  `N-orphaned-handoff` carries `per_round: {"R9": 7}`; this round's `bus.sh orphans`
  reports 12 stranded (11 genuine after Correction 1). The class has met its per-round
  trigger in two consecutive rounds.

1.65–2.4 h per round < 5.13 h x 1.0, so the countermeasure passes. `N-orphaned-handoff`
is also an audit class at three or more instances in one round, so a class-eliminating
barrier is owed regardless; the cost test chooses its form, and this one is the form the
design already specifies.

## 5. The countermeasure, as design

This extends the machinery design's §6.3 obligations ledger; it is **not a second
ledger**. `handoff-no-pr` stays one derived kind, computed each pass from the live world
and never accumulated. The extension:

1. **Derive the open set, not the history.** For each `handoff/<topic>` and
   `handoff-body/<topic>` subject, the closer is a pull request at `fix/<topic>` or
   `fix/<topic>-pr`, the tip inside `main` or a live `fix/` head, a disposition at the
   current sha, or `subject-absent`. The 31,303-line history collapses to the live set
   (12 at 18:00Z). This is §6.3's own fix for S1.
2. **Age and escalate.** Each derived obligation carries `age_h` (from the tip's commit
   time, which `bus.sh`'s ORPHAN line already prints), `deadline`, `repair` and `group`.
   At **24 h or more** the board prints `DISPATCH: <group> <ref> opener`, oldest first —
   a queue, not a level. At **48 h or more** it prints an owner flag. **The thresholds
   belong to tvofi**; this document states the proposed values and their state, and the
   document-only change does not set them. A threshold is policy (`orchestrator.md`'s
   duty) and lands only on tvofi's approving review.
3. **Record the attempt.** `open_pr.sh`, the opener, writes `attempting <ref> <sha>
   <utc>` when it starts and a failed step with its reason on a non-zero exit, so the
   11:33Z `Terminated: 15` is visible in the obligation rather than only in a log. A
   killed attempt is then retried by the beat, not rediscovered by the next session.
4. **Content-covered close.** `content_superseded` gains the arm the earlycutoff case
   needs: a ref whose uncovered commits' added lines are all present on `main` closes as
   `subject-covered`. The byte-identical test stays for the whole-file case; the added
   arm is what lets a re-applied hunk close. This is the exit for the false obligation
   that would otherwise age forever and teach the reader to ignore the line.
5. **Design to build is a new kind, and a different state.** `design-build` (state (a)):
   an approved `DESIGN.md` at a `handoff/` ref with an approving `review/` ref and no
   builder dispatched. Its closer is a builder dispatched at a roster group; its subject
   is the design, not a PR. §6.3's kind table has no such kind and the relay's five OWED
   shapes do not include it. This is the `handoff/orch-machinery` case.
6. **Availability contract — what the ledger must not inherit.** A **missing** store is
   first run. An **unreadable** store is `UNREADABLE` and the pass fails; it is never a
   clean board. A read that answers "obligations exist" is neither: `bus.sh orphans`' rc
   1 with a summary line and ORPHAN rows is a finding, and rc 0 with a summary and zero
   rows is empty. The 143-pass window in §1 is the shape the ledger must refuse: a
   finding must never be parsed as an instrument failure, and an unreadable subject must
   never be parsed as a clean zero. The design's B11 arm states the store half; this
   record adds the exit-code half as a distinct requirement.

**Demonstration.** The prototype is `~/hpo-seats/r10s3/rca-handoff-slip/fold_demo.py`
(scratch; not carried in this change), run read-only against the fetched ref namespace,
the PR head list and the disposition ledger:

    python3 -I fold_demo.py --world live

- **RED**: 22 live subjects; escalates the four genuine aged refs (3 `DISPATCH`:
  r10-roster-ops 47.8 h, r10-i5-docs 44.6 h, r10-rca-harness-friction 42.1 h; 1 owner
  flag: r10-merge-pr-mandate 49.1 h) and closes r10-earlycutoff-coverage as
  content-covered. 15 escalations.
- **Null control**: silent on `r10-trust-relative` (merged #2435 and disposed),
  `r10-tick-drivers` (merged) and `audit-r10-roster` (0.4 h); a ref that resolved does
  not fire.
- **GREEN**: with a fixture giving the five a `fix/<topic>` head — the opening the fix
  produces — the four close and escalations fall 15 to 11. The prototype's 22 is an
  upper bound: it does not yet apply §6.3's name exemptions or `subject-absent`; the
  bus's own stranded count is 12.

The two aged refs above the bus's stranded set (`audit-r9-plan`, `audit-r10-find-B*`,
`audit-r10-arch*`) are why an exemption list and `subject-absent` are part of the
countermeasure, not an addition to it.

## 6. What I could not establish

- **Who sent SIGTERM to the 11:33Z openers.** `p1.log` ends `Terminated: 15` after 11
  passing prepr checks; the prepr slot's expiry (12:03Z) is later, the orchestrator's
  `SEATS.md` was writing through 11:57Z, and no log names the sender. The retry writer in
  §5.3 makes the failure visible; it does not need this answer to do so.
- **Whether all 22 subjects the fold prints are genuine.** The prototype lacks §6.3's
  name exemptions (`handoff/audit-r*-plan`, `handoff/audit-r*-roster`, `wip-sync/*`) and
  `subject-absent`. The bus's stranded count (12, one content-covered) is the conservative
  figure this record uses; the fold's 22 is an upper bound.
- **The exact split of the delay between the cap, the wave order, the 14.25 h detector
  gap and the killed attempts.** Each is measured; a single attribution would need the
  orchestrator's own turn history at 5-minute resolution, which is not on the box.

## 7. Where the finding goes

- The class's `rca` citation in `dev/audit/config/bugclasses.json` still points only at
  `R9-ORPHAN-HANDOFF`; adding `N-orphaned-handoff` to it is a config change and is not in
  this document-only handoff.
- The machinery design (`dev/audit/design/orch-machinery/DESIGN.md` at `09174d94`, §6.3
  and §6.4) is the destination for §5.1–§5.3 and §5.6; §5.5 is a new kind the design
  must add, and §5.4 is a `bus.sh` content-arm defect it must fix. Group
  `R10-ORCH-MACHINERY` exists in the roster with a `not-started` build gated on
  `R10-ROSTER-OPS`.
- §3's (d) observation belongs to the §6.4 record verifier: pin the brief at handoff and
  compare it on a later pass.
- The 24 h and 48 h thresholds are tvofi's; this record names the state they address and
  does not set them.
