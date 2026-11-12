#!/usr/bin/env python3
"""R10-ARCH-DOCS (#2395): every evidence row of a pull-request body holds the text it quotes at the line it cites.

    python3 dev/audit/harnesses/r10_arch_docs_evidence.py BODY.md

THE RULE. An evidence row is a body line of the form `  - ` + backticked `path:line` + a space + the backticked
text. The row holds when that text is a substring of that line of that file in this checkout. A row whose text is
elsewhere in the file is still a miss, printed with the lines that do hold it: a moved citation is corrected in the
body, never matched loosely here. The check says nothing about whether the quoted line supports the sentence it is
filed under; that is the reader's judgement, and this only keeps the citation from drifting off its line.

Prints one `MISS` line per row that does not hold, then `RESULT rows=`, `RESULT hold=` and `RESULT miss=`. Exit 1 on
a miss or on a body with no row, 2 on a usage error.
"""
from __future__ import annotations

import re
import sys
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
ROW = re.compile(r"^  - `([^`:\n]+):(\d+)` (?:`` ?(.+?) ?``|`([^`\n]+)`)$", re.M)


def misses(body: str, root: Path) -> tuple[int, list[str]]:
    rows = ROW.findall(body)
    out = []
    for path, line, wide, plain in rows:
        text, f = wide or plain, root / path
        lines = f.read_text().splitlines() if f.is_file() else []
        if int(line) > len(lines) or text not in lines[int(line) - 1]:
            near = [i + 1 for i, got in enumerate(lines) if text in got][:4]
            out.append(f"MISS {path}:{line} {text!r} (the text is at {near or 'no line'})")
    return len(rows), out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.split("\n\n")[1].strip(), file=sys.stderr)
        return 2
    n, out = misses(Path(argv[1]).read_text(), ROOT)
    print("\n".join(out), end="\n" if out else "")
    print(f"RESULT rows={n}")
    print(f"RESULT hold={n - len(out)}")
    print(f"RESULT miss={len(out)}")
    return 1 if out or not n else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
