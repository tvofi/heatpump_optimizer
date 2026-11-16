#!/usr/bin/env python3
"""D11-s1 round 11, step D11.M1: the mechanism inventory over every cell.

Metric (one line): every file `check_scopes.py --seat D11-s1` prints, classified
by role in the refusal machinery (where it runs, what controls it), with the
count of CI-wired refusal instruments that carry no control a seat can run.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/inventory.py
Writes dev/audit/rounds/round11/D11/s1/inventory.tsv (one row per cell) and prints
RESULT lines. Expected at the baseline: cells=1387 (exact); examined=cells.

Enumerator (the universe, one cell per line):
    python3 tools/audit/check_scopes.py --repo . --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 --seat D11-s1
Columns: path, role, runs_in (ci-required | ci-other | hook | seat | none),
control (self-test | acceptance | driven | n/a | NONE), refuses (exit-nonzero path seen).
`control` is a SCREEN: `driven` means another control-bearing file names the
basename on a non-comment line, which over-credits (a message string counts);
every NONE row was read by hand (REPORT.md). The required-gate job set is
derived from ci.yml's `gate` needs closure (`pr-contract` and its needs) and
the reusable workflows those call.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
Instrumented symbol: tools/audit/check_scopes.py (the enumerator, executed) and
.github/workflows/ci.yml:jobs.gate.needs (parsed, the required context's closure).
Perturbation: add `"steps": ["M1"]` cells to another seat or drop the `rules_sync`
step from governance.yml policy-docs -> cells / ci_required_refusers move.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import re
import subprocess
import sys
import time

import yaml

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OUT = "dev/audit/rounds/round11/D11/s1/inventory.tsv"
c0, t0 = time.process_time(), time.thread_time()

cells = [l.split("\t")[2] for l in subprocess.run(
    ["python3", "tools/audit/check_scopes.py", "--repo", ".", "--ref", BASE, "--seat", "D11-s1"],
    capture_output=True, text=True, check=True).stdout.splitlines() if l.count("\t") >= 2]

# Old->new path moves (tests/layout.json), so a workflow's fallback spelling resolves.
lay = json.load(open("tests/layout.json"))
MOVES = [(e["old"], e["new"]) for e in lay.get("retired", []) + lay.get("lifted", [])
         if isinstance(e.get("old"), str) and isinstance(e.get("new"), str)]


def loc(p):
    if os.path.isfile(p):
        return p
    for o, n in MOVES:
        q = n + p[len(o):] if o.endswith("/") and p.startswith(o) else n if p == o else None
        if q and os.path.exists(q):
            return q
    return None


SCRIPT_RE = re.compile(r"(?:\.claude|tools|tests|dev)/[A-Za-z0-9_./-]+\.(?:py|mjs|js|sh)")


def scripts_in(obj):
    return {l for m in SCRIPT_RE.findall(json.dumps(obj)) if (l := loc(m))}


# The required closure: ci.yml's `gate` and every job it needs, transitively;
# a `uses: ./.github/workflows/x.yml` job brings all of x.yml's jobs.
ci = yaml.safe_load(open(".github/workflows/ci.yml"))
jobs = ci["jobs"]
need, seen = ["gate"], set()
while need:
    j = need.pop()
    if j in seen:
        continue
    seen.add(j)
    n = jobs[j].get("needs") or []
    need += [n] if isinstance(n, str) else list(n)
required = set()
for j in seen:
    required |= scripts_in(jobs[j])
    u = jobs[j].get("uses", "")
    if u.startswith("./.github/workflows/"):
        required |= scripts_in(yaml.safe_load(open(u[2:])))
other_ci = set()
for wf in os.listdir(".github/workflows"):
    other_ci |= scripts_in(yaml.safe_load(open(f".github/workflows/{wf}")))
other_ci -= required
hooks = scripts_in(json.load(open(".claude/settings.json")))

CODE = (".py", ".mjs", ".js", ".sh")
texts = {}
for c in cells:
    if c.endswith(CODE) and os.path.isfile(c):
        texts[c] = open(c, errors="replace").read()
for extra in ("tests/entities.py", "tests/mutation_table.py", "tools/pr/prepr.sh"):
    texts.setdefault(extra, open(extra, errors="replace").read())
ST = re.compile(r"self[-_ ]?test")
ACC = re.compile(r"assertAcceptance|FIXTURE ok|FIXTURE VACUOUS|acceptance\(")
has_st = {f for f, t in texts.items() if ST.search(t)}
has_acc = {f for f, t in texts.items() if ACC.search(t)}
controllers = has_st | has_acc | {"tests/entities.py", "tests/mutation_table.py"}
COMMENT = re.compile(r"^\s*(#|//|\*|/\*)")
live_lines = {f: [l for l in texts[f].splitlines() if not COMMENT.match(l)] for f in controllers if f in texts}


def driven(f):
    b = os.path.basename(f)
    return any(g != f and any(b in l for l in ls) for g, ls in live_lines.items())


REFUSE = re.compile(r"sys\.exit\((?:1|2|main)|process\.exit\((?!0\))|exit [12]\b|exit \$|return 1\b|raise SystemExit")


def role(c):
    if c.startswith(".github/workflows/") or c.startswith(".github/actions/"):
        return "workflow"
    if c == ".claude/settings.json":
        return "hook-config"
    if c.startswith(".claude/hooks/"):
        return "hook"
    if c.startswith((".claude/rules/", ".cursor/rules/")):
        return "generated-rule"
    if c.startswith("dev/audit/rounds/"):
        return "round-evidence"
    if c.startswith("dev/audit/harnesses/"):
        return "harness"
    if "/fixtures/" in c:
        return "fixture"
    if c.endswith(CODE):
        return "instrument"
    if c.endswith(".md"):
        return "policy-or-doc"
    return "data"


rows, noread = [], []
for c in cells:
    r = role(c)
    runs = ("ci-required" if c in required else "ci-other" if c in other_ci else
            "hook" if c in hooks else "seat" if r == "instrument" else "none")
    if r in ("instrument", "hook", "harness") and c in texts:
        ctl = ("self-test" if c in has_st else "acceptance" if c in has_acc else
               "driven" if driven(c) else "NONE")
        refuses = "yes" if REFUSE.search(texts[c]) else "no"
    else:
        ctl, refuses = "n/a", "n/a"
    if runs == "ci-required" and ctl == "NONE" and r == "instrument":
        noread.append(c)
    rows.append((c, r, runs, ctl, refuses))

with open(OUT, "w") as f:
    f.write("path\trole\truns_in\tcontrol\trefuses\n")
    for row in rows:
        f.write("\t".join(row) + "\n")
by = {}
for _, r, runs, ctl, _ in rows:
    by[(r, runs, ctl)] = by.get((r, runs, ctl), 0) + 1
for k in sorted(by):
    print("  ", *k, by[k])
for c in noread:
    print("NO-CONTROL ci-required", c)
print(f"RESULT cells={len(cells)} files")
print(f"RESULT examined={len(rows)} files")
print(f"RESULT ci_required_scripts={len(required)} files")
print(f"RESULT ci_required_instruments_no_control={len(noread)} files")
c1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
