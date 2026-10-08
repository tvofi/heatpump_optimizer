#!/usr/bin/env python3
"""Git merge driver for the measured JSON ledgers and the bug-class register.

    python3 tools/merge/ledger_merge.py --install     once per clone
    python3 tools/merge/ledger_merge.py --self-test
    python3 tools/merge/ledger_merge.py --resolve tests/closures.json   after a refused merge
    python3 tools/merge/ledger_merge.py --replay 2026-09-10   the evidence below

Every fix pull request re-records ``tests/mutation_budgets.json``,
``tests/structure_budgets.json`` and ``tests/closures.json``, so any two
branches in flight collide there in a line merge even when they recorded
different keys. ``--replay`` re-runs every branch-side merge since a date
twice, without and with this driver, and counts the ledger conflicts; from
2026-09-10 to 2026-09-24 that is 60 without it and 0 with it. Where the plain
text merge resolved cleanly the driver writes the same JSON value, and the
same bytes except that raw non-ASCII is written escaped, as the writers do.

The driver parses base, ours and theirs and merges three ways per key:

  * a key one side changed takes that side; a key both sides changed to the
    same value takes it;
  * a dict both sides changed recurses while it is a table (the top level and
    the maps under it: ``survivor_triage``, ``killed_by``, ``closures``,
    ``recorded``). One level down it is a record -- a disposition, one
    script's timing -- and a record both sides rewrote differently refuses,
    because a field-wise mix of two verdicts is neither. Two exceptions: a
    record carrying an ``at`` timestamp (``last_measured.*``) is one
    measurement, so the later ``at`` wins whole; and a record of numbers only
    (``recorded.*``: seconds, rc) merges field by field under the number rule;
  * a list of strings both sides changed is merged as a set (the closures and
    ``survivor_lines``): base, plus what either side added, less what either
    removed;
  * a number both sides changed: in ``structure_budgets.json`` and
    ``mutation_budgets.json`` an integer is a count, so it takes base plus
    both deltas, and a fraction is a cap (``max_survivor_fraction``), so it
    takes the lower -- a sum of two raises would loosen a budget neither side
    chose; in ``closures.json`` it sits under ``recorded`` (seconds, rc),
    which no check reads for a decision, so it takes the larger -- except a
    ``seconds`` inside SECONDS_BAND of the base, which is noise the writer
    keeps out (R9-CI-2b): the side outside the band wins, else the base;
  * ``recorded_at`` both sides changed takes whichever SHA descends from the
    other;
  * in a disposition map (``survivor_triage``, ``killed_by``) a row is first
    given one key on all three sides by what it is -- file, operator and
    pinned ``old`` text -- so a re-key (#1577's content anchors, or a line
    shift) is not read as a deletion plus an addition, and a branch's own
    rows and edits survive it (``_rekey``); run
    ``tests/mutation_table.py --normalize`` afterwards;
  * a top-level key the writer retired (``unpinned_sites``, derived since
    #1577) is dropped when one side deleted it;
  * a prose string one side only appended to (``reason``) takes the other
    side's text plus that addition.

Anything else both sides changed differently REFUSES, and so does a file
whose bytes do not round-trip through the formatter its writer uses (a hand
edit, a new format). A refusal hands the file to git's own text merge: a clean
one stands, and otherwise the file keeps git's ordinary conflict markers and
the driver exits 1 -- exactly what a clone without the driver gets.

A resolved ledger is a merge of two measurements, not a measurement. Every
number it writes is re-checked by the gate that owns the file -- a sum of
deltas that is wrong for a non-additive metric fails ``tests/structure.py``
one way or the other, and a stale closure is ``UNDER-SCOPED`` -- so the driver
can be wrong only loudly. It prints each key it merged numerically so the seat
knows what to re-run.

``dev/audit/config/bugclasses.json`` is not measured but is routed here
too: every root-cause pull request appends its ``_rca`` entry after the same
last entry, so two in flight always conflicted in a line merge (four merges on
2026-10-07, ``dev/audit/rca/R9-RCA-bugclasses.md``). Its numbers are counts
derived from instance lists, so a class record both sides changed refuses
there (two added instances agree on a count and are both wrong); only the
``_rca`` table merges entry by entry, and raw non-ASCII text stays raw.

GitHub never runs a merge driver, so a pull request still shows ``DIRTY``
until main is merged locally (``claim-files.md``, #570). What this removes is
the hand resolution once it is.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

DRIVER_NAME = "ledgermerge"
#: Path -> how a number both sides changed is merged.
LEDGERS = {
    "tests/mutation_budgets.json": "sum",
    "tests/structure_budgets.json": "sum",
    "tests/closures.json": "max",
    "dev/audit/config/bugclasses.json": "refuse",
}
#: Ledgers written in tests/closure.py's layout (R9-CI-2b): every table's keys
#: and string lists sorted, ``sort_keys``. GitHub merges with no driver, so the
#: layout is what keeps two branches apart there; the driver writes it from
#: either side's layout, so a branch cut before the layout merges once into it.
LAYOUT = {"tests/closures.json": ("closures", "inert_reads", "recorded")}
#: tests/closure.py's SECONDS_BAND: a re-timing inside it of the base is the
#: run-to-run noise that writer keeps out of the file.
SECONDS_BAND = 2.0
#: Ledgers whose writer keeps non-ASCII text raw (``ensure_ascii=False``).
RAW = {"dev/audit/config/bugclasses.json"}
#: Top-level keys a ledger's writer no longer stores. #1577 made the unpinned
#: count derived, so a side that deleted it wins over a branch cut before
#: #1577 that still re-recorded it.
RETIRED = {"unpinned_sites"}
#: The ``json.dumps`` shapes the three writers use (mutation_table.py indent 2;
#: structure.py indent 1 sorted; closure.py indent 1). A file that is not
#: byte-identical under one of them (raw or escaped non-ASCII aside) is
#: refused, never reformatted.
FORMATS = (
    {"indent": 1, "sort_keys": True},
    {"indent": 1},
    {"indent": 2},
)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Refuse(Exception):
    """Both sides changed ``path`` in a way this driver will not choose."""


_ABSENT = object()
#: The retired ``FILE:LINE KIND`` disposition key (tests/mutation_table.py).
_LINE_KEY = re.compile(r"^[^:\s]+:\d+ [A-Z_]+$")


def _is_str_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v) and len(set(v)) == len(v)


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _descends(a: str, b: str, repo: str) -> bool:
    """Whether commit ``b`` is an ancestor of ``a`` (``a`` is the newer)."""
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", b, a], cwd=repo,
        capture_output=True,
    ).returncode == 0


def _key_order(ours: dict, theirs: dict) -> list:
    """Ours' keys, with each key only theirs has placed after its predecessor
    in theirs -- where a text merge would have put it. Sorted when both sides
    are (the #1577 ledger keeps its maps in key order)."""
    keys = list(ours)
    if keys == sorted(keys) and list(theirs) == sorted(theirs):
        return sorted(set(keys) | set(theirs))
    prev = None
    for k in theirs:
        if k not in keys:
            keys.insert(keys.index(prev) + 1 if prev in keys else 0, k)
        prev = k
    return keys


def _site(key: str, value) -> tuple | None:
    """A disposition's identity apart from its key: file, operator, pinned text.

    Both key shapes the ledger has used carry the file before the first ``:``
    and the operator as the second word (``FILE:LINE KIND`` retired,
    ``FILE:SCOPE KIND DIGEST`` since #1577); the row carries its ``old`` pin.
    """
    words = key.split(" ")
    if ":" not in words[0] or len(words) < 2 or not isinstance(value, dict):
        return None
    old = value.get("old")
    return (words[0].split(":", 1)[0], words[1], old) if isinstance(old, str) else None


def _rekey(base: dict, ours: dict, theirs: dict, notes: list, where: str):
    """The three sides of a disposition map with each row under one key.

    When a side re-keys rows (#1577 moved every key from its line number to a
    content anchor; a line shift re-keys line-keyed rows), a key merge sees a
    deletion plus an addition, and a row the OTHER side changed or added
    beside it is lost or doubled: #1572 re-applied its 9 rows by hand after
    #1577 landed. So a row whose identity (``_site``) is unique on every side,
    and whose keys differ only in FORM -- line keys on some sides, one content
    anchor on the others -- gets that anchor on all three sides, and the
    ordinary merge then keeps a branch's own rows and applies both sides'
    edits to the same row. A base row that line shifts moved (before #1577)
    takes the moved key the same way, theirs' when both sides moved it, as a
    text merge of main's shifted lines would. Nothing else is a re-key: two
    different anchors, or line keys no base row joins, name the same pinned
    text in two places (``return None`` in two functions) and stay separate
    rows for the key merge. Nothing is renamed unless every row of the map has an identity; a
    row whose identity repeats on a side (identical pinned lines, which the
    anchor tells apart by scope and ordinal) keeps its key, and any rename
    that would collide abandons the pass for the map.
    """
    sides = (base, ours, theirs)
    keyof, twice = [], set()
    for side in sides:
        ids = {}
        for k, v in side.items():
            site = _site(k, v)
            if site is None:
                return sides
            if site in ids:
                twice.add(site)   # identical pinned lines: left to the key merge
            ids[site] = k
        keyof.append(ids)
    canon = {}
    for site in (set(keyof[0]) | set(keyof[1]) | set(keyof[2])) - twice:
        kb, ko, kt = (ids.get(site) for ids in keyof)
        keys = {k for k in (kb, ko, kt) if k is not None}
        anchors = {k for k in keys if not _LINE_KEY.match(k)}
        if len(anchors) == 1 and len(keys) > 1:
            canon[site] = anchors.pop()    # line key(s) on one side, the anchor on another
        elif not anchors and kb is not None and len(keys) > 1:
            # a base row's line shift: theirs' key when it moved, else ours'
            canon[site] = kt if kt not in (None, kb) else ko
    out = []
    moved = 0
    for side in sides:
        renamed = {}
        for k, v in side.items():
            new = canon.get(_site(k, v), k)
            if new in renamed:
                return sides
            moved += new != k
            renamed[new] = v
        out.append(renamed)
    if moved:
        notes.append(f"{where}: {moved} row key(s) aligned across sides by file, "
                     "operator and pinned text; run mutation_table.py --normalize")
    return tuple(out)


def merge3(base, ours, theirs, *, numbers: str, path: str = "",
           repo: str = ROOT, notes: list | None = None, depth: int = 0):
    """Three-way merge of parsed JSON values; raises ``Refuse``."""
    notes = notes if notes is not None else []
    if ours == theirs:
        return ours
    if ours == base:
        return theirs
    if theirs == base:
        return ours
    where = path or "<root>"
    if isinstance(ours, dict) and isinstance(theirs, dict):
        if "at" in ours and "at" in theirs:
            if not (isinstance(ours["at"], str) and isinstance(theirs["at"], str)):
                raise Refuse(f"{where}: 'at' is not a timestamp on both sides")
            notes.append(f"{where}: kept the later measurement")
            return ours if ours["at"] >= theirs["at"] else theirs
        numeric = all(_is_num(v) for v in list(ours.values()) + list(theirs.values()))
        if depth >= 2 and not numeric:
            raise Refuse(f"{where}: both sides rewrote this record differently")
        if numbers == "refuse" and depth >= 1 and not all(
                isinstance(v, dict) for v in list(ours.values()) + list(theirs.values())):
            # The register's class records derive their counts from their
            # instance lists: two sides that each added one instance agree on
            # the count and are both wrong, so only a table of records merges.
            raise Refuse(f"{where}: both sides rewrote this class record")
        b = base if isinstance(base, dict) else {}
        if depth == 1:
            b, ours, theirs = _rekey(b, ours, theirs, notes, where)
            if ours == theirs:
                return ours
            if ours == b:
                return theirs
            if theirs == b:
                return ours
        out = {}
        for k in _key_order(ours, theirs):
            v = merge3(b.get(k, _ABSENT), ours.get(k, _ABSENT), theirs.get(k, _ABSENT),
                       numbers=numbers, path=f"{path}.{k}" if path else k,
                       repo=repo, notes=notes, depth=depth + 1)
            if v is not _ABSENT:
                out[k] = v
        return out
    if _is_str_list(ours) and _is_str_list(theirs):
        b = base if _is_str_list(base) else []
        gone = (set(b) - set(ours)) | (set(b) - set(theirs))
        out = [x for x in ours if x not in gone]
        out += [x for x in theirs if x not in gone and x not in set(ours)]
        if ours == sorted(ours) and theirs == sorted(theirs):
            out.sort()
        notes.append(f"{where}: merged as a set ({len(out)} entries)")
        return out
    if _is_num(ours) and _is_num(theirs):
        if numbers == "max":
            if path.rsplit(".", 1)[-1] == "seconds" and _is_num(base) and base > 0:
                moved = [v for v in (ours, theirs)
                         if not base / SECONDS_BAND <= v <= base * SECONDS_BAND]
                if len(moved) < 2:
                    got = moved[0] if moved else base
                    notes.append(f"{where}: kept {got}; a re-timing inside "
                                 f"{SECONDS_BAND:g}x of {base} is noise")
                    return got
            notes.append(f"{where}: took the larger of {ours} and {theirs}")
            return max(ours, theirs)
        if not all(isinstance(v, int) for v in (base, ours, theirs)):
            # A fraction is a cap (``max_survivor_fraction``), not a count:
            # summing two raises would loosen it past what either side chose,
            # and no gate compares a cap with its base. Take the stricter.
            notes.append(f"{where}: took the lower cap of {ours} and {theirs}")
            return min(ours, theirs)
        if _is_num(base):
            got = base + (ours - base) + (theirs - base)
            notes.append(f"{where}: {base} + both deltas = {got}")
            return got
        raise Refuse(f"{where}: both sides added a different number")
    if path.rsplit(".", 1)[-1] == "recorded_at" and isinstance(ours, str) and isinstance(theirs, str):
        if _descends(ours, theirs, repo):
            return ours
        if _descends(theirs, ours, repo):
            return theirs
        raise Refuse(f"{where}: neither SHA descends from the other")
    if depth == 1 and path in RETIRED and _ABSENT in (ours, theirs):
        notes.append(f"{where}: retired by one side, so dropped")
        return _ABSENT
    if all(isinstance(v, str) for v in (base, ours, theirs)) and base:
        # A prose field one side only appended to (a ledger's `reason`, which
        # a pre-#1577 re-record extended): keep the other side's text and
        # append that side's addition, so neither side's words are lost.
        if ours.startswith(base):
            notes.append(f"{where}: appended this branch's addition to the incoming text")
            return theirs + ours[len(base):]
        if theirs.startswith(base):
            notes.append(f"{where}: appended the incoming addition to this branch's text")
            return ours + theirs[len(base):]
    raise Refuse(f"{where}: both sides changed it differently")


def _format(text: str):
    """The FORMATS entry ``text`` round-trips under, or None."""
    try:
        value = json.loads(text)
    except ValueError:
        return None
    for fmt in FORMATS:
        # A hand edit that pasted a raw non-ASCII character is the same JSON
        # in the same shape; the merge writes it back escaped, as the writer
        # would (14 of the 16 historical ledger refusals were only this).
        for ascii_only in (True, False):
            if json.dumps(value, ensure_ascii=ascii_only, **fmt) + "\n" == text:
                return fmt
    return None


def merge_text(base: str, ours: str, theirs: str, numbers: str,
               repo: str = ROOT, notes: list | None = None, raw: bool = False,
               layout: tuple = ()) -> str:
    """Merged file text, or raise ``Refuse``.

    ``layout`` names the tables of a ledger kept in tests/closure.py's layout:
    either side may be in it or in the writer's older one, and the result is
    written in it."""
    fmt = _format(ours)
    if layout and fmt is not None and _format(theirs) is not None:
        fmt = FORMATS[0]
    elif fmt is None or _format(theirs) != fmt:
        raise Refuse("a side is not in its writer's own JSON format")
    try:
        b = json.loads(base) if base.strip() else {}
    except ValueError:
        raise Refuse("the merge base is not JSON")
    merged = merge3(b, json.loads(ours), json.loads(theirs),
                    numbers=numbers, repo=repo, notes=notes)
    for t in layout:
        if isinstance(merged.get(t), dict):
            merged[t] = {k: sorted(set(v)) if isinstance(v, list)
                         and all(isinstance(x, str) for x in v) else v
                         for k, v in merged[t].items()}
    return json.dumps(merged, ensure_ascii=not raw, **fmt) + "\n"


def run_driver(base_path: str, ours_path: str, theirs_path: str,
               marker_size: str = "7", pathname: str = "") -> int:
    """git merge driver: resolve into ``ours_path``, or leave a conflict there."""
    label = pathname or ours_path
    with open(base_path) as f:
        base = f.read()
    with open(ours_path) as f:
        ours = f.read()
    with open(theirs_path) as f:
        theirs = f.read()
    notes: list = []
    try:
        merged = merge_text(base, ours, theirs, LEDGERS.get(pathname, "sum"), notes=notes,
                            raw=pathname in RAW, layout=LAYOUT.get(pathname, ()))
    except Refuse as why:
        # Fall back to git's own text merge, so the driver is never worse than
        # no driver: a merge the text merge resolves stays resolved.
        text = subprocess.run(
            ["git", "merge-file", f"--marker-size={marker_size}",
             "-L", f"{label} (this branch)", "-L", f"{label} (merge base)",
             "-L", f"{label} (incoming)", ours_path, base_path, theirs_path],
            capture_output=True,
        )
        if text.returncode == 0:
            print(f"LEDGER-MERGE: {label}: text merge ({why})", file=sys.stderr)
            return 0
        print(f"LEDGER-MERGE: refused {label}: {why}", file=sys.stderr)
        return 1
    with open(ours_path, "w") as f:
        f.write(merged)
    with open(ours_path) as f:
        if f.read() != merged:
            print(f"LEDGER-MERGE: refused {label}: WRITE NOT VERIFIED", file=sys.stderr)
            return 1
    print(f"LEDGER-MERGE: resolved {label}", file=sys.stderr)
    for n in notes:
        print(f"  {n}", file=sys.stderr)
    if notes:
        print("  re-run the gate that owns this file before pushing", file=sys.stderr)
    return 0


def resolve(path: str, repo: str = ROOT) -> int:
    """Finish a merge git left conflicted in ``path``, from its index stages.

    The case it exists for (R9-CI-2b): a branch's own copy of this driver is
    the one `git merge` runs, so a branch cut before tests/closures.json's
    layout refuses main's re-sorted table once. After the merge this file is
    main's copy in the work tree; ``--resolve tests/closures.json`` runs it on
    the three stages and stages the result. Refuses a path with no conflict."""
    stage = {}
    for n in (1, 2, 3):
        r = subprocess.run(["git", "show", f":{n}:{path}"], cwd=repo,
                           capture_output=True, text=True)
        stage[n] = r.stdout if r.returncode == 0 else None
    if stage[2] is None or stage[3] is None:
        print(f"LEDGER-MERGE: refused {path}: no conflict to resolve", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as td:
        files = []
        for n in (1, 2, 3):
            files.append(os.path.join(td, str(n)))
            with open(files[-1], "w") as f:
                f.write(stage[n] or "")
        rc = run_driver(files[0], files[1], files[2], "7", path)
        if rc != 0:
            return rc
        with open(files[1]) as f, open(os.path.join(repo, path), "w") as out:
            out.write(f.read())
    return subprocess.run(["git", "add", "--", path], cwd=repo).returncode


def gitattributes_error(repo: str = ROOT, text: str | None = None) -> str | None:
    """Why ``.gitattributes`` does not route every ledger here, or None."""
    if text is None:
        path = os.path.join(repo, ".gitattributes")
        text = open(path).read() if os.path.exists(path) else ""
    routed = {line.split()[0] for line in text.splitlines()
              if line.strip() and not line.lstrip().startswith("#")
              and f"merge={DRIVER_NAME}" in line.split()[1:]}
    missing = sorted(set(LEDGERS) - routed)
    if not missing:
        return None
    return ("UNROUTED LEDGER: .gitattributes does not send "
            + ", ".join(missing) + f" to merge={DRIVER_NAME}")


def install(repo: str = ROOT) -> str:
    """Configure the driver in ``repo``'s git config and read it back."""
    want = {
        f"merge.{DRIVER_NAME}.name": "merge measured JSON ledgers key by key",
        f"merge.{DRIVER_NAME}.driver":
            "python3 tools/merge/ledger_merge.py --merge %O %A %B %L %P",
    }
    already = True
    for key, value in want.items():
        got = subprocess.run(["git", "config", "--get", key], cwd=repo,
                             capture_output=True, text=True).stdout.strip()
        if got != value:
            already = False
            subprocess.run(["git", "config", key, value], cwd=repo, check=True)
    for key, value in want.items():
        got = subprocess.run(["git", "config", "--get", key], cwd=repo,
                             capture_output=True, text=True).stdout.strip()
        if got != value:
            raise RuntimeError(f"{key} reads {got!r} after install; NOT installed")
    return "already-installed" if already else "installed"


def _dump(value, fmt=FORMATS[1]) -> str:
    return json.dumps(value, **fmt) + "\n"


def self_test() -> int:
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        ok &= bool(cond)
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")

    def refused(fn) -> bool:
        try:
            fn()
        except Refuse:
            return True
        return False

    # closures.json, in the shape the replay found: two branches re-recorded
    # different scripts, and both re-timed one they share.
    base = {"_comment": "c", "recorded": {"a": {"seconds": 1.0, "rc": 0},
                                          "b": {"seconds": 2.0, "rc": 0}},
            "closures": {"a": ["x", "y"], "b": ["y"]}}
    ours = json.loads(json.dumps(base))
    theirs = json.loads(json.dumps(base))
    ours["recorded"]["a"]["seconds"] = 21.1
    theirs["recorded"]["a"]["seconds"] = 27.2
    ours["closures"]["a"] = ["w", "x", "y"]
    theirs["closures"]["a"] = ["x"]
    theirs["closures"]["b"] = ["y", "z"]
    got = json.loads(merge_text(_dump(base), _dump(ours), _dump(theirs), "max"))
    check("closures: a timing both sides re-took no longer conflicts",
          got["recorded"]["a"]["seconds"] == 27.2)
    check("closures: an addition on one side and a removal on the other both land",
          got["closures"]["a"] == ["w", "x"])
    tb = {"closures": {"a": ["x", "y"]}}
    got_t = json.loads(merge_text(_dump(tb), _dump({"closures": {"a": ["x"]}}),
                                  _dump({"closures": {"a": ["v", "x", "y"]}}), "max"))
    check("closures: a file only theirs added lands beside ours' removal",
          got_t["closures"]["a"] == ["v", "x"])
    check("closures: a key only one side changed takes that side",
          got["closures"]["b"] == ["y", "z"])

    # R9-CI-2b: the writer's 2x band, applied where both sides re-timed one
    # script, and the layout the driver writes whatever layout it was handed.
    band = lambda o, t: json.loads(merge_text(
        _dump({"recorded": {"a": {"seconds": 200.0, "rc": 0}}}),
        _dump({"recorded": {"a": {"seconds": o, "rc": 0}}}),
        _dump({"recorded": {"a": {"seconds": t, "rc": 0}}}), "max"))["recorded"]["a"]["seconds"]
    check("closures: two re-timings inside 2x of the base keep the base", band(180.0, 230.0) == 200.0)
    check("closures: a re-timing outside 2x wins over one inside", band(180.0, 450.0) == 450.0)
    with tempfile.TemporaryDirectory() as td:
        legacy = {"_comment": "c", "recorded": {"t/b": {"seconds": 1.0, "rc": 0},
                                                "t/a": {"seconds": 1.0, "rc": 0}},
                  "closures": {"t/b": ["y"], "t/a": ["x"]},
                  "inert_reads": {"t/a": ["m", "d"]}}
        lo, lt = json.loads(json.dumps(legacy)), json.loads(json.dumps(legacy))
        lo["inert_reads"]["t/a"].append("q")
        lt["inert_reads"]["t/a"].append("e")
        paths = []
        for name, v in (("b", legacy), ("o", lo), ("t", lt)):
            paths.append(os.path.join(td, name))
            with open(paths[-1], "w") as f:
                f.write(json.dumps(v, indent=1) + "\n")
        with contextlib.redirect_stderr(io.StringIO()):
            rc = run_driver(paths[0], paths[1], paths[2], "7", "tests/closures.json")
        with open(paths[1]) as f:
            text = f.read()
        want = {"_comment": "c", "closures": {"t/a": ["x"], "t/b": ["y"]},
                "inert_reads": {"t/a": ["d", "e", "m", "q"]},
                "recorded": {"t/a": {"rc": 0, "seconds": 1.0}, "t/b": {"rc": 0, "seconds": 1.0}}}
        check("closures: the driver writes the layout from two tail-appended legacy sides",
              rc == 0 and text == json.dumps(want, indent=1, sort_keys=True) + "\n")
        # The one-time transition: a branch's driver predates the layout and
        # refuses main's re-sorted table, so `git merge` leaves the conflict;
        # --resolve, run from the merged tree's copy, finishes it (R9-CI-2b).
        r = os.path.join(td, "repo")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
               "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        g = lambda *a: subprocess.run(["git", "-C", r, *a], capture_output=True, text=True, env=env)
        os.makedirs(os.path.join(r, "tests"))
        g("init", "-q", "-b", "main")
        cj = os.path.join(r, "tests", "closures.json")
        with open(cj, "w") as f:
            f.write(json.dumps(legacy, indent=1) + "\n")
        g("add", "-A"); g("commit", "-qm", "m0")
        g("checkout", "-qb", "fix")
        with open(cj, "w") as f:
            f.write(json.dumps(lo, indent=1) + "\n")
        g("commit", "-qam", "fix")
        g("checkout", "-q", "main")
        lt2 = json.loads(json.dumps(lt))
        lt2["inert_reads"]["t/a"].sort()
        with open(cj, "w") as f:
            f.write(json.dumps(lt2, indent=1, sort_keys=True) + "\n")
        g("commit", "-qam", "layout")
        g("checkout", "-q", "fix")
        merged = g("merge", "-q", "--no-edit", "main").returncode
        with contextlib.redirect_stderr(io.StringIO()):
            rrc = resolve("tests/closures.json", repo=r)
        with open(cj) as f:
            text = f.read()
        staged = g("diff", "--name-only", "--diff-filter=U").stdout.strip()
        check("closures: --resolve finishes a merge an older driver left conflicted",
              merged != 0 and rrc == 0 and staged == ""
              and text == json.dumps(want, indent=1, sort_keys=True) + "\n")
        with contextlib.redirect_stderr(io.StringIO()):
            check("closures: --resolve refuses a path with no conflict to finish",
                  resolve("tests/closures.json", repo=r) == 1)

    # structure_budgets.json: both sides re-recorded, so every count and
    # recorded_at differ. Counts take base plus both deltas.
    sb = {"coordinator_loc": 9150, "dead_methods": 0, "recorded_at": "A"}
    so = dict(sb, coordinator_loc=9170, recorded_at="B")
    st = dict(sb, coordinator_loc=9050, dead_methods=0, recorded_at="C")
    fmt = FORMATS[0]
    try:
        merge_text(_dump(sb, fmt), _dump(so, fmt), _dump(st, fmt), "sum", repo=ROOT)
        unrelated_refused = False
    except Refuse as why:
        unrelated_refused = "recorded_at" in str(why)
    check("structure: a recorded_at pair with no ancestry is refused",
          unrelated_refused)
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    from throwaway_git import throwaway_git_init
    with tempfile.TemporaryDirectory() as tmp:
        env = throwaway_git_init(tmp, "-q")

        def git(*a):
            return subprocess.run(["git", *a], cwd=tmp, check=True, capture_output=True,
                                  text=True, env=env).stdout.strip()
        git("commit", "-q", "--allow-empty", "-m", "old")
        old = git("rev-parse", "HEAD")
        git("commit", "-q", "--allow-empty", "-m", "new")
        new = git("rev-parse", "HEAD")
        so["recorded_at"], st["recorded_at"] = old, new
        got = json.loads(merge_text(_dump(sb, fmt), _dump(so, fmt), _dump(st, fmt),
                                    "sum", repo=tmp))
        check("structure: recorded_at takes the descendant SHA", got["recorded_at"] == new)
        check("structure: a count both sides moved takes base plus both deltas",
              got["coordinator_loc"] == 9070)

    # mutation_budgets.json: disjoint dispositions, one shared measurement.
    mb = {"survivor_triage": {"k1": {"verdict": "equivalent"}},
          "last_measured": {"full": {"at": "2026-09-18", "survivors": 12,
                                     "survivor_lines": ["p"]}}}
    mo = json.loads(json.dumps(mb))
    mt = json.loads(json.dumps(mb))
    mo["survivor_triage"]["k0"] = {"verdict": "equivalent"}
    mt["survivor_triage"]["k2"] = {"verdict": "killed"}
    mo["last_measured"]["full"] = {"at": "2026-09-20", "survivors": 10, "survivor_lines": ["q"]}
    mt["last_measured"]["full"] = {"at": "2026-09-19", "survivors": 11, "survivor_lines": ["r"]}
    got = json.loads(merge_text(_dump(mb, FORMATS[2]), _dump(mo, FORMATS[2]),
                                _dump(mt, FORMATS[2]), "sum"))
    check("mutation: dispositions both sides added all land",
          set(got["survivor_triage"]) == {"k0", "k1", "k2"})
    check("mutation: a measurement both sides re-took keeps the later one whole",
          got["last_measured"]["full"]["survivors"] == 10
          and got["last_measured"]["full"]["survivor_lines"] == ["q"])

    # An unsorted map (the pre-#1577 ledger): a key only theirs added lands
    # after its predecessor in theirs, where a text merge would put it
    # (merge 75231a63 was the one clean merge the first version reordered).
    ub = {"z": 1, "a": 1}
    got = merge_text(_dump(ub), _dump({"z": 1, "a": 1, "m": 1}),
                     _dump({"z": 1, "n": 1, "a": 1}), "sum")
    check("an unsorted map places a new key where the text merge would",
          list(json.loads(got)) == ["z", "n", "a", "m"])

    # A cap both sides raised keeps the lower raise, never their sum (review
    # of #1593: 0.3 -> 0.35 and 0.4 summed to 0.45, a looser cap than either).
    cb = {"max_survivor_fraction": {"changed": 0.2, "full": 0.3}}
    got = json.loads(merge_text(
        _dump(cb, FORMATS[2]),
        _dump({"max_survivor_fraction": {"changed": 0.2, "full": 0.35}}, FORMATS[2]),
        _dump({"max_survivor_fraction": {"changed": 0.2, "full": 0.4}}, FORMATS[2]), "sum"))
    check("mutation: a cap both sides raised takes the lower raise, not the sum",
          got["max_survivor_fraction"]["full"] == 0.35)

    # #1572 after #1577: main re-keyed every disposition to its content anchor
    # while a branch, still on line keys, added rows, edited one and re-keyed
    # another after its own line shift. The branch's rows must survive, its
    # edit must land on main's key, and no row may appear twice.
    P = "custom_components/heatpump_optimizer/"
    rb = {"killed_by": {P + "a.py:10 GUARD_OFF": {"killed_by": "t", "old": "if x:"},
                        P + "a.py:20 CONST": {"killed_by": "t", "old": "n = 1"}}}
    ro = {"killed_by": {P + "a.py:12 GUARD_OFF": {"killed_by": "t", "old": "if x:"},
                        P + "a.py:22 CONST": {"killed_by": "u", "old": "n = 1"},
                        P + "a.py:30 RETURN_DEL": {"killed_by": "t", "old": "return y"}}}
    rt = {"killed_by": {P + "a.py:f GUARD_OFF 1234abcd": {"killed_by": "t", "old": "if x:"},
                        P + "a.py:g CONST 5678abcd": {"killed_by": "t", "old": "n = 1"}}}
    got_r = json.loads(merge_text(_dump(rb, FORMATS[2]), _dump(ro, FORMATS[2]),
                                  _dump(rt, FORMATS[2]), "sum"))["killed_by"]
    check("re-keyed ledger: a row the branch added survives main's re-key",
          got_r.get(P + "a.py:30 RETURN_DEL", {}).get("old") == "return y")
    check("re-keyed ledger: the branch's edit lands on main's key",
          got_r.get(P + "a.py:g CONST 5678abcd", {}).get("killed_by") == "u")
    check("re-keyed ledger: a row both sides re-keyed appears once, under main's key",
          len(got_r) == 3 and P + "a.py:f GUARD_OFF 1234abcd" in got_r)

    # And a row only the branch re-keyed (its own line shift, main untouched)
    # keeps the branch's key, as the text merge does (merge 75231a63).
    sb = {"survivor_triage": {P + "o.py:3565 GUARD_OFF": {"verdict": "gap", "old": "if c:"},
                              P + "o.py:9 CONST": {"verdict": "gap", "old": "k = 2"}}}
    so = {"survivor_triage": {P + "o.py:3588 GUARD_OFF": {"verdict": "gap", "old": "if c:"},
                              P + "o.py:9 CONST": {"verdict": "gap", "old": "k = 2"}}}
    st = {"survivor_triage": {P + "o.py:3565 GUARD_OFF": {"verdict": "gap", "old": "if c:"},
                              P + "o.py:9 CONST": {"verdict": "equivalent", "old": "k = 2"}}}
    got_s = json.loads(merge_text(_dump(sb, FORMATS[2]), _dump(so, FORMATS[2]),
                                  _dump(st, FORMATS[2]), "sum"))["survivor_triage"]
    check("re-keyed ledger: a row only the branch re-keyed keeps the branch's key",
          set(got_s) == {P + "o.py:3588 GUARD_OFF", P + "o.py:9 CONST"})

    # A branch cut before #1577 merging it (#1572's own merge, 87045701): main
    # retired unpinned_sites and rewrote `reason`; the branch re-recorded the
    # count and appended to `reason`.
    pb = {"unpinned_sites": 3725, "reason": "base."}
    po = {"unpinned_sites": 3724, "reason": "base. Re-derived on R8-P2."}
    pt = {"reason": "anchored."}
    try:
        got_p = json.loads(merge_text(_dump(pb, FORMATS[2]), _dump(po, FORMATS[2]),
                                      _dump(pt, FORMATS[2]), "sum"))
    except Refuse as why:
        got_p = {"unpinned_sites": str(why), "reason": str(why)}
    check("pre-#1577 branch: a count main retired is dropped, not refused",
          "unpinned_sites" not in got_p)
    check("pre-#1577 branch: its addition to `reason` is appended to main's text",
          got_p["reason"] == "anchored. Re-derived on R8-P2.")
    check("refuses: a prose field both sides rewrote (neither only appended)",
          refused(lambda: merge_text(_dump({"reason": "a"}), _dump({"reason": "b"}),
                                     _dump({"reason": "c"}), "sum")))

    # Both sides moved a row: the content anchor wins over a line key, on
    # whichever side it is (a branch that already normalized, merging a main
    # that has not).
    ab = {"killed_by": {P + "a.py:10 GUARD_OFF": {"killed_by": "t", "old": "if x:"}}}
    ao = {"killed_by": {P + "a.py:f GUARD_OFF 1234abcd": {"killed_by": "t", "old": "if x:"}}}
    at_ = {"killed_by": {P + "a.py:11 GUARD_OFF": {"killed_by": "t", "old": "if x:"},
                         P + "a.py:40 CONST": {"killed_by": "t", "old": "z = 0"}}}
    got_a = json.loads(merge_text(_dump(ab, FORMATS[2]), _dump(ao, FORMATS[2]),
                                  _dump(at_, FORMATS[2]), "sum"))["killed_by"]
    check("re-keyed ledger: when both sides moved a row, the anchored key wins",
          set(got_a) == {P + "a.py:f GUARD_OFF 1234abcd", P + "a.py:40 CONST"})

    # Only a change of key form is a re-key (review of #1593, round 2). The
    # same pinned text under two anchors is two rows: `return None` added in
    # f on one side and in g on the other must not merge into one.
    def rows(b, o, t, *, strict=False):
        try:
            return json.loads(merge_text(*(_dump({"killed_by": x}, FORMATS[2])
                                           for x in (b, o, t)), "sum"))["killed_by"]
        except Refuse:
            if strict:
                raise
            return {}
    rec = {"killed_by": "t", "old": "    return None"}
    h = {P + "a.py:h CONST 00000000": {"killed_by": "t", "old": "n = 1"}}
    got_2 = rows(h, {**h, P + "a.py:f RETURN_DEL 1111aaaa": rec},
                 {**h, P + "a.py:g RETURN_DEL 1111aaaa": rec})
    check("re-keyed ledger: the same pinned text added under two anchors stays two rows",
          len(got_2) == 3)
    check("re-keyed ledger: the same pinned text added at two line keys stays two rows",
          len(rows(h, {**h, P + "a.py:10 RETURN_DEL": rec},
                   {**h, P + "a.py:50 RETURN_DEL": rec})) == 3)
    got_3 = rows({P + "a.py:f RETURN_DEL 1111aaaa": rec},
                 {P + "a.py:g RETURN_DEL 1111aaaa": rec},
                 {P + "a.py:h RETURN_DEL 1111aaaa": rec})
    check("re-keyed ledger: a row moved to two different anchors is not merged into one",
          len(got_3) != 1)
    # Two line-keyed rows that swapped places on one side: no rename may
    # collide, and the other side's addition still lands.
    x, y = {"killed_by": "t", "old": "if x:"}, {"killed_by": "t", "old": "if y:"}
    k10, k12 = P + "a.py:10 GUARD_OFF", P + "a.py:12 GUARD_OFF"
    got_1 = rows({k10: x, k12: y}, {k12: x, k10: y},
                 {k10: x, k12: y, P + "a.py:30 CONST": {"killed_by": "t", "old": "n = 1"}})
    check("re-keyed ledger: rows that swapped keys on one side keep that side's keys",
          got_1 == {k12: x, k10: y, P + "a.py:30 CONST": {"killed_by": "t", "old": "n = 1"}})
    # The retired count is dropped only when one side deleted it; a count
    # both sides still record merges as a count.
    got_n = json.loads(merge_text(_dump({"unpinned_sites": 10}, FORMATS[2]),
                                  _dump({"unpinned_sites": 8}, FORMATS[2]),
                                  _dump({"unpinned_sites": 11}, FORMATS[2]), "sum"))
    check("a retired count both sides still record merges as base plus both deltas",
          got_n.get("unpinned_sites") == 9)
    check("a retired key both sides still hold is merged, not dropped",
          "unpinned_sites" in json.loads(merge_text(
              _dump({"unpinned_sites": "a."}, FORMATS[2]),
              _dump({"unpinned_sites": "a. b."}, FORMATS[2]),
              _dump({"unpinned_sites": "c."}, FORMATS[2]), "sum")))
    # A repeated pinned line is left out of the alignment on its own; the
    # map's other rows are still aligned, so an edit to one of them lands.
    rn = {"killed_by": "t", "old": "    return None"}
    ix, iu = {"killed_by": "t", "old": "if x:"}, {"killed_by": "u", "old": "if x:"}
    fa, ga, xa = (P + "a.py:f RETURN_DEL 1111aaaa", P + "a.py:g RETURN_DEL 1111aaaa",
                  P + "a.py:k GUARD_OFF 2222bbbb")
    l1, l2, l10 = P + "a.py:1 RETURN_DEL", P + "a.py:2 RETURN_DEL", P + "a.py:10 GUARD_OFF"
    got_t = rows({l1: rn, l2: rn, l10: ix}, {l1: rn, l2: rn, l10: iu},
                 {fa: rn, ga: rn, xa: ix})
    check("re-keyed ledger: a repeated pinned line does not stop the other rows aligning",
          got_t == {fa: rn, ga: rn, xa: iu})
    # A base row both sides' line shifts moved (before #1577): one row, under
    # theirs' key, carrying ours' edit (merges 507f0cf0, 2af75ad4).
    iu12 = {"killed_by": "u", "old": "if x:"}
    check("re-keyed ledger: a row both sides' line shifts moved is one row, under theirs' key",
          rows({P + "a.py:10 GUARD_OFF": ix}, {P + "a.py:12 GUARD_OFF": iu12},
               {P + "a.py:11 GUARD_OFF": ix}) == {P + "a.py:11 GUARD_OFF": iu12})
    # Two rows whose renames would land on one key: the pass is abandoned
    # for the map, and the key merge refuses rather than keep one of them.
    iy, l12 = {"killed_by": "t", "old": "if y:"}, P + "a.py:12 GUARD_OFF"
    got_c = refused(lambda: rows({l10: ix, l12: iy}, {xa: ix, l12: iy}, {l10: ix, xa: iy},
                                 strict=True))
    check("re-keyed ledger: renames that would collide are refused, not collapsed",
          got_c)

    # Refusals: the ones that make the driver safe to route real files to.
    mo2 = json.loads(json.dumps(mb))
    mt2 = json.loads(json.dumps(mb))
    mo2["survivor_triage"]["k1"] = {"verdict": "equivalent", "reason": "one"}
    mt2["survivor_triage"]["k1"] = {"verdict": "killed"}
    check("refuses: one disposition both sides rewrote differently",
          refused(lambda: merge_text(_dump(mb, FORMATS[2]), _dump(mo2, FORMATS[2]),
                                     _dump(mt2, FORMATS[2]), "sum")))
    md = json.loads(json.dumps(mb))
    del md["survivor_triage"]["k1"]
    for label, a, b in (("ours deletes", md, mo2), ("theirs deletes", mo2, md)):
        check(f"refuses: a disposition one side deleted and the other rewrote ({label})",
              refused(lambda a=a, b=b: merge_text(_dump(mb, FORMATS[2]), _dump(a, FORMATS[2]),
                                                  _dump(b, FORMATS[2]), "sum")))
    check("refuses: a side not in its writer's own format",
          refused(lambda: merge_text(_dump(mb), json.dumps(mo, indent=4) + "\n",
                                     _dump(mt), "sum")))
    raw = json.dumps(mo, indent=2, ensure_ascii=False).replace("equivalent", "équivalent", 1) + "\n"
    check("a side with a raw non-ASCII character is merged, not refused",
          not refused(lambda: merge_text(_dump(mb, FORMATS[2]), raw,
                                         _dump(mt, FORMATS[2]), "sum")))
    check("refuses: a side that is not JSON (conflict markers)",
          refused(lambda: merge_text(_dump(mb), "<<<<<<< ours\n", _dump(mt), "sum")))

    # The driver end to end, through the files git hands it.
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, value in (("O", base), ("A", ours), ("B", theirs)):
            p = os.path.join(tmp, name)
            with open(p, "w") as f:
                f.write(_dump(value))
            paths.append(p)
        rc = run_driver(*paths, "7", "tests/closures.json")
        with open(paths[1]) as f:
            written = json.loads(f.read())
        check("driver: resolves into %A and exits 0",
              rc == 0 and written["closures"]["a"] == ["w", "x"])
        with open(paths[1], "w") as f:
            f.write(_dump(mo2, FORMATS[2]))
        with open(paths[2], "w") as f:
            f.write(_dump(mt2, FORMATS[2]))
        with open(paths[0], "w") as f:
            f.write(_dump(mb, FORMATS[2]))
        rc = run_driver(*paths, "7", "tests/mutation_budgets.json")
        with open(paths[1]) as f:
            left = f.read()
        check("driver: a refusal exits 1 and leaves conflict markers in %A",
              rc == 1 and "<<<<<<<" in left)

        # A refusal the plain text merge resolves stays resolved (a side in a
        # hand-edited format, changes far apart): never worse than no driver.
        wide = {f"k{i}": i for i in range(12)}
        for name, value in (("O", wide), ("A", dict(wide, k0=100)), ("B", dict(wide, k11=100))):
            with open(os.path.join(tmp, name), "w") as f:
                f.write(json.dumps(value, indent=4) + "\n")
        rc = run_driver(*paths, "7", "tests/closures.json")
        with open(paths[1]) as f:
            text_merged = json.loads(f.read())
        check("driver: a format refusal falls back to a clean text merge",
              rc == 0 and text_merged["k0"] == 100 and text_merged["k11"] == 100)

    def fake_git(rc: int):
        def git(*a):
            if a[0] == "log":
                return subprocess.CompletedProcess(a, 0, "h p1 p2 Merge main\n", "")
            return subprocess.CompletedProcess(a, rc, f"t\n{next(iter(LEDGERS))}\n", "usage")
        return git
    printed = {}
    for rc in (129, 1):
        printed[rc] = io.StringIO()
        with contextlib.redirect_stdout(printed[rc]), contextlib.redirect_stderr(io.StringIO()):
            printed[rc] = (replay("x", git=fake_git(rc)), printed[rc])
    check("replay: a merge-tree usage error (git < 2.40) is refused, not a zero",
          printed[129][0] == 2 and "conflicts" not in printed[129][1].getvalue())
    check("replay: a conflicted merge-tree (exit 1) is counted (null control)",
          printed[1][0] == 0 and f"{next(iter(LEDGERS))}: 1 conflicts without the "
          "driver, 1 with it" in printed[1][1].getvalue())
    # The bug-class register (2026-10-07: #2012, #2014 and #2018 each needed a
    # hand resolution): two root-cause branches append different _rca entries
    # after the same last one; both land, in order, and raw text stays raw.
    rca = {"date": "2026-10-07", "status": "done", "note": "l\u00e4uft"}
    gb = {"P1": {"total": 2, "instances": ["a", "b"]}, "_rca": {"Z-old": rca}}
    go = json.loads(json.dumps(gb))
    gt = json.loads(json.dumps(gb))
    go["_rca"]["R-ours"] = dict(rca, status="ours")
    gt["_rca"]["R-theirs"] = dict(rca, status="theirs")
    reg = "dev/audit/config/bugclasses.json"
    gtext = merge_text(*(json.dumps(x, indent=2, ensure_ascii=False) + "\n" for x in (gb, go, gt)),
                       LEDGERS[reg], raw=reg in RAW)
    check("bugclasses: two _rca entries appended after the same last entry both land",
          list(json.loads(gtext)["_rca"]) == ["Z-old", "R-theirs", "R-ours"])
    check("bugclasses: raw non-ASCII text is written back raw",
          "\u00e4" in gtext and "\\u00e4" not in gtext)
    go["_rca"]["Z-old"]["status"], gt["_rca"]["Z-old"]["status"] = "a", "b"
    check("bugclasses refuses: one _rca entry both sides rewrote differently",
          refused(lambda: merge_text(_dump(gb, FORMATS[2]), _dump(go, FORMATS[2]),
                                     _dump(gt, FORMATS[2]), LEDGERS[reg])))
    go2, gt2 = json.loads(json.dumps(gb)), json.loads(json.dumps(gb))
    go2["P1"] = {"total": 3, "instances": ["a", "b", "c"]}
    gt2["P1"] = {"total": 3, "instances": ["a", "b", "d"]}
    check("bugclasses refuses: a class both sides added an instance to (equal counts, both wrong)",
          refused(lambda: merge_text(_dump(gb, FORMATS[2]), _dump(go2, FORMATS[2]),
                                     _dump(gt2, FORMATS[2]), LEDGERS[reg])))
    check(".gitattributes routes every ledger to the driver",
          gitattributes_error() is None)
    check("a .gitattributes routing only one ledger is refused",
          (gitattributes_error(text=f"tests/closures.json merge={DRIVER_NAME}\n") or "")
          .startswith("UNROUTED LEDGER"))
    print(f"\n{'all passed' if ok else 'FAILED'}")
    return 0 if ok else 1


def replay(since: str, repo: str = ROOT, git=None) -> int:
    """Re-merge every non-PR merge commit since ``since``; count ledger conflicts.

    Each merge runs under its first parent's ``.gitattributes`` and then under
    this tree's. The driver must be installed; without it the two columns are
    equal. ``merge-tree`` exits 0 (clean) or 1 (conflicted); anything else --
    129 for ``--attr-source`` on a git older than 2.40 -- is a refusal, never
    a zero.
    """
    git = git or (lambda *a: subprocess.run(["git", *a], cwd=repo,
                                            capture_output=True, text=True))
    log = git("log", "--all", "--merges", f"--since={since}", "--format=%H %P %s").stdout
    merges = [l.split(" ", 3) for l in log.splitlines()
              if l.split(" ", 3)[3:] and not l.split(" ", 3)[3].startswith("Merge pull request")]
    before = {f: 0 for f in LEDGERS}
    after = {f: 0 for f in LEDGERS}
    for h, p1, p2, _ in merges:
        # Without: the attributes the merge had (its first parent's, which
        # route no ledger here). With: this tree's.
        for counts, pre in ((before, [f"--attr-source={p1}"]), (after, ["--attr-source=HEAD"])):
            r = git(*pre, "merge-tree", "--write-tree", "--name-only",
                    "--no-messages", p1, p2)
            if r.returncode not in (0, 1):
                print(f"LEDGER-MERGE: refused --replay: `git merge-tree` exited "
                      f"{r.returncode} on {h[:12]} ({r.stderr.strip()[:200]}); "
                      f"--attr-source needs git 2.40 or later", file=sys.stderr)
                return 2
            out = r.stdout.splitlines()[1:]
            for f in LEDGERS:
                counts[f] += f in out
    print(f"{len(merges)} branch-side merges since {since}")
    for f in LEDGERS:
        print(f"  {f}: {before[f]} conflicts without the driver, {after[f]} with it")
    return 0


def main(argv: list) -> int:
    if argv[:1] == ["--merge"] and len(argv) >= 4:
        rest = argv[1:]
        return run_driver(rest[0], rest[1], rest[2],
                          rest[3] if len(rest) > 3 else "7",
                          rest[4] if len(rest) > 4 else "")
    if argv[:1] == ["--install"]:
        print(f"LEDGER-MERGE: {install()}")
        problem = gitattributes_error()
        if problem:
            print(problem, file=sys.stderr)
            return 1
        return 0
    if argv[:1] == ["--resolve"] and len(argv) == 2:
        return resolve(argv[1])
    if argv[:1] == ["--replay"] and len(argv) == 2:
        return replay(argv[1])
    if argv[:1] == ["--self-test"]:
        return self_test()
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
