# Review packet #3551
head: df1512502349af541505b73a81a86beb4dd6f930
base: 513a07dfdc0daf09a054826974dbb64bfea9de27

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=132318422678 skipped
cancel-superseded id=132318426631 queued
prelude id=132318426441 queued
refresh id=132318426518 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 839fcb75: R10-NUDGE-RETIRE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/ci/selftest_scope.py static
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 2 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf
Fix review: blocked 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf root-cause-unrecorded: tests / fast (3.14) red at this head, unanswered by the body (pr-contract refuses); the red is a Saturday wall-clock test inherited from main, not this diff

bus-nonce: 2b5c2b4965555d7759dbed12e3d1c519

Round 3 is a delta review over the reviewed head ef7e3373e763942a38982c679541c5aa750b3935. The head 0f191f49a8 is a merge. Its first parent is ef7e3373e7. Its second parent is a3c9c90cee, which is the handoff branch (round-3 commits f6813b73..ac5ca58c, already merged with main e23124ff at 428c7b8673) merged with origin/main 50373173d4. I measured in a detached worktree at 0f191f49a8. This is round 3, counted from the round-2 verdict at ef7e3373e7.

## Block

The delta's code is sound. Every round-2 finding is resolved, and nothing in the delta is open (Evidence). The one block is CI's owed-red contract:

- At this head, `tests / fast (3.14)` concluded `failure` (job 132252007494, MODE: FULL, forced because tools/ci/selftest_closures.json changed). The failing check is `tests/features.py`'s only FAIL: `a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked` (ev/ci_fast_head.log.gz).
- That check is in the set `merge_train.py owed-reds` prints (ev/owed_reds.txt). `pr-contract / pr-contract` (job 132265340874) started at 00:47Z, after the red concluded at 00:35Z. It printed `red checks the body must answer: ,tests / fast (3.14)` and concluded `failure` (ev/ci_pr_contract.log). The body's `## Red checks` says none is owed, so the trigger is unanswered (fix-review.md step 11).
- The cause is not this diff. `git diff 50373173d4 0f191f49a8 -- tests/ custom_components/` prints nothing. Main's `tests / fast (3.14)` at 50373173d4 (job 132244017151, started 2026-11-13T23:48Z, a Friday) concluded `success`.
- The check's fixture `_chg_seq` anchors on the real clock. At tests/features.py:62334-62336 it calls `dt_util.now()`, then `start += timedelta(days=(5 - start.weekday()) % 7)`, which is the "on a Saturday" case. Blame: b6696bd6e6 and d2184d4061, merged by #3444. Today, 2026-11-14, is a Saturday.
- Local run at this head today: `PYTHONPATH=tests/hastub python3 tests/features.py` gives the same single FAIL, with 5707 ok, rc 1 (ev/features_sat_fail.txt, ev/features_sat.log.gz). This reproduces CI.
- My shifted-clock control is void: dt_util.now shifted back one day globally (ev/friday_shift.py) crashed at check 63 with a TypeError in an unrelated time-sensitive check (ev/features_fri.log.gz). So the Friday half rests on main's green CI run over byte-identical tests/ and custom_components/, not on a local run.
- I name the class root-cause-unrecorded, not detectable, because no cheaper detector than this check shows a calendar-day red before the handoff. The remedy is for the body to answer it under `## Red checks`: name `tests / fast (3.14)`, the cause above with its #3444 origin, and either "no cheaper detector exists: this check is the cheapest", or a re-run on a weekday, which leaves the test unfixed. The test's wall-clock anchor is carried below. Fixing it in this PR would be outside its scope.

## Findings

