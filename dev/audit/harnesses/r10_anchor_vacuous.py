"""Which `killed_by: tests/entities.py` pins are vacuous (R10 mutation-anchor).

    python3 dev/audit/harnesses/r10_anchor_vacuous.py              # census only
    python3 dev/audit/harnesses/r10_anchor_vacuous.py --drive [--all] [--jobs N] [--out F]
    python3 dev/audit/harnesses/r10_anchor_vacuous.py --drive --anchor KEY [--anchor KEY ...]
                                      [--equivalent | --new TEXT] [--no-hide]
    python3 dev/audit/harnesses/r10_anchor_vacuous.py --strike OUT.json --at SHA

The census enumerates every row of the ledger whose `killed_by` is
tests/entities.py (the rule: `load_budgets()["killed_by"]`, entry
`killed_by == "tests/entities.py"`), and for each says whether a line under
its anchor carries a SECOND ledger row (another anchor pinned to the same
file and line, either map). Printed as two sets, both by anchor.

`--drive` re-drives each selected pin's sites -- every inventory site under
the anchor, each with its own mutant -- through the real tests/entities.py in
a worktree of HEAD (`mutation_table.clone_tree`), with the rows the mutant
invalidates hidden (`mutation_table.invalidated_rows`, the fix). The pin's
kill SURVIVES when every site under it is still killed by the mutation
table's own rule (`mutation_table.killed` against a baseline run in the same
tree); it is VACUOUS when some site lives. Selected: the second-pin set, or
every pin with --all. A line `PIN <anchor> SURVIVES|VACUOUS ...` per pin, the
two sets, and the failing checks of each kill, go to stdout and --out.

The controls: `--equivalent` replaces each site's mutant with its own line
plus a trailing comment, and `--new TEXT` with TEXT (one anchor) -- rewrites
no check can tell apart, which must LIVE; `--no-hide` drives without the fix
(no row hidden), the tree as the instrument saw it before, where the same
rewrite reads killed.

`--strike OUT --at SHA` applies a --drive measurement: each VACUOUS pin's
`killed_by` row becomes a `survivor_triage` row with verdict `gap` and the
reason, under the same anchor and `old` pin (`mutation_table.write_budgets`),
so the site keeps a disposition and the unpinned ratchet does not move; a pin
whose row changed since the measurement is left alone.

Run `--drive` under `env -u BASH_ENV`, the finder's recipe: an inherited
BASH_ENV turns two workflow-step checks of tests/entities.py red in the
worktree, the baseline is then red, and the harness refuses to read a verdict.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import sys
import tempfile
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

JUDGE = "tests/entities.py"


def census():
    budgets = mt.load_budgets()
    disp = mt.dispositions(budgets)
    by_anchor: dict[str, list[dict]] = {}
    for s in mt.inventory():
        by_anchor.setdefault(s["anchor"], []).append(s)
    on_line: dict[tuple[str, int], set[str]] = {}
    for a, sites in by_anchor.items():
        if mt.disposition_matches(disp.get(a), sites[0]):
            for s in sites:
                on_line.setdefault((s["file"], s["line"]), set()).add(a)
    pins = sorted(a for a, e in budgets["killed_by"].items()
                  if isinstance(e, dict) and e.get("killed_by") == JUDGE)
    second = sorted(a for a in pins if any(
        len(on_line[(s["file"], s["line"])]) > 1 for s in by_anchor.get(a, [])))
    return budgets, by_anchor, pins, second


def drive(budgets, by_anchor, anchors, jobs, timeout, new=None, hide=True):
    work = Path(tempfile.mkdtemp(prefix="anchor-vacuous-"))
    rows_at = mt.ledger_dir().relative_to(mt.ROOT)
    trees = [mt.clone_tree(work / f"w{i}") for i in range(jobs)]
    try:
        bases = list(cf.ThreadPoolExecutor(jobs).map(
            lambda t: mt.run_script(JUDGE, t, timeout), trees))
        for b in bases:
            print(f"baseline {JUDGE}: rc={b.rc} failed={b.failed} {b.seconds:.0f}s"
                  + (f" {mt.failed_checks(b)}" if b.rc else ""), flush=True)
        if any(b.rc for b in bases):
            raise SystemExit("baseline red: no verdict can be read")
        tasks = [(a, s) for a in anchors for s in by_anchor.get(a, [])]
        free = list(range(jobs))

        def one(task):
            a, s = task
            w = free.pop()
            try:
                t = trees[w]
                path = t / s["file"]
                original = path.read_text()
                lines = original.splitlines(True)
                lines[s["line"] - 1] = (new(s) if new else s["new"]) + "\n"
                after = "".join(lines)
                hidden = (mt.invalidated_rows(budgets, s["file"], original, after)
                          if hide else [])
                rows = {p: p.read_text() for p in
                        (t / rows_at / r for r in hidden) if p.is_file()}
                path.write_text(after)
                for p in rows:
                    p.unlink()
                try:
                    run = mt.run_script(JUDGE, t, timeout)
                finally:
                    path.write_text(original)
                    for p, text in rows.items():
                        p.write_text(text)
                hit = mt.killed(JUDGE, run, bases[w])
                print(f"  site {a} line {s['line']} {s['kind']}: "
                      f"{'killed' if hit else 'LIVES'} rc={run.rc} "
                      f"failed={run.failed} hidden={len(hidden)}", flush=True)
                return a, s, hit, mt.failed_checks(run) if hit else [], len(hidden)
            finally:
                free.append(w)

        with cf.ThreadPoolExecutor(jobs) as ex:
            got = list(ex.map(one, tasks))
    finally:
        for t in trees:
            mt.drop_tree(t)
    out: dict[str, dict] = {}
    for a, s, hit, checks, n_hid in got:
        o = out.setdefault(a, {"sites": 0, "killed": 0, "checks": [], "hidden": 0})
        o["sites"] += 1
        o["killed"] += hit
        o["checks"] += checks
        o["hidden"] = max(o["hidden"], n_hid)
    return out


def strike(out: str, at: str) -> int:
    got = json.loads(Path(out).read_text())
    budgets = mt.load_budgets()
    kb, tri = budgets["killed_by"], budgets.setdefault("survivor_triage", {})
    n = 0
    for a in got["vacuous"]:
        entry = kb.get(a)
        if not isinstance(entry, dict) or entry.get("killed_by") != JUDGE:
            print(f"  left alone (row changed): {a}")
            continue
        d = got["detail"][a]
        tri[a] = {"old": entry["old"], "verdict": "gap", "reason": (
            f"R10 mutation-anchor: the `killed_by: {JUDGE}` pin was vacuous. "
            f"Re-driven at {at} by dev/audit/harnesses/r10_anchor_vacuous.py "
            f"with the {d['hidden']} ledger row(s) the mutant itself makes "
            f"stale hidden from its tree, {d['killed']} of {d['sites']} "
            f"site(s) were killed by {JUDGE}: the recorded kill was a check "
            f"refusing a ledger row the mutant made stale (the --anchor "
            f"self-test, or the survivor_triage staleness check), not one "
            f"that saw the mutation. Was: {entry.get('reason', '')} Not re-driven here "
            f"against the other drivers in its closure, so a gap until one "
            f"is shown to kill it.")}
        del kb[a]
        n += 1
    mt.write_budgets(budgets)
    print(f"STRUCK {n} vacuous pin(s) into survivor_triage gap rows")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--drive", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--anchor", action="append", default=[])
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--equivalent", action="store_true")
    ap.add_argument("--new")
    ap.add_argument("--no-hide", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--strike", metavar="OUT")
    ap.add_argument("--at", default="")
    args = ap.parse_args(argv)
    if args.strike:
        return strike(args.strike, args.at)
    budgets, by_anchor, pins, second = census()
    print(f"CENSUS: {len(pins)} killed_by {JUDGE} pin(s); {len(second)} on a "
          f"line carrying a second ledger row")
    for a in second:
        print(f"  SECOND-PIN {a}")
    if not args.drive:
        return 0
    chosen = args.anchor or (pins if args.all else second)
    new = ((lambda s: args.new) if args.new is not None else
           (lambda s: s["old"] + "  # equivalent") if args.equivalent else None)
    res = drive(budgets, by_anchor, chosen, args.jobs, args.timeout, new,
                not args.no_hide)
    survives = sorted(a for a, o in res.items() if o["killed"] == o["sites"])
    vacuous = sorted(a for a, o in res.items() if o["killed"] < o["sites"])
    for a in sorted(res):
        o = res[a]
        print(f"PIN {a} {'SURVIVES' if a in survives else 'VACUOUS'} "
              f"{o['killed']}/{o['sites']} site(s) killed; hidden rows "
              f"{o['hidden']}; checks {sorted(set(o['checks']))}")
    print(f"DRIVEN {len(res)} pin(s): {len(survives)} kill(s) survive the fix, "
          f"{len(vacuous)} vacuous")
    if args.out:
        Path(args.out).write_text(json.dumps(
            {"driven": sorted(res), "survives": survives, "vacuous": vacuous,
             "second_pin": second, "pins": pins, "detail": res}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
