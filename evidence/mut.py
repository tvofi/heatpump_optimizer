import sys, subprocess, shutil, filecmp
f = sys.argv[1] + "/tools/audit/seat/orchestrator_tick.py"
orig = open(f).read(); shutil.copy(f, f + ".orig")
M = {
 "M1 filter removed": ("if n not in (req or ()) and self.superseded(latest[n])]", "if False]"),
 "M2 conclusion test removed": ('if cr.get("conclusion") != "cancelled" or not cr.get("id"):', 'if not cr.get("id"):'),
 "M3 pattern matches all": ('SUPERSEDED = re.compile(r"Canceling since a higher priority waiting request for \\S+ exists")', 'SUPERSEDED = re.compile(r"")'),
 "M4 unreadable read as superseded": ("notes = json.loads(o) if code == 0 else []", 'notes = json.loads(o) if code == 0 else [{"message": "Canceling since a higher priority waiting request for x exists"}]'),
 "M5 required exclusion removed": ("if n not in (req or ()) and self.superseded", "if self.superseded"),
 "M6 list guard removed": ("return isinstance(notes, list) and any(", "return any("),
 "M7 superseded lanes not dropped from red": ("red = [n for n in red if n not in sup]", "red = red"),
 "M8 match->search (pattern unanchored)": ("SUPERSEDED.match(a.get", "SUPERSEDED.search(a.get"),
 "M9 dict guard removed": ("isinstance(a, dict) and SUPERSEDED", "SUPERSEDED"),
 "M10 ValueError -> True": ("        except ValueError:\n            return False\n        return isinstance(notes, list)", "        except ValueError:\n            return True\n        return isinstance(notes, list)"),
}
for k, (a, b) in M.items():
    assert orig.count(a) == 1, (k, orig.count(a))
    open(f, "w").write(orig.replace(a, b))
    p = subprocess.run([sys.executable, "tools/audit/seat/orchestrator_tick.py", "--self-test"], cwd=sys.argv[1], capture_output=True, text=True)
    out = p.stdout + p.stderr
    fails = [l.strip() for l in out.splitlines() if "FAIL" in l]
    print(f"RESULT {k}: rc={p.returncode} {out.strip().splitlines()[-1] if out.strip() else ''}")
    for l in fails[:5]: print("   ", l[:160])
open(f, "w").write(orig)
print("restored identical:", filecmp.cmp(f, f + ".orig", shallow=False))
