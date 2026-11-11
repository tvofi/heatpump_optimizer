# Proposal triage, session s7, batch 35 (P199-)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch34.md`
(P195-P198). This batch holds the five entries appended after batch 34
(V119-V123) and merges only through the train queue (tvofi, 2026-10-25). Facts
read at origin/main `6fe5170cd`, with the roster read at
`origin/handoff/audit-r10-roster` (208 groups; main's in-tree roster has 199,
and the two agree on every group this batch names). Where a figure is a count
over the tree, the command that prints it is beside it.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P199: dead merge trains go unnoticed (V119)
Verdict: ACCEPT narrowed -> a carry of **R10-FLOW-WIP** (stage `not-started`,
size S, files `tools/audit/seat/pr_cap.py`, `orchestrator_tick.py`,
`INSTRUMENTS.md`; `after` R10-FLOW-PULL, done). The **tick arm only**; the
`train.sh` arm is REJECTED.
Source: s6 `proposals.md` `## V119` (orch s7, 2026-10-26T21:25Z).

Instances: three dead train directories in the round's 27, one of them today's
79-minute blind window, and the cause of the blindness measured on the board
the orchestrator reads.
- Command, in the orchestrator's state directory:
  `for d in train/s*/; do grep -qE "TRAIN (DONE|STOPPED)" "$d"/* || echo "$d"; done`
  prints `train/s38` (log mtime 10-25T11:54), `train/s44` (10-26T04:01; it has
  `TRAIN_RC=143` and no end line) and `train/s60` (10-26T18:02). 27
  `train/s<digits>` dirs exist. So 3 of 27.
- s60: launched 17:01:45Z, died after its 17:02Z recarry and was found dead at
  18:21:51Z — 79 minutes, `seat-ledger.md` line 1124. Its queue held verdicted
  #2858, which merged only at 18:30:14Z under s60b: 88 minutes on the critical
  path, `seat-ledger.md` line 1125.
- s59 is **not** an instance: it wrote `TRAIN STOPPED rc=1` at 17:00:39Z
  (`seat-ledger.md` line 1112). The filing's "s59 and s60 ended with no TRAIN
  DONE/STOPPED line" holds for s60 alone.
- The blind window's cause is not the missing detector: the tick already has
  one. It is fed a stale wiring. The tick is invoked with
  `--queue <state>/train/current-queue.json --train-log <state>/train/current.log`
  (`s7/sweep_mech.sh` line 26), and both are symlinks that still resolve to s58
  (`-> queue58.json`, `-> s58/train.log`), last written 16:59Z, while six trains
  (s59, s60, s60b, s61, s61b, s62) ran after them. At 21:53Z the board printed
  `queue empty`, `no train running`, and
  `log tail: ... TRAIN DONE ... end=2026-10-26T16:59:07Z` (`s7/tick.txt` lines
  3-6): a five-hour-old train described as the current one.
- The existing dead-train flag cannot fire on that input. `train()` computes
  `open_` from the **caller's** queue (`orchestrator_tick.py` lines 508-521),
  so a dead train whose own `train/s60/queue.open` holds an OPEN entry raises
  `train not alive` only when the caller passes that dir's queue. Nothing makes
  the caller do so, and one stale symlink silently disables the arm.

The carried arm, in `orchestrator_tick.py`'s `train()`:
- When no `merge_train.py` process is live (`_seat_procs`, line 489), resolve
  the newest `train/s<digits>` directory beside `--train-log`. A directory with
  no `TRAIN DONE|STOPPED` line in its log and no live pid is `DEAD TRAIN
  train/s60` — flagged, naming the directory, its last log line and how many
  entries its queue holds which are still OPEN (the `_open_numbers()` read it
  already makes).
- Separately: a `--train-log`/`--queue` pair that resolves into a directory
  older than the newest train dir is itself a finding (`stale train wiring:
  reading s58, newest is s62`), flagged. That is the shape that hid s60 and has
  been true since 16:59Z.
- Controls: (1) the s60 shape (dir, no end line, no live pid) flags `DEAD
  TRAIN`; (2) null — a dir with `TRAIN DONE` does not; (3) null — a live
  `merge_train.py` pid does not; (4) the s58-vs-s62 shape flags `stale train
  wiring`; (5) one mutant drops the end-line test and must fail (1).
