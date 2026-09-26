#!/usr/bin/env python3
# D14-s5 detector for bug class I2 ("a measured closure or scope diverges from
# the real dependency graph").
#
# METRIC: seams = number of (script S, repo file F) pairs where F was opened for
#   reading by S's run OR BY ANY PROCESS S SPAWNED (strace -f), F is not in S's
#   committed closure, and tests/closure.py:select([F]) returns mode "scoped"
#   with S skipped -- i.e. a change to F alone would not run a script whose run
#   reads F.  Count key: the plan select() delivers, never the closure text.
# INSTRUMENTED SYMBOLS: tests/closure.py:select (the scope decision),
#   tests/closure.py:_rel and _is_real_file and _STRACE_OPEN (the recorder's
#   own path normalisation and the strace parse its node lane uses).
# COMMAND (repo root):
#   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
#     tools/audit/round9/D14/s5/closure_divergence.py
#   add --scripts tests/a.py,tests/b.py to pick scripts; --perturb union|drop
# EXPECTED (baseline 1936d5ca, box B9, Linux, strace 6.8): seams=31 exact on the
#   default script set: 9 under tests/doc_claims.py (child tests/plan_view.py),
#   22 under tests/deployment_shape.py (its own -P --driver child); --perturb union -> 0 (to_zero); --perturb drop -> 32 (up);
#   null control tests/guard_pins.py (no repo child process) -> 0.
# MACHINE: box B9 cloud container, 4 cores, CPython 3.14.0rc2.
# BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
#
# The read path is the one strace -y prints for the RETURNED descriptor
# (absolute), not the argument: a child whose cwd is a scratch copy opens
# relative paths.
# Why strace and not the audit hook: tests/closure.py records a PYTHON script
# in-process under sys.addaudithook (closure._exec_record); a child process's
# reads never reach that hook, only the child's argv does.  The node lane
# already records under `strace -f`; this harness records the Python scripts
# the same way and asks select() what a change to each unseen file would run.
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import closure  # noqa: E402  production instrument under test

DEFAULT = ["tests/doc_claims.py", "tests/deployment_shape.py",
           "tests/typing_ruler.py", "tests/structure.py", "tests/guard_pins.py"]
# One PID per line: `1234 openat(AT_FDCWD, "path", O_RDONLY|O_CLOEXEC) = 3`
_LINE = re.compile(r"^(\d+)\s+(.*)$")
_RET = re.compile(r"= \d+<([^>]+)>\s*$")
_CLONE = re.compile(r"^(?:clone3?|v?fork)\(.*\)\s+= (\d+)")
_EXEC = re.compile(r'execve\("([^"]+)", \[(.*?)\]')