- tests/features.py:62334-62336 (`_chg_seq`, from #3444) builds its fixture from the real `dt_util.now()` and weekday. The check "a charge-start dip that recovers is learned as neither a draw nor usage …" fails on a Saturday run, with main's code unchanged, and so reddens `tests / fast (3.14)` (an owed required check) on every PR and main push tested on a Saturday. Control: main's identical tests/ and custom_components/ were green on Friday 2026-11-13 (job 132244017151), and red today at this head both in CI and locally (ev/features_sat_fail.txt). The fix is to anchor the fixture on a fixed datetime, as the file's other Saturday cases do (lines 17489, 56767, 71761). Carry: dismissed: no receivable owner exists, because R10-OUTSIDE-DHW-CHARGE-SETTLE (the group whose #3444 added it) is at stage done and no live roster group or carries file owns tests/features.py's DHW draw-learning checks; the orchestrator owes a hotfix group or a carry-<N>.json, which a probe-only reviewer cannot create

## Evidence

- ev/HEAD.txt: 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf. The PR body `## Head` names this head, and the API read of the PR at verdict time gave head.sha 0f191f49a8 (step 7).
- Round-2 block (introduced-red under GITHUB_BASE_REF): resolved. `self_test` now pops GITHUB_BASE_REF and SELFTEST_BASE for the run and restores them afterwards. RESULT at head:
  - unset: `selftest_scope self-test: 148 checks, 0 failed`, rc 0 (ev/selftest.txt).
  - `GITHUB_BASE_REF=main`: 148 checks, 0 failed, rc 0 (ev/selftest_with_GITHUB_BASE_REF.txt).
  - `GITHUB_BASE_REF=nosuchref SELFTEST_BASE=nosuch`: 148 checks, 0 failed (ev/selftest_with_bogus_bases.txt).
  - The regression is pinned: `selftest_scope_mutants.sh` now runs its baseline and every mutant under exported `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch`, and its mutant "the self-test leaks the caller's base selectors" is refused.
- RESULT `sh tools/ci/selftest_scope_mutants.sh` at head: 35 `== ` lines, 35 `self-test rc 1`, `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0 (ev/selftest_scope_mutants.txt). This matches the body's 35. The `FAIL` and `1 failed` lines in that log are the mutants' own refusals, not a baseline red. I re-ran it alone after my own driver had finished, because the two had overlapped once (ev/selftest_scope_mutants_rerun.txt): 35 `== `, 35 refused, `every mutant refused`, rc 0.
- RESULT, my own mutant driver (ev/own_mutants.py, mine, not the finder's; the PR names no finder harness and none is owed for an instrument fix, which round 1 already recorded). Every mutant ran under `GITHUB_BASE_REF=main SELFTEST_BASE=nonesuch` (ev/own_mutants.txt):
  - KILLED pop-only-GITHUB_BASE_REF (148 checks, 1 failed).
  - KILLED pop-only-SELFTEST_BASE (148 checks, 1 failed).
  - KILLED union_entries-keeps-unmeasured-steps.
  - KILLED drift-probe-own-dirs-removed.
  - SURVIVED int-guard-passes-None. This is equivalent on its own: the guard only acts when `self_test` returns non-int, and the script's mutant "the self-test wrapper returns nothing" already pins that pair. Not a finding.
- Resolution read-back per parent (`git merge-tree --write-tree --name-only origin/main ef7e3373e7` conflicts in 4 paths: .claude/workflows/audit-find.js, dev/audit/config/bugclasses.json, dev/audit/config/finding.schema.json, tools/ci/selftest_scope_mutants.sh):
  - selftest_scope_mutants.sh keeps both sides' mutants. Main's four were retargeted to this branch's `union_entry` spellings, and each one still applies once, because the script asserts the count and refuses each one.
  - The class lists keep both main's N-provisional-gate-red-read-final and this branch's R10-SELFTEST-TABLE-SHRINK. `fold_ledger.py check`: 56 classes, 0 violation(s), rc 0 (ev/fold_ledger_check.txt).
- tools/ci/selftest_closures.json: the head's blob 84846dffa2 equals a3c9c90cee's, and it is not main's e81ad4d9d5 (ev/closures_blobs.txt). Per parent (ev/closures_per_parent.py, mine; ev/closures_per_parent.txt):
  - Against origin/main and a3c9c90cee: 0 reads and 0 flags lost, 114 steps each.
  - Against main, the head only adds: one step gains the probe `HEAD`, `objects: true` and git `diff` (ev/closures_vs_main.diff). That is over-approximation, which is safe. The body's line "main's re-recorded table (#3557) at this head" is loose on this point, but no figure depends on it.
  - Against ef7e3373e7, the only reads gone are throwaway-git-helper `probes`. Main's own re-record (#3557) dropped them, so this PR did not remove them.
  - The PR's own shrink guard accepts both ends: `SELFTEST_BASE=origin/main python3 -I tools/ci/selftest_scope.py static` gives `114 gated step(s), 0 problem(s)`, rc 0 (ev/static.txt), which matches the body's figure. `SELFTEST_BASE=ef7e3373e7…` gives 114 gated steps, 0 problems, rc 0 (ev/static_vs_reviewed_head.txt).
- `git merge-tree --write-tree origin/main 0f191f49a8`: rc 0, merges cleanly (ev/mergetree.txt).
- Step 12 scope: the PR's own diff against the merge base is 8 files. None is in custom_components/; the custom_components/, golden and budget paths in `git diff ef7e3373e7 0f191f49a8` are main's. The delta is instrument, test and record only, so the review is not widened. Step 5/14: the PR's own diff touches no VERSION, manifest, notes heading, claim file, budget or tests/closures.json.
- Owed reds (ev/owed_reds.txt): `governance / instrument-self-tests` is not in the set. Step 11's INTRODUCED exception is judged by classify below.
- CI: `merge_train.py classify 0f191f49a8 --pr 3551` printed `WAIT … pending: gate red: none` (rc 3) on every poll from 00:10Z to 00:51Z. At 00:52:54Z it printed `RED 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf pending: none red: gate` (rc 1) (ev/classify.log). The live check-runs at 00:52Z: `tests / fast (3.14)` failure, `pr-contract / pr-contract` failure, `gate` failure, and a second `gate` in_progress (ev/checks_not_green.txt). `governance / instrument-self-tests` concluded success at this head, so the round-2 introduced red is gone in CI too. `git ls-remote origin refs/pull/3551/head` printed 0f191f49a8 at 00:52Z.

## Delta diff: git diff 0f191f49a8895d5da52c4d8344f27ed2b98dc2cf df1512502349af541505b73a81a86beb4dd6f930
diff --git a/RELEASE_NOTES.md b/RELEASE_NOTES.md
index 9f16af6fe3..3bb0dfe9d3 100644
--- a/RELEASE_NOTES.md
+++ b/RELEASE_NOTES.md
@@ -1,3 +1,27 @@
+## v7.1.16
+
+**Patch stamp: 13 merges since v7.1.15 (`git log --first-parent --merges --format=%h v7.1.15..HEAD | wc -l`): the hot-water and heating plans can take the pump's own start condition, the planner prices a hot-water to heating switch that stops the compressor, and the savings reference no longer books heat the pump could not deliver; the rest is tooling.**
+
+### #3531 The pump's start condition is an optional input per duty (R10-OUTSIDE-DHW-START-HYSTERESIS)
+
+With the new optional hot-water and heating hysteresis entities set, the plan no longer starts a charge on a tank at or above the pump's own start temperature, and buys back what the hot-water minimum still needs at steps where a charge can start. If the hot-water minimum is above that start temperature, a repair notice (`dhw_minimum_above_start`) says so. The heating flow floor never uses a lift below the heating hysteresis. Installs that leave the options unset plan as before. Based on outside pull request 3440 by Bankaifan.
+
+### #3526 The planner prices a duty switch that stops the compressor (R10-DUTY-SWITCH-PLANNER-PRICE)
+
+A switch between hot water and heating that the learner reports as stopping the compressor now carries a cost in the plan, including the running time the stop takes, and the planner tries one hot-water placement that avoids it. Built on the finding and table of outside pull request 3420 by Bankaifan.
+
+### #3511 The savings reference holds only a state the pump could deliver (R10-SAV-VALUATION-RESIDUE)
+
+The reference thermostat's held room state is now the highest temperature the reference step can hold within the pump's and the mixing valve's limits, so the reference no longer draws stored heat that nobody paid for. A reference that can hold the target is unchanged.
+
+### Developer tooling, CI and audit machinery only
+
+#3557, #3546, #3558, #3499, #3520, #3539, #3549.
+
+### Record only
+
+#3559 (delivery rows, autofix), #3555, #3554 (roster).
+
 ## v7.1.15
 
 **Patch stamp: 16 merges since v7.1.14 (`git log --first-parent --merges --format=%h v7.1.14..HEAD | wc -l`): the supply switch now keeps its minimum run and pause, the mixing-valve target is labelled as a room temperature, boosts keep the learners clean while their heat settles, and the dashboard card folds its detail sections; the rest is tooling.**
diff --git a/VERSION b/VERSION
index 6329380f96..682452864e 100644
--- a/VERSION
+++ b/VERSION
@@ -1 +1 @@
-7.1.15
+7.1.16
diff --git a/custom_components/heatpump_optimizer/manifest.json b/custom_components/heatpump_optimizer/manifest.json
index 0a11baa27b..b839ba97e5 100644
--- a/custom_components/heatpump_optimizer/manifest.json
+++ b/custom_components/heatpump_optimizer/manifest.json
@@ -25,5 +25,5 @@
     "scipy>=1.10.0",
     "threadpoolctl>=3.5.0"
   ],
-  "version": "7.1.15"
+  "version": "7.1.16"
 }
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index c586c82225..8b635dab94 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -11,7 +11,7 @@
 
 const CARD_TAG = "heatpump-optimizer-card";
 const EDITOR_TAG = "heatpump-optimizer-card-editor";
-const CARD_VERSION = "7.1.15";
+const CARD_VERSION = "7.1.16";
 
 // Home Assistant's default --primary-color (#03a9f4) is 2.63:1 on a white
 // card — too light for text or for white label text on a filled button.
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index e3d6e2186d..1cba7a8c8c 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -373,7 +373,7 @@
   "source": "manifest.json",
   "claim": "manifest version equals VERSION",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented='7.1.15' measured='7.1.15'",
+  "result": "documented='7.1.16' measured='7.1.16'",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index e4521e8162..85ee2484d6 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -45,7 +45,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C39 | `docs/architecture.md:module map` | sensor.py -- 62 sensors | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=62 measured=62 | **true** |  |
 | C40 | `docs/architecture.md:module map` | switch.py -- the comment names every switch the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'], the platform constructs ['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
 | C41 | `docs/architecture.md:module map` | binary_sensor.py -- the comment names every binary sensor the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'], the platform constructs ['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
-| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='7.1.15' measured='7.1.15' | **true** |  |
+| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='7.1.16' measured='7.1.16' | **true** |  |
 | C43 | `hacs.json` | hacs.json requires Home Assistant 2025.2.0 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C44 | `README.md badge` | Home Assistant 2025.2.0+ badge matches hacs.json | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C45 | `README.md Requirements` | Home Assistant 2025.2.0 or newer | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
diff --git a/dev/programme/delivery/3572.md b/dev/programme/delivery/3572.md
new file mode 100644
index 0000000000..6356094349
--- /dev/null
+++ b/dev/programme/delivery/3572.md
@@ -0,0 +1 @@
+- [#3572](https://github.com/tvofi/heatpump_optimizer/pull/3572) — **open**, R10-DIMENSIONS-FULL-COVERAGE: r10 dimensions full coverage (R10-DIMENSIONS-FULL-COVERAGE)
diff --git a/dev/programme/delivery/3578.md b/dev/programme/delivery/3578.md
new file mode 100644
index 0000000000..74f5e0da84
--- /dev/null
+++ b/dev/programme/delivery/3578.md
@@ -0,0 +1 @@
+- [#3578](https://github.com/tvofi/heatpump_optimizer/pull/3578) — **open**, R10-HOTFIX-FEATURES-WEEKEND-CLOCK: pin the charge-settle check's clock to a weekday (R10-HOTFIX-FEATURES-WEEKEND-CLOCK)
diff --git a/dev/programme/delivery/3579.md b/dev/programme/delivery/3579.md
new file mode 100644
index 0000000000..4b5e4045ab
--- /dev/null
+++ b/dev/programme/delivery/3579.md
@@ -0,0 +1 @@
+- [#3579](https://github.com/tvofi/heatpump_optimizer/pull/3579) — **open**, R10-HOTFIX-ENTITIES-REDACTION-FLAKE: r10 hotfix entities redaction flake (R10-HOTFIX-ENTITIES-REDACTION-FLAKE)
diff --git a/tests/entities.py b/tests/entities.py
index fd2d94aeee..82b89583cc 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -25813,15 +25813,80 @@ R.check(
         if repr(_c) in _blob
     ),
 )
+def _diag_payload_at(when):
+    """The diagnostics payload with the clock pinned to ``when``."""
+    dt_util.freeze(when)
+    try:
+        _hass = FakeHass()
+        _entry = FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
+        _entry.runtime_data = integration.HeatPumpOptimizerCoordinator(
+            _hass, FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
+        )
+        return asyncio.run(_diag_mod.async_get_config_entry_diagnostics(_hass, _entry))
+    finally:
+        dt_util.freeze(None)
+
+
+def _clockless(a, b):
+    """``a`` with every value differing from ``b`` replaced by None, at any depth.
+
+    ``a`` and ``b`` are one payload taken at two pinned clocks, so what differs
+    is what the clock wrote (``exported_at``, the draw-range timestamp, any
+    later one) and no field is named here. A rounded coordinate such as "18.1"
+    is searched only in what is left, because a clock reading holds one by
+    chance (the check failed 1 of 2711 on main at 50373173).
+    """
+    if isinstance(a, dict) and isinstance(b, dict):
+        return {k: _clockless(v, b.get(k)) for k, v in a.items()}
+    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
+        return [_clockless(x, y) for x, y in zip(a, b)]
+    return a if a == b else None
+
+
+_CLOCK_A = datetime(2026, 1, 5, 3, 4, 5, tzinfo=UTC)
+_CLOCK_B = datetime(2026, 7, 9, 10, 11, 12, tzinfo=UTC)
+_ROUNDED = tuple(
+    str(round(_c, 1)) for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
+)
+
+
+def _rounded_hits(first, second):
+    """Each rounded coordinate found in the clock-free payload, with its context."""
+    blob = _json.dumps(_clockless(first, second), default=str)
+    return [
+        f"{r!r} in ...{blob[max(0, i - 40) : i + 20]}..."
+        for r in _ROUNDED
+        for i in [blob.find(r)]
+        if i >= 0
+    ]
+
+
+_diag_a = _diag_payload_at(_CLOCK_A)
+_diag_b = _diag_payload_at(_CLOCK_B)
 R.check(
     "the location is redacted whole, from data and from options, not coarsened",
     _diag_at(_diag, "config_setup", const.CONF_SOLAR_LOCATION) == _HA_REDACTED
     and _diag_at(_diag, "config", const.CONF_SOLAR_LOCATION) == _HA_REDACTED
-    and not any(
-        str(round(_c, 1)) in _blob
-        for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
-    ),
-    repr(_diag_at(_diag, "config", const.CONF_SOLAR_LOCATION)),
+    and not _rounded_hits(_diag_a, _diag_b),
+    repr(_diag_at(_diag, "config", const.CONF_SOLAR_LOCATION))
+    + " / rounded matches: "
+    + "; ".join(_rounded_hits(_diag_a, _diag_b)),
+)
+# The flake, deterministically: a clock reading that holds a rounded coordinate
+# fails the whole-blob search and passes the clock-free one.
+_diag_p = _diag_payload_at(datetime(2026, 1, 5, 3, 4, 18, 100000, tzinfo=UTC))
+R.check(
+    "the rounded-coordinate search ignores a clock reading that contains one",
+    any(r in _json.dumps(_diag_p, default=str) for r in _ROUNDED)
+    and not _rounded_hits(_diag_p, _diag_a),
+    "poisoned clock: whole-blob hit expected, clock-free hit not",
+)
+# Null control: a genuinely coarsened coordinate still fails the new search.
+_coarse = {**_diag_a, "config": {**_diag_a["config"], "coarse_probe": _ROUNDED[0]}}
+_coarse_b = {**_diag_b, "config": {**_diag_b["config"], "coarse_probe": _ROUNDED[0]}}
+R.check(
+    "a genuinely coarsened coordinate in the payload still fails the clock-free search",
+    bool(_rounded_hits(_coarse, _coarse_b)),
 )
 R.check(
     "a coordinate nested below the top level, inside a list, is redacted",
diff --git a/tests/features.py b/tests/features.py
index a663d02b74..01a0f60761 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -62331,7 +62331,9 @@ def _chg_seq(temps, charged=True, start_hm=(8, 0), heated_at=(1,), saturday=Fals
     learner.async_save_draws = _save_draws
     module = _sys.modules[type(learner).__module__]
     real_dt = module.dt_util
-    start = dt_util.now().replace(hour=start_hm[0], minute=start_hm[1], second=0)
+    # Monday 2026-11-09, never today: the weekday booking must not depend on the day the suite runs.
+    start = dt_util.now().replace(
+        year=2026, month=11, day=9, hour=start_hm[0], minute=start_hm[1], second=0)
     if saturday:
         start += timedelta(days=(5 - start.weekday()) % 7)
     clock = [start]
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index 4c50cb6178..4e3b2fb18e 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -19,9 +19,9 @@
 #
 # The state names are the ones `node tests/card_drift.mjs --list` prints.
 #
-# claims-for: 7.1.15
+# claims-for: 7.1.16
 #
-# v7.1.15: Supply minimum run and pause, valve target label, boost settling, card folds. The stamp empties the list; the
+# v7.1.16: Pump start condition input, duty-switch pricing, savings reference fix. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
 
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index a107b76be2..8b6433462b 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -62,12 +62,11 @@
 # about one release's diff, it does not expire with the stamp and is not part
 # of the inherited-claims comparison.
 #
-# claims-for: 7.1.15
+# claims-for: 7.1.16
 #
-# v7.1.15: Supply minimum run and pause, valve target label, boost settling, card folds. The stamp empties the list; the
+# v7.1.16: Pump start condition input, duty-switch pricing, savings reference fix. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
-config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the two start-hysteresis pickers (space_hysteresis_entity, dhw_hysteresis_entity), so the plain render, the seeded render and the seed each gain those two keys; every leaf that moves is "present on one side only" and ADDED at this head. Float-free and compared exactly, so re-recorded in the committed file (golden.py --record --only config_flow). No plan reads the options unset: the other 55 fixtures are byte-identical to the merge base (env_drift.py --all, one environment), which is the null.
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tools/policy/check-wave-script.mjs b/tools/policy/check-wave-script.mjs
index be218608f5..806c32b394 100644
--- a/tools/policy/check-wave-script.mjs
+++ b/tools/policy/check-wave-script.mjs
@@ -69,6 +69,14 @@ let pass = 0, fail = 0
 // This is exactly how the control run for the verdict grammar died.
 const J = (x) => JSON.stringify(x ?? null) ?? 'undefined'
 const t = (n, c, d = '') => { c ? (pass++, console.log('  ok   ' + n)) : (fail++, console.log('  FAIL ' + n + ' ' + d)) }
+// THE ONE SWITCH, READ FROM UNPINNED DATA. `wave-script` grades a pull request
+// with the BASE's copy of this file (decision 0013), so this file lands first and
+// must pass over the tree before the driver that carries the denominator (carryOf,
+// seatCarry, denominatorGaps) and over the tree after it. The switch is whether
+// the finder report schema's coverage rows require an enumerator -- a data file
+// the same pull request that lands the driver changes, never the driver's own text.
+// When it is on, the driver MUST export all three and every denominator test runs.
+const DENOM = (JSON.parse(fs.readFileSync(at('dev/audit/config/finding.schema.json'), 'utf8')).properties?.coverage?.items?.required ?? []).includes('enumerator')
 // A block that throws reports as a failure, never as a truncated run. Every
 // grouped assertion below runs inside it: without that the first unexpected
 // throw ends the process and the remaining assertions are silently unreported,
@@ -805,10 +813,10 @@ await block('the finder report schema', async () => {
   const re = (k) => new RegExp(F.properties?.[k]?.pattern ?? '$^')
   const idRe = re('id'), scopeRe = re('scope')
   const ownerRe = new RegExp(S.properties?.leads?.items?.properties?.owner_seat?.pattern ?? '$^')
-  t('scope admits a scopes.json seat id and refuses a bare dimension (D1-s3 yes, D1 no)', scopeRe.test('D1-s3') && scopeRe.test('D14-s5') && !scopeRe.test('D1') && !scopeRe.test('D16-s1'), String(scopeRe))
+  t('scope admits a scopes.json seat id and refuses a bare dimension (D1-s3 yes, D1 no)', scopeRe.test('D1-s3') && scopeRe.test('D14-s5') && !scopeRe.test('D1') && !scopeRe.test('D18-s1') && (!DENOM || scopeRe.test('D17-s1')), String(scopeRe))
   t('a finding numbered under its seat is an id the schema admits (D13-s1-01, D1-s3-51)', idRe.test('D13-s1-01') && idRe.test('D1-s3-51'), String(idRe))
   t("a lead's owner_seat admits a seat id or unknown, and refuses a bare dimension, a file, or anything else (null control)",
-    ownerRe.test('D1-s3') && ownerRe.test('D14-s5') && ownerRe.test('unknown') && !ownerRe.test('D1') && !ownerRe.test('D16-s1') && !ownerRe.test('boost.py') && !ownerRe.test('') && !ownerRe.test('D1-s3 '), String(ownerRe))
+    ownerRe.test('D1-s3') && ownerRe.test('D14-s5') && ownerRe.test('unknown') && !ownerRe.test('D1') && !ownerRe.test('D18-s1') && (!DENOM || ownerRe.test('D17-s1')) &&!ownerRe.test('boost.py') && !ownerRe.test('') && !ownerRe.test('D1-s3 '), String(ownerRe))
   // A design choice, said so: the guess is refused unless it is a class the
   // ledger HAS, so a class the judge adds is added to bugclasses.json and to
   // this enum in one pull request -- this check fails until both carry it.
@@ -951,7 +959,9 @@ await block('the scoped round driver', async () => {
   if (!blk) return
   t('the dispatch block draws on no randomness and no clock', !/Math\.random|Date\b|performance\.now|crypto/.test(blk[0]), 'found one')
   t('and no planSeats: seats come from the scopes, not a rotation over the ledger', !/planSeats/.test(rd), 'audit-find.js still names planSeats')
-  const D = new Function(`${blk[0]}\nreturn { CADENCE, EVERY_DIM_ROUNDS, activeIn, seatsFromScopes, BOXES, CHROMIUM, boxGaps }`)()
+  const D = new Function(`${blk[0]}\nreturn { CADENCE, EVERY_DIM_ROUNDS, activeIn, seatsFromScopes, BOXES, CHROMIUM, boxGaps, carryOf: typeof carryOf === 'function' ? carryOf : undefined, seatCarry: typeof seatCarry === 'function' ? seatCarry : undefined, denominatorGaps: typeof denominatorGaps === 'function' ? denominatorGaps : undefined }`)()
+  t('a schema that requires a denominator has a driver that enforces one (carryOf, seatCarry, denominatorGaps in the DISPATCH block)',
+    !DENOM || [D.carryOf, D.seatCarry, D.denominatorGaps].every((f) => typeof f === 'function'), `schema requires an enumerator; exported: ${['carryOf', 'seatCarry', 'denominatorGaps'].filter((k) => typeof D[k] === 'function')}`)
   // The seat ids and boxes below are read off the committed scopes and the
   // DISPATCH block, never named here: a re-cut of either (round 10 gave every
   // dimension three seats) must not turn a control into a test of old names.
@@ -962,8 +972,12 @@ await block('the scoped round driver', async () => {
   // nor a multiple of three, `on6` is a multiple of six.
   const free = Array.from({ length: 60 }, (_, i) => i + 10).filter((r) => !every.includes(r))
   const off = free.find((r) => r % 2 !== 0 && r % 3 !== 0), on6 = free.find((r) => r % 6 === 0)
-  t(`...and the cadence is otherwise read from the round number (D11 and D5 off at ${off}, both on at ${on6}, D0 on at ${off})`,
-    !!off && !!on6 && !D.activeIn(off, 'D11') && D.activeIn(on6, 'D11') && D.activeIn(on6, 'D5') && !D.activeIn(off, 'D5') && D.activeIn(off, 'D0'), 'the cadence is not derived from the round')
+  // D11 and D13 are held to the driver's own table, not to a number here: the
+  // cadence a tree declares is the cadence it must run (tvofi 2026-11-13 made it
+  // every round, in the pull request that lands the denominator).
+  t(`...and the cadence is otherwise read from the round number (D5 off at ${off}, on at ${on6}; D0 on at ${off}; D11 and D13 follow their CADENCE entry)`,
+    !!off && !!on6 && !D.activeIn(off, 'D5') && D.activeIn(on6, 'D5') && D.activeIn(off, 'D0')
+      && ['D11', 'D13'].every((d) => D.activeIn(off, d) === (D.CADENCE[d] === 1) && D.activeIn(on6, d)), 'the cadence is not derived from the round')
   const ids = L.dims.flatMap((d) => D.seatsFromScopes(scopes, d).map((s) => s.id))
   const fileSeats = Object.entries(scopes).filter(([k]) => !k.startsWith('_')).flatMap(([d, x]) => Object.keys(x.seats).map((k) => `${d}-${k}`))
   t('one seat per scopes.json seat, id <dim>-s<n>, nothing added or dropped', J(ids) === J(fileSeats), `${ids.length} vs ${fileSeats.length}`)
@@ -1005,19 +1019,26 @@ await block('the scoped round driver', async () => {
   // export (or another seat's tree) is visible in its prompt.
   const isoDims = new Set(L.isolated)
   const PREP = { exportDir: '/x', worktrees: Object.fromEntries(fileSeats.filter((id) => isoDims.has(id.split('-')[0])).map((id) => [id, `/w/${id}`])), python: 'py', rotation_ok: true, scopes_ok: true, scopes_rc: 0, scopes_out: 'ok' }
+  // A closed denominator for a seat: one row per step it owns, every carried item answered examined.
+  const closed = (id, args) => {
+    const seat = D.seatsFromScopes(args.scopes, id.split('-')[0]).find((x) => x.id === id)
+    if (!seat) return []
+    const carry = D.seatCarry ? D.seatCarry(args.rotation, args.round, seat) : []
+    return seat.steps.map((m) => ({ step: `${seat.dim}.${m}`, depth: 'deep', enumerator: 'stub-enumerator', universe: 1, examined: 1, not_reached: [], redispatched: carry.filter((c) => c.step === m).map((c) => ({ item: c.id, state: 'examined' })), evidence: 'stub' }))
+  }
   const drive = async (args, { prep = {}, report = () => ({}), nullSeats = [], leadsOut = {}, gather } = {}) => {
     const calls = []
     const agent = async (prompt, o) => {
       calls.push({ label: o.label, prompt, schema: o.schema })
       if (o.label === 'prepare') return { ...PREP, ...prep }
       if (o.label === 'gather' && gather) return gather(prompt)
-      if (o.label === 'gather') return { reports: Object.fromEntries(fileSeats.map((id) => [id, { dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(id) }])), absent_boxes: [] }
+      if (o.label === 'gather') return { reports: Object.fromEntries(fileSeats.map((id) => [id, { dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: closed(id, args), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(id) }])), absent_boxes: [] }
       if (o.label === 'leads') return { report_path: '/r/leads', findings: [], non_findings: [], harnesses: [], converted: [], closed: [], ...leadsOut }
       if (nullSeats.includes(o.label)) return null
       if (o.label === 'intake') return { branch: 'b', registered: [], rejected: [] }
       if (o.label === 'quiet') return { quiet_path: '/q', d3_confirmed: [] }
       if (o.label.startsWith('collect-')) return { branch: 'b', commit: 'c' }
-      return { dimension: o.label.split('-')[0], report_path: `/r/${o.label}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(o.label) }
+      return { dimension: o.label.split('-')[0], report_path: `/r/${o.label}`, coverage: closed(o.label, args), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(o.label) }
     }
     const fn = new Function('agent', 'log', 'phase', 'pipeline', 'args', `return (async () => { ${rbody} })()`)
     let out, error = ''
