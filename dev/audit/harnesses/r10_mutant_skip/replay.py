#!/usr/bin/env python3
"""The mutant/driver reach replay (#1930 fold (e), r10-mutant-skip).

Traces every driver the nightly's net can hand a production site
(`tests/mutation_table.py`'s DEFAULT_SCRIPTS whose closure reaches one), each
on its own unmutated worker tree exactly as the lane drives its baseline, with
the lane's own tracer (`tests/mutation_table.py`, the reach section). Then, for every inventory site and every
driver whose closure reaches the site's file, one row:

    reached   the traced run executed the site's line
    never     a clean traced run never executed it -- the only skippable state
              (`never_reaches`, what the lane's `reach_skip` reads)
    run       no clean row: the driver's run is refused for a skip
              (`reach_problems`), read the file as text, or the line has
              no instruction of its own

and replays the ledger: every `killed_by` row matching a current site must
name a killer whose row is not `never`. A killer that never executed the line
it killed is a counterexample to the skip.

    python3 dev/audit/harnesses/r10_mutant_skip/replay.py --jobs 3 \
        --out dev/audit/harnesses/r10_mutant_skip

writes `reach.json` (per driver: rc, seconds, problems, executed lines) and
`matrix.tsv` (one row per site, one state per driver: `write_matrix`), and prints the census.
`--from reach.json` rebuilds the matrix and census without re-tracing.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import threading
from collections import Counter
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))

import mutation_table as mt  # noqa: E402


def drivers_in_net() -> list[str]:
    closures = mt.load_closures()
    allow = mt.DEFAULT_SCRIPTS.split(",")
    return [s for s in allow
            if any(f.startswith(mt.PKG) for f in closures.get(s, ()))]


def trace(script: str, tree: Path, ref: str | None) -> dict:
    """One driver's traced unmutated run, as the lane invokes it; its reach
    with the run's rc and seconds. Unlike the lane's `traced_baseline`, a red
    run is kept, so the census shows it."""
    args, env = mt.drive_spec(script, ref)
    with tempfile.TemporaryDirectory(prefix="reach-") as d:
        hook = mt.hook_env(Path(d))
        run = mt.run_script(script, tree, 4 * 3600, args, {
            **env, **hook, "PYTHONPATH": mt.traced_pythonpath(
                hook, env.get("PYTHONPATH", "tests/hastub"))})
        reach = mt.collect(Path(d))
    reach["rc"] = run.rc
    reach["seconds"] = round(run.seconds, 1)
    reach["problems"] = mt.reach_problems(reach)
    return reach


def trace_all(drivers: list[str], jobs: int, ref: str | None) -> dict:
    work = Path(tempfile.mkdtemp(prefix="reach-replay-"))
    trees = [mt.clone_tree(work / f"w{i}") for i in range(jobs)]
    out: dict[str, dict] = {}
    shared = [s for s in drivers if s not in mt.EXCLUSIVE]
    lock = threading.Lock()

    def one(tree: Path, s: str) -> None:
        out[s] = reach = trace(s, tree, ref)
        print(f"  traced {s}: rc={reach['rc']} {reach['seconds']}s "
              f"lines={sum(map(len, reach['hits'].values()))} "
              f"problems={reach['problems'] or 'none'}\n", end="", flush=True)

    def work_on(w: int) -> None:
        while True:
            with lock:
                if not shared:
                    return
                s = shared.pop(0)
            one(trees[w], s)

    try:
        mt._share(jobs, work_on)
        for s in (s for s in drivers if s in mt.EXCLUSIVE):
            one(trees[0], s)
    finally:
        for t in trees:
            mt.drop_tree(t)
    return out


def matrix(reach: dict) -> tuple[list[tuple], dict]:
    closures = mt.load_closures()
    drivers = sorted(reach)
    rows = []
    executable: dict[str, set[int]] = {}
    for site in mt.inventory():
        rel = site["file"]
        if rel not in executable:
            executable[rel] = mt.executable_lines(ROOT / rel)
        for s in mt.drivers_for(rel, closures, drivers):
            r = reach[s]
            if mt.never_reaches(r, rel, site["line"], executable[rel]):
                state = "never"
            elif (not mt.reach_problems(r) and rel not in r["reads"]
                  and site["line"] in executable[rel]):
                state = "reached"
            else:
                state = "run"
            rows.append((site["anchor"], site["line"], site["kind"], s, state,
                         site))
    return rows, executable


STATE_CODE = {"reached": "r", "never": "n", "run": "x"}


def write_matrix(path: Path, rows: list[tuple], drivers: list[str],
                 head: str | None) -> None:
    """One line per site: anchor, line, kind, then one state code per driver
    in header order -- `r` reached, `n` never, `x` must run, `.` the driver's
    closure does not reach the file (no pair)."""
    col = {s: i for i, s in enumerate(drivers)}
    by_site: dict[tuple, list[str]] = {}
    for anchor, line, kind, s, state, _ in rows:
        codes = by_site.setdefault((anchor, line, kind), ["."] * len(drivers))
        codes[col[s]] = STATE_CODE[state]
    with path.open("w") as fh:
        fh.write(f"# head {head}; states r=reached n=never x=run .=no pair\n")
        fh.write("anchor\tline\tkind\t" + " ".join(drivers) + "\n")
        for (anchor, line, kind), codes in sorted(by_site.items()):
            fh.write(f"{anchor}\t{line}\t{kind}\t{''.join(codes)}\n")


def read_matrix(path: Path) -> dict[tuple[str, str], str]:
    """{(anchor, driver): state} back out of `write_matrix`'s file."""
    lines = path.read_text().splitlines()
    drivers = lines[1].split("\t")[3].split(" ")
    names = {v: k for k, v in STATE_CODE.items()}
    out = {}
    for ln in lines[2:]:
        anchor, _line, _kind, codes = ln.split("\t")
        for s, c in zip(drivers, codes):
            if c != ".":
                out[(anchor, s)] = names[c]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--from", dest="src", default=None)
    ap.add_argument("--ref", default="HEAD^1",
                    help="the nightly's comparison ref (gate_ref('full'))")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    head = mt._rev(ROOT, "HEAD")
    if a.src:
        traced = json.loads(Path(a.src).read_text())
        reach, head = traced["drivers"], traced["head"]
    else:
        reach = trace_all(drivers_in_net(), a.jobs, a.ref)
        (out / "reach.json").write_text(json.dumps(
            {"head": head, "ref": a.ref, "drivers": reach},
            indent=1, sort_keys=True) + "\n")
    rows, _ = matrix(reach)
    write_matrix(out / "matrix.tsv", rows, sorted(reach), head)

    kb = mt.load_budgets().get("killed_by", {})
    state_of = {(r[0], r[3], r[5]["old"]): r[4] for r in rows}
    sites = {r[0]: r[5] for r in rows}
    replay = Counter()
    counter = []
    for anchor, site in sorted(sites.items()):
        entry = kb.get(anchor)
        if not (mt.disposition_matches(entry, site) and "killed_by" in entry):
            continue
        st = state_of.get((anchor, entry["killed_by"], site["old"]), "no-row")
        replay[st] += 1
        if st == "never":
            counter.append((anchor, entry["killed_by"]))

    by_state = Counter(r[4] for r in rows)
    print(f"\nHEAD {head}")
    print(f"PAIRS {len(rows)} over {len(sites)} anchored sites and "
          f"{len(reach)} traced drivers: " + ", ".join(
              f"{k} {by_state[k]}" for k in ("reached", "never", "run")))
    for s in sorted(reach):
        r = reach[s]
        n = Counter(row[4] for row in rows if row[3] == s)
        print(f"  {s}: rc={r['rc']} {r['seconds']}s never={n['never']} "
              f"reached={n['reached']} run={n['run']}"
              + (f"  [{'; '.join(r['problems'])}]" if r['problems'] else "")
              + (f"  [reads {len(r['reads'])} production file(s) as text]"
                 if r["reads"] else ""))
    # A survivor's sweep is every driver it is handed (`drive_pool`), so the
    # inventory's summed sweep at the recorded solo seconds bounds what the
    # skip can save; a killed mutant stops earlier and saves less.
    secs = {s: float(v.get("seconds", 0.0))
            for s, v in mt.recorded_entries().items()}
    full = sum(secs.get(r[3], 0.0) for r in rows)
    kept = sum(secs.get(r[3], 0.0) for r in rows if r[4] != "never")
    print(f"SURVIVOR SWEEP over the inventory at recorded solo seconds: "
          f"{full:.0f} s every pair, {kept:.0f} s without the never rows "
          f"({100 * (full - kept) / full:.1f}% less)")
    print(f"LEDGER REPLAY {sum(replay.values())} killed_by rows matching a "
          f"current site: " + ", ".join(f"{k} {v}" for k, v in
                                        sorted(replay.items())))
    for anchor, s in counter:
        print(f"  COUNTEREXAMPLE {anchor}: killed by {s}, which never "
              f"executed its line")
    print("LEDGER REPLAY: " + ("no killer is a never row" if not counter
                               else f"{len(counter)} killer(s) are never rows"))
    return 1 if counter else 0


if __name__ == "__main__":
    sys.exit(main())
