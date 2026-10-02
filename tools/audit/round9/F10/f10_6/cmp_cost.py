#!/usr/bin/env python3
"""F10.6 pricing: what CMP_BOUND would cost once it joins the ratchet.

    python3 tools/audit/round9/F10/f10_6/cmp_cost.py FROM TO

Stock: the CMP_BOUND sites `mutation_table.py --list` reports at the working
tree, how many the ledger leaves unpinned, and an independent AST count of
ordering operators (one-line and multi-line) as its control. Burden: for each
first-parent merge in FROM..TO, the sites a merge adds by content -- the
multiset (file, kind, old, new) at M minus at M^1, the per-site ratchet's own
identity plus `new`, so a chain's two bounds count twice -- for CMP_BOUND and,
as the scale it is read against, GUARD_OFF, which the ratchet already charges.
Null controls: a merge against itself adds 0, and a one-line `if x < 1:`
added to a synthetic module adds exactly one site of each kind.
"""
import ast
import statistics
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

KINDS = ("CMP_BOUND", "GUARD_OFF")


def git(*a: str) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True,
                          check=True).stdout


def sites_of(rel: str, src: str, tmp: Path) -> Counter:
    p = tmp / "m.py"
    p.write_text(src)
    return Counter((rel, m["kind"], m["old"].strip(), m["new"].strip())
                   for m in mt.candidates(p, mt.LISTED) if m["kind"] in KINDS)


def at(ref: str, rel: str) -> str:
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], capture_output=True,
                       text=True)
    return r.stdout if r.returncode == 0 else ""


def added(a: str, b: str, tmp: Path) -> Counter:
    files = [f for f in git("diff", "--name-only", "--no-renames", a, b, "--",
                            mt.PKG).split() if f.endswith(".py")]
    out: Counter = Counter()
    for f in files:
        new = sites_of(f, at(b, f), tmp) - sites_of(f, at(a, f), tmp)
        out.update(k[1] for k in new.elements())
    return out


def main() -> int:
    lo, hi = sys.argv[1:3]
    rows = mt.listed_sites("CMP_BOUND", mt.load_budgets())
    ops = one = 0
    for p in sorted(mt.PRODUCTION.rglob("*.py")):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.Compare):
                k = sum(isinstance(o, (ast.Lt, ast.LtE, ast.Gt, ast.GtE))
                        for o in n.ops)
                ops += k
                one += k if n.end_lineno == n.lineno else 0
    print(f"RESULT stock_sites={len(rows)} unpinned="
          f"{sum(u for _, u in rows)} anchors="
          f"{len({s['anchor'] for s, _ in rows})} files="
          f"{len({s['file'] for s, _ in rows})}")
    print(f"RESULT control ordering_ops_all={ops} one_line={one} "
          f"multi_line={ops - one}")
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        null = added(hi, hi, tmp)
        syn = (sites_of("s.py", "def f(x):\n    if x < 1:\n        return 1\n"
                        "    return 0\n", tmp)
               - sites_of("s.py", "def f(x):\n    return 0\n", tmp))
        print(f"RESULT null self_diff={dict(null)} "
              f"perturbation={dict(Counter(k[1] for k in syn.elements()))}")
        merges = git("rev-list", "--first-parent", "--merges", "--reverse",
                     f"{lo}..{hi}").split()
        per = {k: [] for k in KINDS}
        for m in merges:
            got = added(f"{m}^1", m, tmp)
            for k in KINDS:
                per[k].append(got.get(k, 0))
    for k in KINDS:
        v = per[k]
        print(f"RESULT burden {k}: merges={len(v)} adding={sum(1 for x in v if x)}"
              f" total={sum(v)} mean={statistics.mean(v):.2f} "
              f"median={statistics.median(v)} max={max(v)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
