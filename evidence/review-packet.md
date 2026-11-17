# Review packet #3698
head: 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3
base: 38bf516bdd73f926ee9639ffda7b9ca5163fd50e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=133801840567 success
arch-score / arch-score id=133802166411 queued
arm id=133799349411 skipped
budget-raise-gate / budget-raise-gate id=133802166478 queued
cancel-superseded id=133799598361 success
codeql id=133802168609 skipped
codeql / Analyze (actions) id=133801475278 success
codeql / Analyze (javascript-typescript) id=133801475234 success
codeql / Analyze (python) id=133801475472 success
governance id=133802167925 skipped
governance / env-matrix id=133801475141 queued
governance / instrument-self-tests id=133801475154 queued
governance / policy-docs id=133801475051 queued
governance / record id=133801477020 skipped
governance / wave-script id=133801475160 in_progress
hassfest id=133802168657 skipped
hassfest / hassfest id=133801475105 queued
kernel-points id=133802168553 skipped
prelude id=133799598544 success
refresh id=133799598610 success
tests id=133802168752 skipped
tests / briefs id=133801475204 queued
tests / closure-scope id=133801475377 queued
tests / mutation id=133801475193 queued
tests / nightly-status id=133801475196 queued
validate id=133802168766 skipped
validate / validate-hacs id=133801475072 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 133801475154: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows

