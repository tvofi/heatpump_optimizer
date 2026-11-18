#!/usr/bin/env python3
"""D3-s1 helper: find a driven mutant by key (or `file:line` / R10 id) and apply
or describe it in a tree.

  python3 r2/mutant.py find <selector>          -> key<TAB>sub<TAB>file<TAB>line<TAB>kind
  python3 r2/mutant.py apply <selector> <tree>  -> writes the one-line mutation
Selectors: a 16-hex result key, `file.py:LINE[:KIND]`, or an R10 id `C2:M27`.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RES = HERE / "state" / "results"
SUBS = ("pre", "c2", "c3c6", "complete")


def all_results():
    for sub in SUBS:
        d = RES / sub
        if d.exists():
            for p in sorted(d.glob("*.json")):
                yield p.stem, sub, json.loads(p.read_text())


def find(sel: str):
    for k, sub, r in all_results():
        m = r["mutant"]
        fn = m["file"].rsplit("/", 1)[-1]
        if sel == k:
            return k, sub, m
        if sel.startswith(("C2:", "C3C6:")):
            want = sel.split(":", 1)[1]
            if m.get("c2_id") == want or m.get("c3c6_id") == want or m["anchor"].endswith(" " + want):
                if sub in ("c2", "c3c6"):
                    return k, sub, m
            continue
        parts = sel.split(":")
        if len(parts) >= 2 and fn == parts[0] and str(m["line"]) == parts[1]:
            if len(parts) == 2 or m["kind"] == parts[2]:
                return k, sub, m
    raise SystemExit(f"no mutant matches {sel}")


def main() -> int:
    cmd, sel = sys.argv[1], sys.argv[2]
    k, sub, m = find(sel)
    if cmd == "find":
        print(f"{k}\t{sub}\t{m['file']}\t{m['line']}\t{m['kind']}")
        return 0
    tree = Path(sys.argv[3])
    path = tree / m["file"]
    lines = path.read_text().splitlines(True)
    assert lines[m["line"] - 1].rstrip("\n") == m["old"], (m, lines[m["line"] - 1])
    lines[m["line"] - 1] = m["new"] + "\n"
    path.write_text("".join(lines))
    print(f"{k}\t{m['file']}\t{m['line']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
