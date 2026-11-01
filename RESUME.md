# #3045 fix round 5: the payment search (outcome 2, head unmoved at 9ef51b8215dd7216950f177386fb2f5a8f010a47)

Each payment prototype is one local commit on the head, never pushed. To reproduce one, apply its diff to a worktree at the head, commit it, and run `python3 tools/audit/archscore/score.py --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 <commit>`.

## prototype (a) 2113344ead987e306ffaea3cf0c218472426c618
```diff
diff --git a/.github/workflows/tests.yml b/.github/workflows/tests.yml
index e9a458bc3..95d9c2ab7 100644
--- a/.github/workflows/tests.yml
+++ b/.github/workflows/tests.yml
@@ -2294,6 +2294,7 @@ jobs:
         run: |
           set -euo pipefail
           M="$RUNNER_TEMP/metrics"; mkdir -p "$M"
+          python3 -I tests/ci_ratchet.py --archscore-out "$RUNNER_TEMP/archscore.json" & AP=$!
           # This run's three lanes, by name, from this run.
           for lane in fast coverage closures; do
             gh run download "$GITHUB_RUN_ID" --name "ci-metrics-$lane" \
@@ -2308,6 +2309,8 @@ jobs:
           # stopped returning .run_id on 2026-10-12); both stay null-safe in
           # ci_ratchet.window_entries, which owns the selection now.
           python3 -I tests/ci_ratchet.py --gather --metrics-dir "$M"
+          python3 -I tests/ci_ratchet.py --gather-runs "$RUNNER_TEMP/runs.json"
+          wait "$AP"
       # The window is ci.yml's push runs and, across the cut-over, the
       # pre-umbrella Tests runs, each carrying its jobs: the critical path is
       # a CI run's span to its last `tests / *` job (U9a). Its reads and its
@@ -2322,6 +2325,7 @@ jobs:
           python3 tests/ci_ratchet.py
           --metrics-dir "$RUNNER_TEMP/metrics"
           --runs-json "$RUNNER_TEMP/runs.json"
+          --archscore-json "$RUNNER_TEMP/archscore.json"
 
 
   # Same-repo PR only: the closures job already re-recorded under strace.
diff --git a/tests/ci_ratchet.py b/tests/ci_ratchet.py
index 814a9645e..be5f5420e 100644
--- a/tests/ci_ratchet.py
+++ b/tests/ci_ratchet.py
@@ -610,8 +610,9 @@ def critical_path_minutes(runs_json: Path, stat: str = "median") -> float:
 
 
 def derive(metrics_dir: Path, runs_json: Path | None,
-           record: bool = False) -> dict[str, float]:
-    derived: dict[str, float] = dict(archscore_metrics())
+           record: bool = False, archscore_json: Path | None = None) -> dict[str, float]:
+    derived: dict[str, float] = dict(json.loads(archscore_json.read_text())
+                                     if archscore_json else archscore_metrics())
     events = read_metrics(metrics_dir)
     push_runs = [rows for (event, _), rows in events.items()
                  if event == "push"]
@@ -1114,6 +1115,9 @@ def main(argv: list[str] | None = None) -> int:
             return 2
         gather(metrics_dir)
         return 0
+    if argv[:1] == ["--archscore-out"] and len(argv) == 2:
+        Path(argv[1]).write_text(json.dumps(archscore_metrics()))
+        return 0
     if argv[:1] == ["--gather-runs"]:
         window = PUSH_WINDOW
         if len(argv) == 4 and argv[2] == "--window" and argv[3].isdigit() and int(argv[3]) > 0:
@@ -1131,8 +1135,10 @@ def main(argv: list[str] | None = None) -> int:
             return 2
         record_reason = argv[i + 1]
         del argv[i:i + 2]
-    metrics_dir = runs_json = None
+    metrics_dir = runs_json = archscore_json = None
     args = list(argv)
+    if "--archscore-json" in args:
+        i = args.index("--archscore-json"); archscore_json = Path(args[i + 1]); del args[i:i + 2]
     for flag in ("--metrics-dir", "--runs-json"):
         if flag in args:
             i = args.index(flag)
@@ -1152,7 +1158,8 @@ def main(argv: list[str] | None = None) -> int:
             print(f"ci-ratchet: refusing the budget table: {p}",
                   file=sys.stderr)
         return 1
-    derived = derive(metrics_dir, runs_json, record=record_reason is not None)
+    derived = derive(metrics_dir, runs_json, record=record_reason is not None,
+                     archscore_json=archscore_json)
     if record_reason is not None:
         head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                               capture_output=True, text=True,
```

## prototype (b) 94c7d38ebe9c4f4a8ba636d82423080ccb9f3b47
```diff
diff --git a/tests/ci_ratchet.py b/tests/ci_ratchet.py
index 814a9645e..2dfaccd57 100644
--- a/tests/ci_ratchet.py
+++ b/tests/ci_ratchet.py
@@ -641,7 +641,7 @@ def record_table(budgets: dict, derived: dict, head: str, reason: str) -> dict:
     """The table `--record` writes: every derived metric, stamped. A band is a
     bound sized from measured noise, not a derived value: a re-record carries
     it over unchanged."""
-    return {**{k: v for k, v in derived.items()},
+    return {**derived,
             **{k: budgets[k] for k in BAND_KEYS if k in budgets},
             "recorded_at": head, "reason": reason}
 
```

