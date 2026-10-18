"""Every `needs:` edge in every workflow: what it carries and what it costs.

    python3 -I measure/deps.py REPO_CHECKOUT measure/raw > measure/deps.txt

Part 1 (static, from the workflow files): for each edge X -> Y, what Y reads of X:
  outputs  `needs.X.outputs.<o>` in Y
  result   `needs.X.result` in Y
  artifact an artifact name/pattern Y downloads that X uploads
  ORDER    none of these: the edge only orders the two jobs
Part 2 (measured, Tests PR runs from phase 1 and CodeQL PR runs from fetch2.sh): a
replay of each run's DAG with measured durations and per-job queue latency held
fixed. For each edge, the run would end this much sooner if the edge were removed
(Y then starts when its other needs end). Median and max over runs, plus how
often the edge was binding (X was Y's last need to finish).
"""
import json, re, statistics, sys, yaml
from collections import defaultdict
from datetime import datetime
from pathlib import Path

repo, raw = Path(sys.argv[1]), Path(sys.argv[2])
def T(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() if s else None

graphs = {}
print("# Part 1: every needs edge, and what it carries\n")
print("| workflow | X (need) | Y (dependent) | carries |")
print("|---|---|---|---|")
for f in sorted((repo / ".github/workflows").glob("*.yml")):
    text = f.read_text(); d = yaml.safe_load(text); jobs = d.get("jobs") or {}
    ups = {}
    for jid, j in jobs.items():
        for s in j.get("steps") or []:
            if "upload-artifact" in str(s.get("uses", "")):
                ups.setdefault(jid, []).append(str((s.get("with") or {}).get("name", "")))
    g = {}
    for jid, j in jobs.items():
        n = j.get("needs") or []; n = [n] if isinstance(n, str) else n; g[jid] = n
        body = yaml.safe_dump(j)
        downs = [str((s.get("with") or {}).get("name") or (s.get("with") or {}).get("pattern") or "*")
                 for s in j.get("steps") or [] if "download-artifact" in str(s.get("uses", ""))]
        for x in n:
            outs = sorted(set(re.findall(rf"needs\.{re.escape(x)}\.outputs(?:\.|\[')([\w-]+)", body))
                          | ({"[matrix]"} if re.search(rf"needs\.{re.escape(x)}\.outputs\[\s*matrix", body) else set()))
            api = bool(re.search(r"actions/runs|/artifacts|gh run download|gh api", body)) and not outs
            res = f"needs.{x}.result" in body
            arts = [a for a in downs for u in ups.get(x, []) if a.replace("*", "") and (a.rstrip("*") in u or u.split("$")[0].rstrip("-") in a)]
            c = []
            if outs: c.append("outputs " + ",".join(outs))
            if res: c.append("result")
            if arts: c.append("artifact " + ",".join(sorted(set(arts))))
            if not c and api: c.append("API read of the run (artifacts/jobs)")
            print(f"| {f.name} | {x} | {jid} | {'; '.join(c) or '**ORDER only**'} |")
    graphs[f.name] = (g, jobs)

def jid_of(name, jobs):
    if name in jobs: return name
    base = name.split(" (")[0]
    if base in jobs: return base
    for k, j in jobs.items():
        nm = str(j.get("name", ""))
        if nm and "${{" in nm and name.startswith(nm.split("${{")[0]): return k
    return None

def replay(run_jobs, start, g, jobs, drop=None):
    inst = defaultdict(list)
    for j in run_jobs:
        if j["conclusion"] == "skipped" or not j.get("started_at") or not j.get("completed_at"): continue
        k = jid_of(j["name"], jobs)
        if k: inst[k].append((T(j["started_at"]), T(j["completed_at"])))
    end = {k: max(e for _, e in v) for k, v in inst.items()}
    q = {}
    for k, v in inst.items():
        ns = [n for n in g.get(k, []) if n in end]
        ref = max([end[n] for n in ns], default=start)
        q[k] = [(max(0.0, s - ref), e - s) for s, e in v]
    new = {}
    def fin(k, seen=()):
        if k in new: return new[k]
        ns = [n for n in g.get(k, []) if n in end and (k, n) != drop and n not in seen]
        ref = max([fin(n, seen + (k,)) for n in ns], default=start)
        new[k] = max(ref + qq + dd for qq, dd in q[k]); return new[k]
    for k in inst: fin(k)
    binding = {}
    for k in inst:
        ns = [n for n in g.get(k, []) if n in end]
        if ns: binding[k] = max(ns, key=lambda n: end[n])
    return (max(end.values()) if end else start), (max(new.values()) if new else start), binding

def measure(wf, runs_file, prefix):
    g, jobs = graphs[wf]
    runs = json.loads((raw / runs_file).read_text())["workflow_runs"]
    edges = [(y, x) for y, ns in g.items() for x in ns]
    gain = defaultdict(list); bind = defaultdict(int); n = 0
    for r in runs:
        f = raw / f"{prefix}{r['id']}.json"
        if not f.exists() or not r.get("run_started_at"): continue
        rj = json.loads(f.read_text())["jobs"]; st = T(r["run_started_at"])
        base_end, _, b = replay(rj, st, g, jobs)
        if base_end == st: continue
        n += 1
        for y, x in b.items(): bind[(y, x)] += 1
        for e in edges:
            _, alt, _ = replay(rj, st, g, jobs, drop=e)
            gain[e].append(base_end - alt)
    print(f"\n## {wf}: {n} pull_request runs replayed\n")
    print("| X -> Y | binding in | run ends sooner without the edge: median s | max s |")
    print("|---|---|---|---|")
    for (y, x) in sorted(edges, key=lambda e: -statistics.median(gain[e]) if gain[e] else 0):
        v = gain[(y, x)]
        if v: print(f"| {x} -> {y} | {bind[(y, x)]}/{n} | {statistics.median(v):.0f} | {max(v):.0f} |")

print("\n# Part 2: measured cost of each edge")
measure("tests.yml", "tests_runs_pull_request.json", "tests_jobs_")
measure("codeql.yml", "runs_codeql_pr.json", "jobs_")
