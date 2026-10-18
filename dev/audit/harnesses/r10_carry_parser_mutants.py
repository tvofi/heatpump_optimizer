#!/usr/bin/env python3
"""O11 (#2404): every predicate of carry_audit.py's marker parser dies alone.

Written by the O11 fixer, round 5. Rounds 2 and 3 of #2404's review each found
a guard whose halves survived one at a time (the paren form and the segment
scope; then the segment's next-marker and line-end cuts), killed only when
reverted together. This drive enumerates the class rather than the instance:

  SITES    the census, read from the file's own AST: every predicate of the
           parser functions (PARSER) -- test, boolean operand, comparison,
           slice, cut or match call, continue and break (sites()) -- and each
           regex constant (PATTERNS).
  MUTANTS  single-site perturbations, each a one-occurrence replacement. A
           regex alternative, quantifier or anchor is its own mutant.

A site no mutant changes prints `UNMAPPED`; a mutant the self-test does not
kill prints `SURVIVED`, unless EQUIVALENT names why no input tells it apart.
Each mutant is applied alone, `carry_audit.py --self-test` run, and the file
restored byte for byte; the drive refuses a dirty file. Metric:

  RESULT mutant=<name> failed=<n> verdict=killed|SURVIVED|CRASHED|equivalent

A mutant that kills only by crashing the self-test (failed=-1, no FAIL line)
counts as a survivor: no check named what it broke.
  RESULT sites=<n> unmapped=<n> mutants=<n> survived=<n>

Expected at the fixing head: unmapped=0 survived=0. Null control: M0, the file
unmutated, must print failed=0, and a mutant whose pattern is not found aborts.

    python3 dev/audit/harnesses/r10_carry_parser_mutants.py [NAME ...]
"""
from __future__ import annotations

import ast
import re
import subprocess
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
REL = "tools/audit/carry_audit.py"
F = ROOT / REL
PARSER = ("carry_segments", "carry_refs", "carry_dests", "seg_dests", "finding_rows", "audit")
PATTERNS = ("CARRY", "ITEM_REF", "CODE_SPAN", "GROUP_TOK", "ISSUE_TOK", "BRIEF_TOK")

