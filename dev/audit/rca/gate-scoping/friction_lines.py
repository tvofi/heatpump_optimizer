"""Print every `## Friction` entry that cites gate-scoping, one per line, by PR.

    python3 -I friction_lines.py <dir of <PR>.md bodies>

The bodies are fetched with `gh api repos/<repo>/pulls/<N> --jq .body`, one per
merge in the window (`git log --format=%s <tag>..origin/main`, the
`Merge pull request #N` subjects). An entry is a line of the section that names
`gate-scoping` before its first colon-separated event word; continuation lines
are not joined, so the text printed is the entry's first line, cut at 160
characters. `policy_lint.mjs --stats` prints the key's counts but no PR numbers;
this is the enumeration its counts are compared against.
"""
import glob
import os
import re
import sys

SECTION = re.compile(r"^## Friction\s*\n(.*?)(?=^## |\Z)", re.M | re.S)
KEY = re.compile(r"^\s*(?:-\s*)?`?[^:`]*gate-scoping[^:`]*`?\s*:")


def main(d: str) -> int:
    prs = entries = 0
    for f in sorted(glob.glob(os.path.join(d, "*.md")), key=lambda p: int(os.path.basename(p)[:-3])):
        m = SECTION.search(open(f, encoding="utf-8").read())
        hits = [ln for ln in (m.group(1).splitlines() if m else []) if KEY.match(ln)]
        if hits:
            prs += 1
            entries += len(hits)
            for ln in hits:
                print(f"#{os.path.basename(f)[:-3]}\t{ln.strip()[:160]}")
    print(f"TOTAL\t{prs} PR(s) / {entries} entr(ies) over {len(glob.glob(os.path.join(d, '*.md')))} bodies")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