FIGURES: 0 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3698.md b/dev/programme/delivery/3698.md
new file mode 100644
index 0000000000..3601b47eed
--- /dev/null
+++ b/dev/programme/delivery/3698.md
@@ -0,0 +1 @@
+- [#3698](https://github.com/tvofi/heatpump_optimizer/pull/3698) — **open**, Hotfix: product_reads self-test on the per-state d16 cells (main instrument-self-tests red) (R11-HOTFIX-SELFTEST-SCOPES)
diff --git a/tools/audit/product_reads.py b/tools/audit/product_reads.py
index dbdb489276..a9d73ae8c7 100644
--- a/tools/audit/product_reads.py
+++ b/tools/audit/product_reads.py
@@ -39,6 +39,8 @@ RUN_TIMEOUT_S = 900
 # A cell token -> what it observes, every comparison against the plan's or the test's own values. A token
 # printed by `d16-writes --cells` with no entry here prints `state not recorded` and never counts.
 PLAN_STATES = ("idle", "dhw-only", "both", "partial", "full", "min-cold-tank")
+# The duty mode each `d16-writes --cells` state runs under (enumerate.STATES, one row per state).
+DUTY_OF = dict(census.STATES)
 # Option axes -> the const.py names of the configuration keys that carry the level; profile axes -> the
 # tests/profiles.py function whose `profile` argument carries it; binary CONF_*_ENTITY axes read the key's
 # presence. An axis in none of these prints `no witness` per level (no observable in the stub: language,
@@ -113,16 +115,18 @@ def token_holds(tok, ps, write):
     """True / False against a recorded pass state (and the write, for a write site), or None: not recorded."""
     if ps is None:
         return False
-    if tok.startswith("duty="):
-        return ps["duty"] == tok[5:]
+    # every token is a row of census.STATES: it holds only under the duty mode that row names
+    if tok in DUTY_OF and ps["duty"] != DUTY_OF[tok]:
+        return False
+    first = ps["plan"] and ps["ordinal"] == 0 and not (write or {}).get("unavailable")
     if tok in PLAN_STATES:
-        return ps["plan_state"] == tok
+        return first and ps["plan_state"] == tok
+    if tok in ("observe", "off"):
+        return first
     if tok == "baseline":
         return ps["plan"] and ps["k"] is None
     if tok == "restart":
         return ps["ordinal"] > 0
-    if tok == "running":
-        return ps["plan"] and ps["ordinal"] == 0 and not (write or {}).get("unavailable")
     if tok == "unavailable":
         return None if write is None else bool(write.get("unavailable"))
     return None
@@ -708,7 +712,7 @@ def plant(root):
         (root / d).mkdir(parents=True, exist_ok=True)
     w = lambda p, t: (root / p).write_text(t)
     w(f"{PKG}/__init__.py", "")
-    w(f"{PKG}/const.py", "PUMP_DUTY_MODES = ('off', 'control')\nCONF_PUMP_DUTY_MODE = 'pump_duty_mode'\nDEFAULT_PUMP_DUTY_MODE = 'off'\n"
+    w(f"{PKG}/const.py", "PUMP_DUTY_MODES = ('off', 'observe', 'control')\nCONF_PUMP_DUTY_MODE = 'pump_duty_mode'\nDEFAULT_PUMP_DUTY_MODE = 'off'\n"
       "CONF_A_ENTITY = 'a_entity'\nCONF_B_ENTITY = 'b_entity'\nCONF_C_ENTITY = 'c_entity'\nMODES = ('m1', 'm2')\nGRID = ('g1', 'g2')\n"
       "CONF_GRID = 'grid'\nCONF_MODE = 'mode'\nCONF_MODE2 = 'mode2'\n")
     w(f"{PKG}/config_flow.py", "X = (CONF_A_ENTITY, CONF_B_ENTITY, CONF_C_ENTITY)\n")
@@ -751,27 +755,27 @@ def self_test():
         saved, OPTION_KEYS = OPTION_KEYS, {"mode": ("CONF_MODE", "CONF_MODE2"), "grid": ("CONF_GRID",)}
         try:
             cells = universe(root, "d16-writes", cells=True)
-            W, W2, WD = f"write {A}:8 apply", f"write {A}:10 apply", f"write {A}:14 direct"
+            W, W2, WD = f"write {A}:8 apply domain=climate", f"write {A}:10 apply domain=number", f"write {A}:14 direct domain=light"
             H = next(c.split(" |")[0] for c in cells if c.startswith(f"hold {A}"))
             arm("the fake write sites are the arbiter's three `.services.async_call` lines, not the aliased fourth",
                 sorted({c.split(" |")[0] for c in cells if c.startswith("write ")}), sorted([W, W2, WD]))
             R = next(c.split(" |")[0] for c in cells if c.startswith(f"hold {PKG}/off_restore.py"))
             HC = next(c.split(" |")[0] for c in cells if c.startswith(f"hold {PKG}/coordinator.py"))
             led = root / "op.tsv"
-            ops = [(f"{W} | duty=control | running", "payload"), (f"{W} | duty=control | running", "constant"),
-                   (f"{W} | duty=control | running", "restart-payload"), (f"{W} | duty=control | restart", "payload"),
-                   (f"{W} | duty=control | upgrade", "payload"), (f"{H} | duty=control | running", "held"),
-                   (f"{W} | duty=off | running", "payload"), (f"{W} | duty=control | restart", "restart-payload"),
-                   (f"{W} | duty=control | running", "nosuch"), (f"{W} | duty=control | unavailable", "unavailable-payload"),
-                   (f"{W} | duty=control | running", "unavailable-payload"), (f"{W} | duty=control | running", "counter"),
-                   (f"{R} | duty=control | running", "restored"), (f"{W} | duty=control | running", "other-payload"),
-                   (f"{W2} | duty=control | running", "other-payload"), (f"{H} | duty=off | running", "held"),
-                   (f"{W} | duty=control | running", "differs-payload"), (f"{W} | duty=control | running", "now-none-payload"),
-                   (f"{W} | duty=control | restart", "built-second-payload"), (f"{HC} | duty=control | running", "coordinator-held"),
-                   (f"{WD} | duty=control | running", "direct-hold"), (f"{W} | duty=control | running", "always-fails"),
-                   (f"{W} | duty=control | running", "differs-detail"), (f"{W} | duty=control | running", "steady-detail")]
+            ops = [(f"{W} | idle", "payload"), (f"{W} | idle", "constant"),
+                   (f"{W} | idle", "restart-payload"), (f"{W} | restart", "payload"),
+                   (f"{W} | upgrade", "payload"), (f"{H} | idle", "held"),
+                   (f"{W} | off", "payload"), (f"{W} | restart", "restart-payload"),
+                   (f"{W} | idle", "nosuch"), (f"{W} | unavailable", "unavailable-payload"),
+                   (f"{W} | idle", "unavailable-payload"), (f"{W} | idle", "counter"),
+                   (f"{R} | idle", "restored"), (f"{W} | idle", "other-payload"),
+                   (f"{W2} | idle", "other-payload"), (f"{H} | off", "held"),
+                   (f"{W} | idle", "differs-payload"), (f"{W} | baseline", "now-none-payload"),
+                   (f"{W} | restart", "built-second-payload"), (f"{HC} | idle", "coordinator-held"),
+                   (f"{WD} | idle", "direct-hold"), (f"{W} | idle", "always-fails"),
+                   (f"{W} | idle", "differs-detail"), (f"{W} | idle", "steady-detail")]
             led.write_text("# a comment and a blank line are skipped\n\n" + "".join(f"{c}\t{S}{k}\n" for c, k in ops)
-                           + f"{W} | duty=control | running\ttests/dies.py::x\n")
+                           + f"{W} | idle\ttests/dies.py::x\n")
             out = read_operation(root, led, 4)
             base = run_script(root, "tests/fake_script.py", defaults_of(root))
             full = {tuple(l.split("\t")[:2]): "\t".join(l.split("\t")[2:]) for l in out if "\t" in l and "::" in l}
@@ -799,7 +803,7 @@ def self_test():
                 "moved\ttarget=no plan value")
             arm("planted: a hold whose recorded state differs is not reached", v(15).startswith("not witnessed: state differs (recorded duty=control"), True)
             arm("planted: a set-point the plan does not hold", full[(ops[16][0], S + ops[16][1])], "moved\ttarget=differs plan=21.0 sent=22.0")
