# Review packet #2930
head: 33660280381756f968ee197f374e9254eecfde19
base: b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123054142588 skipped
cancel-superseded id=123054924156 queued
prelude id=123054924176 queued
refresh id=123054923821 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/owed_unactioned.py --self-test
             `tools/audit/seat/owed_unactioned.py` is in the tree at this head
  ok         python3 -I dev/audit/rca/owed-unactioned/mutants.py .
             `dev/audit/rca/owed-unactioned/mutants.py` is in the tree at this head
  ok         bash dev/audit/rca/owed-unactioned/live.sh . <session>/s7/ORCH-QUEUE.md <session>/seat-ledger.md
             `dev/audit/rca/owed-unactioned/live.sh` is in the tree at this head
  ok         python3 -I dev/audit/rca/owed-unactioned/replay.py <session>/orch-sweep.log .
             `dev/audit/rca/owed-unactioned/replay.py` is in the tree at this head
  ok         time python3 -I tools/audit/seat/owed_unactioned.py --tick dev/audit/rca/owed-unactioned/boards/tick-1904.txt --state <tmp>/t.json --acks <session>/s7/ORCH-QUEUE.md --acks <session>/seat-ledger.md --no-write --max-board-min 600
             `tools/audit/seat/owed_unactioned.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/ledger.py --log <session>/cloud-relay.log level <hrefs> <empty topics>
             `tools/audit/seat/ledger.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head

FIGURES: 7 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 59f45b2d4..6ca95144d 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -596,6 +596,13 @@ jobs:
           python3 -I tools/audit/seat/roster_queue.py --self-test | tee "$RUNNER_TEMP/roster-queue-self-test.txt"
           grep -Eq '^roster_queue self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/roster-queue-self-test.txt"
 
+      - name: Show the owed-line reader refusing a stale board and a lapsed acknowledgement
+        if: ${{ !cancelled() }}
+        run: |
+          set -o pipefail
+          python3 -I tools/audit/seat/owed_unactioned.py --self-test | tee "$RUNNER_TEMP/owed-unactioned-self-test.txt"
+          grep -Eq '^owed_unactioned self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/owed-unactioned-self-test.txt"
+
       - name: Show the detached launcher refusing its own fixtures
         if: ${{ !cancelled() }}
         run: |
diff --git a/dev/audit/config/bugclasses.json b/dev/audit/config/bugclasses.json
index cbee21360..dc2f96dc0 100644
--- a/dev/audit/config/bugclasses.json
+++ b/dev/audit/config/bugclasses.json
@@ -4534,6 +4534,22 @@
         "dev/audit/rca/R10-RCA-HEADMOVED.md"
       ]
     },
