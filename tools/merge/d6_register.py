"""The three-way merge of the D6 register, ``tools/merge/ledger_merge.py``'s arm.

``dev/audit/rounds/round4/D6/claims.json`` and ``claims.md`` are the committed
output of ``claims.py``: one row per claim, keyed by its id, and many rows carry
a value derived from the tree (an entity count, a link count, a module list).
Two branches that each move the tree re-run the generator, and git's line merge
then conflicts on the row both re-derived, though neither side's value is the
merged tree's and the only right resolution is a re-run.

So the register merges row by row, like the other generated ledgers: a row one
side changed takes that side, a row both sides changed takes the incoming side
whole, a row one side added or deleted is added or deleted. Each file merges
alone (git hands a driver one path), and both apply the same rule to the same
rows, so the merged ``claims.md`` is still the rendering of the merged
``claims.json``.

A merged register is a merge of two runs, not a run, and the driver says so.
What makes a wrong pick loud is ``tests/harness_headers.py``, which re-runs
``claims.py`` on every pull request and fails "the executed harnesses leave
their committed output byte-identical" until the register is regenerated: the
driver moves the re-derivation from a hand resolution of conflict markers to
the gate that already owns the file.

Anything that is not the generator's own layout refuses, so git's text merge
takes the file and nothing is guessed: JSON that ``json.dumps(rows, indent=1)``
does not reproduce byte for byte, a row without a unique string ``id``, a
Markdown row that is not ``| <id> | ...``, a Markdown preamble both sides
changed differently, or a row one side rewrote and the other deleted.

    python3 tools/merge/d6_register.py --self-test
"""
from __future__ import annotations

import json
import re
import sys

ROW = re.compile(r"^\| ([^|\s]+) \|")


class Refuse(Exception):
    """The register is not in its generator's layout, or the merge has no choice."""


def _pick(base, ours, theirs):
    """One row's three-way merge; ``None`` deletes it."""
    if ours == theirs:
        return ours
    if ours == base:
        return theirs
    if theirs == base:
        return ours
    if ours is None or theirs is None:
        raise Refuse("a row one side rewrote, the other deleted")
    return theirs


def _order(base: list, ours: list, theirs: list) -> list:
    """Ours' order plus what theirs added after its predecessor; ``_pick`` deletes."""
    out = list(ours)
    for i, k in enumerate(theirs):
        if k in out:
            continue
        prev = next((p for p in reversed(theirs[:i]) if p in out), None)
        out.insert(out.index(prev) + 1 if prev is not None else 0, k)
    return out


def _merge_rows(base: dict, ours: dict, theirs: dict, order: list) -> list:
    rows = []
    for k in order:
        row = _pick(base.get(k), ours.get(k), theirs.get(k))
        if row is not None:
            rows.append(row)
    return rows


def _json_rows(text: str) -> tuple[list, dict]:
    try:
        rows = json.loads(text)
    except ValueError as exc:
        raise Refuse(f"not JSON: {exc}")
    if not isinstance(rows, list) or not all(
            isinstance(r, dict) and isinstance(r.get("id"), str) for r in rows):
        raise Refuse("not a list of rows each carrying a string id")
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise Refuse("a row id repeats")
    if json.dumps(rows, indent=1) != text:
        raise Refuse("not claims.py's json.dump(indent=1) layout")
    return ids, {r["id"]: r for r in rows}


def merge_json(base: str, ours: str, theirs: str) -> str:
    """Merge three ``claims.json`` texts row by row; ``Refuse`` outside the layout."""
    (bi, b), (oi, o), (ti, t) = _json_rows(base), _json_rows(ours), _json_rows(theirs)
    return json.dumps(_merge_rows(b, o, t, _order(bi, oi, ti)), indent=1)


def _md_rows(text: str) -> tuple[str, list, dict]:
    lines = text.splitlines(keepends=True)
    if not lines or not text.endswith("\n"):
        raise Refuse("not claims.py's newline-terminated table")
    head = next((i for i, ln in enumerate(lines) if ROW.match(ln) and not ln.startswith("| id |")),
                len(lines))
    preamble, body = "".join(lines[:head]), lines[head:]
    ids, rows = [], {}
    for ln in body:
        m = ROW.match(ln)
        if not m:
            raise Refuse(f"a line under the table is not a row: {ln[:60]!r}")
        if m.group(1) in rows:
            raise Refuse("a row id repeats")
        ids.append(m.group(1))
        rows[m.group(1)] = ln
    return preamble, ids, rows


