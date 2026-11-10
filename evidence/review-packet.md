# Review packet #3406
head: 18b19b658171d7918b373b789077f470b113957a
base: 5ab6030d70680830817791707e7c7be1a7b09e11

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=129632496081 success
arch-score / arch-score id=129664801190 success
arm id=129632212687 skipped
budget-raise-gate / budget-raise-gate id=129664801246 success
cancel-superseded id=129664836973 success
codeql id=129664832131 skipped
codeql / Analyze (actions) id=129643944704 success
codeql / Analyze (javascript-typescript) id=129643944752 success
codeql / Analyze (python) id=129643944736 success
gate id=129664800452 success
governance id=129664801070 skipped
governance / delivery-status id=129643946015 skipped
governance / delivery-status-publish id=129643946654 skipped
governance / env-matrix id=129643944825 success
governance / instrument-self-tests id=129643944883 success
governance / policy-docs id=129643944735 success
governance / record id=129643945869 skipped
governance / wave-script id=129643944816 success
hassfest id=129664801405 skipped
hassfest / hassfest id=129643944722 success
kernel-points id=129664852652 skipped
pr-contract id=129664802713 skipped
pr-contract / pr-contract id=129661416480 success
prelude id=129664800844 success
refresh id=129664800231 success
tests id=129664801085 skipped
tests / arch-instrument id=129644638524 success
tests / briefs id=129643944820 success
tests / browser id=129644638674 success
tests / ci-ratchet id=129659794376 skipped
tests / claims-autofix id=129656174704 skipped
tests / closure-scope id=129643944777 success
tests / closures id=129644638605 success
tests / closures-autofix id=129659794941 skipped
tests / coverage id=129644638502 success
tests / coverage-ratchet id=129649365855 success
tests / fast (3.14) id=129644638529 success
tests / graders-head-copy id=129649368080 skipped
tests / lane-proofs id=129656175067 skipped
tests / mutation id=129643944913 success
tests / mutation-autofix id=129644792083 skipped
tests / mutation-pins id=129644790707 skipped
tests / nightly-ha id=129644640432 skipped
tests / nightly-status id=129643946249 skipped
tests / replay id=129644640820 skipped
tests / typing id=129644638520 success
validate id=129664855787 skipped
validate / validate-hacs id=129643944830 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_stress_intern_fill.py edge <tree> typical_slab/shoulder <short>
             `dev/audit/harnesses/r10_stress_intern_fill.py` is in the tree at this head
  ok         python3 tests/stress.py --memory-probe '{"season": "winter", "building": "typical_slab", "dhw": true}' --intern-count
             `tests/stress.py` is in the tree at this head
  ok         GATE_SCOPE=auto PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D9/h7_memory_gate.py
             `dev/audit/rounds/round4/D9/h7_memory_gate.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 9b1bb58db7
             `tools/audit/archscore/score.py` is in the tree at this head
  unverified git grep -n "tracemalloc.start" -- tests dev/audit
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/replay.py
             `tests/replay.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D9/d9_own_d9_06.py
             `dev/audit/rounds/round4/D9/d9_own_d9_06.py` is in the tree at this head
  ok         dev/audit/rounds/round3/D9/h3_memory.py
             `dev/audit/rounds/round3/D9/h3_memory.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D9/h4_retained.py
             `dev/audit/rounds/round4/D9/h4_retained.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D9/h8_leak_attrib.py
             `dev/audit/rounds/round4/D9/h8_leak_attrib.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D9/verify3_h7_mmap.py
             `dev/audit/rounds/round4/D9/verify3_h7_mmap.py` is in the tree at this head
  ok         dev/audit/rounds/round8/evidence/D9/s2_cycle.py
             `dev/audit/rounds/round8/evidence/D9/s2_cycle.py` is in the tree at this head
  ok         dev/audit/rounds/round10/D9/s2/retained.py
             `dev/audit/rounds/round10/D9/s2/retained.py` is in the tree at this head

FIGURES: 16 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_stress_intern_fill.py b/dev/audit/harnesses/r10_stress_intern_fill.py
new file mode 100644
index 000000000..a4483c679
--- /dev/null
+++ b/dev/audit/harnesses/r10_stress_intern_fill.py
@@ -0,0 +1,199 @@
+#!/usr/bin/env python3
+"""R10-HOTFIX-STRESS-MEM-PEAK-2: a traced peak charged the interned-string table.
+
+A solve interns a few fresh strings. When the interpreter's interned-string
+table has fewer free slots than that, the solve rebuilds it inside the traced
+window and the whole new table is billed to the scenario (1.83 MiB on CI,
+3.67 MiB on the cloud seat's image). Where the import fill leaves the table
+moves a few slots from process to process, so one tree read typical_slab/
+shoulder at 2.1 MiB in one run and 3.9 MiB in the next.
+
+Every mode takes TREE, a checkout (the merge base or the head), and drives
+that tree's own tests/stress.py; nothing is re-implemented but the fill.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_stress_intern_fill.py MODE TREE ...
+
+  probes TREE REPS LABEL...   the tree's own --memory-probe, REPS times each:
+      RESULT probes label=<l> traced_mib=<a,b,...>
+  edge TREE LABEL SHORT       stress imported, the table filled SHORT slots
+      short of its rebuild (counted in a forked child sharing the table),
+      then the tree's own _memory_probe_main -- so the fill lands before
+      whatever the tree does before its traced window:
+      RESULT edge label=<l> short=<k> interns_to_rebuild=<n> traced_mib=<x>
+  count TREE LABEL            slots one untraced solve consumes (forked
+      counts before and after build_case):
+      RESULT count label=<l> slots=<n>
+  rss TREE LABEL...           the tree's empty probe and probes:
+      RESULT rss label=<l> baseline_mib=<b> probe_mib=<p> attrib_mib=<a>
+  replay TREE FIXTURE         slots each traced (memory) cycle of
+      tests/replay.py --one FIXTURE consumes, forked counts around it:
+      RESULT replay fixture=<f> memory_cycles=<n> slots=<sorted set> total=<t>
+
+EXPECTED RESULT (cloud seat, merge base 9b1bb58db7 vs this head):
+  edge typical_slab/shoulder 1: base traced_mib ~5.7, head ~2.06 (null
+      control: SHORT 50 reads ~2.06 at both ends)
+  probes: the same readings at both ends, 2.05-2.07 typical_slab/shoulder
+  replay synthetic-dhw-only.json: slots={0} at both ends
+Null control: edge with a large SHORT; the bare probe of `probes`.
+Perturbation: SHORT 1, which a solve that interns at all crosses.
+"""
+from __future__ import annotations
+
+import importlib.util
+import json
+import os
+import runpy
+import tempfile
+import sys
+import tracemalloc
+import warnings
+
+STEP = 512 * 1024  # a table rebuild; one string is under 1 KiB
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+def until_rebuild(tag, limit=2_000_000):
+    tracemalloc.start()
+    try:
+        prev = tracemalloc.get_traced_memory()[0]
+        for n in range(1, limit + 1):
+            sys.intern(f"__r10_fill_{tag}_{n}")
+            cur = tracemalloc.get_traced_memory()[0]
+            if cur - prev > STEP:
+                return n, True
+            prev = cur
+        return limit, False
+    finally:
+        tracemalloc.stop()
+
+
+def forked_count():
+    r, w = os.pipe()
+    with warnings.catch_warnings():
+        warnings.simplefilter("ignore", DeprecationWarning)
+        pid = os.fork()
+    if pid == 0:
+        n, ok = until_rebuild("count")
+        os.write(w, str(n if ok else -1).encode())
+        os._exit(0)
+    os.close(w)
+    n = int(os.read(r, 32))
+    os.waitpid(pid, 0)
+    if n < 0:
+        raise SystemExit("no interned-table rebuild seen")
+    return n
+
+
+def load_stress(tree):
+    os.chdir(tree)
+    sys.path[:0] = [os.path.join(tree, p)
+                    for p in ("tests/hastub", "custom_components", "tests")]
+    sys.argv = ["stress.py"]
+    spec = importlib.util.spec_from_file_location("stress", "tests/stress.py")
+    mod = importlib.util.module_from_spec(spec)
+    sys.modules["stress"] = mod
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def specs(stress):
+    return {c["label"]: {k: v for k, v in c.items() if k != "label"}
+            for c in stress.sweep_combinations()}
+
+
+def main(argv):
+    mode, tree = argv[0], os.path.abspath(argv[1])
+    repo_root(tree)  # refuses a path that is not a checkout
+    if mode == "probes":
+        stress = load_stress(tree)
+        combos, env = specs(stress), stress._memory_probe_env()
+        for label in argv[3:]:
+            reads = [stress._run_memory_probe(
+                ["--memory-probe", json.dumps(combos[label])], env)["traced_mb"]
+                for _ in range(int(argv[2]))]
+            print(f"RESULT probes label={label} traced_mib="
+                  + ",".join(f"{r:.2f}" for r in reads), flush=True)
+    elif mode == "edge":
+        label, short = argv[2], int(argv[3])
+        stress = load_stress(tree)
+        spec = json.dumps(specs(stress)[label])
+        n = forked_count()
+        until_rebuild("edge", limit=n - short)
+        sys.stdout.flush()
+        saved = os.dup(1)
+        with tempfile.TemporaryFile() as captured:
+            os.dup2(captured.fileno(), 1)
+            try:
+                stress._memory_probe_main(["stress.py", "--memory-probe", spec])
+                sys.stdout.flush()
+            finally:
+                os.dup2(saved, 1)
+            captured.seek(0)
+            line = captured.read().decode().strip().splitlines()[-1]
+        print(f"RESULT edge label={label} short={short} interns_to_rebuild={n} "
+              f"traced_mib={json.loads(line)['traced_mb']:.2f}")
+    elif mode == "count":
+        stress = load_stress(tree)
+        spec = specs(stress)[argv[2]]
+        before = forked_count()
+        stress.build_case(**spec)
+        print(f"RESULT count label={argv[2]} slots={before - forked_count()}")
+    elif mode == "rss":
+        stress = load_stress(tree)
+        combos, env = specs(stress), stress._memory_probe_env()
+        base = float(stress._run_memory_probe(["--memory-baseline"], env)["rss_mb"])
+        for label in argv[2:]:
+            probe = float(stress._run_memory_probe(
+                ["--memory-probe", json.dumps(combos[label])], env)["rss_mb"])
+            print(f"RESULT rss label={label} baseline_mib={base:.1f} "
+                  f"probe_mib={probe:.1f} attrib_mib={max(0.0, probe - base):.1f}",
+                  flush=True)
+    elif mode == "replay":
+        fixture = argv[2]
+        os.chdir(tree)
+        sys.path[:0] = [os.path.join(tree, "tests/hastub")]
+        real_start, real_get = tracemalloc.start, tracemalloc.get_traced_memory
+        before, used = [], []
+
+        def from_replay():
+            return sys._getframe(2).f_code.co_filename.endswith("replay.py")
+
+        def start(*a):
+            if from_replay():
+                before.append(forked_count())
+            return real_start(*a)
+
+        def get():
+            cur, peak = real_get()
+            if from_replay() and len(used) < len(before):
+                used.append(before[-1] - forked_count())
+            return cur, peak
+
+        tracemalloc.start, tracemalloc.get_traced_memory = start, get
+        sys.argv = ["tests/replay.py", "--one", fixture]
+        try:
+            runpy.run_path("tests/replay.py", run_name="__main__")
+        except SystemExit:
+            pass
+        sys.stdout.flush()
+        print(f"RESULT replay fixture={os.path.basename(fixture)} "
+              f"memory_cycles={len(used)} slots={sorted(set(used))} "
+              f"total={sum(used)}", file=sys.stderr)
+    else:
+        raise SystemExit(f"unknown mode {mode}")
+
+
+if __name__ == "__main__":
+    main(sys.argv[1:])
diff --git a/dev/programme/delivery/3406.md b/dev/programme/delivery/3406.md
new file mode 100644
index 000000000..c55a56e44
--- /dev/null
+++ b/dev/programme/delivery/3406.md
@@ -0,0 +1 @@
+- [#3406](https://github.com/tvofi/heatpump_optimizer/pull/3406) — **open**, tests/stress.py memory pass: intern-table rebuild charged to the traced window (R10-HOTFIX-STRESS-MEM-PEAK-2)
diff --git a/tests/closures.json b/tests/closures.json
index 726cea124..1c1f4a782 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4233,6 +4233,7 @@
    "dev/audit/harnesses/r10_stats_window.mjs",
    "dev/audit/harnesses/r10_store_load_leads.py",
    "dev/audit/harnesses/r10_store_races_census.py",
+   "dev/audit/harnesses/r10_stress_intern_fill.py",
    "dev/audit/harnesses/r10_structure_alias.py",
    "dev/audit/harnesses/r10_structure_blind.py",
    "dev/audit/harnesses/r10_sweep_driver_arm.py",
diff --git a/tests/stress.py b/tests/stress.py
index bbcf9adae..d7841ed32 100644
--- a/tests/stress.py
+++ b/tests/stress.py
@@ -44,6 +44,7 @@ import tempfile
 import textwrap
 import time
 import tracemalloc
+import warnings
 from datetime import datetime, timedelta
 
 from harness import Results
@@ -2196,6 +2197,46 @@ def rss_attrib_fail_threshold(recorded_attrib: float) -> float:
     return recorded_attrib * MEMORY_BUDGET_FACTOR
 
 
+#: How many slots short of its rebuild `intern_fill_readings` leaves the
+#: interned-string table before a probe's traced window. Each of the seven
+#: probed solves consumes three slots on the cloud seat's image (forked counts
+#: around build_case; filled 1-3 short a traced solve crossed in 9 of 9 runs,
+#: 4 or 6 short in none of 4), so one is the edge any solve that interns at
+#: all crosses.
+INTERN_FILL_SHORT = 1
+#: How far a fill-perturbed probe may read from the clean probe of the same
+#: scenario, in MiB: under a third of the smallest table step measured (1.83
+#: MiB, CI) and over ten times the same-box spread (2.05-2.07, five probes).
+INTERN_FILL_TOLERANCE_MIB = 0.5
+
+
+def intern_fill_readings(spec: dict, env: dict) -> dict:
+    """One scenario's traced peak with the interned table left nearly full.
+
+    The traced arm's second precondition: the reading belongs to the tree,
+    not to where the probe process's import fill left the interpreter's
+    interned-string table. A solve interns a handful of fresh strings; a
+    probe whose fill sits that close to the table's rebuild is charged the
+    whole new table (1.83 MiB on CI), and the fill moves a few slots from
+    one process to the next, so one tree read 2.1 MiB in one run and 3.9 in
+    the next (R10-HOTFIX-STRESS-MEM-PEAK-2). This puts the probe on that
+    edge: INTERN_FILL_SHORT slots short of the rebuild, counted in the
+    probe's own forked child. ``bare`` is the same fill with the probe's
+    headroom step skipped -- the null control that shows the fill lands.
+    """
+    args = [
+        "--memory-probe", json.dumps(spec),
+        "--intern-fill-short", str(INTERN_FILL_SHORT),
+    ]
+    filled = _run_memory_probe(args, env)
+    bare = _run_memory_probe(args + ["--no-intern-headroom"], env)
+    return {
+        "interns_to_rebuild": int(filled["interns_to_rebuild"]),
+        "filled_mb": float(filled["traced_mb"]),
+        "bare_mb": float(bare["traced_mb"]),
+    }
+
+
 def traced_fail_threshold(recorded_traced: float) -> float:
     """The traced peak (MiB) a probe may reach before the check fails.
 
@@ -3161,6 +3202,13 @@ def _memory_probe_main(argv: list[str]) -> int:
     the watermark it rides on.
     """
     spec = json.loads(argv[argv.index("--memory-probe") + 1])
+    interns_to_rebuild = None
+    if "--intern-fill-short" in argv:
+        short = int(argv[argv.index("--intern-fill-short") + 1])
+        interns_to_rebuild = _count_interns_to_rebuild()
+        _intern_until_rebuild("fill", limit=interns_to_rebuild - short)
+    if "--no-intern-headroom" not in argv:
+        give_interned_table_headroom()
     modules_before = set(sys.modules)
     tracemalloc.start()
     build_case(**spec)
@@ -3172,12 +3220,107 @@ def _memory_probe_main(argv: list[str]) -> int:
                 "rss_mb": round(rss_mb(), 1),
                 "traced_mb": round(traced_peak / (1024.0 * 1024.0), 2),
                 "imported": solve_window_imports(modules_before, sys.modules),
+                "interns_to_rebuild": interns_to_rebuild,
             }
         )
     )
     return 0
 
 
+#: The smallest one-step growth of the traced current that reads as the
+#: interned-string table being rebuilt, in bytes. The table is the
+#: interpreter's largest dict: 1.83 MiB on the CI runner, 3.67 MiB on the
+#: cloud seat's image; one fresh interned string costs well under 1 KiB.
+INTERN_REBUILD_STEP_BYTES = 512 * 1024
+#: Fresh interns after which a search for the rebuild gives up: an order of
+#: magnitude past the ~44,000 the cloud seat's image needs from its import fill.
+INTERN_REBUILD_SEARCH_LIMIT = 2_000_000
+
+
+def _intern_until_rebuild(tag: str, limit: int | None = None) -> tuple[int, bool]:
+    """Intern fresh strings, one at a time, until the interned table rebuilds.
+
+    Returns how many were interned and whether the rebuild was seen. Each
+    string is dropped as soon as it is interned: the table deletes a mortal
+    interned string's key on its free and leaves a dummy, so the slot stays
+    spent while the memory is reused for the next string. Keeping them
+    instead held ~11 MiB of strings and trace records under the probe's RSS
+    watermark, which hid every solve's growth below it (attributable
+    8.6-8.9 -> 0.7-0.9 MiB on three probed scenarios). ``limit`` stops
+    short of the search bound: ``--intern-fill-short`` leaves the table that
+    many slots short of its rebuild. Seen under tracemalloc, the one
+    instrument that sees the table's allocation.
+    """
+    bound = INTERN_REBUILD_SEARCH_LIMIT if limit is None else limit
+    tracemalloc.start()
+    try:
+        prev = tracemalloc.get_traced_memory()[0]
+        for count in range(1, bound + 1):
+            sys.intern(f"__stress_intern_{tag}_{count}")
+            cur = tracemalloc.get_traced_memory()[0]
+            if cur - prev > INTERN_REBUILD_STEP_BYTES:
+                return count, True
+            prev = cur
+        return bound, False
+    finally:
+        tracemalloc.stop()
+
+
+def _count_interns_to_rebuild() -> int:
+    """How many fresh interns this process's table takes to its rebuild.
+
+    Counted in a forked child, which shares this process's exact table and
+    leaves it untouched: a second process lands its own import fill a few
+    slots either side (43669-43674 over ten processes of one tree, the
+    hash seed fixed or not), more than a solve consumes, so a count taken
+    there cannot place this one's fill.
+    """
+    if not hasattr(os, "fork"):
+        raise RuntimeError("--intern-fill-short needs os.fork")
+    read_fd, write_fd = os.pipe()
+    with warnings.catch_warnings():
+        # 3.12+ warns on forking a process with threads (BLAS pools here);
+        # the child only interns strings and leaves through os._exit.
+        warnings.simplefilter("ignore", DeprecationWarning)
+        pid = os.fork()
+    if pid == 0:
+        os.close(read_fd)
+        count, rebuilt = _intern_until_rebuild("fill")
+        os.write(write_fd, str(count if rebuilt else -1).encode())
+        os._exit(0)
+    os.close(write_fd)
+    with os.fdopen(read_fd) as reader:
+        count = int(reader.read() or "-1")
+    os.waitpid(pid, 0)
+    if count < 0:
+        raise RuntimeError("the forked count never saw the table rebuild")
+    return count
+
+
+def give_interned_table_headroom() -> int:
+    """Rebuild the interned-string table now, before a probe's traced window.
+
+    The table is interpreter-global and is rebuilt in one step when its free
+    slots run out; a solve interns a handful of fresh strings (three slots,
+    traced, on the cloud seat's image), so whichever traced window crosses
+    the rebuild is charged the whole new table. Where the import-time fill
+    leaves the table moves a few slots from one process to the next, so
+    one tree read 2.1 MiB in one run and 3.9 in the next
+    (R10-HOTFIX-STRESS-MEM-PEAK-2). Interning fresh strings until the
+    rebuild is seen leaves the table freshly rebuilt, and the slots it then
+    has free -- tens of thousands -- are headroom no probed solve comes
+    near. Returns the interns it took; refuses a search that never saw the
+    rebuild.
+    """
+    count, rebuilt = _intern_until_rebuild("room")
+    if not rebuilt:
+        raise RuntimeError(
+            f"no interned-table rebuild in {count} fresh interns: the "
+            f"probe's traced window is not insulated from the runner's fill"
+        )
+    return count
+
+
 def solve_window_imports(before: set, after) -> list[str]:
     """The modules a probe's traced window imported, sorted: owed empty.
 
@@ -3220,6 +3363,9 @@ def _memory_baseline_main(argv: list[str]) -> int:
     the case DETECTION_TARGET is sized for.
     """
     del argv  # the flag alone selects this mode
+    # The probe's headroom step, paid here too, so the table it grows is
+    # in both watermarks and cancels out of the attributable difference.
+    give_interned_table_headroom()
     print(json.dumps({"rss_mb": round(rss_mb(), 1)}))
     return 0
 
@@ -5208,6 +5354,7 @@ if __name__ == "__main__":
     mem_over: list[str] = []
     mem_stale: list[str] = []
     mem_imported: list[str] = []
+    traced_by_label: dict[str, float] = {}
     mem_unrecorded: list[str] = []
     # Readings the attributable stale arm declines because the difference
     # is the platform's import floor rather than the scenario
@@ -5244,6 +5391,7 @@ if __name__ == "__main__":
             continue
         rss_peak = float(probe["rss_mb"])
         traced_peak = float(probe["traced_mb"])
+        traced_by_label[label] = traced_peak
         if probe.get("imported"):
             mem_imported.append(f"{label}: {', '.join(probe['imported'])}")
         rss_attrib = max(0.0, rss_peak - baseline_rss)
@@ -5325,6 +5473,38 @@ if __name__ == "__main__":
         "; ".join(mem_imported)
         + " -- see solve_window_imports: build it at import time",
     )
+    if not record_mode and traced_by_label:
+        # The cheapest probed scenario by recorded work ratio carries the
+        # fill check: three extra probe processes, in every gate pass.
+        fill_label = min(
+            traced_by_label,
+            key=lambda lb: float(budget_table[lb].get("ratio", 0.0)),
+        )
+        fill = intern_fill_readings(combos_by_label[fill_label], probe_env)
+        clean_traced = traced_by_label[fill_label]
+        print(
+            f"  interned-table fill ({fill_label}): "
+            f"{fill['interns_to_rebuild']} interns to the rebuild; filled to "
+            f"{INTERN_FILL_SHORT} short: traced {fill['filled_mb']:.2f} MiB, "
+            f"{fill['bare_mb']:.2f} without the probe's headroom step, "
+            f"{clean_traced:.2f} clean"
+        )
+        R.check(
+            "the interned-table fill perturbation lands: without the probe's "
+            "headroom step a nearly-full table charges the solve its rebuild",
+            fill["bare_mb"] - clean_traced
+            > INTERN_REBUILD_STEP_BYTES / (1024.0 * 1024.0),
+            f"{fill_label}: bare {fill['bare_mb']:.2f} MiB vs clean "
+            f"{clean_traced:.2f} MiB -- the fill check below is vacuous",
+        )
+        R.check(
+            "a probe's traced peak does not depend on where the runner's "
+            "import fill left the interned-string table",
+            abs(fill["filled_mb"] - clean_traced) <= INTERN_FILL_TOLERANCE_MIB,
+            f"{fill_label}: filled {fill['filled_mb']:.2f} MiB vs clean "
+            f"{clean_traced:.2f} MiB (tolerance {INTERN_FILL_TOLERANCE_MIB} "
+            f"MiB) -- see intern_fill_readings",
+        )
     rss_growth_mb = rss_mb() - rss_before_mb
     print(
         f"  parent RSS watermark growth over the memory pass: "

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