+    "R10-RCA-OWED-UNACTIONED": {
+      "class": null,
+      "level": "instance-or-process",
+      "subject": "tick OWED lines stood for hours with no action: triage-s7-batch49 and r10-review-carry 5.7 h and 5.6 h host-up, critical-path r10-orch-beatd (#2916) 1.9 h on 2026-10-28; three more past 4 h on the night's sweep log",
+      "trigger": "recurrence (owner corrections 2026-10-18, 10-22, 10-24, 10-28; 6 instances past the 4 h threshold in about 11.4 host-up hours of sweeps)",
+      "date": "2026-10-28",
+      "status": "proposed",
+      "parts_missing": [],
+      "process_state": "(c) the sweep ran (19 board reads 10:40Z-18:55Z) and its unit, a board read, cannot tell a standing, a handled and a failed-handling owed line apart; the board's rc ignores owed lines, its owed view shows 8 of 26, and 15 of 19 reads filtered the block away",
+      "countermeasure": "built: tools/audit/seat/owed_unactioned.py, run in sweep_template.md step (5): exit 1 on every owed key standing 2 sweeps with no live OWED-ACK (lapsing, 1 h default, 12 h cap); fires on today's and the night's boards, null controls quiet, 10 of 10 mutants killed; session orch_sweep.sh fold and the split ledger home are the orchestrator's",
+      "landed": null,
+      "in_tree_home": "dev/audit/rca/R10-RCA-OWED-UNACTIONED.md",
+      "doc": [
+        "dev/audit/rca/R10-RCA-OWED-UNACTIONED.md"
+      ]
+    },
     "R10-N-vocabulary-drift": {
       "class": "N-vocabulary-drift",
       "level": "class",
diff --git a/dev/audit/rca/R10-RCA-OWED-UNACTIONED.md b/dev/audit/rca/R10-RCA-OWED-UNACTIONED.md
new file mode 100644
index 000000000..ddac625f7
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-OWED-UNACTIONED.md
@@ -0,0 +1,237 @@
+# R10-RCA-OWED-UNACTIONED: tick owed lines that stood for hours with no action
+
+This is a root-cause seat. It follows `root-cause.md` (under
+`dev/governance/roles/`) and `dev/governance/rules/defect-root-cause.md`. It
+ran at `origin/main` `beb570c8` on 2026-10-28, from 19:02Z. The trigger was
+recurrence: the owner corrected this class on 2026-10-28 at 19:00Z ("no pr
+should wait without reason, in particular not CP prs").
+
+Evidence lives in `dev/audit/rca/owed-unactioned/`. The session inputs are
+outside the tree, so each script takes them as arguments:
+
+- `replay.py <orch-sweep.log> <checkout> [--acked]` replays the night's sweep
+  boards. Its outputs are `replay_out.tsv` and `replay_acked_out.tsv`.
+- `live.sh <checkout> <ack files>` runs the two live boards of today, which are
+  saved in `boards/`. Its output is `live_out.txt`.
+- `mutants.py <checkout>` plants ten mutants in the tool. Its output is
+  `mutants_out.tsv`.
+
+## 1. The defect, reproduced
+
+The tick (`orchestrator_tick.py`) prints its owed lines on every pass. Its
+`ledger.escalate` adds `DISPATCH:` lines at 4 h and `OWNER FLAG:` lines at
+12 h. Both thresholds are the owner's ruling of 2026-10-21. The lines were
+printed, and they still stood. Times below come from git, the obligations
+ledger and the orchestrator's queue (`ORCH-QUEUE.md`).
+
+| obligation | complete at | what was done | effective action | standing, host up |
+|---|---|---|---|---|
+| `triage-s7-batch49` (handoff + body) | 10:38:12Z | 10:55Z routed to the opener seat. The opener first ran at 17:36:08Z and refused `BAD-DEST`. At 17:39Z the queue recorded a wait on RCA-HEADMOVED, whose PR #2909 had merged at 16:41:53Z. | 19:09Z, after the owner's 19:00Z correction | 5.7 h |
+| `r10-review-carry` (handoff + body) | 10:44:11Z | 11:00Z routed to the opener. It ran at 17:16:39Z and was refused (`app_approve.sh` conflict). At 17:39Z "re-cut owed" was recorded, and no fixer started. | 19:09Z | 5.6 h |
+| `r10-orch-beatd`, `repair=review`, **critical-path #2916** | 17:17:21Z (`c991d64c`) | The relay printed `HELD-REVIEW #2916 ... list #2916 in cloud-handoff-release` on all 33 of its passes in the log. At 19:00Z the queue recorded "Relay updates #2916 -> then review", which was false: the relay was holding it. | 19:09Z | 1.9 h |
+
+The host was down from 12:42Z to 15:32Z (power loss, `ORCH-QUEUE.md` 15:45Z).
+That 2.83 h is taken out of the standing figures.
+
+The same shape appears on the night of 2026-10-28, in the session board's own
+log (`orch-sweep.log`, 31 sweeps, 00:27Z to 05:56Z). `triage-s6-batch40` stood
+on all 31 sweeps, aging from 4.8 h to 10.2 h, and was disposed at 08:58Z.
+`r10-learner-default` stood on 28 sweeps, aging from 4.6 h to 9.6 h, and got a
+fixer at 08:38Z. `r10-cop-partload` `54437ac8` stood on 23 sweeps, aging from
+0.8 h to 4.8 h.
+
+## 2. The cause
+
+**Nothing in the sweep carries owed state as a result, so the sweep can report
+done while an owed line stands. It also checks a handled line no more than an
+unhandled one.** Three mechanisms make this up, each measured:
+
+1. **The board's exit code ignores owed lines.** `orch_sweep.sh`, the session
+   copy of the sweep board, sets `rc=1` only for a dead loop, a dead seat, a
+   stale tick or beat, or a red train. Its owed block comes last: on average
+   it starts at line 56 of a 65-line board (`orch-sweep.log`, 32 blocks). It
+   is `grep -E '^-> (OWED|REVIEW OWED)' | tail -8 | cut -c1-170`. On the
+   19:04Z board that shows 8 of the 26 owed-family lines. It never shows a
+   `DISPATCH:`, `OWNER FLAG:` or `DESIGN-BUILD:` line, so the tick's own age
+   escalation never reaches it.
+2. **The orchestrator's ad-hoc filters removed the block, and nothing
+   signalled it.** The orchestrator read the board 19 times between 10:40Z and
+   18:55Z (Bash `tool_use` records in the session transcript):
+   - 11 reads were `orch_sweep.sh 2>&1 | grep -v '^ ok' | sed -n '1,/verdict refs/p' | head -40`.
+     That pipeline stops before the owed block by construction.
+   - 1 read was `sed -n '1,/-- pull requests/p'`.
+   - 2 reads were `grep -E` patterns that have no `OWED` alternative.
+   - 1 read was a bare `head -40`.
+   - 4 reads could show the block: one `tail -60`, and three `grep ... OWED ... | head`.
+
+   So 15 of 19 reads did not display the block. Since `rc` ignored it, the
+   reads did not look any different.
+3. **A recorded action is never re-checked.** Each of today's three lines had
+   an action written against it: a routing at 10:55Z and 11:00Z, a named wait
+   at 17:39Z, and a belief at 19:00Z. Each action then failed: the opener did
+   not run for 6.3 h, the wait's precondition had already cleared, and the
+   relay held the update. The line printed exactly as it had before the
+   action. No instrument ages an action, so "handled once" and "handled" read
+   the same.
+
+**Contributing: standing noise from a split ledger home.** The standing relay
+runs `cloud_relay.sh pass --log <r10s6>/cloud-relay.log`. `cloud_relay.sh
+dispose` wrote the session's dispositions there:
+- `roster-b24-wip` and `triage-s6-batch40` at 08:58Z;
+- `r10-handoff-bodies` at 09:12Z.
+
+`tick_loop.sh` was started without `HPO_STATE_DIR`. Its own relay pass and
+the tick therefore use `~/.local/state/hpo`, whose `dispositions.tsv` (last
+written 2026-10-27T11:28Z) holds none of them. `ledger.py level`, run against
+the relay's home, prints `disposed=2` for `roster-b24-wip` and
+`r10-handoff-bodies`. On the tick's board, those two still print `DISPATCH:`
+and `OWNER FLAG:` at 31.2 h and 18.3 h. On the morning's board the
+orchestrator wrote that the tick's lines for these refs were known. A board
+that always carries known-stale `OWNER FLAG` lines teaches its reader to skip
+them.
+
+## 3. Process state: (c)
+
+The process existed and was followed:
+- the tick's level-triggered owed lines (after the 2026-10-18 edge-trigger
+  miss);
+- the aging escalation (2026-10-21);
+- `sweep_template.md` step (5), "act on the newest actionable lines";
+- the standing instruction to act on every owed line in the turn. The
+  orchestrator's memory recorded it on 2026-10-18, 10-22, 10-24 (twice) and
+  10-28.
+
+The sweep ran every 10 to 15 minutes, with 19 board reads in the window
+above, and actions were recorded against all three lines. It did not produce
+the result because its unit, the board read, cannot tell the three cases
+apart: a standing line, a handled line and a line whose handling failed. The
+board's exit code says nothing about any of them.
+
+This is not (b). Three firmer instructions were written in eight days, and the
+class recurred after each. That is the pattern `root-cause.md` section 2
+warns of: an instruction that was obeyed, and wrong. It is not (a), because
+the tick-side signal and its escalation exist. The countermeasure therefore
+changes the unit, so that a sweep's result carries the owed state and a
+handled line returns after a bounded time.
+
+## 4. How far the class reaches
+
+- **Hidden owed builds.** `DESIGN-BUILD: R10-CONFIGFLOW-PAGES` and
+  `DESIGN-BUILD: R10-UX-HEALTH` are on the board: approved designs with no
+  build dispatched. The session board's owed grep omits that prefix, so it
+  has never shown them. Their age is not measured here.
+- **Hidden reviews.** `REVIEW OWED: #2887` and `#2896` sit above the `tail -8`
+  cut on the 19:04Z board.
+- **Split ledger home.** See section 2. Session configuration: the tick
+  restart line in `sweep_mech.sh` (`loop tick ... tick_loop.sh`) needs
+  `HPO_STATE_DIR` set to the relay log's directory, or else the standing
+  relay must drop `--log`. The orchestrator owes that line. It is not in the
+  tree.
+- **Open PRs with no owed line.** #2919, #2917 and #2906 stood with no
+  handoff, so no owed line exists for them. That half is triage proposal
+  **V179** (tick per-PR reconciliation) and is not duplicated here.
+- **Same shape elsewhere in the tree.** `orchestrator_tick.py`'s docstring
+  states "the list is a report, not a gate", and it always exits 0.
+  `ledger.py board` exits 1 when obligations exist, but nothing in the sweep
+  reads that code. `pulse.py` is the sweep's other liveness reader. It names
+  waiting consumers, and step (5) already makes its `UNREADABLE` not clean.
+  No other sweep instrument folds owed state into a result.
+
+## 5. Cost test
+
+    cost(countermeasure, recurring) < cost(defect) x P(recurrence)
+
+Both sides are wall-clock per day.
+
+- **cost(defect).** Today's three instances left 13.2 h of owed work idle
+  while the host was up (5.7 + 5.6 + 1.9). The 1.9 h are on the critical
+  path, so the round's closure moves by up to 1.9 h: #2916's review cannot
+  start before its held update lands. The night's three instances are each
+  at least 4 h in the log alone.
+- **P(recurrence).** Measured, not estimated. Six instances stood past the
+  owner's 4 h threshold in about 11.4 host-up hours of observed sweeps: the
+  night log's 5.5 h, plus today's 10:38Z to 12:42Z and 15:32Z to 19:09Z. Six
+  owner corrections of the class are recorded on four days between
+  2026-10-18 and 2026-10-28. So P per day is 1.
+- **cost(countermeasure, recurring).**
+  - Runtime: 0.08 s per sweep, measured five times on the 19:04Z board with
+    the session's 750 KB of queue and ledger as acknowledgement files.
+  - Acknowledgement load: the night replay holds a mean of 5.6 unactioned
+    keys per sweep (`replay_out.tsv`). At one 1 h acknowledgement per
+    standing key and about 30 s per line, that is at most 2.8 min/h, or
+    67 min/day, if nothing is ever discharged. That time is the re-check the
+    defect lacked; it is not overhead on top of it. A parked line can carry
+    `ttl=12`.
+- **Verdict.** 67 min/day at most, against at least 1.9 h/day on the critical
+  path alone and 13.2 h/day of idle owed work. **Build.**
+
+## 6. The countermeasure: `tools/audit/seat/owed_unactioned.py`
+
+The state it addresses is (c): it changes the unit from a board read to a
+result.
+
+- It reads the tick's **whole** owed family: `-> OWED…`, `REVIEW OWED:`,
+  `DISPATCH:`, `OWNER FLAG:` and `DESIGN-BUILD:`. It keys each line on its
+  topic or `#<pr>`, so the four lines `r10-review-carry` prints are one
+  obligation.
+- A state file counts the sweeps each key has stood on. A sweep is a distinct
+  board, by provenance time, so re-reading the same board adds nothing.
+- At 2 sweeps, a key is **UNACTIONED** unless an acknowledgement covers it. An
+  acknowledgement is a live `OWED-ACK <UTC> <key> <id> [ttl=<h>] <reason>`
+  line whose id prefixes a sha the key carries now. A new tip therefore needs
+  a new acknowledgement.
+- An acknowledgement lapses after its ttl: 1 h by default, 12 h at most. The
+  most recent handling of a line is therefore always re-checked within 12 h.
+  Free text in a queue covers nothing; that is exactly the 10:55Z and 17:39Z
+  routing lines.
+- Exit 1 prints the block, oldest first, each entry with a ready ack line.
+- Exit 2 means it cannot say: no provenance line, a board older than 20 min,
+  an owed line it cannot key, or an unreadable state file. It never exits 0
+  in that case.
+
+`sweep_template.md` step (5) now runs it on every sweep, and the sweep is not
+done while it exits 1. Its `INSTRUMENTS.md` entry is beside the others.
+
+### Demonstration
+
+- **It fires on today's case.** `live_out.txt` reads the 19:04Z and 19:12Z
+  boards against one fresh state, with the session's real `ORCH-QUEUE.md` and
+  `seat-ledger.md` as acknowledgement files. Both hold 0 `OWED-ACK` lines.
+  The first board exits 0, because all 12 keys are new. The second exits 1
+  with all 12 UNACTIONED, including:
+  - `r10-orch-beatd` (its `handoff-held #2916 REVIEW` line and its
+    `repair=review` line, as one entry);
+  - `triage-s7-batch49` and `r10-review-carry`, with their `DISPATCH:` lines;
+  - both `DESIGN-BUILD` lines.
+- **It fires on the night's case.** `replay_out.tsv` replays the 31 night
+  boards. The first exits 0, and the other 30 exit 1. `triage-s6-batch40`
+  and `r10-learner-default` are each UNACTIONED from their own second sweep,
+  11 minutes after first sight. On the session board they stood for 5 h, and
+  the board's `rc` never moved for them.
+- **Null controls.**
+  - `replay_acked_out.tsv` re-takes an acknowledgement for every key on every
+    sweep: 31 of 31 boards exit 0.
+  - In `live_out.txt`, acknowledging all 12 keys at 19:13Z makes the 19:12Z
+    board exit 0.
+  - The self-test's all-clear board exits 0 with 0 keys.
+- **It is not green by skipping.** These self-test arms each exit 2: a board
+  with no provenance line, a 45-minute-old board, an owed line it cannot key,
+  and a corrupt state file. A future, over-long or malformed acknowledgement
+  is refused and covers nothing.
+- **Mutation proof.** `mutants_out.tsv` plants 10 mutants, one per predicate
+  above, and the self-test kills all 10. The self-test runs 21 checks
+  offline.
+
+## 7. Owed by others; not built here
+
+- **The session board, `orch_sweep.sh`.** It is not in the tree; the
+  orchestrator applies this. Print the tool's output first, directly under
+  the `== SWEEP` line, so that any `head` filter keeps it. Fold the tool's
+  exit code into `rc`. Delete the `-- owed (tick)` grep, which is the
+  `tail -8` view. The pull-request body carries the exact lines.
+- **The split ledger home** (section 4). This is session configuration, owned
+  by the orchestrator.
+- **V179.** Open pull requests with no owed line are triage's.
+- **Not proposed: a fourth memory instruction.** Section 3 explains why.
+- **Policy.** None of it changes. `sweep_template.md` is a usage guide by its
+  own header, and `INSTRUMENTS.md` adds no obligation.
diff --git a/dev/audit/rca/owed-unactioned/boards/tick-1904.txt b/dev/audit/rca/owed-unactioned/boards/tick-1904.txt
new file mode 100644
index 000000000..d69c8ba7f
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/boards/tick-1904.txt
@@ -0,0 +1,27 @@
+BOARD measured from origin/main at beb570c817c4, 2026-10-28T19:04:55.499677+00:00
+-> REVIEW OWED: #2887 17d3cf384a91
+-> REVIEW OWED: #2896 82a6ef4a1004
+-> OWED: OWED 2026-10-28T19:04:46Z handoff-update refs/heads/handoff/r10-buffer-store 6ff573112cbfd1e0dc410cd0f056f3d978c54116
+-> OWED: OWED 2026-10-28T19:04:37Z handoff-held refs/heads/handoff/r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d #2916 REVIEW
+-> OWED: OWED 2026-10-28T19:04:48Z handoff-no-pr refs/heads/handoff-body/r10-handoff-bodies 0e34b52305292d333fd0c33839e9f2ce0e67ee0d ct=1793148745
+-> OWED: OWED 2026-10-28T19:04:48Z handoff-no-pr refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255f6fb65181368234cf01fba7333cd ct=1793135566
+-> OWED: OWED 2026-10-28T19:04:48Z handoff-no-pr refs/heads/handoff-body/r10-review-carry 855634af515a5ab7e3e70e0705a249bc843bf65f ct=1793184251 attempt=2026-10-28T17:16:39Z,unopened
+-> OWED: OWED 2026-10-28T19:04:48Z handoff-no-pr refs/heads/handoff-body/triage-s7-batch49 b264fdd66f9427fb1a777a193e48960a161156bb ct=1793183892 attempt=2026-10-28T17:36:08Z,unopened
+-> OWED: OWED 2026-10-28T19:04:48Z handoff-no-pr refs/heads/handoff/r10-review-carry 32221ca27fadfcf5735889b24cafa162eb395cd8 ct=1793183831 attempt=2026-10-28T17:16:39Z,unopened
+-> OWED: OWED 2026-10-28T19:04:48Z handoff-no-pr refs/heads/handoff/roster-b24-wip 7191d786acaa7e4d6b06b82c1131ec32ddefcddf ct=1793102500
+-> OWED: OWED 2026-10-28T19:04:48Z handoff-no-pr refs/heads/handoff/triage-s7-batch49 40bec0ab6c44747b9311abb80ca8220b2656b0b7 ct=1793181926 attempt=2026-10-28T17:36:08Z,unopened
+-> DISPATCH: ? refs/heads/handoff/roster-b24-wip 7191d786acaa no body ref (31.1h)
+-> DISPATCH: ? refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255 no code ref (21.9h)
+-> DISPATCH: ? refs/heads/handoff-body/r10-handoff-bodies 0e34b5230529 no code ref (18.2h)
+-> DISPATCH: ? refs/heads/handoff/triage-s7-batch49 40bec0ab6c44 opener (9.0h; last attempt 2026-10-28T17:36:08Z,unopened)
+-> DISPATCH: R10-REVIEW-CARRY refs/heads/handoff/r10-review-carry 32221ca27fad opener (8.5h; last attempt 2026-10-28T17:16:39Z,unopened)
+-> OWNER FLAG: ? refs/heads/handoff/roster-b24-wip 7191d786acaa stranded 31.1h (threshold 12h)
+-> OWNER FLAG: ? refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255 stranded 21.9h (threshold 12h)
+-> OWNER FLAG: ? refs/heads/handoff-body/r10-handoff-bodies 0e34b5230529 stranded 18.2h (threshold 12h)
+-> DESIGN-BUILD: R10-CONFIGFLOW-PAGES design/r10-configflow-pages 32892dc67863 approved, no build dispatched (stage not-started)
+-> DESIGN-BUILD: R10-UX-HEALTH design/r10-ux-health e6797ca9d94e approved, no build dispatched (stage not-started)
+-> OWED handoff: audit-r10-roster 2ce021c6f19c4c4069d50994a271fd1e7b872834 1.4h uncovered=5 repair=opener -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: r10-buffer-store 6ff573112cbfd1e0dc410cd0f056f3d978c54116 2.1h uncovered=5 repair=update -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d 1.8h uncovered=1 repair=review -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: r10-review-carry 32221ca27fadfcf5735889b24cafa162eb395cd8 8.4h uncovered=6 repair=opener -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: triage-s7-batch49 40bec0ab6c44747b9311abb80ca8220b2656b0b7 9.0h uncovered=1 repair=opener -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
diff --git a/dev/audit/rca/owed-unactioned/boards/tick-1912.txt b/dev/audit/rca/owed-unactioned/boards/tick-1912.txt
new file mode 100644
index 000000000..9c1f46259
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/boards/tick-1912.txt
@@ -0,0 +1,27 @@
+BOARD measured from origin/main at beb570c817c4, 2026-10-28T19:12:36.691745+00:00
+-> REVIEW OWED: #2887 17d3cf384a91
+-> REVIEW OWED: #2896 82a6ef4a1004
+-> OWED: OWED 2026-10-28T19:12:49Z handoff-update refs/heads/handoff/r10-buffer-store 6ff573112cbfd1e0dc410cd0f056f3d978c54116
+-> OWED: OWED 2026-10-28T19:12:26Z handoff-held refs/heads/handoff/r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d #2916 REVIEW
+-> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/r10-handoff-bodies 0e34b52305292d333fd0c33839e9f2ce0e67ee0d ct=1793148745
+-> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255f6fb65181368234cf01fba7333cd ct=1793135566
+-> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/r10-review-carry 855634af515a5ab7e3e70e0705a249bc843bf65f ct=1793184251 attempt=2026-10-28T17:16:39Z,unopened
+-> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/triage-s7-batch49 b264fdd66f9427fb1a777a193e48960a161156bb ct=1793183892 attempt=2026-10-28T17:36:08Z,unopened
+-> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff/r10-review-carry 32221ca27fadfcf5735889b24cafa162eb395cd8 ct=1793183831 attempt=2026-10-28T17:16:39Z,unopened
+-> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff/roster-b24-wip 7191d786acaa7e4d6b06b82c1131ec32ddefcddf ct=1793102500
+-> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff/triage-s7-batch49 40bec0ab6c44747b9311abb80ca8220b2656b0b7 ct=1793181926 attempt=2026-10-28T17:36:08Z,unopened
+-> DISPATCH: ? refs/heads/handoff/roster-b24-wip 7191d786acaa no body ref (31.2h)
+-> DISPATCH: ? refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255 no code ref (22.0h)
+-> DISPATCH: ? refs/heads/handoff-body/r10-handoff-bodies 0e34b5230529 no code ref (18.3h)
+-> DISPATCH: ? refs/heads/handoff/triage-s7-batch49 40bec0ab6c44 opener (9.1h; last attempt 2026-10-28T17:36:08Z,unopened)
+-> DISPATCH: R10-REVIEW-CARRY refs/heads/handoff/r10-review-carry 32221ca27fad opener (8.6h; last attempt 2026-10-28T17:16:39Z,unopened)
+-> OWNER FLAG: ? refs/heads/handoff/roster-b24-wip 7191d786acaa stranded 31.2h (threshold 12h)
+-> OWNER FLAG: ? refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255 stranded 22.0h (threshold 12h)
+-> OWNER FLAG: ? refs/heads/handoff-body/r10-handoff-bodies 0e34b5230529 stranded 18.3h (threshold 12h)
+-> DESIGN-BUILD: R10-CONFIGFLOW-PAGES design/r10-configflow-pages 32892dc67863 approved, no build dispatched (stage not-started)
+-> DESIGN-BUILD: R10-UX-HEALTH design/r10-ux-health e6797ca9d94e approved, no build dispatched (stage not-started)
+-> OWED handoff: audit-r10-roster be898eaef54a6ba1f996b4ca9b11c6f93ce94ea4 0.0h uncovered=7 repair=opener -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: r10-buffer-store 6ff573112cbfd1e0dc410cd0f056f3d978c54116 2.3h uncovered=5 repair=update -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d 1.9h uncovered=1 repair=review -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: r10-review-carry 32221ca27fadfcf5735889b24cafa162eb395cd8 8.6h uncovered=6 repair=opener -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
+-> OWED handoff: triage-s7-batch49 40bec0ab6c44747b9311abb80ca8220b2656b0b7 9.1h uncovered=1 repair=opener -- no PR head carries it: open_pr.sh (opener), update_pr.sh (update) or a human decision (review)
diff --git a/dev/audit/rca/owed-unactioned/live.sh b/dev/audit/rca/owed-unactioned/live.sh
new file mode 100644
index 000000000..9f3c86e95
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/live.sh
@@ -0,0 +1,21 @@
+#!/bin/bash
+# live.sh <checkout> <ack file>...: the two live boards of 2026-10-28 (boards/), each read one
+# minute after its provenance time against one fresh state, with the session's own queue and
+# seat ledger as the ack files; then the null control, every key acknowledged at the second board.
+set -uo pipefail
+W=$1; shift; T=$W/tools/audit/seat/owed_unactioned.py; B=$(cd "$(dirname "$0")" && pwd)/boards
+S=$(mktemp -d); trap 'rm -rf "$S"' EXIT
+A=(); for f in "$@"; do A+=(--acks "$f"); echo "ack file $(basename "$f"): $(grep -c 'OWED-ACK' "$f") OWED-ACK line(s)"; done
+for b in tick-1904 tick-1912; do
+  at=$(head -1 "$B/$b.txt" | sed -E 's/.*, ([0-9T:-]+)\..*/\1Z/')
+  now=$(python3 -c "import datetime as d,sys;print((d.datetime.fromisoformat(sys.argv[1].replace('Z','+00:00'))+d.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ'))" "$at")
+  echo "== $b at $now"; python3 -I "$T" --tick "$B/$b.txt" --state "$S/live.json" "${A[@]}" --now "$now" | cut -c1-160; echo "rc=${PIPESTATUS[0]}"
+done
+echo "== null control: tick-1912 again, every key acknowledged at $now"
+python3 -I - "$T" "$B/tick-1912.txt" "$now" > "$S/acks.md" <<'PY'
+import importlib.util, sys
+s = importlib.util.spec_from_file_location("ou", sys.argv[1]); ou = importlib.util.module_from_spec(s); s.loader.exec_module(ou)
+for k, v in ou.board(open(sys.argv[2]).read())[1].items():
+    print(f"OWED-ACK {sys.argv[3]} {k} {(v['shas'] or ['-'])[0]} ttl=1 null control: named next action")
+PY
+python3 -I "$T" --tick "$B/tick-1912.txt" --state "$S/live.json" --acks "$S/acks.md" --now "$now" | head -1; echo "rc=${PIPESTATUS[0]}"
diff --git a/dev/audit/rca/owed-unactioned/live_out.txt b/dev/audit/rca/owed-unactioned/live_out.txt
new file mode 100644
index 000000000..6b1e01775
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/live_out.txt
@@ -0,0 +1,62 @@
+ack file ORCH-QUEUE.md: 0 OWED-ACK line(s)
+ack file seat-ledger.md: 0 OWED-ACK line(s)
+== tick-1904 at 2026-10-28T19:05:55Z
+owed: 12 key(s) on board 2026-10-28T19:04:55Z; 0 acknowledged, 0 unactioned (standing 2+ sweeps with no live OWED-ACK)
+rc=0
+== tick-1912 at 2026-10-28T19:13:36Z
+owed: 12 key(s) on board 2026-10-28T19:12:36Z; 0 acknowledged, 12 unactioned (standing 2+ sweeps with no live OWED-ACK)
+UNACTIONED
+  #2887  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> REVIEW OWED: #2887 17d3cf384a91
+      ack: OWED-ACK 2026-10-28T19:13:36Z #2887 17d3cf384a91 ttl=1 <next action, by whom; what it waits on>
+  #2896  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> REVIEW OWED: #2896 82a6ef4a1004
+      ack: OWED-ACK 2026-10-28T19:13:36Z #2896 82a6ef4a1004 ttl=1 <next action, by whom; what it waits on>
+  audit-r10-roster  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED handoff: audit-r10-roster be898eaef54a6ba1f996b4ca9b11c6f93ce94ea4 0.0h uncovered=7 repair=opener -- no PR head carries it: open_pr.sh (opener), u
+      ack: OWED-ACK 2026-10-28T19:13:36Z audit-r10-roster be898eaef54a ttl=1 <next action, by whom; what it waits on>
+  r10-buffer-store  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED: OWED 2026-10-28T19:12:49Z handoff-update refs/heads/handoff/r10-buffer-store 6ff573112cbfd1e0dc410cd0f056f3d978c54116
+      -> OWED handoff: r10-buffer-store 6ff573112cbfd1e0dc410cd0f056f3d978c54116 2.3h uncovered=5 repair=update -- no PR head carries it: open_pr.sh (opener), u
+      ack: OWED-ACK 2026-10-28T19:13:36Z r10-buffer-store 6ff573112cbf ttl=1 <next action, by whom; what it waits on>
+  r10-configflow-pages  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> DESIGN-BUILD: R10-CONFIGFLOW-PAGES design/r10-configflow-pages 32892dc67863 approved, no build dispatched (stage not-started)
+      ack: OWED-ACK 2026-10-28T19:13:36Z r10-configflow-pages 32892dc67863 ttl=1 <next action, by whom; what it waits on>
+  r10-handoff-bodies  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/r10-handoff-bodies 0e34b52305292d333fd0c33839e9f2ce0e67ee0d ct=1793148745
+      -> DISPATCH: ? refs/heads/handoff-body/r10-handoff-bodies 0e34b5230529 no code ref (18.3h)
+      -> OWNER FLAG: ? refs/heads/handoff-body/r10-handoff-bodies 0e34b5230529 stranded 18.3h (threshold 12h)
+      ack: OWED-ACK 2026-10-28T19:13:36Z r10-handoff-bodies 0e34b5230529 ttl=1 <next action, by whom; what it waits on>
+  r10-orch-beatd  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED: OWED 2026-10-28T19:12:26Z handoff-held refs/heads/handoff/r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d #2916 REVIEW
+      -> OWED handoff: r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d 1.9h uncovered=1 repair=review -- no PR head carries it: open_pr.sh (opener), upd
+      ack: OWED-ACK 2026-10-28T19:13:36Z r10-orch-beatd c991d64cdaef ttl=1 <next action, by whom; what it waits on>
+  r10-rca-state-beat-gate  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255f6fb65181368234cf01fba7333cd ct=1793135566
+      -> DISPATCH: ? refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255 no code ref (22.0h)
+      -> OWNER FLAG: ? refs/heads/handoff-body/r10-rca-state-beat-gate a0d474025255 stranded 22.0h (threshold 12h)
+      ack: OWED-ACK 2026-10-28T19:13:36Z r10-rca-state-beat-gate a0d474025255 ttl=1 <next action, by whom; what it waits on>
+  r10-review-carry  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/r10-review-carry 855634af515a5ab7e3e70e0705a249bc843bf65f ct=1793184251 attempt=2
+      -> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff/r10-review-carry 32221ca27fadfcf5735889b24cafa162eb395cd8 ct=1793183831 attempt=2026-1
+      -> DISPATCH: R10-REVIEW-CARRY refs/heads/handoff/r10-review-carry 32221ca27fad opener (8.6h; last attempt 2026-10-28T17:16:39Z,unopened)
+      -> OWED handoff: r10-review-carry 32221ca27fadfcf5735889b24cafa162eb395cd8 8.6h uncovered=6 repair=opener -- no PR head carries it: open_pr.sh (opener), u
+      ack: OWED-ACK 2026-10-28T19:13:36Z r10-review-carry 855634af515a ttl=1 <next action, by whom; what it waits on>
+  r10-ux-health  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> DESIGN-BUILD: R10-UX-HEALTH design/r10-ux-health e6797ca9d94e approved, no build dispatched (stage not-started)
+      ack: OWED-ACK 2026-10-28T19:13:36Z r10-ux-health e6797ca9d94e ttl=1 <next action, by whom; what it waits on>
+  roster-b24-wip  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff/roster-b24-wip 7191d786acaa7e4d6b06b82c1131ec32ddefcddf ct=1793102500
+      -> DISPATCH: ? refs/heads/handoff/roster-b24-wip 7191d786acaa no body ref (31.2h)
+      -> OWNER FLAG: ? refs/heads/handoff/roster-b24-wip 7191d786acaa stranded 31.2h (threshold 12h)
+      ack: OWED-ACK 2026-10-28T19:13:36Z roster-b24-wip 7191d786acaa ttl=1 <next action, by whom; what it waits on>
+  triage-s7-batch49  sweeps=2 first=2026-10-28T19:04:55Z (0.1h)
+      -> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff-body/triage-s7-batch49 b264fdd66f9427fb1a777a193e48960a161156bb ct=1793183892 attempt=
+      -> OWED: OWED 2026-10-28T19:12:53Z handoff-no-pr refs/heads/handoff/triage-s7-batch49 40bec0ab6c44747b9311abb80ca8220b2656b0b7 ct=1793181926 attempt=2026-
+      -> DISPATCH: ? refs/heads/handoff/triage-s7-batch49 40bec0ab6c44 opener (9.1h; last attempt 2026-10-28T17:36:08Z,unopened)
+      -> OWED handoff: triage-s7-batch49 40bec0ab6c44747b9311abb80ca8220b2656b0b7 9.1h uncovered=1 repair=opener -- no PR head carries it: open_pr.sh (opener), 
+      ack: OWED-ACK 2026-10-28T19:13:36Z triage-s7-batch49 b264fdd66f94 ttl=1 <next action, by whom; what it waits on>
+rc=1
+== null control: tick-1912 again, every key acknowledged at 2026-10-28T19:13:36Z
+owed: 12 key(s) on board 2026-10-28T19:12:36Z; 12 acknowledged, 0 unactioned (standing 2+ sweeps with no live OWED-ACK)
+rc=0
diff --git a/dev/audit/rca/owed-unactioned/mutants.py b/dev/audit/rca/owed-unactioned/mutants.py
new file mode 100644
index 000000000..fe1d11985
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/mutants.py
@@ -0,0 +1,38 @@
+#!/usr/bin/env python3
+"""Plant each predicate's mutant in a scratch copy of owed_unactioned.py and
+demand its --self-test refuse it. Prints one row per mutant: KILLED or SURVIVED.
+
+    python3 -I mutants.py <checkout>
+"""
+import os, shutil, subprocess, sys, tempfile
+
+SRC = os.path.join(sys.argv[1], "tools/audit/seat/owed_unactioned.py")
+MUTANTS = [
+    ("fires one sweep late", 'elif s["sweeps"] >= after:', 'elif s["sweeps"] > after:'),
+    ("an ack never lapses", "if exp > now:", "if True:"),
+    ("a stale board reads clean", "a stale board cannot say a line was discharged\")\n        return 2",
+     "a stale board cannot say a line was discharged\")\n        return 0"),
+    ("any ack covers any tip", "x.startswith(a[0]) or (len(a[0]) >= 7 and a[0].startswith(x)) for x in ids)",
+     "True for x in ids)"),
+    ("a re-read board counts a sweep", "(1 if fresh else 0)", "1"),
+    ("DISPATCH lines leave the family", "OWED|REVIEW OWED:|DISPATCH:|", "OWED|REVIEW OWED:|"),
+    ("a future ack is accepted", "at > now + dt.timedelta(minutes=5)", "False"),
+    ("an over-long ttl is accepted", "not 0 < ttl <= TTL_MAX", "not 0 < ttl"),
+    ("an unkeyable line is skipped", 'raise Unreadable(f"an owed line names no topic', 'return "?", shas\n    raise Unreadable(f"an owed line names no topic'),
+    ("an unreadable state starts fresh", 'out(f"UNREADABLE: state {state_path}: {e}")\n        return 2',
+     'state = {"board": None, "keys": {}}'),
+]
+src = open(SRC).read()
+bad = 0
+with tempfile.TemporaryDirectory() as d:
+    for name, a, b in MUTANTS:
+        if src.count(a) != 1:
+            print(f"UNAPPLIED\t{name}"); bad += 1; continue
+        p = os.path.join(d, "owed_unactioned.py")
+        open(p, "w").write(src.replace(a, b))
+        r = subprocess.run([sys.executable, "-I", p, "--self-test"], capture_output=True, text=True)
+        tag = "KILLED" if r.returncode != 0 else "SURVIVED"
+        bad += tag != "KILLED"
+        print(f"{tag}\t{name}\t{r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-80:]}")
+print(f"mutants: {len(MUTANTS)}, not killed {bad}")
+sys.exit(1 if bad else 0)
diff --git a/dev/audit/rca/owed-unactioned/mutants_out.tsv b/dev/audit/rca/owed-unactioned/mutants_out.tsv
new file mode 100644
index 000000000..0c678f31d
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/mutants_out.tsv
@@ -0,0 +1,11 @@
+KILLED	fires one sweep late	owed_unactioned self-test: 21 checks, 5 failed
+KILLED	an ack never lapses	owed_unactioned self-test: 21 checks, 1 failed
+KILLED	a stale board reads clean	owed_unactioned self-test: 21 checks, 1 failed
+KILLED	any ack covers any tip	owed_unactioned self-test: 21 checks, 1 failed
+KILLED	a re-read board counts a sweep	owed_unactioned self-test: 21 checks, 1 failed
+KILLED	DISPATCH lines leave the family	owed_unactioned self-test: 21 checks, 3 failed
+KILLED	a future ack is accepted	owed_unactioned self-test: 21 checks, 1 failed
+KILLED	an over-long ttl is accepted	owed_unactioned self-test: 21 checks, 1 failed
+KILLED	an unkeyable line is skipped	owed_unactioned self-test: 21 checks, 1 failed
+KILLED	an unreadable state starts fresh	owed_unactioned self-test: 21 checks, 1 failed
+mutants: 10, not killed 0
diff --git a/dev/audit/rca/owed-unactioned/replay.py b/dev/audit/rca/owed-unactioned/replay.py
new file mode 100644
index 000000000..8980bc8e1
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/replay.py
@@ -0,0 +1,47 @@
+#!/usr/bin/env python3
+"""Replay the session sweep log's owed blocks through owed_unactioned.py.
+
+    python3 -I replay.py <orch-sweep.log> <checkout> [--acked]
+
+orch-sweep.log is the session board's own output (`orch_sweep.sh`), one
+`== SWEEP <UTC> ==` block per sweep, its `-- owed (tick)` block being the
+tick's `-> OWED` lines that board kept. Each block becomes one board, read at
+its sweep time plus one minute, against one state file, as the sweep would
+have run it. Prints one TSV row per sweep: time, rc, owed keys, unactioned
+keys. `--acked` writes, at each key's first sweep, an OWED-ACK that the
+orchestrator re-takes every sweep (ttl=1): the null control, which must print
+rc 0 throughout.
+"""
+import datetime as dt, importlib.util, os, re, sys, tempfile
+
+log, root = sys.argv[1], sys.argv[2]
+acked = "--acked" in sys.argv
+spec = importlib.util.spec_from_file_location("ou", os.path.join(root, "tools/audit/seat/owed_unactioned.py"))
+ou = importlib.util.module_from_spec(spec); spec.loader.exec_module(ou)
+
+sweeps, cur = [], None
+for line in open(log, errors="replace"):
+    m = re.match(r"== SWEEP (\S+) ==", line)
+    if m:
+        cur = [m.group(1), []]; sweeps.append(cur); continue
+    s = line.strip()
+    if cur and s.startswith("-> OWED"):
+        cur[1].append(s)
+
+print("sweep\trc\towed\tunactioned")
+with tempfile.TemporaryDirectory() as d:
+    state = os.path.join(d, "state.json")
+    for at, lines in sweeps:
+        t = ou.utc(at)
+        board = f"BOARD measured from origin/main at replay, {at}\n" + "\n".join(lines) + "\n"
+        acks = []
+        if acked:
+            keys = ou.board(board)[1]
+            acks = [("acks", "\n".join(f"OWED-ACK {at} {k} {(v['shas'] or ['-'])[0]} ttl=1 replay null control: re-taken each sweep"
+                                       for k, v in keys.items()))]
+        out = []
+        rc = ou.run(board, state, acks, t + dt.timedelta(minutes=1), 2, 20, True, out.append)
+        head = out[0] if out else ""
+        n = re.search(r"owed: (\d+) key", head)
+        bad = [o.split()[0] for o in out if re.match(r"  \S+  sweeps=", o)]
+        print(f"{at}\t{rc}\t{n.group(1) if n else '?'}\t{','.join(bad)}")
diff --git a/dev/audit/rca/owed-unactioned/replay_acked_out.tsv b/dev/audit/rca/owed-unactioned/replay_acked_out.tsv
new file mode 100644
index 000000000..e76c49126
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/replay_acked_out.tsv
@@ -0,0 +1,32 @@
+sweep	rc	owed	unactioned
+2026-10-28T00:27:03Z	0	6	
+2026-10-28T00:38:13Z	0	6	
+2026-10-28T00:49:30Z	0	7	
+2026-10-28T01:00:28Z	0	8	
+2026-10-28T01:11:32Z	0	7	
+2026-10-28T01:22:41Z	0	7	
+2026-10-28T01:33:47Z	0	7	
+2026-10-28T01:44:51Z	0	7	
+2026-10-28T01:55:53Z	0	7	
+2026-10-28T02:06:57Z	0	7	
+2026-10-28T02:18:05Z	0	8	
+2026-10-28T02:29:10Z	0	8	
+2026-10-28T02:40:11Z	0	7	
+2026-10-28T02:51:03Z	0	7	
+2026-10-28T03:01:51Z	0	6	
+2026-10-28T03:12:25Z	0	6	
+2026-10-28T03:23:00Z	0	6	
+2026-10-28T03:33:47Z	0	6	
+2026-10-28T03:44:49Z	0	7	
+2026-10-28T03:55:56Z	0	7	
+2026-10-28T04:06:50Z	0	6	
+2026-10-28T04:17:52Z	0	7	
+2026-10-28T04:28:50Z	0	7	
+2026-10-28T04:39:46Z	0	6	
+2026-10-28T04:50:24Z	0	7	
+2026-10-28T05:01:25Z	0	7	
+2026-10-28T05:12:26Z	0	6	
+2026-10-28T05:23:25Z	0	6	
+2026-10-28T05:34:25Z	0	7	
+2026-10-28T05:45:31Z	0	8	
+2026-10-28T05:56:33Z	0	7	
diff --git a/dev/audit/rca/owed-unactioned/replay_out.tsv b/dev/audit/rca/owed-unactioned/replay_out.tsv
new file mode 100644
index 000000000..1decf2938
--- /dev/null
+++ b/dev/audit/rca/owed-unactioned/replay_out.tsv
@@ -0,0 +1,32 @@
+sweep	rc	owed	unactioned
+2026-10-28T00:27:03Z	0	6	
+2026-10-28T00:38:13Z	1	6	audit-r10-roster,r10-cop-partload,r10-learner-default,r10-review-carry,roster-b24-wip,triage-s6-batch40
+2026-10-28T00:49:30Z	1	7	audit-r10-roster,r10-cop-partload,r10-learner-default,roster-b24-wip,triage-s6-batch40
+2026-10-28T01:00:28Z	1	8	audit-r10-roster,r10-cop-partload,r10-learner-default,triage-s6-batch40,#2891
+2026-10-28T01:11:32Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,#2891
+2026-10-28T01:22:41Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,#2891,fix-r10-diag-ages,r10-buffer-store,r10-flow-jidoka-p2
+2026-10-28T01:33:47Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,#2891,r10-buffer-store
+2026-10-28T01:44:51Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-buffer-store,r10-house-grade,r10-immersion-latch
+2026-10-28T01:55:53Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-immersion-latch,roster-b24-wip
+2026-10-28T02:06:57Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-immersion-latch,roster-b24-wip,fix-r10-immersion-latch-pr
+2026-10-28T02:18:05Z	1	8	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-immersion-latch,fix-r10-cop-partload
+2026-10-28T02:29:10Z	1	8	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-immersion-latch,r10-flow-board,r10-roster-freeze-close
+2026-10-28T02:40:11Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster
+2026-10-28T02:51:03Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T03:01:51Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T03:12:25Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T03:23:00Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T03:33:47Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T03:44:49Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T03:55:56Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T04:06:50Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T04:17:52Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T04:28:50Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,r10-flow-board
+2026-10-28T04:39:46Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster
+2026-10-28T04:50:24Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip
+2026-10-28T05:01:25Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,r10-roster-freeze-close,audit-r10-roster,roster-b24-wip,r10-buffer-store
+2026-10-28T05:12:26Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,audit-r10-roster,roster-b24-wip,r10-buffer-store
+2026-10-28T05:23:25Z	1	6	r10-cop-partload,r10-learner-default,triage-s6-batch40,audit-r10-roster,roster-b24-wip,r10-buffer-store
+2026-10-28T05:34:25Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,audit-r10-roster,roster-b24-wip,r10-buffer-store
+2026-10-28T05:45:31Z	1	8	r10-cop-partload,r10-learner-default,triage-s6-batch40,audit-r10-roster,r10-buffer-store,r10-dependabot-setuptools
+2026-10-28T05:56:33Z	1	7	r10-cop-partload,r10-learner-default,triage-s6-batch40,audit-r10-roster,r10-buffer-store,fix-r10-buffer-store-pr
diff --git a/dev/programme/delivery/2930.md b/dev/programme/delivery/2930.md
new file mode 100644
index 000000000..8a21350fa
--- /dev/null
+++ b/dev/programme/delivery/2930.md
@@ -0,0 +1 @@
+- [#2930](https://github.com/tvofi/heatpump_optimizer/pull/2930) — **open**, R10-RCA-OWED-UNACTIONED: the root-cause record for tick owed lines that (R10-RCA-OWED-UNACTIONED)
diff --git a/tests/closures.json b/tests/closures.json
index 6063b8d8c..bf5db8477 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3597,6 +3597,7 @@
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
    "tools/audit/seat/orchestrator_tick.py",
+   "tools/audit/seat/owed_unactioned.py",
    "tools/audit/seat/plan_audit.py",
    "tools/audit/seat/plan_page.py",
    "tools/audit/seat/proof_watch.py",
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index c2a5128fe..50448a489 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -702,6 +702,20 @@ sweep's standing-seat liveness step keep them alive.
   roster ref: exit 1 prints one dispatch line and the unowned lines, and a
   run without its `CARRY-SWEEP:` summary is UNREADABLE. Its driver is
   `tick_loop.sh`.
+- `owed_unactioned.py` — says which tick owed lines have outlived a sweep with
+  no live acknowledgement (dev/audit/rca/R10-RCA-OWED-UNACTIONED.md). It reads
+  the board's whole owed family (`-> OWED…`, `REVIEW OWED:`, `DISPATCH:`,
+  `OWNER FLAG:`, `DESIGN-BUILD:`), keys each line on its topic or `#<pr>`, and
+  counts in `--state` the boards each key has stood on. A key standing
+  `--after` (2) sweeps is UNACTIONED unless an `--acks` file holds a live
+  `OWED-ACK <UTC> <key> <id> [ttl=<h>] <reason>` whose id prefixes a sha the
+  key carries now; an acknowledgement lapses after its ttl (default 1 h, at
+  most 12), so a handled line comes back for its handling to be checked, and
+  free queue text covers nothing. When: every sweep, step (5) of
+  `sweep_template.md`. Exit 0 none unactioned, 1 the UNACTIONED block (each
+  with a ready ack line), 2 UNREADABLE: no provenance line, a board older than
+  `--max-board-min`, an owed line it cannot key, an unreadable state.
+  `--self-test` drives it offline.
 - `plan_audit.py` — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the
   `audit-plan` workflow. `ledger` parses each merged PR's
   `## Architecture score` block with the parser `score.py`'s own report
diff --git a/tools/audit/seat/owed_unactioned.py b/tools/audit/seat/owed_unactioned.py
new file mode 100644
index 000000000..edc6ccdaf
--- /dev/null
+++ b/tools/audit/seat/owed_unactioned.py
@@ -0,0 +1,336 @@
+#!/usr/bin/env python3
+"""Say which tick OWED lines have outlived a sweep with no live acknowledgement.
+
+    python3 -I tools/audit/seat/owed_unactioned.py --tick <tick.txt> --state <state.json> \
+        [--acks <file>]... [--after 2] [--max-board-min 20] [--now <ISO>] [--no-write]
+    python3 -I tools/audit/seat/owed_unactioned.py --self-test
+
+WHY THIS EXISTS (dev/audit/rca/R10-RCA-OWED-UNACTIONED.md). The tick prints its
+owed lines level-triggered, every pass, and escalates a stranded handoff by age;
+the sweep read them and still left them standing for hours, because a line the
+orchestrator handled once -- routed to a seat, waited on a named PR, believed the
+relay would move -- prints identically after that handling has failed. Nothing
+asked again. On 2026-10-28 the critical-path handoff r10-orch-beatd (#2916) stood
+1.7 h on `repair=review` while the relay printed HELD-REVIEW on every pass, and
+two handoffs routed to the opener at 10:55Z stood 8 h.
+
+WHAT IT DOES. It reads the tick board's owed family -- every `-> ` line that
+starts `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:` or `DESIGN-BUILD:` --
+and keys each on its obligation: the handoff topic, or `#<pr>`. The state file
+counts the sweeps (distinct boards, by the board's provenance time) each key has
+stood on. A key standing on `--after` sweeps or more is UNACTIONED unless an
+acknowledgement line in an `--acks` file covers it now:
+
+    OWED-ACK <UTC ISO> <key> <id> [ttl=<hours>] <next action; what it waits on>
+
+The id is a prefix of a sha the key's lines carry this board (the ledger's own
+id column for a kind with no sha, `-` for a line with none), so a new tip needs
+a new acknowledgement. An acknowledgement lapses after ttl hours (default 1, at
+most 12, the owner's OWNER FLAG threshold), so a handled line comes back and the
+handling is checked again. Free text in a queue file is not an acknowledgement.
+
+EXIT. 0: no owed key is unactioned. 1: the UNACTIONED block, oldest first, each
+with a ready OWED-ACK line to fill in -- the sweep is not done. 2: cannot say --
+no tick file, no provenance line, a board older than --max-board-min, an owed
+line it cannot key, an unreadable state file -- never a clean zero. A refused
+OWED-ACK line is printed and covers nothing.
+"""
+from __future__ import annotations
+
+import argparse
+import datetime as dt
+import json
+import os
+import re
+import sys
+import tempfile
+
+FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:)")
+BOARD = re.compile(r"^BOARD measured from origin/main at \S+, (\S+)")
+SHA = re.compile(r"\b[0-9a-f]{12,40}\b")
+REF = re.compile(r"\b(?:refs/heads/)?(?:handoff-body|handoff|design)/(\S+)")
+ACK = re.compile(r"OWED-ACK (\S+) (\S+) (\S+)(?: ttl=(\S+))? +(\S.*)$")
+TTL_DEFAULT, TTL_MAX = 1.0, 12.0
+
+
+class Unreadable(Exception):
+    pass
+
+
+def utc(s: str) -> dt.datetime:
+    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
+    if t.tzinfo is None:
+        raise ValueError(f"{s}: no zone")
+    return t.astimezone(dt.timezone.utc)
+
+
+def key_of(line: str) -> "tuple[str, list[str]]":
+    """(key, shas) for one owed-family line; Unreadable when it names no obligation."""
+    body = line[3:]
+    shas = [s[:12] for s in SHA.findall(body)]
+    m = re.match(r"REVIEW OWED: (#\d+)", body)
+    if m:
+        return m.group(1), shas
+    m = re.match(r"OWED handoff: (\S+) ", body)
+    if m:
+        return m.group(1), shas
+    m = re.match(r"OWED: OWED \S+ \S+ (\S+) (\S+)", body)
+    if m:
+        subj = m.group(1)
+        shas = shas or [m.group(2)]  # a kind whose id is no sha (push-stuck: a pid)
+        r = REF.match(subj)
+        return (r.group(1) if r else f"#{subj}" if subj.isdigit()
+                else subj.removeprefix("refs/heads/")), shas
+    m = REF.search(body)
+    if m and re.match(r"(DISPATCH|OWNER FLAG|DESIGN-BUILD): ", body):
+        return m.group(1), shas
+    raise Unreadable(f"an owed line names no topic or pull request: {line[:120]}")
+
+
+def board(text: str) -> "tuple[dt.datetime, dict]":
+    lines = text.splitlines()
+    m = BOARD.match(lines[0]) if lines else None
+    if not m:
+        raise Unreadable("no `BOARD measured from origin/main at <sha>, <UTC>` provenance line")
+    keys: dict = {}
+    for line in lines:
+        if FAMILY.match(line):
+            k, shas = key_of(line)
+            e = keys.setdefault(k, {"shas": [], "lines": []})
+            e["shas"] += [s for s in shas if s not in e["shas"]]
+            e["lines"].append(line)
+    return utc(m.group(1)), keys
+
+
+def acks(texts: list, now: dt.datetime) -> "tuple[dict, list[str]]":
+    """{key: [(sha, expiry, reason)]} live now, and the refused lines."""
+    live, refused = {}, []
+    for name, text in texts:
+        for n, line in enumerate(text.splitlines(), 1):
+            if "OWED-ACK" not in line:
+                continue
+            m = ACK.search(line)
+            why = None
+            if not m:
+                why = "not `OWED-ACK <UTC ISO> <key> <sha> [ttl=<h>] <reason>`"
+            else:
+                try:
+                    at = utc(m.group(1))
+                    ttl = float(m.group(4) or TTL_DEFAULT)
+                except ValueError as e:
+                    at, ttl, why = None, 0.0, f"unparsable time or ttl ({e})"
+                if why is None and not 0 < ttl <= TTL_MAX:
+                    why = f"ttl={m.group(4)} outside (0, {TTL_MAX:g}] hours"
+                if why is None and at > now + dt.timedelta(minutes=5):
+                    why = "stamped ahead of the clock"
+            if why:
+                refused.append(f"REFUSED ack {name}:{n}: {why}")
+                continue
+            exp = at + dt.timedelta(hours=ttl)
+            if exp > now:
+                live.setdefault(m.group(2), []).append((m.group(3), exp, m.group(5)))
+    return live, refused
+
+
+def run(tick: str, state_path: str, ack_texts: list, now: dt.datetime, after: int,
+        max_board_min: float, write: bool, out) -> int:
+    try:
+        when, keys = board(tick)
+    except (Unreadable, ValueError) as e:
+        out(f"UNREADABLE: {e}")
+        return 2
+    age = (now - when).total_seconds() / 60
+    if age > max_board_min:
+        out(f"UNREADABLE: the board is {age:.0f} min old (over {max_board_min:g}); "
+            "a stale board cannot say a line was discharged")
+        return 2
+    try:
+        with open(state_path, encoding="utf-8") as fh:
+            state = json.load(fh)
+        if not isinstance(state.get("keys"), dict):
+            raise ValueError("no `keys` object")
+    except FileNotFoundError:
+        state = {"board": None, "keys": {}}
+    except (OSError, ValueError) as e:
+        out(f"UNREADABLE: state {state_path}: {e}")
+        return 2
+    stamp = when.strftime("%Y-%m-%dT%H:%M:%SZ")
+    fresh = stamp != state.get("board")
+    seen = {}
+    for k in keys:
+        old = state["keys"].get(k)
+        if old is None:
+            seen[k] = {"first": stamp, "sweeps": 1}
+        else:
+            seen[k] = {"first": old["first"], "sweeps": old["sweeps"] + (1 if fresh else 0)}
+    if write:
+        d = os.path.dirname(os.path.abspath(state_path))
+        fd, tmp = tempfile.mkstemp(dir=d, prefix=".owed-unactioned.")
+        with os.fdopen(fd, "w", encoding="utf-8") as fh:
+            json.dump({"board": stamp, "keys": seen}, fh, indent=1, sort_keys=True)
+        os.replace(tmp, state_path)
+    live, refused = acks(ack_texts, now)
+    for r in refused:
+        out(r)
+    acked, bad = [], []
+    for k, s in sorted(seen.items(), key=lambda kv: (kv[1]["first"], kv[0])):
+        ids = keys[k]["shas"]
+        cover = [a for a in live.get(k, []) if (a[0] == "-" and not ids) or any(
+            x.startswith(a[0]) or (len(a[0]) >= 7 and a[0].startswith(x)) for x in ids)]
+        if cover:
+            acked.append((k, max(cover, key=lambda a: a[1])))
+        elif s["sweeps"] >= after:
+            bad.append((k, s))
+    out(f"owed: {len(seen)} key(s) on board {stamp}; {len(acked)} acknowledged, "
+        f"{len(bad)} unactioned (standing {after}+ sweeps with no live OWED-ACK)")
+    for k, (sha, exp, reason) in acked:
+        out(f"  acked {k} {sha} until {exp.strftime('%H:%MZ')}: {reason[:100]}")
+    if not bad:
+        return 0
+    out("UNACTIONED")
+    for k, s in bad:
+        h = (now - utc(s["first"])).total_seconds() / 3600
+        out(f"  {k}  sweeps={s['sweeps']} first={s['first']} ({h:.1f}h)")
+        for line in keys[k]["lines"]:
+            out(f"      {line[:200]}")
+        sha = keys[k]["shas"][0] if keys[k]["shas"] else "-"
+        out(f"      ack: OWED-ACK {now.strftime('%Y-%m-%dT%H:%M:%SZ')} {k} {sha} ttl=1 "
+            "<next action, by whom; what it waits on>")
+    return 1
+
+
+# ------------------------------------------------------------------ self-test
+def self_test() -> int:
+    passed = failed = 0
+
+    def check(name: str, cond: bool) -> None:
+        nonlocal passed, failed
+        passed, failed = passed + bool(cond), failed + (not cond)
+        if not cond:
+            print(f"FAIL {name}")
+
+    t0 = utc("2026-10-28T17:20:00Z")
+
+    def tick(at: dt.datetime, *lines: str) -> str:
+        return "\n".join([f"BOARD measured from origin/main at beb570c817c4, {at.isoformat()}",
+                          "== PRS ==", "-> #2887: mergeable state DIRTY"] + list(lines)) + "\n"
+
+    beatd = ("-> OWED handoff: r10-orch-beatd c991d64cdaef342d282d1a8e991dadc2671f917d 1.6h "
+             "uncovered=1 repair=review -- no PR head carries it")
+    held = ("-> OWED: OWED 2026-10-28T18:57:09Z handoff-held refs/heads/handoff/r10-orch-beatd "
+            "c991d64cdaef342d282d1a8e991dadc2671f917d #2916 REVIEW")
+    disp = ("-> DISPATCH: ? refs/heads/handoff/triage-s7-batch49 40bec0ab6c44 opener (8.9h; "
+            "last attempt 2026-10-28T17:36:08Z,unopened)")
+    review = "-> REVIEW OWED: #2896 5f3a5dd615b5"
+    event = ("-> OWED: OWED 2026-10-28T18:11:39Z verdict-unposted 2920 "
+             "9328902275ba97b94d71f1778cf23f1eb2df031c Fix review: blocked")
+
+    with tempfile.TemporaryDirectory() as d:
+        def go(text, acks_=(), now=None, state="s.json", after=2, write=True):
+            lines: list = []
+            rc = run(text, os.path.join(d, state), [("acks", a) for a in acks_],
+                     now or utc(BOARD.match(text).group(1)) + dt.timedelta(minutes=1),
+                     after, 20, write, lines.append)
+            return rc, "\n".join(lines)
+
+        # keying: one obligation per topic or pull request, whatever the line's shape
+        _, k = board(tick(t0, beatd, held, disp, review, event))
+        check("beatd's two line shapes are one key", set(k) == {"r10-orch-beatd", "triage-s7-batch49",
+                                                                 "#2896", "#2920"})
+        check("the key carries its sha", "c991d64cdaef" in k["r10-orch-beatd"]["shas"])
+        check("a non-owed flagged line is not owed", not any("#2887" in x for x in k))
+        _, k2 = board(tick(t0, "-> OWED: OWED 2026-10-28T00:53:40Z push-stuck fix-r10-diag-ages 98785 STUCK 1641s"))
+        check("a kind with no sha keys on its id column", k2.get("fix-r10-diag-ages", {}).get("shas") == ["98785"])
+
+        # the defect: the same lines on successive boards, nothing acknowledges them
+        rc1, o1 = go(tick(t0, beatd, disp))
+        check("first sweep: new, not yet unactioned", rc1 == 0 and "UNACTIONED" not in o1)
+        rc2, o2 = go(tick(t0 + dt.timedelta(minutes=10), beatd, disp))
+        check("second sweep: unactioned, exit 1", rc2 == 1 and "UNACTIONED" in o2
+              and "r10-orch-beatd  sweeps=2" in o2 and "triage-s7-batch49  sweeps=2" in o2)
+        check("it prints a ready ack line", "ack: OWED-ACK " in o2 and " r10-orch-beatd c991d64cdaef ttl=1" in o2)
+        rc2b, o2b = go(tick(t0 + dt.timedelta(minutes=10), beatd, disp))
+        check("the same board re-read adds no sweep", "sweeps=2" in o2b and "sweeps=3" not in o2b)
+        check("free text in a queue names the topic and covers nothing",
+              go(tick(t0 + dt.timedelta(minutes=20), beatd, disp),
+                 ["- 17:39Z opener done: batch49 refused BAD-DEST; r10-orch-beatd relay updates #2916"])[0] == 1)
+
+        # acknowledgements: live, matching sha, lapsing
+        now = t0 + dt.timedelta(minutes=31)
+        ok = [f"OWED-ACK {(now - dt.timedelta(minutes=5)).isoformat()} r10-orch-beatd c991d64cd "
+              "release #2916 in cloud-handoff-release; reviewer at e09b123f9 finishing",
+              f"OWED-ACK {(now - dt.timedelta(minutes=5)).isoformat()} triage-s7-batch49 40bec0ab6 ttl=2 "
+              "opener re-run after RCA-HEADMOVED carry; opener seat s7"]
+        rc3, o3 = go(tick(t0 + dt.timedelta(minutes=30), beatd, disp), ok, now=now)
+        check("null control: every standing key acknowledged -> exit 0", rc3 == 0 and "2 acknowledged" in o3)
+        later = t0 + dt.timedelta(minutes=95)
+        rc4, o4 = go(tick(t0 + dt.timedelta(minutes=90), beatd, disp), ok, now=later)
+        check("a 1 h ack lapses, a 2 h ack holds", rc4 == 1 and "r10-orch-beatd  sweeps" in o4
+              and "triage-s7-batch49  sweeps" not in o4)
+        newtip = beatd.replace("c991d64cdaef342d282d1a8e991dadc2671f917d", "a" * 40)
+        rc5, _ = go(tick(t0 + dt.timedelta(minutes=40), newtip), ok, now=t0 + dt.timedelta(minutes=41),
+                    state="tip.json", after=1)
+        check("an ack for the old tip does not cover a new tip", rc5 == 1)
+        bad_ack = [f"OWED-ACK {(now + dt.timedelta(hours=1)).isoformat()} r10-orch-beatd c991d64cd later",
+                   f"OWED-ACK {now.isoformat()} r10-orch-beatd c991d64cd ttl=48 park it",
+                   "OWED-ACK r10-orch-beatd soon"]
+        rc6, o6 = go(tick(t0 + dt.timedelta(minutes=30), beatd), bad_ack, now=now,
+                     state="bad.json", after=1)
+        check("future, over-long and malformed acks are refused and cover nothing",
+              rc6 == 1 and o6.count("REFUSED ack") == 3)
+
+        # discharge and the clean board
+        rc7, o7 = go(tick(t0 + dt.timedelta(minutes=100), disp), ok, now=later + dt.timedelta(minutes=6))
+        check("a discharged key leaves the state", rc7 == 0 and "r10-orch-beatd" not in o7)
+        with open(os.path.join(d, "s.json"), encoding="utf-8") as fh:
+            check("state drops it too", "r10-orch-beatd" not in json.load(fh)["keys"])
+        rc8, o8 = go(tick(t0), state="clean.json", after=1)
+        check("null control: an all-clear board exits 0 with 0 keys", rc8 == 0 and "owed: 0 key(s)" in o8)
+
+        # never green by skipping
+        check("no provenance line: exit 2", go("-> OWED handoff: x " + "a" * 40 + "\n", now=t0)[0] == 2)
+        check("a stale board: exit 2", go(tick(t0, beatd), now=t0 + dt.timedelta(minutes=45),
+                                          state="stale.json")[0] == 2)
+        check("an owed line it cannot key: exit 2", go(tick(t0, "-> OWED something new"),
+                                                       state="unk.json")[0] == 2)
+        with open(os.path.join(d, "broken.json"), "w", encoding="utf-8") as fh:
+            fh.write("{")
+        check("an unreadable state: exit 2", go(tick(t0, beatd), state="broken.json")[0] == 2)
+        rc9, _ = go(tick(t0, beatd), state="nowrite.json", write=False)
+        check("--no-write writes nothing", not os.path.exists(os.path.join(d, "nowrite.json")))
+
+    print(f"owed_unactioned self-test: {passed + failed} checks, {failed} failed")
+    return 1 if failed else 0
+
+
+def main(argv: list) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
+    ap.add_argument("--tick")
+    ap.add_argument("--state")
+    ap.add_argument("--acks", action="append", default=[])
+    ap.add_argument("--after", type=int, default=2)
+    ap.add_argument("--max-board-min", type=float, default=20.0)
+    ap.add_argument("--now")
+    ap.add_argument("--no-write", action="store_true")
+    ap.add_argument("--self-test", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    if not a.tick or not a.state or a.after < 1:
+        ap.error("--tick and --state are required, and --after is at least 1")
+    try:
+        with open(a.tick, encoding="utf-8", errors="replace") as fh:
+            tick = fh.read()
+        texts = []
+        for p in a.acks:
+            with open(p, encoding="utf-8", errors="replace") as fh:
+                texts.append((os.path.basename(p), fh.read()))
+    except OSError as e:
+        print(f"UNREADABLE: {e}")
+        return 2
+    now = utc(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
+    return run(tick, a.state, texts, now, a.after, a.max_board_min, not a.no_write, print)
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 6341b938d..5abc54e35 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -62,7 +62,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #201 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), the finished seat's worktrees under {{seat_root}} and its scratch removed, `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}}`, and the plan artifact regenerated with `{{plan_generator}}` and republished at {{plan_artifact}}.
 
-(5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background on `dev/governance/roles/standing-tick.md`, whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Act on the newest actionable lines of {{tick_log}}; the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board.
+(5) Tick watcher. If {{tick_alive}} is missing or older than {{tick_stale_min}} minutes, the tick seat has died: start a new one in the background on `dev/governance/roles/standing-tick.md`, whose prompt is the contents of {{tick_brief}}; it runs `tools/audit/seat/orchestrator_tick.py`. Log the restart in {{seat_ledger}}. Act on the newest actionable lines of {{tick_log}}; the tick only lists, the sweep acts (`tools/audit/seat/INSTRUMENTS.md`, `orchestrator_tick.py`). The `pulse.py` lines step (1b) printed name each consumer whose owed input is waiting on it (opener, verdict router or train, state beat, a standing seat's queue): drive that consumer before the rest of the sweep, and log it in {{seat_ledger}}; `UNREADABLE` is not a clean board. Then run `python3 -I tools/audit/seat/owed_unactioned.py --tick {{tick_log}} --state {{orch_scratch}}/owed-unactioned.json --acks {{seat_ledger}}`: it reads the tick's whole owed family (never a `grep | head` or `tail` of it) and exits 1 on each owed line that has stood two sweeps with no live `OWED-ACK` line. Each such line gets its action this sweep, or an `OWED-ACK` line in {{seat_ledger}} naming its next action and what it waits on; an acknowledgement lapses after its ttl, so the next sweep re-checks the handling. The sweep is not done while it exits 1, and its 2 is `UNREADABLE`, never clean (`dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`).
 
 (6) Verdicts and CI. Read any moved `review/*` or `probe/*` refs and the cloud runs; confirm each verdict at its exact head with `tools/audit/seat/bus.sh confirm` (`dev/governance/roles/nudge.md` step 1). A red required check at an open head goes back to its fixer with the line `tools/audit/seat/failure_logs.sh` prints (`dev/governance/roles/nudge.md` steps 4 and 15).
 

