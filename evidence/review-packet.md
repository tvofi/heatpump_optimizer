# Review packet #3051
head: eeb947e513fb1b43bd81946e3818f51195e33c48
base: 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124618739938 neutral
arch-score / arch-score id=124618582403 success
arm id=124618516273 skipped
budget-raise-gate / budget-raise-gate id=124618582456 success
cancel-superseded id=124618480769 success
codeql / Analyze (actions) id=124618582397 success
codeql / Analyze (javascript-typescript) id=124618582425 success
codeql / Analyze (python) id=124618582417 in_progress
governance / delivery-status id=124618582498 success
governance / delivery-status-publish id=124618583445 skipped
governance / env-matrix id=124618582485 in_progress
governance / instrument-self-tests id=124618582413 in_progress
governance / policy-docs id=124618582467 success
governance / record id=124618583915 skipped
governance / wave-script id=124618582423 success
hassfest / hassfest id=124618582402 success
kernel-points id=124618583899 skipped
prelude id=124618480997 success
refresh id=124618480971 success
tests / arch-instrument id=124618696212 in_progress
tests / briefs id=124618582438 success
tests / browser id=124618696239 in_progress
tests / closure-scope id=124618582383 success
tests / closures id=124618696152 in_progress
tests / coverage id=124618696123 in_progress
tests / fast (3.14) id=124618696197 in_progress
tests / mutation id=124618582429 success
tests / mutation-autofix id=124618749598 skipped
tests / mutation-pins id=124618748929 skipped
tests / nightly-ha id=124618697742 skipped
tests / nightly-status id=124618582523 success
tests / replay id=124618697574 skipped
tests / typing id=124618696210 success
validate / validate-hacs id=124618582406 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: eeb947e513fb1b43bd81946e3818f51195e33c48 lacks origin/main c3a47e5656ef858674a1fd011c0e2f039c4ed838; roster read at origin/main
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept
             `tests/gate_lock.py` is in the tree at this head
  ok         python3 -I tools/audit/carry_audit.py --self-test
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_carry_parser_mutants.py
             `dev/audit/harnesses/r10_carry_parser_mutants.py` is in the tree at this head
  ok         python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <da4e6e9ea:BODY.md>
             `tools/audit/carry_audit.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  unverified python3
             python3 with no script argument
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/field_coverage.mjs
             `tools/policy/field_coverage.mjs` is in the tree at this head
  ok         python3 tests/gate_lock.py --lock-dir <d> slot-take --label pN --owner-pid <live pid>
             `tests/gate_lock.py` is in the tree at this head
  ok         python3 -I tools/audit/carry_audit.py
             `tools/audit/carry_audit.py` is in the tree at this head

FIGURES: 9 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.claude/rules/gate-scoping.md b/.claude/rules/gate-scoping.md
index 879a597f7..9224eae4e 100644
--- a/.claude/rules/gate-scoping.md
+++ b/.claude/rules/gate-scoping.md
@@ -23,8 +23,8 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 `slot`, one of `$HPO_HEAVY_SLOTS` (four), for one unrecorded or recorded in `closures.json` at or above
 `SLOT_MIN_SECONDS`; else `none`. `$HPO_SLOT_LABEL` names a run's slot. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
-free, a slot once its pid is gone. A seat that waited one lease period may leave `stress.py` to CI,
-named unrun. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
+free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
+retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
 with `tests/gate_lock.py`, never `mkdir`:
 
 ```
