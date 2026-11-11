# Review packet #3448
head: c562b07972c71226a8cb54d0efd4376c76921c1c
base: f24d107bd7aa170bea7419251a4b7f4f48b732f6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=130468961652 success
arch-score / arch-score id=130471594317 success
arm id=130468514859 skipped
budget-raise-gate / budget-raise-gate id=130471594328 success
cancel-superseded id=130471284552 success
codeql id=130471595894 skipped
codeql / Analyze (actions) id=130468866024 success
codeql / Analyze (javascript-typescript) id=130468865951 success
codeql / Analyze (python) id=130468865928 success
gate id=130472127525 failure
governance id=130471596063 skipped
governance / delivery-status id=130468866223 success
governance / delivery-status-publish id=130468868149 skipped
governance / env-matrix id=130468865950 success
governance / instrument-self-tests id=130468866242 in_progress
governance / policy-docs id=130468865975 success
governance / record id=130468868864 skipped
governance / wave-script id=130468866083 success
hassfest id=130471595748 skipped
hassfest / hassfest id=130468866401 success
kernel-points id=130471595533 skipped
pr-contract id=130472129669 skipped
prelude id=130471284143 success
refresh id=130471284623 success
sweep-self id=130472459854 skipped
tests id=130471595736 skipped
tests / arch-instrument id=130469147709 success
tests / briefs id=130468866050 success
tests / browser id=130469147713 success
tests / claims-autofix id=130470857637 skipped
tests / closure-scope id=130468865925 success
tests / closures id=130469147831 in_progress
tests / coverage id=130469147649 in_progress
tests / fast (3.14) id=130469147605 success
tests / mutation id=130468866015 success
tests / mutation-autofix id=130469312487 skipped
tests / mutation-pins id=130469311393 skipped
tests / nightly-ha id=130469150629 skipped
tests / nightly-status id=130468866108 failure
tests / replay id=130469149874 skipped
tests / typing id=130469147731 success
validate id=130471595998 skipped
validate / validate-hacs id=130468865952 success

## Refusals
red-unanswered: concluded red check `gate` is not named in ## Red checks

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at c562b07972c71226a8cb54d0efd4376c76921c1c in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         bash tools/audit/seat/cloud_relay.sh --self-test
             `tools/audit/seat/cloud_relay.sh` is in the tree at this head
  unverified git show a7628041dc:tools/audit/seat/cloud_relay.sh | grep -n 'carry_fold_arm() {\|FETCH_HEAD\|level_set carry-fold'
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test'
             `tools/audit/seat/mutant_run.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff a7628041dc HEAD
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 185699076fb42c0082be4e5eaae31ab1abf2c1ad)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 185699076fb42c0082be4e5eaae31ab1abf2c1ad
Fix review: blocked 185699076fb42c0082be4e5eaae31ab1abf2c1ad mutation-vacuous: rv-real-bodypush-outside-wt rv-nohandoff-not-on-level rv-folded-memo-no-entry rv-privref-not-deleted

bus-nonce: dd0783524bf6f8b4eeccb75eb4441eae

## Block

Round 1 (first review). Measured head 185699076fb42c0082be4e5eaae31ab1abf2c1ad, still the tip of `handoff/r10-review-dispatch-residue-p1` when this verdict was written (`ev/head-recheck.txt`).

The body's seven named mutants are all KILLED. But the driver run at this head (`ev/mutants.txt`, spec `ev/mutants.json`) reports four survivors on changed production lines in `tools/audit/seat/cloud_relay.sh` `carry_fold_arm`. Two of them leave behaviour the body claims with nothing testing it:

- `rv-real-bodypush-outside-wt`: `(cd "$wt" && bash "$HERE/body_push.sh" ...)` becomes `(bash "$HERE/body_push.sh" ...)`. It SURVIVES. That one-token edit puts back exactly the Carry 14 defect: body_push.sh runs in the relay's own checkout, at main's tip, not the handoff tip. The self-test always sets `HPO_RELAY_BODYPUSH`, so the production `body_push.sh` line is never executed. Its stub twin `rv-stub-outside-wt` is KILLED. The body says "`HPO_RELAY_BODYPUSH` now replaces only the `body_push.sh` call inside that worktree", but in fact it replaces a separate copy of the whole line. A cure that is cheap and in place: one shared call, the way `HPO_RELAY_FOLD` already works (e.g. `(cd "$wt" && ${HPO_RELAY_BODYPUSH:-bash "$HERE/body_push.sh"} "$topic" "$body")`). Then the stub runs the production line.
- `rv-nohandoff-not-on-level`: `if [ $rc = 0 ]` becomes `if [ $rc = 0 ] || [ -z "$htip" ]`. It SURVIVES. Under this mutant, a CARRY-LANDED topic with no `handoff/<topic>` is recorded in `cloud-folded` and announced FOLDED, with no body ever pushed. The body claims "A missing handoff is now on the level; at the base it was only printed, with no level line", and no self-test arm creates a fold topic without a `handoff/` ref (the self-test's `cfref handoff/` calls are only for cf-a, cf-e, cf-f and cf-g). One arm is owed: a CARRY-LANDED topic with no handoff ref is OWED "no handoff/<topic>", on the level, and not in `cloud-folded`.
- `rv-folded-memo-no-entry` (a topic already in `cloud-folded` is not memoed) SURVIVES. It is equivalent: the `cloud-folded` grep that follows also skips with no fetch. It needs no test and is listed because survivor_list.py requires every survivor.
- `rv-privref-not-deleted` (`git update-ref -d refs/hpo-relay/fold/<topic>` replaced by `true`) SURVIVES. This is cleanup only: the refspec is forced (`+`), so a stale private ref cannot be the next worktree's head. It is listed for completeness, and no test is required.

The re-cut owes the two arms or edits above, plus a mutant run showing `rv-real-bodypush-outside-wt` and `rv-nohandoff-not-on-level` KILLED.

## Evidence

- RESULT base self-test at a7628041dc: `cloud_relay self-test: 416 checks, 0 failed`, rc=0 (`ev/selftest-base.txt`). The body's figure is re-derived.
- RESULT head self-test: `433 checks, 0 failed`, rc=0 (`ev/selftest-head.txt`). Re-derived.
- RESULT failing-test-first: head file with base's `carry_fold_arm` spliced in, giving `433 checks, 9 failed`, rc=1 (`ev/selftest-red.txt`). The nine FAIL names include all four the body quotes. Re-derived.
- RESULT body's mutants re-created by this reviewer: foldref-fetch-head, foldtip-assert-off, foldmemo-drops-line, foldmemo-no-skip, foldttl-never-retry, foldttl-always-retry and foldtip-wide-lsremote are all KILLED, and NULL SURVIVED. The reviewer's own rv-memo-key-ignores-body, rv-blocked-never-stands, rv-memo-not-saved and rv-stub-outside-wt are KILLED. The four survivors are above.
- Null controls: the self-test checks `null control (carry 14): ...` and `null control: a moved wip ref is judged again` / `... as is a moved body ref` pass at the head. The carry-14 null control fails on the spliced base arm, because there the stub ran outside the worktree. `foldmemo-drops-line` is KILLED, as Carry 22's control requires.
- Harness: the finding has no committed out-of-tree harness. The carries' own instrument is the self-test arms the roster prescribes, and all the prescribed arms are present: Carry 14's planted concurrent fetch, the sequential null control and two mutants; Carry 22's not-refetched check with the level line standing, the moved-ref re-judge, and the TTL before and after. The cost figures (27-33 s, about 181 s per pass) are the triage's live-relay numbers. This reviewer could not re-derive them either, because no relay state exists in a cloud seat.
- Base anchors 805, 818, 838, 843 and 849 were re-derived (`ev/anchors-and-class.txt`).
- Class: `git grep 'worktree add[^|;]*FETCH_HEAD'` at the head over tools/ and .claude/ returns one other site, `.claude/workflows/audit-plan.js:144`. That is a one-shot plan reviewer's prose instruction in its own session, not a long-lived checkout with concurrent fetches. It is outside P556's cause and the reviewer finds no open seam. The body names no rule, but each carry states one seam.
- merge-tree: `git merge-tree --write-tree origin/main 185699076f` gives rc=0 and tree e67f818dc0, so it is clean against origin/main f24d107bd7 (`ev/merge-tree.txt`).
- VERSION, RELEASE_NOTES.md and the manifest are untouched (`ev/version-untouched.txt`). The diff is one file. Claims files are untouched, so there is no golden drift to compare.
- Gate scope: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `tests/doc_claims.py` printed `ALL 297 checks PASSED` (`ev/doc_claims.txt`). `tests/structure.py` printed `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). Archscore printed `dS +0.0000 NULL` (`ev/archscore.txt`). No budget moved.
- CI: no pull request exists yet, so there is no review packet and no CI run to read. There are no red checks to answer. `merge_train.py owed-reds` is in `ev/owed-reds.txt`.
- Carry accounting: the roster group R10-REVIEW-DISPATCH-RESIDUE at `handoff/audit-r10-roster` dbff400dec now holds 26 carries. Carry[14] (P556) and carry[22] (P580) match the body's scope, and the body's Carry 17 / part-6 exclusion and the "do not widen dispose" constraint are honoured. The body's statement that "Carry 24 refers to no carry" held at 88fe33042c (24 entries) and no longer holds at dbff400dec, where index 24 is DESIGN-REVIEW-ROUND-CONTEXT. See Findings.
- Forward-carry: the body says none, and this reviewer found no later-stage constraint produced by the diff.