@@ -1068,7 +1089,7 @@ await block('the scoped round driver', async () => {
   const seatBoxes = Object.keys(D.BOXES).filter((b) => D.BOXES[b].heavy.length + D.BOXES[b].light.length)
   t(`from "intake" gathers once per box, each prompt naming its own box (${seatBoxes.length} boxes)`,
     gathers.length === seatBoxes.length && seatBoxes.every((b) => gathers.filter((c) => c.prompt.includes(`reports-${b}.json`)).length === 1), J(gathers.map((c) => (/reports-(B\d+)\.json/.exec(c.prompt) ?? [])[1])))
-  const rep = (id) => ({ dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [] })
+  const rep = (id) => ({ dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: closed(id, base), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [] })
   const boxIn = (prompt) => (/reports-(B\d+)\.json/.exec(prompt) ?? [])[1]
   const own = (b) => Object.fromEntries([...D.BOXES[b].heavy, ...D.BOXES[b].light].map((id) => [id, rep(id)]))
   const cutBox = bx
@@ -1100,7 +1121,7 @@ await block('the scoped round driver', async () => {
   t(`an unknown box is refused (${noBox})`, !D.BOXES[noBox] && /is not one of/.test((await drive({ ...base, box: noBox })).error), `${noBox} accepted`)
   const both = await drive({ ...base, box: 'B1', from: 'intake' })
   t('box and from "intake" together are refused before Prepare', /exclusive/.test(both.error) && both.labels.length === 0, both.error || J(both.labels))
-  // Round `off` runs neither D5, D6, D11 nor D13 (cadence 2 and 3): a box
+  // Round `off` runs neither D5 nor D6 (cadence 2; D11 and D13 run every round): a box
   // holding both active and inactive seats carries only the active ones, and
   // the placement check is taken over the active seats.
   const mixed = Object.keys(D.BOXES).find((b) => { const ss = [...D.BOXES[b].heavy, ...D.BOXES[b].light].map((s) => D.activeIn(off, s.split('-')[0])); return ss.includes(true) && ss.includes(false) })
@@ -1205,6 +1226,82 @@ await block('the scoped round driver', async () => {
     /handoff\/audit-r9-find-<box>/.test(glp) && !/handoff\/audit-r9-find-<box>/.test(lp), glp.slice(-400))
   t('and the round\'s ledger entry names every active dimension, one step list per seat',
     Object.keys(r9.out?.rotation_round ?? {}).length === L.dims.length && r9.out.rotation_round.D1.seats.length === Object.keys(scopes.D1.seats).length, J(Object.keys(r9.out?.rotation_round ?? {})))
+
+  // The denominator (COMMON.md; tvofi 2026-11-13): a report names what its steps
+  // range over, how much it examined and what it left, and what the round before
+  // left is the first work of this one. Each refusal has its null control here.
+  if (!DENOM) console.log("  skip   the denominator block: the schema's coverage rows require no enumerator at this tree")
+  else await block('the denominator', async () => {
+    const seat = { dim: 'D1', steps: ['M1', 'M2'] }
+    const row = (m, o = {}) => ({ step: `D1.${m}`, enumerator: 'e', universe: 2, examined: 2, not_reached: [], redispatched: [], evidence: 'x', ...o })
+    const ok = { coverage: [row('M1'), row('M2')] }
+    const gaps = (rep, carry = []) => D.denominatorGaps(seat, rep, carry)
+    const refuses = (name, rep, re, carry = []) => { const g = gaps(rep, carry); t(`denominatorGaps refuses ${name}`, g.length > 0 && g.some((x) => re.test(x)), J(g)) }
+    t('denominatorGaps passes a closed report, one row per step (null control)', J(gaps(ok)) === J([]), J(gaps(ok)))
+    refuses('a step with no row', { coverage: [row('M1')] }, /M2/)
+    refuses('two rows for one step', { coverage: [row('M1'), row('M1'), row('M2')] }, /M1/)
+    refuses('an empty enumerator', { coverage: [row('M1', { enumerator: ' ' }), row('M2')] }, /M1/)
+    refuses('examined above universe', { coverage: [row('M1', { examined: 3 }), row('M2')] }, /M1/)
+    refuses('a non-integer universe', { coverage: [row('M1', { universe: 1.5, examined: 1 }), row('M2')] }, /M1/)
+    refuses('examined below universe with nothing listed not reached', { coverage: [row('M1', { examined: 1 }), row('M2')] }, /M1/)
+    refuses('examined equal to universe with a not_reached list', { coverage: [row('M1', { not_reached: ['a'] }), row('M2')] }, /M1/)
+    refuses('an absent coverage', {}, /M1/)
+    const c1 = { id: 'C1', step: 'M1', item: 'x', age: 1, overdue: false }
+    const withAns = (state) => ({ coverage: [row('M1', state ? { universe: 2, examined: state === 'examined' ? 2 : 1, not_reached: state === 'examined' ? [] : ['x'], redispatched: [{ item: 'C1', state }] } : {}), row('M2')] })
+    refuses('a carried item left unanswered', ok, /C1/, [c1])
+    t('...and passes it answered examined, or answered not_reached when not overdue and the counts close (null control)', J(gaps(withAns('examined'), [c1])) === J([]) && J(gaps(withAns('not_reached'), [c1])) === J([]), J([gaps(withAns('examined'), [c1]), gaps(withAns('not_reached'), [c1])]))
+    refuses('an overdue carried item answered not_reached', withAns('not_reached'), /C1/, [{ ...c1, overdue: true }])
+    t('...and passes the same overdue item answered examined (null control)', J(gaps(withAns('examined'), [{ ...c1, overdue: true }])) === J([]), J(gaps(withAns('examined'), [{ ...c1, overdue: true }])))
+
+    const led = { D1: { steps: ['M1', 'M2', 'M3'], rounds: {
+      9: { coverage: { M3: { enumerator: 'e', universe: 3, examined: 1, not_reached: ['a', 'b'] } } },
+      10: { coverage: { M1: 'spot', M2: 'deep', M3: { enumerator: 'e', universe: 3, examined: 2, not_reached: ['a'] } }, unfinished: [{ step: 'D1.M2', what: 'left' }] } } } }
+    const co = D.carryOf(led, 11, 'D1')
+    t('carryOf at round 11 reads round 10: the whole step for M1, "a" aged 2 for M3, the unfinished entry for M2; nothing for deep M2, "b" not carried',
+      co.length === 3 && co.filter((c) => c.step === 'M1').length === 1 && /whole step/.test(co.find((c) => c.step === 'M1')?.item ?? '') && co.find((c) => c.step === 'M3')?.item === 'a' && co.find((c) => c.step === 'M3')?.age === 2
+      && co.filter((c) => c.step === 'M2').length === 1 && co.find((c) => c.step === 'M2')?.item === 'unfinished: left' && !co.some((c) => c.item === 'b'), J(co))
+    const co10 = D.carryOf(led, 10, 'D1')
+    t('...at round 10 it reads round 9 only: a and b, each aged 1', co10.length === 2 && co10.every((c) => c.step === 'M3' && c.age === 1) && J(co10.map((c) => c.item)) === J(['a', 'b']), J(co10))
+    t('...and a dimension with no earlier round carries nothing (null control)', J(D.carryOf(led, 9, 'D1')) === J([]) && J(D.carryOf(led, 11, 'D2')) === J([]), J(D.carryOf(led, 9, 'D1')))
+
+    const sc = D.seatCarry(led, 11, { dim: 'D1', steps: ['M3', 'M2'] })
+    t('seatCarry numbers C1.. in order and keeps only the seat\'s steps', J(sc.map((c) => [c.id, c.step])) === J([['C1', 'M3'], ['C2', 'M2']]) && J(D.seatCarry(led, 11, { dim: 'D1', steps: ['M1'] }).map((c) => c.id)) === J(['C1']), J(sc))
+    const ov = (rotate) => D.seatCarry({ D1: { ...led.D1, ...(rotate ? { rotate } : {}) } }, 11, { dim: 'D1', steps: ['M3'] })[0].overdue
+    t('seatCarry marks the age-2 item overdue at bound 3, not at bound 4, not with no rotate', ov({ M3: { bound: 3 } }) === true && ov({ M3: { bound: 4 } }) === false && ov(undefined) === false, J([ov({ M3: { bound: 3 } }), ov({ M3: { bound: 4 } }), ov(undefined)]))
+
+    // Driven: the real committed scopes and ledger at round 11.
+    const b11 = { ...base, round: 11 }
+    const empty = await drive(b11, { report: (l) => (l === 'D1-s1' ? { coverage: [] } : {}) })
+    t('a seat whose report carries no denominator is dispatched twice, ends missing, and intake does not run',
+      empty.labels.filter((l) => l === 'D1-s1').length === 2 && J(empty.out?.missing) === J(['D1-s1']) && !empty.labels.includes('intake'), J({ n: empty.labels.filter((l) => l === 'D1-s1').length, missing: empty.out?.missing, error: empty.error }))
+    const full11 = await drive(b11)
+    t('...and with the default stub every seat reports and intake runs (null control)', full11.error === '' && J(full11.out?.missing) === J([]) && full11.labels.includes('intake') && full11.labels.filter((l) => l === 'D1-s1').length === 1, J({ error: full11.error, missing: full11.out?.missing }))
+
+    const fp = (l) => full11.calls.find((c) => c.label === l)?.prompt ?? ''
+    t('a seat with carry (D4-s1, whose round-10 M1 was "spot") is told FIRST WORK with its C ids', fp('D4-s1').includes('FIRST WORK') && fp('D4-s1').includes('C1') && !fp('D4-s1').includes('handed your steps nothing not reached'), fp('D4-s1').slice(-400))
+    const none = await drive({ ...b11, rotation: { ...ledger, D4: { ...ledger.D4, rounds: {} } } })
+    const np = (l) => none.calls.find((c) => c.label === l)?.prompt ?? ''
+    const d4 = none.labels.filter((l) => /^D4-s\d+$/.test(l))
+    t('a dimension with no earlier round is told it was handed nothing, and no FIRST WORK (null control)', d4.length > 0 && d4.every((l) => np(l).includes('handed your steps nothing not reached') && !np(l).includes('FIRST WORK')), J(d4))
+
+    // The ledger entry is the sum over the seats that own the step.
+    const owners = (d, m) => D.seatsFromScopes(scopes, d).filter((x) => x.steps.includes(m)).map((x) => x.id)
+    const [sd, sm] = L.dims.filter((d) => scopes[d]).flatMap((d) => scopes[d].steps.map((m) => [d, m])).sort((a, b) => owners(b[0], b[1]).length - owners(a[0], a[1]).length)[0]
+    const led11 = full11.out?.rotation_round?.[sd]?.coverage?.[sm]
+    const k = owners(sd, sm).length
+    t(`the round's ledger coverage is exactly {enumerator, universe, examined, not_reached}, summed over the ${k} seat(s) owning ${sd}.${sm}`,
+      J(Object.keys(led11 ?? {}).sort()) === J(['enumerator', 'examined', 'not_reached', 'universe']) && led11.universe === k && led11.examined === k && J(led11.not_reached) === J([]), J(led11))
+    const s41 = D.seatsFromScopes(scopes, 'D4').find((x) => x.id === 'D4-s1')
+    const carry41 = D.seatCarry(ledger, 11, s41)
+    const m41 = carry41[0]?.step
+    const answered = await drive(b11, { report: (l) => (l !== 'D4-s1' ? {} : { coverage: closed('D4-s1', b11).map((r) => (r.step !== `D4.${m41}` ? r : { ...r, examined: 0, universe: 1, not_reached: ['z'], redispatched: [...r.redispatched.filter((x) => x.item !== 'C1'), { item: 'C1', state: 'not_reached' }] })) }) })
+    const nr = answered.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []
+    t('a carried item answered not_reached stays in the ledger under its original words, beside the seat\'s own not_reached',
+      !!m41 && carry41[0].overdue === false && nr.includes('z') && nr.includes(carry41[0].item), J({ m41, nr, item: carry41[0]?.item, error: answered.error, missing: answered.out?.missing }))
+    t('...and the default run keeps neither (null control)', !(full11.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []).includes('z') && !(full11.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []).includes(carry41[0]?.item), J(full11.out?.rotation_round?.D4?.coverage?.[m41]))
+
+    t('the cadence: D11, D13, D16 and D17 run at round 11, D5 does not', D.activeIn(11, 'D11') && D.activeIn(11, 'D13') && D.activeIn(11, 'D16') && D.activeIn(11, 'D17') && !D.activeIn(11, 'D5'), J(['D11', 'D13', 'D16', 'D17', 'D5'].map((d) => [d, D.activeIn(11, d)])))
+  })
 })
 
 // THE ROUND-9 VERIFY DRIVER, ADMITTED BEFORE IT LANDS -- R1a's route for the

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