def merge_md(base: str, ours: str, theirs: str) -> str:
    """Merge three ``claims.md`` texts row by row; ``Refuse`` outside the layout."""
    (bp, bi, b), (op, oi, o), (tp, ti, t) = _md_rows(base), _md_rows(ours), _md_rows(theirs)
    if op != tp and bp not in (op, tp):
        raise Refuse("the preamble both sides changed differently")
    pre = tp if op == bp else op
    return pre + "".join(_merge_rows(b, o, t, _order(bi, oi, ti)))


def self_test() -> int:
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def refused(fn, *a) -> bool:
        try:
            fn(*a)
        except Refuse:
            return True
        return False

    def row(i, result, verdict="true"):
        return {"id": i, "source": "s", "claim": "c", "command": "x",
                "result": result, "verdict": verdict, "truth": ""}

    def dump(rows):
        return json.dumps(rows, indent=1)

    def md(rows):
        return ("# t\n\nGenerated.\n\n| id | source | claim | check | result | verdict | t |\n"
                "|---|---|---|---|---|---|---|\n"
                + "".join(f"| {r['id']} | `s` | c | `x` | {r['result']} | **{r['verdict']}** |  |\n"
                          for r in rows))

    # The replay's shape: both branches re-derived C32's count, only theirs C42's.
    base = [row("C1", "n=1"), row("C32", "documented=98 measured=98"), row("C42", "v1")]
    ours = [row("C1", "n=1"), row("C32", "documented=99 measured=99"), row("C42", "v1")]
    theirs = [row("C1", "n=2"), row("C32", "documented=101 measured=101"), row("C42", "v2")]
    want = [row("C1", "n=2"), row("C32", "documented=101 measured=101"), row("C42", "v2")]
    check("json: a row both sides re-derived takes the incoming row, the others theirs",
          merge_json(dump(base), dump(ours), dump(theirs)) == dump(want))
    check("md: the same rows merge to the rendering of the merged json",
          merge_md(md(base), md(ours), md(theirs)) == md(want))
    mine = [row("C1", "n=3"), row("C32", "documented=98 measured=98"), row("C42", "v1")]
    check("json: a row only ours changed keeps ours (null control for the incoming pick)",
          json.loads(merge_json(dump(base), dump(mine), dump(base)))[0]["result"] == "n=3")
    check("md: a row only ours changed keeps ours",
          "| n=3 |" in merge_md(md(base), md(mine), md(base)))
    added_o = base[:1] + [row("C2", "o")] + base[1:]
    added_t = base + [row("C99", "t")]
    got = [r["id"] for r in json.loads(merge_json(dump(base), dump(added_o), dump(added_t)))]
    check("json: rows each side added both land, in the generator's order",
          got == ["C1", "C2", "C32", "C42", "C99"])
    got = [ROW.match(ln).group(1) for ln in merge_md(md(base), md(added_o), md(added_t))
           .splitlines() if ROW.match(ln) and not ln.startswith("| id |")]
    check("md: rows each side added both land, in the same order",
          got == ["C1", "C2", "C32", "C42", "C99"])
    mid_t = base[:1] + [row("C5", "t")] + base[1:]
    got = [r["id"] for r in json.loads(merge_json(dump(base), dump(added_o), dump(mid_t)))]
    check("json: a row theirs added mid-table lands after its predecessor there",
          got == ["C1", "C5", "C2", "C32", "C42"])
    dropped = base[:2]
    check("json: a row theirs deleted and ours left alone is deleted",
          [r["id"] for r in json.loads(merge_json(dump(base), dump(base), dump(dropped)))]
          == ["C1", "C32"])
    check("json: a row ours rewrote and theirs deleted refuses",
          refused(merge_json, dump(base), dump(ours), dump([base[0], base[2]])))
    check("json: a file not in json.dump(indent=1)'s layout refuses",
          refused(merge_json, dump(base), json.dumps(ours, indent=2), dump(theirs)))
    check("json: a repeated id refuses",
          refused(merge_json, dump(base), dump(ours + ours[:1]), dump(theirs)))
    check("json: a row with no id refuses",
          refused(merge_json, dump(base), dump(ours + [{"x": 1}]), dump(theirs)))
    check("md: a stray line under the table refuses",
          refused(merge_md, md(base), md(ours) + "note\n", md(theirs)))
    check("md: a preamble both sides changed differently refuses",
          refused(merge_md, md(base), "A" + md(ours), "B" + md(theirs)))
    check("md: a preamble one side changed takes that side",
          merge_md(md(base), md(base), "A" + md(base)).startswith("A# t"))
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
    sys.exit(2)
