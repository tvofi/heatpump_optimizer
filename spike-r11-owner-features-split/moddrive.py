"""Spike (design ref only, never merges): the file-edit drive for module-level rows.

    cd <base tree>; SPIKE=<swap_run dir> python3 moddrive.py LINES.json PARTS.json SCRIPT OUT.jsonl --rows FILE [--workers W]

A module-level line runs at import, so no fork point shares a prefix. Per row: the mutant is written
into a per-worker git worktree of the base (never a copy without .git), SCRIPT runs there under
swap_run's swap mode (each part on its own state copy), and the run stops at its first FAIL line,
attributed by `@@SPAN <id> <part>` to its part. CPU-s is every process of the run's own session
(script, solve workers), read by ps just before the stop, plus the script's own rusage on exit.
A row that ends with no FAIL survived. The base's swap run of SCRIPT prints no FAIL (revision 3's
d_p0.txt); null rows (`NULL` in FILE) run unmutated and must survive.
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time
import queue
from pathlib import Path

ROOT = Path.cwd()
SPIKE = os.environ["SPIKE"]
sys.path[:0] = [str(ROOT / "tests"), SPIKE, os.path.dirname(os.path.abspath(__file__))]
import forkdrive  # noqa: E402


def session_cpu(sid):
    out = subprocess.run(["ps", "-axo", "pid=,pgid=,time="], capture_output=True, text=True).stdout
    return sum(forkdrive._ps_seconds(f[2]) for f in (l.split() for l in out.splitlines())
               if len(f) == 3 and f[1] == str(sid))


def drive(tree, script, parts_path, rel, text):
    orig = (tree / rel).read_bytes() if rel else None
    if rel:
        (tree / rel).write_text(text)
    env = dict(os.environ, PYTHONPATH="tests/hastub:tests", PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    p = subprocess.Popen([sys.executable, f"{SPIKE}/swap_run.py", "run", "swap", "--script", script, "--parts", parts_path],
                         cwd=tree, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         start_new_session=True)
    verdict, span, part, detail, live = "survived", "header", "header", "", 0.0
    try:
        for ln in p.stdout:
            if ln.startswith("@@SPAN "):
                bits = ln[7:].rstrip("\n").rsplit(" ", 1)
                span, part = bits[0], bits[-1]
                continue
            if ln.lstrip().startswith("FAIL"):
                verdict, detail = "killed", ln.strip()[:200]
                live = session_cpu(p.pid)
                os.killpg(p.pid, signal.SIGKILL)
                break
    finally:
        p.stdout.close()
        _, status, ru = os.wait4(p.pid, 0)
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if rel:
            (tree / rel).write_bytes(orig)
    if verdict == "survived" and os.waitstatus_to_exitcode(status) not in (0,):
        verdict, detail = "killed", f"exit {os.waitstatus_to_exitcode(status)}"
    own = ru.ru_utime + ru.ru_stime
    return {"verdict": verdict, "span": span, "part": part, "detail": detail,
            "cpu_s": round(max(own, live), 2), "script_cpu_s": round(own, 2)}


def main():
    a = sys.argv[1:]
    lines_path, parts_path, script, out_path = a[:4]
    workers = int(a[a.index("--workers") + 1]) if "--workers" in a else 1
    want = [l.strip() for l in open(a[a.index("--rows") + 1]) if l.strip()]
    rows, _ = forkdrive.rows_for(lines_path, json.load(open(parts_path)), script)
    idx = {r["anchor"]: r for r in rows}
    q = queue.Queue()
    for w in want:
        q.put(w)
    trees = []
    for w in range(workers):
        t = Path(f"/tmp/hpo-design-features-split-mod{w}")
        if not t.exists():
            subprocess.run(["git", "worktree", "add", "--detach", str(t), "HEAD"], check=True, capture_output=True)
        (t / script).write_bytes((ROOT / script).read_bytes())
        trees.append(t)
    lock = threading.Lock()
    outf = open(out_path, "a")

    def work(t):
        while True:
            try:
                w = q.get_nowait()
            except queue.Empty:
                return
            t0 = time.time()
            if w == "NULL":
                res = drive(t, script, os.path.abspath(parts_path), None, None)
            else:
                r = idx[w]
                ms = forkdrive.mutant_source(w, r["file"])
                res = {"verdict": "refused", "detail": "no mutant"} if ms is None else \
                    drive(t, script, os.path.abspath(parts_path), r["file"], ms[1].decode())
            res.update(anchor=w, module_level=True, wall_s=round(time.time() - t0, 1))
            with lock:
                outf.write(json.dumps(res) + "\n")
                outf.flush()
                print(f"@@DONE {w} {res['verdict']} {res.get('part')} cpu={res.get('cpu_s')}", flush=True)

    ths = [threading.Thread(target=work, args=(t,)) for t in trees]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    print("@@END", flush=True)


if __name__ == "__main__":
    main()