MUTANTS = [
    # carry_segments: the span skip and its bounds, the next-marker and line-end cuts
    ("M13", "        if any(a <= at < b for a, b in spans):", "        if False:"),
    ("S-span-hi", "a <= at < b for", "a <= at <= b for"),
    ("S-span-lo", "a <= at < b for", "a < at < b for"),
    ("M16", "text[at:starts[i + 1] if i + 1 < len(starts) else len(text)]", "text[at:len(text)]"),
    ("S-next-last", "if i + 1 < len(starts) else len(text)", "if i + 1 < len(starts) else -1"),
    ("M15b", '.split("\\n", 1)[0])', ")"),
    ("S-skip", "            continue\n        # each", "            pass\n        # each"),
    ("S-lines", "    starts = [m.start() for m in CARRY.finditer(text)]",
     "    starts = [m.start() for m in CARRY.finditer(text.split(\"\\n\")[0])]"),
    ("S-segs", "        segs.append(", "        0 and segs.append("),
    ("S-spans", "    spans = [m.span() for m in CODE_SPAN.finditer(text)]", "    spans = []"),
    # carry_refs / carry_dests: the segment scope (M15), the destinations kept
    ("M15", "        for ref in ITEM_REF.findall(seg):", "        for ref in ITEM_REF.findall(text):"),
    ("R-found", "        found += ds\n", "        found += []\n"),
    ("R-extend", "            refs.setdefault(ref, []).extend(ds)", "            refs.setdefault(ref, ds)"),
    ("R-seg", "        ds = seg_dests(seg)", "        ds = seg_dests(seg.split(\"(\", 1)[0])"),
    ("R-dests", "    return carry_refs(text)[0]", "    return carry_refs(text)[1]"),
    # seg_dests: the rest, dismissed, the split, each token predicate
    ("D-maxsplit", 'rest = seg.split(":", 1)[1]', 'rest = seg.split(":")[1]'),
    ("D-after", 'rest = seg.split(":", 1)[1]', 'rest = seg.split(":", 1)[0]'),
    ("D-rest-ws", 'rest = seg.split(":", 1)[1].strip().strip', 'rest = seg.split(":", 1)[1].strip'),
    ("D-rest-strip", '    rest = seg.split(":", 1)[1].strip().strip("`*_")', '    rest = seg.split(":", 1)[1].strip()'),
    ("D-dism-I", 'dm = re.match(r"dismissed\\s*:\\s*(.*)", rest, re.I)', 'dm = re.match(r"dismissed\\s*:\\s*(.*)", rest)'),
    ("D-dm", "    if dm:\n", "    if False:\n"),
    ("D-dism-off", 'dm = re.match(r"dismissed\\s*:\\s*(.*)", rest, re.I)', "dm = None"),
    ("D-split-punct", 'r"[,;|/]\\s*|\\s+and\\s+|\\s+"', 'r"\\s+and\\s+|\\s+"'),
    ("D-split-and", 'r"[,;|/]\\s*|\\s+and\\s+|\\s+"', 'r"[,;|/]\\s*|\\s+"'),
    ("D-split-ws", 'r"[,;|/]\\s*|\\s+and\\s+|\\s+"', 'r"[,;|/]\\s*|\\s+and\\s+"'),
    ("D-tok-strip", '        tok = tok.strip("`*_().:")', "        tok = tok"),
    ("D-empty", "        if not tok or tok.lower()", "        if tok.lower()"),
    ("D-item", 'or tok.lower() == "item" or', "or"),
    ("D-hex", ' or re.fullmatch(r"[0-9a-f]{8}", tok):', ":"),
    ("D-group", "        if GROUP_TOK.match(tok) or ISSUE_TOK", "        if ISSUE_TOK"),
    ("D-issue", "GROUP_TOK.match(tok) or ISSUE_TOK.match(tok) or BRIEF", "GROUP_TOK.match(tok) or BRIEF"),
    ("D-brief", " or BRIEF_TOK.match(tok):\n", ":\n"),
    ("D-skip", "            continue\n        if GROUP_TOK", "            break\n        if GROUP_TOK"),
    ("D-next", "            found.append(tok)\n            continue", "            found.append(tok)\n            break"),
    ("D-break", "        break  # prose after the destinations", "        continue"),
    # finding_rows / audit: the routing by reference
    ("A-body-none", '    texts = [("body", body or "", False)]', '    texts = [("body", body, False)]'),
    ("A-comment-none", '        b = c.get("body") or ""', '        b = c.get("body")'),
    ("A-body-key", '        b = c.get("body") or ""', '        b = c.get("text") or ""'),
    ("A-verdict", "        if VERDICT.match(b.lstrip()):", "        if True:"),
    ("A-named", "                refs.setdefault(ref, []).extend(rds)", "                pass"),
    ("A-extend", "                refs.setdefault(ref, []).extend(rds)", "                refs.setdefault(ref, rds)"),
    ("A-lstrip", "        if VERDICT.match(b.lstrip()):", "        if VERDICT.match(b):"),
    ("A-flagged", '            if it["flagged"]:', "            if True:"),
    ("A-union", '        r["dests"] = r["dests"] + refs.get(r["id"], [])', '        r["dests"] = r["dests"] or refs.get(r["id"], [])'),
    ("A-union-off", '        r["dests"] = r["dests"] + refs.get(r["id"], [])', "        pass"),
    ("A-bad", "            (notes if ok else bad).append(", "            notes.append("),
    ("A-note", '(f"{tok}: {note}" if note else tok)', "(tok)"),
    ("A-status-u", 'r["status"] = "unrouted" if not r["dests"] else', 'r["status"] = "unrouted" if False else'),
    ("A-status-b", '("bad" if bad else "routed")', '("routed")'),
    # the patterns: each alternative, anchor and quantifier
    ("P-carry-look", 'CARRY = re.compile(r"(?<![\\w-])Carry:")', 'CARRY = re.compile(r"Carry:")'),
    ("P-carry-dash", 'CARRY = re.compile(r"(?<![\\w-])Carry:")', 'CARRY = re.compile(r"(?<![\\w])Carry:")'),
    ("M14", 'ITEM_REF = re.compile(r"\\(item\\s+([0-9a-f]{8})\\)")', 'ITEM_REF = re.compile(r"\\bitem\\s+([0-9a-f]{8})\\b")'),
    ("P-ref-open", 'ITEM_REF = re.compile(r"\\(item\\s+([0-9a-f]{8})\\)")', 'ITEM_REF = re.compile(r"item\\s+([0-9a-f]{8})\\)")'),
    ("P-ref-close", 'ITEM_REF = re.compile(r"\\(item\\s+([0-9a-f]{8})\\)")', 'ITEM_REF = re.compile(r"\\(item\\s+([0-9a-f]{8})")'),
    ("P-span-pre", 'CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)', 'CODE_SPAN = re.compile(r"(`+)(?!`)'),
    ("P-span-open", 'CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)', 'CODE_SPAN = re.compile(r"(?<!`)(`+)'),
    ("P-span-body", '(?!`)[\\s\\S]*?(?<!`)\\1(?!`)")', '(?!`)[^\\n]*?(?<!`)\\1(?!`)")'),
    ("P-span-close", '[\\s\\S]*?(?<!`)\\1(?!`)")', '[\\s\\S]*?\\1(?!`)")'),
    ("P-span-post", '(?<!`)\\1(?!`)")', '(?<!`)\\1")'),
    ("P-span-run", '(?<!`)\\1(?!`)")', '(?<!`)`+(?!`)")'),
    ("P-group-dash", 'GROUP_TOK = re.compile(r"\\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\\Z")', 'GROUP_TOK = re.compile(r"\\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*\\Z")'),
    ("P-group-end", 'GROUP_TOK = re.compile(r"\\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\\Z")', 'GROUP_TOK = re.compile(r"\\A[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+")'),
    ("P-issue-end", 'ISSUE_TOK = re.compile(r"\\A#(\\d+)\\Z")', 'ISSUE_TOK = re.compile(r"\\A#(\\d+)")'),
    ("P-brief-name", 'BRIEF_TOK = re.compile(r"\\AO(\\d+)(?:-[a-z0-9][a-z0-9-]*)?\\Z")', 'BRIEF_TOK = re.compile(r"\\AO(\\d+)\\Z")'),
    ("P-brief-end", 'BRIEF_TOK = re.compile(r"\\AO(\\d+)(?:-[a-z0-9][a-z0-9-]*)?\\Z")', 'BRIEF_TOK = re.compile(r"\\AO(\\d+)(?:-[a-z0-9][a-z0-9-]*)?")'),
]
EQUIVALENT = {
    # A Carry: at a span's first character is impossible: that character is a backtick.
    "S-span-lo": "a span opens on a backtick, so no `Carry:` starts at a span's first offset",
    # gh returns a string body, and `items()` would raise on None, as the head's `or ""` avoids.
}