- Roughly 25-35 lines plus 3-4 arms in the tick's existing self-test (the
  `dead train reported` arm at line 2369 is the model).

Rejected: `train.sh` refusing an undetached launch.
- The defect it addresses is real — s60 "launched undetached, died with its
  seat's shell" (`seat-ledger.md` line 1124) — but `train.sh` is foreground by
  design ("the caller detaches and owns the schedule", `train.sh:34-35`), and a
  shell cannot honestly test whether its caller detached. The implementable
  shape is an env claim (`HPO_TRAIN_DETACHED=1`) that a caller can set without
  detaching, or a self-daemonising `train.sh` that changes the foregound
  contract `add` and the tick both rely on. Neither is cheaper than the
  detector, and the detector covers every cause of a dead train (crash, kill,
  dead shell), not only this launch mistake.
- The operational half is already in hand: the sweep re-derives train liveness
  out of tree (`s7/sweep_mech.sh`, since 21:10Z); this carry moves the part
  that belongs to a tracked instrument into it, where the tick's own report
  cannot be bypassed by a caller's stale argument.

Cost:
- One S fixer round and one review round, on a group that is already S and
  `not-started` (no carry is displaced).
- Standing: one `ls`-equivalent directory read per tick when no train is live,
  and no GitHub API call added.

Benefit: 79-88 minutes of a critical-path merge on the one measured instance,
against a detector that reports it at the next tick; and it removes a board
line that was false by five hours at 21:53Z.

Binding: the tick's inputs are the caller's; an arm that grades the newest
train dir is the only shape that does not depend on a hand-kept symlink. The
alternative launch guard cannot be enforced honestly from inside `train.sh`.

For the orchestrator, not a carry: the symlink pair itself is out-of-tree
state. Until this lands, point the tick at the live train's own
`train/s<n>/queue*.json` and `train.log` at each launch, or accept that its
TRAIN section describes the last train it was wired to.

## P200: the reviewer verdict relay format is unstated where reviewers read (V120)
Verdict: ACCEPT narrowed -> a carry of **R10-ORCH-REVIEW-PACKET** (stage
`not-started`, size M, files `tools/audit/seat/bus.sh`,
`tools/audit/seat/review_packet.py`, `dev/governance/roles/fix-review.md`,
`tools/audit/seat/INSTRUMENTS.md`). The four checked items are stated in
`fix-review.md`; a `bus.sh verdict-template` verb is REJECTED.
Source: s6 `proposals.md` `## V120` (orch s7, 2026-10-26T21:25Z).

Instances: four verdicts today, seven defects, one of them four repairs on a
single probe.
- rev-2745 (`08190af7`, verdict at `1a13f2b3`) needed four orchestrator
  repairs before `cloud_relay.sh` accepted the probe: the ref used the full
  nonce instead of its first 8, `blocked:` instead of the `blocked <head>
  <class>:` marker, no `bus-nonce:` line, and no `ev/` file naming the head
  (`seat-ledger.md` line 1131, 19:45Z).
- rev-2849: relay refused — subject `verdict: #2849 ...` on a probe ref
  (`seat-ledger.md` line 1078, 14:22Z).
- rev-2853: verdict at an old head; rev-2858: old free-text subject
  (`seat-ledger.md` line 1166, the `probe-refused` row).
- The two reviewer briefs that spelled the layout out relayed first time:
  `brief-rev-2858.txt` states the first line, the nonce line, `ev/` with a file
  naming the 40-hex head and the ref `probe/rev-2858-7540ca11`; the filing
  records the #2864 and #2865 briefs doing the same.

What is actually checked, read at `cloud_relay.sh` lines 199-224:
- the ref is `refs/heads/probe/rev-<pr>-<nonce first 8>` (line 199);
- the commit subject is exactly `verdict <pr> <head40>` (line 208);
- the first line is `Fix review: merge <head40>` or `Fix review: blocked
  <head40> <class>: <reason>` with `class` matching `[a-z-]+` (lines 219-220);
- a line `bus-nonce: <32 hex>` exists (line 221);
- an `ev/` directory exists (line 223). Of these, `fix-review.md` line 7 states
  only the evidence file naming the head and the nonce line: **four are
  unstated** — the ref name, the subject, the first-line grammar, and the
  `ev/` directory name. That is exactly the four the #2745 probe cost.

