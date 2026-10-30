# Review packet #2975
head: 95342761df4fe8a78dca8da71cd7aaa9b3618ce7
base: 039eee1dc9c210edd31a6e1a806f4ceb9c0d048b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124018057225 neutral
arch-score / arch-score id=124017773988 success
arm id=124017678640 skipped
budget-raise-gate / budget-raise-gate id=124017774083 success
cancel-superseded id=124017640424 success
codeql / Analyze (actions) id=124017774349 success
codeql / Analyze (javascript-typescript) id=124017774216 success
codeql / Analyze (python) id=124017774242 in_progress
governance / delivery-status id=124017773876 success
governance / delivery-status-publish id=124017775696 skipped
governance / env-matrix id=124017773699 in_progress
governance / instrument-self-tests id=124017773900 in_progress
governance / policy-docs id=124017773884 success
governance / record id=124017776223 skipped
governance / wave-script id=124017773899 success
hassfest / hassfest id=124017773834 success
kernel-points id=124017776005 skipped
prelude id=124017640928 in_progress
refresh id=124017640816 success
tests / arch-instrument id=124017963228 success
tests / briefs id=124017774259 success
tests / browser id=124017963463 in_progress
tests / closure-scope id=124017774258 success
tests / closures id=124017963408 in_progress
tests / coverage id=124017963337 in_progress
tests / fast (3.14) id=124017963304 in_progress
tests / mutation id=124017773946 success
tests / mutation-autofix id=124018054416 skipped
tests / mutation-pins id=124018053550 skipped
tests / nightly-ha id=124017965989 skipped
tests / nightly-status id=124017773971 success
tests / replay id=124017965745 skipped
tests / typing id=124017963227 success
validate / validate-hacs id=124017773814 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 02704dfd: R10-COP-GATE
NOTE body item d7c93e69: R10-COP-GATE
NOTE body item 8bab16ec: R10-COP-GATE
NOTE body item 67905fec: R10-COP-GATE
NOTE body item b73ff537: R10-COP-GATE
NOTE body item d35d033b: R10-COP-GATE
NOTE body item 3244f544: R10-COP-GATE
NOTE body item d53c8d8d: R10-COP-GATE
NOTE body item 49ffb9bf: R10-COP-GATE
NOTE body item 44da23b0: R10-COP-GATE
NOTE body item b55dd6f3: R10-COP-GATE
CARRY-AUDIT: 11 finding item(s): 11 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/features.py
             `tests/features.py` is in the tree at this head
  unverified python3
             python3 with no script argument
  ok         python3 tests/closure.py select --diff 66974d47312caa46e9817b9aeae7186e9764e560 --workdir D
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only 66974d47312c...
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified git diff c9bf05dfe 836198dbb --name-only
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 8 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2975.md b/dev/programme/delivery/2975.md
new file mode 100644
index 000000000..d85badf89
--- /dev/null
+++ b/dev/programme/delivery/2975.md
@@ -0,0 +1 @@
+- [#2975](https://github.com/tvofi/heatpump_optimizer/pull/2975) — **open**, R10-COP-GATE r4: both readers of a pending prediction pair nothing outside the window (R10-COP-GATE)
diff --git a/tests/features.py b/tests/features.py
index c86c95e14..720dc1c27 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -67465,6 +67465,33 @@ R.check(
 )
 
 
+# Both readers of a pending prediction -- the accuracy sample and the draw
+# window -- go through pairs_interval, so a prediction older than the window or
+# a re-run inside it pairs neither; one 30 minutes old pairs both (null).
+def _cg_aged(age):
+    coord = _cf_coord()
+    coord._current_state.outdoor_temperature = 8.0
+    coord._current_action = {"power": 1.5, "dhw_power": 0.0}
+    coord._measured_power = 1.5
+    coord._record_accuracy()
+    coord._pending_prediction["when"] -= age
+    coord._record_accuracy()
+    return len(coord._accuracy.samples), len(coord._accuracy.draw.samples)
+
+
+_cg_ages = {
+    "1 min": _cg_aged(timedelta(minutes=1)),
+    "30 min": _cg_aged(timedelta(minutes=30)),
+    "3 h": _cg_aged(timedelta(hours=3)),
+}
+R.check(
+    "a pending prediction a minute or three hours old pairs neither an accuracy "
+    "sample nor a draw reading; one 30 minutes old pairs both (null)",
+    _cg_ages == {"1 min": (0, 0), "30 min": (1, 1), "3 h": (0, 0)},
+    f"{_cg_ages!r}",
+)
+
+
 # R9-UX-6: money and memory -- the receipt, the capacity line, the replay
 # ---------------------------------------------------------------------------
 from harness import FakeEntry as _ux6_Entry, FakeHass as _ux6_Hass  # noqa: E402

