# Review packet #3213
head: a01e980f0aa5290276a8d9951471863db33470af
base: b3cd1628886cc5821606206dfea7b4abbf2c171e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=126907684324 skipped
cancel-superseded id=126907690113 queued
prelude id=126907690415 queued
refresh id=126907690277 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat 783d8dc72811ab75ae4ffca367456f44896f47d3...7f56ffb03e46c8adadaf08bc3575c3a9648a445d
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
diff --git a/dev/programme/delivery/3213.md b/dev/programme/delivery/3213.md
new file mode 100644
index 000000000..a019c1d6c
--- /dev/null
+++ b/dev/programme/delivery/3213.md
@@ -0,0 +1 @@
+- [#3213](https://github.com/tvofi/heatpump_optimizer/pull/3213) — **open**, triage: batch 123, P388 ACCEPT (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch123.md b/dev/programme/triage/s6-batch123.md
new file mode 100644
index 000000000..9a4354580
--- /dev/null
+++ b/dev/programme/triage/s6-batch123.md
@@ -0,0 +1,42 @@
+# Proposal triage, session s12, batch 123 (P388)
+
+The rolling batch after batch 122. Facts were read at origin/main, at the round's roster branch
+`origin/handoff/audit-r10-roster`, and in the live train log (`train/current.log`), with no API read.
+
+## P388: a pre-flight park cured at the same verdict cannot rejoin the live train
+
+Verdict: ACCEPT, already owned. R10-TRAIN-MERGE-LOOP carry 3 holds this item, so no new group; one carry widens its instances and
+replaces the proposal's form. Do not add a class to `READMIT_SAME_VERDICT` alone: the fix re-runs the pre-flight read at the add.
+
+Source: the orchestrator's queue line of 2026-11-04T21:09:35Z: a batch PARK for a cause outside the head is recorded as a skip at that
+verdict, so `train.sh add` answers ALREADY after the cause is cured at the same head. It proposes treating a policy or carry park as
+environment-class when its rule now passes.
+
+Instances:
+- **The code.** `already_held` (`merge_train.py`) holds a skip at the same verdict unless its class is in `READMIT_SAME_VERDICT`, which is `HOLDER` and
+  `BRANCH_POLICY`. `Train.preflight` gives a park a class only at step `recarry`, so a `policy` or `findings` park has none.
+- **Same-verdict refusals in `train/current.log`,** each `ALREADY` line matched to the entry's previous `PARK` or `SKIP` line, by distinct pull request and verdict:
+
+  | pull request, verdict | preceding line | re-read at the add would decide it? |
+  |---|---|---|
+  | #3000 `9cb49191` | PARK policy | yes |
+  | #3059 `ffec33d8` | PARK policy | yes |
+  | #3051 `72ea40aa` | PARK policy | yes |
+  | #3065 `1ac45d87` | PARK policy | yes |
+  | #3200 `c46a9c6a` | PARK policy | yes, this filing |
+  | #3074 `dafcc575` | PARK findings | yes, carry 3's instance |
+  | #3091 `64564359` | SKIP ci | no, not a park: out of this ruling |
+  | #3065 `9e7b016f` | SKIP ci | no, not a park: out of this ruling |
+  | #3174 `558c54a0` | SKIP recarry | no, not a park: out of this ruling |
+
+  That is 6 of 9. Whether each of the 6 had been cured when it was re-added is not in the log. The queue line says #3200 was. #3185 is parked at
+  `findings` in the log, but its only ALREADY line reads "spooled", so it is not an instance of this refusal so far.
+- **The cost.** The entry waits for the train to end, or takes a needless new head and a re-review. Train pid 38222, holding #3200, had run 4 h 37 min when read (`ps`), which bounds one wait.
+  The log has no timestamps, so the other waits are not measured. This is enough to confirm an already-owned S item, not to move it up the plan.
+- **Why a class alone is wrong.** `admit_add` has no `findings` rule. With `policy` and `findings` in `READMIT_SAME_VERDICT`, an uncured `findings` park would print ADDED and re-park at the next batch. Under a mandate id `admit_add`'s `policy` rule also passes without the approval. `PreFlight.entry` is the read that parked it, so it is the read that can say the cause is gone, for any park step, with no list of steps to keep.
+
+Cost: an estimated 15 to 30 lines in `merge_train.py` and self-test arms in one existing S group, not started, plan slot 24. One `PreFlight.entry` per same-verdict re-add, a handful of `gh` and git reads, paid only then. `merge_train.py` is not a policy file, so it has no `policy_lint.mjs --budgets` row. No standing cost, no new file, no new check.
+
+Binding:
+- **Carry on R10-TRAIN-MERGE-LOOP:** Widens carry 3 and sets its form. Same-verdict re-adds refused after a pre-flight park in `train/current.log`: `policy` on #3000, #3059, #3051, #3065 at `1ac45d87` and #3200; `findings` on #3074. In `train_add`, when the entry's skip is a pre-flight park at this verdict, run `queue_pre_flight.PreFlight.entry` under the same construction `Train.preflight` uses: PASS admits it, and anything else logs `ADD REFUSED #<pr> <step>: <why>`, rc 1, never ADDED. Do not add these parks to `READMIT_SAME_VERDICT` alone: `admit_add` has no `findings` rule. Record the park so `already_held` can tell it from a `ci` or `merge` skip, which stay held at the same verdict, and keep `train_add` and the drain on the one predicate (`s6-batch32.md#P189`), so the drain does not drop what the add admitted. Arms: a cured `policy` park and a cured `findings` park each rejoin at the same verdict and reach the next batch; the same parks uncured are refused, with no spool line (control); a `SKIP ci` at the same verdict stays ALREADY (null); a park at a new verdict behaves as today. Mutant: dropping the re-read fails the uncured arm. triage: dev/programme/triage/s6-batch123.md#P388
+- **Plan slot unchanged.** Moving the group up needs a measured wait, not the count above. The workaround stays a fresh add after the train ends.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
