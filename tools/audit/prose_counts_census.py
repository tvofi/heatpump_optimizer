#!/usr/bin/env python3
"""Every prose count shape in the reader corpus, and what reads it (R9-RO-PC1).

    PYTHONPATH=tests/hastub:tests:custom_components python3 tools/audit/prose_counts_census.py
    ... --rows   # each unread row with its line, not only the per-noun totals

The rule that enumerates the stale-prose-count class's seams. `tests/doc_claims`
`check_prose_tree_counts` reads eleven count SHAPES over the reader corpus and
compares each to a measurement the tree derives; this command enumerates every
`<number> <plural noun>` the corpus states, subtracts the spans those shapes
claimed, and prints what is left against a disposition. A noun with no entry is
REFUSED, so a count shape that lands tomorrow without a reader is found by
running this, without anyone listing it in advance -- and an entry whose noun
states no unclaimed count any more is DEAD, so the table cannot rot into a
second hand-maintained enumeration (the bounded direction, decision 0003).

The shapes, and the claiming rule that decides which shape takes a span, are
imported from tests/doc_claims.py: there is one copy, and this command cannot
drift from the arm it describes. Its exit is evidence, not a gate --
`tools/audit/` is INERT and nothing runs this in CI -- so a REFUSED line is a
finding for the next seat, not a red check.

Read the summary, not the rows. `steps` is the one large unread group: the
~60 `steps` cells in configuration.md's tables are compared only as C30's
Default and C31's min/max, so planting 0.5 steps to 0.7 steps leaves every
instrument green. A count spelled as a word ("five pages", "twelve files") is
not enumerated here at all, and is the other named limit.
"""
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
for _extra in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(ROOT / _extra))

import doc_claims as dc  # noqa: E402

#: noun -> why the count it states is read, or why it is not a count of a set.
#: Only nouns the arm's shapes do NOT read appear here; a noun the arm reads
#: states no seam by construction, and is listed by the shape block instead.
DISPOSITIONS = {
    "entities": "read elsewhere: check_entity_prose scans the whole corpus for '<N> entities'",
    "sensors": "read elsewhere: claims.py C39 and entities.py's module-map platform comments",
    "buttons": "read elsewhere: entities.py's module-map platform comments",
    "switches": "read elsewhere: entities.py's module-map platform comments",
    "fields": "read by the arm when the sentence names its service; 'All N fields' inside a service paragraph is read by check_service_fields",
    "steps": "a slider increment, not a count of a set -- and the one large unread group: C30 reads Default and C31 the min/max, so a planted '0.7 steps' is green everywhere",
    "hours": "a duration",
    "minutes": "a duration",
    "seconds": "a duration",
    "days": "a duration",
    "degree-hours": "a duration",
    "litres": "a volume",
    "is": "not a count",
    "means": "not a count",
    "keeps": "not a count",
    "leaves": "not a count",
    "treats": "not a count",
    "says": "not a count",
    "lets": "not a count",
    "sends": "not a count",
    "suits": "not a count",
    "trusts": "not a count",
    "makes": "not a count",
    "caps": "not a count",
    "arrives": "not a count",
    "plus": "not a count",
    "across": "not a count",
}

SEAM = re.compile(r"\b(\d{1,4})\s+([a-z][a-z-]*s)\b")


def main() -> int:
    show_rows = "--rows" in sys.argv[1:]
    rows, unread = dc.prose_count_scan(dc.CORPUS)
    claimed: dict[tuple[str, int], list[tuple[int, int]]] = collections.defaultdict(list)
    for document, line, start, end, *_rest in rows:
        claimed[(document, line)].append((start, end))
    print(f"shapes={len(dc._PROSE_COUNT_SHAPES)} claims={len(rows)} "
          f"documents={len(dc.CORPUS)}")
    for name, _pattern, _quantities in dc._PROSE_COUNT_SHAPES:
        print(f"  read  {name}")
    if unread:
        print(f"  REFUSED   a shape the corpus never states: {unread}")

    seamed: dict[str, int] = collections.Counter()
    refused = 0
    for document, text in sorted(dc.CORPUS.items()):
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in SEAM.finditer(line):
                if any(start <= match.start(1) < end
                       for start, end in claimed.get((document, lineno), ())):
                    continue
                noun = match.group(2)
                seamed[noun] += 1
                if noun not in DISPOSITIONS:
                    refused += 1
                    print(f"  REFUSED   {document}:{lineno}: '{match.group(0)}' "
                          "has no disposition")
                elif show_rows:
                    print(f"  row   {document}:{lineno}  {match.group(0)}  :: {line.strip()[:96]}")

    print(f"\nseams={sum(seamed.values())} nouns={len(seamed)}")
    for noun, count in seamed.most_common():
        print(f"  {count:4d}  {noun:<13} {DISPOSITIONS.get(noun, 'REFUSED: no disposition')}")
    dead = sorted(noun for noun in DISPOSITIONS if noun not in seamed)
    if dead:
        print(f"  DEAD      dispositions matching no unclaimed count: {dead}")
    print(f"\nRESULT seam_rows={sum(seamed.values())} nouns={len(seamed)} "
          f"refused={refused} dead={len(dead)}")
    return 1 if (refused or dead or unread) else 0


if __name__ == "__main__":
    raise SystemExit(main())
