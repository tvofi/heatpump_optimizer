# Review packet #3255
head: a8d19cf1950250e378b3cf0dfd4f8c5c29e01255
base: 9cbd7dd0d7a66163b5b593dfe55f1d8b220785de

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
arch-score / arch-score id=128232647084 success
budget-raise-gate / budget-raise-gate id=128232700869 success
cancel-superseded id=128232646854 success
codeql id=128232701174 skipped
codeql / Analyze (actions) id=128230601247 success
codeql / Analyze (javascript-typescript) id=128230551909 success
codeql / Analyze (python) id=128230590719 success
gate id=128232646122 success
governance id=128232647839 skipped
governance / delivery-status id=128230551171 success
governance / delivery-status-publish id=128230552176 skipped
governance / env-matrix id=128230551521 success
governance / instrument-self-tests id=128230551793 cancelled
governance / policy-docs id=128230605465 success
governance / record id=128230599044 skipped
governance / wave-script id=128230588153 success
hassfest id=128232647102 skipped
hassfest / hassfest id=128230588034 success
kernel-points id=128232647297 skipped
pr-contract id=128232647674 skipped
pr-contract / pr-contract id=128231701668 success
prelude id=128232646414 success
refresh id=128232694320 success
tests id=128232687283 skipped
tests / arch-instrument id=128230553339 success
tests / briefs id=128230601787 success
tests / browser id=128230553185 success
tests / ci-ratchet id=128230554824 skipped
tests / claims-autofix id=128230554618 skipped
tests / closure-scope id=128230551492 success
tests / closures id=128230552857 success
tests / closures-autofix id=128230553974 skipped
tests / coverage id=128230552951 success
tests / coverage-ratchet id=128230555189 success
tests / fast (3.14) id=128230552920 success
tests / graders-head-copy id=128230553513 success
tests / lane-proofs id=128230553749 success
tests / mutation id=128230601173 success
tests / mutation-autofix id=128230554032 skipped
tests / mutation-pins id=128230553117 skipped
tests / nightly-ha id=128230553393 skipped
tests / nightly-status id=128230551759 success
tests / replay id=128230552961 skipped
tests / typing id=128230552628 success
validate id=128232647108 skipped
validate / validate-hacs id=128230585464 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 5a56edc5: dismissed:drafted for the owner, nothing in this tree consumes it until approved.
NOTE body item 9871b246: dismissed:the cost number that would reverse the refusal is not produced by any group.
NOTE body item 16a28f20: dismissed:one instance does not make a class.
NOTE body item e64e5c55: dismissed:paid in this change.
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/policy_lint.mjs --stats --since v7.0.4
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 -I tools/audit/seat/r10_ledger_mutants.py --self-test
             `tools/audit/seat/r10_ledger_mutants.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head

FIGURES: 3 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/rules/ci-autofix.md b/.claude/rules/ci-autofix.md
index 0a7063317..efb4b6f00 100644
--- a/.claude/rules/ci-autofix.md
+++ b/.claude/rules/ci-autofix.md
@@ -65,9 +65,6 @@ every unrelated `fast` failure): its summary line is its only signal.
   `no-copies` and NOT-A-FILE failures fail recordings too, and their closures
   were never stale.
 
-  A failed recording reads files a clean run never does (`linecache`): an
-  UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.
-
 | Failure | Job | Commit subject | Code |
 |---|---|---|---|
 | `UNDER-SCOPED`, INERT READS | `closures-autofix` | `ci: re-record closures` | `closure.apply_under_scoped_recordings` |
@@ -79,8 +76,8 @@ a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the r
 until approved: all three jobs approve them (kept until M-3), fail-soft without their
 secrets, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
 
-When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants`
-stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
+When `mutation-autofix` goes red, run `--pin-killed` yourself. Until `mutation-pins` concludes the body says `unmeasured`;
+`pinned` only if `--pin-killed` ran on this head. A pin stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
 golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
 not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.
 
diff --git a/.cursor/rules/ci-autofix.mdc b/.cursor/rules/ci-autofix.mdc
index 5c3c2d1f5..3c4ed0ec2 100644
--- a/.cursor/rules/ci-autofix.mdc
+++ b/.cursor/rules/ci-autofix.mdc
@@ -60,9 +60,6 @@ every unrelated `fast` failure): its summary line is its only signal.
   `no-copies` and NOT-A-FILE failures fail recordings too, and their closures
   were never stale.
 
-  A failed recording reads files a clean run never does (`linecache`): an
-  UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.
-
 | Failure | Job | Commit subject | Code |
 |---|---|---|---|
 | `UNDER-SCOPED`, INERT READS | `closures-autofix` | `ci: re-record closures` | `closure.apply_under_scoped_recordings` |
@@ -74,8 +71,8 @@ a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the r
 until approved: all three jobs approve them (kept until M-3), fail-soft without their
 secrets, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
 
