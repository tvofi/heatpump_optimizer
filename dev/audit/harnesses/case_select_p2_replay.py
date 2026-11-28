#!/usr/bin/env python3
"""R11-CI-CASE-SELECT P2 evidence 5: the plan against known mutants from tests/mutation_ledger/.

    python3 dev/audit/harnesses/case_select_p2_replay.py plans --seed S --n N
    python3 dev/audit/harnesses/case_select_p2_replay.py run --seed S --n N --script tests/features.py \
        --limit K --baseline LOG

The population is every `tests/mutation_ledger/killed_by/` pin whose `killed_by`
is a case script, counted at run time. `plans` draws a seeded sample of N,
stratified by production file (round-robin over the files, each file's pins
in seeded order), and plans each pin with its mutated file as the only diff,
at sample fraction 0, against `tests/case_closures.json` at this checkout. It
prints the plan's size and seconds and the null plan's: the spans whose
`files` miss the mutated file and that no such span reaches forward, plus
what they need.

`run` takes the first K drawn pins of one script and, for each, regenerates
the mutant (`tests/mutation_table.py candidates`, matched by ledger anchor) in
THIS checkout's file. It runs the plan span-wise, stopping at the first FAIL
whose name is not among the baseline's FAIL names (`--baseline`: an
unmutated full run's log of the same script, which for entities.py prints
fixture FAIL lines). Then it runs the null plan the same way. A plan with no
new FAIL is then run whole (`python3 <script>`): a full kill there is a
DEFECT, no kill there marks the pin STALE at this head. It restores the file
after each pin; run it in a worktree of its own.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
import case_select as C  # noqa: E402


def pins() -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(ROOT / "tests/mutation_ledger/killed_by/**/*.json"), recursive=True)):
        d = json.loads(Path(f).read_text())
        if d.get("killed_by") in C.SCRIPTS:
            d["file"] = d["anchor"].split(":", 1)[0]
            out.append(d)
    return out


def draw(population: list[dict], seed: str, n: int) -> list[dict]:
    rnd = random.Random(seed)
    by: dict[str, list[dict]] = {}
    for p in population:
        by.setdefault(p["file"], []).append(p)
    for v in by.values():
        rnd.shuffle(v)
    order = sorted(by)
    rnd.shuffle(order)
    out: list[dict] = []
    while len(out) < n and any(by.values()):
        for f in order:
            if by[f] and len(out) < n:
                out.append(by[f].pop())
    return out


def plans_for(script: str, f: str, table: dict) -> tuple[set[str], set[str], float, float, float]:
    """(plan, null plan, plan seconds, null seconds, all seconds) with `f` the only diff."""
    source = (ROOT / script).read_text()
    blob = table["scripts"][script]["blob"]
    ids, line, _ = C.plan(script, source, [f], table, base_blob=blob, head_blob=blob,
                          event="pull_request", seed="", fraction=0.0)
    e = C.entry(table, script)
    spans = C.split(source)[2]
    allids = {s.id for s in spans}
    if ids is None:
        raise SystemExit(f"replay: {line}")
    # The null: rule (i) off for f, i.e. the spans the plan left out, with their producers.
    import ast
    header = C.split(source)[0]
    needs = C.static_needs(spans, header, C._aliases(ast.parse(source)))
    for s in spans:
        needs[s.id] |= set(e["spans"].get(s.id, {}).get("needs", ())) & allids
    miss = allids - ids
    null = miss | C._closure(miss, needs)
    sec = lambda xs: sum(e["spans"][i]["seconds"] for i in xs if i in e["spans"])  # noqa: E731
    return ids, null, sec(ids), sec(null), sec(allids)


def cmd_plans(a) -> int:
    table = C.load()
    pop = pins()
    print(f"REPLAY population {len(pop)} pins naming a case script; seed {a.seed}; n {a.n}")
    for p in draw(pop, a.seed, a.n):
        ids, null, s1, s0, st = plans_for(p["killed_by"], p["file"], table)
        print(f"PIN {p['killed_by']} {p['anchor']} plan {len(ids)} spans {s1:.0f}s null {len(null)} spans "
              f"{s0:.0f}s of {st:.0f}s")
    return 0


def mutant(p: dict) -> dict | None:
    import mutation_table as M
    path = ROOT / p["file"]
    src = path.read_text()
    for m in M.anchor_sites(src, list(M.candidates(path, src=src))):
        if m["anchor"] == p["anchor"]:
            return m
    return None


def _fail_names(text: str) -> set[str]:
    return {ln.strip()[5:].split("  [")[0].strip() for ln in text.splitlines() if ln.startswith("  FAIL ")}


def run_plan(script: str, ids: set[str] | None, known: set[str]) -> tuple[bool, str]:
    """(a FAIL not in `known` appeared, its name), stopping the run at the first one."""
    with tempfile.NamedTemporaryFile("w", suffix=".plan", delete=False) as fh:
        fh.write("\n".join(sorted(ids or ())) + "\n")
    cmd = ([sys.executable, str(ROOT / "tests/case_select.py"), "run", script, "--plan", fh.name]
           if ids is not None else [sys.executable, script])
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tests/hastub"))
    pr = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    hit = ""
    for ln in pr.stdout:
        if ln.startswith("  FAIL "):
            name = ln.strip()[5:].split("  [")[0].strip()
            if name not in known:
                hit = name
                pr.kill()
                break
    pr.wait()
    os.unlink(fh.name)
    return bool(hit), hit


def cmd_run(a) -> int:
    table = C.load()
    known = _fail_names(Path(a.baseline).read_text()) if a.baseline else set()
    chosen = [p for p in draw(pins(), a.seed, a.n) if p["killed_by"] == a.script][: a.limit]
    tally = {"KILLED": 0, "DEFECT": 0, "STALE": 0, "UNAPPLIED": 0, "null-killed": 0}
    for p in chosen:
        m = mutant(p)
        if m is None:
            tally["UNAPPLIED"] += 1
            print(f"PIN {p['anchor']} UNAPPLIED (no candidate carries this anchor at this head)", flush=True)
            continue
        path = ROOT / p["file"]
        orig = path.read_text()
        lines = orig.splitlines(keepends=True)
        lines[m["line"] - 1] = m["new"] + ("\n" if not m["new"].endswith("\n") else "")
        ids, null, s1, s0, st = plans_for(a.script, p["file"], table)
        try:
            path.write_text("".join(lines))
            killed, name = run_plan(a.script, ids, known)
            nk, nname = run_plan(a.script, null, known)
            verdict = "KILLED"
            if not killed:
                fk, _ = run_plan(a.script, None, known)
                verdict = "DEFECT" if fk else "STALE"
        finally:
            path.write_text(orig)
        tally[verdict] += 1
        tally["null-killed"] += nk
        print(f"PIN {p['anchor']} {verdict} plan {len(ids)} ({name[:70]!r}) null {len(null)} "
              f"{'KILLS' if nk else 'passes'} ({nname[:50]!r})", flush=True)
    print("RESULT " + " ".join(f"{k}={v}" for k, v in tally.items()))
    return 1 if tally["DEFECT"] else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("plans", "run"))
    ap.add_argument("--seed", default="r11-case-select-p2")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--script", default="tests/features.py")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--baseline", default="")
    args = ap.parse_args()
    sys.exit(cmd_plans(args) if args.cmd == "plans" else cmd_run(args))