## prototype (c) e4bebfe39ec5d2d89e0e70f818d134a981560645
```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 41eeb74c0..285e1bddb 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -90,7 +90,8 @@ jobs:
     steps:
       - uses: actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5
         with:
-          fetch-depth: 0
+          # A push to main derives nothing from history; every other event may.
+          fetch-depth: ${{ (github.event_name == 'push' && github.ref == 'refs/heads/main') && 1 || 0 }}
           persist-credentials: false
       - name: Restore the programs from the base
         env:
```

## Scores, 2026-11-01
```
== head 9ef51b8215dd7216950f177386fb2f5a8f010a47
Architecture score: dS +0.0000 NULL
Architecture score: dS +0.0000 NULL
== a 2113344ead987e306ffaea3cf0c218472426c618
Architecture score: dS +0.0000 NULL
Architecture score: dS +0.0000 NULL
== b 94c7d38ebe9c4f4a8ba636d82423080ccb9f3b47
Architecture score: dS +0.0000 NULL
Architecture score: dS +0.0000 NULL
== c e4bebfe39ec5d2d89e0e70f818d134a981560645
Architecture score: dS +0.0000 NULL
Architecture score: dS +0.0000 NULL
```

## Fetch timing (refs/heads/main into an empty repository)
```
run1 depth=full 22.608569691 s
run1 depth=1 2.969915449 s
run2 depth=full 19.424398835 s
run2 depth=1 3.169905730 s
```

## critjob.py (sha1 9fa09d25fab72040a9fadbd979c24b6df5bcfb45)
```python
import sys, json, copy, statistics, datetime as dt, collections
sys.path.insert(0, "tests"); import ci_ratchet as c
runs = json.load(open(sys.argv[1]))["workflow_runs"]
def shift(j, mins):
    e = c._at(j["completed_at"]) - dt.timedelta(minutes=mins)
    j["completed_at"] = e.isoformat().replace("+00:00", "Z")
base = []; crit = collections.Counter(); per = []
for r in runs:
    m = c.run_minutes(r)
    if m is None: continue
    base.append(m)
    names = []
    for i, j in enumerate(r["jobs"]):
        if not j.get("completed_at"): continue
        r2 = copy.deepcopy(r); shift(r2["jobs"][i], 0.5)
        if c.run_minutes(r2) < m - 0.2: names.append(j["name"])
    crit[" > ".join(names) or "?"] += 1
    per.append((r["head_sha"][:9], m, names))
print("n", len(base), "median", statistics.median(base))
for k, v in crit.most_common(): print(f"{v:3d}  {k}")
# median of sliding 8
ms=[statistics.median(base[i:i+8]) for i in range(len(base)-7)]
print("8-run median range", min(ms), max(ms), "newest8", ms[0])
```

## sim.py (sha1 aed8cb5177ff3c48f7c276426c037fc35f51dc1d)
```python
import sys, json, copy, statistics as st, datetime as dt
sys.path.insert(0, "tests"); import ci_ratchet as c
runs = json.load(open(sys.argv[1]))["workflow_runs"]
def sim(cut_s, job="tests / ci-ratchet"):
    out=[]
    for r in runs:
        r2=copy.deepcopy(r)
        for j in r2["jobs"]:
            if j["name"]==job and j.get("completed_at") and j.get("started_at"):
                w=(c._at(j["completed_at"])-c._at(j["started_at"])).total_seconds()
                cut=min(cut_s, max(0.0, w-5))
                j["completed_at"]=(c._at(j["completed_at"])-dt.timedelta(seconds=cut)).isoformat().replace("+00:00","Z")
        m=c.run_minutes(r2)
        if m is not None: out.append(m)
    ms=[st.median(out[i:i+8]) for i in range(len(out)-7)]
    return st.median(out), min(ms), max(ms), max(abs(x-st.median(out)) for x in ms)
for cut in (0, 10, 28, 36):
    med, lo, hi, dev = sim(cut)
    print(f"ci-ratchet -{cut:2d}s: median {med:.3f}  8-run medians {lo:.3f}..{hi:.3f}  max|dev| {dev:.3f}  headroom {34.267-med:+.3f}")
```

## Outputs, 2026-11-01
```
ci-ratchet - 0s: median 33.867  8-run medians 32.916..34.575  max|dev| 0.951  headroom +0.400
ci-ratchet -10s: median 33.700  8-run medians 32.833..34.409  max|dev| 0.867  headroom +0.567
ci-ratchet -28s: median 33.416  8-run medians 32.683..34.108  max|dev| 0.733  headroom +0.851
ci-ratchet -36s: median 33.341  8-run medians 32.617..33.975  max|dev| 0.725  headroom +0.926
```
