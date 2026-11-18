# Review packet #3608
head: 731ceaa3d3505006973cef6b213a84cda4569acc
base: 5825e1346c14eecace5c87c046558774145a94dc

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=134901388143 skipped
cancel-superseded id=134901474754 queued
prelude id=134901475155 queued
refresh id=134901474187 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/seat/record_row.py --row-numbers --plan-file <plan.json>
             `tools/audit/seat/record_row.py` is in the tree at this head
  ok         python3 tools/audit/seat/record_row.py --enumerate --repo tvofi/heatpump_optimizer --since ee9e23372c^
             `tools/audit/seat/record_row.py` is in the tree at this head
  unverified git diff --stat origin/main...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head

FIGURES: 3 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 9371c9e6a3a76f37fe522501881285df1df89099)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 9371c9e6a3a76f37fe522501881285df1df89099
Fix review: blocked 9371c9e6a3a76f37fe522501881285df1df89099 merge-resolution: the main merge 9371c9e6 unioned main's merged rows into the branch's, leaving dev/programme/delivery/3451.md, 3521.md and 3593.md two lines each for one PR (record_row.py: each row file is exactly one line); take main's line so the PR's own diff drops those three files

bus-nonce: 55bc8b2f120e431e3215ecc49715139d

## Delta diff: git diff 9371c9e6a3a76f37fe522501881285df1df89099 731ceaa3d3505006973cef6b213a84cda4569acc
diff --git a/dev/programme/delivery/3451.md b/dev/programme/delivery/3451.md
index 951aab5b3a..6065b92353 100644
--- a/dev/programme/delivery/3451.md
+++ b/dev/programme/delivery/3451.md
@@ -1,2 +1 @@
-- [#3451](https://github.com/tvofi/heatpump_optimizer/pull/3451) — **merged `a39627d`**, R10-PROCESS-SLIM (part 2): r10 process slim p2.
 - [#3451](https://github.com/tvofi/heatpump_optimizer/pull/3451) — **merged `a39627d`**, R10-PROCESS-SLIM (part 2): r10 process slim p2 (R10-PROCESS-SLIM).
diff --git a/dev/programme/delivery/3521.md b/dev/programme/delivery/3521.md
index 613c754686..430ba160d9 100644
--- a/dev/programme/delivery/3521.md
+++ b/dev/programme/delivery/3521.md
@@ -1,2 +1 @@
-- [#3521](https://github.com/tvofi/heatpump_optimizer/pull/3521) — **merged `dc46b12`**, R10-OUTSIDE-CONTRIBUTOR-CYCLE (part 2): r10 outside contributor cycle p2.
 - [#3521](https://github.com/tvofi/heatpump_optimizer/pull/3521) — **merged `dc46b12`**, R10-OUTSIDE-CONTRIBUTOR-CYCLE (part 2): r10 outside contributor cycle p2 (R10-OUTSIDE-CONTRIBUTOR-CYCLE).
diff --git a/dev/programme/delivery/3593.md b/dev/programme/delivery/3593.md
index fcc3005fa6..11144b5cfc 100644
--- a/dev/programme/delivery/3593.md
+++ b/dev/programme/delivery/3593.md
@@ -1,2 +1 @@
-- [#3593](https://github.com/tvofi/heatpump_optimizer/pull/3593) — **merged `b046b22`**, R10-COP-LEARNER-DRAW-FLOOR: r10 cop learner draw floor.
 - [#3593](https://github.com/tvofi/heatpump_optimizer/pull/3593) — **merged `b046b22`**, R10-COP-LEARNER-DRAW-FLOOR: r10 cop learner draw floor (R10-COP-LEARNER-DRAW-FLOOR).

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
