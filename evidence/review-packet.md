# Review packet #2964
head: 67be951d3980dcfa9a2c5ce8b099f9239f3db904
base: e5ddba1fad5e6eccfeceaeaaa249bc459963405b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123726596224 neutral
arch-score / arch-score id=123726258796 success
arm id=123726057226 skipped
budget-raise-gate / budget-raise-gate id=123726258866 success
cancel-superseded id=123726060596 success
codeql / Analyze (actions) id=123726258458 success
codeql / Analyze (javascript-typescript) id=123726258723 success
codeql / Analyze (python) id=123726258537 in_progress
governance / delivery-status id=123726258935 success
governance / delivery-status-publish id=123726261078 skipped
governance / env-matrix id=123726259047 in_progress
governance / instrument-self-tests id=123726258875 in_progress
governance / policy-docs id=123726259185 success
governance / record id=123726260749 skipped
governance / wave-script id=123726258916 success
hassfest / hassfest id=123726258893 success
kernel-points id=123726259966 skipped
prelude id=123726060658 success
refresh id=123726060097 success
tests / arch-instrument id=123726500892 success
tests / briefs id=123726258712 success
tests / browser id=123726501399 in_progress
tests / closure-scope id=123726258599 success
tests / closures id=123726501129 in_progress
tests / coverage id=123726500944 in_progress
tests / fast (3.14) id=123726500891 in_progress
tests / mutation id=123726258720 success
tests / mutation-autofix id=123726627386 skipped
tests / mutation-pins id=123726627588 skipped
tests / nightly-ha (2025.2.0) id=123726501217 in_progress
tests / nightly-ha (stable) id=123726501072 in_progress
tests / nightly-status id=123726258955 failure
tests / replay id=123726504095 skipped
tests / typing id=123726500893 in_progress
validate / validate-hacs id=123726258504 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 71dbd532: R10-NIGHTLY-HB-RESPAWN
NOTE body item 61287b2f: dismissed:seat environment cost, not a policy defect
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         dev/audit/harnesses/r10_fly_nightly_hb.py
             `dev/audit/harnesses/r10_fly_nightly_hb.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <head worktree> --mode side --runs 30 --out <dir> --image <stable+threadpoolctl>
             `dev/audit/harnesses/r10_fly_nightly_hb.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <merge-base worktree> --mode probe --runs 40 --out <dir> --image <stable+threadpoolctl>
             `dev/audit/harnesses/r10_fly_nightly_hb.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <head worktree> --mode N1 --runs 2 --out <dir> --image <stable+threadpoolctl>
             `dev/audit/harnesses/r10_fly_nightly_hb.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 486e65cbd9c8451c01624f13b773feb6d722ad9b --workdir <dir>
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         tests/debug_collect.py
             `tests/debug_collect.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D7/sysid_estimator_frontier.py costs at most 50% of its CPU bound [cpu=245.9s against 240s]
             `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 12 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_fly_nightly_hb.py b/dev/audit/harnesses/r10_fly_nightly_hb.py
