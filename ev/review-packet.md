# Review packet #3887
head: fb86f2f77a59eaf6760397fc779f187816beef42
base: 3210fcd7334af9a870a8a7c23322fcaead7e14eb

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=138958080862 success
arch-score / arch-score id=138969764538 success
arm id=138957526986 skipped
budget-raise-gate / budget-raise-gate id=138969745344 success
cancel-superseded id=138969774706 success
codeql id=138969759513 skipped
codeql / Analyze (actions) id=138957809940 success
codeql / Analyze (javascript-typescript) id=138957809978 success
codeql / Analyze (python) id=138957809933 success
gate id=138969717720 success
governance id=138969739456 skipped
governance / env-matrix id=138957809918 success
governance / instrument-self-tests id=138957809884 success
governance / policy-docs id=138957809896 success
governance / record id=138957811836 skipped
governance / wave-script id=138957809931 success
hassfest id=138969718468 skipped
hassfest / hassfest id=138957809607 success
kernel-points id=138969777201 skipped
pr-contract id=138969719746 skipped
pr-contract / pr-contract id=138968199832 success
prelude id=138969761368 success
refresh id=138969717409 success
sweep-self id=138970114941 skipped
tests id=138969718833 skipped
tests / arch-instrument id=138958179854 success
tests / briefs id=138957809840 success
tests / browser id=138958179907 success
tests / ci-ratchet id=138968197749 skipped
tests / claims-autofix id=138962818446 skipped
tests / closure-scope id=138957809985 success
tests / closures id=138958180060 success
tests / closures-autofix id=138968197394 skipped
tests / coverage id=138958179970 success
tests / coverage-ratchet id=138964363596 success
tests / fast (3.14) id=138958179909 success
tests / graders-head-copy id=138964363614 success
tests / lane-proofs id=138964363655 success
tests / mutation id=138957809714 success
tests / mutation-autofix id=138958294942 skipped
tests / mutation-pins id=138958294122 skipped
tests / nightly-ha id=138958181596 skipped
tests / nightly-status id=138957810088 failure
tests / replay id=138958182320 skipped
tests / typing id=138958179812 success
validate id=138969775335 skipped
validate / validate-hacs id=138957809648 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 92b36fa715..ad173d469f 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -275,7 +275,12 @@ jobs:
     # request whose every changed file is product (prelude.machinery).
     if: inputs.machinery != 'false'
     runs-on: ubuntu-latest
-    # 30 minutes. Run in line, this job's steps reached it: two main runs
+    # 45 minutes on a pull request (P-R11-SELFTEST-TIMEOUT). A full-scope
+    # run, which a gate-file diff makes (all 128 steps), took 1783 s green on
+    # #3868 at 2ac9d407. On #3880 at 29187b1e it was cancelled at the old 30,
+    # at 1812 s and 1814 s, with no step hanging; the same work ran in 1292 s
+    # on 2026-11-23. The old 30 came from this history. Run in line, this
+    # job's steps reached it: two main runs
     # were cancelled there and its last four successful ones finished inside
     # its final 90 s, mostly in five self-tests (prepr.sh's, beatd.py's, and
     # pr_args.sh's once alone and once each through open_pr.sh and
@@ -295,9 +300,12 @@ jobs:
     # that misses what it read (`drift`), so a wrong closure turns main red
     # within one merge. The rule, its fail-closed arms and its blind spots
     # are tools/ci/selftest_scope.py's docstring.
-    # A push traces every step and folds the traces, so it gets 90
-    # (r11-hotfix-main-selftest-red). Over main's eleven ci.yml push runs on
-    # 2026-11-15 (b046b22d to 66865be3) the job finished in 34.5 to 52.9
+    # A push traces every step and folds the traces, so it gets 120
+    # (P-R11-SELFTEST-TIMEOUT). Of main's last seven completed push attempts
+    # to 2026-11-25, three were cancelled at the old 90 (5416-5418 s:
+    # 2f4e32c2, 3153a635 attempt 1, 8531d607) and the rest finished in 2958
+    # to 4331 s. The 90 came from this history (r11-hotfix-main-selftest-red).
+    # Over main's eleven ci.yml push runs on 2026-11-15 (b046b22d to 66865be3) the job finished in 34.5 to 52.9
     # minutes or was cancelled at 60; each cancelled one had reached the
     # mutant step at 57.2 to 59.8 minutes, which with the mutant and drift
     # steps' own spread (1.0-1.4 and 4.3-6.0, flat across runs) projects to
@@ -307,7 +315,7 @@ jobs:
     # drift check and the selftest-closures artifact per shard. Re-derive,
     # never carry: list the job in main's ci.yml push runs, duration =
     # completed_at - started_at, and the mutant step's started_at.
-    timeout-minutes: ${{ github.event_name == 'push' && 90 || 30 }}
+    timeout-minutes: ${{ github.event_name == 'push' && 120 || 45 }}
     env:
       HPO_JOB_GRADES: nothing
       SELFTEST_TRACE: ${{ github.event_name == 'push' && '1' || '' }}
diff --git a/dev/programme/delivery/3887.md b/dev/programme/delivery/3887.md
new file mode 100644
index 0000000000..41e3c62453
--- /dev/null
+++ b/dev/programme/delivery/3887.md
@@ -0,0 +1 @@
+- [#3887](https://github.com/tvofi/heatpump_optimizer/pull/3887) — **open**, ci: instrument-self-tests job cap 30->45 min on pull requests, 90->120 on push (R11-HOTFIX-SELFTEST-TIMEOUT)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
