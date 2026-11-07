#!/usr/bin/env python3
"""R10-CI-OWN-DELIVERY-ROW step 1: does any lane the C7(a) idling skips read
dev/programme/delivery/ at the head?

The machinery lanes (tools/ci/prelude.py `machinery`) are the steps whose
`if:` (or whose job's `if:`) names `inputs.machinery` or `MACHINERY_IDLE`, in
.github/workflows/tests.yml and governance.yml. This driver reads those steps
off the workflow YAML of the tree it runs in, so it covers a step added later
without an edit here. It runs each lane's `run:` steps in order, in a fresh
`git clone` of HEAD, under one `strace -f -y`. Then it reports every syscall
naming a path under `<clone>/dev/programme/delivery/`, plus every exec whose
argv names `dev/programme`, so a `git show HEAD:<row>` counts as a read too.
`uses:` steps (checkout, setup-*, upload-artifact) are listed, not run.

The closures lane's recorder runs each script under its own strace, and
ptrace cannot nest. A PATH shim named `strace` therefore stands in for it:
the shim runs the command untraced and leaves an empty log. The outer trace
then sees every script and child the recorder would have traced.

The positive control is a planted step, `cat` of a row plus a `git show` of
another, run through the same tracer and scan. The scan must report all three reads (the `cat` exec, its open, the `git show` exec)
(`control` lane). Without that, a tracer that recorded nothing would read as a
clean result.

    python3 dev/audit/harnesses/lane_reads_delivery.py [--lanes a,b] --out DIR

Lanes: control, instrument-self-tests, env-matrix, arch-instrument, closures.
EXPECTED RESULT control_hits=3
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
LANES = {  # lane -> (workflow, job)
    "instrument-self-tests": ("governance.yml", "instrument-self-tests"),
    "env-matrix": ("governance.yml", "env-matrix"),
    "arch-instrument": ("tests.yml", "arch-instrument"),
    "closures": ("tests.yml", "closures"),
}
GATE = re.compile(r"inputs\.machinery|MACHINERY_IDLE")
EXPR = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")
ROW = "dev/programme/delivery"
SHIM = """#!/bin/sh
# stands in for tests/closure.py's strace: run the command untraced, empty log
while [ $# -gt 0 ]; do
  case "$1" in
    -o) : > "$2"; shift 2 ;;
    -e|-s|-p|-u) shift 2 ;;
    -*) shift ;;
    *) break ;;
  esac
done
exec "$@"
"""


def expr_value(e: str, tmp: str) -> str:
    """The value a pull_request run gives each expression these steps carry;
    the widest arm where there is a choice (full scope, full re-derive)."""
    table = {
        "secrets.GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN", ""),
        "runner.temp": tmp,
        "github.repository": "tvofi/heatpump_optimizer",
        "github.token": os.environ.get("GITHUB_TOKEN", ""),
        "needs.closure-scope.outputs.case": "full",
        "needs.closure-scope.outputs.scripts": "",
        "needs.closure-scope.outputs.case == 'scoped' && 'scoped' || 'full'": "full",
        "inputs.gate_scope == 'auto' && 'auto' || 'full'": "full",
        "inputs.base || 'main'": "main",
    }
    if e.startswith("github.event.pull_request.base.sha"):
        return "origin/main"
    if e not in table:
        raise SystemExit(f"lane_reads_delivery: no value for expression {e!r}; add it to expr_value")
    return table[e]


def on_pull_request(cond) -> bool:
    """False for an `if:` whose top level (parenthesised groups removed) pins
    another event: the C7(a) idling only ever skips a pull_request's steps."""
    top = str(cond or "")
    while re.search(r"\([^()]*\)", top):
        top = re.sub(r"\([^()]*\)", "", top)
    return not re.search(r"github\.event_name == '(?!pull_request')", top)


def steps(clone: Path, lane: str) -> list[dict]:
    wf, job = LANES[lane]
    j = yaml.safe_load((clone / ".github/workflows" / wf).read_text())["jobs"][job]
    whole = bool(GATE.search(str(j.get("if") or "")))
    return [s for s in j["steps"] if (whole or GATE.search(str(s.get("if") or ""))) and on_pull_request(s.get("if"))]


