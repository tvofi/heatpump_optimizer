# Review packet #3204
head: e5381d941c448e63fd3a6215378e0d3adb53e3bb
base: d7582ed404a87603bd02fefda610d7ebbe4181e1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126749632363 success
arch-score / arch-score id=126784869105 success
arm id=126743005328 skipped
budget-raise-gate / budget-raise-gate id=126784868559 success
cancel-superseded id=126784868087 success
codeql id=126767815636 skipped
codeql / Analyze (actions) id=126784868577 success
codeql / Analyze (javascript-typescript) id=126784869616 success
codeql / Analyze (python) id=126784869254 success
gate id=126785416580 success
governance id=126767815596 skipped
governance / delivery-status id=126784869004 success
governance / delivery-status-publish id=126784869097 skipped
governance / env-matrix id=126784868993 success
governance / instrument-self-tests id=126784868427 success
governance / policy-docs id=126784869034 success
governance / record id=126784869679 skipped
governance / wave-script id=126784868716 success
hassfest id=126767814856 skipped
hassfest / hassfest id=126784868714 success
kernel-points id=126784868044 skipped
pr-contract / pr-contract id=126784989365 success
prelude id=126784939027 success
refresh id=126784866502 success
tests id=126767814685 skipped
tests / arch-instrument id=126784871204 success
tests / briefs id=126784869662 success
tests / browser id=126784871411 success
tests / ci-ratchet id=126784873181 skipped
tests / claims-autofix id=126784872812 skipped
tests / closure-scope id=126784869419 success
tests / closures id=126784871504 success
tests / closures-autofix id=126784872956 skipped
tests / coverage id=126784870244 success
tests / coverage-ratchet id=126784873638 success
tests / fast (3.14) id=126784871519 success
tests / graders-head-copy id=126784871824 success
tests / lane-proofs id=126784872372 success
tests / mutation id=126784868199 success
tests / mutation-autofix id=126784872555 skipped
tests / mutation-pins id=126784871576 skipped
tests / nightly-ha id=126784871898 skipped
tests / nightly-status id=126784866240 failure
tests / replay id=126784871080 skipped
tests / typing id=126784871261 success
validate id=126767816151 skipped
validate / validate-hacs id=126784869138 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat d7582ed40...e26398a0a4f0c9f54b6e4163c3f8303e60eebbea
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
diff --git a/dev/programme/delivery/3204.md b/dev/programme/delivery/3204.md
new file mode 100644
index 000000000..9665602cf
--- /dev/null
+++ b/dev/programme/delivery/3204.md
@@ -0,0 +1 @@
+- [#3204](https://github.com/tvofi/heatpump_optimizer/pull/3204) — **open**, triage: batch 118, P382 ACCEPT (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch118.md b/dev/programme/triage/s6-batch118.md
new file mode 100644
index 000000000..e8962c6e6
--- /dev/null
+++ b/dev/programme/triage/s6-batch118.md
@@ -0,0 +1,108 @@
+# Proposal triage, session s11, batch 118 (P382)
+
+The rolling batch after batch 117. Facts were read at origin/main `d7582ed40`, at the round's roster
+branch `origin/handoff/audit-r10-roster` (`9bc39aede`), in the seat ledger (`seat-ledger.md`, line
+numbers below are of that file less its `unwired open` lines), in the root-cause record
+`rca/base-copy-grader-bootstrap.md`, and from the return refs on origin.
+
+## P382: a cloud seat escalation ref
+
+Verdict: ACCEPT, narrowed to one carry on R10-TICK-LEVELS. The filed form, a new `escalate/<topic>`
+ref family, is refused: the question already reaches origin as `BLOCKED.md` on `handoff-wip/<topic>`,
+and what is missing is a reader. The carry adds the reader, removes two arms that read that push as
+healthy, and puts one sentence in the fixer brief.
+
+Source: the orchestrator's message of 2026-11-04. A cloud seat cannot message back, so a stuck seat
+cannot ask mid-run. It proposes a one-line question pushed to `escalate/<topic>`, and the wake loop
+reporting new refs of that shape.
+
+Instances, from the ledger's own timings. Every one is a fixer that ended its turn on a question,
+so an answer reached it only through a refire:
+
+| instance | stopped | answered or found | lag | what it asked | output on origin |
+|---|---|---|---|---|---|
+| R10-DEPS-ACTIONS-BUMP | 11-01 19:11Z | 11-02 02:08Z (L3614) | 6 h 57 m | split? | not traced |
+| R10-MACHINERY-RATCHETS | 11-01 23:39Z | 11-02 05:24Z (L3682) | 5 h 45 m | split? | `handoff-wip` |
+| #3065 r6 | 11-02 04:40Z | 08:36Z (L3755) | about 4 h | cap overflow: trim or raise? | dispatch read it as not returned |
+| #3065 r7 | 11-02 09:05Z | 09:52Z (L3781) | 47 m | body_push refused on hot-file | code handoff, no body |
+| #3169 r2 | 11-02 09:07Z | 10:06Z (L3791) | 59 m | the ruling's premise was false | **no ref moved** |
+| #3169 r3 | 11-02 10:44Z | 12:06Z (L3807) | 1 h 22 m | cap cannot hold: split? | `handoff-wip` subject says BLOCKED |
+| fix-tick1 (R10-TICK-LEVELS p1) | 11-04 08:39Z | 09:43Z (L3991) | 1 h 4 m | design choice | not traced |
+
+Two more are not priced as answerable:
+- **#3085 r8.** `BLOCKED.md` on `handoff-wip` at 13:18:46Z; first ledger read at 15:23:12Z. The answer
+  was event-gated on #3089, so an earlier read would not have cleared it.
+- **R10-RCA-CI-CRITPATH-3.** `BLOCKED.md` at 17:10:11Z today. **Still unanswered at this ruling**: it
+  asks for a carry landing on R10-PREPR-CAP (item `ce268b05`).
+
+Excluded: R10-CI-LAYOUT-P2's note of 10-22 predates the ledger and has no timing. Local seats, such
+as `56a61fb7` (L1109), can be messaged.
+
+- **Priced.** The seven lags total 20 h 54 m. DEPS and MACHINERY are the 12 h 45 m the root-cause record
+  counts (line 128), and P371 (`s6-batch113.md#P371`) already owes that class a route with no
+  question. It has not landed: `grep -c BOOTSTRAP tools/pr/ci_predict.py` on main reads 0. So the
+  benefit priced here is the other five: **8 h 12 m over 11-02 and 11-04**, of which #3065 was on the
+  critical path (L3755).
+- **Bound.** The tick runs every 300 s (`tick_loop.sh` line 54), so a reader leaves at most 5 m each,
+  **at most 7 h 47 m saved**. It is an upper bound on two counts: the lags include the deciding, and
+  the ledger cannot separate deciding from noticing.
+- **Denominator and undercount.** `cloud-sessions.tsv` holds 776 fires since 10-24. The table lists
+  only what the ledger recorded. The countermeasures of L3791 (`list_runs` each sweep) and
+  `s11/seat_watch.sh` already run, and #3085 r8's 2 h 4 m came after both, so they have not closed it.
+  **Not read:** the seats' cloud run logs, which this seat has no tool for. No instance shows a seat
+  idling mid-run with its work unfinished and resumable; each ended.
+
+The existing routes, each measured:
+- **`handoff-wip` with `BLOCKED.md`: carries the question and nothing reads it.** `git grep 'BLOCKED\.md'
+  -- tools dev/governance .claude` is empty, and `blind_spots.py` has no such arm. Two of the 76 refs
+  hold the file, each naming its question, and neither seat's brief named the file. Four s11 briefs
+  now name it by hand. `cloud_dispatch.py` does not.
+- **That push reads as healthy, which is worse than silence.** `noreturn_arm` counts a `handoff-wip`
+  move as a return (`cloud_relay.sh` lines 612 to 616). `_seat_on` in #3200 at `d7e67e0d7` (lines 827
+  to 829) counts it as a seat on the pull request, which holds off RED-UNOWNED. A seat that stops and
+  says so is therefore hidden from both.
+- **Blocked verdicts: not this route.** `BLOCKED-UNFIXED` is the reviewer's verdict on a head. A fixer
+  cannot post one, and all seven stops are fixers.
+- **A handoff with a note: unavailable when it is needed.** `RESUME.md` is on 4 of 346 body refs, and
+  it rides `body_push.sh`, whose refusal was the stop on #3065 r7, #3085 r8 and
+  R10-RCA-CI-CRITPATH-3. It also reads as a finished handoff.
+
+Rule run, on all 76 `handoff-wip` tips: owed when the tip holds `BLOCKED.md` and no `dispatch/fixer-<topic>`
+is newer than it.
+- `r10-rca-ci-critpath-3`, tip 17:10:11Z, dispatch 16:29:42Z: **owed, and true**.
+- `r10-closeout-cleanup`, tip 13:18:46Z, dispatch 15:25:52Z: clear, and true (the continuation is fired).
+- The other 74 print nothing (the null control).
+- Rule run on the table: it fires only where a seat writes the file, so it reaches #3169 r2 and fix-tick1
+  only through the brief sentence. That sentence is unproven on a seat that pushed nothing. **The two
+  writers wrote it unprompted; that is the only compliance evidence.**
+
+Cost:
+- **Filed form, refused.** `escalate/` must be added to the write limit of each role's brief
+  (`cloud_dispatch.py` lines 262 to 286, whose self-test pins that tail), to a `ref_privacy.py` push
+  disposition, to `prune_refs.py`'s families, and to a new watcher arm. It would also add a poll or a
+  session end, because it carries no answer back. All that buys nothing `BLOCKED.md` lacks.
+- **Carry.** About 15 lines in `orchestrator_tick.py`, 4352 lines on main and 4707 at #3200's `d7e67e0d7`, a hot file, plus
+  one `git fetch` of `refs/heads/handoff-wip/*` per pass: no API call. Three fixture arms, one
+  sentence in `cloud_dispatch.py`, plus one `set-files` op, since the group's list omits that file.
+- `orchestrator_tick.py` and `cloud_dispatch.py` are not policy files, so neither has a
+  `policy_lint.mjs --budgets` row. No policy file is touched.
+
+Binding:
+- **Why the reader clears the bar.** At most 7 h 47 m in about three days against 15 lines and no standing
+  API cost, with both masking arms defects in their own right. The filed form pays more for the same notice.
+- **What changes the answer on the filed form.** An instance of a seat that keeps working while it waits,
+  and whose question a live reply ref would have answered. None is in the table, and a reply route is not
+  what was proposed.
+- **Carry text for R10-TICK-LEVELS:** A fixer's stop on a question is owed. A `handoff-wip/<topic>` tip holding
+  `BLOCKED.md`, with no `dispatch/fixer-<topic>` newer than it and no ledger disposition at its sha, prints an
+  OWED line naming the topic, the sha and the file's `Question` line. Seven stops on 11-01 to 11-04 waited
+  47 m to 7 h because nothing read the file. The same tip is not a seat on it: `_seat_on` does not count it
+  (`orchestrator_tick.py`), and `noreturn_arm` (`cloud_relay.sh`) leaves it to this level. `cloud_dispatch.py`'s
+  fixer brief gains: "If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to
+  `handoff-wip/<topic>`, even with no code." Fixture arms: (a) a tip with the file and an older dispatch owes;
+  (b) a newer dispatch clears it (the null control); (c) a tip without the file prints nothing, and a red pull
+  request whose only move is a `BLOCKED.md` tip still prints RED-UNOWNED. Mutation: dropping the dispatch
+  comparison fails (b); dropping the `_seat_on` exclusion fails (c). triage: dev/programme/triage/s6-batch118.md#P382
+- **What stays with the orchestrator.** Add `tools/audit/seat/cloud_dispatch.py` to the group's files. A stand-in
+  arm in `blind_spots.py` is its own choice until the level lands. The R10-RCA-CI-CRITPATH-3 question above is
+  owed now.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