## Findings

- The body's filler "Carry 24 refers to no carry" is stale at roster tip dbff400dec: index 24 now exists (0-based), and review_packet.py's whole-group 1-based count would now demand Carries 1-26. That is the BRIEF-CARRIES-PART-SCOPE defect the roster already holds as this group's carry[25]. The re-cut body should restate its carry note against the roster at its own push. Carry: dismissed: already carried as R10-REVIEW-DISPATCH-RESIDUE carry[25] (BRIEF-CARRIES-PART-SCOPE) on handoff/audit-r10-roster dbff400dec

## Friction

none

## Delta diff: git diff 185699076fb42c0082be4e5eaae31ab1abf2c1ad c562b07972c71226a8cb54d0efd4376c76921c1c
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index cabf0be13..06e7a90bb 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -265,7 +265,9 @@ FEEDBACK_RATE_K_PER_MIN = 0.2
 FEEDBACK_DEADBAND_SHARE = 0.1
 #: How far below the inlet the loop may wind the target down, K. A controller
 #: stops a running compressor when its inlet reaches target plus its heating
-#: hysteresis, 0.5 K at the least on the reporting firmware; less one 0.1 K
+#: hysteresis, a setting whose minimum is 0.5 K on the reporting firmware
+#: (3.92.3; #3372 comment 6756915104, which also says not to assume 2 K, and
+#: that input 10107 carries the start threshold in effect); less one 0.1 K
 #: entity step and a 0.1 K inlet rise between passes, 0.3 K cannot stop it at
 #: any permitted hysteresis, because a loop write is sent even when it moves
 #: less than :data:`SETPOINT_TOLERANCE` (:func:`_note_sent`).
