# Review packet #3211
head: 1fca63cb1665af349fd51c57820150a280ddba09
base: 783d8dc72811ab75ae4ffca367456f44896f47d3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=126901520255 skipped
cancel-superseded id=126901543218 queued
prelude id=126901543829 queued
refresh id=126901543599 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e...5996dcf63390265662bf2f9fe48ad527252d5bef
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 0 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3211.md b/dev/programme/delivery/3211.md
new file mode 100644
index 000000000..24579ab34
--- /dev/null
+++ b/dev/programme/delivery/3211.md
@@ -0,0 +1 @@
+- [#3211](https://github.com/tvofi/heatpump_optimizer/pull/3211) — **open**, triage: batch 121, P386 ACCEPT (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch121.md b/dev/programme/triage/s6-batch121.md
new file mode 100644
index 000000000..6eb7cdec5
--- /dev/null
+++ b/dev/programme/triage/s6-batch121.md
@@ -0,0 +1,124 @@
+# Proposal triage, session s12, batch 121 (P386)
+
+The rolling batch after batch 120. Facts were read at origin/main `2a9cd3476`, at the round's roster
+branch `origin/handoff/audit-r10-roster`, in the session's pull-request logs (`pr/*/p1.log`,
+`pr/upd-*.log`), in `s7/plan-live.json` and in the seat ledger.
+
+**Numbering.** The queue files this as P377, which already names `s6-batch115.md#P377`, with a different
+subject. P384 and P385 are in batch 120, not yet on main. This entry takes the next free number.
+
+## P386: a fixer's prepr is not repeated at open or update (filed as P377)
+
+Verdict: ACCEPT. The owner decided whether (tvofi, 2026-11-04), so this entry rules routing and form
+only. Route: R10-HANDOFF-PATH, whose carries already hold the item, moved to the front of the queue with
+its part 1 cut to this reuse alone, and no new group. Form: a receipt the fixer's own prepr writes, a
+fail-closed verdict in `app_push.sh` beside `--recarry` and `--row-only`, and the merged-tree checks kept.
+
+Source: the owner's directive, in the orchestrator's queue line of 2026-11-04T20:38:44Z: heavy pre-PR
+scripts run once, on code that can affect them, and a fixer's run is not repeated at open or update. It
+asks where R10-OPENER-REUSE's carries went, what #3089 and `app_push --row-only` already deliver, and
+which group takes the rest, keeping the checks a merged tree truly needs.
+
+Instances:
+- **Where the carries went: all to R10-HANDOFF-PATH.** On the roster, R10-OPENER-REUSE is `absorbed`
+  (`merged PR-3164 3905069f`), and its reuse carries are marked `[moved: R10-HANDOFF-PATH]`. They stand there
+  as carry 3 (the rule, from the plan-regain study) and carry 4 (`tests/structure.py` on the merged tree,
+  from #3052's red). That group is `not-started`, with `after: []`, 11 carries and size M. The plan starts it
+  at 2026-11-05T19:50Z, in batch 27 of 57 (`s7/plan-live.json`), so unmoved it waits about a day. It is not
+  on the critical path.
+- **What is delivered.**
+
+  | path | what it spares | where |
+  |---|---|---|
+  | `update_pr.sh`: main merged only when DIRTY or `merge-tree` conflicts | a main-only merge on an update | #3089, merged 20:08:34Z on 2026-11-04; carry 9 is answered by it |
+  | BODY-ONLY: the head does not move, so nothing is pushed | any prepr on a body repair | #3089 |
+  | `--row-only`: exactly one row commit on the live head | prepr on a row push | `app_push.sh` lines 107 to 122 |
+  | open's second push (p2) asks `--row-only` | one of an open's two prepr runs | `open_pr.sh` lines 7 and 132 (P53) |
+  | `--recarry`: a train's clean merge | prepr on a recarry | `train.log`: `RECARRY: prepr SKIPPED` |
+
+- **The gap, in two lines.**
+  - An update that merges code: `update_pr.sh` line 128 asks `--row-only` only when `HEAD^@` is the live
+    head, and its header says "A head that merges new code, or main, never asks".
+  - An open's first push: `open_pr.sh` line 118 passes no flag, and line 103 merges main.
+  - No receipt exists to reuse. `prepr.sh` prints `PRE-PR: <sha> <digest>` (line 4248) and writes it nowhere,
+    `body_push.sh` runs only `--body-check`, and the only record is prose in a body.
+- **The cost today, measured.** Every `pr/*/p1.log` and `pr/upd-*.log` modified in the last 24 h at 20:50Z
+  with a `heavy slot taken` line, from take time (`expires_at` less the 1800 s lease) to the log's mtime: 45
+  runs, 538 min of slot. The directive's 4 are among them, and their figures are partial: #3195 29 min (ended `rc=-15`),
+  and the machinery part 2 open 33 min, #3197 11 min and #3085 13 min, all three still running when read.
+  Carry 3's earlier figure was 59 runs and 3021 min in 24 h. The figure bounds the benefit; the share that
+  would reuse is not measured, because no receipt exists yet.
+- **Earlier rulings this overrides or binds.**
+  - `s6-batch51.md#P250` DEFER and the group dropped on 2026-10-31 (R10-FLY-OPEN-PREPR-REUSE, ledger 21:33:05Z,
+    closure-keyed skip rate 1 of 10 opens) both keyed the skip to main not moving under a closure. That key
+    is why it fired on almost nothing (`s6-batch95.md#P346`: 0 of 4 code opens). The owner's rule replaces the
+    key: code a fixer ran is not re-run because main moved, since main's commits passed on main and CI gates the
+    merged head (`prepr.sh` line 15: the PRE-PR line is a claim, and CI's re-execution is the proof).
+  - `#P346` still binds what stays: the open-time `ci predict` caught a real red at 18:34Z on 2026-10-31, against
+    the main the open merged. #3195's `unpinned sites` refusal is the same family.
+- **What a merged tree needs, from the step list of a passing run** (`upd-fix-r10-rca-gate-stale.log`).
+  - Keyed to the code alone, and dropped on a receipt: `policy_lint`, `mutants`, `rules_sync`, `fragments`,
+    `hooks`, `codeowners_gap`, `brief_lint`, `field coverage`, `agreement lane`, `register check`,
+    `pinned graders`, `self-test`, `wave-script`, `diff mutants`, `no-copies`, `throwaway git`.
+  - Keyed to main, the body or the merge, and kept: `merge-base`, `no version`, `claim files`, `claims hygiene`,
+    `ci predict`, `unpinned sites`, `layout guard`, `ref privacy`, `temp paths`, `preflight`, `pr-body`, `figures`,
+    `carry`, `ancestry reds`, and `tests/structure.py` on the merged tree (carry 4: 24 s, and it would have caught #3052).
+  - This split is a reading of each step's input, not a measured one. The fixer pins it, with the kept steps'
+    wall time.
+- **Rule run: the verdict on the four named instances.** Read at `2a9cd3476` (`git merge-base --is-ancestor`,
+  `git merge-tree --write-tree`, and the body at each `handoff-body`):
+
+  | instance | code | to the live head | main merge | body names a passing prepr at this code | verdict |
+  |---|---|---|---|---|---|
+  | #3197 update | `bb3bcda5d` | live is in the code | clean, 0 behind | yes, "rerun on this head" | reuse |
+  | #3195 update | `e0a411f21` | diverged, a clean merge | clean, 48 behind | yes, "at this head, rc=0" | reuse |
+  | #3085 update | `5e6d43ae1` | live is in the code | clean, 68 behind | no, it names `92b159d7` | full prepr, the fail-closed arm |
+  | machinery part 2 open | `ee19e1f5b` | no pull request yet | clean, 72 behind | no line naming an rc | full prepr, the fail-closed arm |
+
+  Read from prose, since no receipt exists. With the receipt, the last two turn on whether the fixer's run was
+  at that sha.
+  - **Null controls, by the rule:** a sha with no receipt runs full; a conflicted merge runs full.
+
+Cost:
+- About 70 lines: 3 in `tools/pr/prepr.sh` (the receipt), about 8 in `tools/audit/seat/body_push.sh`, about 40 in
+  `tools/pr/app_push.sh` (`reuse_verdict`, mirroring `recarry_verdict` and `row_only_verdict`), 2 each in
+  `open_pr.sh` and `update_pr.sh`, and self-test arms in each. No new file and no new check.
+- `prepr.sh` and `app_push.sh` are outside the group's `files`, so the route needs `set-files`. R10-PREPR-CAP also
+  edits `prepr.sh` at a different seam (slot and scope).
+- None of these is a policy file, so none has a `policy_lint.mjs --budgets` row. `fixer.md` is unchanged: its
+  prepr-before-handoff duty is what the receipt records.
+- The risk accepted: a red the skipped steps would have found at open is found by CI, at the cost of a CI round
+  and a repair. That is the owner's trade.
+
+Binding:
+- **Why this group, and not a new one.** It already owns `update_pr.sh`, `open_pr.sh` and carries 3 and 4, so a new
+  group would duplicate them. What it needs is order, not a home.
+- **Why part 1 is cut.** Its other carries (one checkout per pull request, exit 75, the retry, `open_driver` repairs)
+  are separate edits, and bundling them would keep this behind review rounds it does not need.
+- **For the orchestrator, by `roster_edit.py`, at front of queue:**
+  - `append-carry` the text below;
+  - `set-files R10-HANDOFF-PATH`, adding `tools/pr/app_push.sh`, `tools/pr/prepr.sh` and
+    `tools/audit/seat/body_push.sh`;
+  - answer carry 9 with #3089's merge;
+  - dispatch part 1 ahead of the plan's batch 27.
+- **Carry text for R10-HANDOFF-PATH, part 1, front of queue (owner directive 2026-11-04):** a fixer's prepr is not
+  repeated at open or update. Part 1 is this carry with carries 3 and 4, and no other; the rest is part 2. Carry 3's
+  "PRE-PR rc=0 line" is built here, and carry 9 is answered by #3089's merge. (1) Receipt: on rc=0, `prepr.sh` run
+  with a body writes `<HEAD sha> <tree sha>` to a file in the git dir. `body_push.sh` reads it and, when its sha is
+  the handoff's code head, adds a `Prepr: <sha> <tree>` trailer to the `handoff-body/<topic>` commit. `--body-check`
+  writes none, and a run with a skip flag other than `PREPR_SKIP_CLOSURES` writes none. (2) Verdict: `app_push.sh
+  --reuse`, beside `recarry_verdict` and `row_only_verdict`, failing closed, is taken only when the body ref's
+  trailer names the code sha C, C's tree is the trailer's, and HEAD differs from a clean automatic merge of C with
+  the live head and origin/main only by the PR's own row: no resolution, no other commit. Anything else runs the full
+  prepr. One `app_push: REUSE:` line names the path and why. `update_pr.sh` and `open_pr.sh` p1 ask for it, and a
+  head the verdict refuses runs the full prepr as today. (3) What it still runs, with no heavy slot: `row_only_checks`,
+  and the steps keyed to main, the body or the merge (`no version`, `claim files`, `claims hygiene`, `ci predict`,
+  `unpinned sites`, `layout guard`, `ref privacy`, `temp paths`, `preflight`, `figures`, `ancestry reds`), plus `tests/structure.py`
+  on the merged tree, the `merge-tree` result where the head did not merge main. Check each step's input before
+  dropping it, and report the kept steps' wall time at the group's merge base. Do not key the skip to main not moving
+  under a closure: that key fired on 0 of 4 code opens (`s6-batch95.md#P346`). Fixture arms: (a) an update to a
+  receipted sha with a clean merge takes no heavy slot; (b) a sha with no receipt, or with a trailer naming another sha,
+  runs the full prepr (the null control); (c) a conflict resolved in the merge runs the full prepr; (d) a clean merge
+  whose `tests/structure.py` fails is refused; (e) a `ci predict` red on the merged main is refused (#3195's and the
+  2026-10-31 18:34Z class); (f) a tree differing from the trailer's runs the full prepr. Mutants: dropping the tree
+  comparison fails (f), and dropping `tests/structure.py` fails (d). triage: dev/programme/triage/s6-batch121.md#P386

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
