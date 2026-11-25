#!/usr/bin/env python3
"""V2 (own harness): write each candidate's mutant line into the real production file of a private clone of the
baseline tree (refusing when the line is not the record's `old`), re-run the probe's scenario there, restore the
file byte-for-byte, and keep the output.  Metric (mine): of the probe's arms that move in the clean run (V1),
how many read the finder's MUTANT value in the BASELINE arm once the mutation is on disk, i.e. whether the
finder's in-memory perturbation is the real one-line mutant.  One worker per clone; clones are APFS copies."""
import json, os, re, subprocess, sys, time, pathlib, shutil
from concurrent.futures import ThreadPoolExecutor
D = pathlib.Path("<seat-dir>")
OUT = D / "v2"; OUT.mkdir(exist_ok=True)
N = int(os.environ.get("V2_JOBS", "4"))
cands = json.load(open(D / "candidates.json"))
only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None
todo = [c for c in cands if (not only or c["box"] in only) and not (OUT / f"{c['key']}.json").exists()]


def clone(i):
    t = D / f"v2tree{i}"
    if not t.exists():
        subprocess.run(["cp", "-cR", str(D / "base"), str(t)], check=True)
    return t


def mutant(c, tree):
    src = re.search(r"--src (\S+)", c.get("gate_command") or "")
    src = src.group(1) if src else "complete"
    return json.loads((tree / "dev/audit/rounds/round11/D3/s1/state/results" / src / f"{c['key']}.json").read_text())["mutant"]


def run(i, c):
    tree = clone(i)
    m = mutant(c, tree)
    p = tree / m["file"]
    orig = p.read_bytes()
    lines = orig.decode().split("\n")
    k = int(m["line"]) - 1
    rec = {"key": c["key"], "box": c["box"], "file": m["file"], "line": m["line"], "old": m["old"], "new": m["new"]}
    if lines[k] != m["old"]:
        rec.update(applied=False, note=f"line is {lines[k]!r}")
    else:
        lines[k] = m["new"]
        p.write_text("\n".join(lines))
        for pyc in (p.parent / "__pycache__").glob(p.stem + ".*.pyc"):
            pyc.unlink()
        t = time.time()
        try:
            r = subprocess.run([sys.executable, c["probe_path"]], cwd=tree, env=dict(os.environ, PYTHONPATH="tests/hastub"),
                               capture_output=True, text=True, timeout=900)
            rec.update(applied=True, rc=r.returncode, stdout=r.stdout[-20000:], stderr=r.stderr[-3000:])
        except subprocess.TimeoutExpired:
            rec.update(applied=True, rc="timeout", stdout="", stderr="")
        finally:
            p.write_bytes(orig)
            for pyc in (p.parent / "__pycache__").glob(p.stem + ".*.pyc"):
                pyc.unlink()
        rec.update(wall_s=round(time.time() - t, 1), load1=round(os.getloadavg()[0], 1))
    json.dump(rec, open(OUT / f"{c['key']}.json", "w"))
    print(c["box"], c["key"], rec.get("applied"), rec.get("rc"), flush=True)


def worker(i):
    while todo:
        try:
            c = todo.pop(0)
        except IndexError:
            return
        run(i, c)


with ThreadPoolExecutor(N) as ex:
    list(ex.map(worker, range(N)))
for i in range(N):
    shutil.rmtree(D / f"v2tree{i}", ignore_errors=True)
print("V2-DONE", flush=True)
