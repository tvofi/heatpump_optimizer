import json, sys, subprocess, types
R = "/home/user/heatpump_optimizer"; REF = "origin/handoff/audit-r10-roster"
src = open("/home/user/rev/tools/plan/replan.py").read()
a = 'or k in INSTRUMENT_KINDS:\n        return "instrument"'; assert src.count(a) == 1
def load(s, name):
    m = types.ModuleType(name); m.__file__ = "/home/user/rev/tools/plan/replan.py"; sys.modules[name] = m
    exec(compile(s, m.__file__, "exec"), m.__dict__); return m
o = load(src, "rp_o"); mu = load(src.replace(a, 'or k in ("instrument", "policy"):\n        return "instrument"'), "rp_m")
roster = json.loads(subprocess.run(["git","-C",R,"show",f"{REF}:dev/programme/rosters/wave-r10-groups.json"],capture_output=True,text=True).stdout)
d = [(g["group"], g.get("kind"), o.roster_lane(g), o.work_class(g), mu.work_class(g), o.is_done(g)) for g in roster["groups"] if o.work_class(g) != mu.work_class(g)]
print("m13 live work_class differences over", len(roster["groups"]), "groups:", len(d))
for x in d: print(" ", x)