@@ -1009,6 +1011,12 @@ def _clamp_cut(held: ArbiterState, slot: str, value: Any, observed: Any, at: dat
     the rest of the run, and ``hold`` reads it as held. A cut of
     today's target, or any other reading (a person, a revert to the
     controller's default), is ``hold``'s as before and starts the run over.
+
+    On a Luxtronik the two limits are Smart Home Interface inputs 10104
+    (parameter 979) and 10103 (parameter 87), which clamp register 10001
+    (#3372 comment 6756915104). They are inferred from the readback here:
+    no configured entity names them, and a controller without them is cut
+    the same way.
     """
     if slot != "space_setpoint":
         return False
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index e82329357..d3cc9c43c 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -992,7 +992,7 @@
  {
   "id": "C111",
   "source": "README.md + docs/*.md",
-  "claim": "every external link answers 200 to a HEAD request (20 links)",
+  "claim": "every external link answers 200 to a HEAD request (21 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links",
   "result": "not run: pass --links",
   "verdict": "unverifiable",
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 89a7a0b2a..7865068d2 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -114,7 +114,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C108 | `README.md + docs/*.md` | every relative link resolves (89 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 89 links, broken=[], of which removed-by-the-export=[] | **true** |  |
 | C109 | `README.md + docs/how-it-works.md` | the links to docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md resolve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | finder_wall in tools/audit/prepare_baseline.sh removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md; this tree cannot answer | **unverifiable** | not checkable in the export -- finder_wall removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md |
 | C110 | `README.md + docs/*.md` | every image the documentation embeds exists (21 images) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 21 images, missing=[] | **true** |  |
-| C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (20 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
+| C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (21 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
 | C112 | `strings.json + translations/*.json` | every translation file carries exactly the keys strings.json declares | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | languages=['de', 'en', 'sv'], missing={'de': 0, 'en': 0, 'sv': 0}, extra={'de': 0, 'en': 0, 'sv': 0} | **true** |  |
 | C113 | `README.md` | entity names are translated into English, Swedish and German | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['de', 'en', 'sv'] measured=['de', 'en', 'sv'] | **true** |  |
 | C114 | `README.md` | every entity's display name comes from the translation files | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | untranslated=[] | **true** |  |
diff --git a/dev/programme/delivery/3424.md b/dev/programme/delivery/3424.md
new file mode 100644
index 000000000..84c76458c
--- /dev/null
+++ b/dev/programme/delivery/3424.md
@@ -0,0 +1 @@
+- [#3424](https://github.com/tvofi/heatpump_optimizer/pull/3424) — **open**, R10-TRAIN-RESIDUE: r10 train residue (R10-TRAIN-RESIDUE)
diff --git a/dev/programme/delivery/3427.md b/dev/programme/delivery/3427.md
new file mode 100644
index 000000000..e79b456be
--- /dev/null
+++ b/dev/programme/delivery/3427.md
@@ -0,0 +1 @@
+- [#3427](https://github.com/tvofi/heatpump_optimizer/pull/3427) — **open**, R10-GH-READ-RESIDUE: r10 gh read residue (R10-GH-READ-RESIDUE)
diff --git a/dev/programme/delivery/3433.md b/dev/programme/delivery/3433.md
new file mode 100644
index 000000000..22519ccc8
--- /dev/null
+++ b/dev/programme/delivery/3433.md
@@ -0,0 +1 @@
+- [#3433](https://github.com/tvofi/heatpump_optimizer/pull/3433) — **open**, R10-WATER-SETPOINT-FEEDBACK residue: the contributor's answers on registers, watchdog and hysteresis (carry 8) (R10-WATER-SETPOINT-FEEDBACK)
diff --git a/dev/programme/delivery/3448.md b/dev/programme/delivery/3448.md
new file mode 100644
index 000000000..93f7177f3
--- /dev/null
+++ b/dev/programme/delivery/3448.md
@@ -0,0 +1 @@
+- [#3448](https://github.com/tvofi/heatpump_optimizer/pull/3448) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 1): r10 review dispatch residue p1 (R10-REVIEW-DISPATCH-RESIDUE)
diff --git a/docs/configuration.md b/docs/configuration.md
index c017a157f..903816fc6 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -746,15 +746,25 @@ writes, at every 15-minute plan step:
     such a controller presumably stops), and no higher than the controller accepts: a Luxtronik
     clamps the target to its own minimum return target and return limit, so a ceiling above the
     limit is written but not followed. A controller that starts heating only once the target sits
-    its hysteresis above the return (2 K on a Luxtronik's default) is not started by a smaller lift;
-    it only keeps a running compressor near its minimum. On the install this was written for, a
+    its hysteresis above the return is not started by a smaller lift;
+    it only keeps a running compressor near its minimum. That hysteresis is a setting of the
+    controller, not a fixed 2 K: a Luxtronik accepts 0.5 K at the least, and the start threshold in
+    effect (the return target less the hysteresis) is input 10107 of its Smart Home Interface, which
+    ha-luxtronik-shi publishes as its *Demand border* sensor
+    ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)).
+    This integration does not read it. On the install this was written for, a
     0.5 K lift held 26–31 Hz once running, 1–1.5 K ramped to 73–81 Hz. For a low-temperature floor
     heating, 0.5–2 K and 30–40 °C may be a starting point; check them against the compressor's
     frequency and power.
   - The integration that exposes the controller must poll it at least
     every 10 minutes and restore its heating mode after a controller
     restart: a Luxtronik Smart Home Interface drops every value set through
-    it after 600 s without access and after each restart. A reverted
+    it after 600 s without access and after each restart. Any access
+    re-arms those 600 s, a read as much as a write, so polling alone keeps
+    a written value; ha-luxtronik-shi polls every 30 s by default and
+    offers 10–300 s, and restores what it wrote after a controller restart
+    only where its restore-after-device-reset option is on
+    ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)). A reverted
     set-point is noticed and written again; a reverted heating mode is not
     visible to this integration. No second tool may write the same
     registers: a Luxtronik then silently discards writes (error 816).
@@ -773,7 +783,7 @@ writes, at every 15-minute plan step:
   draw, averaged over 3 minutes, is above the planned level and up while it
   is below, and holds it while the two are within 10 % of the planned level
   (of the pump's minimum power, where the plan asks less).
-  It goes no lower than 0.1 K below the inlet, no higher than the ceiling,
+  It goes no lower than 0.3 K below the inlet, no higher than the ceiling,
   and never to the gate. Hot water, both duties, a boost, a defrost, the
   system-identification experiment and full power write the value above
   unchanged and start the loop over. Where the controller cuts a written
@@ -783,7 +793,13 @@ writes, at every 15-minute plan step:
     minimum), or the first write of a run does not start a stopped
     compressor — the same limitation as without the loop;
   - its minimum return target sits below the return during the heating
-    season, or the loop cannot wind the compressor down past it.
+    season, or the loop cannot wind the compressor down past it. A
+    Luxtronik cuts the set-point to its minimum return target (input 10104
+    of its Smart Home Interface, parameter 979) and its return limit (input
+    10103, parameter 87), both of which ha-luxtronik-shi publishes as
+    sensors ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)).
+    This integration does not read them: it takes the two limits from the
+    value the controller reports back after a write.
 - **For an *Indoor temperature* entity** each of the three is the step's
   planned room temperature, clamped to the entity's range (5 °C as the gate
   where the mode offers no hot-water-only option). An entity whose own
diff --git a/tests/ci_ratchet.py b/tests/ci_ratchet.py
index 14c90c71a..3ef2e6303 100644
--- a/tests/ci_ratchet.py
+++ b/tests/ci_ratchet.py
@@ -649,21 +649,29 @@ def run_chain(r: dict) -> "list[str] | None":
     return chain[::-1]
 
 
-def gather_runs(out_file, *, repo=None, runner=None, window: int = PUSH_WINDOW) -> int:
+def gather_runs(out_file, *, repo=None, runner=None, window: int = PUSH_WINDOW, sleep=None) -> int:
     """The ci-ratchet job's runs.json: the newest `window` (PUSH_WINDOW when
     grading) push runs of ci.yml and the pre-umbrella tests.yml together, each
     with its jobs. Any failed read refuses by name: a short window is not a
-    fast one."""
+    fast one. Every read rides tools/audit/seat/gh_read.py's read rule (4 reads,
+    transient statuses only): main went red twice in a day (2026-11-10, -11) on
+    one HTTP 502 here, the grading step never having run."""
+    sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
+    import gh_read  # noqa: E402 -- the one read rule
     repo = repo or os.environ.get("GITHUB_REPOSITORY")
     if not repo:
         raise _refusal("--gather-runs needs GITHUB_REPOSITORY")
     run = runner or subprocess.run
 
     def api(*argv):
-        proc = run(["gh", "api", *argv], capture_output=True, text=True)
-        if proc.returncode != 0 or not (proc.stdout or "").strip():
-            raise _refusal(f"gh api {argv[-1]} failed (rc {proc.returncode}): "
-                           f"{(proc.stderr or '').strip()[:300]}")
+        def attempt():
+            proc = run(["gh", "api", *argv], capture_output=True, text=True)
+            if proc.returncode != 0 or not (proc.stdout or "").strip():
+                return proc, (proc.stderr or "").strip() or "gh printed nothing"
+            return proc, None
+        proc, failure, _n, why = gh_read.retry(attempt, gh_read.gh_wait, sleep or time.sleep)
+        if failure is not None:
+            raise _refusal(f"gh api {argv[-1]} failed (rc {proc.returncode}) {why}: {failure[:300]}")
         return proc.stdout
     runs = []
     for wf in PUSH_RUNS:
@@ -1156,10 +1164,34 @@ def self_test() -> int:
         ck("--gather-runs --window N keeps the newest N (a record's wider window)",
            n == 3 and sum("/jobs?" in a[-1] for a in reads) == 3
            and all("per_page=3" in a[-1] for a in reads if "/jobs?" not in a[-1]), msg or f"n={n}")
-        msg = refused(lambda: gather_runs(f, repo="o/r", runner=lambda argv, **_kw: subprocess.CompletedProcess(
+        naps = []
+        msg = refused(lambda: gather_runs(f, repo="o/r", sleep=naps.append, runner=lambda argv, **_kw: subprocess.CompletedProcess(
             argv, 1, "", "gh: HTTP 502")))
-        ck("a failed runs read refuses by name (a short window is not a fast one)",
-           "failed (rc 1)" in msg and "HTTP 502" in msg, msg or "no refusal")
+        ck("a sustained 502 on the runs read refuses by name after the read rule's 4 reads (a short window is not a fast one)",
+           "failed (rc 1)" in msg and "HTTP 502" in msg and len(naps) == 3, msg or "no refusal")
+        # R10-GH-READ-RESIDUE: one 502 on the jobs listing of one run (main red 2026-11-10, -11) is ridden out.
+        reads.clear()
+        flaky = []
+
+        def gh_502_once(argv, **kw):
+            if "/jobs?" in argv[-1] and not flaky:
+                flaky.append(argv)
+                return subprocess.CompletedProcess(argv, 1, "", "gh: HTTP 502")
+            return gh(argv, **kw)
+        n, msg = safe(lambda: gather_runs(f, repo="o/r", runner=gh_502_once, sleep=lambda _s: None))
+        ck("one injected 502 on a jobs listing still gathers the whole window",
+           n == 16 and len(flaky) == 1 and all("jobs" in r for r in json.loads(f.read_text())["workflow_runs"]
+                                               if run_kind(r) is not None), msg or f"n={n}")
+        reads.clear()
+        gone = []
+        naps.clear()
+
+        def gh_404(argv, **_kw):
+            gone.append(argv)
+            return subprocess.CompletedProcess(argv, 1, "", "gh: Not Found (HTTP 404)")
+        msg = refused(lambda: gather_runs(f, repo="o/r", runner=gh_404, sleep=naps.append))
+        ck("null control: a 404 refuses after one read, no sleep",
+           len(gone) == 1 and not naps and "HTTP 404" in msg, msg or "no refusal")
 
     # --- runner queue is not work (main red, CI job 121295715608) ----------
     # Run 40225415246, its timeline as the jobs API gave it (minutes from the
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 2f0d65cf7..db9014512 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -4391,6 +4391,59 @@ def stateless_findings(pages: dict[str, str], exempt=STATELESS_EXEMPT) -> list[s
     return out
 
 
+def power_feedback_facts() -> dict[str, str]:
+    """The phrases configuration.md owes the power-feedback loop, from its constants."""
+    from heatpump_optimizer import pump_arbiter as pa
+
+    return {
+        "start hold": f"first {pa.FEEDBACK_START_HOLD.total_seconds() / 60:g} minutes of a run",
+        "rate": f"{pa.FEEDBACK_RATE_K_PER_MIN:g} K per minute",
+        "window": f"averaged over {pa.FEEDBACK_WINDOW.total_seconds() / 60:g} minutes",
+        "deadband": f"within {pa.FEEDBACK_DEADBAND_SHARE * 100:g} % of the planned level",
+        "lower bound": f"no lower than {pa.FEEDBACK_DOWN_K:g} K below the inlet",
+    }
+
+
+#: The contributor's answers on the Luxtronik Smart Home Interface (Carry 8 of
+#: R10-WATER-SETPOINT-FEEDBACK): the source of the watchdog, clamp-register and
+#: hysteresis statements, cited where each is made.
+_SHI_ANSWERS = "pull/3372#issuecomment-6756915104"
+
+
+def check_power_feedback_claims() -> None:
+    R.section("the power-feedback loop's figures and controller facts (R10-WATER-SETPOINT-FEEDBACK Carry 8)")
+    text = DOCS["configuration.md"]
+    loop = _section(text, "- **Power feedback (", "\n- **", "configuration.md")
+    poll = _section(text, "  - The integration that exposes the controller must poll", "\n  - ", "configuration.md")
+    start = _section(text, "A controller that starts heating only once", "On the install this was written for", "configuration.md")
+    if loop is None or poll is None or start is None:
+        return
+    flat = " ".join(loop.split())
+    for name, phrase in power_feedback_facts().items():
+        R.check(f"the loop's {name} is the constant's: {phrase!r}", phrase in flat)
+    for name, body, facts in (
+        ("the polling precondition", poll, ("600 s", "restart")),
+        ("the start condition", start, ("10107", "0.5 K")),
+        ("the loop's preconditions", loop, ("10104", "10103", "0.5 K")),
+    ):
+        R.check(f"{name} cites the contributor's answers", _SHI_ANSWERS in body)
+        missing = [fact for fact in facts if fact not in body]
+        R.check(f"{name} states {', '.join(facts)}", not missing, repr(missing))
+    R.check("no start condition is stated as a 2 K Luxtronik default",
+            "2 K on a Luxtronik" not in " ".join(text.split()))
+    import inspect
+    from heatpump_optimizer import pump_arbiter as pa
+
+    source = inspect.getsource(pa)
+    down = re.search(r"((?:^#:.*\n)+)FEEDBACK_DOWN_K = ", source, re.M)
+    R.check("pump_arbiter still comments FEEDBACK_DOWN_K (anchor)", down is not None)
+    comment_id = _SHI_ANSWERS.rsplit("-", 1)[1]
+    R.check("the assumed minimum hysteresis behind FEEDBACK_DOWN_K cites the contributor's answers",
+            down is not None and comment_id in down.group(1))
+    R.check("the inferred clamp bounds (_clamp_cut) cite the contributor's answers and name both inputs",
+            all(fact in (pa._clamp_cut.__doc__ or "") for fact in (comment_id, "10104", "10103")))
+
+
 def check_stateless() -> None:
     R.section("the user pages describe the integration as it is, with no change history (R10-USER-DOCS-FINAL)")
     pages = _user_pages()
@@ -4479,6 +4532,7 @@ def main() -> int:
     check_coffee_button()
     check_readme_marketplace()
     check_surface_coverage()
+    check_power_feedback_claims()
     check_stateless()
     return R.close("checks")
 
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index a10b5b2dc..714d6b389 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -1911,6 +1911,21 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   awk -v e=$(( $(date +%s) - 3601 )) '$1 == "cf-g" { $5 = e } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
   rm -f "$t/folds"; carry_fold_arm >/dev/null 2>&1
   chk "... and retried once it is" 0 grep -q -- "--topic cf-g " "$t/folds"
+  # The production body_push.sh line (no HPO_RELAY_BODYPUSH): HERE points at a stand-in body_push.sh that records its working tree's HEAD.
+  mkdir -p "$t/fakehere"; printf '#!/bin/bash\necho "$@" >> %s/rbps\ngit rev-parse HEAD >> %s/rheads\n' "$t" "$t" > "$t/fakehere/body_push.sh"
+  cfref handoff/cf-i code.txt "code I"; cfref handoff-wip/cf-i BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-i-body BODY.md "the body I"
+  : > "$t/rbps"; : > "$t/rheads"; cfo=$(unset HPO_RELAY_BODYPUSH; HERE=$t/fakehere; carry_fold_arm 2>&1)
+  chk "the production body_push.sh line runs the script on the kept body (carry 14)" 0 grep -q "^cf-i .*cloud-fold-cf-i.md" "$t/rbps"
+  chk "... inside the worktree at handoff/cf-i's tip, not the relay's own checkout" 0 grep -qx "$(cftip handoff/cf-i)" "$t/rheads"
+  chk "... and never at main's tip" 1 grep -qx "$(cftip main)" "$t/rheads"
+  # A CARRY-LANDED topic with no handoff/<topic> is OWED on the level, never recorded as folded or announced.
+  cfref handoff-wip/cf-h BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-h-body BODY.md "the body H"
+  : > "$t/bps"; cfo=$(carry_fold_arm 2>&1)
+  chk "a CARRY-LANDED topic with no handoff/<topic> is OWED" 0 grep -q "OWED carry-fold cf-h .*no handoff/cf-h" <<< "$cfo"
+  chk "... on the level" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-h .*no handoff/cf-h" "$LOG.level"
+  chk "... with no cloud-folded entry" 1 grep -q "^cf-h " "$t/state/cloud-folded"
+  chk "... no FOLDED announcement" 1 grep -q "FOLDED cf-h" <<< "$cfo"
+  chk "... and no body_push.sh run" 1 grep -q "^cf-h " "$t/bps"
   unset HPO_RELAY_FOLD HPO_RELAY_BODYPUSH; cd "$t/w" || exit 1
   cd / && rm -rf "$t"
   echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
diff --git a/tools/audit/seat/gh_calls.py b/tools/audit/seat/gh_calls.py
index 0f5ed462d..64ac22d04 100644
--- a/tools/audit/seat/gh_calls.py
+++ b/tools/audit/seat/gh_calls.py
@@ -171,7 +171,7 @@ def self_test():
         # a real gh (the CI runner does; a Mac does not).
         tools = w / "tools"
         tools.mkdir()
-        for tool in ("ps", "tr", "cut", "wc", "mv", "date", "cat", "sh", "sed", "mkdir", "env", "python3", "chmod"):
+        for tool in ("ps", "tr", "cut", "wc", "mv", "date", "cat", "sh", "sed", "mkdir", "env", "python3", "chmod", "git"):
             found = shutil.which(tool)
             if found:
                 (tools / tool).symlink_to(found)
@@ -575,6 +575,39 @@ def self_test():
             ("gh extension exec", ["extension", "exec", "x"]))
         for label, args in refused:
             check(f"{label} is refused", run(args).returncode == 1)
+        # R10-GH-READ-RESIDUE (P449): one install on the daemons' PATH, run from any checkout. The
+        # baked tree t1, a worktree t2 of it, a clone t3 git does not register beside it, and an
+        # untracked file t4 of the same name.
+        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+        from throwaway_git import throwaway_git_clone, throwaway_git_init  # noqa: E402 -- the one throwaway-repo builder
+        t1 = w / "t1"
+        (t1 / "tools" / "pr").mkdir(parents=True)
+        (t1 / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text())
+        genv = throwaway_git_init(t1, "-q")
+        for argv in (["add", "."], ["commit", "-qm", "x"], ["worktree", "add", "-q", str(w / "t2")]):
+            subprocess.run(["git", *argv], cwd=t1, env=genv, check=True)
+        # t5: a registered worktree whose gh_comment.py git does not track (the tracked half of the rule)
+        subprocess.run(["git", "worktree", "add", "-q", str(w / "t5")], cwd=t1, env=genv, check=True)
+        subprocess.run(["git", "rm", "-q", "--cached", "tools/pr/gh_comment.py"], cwd=w / "t5", env=genv, check=True)
+        throwaway_git_clone(t1, w / "t3", "-q")
+        (w / "t4" / "tools" / "pr").mkdir(parents=True)
+        (w / "t4" / "tools" / "pr" / "gh_comment.py").write_text(gcs.read_text())
+        baked = good.replace("gcpy=@HPO_GH_COMMENT@\n", f"gcpy={t1}/tools/pr/gh_comment.py\n")
+        for label, tree, want_rc in (
+                ("the baked tree's own script", "t1", 7),
+                ("a second registered worktree's tracked script", "t2", 7),
+                ("null control: a clone git does not list beside the baked tree", "t3", 1),
+                ("null control: an untracked file of the same path and name", "t4", 1),
+                ("null control: a registered worktree whose script is not tracked", "t5", 1)):
+            check(f"second tree: {label}",
+                  run([], via=f"{py} -I {w / tree}/tools/pr/gh_comment.py {W}", shim_text=baked).returncode == want_rc)
+        guard_mut = baked.replace('[ "$wl" = "worktree $troot" ] && ok=1', 'ok=1')
+        check("mutant: the worktree registration dropped lets an unlisted clone through",
+              guard_mut != baked and run([], via=f"{py} -I {w / 't3'}/tools/pr/gh_comment.py {W}", shim_text=guard_mut).returncode == 7)
+        tr_mut = baked.replace(" && git -C \"$troot\" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1", "")
+        check("mutant: the tracked-file predicate dropped lets an untracked script in a registered worktree through",
+              tr_mut != baked and run([], via=f"{py} -I {w / 't5'}/tools/pr/gh_comment.py {W}", shim_text=tr_mut).returncode == 7)
+        install(good)
         mut = good.replace("trackers='201 ", "trackers='0 ")
         check("mutant: the guard's issue number changed lets the planted post through",
               mut != good and run(planted, shim_text=mut).returncode == 7)
diff --git a/tools/audit/seat/merge_train.py b/tools/audit/seat/merge_train.py
index 986b1c7b4..57bd64199 100644
--- a/tools/audit/seat/merge_train.py
+++ b/tools/audit/seat/merge_train.py
@@ -2399,7 +2399,9 @@ class Train:
         """Whether `policy_approve` posts step 5's approval at <h>: (mandate id,
         policy paths, why). The id is None when nothing is posted, and <why>
         then says why ('' when there is nothing to say: no policy path, no
-        --mandate, or the owner's approval already at <h>). A read only -- the
+        --mandate, or the owner's approval already at <h>; or a refusal: the
+        owner's own latest CHANGES_REQUESTED, or a `gh` account that is not
+        the owner's). A read only -- the
         one decision `policy_approve` posts on and `policy_admits` (the
         pre-flight) judges with, so the two cannot drift."""
         cid = self.mandate_id()
@@ -2414,6 +2416,19 @@ class Train:
         if any(g._is_owner(r.get("user")) and r.get("state") == "APPROVED" and r.get("commit_id") == h
                for r in self._reviews(pr, "the policy approval")):
             return None, pol, ""  # the owner's approval is at the head already: never re-posted
+        own = [r for r in self._reviews(pr, "the policy approval")
+               if g._is_owner(r.get("user")) and not g.AGENT_DECLARED.search(r.get("body") or "")
+               and r.get("state") in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED")]
+        if own and own[-1].get("state") == "CHANGES_REQUESTED":
+            # `budget_raise_gate.approval`'s rule, which refuses a mandated approval over it.
+            return None, pol, (f"{g.OWNER_LOGIN}'s own latest decisive review is CHANGES_REQUESTED, "
+                               "which a mandated approval does not override")
+        code, login = self.run(["gh", "api", "user", "--jq", ".login"])
+        if code or login.strip() != g.OWNER_LOGIN:
+            # The post is the owner's review and the pre-flight judges it as the owner's: a
+            # `gh` account that is not the owner posts one `policy_gate` refuses at the merge.
+            return None, pol, (f"the gh account is {login.strip()[:40] or 'unreadable'}, not {g.OWNER_LOGIN}"
+                               if not code else "the gh account could not be read")
         now = datetime.datetime.now(datetime.timezone.utc)
         try:
             live, why = g.mandate_state(cid, *self._mandate_read(cid), now, now.strftime("%Y-%m-%dT%H:%M:%SZ"),
@@ -4382,6 +4397,8 @@ def _self_test() -> int:
                 return 0, world.get("required", "fast\n")
             if "app_approve.sh" in a:
                 return world.get("approve", (0, "APPROVED"))
+            if argv[:3] == ["gh", "api", "user"]:  # the acting account
+                return 0, world.get("post_user", {"login": "orchestrator"})["login"]
             if argv[:3] == ["gh", "pr", "review"]:
                 # What GitHub would hold after the post: the next reviews read
                 # returns it -- unless the read-back is meant to fail.
@@ -4922,6 +4939,16 @@ def _self_test() -> int:
         check(f"policy post null: {name} posts nothing, and the policy stop is today's",
               rc == 1 and posts(calls) == 0 and "policy:" in lines[-1] and "no decisive review" in lines[-1]
               and not merged(calls))
+    # Carries 7/11 and 8/12 (R10-TRAIN-RESIDUE): the post and the pre-flight's simulation share
+    # `policy_approval_due`, so one refusal each covers both.
+    rc, lines, calls = go({**POL, "reviews": [], "mandate": mandate(NOW),
+                           "post_user": {"login": "someone-else", "id": 9, "type": "User"}}, mandate=str(MID))
+    check("policy post: a gh account that is not the owner posts nothing, and the stop names the account",
+          rc == 1 and posts(calls) == 0 and not merged(calls) and any("gh account is someone-else" in ln for ln in lines))
+    rc, lines, calls = go({**POL, "reviews": [{**owner_review(H0, NOW), "state": "CHANGES_REQUESTED", "body": ""}],
+                           "mandate": mandate(NOW), "post_user": OWNER}, mandate=str(MID))
+    check("policy post: the owner's own latest CHANGES_REQUESTED posts no mandated approval",
+          rc == 1 and posts(calls) == 0 and not merged(calls) and "CHANGES_REQUESTED" in lines[-1])
     rc, lines, calls = go({**POL, "reviews": [owner_review(H0, NOW)], "mandate": mandate(NOW), "post_user": OWNER},
                           mandate=str(MID))
     check("policy post: an owner approval already at the head is not re-posted, and it lands",
@@ -7633,6 +7660,8 @@ def _batch_self_test(check) -> None:
                 rf = w.get("reviews_for")
                 return 0, json.dumps([(rf(w["heads"][int(n)]) if rf else [])
                                       + [r for r in w.get("posted", []) if r["pr"] == int(n)]])
+            if argv[:3] == ["gh", "api", "user"]:  # the acting account: the owner's
+                return 0, _mandate_gate().OWNER_LOGIN
             if argv[:3] == ["gh", "pr", "review"]:  # posted as the owner's account, as `gh` is
                 gm = _mandate_gate()
                 w.setdefault("posted", []).append(
diff --git a/tools/audit/seat/queue_pre_flight.py b/tools/audit/seat/queue_pre_flight.py
index f7f02fa4e..20a8afbc1 100644
--- a/tools/audit/seat/queue_pre_flight.py
+++ b/tools/audit/seat/queue_pre_flight.py
@@ -371,6 +371,8 @@ def _self_test() -> int:
                 return 0, json.dumps([world.get("comments", [])])
             if argv[:2] == ["gh", "api"] and a.endswith("/pulls/7 --jq .body // \"\""):
                 return 0, world.get("body", "")
+            if argv[:3] == ["gh", "api", "user"]:  # the acting account `policy_approval_due` reads: the owner's
+                return 0, mt._mandate_gate().OWNER_LOGIN
             return 0, ""
         return run
 
diff --git a/tools/audit/seat/shims/seat-gh b/tools/audit/seat/shims/seat-gh
index 15d7b0c8f..75060fd9a 100755
--- a/tools/audit/seat/shims/seat-gh
+++ b/tools/audit/seat/shims/seat-gh
@@ -336,6 +336,20 @@ if [ -n "${hit:-}" ]; then
     done
     if [ -n "$script" ] && [ -n "$gcpy" ]; then
       a=$(rp "$script") && b=$(rp "$gcpy") && [ "$a" = "$b" ] && ok=1
+      # Another tree's gh_comment.py (R10-GH-READ-RESIDUE, P449): the daemons' PATH carries one
+      # install, run from any checkout. Admitted by real path when it is the tracked
+      # tools/pr/gh_comment.py of a worktree git registers beside the baked tree's; a file
+      # merely so named, in a directory git does not list, stays refused.
+      if [ -z "$ok" ] && [ -n "$a" ]; then
+        case $a in */tools/pr/gh_comment.py)
+          troot=${a%/tools/pr/gh_comment.py} broot=${gcpy%/tools/pr/gh_comment.py}
+          if [ "$broot" != "$gcpy" ] && git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1; then
+            while IFS= read -r wl; do
+              [ "$wl" = "worktree $troot" ] && ok=1
+            done < <(git -C "$broot" worktree list --porcelain 2>/dev/null)
+          fi ;;
+        esac
+      fi
     fi ;;
   esac
   [ -n "$ok" ] || { echo "gh shim: a comment write on a record issue (#${trackers// /, #}) goes through tools/pr/gh_comment.py (its mandate guard refuses a post that voids a mandate); refused" >&2; exit 1; }
diff --git a/tools/ci/codescan_wait.py b/tools/ci/codescan_wait.py
index 41e9f016a..95d80cf67 100644
--- a/tools/ci/codescan_wait.py
+++ b/tools/ci/codescan_wait.py
@@ -95,6 +95,20 @@ def source(get, repo, run_id, pr, base, stop, sleep=time.sleep, now=time.monoton
         sleep(POLL_S)
 
 
+def carried_over(j):
+    """A job a partial re-run lists from the earlier attempt: completed `success` and no `steps` key at all.
+    Its analysis ran and uploaded then, and the listing no longer carries the step row; an empty or
+    lagging `steps` list is not this (the row is there, or the leg is mid-write)."""
+    return j.get("status") == "completed" and j.get("conclusion") == "success" and "steps" not in j
+
+
+def analysis(j):
+    """The conclusion of a job's analysis step: its row's, `success` for a carried-over job, else None."""
+    if carried_over(j):
+        return "success"
+    return next((s.get("conclusion") for s in j.get("steps") or [] if s["name"] == STEP), None)
+
+
 def settled(jobs):
     """Every codeql job listed completed, and each either skipped outright or with its analysis step concluded:
     a leg whose step row lags reads as stood down in `legs_uploaded`, and goes unread."""
@@ -105,7 +119,7 @@ def settled(jobs):
             return False
         if j.get("conclusion") in ("skipped", "cancelled"):
             continue
-        if not any(s["name"] == STEP and s.get("conclusion") for s in j.get("steps") or []):
+        if not analysis(j):
             return False
     return True
 
@@ -115,7 +129,7 @@ def legs_uploaded(jobs):
     out = []
     for j in jobs:
         name = j["name"]
-        if name in CODEQL and any(s["name"] == STEP and s["conclusion"] == "success" for s in j.get("steps") or []):
+        if name in CODEQL and analysis(j) == "success":
             out.append(name[name.index("(") + 1:-1])
     return sorted(out)
 
@@ -321,6 +335,20 @@ def self_test() -> int:
     reads.clear()
     check("20 null: a settled stand-down (step skipped) is not waited for",
           go(world(A.THREE[1:], A.EMPTY, [], run_jobs={100: jobs(skip=("python",))})) == [])
+    # 21-24: a partial re-run lists the carried-over jobs without `steps` (R10-GH-READ-RESIDUE, d678abfc)
+    bare = [{"name": nm, "status": "completed", "conclusion": "success"} for nm in CODEQL]
+    check("21 carried-over step-less success jobs are settled and all legs uploaded",
+          settled(bare) and legs_uploaded(bare) == legs_uploaded(jobs()) != [])
+    check("22 null: a step-less job that did not succeed is neither settled nor an uploaded leg",
+          not settled([dict(j, conclusion="failure") for j in bare]) and legs_uploaded([dict(j, conclusion="failure") for j in bare]) == [])
+    check("23 null: a lagging step row (steps present, no conclusion) is still unsettled",
+          not settled(lag()) and legs_uploaded(lag()) == [])
+    done_lag = lambda st: [{"name": nm, "status": "completed", "conclusion": "success", "steps": st} for nm in CODEQL]   # noqa: E731
+    check("23b null: a completed success job with a lagging or empty `steps` list is not carried over: unsettled, not uploaded",
+          all(not settled(done_lag(st)) and legs_uploaded(done_lag(st)) == []
+              for st in ([], [{"name": STEP, "conclusion": None}])))
+    check("24 null: a step-less job still in progress is unsettled",
+          not settled([dict(j, status="in_progress") for j in bare]))
     print(f"codescan_wait self-test: {n} checks, {bad} failed")
     return 1 if bad else 0
 
diff --git a/tools/pr/app_push.sh b/tools/pr/app_push.sh
index b499d50ae..58b8b402b 100644
--- a/tools/pr/app_push.sh
+++ b/tools/pr/app_push.sh
@@ -615,7 +615,10 @@ HELPER
   # (#1267) -- 64 MiB keeps such a push in one Content-Length request.
   # Asynchronous, as prepr above, so a stop signal interrupts the `wait`.
   local push_rc=0
-  GIT_TERMINAL_PROMPT=0 git -C "$wt" -c credential.helper= -c "credential.helper=$PRIV/credhelper.sh" \
+  # Under gh_read's git retry (git_transient only: a 5xx, a reset, a timeout; a
+  # rejection answers at once), as remerge_main.sh's fetches are.
+  GIT_TERMINAL_PROMPT=0 python3 "$(cd "$(dirname -- "$0")/../audit/seat" && pwd)/gh_read.py" --git-retry \
+    git -C "$wt" -c credential.helper= -c "credential.helper=$PRIV/credhelper.sh" \
     -c http.postBuffer=64m push "https://github.com/$repo.git" "$br" &
   wait $! || push_rc=$?
   [ "$push_rc" = 0 ] || die "the App's push of $br to $repo was refused; no pull request was opened or re-bodied"
@@ -676,7 +679,8 @@ cp "$(dirname -- "$SELF")/app_mint.sh" "$W/tool/"
 # The real guard, at the path the copy resolves it by (../audit/seat/), and the
 # signal reap it sources from there.
 mkdir -p "$W/audit/seat" && cp "$(dirname -- "$SELF")/../audit/seat/ref_privacy.py" "$W/audit/seat/" \
-  && cp "$(dirname -- "$SELF")/../audit/seat/pr_args.sh" "$W/audit/seat/"
+  && cp "$(dirname -- "$SELF")/../audit/seat/pr_args.sh" "$W/audit/seat/" \
+  && cp "$(dirname -- "$SELF")/../audit/seat/gh_read.py" "$W/audit/seat/"
 FAILS=0; N=0
 st() { N=$((N + 1)); if [ "$1" = "$2" ]; then echo "ok   $3"; else echo "FAIL $3 (got '$1', want '$2')"; FAILS=$((FAILS + 1)); fi; }
 SHA=1111111111111111111111111111111111111111
@@ -747,6 +751,7 @@ case "$*" in
     else printf 'a\0371+t@users.noreply.github.com\0371+t@users.noreply.github.com\037fix: the stub subject\036'; fi ;;
   *"push https://github.com/"*)
     if [ -f "$STUB/push-fails" ]; then echo "error: stub push refused" >&2; exit 1; fi
+    if [ -f "$STUB/push-flaky" ]; then rm -f "$STUB/push-flaky"; echo "error: RPC failed; HTTP 502 curl 22 The requested URL returned error: 502" >&2; exit 1; fi
     if [ -f "$STUB/push-tree" ]; then  # a push still running when the pusher is stopped
       echo $$ >> "$STUB/pids"
       bash -c 'sleep 30 & echo $! >> "$0"; wait' "$STUB/pids" & echo $! >> "$STUB/pids"
@@ -990,6 +995,13 @@ st "$(grep -c '^curl \(POST\|PATCH\) repos/o/r/pulls' "$W/pushfail/log")" 0 "and
 st "$(calls pushfail 'curl DELETE installation/token')" 1 "the token is revoked after the failed push"
 st "$(leftover pushfail)" 0 "and the private directory is gone, token and all"
 
+# R10-GH-READ-RESIDUE: one transient push failure is ridden out (gh_read's
+# git_transient); a refusal is pushed once and answered at once (the null control).
+mkcase pushflaky; : > "$W/pushflaky/push-flaky"
+run pushflaky o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 0 "a push that fails once on a 502 still lands and opens the pull request"
+st "$(grep -c '^git .*push https://github.com/' "$W/pushflaky/log")" 2 "the push was tried twice (one transient failure, one success)"
+st "$(grep -c '^git .*push https://github.com/' "$W/pushfail/log")" 1 "a refused push is tried once, never retried"
+
 mkcase mangle; : > "$W/mangle/mangle-body"
 run mangle o/r "$W/tool-wt" "$BR" "$W/body.md"; st $? 1 "a body that reads back different refuses, though the POST returned 0"
 st "$(grep -c 'modulo one trailing newline' "$W/mangle/err")" 1 "naming the byte-identity rule it failed"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