-When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants`
-stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
+When `mutation-autofix` goes red, run `--pin-killed` yourself. Until `mutation-pins` concludes the body says `unmeasured`;
+`pinned` only if `--pin-killed` ran on this head. A pin stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
 golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
 not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.
 
diff --git a/dev/audit/rca/R10-RCA-CLASS-OPEN.md b/dev/audit/rca/R10-RCA-CLASS-OPEN.md
new file mode 100644
index 000000000..2b16eb2a8
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-CLASS-OPEN.md
@@ -0,0 +1,136 @@
+# R10-RCA-CLASS-OPEN: the reviewer finds the next spelling of a class the change left open (#2950)
+
+The root-cause record for the recurring-friction key `class-open` (#2950, verdict
+class), which `R10-RCA-FRICTION-RESIDUE.md` section 6 measured at 6 PRs / 13
+entries (#2784) and left with "the countermeasure refusal stands".
+
+**Merge base and window.** Measured on 2026-11-06 at `origin/main`
+`7e8939d38`; window `v7.0.4..origin/main` (tag `b448d26063cd`), 517 merged
+PRs, 450 with a parsable verdict. The earlier record's 5.2-day window is a
+control, not a source.
+
+## 1. The count
+
+`node tools/policy/policy_lint.mjs --stats --since v7.0.4`: `class-open` **32 PRs
+/ 56 entries** (threshold 3), against 6 / 13 in the earlier record's window.
+Read comment by comment, the 56 entries are 55 distinct heads (#3223's last
+verdict was posted twice on the same head) on 32 PRs, so **23 repeat rounds**:
+the reviewer blocked the same PR on `class-open` more than once. Twelve PRs
+hold 35 of the 55 (#2697 6, #2925 5, #3085 4, #3049 3, #3223 3, and #2711,
+#2819, #2872, #2989, #3048, #3170, #3218 two each); 20 PRs hold one.
+
+PRs, by search over the window's merge list then a first-line read of each
+`blocked <sha> class-open:` comment (the search matched 34 PRs; #2698 and
+#2798 name the word elsewhere than as the verdict's class, so 32 remain,
+equal to the histogram): #2697, #2706, #2707, #2711, #2770, #2819, #2853,
+#2872, #2887, #2903, #2915, #2925, #2933, #2989, #3006, #3016, #3048, #3049,
+#3055, #3062, #3073, #3085, #3089, #3090, #3169, #3170, #3174, #3181, #3186,
+#3191, #3218, #3223.
+
+## 2. What the entries say
+
+Every first line names a *sibling spelling or site the change left open*, not
+a defect in what it changed:
+
+- Guards over text shapes, where the input space is open: #2697 (a merge-call
+  parser, six rounds: `gh  pr merge` double-space, quoted arm, case-arm writer,
+  wrapped argv), #3049 (parent-command redaction: space-delimited flags, then
+  glued `-cCODE`/`--eval=CODE`, then `-W/-X` values), #3048 and #3062 (a
+  change-history lexicon: four passages, then more in other docs, then
+  translated strings), #3223 (`seat-gh` blocking `issue comment 201`, then
+  `issue close --comment`, then `api` writes with case variants), #3055
+  (`bare_array.py` a never-empty reason after a mut marker).
+- Deletion and race guards over many sites: #3085 (`prune_refs`, then
+  `worktree_gc.sh` classes A, B and C, each a ref or HEAD that moved after
+  the read), #2989 (`open_pr.sh` two failure paths), #3089.
+- Production-code siblings: #2819 and #2872 (two code paths with the same
+  threshold or derate), #2887, #3006, #3170 (host-zone checks under other
+  zones), #3218.
+- Grader and key coverage: #2925 (five files outside the graders key, four
+  rounds).
+
+Of the 55 distinct entries the guard-and-lexicon shapes (nine PRs: #2697,
+#3049, #3048, #3062, #3223, #3055, #3085, #2989, #3089) hold **23**, and
+**14 of the 23 repeat rounds** (#2697 5, #3085 3, #3049 2, #3223 2, #3048 1,
+#2989 1), counted per PR from the distinct heads above.
+
+## 3. Named cause
+
+The fixer closes the instances the finder named and the class by *examples*:
+for a guard over a space of spellings (shell syntax, flags, option forms,
+case, quoting, refs that move), the fixer's enumeration of the class is
+manual, and the reviewer's adversarial enumeration is the first one that is
+independent. Each reviewer round produces the next sibling because neither
+side holds a *generated* corpus over the space: the fixer's harness is the
+finder's harness plus the ones the fixer thought of, and `fix-review.md`
+asks the reviewer to probe the class (step 10), which it does, once per
+round, by hand.
+
+This cause is **checked against the alternative** that class-open is the
+reviewer's vocabulary for any rework: it is not. The other 23 of the 32 PRs
+are not guards (for example #2819, #2872, #2887, #3006, #3170, #3218, #3174,
+#3186, #2853, #2915), and they hold 9 of the 23 repeat rounds: their siblings are sites in production code or docs, one
+round each, and are the ordinary cost of a review finding a second instance.
+Only the guard population repeats.
+
+## 4. Process state
+
+**(c)**: the process was followed and did not produce the intended result.
+`fixer.md` requires a class sweep and a null control, `fix-review.md` step 10
+refuses a class left open, and both were obeyed (the blocks quote the missed
+sibling and the fixer's next head covers it). The intended result, a class
+closed in one fixer round, is not produced for guards over open spaces,
+because a hand enumeration of an open space has no stopping point the
+fixer can verify. Not (b): the entries say the sweep was done. Not (a): the
+step and the word exist, #2561 taught them. Not (d): nothing changed
+underneath it. The rate rose: **6 / 173 = 3.5 %** of verdict-carrying PRs in the earlier
+record's window (its section 1 denominator) against **32 / 450 = 7.1 %** here, about twice.
+
+## 5. Cost test
+
+Defect: `R10-RCA-FRICTION-RESIDUE.md` section 2 measured `class-open` at a
+median **153 min** from block to next verdict (6 PRs; quoted, not re-timed).
+Repeat rounds in the window: 23 x 153 min = **3519 min**; of which guard
+shapes 14 x 153 = **2142 min**.
+
+Candidate countermeasure (not built; policy text and a per-PR cost): for a PR
+that adds or changes a guard that classifies text by shape (parser, redaction,
+allow-list, lexicon), the fixer drives the real guard over a *generated*
+spelling corpus (case, quoting, glued options, wrapping, delimiters) and
+states the corpus size in the body, and the reviewer's surviving siblings are
+added to the corpus. Standing cost: the fixer's time per guard PR, which this
+record cannot measure from the window (no PR reports the time its sweep took).
+If the corpus costs one review round (153 min) per guard PR, the nine guard
+PRs cost 1377 min against 2142 min of guard repeat rounds, so it pays only if
+it removes at least 64 % of them. No measurement of the removal rate exists; the closest evidence
+is that #2697's six rounds closed only when the parser was rewritten around
+the grammar rather than patched by spelling, which is the shape of the
+candidate but one instance.
+
+## 6. Decision: recorded refusal, with the numbers, owner informed
+
+The candidate passes the cost test only at a removal rate the window cannot
+confirm and changes `fixer.md`, which is policy and capped. Per
+`defect-root-cause.md` ("policy changes only with the owner's approval"), this
+record **does not land it**: it drafts the wording below and routes the
+decision, with the numbers, to the owner. The earlier refusals
+(`R10-RCA-FRICTION-RESIDUE.md` section 6; `R10-RCA-HARNESS-FRICTION.md`
+section 8: a per-child check) priced 6 PRs; at 32 PRs / 3519 min the same
+refusal's price side has moved 5x. It is not reopened as "built"; it is
+reopened as "owed a ruling".
+
+Draft sentence for `fixer.md` step 5, if the owner approves:
+"A guard that classifies text by shape is driven over a generated spelling
+corpus (case, quoting, glued options, delimiters, wrapping) with the corpus
+size named in the body; a spelling the reviewer finds is added to it."
+
+**Waiting on the owner's ruling** for that sentence; nothing else is waiting.
+
+## 7. Not established here
+
+- The removal rate is unknown; so is the fixer-side cost.
+- The shape split (guard vs production) is by first-line text read, not a
+  mechanical classifier; a re-count by another reader may differ by a PR or
+  two. The totals (32 / 56 / 23) are the histogram's.
+- Whether the twofold rate rise has a cause beyond more guard PRs in the
+  round is not established.
diff --git a/dev/audit/rca/R10-RCA-FRICTION-SWEEP.md b/dev/audit/rca/R10-RCA-FRICTION-SWEEP.md
new file mode 100644
index 000000000..ed2cc04f8
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-FRICTION-SWEEP.md
@@ -0,0 +1,177 @@
+# R10-RCA-FRICTION-SWEEP: sufficiency of the existing friction records, the landed countermeasures, and three carried measurements
+
+The ledger record for the group that answers the recurring-friction keys
+`R10-FRICTION-REGRESSION` left owed. One record per key sits in its own file
+(`R10-RCA-ROOT-CAUSE-DETECTABLE.md` #2875 and #2865, `R10-RCA-CLASS-OPEN.md`
+#2950, `R10-RCA-MUTATION-VACUOUS.md` #2998 and #2942). This file judges the four
+records that already existed, answers the carried measurements that have no
+key of their own, and shows the demonstrations for the policy tooling this
+group lands.
+
+**Merge base and window.** All figures measured 2026-11-06 at `origin/main`
+`7e8939d38`, window `v7.0.4..origin/main` (tag `b448d26063cd`): 517 merged
+pull requests, 450 with a parsable verdict, from `node tools/policy/policy_lint.mjs
+--stats --since v7.0.4` (the walk takes about 11 minutes). Earlier records'
+windows are controls.
+
+## 1. The four existing records, judged for sufficiency (not rewritten)
+
+Each is judged against `root-cause.md`: a named cause, a process state, a cost
+test with numbers, a countermeasure or a recorded refusal. All four carry all
+four. They are left as they are; the re-measure at this base is appended
+here, never into them.
+
+| record | issue | verdict | why, and the re-measure at this base |
+|---|---|---|---|
+| `R10-RCA-MUTATION-SURVIVOR.md` | #2840 | **sufficient** | cause (autofix pins kills only), state (c), cost test (P = 4/28, 161 min), countermeasure B landed, C carried, A refused. Key now reads `mutation-survivor` **9 PRs / 11 entries** (#2579, #2817, #2820, #2912, #2962, #3001, #3097, #3150, #3153): recurring, but its tools/ population is the one `R10-RCA-MUTATION-VACUOUS.md` section 5 re-prices, and C is the group's `R10-FLY-LEDGER-SAMPLE`'s. Not credited or refuted: which of the 9 are on heads after B landed is not derived. |
+| `R10-FRICTION-GATE-SCOPING.md` | #2835 | **sufficient, with section 2 below** | cause (inherited `BASH_ENV` re-prepends the toolchain), states (d)/(c)/(b), a countermeasure landed (`_stub_path_env` and its red/green check). It prices 10 PRs / 11 entries; the key reads **12 / 13** now. |
+| `R10-RCA-FIXER-MD-KEY.md` | #2895 | **sufficient** | cause (cloud seats lack the toolchain the prompt promises), state (d), cost estimate labelled untimed (5-15 min), the session-start `toolchain:` hook built, owner action named. Key now reads `tools/audit/briefs/fixer.md` **17 PRs / 25 entries** against its 8 / 11. The record found one group (A) owed a defect; the growth is not decomposed here and was not the question. This session's own start-up printed the `toolchain:` line and `cloud-setup.sh --check` read OK: one observed instance of the hook doing its job, not a measurement. |
+| `R10-RCA-FRICTION-CLAIM-FALSE.md` | #2907 | **sufficient** | cause (a ruling cites figures and never runs its stated rule on its instances), states (a)/(b)/(d), the one-sentence `proposal-triage.md` countermeasure landed. Key now reads `claim-false` **5 PRs / 9 entries** (4 PRs in its window). Whether the 5th is after the sentence landed is not derived. |
+
+`R10-RCA-FRICTION-REGRESSION.md` (#2860) landed in #3000 and is not part of
+this judgement; the key now reads `regression` 4 PRs / 4 entries (3 in its
+window). The record's `L` mechanism (a CI browser lane no local path runs) is
+the same shape as `R10-RCA-ROOT-CAUSE-DETECTABLE.md`'s cause A.
+
+## 2. #2835 on `gate-scoping.md`: Carry 7's measurement (measure first)
+
+The carry asks: name the PRs and the rule hit each made, then decide whether
+the keying rule or the gate changes. It was written when the key read 6 PRs.
+At this base `.claude/rules/gate-scoping.md` reads **12 PRs / 13 entries**
+(threshold 3).
+
+Entries named in PR bodies' `## Friction` sections, read by body search over
+the window and then each line: BASH_ENV `#2698, #2707, #2834, #2837`;
+interpreter `#2627, #2870`; lease and runtime `#2873` (two entries),
+**`#2968`**; closures recording `#2780`; no step for the check `#2622, #2700`.
+That is 11 PRs; `#2968` is the only one the existing record does not name
+(its entry: the scoped gate "outlives the 30-minute background-task limit",
+`arch_score.py` alone 1407 s). The 12th PR the histogram counts was **not
+identified** by this search; the record does not claim it.
+
+Decision on the carry's question:
+
+- **The keying rule does not change.** The key is the rule file; the 12 PRs
+  fall into five causes (BASH_ENV 4, interpreter 2, lease/runtime 2, closures
+  recording 1, no step 2) and one unidentified. Splitting by cause leaves
+  BASH_ENV at 4 and everything else below 3, which is the existing record's
+  finding.
+- **The gate does not change for #2968 and #2873's runtime half.** Two PRs of
+  "the scoped gate outlives a 30-minute cap": below the threshold of 3, and the
+  cap is a property of the seat's background-task limit, not of the gate. This
+  seat's own brief says to wait with Monitor windows up to an hour, which is
+  the working answer for a seat that has one. Refused at 2 instances; the cost
+  test, with the one measured number (1407 s for one script), is: standing cost
+  of a gate change > 0, defect cost = one re-run, P below the class threshold.
+- BASH_ENV (4 PRs) is the landed countermeasure's, unchanged.
+
+## 3. Carry 4: the `R10-FLOW-ANDON` cost test against `R10-RCA-ORCH-CONTINUITY.md`
+
+`R10-RCA-ORCH-CONTINUITY.md` (state (a): liveness is not readable from origin)
+records no cost test against R10-FLOW-ANDON (`git grep -i andon -- dev/audit/rca/`
+is empty). The study's countermeasure was **built after the record**:
+`dev/programme/delivery/2582.md` (#2582, merged `fea3d3c`) added
+`tick_loop.sh`'s per-pass `heartbeat.sh --once`, which pushes
+`heartbeat/orchestrator` to a commit whose message is the pass line
+(`TICK-PASS <time> relay=<rc> tick=<rc> code=<code> behind=<n>`), bounded by
+`timeout 60`, failure printed and never fatal (`tools/audit/seat/tick_loop.sh`
+line 174). The off-host watcher that alerts when the ref is older than 20
+minutes is "an owner-scheduled cloud task", outside the tree.
+
+Cost test, in the unit of the record it answers (wall-clock per day), with
+the record's own measured figures quoted and labelled:
+
+- Defect: **3.0 h/day** idle (4 incidents in 6.33 days, mean idle 3.9 h;
+  `R10-RCA-ORCH-CONTINUITY.md`).
+- That record's cost for the off-host hourly check is **3.3 min/day**. A
+  20-minute bound is three checks an hour; scaled linearly it is **9.9 min/day**
+  (arithmetic on a quoted figure, not a measurement).
+- Standing cost of the heartbeat push itself: bounded by 60 s per tick pass;
+  the pass frequency is not stated in the tree, so a per-day figure is not
+  computed. The bound makes a failed push cost at most that, once per pass.
+
+`9.9 min/day < 180 min/day x P` holds for any `P > 0.055` (about one day in
+eighteen with a stop); the measured rate was 4 in 6.33 days. The decision:
+**the countermeasure was right to build and stays**; nothing is rebuilt.
+
+A reading of the live ref, since a record about continuity should read it:
+`heartbeat/orchestrator` on origin had a committer date of 2026-11-06
+11:25 UTC when read at 12:03 UTC, **38 minutes** old and past the 20-minute
+bound. Whether that is a stop or a quiet period, and whether the off-host
+watcher exists and alerted, is not established here (the watcher is outside
+the tree); it is stated so the owner can look.
+
+## 4. The landed countermeasures (Carry 2) and their demonstrations
+
+Approved by tvofi on 2026-10-29 ("All of these are approved.", quoted in the
+brief). Re-measured at this base with `node tools/policy/policy_lint.mjs
+--stats --since v7.0.4`, before the change and after; the record
+`R10-RCA-FRICTION-RESIDUE.md`'s figures are snapshots.
+
+**(1) #2436, a derived `other (untaught)` family** in `policy_lint.mjs`'s
+`statsFamilies`: every verdict-histogram key `VERDICT_CLASSES` does not teach,
+other than the passing verdict, members computed at read time, the #2410
+subtraction applied. After: `other (untaught) (family)` **65 PRs / 78 entries**
+(of a union of 121; nine untaught words that file their own, `ci-red`,
+`body-stale`, `defect`, `claim-refuted`, `regression`, `mutation-survivor`,
+`figure-wrong`, `merge-conflict` and `claim-false`, are subtracted), over
+threshold, would open once. Against the earlier record's 46 PRs at a 218-PR
+window this is the same shape at a window 2.4 times longer. Control, by diff
+of the two runs' non-family rows: **every taught and every id row prints
+byte-identically** (`diff` empty), and the literal `other` row still reads
+2 PRs / 3 entries.
+
+**(2) #2437, a declared `root-cause` family** over
+`root-cause-unanswered`, `-detectable`, `-unrecorded`. After: union 21 PRs;
+all three members file their own line (5, 12, 5), so the #2410 subtraction
+takes all 21 and the family row reads **0 PRs / 0 entries (of 21)** and does
+not fire. The earlier record's prediction (union 6, family 3) was for a window
+in which only one member filed; at this base every member does. That is the
+family working as designed, and it is recorded plainly: **in this window it
+adds no filing**, and it is the case the map exists for the day a window splits
+the obligation across words at 1 and 2 each.
+
+**(3) #2429, `ci-autofix.md`**: the wait is bounded (until `mutation-pins`
+concludes the body says `unmeasured`), and a body says `pinned` only when
+`--pin-killed` ran on this head. The file's cap
+(`dev/governance/config/policy_budgets.json`) had 3 tokens of headroom. The
+rule keeps "(kept until M-3)" (`ci.yml`, `tests.yml`, `merge-main.yml` and
+`HANDOVER.md` still say "until M-3") and "the reviewer re-checks it". The two
+new sentences were shortened, and the cap was still exceeded, so the paragraph
+about `linecache` artefacts in the failed-recording bullet is deleted: a policy
+change the 2026-10-29 approval does not cover, named under `## Approval` in the
+body. Its action half ("fix it first") stays in the bullet above; the warning
+that an UNDER-SCOPED beside a failed recording may be an artefact is gone.
+`.claude/rules/` and `.cursor/rules/` are regenerated by
+`node tools/policy/rules_sync.mjs`.
+
+**Fixture pins and mutation proof.** `policy_lint.mjs` acceptance gains three
+pins. (i) The fold: three untaught words on one PR each fire the derived family
+at 3; a taught word and the passing verdict are out; a word that files alone is
+subtracted; with no derived list there is no row; the three root-cause words
+fold to 3. (ii) The wiring: `statsFindings` driven over synthetic merged PRs
+yields exactly one `verdict family` would-open for `other (untaught)` for three
+untaught words, exactly one for `mutation` for `mutation-unpinned`,
+`unpinned-site` and `mutation-survivors`, and none for a taught-only window.
+(iii) `cmdStats` builds its table from the shared `derivedInput`. Mutants, each
+run with `node tools/policy/policy_lint.mjs` and restored byte for byte, the
+unmutated tree as the null control (rc 0): `statsFindings` passing `null`
+(killed), `cmdStats` passing no derived list (killed), `mutation-unpinned`
+dropped from the family (killed), all three spellings dropped (killed),
+`unpinned-site` and `mutation-survivors` dropped (killed), passing-verdict
+exclusion removed and `root-cause-unrecorded` removed (killed by (i)).
+
+## 4b. #3156 (`ci-red`): not disposed by this group
+
+The group's `issues` lists #3156, which asks for a record of the `ci-red`
+friction key. This group lands no record for it: `ci-red` appears here only as
+an example word. It is not a countermeasure of the four records above, and a
+`ci-red` record needs its own measurement of the key's PRs. Disposition:
+re-route #3156 to its own group; the delivery must not close it from this PR.
+
+## 5. Not established here
+
+- The 12th gate-scoping PR (section 2).
+- Whether the off-host heartbeat watcher exists (section 3).
+- For each existing record, which re-measured entries fall after its
+  countermeasure landed (section 1).
diff --git a/dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md b/dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md
new file mode 100644
index 000000000..9016c8c5e
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md
@@ -0,0 +1,187 @@
+# R10-RCA-MUTATION-VACUOUS: the reviewer's hand mutant survives, in two populations (#2998, #2660, #2942)
+
+The root-cause record for the recurring-friction key `mutation-vacuous` (#2998,
+refiled after #2660 closed with `R10-RCA-FRICTION-RESIDUE.md`) and for the
+`mutation (family)` refiling #2942 (Carry 3 and Carry 6 of this group). It lands
+one tooling change to the family map and records one refusal.
+
+**Merge base and window.** Measured on 2026-11-06 at `origin/main`
+`7e8939d38`. Window `v7.0.4..origin/main` (tag `b448d26063cd`), 517 merged PRs,
+450 carrying a parsable verdict. The earlier records quote `v7.0.5` and
+`92588d581` figures; they are controls here, not sources.
+
+## 1. The count
+
+`node tools/policy/policy_lint.mjs --stats --since v7.0.4`:
+
+- `mutation-vacuous`: **31 PRs / 38 entries**, threshold 3.
+- `mutation-survivor`: 9 PRs / 11 entries.
+- `mutation (family)`: 1 PR / 2 entries, "of 41; mutation-vacuous,
+  mutation-survivor file their own" (the #2410 subtraction working).
+
+The 31 PRs, read from the first line of each `Fix review: blocked <sha>
+mutation-vacuous:` comment (search over the window's merge list, then each line
+read; equal to the histogram's 31): #2580, #2605, #2645, #2647, #2697, #2709,
+#2712, #2832, #2873, #2916, #2919, #2920, #2937, #2968, #2978, #3004, #3016,
+#3042, #3047, #3054, #3075, #3078, #3089, #3149, #3164, #3184, #3193, #3217,
+#3219, #3221, #3231. Each carries a `git diff --name-only <first parent>
+<merge>` over `custom_components/` (below).
+
+Control: `#2660`'s own reading, "held: 7/8 before `662a380`, 1/1 after", does
+not hold over this window. Merge dates: 5 PRs merged before `662a380`
+(2026-10-25) and **26 after**, so the key did not fall; it came back at a
+higher rate. 38 entries on 31 PRs is 7 repeat rounds.
+
+## 2. Two populations, split by what the PR changes
+
+By merge diff (a merge date is an upper bound for "heads pushed after"; the
+PR's last head is not re-derived):
+
+| population | PRs | after `662a380` | merged after `42b23e493` (#3059, 2026-11-01) |
+|---|---|---|---|
+| changes `custom_components/` | #2647, #2712, #2832, #2873, #2919, #2968, #3016, #3047, #3078, #3184, #3193, #3219, #3231 (13) | 12 | 6: #3047, #3078, #3184, #3193, #3219, #3231 |
+| changes only `tools/`, `tests/` or docs | the other 18 | 14 | 7: #3054, #3075, #3089, #3149, #3164, #3217, #3221 |
+
+### Population C (`custom_components/`, 13)
+
+The reviewer's surviving mutants are deletions of guards or defaults in the
+production code: `_ATTRIBUTE_TARGET_DOMAINS` losing `water_heater` (#3231),
+`freq_control.py:228` GUARD_OFF (#3184), `_solve_hubs` default ruling (#3193),
+`coordinator.py` `local_tz` (#3016), `diagnostics._over_age` (#2873). This is
+the population `mutation-autofix` and `tests/mutation_table.py` cover.
+Countermeasure C (`mutation-autofix` reddens on a site left alive, #3059,
+`42b23e493`) is in force from that SHA. Six C-population PRs merged after it
+still blocked on a survivor, so the autofix going red did not stop the
+reviewer finding one the author had not pinned: the two are different
+detectors. The autofix pins what a *driver kills*; #3231's mutant survives
+every driver, the body's claim ("killed by ...") was wrong or unmeasured
+(compare #3184: "survives every suite check, including the one the body names
+as its killer"; #2832: "the body names 655 as killed by...").
+
+### Population T (`tools/`, 18)
+
+The mutants are the reviewer's hand mutants of seat tooling's own self-tests:
+`ci-watch.sh sleep "$POLL_S"` (#2937), `check_scopes.py main()` exit bypass
+(#3149), `prepr.sh` `merged_steps` call (#3221), `confirmGapMerge` guard
+(#3217), the `cloud_relay.sh` freeze bypass (#3089). These are outside
+`mutation_table.py` (which covers `custom_components/`) and outside
+`mutation-autofix`: `R10-RCA-MUTATION-SURVIVOR.md` (#2961) priced them on two
+instances and refused. This window has 18.
+
+## 3. Named cause
+
+**C:** the body asserts a pin ("killed by X") the author did not measure on
+this head; the autofix's red is a late, per-site detector and the claim is
+what the reviewer re-measures. `ci-autofix.md` (this PR) now requires that a
+body says `pinned` only when `--pin-killed` ran on this head, which addresses
+the claim, not the survivor.
+
+**T:** a self-test for seat tooling is judged by whether it kills the plants
+its author wrote, and the reviewer's *next* plant is the finding. The tools
+have no mutation measurement at all (the `tests/mutation_budgets.json` and
+`mutation_table.py` machinery is `custom_components/`-only), so every
+reviewer round on a tool is the only mutation measurement the tool gets.
+
+## 4. Process state
+
+**C: (c).** `#2660`'s countermeasure (`662a380`, `fixer.md` wording) was
+obeyed in form and did not produce the result; C's later countermeasure
+(`42b23e493`, autofix red on a left-alive site) is a second layer. The key
+did not fall after either.
+
+**T: (a).** For tools there is no mutation process to follow or not;
+`R10-RCA-MUTATION-SURVIVOR.md` found the same and refused on cost.
+
+## 5. Cost test, re-priced
+
+Defect cost: `R10-RCA-FRICTION-RESIDUE.md` section 2 measured
+`mutation-vacuous`'s median time from block to next verdict at **111 min**
+(a labelled quote from that record, 8 PRs; not re-measured). The window has
+38 entries on 31 PRs; each first entry is a block that costs one fixer round
+and one review round, so ~31 x 111 min = 3441 min, of which the repeat rounds
+(7) are 777 min.
+
+**T, 18 PRs.** `R10-RCA-MUTATION-SURVIVOR.md` refused a local mutation arm
+for tools/ with `840 min/window` standing cost against a `644 min` defect on 2
+PRs ("Local --pin-killed refused"). Re-priced at 18 PRs, the defect side is
+18 x 111 = **1998 min**, against the same 840 min standing cost *if the
+arm's cost scaled the same way* - which it does not know: the 840 min was
+priced for `custom_components/` pins and tools have no table to pin. A cost
+test needs an arm that exists; none does. The recorded decision is therefore:
+**do not build a tools/ mutation arm now**; the cost side is unknown, not
+high, and the defect side has moved from 644 to 1998 min. What changes the
+answer is a measured cost of a tools/ mutation table, which no seat has
+produced.
+
+This is a **refusal that depends on a number nobody has**, so it is not
+closed: the owner may want a seat to price a `tools/` mutation table (plants
+registered per tool, the shape `r10_*_mutants.py` already has for four
+drivers). Waiting on that ruling is stated in the body.
+
+**C, 13 PRs.** 6 merged after #3059. Count for crediting the countermeasure:
+entries on heads pushed after `42b23e493`; the merge date is the only data
+here and over-counts. It is not credited; #3059 is not shown to have failed
+either: its red names an unpinned site the author left alive, the six reviewer
+mutants are survivors the author did not know existed.
+
+## 6. #2942, the `mutation (family)` refiling: a new cause, not state (c) of the old one
+
+The question (Carry 3): is the refiling the same cause (then the #2410
+countermeasure failed) or a new one?
+
+`#2410`'s countermeasure is the subtraction: the family counts only what no
+member files. It still works as built: the family row reads 1 PR / 2 entries
+"of 41", with the two filing members subtracted. Control: without the
+subtraction the union would be 41.
+
+The refiling comes from a different place, the member list. The reviewer
+vocabulary produced three more spellings of the mutation obligation in this
+window, none a member, each its own unfiled row:
+
+| spelling | PRs (first-line reads) |
+|---|---|
+| `mutation-unpinned` | #2632, #2997 |
+| `unpinned-site` | #2629, #3143 |
+| `mutation-survivors` | #2917 |
+
+None of those five is among the 31 `mutation-vacuous` or 9 `mutation-survivor`
+PRs, so the subtraction takes none of them: with the three words declared
+members, the family residual goes from **1 to 6 PRs** (5 + the 1 `vacuous-test`
+PR it already holds) and fires at the threshold of 3. That is the shape
+`R10-RCA-FRICTION-RESIDUE.md` section 4 named for `other`: the declared list
+is a closed enumeration, and the spelling moves.
+
+**Process state: (c)** for the list - the family exists, was extended once by
+measured synonyms (#2561 section 5), and is obeyed; its unit is a word list
+that goes stale as the reviewer coins new words. It is the declared half of
+the problem the derived family `other (untaught)` (this PR, #2436) solves for
+all untaught words at once; the two words that are *obligation-specific*
+(mutation) still belong in the declared family, because the derived family is
+one row for every untaught word and the obligation here has a name.
+
+**Countermeasure (landed):** `FRICTION_FAMILIES.mutation` gains
+`mutation-unpinned`, `unpinned-site`, `mutation-survivors`. Demonstration, measured
+with `--stats --since v7.0.4` before and after: the `mutation (family)` row
+1 PR / 2 entries (of 41) -> **6 PRs / 7 entries (of 46)**, over threshold, one
+would-open line; controls: every other row prints byte-identically
+(`policy_lint.mjs` acceptance: 267 pins, 0 errors), and the family-pinning
+fixture windows (`friction-families.json`) carry no new word. It is a
+tooling edit to a declared list; per `ratchet-budgets.md` it adds no policy
+text.
+
+## 7. #2998 itself
+
+Disposition: the key is real and not `#2660`-held. Population C is reviewed
+above (countermeasure in force, not credited, not refuted). Population T is a
+recorded refusal that waits on a number (section 5). The family refiling #2942
+is a new cause, countermeasure landed (section 6). The T-population refusal
+is a recorded result of the cost test, with the number that would reverse it
+named (the unpriced cost of a `tools/` mutation table); the owner may order
+that pricing, and nothing else here waits on a ruling.
+
+## 8. Not established here
+
+- "Heads pushed after #3059" is not derived; merge dates stand in and
+  over-count.
+- Median 111 min is quoted from `R10-RCA-FRICTION-RESIDUE.md`; not re-timed.
+- The cost of a `tools/` mutation table is unpriced.
diff --git a/dev/audit/rca/R10-RCA-ROOT-CAUSE-DETECTABLE.md b/dev/audit/rca/R10-RCA-ROOT-CAUSE-DETECTABLE.md
new file mode 100644
index 000000000..b5bd63c8b
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-ROOT-CAUSE-DETECTABLE.md
@@ -0,0 +1,188 @@
+# R10-RCA-ROOT-CAUSE-DETECTABLE: a red check the body did not answer, and the seat mutant self-tests no local path ran (#2875, #2865)
+
+The root-cause record for the recurring-friction key `root-cause-detectable`
+(#2875) and for the red-check trigger on #2865 (Carry 5 of this group), which
+`dev/governance/roles/root-cause.md` and `dev/governance/rules/defect-root-cause.md`
+owe. It lands one countermeasure, in `tools/pr/ci_predict.py`.
+
+**Merge base and window.** Measured on 2026-11-06 at `origin/main`
+`7e8939d38`. Window `v7.0.4..origin/main`, tag `v7.0.4` =
+`b448d26063cdb56aef915ceb604b807a885f9d71`. Instrument:
+`node tools/policy/policy_lint.mjs --stats --since v7.0.4`, 517 merged pull
+requests, 450 carrying a parsable verdict. Nothing is carried from earlier
+records: the figures in `R10-RCA-FRICTION-RESIDUE.md` (3 PRs, 5.2 days) are a
+control, not a source.
+
+## 1. The count, and the 12 instances
+
+`root-cause-detectable` reads **12 PRs / 12 entries** (threshold 3), the
+sibling words `root-cause-unrecorded` 5 / 6 and `root-cause-unanswered` 5 / 5.
+Twelve pull requests are named by the first line of a `Fix review: blocked <sha>
+root-cause-detectable:` comment (gathered by comment search over the window's
+merge list, then each first line read; the count equals the histogram's):
+
+| check that was red | PRs | the cheaper detector the reviewer named |
+|---|---|---|
+| `governance / instrument-self-tests` | #2664, #2870, #3049, #3200, #3221 | `ref_privacy.py --check` (#2664); `selftest_wiring.py --check` (#2870); the PR's own `gh_calls` self-test (#3049); `r10_ledger_mutants.py` T3 anchor (#3200); the line for #3221 names the job only |
+| `tests / closures` family | #2869 (`closure.py` selftest, "about three seconds"), #2883 (INERT READS), #3206 (names the job only) | `python3 tests/closure.py` selftest / the scoped gate |
+| `tests / fast` | #3051, #3066 (`harness_headers.py`, 0.7 s via `inline_scan`), #2873 (`card.mjs`, 118 s) | `tests/harness_headers.py`; `node tests/card.mjs` |
+| `pr-contract` | #2841 | `tools/pr/preflight.sh`, seconds |
+
+Control: a class word with no instance in the window (`version`) counts 0 by the
+same search, and the search reproduces the histogram's 12 exactly.
+
+## 2. Named cause
+
+There are two causes under one word, and they are separable by what the
+reviewer wrote.
+
+**Cause A (nine of twelve): a CI job that no local path predicts.**
+`tools/pr/ci_predict.py` is the local predictor `prepr.sh` runs for the CI
+jobs a seat cannot see. Its `instrument` arm predicted two of the dozens of
+checks `governance / instrument-self-tests` runs: `ref_privacy.py --check`
+(`privacy_preds`) and `selftest_wiring.py --check` (`wiring_preds`). Each
+instance in the instrument row is the next check of the same job that the arm
+does not run. #2664 and #2870 are the two it now predicts; both were added
+after the instance that exposed them (`R10-RCA-2671-WAVE-SCRIPT.md`
+countermeasure B, #2870's repair). #3200 and #2865 are a third: the seat
+mutant drivers.
+
+**Cause B (the body column, all twelve): the answer is owed before the red is
+knowable.** The body is written and pushed at handoff, before the pull request
+exists and before CI has run; the trigger is enforced by the reviewer reading
+the PR's checks afterwards. A seat that has no local detector for a red check
+cannot answer it in the body, so every instance of Cause A is also an instance
+of B. The instances whose detector *did* exist locally (#2841, #2869, #3051,
+#3066: `preflight.sh`, `closure.py`, `harness_headers.py`) are cause B alone:
+the detector ran in the scoped gate or in `prepr.sh`, was not run, or its red
+was not carried into `## Red checks`. This record does not establish which of
+the three for each; the reviewer lines do not say.
+
+## 3. #2865, reproduced: why the mutant self-tests are Cause A
+
+`#2865` (R10-ORCH-DISPATCH-REG) went red on `governance / instrument-self-tests`
+(run 40368808901, job 121733907279: `FAIL T3_review_owed_silent: anchor occurs
+once in tools/audit/seat/orchestrator_tick.py`) because an edit to a planted
+file moved a seat mutant's anchor. At this base:
+
+- `governance.yml` runs four drivers, `r10_roster_ops_mutants.py`,
+  `r10_stamp_round_mutants.py`, `r10_ledger_mutants.py` and
+  `r10_mandate_guard_mutants.py`, each with `--self-test`.
+- Each driver refuses to start when a plant's anchor no longer occurs exactly
+  once in its target (the `ck(... anchor occurs once ...)` line,
+  `r10_ledger_mutants.py:128`). The plants live in files other than the driver,
+  so an ordinary edit to `ledger.py`, `orchestrator_tick.py`, `cloud_relay.sh`,
+  `stamp.py` or the roster library can break a driver the author never touched.
+- `tools/pr/prepr.sh` calls none of them, and `ci_predict.py` predicted none:
+  `wiring_preds` and `privacy_preds` were the whole `instrument` arm.
+
+Timings measured here, one run each: roster_ops 1.13 s, stamp_round 0.33 s,
+ledger 0.71 s, mandate_guard 0.10 s; **2.28 s for the four**.
+
+**Why it is a reach problem and not a rule problem.** The mutants are, by
+design, hand mutants of *other* files (`r10_ledger_mutants.py` docstring: "each
+plant is one exact one-occurrence replacement in one of the files the ledger
+change touched"). A PR that edits `orchestrator_tick.py` has no reason to open
+`r10_ledger_mutants.py`. The instruments guide lists the drivers; nothing
+connects a changed target to the driver that plants into it.
+
+## 4. Process state
+
+**(c): the process was followed and did not produce the intended result.**
+`prepr.sh` step 6d runs `ci_predict.py` precisely to predict the jobs CI runs
+that a seat cannot; it was run, it predicted green, and `instrument-self-tests`
+went red. The arm's *unit* was two named checks of a job that has dozens
+(`governance.yml` lines 767-796 alone run four mutant drivers); it was
+extended once per instance, each time to the one check that had just failed.
+Not (a): the predictor existed for this job. Not (b): #2865's body ran
+`prepr.sh` and named the cheaper detector. Not (d): nothing changed
+underneath the arm; its coverage of the job was always partial.
+
+The reviewer's own disposition on #2865 was to route the countermeasure to the
+orchestrator's root-cause routing, which never happened; this is that record.
+
+## 5. How far the class reaches
+
+The class is "a job with N checks, a predictor with k < N of them".
+`governance / instrument-self-tests` is the measured case (5 of the 12). The
+same job runs other `--self-test` lines, for example `gh_calls`, `ledger`,
+`orchestrator_tick`, `plan_page`, `pr_args`, `pr_cap`, `open_driver`,
+`proof_watch`, `prune_refs`: **a PR that edits one of those files fails its own
+self-test**, as #3049 did. That wider arm (run the `--self-test` of every wired
+instrument the diff changes) is not built here: of the 12 instances it would
+have caught one beyond those now predicted (#3049), its standing cost per run
+is unmeasured, and one instance does not make a class. It is recorded as the
+next step if a second PR (not #3049) fails its own instrument self-test in a
+window after this lands. The `closures` family (3 PRs) and `fast` (3 PRs) rows
+are the other jobs and are not this record's: the detectors those reviewers
+name are in the scoped gate.
+
+## 6. Cost test
+
+`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock,
+per occurrence.
+
+- **Defect cost.** `R10-RCA-FRICTION-RESIDUE.md` section 2 measured the median
+  time from a `root-cause-detectable` block to the next verdict at **181 min**
+  (3 PRs, `v7.0.4` at its base). Not re-measured: the per-PR fetch it used is
+  not re-run here; the figure is labelled as that record's.
+- **P(recurrence).** The mutant-driver shape has two instances in the window
+  (#2865 and #3200); 2 of 517 merged pull requests. The class word as a
+  whole: 12 of 450 verdict-carrying PRs, 2.7 %.
+- **Standing cost.** The new arm runs a driver only when the diff touches a
+  file the driver quotes as a plant target (or the driver itself): at most
+  2.28 s, only for such a diff; every other diff pays a file read and a regex.
+  Even charged to every one of the 517 merges the ceiling is 517 x 2.28 s =
+  19.6 min, against 2 x 181 min = 362 min of defect for the two instances
+  alone.
+
+The test passes with a margin of about 18x at its worst-case ceiling, so the
+countermeasure is built.
+
+## 7. Countermeasure (landed): the `mutants` arm
+
+`tools/pr/ci_predict.py`: `mutant_preds(root, changed)`, registered in `ARMS`
+as `mutants` and called from `predict`. It reads which drivers
+`governance.yml` runs, takes each driver's plant targets as the repository
+paths its source quotes (plus itself), and runs `--self-test` only for a driver
+with a target in the diff. A red is `("instrument", "SEAT MUTANT SELF-TEST
+<driver>: <first FAIL line>")`, the job the CI red is filed under.
+
+Addresses state **(c)**: it changes the unit of the arm (a driver whose target
+moved), not the arm count.
+
+**Demonstration, both runs.** `python3 tools/pr/ci_predict.py --self-test`
+carries three new rows over a planted driver and target:
+
+```
+  ok   a planted target edited so its anchor is gone is predicted red
+  ok   the same target with its anchor intact is predicted green
+  ok   null control: a diff touching no planted target runs no driver (the anchor is gone, no red)
+```
+
+Against the real tree at this base, with `orchestrator_tick.py` in the
+changed set: intact tree -> `[]`; with `r10_ledger_mutants.py`'s own T-plant
+anchor duplicated into `orchestrator_tick.py` ->
+`[('instrument', 'SEAT MUTANT SELF-TEST r10_ledger_mutants.py: FAIL T1_unkinded_printed: the mutant parses')]`;
+changed set `{README.md}` -> `[]`. The file was restored byte for byte
+afterwards.
+
+**Mutation proof.** With the driver-selection line replaced by `if False:`
+(always run), the null-control row fails and the self-test is red; the file
+was restored (`cmp` against a copy).
+
+**Not claimed.** The arm is not a plant at the `predict` call site (the
+`ARMS` tuple and the `arms` table carry it, the self-test drives the helper).
+The follow-up row in the call-site plant table is the standing shape
+(`#1591`'s lesson); it is not added here, so a deleted `mutants` entry in
+`arms` would leave the helper green. That gap is stated, not hidden.
+
+## 8. Not established here
+
+- Which of #2841, #2869, #3051, #3066 were failures to run a local detector
+  and which were failures to write the result into `## Red checks`: the
+  reviewer lines do not say.
+- Cause B has no countermeasure recorded here beyond the arm: a body cannot
+  answer a red it cannot see, and writing a guess into `## Red checks` would be
+  the false-answer defect `defect-root-cause.md` enforcement exists to prevent.
+- #3221 and #3206 name only the job; their cheaper detector is not stated.
diff --git a/dev/governance/rules/ci-autofix.md b/dev/governance/rules/ci-autofix.md
index 0a7063317..efb4b6f00 100644
--- a/dev/governance/rules/ci-autofix.md
+++ b/dev/governance/rules/ci-autofix.md
@@ -65,9 +65,6 @@ every unrelated `fast` failure): its summary line is its only signal.
   `no-copies` and NOT-A-FILE failures fail recordings too, and their closures
   were never stale.
 
-  A failed recording reads files a clean run never does (`linecache`): an
-  UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.
-
 | Failure | Job | Commit subject | Code |
 |---|---|---|---|
 | `UNDER-SCOPED`, INERT READS | `closures-autofix` | `ci: re-record closures` | `closure.apply_under_scoped_recordings` |
@@ -79,8 +76,8 @@ a `GITHUB_TOKEN` push's `pull_request` runs are held `action_required`, so the r
 until approved: all three jobs approve them (kept until M-3), fail-soft without their
 secrets, when an App push or body edit cures it. Absent is not green (`orchestrator.md` section 11).
 
-When `mutation-autofix` goes red, run `--pin-killed` yourself. A `ci: pin killed mutants`
-stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
+When `mutation-autofix` goes red, run `--pin-killed` yourself. Until `mutation-pins` concludes the body says `unmeasured`;
+`pinned` only if `--pin-killed` ran on this head. A pin stales the body's `## Red checks` `mutation` line; the reviewer re-checks it. Do not automate survivor triage,
 golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint. A new selectable script with **no** recording is
 not UNDER-SCOPED — add it to a derive lane or `--single` it; autofix cannot invent a trace.
 
diff --git a/dev/programme/delivery/3255.md b/dev/programme/delivery/3255.md
new file mode 100644
index 000000000..2208c1f8c
--- /dev/null
+++ b/dev/programme/delivery/3255.md
@@ -0,0 +1 @@
+- [#3255](https://github.com/tvofi/heatpump_optimizer/pull/3255) — **open**, R10-FRICTION-RECORDS: friction records (R10-FRICTION-RECORDS)
diff --git a/tools/policy/policy_lint.mjs b/tools/policy/policy_lint.mjs
index 97d0124ea..2439f84bb 100644
--- a/tools/policy/policy_lint.mjs
+++ b/tools/policy/policy_lint.mjs
@@ -2813,11 +2813,29 @@ const FRICTION_THRESHOLD = 3
 // actually split. The mutation family's last four words are #2561 section 5's
 // measured synonyms of the mutation obligation (v7.0.0..df6ca4bc: test-vacuous
 // on 2 pull requests, the other three on 1 each).
+// The last three mutation members are v7.0.4..7e8939d38's spellings of the same
+// obligation: mutation-unpinned 2 pull requests, unpinned-site 2, mutation-survivors
+// 1, five that no other member holds (R10-RCA-MUTATION-VACUOUS.md, #2942).
 const FRICTION_FAMILIES = [
-  { name: 'mutation', members: ['mutation', 'mutation-vacuous', 'mutation-survivor', 'test-vacuous', 'vacuous-test', 'vacuous-check', 'mutant-survives'] },
+  { name: 'mutation', members: ['mutation', 'mutation-vacuous', 'mutation-survivor', 'test-vacuous', 'vacuous-test', 'vacuous-check', 'mutant-survives', 'mutation-unpinned', 'unpinned-site', 'mutation-survivors'] },
   { name: 'environment', members: ['environment', 'seat-environment'] },
+  // One obligation under three class words (#2437, R10-RCA-FRICTION-RESIDUE
+  // section 5): the root-cause check the fix reviewer enforces, split by what
+  // went wrong with the body's answer. Measured v7.0.4..origin/main: 5, 6 and
+  // 12 pull requests under the three words.
+  { name: 'root-cause', members: ['root-cause-unanswered', 'root-cause-detectable', 'root-cause-unrecorded'] },
 ]
 
+// THE DERIVED FAMILY (#2436, R10-RCA-FRICTION-RESIDUE section 4). The reviewer
+// may write any class word and the wave routes an untaught one to `other`, so
+// the obligation's unit is the spelling and a spelling that moves never reaches
+// the threshold. This family is every VERDICT histogram key that
+// VERDICT_CLASSES does not teach, other than the passing verdict, computed at
+// read time so no list of words can go stale. It is additive like the declared
+// families: the #2410 subtraction applies, every taught row prints
+// byte-identically, and a window with no untaught word prints no row.
+export const UNTAUGHT_FAMILY = 'other (untaught)'
+
 // The fold itself, pure over any histogram cell map (the verdict classes or
 // the friction rule ids): one row per declared family with at least one member
 // present in the window. A family with no member present produces no row at
@@ -2832,9 +2850,19 @@ const FRICTION_FAMILIES = [
 // occasions filed twice, and the 2 left were below the threshold. `filed`
 // names the members that filed, `union` is the count before they are taken
 // out, so the table can show both.
-function statsFamilies(hist) {
+// The one place the derived family's input is built: the would-open lines
+// (`statsFindings`) and the `--stats` table (`cmdStats`) both call it, and the
+// wiring pin below holds `cmdStats` to the call.
+export const derivedInput = (blocks, passing) => (blocks ? { taught: blocks, passing } : null)
+function statsFamilies(hist, derived = null) {
   const out = []
-  for (const { name, members } of FRICTION_FAMILIES) {
+  const declared = [...FRICTION_FAMILIES]
+  if (derived?.taught?.length) {
+    const taught = new Set(derived.taught)
+    const members = [...hist.keys()].filter((k) => !taught.has(k) && k !== derived.passing)
+    declared.push({ name: UNTAUGHT_FAMILY, members })
+  }
+  for (const { name, members } of declared) {
     const cells = members.map((m) => hist.get(m)).filter(Boolean)
     if (!cells.length) continue
     const filed = members.filter((m) => (hist.get(m)?.prs.size ?? 0) >= FRICTION_THRESHOLD)
@@ -3174,7 +3202,7 @@ export function statsFindings({ prs, fetched, fetchError, classes, blocks = bloc
   // message shape is the one `friction_issues.mjs`'s WOULD_OPEN_RE parses:
   // kind, count, threshold.
   for (const [kind, hist] of [['verdict family', verdicts], ['friction family', friction]]) {
-    for (const fam of statsFamilies(hist)) {
+    for (const fam of statsFamilies(hist, kind === 'verdict family' ? derivedInput(blocks, passing) : null)) {
       const n = fam.prs.size
       if (n < FRICTION_THRESHOLD) continue
       out.push({
@@ -6150,6 +6178,84 @@ function assertAcceptance(derived) {
       }
     }
     pins += 1
+    // THE DERIVED AND THE ROOT-CAUSE FAMILIES (#2436, #2437), driven over
+    // synthetic histograms: three untaught words on one pull request each fire
+    // `other (untaught)` at 3 while no word reaches 3 alone; a taught word and
+    // the passing verdict are not members (null control: every taught row stays
+    // out, a window with no untaught word prints no row); a word that files on
+    // its own is subtracted (#2410); and the three root-cause words fold to one
+    // family that a taught-only window never prints.
+    {
+      const mk = (rows) => {
+        const h = new Map()
+        for (const [k, prs] of rows) for (const pr of prs) bump(h, k, pr)
+        return h
+      }
+      const d = { taught: ['harness', 'other', 'class-open'], passing: 'merge' }
+      const fam = (h, name) => statsFamilies(h, d).find((f) => f.name === name)
+      const split = mk([['body-stale', [1]], ['figure-wrong', [2]], ['claim-drift', [3]], ['harness', [4, 5, 6, 7]], ['merge', [8, 9, 10]]])
+      const u = fam(split, UNTAUGHT_FAMILY)
+      const taughtOnly = mk([['harness', [1, 2, 3]], ['other', [4]], ['merge', [5]]])
+      const filedAlone = mk([['ci-red', [1, 2, 3]], ['body-stale', [4]]])
+      const f = fam(filedAlone, UNTAUGHT_FAMILY)
+      const rcFam = fam(mk([['root-cause-unanswered', [1]], ['root-cause-detectable', [2]], ['root-cause-unrecorded', [3]]]), 'root-cause')
+      if (
+        !u || u.prs.size !== 3 || u.union !== 3 || fam(taughtOnly, UNTAUGHT_FAMILY) ||
+        !f || f.prs.size !== 1 || f.union !== 4 || f.filed.join() !== 'ci-red' ||
+        statsFamilies(split).some((x) => x.name === UNTAUGHT_FAMILY) ||
+        !rcFam || rcFam.prs.size !== 3 || fam(taughtOnly, 'root-cause')
+      ) {
+        console.log('\nFIXTURE VACUOUS: the derived `other (untaught)` or the declared `root-cause` family did not fold as pinned (3 untaught words on 3 PRs -> 3; taught and passing words out; a word filing alone subtracted; no derived list given -> no row; root-cause 1+1+1 -> 3)')
+        rc = 1
+      }
+    }
+    pins += 1
+    // THE WIRING, NOT THE FOLD (#2436, #2942): `statsFindings` is what the
+    // governance cron files from, so the derived list it hands `statsFamilies`
+    // is driven end to end over synthetic merged pull requests. Three untaught
+    // words on three PRs yield exactly one `verdict family` would-open for
+    // `other (untaught)`; three `mutation` siblings (the #2942 spellings) on
+    // three PRs yield one for `mutation` and none for the derived family; a
+    // taught-only window opens neither.
+    {
+      const h40 = 'a'.repeat(40)
+      const win = (rows) => {
+        const prs = []
+        const fetched = new Map()
+        rows.forEach((word, i) => {
+          const pr = String(7100 + i)
+          prs.push({ pr, subject: `x (#${pr})` })
+          fetched.set(pr, { body: '', comments: [{ body: `Fix review: blocked ${h40} ${word}: x` }] })
+        })
+        return { prs, fetched }
+      }
+      const opens = (rows, extraTaught = []) => {
+        const { prs, fetched } = win(rows)
+        const blocks = ['harness', 'other', 'class-open', ...extraTaught]
+        return statsFindings({ prs, fetched, fetchError: null, classes: ['merge', 'blocked'], blocks, passing: 'merge' })
+          .filter((f) => /would open .*\(family\)" -- verdict family/.test(f.message))
+          .map((f) => /recurring friction: ([^"]+) \(family\)/.exec(f.message)[1])
+      }
+      const untaught = opens(['body-stale', 'figure-wrong', 'claim-drift'])
+      const mutWords = ['mutation-unpinned', 'unpinned-site', 'mutation-survivors']
+      const mut = opens(mutWords, mutWords)
+      const taughtOnly = opens(['harness', 'harness', 'other'])
+      if (
+        untaught.join('|') !== UNTAUGHT_FAMILY || mut.join('|') !== 'mutation' || taughtOnly.length
+      ) {
+        console.log(`\nFIXTURE VACUOUS: statsFindings did not file the families end to end (3 untaught words on 3 PRs -> ${JSON.stringify(untaught)}, want one \`${UNTAUGHT_FAMILY}\`; mutation-unpinned + unpinned-site + mutation-survivors -> ${JSON.stringify(mut)}, want one \`mutation\`; a taught-only window -> ${JSON.stringify(taughtOnly)}, want none)`)
+        rc = 1
+      }
+    }
+    pins += 1
+    // `cmdStats` reads the network, so its table wiring is pinned by shape: the
+    // verdict table's family call must take the shared derived input, or the
+    // `other (untaught)` row vanishes from `--stats` with every count unchanged.
+    if (!/statsFamilies\(verdicts, derivedInput\(blocks, passingVerdict\(\)\)\)/.test(read('tools/policy/policy_lint.mjs') ?? '')) {
+      console.log('\nFIXTURE VACUOUS: cmdStats no longer builds the verdict table\'s families from derivedInput(blocks, passingVerdict()); the derived `other (untaught)` row would drop from --stats in silence')
+      rc = 1
+    }
+    pins += 1
     // A family that contains the passing verdict would open rework as
     // friction -- the one class the histogram withholds from its own row. The
     // declared set must never do it, and the pin is here so the next declared
@@ -7467,7 +7573,7 @@ function cmdStats(since, cacheFile) {
     // over BOTH maps (FRICTION_FAMILIES: mutation's siblings are verdict
     // classes, environment's are friction rule ids). A window with no family
     // member prints none, and stays byte-identical to the pre-fold counter.
-    const families = { 'verdict class': statsFamilies(verdicts), rework: [], 'friction rule id': statsFamilies(friction) }
+    const families = { 'verdict class': statsFamilies(verdicts, derivedInput(blocks, passingVerdict())), rework: [], 'friction rule id': statsFamilies(friction) }
     for (const [label, hist] of [['verdict class', verdicts], ['rework', rework], ['friction rule id', friction]]) {
       console.log(`\n${label} (PRs / entries):`)
       const rows = [...hist.entries()].sort((a, b) => b[1].prs.size - a[1].prs.size || b[1].entries - a[1].entries)
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index 450810418..22bc0262b 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -499,6 +499,42 @@ def wiring_preds(root: Path, changed: set[str]) -> list[tuple[str, str]]:
             for g in gaps if len(g) > 1 and named(g[1].rstrip(":"))]
 
 
+def mutant_preds(root: Path, changed: set[str]) -> list[tuple[str, str]]:
+    """`instrument-self-tests`'s seat mutant drivers (`r10_*_mutants.py
+    --self-test`), run when the diff touches a file a driver plants into.
+
+    Each driver refuses to start when an anchor it replaces no longer occurs
+    exactly once, so an edit to a planted file reddens the CI job and no local
+    path ran it (#2865: `orchestrator_tick.py` moved `r10_ledger_mutants.py`'s
+    T3 anchor; dev/audit/rca/R10-RCA-ROOT-CAUSE-DETECTABLE.md). The drivers are
+    the ones governance.yml runs; a driver's plant targets are the repository
+    paths its source quotes, and the driver itself counts as a target. A diff
+    touching none of them runs nothing, so the standing cost is the 2.3 s the
+    four drivers take, paid only by a diff that can move an anchor.
+    """
+    wf = root / ".github" / "workflows" / "governance.yml"
+    if not wf.is_file():
+        return []
+    drivers = sorted(set(re.findall(r"tools/audit/seat/(r10_\w+_mutants\.py) --self-test",
+                                    wf.read_text())))
+    out: list[tuple[str, str]] = []
+    for name in drivers:
+        rel = f"tools/audit/seat/{name}"
+        src = root / rel
+        if not src.is_file():
+            continue
+        quoted = set(re.findall(r"[\"'](tools/[\w./-]+\.(?:py|sh|mjs))[\"']", src.read_text()))
+        if not ((quoted | {rel}) & changed):
+            continue
+        r = subprocess.run([sys.executable, "-I", rel, "--self-test"], cwd=root,
+                           capture_output=True, text=True)
+        if r.returncode:
+            fails = [ln.strip() for ln in (r.stdout + r.stderr).splitlines() if "FAIL" in ln]
+            out.append(("instrument", f"SEAT MUTANT SELF-TEST {name}: "
+                        + (fails[0] if fails else f"rc={r.returncode}")))
+    return out
+
+
 def privacy_preds(root: Path) -> list[tuple[str, str]]:
     """`instrument-self-tests`'s `ref_privacy.py --check`, which no local path
     ran (dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md, countermeasure B): its own
@@ -827,7 +863,7 @@ def unpinned(base):
 # alone, and reaching it by running every other arm cost 6.5 s of CPU against
 # the 5 s budget the seat's checks meet (eight others then; R10-FLOW-JIDOKA's
 # review, 2026-10-26).
-ARMS = ("orphans", "layout", "privacy", "wiring", "agreement", "graders", "no-recording",
+ARMS = ("orphans", "layout", "privacy", "wiring", "mutants", "agreement", "graders", "no-recording",
         "under-scoped", "inert-siblings", "left-inert", "mutation", "self-test-reads")
 
 
@@ -858,6 +894,7 @@ def predict(root: Path, base_ref: str, pairs: set | None = None,
         ("layout", lambda: layout_preds(root, base)),
         ("privacy", lambda: privacy_preds(root)),
         ("wiring", lambda: wiring_preds(root, changed)),
+        ("mutants", lambda: mutant_preds(root, changed)),
         ("agreement", lambda: agreement_preds(root, base_ref)),
         ("graders", lambda: grader_preds(root, base_ref)),
         ("no-recording", lambda: no_recording(root, base, changed, closure)),
@@ -1166,6 +1203,39 @@ def wiring_self_test(root: Path) -> int:
     return bad
 
 
+def mutant_self_test(root: Path) -> int:
+    """`mutant_preds` over a planted driver: a moved anchor, the intact twin, a null."""
+    import tempfile
+    bad = 0
+    with tempfile.TemporaryDirectory() as d:
+        t = Path(d)
+        seat = t / "tools" / "audit" / "seat"
+        seat.mkdir(parents=True)
+        (t / ".github" / "workflows").mkdir(parents=True)
+        (t / ".github" / "workflows" / "governance.yml").write_text(
+            "      - run: python3 -I tools/audit/seat/r10_x_mutants.py --self-test\n")
+        (seat / "r10_x_mutants.py").write_text(
+            'import sys\nT = "tools/audit/seat/owner.py"\n'
+            'src = open(T).read()\n'
+            'sys.exit(0 if src.count("ANCHOR") == 1 else (print("FAIL T3 anchor occurs once") or 1))\n')
+        (seat / "other.py").write_text("x = 1\n")
+        owner = seat / "owner.py"
+        cases = [
+            ("a planted target edited so its anchor is gone is predicted red",
+             "x = 1\n", {"tools/audit/seat/owner.py"}, 1),
+            ("the same target with its anchor intact is predicted green",
+             "ANCHOR\n", {"tools/audit/seat/owner.py"}, 0),
+            ("null control: a diff touching no planted target runs no driver (the anchor is gone, no red)",
+             "x = 1\n", {"tools/audit/seat/other.py"}, 0),
+        ]
+        for label, body, changed, want in cases:
+            owner.write_text(body)
+            got = len(mutant_preds(t, changed))
+            print(f"  {'ok  ' if got == want else 'FAIL'} {label}")
+            bad += got != want
+    return bad
+
+
 def null_control_self_test(root: Path) -> int:
     """`null_control_preds` over a comment-free pool, a commented one and a mix."""
     sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
@@ -1232,6 +1302,7 @@ def self_test() -> int:
     bad += self_test_reads_self_test(root)
     bad += rekey_self_test()
     bad += wiring_self_test(root)
+    bad += mutant_self_test(root)
     bad += null_control_self_test(root)
     bad += graders_self_test(root)
     gate = root / "tools" / "ci" / "gate.py"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
