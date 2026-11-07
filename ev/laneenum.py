import json, sys, subprocess, re
W = sys.argv[1]; R = "/home/user/heatpump_optimizer"; REF = "origin/handoff/audit-r10-roster"
ls = subprocess.run(["git","-C",R,"ls-tree","--name-only",REF,"dev/programme/rosters/"],capture_output=True,text=True).stdout.split()
cands = sorted((int(m.group(1)),p) for p in ls if (m:=re.search(r"wave-r(\d+)-groups\.json$",p)))
path = cands[-1][1]
roster = json.loads(subprocess.run(["git","-C",R,"show",f"{REF}:{path}"],capture_output=True,text=True).stdout)
sha = subprocess.run(["git","-C",R,"rev-parse",REF],capture_output=True,text=True).stdout.strip()
print(f"roster {REF} {sha} {path}")
G = {g["group"]: g for g in roster["groups"]}
base = json.load(open(f"{W}/ev/plan-base.json"))["groups"]; head = json.load(open(f"{W}/ev/plan-rev.json"))["groups"]
print("groups", len(G), len(base), len(head))
def counts(p, open_only=False):
    c = {}
    for n, v in p.items():
        if open_only and v["done"]: continue
        c[v["lane"]] = c.get(v["lane"], 0) + 1
    return dict(sorted(c.items()))
for lab, p in (("base", base), ("head", head)):
    print(lab, "all", counts(p)); print(lab, "open", counts(p, True))
INST = ("tools/","tests/",".github/",".claude/","dev/","docs/")
ROOT = {"CLAUDE.md","AGENTS.md","README.md","RELEASE_NOTES.md"}
def cls(f):
    if f.startswith("custom_components/"): return "integ"
    if f.startswith(INST) or f in ROOT: return "inst"
    return "bare" if "/" not in f else "other"
def owned(g): return list(g.get("files") or []) + list(g.get("hot_files") or [])
TOOLK = ("instrument","policy","rca","tooling")
moved = [n for n in head if base.get(n, {}).get("lane") != head[n]["lane"]]
dirs = {}
for n in moved: dirs[f"{base[n]['lane']}->{head[n]['lane']}"] = dirs.get(f"{base[n]['lane']}->{head[n]['lane']}", 0) + 1
print("moved", len(moved), dirs, "open moved", sum(1 for n in moved if not head[n]["done"]))
bad = []
for n in sorted(moved):
    g = G[n]; fs = owned(g); cs = sorted({cls(f) for f in fs})
    ok = (cs == ["inst"]) or (not fs and (g.get("kind") in TOOLK or g.get("class") == "instrument"))
    print(f"MOVED {n}\t{base[n]['lane']}->{head[n]['lane']}\tkind={g.get('kind')} class={g.get('class')} done={head[n]['done']} files={cs}{'' if ok else '  <-- SUSPECT'}")
    if not ok: bad.append(n)
print("moved-suspect", bad)
sus2 = []
for n in sorted(head):
    if head[n]["lane"] != "Core model": continue
    g = G[n]; fs = owned(g); cs = sorted({cls(f) for f in fs})
    why = "integ" if "integ" in cs else ("bare/other" if cs and cs != ["inst"] else ("nofile" if not fs else "ONLY-INST"))
    if why == "ONLY-INST" or (why == "nofile" and (g.get("kind") in TOOLK or g.get("class") == "instrument")): sus2.append(n)
    print(f"CORE {n}\t{why}\tkind={g.get('kind')} class={g.get('class')} done={head[n]['done']} files={cs}")
print("core-suspect", sus2)
w = [n for n in head if head[n]["lane"] in ("Instruments","Docs") and any(cls(f) == "integ" for f in owned(G[n]))]
print("inst/docs owning integration file at head:", sorted(w), "of which moved:", sorted(set(w) & set(moved)))
