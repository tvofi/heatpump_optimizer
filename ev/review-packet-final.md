# Review packet #3661
head: af7d2813775aa51f817135b7df4edc55fcfa2046
base: b94425b94f0d25a02576e98fa10a8ff324974a0c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133186875338 success
arch-score / arch-score id=133199926036 success
arm id=133186382317 skipped
budget-raise-gate / budget-raise-gate id=133199882587 success
cancel-superseded id=133199960113 success
codeql id=133199953769 skipped
codeql / Analyze (actions) id=133186706982 success
codeql / Analyze (javascript-typescript) id=133186706937 success
codeql / Analyze (python) id=133186707044 success
gate id=133199880858 success
governance id=133199932916 skipped
governance / env-matrix id=133186707404 success
governance / instrument-self-tests id=133186707156 success
governance / policy-docs id=133186707210 success
governance / record id=133186714186 skipped
governance / wave-script id=133186707176 success
hassfest id=133199882320 skipped
hassfest / hassfest id=133186706691 success
kernel-points id=133199882612 skipped
pr-contract id=133199882544 skipped
pr-contract / pr-contract id=133198687679 success
prelude id=133199881371 success
refresh id=133199945740 success
sweep-self id=133200200659 skipped
tests id=133199882202 skipped
tests / arch-instrument id=133187143148 success
tests / briefs id=133186707401 success
tests / browser id=133187142984 success
tests / ci-ratchet id=133198382146 skipped
tests / claims-autofix id=133191906248 skipped
tests / closure-scope id=133186707019 success
tests / closures id=133187143052 success
tests / closures-autofix id=133197208107 skipped
tests / coverage id=133187143022 success
tests / coverage-ratchet id=133198380130 success
tests / fast (3.14) id=133187142971 success
tests / graders-head-copy id=133198380098 success
tests / lane-proofs id=133198380457 success
tests / mutation id=133186707170 success
tests / mutation-autofix id=133187262400 skipped
tests / mutation-pins id=133187261045 skipped
tests / nightly-ha id=133187144767 skipped
tests / nightly-status id=133186707157 failure
tests / replay id=133187145886 skipped
tests / typing id=133187143243 success
validate id=133199881528 skipped
validate / validate-hacs id=133186706704 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded

## carry_audit at the head
NOTE body item dd8248c8: R11-CLOSEOUT-CLEANUP: R11-CLOSEOUT-CLEANUP resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 1 script(s) run, 32 scoped out.
             no segment of this names a program this check knows
  ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 2 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3661.md b/dev/programme/delivery/3661.md
new file mode 100644
index 0000000000..86c436944c
--- /dev/null
+++ b/dev/programme/delivery/3661.md
@@ -0,0 +1 @@
+- [#3661](https://github.com/tvofi/heatpump_optimizer/pull/3661) — **open**, R11-HOTFIX-TICK-SEAT-WINDOW: tick reads SEAT_WINDOW_MIN from owed_watch (R11-HOTFIX-TICK-SEAT-WINDOW)
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 395302934b..f52fe8d93b 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -1720,14 +1720,14 @@ class Tick:
         `source: outside` group G, each `after` edge walked transitively over
         the groups that still gate (roster_lib.gates), prints one line per
         deepest group of a blocking path that no seat ref (SEAT_REFS) has
-        moved inside SEAT_WINDOW_MIN. A path ending in a live seat prints
+        moved inside owed_watch.SEAT_WINDOW_MIN. A path ending in a live seat prints
         nothing; an unreadable ref listing is UNREADABLE, never a clean chain."""
         groups, open_g = rl.groups_of(roster), rl.open_groups(roster)
         outside = [g for g in open_g if open_g[g].get("source") == "outside"]
         seats = self._seats(S, rl, roster, "outside chains") if outside else {}
         if seats is None:
             return
-        window = datetime.timedelta(minutes=SEAT_WINDOW_MIN)
+        window = datetime.timedelta(minutes=owatch.SEAT_WINDOW_MIN)
 
         def idle(gid):
             at = [self._commit_at("origin/" + r) for r in seats.get(gid, [])]

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
