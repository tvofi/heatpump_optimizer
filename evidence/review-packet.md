# Review packet #2906
head: 59bf9622a8ad38e5b7673a2a4835892a05e8a5ef
base: beb570c817c4efcae0d5f6f4bba52f3383baf8db

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=123044641038 success
arch-score / arch-score id=123044352100 success
arm id=123042302634 skipped
budget-raise-gate / budget-raise-gate id=123044352113 success
cancel-superseded id=123042316509 success
codeql / Analyze (actions) id=123044351691 success
codeql / Analyze (javascript-typescript) id=123044351717 success
codeql / Analyze (python) id=123044351668 success
governance / delivery-status id=123044352035 success
governance / delivery-status-publish id=123044354619 skipped
governance / env-matrix id=123044351886 in_progress
governance / instrument-self-tests id=123044351813 in_progress
governance / policy-docs id=123044351798 success
governance / record id=123044353855 skipped
governance / wave-script id=123044351769 success
hassfest / hassfest id=123044351875 success
kernel-points id=123044355848 skipped
prelude id=123042316222 success
refresh id=123042316540 success
tests / arch-instrument id=123045875679 queued
tests / briefs id=123044351956 success
tests / browser id=123045875534 in_progress
tests / closure-scope id=123044351761 success
tests / closures id=123045875615 queued
tests / coverage id=123045875400 in_progress
tests / fast (3.14) id=123045875473 in_progress
tests / mutation id=123044351762 success
tests / mutation-autofix id=123045055208 skipped
tests / mutation-pins id=123045054569 skipped
tests / nightly-ha id=123045878669 skipped
tests / nightly-status id=123044352050 success
tests / replay id=123045877750 skipped
tests / typing id=123045875588 in_progress
validate / validate-hacs id=123044351859 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 43ed4eeb: R10-FLOW-BOARD
NOTE body item 4ae3a4ea: dismissed:the orchestrator runs handoff_push.sh on the pushed refs
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git log edd7e0e14e08279d0ddc53ec4fcc983570edf12a --since=2026-10-01T00:00:00Z --no-merges --format=%s -- tests/closures.json | wc -l
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git log refs/pull/2883/head --no-merges --format='%h %s' -- tests/closures.json
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 0 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2906.md b/dev/programme/delivery/2906.md
new file mode 100644
index 000000000..a6a8ab22b
--- /dev/null
+++ b/dev/programme/delivery/2906.md
@@ -0,0 +1 @@
+- [#2906](https://github.com/tvofi/heatpump_optimizer/pull/2906) — **open**, triage s8 batch 47: rule P235 (V149) (triage-s8-batch47)
diff --git a/dev/programme/triage/s6-batch47.md b/dev/programme/triage/s6-batch47.md
new file mode 100644
index 000000000..07954d3fd
--- /dev/null
+++ b/dev/programme/triage/s6-batch47.md
@@ -0,0 +1,54 @@
+# Proposal triage, session s8, batch 47 (P235)
+
+One entry: V149, written by the orchestrator s8 on 2026-10-28 from fixer s8's root-cause
+note on #2883, quoted from `proposals.md` as it stands. Every other id in `proposals.md` up to
+V148 has a ruling on `origin/main` (batches 35-44) or in batches 45 (#2900, P227-P231) and 46
+(#2902, P232-P234). Facts read at origin/main `edd7e0e14`; roster at `origin/main`'s
+`dev/programme/rosters/wave-r10-groups.json`.
+
+## P235: a self-test's argv path is a closure read that only CI's recording sees
+
+Verdict: DEFER -- owned by the red-check root-cause route on #2883 (**R10-FLOW-BOARD**,
+`resume.stage` `in-progress`): `defect-root-cause.md`'s second trigger, answered in that pull
+request's body and by its own root-cause seat. The triage contract keeps such a countermeasure
+on its route: "A defect countermeasure policy already requires (a root-cause countermeasure, a
+carry for a red check, a finding's fix) is not a proposal and keeps its route"
+(`proposal-triage.md`). What would change the answer: that seat's cost test recording that no
+countermeasure is worth building, *and* a further instance on another pull request; the class
+would then be a measured process proposal with no owner, and comes back here.
+
+Source: `proposals.md` V149 (fixer s8 (#2883) SEAT-OWED root-cause, routed by orchestrator s8,
+2026-10-28).
+
+Instances: one verified; the filing counts two, both on #2883.
+- `git log refs/pull/2883/head --no-merges -- tests/closures.json`: `28b0fa0f3` "closures:
+  entities.py reads the two roster paths roster_lib.blob_at's self-test puts on argv (#2883
+  review 3)" -- a CI-only `tests / closures` red, repaired in review round 3.
+- The filing's other instance (#2883's earlier `INERT READS UNDER-APPROXIMATED: tests/entities.py:
+  tools/audit/merge_throughput.py`) was repaired in `d218ef378`, which edits `tests/closure.py`
+  (`git log refs/pull/2883/head -S'merge_throughput.py' -- tests/closure.py tests/closures.json`);
+  nothing in that commit shows it was the argv arm, so it is not counted here.
+- Programme-wide: of `git log edd7e0e14e08279d0ddc53ec4fcc983570edf12a --since=2026-10-01T00:00:00Z
+  --no-merges -- tests/closures.json` (314 commits; a fixed commit and a fixed instant, since a bare
+  date takes the current time of day and the count moved with the clock), none names an argv or command-line read in its subject (`grep -i 'argv\|command
+  line'`); the closures repairs of the month are INERT READS, which `ci_predict --apply-inert`
+  already writes before the push.
+- The mechanism is as filed: `tests/closure.py:1221-1225` (`for argv in spawned:`) adds every
+  existing repo path on a child's command line to the script's reads, and
+  `tools/pr/ci_predict.py:795` prints its green line with the caveat "(a data-file read is not
+  seen)".
+
+Cost: a new recording arm in `ci_predict.py` or `prepr.sh` (a hot file; R10-FLOW-JIDOKA lists it)
+that runs each changed file's self-test under the closure recorder and diffs its reads against
+`tests/closures.json`, with its self-test and a mutant; the filer measures 3.9 s per changed
+self-test at run time. An existing, costlier route already covers the case on demand:
+`PREPR_RECORD_CLOSURES=1` records the scoped closures on a non-Linux seat (`prepr.sh:672-675`),
+and Python lanes record soundly on Darwin through `sys.addaudithook` (`ci-autofix.md`); it was
+made opt-in by `2b84db687` because it costs 10-25 minutes per handoff.
+
+Binding: route, then frequency. The filing is a root-cause note on a red check, so the cause,
+the process state and the cheaper detector's cost test belong to a root-cause seat beside
+#2883's fix (`root-cause.md`), which can name a countermeasure or record that none pays; a triage
+ACCEPT here would decide that seat's answer before it is measured. On the numbers alone the trade
+is not yet clear either: one verified red round in a month of 314 closures commits, against a new
+arm in a hot instrument.

