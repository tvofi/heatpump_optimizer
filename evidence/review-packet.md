# Review packet #3203
head: c6c212f7524abfefa1c4590821bad7ea84cd2650
base: d7582ed404a87603bd02fefda610d7ebbe4181e1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126786360935 success
arch-score / arch-score id=126786249034 success
arm id=126785973972 skipped
budget-raise-gate / budget-raise-gate id=126786249090 success
cancel-superseded id=126785976220 success
codeql / Analyze (actions) id=126786249550 success
codeql / Analyze (javascript-typescript) id=126786248915 success
codeql / Analyze (python) id=126786248955 success
governance / delivery-status id=126786249059 success
governance / delivery-status-publish id=126786252045 skipped
governance / env-matrix id=126786248853 in_progress
governance / instrument-self-tests id=126786248934 in_progress
governance / policy-docs id=126786248961 success
governance / record id=126786251689 skipped
governance / wave-script id=126786248932 success
hassfest / hassfest id=126786249315 success
kernel-points id=126786250322 skipped
prelude id=126785976106 in_progress
refresh id=126785975942 success
tests / arch-instrument id=126786577696 success
tests / briefs id=126786248879 success
tests / browser id=126786577709 success
tests / closure-scope id=126786248935 success
tests / closures id=126786577718 success
tests / closures-autofix id=126788249100 skipped
tests / coverage id=126786577600 success
tests / coverage-ratchet id=126787001474 success
tests / fast (3.14) id=126786577445 in_progress
tests / graders-head-copy id=126787001901 success
tests / mutation id=126786248862 success
tests / mutation-autofix id=126786583408 skipped
tests / mutation-pins id=126786583649 skipped
tests / nightly-ha id=126786580678 skipped
tests / nightly-status id=126786248920 failure
tests / replay id=126786581182 skipped
tests / typing id=126786577964 success
validate / validate-hacs id=126786248988 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat d7582ed40...a7b0e93f0ff8e989985688e790cfa52eb87c9f58
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
diff --git a/dev/programme/delivery/3203.md b/dev/programme/delivery/3203.md
new file mode 100644
index 000000000..f1bc32fc7
--- /dev/null
+++ b/dev/programme/delivery/3203.md
@@ -0,0 +1 @@
+- [#3203](https://github.com/tvofi/heatpump_optimizer/pull/3203) — **open**, triage: batch 116, P378 DEFER (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch116.md b/dev/programme/triage/s6-batch116.md
new file mode 100644
index 000000000..ed322ec6a
--- /dev/null
+++ b/dev/programme/triage/s6-batch116.md
@@ -0,0 +1,75 @@
+# Proposal triage, session s10, batch 116 (P378)
+
+The rolling batch after batch 115. Facts were read at origin/main `b8e823699`, at the round's
+roster branch `origin/handoff/audit-r10-roster` (`efd37113a`), from GitHub's pull-request files,
+and in the session's seat ledger and the dispatch seat's fire ledger and handoffs. The owner was
+re-read at roster `a62d10eb0`, after the s11 replan folded R10-TICK-PR-BUCKETS.
+
+## P378: the dispatch seat lists already-fired payloads as fire-owed
+
+Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule). The item is already owned: the
+FIRE-OWED tick level of R10-TICK-LEVELS (the carry opening "Three owed classes", item 3), with the
+payload-file key that the carry citing `s6-batch115.md#P375` applies to it. No carry, no group and
+no policy edit. The answer changes if R10-TICK-LEVELS closes without building the FIRE-OWED level
+with its payload-file arm, or if a false
+fire-owed line holds a pull request that touches `custom_components/`.
+
+Source: the orchestrator s10's message of 2026-11-02, about 20:30Z, a slip from that day's
+sweeps. It proposes one line in `dev/governance/roles/standing-dispatch.md`: before reporting a
+payload fire-owed, check the dispatch seat's fire ledger (`ledger-standin.txt`) for a FIRED line
+naming the payload file.
+
+Instances:
+- **Four false fire-owed reports, each already fired** (the orchestrator's report). Each render
+  is in the seat ledger and each fire is in the fire ledger, 12 to 17 s later:
+  - #3089 r5: rendered 17:29:12Z, `FIRED payload-fix-3089-r5.json` at 17:29:26Z (line 223).
+  - #3177 r1: rendered 18:15:52Z, `FIRED payload-3177-r1.json` at 18:16:04Z (line 224).
+  - #3085 r2: rendered 20:15:14Z, `FIRED payload-3085-r2.json` at 20:15:31Z (line 229).
+  - #3174 r4: rendered 20:24:58Z, `FIRED payload-3174-r4.json` at 20:25:14Z (line 230).
+  - An earlier batch at about 16:26Z, for example `FIRED payload-3085-r1.json` at 16:26:08Z
+    (line 219).
+- **Every one of them is fired by payload filename alone.** Since 2026-11-02T11:10Z the fire
+  ledger writes `FIRED payload-<name>.json` with no PR number or topic (lines 201 to 230); the
+  earlier lines wrote `#<n> r<k>`.
+- **The proposed rule is already in force, and the instances happened under it.** The dispatch
+  seat's session handoff has opened with "RULE AT THE TOP: before listing anything fire-owed,
+  grep ... ledger-standin.txt for a FIRED line by PR number, topic AND the payload filename" in
+  its s10g handoff (written about 16:18Z), its s10h handoff and its current s10i handoff (written
+  about 17:30Z). All four instances above are later than 17:29Z.
+- **No production pull request is held.** From `gh pr view <n> --json files`: #3089
+  (`fix/r10-flow-body-only`, 8 files), #3177 (`fix/triage-s9-batch115`, 3 files), #3085
+  (`fix/r10-closeout-cleanup`, 12 files) and #3174 (`fix/r10-replay-cost-budget`, 2 files)
+  each have 0 files under `custom_components/`.
+- **The mechanised form has a live owner.** On roster `efd37113a` the item sat on
+  R10-TICK-PR-BUCKETS. On roster `a62d10eb0` that group's stage is `absorbed`, and R10-TICK-LEVELS
+  is `in-progress` with `pr: 3200`. Its FIRE-OWED arm is in #3200 at `d7e67e0d7`
+  (`orchestrator_tick.py` line 948), which has not merged.
+  - The carry opening "Three owed classes", item 3, specifies a FIRE-OWED level ("a rendered cloud
+    payload with no fire recorded") with the null control "a payload with a FIRED line prints
+    nothing".
+  - The carry citing `s6-batch115.md#P375` keys a fire on "a payload file for it
+    (`payload-fix-<n>-r<k>.json` or `payload-<n>-r<k>.json`)" and says "Apply the same definition
+    to FIRE-OWED".
+
+Cost:
+- One sentence in a role contract, which is policy: it merges only on the owner's approving
+  review.
+- The sentence would name a session-local file that is not in the tree, so the contract would
+  bind a seat to a path a later round may not have.
+- No capped file is touched by this ruling.
+
+Binding:
+- **Why LOG.** The friction is one extra message round per instance. It holds no pull request
+  that touches `custom_components/`, and no measured gain above 10% is offered.
+- **The proposed text has a measured null.** The same instruction, in the same words, stood at
+  the top of the seat's own handoff while all four instances happened. A second copy of it in the
+  contract changes nothing the first did not.
+- **The owner is the tick level, not the seat.** R10-TICK-LEVELS's FIRE-OWED level computes what
+  is owed from the fire ledger, with the P375 carry's payload-file key and a null control for a
+  fired payload.
+  Once it is built, the dispatch seat's running fire-owed list is redundant; the seat need report
+  only the payload it rendered in that report.
+- **Until it is built**, the session-local stand-in is the orchestrator's: read a dispatch seat's
+  fire-owed line as a claim to check against the fire ledger, as the stand-in `blind_spots.py`
+  FIRE-OWED arm already does. The P375 patch to that stand-in, adding the payload-file key, covers
+  this arm too.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