Why `fix-review.md` and why not a `bus.sh` verb:
- The reviewer reads the role file; it never runs `bus.sh` (the brief and the
  role both say so). A template verb would be a second statement of
  `cloud_relay.sh`'s checks that can drift from them, and reviewers would still
  not see it.
- The destination group already edits `fix-review.md` for the review packet, so
  the marginal lines ride that round rather than opening one.

Cost, measured:
- `node tools/policy/policy_lint.mjs --budgets` at `6fe5170cd` prints the
  fix-review row as `140 lines, cap 140; 2448 tokens, cap 2451`, against a file
  of 140 lines (`wc -l dev/governance/roles/fix-review.md`). The file has 0
  lines and 3 tokens of headroom: the carry must **pay** by deleting prose in
  the same file, not by appending.
- About 8-10 lines at the file's density, one opus fixer round inside the
  group's dispatch. If that dispatch has already frozen its head (a fixer was
  briefed at 21:51Z), the carry joins its resume notes and lands in the delta
  round; it does not justify a second dispatch.
- Policy: `dev/governance/**` is policy, so the merge needs the owner-approved
  route under the live mandate (6329234399, scope `all`).

Benefit: seven defects on four verdicts in one day, each costing an orchestrator
repair round-trip and leaving a verdict unrelayed while it waits. The two
briefs that spelled the layout cost nothing and relayed first time — the
countermeasure is proven in the same window it is measured in.

Binding: the file's caps (0 lines, 3 tokens). An append without a payment
fails `policy_lint --budgets`, so the carry is accepted only in the paying
shape; if the payment cannot be found, the sentence goes into the reviewer
brief template that `handover_prompt.py` renders instead (same content, no cap
pressure), and the role file keeps a one-line pointer.

## P201: nothing checks every open issue/PR sits on a live roster group (V121)
Verdict: REJECT as filed — it duplicates #2733, which is open and owned by a
live group; one delta (pull requests) is recorded below as prose for that
group.
Source: s6 `proposals.md` `## V121` (orch s7, 2026-10-26T21:25Z).

Instances: measured at `6fe5170cd`, re-read at roster-branch tip `9937317d8`
(2026-10-26T22:20Z).
- Open issues: `gh -R tvofi/heatpump_optimizer issue list --state open --limit
  200` returns 73; 72 besides #201. Join each number against **every** group's
  `issues` and `fixes` on `origin/handoff/audit-r10-roster`, counting a number
  routed when any live group lists it (a number can sit on a done group and a
  live one): **72 of 72 resolve to a live group** — 0 to no group, 0 to only
  done or absorbed groups. 23 of the 72 are also listed by a done or absorbed
  group, which is the close-out question, not a routing gap.
- Open PRs: 6 (`gh -R tvofi/heatpump_optimizer pr list --state open`). A PR
  resolves through the group whose `resume.pr` equals it: five do — #2854
  `R10-HEAT-METER`, #2853 `R10-FLOW-JIDOKA`, #2819 `R10-ARCH-SHAPES`, #2745
  `R10-SAV-COMFORT`, #2678 `R10-DEPENDABOT-SETUPTOOLS`, all live. #2866 is the
  roster record PR and has no group by design.
- The figures this entry was drafted on (4 issues unowned, 11 done-only, #2678
  unowned) were join artifacts, not roster states: they came from matching only
  the first group listing a number and from a roster read before the friction
  groups were appended (they landed at 20:47Z, roster commit `7a9a766b4`). The
  any-live join above replaces them. The correction is the ruling's own point:
  this invariant is only true as a whole-corpus read re-taken, and a one-off
  read of it reports gaps that are not there.

The duplicate: #2733's body already specifies this — "invariant 3 (an open
issue has a live owner) is a tick report line from the cached issue list,
report-only on push" — and `roster-queue.txt` wires #2733 to
R10-ORCH-ROSTER-SCHEMA (the absorbed R10-ROUTING-INVARIANTS carries it). A
second ruling would dispatch a second builder of the same tick line.

Cost of accepting as filed: a third carry on a 22-carry M group and a second
specification of one check, which is the shape that already produced two
disagreeing readers elsewhere in this round.

Binding: duplication. The only content not in #2733 is the pull-request half,
which is a few lines inside the same tick line #2733 builds: read the open PR
list it already fetches for the TRAIN section (`_open_numbers()`) and flag a PR
whose number matches no group's `resume.pr`. At this reading that flags one PR,
#2866, the roster's own record PR, so the group should exclude it by name or
accept one expected line per roster PR. Recorded here for the group's carry
text; it is not a new ruling and needs no cite.

