import subprocess, sys, shutil, pathlib
wt = pathlib.Path.home()/"wt/tools/audit/seat"
muts = [
 ("plant_recall.py", 'if (t / ".git").exists():', 'if False:'),
 ("plant_recall.py", 'tally[key] = (f + (state == "FOUND"), n + 1)', 'tally[key] = (f + (state != "MISSED"), n + 1)'),
 ("plant_recall.py", 'f.write_text(f.read_text(errors="replace").replace(p["old"], p["new"], 1))', 'f.write_text(f.read_text(errors="replace").replace(p["old"], p["new"]))'),
 ("plant_recall.py", 'return plant["file"] in (finding.get("files") or []) and \\', 'return True and \\'),
 ("plant_recall.py", 'cells |= {f"{parts[0]}={lv}" for lv in parts[2].split(",") if lv}', 'cells |= {f"{parts[0]}={lv}" for lv in parts[2].split(",")[:1] if lv}'),
 ("plant_recall.py", 'if plants_path.resolve().is_relative_to(t.resolve()):', 'if False:'),
 ("plant_recall.py", 'while (nxt := into(cur)) and nxt in raw and nxt not in seen:', 'while False:'),
 ("finder_overlap.py", 'n1, n2, m = len(bugs_a), len(bugs_b), len(bugs_a & bugs_b)', 'n1, n2, m = len(bugs_a), len(bugs_b), len(ids_a & ids_b)'),
 ("finder_overlap.py", 'est = (n1 + 1) * (n2 + 1) / (m + 1) - 1', 'est = n1 * n2 / max(m, 1)'),
 ("finder_overlap.py", 'same = a["model"].strip().lower() == b["model"].strip().lower()', 'same = a["model"] == b["model"]'),
 ("finder_overlap.py", 'return {i: cid if v in plant_recall.REAL else None', 'return {i: i if v in plant_recall.REAL else None'),
]
for fn, old, new in muts:
    d = pathlib.Path(sys.argv[1]); shutil.rmtree(d, ignore_errors=True); shutil.copytree(wt, d)
    src = (d/fn).read_text(); assert src.count(old)==1, (fn, old); (d/fn).write_text(src.replace(old,new,1))
    r = subprocess.run([sys.executable,"-I",str(d/fn),"--self-test","--no-mutants"],capture_output=True,text=True)
    fails=[l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    print(("KILLED " if r.returncode else "SURVIVED ")+fn+": "+new[:70], "|", (fails[:1] or [r.stdout.strip().splitlines()[-1:] ])[0])