CUTS = {"split", "strip", "rstrip", "lstrip", "lower", "get", "match", "fullmatch", "findall", "finditer"}


def sites(src: str) -> list[tuple[int, int, str]]:
    """(start, end, label) character spans of every predicate the census owns:
    in PARSER, each `if`/conditional test, boolean operand (a trailing constant
    default, `x or ""`, is one site with its operand), comparison, slice or
    index (a string key is a field read, not one), cut or match call,
    `continue` and `break`, outside f-strings (a label, not a predicate); and
    each PATTERNS line."""
    tree = ast.parse(src)
    offs = [0]
    for ln in src.splitlines(keepends=True):
        offs.append(offs[-1] + len(ln))

    def span(n):
        return offs[n.lineno - 1] + n.col_offset, offs[n.end_lineno - 1] + n.end_col_offset

    out = []

    def add(n, fn, kind):
        a, b = span(n)
        text = src[a:b].split("\n", 1)[0].strip()[:60]
        out.append((a, b, f"{fn} l{n.lineno} {kind} {text}"))

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in PARSER:
            fmt = {id(x) for j in ast.walk(node) if isinstance(j, ast.JoinedStr) for x in ast.walk(j)}
            for s in (x for st in node.body for x in ast.walk(st) if id(x) not in fmt):
                if isinstance(s, (ast.If, ast.IfExp)):
                    add(s.test, node.name, "test")
                elif isinstance(s, ast.BoolOp):
                    vals = s.values
                    if isinstance(vals[-1], ast.Constant):
                        add(s, node.name, "default")
                        vals = vals[:-2]
                    for v in vals:
                        add(v, node.name, "operand")
                elif isinstance(s, ast.comprehension):
                    for i in s.ifs:
                        add(i, node.name, "filter")
                elif isinstance(s, ast.Compare):
                    add(s, node.name, "compare")
                elif isinstance(s, ast.Subscript) and not isinstance(s.ctx, ast.Store) and not (
                        isinstance(s.slice, ast.Constant) and isinstance(s.slice.value, str)):
                    add(s.slice, node.name, "slice")
                elif isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute) and s.func.attr in CUTS:
                    a, b = span(s)
                    out.append((offs[s.func.end_lineno - 1] + s.func.end_col_offset - len(s.func.attr), b,
                                f"{node.name} l{s.lineno} call .{s.func.attr}{src[a:b][-40:]}"))
                elif isinstance(s, (ast.Continue, ast.Break)):
                    add(s, node.name, type(s).__name__.lower())
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in PATTERNS for t in node.targets):
            add(node, "pattern", node.targets[0].id)
    return out


