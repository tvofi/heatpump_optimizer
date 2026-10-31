# Review packet #3017
head: 7b42b54998f1544050329cacab65d20c0a513b09
base: 5d4e0bcfb88413ddf9ca7f0884c36bbec9235447

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=124368855535 skipped
cancel-superseded id=124368860492 queued
prelude id=124368860839 queued
refresh id=124368860736 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body
             `tools/audit/carry_audit.py` is in the tree at this head
  unverified git log
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3017.md b/dev/programme/delivery/3017.md
new file mode 100644
index 000000000..dd1bf90f3
--- /dev/null
+++ b/dev/programme/delivery/3017.md
@@ -0,0 +1 @@
+- [#3017](https://github.com/tvofi/heatpump_optimizer/pull/3017) — **open**, triage: s8 batch 75 (P309-P311 rulings) (R10-TRIAGE-S6)
diff --git a/dev/programme/triage/s6-batch75.md b/dev/programme/triage/s6-batch75.md
new file mode 100644
index 000000000..85d341822
--- /dev/null
+++ b/dev/programme/triage/s6-batch75.md
@@ -0,0 +1,143 @@
+# Proposal triage, session s8, batch 75 (P309-P311)
+
+The rolling batch (V182) after batch 74. Three proposals from the root-cause probe
+R10-RCA-JIDOKA-YIELD, filed by the orchestrator s8 (2026-10-30T21:02Z). The report is the body at
+`origin/handoff-body/r10-rca-jidoka-yield` `c8f3acd99`. Facts were read at origin/main `437f1ba9b`
+and on the roster branch `origin/handoff/audit-r10-roster`. Both of the probe's measurements were
+re-run here, detached (`tools/audit/seat/daemonize.py`).
+
+## P309: M1, carry_audit flags an owed roster carry stated outside the carry sections (shape C)
+
+Verdict: ACCEPT narrowed. New S group **R10-RCA-JIDOKA-YIELD**
+(`groups/R10-RCA-JIDOKA-YIELD.json`). Its one pull request lands:
+- the RCA document at `dev/audit/rca/R10-RCA-JIDOKA-YIELD.md` (the report's text);
+- the M1 arm in `tools/audit/carry_audit.py`'s body branch, with fixture, mutant and
+  `tools/policy/field_coverage.mjs` registration;
+- the correction of the WHY comment at `tools/pr/prepr.sh:974-978`.
+
+**Narrowed:** the arm does not read text inside a code span or double quotes. Measured below, the
+probe's own report is a false positive without that.
+
+**The RCA document needs no new closure classification.** `dev/audit/` is an INERT prefix in
+`tests/closure.py` (line 321: "prose and evidence no gate script opens"). The fixer confirms it with
+`tests/entities.py`.
+
+**No conflict with P308** (`s6-batch74.md`, R10-FLY-RELAY-REVIEW-FF): P308 edits the verdict
+`## Evidence` branch (`carry_audit.py:206-209`), and M1 edits the body `else` branch (line 222).
+Same file, distinct seams.
+
+Source: the orchestrator s8's message of 2026-10-30T21:02Z, item (a). The report's section (3).
+
+Instances, re-measured here:
+- **The defect.** The #3010 r1 body (`da4e6e9ea:BODY.md`, `handoff-body/r10-fly-train-defaults`)
+  holds the paragraph "**Roster carry (open, not answered by this change).** Carry 1: **not done in
+  this pull request.**" before `## Head`.
+  - main's `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` prints
+    `CARRY-AUDIT: 0 finding item(s)`.
+  - A scratch copy with the probe's `OWED_CARRY` arm on the body branch prints `UNROUTED body item
+    c78ecb78 [owed carry]` and `1 finding item(s): 0 routed, 1 unrouted`, rc 1.
+  - With ` Carry: R10-FLY-TRAIN-DEFAULTS` appended to that paragraph it prints `1 routed, 0
+    unrouted`, rc 0.
+- **Null control, re-run** over every `handoff-body/*` tip (223 today, the probe's 222 plus one):
+  main rc 0 on 165, the patched copy on 155, and 10 flip.
+  - Nine are the probe's catches: r10-cop-partload-p2, r10-fly-openpr-atomic, r10-fly-train-defaults
+    (#3010), r10-orch-planpage, r10-sav-comfort, -r2 and -r3, r10-train-overlap-grade and
+    r10-ux-health-p2. Each flipped item is an owed carry stated as not done, with no route. For
+    example: "Carry 4 (P71, ...): not in this diff."; "Carry 8 (...): still not met."; "Carry 2
+    (#2577 ...): not in this part and still open".
+  - The tenth is new: **r10-rca-jidoka-yield, the probe's own report.** Its items `00929b43` and
+    `5bfb2857` quote the #3010 paragraph, one in double quotes and one inside a code span. That is
+    a false positive, and it is why the arm is narrowed. With a quote and code-span strip the
+    expected result is 9 flips, all real.
+- **Cost test.** The probe's figures are about 18 min/day of defect (shape C, 1 block in 4.66 days
+  × an 84 min median) against about 2 min/day standing cost (0.12 s per run, about 3 runs per PR at
+  about 45 PRs/day, plus one marker line on about 4% of bodies). Its block count re-runs exactly
+  (P310).
+
+Cost:
+- About 6 lines in `carry_audit.py` (the regex, the strip, the branch) plus a fixture row set, one
+  mutant and a `field_coverage.mjs` registration.
+- One comment correction in `prepr.sh`, and one new markdown file under an INERT prefix.
+- Sonnet fixer, opus reviewer, one pull request. No new check, API call or standing CPU.
+  `carry_audit.py` and `prepr.sh` are not capped files.
+
+Binding: measured 18 vs 2 min/day, demonstrated red on the defect and green once routed. Of 223
+bodies, 9 real catches and 1 quotation false positive, which the narrowing removes. Clearly
+positive. A new S group rather than R10-FLY-RELAY-REVIEW-FF: that host already carries P293, P296,
+P306, P308 and the CARRY-DISPOSITION fold, so it is at three-round risk. M1 is this RCA's own
+countermeasure and lands beside its document.
+
+## P310: M2, `Carry: <GROUP>` must name a destination that holds the item (shape A)
+
+Verdict: ACCEPT as already carried, flagged for priority dispatch. CARRY 0 of
+R10-FLY-RELAY-REVIEW-FF (folded from R10-FLY-CARRY-DISPOSITION) is this check:
+- `carry_audit.py landed`: a body item's id is present in its routed group's carry or brief at
+  `--roster-ref`, with `CARRY-MISSING` lines and rc 1;
+- `land-ops`: append-carry ops tagged `(items <ids>)`;
+- `bus.sh dispatch` refuses on rc 1.
+
+It is unbuilt: `carry_audit.py` at main has only `check`, `pr`, `sweep` and `owners` (lines
+542-554). M2's one widening: a carry may name the **source topic** (the PR number or handoff topic)
+instead of the item id. The id is the sha1 of the item's whitespace-collapsed text
+(`carry_audit.py:230`), so rewording an item re-mints it.
+
+**Policy approval, recorded as given.** The orchestrator s8 approved M2's policy part on
+2026-10-30, under mandate 6329234399. That approval is the orchestrator's mandate approval, not
+tvofi's personal review. Its scope: a fixer writes each roster carry so that it names
+`carry_audit`'s item id or the source topic, and dispatch refuses a body whose `Carry: <GROUP>`
+destination does not hold the item. This is fix-review step 10 made mechanical. This ruling records
+that approval and does not grant it.
+
+Source: the orchestrator s8's message of 2026-10-30T21:02Z, item (b). The report's section (3).
+
+Instances, re-measured here:
+- The probe's enumerator (`vcore.py`, its appendix) re-run over every `verdict/*` and
+  `archive/verdict/*` commit (1330 today, the probe's 1328 plus two). It reproduces the probe's table
+  exactly: after #2838, 21 carry-missing of 125 blocked verdicts, on 19 of the 73 PRs with a block
+  (168 reviewed); before #2838, 50 of 334.
+- The probe's per-verdict table puts 14 of those 21 in shape A. The marker names a live destination
+  whose brief does not hold the finding. In 12 of the 21, the reviewer's own `carry_audit` run
+  printed 0 unrouted on the blocked body.
+
+Cost:
+- Inside a group already open on this file, `carries-open`. The roster read is the fetch
+  `carry_line` already does, and the added time is under 1 s per run (probe).
+- The new obligation is on the carry text: item id or source topic. `land-ops` writes it
+  mechanically.
+- No capped file changes in this ruling. The policy text that states the fixer obligation is the
+  group's to write, under the approval above.
+
+Binding: shape A at 14 blocks in 4.66 days × the 84 min median is about 252 min/day. That is the
+largest single yield in the round's block record, against a sub-second check whose design is
+already carried. Clearly positive. **Priority dispatch:** the roster op raises R10-FLY-RELAY-REVIEW-FF's
+CARRY 0 to be dispatched first, alone if needed, ahead of the group's other carries.
+
+## P311: shape B, liveness rules carry_audit's destination test does not model
+
+Verdict: DEFER. The report found no barrier within its bound, and the six blocks split into five
+distinct rules with at most two blocks each:
+- (1) A destination behind `#N` whose groups are done or absorbed: #2896 r1 and r2, one PR.
+- (2) A double destination: #2896 r2.
+- (3) A marker in a section carry_audit does not read: #2962, `Carry: #2959` in `## Mutation
+  proof`.
+- (4) A destination after-edged on the consumer: #3004 r1.
+- (5) A batch that marks its own destinations done: #2914.
+- (6) `#201` with no carry file citing it: #2528, before step 7e existed.
+
+Rule (1), with (5) as its write-time form, is already owned. R10-ORCH-ROSTER-SCHEMA's #2733
+remainder (a STRANDED report for a carry on a done or absorbed group) and the carries-open downgrade
+(P305, `s6-batch71.md`) together refuse or report a destination that is done or absorbed.
+
+Source: the orchestrator s8's message of 2026-10-30T21:02Z, item (c). The report's section (3).
+
+Cost of building each as an arm now: one `Dests.check` arm and fixture each, five arms for six
+blocks over 4.66 days.
+
+Binding: no rule reaches three instances. The largest is already owned elsewhere, and M2 (P310)
+also refuses part of shape B once a destination must hold the item. An unmeasured per-rule benefit
+is DEFER, never ACCEPT.
+
+What would change the answer: a third instance of any one of rules (2) to (4) after M2 lands, or
+rule (3) recurring. Rule (3), a `Carry:` marker in a section carry_audit ignores, is the cheapest:
+one warning line for a marker found outside the read sections. Its third instance alone would
+justify it.