def trace(script: str, tmp: Path) -> tuple[int, dict[str, set[str]], float]:
    """{repo file: {reader argv0...}} opened for reading by script's process tree."""
    out = tmp / (Path(script).name + ".strace")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "tests" / "hastub")
    env["HPO_PLANDATA"] = str(tmp / "plan.json")
    t0 = time.monotonic()
    proc = subprocess.run(
        ["strace", "-f", "-qq", "-y", "-s", "512", "-e", "trace=openat,execve,clone,clone3,fork,vfork", "-o", str(out),
         sys.executable, script], cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wall = time.monotonic() - t0
    who: dict[str, str] = {}          # pid -> argv0 argv1 of its last exec
    parent: dict[str, str] = {}       # tid/pid -> the pid that cloned it
    pending: dict[str, str] = {}      # pid -> text of an <unfinished ...> call
    reads: dict[str, set[str]] = {}

    def label(pid: str) -> str:
        seen = set()
        while pid not in who and pid in parent and pid not in seen:
            seen.add(pid)
            pid = parent[pid]     # a thread or an un-exec'd fork reads as its creator
        return who.get(pid, "<script>")

    for line in out.read_text(errors="replace").splitlines():
        m = _LINE.match(line)
        if not m:
            continue
        pid, rest = m.groups()
        if rest.endswith("<unfinished ...>"):
            pending[pid] = rest
            continue
        if rest.startswith("<... "):
            rest = pending.pop(pid, "").replace("<unfinished ...>", "") + rest
        c = _CLONE.search(rest)
        if c:
            parent[c.group(1)] = pid
            continue
        e = _EXEC.search(rest)
        if e:
            if re.search(r"\)\s+= 0\s*$", rest):
                args = re.findall(r'"([^"]*)"', e.group(2))
                who[pid] = " ".join(Path(a).name if i == 0 else a
                                    for i, a in enumerate(args[:2]))
            continue
        o = closure._STRACE_OPEN.search(rest)
        if not o or "= -1" in rest:
            continue
        # `-y` decorates the returned descriptor with its ABSOLUTE path; a
        # child running in a scratch copy of the tree opens RELATIVE paths
        # that would otherwise resolve against this checkout.
        ret = _RET.search(rest)
        path = ret.group(1) if ret else o.group(1)
        if "O_WRONLY" in rest or "O_CREAT" in rest or "O_RDWR" in rest:
            continue          # a write is not a dependency
        r = closure._rel(path)
        if r and closure._is_real_file(r):
            reads.setdefault(r, set()).add(label(pid))
    return proc.returncode, reads, wall


def seams_for(script: str, reads: dict[str, set[str]], table: dict) -> list[dict]:
    mine = set(table["closures"].get(script, []))
    out = []
    for f in sorted(reads):
        if closure.unit_of(f) in mine:
            continue
        plan = closure.select([f])
        if plan["mode"] == "scoped" and script not in plan["run"]:
            out.append({"script": script, "file": f,
                        "readers": sorted(reads[f])})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts", default=",".join(DEFAULT))
    ap.add_argument("--perturb", choices=["none", "union", "drop"], default="none",
                    help="union: fold every traced read into the script's closure "
                         "(the fix shape; seams must go to zero). drop: remove one "
                         "recorded, script-only file from a clean script's closure "
                         "(a one-line re-introduction; seams must go up by one).")
    a = ap.parse_args()
    scripts = [s for s in a.scripts.split(",") if s]
    tmp = Path(tempfile.mkdtemp(prefix="d14s5-i2-"))
    committed = json.loads(closure.CLOSURES.read_text())
    table = json.loads(json.dumps(committed))
    traced = {}
    t_cpu0 = time.process_time(); t_thr0 = time.thread_time()
    for s in scripts:
        rc, reads, wall = trace(s, tmp)
        traced[s] = reads
        print(f"traced {s}: rc={rc} reads={len(reads)} wall={wall:.1f}s", flush=True)
    if a.perturb == "union":
        for s in scripts:
            table["closures"][s] = sorted(set(table["closures"][s])
                                          | {closure.unit_of(f) for f in traced[s]})
    elif a.perturb == "drop":
        # The first file guard_pins.py reads that sits in its closure AND in
        # another script's closure: dropping it from guard_pins.py's closure
        # leaves select() scoped (the file is still "known") and skipping
        # guard_pins.py -- one re-introduced seam.
        s = "tests/guard_pins.py"
        if s not in scripts:
            scripts.append(s); traced[s] = trace(s, tmp)[1]
        others = {x for k, v in table["closures"].items() if k != s for x in v}
        f = next(x for x in sorted(traced[s])
                 if x in table["closures"][s] and x in others)
        print(f"drop: {f} from {s}'s closure")
        table["closures"][s] = [x for x in table["closures"][s] if x != f]
    patched = tmp / "closures.json"
    patched.write_text(json.dumps(table))
    closure.CLOSURES = patched          # select() reads the module global
    seams = []
    for s in scripts:
        mine = seams_for(s, traced[s], table)
        seams += mine
        print(f"RESULT seams[{s}]={len(mine)} count")
    for x in seams:
        print(f"  SEAM {x['script']} reads {x['file']} via {', '.join(x['readers'])}"
              f"{' [INERT]' if closure.is_inert(x['file']) else ''}")
    print(f"RESULT seams={len(seams)} count")
    def family(x) -> str:
        root = [r for r in x["readers"]
                if r == "<script>" or (r.startswith(Path(sys.executable).name)
                                       and x["script"] in r)]
        if root:
            return "in-process"
        heads = {r.split()[0] for r in x["readers"]}
        if heads <= {"git"}:
            return "git"
        if any(h.startswith("python") for h in heads):
            return "python-child"
        if "node" in heads:
            return "node-child"
        return "other-child"
    fam = {}
    for x in seams:
        x["family"] = family(x)
        fam[x["family"]] = fam.get(x["family"], 0) + 1
    by_child = sum(v for k, v in fam.items() if k != "in-process")
    print(f"RESULT seams_child_process={by_child} count")
    for k in ("in-process", "python-child", "node-child", "git", "other-child"):
        print(f"RESULT seams_by_reader[{k}]={fam.get(k, 0)} count")
        pm = sum(1 for x in seams if x["family"] == k and not closure.is_inert(x["file"]))
        print(f"RESULT seams_by_reader_measured_file[{k}]={pm} count")
    inert = sum(1 for x in seams if closure.is_inert(x["file"]))
    print(f"RESULT seams_on_INERT_files={inert} count")
    print(f"RESULT seams_on_measured_files={len(seams) - inert} count")
    cpu = time.process_time() - t_cpu0
    thr = time.thread_time() - t_thr0
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in Path("/proc/vmstat").read_text().splitlines()
              if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
