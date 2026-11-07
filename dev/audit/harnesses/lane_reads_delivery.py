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

A fresh clone's files are as new as its index, so git rehashes every tracked
file, rows included, the first time a command refreshes it. `--refresh-index`
refreshes it before the steps run, which separates that rehash from a step
that reads a row.

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


def run_lane(lane: str, out: Path, refresh: bool = False) -> dict:
    tmp = out / f"{lane}{'.refreshed' if refresh else ''}.tmp"
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
    if refresh:  # the null control: a stat-clean index, so git rehashes no file
        time.sleep(2)
        subprocess.run(["git", "-C", str(clone), "update-index", "-q", "--really-refresh"], check=True)
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
    # One strace per step, so each hit is that step's. The full log runs to
    # gigabytes on the self-test lane, so strace pipes it through awk. Awk
    # keeps the lines naming dev/programme and every successful exec, the
    # latter so a hit can be put to the command that made it. It also counts
    # every line, so a step that traced nothing reads as 0, not clean.
    (tmp / "filter.awk").write_text(
        '/dev\\/programme/ || (/execve\\(/ && / = 0$/) || /(clone3?|v?fork)[(]|<[.][.][.] (clone3?|v?fork) resumed>/ '
        '{ print > (out ".hits") }\n'
        'END { print NR > (out ".n") }\n')
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
        sink = f"|awk -v out={tmp}/step{i} -f {tmp}/filter.awk"
        script.append(f"echo '::step {i}'; ( cd {clone}/{wd} && [ -f {rt}/env ] && set -a && . {rt}/env; "
                      f"set +a; cd {clone}/{wd}; exec /usr/bin/strace -f -qq -y -s 4096 "
                      f"-e trace=%file,execve,getdents64,clone,clone3,fork,vfork -o '{sink}' "
                      f"env {exports} bash --noprofile --norc -eo pipefail {f} ) "
                      f"> {tmp}/step{i}.log 2>&1; echo \"::exit {i} $?\"")
        listed.append({"step": name, "ran": True, "i": i})
    (tmp / "lane.sh").write_text("\n".join(script) + "\n")
    t0 = time.time()
    p = subprocess.run(["bash", str(tmp / "lane.sh")], env=env, capture_output=True, text=True)
    exits = dict(re.findall(r"::exit (\d+) (\d+)", p.stdout))
    for e in listed:
        if not e["ran"]:
            continue
        e["exit"] = int(exits.get(str(e["i"]), -1))
        base = tmp / f"step{e['i']}"
        n = Path(f"{base}.n")
        e["trace_lines"] = int(n.read_text().strip() or 0) if n.exists() else 0
        hits = Path(f"{base}.hits")
        e.update(scan(hits, clone) if hits.exists() else scan_empty())
    return {"lane": lane, "steps": listed, "seconds": round(time.time() - t0)}


KINDS = ("open", "list", "exec-names", "stat", "exec-excludes")
READS = ("open", "list", "exec-names")  # what counts as reading a row


def scan_empty() -> dict:
    return {"kinds": {k: 0 for k in KINDS}, "by_command": {}, "examples": {}}


def _argv(line: str) -> list[str]:
    m = re.search(r'execve\("[^"]*", \[(.*?)\](?:, 0x| /\*)', line)
    return re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)) if m else []


