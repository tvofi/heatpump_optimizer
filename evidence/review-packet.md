# Review packet #2931
head: 5a1a60c87abe79629f4ab647c2d1b72b62e4a788
base: b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123064731456 skipped
cancel-superseded id=123064733443 queued
prelude id=123064733351 queued
refresh id=123064733664 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 94d0a804: R10-TRAIN-OVERLAP-GRADE: R10-TRAIN-OVERLAP-GRADE resolved on origin/handoff/audit-r10-roster
NOTE body item 31a6d394: R10-FLOW-WIP
NOTE body item 5b4a5068: R10-ORCH-LEDGER
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tools/audit/seat/merge_train.py
             `tools/audit/seat/merge_train.py` is in the tree at this head
  unverified git ls-tree origin/main dev/audit/config/
             `git ls-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 1 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2931.md b/dev/programme/delivery/2931.md
new file mode 100644
index 000000000..0e27c44f5
--- /dev/null
+++ b/dev/programme/delivery/2931.md
@@ -0,0 +1 @@
+- [#2931](https://github.com/tvofi/heatpump_optimizer/pull/2931) — **open**, triage s7 batch 56: rule P267 (V181) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch56.md b/dev/programme/triage/s6-batch56.md
new file mode 100644
index 000000000..3bd589f7b
--- /dev/null
+++ b/dev/programme/triage/s6-batch56.md
@@ -0,0 +1,171 @@
+# Proposal triage, session s7, batch 56 (P267)
+
+One entry: V181, filed 2026-10-28T19:43:00Z and quoted from `proposals.md` as it stands. The
+owner directed it: when the account's concurrent-job limit binds, pause the CI of the
+lowest-priority PR so that runners are freed for main and the train head. That makes the outcome
+the owner's. This ruling sets the shape and the owner group. Facts were read at origin/main
+`b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa` and at the live roster
+`origin/handoff/audit-r10-roster` `be898eaef54a6ba1f996b4ca9b11c6f93ce94ea4`.
+
+## P267: when the train head or main waits for a runner, pause the lowest-priority PR's CI and rerun it later
+
+Verdict: ACCEPT, narrowed, into **R10-TRAIN-OVERLAP-GRADE**, which owns
+`tools/audit/seat/merge_train.py` and is at stage `carries-open`. It does not go to P266's
+canceller.
+
+Source: `proposals.md` V181 (the orchestrator, owner-directed, 2026-10-28T19:43:00Z), with the owner's three amendments. 19:44:50Z: the priority order is a configurable, self-tested, tracked setting with a documented default, and every instrument that schedules or cancels CI reads it. 19:47:33Z: critical-path and hotfix PRs jump any queue (train, review, fixer, CI) above all but a main push, and instrument PRs are ordered among themselves by measured hours saved. 19:48:44Z: production-code PRs go before instrument PRs, unless the instrument PR is critical or saves at least 12 h, and 12 h is a configurable default.
+
+Instances:
+- **Only the train knows the priority order.** The order the owner set is main push, then the
+  train head (critical path first), then train queue order, then CP PRs, then the rest. Train
+  position exists only in `merge_train.py`. `cancel_superseded.py` (P266) knows a branch and its
+  live head, and nothing about the queue, so putting priority there would give one file two
+  rules.
+- **The train's own overlap creates the contention.** `--overlap` recarries the queue up front
+  (`merge_train.py` line 172 and its recarry phase near line 488). Every queued entry's CI then
+  starts at once and competes for runners with the head's.
+- **The train already re-runs runs by API.** `unstale` (line 2452) POSTs
+  `actions/runs/<id>/rerun` once per stale run and logs the run id. The pause-and-rerun path adds
+  one more arm to code that already does this.
+- **The P266 sweep cannot fight it.** P266 never cancels a run at a live head, and it never
+  reruns anything. A paused run is at its PR's live head, so the sweep leaves it alone.
+
+Carry (narrowed shape):
+1. **Detect.** While `wait_ci` (line 1142) waits on the head, or on main after a landing, it reads
+   the jobs of those runs on its existing poll. "The limit binds" means a head or main job has
+   been `queued` for at least 5 min. GitHub exposes no account limit, so a job's queued age is the
+   only reading.
+2. **Choose one victim per pass**, from the lowest priority up:
+   - the lowest `ci_priority.rank()` first (item 7), so the default pauses
+     `instrument` before `instrument-major`, before `production`;
+   - never a class in `never_pause` (main push, CP and hotfix, train head);
+   - never queue position 2;
+   - never a run at another head (the P266 sweep owns those).
+3. **Pause.** POST `actions/runs/<id>/cancel` for the victim's active runs at its live head. Then
+   record `{pr, head, run_ids, paused_at}` in a `paused.json` beside the train's queue state, and
+   log `PAUSE #<n> at <head8>: runs <ids> for <head-or-main>`.
+4. **Resume.** When the head and main have no job queued, or when the train exits by any path
+   (`finally`, including `Stop`), POST `actions/runs/<id>/rerun-failed-jobs` for each recorded
+   run whose PR head is unchanged. That reruns only the cancelled and failed jobs and keeps the
+   jobs that had finished. A record whose head moved is dropped, because its new push runs anyway.
+   Log `RESUME #<n>`.
+5. **Crash safety.** Every train start first resumes any `paused.json` record left by a killed
+   run, before its own queue, and logs it. A paused record older than 60 min with no train running
+   is the obligations ledger's to report (R10-ORCH-LEDGER, P265's `owed` bucket reason "paused CI
+   never resumed"). It goes there as a second carry, because this group does not edit
+   `orchestrator_tick.py`.
+6. **Rate.** At most one pause per 5 min, and the train's existing poll cadence, with no new
+   polling loop.
+7. **The setting (the owner's amendments).** One tracked file, `dev/audit/config/ci_priority.json`,
+   holds the order for every queue: train, review dispatch, fixer dispatch and CI. It sits in the
+   directory that already holds `scopes.json` and `rotation.json`. Its schema and defaults:
+   - `order` lists the classes highest first. The default is the owner's: `["main-push",
+     "cp-hotfix", "train-head", "production", "instrument-major", "instrument"]`.
+   - `major_savings_h` is `12`. An instrument PR whose measured savings reach it is
+     `instrument-major`.
+   - `tiebreak` orders within a class. The default is `["cp-rank", "savings-desc",
+     "train-position", "age"]`: critical-path rank, then measured hours saved (highest first,
+     which is how instrument PRs order among themselves), then train queue position, then PR
+     age.
+   - `never_pause` defaults to `["main-push", "cp-hotfix", "train-head"]`.
+   - `never_cancel` defaults to `["main-push", "cp-hotfix"]`. It applies to every pause. P266's
+     superseded-run sweep honours only `main-push` from it, because a superseded run is dead work
+     at a head no one reads; the owner can widen that (DECISION-OWED below).
+   - `hotfix_prefixes` defaults to `["R10-HOTFIX-"]`.
+   - `savings_h` maps a group to `{hours, source}`. The source is the ruling or cost test that
+     measured it, for example `dev/programme/triage/<batch>.md#P<n>`. A missing entry is 0.
+
+   **Classification is mechanical**:
+   - `cp-hotfix` is a group in `roster_lib.critical_path_groups` or a name with a hotfix prefix.
+   - `production` is a PR whose three-dot diff touches `custom_components/`.
+   - `instrument-major` and `instrument` are the remaining PRs, split by `savings_h` against
+     `major_savings_h`.
+   - `train-head` is the train's entry at position 1.
+   - `main-push` is a `push` run on main.
+
+   **The reader.** `tools/audit/seat/ci_priority.py` (`load()`, `classify(pr, train, roster)`,
+   `rank(prs)` and `--self-test`) is the file's only parser. It **refuses** with rc 2, naming the
+   key, any config that does one of these:
+   - drops `main-push` or `cp-hotfix` from `never_pause`;
+   - puts anything above `main-push`;
+   - names an unknown class, or omits a known one;
+   - has a `savings_h` entry without a `source`.
+
+   The owner's floor, "never cancel CP or main", therefore cannot be edited away.
+
+   **Who reads it.** Every instrument that schedules or cancels CI, or orders a queue:
+   - this group's pause, resume and queue order;
+   - R10-FLY-CANCEL-SWEEP's `sweep` (P266), for `never_cancel`;
+   - R10-FLOW-WIP's ranked dispatch list (the `next` subcommand in its brief);
+   - R10-ORCH-LEDGER's owed-PR ordering (P265's "critical-path PRs first").
+
+   R10-FLOW-WIP and R10-ORCH-LEDGER each get a carry saying so. This group adds the file and the reader. Classify both (a measured closure or `tests/closure.py`
+   INERT) so that `tests/entities.py` passes. If another reader's group lands first, it adds them to
+   exactly this schema, and the rest reuse them.
+8. **Controls:**
+   - head job queued 6 min with the tail entry's runs active: the tail is cancelled and recorded;
+   - the head's queue clears: `rerun-failed-jobs` runs on the tail's ids;
+   - a CP tail entry is skipped and the next victim is taken;
+   - `main` and queue position 2 are never chosen;
+   - a record whose head moved is dropped without a rerun;
+   - a train that stops mid-pause resumes in `finally`;
+   - mutant: dropping the CP guard pauses the CP fixture, and fails;
+   - with the default file, a production PR is paused after an instrument PR saving 3 h, and
+     before an instrument PR saving 14 h; a hotfix PR is never paused;
+   - setting `major_savings_h` to 20 makes the 14 h instrument PR be paused before the
+     production PR;
+   - a config that drops `cp-hotfix` from `never_pause`, or has a `savings_h` entry with no
+     `source`, is refused rc 2 by the reader;
+   - null: a head with no queued job pauses nothing, and `rank()` over the default file
+     reproduces the owner's order.
+
+Not carried:
+- Pausing in `cancel_superseded.py`, for the reason in the first instance.
+- A full `rerun` instead of `rerun-failed-jobs`. That discards finished green jobs.
+- Limiting `--overlap`'s recarry depth instead of pausing. That would prevent rather than pause,
+  and the owner directed the pause. It remains a cheaper complement if the PAUSE lines show the
+  tail paused on most landings.
+
+Cost: about 80-120 lines and eight self-test arms in `merge_train.py` (5831 lines), plus the config file and a reader of about 80-100 lines with its own self-test. The three other readers each add a call, in their own groups. Each pause costs one cancel and one rerun per run, and the victim's CI is delayed by
+the head's queue time.
+
+Binding: the owner directs the outcome. The shape puts priority in the only file that knows the
+queue, and it resumes on every exit path. It loses no finished jobs. A crash is resumed at the next
+train start. The benefit is not measured today, because nothing records how long a head waits for a
+runner. The PAUSE and RESUME lines are that measurement from the first landing on.
+
+### Owed to the owner from P267
+
+- P266's sweep cancels superseded runs (dead work at a head nobody reads) even on CP and hotfix
+  PRs. This ruling reads the owner's "never cancel CP or main CI" as a rule about pausing live-head
+  runs. If the owner means superseded runs as well, `never_cancel` applies to the sweep in full.
+  That is a one-key change in the setting, not new code.
+
+## Three archived review findings, checked before routing (no carry owed)
+
+The orchestrator asked for each to go as a carry to its owning group. Each was read from its
+archive tag and checked against origin/main `b6f6ceca4` and the roster above. All three are
+already resolved in the tree, so routing any of them would hand a builder landed work. That is the
+`carry-stale` class review/2545 itself blocked on.
+
+- **review/2528** (`archive/review-2528` `103da8f7b`; #2528 merged as `f0724675f`). The block was
+  carry-missing: prepr's foreground heavy steps 3-3h, routed to #201, had no owner. The carry did
+  land, in R10-FLOW-JIDOKA's brief: "Carry from #2528 (R10-PREPR-CAP): tools/pr/prepr.sh steps 3
+  to 3h run heavy work in the foreground ..." (roster `edit-brief` `2ce054264`, 2026-10-22).
+  JIDOKA delivered it as `1b9a86266` ("heavy steps reaped"), and is `done` (#2853). On main,
+  `heavy_run` (`tools/pr/prepr.sh:767-779`) runs each heavy step in the background under a
+  watchdog that kills its process group when prepr dies. `carry-201.json` still does not cite
+  #2528, but the work has an owner and has landed. Disposition: resolved.
+- **review/2545** (`archive/review-2545` `728c633ef`; #2545 merged as `f35a5a373`). The block was
+  carry-stale: the record handed the one-shot OWED keying to R10-ORCH-MACHINERY after `b38c6431a`
+  had landed it. The merged record is repaired. `dev/audit/rca/N-orphaned-handoff.md:48` reads
+  "**Landed at the merge base: `b38c6431a`**", and line 55 reads "The one-shot keying and the
+  replay are therefore closed". No roster carry contains the stale instruction ("Key each event
+  on its PR"). Disposition: resolved.
+- **review/2577** (`archive/review-2577` `16ed57ce7`; #2577 merged as `b980e2fa0`). The block was
+  surviving mutants: an explicit roster ref was silently replaced by the default, and the
+  `--group` CLI's `--head`/`--roster-ref` pass-through was unpinned. Both are now pinned in
+  `tools/audit/seat/cloud_dispatch.py`'s self-test: "an explicit roster ref is read, not the
+  round's roster branch" (line 535), "the --group CLI passes --head and --roster-ref through"
+  (line 544), and a second-clone re-dispatch (line 585). The mutants were not re-driven here. The
+  checks name exactly the two survivors. Disposition: resolved.

