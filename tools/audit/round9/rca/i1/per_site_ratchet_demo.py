#!/usr/bin/env python3
"""R9 RCA I1: the per-site ratchet, shown failing on each round-9 I1 seam
re-introduced beside a count trade, passing once the seam is pinned, and
silent on a null edit. Also replays ten real post-#1426 merges.

The candidate generator and the rule under test are this tree's
tests/mutation_table.py (the prototype); the "old" rule is the count
comparison `ratchet_refusal(base_count, unpinned)` alone, which is what
origin/main enforces.

Tree-level, one file per case: the other production files are identical at
both ends, so their sites cancel in the count and never appear in
`added_unpinned`.

  PYTHONPATH=tests/hastub python3 tools/audit/round9/rca/i1/per_site_ratchet_demo.py
  ... --history      also replay the ten merges (about ten minutes of CPU)
  ... --history-only only the replay
"""
from __future__ import annotations

import ast
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402  the prototype under test
import importlib.util, subprocess  # noqa: E402

def _main_module():
    """origin/main's mutation_table.py: the tool and rule enforced today."""
    src = subprocess.run(["git", "show", "origin/main:tests/mutation_table.py"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    f = Path(tempfile.mkdtemp(prefix="rca-i1-main-")) / "mutation_table_main.py"
    f.write_text(src.replace("ROOT = Path(__file__).resolve().parent.parent",
                             f"ROOT = Path({str(ROOT)!r})", 1))
    spec = importlib.util.spec_from_file_location("mutation_table_main", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.ROOT = mt.ROOT
    return mod
MAIN = _main_module()

PKG = mt.PKG
# (finding, file, line text at origin/main) -- the round-9 I1 production seams.
SEAMS = [
    ("D3-s1-91", "coordinator.py", "if last.tzinfo is None and now.tzinfo is not None:"),
    ("D3-s1-91", "coordinator.py", "if when.tzinfo is None and now.tzinfo is not None:"),
    ("D3-s2-01", "flow_lift.py", "if not np.isfinite(bias) or samples < 0:"),
    ("D3-s2-01", "tariff.py", "if not math.isfinite(tracker._window_factor):"),
    ("D3-s2-01", "price_model.py", "if not np.all(np.isfinite(parsed)):"),
    ("D3-s2-02", "price_model.py", "[max(0.0, float(v)) for v in s] for s in var"),
    ("D3-s3-01", "open_meteo.py", "if parsed.tzinfo is None:"),
    ("D3-s3-02", "dhw_draws.py", 'stats._open_kwh = max(0.0, float(data.get("open_kwh", 0.0)))'),
    ("D3-s3-03", "ledger.py", "if not (np.isfinite(kwh) and np.isfinite(sek)):"),
    ("D3-s3-04", "dhw_learning.py", "if self._external_heat_active():"),
    ("D3-s3-05", "legionella.py", "if switch.failed == self.write_failed_notice:"),
    # D14-s5-02's own shape, #1316's: a numpy clamp the old inventory never listed.
    ("D14-s5-02", "curve_learning.py", "np.clip("),
]


def sites_of(rel: str, src: str, tool=None) -> list[dict]:
    tool = tool or mt
    d = Path(tempfile.mkdtemp(prefix="rca-i1-"))
    p = d / Path(rel).name
    p.write_text(src)
    return mt.anchor_sites(src, [dict(m, file=rel) for m in tool.candidates(p)])


def main_verdict(rel: str, base_src: str, head_src: str, ledger: dict) -> tuple[int, int]:
    """(refuses, delta) under origin/main's own candidates and count rule."""
    b = MAIN.unpinned_sites(ledger, sites_of(rel, base_src, MAIN))
    h = MAIN.unpinned_sites(ledger, sites_of(rel, head_src, MAIN))
    return int(MAIN.ratchet_refusal(len(b), h) == 1), len(h) - len(b)


def verdicts(rel: str, base_src: str, head_src: str, ledger: dict,
             pin_head: set[str] = frozenset()) -> tuple[int, int, int, list]:
    """(count_rule_refuses, per_site_refuses, delta, added) for one file."""
    base = mt.unpinned_sites(ledger, sites_of(rel, base_src))
    head_sites = sites_of(rel, head_src)
    led = ledger
    if pin_head:
        led = dict(ledger, killed_by=dict(ledger.get("killed_by", {})))
        for s in head_sites:
            if s["anchor"] in pin_head:
                led["killed_by"][s["anchor"]] = dict(old=s["old"], killed_by="tests/features.py")
    head = mt.unpinned_sites(led, head_sites)
    old = mt.ratchet_refusal(len(base), head) == 1
    added = mt.added_unpinned(head, base)
    return int(old), int(old or bool(added)), len(head) - len(base), added


def drop_stmt(src: str, lineno: int) -> str:
    """The source with the statement starting at `lineno` removed whole
    (an `if` with its body), or `pass` left if it was a block's only one."""
    tree = ast.parse(src)
    lines = src.splitlines(True)
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            body = getattr(node, field, None)
            if not isinstance(body, list):
                continue
            for st in body:
                if st.lineno <= lineno <= st.end_lineno:
                    if st.lineno == lineno or not hasattr(st, "body"):
                        ind = lines[st.lineno - 1][: len(lines[st.lineno - 1]) - len(lines[st.lineno - 1].lstrip())]
                        repl = [ind + "pass\n"] if len(body) == 1 else []
                        return "".join(lines[: st.lineno - 1] + repl + lines[st.end_lineno:])
    raise ValueError(f"no statement at {lineno}")


def trade_line(src: str, rel: str, ledger: dict, avoid: int) -> int:
    """An unpinned no-else GUARD_OFF `if` elsewhere in the file carrying at
    least as many unpinned sites as the seam: the diff removes it, so the
    count nets to zero or below -- #1569's shape."""
    unp = mt.unpinned_sites(ledger, sites_of(rel, src))
    per_line: dict[int, int] = {}
    for s in unp:
        per_line[s["line"]] = per_line.get(s["line"], 0) + 1
    tree = ast.parse(src)
    ifs = [n for n in ast.walk(tree) if isinstance(n, ast.If) and not n.orelse
           and not (n.lineno <= avoid <= n.end_lineno) and not (avoid <= n.lineno <= avoid + 40)]
    ifs.sort(key=lambda n: -sum(per_line.get(ln, 0) for ln in range(n.lineno, n.end_lineno + 1)))
    return ifs[0].lineno


def main() -> int:
    t0 = time.process_time()
    if "--history-only" in sys.argv:
        history()
        print(f"RESULT cpu_seconds={time.process_time() - t0:.2f}")
        return 0
    ledger = mt.load_budgets()
    rows = []
    for fid, fname, needle in SEAMS:
        rel = PKG + fname
        head = (ROOT / rel).read_text()
        ln = next(i for i, l in enumerate(head.splitlines(), 1) if needle in l)
        # The PR re-introduces the seam and removes another unpinned guard.
        tl = trade_line(head, rel, ledger, ln)
        base = drop_stmt(head, ln)
        head_t = drop_stmt(head, tl)
        base_t = base  # the base still has the traded guard
        o, n, delta, added = verdicts(rel, base_t, head_t, ledger)
        mo, mdelta = main_verdict(rel, base_t, head_t, ledger)
        mno, _ = main_verdict(rel, base, head, ledger)
        seam_anchors = {s["anchor"] for s in added}
        # Fixed: the same PR, with every added site pinned (a killed_by row).
        fo, fn, _, fadded = verdicts(rel, base_t, head_t, ledger, pin_head=seam_anchors)
        # Null: the same file at both ends.
        no, nn, _, nadded = verdicts(rel, head, head, ledger)
        rows.append((fid, fname, ln, delta, o, n, len(added), fn, len(fadded), nn, len(nadded), mo, mno))
        print(f"  {fid:9} {fname}:{ln:<5} main[traded]={mo} main[untraded]={mno} | proto delta={delta:+d} count_rule_refuses={o} "
              f"per_site_refuses={n} added={len(added)} | pinned: refuses={fn} added={len(fadded)} "
              f"| null: refuses={nn} added={len(nadded)}")
    n_fail = sum(r[5] for r in rows)
    print(f"RESULT seams={len(rows)} count")
    print(f"RESULT main_refused_traded={sum(r[11] for r in rows)} count")
    print(f"RESULT main_refused_untraded={sum(r[12] for r in rows)} count")
    print(f"RESULT count_rule_refused={sum(r[4] for r in rows)} count")
    print(f"RESULT per_site_refused={n_fail} count")
    print(f"RESULT per_site_refused_after_pin={sum(r[7] for r in rows)} count")
    print(f"RESULT per_site_refused_null={sum(r[9] for r in rows)} count")
    print(f"RESULT cpu_seconds={time.process_time() - t0:.2f}")
    if "--history" in sys.argv:
        history()
    return 0


MERGES = ["6f58d5ee", "233a36bd", "266d795b", "c59672bc", "97dc04f2",
          "e0b83bbd", "ae3bb36a", "10bb8bb4", "66301a98", "c182e1cb"]


def at_ref(ref: str) -> list[dict]:
    listing = mt._git_or_none("ls-tree", "-r", ref, "--", PKG) or ""
    sites: list[dict] = []
    for row in listing.splitlines():
        meta, path = row.split("\t", 1)
        if path.endswith(".py"):
            src = mt._git_or_none("cat-file", "blob", meta.split()[2]) or ""
            sites.extend(sites_of(path, src))
    led, _ = mt.normalize(mt.load_budgets_at(ref), sites)
    return mt.unpinned_sites(led, sites)


def history() -> None:
    old_r = new_r = 0
    for m in MERGES:
        b, h = at_ref(m + "^1"), at_ref(m)
        o = mt.ratchet_refusal(len(b), h) == 1
        added = mt.added_unpinned(h, b)
        old_r += o
        new_r += o or bool(added)
        print(f"  HIST {m} base={len(b)} head={len(h)} delta={len(h) - len(b):+d} "
              f"count_rule_refuses={int(o)} added={len(added)}")
        for s in added:
            print(f"      + {s['file'].split('/')[-1]}:{s['line']} {s['kind']} {s['old'].strip()[:60]}")
    print(f"RESULT history_count_rule_refused={old_r} count")
    print(f"RESULT history_per_site_refused={new_r} count")


if __name__ == "__main__":
    sys.exit(main())