-            arm("null: a pass with no `now` reads the clock", v(17), "moved")
+            arm("null: a pass with no `now` reads the clock: past the plan, it is baseline", v(17), "moved")
             arm("null: the real coordinator class built second on one entry and applied first is restart (construction order)", v(18), "moved")
             arm("null: a hold in the coordinator module is reached", v(19), "reached")
             arm("planted: a write outside every pass", v(20), "not witnessed: state differs (recorded outside every pass)")
@@ -809,7 +813,7 @@ def self_test():
             arm("planted: a check that stays ok with a detail the perturbed site does not reach does not move", v(23),
                 "not witnessed: the check does not move")
             arm("planted: a launcher that dies before writing its record",
-                got[(f"{W} | duty=control | running", "tests/dies.py::x")].startswith("not witnessed: unknown check (launcher: "), True)
+                got[(f"{W} | idle", "tests/dies.py::x")].startswith("not witnessed: unknown check (launcher: "), True)
             n_checks = len(base["by_check"])
             arm("per-script, outside-every-pass and unlisted-writer lines", [l for l in out if not l.startswith(("write ", "hold ", "RESULT"))],
                 ["script tests/dies.py\tchecks=0\twrites outside every pass=0\terror=launcher: " + next(
@@ -817,7 +821,7 @@ def self_test():
                  f"script tests/fake_script.py\tchecks={n_checks}\twrites outside every pass=1\terror=RuntimeError: planted",
                  f"outside every pass {R.split(' ')[1]}\t1 (never witnessable: no plan)",
                  f"outside every pass {A}:14\t1 (never witnessable: no plan)", f"unlisted writer {A}:12\t1"])
-            arm("RESULT counts distinct cells", out[-1], f"RESULT read=operation universe={len(cells)} examined=7 moved=8 reached=3")
+            arm("RESULT counts distinct cells", out[-1], f"RESULT read=operation universe={len(cells)} examined=8 moved=8 reached=3")
             arm("planted (ii): a site never reached", _never_reached(root, S), "not witnessed: site never reached before the check")
             arm("null: no site perturbed turns no check but the planted FAIL (the recorders keep each return value and argv)",
                 sorted(k for k, c in base["by_check"].items() if not c["ok"]), ["always-fails"])
@@ -828,7 +832,7 @@ def self_test():
             ps = {"duty": "control", "plan": True, "k": None, "plan_state": None, "ordinal": 0}
             arm("token: baseline is a plan held and no step covering now", (token_holds("baseline", ps, None), token_holds("baseline", {**ps, "k": 0}, None)), (True, False))
             arm("token: an unknown token is not recorded", token_holds("boost-partial", ps, None), None)
-            arm("token: a write outside every pass holds no token", token_holds("duty=control", None, None), False)
+            arm("token: a write outside every pass holds no token", token_holds("idle", None, None), False)
             arm("token: a plan-state token reads the recorded plan state", (token_holds("idle", {**ps, "plan_state": "idle"}, None),
                 token_holds("both", {**ps, "plan_state": "idle"}, None)), (True, False))
             # generality
@@ -894,18 +898,18 @@ def self_test():
                 arm(f"{name}: a ledger row naming no item exits 2, citing its line",
                     _refused(name, root, "# c\nnosuch\tx::y\n" if name == "operation" else "# c\nnosuch\tsimulation\tx::y\n", "x.tsv:2: 'nosuch'"), True)
                 arm(f"{name}: an empty ledger exits 2", _exit(name, root, "# nothing\n")[0], 2)
-            item = f"{W} | duty=control | running"
+            item = f"{W} | idle"
             for name, text in (("operation", f"{item}\tsimulation\t{S}payload\n"), ("operation", f"{item}\t{S}payload\textra\n"),
                                ("operation", f"{item}\ttests/fake_script.py payload\n"), ("generality", f"level mode=m1\t{S}payload\n"),
                                ("generality", f"level mode=m1\tsimulation\ttests/fake_script.py payload\n"),
                                ("generality", f"level mode=m1\tguesswork\t{S}payload\n")):
                 arm(f"{name}: a malformed row exits 2: {text.strip()!r}", _refused(name, root, text, "x.tsv:1: a row is"), True)
-            arm("operation: a read that prints its RESULT exits 0", _exit("operation", root, f"{W} | duty=control | running\t{S}payload\n")[0],
+            arm("operation: a read that prints its RESULT exits 0", _exit("operation", root, f"{W} | idle\t{S}payload\n")[0],
                 "RESULT printed, exit 0")
             (root / PKG / "pump_arbiter.py").write_text("x = 1\n")
             (root / PKG / "log_latch.py").write_text("")
             (root / PKG / "off_restore.py").write_text("")
-            arm("operation: an emptied universe source exits 2", _exit("operation", root, f"{W} | duty=control | running\t{S}payload\n")[0], 2)
+            arm("operation: an emptied universe source exits 2", _exit("operation", root, f"{W} | idle\t{S}payload\n")[0], 2)
             (root / census.OBJECTIVE).unlink()
             arm("generality: an emptied universe source exits 2", _exit("generality", root, f"level mode=m1\tsimulation\t{S}payload\n")[0], 2)
             arm("a read with no --ledger exits 2 before reading", _usage_exit(["operation", "--repo", str(root)]), 2)
@@ -943,7 +947,7 @@ def _never_reached(root, S):
     keep = p.read_text()
     p.write_text(keep + "async def unused(hass):\n    await hass.services.async_call('a', 'b', {})\n")
     try:
-        cell = next(c for c in universe(root, "d16-writes", cells=True) if " unused | duty=control | running" in c)
+        cell = next(c for c in universe(root, "d16-writes", cells=True) if " unused domain=a | idle" in c)
         led = root / "never.tsv"
         led.write_text(f"{cell}\t{S}payload\n")
         return next(l.split("\t")[2] for l in read_operation(root, led, 2) if l.startswith(cell + "\t"))
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 65b012b82a..b6d975309e 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -203,6 +203,7 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/prepare_baseline.sh",
+    "tools/audit/product_reads.py",
     "tools/audit/prose_counts_census.py",
     "tools/audit/repo_root.mjs",
     "tools/audit/repo_root.py",
@@ -321,6 +322,8 @@
     "tools/audit/seat/sweep_template.md",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -2915,6 +2918,7 @@
     "tools/ci/gate.py",
     "tools/ci/ghapi.py",
     "tools/ci/prelude.py",
+    "tools/ci/selftest_scope.py",
     "tools/policy/agreement_py.py",
     "tools/pr/ci_predict.py"
    ],
@@ -3562,6 +3566,9 @@
     "dev/audit/rounds/round10/study-ident",
     "dev/audit/rounds/round10/study-reseed",
     "dev/audit/rounds/round10/user-text",
+    "dev/audit/rounds/round11",
+    "dev/audit/rounds/round11/evaluation",
+    "dev/audit/rounds/round11/product-reads",
     "dev/audit/rounds/round3",
     "dev/audit/rounds/round3/D0",
     "dev/audit/rounds/round3/D0/reports",
@@ -3825,6 +3832,7 @@
     "dev/audit/waves/w5-g5-195-coverage/coverage/logs",
     "dev/audit/yardstick",
     "dev/audit/yardstick/round10",
+    "dev/audit/yardstick/round11",
     "dev/governance",
     "dev/governance/config",
     "dev/governance/decisions",
@@ -3850,6 +3858,7 @@
     "docs/design/2026-09-05-monthly-savings-history",
     "docs/design/2026-09-05-wood-furnace-economics",
     "docs/design/2026-11-10-duty-switch-restart-learning",
+    "docs/design/2026-11-12-honest-starts-and-runs",
     "docs/img",
     "docs/img/brand",
     "docs/img/card",
@@ -3945,6 +3954,7 @@
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
     "tests/mutation_ledger/killed_by/running_signal.py",
+    "tests/mutation_ledger/killed_by/runs.py",
     "tests/mutation_ledger/killed_by/sensor.py",
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
@@ -3991,6 +4001,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
+    "tests/mutation_ledger/survivor_triage/runs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
     "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
@@ -4150,6 +4161,8 @@
     "tests/golden.py",
     "tests/ha_floor.py",
     "tests/harness.py",
+    "tests/hastub/homeassistant/__init__.py",
+    "tests/hastub/homeassistant/util/**",
     "tests/host_probe.py",
     "tests/issue996_count.py",
     "tests/lane_skip.py",
@@ -4177,6 +4190,7 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/prepare_baseline.sh",
+    "tools/audit/product_reads.py",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
     "tools/audit/seat/beat_jobs_selftest.py",
@@ -4272,6 +4286,8 @@
     "tools/audit/seat/sweep_render.py",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -4878,6 +4894,8 @@
     "tools/audit/seat/sweep_template.md",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -4962,9 +4980,11 @@
    "run_sha": "95edb059af375232f0da09f23b7ab1bc4166923800970f72578cf90b3be9173a",
    "files": [
     "dev/audit/config/bugclasses.json",
+    "dev/audit/rca/R10-N-log-flood.md",
     "tests/throwaway_git.py",
     "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/round_metrics.py",
     "tools/audit/seat/scorecard.py"
    ],
    "probes": [
@@ -5305,6 +5325,7 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/prepare_baseline.sh",
+    "tools/audit/product_reads.py",
     "tools/audit/prose_counts_census.py",
     "tools/audit/repo_root.mjs",
     "tools/audit/repo_root.py",
@@ -5418,6 +5439,8 @@
     "tools/audit/seat/sweep_render.py",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -5613,6 +5636,7 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/prepare_baseline.sh",
+    "tools/audit/product_reads.py",
     "tools/audit/prose_counts_census.py",
     "tools/audit/repo_root.mjs",
     "tools/audit/repo_root.py",
@@ -5732,6 +5756,8 @@
     "tools/audit/seat/sweep_template.md",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -5994,6 +6020,7 @@
     "NOTICE",
     "README.md",
     "RELEASE_NOTES.md",
+    "ROADMAP.md",
     "SECURITY.md",
     "VERSION",
     "blueprints/**",
@@ -6303,6 +6330,9 @@
     "dev/audit/rounds/round10/study-ident/.gitattributes",
     "dev/audit/rounds/round10/study-reseed/.gitattributes",
     "dev/audit/rounds/round10/user-text/.gitattributes",
+    "dev/audit/rounds/round11/.gitattributes",
+    "dev/audit/rounds/round11/evaluation/.gitattributes",
+    "dev/audit/rounds/round11/product-reads/.gitattributes",
     "dev/audit/rounds/round3/.gitattributes",
     "dev/audit/rounds/round3/D0/.gitattributes",
     "dev/audit/rounds/round3/D0/reports/.gitattributes",
@@ -6564,6 +6594,7 @@
     "dev/audit/waves/w5-g5-195-coverage/coverage/logs/.gitattributes",
     "dev/audit/yardstick/.gitattributes",
     "dev/audit/yardstick/round10/.gitattributes",
+    "dev/audit/yardstick/round11/.gitattributes",
     "dev/governance/.gitattributes",
     "dev/governance/config/.gitattributes",
     "dev/governance/config/cfr_exclusions.json",
@@ -6592,6 +6623,7 @@
     "docs/design/2026-09-05-monthly-savings-history/.gitattributes",
     "docs/design/2026-09-05-wood-furnace-economics/.gitattributes",
     "docs/design/2026-11-10-duty-switch-restart-learning/.gitattributes",
+    "docs/design/2026-11-12-honest-starts-and-runs/.gitattributes",
     "docs/img/.gitattributes",
     "docs/img/brand/.gitattributes",
     "docs/img/card/.gitattributes",
@@ -6753,6 +6785,7 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/prepare_baseline.sh",
+    "tools/audit/product_reads.py",
     "tools/audit/prose_counts_census.py",
     "tools/audit/repo_root.mjs",
     "tools/audit/repo_root.py",
@@ -6866,6 +6899,8 @@
     "tools/audit/seat/sweep_render.py",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -7319,6 +7354,9 @@
     "dev/audit/rounds/round10/study-ident",
     "dev/audit/rounds/round10/study-reseed",
     "dev/audit/rounds/round10/user-text",
+    "dev/audit/rounds/round11",
+    "dev/audit/rounds/round11/evaluation",
+    "dev/audit/rounds/round11/product-reads",
     "dev/audit/rounds/round3",
     "dev/audit/rounds/round3/D0",
     "dev/audit/rounds/round3/D0/reports",
@@ -7582,6 +7620,7 @@
     "dev/audit/waves/w5-g5-195-coverage/coverage/logs",
     "dev/audit/yardstick",
     "dev/audit/yardstick/round10",
+    "dev/audit/yardstick/round11",
     "dev/governance",
     "dev/governance/config",
     "dev/governance/decisions",
@@ -7607,6 +7646,7 @@
     "docs/design/2026-09-05-monthly-savings-history",
     "docs/design/2026-09-05-wood-furnace-economics",
     "docs/design/2026-11-10-duty-switch-restart-learning",
+    "docs/design/2026-11-12-honest-starts-and-runs",
     "docs/img",
     "docs/img/brand",
     "docs/img/card",
@@ -7702,6 +7742,7 @@
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
     "tests/mutation_ledger/killed_by/running_signal.py",
+    "tests/mutation_ledger/killed_by/runs.py",
     "tests/mutation_ledger/killed_by/sensor.py",
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
@@ -7748,6 +7789,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
+    "tests/mutation_ledger/survivor_triage/runs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
     "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
@@ -8436,12 +8478,15 @@
     "tests/throwaway_git.py",
     "tools/audit/carry_audit.py",
     "tools/audit/seat/closeout.py",
+    "tools/audit/seat/gh_read.py",
+    "tools/audit/seat/gh_read_run.py",
     "tools/audit/seat/prune_refs.py",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/roster_edit.py",
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_sync.py",
     "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/toolchain.py",
     "tools/audit/seat/topic_grammar.py"
    ],
    "probes": [
@@ -8468,6 +8513,8 @@
    "files": [
     "tests/throwaway_git.py",
     "tools/audit/machinery_ratchet.py",
+    "tools/audit/seat/review_strength.py",
+    "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/round_metrics.py",
     "tools/audit/seat/round_metrics_selftest.py"
    ],
@@ -8475,12 +8522,14 @@
     ".",
     "tests",
     "tools",
-    "tools/audit"
+    "tools/audit",
+    "tools/ci"
    ],
    "dirs": [
     "tests",
     "tools/audit",
-    "tools/audit/seat"
+    "tools/audit/seat",
+    "tools/ci"
    ],
    "index": false,
    "objects": false,
@@ -8788,6 +8837,7 @@
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
     "tests/mutation_ledger/killed_by/running_signal.py",
+    "tests/mutation_ledger/killed_by/runs.py",
     "tests/mutation_ledger/killed_by/sensor.py",
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
@@ -8833,6 +8883,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
+    "tests/mutation_ledger/survivor_triage/runs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
     "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
@@ -8946,6 +8997,7 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/prepare_baseline.sh",
+    "tools/audit/product_reads.py",
     "tools/audit/prose_counts_census.py",
     "tools/audit/repo_root.mjs",
     "tools/audit/repo_root.py",
@@ -9064,6 +9116,8 @@
     "tools/audit/seat/sweep_render.py",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -9473,6 +9527,7 @@
     "tests/mutation_ledger/killed_by/repairs.py/.gitattributes",
     "tests/mutation_ledger/killed_by/replay_doc.py/.gitattributes",
     "tests/mutation_ledger/killed_by/running_signal.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/runs.py/.gitattributes",
     "tests/mutation_ledger/killed_by/sensor.py/.gitattributes",
     "tests/mutation_ledger/killed_by/services.py/.gitattributes",
     "tests/mutation_ledger/killed_by/setpoint_check.py/.gitattributes",
@@ -9519,6 +9574,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/repairs.py/.gitattributes",
+    "tests/mutation_ledger/survivor_triage/runs.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/sensor.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/slab_seed.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py/.gitattributes",
@@ -9744,6 +9800,7 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/prepare_baseline.sh",
+    "tools/audit/product_reads.py",
     "tools/audit/prose_counts_census.py",
     "tools/audit/repo_root.mjs",
     "tools/audit/repo_root.py",
@@ -9857,6 +9914,8 @@
     "tools/audit/seat/sweep_render.py",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
