#!/usr/bin/env python3
"""#3885 item 2: the pull request's seeded case sample -- its mutation proof, null controls and cost.

    python3 dev/audit/harnesses/ci3885_sampling.py mutants
    python3 dev/audit/harnesses/ci3885_sampling.py routes
    python3 dev/audit/harnesses/ci3885_sampling.py stable SCRIPT SEED FILES
    python3 dev/audit/harnesses/ci3885_sampling.py count LOG SCRIPT
    python3 dev/audit/harnesses/ci3885_sampling.py census N [--ref origin/main]

`mutants` edits one predicate of tests/case_select.py's plan at a time, in
place, runs `tests/case_select.py --self-test` and prints the checks that fail;
the file is restored after each. A site not found exactly once is refused,
never counted. `routes` drives tests/entities.py's own run.sh routing pin
(`_csel_routes`, sourced from the script) against tests/run.sh, then against
run.sh with the event test removed, and prints both verdicts: the mutant must
fail. `stable` plans SCRIPT twice with SEED over the paths listed in FILES and
compares the printed lines byte for byte. `count` counts a run log's `-- `
section headings and compares them with the spans `case_select.split` cuts
from SCRIPT and with the log's own `CASES:` line, the count a whole run is
proved by. `census` replays the last N first-parent merges of REF: each
merge's first-parent diff, planned for both scripts against this tree's table
with the seed `<k>-<merge sha>` and the closures committed at the merge's
first parent as select's base, printed as the mode, its reason, and the
recorded seconds share of the spans the plan runs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    for d in p.parents:
        if (d / "tests" / "case_select.py").is_file():
            return d
    raise SystemExit("ci3885_sampling: no repository root above this file")


ROOT = _repo_root()
CS = ROOT / "tests" / "case_select.py"
sys.path.insert(0, str(ROOT / "tests"))

MUTANTS = (
    ("draw keyed on the ordinal", 'if int(hashlib.sha256(f"{seed}\\0{i}".encode())',
     'if int(hashlib.sha256(f"{seed}\\0{sorted(ids).index(i)}".encode())'),
    ("rule (i) diff removed", 'elif units & set(t["files"]):', "elif False:"),
    ("rule (ii) edited removed", 'if t is None or t["hash"] != s.hash:\n            rules[s.id] = "edited"',
     'if False:\n            rules[s.id] = "edited"'),
    ("rule (iii) forward removed", "for i in _closure_star(set(rules), feeds) - set(rules):", "for i in set():"),
    ("rule (v) needed removed", "for i in _closure_star(set(rules), needs) - set(rules):", "for i in set():"),
    ("draw over the diff's spans too", "for i in draw([i for i in ids if i not in rules], seed, fraction):",
     "for i in draw(ids, seed, fraction):"),
    ("header-files arm removed", 'hit = sorted(units & set(e["header"]) - {rel})', "hit = []"),
    ("closures.json exclusion removed", "(closure.is_gate_file(f) and f != closure.CLOSURES_REL)",
     "closure.is_gate_file(f)"),
    ("script's own file kept in the header arm", 'hit = sorted(units & set(e["header"]) - {rel})',
     'hit = sorted(units & set(e["header"]))'),
    ("closure-not-recorded arm removed", "stray = sorted(units & set(closures.get(rel, ())) - recorded)",
     "stray = []"),
    ("gate/runner arm removed", "if gate:\n        return full", "if False:\n        return full"),
    ("header-hash arm removed", 'if e["header_hash"] != header_hash:', "if False:"),
    ("seed shape removed", "if not seed or not _SEED_SHAPE.match(seed):", "if not seed:"),
    ("script-scope arm removed", 'if scope.get("mode") != "scoped":', "if False:"),
    ("repeated-title arm removed", "if len(group) > 1 and moved:", "if False:"),
)


def mutants() -> int:
    orig = CS.read_text()
    bad = 0
    try:
        for name, a, b in MUTANTS:
            if orig.count(a) != 1:
                print(f"REFUSED {name}: site found {orig.count(a)} times")
                bad += 1
                continue
            CS.write_text(orig.replace(a, b))
            r = subprocess.run([sys.executable, str(CS), "--self-test"], capture_output=True, text=True, cwd=ROOT)
            fails = [ln.strip()[5:].split("  [")[0] for ln in r.stdout.splitlines() if ln.startswith("  FAIL")]
            print(f"{'KILLED ' if r.returncode and fails else 'SURVIVED'} {name}: rc={r.returncode}, "
                  f"{len(fails)} failing: {fails[:2]}")
            bad += not (r.returncode and fails)
    finally:
        CS.write_text(orig)
    print(f"MUTANTS: {len(MUTANTS) - bad} of {len(MUTANTS)} killed")
    return 1 if bad else 0


def _pin_source() -> str:
    src = (ROOT / "tests" / "entities.py").read_text()
    i = src.index("def _gl_stub_tree")
    stub = src[i:src.index("\n\n\n", i)]
    j = src.index("def _csel_routes")
    k = src.index("\nR.check(", j)
    k = src.index("\n)\n", k) + 3
    return stub + "\n\n\n" + src[j:k]


def _routes_verdict() -> tuple[bool, str]:
    import closure as _closure  # noqa: F401 - the pin's own globals
    import re as _re  # noqa: F401
    import os as _os  # noqa: F401
    import subprocess as _subprocess  # noqa: F401
    import tempfile as _tempfile  # noqa: F401
    seen: list[tuple[bool, str]] = []

    class R:
        @staticmethod
        def check(name, ok, detail=""):
            seen.append((bool(ok), str(detail)))

    exec(_pin_source(), {**locals(), "Path": Path, "sys": sys, "R": R})
    return seen[-1]


def routes() -> int:
    run_sh = ROOT / "tests" / "run.sh"
    orig = run_sh.read_text()
    site = '[ "${HPO_CI_EVENT:-}" = pull_request ] && [ "$GATE_SCOPE" = auto ]'
    if orig.count(site) != 1:
        print(f"REFUSED: the routing predicate is found {orig.count(site)} times in tests/run.sh")
        return 1
    ok, detail = _routes_verdict()
    print(f"ROUTES at the tree: {'PASS' if ok else 'FAIL'} ({detail[:200]})")
    try:
        run_sh.write_text(orig.replace(site, '[ "$GATE_SCOPE" = auto ]'))
        mok, mdetail = _routes_verdict()
    finally:
        run_sh.write_text(orig)
    print(f"ROUTES with the event test removed: {'PASS' if mok else 'FAIL'} ({mdetail[:300]})")
    return 0 if ok and not mok else 1


def stable(script: str, seed: str, files: str) -> int:
    outs = [subprocess.run([sys.executable, str(CS), "plan", script, "--seed", seed, "--files", files],
                           capture_output=True, cwd=ROOT).stdout for _ in range(2)]
    print(outs[0].decode().splitlines()[0])
    same = outs[0] == outs[1]
    print(f"STABLE: {'byte-identical' if same else 'DIFFERENT'} over {len(outs[0])} bytes, two runs")
    return 0 if same and outs[0] else 1


def count(log: str, script: str) -> int:
    import case_select as C
    text = Path(log).read_text(errors="replace")
    heads = sum(1 for ln in text.splitlines() if ln.startswith("-- "))
    n = len(C.split((ROOT / script).read_text())[2])
    m = re.search(r"^CASES: (FULL|SCOPED) \S+ -- (\d+) of (\d+) spans", text, re.M)
    print(f"COUNT {script}: {heads} section headings in {log}; split cuts {n}; CASES line "
          f"{m.group(0) if m else 'absent'}")
    return 0


def census(n: int, ref: str) -> int:
    import case_select as C
    import closure
    table = C.load()
    merges = subprocess.run(["git", "rev-list", "--first-parent", "--merges", f"-{n}", ref],
                            capture_output=True, text=True, cwd=ROOT).stdout.split()
    tally = {}
    for k, m in enumerate(merges, 1):
        files = closure.changed_between(f"{m}^1", m, dots="..")
        subj = subprocess.run(["git", "log", "-1", "--format=%s", m], capture_output=True, text=True,
                              cwd=ROOT).stdout.strip()[:60]
        cells = []
        shown = subprocess.run(["git", "show", f"{m}^1:{closure.CLOSURES_REL}"], capture_output=True,
                               text=True, cwd=ROOT)
        base = json.loads(shown.stdout)["closures"] if shown.returncode == 0 else None
        scope = closure.select(files, base)
        for s in C.SCRIPTS:
            if s not in scope.get("run", []):
                cells.append(f"{Path(s).name}: not selected")
                tally[(s, "not selected")] = tally.get((s, "not selected"), 0) + 1
                continue
            p = C.plan(str(ROOT / s), files, f"{k}-{m}", scope=scope)
            e = C.entry(table, s)
            secs = {i: v["seconds"] for i, v in e["spans"].items()}
            total = sum(secs.values())
            if p["mode"] == "full":
                cells.append(f"{Path(s).name}: FULL ({p['reason'][:70]})")
                tally[(s, "full")] = tally.get((s, "full"), 0) + 1
            else:
                share = sum(secs.get(i, 0.0) for i in p["rules"]) / total
                cells.append(f"{Path(s).name}: SCOPED {len(p['rules'])}/{p['n']} spans, {share:.2f} of seconds")
                tally[(s, "scoped")] = tally.get((s, "scoped"), 0) + 1
        print(f"{m[:10]} {subj}\n    " + "\n    ".join(cells))
    print("CENSUS: " + ", ".join(f"{Path(s).name} {mode} {c}" for (s, mode), c in sorted(tally.items())))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("mutants")
    sub.add_parser("routes")
    st = sub.add_parser("stable")
    st.add_argument("script")
    st.add_argument("seed")
    st.add_argument("files")
    co = sub.add_parser("count")
    co.add_argument("log")
    co.add_argument("script")
    ce = sub.add_parser("census")
    ce.add_argument("n", type=int)
    ce.add_argument("--ref", default="origin/main")
    a = ap.parse_args(argv)
    os.chdir(ROOT)
    if a.cmd == "mutants":
        return mutants()
    if a.cmd == "routes":
        return routes()
    if a.cmd == "stable":
        return stable(a.script, a.seed, a.files)
    if a.cmd == "count":
        return count(a.log, a.script)
    return census(a.n, a.ref)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
