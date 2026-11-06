"""Parse tests / replay (and nightly slow) job logs into draws.tsv.

One row per (job, fixture, arm): job, run, event, created, conclusion, fixture,
arm (clean|cpu|memory|loop), ref_ms, loop_ref_ms, cpu_ratio, peak_kib, loop_cpu_ratio.
"""
import ast, os, re, sys

CI = os.path.expanduser("~/ci")
jobs = {}
for ln in open(f"{CI}/jobs.tsv"):
    run, ev, cr, jid, name, concl = ln.rstrip("\n").split("\t")
    jobs[jid] = (run, ev, cr, name, concl)

COST = re.compile(r"cycles over \d+ entities in [\d.]+ s; cost (\{.*\})")
ARM = re.compile(r"\s(cpu|memory|loop) doubled: cost (\{.*\})")
FIX = re.compile(r"-- replay (\S+\.json)")
out = []
for jid, (run, ev, cr, name, concl) in jobs.items():
    p = f"{CI}/logs/{jid}.log"
    if not os.path.exists(p):
        continue
    fixture = None
    for ln in open(p, errors="replace"):
        m = FIX.search(ln)
        if m:
            fixture = m.group(1)
            continue
        m = COST.search(ln)
        arm = "clean"
        if not m:
            m2 = ARM.search(ln)
            if not m2:
                continue
            arm, blob = m2.group(1), m2.group(2)
        else:
            blob = m.group(1)
        try:
            d = ast.literal_eval(blob)
        except Exception:
            continue
        out.append((jid, run, ev, cr, concl, name, fixture, arm, d.get("ref_ms"),
                    d.get("loop_ref_ms"), d.get("cpu_ratio"), d.get("peak_kib"),
                    d.get("loop_cpu_ratio")))
with open(f"{CI}/draws.tsv", "w") as f:
    f.write("job\trun\tevent\tcreated\tconclusion\tjobname\tfixture\tarm\tref_ms\tloop_ref_ms\tcpu_ratio\tpeak_kib\tloop_cpu_ratio\n")
    for r in out:
        f.write("\t".join(str(x) for x in r) + "\n")
print(len(out), "rows from", len({r[0] for r in out}), "jobs")