def changed(src: str, old: str, new: str) -> tuple[int, int]:
    """The character span of <src> a mutant rewrites."""
    at = src.index(old)
    p = 0
    while p < min(len(old), len(new)) and old[p] == new[p]:
        p += 1
    q = 0
    while q < min(len(old), len(new)) - p and old[-1 - q] == new[-1 - q]:
        q += 1
    return at + p, at + max(len(old) - q, p + 1)


def self_test() -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-I", str(F), "--self-test"], capture_output=True, text=True)
    out = r.stdout + r.stderr
    m = re.search(r"self-test: (\d+) checks, (\d+) failed", out)
    return (int(m.group(2)) if m else -1), out


def main(argv: list[str]) -> int:
    if subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", REL]).returncode:
        print(f"{REL} has uncommitted edits; the restore would erase them")
        return 2
    orig = F.read_bytes()
    src = orig.decode()
    want = set(argv)
    failed0, out0 = self_test()
    print(f"RESULT mutant=M0 failed={failed0} verdict={'baseline' if failed0 == 0 else 'BROKEN'}")
    if failed0:
        print(out0)
        return 2
    survived, spans = [], []
    try:
        for name, old, new in MUTANTS:
            if src.count(old) != 1:
                print(f"PATTERN NOT FOUND ONCE {name}: {old!r}")
                return 2
            spans.append(changed(src, old, new))
            if want and name not in want:
                continue
            F.write_text(src.replace(old, new))
            n, out = self_test()
            F.write_bytes(orig)
            verdict = ("killed" if n > 0 else "CRASHED" if n < 0
                       else "equivalent" if name in EQUIVALENT else "SURVIVED")
            print(f"RESULT mutant={name} failed={n} verdict={verdict}")
            for ln in out.splitlines():
                if ln.startswith("FAIL") or n < 0:
                    print(f"     {ln}")
            if verdict in ("SURVIVED", "CRASHED"):
                survived.append(name)
    finally:
        F.write_bytes(orig)
    census = sites(src)
    unmapped = [lab for a, b, lab in census if not any(x < b and a < y for x, y in spans)]
    for lab in unmapped:
        print(f"UNMAPPED {lab}")
    print(f"RESULT sites={len(census)} unmapped={len(unmapped)} mutants={len(MUTANTS)} "
          f"survived={len(survived)}")
    return 1 if survived or unmapped else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
