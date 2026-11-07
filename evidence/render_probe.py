# reviewer-built render probe (not the finder's file; round 2's probe was not committed)
import sys, pathlib
r = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(r / "tools/audit/seat"))
import sweep_render as s
t = (r / "tools/audit/seat/sweep_template.md").read_text()
names = s.declared(t)
base = {n: f"/tmp/probe/{n}" for n in names if n not in s.OPTIONAL_FLAGS}
def go(label, ov):
    try: s.render(t, ov, r); print(label, "-> OK")
    except s.Refused as e: print(label, "-> REFUSED:", e)
five = ["gantt_roster", "gantt_acks", "fire_ledger", "train_glob", "unheld_skip"]
go("control (declared keys only)", {k: v for k, v in base.items() if k not in five})
go("all five + declared", {**base, **{k: f"/tmp/probe/{k}" for k in five}})
for k in five:
    go(f"declared minus {k}", {kk: v for kk, v in base.items() if kk != k} if k in base else base)
go("null: + zz_undeclared_probe", {**base, "zz_undeclared_probe": "x"})
