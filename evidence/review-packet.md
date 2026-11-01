# Review packet #3084
head: 9fb03fc0241a95b2d5dfb72347346fc9a5e129c3
base: e4c9e2016a455d787d3a7604ef88c803c3ba5c70

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=124880989961 skipped
cancel-superseded id=124880994350 queued
prelude id=124880994230 queued
refresh id=124880994400 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh api repos/tvofi/heatpump_optimizer/actions/jobs/124777140994
             gh api: every long flag accepted
  ok         gh pr view 3045
             gh pr view: every long flag accepted
  ok         tests/ci_ratchet.py
             `tests/ci_ratchet.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3084.md b/dev/programme/delivery/3084.md
new file mode 100644
index 000000000..151191a13
--- /dev/null
+++ b/dev/programme/delivery/3084.md
@@ -0,0 +1 @@
+- [#3084](https://github.com/tvofi/heatpump_optimizer/pull/3084) — **open**, triage: s9 batch 100 (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch100.md b/dev/programme/triage/s6-batch100.md
new file mode 100644
index 000000000..f1dd61e95
--- /dev/null
+++ b/dev/programme/triage/s6-batch100.md
@@ -0,0 +1,98 @@
+# Proposal triage, session s9, batch 100 (P355, P356)
+
+The rolling batch after batch 99, which was pushed first and left at its head. Facts were read at
+origin/main `df66556f2`, at `tests / ci-ratchet` job 124777140994 (run 41280712426, main's push
+run at `df66556f2`), and in #3045's body (head `9ef51b821`, open, approved). Both proposals come
+from the #3045 fixer's measurement over about 60 main push runs. The orchestrator s9 sent them by
+message on 2026-11-01.
+
+## P355: run the ci-ratchet's archscore measurement beside its network fetches
+
+Verdict: REJECT.
+
+Source: orchestrator s9, from the #3045 fixer.
+- **What is proposed.** `tests / ci-ratchet` runs its fetch steps before `Grade the ratchet`,
+  which measures the archscore vector (`.github/workflows/tests.yml` lines 2291, 2316 and 2321).
+  Running the measurement beside the fetches would take about 0.45 min off the median critical
+  path, 33.867 down to 33.416.
+
+Instances:
+- **Job 124777140994, the latest at origin/main.** Its step times:
+  - "Gather this run's and the recent window's metrics": 06:52:07-06:52:38, 31 s;
+  - "Fetch the recent push runs' durations": 06:52:38-06:52:46, 8 s;
+  - "Grade the ratchet": 06:52:46-06:53:16, 30 s;
+  - the whole job: 06:52:02-06:53:16, 74 s.
+
+  So the overlap is bounded by the shorter side, about 30 s, which matches the stated 0.45 min.
+- **Who waits on that 30 s.**
+  - The job runs only on a push to main: its `if` is `github.event_name == 'push' &&
+    github.ref == 'refs/heads/main'`. No pull-request run carries it.
+  - The merge train runs `--overlap`, under which `main_green` is log-only: "do not wait on
+    main's CI before a merge" (`merge_train.py` `main_green`, the owner's P7 decision). So no
+    batch merge waits on it.
+  - Only a serial entry after a D merge waits "once main's run on it is green" (`merge_train.py`
+    docstring, step 5). That is one main push run of 40-60 min, of which this is 30 s.
+- **What it would buy on the ratchet.** 0.45 min of `critical_path_minutes` headroom. #3045,
+  open and approved, adds a measured band of 1.3 min on that row (see P356).
+
+Cost:
+- **A workflow edit, so the PR's gate runs `MODE: FULL`** (CLAUDE.md rule 1). That is one full
+  suite on the account's job cap, which is the CI bottleneck now.
+- **A new interface in the gate workflow.** Steps in a job run in sequence, so the overlap needs
+  either a background process that one step starts and a later step waits on, or the fetches
+  moved into `tests/ci_ratchet.py` with threads. Either way it adds a file handoff between the
+  measurement and the grade, and a self-test arm to pin it.
+- No capped file. `tests/ci_budgets.json` is not edited.
+
+Binding: the benefit is 30 s on a push-only job that no merge waits on, plus 0.45 min of ratchet
+headroom that #3045's band already exceeds. Against that are a forced full gate run and a
+cross-step interface in the gate workflow. The trade is marginal, so REJECT. The answer changes
+if a merge path starts waiting on main's push run, for example if `--overlap` is dropped, or if
+`ci-ratchet` grows past a few minutes.
+
+Rule run on the instance: job 124777140994. Under the proposal, "Grade the ratchet" (30 s) would
+overlap "Gather" (31 s), saving about 30 s of a 74 s job on a run whose result no merge reads
+before merging.
+
+## P356: grade the critical-path budget on the median of 40 runs
+
+Verdict: DEFER, to #3045 (R10-HOTFIX-CI-CRITPATH-2, open, approved at `9ef51b821`), which already
+owns this item.
+
+Source: orchestrator s9, from the #3045 fixer. main is green with 0.034 min of headroom and
+flaps on host variance.
+- **What is proposed.** Grade `critical_path_minutes` at the median of 40 push runs instead of 8.
+
+Instances:
+- **Today's grade.** `tests/ci_ratchet.py` grades the median of the newest `PUSH_WINDOW = 8`
+  push runs (line 469; `critical_path_minutes`, line 574) and records at the p90 of a 40-run
+  window (module docstring). The budget is 34.267 (`tests/ci_budgets.json`).
+- **#3045's measurement.** Over 59 push runs (2026-10-30..31), the median is 33.767 and sigma is
+  1.638. Sliding 8-run medians run 32.916..34.575, and the largest |median8 - window median| over
+  145 runs is 1.300. That spread is larger than the headroom, which is the cause of the flap.
+- **#3045's fix**, ordered by the owner under the mandate: `critical_path_minutes_band: 1.3`.
+  `compare()` reports GREW only past budget + band. The band is typed MAX0, so widening it is a
+  raise. Its null control reproduces main's red and then clears it with the band.
+
+Cost:
+- Adopting this proposal as well would change what the row grades, while #3045's band is sized
+  to the 8-run statistic. The two fixes would have to be re-derived together.
+- A 40-run median lags real growth. About half the window must move before the grade does, which
+  at the measured 59 runs over two days is about 16 h. The 8-run median moves in about 4 runs.
+- It is five times the per-run jobs reads in `--gather-runs` (40 run job lists against 8) on
+  every main push.
+
+Binding: the flap is the owned and measured subject of #3045, which is open and approved. A
+second statistic for the same row, before that fix is on main, is unmeasured against it. The
+proposal gives no false-red rate or detection delay for 40-median against 8-median plus the 1.3
+band. What would change the answer:
+1. #3045 merges and main still goes red on `critical_path_minutes` inside its band's measured
+   spread; or
+2. a measurement on the same 145 runs shows that a 40-run median with a narrower band has the
+   same false-red rate and a shorter detection delay than 8-run plus 1.3.
+
+Then it is a carry on #3045's group.
+
+Rule run on the instance: today, main at 0.034 min of headroom on an 8-run median whose sampling
+spread is up to 1.3 min. Under #3045 the same window grades `ok ... band 1.3` (its null control).
+Under this proposal the window would be 40 runs, and its effect is unmeasured.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