def run_lane(lane: str, out: Path) -> dict:
    tmp = out / f"{lane}.tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    clone = tmp / "ws"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(ROOT), str(clone)], check=True)
    url = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"],
                         capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "-C", str(clone), "remote", "set-url", "origin", url], check=True)
    main = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "origin/main"],
                          capture_output=True, text=True, check=True).stdout.strip()
    subprocess.run(["git", "-C", str(clone), "update-ref", "refs/remotes/origin/main", main], check=True)
    rt = tmp / "runner"
    rt.mkdir()
    env = dict(os.environ, CI="true", GITHUB_ACTIONS="true", RUNNER_TEMP=str(rt),
               GITHUB_WORKSPACE=str(clone), GITHUB_EVENT_NAME="pull_request",
               GITHUB_ENV=str(rt / "env"), GITHUB_OUTPUT=str(rt / "out"),
               GITHUB_STEP_SUMMARY=str(rt / "summary"), GITHUB_REPOSITORY="tvofi/heatpump_optimizer")
    if lane == "closures":
        shim = tmp / "shim"
        shim.mkdir()
        (shim / "strace").write_text(SHIM)
        (shim / "strace").chmod(0o755)
        env["PATH"] = f"{shim}:{env['PATH']}"
    if lane == "control":
        rows = sorted(p.name for p in (clone / ROW).iterdir())[:2]
        chosen = [{"name": "planted reader", "run": f"cat {ROW}/{rows[0]} >/dev/null\n"
                   f"git show HEAD:{ROW}/{rows[1]} >/dev/null\n"}]
    else:
        chosen = steps(clone, lane)
    script = ["#!/bin/bash", "set -o pipefail", f"cd {clone}"]
    listed = []
    for i, s in enumerate(chosen):
        name = s.get("name") or s.get("uses")
        if "run" not in s:
            listed.append({"step": name, "ran": False})
            continue
        senv = {k: EXPR.sub(lambda m: expr_value(m.group(1), str(rt)), str(v)) for k, v in (s.get("env") or {}).items()}
        body = EXPR.sub(lambda m: expr_value(m.group(1), str(rt)), s["run"])
        f = tmp / f"step{i}.sh"
        f.write_text(body)
        exports = " ".join(f"{k}={json.dumps(v)}" for k, v in senv.items())
        wd = s.get("working-directory", ".")
        script.append(f"echo '::step {i}'; ( cd {clone}/{wd} && [ -f {rt}/env ] && set -a && . {rt}/env; "
                      f"set +a; cd {clone}/{wd}; env {exports} bash --noprofile --norc -eo pipefail {f} ) "
                      f"> {tmp}/step{i}.log 2>&1; echo \"::exit {i} $?\"")
        listed.append({"step": name, "ran": True, "i": i})
    (tmp / "lane.sh").write_text("\n".join(script) + "\n")
    trace = out / f"{lane}.strace"
    t0 = time.time()
    p = subprocess.run(["/usr/bin/strace", "-f", "-qq", "-y", "-s", "4096", "-o", str(trace),
                        "-e", "trace=%file,execve,getdents64", "bash", str(tmp / "lane.sh")],
                       env=env, capture_output=True, text=True)
    exits = dict(re.findall(r"::exit (\d+) (\d+)", p.stdout))
    for e in listed:
        if e["ran"]:
            e["exit"] = int(exits.get(str(e["i"]), -1))
    hits = scan(trace, clone)
    return {"lane": lane, "steps": listed, "hits": hits, "seconds": round(time.time() - t0),
            "trace_lines": sum(1 for _ in trace.open(errors="replace"))}


def scan(trace: Path, clone: Path) -> list[str]:
    """Every traced syscall touching the clone's delivery rows, and every exec
    naming dev/programme in its argv. A relative path is resolved against
    nothing and kept, so an unresolved open cannot hide a read."""
    under = f"{clone}/{ROW}"
    hits = []
    for line in trace.open(errors="replace"):
        if ROW not in line and "dev/programme" not in line:
            continue
        if under in line:
            hits.append(line.rstrip())
        elif "execve(" in line and "dev/programme" in line.split("execve(", 1)[1]:
            hits.append(line.rstrip())
        elif re.search(r'"(\./)?' + re.escape(ROW), line):  # relative, unresolved
            hits.append(line.rstrip())
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lanes", default="control," + ",".join(LANES))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for lane in a.lanes.split(","):
        r = run_lane(lane, out)
        (out / f"{lane}.json").write_text(json.dumps(r, indent=1))
        ran = [s for s in r["steps"] if s["ran"]]
        bad = [s["step"] for s in ran if s["exit"] != 0]
        print(f"lane {lane}: {len(ran)} run step(s), {len(r['steps']) - len(ran)} uses: step(s) listed, "
              f"{len(bad)} exited non-zero, {r['trace_lines']} trace lines, {len(r['hits'])} row read(s), "
              f"{r['seconds']} s")
        for s in bad:
            print(f"  non-zero: {s}")
        for h in r["hits"][:20]:
            print(f"  HIT {h[:300]}")
        if lane == "control":
            print(f"RESULT control_hits={len(r['hits'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
