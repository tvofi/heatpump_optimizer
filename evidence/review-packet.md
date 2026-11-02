# Review packet #3177
head: d9c5ec202752cb4207a400812ebd606b418f4818
base: d40e377e5d1d7fba3fae4bbbd9311e14fa47a988

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=125460642665 success
arch-score / arch-score id=125460436395 success
arm id=125460212861 skipped
budget-raise-gate / budget-raise-gate id=125460436244 success
cancel-superseded id=125460211064 success
codeql / Analyze (actions) id=125460436676 success
codeql / Analyze (javascript-typescript) id=125460436524 success
codeql / Analyze (python) id=125460436362 success
governance / delivery-status id=125460436301 success
governance / delivery-status-publish id=125460439123 skipped
governance / env-matrix id=125460436387 in_progress
governance / instrument-self-tests id=125460436497 in_progress
governance / policy-docs id=125460436476 success
governance / record id=125460440079 skipped
governance / wave-script id=125460436516 success
hassfest / hassfest id=125460436503 success
kernel-points id=125460438646 skipped
prelude id=125460211356 in_progress
refresh id=125460211186 success
tests / arch-instrument id=125460884696 success
tests / briefs id=125460436482 success
tests / browser id=125460884773 in_progress
tests / closure-scope id=125460436218 success
tests / closures id=125460885203 in_progress
tests / coverage id=125460884752 in_progress
tests / fast (3.14) id=125460884686 in_progress
tests / mutation id=125460436460 success
tests / mutation-autofix id=125461250755 skipped
tests / mutation-pins id=125461248810 skipped
tests / nightly-ha id=125460886359 skipped
tests / nightly-status id=125460436561 success
tests / replay id=125460888100 skipped
tests / typing id=125460884680 in_progress
validate / validate-hacs id=125460436373 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --stat 3905069f3...1d35b423c
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
diff --git a/dev/programme/delivery/3177.md b/dev/programme/delivery/3177.md
new file mode 100644
index 000000000..c494c9653
--- /dev/null
+++ b/dev/programme/delivery/3177.md
@@ -0,0 +1 @@
+- [#3177](https://github.com/tvofi/heatpump_optimizer/pull/3177) — **open**, triage: s9 batch 115 (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch115-rca-topic-family.md b/dev/programme/triage/s6-batch115-rca-topic-family.md
new file mode 100644
index 000000000..5113b8778
--- /dev/null
+++ b/dev/programme/triage/s6-batch115-rca-topic-family.md
@@ -0,0 +1,215 @@
+<!-- Root-cause seat document for the topic-family class, carried into the tree by triage batch 115 (P377) so the R10-TICK-PR-BUCKETS fixer can land it at dev/audit/rca/topic-family.md. Host paths are scrubbed; the text is otherwise as the seat wrote it. -->
+
+# RCA: instruments keyed on an exact topic miss its split parts (`<topic>-p<N>`)
+
+Root-cause seat, 2026-11-02T16:39Z. Facts read at origin/main `ea59e9a09`, the round roster
+`handoff/audit-r10-roster` `2c50a2cfc`, a full `git ls-remote origin` snapshot (8453 refs, 235
+`dispatch/fixer-*`), `gh pr list --state all` (158 PRs created since 2026-10-30), the session's seat ledger, the batch 106/112/115 triage files, and
+the session-local `blind_spots.py` and its backup. The simulators were session-local scratch scripts (`sim.py`, and `sim2.py`, the same with bare `-<N>` included); their figures are quoted below.
+
+## 1. Cause
+
+**Named cause.** The topic string is the join key between five records: the dispatch ref
+(`dispatch/fixer-<topic>`), the return refs (`handoff/`, `handoff-wip/`, `handoff-body/<topic>`),
+the PR head (`fix/<topic>[-pr]`), the roster group (`<TOPIC>` upper-cased), and the ledgers. Nothing
+defines the topic's grammar in one place. Every instrument parses the relation it needs from the
+exact string itself. Splitting work into parts adds `-p<N>` and changes the topic partway through
+that work. Each join that crosses a split then misses, unless its author thought of parts.
+
+**Reproduced, not accepted.** Instance by instance:
+
+1. **Opener (topic -> group).** The session-local opener upper-cased the topic. Each part topic
+   logged `NEEDS-TITLE` (P363: `r10-fly-train-defaults-p2`, `r10-roster-ops-2-p1`,
+   `r10-sav-comfort-p2`, plus a title override for `r10-ux-health-p3`; P370: `r10-deps-actions-bump-p1`
+   at 03:24Z). This is fixed in the tree: `open_driver.resolve()` (commit `20cfab74c`) tries the
+   exact name, then one `-p<N>` stripped, then one `-<N>` stripped, behind a body check. The fix
+   is private to the opener.
+2. **`noreturn_arm` (dispatch -> return).** Confirmed from the refs:
+   `dispatch/fixer-r10-agreement-bootstrap` `b3f577cb` is at 08:08:44Z. Every exact-topic
+   return ref predates it: handoff and handoff-wip at 05:41Z, handoff-body at 06:37Z, and
+   fix/ at 07:14Z. The seat returned on `handoff/r10-agreement-bootstrap-p1`, which then
+   merged as #3173. **A sharper cause than "the arm forgot parts": the orchestrator's own
+   ruling told the seat to use the part topic.** The r2 PROMPT.md (commit `766ac672`, line 4) has
+   the seat step-push to `handoff-wip/r10-agreement-bootstrap`, the family topic. Line 10 then
+   has it hand part 1 off as `handoff/r10-agreement-bootstrap-p1` with
+   `body_push.sh r10-agreement-bootstrap-p1`. So one seat writes under two topics. The dispatch
+   ref records only the first. The part name exists only as free text in the prompt.
+3. **`blind_spots.py` (PR -> handoff, and "a seat is on it").** **Misattributed in part.**
+   - The script's measured misses are #3085 (4 RED-UNOWNED lines, 15:37Z-16:09Z) and the #3174
+     retake. Both come from P375's class: a fire named only by its payload file, and handoff-wip
+     motion that was never read. `r10-closeout-cleanup` is not a part topic.
+   - I ran the original `cands` against the new ones over all 158 PRs since 10-30. That set holds
+     16 part-topic PRs, and each one carries its own exact `handoff/` and `handoff-body/` refs.
+     So the old `-(pr|2)` strip missed no code or body ref. The new `-p\d+` strip changes the
+     result for one PR only: #2992 (`r10-train-overlap-grade-p3`, merged), whose
+     `handoff-wip` now resolves to the family's.
+   - The patched line 61 takes the **max** handoff-wip time over both candidates. A part PR's red
+     is therefore silenced by motion anywhere in its family. That is right when the family seat
+     is the one working on the part, which is instance 2's prompt shape. It masks the red when a
+     sibling part's seat is the one moving.
+   - So instance 3 is a site of the class. It is not a measured miss of the class.
+
+**How far the class reaches (search of `tools/audit/seat` at `ea59e9a09`).** The topic grammar
+is parsed independently at six places:
+
+| site | relation | part handling | status |
+|---|---|---|---|
+| `open_driver.py:88-109` `resolve` | topic -> group | exact, then `-p<N>`, then `-<N>`, behind a body check | correct, private |
+| `roster_sync.py:259-275` `matches` | group topic -> PR heads | `name == t or startswith(t + "-")`, longest topic wins | correct, private |
+| `cloud_relay.sh:533,540` (sed/awk) | PR head -> topic | strips `fix/` and `-pr` | correct (PR and handoff share the part topic) |
+| `open_driver.py:272` | topic -> PR exists | `fix/<topic>` or `fix/<topic>-pr` | correct |
+| `cloud_relay.sh:612-614` `noreturn_arm` | dispatch -> return | exact only | **defect** |
+| `blind_spots.py:46,61` (session) | PR -> handoff / wip | strips `-pr`, `-2` and (patched) `-p<N>`, max wip | stand-in; its tracked form is R10-TICK-PR-BUCKETS carry 6 plus b115-P375, **not built** |
+
+The same grammar is written three different ways: `startswith(t+"-")`, `-p(\d+)`, and
+`-(pr|2|p\d+)`. Those ways disagree about bare `-<N>`. `R10-ROSTER-OPS-2`, `R10-STALE-PATHS-2`
+and `R10-TICK-DRIVERS-2` are real groups, so the opener treats a bare `-<N>` as a part, roster_sync
+treats it as a prefix match won by the longer topic, and blind_spots strips only `-2`.
+The next tracked tick level is R10-TICK-PR-BUCKETS: not started, carries 6 and b115-P375. It will
+write a seventh site unless it is handed a shared reader.
+
+## 2. Process state: (a), the process did not exist
+
+- No policy file, role contract or instrument defines the topic grammar. A
+  `git grep` for `-p<N>`, `<topic>-p` and "part topic" across `dev/governance`,
+  `tools/audit/seat`, `tools/pr`, `.claude` and `CLAUDE.md` finds only `open_driver.py` (with its
+  `.md` and the INSTRUMENTS.md line) and `roster_sync.py:43`. Both are a consumer's private
+  rule, not a definition.
+- Decision 0013's "check the instrument inventory before hand-rolling" (CLAUDE.md, Instruments)
+  lists merge, push, body, gate and watch loops. Topic parsing has no entry, and none existed to
+  find.
+- It is not (d). Part topics predate the defective arm. #3005 (`r10-cop-gate-p5-pr`) was created
+  2026-10-30T17:23Z. The `noreturn_arm` commits are dated 2026-10-31 17:30Z to 18:16Z, and it went
+  live when #3065 merged: orch-wt2 fast-forwarded to `a568a2e12` at 14:58Z on 2026-11-02.
+- It is not (b). No author or seat skipped a rule. P363's triage fixed its own site as the
+  ruling directed. Nothing asked triage to search the class's sibling instruments, and that is
+  how the class reached a second and third site.
+- The split-in-prompt naming (instance 2) is part of the same absence. Nothing makes a split
+  ruling name its part topics on the dispatch record. The record keeps the family topic, and the
+  part name lives only in prose.
+
+## 3. Cost test, measured
+
+All times are UTC, read from the seat ledger and the PR API. Wall-clock is per occurrence.
+
+| instance | false or missed lines | wall-clock |
+|---|---|---|
+| opener | 4 part-topic `NEEDS-TITLE` (3 of 69 RESULT lines 10-31 17:36Z to 11-01 19:27Z; 1 of 88 by 11-02 03:24Z); 1 title override (`r10-ux-health-p3`); a 19:47Z turn writing 3 more overrides | sav-comfort-p2 (CP head) 19:21Z to 19:35Z, **14 min**; roster-ops-2-p1 19:08Z to 19:19:28Z, **11 min**; deps-actions-bump-p1 03:24Z to 03:29:40Z, **5 min**; fly-train-defaults-p2 01:09Z to 13:23Z = 12 h 14 min, **confounded** with that day's opener-repair outage, so not counted. Two triage rulings (P363, P370) and a carry (built, `20cfab74c`) |
+| `noreturn_arm` | 1 false `OWED seat-no-return` (16:09:47Z). That is **1 of 1 fires** since the arm went live; 3 ledger lines to dispose of it | 16:09:47Z to 16:26:08Z, **16 min**. The dispatch seat's 16:23:15Z OWED-ACK said "renders resume fixer now". It was caught at 16:25:48Z, so a duplicate **opus** resume fixer was avoided by a hand check, not by any instrument. One triage ruling (P376) and this seat |
+| `blind_spots` | **0** lines attributable to this class (section 1) | 0. Its 4 #3085 lines and the #3174 retake belong to P375 |
+
+Measured total: **6 false or missed lines**: 4 NEEDS-TITLE, 1 forced override and 1 false OWED.
+On top of those, 3 overrides were written in advance. The measured holds add up to **46 min**.
+One near-duplicate opus seat was avoided by a hand check. Three triage rulings and one RCA seat
+came out of it.
+
+**P(recurrence).** 13 of the 235 dispatched topics on origin split into parts in 3 days
+(10-30 to 11-02), and 16 of the 158 PRs are part PRs (10%). Splitting is now a standing repair
+move: the r2 prompt cites "the split that already solved this class twice". With the opener
+fixed, the live exposure is `noreturn_arm`. Over all 235 dispatch refs it produced 1 false fire
+on 13 splits, about 0.3 per day. A tracked RED-UNOWNED level built without a reader would add a
+second exposure, of the same size as the #3085 class: 4 lines in 32 min.
+
+**Countermeasure, standing cost.** A pure function with no I/O of its own. In `noreturn_arm` it
+costs one extra `git ls-remote` with three patterns, made only for an aged dispatch whose exact
+refs did not move. In the current window that is 1 of 34 dispatches, about 0.5 s per 120 s
+pass. Everywhere else it costs about 0 s.
+
+    cost(countermeasure, recurring) ~ 0.5 s/pass  <<  16 min x 0.3/day (+ an opus duplicate-seat risk)
+
+**Verdict: build.** The class has three or more instances, which makes it an audit class that owes
+a barrier (`defect-root-cause.md`). The cost test picks the barrier's form: one shared reader, not
+a fourth per-site rule.
+
+## 4. Countermeasure: one topic grammar in `tools/audit/seat`
+
+It addresses state (a): it creates the definition that did not exist, and every site reads it.
+
+**Demonstrated, by simulating the two rules over the real refs** (`sim.py`, read-only):
+
+- **Fails on the defect.** The exact rule (today's `noreturn_arm`) finds no return for
+  `r10-agreement-bootstrap`, which fires.
+- **Passes once fixed.** The family rule finds `handoff/r10-agreement-bootstrap-p1` moved after
+  the dispatch, so it does not fire.
+- **Null control, it does not go green by skipping.**
+  - Over all 235 dispatch refs, 55 have no exact-topic return.
+  - The family rule clears exactly 1 of them (`r10-agreement-bootstrap`) and still reports 54.
+  - Across the 13 split families, it changes the verdict only where the exact refs did not move.
+  - Of the 34 dispatches in the arm's window now, the exact rule fires 1 (the false one) and the
+    family rule fires 0.
+- **Bare `-<N>`.** Including it in the family changes nothing on today's refs (`sim2.py`: same
+  55/54/1). It is still excluded, because `R10-ROSTER-OPS-2` and the other `-<N>` names are
+  distinct groups whose motion must never count as another group's return. That reason is a
+  risk, not a measurement, and it is stated as one.
+
+The fixer still owes the in-tree proof: a self-test row for each consumer, run red on the defect
+and green on the fix, with a mutant.
+
+### Carry brief, routable to R10-TICK-PR-BUCKETS (recommended) or R10-OPENER-REUSE
+
+Route to **R10-TICK-PR-BUCKETS**. It is `not-started`, and it would otherwise build the seventh
+site (carry 6 plus b115-P375's tracked RED-UNOWNED level). It also owns `ledger.py` and
+`orchestrator_tick.py`. R10-OPENER-REUSE (`carries-open`, owns `open_pr.sh` and `update_pr.sh`) is
+the fallback; only the `open_driver` move is native to it. Either way the carry adds
+`cloud_relay.sh` (hot) and `roster_sync.py` to the group's files.
+
+> From the root-cause seat for the topic-family class (2026-11-02; triage P363, P370, P376; RCA in
+> `dev/programme/triage/s6-batch115-rca-topic-family.md`, to be landed as `dev/audit/rca/topic-family.md` and cited
+> by `rca` in `bugclasses.json` in this PR). The topic is the join key between dispatch, return,
+> PR and roster records. Its grammar is parsed separately at six sites, and the sites disagree.
+> `noreturn_arm` (`cloud_relay.sh` 595-626) keys on the exact dispatch topic. It false-fired
+> `SEAT ENDED NO RETURN r10-agreement-bootstrap` at 16:09Z on 11-02, after the seat had returned
+> on `handoff/r10-agreement-bootstrap-p1` (merged #3173), because the split ruling named the part
+> topic only in the prompt's prose.
+>
+> Change: add `tools/audit/seat/topic_grammar.py`, one module that owns the grammar, with a CLI
+> for bash callers:
+> (1) `pr_topic(head)`: strip `fix/` and one trailing `-pr`.
+> (2) `family(topic)`: the base is the topic less one trailing `-p<N>`; the family is the base
+>     plus every `<base>-p<N>`. A bare `-<N>` is never a family member, because
+>     R10-ROSTER-OPS-2, R10-STALE-PATHS-2 and R10-TICK-DRIVERS-2 are distinct groups.
+> (3) `family_refs(topic, ls_remote_text, kinds)`: the listed `refs/heads/<kind>/<member>` refs
+>     whose member full-matches the family. Never a prefix: `handoff-wip` step refs and sibling
+>     topics such as `r10-deeplink-census` against `r10-deeplink` must not match.
+> (4) `group_of(...)`: `open_driver.resolve`'s exact, then `-p<N>`, then `-<N>` order, moved
+>     unchanged, with its body check.
+> (5) `owner_topic(head, topics)`: `roster_sync.matches`'s longest-topic rule, moved unchanged.
+>
+> Consumers:
+> - `noreturn_arm` asks for the exact refs as today. When none moved, it lists the three kinds
+>   for `<topic>-p*` and counts a moved family member as a return.
+> - `open_driver.py` and `roster_sync.py` import (4) and (5). Their behaviour is unchanged and
+>   their existing self-tests stay green.
+> - `cloud_relay.sh:533,540` call (1).
+> - The tracked RED-UNOWNED level this group builds reads (2) for "a seat is on it": handoff-wip
+>   motion anywhere in the PR's family. A family seat writes the part's wip under the base topic
+>   (r2 PROMPT.md `766ac672`, line 4).
+>
+> Rows:
+> - `r10-agreement-bootstrap` dispatched at T, with only `handoff/…-p1` moved after T: no fire.
+> - `r10-roster-ops` dispatched, with only `handoff/r10-roster-ops-2` moved: fire.
+> - `r10-deeplink` with `handoff/r10-deeplink-census` moved: fire.
+>
+> Null controls: a dispatch whose family moved nothing still fires, and over origin's 235
+> dispatch refs, 55 have no exact return and the family rule clears exactly 1. One mutant counts
+> a bare `-<N>` as a family member and must fail the `r10-roster-ops` row. A second matches by
+> prefix and must fail the `r10-deeplink` row.
+>
+> Not in scope: renaming topics, and changing what `cloud_dispatch.py` writes. If the fixer finds
+> it cheaper for a split ruling to dispatch each part under its own `dispatch/fixer-<topic>-p<N>`,
+> it says so in the body. The reader is still owed, because a seat can split on its own.
+
+**Orchestrator's own stand-in, outside the carry and the orchestrator's operational call.**
+`blind_spots.py:46` should keep exact-first for `handoff/` and `handoff-body/`, where the change
+is harmless. Line 61's max-over-family wip should be recorded as the family rule above, not as a
+fix for a measured miss: it has silenced none to date. It can mask a part PR's red when a sibling
+part is the one moving.
+
+## 5. Recording
+
+This seat opens no PR and files no issue, by its brief. Still owed:
+- The landing PR carries the in-tree RCA document (`dev/audit/rca/topic-family.md`) and its
+  `bugclasses.json` entry with `rca`. Without that entry, `fold_ledger.py check` will keep
+  listing the class as having no barrier and no RCA document.
+- There is no issue to receive a **Root cause** section. P376 is a triage LOG, and this class
+  has no issue.
diff --git a/dev/programme/triage/s6-batch115.md b/dev/programme/triage/s6-batch115.md
new file mode 100644
index 000000000..1246b913d
--- /dev/null
+++ b/dev/programme/triage/s6-batch115.md
@@ -0,0 +1,300 @@
+# Proposal triage, session s10, batch 115 (P373)
+
+The rolling batch after batch 114. Facts were read at origin/main `3905069f3`, at the round's
+roster branch `origin/handoff/audit-r10-roster` (`f6df1ab5d`), from the GitHub Actions runs list
+for the repository, and in the session's seat ledger.
+
+## P373: rolling record and roster branches, one pull request each per stamp window
+
+Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule). No carry and no group. Parts (1)
+and (3) are LOG. Part (2) describes a lane that already works this way. Part (4) is refused on
+its cost. The measured saving is reached with no instrument change, by applying the record
+batching size the owner already set. The answer changes on a measured CI-time saving above 10%
+that only the rolling design reaches, with its baseline and a null control.
+
+Source: the orchestrator s10's message of 2026-11-02, about 12:15Z, filed at the owner's
+request. It proposes:
+- (1) one rolling record pull request per stamp window, appended by the triage seat through
+  `update_pr`, reviewed as a delta;
+- (2) the same for roster landings;
+- (3) closing the window at stamp planning;
+- (4) folding the 8 open record pull requests into the first rolling branch.
+
+Instances:
+- **The 8 open record pull requests.** From `gh pr view <n> --json headRefName,files`:
+  - #3154, #3157, #3158, #3159, #3161, #3171 and #3172 are triage batches 108 to 114.
+  - **Each carries exactly one ruling**: one `s6-batch<N>.md` file and its own delivery row.
+  - #3091 is `fix/r10-record-s9-owed`. It changes a carry file, two delivery rows and
+    `tests/closures.json`.
+  - None of the 8 touches `custom_components/`.
+- **The CI share, measured.** The source is `gh api repos/tvofi/heatpump_optimizer/actions/runs`
+  for runs created since 2026-11-01T10:00Z. That is 1000 runs, the API's cap, which reach back
+  to 2026-11-01T17:17:41Z, a window of about 19 hours.
+  - Each run's wall time is `updated_at` less `run_started_at`, and it includes queueing.
+  - Branches `fix/triage-s9-batch*`: 80 runs, 559 run-minutes. That is **7.6%** of all run
+    time and 12.6% of non-main run time.
+  - Branches `fix/r10-record*` and `record/*`: 25 runs, 185 run-minutes, **2.5%** of all run
+    time.
+  - Fix branches: 306 runs, 3572 run-minutes, 48.8%.
+  - Main: 580 runs, 2890 run-minutes, 39.5%.
+  - The triage runs are 24 `CI code`, 24 `CI edit`, 24 Dependabot auto-merge and 8 `CI review`,
+    over 7 pull requests: about 11 runs and 80 run-minutes per one-ruling pull request.
+- **The roster lane already rolls.** Roster landings do not open pull requests:
+  - `roster_drain.py` pushes each op to `handoff/audit-r10-roster`, which is 1055 commits ahead
+    of origin/main (`git rev-list --count`).
+  - The roster reaches main in bulk landings. The last is `75278a0e0` "Land the round-10 roster
+    on main".
+  - `gh pr list --head handoff/audit-r10-roster` lists only #2277, #2343, #2348 and #2352, all
+    from 2026-10-15 to 10-17.
+- **The batching size is already set and this seat has not applied it.** The owner's direction of
+  2026-10-25 is that triage, roster and record pull requests carry 8 to 10 entries. A
+  critical-path-unblocking entry may open early. Batches 108 to 114 were one ruling each. That
+  is this seat's slip, not a gap in the instruments.
+- **Stamp merges are not serial.** Record pull requests merge only in a stamp's batch, and
+  batch-by-default trains (`merge_train.py` queue) merge a stamp's record pull requests on one
+  proof. The "8 serial merges" in the proposal is therefore one batch, not eight CI cycles.
+
+Cost:
+- Parts (1) to (3) change four instruments:
+  - the triage seat's push path, from a new handoff to `update_pr` on a standing branch;
+  - the opener's topic-to-PR mapping, which must not open an appended topic;
+  - `review_carry`'s fresh-review scope, which must cover a delta;
+  - the merge train's stamp queue.
+- Each change brings its own self-test arms, mutants and review rounds. The opener and
+  review_carry are both hot in round 10 (R10-OPENER-REUSE, R10-ORCH-REVIEW-PACKET).
+- A rolling pull request still runs full CI on every `update_pr`. The per-ruling CI cost of an
+  append is therefore one run-set, the same as a batch pull request, unless an append skips CI,
+  which the proposal does not claim.
+- Part (4) costs 8 closures and 8 pointer comments, plus one new pull request with its own full
+  CI. It saves no CI already spent, and no stamp merge, because those already go on one batch.
+- No capped file is touched by this ruling.
+
+Binding:
+- **Why LOG.** The friction does not hold a pull request that touches `custom_components/`.
+- **The exemption is not met.**
+  - The whole triage lane is 7.6% of CI run time, and triage plus record is 10.1%, both measured
+    with queue time included.
+  - That is the ceiling of any saving, and neither design reaches it: a rolling branch keeps one
+    CI run-set per append.
+  - No measured figure above 10% with a baseline and a null control was given, so the proposal is
+    ruled under the LOG class, not on its merits.
+- **The same saving at no build cost.** From batch 115 on, this seat applies the owner's 8-to-10
+  size. It holds rulings in one batch and pushes the batch when it holds 8 rulings, when the
+  orchestrator plans a stamp, or early for a ruling whose carry unblocks a critical-path merge.
+  - Waiting costs nothing for a DEFER or a REJECT.
+  - An ACCEPT carry is held until its ruling is on main, and record pull requests merge only at a
+    stamp, so the carry lands no later.
+  - At about 11 runs and 80 run-minutes per pull request, one pull request per 8 rulings in
+    place of 8 saves about 7 x 80 = 560 run-minutes per 8 rulings. That equals the lane's whole
+    measured window, which held 7 rulings.
+- **Part (2) needs nothing built.** The roster branch already rolls.
+- **Part (4) is refused on its binding cost.** One more full CI run and 8 closures buy no saving,
+  because the 8 open pull requests have already run their CI and merge on one stamp batch.
+
+## P374: a verdict ref takes a second commit with the same tree, and the pull request deadlocks
+
+Verdict: ACCEPT, as a defect in an instrument: option (a), narrowed to `append_commit` in
+`tools/audit/seat/bus.sh`. Option (b) is refused. The carry, b115-P374, goes to
+R10-FLY-RAISE-REVIEWABLE, whose files already hold `bus.sh` and `merge_train.py` and whose next
+step is a fixer.
+
+Source: the orchestrator s10's message of 2026-11-02, about 13:50Z, after a hand fix (seat
+ledger, 13:49:10Z `DEADLOCK-BY-HAND #3173`).
+
+Instances:
+- **#3173** (`fix/r10-agreement-bootstrap-p1`, R10-AGREEMENT-BOOTSTRAP p1). Read from
+  `git cat-file -p` on each commit:
+  - `verdict/3173` got `f9aafd42` at 14:44:06+01, confirmed from `review/3173` at `2eab795f`.
+  - It then got `dba76851` at 14:44:12+01, parented on `f9aafd42` and confirmed from
+    `review/3173` at `e6899918`.
+  - Both have tree `50c657668ec5`. The messages differ only in that `bus-confirmed` line and a
+    `bus-model: opus` line, so the two are not byte-identical.
+- **The double writer is the reviewer's push, not the relay.** `git log origin/review/3173`:
+  - `2eab795f` at 14:43:56+01, on `6bc25136`;
+  - `e6899918` at 14:44:03+01, on `2eab795f`, with an empty diff and the same message.
+  - `push-verdict` therefore ran twice on one verdict, and each review head was confirmed once.
+- **Why the second confirm passed its replay guard.** The guard in `confirm()` (`bus.sh` lines
+  567-571 at origin/main `3905069f3`) reads `posted-signed` before it pushes. The second confirm
+  started before the first had posted, passed, and appended `dba76851`. Only then did
+  `post_verdict` (lines 353-355) refuse it as a replay. That left the posted commit one behind
+  the tip.
+- **Why the train refused.** `merge_train.py` line 2472 refuses when "the newest posted verdict
+  (comment ...) is not verdict/<n>'s tip". That is a deliberate guard, pinned by its self-test
+  arm "a newest posted verdict that is not the bus tip waits (#18: confirmed, not posted)"
+  (line 4773).
+- **One instance** in the seat ledger. The defect has the same shape as P368: a verified
+  deadlock in an instrument, worked around by hand.
+
+Rule run on the instance:
+- With the carry's rule, the reviewer's second `push-verdict` reads `review/3173`'s tip
+  `2eab795f`. Its tree equals the tree being pushed, so it pushes nothing. `e6899918` never
+  exists and there is no second confirm.
+- If two confirms still race, the second reads `verdict/3173`'s tip `f9aafd42`, whose tree is
+  the same, and appends nothing. The posted commit stays the tip, which is the state the hand fix
+  restored.
+
+Cost:
+- One guard in one shell function, `append_commit`, which both `push-verdict` and `confirm`
+  call: about 6 lines.
+- Three self-test arms in `bus.sh`'s existing self-test and one mutant in
+  `dev/audit/harnesses/r10_seat_selftests_mutants.py`.
+- An S group that already holds `bus.sh`, so no new group and no new file.
+- Option (b) would loosen `merge_train.py`'s verdict-identity check, a merge gate, for every pull
+  request in order to cover a state that (a) stops from being written. That is the binding
+  cost of refusing (b).
+- No capped file is touched by this ruling.
+
+Binding:
+- **Why ACCEPT.** A verified defect in an instrument, not a proposal. It deadlocks any pull
+  request whose reviewer re-runs `push-verdict`, production pull requests included.
+- **The tree is the right key.** `post_verdict` already treats "<pr> <tree>" as what was signed,
+  and "each round's nonce makes its tree distinct" (lines 346-351). A same-tree append can only
+  repeat a verdict, never carry a new one.
+- **Delivery.** The carry lands when this batch is on main. If R10-FLY-RAISE-REVIEWABLE's fixer
+  is dispatched before then, the orchestrator hands the fixer this entry directly.
+
+## P375: RED-UNOWNED reads a fired seat as no seat, missing payload-named fires and handoff-wip
+
+Verdict: ACCEPT, narrowed to propagating the finding into the brief that builds the tracked
+level: carry b115-P375 on R10-TICK-PR-BUCKETS. That group's carry 6 specifies RED-UNOWNED as
+"no seat dispatched" and leaves the meaning of "dispatched" open. No new group and no new check.
+The session-local stand-in is the orchestrator's own script and outside the roster.
+
+Source: the orchestrator s10's message of 2026-11-02, about 16:30Z, a slip from that day's
+sweeps.
+
+Instances:
+- **#3085, four lines from 15:37Z to 16:09Z** (orchestrator's report).
+  - The dispatch seat's `ledger-standin.txt` line 212 reads
+    `2026-11-02T15:03:29Z FIRED payload-fix-3085-r5.json`.
+  - The stand-in `blind_spots.py` (sweep runner, line 61) calls
+    `fired_after(["#3085 ", "#3085)", topic], now - 3 h)`. Line 212 names neither `#3085` nor
+    `r10-closeout-cleanup`, only the payload file, so the fire is invisible.
+  - Earlier FIRED lines for #3085 (ledger-standin lines 94, 112 and 147) wrote `#3085 r<k>`; the
+    line format changed and the predicate did not.
+  - The script never reads `handoff-wip/<topic>`, which moved at 15:08Z (orchestrator's report).
+- **#3174, the same class, by hand.** Seat ledger at 16:16:43Z: "ordered #3174 retake on
+  BLOCKED-SILENT without checking handoff-wip (moved 16:13Z); dispatch caught it".
+- **The tracked form is not built yet.**
+  - On roster `2c50a2cfc`, R10-TICK-PR-BUCKETS is at stage `not-started` with 7 carries.
+  - Carry 6 asks for "three tick levels with these predicates", each with a null control and a
+    planted positive.
+  - `blind_spots.py`'s docstring names it as that carry's stand-in.
+
+Rule run on the instances:
+- With the carry's definition, line 212 is a fire for #3085, because it names a payload file for
+  pull request 3085. So is `handoff-wip/r10-closeout-cleanup` moving at 15:08Z. RED-UNOWNED
+  prints nothing for #3085 until 18:03Z.
+- #3174's handoff-wip motion at 16:13Z likewise holds it.
+
+Cost:
+- Carry text only. It fixes the meaning of one word in a predicate the group already owes:
+  about 5 lines in the level it writes, and one planted arm.
+- Without it, the tracked level copies the stand-in's blind spot. It would fire on every pull
+  request whose fix is in progress, and a false RED-UNOWNED invites a duplicate fixer, which is
+  how #3174's retake was ordered.
+- No capped file is touched by this ruling.
+
+Binding:
+- **Why ACCEPT.** A finding that changes how a later stage must work goes into that stage's own
+  brief before it is built (`finding-propagation.md`). This is not a proposal for new
+  machinery, so the LOG class does not apply.
+- **What stays with the orchestrator.** The two-line patch to its own stand-in: add payload-file
+  keys to `fired_after`, and treat a handoff-wip move in the window as a fire.
+
+## P376: seat-no-return fires for a dispatch that returned on a split-part topic
+
+Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule), with the class sent to a root-cause
+seat. On its own, the false line costs one OWED-ACK, or deleting the dispatch ref, which is the
+level's documented disposal. It holds no merge. What changes the answer is the root-cause
+seat's countermeasure for split-part topics, below, which may route this site with the others.
+
+Source: the orchestrator s10's message of 2026-11-02, about 16:30Z.
+
+Instances:
+- **r10-agreement-bootstrap.** `git log -1 --format=%cI` on each ref:
+  - `dispatch/fixer-r10-agreement-bootstrap` (`b3f577cb`) is at 08:08:44Z.
+  - The exact-topic return refs all predate it: `handoff/` and `handoff-wip/` at 05:41Z,
+    `handoff-body/` at 06:37Z, `fix/r10-agreement-bootstrap` at 07:14Z.
+  - The seat returned on the split-part topic: `handoff/r10-agreement-bootstrap-p1` at 11:36Z
+    and `handoff-body/r10-agreement-bootstrap-p1` at 12:34Z. #3173 then merged.
+  - The orchestrator acknowledged it in the seat ledger at 16:26:08Z (OWED-ACK, "false
+    positive").
+- **The mechanism is the topic name, not the session.** `noreturn_arm` in
+  `tools/audit/seat/cloud_relay.sh` (lines 595-626 at origin/main `ea59e9a09`) asks only for
+  `handoff/`, `handoff-wip/`, `handoff-body/<topic>`, `fix/<topic>-pr` and `fix/<topic>` with
+  the dispatch's exact topic. A return on `<topic>-p<N>` is never asked for.
+  - The report's reading, "keys on the session ending", does not match the code. The predicate
+    reads no session state: the dispatch tip's age and those five refs are its only inputs.
+- **The same blindness, elsewhere.**
+  - The opener: P363 (`s6-batch106.md`) and P370 (`s6-batch112.md`), with 4 part topics missed
+    by 03:24Z.
+  - The stand-in `blind_spots.py` line 46, whose candidates strip only `-pr` and `-2`, not
+    `-p<N>`.
+  - That makes three instruments with one cause: each keys on an exact topic, and none knows a
+    topic's part family.
+
+Cost:
+- A fix inside `noreturn_arm` alone means another per-instrument rule. It needs about 10 lines
+  and a self-test arm in `cloud_relay.sh`, which is hot in round 10, to suppress one false
+  OWED line per split.
+- The class already has a third site, so per-site fixes keep re-paying the same cost.
+- No capped file is touched by this ruling.
+
+Binding:
+- **Why LOG.** The friction holds no pull request that touches `custom_components/`, and no
+  measured gain is offered.
+- **The class is the root-cause seat's.** At the third instrument, a recurring defect is owed a
+  root-cause seat (`CLAUDE.md`, "A recurring error is not a third issue";
+  `dev/governance/roles/root-cause.md`), not a third per-site carry. Dispatching it is the
+  orchestrator's call. Its countermeasure decides whether one topic-family reader replaces the
+  per-site rules, including R10-OPENER-REUSE carry 10.
+
+## P377: one topic grammar for the split-part class (the root-cause seat's barrier)
+
+Verdict: ACCEPT, as a root-cause countermeasure. It keeps that route and is not ruled as a
+proposal under the LOG class. The carry, b115-P377, goes to R10-TICK-PR-BUCKETS, with
+R10-OPENER-REUSE as the fallback. A set-files op adds the consumers it edits to the group's
+files. The root-cause document rides in this batch as `s6-batch115-rca-topic-family.md`, so
+that the fixer, which cannot read the host, lands it from the tree.
+
+Source:
+- The orchestrator s10's message of 2026-11-02, about 16:55Z. It relayed the root-cause seat's
+  verdict "build" for the class P376 sent to it.
+- The document is `s6-batch115-rca-topic-family.md` in this directory: the seat's text with its
+  host paths scrubbed (`ref_privacy.py scrub`: 0 of 2 files would change).
+
+Instances, checked against origin/main `ea59e9a09`:
+- **The class's three instances.** The opener (P363 and P370), `noreturn_arm` (P376), and the
+  stand-in `blind_spots.py`.
+  - The document re-attributes the stand-in's measured misses to P375's class.
+  - It keeps the stand-in as a site of this class, with no measured miss.
+- **Its six-site table checks out.**
+  - `open_driver.py` line 88 is `def resolve(topic, groups, body_head, titles)`.
+  - `roster_sync.py` line 259 is `def matches(roster, prs)`.
+  - `cloud_relay.sh` lines 533 and 540 strip `fix/` and `-pr` with sed and awk.
+  - `noreturn_arm` is lines 595-626.
+- **The recording targets exist.** `dev/audit/config/bugclasses.json` is a dict of 53 classes,
+  whose entries carry an `rca` key. `tools/audit/fold_ledger.py` is the checker that reads it.
+- **Its measured cost.** 6 false or missed lines, 46 min of measured holds, and one duplicate
+  opus seat avoided by a hand check. Splitting is a standing move: 13 of 235 dispatched topics
+  split in 3 days.
+
+Cost:
+- The document's figure for the standing cost is about 0.5 s per 120 s relay pass. Only an aged
+  dispatch whose exact refs did not move pays one extra `ls-remote`.
+- New code: one new module in `tools/audit/seat`. Two consumers move their existing rules into
+  it unchanged, and two call sites change.
+- Tests: three rows, two null controls and two mutants.
+- Hot files: `cloud_relay.sh` is hot in round 10, and it enters R10-TICK-PR-BUCKETS's files.
+  That widens an M group that is `not-started`. It does not widen a group in flight.
+- No capped file is touched by this ruling.
+
+Binding:
+- **Why ACCEPT.** The class has three instances, so it owes a barrier (`defect-root-cause.md`).
+  The cost test, roughly 0.5 s a pass against 16 min times 0.3 a day plus a duplicate-seat risk,
+  picks a shared reader over a fourth per-site rule.
+- **Why this group.** R10-TICK-PR-BUCKETS would otherwise build a seventh site: its carry 6, and
+  b115-P375's definition of "a seat is on it", which reads handoff-wip by family.
+- **The fallback.** If the orchestrator routes the carry to R10-OPENER-REUSE, the same text
+  applies, and the set-files op names that group instead.

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