For the orchestrator, not a carry: the 23 issues a done or absorbed group also
lists are the close-out queue, and one is verified closable in this batch
(#2494, below). The four filings an earlier read of this entry called unowned
are on live groups already (`#2835` `R10-FRICTION-GATE-SCOPING`, `#2840`
`R10-FRICTION-MUTATION-SURVIVOR`, `#2855` `R10-RCA-FRICTION-RESIDUE`, `#2860`
`R10-FRICTION-REGRESSION`).

## P202: the train grades any red check-run of a name, not the newest (V122)
Verdict: REJECT. The proposed mechanism inverts rule A5 and cannot admit the
pull request it was written for; the binding constraint is GitHub's own
required-check evaluation, which the train already reads before it merges.
Source: s6 `proposals.md` `## V122` (orch s7, 2026-10-26T21:25Z).

Instances: one, and it is not a grading error.
- s61 stopped at 20:30Z with `#2864 red at its head: gate`, check-run
  `121687736029` (failure 16:06Z, a rate-limit red) beside
  `121690658158` (success 16:11Z) at the same head; noticed at the sweep
  20:40Z; s61b and then s62 merged the same PRs at 20:45Z and 20:56Z
  (`seat-ledger.md` lines 1145 and 1150). Cost: one train relaunch and 10
  minutes of merge-seat time.
- The two runs are **different CI check suites**, not two runs of one suite.
  `merge_train.py`'s `latest_runs()` (lines 346-358) keeps the latest run **per
  suite** for `gate` and takes the worst suite standing, and its comment states
  why: "GitHub's ruleset refuses a merge while ANY suite at the head carries a
  non-success required run" (A5, R10-CI-LAYOUT P2b). The same rule is
  implemented in `proof_watch.py` line 202 and pinned by the platform-gate
  self-test probes at `merge_train.py` lines 4239-4251.

Why the candidate cannot pay:
- Even if the local rule read newest-per-name green, `at_head()` calls
  `cross_check()` whenever `gate` is required (`merge_train.py` lines 1693-1696)
  before approving. `cross_check` reads GitHub's `statusCheckRollup`
  `isRequired` evaluation through `platform_gate()` (lines 387-420) and raises
  "a disagreement is a refusal (A5)" when the platform reads not-green. With a
  superseded red suite still at the head, that is the same stop one step later;
  with the platform reading green, the local rule was already right to stop
  less conservatively — and nothing in this instance shows which.
- The measured fact that decides it is absent: no head exists today carrying an
  older red `gate` suite and a newer green one at which GitHub's own evaluation
  reads green. `gh api repos/.../commits/30c940e5/check-runs` now returns only
  successes, so the instance cannot be replayed.

Binding: A5. The train's per-suite rule is not a guess about GitHub; the merge
path re-reads GitHub's evaluation before every approval, so the local rule can
only be equal to or earlier than the platform's verdict. Changing it to
newest-per-name would either change nothing (the platform refuses) or hide a
real red.

What would change the answer: a head at which `statusCheckRollup`'s required
`gate` contexts are all success while an older completed `gate` failure stands
in an earlier suite, and a merge that GitHub then permits. That head in the
Instances line makes this an ACCEPT to R10-TRAIN-OVERLAP-GRADE (live, `queued`,
owns `merge_train.py`), with the removal criterion that one such head merges
where the train would have stopped. The cheaper diagnostic — the stop's log
line naming the red check-run's suite id and age, three lines in the same
function — is worth having either way and is not a proposal.

## P203: the tick marks mandate-approved owner gates as blocked (V123)
Verdict: ACCEPT narrowed -> a carry of **R10-ORCH-ROSTER-SCHEMA** (stage
`not-started`, size M, files `tools/audit/seat/roster_lib.py`,
`roster_sync.py`, `roster_edit.py`; `after` all done). The classifier goes in
`roster_lib` and the tick calls it; a tick-only string heuristic is REJECTED.
Source: s6 `proposals.md` `## V123` (orch s7, 2026-10-26T20:56:21Z).

Instances: every tick, and the board's own line carries the count.
- The board at 21:53Z prints `34 group(s) blocked on owner disposition; oldest
  issue #2259 is 11d old -- surface them to the owner` (`s7/tick.txt` line
  152).
- The same count, re-derived with the tick's own loader at roster-branch tip
  `9937317d8` (22:20Z): `roster_lib.open_groups` gives 70 open groups, 34 with
  a non-empty `owner_gate` — 32 name a mandate (6175172275, 6319294694 or
  6329234399), 2 begin `code-owned:` (`R10-ARCHSCORE-SPELLINGS`,
  `R10-DEPENDABOT-SETUPTOOLS`) and 3 begin `policy:`; several rows match more
  than one, and **none of the 34 states a decision still to be taken**. So 34
  of 34 are covered gates dressed as blocked ones. The 21:53Z reading of the
  same loader gave 71 open and the same 34 gated; the roster branch moves under
  a count, which is why the class, not the total, is what the fixture pins.
- The instance is not new: `seat-ledger.md` line 1162 records the same reading
  at 32 of 32 for the roster of that moment.
- Cause, read at `orchestrator_tick.py` lines 1808-1827: `gated = [... if
  gid in open_g and g.get("owner_gate")]` — the presence of any string is the
  whole test, `flag=True` is set, and one `gh api repos/.../issues/<n>` read of
  the oldest gated issue's `created_at` is made to print its age.

The carried arm:
- `roster_lib` gains `gate_kind(gate)` over the gate text, returning `covered`
  (names a mandate id, or is a `code-owned:`, `policy:` or `budget:` gate,
  which the mandate in force covers) or `owner` (the text states a decision
  not yet taken, today only `owner decision after the probe`).
- The tick reports covered gates informationally with no flag, and flags only
  `owner` ones; the oldest-issue age read is made only when an `owner` gate
  exists (so on today's roster, zero calls per tick instead of one).
- Controls: a fixture of the 34 gate strings from the roster, all classifying
  `covered`; the `owner decision after the probe` text classifying `owner`;
  one mutant that treats every gate as `owner` fails the 34-row fixture; one
  that treats every gate as `covered` fails the owner row; null — a group with
  no gate is not in the line at all.
- One helper (about 15-25 lines) plus the tick's call site (about 3), and the
  fixture rows. No roster data migration: the classifier reads the existing
  strings, so `roster_edit.py` and `roster_sync.py` are not touched in this arm.

Cost: one S-sized slice of an M group's round; no schema migration; and it
**removes** one GitHub REST call per tick (288/day at the 300 s cadence) from
the installation bucket the rate-limit class is about.

Benefit: 34 flagged-but-false lines on every board the orchestrator reads,
against the tick contract's "report only owed or new items"; and the flagged
line is the one the completion criterion's last step is judged on, so a false
positive there costs a re-derivation every pass.

Binding: one fact decided twice. The gate's meaning belongs to the roster
schema (the tick already imports `roster_lib` for `groups_of`/`open_groups`);
a regex in the tick would be the second reader, and this round has paid for
that shape repeatedly. `R10-FLOW-MQ-PROBE`'s "owner decision after the probe"
is on the roster branch already `done`, so no group today is `owner` — the
fixture must still pin the string, because it is the one kind the arm exists to
keep flagged.

---

# Measure-first issues, re-measured at 6fe5170cd

The dispatch asks for each open issue whose body defers its size or scope to a
measurement. Five carry such a clause; each is answered below with the number,
and none is closed by this seat (no `Closes` is written here — the orchestrator
closes).

## MF1: #2800 R10-FLY-POOL-INSTRUMENT — "Measure first: cloud_dispatch's current pool-line handling at main, if any."
Measured: there is none.
- `grep -n "pool\|POOL" tools/audit/seat/cloud_dispatch.py` prints nothing in
  747 lines; no `tools/audit/seat/pool.py` is tracked (`git ls-tree -r
  --name-only origin/main | grep pool` finds only harness/fixture names).
- Disposition: the measurement the brief defers to is satisfied and the brief's
  premise holds — the group adds a call into a new module and refactors
  nothing. The clause can be replaced with this result in the fold carry
  (`carries/fold-R10-FLY-POOL-INSTRUMENT.md`, which still carries the deferral
  verbatim). No body re-scope beyond that.

## MF2: #2801 R10-FLY-RECORD-BEAT — "measure first whether any check reads the [HANDOVER `updated-for`] field."
Measured: yes, three checks and one report read it.
- `tests/entities.py` lines 16330-16395: `updated-for:` must exist, name an
  ancestor of `HEAD`, and name an ancestor of `origin/main`.
- `tools/audit/seat/orchestrator_tick.py`: `UPDATED_FOR` (line 137) and the
  STATE section's staleness line (1552-1588) report how far behind main it is.
- `.github/workflows/nightly.yml` line 59 names the ancestry read.
- Disposition: the premise behind "NOT in this group … deferred" is false. The
  refresh is owed by whoever moves the handover, and the fold carry
  (`carries/fold-R10-FLY-RECORD-BEAT.md`) should say so instead of deferring
  it. Nothing else in #2801 changes.

## MF3: #2494 R10-MERGE-SUBJECT-HARDEN — "measure … then tighten", both findings
Measured: both findings are already fixed on main, and the group is `done`.
- `git log -S"shell continuation line is refused" -- tools/policy/agreement.mjs`
  gives `09b1d002c` (2026-10-24), "fix(R10-MERGE-SUBJECT-HARDEN): the title
  template is the host's shape, and the writer scan reads the call", 69+/6-,
  and `git merge-base --is-ancestor 09b1d002c origin/main` holds.
- The measurement it reports: on main's first-parent merges the tightened and
  the old rule agree (15 each at that commit). Re-derived at `6fe5170cd`:
  383 first-parent commits past the cutoff, **370 merges, all 370 in the
  host's `Merge pull request #N from owner/branch` shape, 0 squash-shaped,
  0 in neither template**, 13 single-parent commits (stamps, `ci: record
  nightly kills`) that the guard does not judge. So the "title `(#N)` laxity"
  has no instance in this tree's history: the repository merges with `--merge`
  and never produces the squash shape.
- `node tools/policy/agreement.mjs --self-test` at `6fe5170cd`: `SELF-TEST 180
  of 180 probes held`, including `a --subject on a shell continuation line is
  refused, at the call line` and `a --subject in an argv list split over lines
  is refused`.
- Disposition: **#2494 is closable** with the commit and the 180/180. Its group
  `R10-MERGE-SUBJECT-HARDEN` is `done` on both rosters, so this is one of the
  11 done-group issues in P201's count, and the only one verified here. Its
  other carry (the #2671 shared-grammar routing question) is an owner call on a
  different PR and is not part of this issue.

## MF4: #2509 R10-MUTANT-SKIP — "Build it measure-first, in this order: (1) build the 595-row replay …"
Not measurable from this seat: the measurement *is* the deliverable (a 595-row
replay recorded from real runs), and it is the group's own first step with a
removal criterion already written into the brief. The group is `done` on main's
roster with PR #2749 (`commit 6b5d2a8169d6…`) and the issue is still open, so
the orchestrator should read that PR's body for the recorded matrix-or-refusal
and close #2509 on it. No re-scope here.

## MF5: #2501 R10-COP-PARTLOAD — "Measure first on synthetic installs: COP vs compressor power at a fixed lift …"
Not measurable from this seat, and not its to measure: the group is `queued`
and its fixer's first step is exactly that measurement (the fixer brief for it
was written in this session's window). No re-scope.

---

For the orchestrator, in dispatch order:
1. **R10-FLY-WIP**: apply P199's carry before its dispatch (it is `not-started`,
   no fixer briefed).
2. **R10-ORCH-REVIEW-PACKET**: P200's carry joins the group's live fixer resume
   (a fixer was briefed at 21:51Z); if its head is frozen, it lands in the
   delta round. Pay the `fix-review.md` cap by deletion.
3. **R10-ORCH-ROSTER-SCHEMA**: apply P203's carry before its dispatch; the same
   group already owns #2733, so P201's PR half goes into that group's carry
   text as prose, not as a carry of its own.
4. **Close #2494** with `09b1d002c` and `SELF-TEST 180 of 180 probes held` — it
   is done in the tree and its group is done on both rosters.
5. Also close, after reading their merged PRs: the other 22 issues a done or
   absorbed group still lists (P201's corrected count, #2494 aside). They are
   the close-out debt V121's line would have surfaced; #2494 shows the class is
   real.
6. Until P199 lands, point the tick at the live train's own queue and log at
   each launch; its TRAIN section described s58 for five hours.
