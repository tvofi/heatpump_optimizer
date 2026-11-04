# Review packet #3202
head: 71b40615a67c4a54ded67a9ddd3d96ebdf9f666f
base: d7582ed404a87603bd02fefda610d7ebbe4181e1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=126737645839 success
arch-score / arch-score id=126737319242 success
arm id=126736350356 skipped
budget-raise-gate / budget-raise-gate id=126737319514 queued
cancel-superseded id=126736290312 queued
codeql / Analyze (actions) id=126737318976 success
codeql / Analyze (javascript-typescript) id=126737319011 success
codeql / Analyze (python) id=126737319038 success
governance / delivery-status id=126737319356 queued
governance / delivery-status-publish id=126737321626 skipped
governance / env-matrix id=126737319540 queued
governance / instrument-self-tests id=126737319257 queued
governance / policy-docs id=126737319179 queued
governance / record id=126737321223 skipped
governance / wave-script id=126737319322 queued
hassfest / hassfest id=126737319175 queued
kernel-points id=126737321609 skipped
prelude id=126736289852 success
refresh id=126736290639 queued
tests / briefs id=126737319107 queued
tests / closure-scope id=126737319124 queued
tests / mutation id=126737319060 queued
tests / nightly-status id=126737319046 queued
validate / validate-hacs id=126737319407 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat d7582ed40...01df01e4881c6b939bc08a9c58874020acb3350e
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
diff --git a/dev/programme/delivery/3202.md b/dev/programme/delivery/3202.md
new file mode 100644
index 000000000..69a524bda
--- /dev/null
+++ b/dev/programme/delivery/3202.md
@@ -0,0 +1 @@
+- [#3202](https://github.com/tvofi/heatpump_optimizer/pull/3202) — **open**, triage: batch 117, P379 DEFER, P380 REJECT, P381 ACCEPT (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch117.md b/dev/programme/triage/s6-batch117.md
new file mode 100644
index 000000000..c70c6ab93
--- /dev/null
+++ b/dev/programme/triage/s6-batch117.md
@@ -0,0 +1,182 @@
+# Proposal triage, session s11, batch 117 (P379 to P381)
+
+The rolling batch after batch 116. Facts were read at origin/main `d7582ed40`, at the round's
+roster branch `origin/handoff/audit-r10-roster` (`9bc39aede`), in the merge train's log
+(`~/.local/state/hpo/merge_train/train.log`) and in the session's event log.
+
+**Numbering.** The queue (`s7/triage-queue-s7.txt`, lines 53 to 55) files these as P372, P373 and
+P374. Those numbers already name rulings on main: `s6-batch114.md#P372` and `s6-batch115.md#P373`,
+`#P374`, with different subjects. P375 to P377 are in batch 115. P378 is in batch 116, which exists
+only on the local branch `triage/s9-batch116` (`df0c264cc`). These entries take the next free
+numbers, and each title names the number it was filed under.
+
+## P379: a red-main hotfix takes the ordinary path (filed as P372)
+
+Verdict: DEFER. The CI-priority half is owned by R10-CI-PRIORITY-PAUSE. The prepr half has an
+unmeasured benefit, and the route it asks for already exists for the one retry the filer
+classified. The answer changes on the run log's four retries classified by failing step, showing
+at least two that were neither a body refusal nor a closures step, on a hotfix whose brief named
+`--body-check`.
+
+Source: the orchestrator's queue line of 2026-11-04T16:45:50Z, citing the fixer's run log
+`cse_01MwNjEDW8chsA76YepFuCtb`. It proposes a hotfix path: one prepr reused across body-only edits,
+and CI priority ahead of the queue.
+
+Instances:
+- **R10-HOTFIX-CI-CRITPATH-4, the one instance.**
+  - `tests / ci-ratchet` failed at main `8e90d8144` at 11:44:14Z (`gh api
+    commits/8e90d8144/check-runs`).
+  - #3201 was created at 15:10:08Z (`gh pr list --search 'CRITPATH-4 in:title'`). That is 3 h 26 m,
+    against the filer's "4 h", which this seat could not locate a start for.
+  - Its commits run from 12:11:40Z to 14:10:49Z (`gh pr view 3201 --json commits`), and the row
+    commit is at 15:10:15Z.
+  - The bot's `ci: re-record closures` `abf21ae34` is at 15:51:57Z.
+  - **Not read:** the run log is a cloud session's and this seat has no tool for it. "13 min per
+    retry", "4 retries" and "18 min x3" are the filer's figures.
+- **Rule on the filer's one classified retry, the roster carry line: a route already exists.**
+  `tools/pr/prepr.sh --body-check <body.md>` runs step 7 alone (`prepr.sh` line 21; the entry is at
+  line 1621). The check that refuses a dead carry marker is in that step (line 1028, and line 2860:
+  "--body-check's carry step"). It takes no full prepr.
+- **Rule on the closure re-records: a route already exists, and the local recording bought
+  nothing.** `brief-critpath4.txt` line 3 already says `PREPR_SKIP_CLOSURES=1`. The head still took
+  the bot's closures commit. Whether the three 18-minute runs were the seat's or CI's needs the
+  run log.
+- **Rule on the recarry: a reuse already exists.** `train.log` for #3192 reads `RECARRY: prepr
+  SKIPPED: HEAD 6946e9d7 is the clean merge of the live head 1f8ca9d9 and origin/main's 3583448e,
+  and the body is the live one`.
+- **CI priority has an owner.** R10-CI-PRIORITY-PAUSE, stage `not-started`, after R10-TICK-LEVELS,
+  owns the tier module and the train's pause and resume (roster `carry`, P267 and P268). Its
+  tiers already place a hotfix ahead of the queue. The stand-in `s11/ci_priority.py` ran on
+  #3201's behalf from 16:24:31Z (`s11/ci_priority.log`, 6 acts).
+- **Frequency.** The roster holds five CI-red hotfix groups in the round: R10-HOTFIX-BATCH-ERREXIT,
+  -UUTILS-SLEEP, -CI-CRITPATH-3, -RECORD-ATTRIB and -CI-CRITPATH-4.
+
+Cost:
+- A distinct hotfix route through `tools/pr/prepr.sh` would add a branch to a hot file, plus a rule
+  for when a head qualifies. Skipping checks on the path that repairs a red main is the least
+  affordable place to lose a prediction: `brief-critpath4.txt` records that "a scoped gate hid a
+  red on #3180".
+- Bound on the benefit, from the filer's figures: at most 3 x 13 min of retries and 3 x 18 min of
+  closures, 93 min per instance, before removing what the existing routes already answer.
+- No capped file is touched by this ruling.
+
+Binding: an unmeasured benefit is DEFER (`proposal-triage.md`). No roster op. The next hotfix brief
+names `tools/pr/prepr.sh --body-check` for a body-only refusal, which is brief text and not a
+proposal.
+
+## P380: classify main's red by whether a queue entry's diff can reach it (filed as P373)
+
+Verdict: REJECT. The binding cost is new classification code in `merge_train.py`, 7454 lines and
+a hot file, against a refusal that does not occur on the train's default flags: 0 instances in the
+whole log. The answer changes on a `nothing more lands` line from a default-flag train, or on a
+batch proof reddened by a red it cannot reach.
+
+Source: the orchestrator's queue line of 2026-11-04T16:45:50Z. It reads "the train's red-main
+refusal plus --overlap one-car route is the only way through", and proposes classifying main's
+red in admission.
+
+Instances:
+- **The refusal does not fire.** `grep -c 'nothing more lands' train.log` reads 0. `grep -cE 'is
+  (RED|not green) .*logs it and does not wait' train.log` reads 14, every red-main line in the log
+  since 2026-10-16. `main_green` is log-only under `--overlap` (`merge_train.py` line 2889), and
+  `train.sh` sets `--overlap` unless `--no-overlap` is passed (`train.sh` lines 33 and 90).
+- **The instance itself, rule run on it.** At 16:36Z the train logged `OVERLAP: main at
+  8e90d8144331 is RED (gate) before admission; --overlap logs it and does not wait`, then `PRE-FLIGHT:
+  1 of 1 admitted` and `#3194 MERGED 3583448e`. So a red main admitted the one car that was
+  queued. The next batch read `PRE-FLIGHT: 8 of 8 admitted` and formed its proof, which is
+  serial or multi-car by file class and not by main's colour.
+- **A ci-ratchet red cannot reach an entry.** The job's condition is `github.event_name == 'push'
+  && github.ref == 'refs/heads/main'` (`.github/workflows/tests.yml` lines 2265 to 2267). It runs
+  on no pull-request head and no batch proof, so the reach classifier would answer a question the
+  workflow already answers.
+- **What did hold main.** First-parent main has no merge from `8e90d8144` (11:03Z) to `3583448e1`
+  (16:36Z). The log shows `TRAIN_RC=1 end=2026-11-04T11:04:39Z` and the next `train.sh` start at
+  16:36Z. No train ran in those 5 h 31 m, so the gap is not a train refusal.
+- **Not settled at this ruling.** Proof `batch/20261104-163602-b2-1` was still pending (`poll 3,
+  t+484s, concluded: 0/1`), so a multi-car proof over this red is not yet evidenced. A red proof
+  there would be the answer-changing instance.
+
+Cost: the classifier needs the closure read at admission, a planted-red arm and a null control in
+a self-test on `merge_train.py`. The proof's attribution step (`merge_train.py` line 137) already
+drops an entry by closure. No capped file is touched by this ruling.
+
+Binding: `orchestrator.md`'s merge section already rules a failure the diff cannot reach as not
+that diff's. Nothing to build, no roster op.
+
+## P381: false owed lines: BODY-AHEAD, RED-UNOWNED, audit-coverage (filed as P374)
+
+Verdict: ACCEPT, narrowed to one carry on R10-TICK-LEVELS: the tracked BODY-AHEAD arm must have
+a way to clear without a head move. The refire, the stand-in's RED-UNOWNED and the audit-coverage
+lines are the orchestrator's own operations below, with no group and no check.
+
+Source: the orchestrator's queue line of 2026-11-04T16:45:50Z.
+
+Instances:
+- **The refire is one defect in the wake loop, and it is not in any predicate.** `s9/wake.sh` and
+  `s11/wake-copy.sh` hold `nw=$(grep -vxF -f $BS $BS.new 2>/dev/null || cat $BS.new)`. `grep -v`
+  exits 1 when it selects nothing, which is exactly when nothing is new, so `|| cat` prints the
+  whole list. Rule run in a scratch directory: unchanged list prints `a b`, one new line prints
+  `c`. With `if [ -f $BS ]; then grep -vxF -f $BS $BS.new; else cat $BS.new; fi`, the unchanged list
+  prints nothing, one new line prints `c`, and an absent list prints all (the null control).
+  Effect: `s9/events.txt` has 59 blind-spot lines on 2026-11-04, of 12 distinct texts.
+  `RED-UNOWNED #3091` has 27 and `BODY-AHEAD #3089` has 13.
+- **BODY-AHEAD #3089, the predicate.** `handoff-body/r10-flow-body-only` `ad7f27a7f` is at 12:19:15Z.
+  Head `98beb50fd` is at 11:35:16Z and contains the code handoff `39e9abd50` (`merge-base
+  --is-ancestor`, rc 0). `body_patch.sh` does not move a head, by design, so the line stood from
+  12:32:35Z to 16:27:18Z and ended only when the train's recarry moved the head to `ecf4ef3fe`.
+- **Rule on the tracked arm in #3200 at `d7e67e0d7`.** `orchestrator_tick.py` lines 903 to 913 owe
+  when the body ref is younger than the head and the code handoff is in the head. It reads nothing
+  about whether the body was applied, so its own remedy, `body_patch.sh`, cannot clear it.
+- **The stand-in's comparison is not the fix.** `blind_spots.py` compares the ref's `BODY.md` to the
+  live body, whitespace-normalised. Rule run on four open pull requests: #3089, #3181, #3193 and
+  #3085 all read unequal (for example #3085 at 22248 against 22240 characters), since the push path rewrites
+  `## Head` (`handoff_push.sh` header). It would fire on an applied body too.
+- **RED-UNOWNED, the stand-in only.** `blind_spots.py` joins every `gate` run's conclusion and tests
+  for `failure`, so an old failure beside a queued rerun reads red. The tracked arm in #3200 reads
+  `self.latest(runs)` through `judge` (line 1090), where pending outranks red, so it needs no
+  carry. **The queued-rerun shape is not reproduced on an instance:** #3197's two runs are both
+  `completed failure`, so its line was true when last read, and #3091's state at 14:37:57Z can no
+  longer be read.
+- **DESIGN-BUILD for audit coverage.** `design/r10-audit-coverage` is not the group id
+  R10-AUDIT-COVERAGE-ENDGAME, so `group_for_branch` returns None and the stage reads as not
+  dispatched. `s6-batch93.md#P333` already refused widening that match. #3149 merged at 03:41:59Z on
+  11-02, and only a time-limited OWED-ACK has answered the line since (`unact.txt` line 9).
+- **seat-no-return for audit coverage.** `dispatch/fixer-r10-audit-coverage-endgame` `c4e4ba510` is at
+  19:18:06Z on 11-02, after #3149's merge, and no return ref is newer (`handoff/` is at 21:42:36Z on
+  11-01). The arm is right by its own rule: this ref is a dispatch written after the work merged. Its
+  48 h window ends it at 19:18Z on 11-04 (`cloud_relay.sh` line 596).
+
+Rule run for the carry, on the instances: with a disposition at `ad7f27a7f`, #3089 prints no
+BODY-AHEAD at `98beb50fd`. A later body ref at a new sha prints again, because the repair is new.
+This is a reading of the predicate, to be pinned by the fixture arms; the code does not exist yet.
+
+Cost:
+- Carry: about 3 lines in the arm and two fixture arms, in a pull request already taking a repair
+  round (verdict `blocked` at `d7e67e0d7`). `orchestrator_tick.py` already reads
+  `lg.dispositions(...)` for DESIGN-BUILD. No new check, file or API call.
+- `orchestrator_tick.py` is not a policy file, so it has no `policy_lint.mjs --budgets` row. No
+  policy file is touched.
+- Without it, every repair applied through the level's own remedy reads owed each pass until an
+  unrelated head move: five pull requests hit the stand-in's line on 2026-11-04 (`s9/events.txt`), with #3089 standing
+  3 h 55 m. Only #3089 is verified false; the other four were not traced.
+
+Binding:
+- **Why ACCEPT.** The arm has been built and its remedy cannot clear it, so this is a defect
+  caught before merge and a finding for that stage's brief (`finding-propagation.md`), the same
+  ground as `s6-batch115.md#P375`.
+- **Carry text for R10-TICK-LEVELS:** BODY-AHEAD clears on a disposition. In the arm at
+  `orchestrator_tick.py` line 903, a pull request whose `handoff-body/<topic>` sha holds a ledger
+  disposition (`ledger.py dispose refs/heads/handoff-body/<topic> <sha40> body-patched`, read through
+  `lg.dispositions` as DESIGN-BUILD does) does not owe. `body_patch.sh` does not move a head, so
+  without this the level's remedy cannot clear it (#3089, 12:32Z to 16:27Z on 2026-11-04). Do not
+  compare the ref's BODY.md to the live body: the push path rewrites `## Head`, and 4 of 4 open
+  pull requests read unequal. Fixture arms: (a) a disposition at the ref's sha prints nothing; (b)
+  a disposition at an older sha still owes (the null control). Mutation: dropping the disposition
+  read fails arm (a). triage: dev/programme/triage/s6-batch117.md#P381
+- **What stays with the orchestrator, all session-local or one operation:**
+  - the one-line wake fix above, in both copies;
+  - `python3 -I tools/audit/seat/ledger.py --log "$HPO_STATE_DIR/cloud-relay.log" dispose
+    refs/heads/design-verdict/r10-audit-coverage 5b77e98dd74a24d7b5ff1d94ac4e6820ab9bc7f8 built-as-3149`;
+  - seat-no-return: let the window end it, or delete the dispatch ref, the level's documented disposal
+    (`s6-batch115.md#P376`);
+  - the stand-in's RED-UNOWNED retires with #3200, so a patch is optional.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
