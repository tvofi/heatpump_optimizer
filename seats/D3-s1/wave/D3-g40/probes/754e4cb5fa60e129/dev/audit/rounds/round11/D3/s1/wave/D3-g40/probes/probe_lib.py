#!/usr/bin/env python3
# Shared two-arm driver for box D3-g40's probes (not itself a probe).
# Each arm is a temp directory holding `git archive <BASE> custom_components tests/hastub`, so a probe never
# imports from the gate's tree (which carries a mutant while a gate runs). The mutant arm replaces exactly one
# line of custom_components/heatpump_optimizer/tariff.py (old text asserted) -- the one-line mutant itself.
# The probe's snippet runs in a fresh `python3 -I`-free subprocess per arm with the thread pin and
# PYTHONPATH=<arm>:<arm>/tests/hastub, and prints one JSON object on its last stdout line.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import io, json, subprocess, sys, tarfile, tempfile
from pathlib import Path

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
TARIFF = "custom_components/heatpump_optimizer/tariff.py"


def _git_dir(start):
    here = Path(start).resolve()
    for cand in (here, *here.parents):
        if (cand / ".git").exists():
            return cand
    raise RuntimeError("no git checkout above " + str(start))


def _arm(root, line=None, old=None, new=None):
    blob = subprocess.run(["git", "-C", str(_git_dir(__file__)), "archive", BASE, "custom_components", "tests/hastub"],
                          check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(blob)) as tf:
        tf.extractall(root, filter="data")
    if line is not None:
        p = Path(root) / TARIFF
        lines = p.read_text().split("\n")
        got = lines[line - 1]
        assert got.strip() == old.strip(), f"line {line} is {got!r}, not {old!r}"
        indent = got[: len(got) - len(got.lstrip())]
        lines[line - 1] = indent + new.strip()
        p.write_text("\n".join(lines))
    return root


def run(snippet, root):
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{root}:{root}/tests/hastub"
    env["PYTHONWARNINGS"] = "default"
    r = subprocess.run([sys.executable, "-c", snippet], cwd=root, env=env, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        return {"error": r.stderr.strip().splitlines()[-1] if r.stderr.strip() else f"rc {r.returncode}"}
    return json.loads(r.stdout.strip().splitlines()[-1])


def two_arms(snippet, line, old, new):
    """(baseline result, mutant result) of the snippet."""
    with tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as m:
        return run(snippet, _arm(b)), run(snippet, _arm(m, line, old, new))


def machine_lines():
    try:
        load1 = open("/proc/loadavg").read().split()[0]
    except OSError:
        load1 = "nan"
    print(f"RESULT load1={load1}")
    print("RESULT thread_factor=1.0 ratio  (single-threaded pure-value probe; thread pin set)")
    try:
        swp = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except (OSError, IndexError):
        swp = "nan"
    print(f"RESULT swapins={swp}")
