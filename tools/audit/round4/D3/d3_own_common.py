#!/usr/bin/env python3
"""Shared runner for the round-4 D3 verifier's own harnesses (d3_own_S*.py).

Not itself a harness: no RESULT lines of its own beyond pass-through helpers.

Contract bits implemented here for every d3_own_* harness:
- thread pins (before any numpy import anywhere in-process or in drivers),
- mutations applied ONLY in the scratch worktree ../audit-r4-verify-D3-1-scratch,
  restored in `finally` and verified by SHA-256,
- drivers run from the scratch tree root with PYTHONPATH=tests/hastub and a
  private HPO_PLANDATA under a temp root,
- RESULT thread_factor / load1 / swapins printed by the caller at the end.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import contextlib
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

try:  # stream progress when redirected to a log
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

HERE = Path(__file__).resolve().parent
OWN_ROOT = HERE.parents[3]                    # the verifier's worktree root
SCRATCH = OWN_ROOT.parent / "audit-r4-verify-D3-1-scratch"
CACHE = HERE / "d3_own_base_cache.json"
FAILED_RE = re.compile(r"^\s*(\d+) of (\d+) .*FAILED\s*$", re.M)
PY = sys.executable


_ensured = False


def ensure_scratch() -> Path:
    """The scratch worktree exists, creating it from OWN_ROOT@HEAD if not.

    Mutations never touch the verifier's own worktree; the scratch tree is a
    detached worktree at the same commit, so both arms run the same tree.
    """
    global _ensured
    if _ensured or SCRATCH.exists():
        _ensured = True
        return SCRATCH
    rc, out, _ = sh(["git", "worktree", "add", "--detach", str(SCRATCH),
                     "HEAD"], cwd=OWN_ROOT, timeout=120)
    assert rc == 0, f"could not create scratch worktree: {out}"
    _ensured = True
    return SCRATCH


def load1() -> float:
    return os.getloadavg()[0]


def heavy_neighbours() -> int:
    """Count concurrent stress.py / run.sh processes (README resource rule)."""
    p = subprocess.run(["ps", "auxww"], capture_output=True, text=True)
    return sum(
        1 for line in p.stdout.splitlines()
        if re.search(r"[s]tress\.py|[t]ests/run\.sh", line)
    )


def swapins() -> int:
    try:
        p = subprocess.run(["sysctl", "-n", "vm.swapins"],
                           capture_output=True, text=True)
        return int(p.stdout.strip() or 0)
    except Exception:
        return 0


_T0_PROC = time.process_time()
_T0_THR = time.thread_time()


def thread_factor() -> float:
    """Whole-process CPU/thread ratio; >1.05 would void a timing RESULT."""
    thr = (time.thread_time() - _T0_THR) or 1e-9
    pro = (time.process_time() - _T0_PROC) or 1e-9
    return round(pro / thr, 3)


def driver_env() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub"
    tmp = Path("/tmp/d3r4-verify-own")
    tmp.mkdir(parents=True, exist_ok=True)
    env["HPO_PLANDATA"] = str(tmp / "plandata.json")
    return env


def sh(cmd: list, cwd: Path, timeout: float = 2400.0):
    started = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                           timeout=timeout, env=driver_env())
        out = p.stdout + p.stderr
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", 124
    return rc, out, round(time.monotonic() - started, 1)


def run_driver(script: str) -> dict:
    ensure_scratch()
    rc, out, secs = sh([PY, script], cwd=SCRATCH)
    hits = FAILED_RE.findall(out)
    return {"rc": rc, "failed": int(hits[-1][0]) if hits else 0,
            "seconds": secs}


def _cache_load() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {"runs": {}}


def head_sha() -> str:
    rc, out, _ = sh(["git", "rev-parse", "HEAD"], cwd=SCRATCH, timeout=30)
    return out.strip()


def baseline(script: str) -> dict:
    """The PASSING arm, run by this session's harness in the scratch tree.

    Cached per (tree SHA, script, script sha256) so sibling harnesses on the
    same tree do not each re-pay features.py; a cache hit is still a run this
    session executed itself on this exact tree.
    """
    key_src = (SCRATCH / script).read_bytes()
    key = f"{head_sha()}:{script}:{hashlib.sha256(key_src).hexdigest()[:12]}"
    cache = _cache_load()
    hit = cache["runs"].get(key)
    if hit and hit.get("rc") == 0:
        print(f"  [baseline cache hit] {script} rc={hit['rc']} "
              f"failed={hit['failed']} {hit['seconds']}s")
        return hit
    rec = run_driver(script)
    print(f"  [baseline arm] {script} rc={rec['rc']} failed={rec['failed']} "
          f"{rec['seconds']}s")
    if rec["rc"] != 0:
        print(f"  !! baseline arm NOT green: {script} rc={rec['rc']} "
              f"failed={rec['failed']} — kill rule void for this script")
    cache["runs"][key] = rec
    CACHE.write_text(json.dumps(cache, indent=1) + "\n")
    return rec


@contextlib.contextmanager
def mutant(rel: str, line_no: int, old: str, new: str):
    """Apply a one-line mutation in the SCRATCH tree only; restore after.

    `old`/`new` are compared/applied on the STRIPPED text; the original
    line's indentation is preserved on the replacement.
    """
    path = SCRATCH / rel
    original = path.read_text()
    orig_hash = hashlib.sha256(original.encode()).hexdigest()
    lines = original.splitlines(True)
    got = lines[line_no - 1].rstrip("\n")
    assert got.strip() == old.strip(), (
        f"{rel}:{line_no} is {got!r}, expected {old!r}")
    indent = got[: len(got) - len(got.lstrip())]
    nl = "\n" if lines[line_no - 1].endswith("\n") else ""
    lines[line_no - 1] = indent + new.strip() + nl
    path.write_text("".join(lines))
    try:
        yield path
    finally:
        path.write_text(original)
        back = hashlib.sha256(path.read_text().encode()).hexdigest()
        assert back == orig_hash, f"FAILED TO RESTORE {rel}"


def probe(code: str, label: str) -> dict:
    """Run a python -c probe INSIDE the scratch tree (under any mutation)."""
    ensure_scratch()
    rc, out, secs = sh([PY, "-c", code], cwd=SCRATCH, timeout=600)
    if rc != 0:
        print(f"  [probe {label}] rc={rc}\n{out[-2000:]}")
        return {"rc": rc, "value": None, "seconds": secs}
    val = json.loads(out.strip().splitlines()[-1])
    return {"rc": rc, "value": val, "seconds": secs}


def arms(rel: str, line_no: int, old: str, new: str, scripts: list,
         finding: str, probes: dict | None = None):
    """Both arms of the verifier contract: killed = fails WITH the mutant AND
    passes WITHOUT it. Probes run inside the mutation window."""
    killed_by = None
    per_script = {}
    for script in scripts:
        base = baseline(script)
        if base["rc"] != 0:
            per_script[script] = {"base": base, "mut": None,
                                  "note": "baseline not green; arms void"}
            continue
        with mutant(rel, line_no, old, new):
            mut = run_driver(script)
        print(f"  [mutant arm] {script} rc={mut['rc']} failed={mut['failed']} "
              f"{mut['seconds']}s")
        per_script[script] = {"base": base, "mut": mut}
        if mut["rc"] != base["rc"] or mut["failed"] > base["failed"]:
            killed_by = killed_by or script
    probe_out = {}
    if probes:
        probe_out["base"] = probe(probes["code"], "base")
        with mutant(rel, line_no, old, new):
            probe_out["mut"] = probe(probes["code"], "mut")
    return {"killed_by": killed_by, "scripts": per_script, "probes": probe_out}
