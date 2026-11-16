# group_class of every class-less group of the r10/r11 rosters, with roster_lib at the merge base vs the head.
import sys, json, subprocess, importlib.util
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
head = load("tools/audit/seat/roster_lib.py", "rl_head")
base = load(sys.argv[1], "rl_base"); base._ROOT = head._ROOT
import pathlib; base.__file__ = str(pathlib.Path("tools/audit/seat/roster_lib.py").resolve())
print("lane-less X:", base.group_class({"group": "X"}), "->", head.group_class({"group": "X"}))
for r in ("wave-r10-groups.json", "wave-r11-groups.json"):
    d = json.loads(subprocess.run(["git", "show", f"origin/handoff/audit-r10-roster:dev/programme/rosters/{r}"], capture_output=True, text=True).stdout)
    nc = [g for g in d["groups"] if not g.get("class")]
    flips = [g["group"] for g in nc if base.group_class(g) != head.group_class(g)]
    print(r, "class-less", len(nc), "flipped", len(flips), flips[:8])
