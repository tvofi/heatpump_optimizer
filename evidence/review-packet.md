# Review packet #2921
head: e42df200774f19af6805f6a7fa2912a9318af328
base: beb570c817c4efcae0d5f6f4bba52f3383baf8db

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=122989836092 skipped
cancel-superseded id=122989839316 queued
prelude id=122989839728 queued
refresh id=122989839915 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         gh api rate_limit
             gh api: every long flag accepted

FIGURES: 1 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2921.md b/dev/programme/delivery/2921.md
new file mode 100644
index 000000000..88b83c4f6
--- /dev/null
+++ b/dev/programme/delivery/2921.md
@@ -0,0 +1 @@
+- [#2921](https://github.com/tvofi/heatpump_optimizer/pull/2921) — **open**, triage s7 batch 50: rule P248 (V162) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch50.md b/dev/programme/triage/s6-batch50.md
new file mode 100644
index 000000000..302dd9dc8
--- /dev/null
+++ b/dev/programme/triage/s6-batch50.md
@@ -0,0 +1,56 @@
+# Proposal triage, session s7, batch 50 (P248)
+
+One entry: V162, filed by the orchestrator s10's sweep at 2026-10-28T09:55Z, quoted from
+`proposals.md` as it stands. Facts were read at origin/main `0b8f8b585`.
+
+## P248: one shared poller caches PR and check-run state, and seats and the sweep read the cache instead of the REST API
+
+Verdict: DEFER. The local standing pollers belong to **R10-ORCH-BEATD**: its one supervised beat
+replaces the tick, dispatch and roster seats with jobs, and runs the CI and proof waits as
+`kind:"watch"` jobs with 60 s floors (design note §3, §6 (c)5). The quota line the proposal pairs
+with it is already in the tree.
+
+What would change the answer: a second exhaustion, with the consumer that drew the bucket named,
+after BEATD's arm (c) is live. Until a consumer is attributed, a cache has no measured target.
+
+Source: `proposals.md` V162 (orchestrator s10 sweep, 2026-10-28T09:55Z).
+
+Instances:
+- **One verified exhaustion.** The seat ledger at 09:57Z (merge s8) reads "GitHub REST bucket
+  exhausted until 10:02Z (shared token), poll now one GraphQL list/pass". The merge seat degraded
+  to GraphQL, as the filing says.
+- **One unverified possible earlier instance.** The seat ledger on 2026-10-26T05:09Z reads "s46
+  stopped on rate-limit red". It names no bucket, and the installation token's bucket is the
+  recorded cause of that class (R10-RCA-INSTALL-RATELIMIT, R10-RCA-RATELIMIT-RECUR).
+- **No attribution.** No log on this host names which consumer spent the 5000. The filing's
+  "about 10 local and cloud seats each polling every 5 min" is an estimate.
+- **The present rate is a third of the bucket.** At 10:40:58Z, `gh api rate_limit` (which does not
+  count against core) read core 494 used, 4506 remaining, with reset at 11:02:51Z. That is about
+  1,350 calls an hour, 27 % of the bucket. GraphQL read 200 of 5000.
+- **The quota line exists.** `tools/audit/seat/orchestrator_tick.py` lines 1277-1287 read
+  `rate_limit` every pass and flag `API quota low: <remaining>/<limit>` below `RATE_FLOOR = 0.2`
+  (line 159). The self-test pins it (lines 3120-3136).
+- **The tick's own cost is measured** in its docstring (lines 93-97): 67 calls at 27 open PRs and
+  84 at 21, so roughly 30 per pass at today's 7 open PRs and 12 passes an hour.
+- **Spent-bucket handling exists.** `tools/audit/seat/gh_read.py` (lines 18-26) re-reads no sooner
+  than a spent bucket's `x-ratelimit-reset`, and refuses at once when that wait exceeds its
+  settle, instead of sleeping out the hour.
+- **One duplicate reader is out of tree.** The orchestrator's own `orch_sweep.sh` runs `gh api
+  --paginate --slurp .../commits/$sha/check-runs` per open PR (its line 205), and the board it
+  reports already holds those reads. That half is the orchestrator's script, as P230 and P236
+  ruled for the same file, not a tree change.
+
+Cost of the cache as filed:
+- **A new daemon and a cache format.** The readers to convert: `orchestrator_tick.py` (24 GitHub
+  call sites), `merge_train.py` (113), `proof_watch.py` (6), `ci-watch.sh` (5), and the cloud seats,
+  which share the token from another host and cannot read a local file.
+- **A correctness risk.** The train grades the newest check-run per name at the head it merges
+  (V122). A cached read up to 5 min old there is a stale-green merge risk that
+  `--match-head-commit` does not cover, because that flag pins the sha, not the conclusions read.
+- **The standing-poller part is BEATD's.** It is the seam BEATD is building, so a second poller
+  beside it is a second owner of the same schedule.
+
+Binding: one stall of about 40 minutes in this round, with its consumer unattributed, against a
+daemon over 150 call sites with a stale-read risk at merge. The mechanism that removes duplicate
+standing polls is already designed in BEATD, and the quota line already ships. A clear gain is not
+shown, so the ruling is DEFER to the owning group, with the attribution that would change it.