def scan(hits: Path, clone: Path) -> dict:
    """Each traced syscall touching the clone's delivery rows, by kind and by
    the command that made it: the process's last exec, first four argv
    words, inherited across a fork or thread until the child execs. `open` is an open of a row or of the directory; `list` a getdents64
    on it; `exec-names` an exec whose argv names dev/programme other than as
    an exclusion (`:!`, `:(exclude)`); `exec-excludes` one naming it only so;
    `stat` a stat-family call, which reads no content. A path under another
    root (a self-test's fixture repository) is not the clone's and not counted."""
    under = f"{clone}/{ROW}"
    rel = re.compile(r'(AT_FDCWD<' + re.escape(str(clone)) + r'[^>]*>|^\d+\s+\w+\()"?(\./)?' + re.escape(ROW))
    lines = hits.read_text(errors="replace").splitlines()
    fork = re.compile(r"(?:\b(?:clone3?|v?fork)\(.*|<\.\.\. (?:clone3?|v?fork) resumed>.*)\)\s+=\s+(\d+)$")
    # Two passes: strace may print a child's first syscalls before its
    # parent's clone returns, so the fork edges and execs are collected first.
    parent: dict[str, str] = {}
    execs: dict[str, list[tuple[int, str]]] = {}
    for n, line in enumerate(lines):
        pid = line.split(None, 1)[0]
        m = fork.search(line)
        if m:
            parent.setdefault(m.group(1), pid)
        elif "execve(" in line and re.search(r"\)\s+=\s+0$", line):
            execs.setdefault(pid, []).append((n, " ".join(
                a.rsplit("/", 1)[-1] if j == 0 else a.replace(str(clone), "<clone>")
                for j, a in enumerate(_argv(line)[:4]))[:160]))

    def command(pid: str, n: int, depth: int = 0) -> str:
        """`pid`'s last exec at line n, else its parent's (a child or thread
        runs its parent's command until it execs)."""
        done = [c for k, c in execs.get(pid, ()) if k <= n]
        if done:
            return done[-1]
        return command(parent[pid], n, depth + 1) if pid in parent and depth < 64 else "?"

    out = scan_empty()
    for n, line in enumerate(lines):
        pid = line.split(None, 1)[0]
        if fork.search(line) or (re.search(r"\b(clone3?|v?fork)\(", line) and "dev/programme" not in line):
            continue
        if "execve(" in line and re.search(r"\)\s+=\s+0$", line):
            named = [a for a in _argv(line) if "dev/programme" in a]
            if not named:
                continue
            kind = "exec-excludes" if all(a.startswith((":!", ":(exclude)")) for a in named) else "exec-names"
        elif under not in line and not rel.search(line):
            continue
        elif "getdents64(" in line:
            kind = "list"
        elif re.search(r"\b(open|openat|openat2|creat)\(", line):
            kind = "open"
        else:
            kind = "stat"
        out["kinds"][kind] += 1
        c = command(pid, n)
        out["by_command"].setdefault(c, {}).setdefault(kind, 0)
        out["by_command"][c][kind] += 1
        out["examples"].setdefault(kind, line[:400])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lanes", default="control," + ",".join(LANES))
    ap.add_argument("--out", required=True)
    ap.add_argument("--refresh-index", action="store_true",
                    help="refresh the clone's index first: separates git's own rehash of a fresh checkout "
                         "(every tracked file, rows included) from a step that reads a row")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for lane in a.lanes.split(","):
        r = run_lane(lane, out, a.refresh_index)
        lane = lane + (" (index refreshed)" if a.refresh_index else "")
        (out / f"{lane.split()[0]}{'.refreshed' if a.refresh_index else ''}.json").write_text(json.dumps(r, indent=1))
        ran = [s for s in r["steps"] if s["ran"]]
        bad = [s["step"] for s in ran if s["exit"] != 0]
        readers = [s for s in ran if any(s["kinds"][k] for k in READS)]
        print(f"lane {lane}: {len(ran)} run step(s), {len(r['steps']) - len(ran)} uses: step(s) listed, "
              f"{len(bad)} exited non-zero, {sum(s['trace_lines'] for s in ran)} trace lines, "
              f"{len(readers)} step(s) read a row, {r['seconds']} s")
        for s in ran:
            if s["exit"] != 0 or s["trace_lines"] == 0 or s in readers:
                k = " ".join(f"{x}={s['kinds'][x]}" for x in KINDS if s["kinds"][x])
                print(f"  [{s['i']}] exit={s['exit']} lines={s['trace_lines']} {k or 'no row syscall'} :: {s['step']}")
                for c, v in s["by_command"].items():
                    if any(v.get(x) for x in READS):
                        print(f"      by {c}: {v}")
        if lane.startswith("control"):
            print(f"RESULT control_hits={sum(s['kinds'][k] for s in ran for k in READS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