@@ -37,16 +37,16 @@ The owner file carries your label and a 30-minute `expires_at`. `renew` exits 75
 waits: finish, release, take again behind it. `run.sh` under `HPO_GATE_LOCK_LABEL` renews it, and
 refuses every leased script at once if that label holds none: `take` first (#2368).
 
-**The mypy census runs here, given pins**: `HPO_TYPING_PYTHON` names one carrying them; unset it prints the install command, unpinned it fails (#1091, #1099, #1095).
-**A gate run rewrites `tools/audit/round4/D6/`**: check it out before any `git add -A` (#1054).
+**The mypy census runs here, given pins**: `HPO_TYPING_PYTHON` names one carrying them; unset it prints the install command, unpinned it fails.
+**A gate run rewrites `tools/audit/round4/D6/`**: check it out before any `git add -A`.
 
 ## `prepr.sh` is not CI
 
 CI grades with the base's copy of each pinned grader, prepr with this head's: a grammar only this diff
 registers in `tools/policy/agreement.mjs` passes prepr's agreement lane and is refused by `wave-script`
 (#2366). Step 3f runs `brief_lint.mjs` only when a pinned path changed: run
-`node tools/policy/brief_lint.mjs` before a handoff (#2373). Step 6b's `failed while being recorded` is
-an exit code from one unleased run, not a cause: re-run that script alone first (#2375).
+`node tools/policy/brief_lint.mjs` before a handoff. Step 6b's `failed while being recorded` is
+an exit code from one unleased run, not a cause: re-run that script alone first.
 
 ## Never run a full `tests/derive_closures.sh` off Linux
 
diff --git a/.cursor/rules/gate-scoping.mdc b/.cursor/rules/gate-scoping.mdc
index 96e735772..48dc36db2 100644
--- a/.cursor/rules/gate-scoping.mdc
+++ b/.cursor/rules/gate-scoping.mdc
@@ -22,8 +22,8 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 `slot`, one of `$HPO_HEAVY_SLOTS` (four), for one unrecorded or recorded in `closures.json` at or above
 `SLOT_MIN_SECONDS`; else `none`. `$HPO_SLOT_LABEL` names a run's slot. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
-free, a slot once its pid is gone. A seat that waited one lease period may leave `stress.py` to CI,
-named unrun. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
+free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
+retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
 with `tests/gate_lock.py`, never `mkdir`:
 
 ```
@@ -36,16 +36,16 @@ The owner file carries your label and a 30-minute `expires_at`. `renew` exits 75
 waits: finish, release, take again behind it. `run.sh` under `HPO_GATE_LOCK_LABEL` renews it, and
 refuses every leased script at once if that label holds none: `take` first (#2368).
 
-**The mypy census runs here, given pins**: `HPO_TYPING_PYTHON` names one carrying them; unset it prints the install command, unpinned it fails (#1091, #1099, #1095).
-**A gate run rewrites `tools/audit/round4/D6/`**: check it out before any `git add -A` (#1054).
+**The mypy census runs here, given pins**: `HPO_TYPING_PYTHON` names one carrying them; unset it prints the install command, unpinned it fails.
+**A gate run rewrites `tools/audit/round4/D6/`**: check it out before any `git add -A`.
 
 ## `prepr.sh` is not CI
 
 CI grades with the base's copy of each pinned grader, prepr with this head's: a grammar only this diff
 registers in `tools/policy/agreement.mjs` passes prepr's agreement lane and is refused by `wave-script`
 (#2366). Step 3f runs `brief_lint.mjs` only when a pinned path changed: run
-`node tools/policy/brief_lint.mjs` before a handoff (#2373). Step 6b's `failed while being recorded` is
-an exit code from one unleased run, not a cause: re-run that script alone first (#2375).
+`node tools/policy/brief_lint.mjs` before a handoff. Step 6b's `failed while being recorded` is
+an exit code from one unleased run, not a cause: re-run that script alone first.
 
 ## Never run a full `tests/derive_closures.sh` off Linux
 
diff --git a/dev/audit/harnesses/r10_carry_parser_mutants.py b/dev/audit/harnesses/r10_carry_parser_mutants.py
index 2d35b84a4..9f396bf09 100644
--- a/dev/audit/harnesses/r10_carry_parser_mutants.py
+++ b/dev/audit/harnesses/r10_carry_parser_mutants.py
@@ -147,8 +147,13 @@ MUTANTS = [
     ("I-carry-lower", "        elif sec.lower() in CARRY_SECTIONS:", "        elif sec in CARRY_SECTIONS:"),
     ("I-none", '            why = "" if NONE_ITEM.match(t) else "section"', '            why = "section"'),
     ("I-bsec", '            why = ("section" if LEAD.search(sec) else', '            why = ("section" if False else'),
-    ("I-blead", '"lead" if LEAD.match(first)\n                   else "under lead" if inherited else "")\n        flagged', '"lead" if False\n                   else "under lead" if inherited else "")\n        flagged'),
-    ("I-binh", 'else "under lead" if inherited else "")\n        flagged', 'else "under lead" if False else "")\n        flagged'),
+    ("I-blead", '"lead" if LEAD.match(first)\n                   else "under lead" if inherited else "owed carry" if owed_carry(t) else "")\n        flagged', '"lead" if False\n                   else "under lead" if inherited else "owed carry" if owed_carry(t) else "")\n        flagged'),
+    ("I-binh", 'else "under lead" if inherited else "owed carry"', 'else "under lead" if False else "owed carry"'),
+    # M1 (R10-RCA-JIDOKA-YIELD): the owed-carry arm, and each half of its strip
+    ("I-owed-arm", ' else "owed carry" if owed_carry(t) else "")', ' else "")'),
+    ("I-owed-strip", 'OWED_CARRY.search(QUOTED.sub(" ", bare))', 'OWED_CARRY.search(text)'),
+    ("I-owed-code", 'OWED_CARRY.search(QUOTED.sub(" ", bare))', 'OWED_CARRY.search(QUOTED.sub(" ", text))'),
+    ("I-owed-quote", 'OWED_CARRY.search(QUOTED.sub(" ", bare))', 'OWED_CARRY.search(bare)'),
     ("I-lead-para", '        if it["kind"] == "para" and t.endswith', '        if t.endswith'),
     ("I-lead-colon", ' and t.endswith(":") and flagged:', ' and flagged:'),
     ("I-lead-flag", ' and t.endswith(":") and flagged:', ' and t.endswith(":"):'),
diff --git a/dev/audit/rca/R10-RCA-JIDOKA-YIELD.md b/dev/audit/rca/R10-RCA-JIDOKA-YIELD.md
new file mode 100644
index 000000000..c6a8e77de
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-JIDOKA-YIELD.md
@@ -0,0 +1,132 @@
+# R10-RCA-JIDOKA-YIELD: why step 7e did not cut carry-missing blocks (probe at 437f1ba9b)
+
+## Premise correction: the step is #2838's, not #2853's
+
+Step 7e (`carry_line`, `tools/pr/prepr.sh:990`), and its call inside `--body-check` (the call `body_push.sh` runs), arrived in commit 1b9a86266. They reached main in **#2838** (bdf69a5c3, 2026-10-26T04:40:21Z). `git show bdf69a5c3^1:tools/pr/prepr.sh | grep -c 'cline=$(carry_line'` prints 0, and the same command at bdf69a5c3 prints 1. **#2853** (53c4b9cb0, 2026-10-28T03:16:58Z) added only `--fill-red` to `body_push.sh`, plus claims, privacy and figure steps. So the window that tests step 7e starts at #2838. Below, both cut points are reported.
+
+## Re-measured yield
+
+Enumerator. Corpus: every commit reachable from `refs/heads/verdict/*` and `refs/tags/archive/verdict/*` (534 refs, 1328 commits). Each subject is parsed as `verdict: #N Fix review: <word> [<sha>] [<class>:...]`. Verdicts are deduped on (PR, word, sha, class), keeping the earliest, which leaves 1126 verdicts and 459 blocked. The clock is the commit's `%ct` (epoch, so no timezone is involved). The window runs from the first verdict (2026-10-06T18:01Z) to 437f1ba9's commit (2026-10-30T20:32:38Z).
+
+```
+git fetch origin '+refs/heads/verdict/*:refs/remotes/origin/verdict/*' '+refs/tags/archive/verdict/*:refs/tags/archive/verdict/*'
+git log --format='%H%x09%ct%x09%cI%x09%s' $(git for-each-ref --format='%(refname)' refs/remotes/origin/verdict refs/tags/archive/verdict) | sort -u > vc.tsv
+python3 -I vcore.py vc.tsv   # vcore.py: the parser/dedupe/window script in the appendix
+```
+
+| window | carry-missing / blocked verdicts | PRs with carry-missing / PRs with a block | PRs reviewed |
+|---|---|---|---|
+| before #2838 | 50/334 (15.0%) | 45/199 (22.6%) | 390 |
+| #2838..#2853 | 5/35 (14.3%) | 5/23 (21.7%) | 50 |
+| after #2853 | 16/90 (17.8%) | 14/53 (26.4%) | 122 |
+| after #2838 | 21/125 (16.8%) | 19/73 (26.0%) | 168 |
+| after #2838, PRs numbered >2838 only | 18/100 (18.0%) | 16/56 (28.6%) | 146 |
+
+The rate is 2.57/day before #2838 and 4.51/day after it. Measured from block to the next verdict on the same PR, a carry-missing block costs a median 84 min (p25 36, p75 216, n=69). The step did not lower the share on either cut. The orchestrator's crude 95/652 and 22/121 differ from this table in dedupe and class prefix. This table counts the `carry-missing` class exactly. The `carry-unrouted`, `carry-stale` and `carry-scope` classes are excluded.
+
+## (1) Each post-#2838 carry-missing block: did step 7e run, and why did it not refuse?
+
+Step 7e runs at every `open_pr.sh` (prepr `CARRY_LINE=$(carry_line "$BODY")`, `prepr.sh:3936`). For a cloud seat it also runs at `body_push.sh` whenever `handoff/<topic>` exists, because `--body-check` folds `carry_line`'s rc into its own and `body_push` refuses on it. Cloud and local fixers therefore both reach it. PRs numbered below 2838 (#2528, #2554, #2580) were opened before it existed.
+
+"Reviewer's carry_audit" below means what the blocking verdict's own evidence printed for `carry_audit.py check --body` at the blocked head (`git grep CARRY-AUDIT <verdict commit>`).
+
+| verdict | PR | reviewer's carry_audit | shape |
+|---|---|---|---|
+| 9008a6854 | #2849 | 2 routed, 0 unrouted | A |
+| 36b59ff31 | #2852 | 2 routed, 0 unrouted | A (marker names the PR's own group, which closes at merge) |
+| e3bc3b7fd | #2854 | not in evidence | A (codes "live only in the PR body") |
+| 9cabb1d70 | #2871 | 3 routed, 0 unrouted | A (carried only in this body) |
+| a374d0b6c | #2899 | not in evidence | A |
+| aa2a03c01 | #2906 | not in evidence | A |
+| aca91d7d1 | #2896 r1 | 17 routed, 0 unrouted | B (`#2733`'s groups done/absorbed; the reviewer notes carry_audit accepts it) |
+| d91a634f7 | #2896 r2 | 17 routed, 0 unrouted | B (second destination; "it does not see the double destination") |
+| b70714b39 | #2914 | not in evidence | B (destination groups re-derived `done` by the same batch) |
+| 403f83c25 | #2528 (pre-step) | not in evidence | B (routed to #201, which has no carry file citing it) |
+| a1c12e533 | #2554 (pre-step) | not in evidence | A |
+| 98ef788b0 | #2580 (pre-step) | 2 routed, 0 unrouted | A ("That routing is syntactic. The block above is about the destination's content.") |
+| d0033ecbe | #2946 | 3 routed, 0 unrouted | A |
+| e5e2a0c8b | #2925 | 1 routed, 0 unrouted | A (open seam carried to no stage) |
+| 16e5d627e | #2961 | 7 routed, 0 unrouted | A |
+| 39f4cfdfa | #2962 | 0 finding items | B (`Carry: #2959` sits in `## Mutation proof`, a section carry_audit does not read as a finding) |
+| 1af0c637c | #2925 | 2 routed, 0 bad (body) | A |
+| 258bc873b | #2992 | 4 routed, 0 unrouted | A (seam "only in the PR body") |
+| 0f8e3454e | #2995 | not in evidence | A |
+| 354e3f218 | #3004 r1 | not in evidence | B (owed roster carry routed to R10-FLOW-WIP, a consumer after-edged on it: a live destination, an invalid disposition) |
+| 35f15ea69 | #3010 r1 | 0 finding items | C |
+
+The shapes, as counts of the 21 verdicts:
+- **A (14).** The marker names a live destination, but the destination's brief on `handoff/audit-r10-roster` does not hold the finding and its control.
+- **B (6).** The marker names a destination that carry_audit's liveness test accepts, but the disposition is invalid for a reason that test does not model.
+- **C (1).** An owed roster carry is stated in prose outside the sections carry_audit reads, and the carry sections say `none`.
+
+In none of these did the step skip, or refuse and get bypassed. Where the verdict recorded the run (12 of 21), carry_audit returned 0 unrouted on the very body that was blocked. Step 7e ran, could not have refused these bodies, and so passed them.
+
+**#3010 r1, reproduced.**
+- The fixer's code head 0b79e8de equals `handoff/r10-fly-train-defaults`.
+- The fixer's base cf4f6b7a6 contains bdf69a5c3, and its prepr.sh holds the `--body-check` carry call (count 1).
+- `handoff-body/r10-fly-train-defaults` da4e6e9ea (2026-10-30T18:43:56Z) is the r1 body.
+- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <da4e6e9ea:BODY.md>` prints `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`, rc 0, in 0.31 s.
+
+The owed item ("**Roster carry (open, not answered by this change).** Carry 1: **not done in this pull request.**") sits in an untitled paragraph before `## Head`. Its first words do not match `LEAD` (`carry_audit.py:121-123`), and `## Forward-carry` says `none`, so `items()` (`carry_audit.py:218-222`) flags nothing. The handoff's `brief-carries` arm (`review_packet.py:358`) also passes it, because it only counts that `Carry 1` is named. Each check passes, and the hole lies between the two: a carry the body names as *not done* owes no route.
+
+## (2) Process state: (c)
+
+The process existed and was followed: step 7e ran at the open and at `body_push`. It did not produce the intended result, because its unit is narrower than the defect class it was built to remove. The WHY at `prepr.sh:974-978` says "25 were `carry-missing` ... This is that same checker". That premise is false. The `carry-missing` verdict is fix-review.md step 10: "open it (a roster carry at the body's `handoff/audit-r<N>-roster` SHA) and confirm it states its control as a precondition". That step judges whether the destination holds the finding. carry_audit judges whether a marker exists and names a live destination. The evidence is the 12 verdicts above whose own carry_audit run printed 0 unrouted on a body they blocked as carry-missing. The case is not (b), since nothing was skipped, and not (d), since the class had the same shape before and after (15.0% → 16.8%). This is #2073's pattern: a half-port that checks one direction of the reviewer's test.
+
+**Class reach.** The 222 `handoff-body/*` tips were run under the patched arm below. They hold 8 further bodies, besides #3010, with an owed roster carry stated as not done and no route: r10-cop-partload-p2, r10-fly-openpr-atomic (2 items), r10-orch-planpage, r10-sav-comfort, r10-sav-comfort-r2, r10-sav-comfort-r3, r10-train-overlap-grade (9 items) and r10-ux-health-p2. Shape C is therefore latent at about 4% of bodies, though only one has been blocked so far. Shapes A and B are 20 of the 21 blocks.
+
+## (3) Countermeasure and cost test
+
+This is an audit class (21 carry-missing verdicts in round 10 since the step, 71 in all), so a barrier is owed.
+
+**M1, demonstrated (covers shape C).** A body item outside the carry sections that names a roster carry index together with a not-done phrase becomes a finding item, which then needs a `Carry:` marker. Scratch copy of `tools/audit/carry_audit.py`:
+
+```
++OWED_CARRY = re.compile(r"\bcarry\s*\[?\d+\]?\W{0,6}[^.\n]{0,80}?\b(?:not done|not (?:built|answered|implemented)|not in this (?:part|diff|pull request|change)|still (?:not met|open|owed)|owed (?:by|to|in))", re.I)
+@@ items(), body branch
+-                   else "under lead" if inherited else "")
++                   else "under lead" if inherited else "owed carry" if OWED_CARRY.search(t) else "")
+```
+
+- **On the defect** (#3010 r1 body, da4e6e9ea): rc 1, `UNROUTED body item c78ecb78 [owed carry]: "**Roster carry (open, not answered by this change).** Carry 1: **not done in this pull request.** ..."`, summary `1 finding item(s): 0 routed, 1 unrouted`.
+- **Once routed** (the same body with ` Carry: R10-FLY-TRAIN-DEFAULTS` appended to that paragraph): rc 0, `1 routed, 0 bad destination(s)`.
+- **Null control** over the 222 `handoff-body/*` tips: the unpatched script returns rc 0 on 164 and the patched one on 155. The 9 bodies that flip are #3010 and the 8 listed under class reach. Each is an owed carry with no route, so each is a catch by finding-propagation.md's own rule, not noise. The patched copy's `--self-test` prints `206 checks, 0 failed`. The arm has no fixture or mutant yet. When it is built, it owes a fixture, a mutant, and its `field_coverage.mjs` registration.
+- **Cost test**, in wall-clock per day of round 10:
+  - Defect side: shape C was 1 block in 4.66 days (0.21/day) × 84 min median = **about 18 min/day**.
+  - Standing cost: carry_audit runs in 0.12 s (patched, #3010 body) and runs about 3 times per PR (body_push, open, pr-contract). At about 45 PRs/day (122 reviewed in the 2.72 days after #2853), that is about 16 s/day. Add one marker line on 4% of bodies at about 1 min each, about 108 s/day. Total **about 2 min/day**.
+  - 2 < 18, so M1 passes.
+
+**M2, not demonstrated (shape A, the yield).** For each `Carry: <GROUP>` marker in the body, require the group's roster entry at the round ref to hold a carry naming the item id (carry_audit's printed `item <id>`) or the source topic. That is the mechanical form of fix-review step 10's "open it". It would have refused every A row whose verdict says "only in the PR body". It needs fixers to write carries with the item id, which changes what a seat must do. That makes it policy (finding-propagation.md), so it is the owner's call and this probe does not build it. Its cost test, against shape A at 14 blocks / 4.66 days × 84 min = **about 252 min/day**: the roster read is the same fetch `carry_line` already does, and the added time is under 1 s per run.
+
+**Shape B (6)** is a set of distinct liveness rules: a done or absorbed group behind `#N`, a double destination, a marker outside finding sections, an after-edged consumer, and a batch that marks its own destinations done. Each is a candidate `Dests.check` arm. No barrier was found within the bound, so the owner is asked.
+
+The WHY at `prepr.sh:974-978` misstates the class. M1's pull request (R10-PREPR-CAP) corrects it.
+
+## Appendix: vcore.py (the enumerator)
+
+```python
+import re,sys,collections,datetime as dt
+rows=[]
+for l in open(sys.argv[1]):
+    h,ct,ci,s=l.rstrip('\n').split('\t',3)
+    m=re.match(r'verdict: #(\d+) Fix review: (\w+)(?: ([0-9a-f]{7,40}))?\s*(.*)',s)
+    if not m: continue
+    pr,word,sha,rest=m.groups(); cls=''
+    if word=='blocked':
+        cm=re.match(r'([A-Za-z0-9_.-]+)',rest); cls=cm.group(1).rstrip(':').lower() if cm else ''
+    rows.append((int(ct),int(pr),word,sha or '',cls,s,h))
+seen={}
+for r in sorted(rows):
+    k=(r[1],r[2],r[3],r[4])
+    if k not in seen: seen[k]=r
+V=list(seen.values())
+T={'2838':dt.datetime(2026,10,26,4,40,21,tzinfo=dt.timezone.utc).timestamp(),
+   '2853':dt.datetime(2026,10,28,3,16,58,tzinfo=dt.timezone.utc).timestamp()}
+end=dt.datetime(2026,10,30,20,32,38,tzinfo=dt.timezone.utc).timestamp()
+first=min(v[0] for v in V)
+wins=[('pre-2838',first,T['2838']),('2838..2853',T['2838'],T['2853']),('post-2853',T['2853'],end),('post-2838',T['2838'],end)]
+for lab,opened in [('all PRs',lambda n:True),('PRs numbered >2838',lambda n:n>2838)]:
+  for name,a,b in wins:
+    w=[v for v in V if a<=v[0]<b and opened(v[1])]; bl=[v for v in w if v[2]=='blocked']; c=[v for v in bl if v[4]=='carry-missing']
+    print(lab,name,len(c),len(bl),len({v[1] for v in c}),len({v[1] for v in bl}),len({v[1] for v in w}))
+```
diff --git a/dev/governance/roles/nudge.md b/dev/governance/roles/nudge.md
index d126e323b..23f5e3a00 100644
--- a/dev/governance/roles/nudge.md
+++ b/dev/governance/roles/nudge.md
@@ -70,7 +70,7 @@ Direct-merge only what step 3 leaves out of the queue, other than a `record:` pu
 
 ## 8. Prepr slots
 
-Up to four `prepr.sh` run at a time: each takes one of `tests/gate_lock.py`'s four heavy slots, and a fifth queues. A seat's own prepr counts. `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh`, `tools/pr/app_push.sh` and a `tests/derive_closures.sh` run each count as one. Do not start a fifth. Do not recarry a branch a seat is writing. Skip a group whose fixer or reviewer worktree was written in the last 15 minutes, or whose own prepr is running. Recarry may run during a train's CI wait. It may not run while the train itself is in recarry.
+Up to four `prepr.sh` run at a time: each takes one of `tests/gate_lock.py`'s four heavy slots, and a fifth queues: the lease, not the tick's count, is the cap. A seat's own prepr counts. `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh`, `tools/pr/app_push.sh` and a `tests/derive_closures.sh` run each count as one. Do not recarry a branch a seat is writing. Skip a group whose fixer or reviewer worktree was written in the last 15 minutes, or whose own prepr is running. Recarry may run during a train's CI wait. It may not run while the train itself is in recarry.
 
 ## 9. Conflicting or DIRTY
 
diff --git a/dev/governance/rules/gate-scoping.md b/dev/governance/rules/gate-scoping.md
index 879a597f7..9224eae4e 100644
--- a/dev/governance/rules/gate-scoping.md
+++ b/dev/governance/rules/gate-scoping.md
@@ -23,8 +23,8 @@ clears `tests/entities.py`'s history reds (#1693, #1699, #1704).
 `slot`, one of `$HPO_HEAVY_SLOTS` (four), for one unrecorded or recorded in `closures.json` at or above
 `SLOT_MIN_SECONDS`; else `none`. `$HPO_SLOT_LABEL` names a run's slot. Arrival orders
 each priority band; a dead or expired ticket is skipped. An expired or abandoned lease is
-free, a slot once its pid is gone. A seat that waited one lease period may leave `stress.py` to CI,
-named unrun. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
+free, a slot once its pid is gone. A `lease` wait ends at the script's recorded seconds, rc 76: `run.sh` names it unrun. `flock-wrap`
+retakes a lapsed lease. That lease, not the tick's count, is nudge.md §8's cap; hold it by hand
 with `tests/gate_lock.py`, never `mkdir`:
 
 ```
@@ -37,16 +37,16 @@ The owner file carries your label and a 30-minute `expires_at`. `renew` exits 75
 waits: finish, release, take again behind it. `run.sh` under `HPO_GATE_LOCK_LABEL` renews it, and
 refuses every leased script at once if that label holds none: `take` first (#2368).
 
-**The mypy census runs here, given pins**: `HPO_TYPING_PYTHON` names one carrying them; unset it prints the install command, unpinned it fails (#1091, #1099, #1095).
-**A gate run rewrites `tools/audit/round4/D6/`**: check it out before any `git add -A` (#1054).
+**The mypy census runs here, given pins**: `HPO_TYPING_PYTHON` names one carrying them; unset it prints the install command, unpinned it fails.
+**A gate run rewrites `tools/audit/round4/D6/`**: check it out before any `git add -A`.
 
 ## `prepr.sh` is not CI
 
 CI grades with the base's copy of each pinned grader, prepr with this head's: a grammar only this diff
 registers in `tools/policy/agreement.mjs` passes prepr's agreement lane and is refused by `wave-script`
 (#2366). Step 3f runs `brief_lint.mjs` only when a pinned path changed: run
-`node tools/policy/brief_lint.mjs` before a handoff (#2373). Step 6b's `failed while being recorded` is
-an exit code from one unleased run, not a cause: re-run that script alone first (#2375).
+`node tools/policy/brief_lint.mjs` before a handoff. Step 6b's `failed while being recorded` is
+an exit code from one unleased run, not a cause: re-run that script alone first.
 
 ## Never run a full `tests/derive_closures.sh` off Linux
 
diff --git a/dev/programme/delivery/3051.md b/dev/programme/delivery/3051.md
new file mode 100644
index 000000000..d3a8a9b47
--- /dev/null
+++ b/dev/programme/delivery/3051.md
@@ -0,0 +1 @@
+- [#3051](https://github.com/tvofi/heatpump_optimizer/pull/3051) — **open**, R10-PREPR-CAP: prepr cap (R10-PREPR-CAP)
diff --git a/tests/gate_lock.py b/tests/gate_lock.py
index 211957dc0..503b13bac 100644
--- a/tests/gate_lock.py
+++ b/tests/gate_lock.py
@@ -118,6 +118,12 @@ MACHINE_MEASURING = ("tests/stress.py", "tests/harness_headers.py")
 # A waiter rewrites its ticket every poll; one this far past it is dead.
 TICKET_SECONDS = 60
 RENEW_REFUSED_RC = 75
+# A bounded wait that ran out (P206): distinct from the renew refusal, so a
+# caller can name the lease unrun instead of failing or passing it.
+WAIT_BOUND_RC = 76
+# Written by `take`, removed by `release`: the witness that a label once held
+# the lease, so `flock_wrap` can tell a lapsed lease from one never taken (P211).
+HELD_PREFIX = "held-"
 # --- priority (#gate-priority, tvofi 2026-10-20) -----------------------------
 # The lease carries an integer priority; it never decides who deserves one. The
 # environment channel is what a caller prepr.sh cannot edit uses, and the
@@ -143,6 +149,10 @@ class RenewRefused(RuntimeError):
     """Another label waits for the lease, so the holder may not extend it."""
 
 
+class WaitBoundExceeded(Exception):
+    """A bounded wait for the lease ran past its bound (P206)."""
+
+
 @dataclass(frozen=True)
 class Owner:
     label: str
@@ -516,9 +526,13 @@ def take(
     wait: bool = True,
     owner_pid: int | None = None,
     priority: int | None = None,
+    wait_bound: float | None = None,
 ) -> Owner:
     """Acquire the gate lease for ``label``, queueing behind older live tickets.
 
+    ``wait_bound`` seconds ends the wait with `WaitBoundExceeded`; None waits
+    without end, the behaviour of every caller that does not name a bound.
+
     ``owner_pid`` names a process that outlives the commands holding the lease
     (a seat's ``$PPID``). It is recorded in the owner file so a later take can
     steal an orphaned lease whose holder exited without releasing (#1143).
@@ -527,6 +541,7 @@ def take(
     """
     prio = _declared_priority(priority)
     said, ticket = False, None
+    started = time.monotonic()
     try:
         while True:
             owner = read_owner(lock_dir)
@@ -536,6 +551,7 @@ def take(
                 if not queue or queue[0].path == ticket:
                     fresh = _new_owner(label, lease_seconds, owner_pid)
                     if fresh.create(lock_dir / OWNER_NAME):
+                        _mark_held(lock_dir, label)
                         return fresh
                     continue
                 held = f"{queue[0].label}, at the head of the queue"
@@ -544,6 +560,7 @@ def take(
                 if owner.expired:
                     fresh = _new_owner(label, lease_seconds, owner_pid)
                     fresh.write(lock_dir / OWNER_NAME)
+                    _mark_held(lock_dir, label)
                     return fresh
                 return renew(label, lock_dir=lock_dir, lease_seconds=lease_seconds,
                              owner_pid=owner_pid)
@@ -559,12 +576,39 @@ def take(
                 print(f"gate_lock: waiting for the lease held by {held}"
                       " (yours? export HPO_GATE_LOCK_LABEL with that label)", file=sys.stderr)
                 said = True
+            waited = time.monotonic() - started
+            if wait_bound is not None and waited >= wait_bound:
+                raise WaitBoundExceeded(
+                    f"waited {waited:.0f} s for the lease held by {held}, "
+                    f"past its bound of {wait_bound:.0f} s")
             time.sleep(WAIT_POLL_SECS)
     finally:
         if ticket is not None:
             ticket.unlink(missing_ok=True)
 
 
+def _held_path(lock_dir: Path, label: str) -> Path:
+    return lock_dir / (HELD_PREFIX + label.replace("/", "_"))
+
+
+def _mark_held(lock_dir: Path, label: str) -> None:
+    _held_path(lock_dir, label).touch()
+
+
+def wait_bound_for(scope_run: str) -> float:
+    """The wait bound for the script(s) in run.sh's SCOPE_RUN file: the longest
+    recorded duration among them, so a bound is never shorter than the run it
+    waits behind; ``LEASE_SECONDS`` when a name is unnamed or unrecorded."""
+    try:
+        names = Path(scope_run).read_text().split()
+    except OSError:
+        return float(LEASE_SECONDS)
+    seconds = [_recorded_seconds(name) for name in names]
+    if not seconds or any(sec is None for sec in seconds):
+        return float(LEASE_SECONDS)
+    return float(max(seconds))
+
+
 def renew(
     label: str,
     *,
@@ -608,6 +652,7 @@ def release(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR) -> bool:
         raise RuntimeError(f"lease held by {owner.label}, not {label}")
     (lock_dir / OWNER_NAME).unlink(missing_ok=True)  # the queue stays
     (lock_dir / HOLDING_NAME).unlink(missing_ok=True)
+    _held_path(lock_dir, label).unlink(missing_ok=True)
     return True
 
 
@@ -862,18 +907,32 @@ def slot_auto_lease(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOC
             release_slot(label, lock_dir=lock_dir)
 
 
-def flock_wrap(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR) -> int:
+def flock_wrap(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR,
+               wait_bound: float | None = None) -> int:
     """Renew the lease, hold flock for ``argv``, release flock on exit.
 
     A renew refused because another label waits releases and takes again, at
-    the back of the queue. A label that holds no lease fails at once: it means
-    *I hold it already*, and taking one here would leave it held after the run."""
+    the back of the queue. A lease that lapsed between two commands (P211) is
+    refreshed when it is still this label's and nobody waits, and otherwise
+    taken again behind whoever waits, because the label held it once. A label
+    that never held one fails at once: it means *I hold it already*, and taking
+    one here would leave it held after the run."""
     try:
         renew(label, lock_dir=lock_dir)
     except RenewRefused as exc:
         print(f"gate_lock: {exc}; {label} re-queues", file=sys.stderr)
         release(label, lock_dir=lock_dir)
-        take(label, lock_dir=lock_dir)
+        take(label, lock_dir=lock_dir, wait_bound=wait_bound)
+    except RuntimeError:
+        if not _held_path(lock_dir, label).exists():
+            raise
+        owner = read_owner(lock_dir)
+        mine = owner is not None and owner.label == label
+        if mine and any(w.label != label for w in _queue(lock_dir)):
+            release(label, lock_dir=lock_dir)
+            _mark_held(lock_dir, label)
+        print(f"gate_lock: {label}'s lease lapsed; taking it again", file=sys.stderr)
+        take(label, lock_dir=lock_dir, wait_bound=wait_bound)
     with flock_context(lock_dir, blocking=True) as fd:
         return run_group(argv, fd=fd)
 
@@ -987,9 +1046,10 @@ def holding_slot() -> bool:
 
 
 @contextlib.contextmanager
-def leased(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR):
+def leased(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR,
+           wait_bound: float | None = None):
     """Take the lease (queueing), hold flock inside, release on any exit."""
-    take(label, lock_dir=lock_dir)
+    take(label, lock_dir=lock_dir, wait_bound=wait_bound)
     try:
         with flock_context(lock_dir, blocking=True) as fd:
             yield fd
@@ -998,10 +1058,11 @@ def leased(label: str, *, lock_dir: Path = DEFAULT_LOCK_DIR):
             release(label, lock_dir=lock_dir)
 
 
-def auto_lease(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR) -> int:
+def auto_lease(label: str, argv: list[str], *, lock_dir: Path = DEFAULT_LOCK_DIR,
+               wait_bound: float | None = None) -> int:
     """Take the lease (queueing), hold flock for ``argv``, release on any exit."""
     env = {**os.environ, "HPO_GATE_LOCK_LABEL": label}
-    with leased(label, lock_dir=lock_dir) as fd:
+    with leased(label, lock_dir=lock_dir, wait_bound=wait_bound) as fd:
         return run_group(argv, env, fd)
 
 
@@ -1116,9 +1177,23 @@ def _cmd_slot_leased(args: argparse.Namespace) -> int:
     return 0
 
 
+def _bounded(args: argparse.Namespace, call) -> int:
+    """Run ``call(wait_bound)``; a wait past its bound exits `WAIT_BOUND_RC`
+    with one line, and touches ``--wait-marker`` so the caller names it unrun."""
+    bound = wait_bound_for(args.script) if args.script else None
+    try:
+        return call(bound)
+    except WaitBoundExceeded as exc:
+        print(f"gate_lock: {exc}; {args.label} gives up the wait", file=sys.stderr)
+        if args.wait_marker:
+            Path(args.wait_marker).touch()
+        return WAIT_BOUND_RC
+
+
 def _cmd_flock_wrap(args: argparse.Namespace) -> int:
     try:
-        return flock_wrap(args.label, args.argv, lock_dir=args.lock_dir)
+        return _bounded(args, lambda b: flock_wrap(
+            args.label, args.argv, lock_dir=args.lock_dir, wait_bound=b))
     except RuntimeError as exc:  # a label never taken: refuse, run nothing
         print(f"gate_lock: flock-wrap refused, {args.label} holds no lease: {exc}", file=sys.stderr)
         return 1
@@ -1126,7 +1201,8 @@ def _cmd_flock_wrap(args: argparse.Namespace) -> int:
 
 def _cmd_auto_lease(args: argparse.Namespace) -> int:
     argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
-    return auto_lease(args.label, argv, lock_dir=args.lock_dir)
+    return _bounded(args, lambda b: auto_lease(
+        args.label, argv, lock_dir=args.lock_dir, wait_bound=b))
 
 
 def _cmd_slot_auto_lease(args: argparse.Namespace) -> int:
@@ -1177,6 +1253,10 @@ def _parser() -> argparse.ArgumentParser:
         help="renew, hold flock for a subprocess, release flock on exit",
     )
     wrap_p.add_argument("--label", required=True)
+    wrap_p.add_argument("--script", default=None,
+                     help="run.sh's SCOPE_RUN file: bound the wait by its recorded duration")
+    wrap_p.add_argument("--wait-marker", default=None,
+                     help="file touched when the wait ran past its bound")
     wrap_p.add_argument("argv", nargs=argparse.REMAINDER, help="command after --")
     wrap_p.set_defaults(func=_cmd_flock_wrap)
 
@@ -1188,6 +1268,10 @@ def _parser() -> argparse.ArgumentParser:
 
     auto_p = sub.add_parser("auto-lease", help="take, hold flock for a command, release")
     auto_p.add_argument("--label", required=True)
+    auto_p.add_argument("--script", default=None,
+                     help="run.sh's SCOPE_RUN file: bound the wait by its recorded duration")
+    auto_p.add_argument("--wait-marker", default=None,
+                     help="file touched when the wait ran past its bound")
     auto_p.add_argument("argv", nargs=argparse.REMAINDER, help="command after --")
     auto_p.set_defaults(func=_cmd_auto_lease)
 
@@ -1235,6 +1319,95 @@ def _parser() -> argparse.ArgumentParser:
     return p
 
 
+def _wait_cases(g) -> list[tuple[str, bool, str]]:
+    """P206 (a bounded wait) and P211 (a lapsed own lease), against module ``g``."""
+    import tempfile
+
+    out = []
+    poll = g.WAIT_POLL_SECS
+    g.WAIT_POLL_SECS = 0.05
+    try:
+        with tempfile.TemporaryDirectory() as tds:
+            root = Path(tds)
+            d = root / "wait"
+            g.take("holder", lock_dir=d, lease_seconds=60, wait=False)
+            t0 = time.monotonic()
+            try:
+                g.take("w", lock_dir=d, lease_seconds=60, wait_bound=0.3)
+                past = False
+            except g.WaitBoundExceeded:
+                past = time.monotonic() - t0 >= 0.3
+            out.append(("a waiter past its bound raises WaitBoundExceeded", past, ""))
+            ns = argparse.Namespace(label="w", script=str(root / "scope"),
+                                    wait_marker=str(root / "marker"))
+            import io
+            buf = io.StringIO()
+            real_bound = g.wait_bound_for
+            g.wait_bound_for = lambda _scope: 0.2  # the bound an awaited script would set
+            try:
+                with contextlib.redirect_stderr(buf):
+                    rc = g._bounded(ns, lambda b: g.take(
+                        "w", lock_dir=d, lease_seconds=60, wait_bound=b) and 0)
+            finally:
+                g.wait_bound_for = real_bound
+            err = buf.getvalue()
+            out.append(("and exits WAIT_BOUND_RC with one line and the marker",
+                        rc == g.WAIT_BOUND_RC and (root / "marker").exists()
+                        and err.count("gives up the wait") == 1, f"rc={rc} err={err!r}"))
+            g.release("holder", lock_dir=d)
+            got = g.take("w", lock_dir=d, lease_seconds=60, wait_bound=5)
+            out.append(("a take within its bound still runs", got.label == "w", ""))
+            g.release("w", lock_dir=d)
+            stress = root / "scope.stress"
+            stress.write_text("tests/stress.py\n")
+            recorded = _recorded_seconds("tests/stress.py")
+            unnamed = root / "scope.unnamed"
+            unnamed.write_text("tests/not_a_recorded_script.py\n")
+            out.append(("the bound is the recorded duration, else LEASE_SECONDS",
+                        recorded is not None and wait_bound_for(str(stress)) == recorded
+                        and wait_bound_for(str(unnamed)) == LEASE_SECONDS,
+                        f"recorded={recorded}"))
+
+            # P211: the lease lapsed between two commands of a label that held it.
+            ran = root / "ran"
+            cmd = [sys.executable, "-c", f"open({str(ran)!r}, 'w').close()"]
+            d2 = root / "lapse"
+            g.take("seat", lock_dir=d2, lease_seconds=60, wait=False)
+            past_t = datetime.now(UTC) - timedelta(seconds=5)
+            Owner("seat", past_t, past_t).write(d2 / OWNER_NAME)
+            rc = g.flock_wrap("seat", cmd, lock_dir=d2)
+            fresh = g.read_owner(d2)
+            out.append(("an expired own lease with no waiter refreshes and runs",
+                        rc == 0 and ran.exists() and fresh is not None
+                        and fresh.label == "seat" and not fresh.expired, f"rc={rc}"))
+            g.release("seat", lock_dir=d2)
+            ran.unlink(missing_ok=True)
+            d3 = root / "queued"
+            g.take("seat", lock_dir=d3, lease_seconds=60, wait=False)
+            Owner("seat", past_t, past_t).write(d3 / OWNER_NAME)
+            at = (datetime.now(UTC) + timedelta(seconds=60)).isoformat()
+            (d3 / f"{TICKET_PREFIX}000000000001").write_text(
+                f"label=w\npid={os.getpid()}\nexpires_at={at}\n")
+            try:
+                g.flock_wrap("seat", cmd, lock_dir=d3, wait_bound=0.3)
+                queued = False
+            except g.WaitBoundExceeded:
+                queued = True
+            out.append(("one with a waiting ticket re-queues and does not run beside it",
+                        queued and not ran.exists(), f"ran={ran.exists()}"))
+            d4 = root / "never"
+            try:
+                g.flock_wrap("stranger", cmd, lock_dir=d4)
+                refused = False
+            except RuntimeError:
+                refused = True
+            out.append(("a label that never held one is still refused", refused
+                        and not ran.exists(), ""))
+    finally:
+        g.WAIT_POLL_SECS = poll
+    return out
+
+
 # --- acceptance (#404) -------------------------------------------------------
 
 
@@ -1953,6 +2126,10 @@ def _acceptance() -> int:
     for name, ok, detail in _slot_hold_cases(sys.modules[__name__]):
         R.check(name, ok, detail)
 
+    R.section("wait bound and lapsed lease")
+    for name, ok, detail in _wait_cases(sys.modules[__name__]):
+        R.check(name, ok, detail)
+
     for d in (d1, d2, d3, d4, d5, d6):
         if d.exists():
             _clear_lock(d)
diff --git a/tests/run.sh b/tests/run.sh
index a2302a57e..cc60f29b9 100755
--- a/tests/run.sh
+++ b/tests/run.sh
@@ -284,6 +284,7 @@ in_scope() {
 failed=0
 LANE="${LANE:-main}"
 step=0
+WAIT_UNRUN=""
 suite_start=$(date +%s)
 
 # Why a given script was scoped out, in the words tests/closure.py used.
@@ -343,12 +344,23 @@ leased() {
         "$PYTHON" tests/gate_lock.py slot-auto-lease --label "run.sh-$$" --owner-pid $$ -- "$@"
       fi ;;
     *)
+      # A wait that ran past its bound (P206) leaves a marker; run_always then
+      # records the script as a named unrun, never as a pass.
+      rm -f "$one.waited"
       if [ -n "${HPO_GATE_LOCK_LABEL:-}" ]; then
-        "$PYTHON" tests/gate_lock.py flock-wrap --label "$HPO_GATE_LOCK_LABEL" -- "$@"
+        "$PYTHON" tests/gate_lock.py flock-wrap --label "$HPO_GATE_LOCK_LABEL" \
+          --script "$one" --wait-marker "$one.waited" -- "$@"
       else
         echo "  LEASE: $s runs under the gate lease as run.sh-$$"
-        "$PYTHON" tests/gate_lock.py auto-lease --label "run.sh-$$" -- "$@"
-      fi ;;
+        "$PYTHON" tests/gate_lock.py auto-lease --label "run.sh-$$" \
+          --script "$one" --wait-marker "$one.waited" -- "$@"
+      fi
+      local rc=$?
+      if [ -e "$one.waited" ]; then
+        WAIT_UNRUN="$s"
+        return 0
+      fi
+      return $rc ;;
   esac
 }
 
@@ -364,9 +376,11 @@ run_always() {
   if [ "$JOBS" -le 1 ]; then
     echo
     echo "########## $* ##########"
+    WAIT_UNRUN=""
     leased "$@" || rc=$?
   else
     printf '  [%s] start  %s\n' "$(date +%H:%M:%S)" "$*"
+    WAIT_UNRUN=""
     leased "$@" > "$WORKDIR/$id.log" 2>&1 || rc=$?
     finished=$(date +%s)
     printf '  [%s] %-6s %s (%ss)\n' \
@@ -374,6 +388,15 @@ run_always() {
       "$*" "$((finished - started))"
   fi
   finished=$(date +%s)
+  if [ -n "$WAIT_UNRUN" ]; then
+    # The sanctioned exit (gate-scoping.md): a named unrun left to CI, never a pass.
+    local note="SKIP: $WAIT_UNRUN (waited past its bound for the gate lease; left to CI, named unrun)"
+    printf '%s\n' "$note" > "$WORKDIR/$id.log"
+    [ "$JOBS" -le 1 ] && { echo; echo "$note"; }
+    printf '%s\t0\t%s\t#skip %s\n' "$id" "$((finished - started))" "$WAIT_UNRUN" \
+      >> "$WORKDIR/$LANE.manifest"
+    return 0
+  fi
   printf '%s\t%s\t%s\t%s\n' "$id" "$rc" "$((finished - started))" "$*" \
     >> "$WORKDIR/$LANE.manifest"
   if [ "$rc" -ne 0 ] && [ "$JOBS" -le 1 ]; then
diff --git a/tools/audit/carry_audit.py b/tools/audit/carry_audit.py
index d004c6b1f..dd2d6ec41 100644
--- a/tools/audit/carry_audit.py
+++ b/tools/audit/carry_audit.py
@@ -126,6 +126,15 @@ NOTE_HEADING = re.compile(NONBLOCK.pattern + r"|residual|\bowed\b|instrument fin
                           r"|out of scope|follow-?up|^carry\b", re.I)
 BLOCK_HEADING = re.compile(r"\bblock", re.I)
 
+# A roster carry index stated as not done, outside the carry sections (R10-RCA-JIDOKA-YIELD,
+# M1; #3010 r1: "Carry 1: **not done in this pull request.**" under no heading
+# `LEAD` reads). Matched on the item with its code spans and double-quoted text
+# removed (`owed_carry`): unstripped, a body quoting the phrase as an example is read.
+OWED_CARRY = re.compile(r"\bcarry\s*\[?\d+\]?\W{0,6}[^.\n]{0,80}?\b(?:not done|not (?:built|answered|implemented)"
+                        r"|not in this (?:part|diff|pull request|change)|still (?:not met|open|owed)"
+                        r"|owed (?:by|to|in))", re.I)
+QUOTED = re.compile(r'"[^"\n]*"|\u201c[^\u201d\n]*\u201d')
+
 CARRY = re.compile(r"(?<![\w-])Carry:")
 ITEM_REF = re.compile(r"\(item\s+([0-9a-f]{8})\)")
 # a code span as CommonMark closes one: a backtick run closes only on a run of
@@ -219,7 +228,7 @@ def items(text: str, verdict: bool) -> list[dict]:
             why = "" if NONE_ITEM.match(t) else "section"
         else:
             why = ("section" if LEAD.search(sec) else "lead" if LEAD.match(first)
-                   else "under lead" if inherited else "")
+                   else "under lead" if inherited else "owed carry" if owed_carry(t) else "")
         flagged = bool(why)
         it["why"] = why
         it["lead"] = False
@@ -231,6 +240,12 @@ def items(text: str, verdict: bool) -> list[dict]:
     return out
 
 
+def owed_carry(text: str) -> bool:
+    """Whether an item states a roster carry as not done, outside code and quotes."""
+    bare = CODE_SPAN.sub(" ", text)
+    return bool(OWED_CARRY.search(QUOTED.sub(" ", bare)))
+
+
 def carry_segments(text: str) -> list[str]:
     """The text of every `Carry:` marker in <text>, each cut at the next `Carry:`
     or the line end; a `Carry:` inside a code span is a quoted example, not one."""
@@ -860,6 +875,22 @@ def _self_test() -> int:
     r = run(head + "## Friction\n\n- PULL_REQUEST_TEMPLATE.md: unenforced: its example "
             "`Carry: R10-LIVE` names a group a fixer copies unchecked. Carry: R10-LIVE\n")
     check("the same finding with a plain marker routes (null control)", r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
+    # M1 (R10-RCA-JIDOKA-YIELD): a roster carry stated as not done, outside the
+    # carry sections, is a finding item needing a marker. #3010 r1's paragraph.
+    owed = ("**Roster carry (open, not answered by this change).** Carry 1: **not done in "
+            "this pull request.** The group's roster entry folded R10-FLOW-POSTMERGE.\n")
+    r = run(head + owed)
+    check("an owed roster carry in an untitled paragraph is an unrouted [owed carry] item",
+          r["u"] == 1 and [x["why"] for x in r["rows"]] == ["owed carry"])
+    r = run(head + owed.rstrip() + " Carry: R10-LIVE\n")
+    check("the same paragraph with a Carry: marker routes (null control)",
+          r["u"] == 0 and r["b"] == 0 and len(r["rows"]) == 1)
+    r = run(head + 'The reviewer wrote "Carry 1: not done in this pull request" as an example.\n')
+    check("an owed-carry phrase inside double quotes is not read", r["rows"] == [])
+    r = run(head + "The probe pattern `Carry 1: not done in this pull request` is an example.\n")
+    check("... nor one inside a code span", r["rows"] == [])
+    r = run(head + "Carry 1 landed in this change and is answered by the test below.\n")
+    check("a carry index with no not-done phrase is no finding (null control)", r["rows"] == [])
     # One row per boundary of the marker grammar, each with the status it must
     # read: dev/audit/harnesses/r10_carry_parser_mutants.py names the mutant
     # each row kills alone, so no predicate is pinned only with another.
diff --git a/tools/policy/field_coverage.mjs b/tools/policy/field_coverage.mjs
index 64ebd6531..071f4855d 100644
--- a/tools/policy/field_coverage.mjs
+++ b/tools/policy/field_coverage.mjs
@@ -357,6 +357,7 @@ const DECLARED = {
   'pinned tools/audit/prepare_baseline.sh': { none: 'check-wave-script reads its ISOLATED_DIMS line as text; it grades no input here' },
   'pinned tools/audit/round6/D11/fix/codeowners_gap.py': { none: 'reads CODEOWNERS and workflows; residual (D11-s1-03), no arm here' },
   'stamp rule 4': { none: 'reads commit parents and subjects; residual (D11-s1-02), no arm here' },
+  'carry_audit owed-carry': { none: 'reads the prose of a body item (a carry index beside a not-done phrase), not a structured input; graded by carry_audit --self-test, whose rows fail under the arm\'s two mutants' },
 }
 
 function derivedSet(report) {
@@ -368,6 +369,9 @@ function derivedSet(report) {
   const stamp = fs.readFileSync(path.join(ROOT, 'tools/release/stamp.py'), 'utf8')
   if (/^def rule4_problem\(/m.test(stamp)) set.push('stamp rule 4')
   else report.refused.push('registry: tools/release/stamp.py defines no rule4_problem, so rule 4 is not in the set')
+  const audit = fs.readFileSync(path.join(ROOT, 'tools/audit/carry_audit.py'), 'utf8')
+  if (/^OWED_CARRY = /m.test(audit)) set.push('carry_audit owed-carry')
+  else report.refused.push('registry: tools/audit/carry_audit.py defines no OWED_CARRY, so its owed-carry arm is not in the set')
   return set
 }
 
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index acca5adc0..3ff71ba5a 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -518,7 +518,20 @@ for p in [*sorted(pathlib.Path("tests").glob("*.py")),
 sys.exit(1 if bad else 0)
 PY
 }
+# One prepr resolves the interpreter once (V148): `recorder_parses` costs ~5 s, and
+# step 6a and step 6c's `copies_line` both ask. The main flow sets
+# PREPR_RECORDER_CACHE to a file; a command substitution cannot share a variable,
+# a file it can. Unset (every self-test fixture), each call resolves afresh.
 recorder_python() { # -> the interpreter on stdout; rc 1 with the remedy when none parses
+  local cache=${PREPR_RECORDER_CACHE:-} out r
+  if [ -n "$cache" ] && [ -s "$cache" ]; then
+    printf '%s\n' "$(tail -n +2 "$cache")"; return "$(head -n 1 "$cache")"
+  fi
+  out=$(recorder_python_resolve); r=$?
+  [ -z "$cache" ] || printf '%s\n%s\n' "$r" "$out" > "$cache"
+  printf '%s\n' "$out"; return "$r"
+}
+recorder_python_resolve() { # the uncached resolution
   local c state=${HPO_STATE_DIR:-$HOME/.local/state/hpo}
   if [ -n "${HPO_RECORDER_PYTHON:-}" ]; then
     if recorder_parses "$HPO_RECORDER_PYTHON"; then
@@ -971,11 +984,13 @@ body_line() { # body file, head sha, title, paths file, merge base, head, [unpin
 }
 
 # Step 7e's whole body, so `--self-test` drives the code the step runs.
-# WHY THIS EXISTS (R10-FLOW-JIDOKA). Of round 10's blocked fix reviews, 25 were
-# `carry-missing`: a finding with no destination, which `pr-contract` decides
-# only after the push, with `carry_audit.py check --body`. This is that same
-# checker on the body this run is handed, so the refusal lands before review.
-# It adds no rule (decision 0012); carry_audit.py decides, unmodified.
+# WHY THIS EXISTS (R10-FLOW-JIDOKA). `pr-contract` decides a body's markers only
+# after the push, with `carry_audit.py check --body`; this is that same checker on
+# the body this run is handed, so a missing or dead marker is refused before review.
+# It does NOT judge the `carry-missing` verdict, which is fix-review.md step 10
+# (the destination holds the finding and its control): carry_audit's test is a
+# marker that names a live destination. That gap is process state (c), the step
+# followed and short of its intent: dev/audit/rca/R10-RCA-JIDOKA-YIELD.md.
 #
 # THE ROSTER IS THE ROUND'S BRANCH, FETCHED NOW. fix-review.md step 10 opens a
 # carry at the round's `handoff/audit-r<N>-roster`, never in this worktree, so
@@ -1030,13 +1045,16 @@ preflight_body() { # body file, roster dir, [forwarded numbers...] -> preflight'
 # custom_components/ (a new production name a test already defines) -- runs it
 # here. The scan reads the whole tree, so its wall time is paid only then.
 copies_line() { # tree root, changed-paths file -> one line; rc 0 clean, 1 a copy, 3 skipped
-  local out r
+  local out r py
   if ! grep -qE '^(tests|custom_components)/.*\.py$' "$2" 2>/dev/null; then
     echo "the diff changes no .py under tests/ or custom_components/, so no test can newly share a production name"
     return 3
   fi
   [ -f "$1/tests/closure.py" ] || { echo "no tests/closure.py under $1, so no-copies was not run"; return 3; }
-  out=$(cd "$1" && PYTHONPATH=tests/hastub python3 tests/closure.py no-copies 2>&1); r=$?
+  # The interpreter that parses the tree (V148): the bare `python3` is the system
+  # one on a seat whose PATH still resolves to 3.11, which cannot parse it.
+  py=$(cd "$1" && recorder_python) || { printf '%s\n' "$py"; return 1; }
+  out=$(cd "$1" && PYTHONPATH=tests/hastub "$py" tests/closure.py no-copies 2>&1); r=$?
   if [ "$r" -eq 0 ]; then printf '%s\n' "$out" | tail -1; return 0; fi
   echo "$(printf '%s\n' "$out" | grep -m1 '^COPY-CLAIMED' || printf '%s\n' "$out" | tail -1) ($(printf '%s\n' "$out" | grep -c '^COPY-CLAIMED') in all) -- import the production symbol instead (tests/README.md), or the closures job refuses it"
   return 1
@@ -2028,6 +2046,29 @@ EOS
   got=$(copies_line "$CR" "$CR/changed-none.txt"); r=$?
   st "$r" 3 "a diff touching no .py under tests/ or custom_components/ skips, even over a copy"
   case "$got" in *'changes no .py under tests/ or custom_components/'*) st 1 1 "and the skip line names the boundary";; *) st 0 1 "and the skip line names the boundary";; esac
+  # V148: the interpreter is recorder_python's, never the bare PATH python3.
+  CPB=$(mktemp -d); mkdir -p "$CPB/bin" "$CPB/good" "$CPB/state/venv-ci/bin" "$CPB/empty"
+  printf '#!/bin/sh\nexit 1\n' > "$CPB/bin/python3"; chmod +x "$CPB/bin/python3"
+  printf '#!/bin/sh\nexit 0\n' > "$CPB/state/venv-ci/bin/python3"; chmod +x "$CPB/state/venv-ci/bin/python3"
+  printf '#!/bin/sh\necho "venv ran: $*"\n' > "$CPB/good/pyrun"; chmod +x "$CPB/good/pyrun"
+  # A PATH whose first python3 cannot parse the tree, plus a parsing seat venv:
+  # the venv runs (a wrapper that parses AND prints, so the run is visible).
+  printf '#!/bin/sh\n[ "$1" = - ] && exit 0\necho "no-copies ran under the venv"\n' > "$CPB/state/venv-ci/bin/python3"
+  got=$(HPO_STATE_DIR="$CPB/state" PATH="$CPB/bin:$PATH" copies_line "$CR" "$CR/changed-py.txt"); r=$?
+  st "$r" 0 "a PATH python3 that cannot parse the tree is skipped for the parsing seat venv"
+  case "$got" in *'no-copies ran under the venv'*) st 1 1 "and no-copies ran under that venv, not the bare python3";; *) st 0 1 "and no-copies ran under that venv, not the bare python3";; esac
+  got=$(HPO_STATE_DIR="$CPB/empty" PATH="$CPB/bin:$PATH" copies_line "$CR" "$CR/changed-py.txt"); r=$?
+  st "$r" 1 "with no interpreter that parses the tree no-copies is refused, never read as clean or skipped"
+  case "$got" in *seat_venv.sh*) st 1 1 "and the refusal names seat_venv.sh";; *) st 0 1 "and the refusal names seat_venv.sh";; esac
+  printf '#!/bin/sh\n[ "$1" = - ] && exit 0\necho "no-copies ran under the override"\n' > "$CPB/good/pyrun"
+  got=$(HPO_RECORDER_PYTHON="$CPB/good/pyrun" HPO_STATE_DIR="$CPB/empty" PATH="$CPB/bin:$PATH" copies_line "$CR" "$CR/changed-py.txt"); r=$?
+  case "$got" in *'under the override'*) st 1 1 "HPO_RECORDER_PYTHON naming a parsing interpreter is the one that runs (null control)";; *) st 0 1 "HPO_RECORDER_PYTHON naming a parsing interpreter is the one that runs (null control)";; esac
+  # One resolution per run: with the cache set, the second ask replays the first.
+  RC_CACHE="$CPB/cache"; : > "$RC_CACHE"
+  first=$(PREPR_RECORDER_CACHE="$RC_CACHE" HPO_RECORDER_PYTHON="$CPB/good/pyrun" recorder_python)
+  second=$(PREPR_RECORDER_CACHE="$RC_CACHE" HPO_RECORDER_PYTHON=/bin/false recorder_python)
+  st "$second" "$first" "a second recorder_python in one run replays the cached resolution"
+  rm -rf "${CPB:?}"
   rm -f "$CR/tests/closure.py"
   got=$(copies_line "$CR" "$CR/changed-py.txt"); r=$?
   st "$r" 3 "a tree with no tests/closure.py skips, never refuses"
@@ -3595,6 +3636,9 @@ else
   rm -f "$slot_stderr"
 fi
 
+# One interpreter resolution per run, shared by steps 6a and 6c (`recorder_python`).
+PREPR_RECORDER_CACHE=/tmp/prepr-recpy.$$; : > "$PREPR_RECORDER_CACHE"  # not exported: the nested --self-test must resolve afresh
+
 # --- 2. the scoped gate's MODE line, printed rather than inferred.
 # CLAUDE.md rule 1: `MODE: SCOPED -- 0 script(s) run` and `MODE: FULL` both
 # print zero and mean opposite things. Printing it is the whole step; a seat
@@ -3852,7 +3896,7 @@ if diff_paths "$BASE" "$COPY_PATHS"; then
 else
   step "no-copies" 1 "the changed-path list did not derive from $BASE...HEAD, so no-copies was not run"
 fi
-rm -f "$COPY_PATHS"
+rm -f "$COPY_PATHS" "$PREPR_RECORDER_CACHE"
 
 # --- 6e. no moved path re-added: tests.yml's fast job runs the layout guard;
 # `moved_line` above, 0.4 to 2.1 s. It reads the index against $BASE, so it needs