new file mode 100644
index 000000000..2fa6017f8
--- /dev/null
+++ b/dev/audit/harnesses/r10_fly_nightly_hb.py
@@ -0,0 +1,211 @@
+"""R10-FLY-NIGHTLY-HB: the heartbeat container run N times, with the sampler probed.
+
+The measurement behind the heartbeat sampler change, as a script over the tree's
+own ``nightly_ha._stage(two_zone_dhw=True)`` and ``docker_command(...,
+["--heartbeat-only"], ("SYS_PTRACE",))``. Every mode edits only the staged copy.
+
+``--mode probe`` (a tree whose sampler is py-spy, the base): the staged py-spy
+is wrapped. A call still running after 4.5 s is a hang; the wrapper then records
+py-spy's own state (/proc stat: R or S, utime, stime), runs CPython's
+``_remote_debugging`` unwinder against the same process twice, and a blocking
+(ptrace-stopping) py-spy with a 20 s cut. Every first call is followed, while
+the spin is still held, by one unwinder sample.
+
+``--mode side`` (a tree whose sampler is the unwinder, the fix): every sample
+also starts the staged py-spy beside it with a 4.5 s cut, so a run on a process
+py-spy cannot read is identified, with the control's verdict on that process.
+
+``--mode N1|N2|N3`` (a fix tree): null controls. N1 the spin stalls nothing,
+N2 the watcher never dumps, N3 the sampler reads a pid that does not exist;
+each must fail hb:positive_control. N4 (the mutation proof) deletes the fix's
+own predicate, so the sampler is py-spy wherever it is staged.
+
+``--inproc real|hung`` runs the tree's own ``_async_hb_control`` in this
+interpreter instead, no Docker, with a py-spy staged where the lane looks: the
+real one, or ``hung``, one that never returns -- the failure the nightly
+measured, whose spin is held to the sample's full timeout (gap about
+HB_DUMP_S + the timeout). A base tree is handed that py-spy; a fix tree finds
+it only where the interpreter has no unwinder, or under N4. Run it under a
+3.14 interpreter to drive the unwinder; ``--mode plain`` edits nothing. It
+needs only the CPython the tree runs on, so it measures the sampler, never real
+Home Assistant.
+
+Needs Docker, the image pulled, py-spy 0.4.2 on PATH, and an image layer holding
+the ``threadpoolctl`` wheel (see r10_nightly_pyspy_retry.py).
+
+    python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <worktree> \\
+        --mode side --runs 200 --out <dir> --image <image+threadpoolctl>
+
+Prints one line per run, then ``SUMMARY mode=<m> runs=<n> ok=<k> fail=<f>
+spy_hung=<h>`` (h: runs where a py-spy call ran past 4.5 s). Evidence of every
+failed or py-spy-hung run is kept under ``--out``.
+"""
+
+from __future__ import annotations
+
+import argparse
+import importlib.util
+import json
+import shutil
+import subprocess
+import sys
+from pathlib import Path
+
+PROBE = """import time, _remote_debugging as rd
+t = time.monotonic()
+try:
+    st = rd.RemoteUnwinder(1, all_threads=True).get_stack_trace()
+    print(f"stdlib ok {time.monotonic() - t:.3f}s threads={len(st)} names={'_hb_spin' in repr(st)}")
+except Exception as e:
+    print(f"stdlib err {time.monotonic() - t:.3f}s {type(e).__name__}: {e}")
+"""
+WRAP = r"""#!/bin/sh
+c=/tmp/hpo-spy-calls; echo >> "$c"; k=$(wc -l < "$c" | tr -d ' ')
+d=$(dirname "$0"); L=/config/spy-$k.log
+"$d/py-spy.real" "$@" &
+p=$!
+( sleep 4.5; if kill -0 $p 2>/dev/null; then
+    echo "hung call $k: $(cut -d' ' -f3,14,15 /proc/$p/stat) (state utime stime)" >> "$L"
+    for j in 1 2; do timeout 10 python3 "$d/probe.py" >> "$L" 2>&1; done
+    if [ "$k" = 1 ]; then timeout 20 "$d/py-spy.real" dump --pid 1 > /dev/null 2>&1
+      echo "blocking py-spy rc=$?" >> "$L"; fi
+  fi ) >/dev/null 2>&1 &
+wait $p; rc=$?
+[ "$k" = 1 ] && timeout 10 python3 "$d/probe.py" >> /config/first.log 2>&1
+exit $rc
+"""
+SIDE = r"""#!/bin/sh
+c=/tmp/hpo-side-calls; echo >> "$c"; k=$(wc -l < "$c" | tr -d ' ')
+for a; do pid=$a; done
+( timeout 4.5 /opt/hpo/py-spy dump --nonblocking --pid "$pid" > /config/side-$k.out 2>&1
+  echo "side py-spy call $k rc=$? names=$(grep -c _hb_spin /config/side-$k.out)" >> /config/spy-$k.log ) >/dev/null 2>&1 &
+exec "$@"
+"""
+EDITS = {
+    "side": ('return [sys.executable, "-c", _STDLIB_SAMPLE]',
+             'return ["/opt/hpo/side.sh", sys.executable, "-c", _STDLIB_SAMPLE]'),
+    "N1": ("    end, bound = start + seconds, start + hold_max\n", "    end, bound = start, start\n"),
+    "N2": ("            if stalled >= self.dump_after and not self._stall_dumped:", "            if False:"),
+    "N3": ("[*self.sampler, str(os.getpid())]", "[*self.sampler, '999999']"),
+    "N4": ('    if importlib.util.find_spec("_remote_debugging") is not None:\n', "    if False:\n"),
+}
+HUNG = "#!/bin/sh\nexec sleep 600\n"
+
+
+def _load(tree: Path):
+    sys.path[:0] = [str(tree / "tests"), str(tree / "tests" / "hastub"), str(tree)]
+    spec = importlib.util.spec_from_file_location("nightly_ha", tree / "tests" / "nightly_ha.py")
+    mod = importlib.util.module_from_spec(spec)
+    sys.modules["nightly_ha"] = mod
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def run_once(n, run_dir: Path, mode: str, image: str) -> tuple[str, str, bool, str]:
+    config, driver = n._stage(run_dir, two_zone_dhw=True)
+    spy = driver / "py-spy"
+    if not spy.exists():
+        raise SystemExit("no py-spy staged: put py-spy 0.4.2 on PATH")
+    (driver / "probe.py").write_text(PROBE)
+    if mode == "probe":
+        shutil.move(spy, driver / "py-spy.real")
+        spy.write_text(WRAP)
+        spy.chmod(0o755)
+    else:
+        staged = driver / "nightly_ha.py"
+        src, (old, new) = staged.read_text(), EDITS[mode]
+        if src.count(old) != 1:
+            raise SystemExit(f"--mode {mode}: the tree has no single {old.strip()!r}")
+        staged.write_text(src.replace(old, new))
+        if mode == "side":
+            (driver / "side.sh").write_text(SIDE)
+            (driver / "side.sh").chmod(0o755)
+    cmd = n.docker_command(image, config, driver, 240.0, ["--heartbeat-only"], ("SYS_PTRACE",))
+    out = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
+    (run_dir / "out.txt").write_text(out.stdout + out.stderr)
+    # The lane's own result marker, read by the lane's own reader.
+    markers = n._markers(out)
+    verdict = json.loads(markers[-1]).get("hb:positive_control") if markers else None
+    logs = " | ".join(p.read_text().strip().replace("\n", "; ")
+                      for p in sorted(config.glob("spy-*.log")) + sorted(config.glob("first.log")))
+    hung = "hung call" in logs or "rc=124" in logs or "rc=143" in logs
+    word = "NONE" if verdict is None else ("ok" if verdict[0] else "FAIL")
+    return word, (verdict[1] if verdict else ""), hung, logs
+
+
+def run_inproc(tree: Path, mode: str, spy: str, stage: Path) -> tuple[str, str]:
+    """One control in this process over the tree's (edited) nightly_ha.py."""
+    import asyncio
+
+    src = (tree / "tests" / "nightly_ha.py").read_text()
+    if mode != "plain":
+        old, new = EDITS[mode]
+        if src.count(old) != 1:
+            raise SystemExit(f"--mode {mode}: the tree has no single {old.strip()!r}")
+        src = src.replace(old, new)
+    sys.path[:0] = [str(tree / "tests"), str(tree / "tests" / "hastub"), str(tree)]
+    mod = type(sys)("nightly_ha")
+    mod.__file__ = str(tree / "tests" / "nightly_ha.py")
+    sys.modules["nightly_ha"] = mod
+    exec(compile(src, mod.__file__, "exec"), mod.__dict__)  # noqa: S102 - the tree's own driver
+    staged = stage / "py-spy"
+    if not staged.exists():
+        if spy == "hung":
+            staged.write_text(HUNG)
+            staged.chmod(0o755)
+        else:
+            real = shutil.which("py-spy")
+            if real is None:
+                raise SystemExit("--inproc real: put py-spy 0.4.2 on PATH")
+            staged.symlink_to(real)
+    mod.IN_DRIVER_DIR = str(stage)
+    kw = {} if hasattr(mod, "sample_command") else {"py_spy": str(staged)}
+    checks = mod.Checks()
+    tries = asyncio.run(mod._async_hb_control(checks, **kw))
+    readings = [mod.hb_control_reading(t) for t in tries]
+    gaps = [round(t["max_gap"] * 1000, 1) for t in tries]
+    sampler = mod.sample_command()[0] if kw == {} and mod.sample_command() else str(staged)
+    word = "FAIL" if "hb:positive_control" in checks.failures() else "ok"
+    return word, f"readings={readings} gaps_ms={gaps} sampler={Path(sampler).name}"
+
+
+def main() -> int:
+    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    ap.add_argument("--tree", type=Path, required=True)
+    ap.add_argument("--mode", choices=("probe", "side", "plain", "N1", "N2", "N3", "N4"),
+                    required=True)
+    ap.add_argument("--inproc", choices=("real", "hung"),
+                    help="run the control in this interpreter, no Docker, with this py-spy staged")
+    ap.add_argument("--runs", type=int, default=1)
+    ap.add_argument("--out", type=Path, required=True)
+    ap.add_argument("--image", default="homeassistant/home-assistant:stable")
+    args = ap.parse_args()
+    if args.inproc:
+        if args.mode in ("probe", "side"):
+            raise SystemExit(f"--mode {args.mode} needs the container; --inproc takes plain or N1-N4")
+        args.out.mkdir(parents=True, exist_ok=True)
+        ok = 0
+        for i in range(1, args.runs + 1):
+            verdict, detail = run_inproc(args.tree.resolve(), args.mode, args.inproc, args.out)
+            ok += verdict == "ok"
+            print(f"run {i}: {verdict} {detail}", flush=True)
+        print(f"SUMMARY mode={args.mode} inproc={args.inproc} python={sys.version.split()[0]} "
+              f"runs={args.runs} ok={ok} fail={args.runs - ok}")
+        return 0
+    n = _load(args.tree.resolve())
+    ok = fail = hung_runs = 0
+    for i in range(1, args.runs + 1):
+        run_dir = args.out / f"run{i}"
+        shutil.rmtree(run_dir, ignore_errors=True)
+        run_dir.mkdir(parents=True)
+        verdict, detail, hung, logs = run_once(n, run_dir, args.mode, args.image)
+        ok, fail, hung_runs = ok + (verdict == "ok"), fail + (verdict != "ok"), hung_runs + hung
+        print(f"run {i}: {verdict} {detail} || {logs}", flush=True)
+        if verdict == "ok" and not hung:
+            shutil.rmtree(run_dir, ignore_errors=True)
+    print(f"SUMMARY mode={args.mode} runs={args.runs} ok={ok} fail={fail} spy_hung={hung_runs}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/2964.md b/dev/programme/delivery/2964.md
new file mode 100644
index 000000000..7d1f2b80e
--- /dev/null
+++ b/dev/programme/delivery/2964.md
@@ -0,0 +1 @@
+- [#2964](https://github.com/tvofi/heatpump_optimizer/pull/2964) — **open**, R10-FLY-NIGHTLY-HB: heartbeat stall sampler uses the stdlib remote unwinder where it exists (R10-FLY-NIGHTLY-HB)
diff --git a/dev/programme/rosters/wave-r10-groups.json b/dev/programme/rosters/wave-r10-groups.json
index 1a0feb616..15870cef9 100644
--- a/dev/programme/rosters/wave-r10-groups.json
+++ b/dev/programme/rosters/wave-r10-groups.json
@@ -8017,7 +8017,9 @@
    "after": [
     "R10-NIGHTLY-PYSPY-RETRY"
    ],
-   "carry": [],
+   "carry": [
+    "From R10-FLY-NIGHTLY-HB (handoff/r10-fly-nightly-hb): this group's premise is changed, re-measure before building. The stable-lane hang is py-spy 0.4.2 failing structurally on the process, not a per-sample race: on the 4 local hung processes probed, py-spy past \"Found interpreter\" spun in R state, blocking (ptrace-stopped) dump hung too (rc=143 at a 20 s cut), on every call for the process life. That fix samples with CPython's own _remote_debugging unwinder wherever the container's interpreter ships one (3.14+, the stable arm), and with py-spy only on the 3.13 floor, where #2479 measured 0 hangs. The unwinder answered on 24 of 24 probes of those hung processes and named the spin on 23. So option (b), a container respawn, is owed only if, on a main carrying that fix, a nightly-ha stable run again fails hb:positive_control with every try's sampler section timed out or rc!=0; count it over the nightly history at your own merge-base (gh run list --workflow nightly.yml, non-push events, per-job hb:positive_control line), against the same count before that fix's merge as the null control. Absent such a red, close the group as superseded rather than build (b)."
+   ],
    "architect_note": "",
    "brief": "Owner of the residual left by R10-NIGHTLY-PYSPY-RETRY (#2605; verdict review/2605 f00094d17, finding 2). Real Home Assistant's py-spy hang is per process, not per sample. A held spin hung 3 of 3 tries, and a fresh-spin retry rescued 0 of 2 (F7). So the heartbeat lane's `stable` false-red rate stays at about 6.7 % per dev/audit/rca/nightly-ha-pyspy-timeout.md. Decision O-4 (orchestrator, mandate 6329234399): build option (b). When every control try times out in py-spy, restart the heartbeat HA container once (a fresh process) and re-run the control. Do not make a timeout inconclusive: that changes what the check asserts. Option (c), a longer non-blocking timeout, is the fallback only if (b) is measured not to rescue. Keep the check's power: a stub that never answers, or answers without naming the spin, still fails hb:positive_control after the respawn. Measure the false-red rate before and after over the nightly history, with a flat null control.",
    "resume": {
diff --git a/tests/closures.json b/tests/closures.json
index 8b3f2f339..dcfd62d86 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3711,6 +3711,7 @@
    "dev/audit/harnesses/r10_flow_autotrain_live.py",
    "dev/audit/harnesses/r10_flow_autotrain_mutants.sh",
    "dev/audit/harnesses/r10_flow_dispatch_mutants.py",
+   "dev/audit/harnesses/r10_fly_nightly_hb.py",
    "dev/audit/harnesses/r10_fly_orphans_landed.sh",
    "dev/audit/harnesses/r10_ftol_cell_search.py",
    "dev/audit/harnesses/r10_gate_defer_race.py",
diff --git a/tests/entities.py b/tests/entities.py
index 2df47f388..ce5526a4a 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -18149,7 +18149,7 @@ R.check(
 )
 
 
-_HB_BOTH = "in _hb_spin\npy-spy rc=0:\nThread 1 (active+gil)\n    _hb_spin (nightly_ha.py:1)\n"
+_HB_BOTH = "in _hb_spin\nsampler rc=0:\nThread 1 (active+gil)\n    _hb_spin (nightly_ha.py:1)\n"
 
 
 def _hb_ctl(gap: float, dump: str = _HB_BOTH) -> bool:
@@ -18163,10 +18163,10 @@ def _hb_ctl(gap: float, dump: str = _HB_BOTH) -> bool:
 _HB_C = _nightly.HB_CONTROL_S
 R.check(
     "hb:positive_control passes at the spin, and fails just under it, "
-    "without the spin's frame, or without py-spy's own rc=0 section naming it",
+    "without the spin's frame, or without the sampler's own rc=0 section naming it",
     _hb_ctl(_HB_C) and not _hb_ctl(_HB_C - 0.001) and not _hb_ctl(_HB_C, "idle")
-    and not _hb_ctl(_HB_C, "in _hb_spin\npy-spy rc=1:\nPermission denied\n")
-    and not _hb_ctl(_HB_C, "in _hb_spin\npy-spy rc=0:\nThread 1 (idle)\n"),
+    and not _hb_ctl(_HB_C, "in _hb_spin\nsampler rc=1:\nPermission denied\n")
+    and not _hb_ctl(_HB_C, "in _hb_spin\nsampler rc=0:\nThread 1 (idle)\n"),
     "check_hb_positive_control arms",
 )
 
@@ -18179,13 +18179,13 @@ def _hb_tries(*tries: tuple[float, str]) -> bool:
     return "hb:positive_control" not in c.failures()
 
 
-_HB_SPIED_ONLY = "py-spy rc=0:\n    _hb_spin (nightly_ha.py:1)\n"
+_HB_SPIED_ONLY = "sampler rc=0:\n    _hb_spin (nightly_ha.py:1)\n"
 R.check(
     "hb:positive_control passes on any one try that reads all three, and never "
     "on three readings split across tries",
-    _hb_tries((_HB_C, "py-spy did not run: TimeoutExpired"), (_HB_C, _HB_BOTH))
+    _hb_tries((_HB_C, "sampler did not run: TimeoutExpired"), (_HB_C, _HB_BOTH))
     and not _hb_tries((_HB_C, "in _hb_spin\n"), (_HB_C - 0.1, _HB_SPIED_ONLY))
-    and not _hb_tries((_HB_C - 0.1, _HB_BOTH), (_HB_C, "in _hb_spin\npy-spy rc=1:\n")),
+    and not _hb_tries((_HB_C - 0.1, _HB_BOTH), (_HB_C, "in _hb_spin\nsampler rc=1:\n")),
     "check_hb_positive_control over tries",
 )
 
@@ -18220,7 +18220,7 @@ def _hb_spy_run(*answers: str, rest: float = 0.05) -> tuple[bool, list[dict], in
         c = _nightly.Checks()
         began = _time.monotonic()
         tries = asyncio.run(_nightly._async_hb_control(
-            c, rest=rest, py_spy=str(stub), spy_timeout=_HB_SPY_T, dump_after=0.2,
+            c, rest=rest, sampler=[str(stub)], sample_timeout=_HB_SPY_T, dump_after=0.2,
         ))
         took = _time.monotonic() - began
         made = len(calls.read_text().splitlines()) if calls.exists() else 0
@@ -18280,26 +18280,100 @@ R.check(
     "the control's retry is bounded: each sample cut short of the old 30 s, each "
     "spin held at most one sample's timeout, under the hang bound",
     _nightly.HB_CONTROL_TRIES >= 2
-    and _nightly.PY_SPY_TIMEOUT_S < 30
-    and _nightly.HB_DUMP_S + _nightly.PY_SPY_TIMEOUT_S <= _nightly.HB_CONTROL_HOLD_S
+    and _nightly.SAMPLE_TIMEOUT_S < 30
+    and _nightly.HB_DUMP_S + _nightly.SAMPLE_TIMEOUT_S <= _nightly.HB_CONTROL_HOLD_S
     < _nightly.HB_HANG_S,
-    f"tries={_nightly.HB_CONTROL_TRIES} timeout={_nightly.PY_SPY_TIMEOUT_S}s "
+    f"tries={_nightly.HB_CONTROL_TRIES} timeout={_nightly.SAMPLE_TIMEOUT_S}s "
     f"hold={_nightly.HB_CONTROL_HOLD_S}s hang={_nightly.HB_HANG_S}s",
 )
-# The real boot passes no spy_timeout (pinned above), so the lane's cut is the
+# The real boot passes no sample_timeout (pinned above), so the lane's cut is the
 # constructor default: a default of 30 s would put the base's cost back.
 _hb_whole = _nightly.HB_CONTROL_TRIES * (_nightly.HB_CONTROL_HOLD_S + _nightly.HB_CONTROL_REST_S)
 R.check(
-    "the real lane cuts py-spy at PY_SPY_TIMEOUT_S, and the whole control, every "
+    "the real lane cuts the sampler at SAMPLE_TIMEOUT_S, and the whole control, every "
     "try hung, is bounded under 22 s",
-    _inspect.signature(_nightly.LoopHeartbeat).parameters["spy_timeout"].default
-    is _nightly.PY_SPY_TIMEOUT_S
-    and "spy_timeout" not in _inspect.getsource(_nightly._async_hb_measure)
+    _inspect.signature(_nightly.LoopHeartbeat).parameters["sample_timeout"].default
+    is _nightly.SAMPLE_TIMEOUT_S
+    and "sample_timeout" not in _inspect.getsource(_nightly._async_hb_measure)
     and _hb_whole < 22.0,
-    f"default spy_timeout="
-    f"{_inspect.signature(_nightly.LoopHeartbeat).parameters['spy_timeout'].default}; "
+    f"default sample_timeout="
+    f"{_inspect.signature(_nightly.LoopHeartbeat).parameters['sample_timeout'].default}; "
     f"whole control {_hb_whole:.2f}s",
 )
+# R10-FLY-NIGHTLY-HB: py-spy 0.4.2 hung, blocking or not, for the life of some
+# CPython 3.14.9 HA processes, so every try of the control failed; the
+# interpreter's own remote unwinder read those processes. The lane samples with
+# that unwinder wherever the interpreter ships it, and with py-spy only where
+# it does not (the 3.13 floor).
+def _hb_sampler_with(unwinder: bool, staged: bool) -> list[str] | None:
+    util, find, access = _nightly.importlib.util, _nightly.importlib.util.find_spec, _nightly.os.access
+    util.find_spec = lambda name, *a: (
+        (object() if unwinder else None) if name == "_remote_debugging" else find(name, *a)
+    )
+    _nightly.os.access = lambda path, mode: staged if str(path).endswith("/py-spy") else access(path, mode)
+    try:
+        return _nightly.sample_command()
+    finally:
+        util.find_spec, _nightly.os.access = find, access
+
+
+_hb_stdlib = [sys.executable, "-c", _nightly._STDLIB_SAMPLE]
+_hb_pyspy = [f"{_nightly.IN_DRIVER_DIR}/py-spy", "dump", "--nonblocking", "--pid"]
+R.check(
+    "the stall sampler is the interpreter's own unwinder where it ships one, staged or "
+    "not; else the staged py-spy, nonblocking; else none",
+    _hb_sampler_with(True, True) == _hb_stdlib and _hb_sampler_with(True, False) == _hb_stdlib
+    and _hb_sampler_with(False, True) == _hb_pyspy and _hb_sampler_with(False, False) is None,
+    f"{_hb_sampler_with(True, True)} / {_hb_sampler_with(False, True)} / {_hb_sampler_with(False, False)}",
+)
+
+
+import contextlib as _hb_contextlib  # noqa: E402
+
+
+def _hb_stdlib_reads(spin: bool) -> str:
+    """The stdlib sample of a child that is, or is not, inside a function named ``_hb_spin``.
+
+    The sample runs in this process against its own child: a sampler reading
+    its parent, as the lane's does, needs CAP_SYS_PTRACE under Yama's default
+    ptrace_scope, which the heartbeat container is given and this host is not.
+    """
+    body = "def _hb_spin():\n    while True: pass\n" + ("_hb_spin()\n" if spin else "while True: pass\n")
+    child = subprocess.Popen([sys.executable, "-c", body])
+    try:
+        _time.sleep(0.5)
+        out, argv = _io.StringIO(), sys.argv
+        sys.argv = ["-c", str(child.pid)]
+        try:
+            with _hb_contextlib.redirect_stdout(out):
+                exec(_nightly._STDLIB_SAMPLE, {})  # noqa: S102 - the lane's own snippet
+        finally:
+            sys.argv = argv
+        return out.getvalue()
+    finally:
+        child.kill()
+        child.wait()
+
+
+if _nightly.importlib.util.find_spec("_remote_debugging") is not None:
+    _hb_in, _hb_out = _hb_stdlib_reads(True), _hb_stdlib_reads(False)
+    _hb_reads = (
+        _nightly.hb_control_reading({"max_gap": _HB_C, "dumps": ["in _hb_spin\nsampler rc=0:\n" + _hb_in]}),
+        _nightly.hb_control_reading({"max_gap": _HB_C, "dumps": ["in _hb_spin\nsampler rc=0:\n" + _hb_out]}),
+    )
+    R.check(
+        "the stdlib sample of a real spinning process reads as the spin to the control, "
+        "and of the same process outside it does not",
+        _hb_reads[0] == (True, True, True) and _hb_reads[1] == (True, True, False),
+        f"spinning: {_hb_reads[0]} {_hb_in[-160:]!r}; idle: {_hb_reads[1]} {_hb_out[-160:]!r}",
+    )
+else:
+    R.check(
+        "the stdlib sample of a real spinning process reads as the spin to the control "
+        "(this interpreter has no remote unwinder: the lane samples it with py-spy)",
+        _hb_sampler_with(False, True) == _hb_pyspy,
+        f"{sys.version.split()[0]} has no _remote_debugging",
+    )
 _hb_cmd = _nightly.docker_command(
     "img", Path("/c"), Path("/d"), 9.0, ["--heartbeat-only"], caps=("SYS_PTRACE",)
 )
@@ -18337,7 +18411,7 @@ R.check(
     "every heartbeat scenario dwells before it settles, and py-spy never pauses the loop",
     _nightly.HB_DWELL_S >= 1.0
     and "asyncio.sleep(HB_DWELL_S)" in _inspect.getsource(_nightly._async_hb_settle)
-    and '"--nonblocking"' in _inspect.getsource(_nightly.LoopHeartbeat.dump),
+    and '"--nonblocking"' in _inspect.getsource(_nightly.sample_command),
     f"HB_DWELL_S={_nightly.HB_DWELL_S}",
 )
 R.check(
diff --git a/tests/nightly_ha.py b/tests/nightly_ha.py
index de2bcb89d..e7e9f23de 100644
--- a/tests/nightly_ha.py
+++ b/tests/nightly_ha.py
@@ -128,6 +128,7 @@ import ast
 import asyncio
 import dataclasses
 import importlib
+import importlib.util
 import json
 import math
 import os
@@ -280,19 +281,30 @@ HB_MAX_DUMPS = 3  # per scenario, so a slow runner cannot flood the log
 HB_FREEZE_S = 1.0
 HB_HANG_S = 60.0  # no tick at all this long: report by name, then exit
 HB_CONTROL_S = 0.6  # the positive control's CPU spin, over HB_DUMP_S
-# One ``py-spy dump --nonblocking`` races the process it reads: against CPython
-# 3.14.6 about 7% of stable runs had the one sample run past a 30 s timeout and
-# fail hb:positive_control (dev/audit/rca/nightly-ha-pyspy-timeout.md, #2479).
-# A healthy sample returned in at most 0.15 s on all 710 in-image samples the
-# RCA took, so 5 s is over 30x that, and a hung one costs 5 s instead of 30.
-PY_SPY_TIMEOUT_S = 5.0
+# The out-of-process sample a stall dump takes. On an interpreter that ships
+# CPython's own remote unwinder (3.14+) it is that unwinder, run in a child;
+# elsewhere (the 3.13 floor) the staged ``py-spy dump --nonblocking``. py-spy
+# 0.4.2 cannot walk some CPython 3.14.9 HA processes at all: past "Found
+# interpreter" it spins in its stack walk, blocking or not, for the life of the
+# process, so every try of the control hung (nightly run 40806276912;
+# R10-FLY-NIGHTLY-HB measured it locally). The stdlib unwinder answered on every
+# probe of the processes py-spy hung on.
+_STDLIB_SAMPLE = (
+    "import sys, _remote_debugging as rd\n"
+    "for t in rd.RemoteUnwinder(int(sys.argv[1]), all_threads=True).get_stack_trace():\n"
+    "    print(f'Thread {t.thread_id}')\n"
+    "    for f in t.frame_info:\n"
+    "        print(f'    {f.funcname} ({f.filename}:{f.lineno})')\n"
+)
+# A healthy sample returned in at most 0.15 s on all 710 in-image py-spy samples
+# the #2479 RCA took (dev/audit/rca/nightly-ha-pyspy-timeout.md), so 5 s is over
+# 30x that, and a hung one costs 5 s instead of the 30 it once did.
+SAMPLE_TIMEOUT_S = 5.0
 # The control tries a fresh spin, sampled once, up to this many times. On real
-# HA this was measured NOT to rescue a hang: in every hung run the hang held for
-# the life of the HA process, across retries inside one held spin and across
-# fresh spins 1 s apart (R10-NIGHTLY-PYSPY-RETRY, F6 and F7); a container
-# respawn is R10-NIGHTLY-HB-RESPAWN's. The retry is kept because it bounds what
-# a red costs, and because a try whose sample came back late, missed the spin
-# or answered rc!=0 is retried rather than failed.
+# HA a retry was measured NOT to rescue a py-spy hang, which holds for the life
+# of the process (R10-NIGHTLY-PYSPY-RETRY, F6 and F7). The retry is kept because
+# it bounds what a red costs, and because a try whose sample came back late,
+# missed the spin or answered rc!=0 is retried rather than failed.
 HB_CONTROL_TRIES = 3
 HB_CONTROL_REST_S = 1.0  # loop time between tries, so each spin starts afresh
 # Each spin outlasts HB_CONTROL_S until its sample has returned, so a slow but
@@ -300,7 +312,7 @@ HB_CONTROL_REST_S = 1.0  # loop time between tries, so each spin starts afresh
 # HB_HANG_S. Worst case for the whole control, every try hung:
 # HB_CONTROL_TRIES * (HB_CONTROL_HOLD_S + HB_CONTROL_REST_S) = 21.75 s, which
 # tests/entities.py pins under 22 s.
-HB_CONTROL_HOLD_S = HB_DUMP_S + PY_SPY_TIMEOUT_S + 1.0
+HB_CONTROL_HOLD_S = HB_DUMP_S + SAMPLE_TIMEOUT_S + 1.0
 HB_SETTLE_S = 120.0  # wait for the last reload's first solve to finish
 # Every scenario stays measured this long after its last action, before any
 # settling: work an abort or a save defers (a listener, a scheduled refresh)
@@ -1876,7 +1888,7 @@ async def _async_check_a9(checks: Checks, hass, entry):
 # probe is not: the largest gap between two of its ticks is how long the loop
 # went without running anything. A thread watches the last tick, so a stall
 # is dumped while it is still open -- the loop thread's Python stack first
-# (instant), then ``py-spy dump`` when the host staged one. LIMIT: the
+# (instant), then the out-of-process sample (``sample_command``). LIMIT: the
 # watcher needs the GIL, so a stall inside C code that holds it is measured
 # but dumped only once it lets go.
 
@@ -1902,10 +1914,11 @@ class LoopHeartbeat:
     """A ``call_later`` probe on a running loop and a thread watching it."""
 
     def __init__(self, loop, *, tick=HB_TICK_S, dump_after=HB_DUMP_S,
-                 hang_after=HB_HANG_S, on_hang=None, py_spy=None,
-                 spy_timeout=PY_SPY_TIMEOUT_S, dumped: threading.Event | None = None) -> None:
-        self.loop, self.tick, self.py_spy, self.spy_timeout = loop, tick, py_spy, spy_timeout
-        # Set each time a stall's dump has returned, py-spy's sample included.
+                 hang_after=HB_HANG_S, on_hang=None, sampler: list[str] | None = None,
+                 sample_timeout=SAMPLE_TIMEOUT_S, dumped: threading.Event | None = None) -> None:
+        self.loop, self.tick, self.sampler = loop, tick, sampler
+        self.sample_timeout = sample_timeout
+        # Set each time a stall's dump has returned, the sample included.
         self.dumped = dumped if dumped is not None else threading.Event()
         self.dump_after, self.hang_after, self.on_hang = dump_after, hang_after, on_hang
         self.max_gap, self.ticks, self.dumps = 0.0, 0, []
@@ -1960,17 +1973,15 @@ class LoopHeartbeat:
             frame = frame.f_back
         stack = "".join(reversed(lines)) or "<no loop frame>\n"
         text = f"stall >= {stalled * 1000:.0f} ms; loop thread:\n{stack}"
-        if self.py_spy:
+        if self.sampler:
             try:
-                # --nonblocking: a default dump ptrace-stops the process, loop
-                # included, and that pause would be added to the gap it reports.
                 spy = subprocess.run(
-                    [self.py_spy, "dump", "--nonblocking", "--pid", str(os.getpid())],
-                    capture_output=True, text=True, timeout=self.spy_timeout,
+                    [*self.sampler, str(os.getpid())],
+                    capture_output=True, text=True, timeout=self.sample_timeout,
                 )
-                text += f"py-spy rc={spy.returncode}:\n{spy.stdout}{spy.stderr[-400:]}"
+                text += f"sampler rc={spy.returncode}:\n{spy.stdout}{spy.stderr[-400:]}"
             except (OSError, subprocess.SubprocessError) as err:
-                text += f"py-spy did not run: {type(err).__name__}: {err}\n"
+                text += f"sampler did not run: {type(err).__name__}: {err}\n"
         return text
 
 
@@ -2006,11 +2017,11 @@ def check_hb_scenario(checks: Checks, name: str, summary: dict, *,
 
 
 def hb_control_reading(summary: dict) -> tuple[bool, bool, bool]:
-    """One try of the control: (gap seen, dump names the spin, py-spy rc=0 names it)."""
+    """One try of the control: (gap seen, dump names the spin, sampler rc=0 names it)."""
     named = any("_hb_spin" in d for d in summary["dumps"])
     spied = any(
-        "_hb_spin" in d.split("py-spy rc=0:", 1)[1]
-        for d in summary["dumps"] if "py-spy rc=0:" in d
+        "_hb_spin" in d.split("sampler rc=0:", 1)[1]
+        for d in summary["dumps"] if "sampler rc=0:" in d
     )
     return summary["max_gap"] >= HB_CONTROL_S, named, spied
 
@@ -2018,9 +2029,10 @@ def hb_control_reading(summary: dict) -> tuple[bool, bool, bool]:
 def check_hb_positive_control(checks: Checks, summaries: list[dict]) -> None:
     """In one try, the gap is seen and BOTH dumpers name the spin.
 
-    Requiring py-spy's own section (rc=0, naming ``_hb_spin``) is what pins
-    the wiring: a heartbeat container without SYS_PTRACE, or without the
-    staged binary, still dumps the Python stack and would pass on it alone.
+    Requiring the sampler's own section (rc=0, naming ``_hb_spin``) is what
+    pins the out-of-process read: a heartbeat without a sampler, or one that
+    cannot read the process, still dumps the Python stack and would pass on it
+    alone.
     A try whose sample hung or missed is counted, not failed.
     """
     readings = [hb_control_reading(s) for s in summaries]
@@ -2031,7 +2043,7 @@ def check_hb_positive_control(checks: Checks, summaries: list[dict]) -> None:
         "hb:positive_control",
         any(all(r) for r in readings),
         f"a {HB_CONTROL_S * 1000:.0f} ms spin read as {gap * 1000:.1f} ms; "
-        f"dump names the spin: {named}; py-spy rc=0 names it: {spied}; "
+        f"dump names the spin: {named}; sampler rc=0 names it: {spied}; "
         f"try {shown + 1} of {len(summaries)} (at most {HB_CONTROL_TRIES})",
     )
 
@@ -2057,16 +2069,21 @@ def _hb_on_hang(checks: Checks, name: str):
     return on_hang
 
 
-def _py_spy_path() -> str | None:
+def sample_command() -> list[str] | None:
+    """The stall sampler's argv, the pid appended: the interpreter's own unwinder, else py-spy."""
+    if importlib.util.find_spec("_remote_debugging") is not None:
+        return [sys.executable, "-c", _STDLIB_SAMPLE]
     path = f"{IN_DRIVER_DIR}/py-spy"
-    return path if os.access(path, os.X_OK) else None
+    # --nonblocking: a default dump ptrace-stops the process, loop included,
+    # and that pause would be added to the gap it reports.
+    return [path, "dump", "--nonblocking", "--pid"] if os.access(path, os.X_OK) else None
 
 
 async def _async_hb_measure(checks: Checks, name: str, drive,
                             **sampling) -> tuple[dict, str | None]:
     hb = LoopHeartbeat(
         asyncio.get_running_loop(), on_hang=_hb_on_hang(checks, name),
-        **{"py_spy": _py_spy_path(), **sampling},
+        **{"sampler": sample_command(), **sampling},
     )
     hb.start()
     raised = None

