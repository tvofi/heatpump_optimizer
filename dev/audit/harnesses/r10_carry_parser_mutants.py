#!/usr/bin/env python3
"""O11 (#2404): every predicate of carry_audit.py's parser dies alone.

Written by the O11 fixer, round 5. Rounds 2 and 3 of #2404's review each found
a guard whose halves survived one at a time (the paren form and the segment
scope; then the segment's next-marker and line-end cuts), killed only when
reverted together. This drive enumerates the class rather than the instance,
over the whole parser: what an item is and when it is a finding (`items()`),
the marker grammar, the routing, and the ledger key.

  SITES    the census, read from the file's own AST: every predicate of the
           parser functions (PARSER) -- test, boolean operand, comparison,
           slice, cut or match call, continue and break (sites()) -- and each
           regex constant (PATTERNS).
  MUTANTS  single-site perturbations, each a one-occurrence replacement, and
           one per alternative of each PATTERNS regex and element of a
           PATTERNS tuple, generated (alternatives()). A quantifier or anchor
           is its own written mutant.

A site no mutant changes prints `UNMAPPED`; a mutant the self-test does not
kill prints `SURVIVED`, unless EQUIVALENT names why no input tells it apart.
Each mutant is applied alone, `carry_audit.py --self-test` run, and the file
restored byte for byte; the drive refuses a dirty file. Metric:

  RESULT mutant=<name> failed=<n> verdict=killed|SURVIVED|CRASHED|equivalent
  RESULT sites=<n> unmapped=<n> mutants=<n> survived=<n>

A mutant that kills only by crashing the self-test (failed=-1, no FAIL line)
counts as a survivor: no check named what it broke.

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
PARSER = ("items", "carry_segments", "carry_refs", "carry_dests", "seg_dests", "finding_rows", "audit",
          "ledger_unrouted")
PATTERNS = ("HEADING", "BULLET", "TABLE_SEP", "FRICTION_ENTRY", "VERDICT", "CARRY_SECTIONS", "NONE_ITEM",
            "TRAILER", "EVIDENCE_LINE", "EVIDENCE_HEADING", "DEFERRED", "NONBLOCK", "LEAD", "NOTE_HEADING", "BLOCK_HEADING", "CARRY", "ITEM_REF", "CODE_SPAN",
            "GROUP_TOK", "ISSUE_TOK", "BRIEF_TOK", "LEDGER_FINDING")

MUTANTS = [
    # items(): the lines read
    ("I-split", '    for ln in text.split("\\n"):', '    for ln in [text]:'),
    ("I-fence", '        if ln.lstrip().startswith(("```", "~~~")):', '        if ln.startswith(("```", "~~~")):'),
    ("I-fence-tilde", 'startswith(("```", "~~~")):', 'startswith(("```",)):'),
    ("I-fence-off", "            fenced = not fenced\n            continue", "            continue"),
    ("I-fence-keep", "            fenced = not fenced\n            continue", "            fenced = not fenced"),
    ("I-fenced", "        if not fenced and not ln.lstrip()", "        if not ln.lstrip()"),
    ("I-comment", ' and not ln.lstrip().startswith("<!--"):', ":"),
    ("I-comment-ws", 'not ln.lstrip().startswith("<!--")', 'not ln.startswith("<!--")'),
    # items(): flush
    ("I-flush-strip", '        body = "\\n".join(cur).strip()', '        body = "\\n".join(cur)'),
    ("I-flush-empty", "        if body and not TABLE_SEP", "        if not TABLE_SEP"),
    ("I-flush-sep", "        if body and not TABLE_SEP.match(body):", "        if body:"),
    # items(): the line loop
    ("I-heading", "        if h:\n", "        if False:\n"),
    ("I-heading-ws", "        h = HEADING.match(ln)", "        h = HEADING.match(ln.lstrip())"),
    ("I-heading-cont", "            section = h.group(2)\n            continue", "            section = h.group(2)"),
    ("I-blank", "        if not ln.strip():", "        if not ln:"),
    ("I-blank-para", '            if kind == "para":\n                flush()', '            if False:\n                flush()'),
    ("I-blank-bullet", '            elif kind == "bullet":\n                cur.append("")', '            elif False:\n                cur.append("")'),
    ("I-blank-cont", '                cur.append("")\n            continue', '                cur.append("")\n            pass'),
    ("I-table", '        if ln.lstrip().startswith("|"):', '        if ln.startswith("|"):'),
    ("I-table-off", '        if ln.lstrip().startswith("|"):', "        if False:"),
    ("I-table-cont", '            cur = [ln]\n            flush()\n            continue', '            cur = [ln]\n            flush()'),
    ("I-bullet", "        starts = bool(BULLET.match(ln)) or (", "        starts = False or ("),
    ("I-fr-sec", 'section.lower() == "friction" and FRICTION', 'True and FRICTION'),
    ("I-fr-lower", 'section.lower() == "friction"', 'section == "friction"'),
    ("I-fr-entry", ' and FRICTION_ENTRY.match(ln) and not ln.startswith("  "))', ' and not ln.startswith("  "))'),
    ("I-fr-indent", ' and not ln.startswith("  "))', ")"),
    ("I-starts", "        if starts:\n", "        if False:\n"),
    ("I-para-blank", '        elif cur[-1:] == [""] and not', '        elif True and not'),
    ("I-para-ix", '        elif cur[-1:] == [""] and not', '        elif cur[:1] == [""] and not'),
    ("I-para-indent", ' and not ln.startswith((" ", "\\t")):', ':'),
    ("I-para-tab", 'not ln.startswith((" ", "\\t")):', 'not ln.startswith((" ",)):'),
    ("I-kind-none", '            if kind is None:\n                kind = "para"', '            if False:\n                kind = "para"'),
    # items(): classification
    ("I-blocked-word", 'split(None, 3)[2:3] == ["blocked"]', 'split(None, 3)[2:3] == ["merge"]'),
    ("I-blocked-ix", 'split(None, 3)[2:3] == ["blocked"]', 'split(None, 3)[1:2] == ["blocked"]'),
    ("I-blocked-ws", 'text.split(None, 3)', 'text.split(" ", 3)'),
    ("I-first", '        first = re.sub(r"^[\\s>*_`-]*(?:\\d+[.)]\\s*)?[*_`]*", "", t)', '        first = t'),
    ("I-first-num", '(?:\\d+[.)]\\s*)?[*_`]*", "", t)', '[*_`]*", "", t)'),
    ("I-first-emph", '(?:\\d+[.)]\\s*)?[*_`]*", "", t)', '(?:\\d+[.)]\\s*)?", "", t)'),
    ("I-lead-reset", '        if it["kind"] != "bullet":\n            lead_flag = False', '        if False:\n            lead_flag = False'),
    ("I-inh-flag", "        inherited = lead_flag  #", "        inherited = False  #"),
    ("I-trailer", "        if TRAILER.match(first) or VERDICT.match(first):", "        if VERDICT.match(first):"),
    ("I-verdict-line", "        if TRAILER.match(first) or VERDICT.match(first):", "        if TRAILER.match(first):"),
    ("I-verdict", "        elif verdict:\n", "        elif False:\n"),
    # items(): evidence (r10-verdict-item-barrier)
    ("I-ev-line", "        elif EVIDENCE_LINE.match(first) or verdict and", "        elif verdict and"),
    ("I-ev-verdict", " or verdict and EVIDENCE_HEADING.match(sec):", " or EVIDENCE_HEADING.match(sec):"),
    ("I-ev-heading", " or verdict and EVIDENCE_HEADING.match(sec):", ":"),
    ("I-ev-match", "EVIDENCE_HEADING.match(sec)", "EVIDENCE_HEADING.search(sec)"),
    ("I-ev-lead", 'why = ("lead" if LEAD.match(first) else "evidence"', 'why = ("lead" if False else "evidence"'),
    ("I-ev-deferred", 'else "evidence" if DEFERRED.search(t)', 'else "evidence" if False'),
    ("I-ev-inh", 'else "under lead" if inherited else "")\n        elif verdict:', 'else "under lead" if False else "")\n        elif verdict:'),
    ("I-bsec-block", "            block_sec = BLOCK_HEADING.search(sec) and not", "            block_sec = True and not"),
    ("I-bsec-nonblock", " and not NONBLOCK.search(sec)\n", "\n"),
    ("I-nsec", "NONBLOCK.search(sec) if blocked_verdict else NOTE_HEADING.search(sec)", "NOTE_HEADING.search(sec)"),
    ("I-nsec-b", "NONBLOCK.search(sec) if blocked_verdict else NOTE_HEADING.search(sec)", "NONBLOCK.search(sec)"),
    ("I-why-nb", 'why = ("non-blocking" if NONBLOCK.search(t) else', 'why = ("non-blocking" if False else'),
    ("I-why-block", '"" if block_sec\n', '"" if False\n'),
    ("I-why-note", '"section" if note_sec else "lead" if LEAD.match(first)\n                   else "under', '"section" if False else "lead" if LEAD.match(first)\n                   else "under'),
    ("I-why-vlead", 'else "lead" if LEAD.match(first)\n                   else "under lead" if inherited else "")\n        elif', 'else "lead" if False\n                   else "under lead" if inherited else "")\n        elif'),
    ("I-why-vinh", 'else "under lead" if inherited else "")\n        elif sec', 'else "under lead" if False else "")\n        elif sec'),
    ("I-carry-sec", "        elif sec.lower() in CARRY_SECTIONS:", "        elif False:"),
    ("I-carry-lower", "        elif sec.lower() in CARRY_SECTIONS:", "        elif sec in CARRY_SECTIONS:"),
    ("I-none", '            why = "" if NONE_ITEM.match(t) else "section"', '            why = "section"'),
    ("I-bsec", '            why = ("section" if LEAD.search(sec) else', '            why = ("section" if False else'),
    ("I-blead", '"lead" if LEAD.match(first)\n                   else "under lead" if inherited else "")\n        flagged', '"lead" if False\n                   else "under lead" if inherited else "")\n        flagged'),
    ("I-binh", 'else "under lead" if inherited else "")\n        flagged', 'else "under lead" if False else "")\n        flagged'),
    ("I-lead-para", '        if it["kind"] == "para" and t.endswith', '        if t.endswith'),
    ("I-lead-colon", ' and t.endswith(":") and flagged:', ' and flagged:'),
    ("I-lead-flag", ' and t.endswith(":") and flagged:', ' and t.endswith(":"):'),
    ("I-id-ws", 'hashlib.sha1(re.sub(r"\\s+", " ", t).encode()).hexdigest()[:8]', 'hashlib.sha1(t.encode()).hexdigest()[:8]'),
    ("I-id-len", ".hexdigest()[:8]", ".hexdigest()[:7]"),
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
    ("D-hex", " or re.fullmatch(", " or 0 and re.fullmatch("),
    ("D-hex-arg", '", tok):\n            continue', '", tok[1:]):\n            continue'),
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
    # ledger_unrouted: the key and the marker
    ("L-key", "            if LEDGER_FINDING.search(ln) and not carry_dests(ln)]", "            if not carry_dests(ln)]"),
    ("L-carry", "            if LEDGER_FINDING.search(ln) and not carry_dests(ln)]", "            if LEDGER_FINDING.search(ln)]"),
    # the patterns: each anchor and quantifier (alternatives are generated)
    ("P-head-ws", 'HEADING = re.compile(r"^(#{1,6})\\s+', 'HEADING = re.compile(r"^(#{1,6})\\s*'),
    ("P-head-close", '(.*?)\\s*#*\\s*$")', '(.*?)\\s*$")'),
    ("P-tsep", 'TABLE_SEP = re.compile(r"^\\s*\\|?\\s*:?-{3,}")', 'TABLE_SEP = re.compile(r"^\\s*\\|?\\s*:?-{4,}")'),
    ("P-fentry", '`?[A-Za-z0-9_./#-]+`?\\s*:\\s*`?[a-z-]+`?\\s*:")', '`?[A-Za-z0-9_./#-]+`?\\s*:")'),
    ("P-verdict-sha", '[0-9a-f]{7,40}\\b")', '[0-9a-f]{40}\\b")'),
    ("P-later-compound", '|\\blater\\b(?!-)|', '|\\blater\\b|'),
    ("P-ev-word", 'EVIDENCE_HEADING = re.compile(r"evidence\\b", re.I)', 'EVIDENCE_HEADING = re.compile(r"evidence", re.I)'),
    ("P-block", 'BLOCK_HEADING = re.compile(r"\\bblock", re.I)', 'BLOCK_HEADING = re.compile(r"\\bblocked", re.I)'),
    # the patterns: the marker grammar's anchors and quantifiers
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


def alternatives(src: str) -> list[tuple[str, str, str]]:
    """One mutant per alternative of every PATTERNS regex, at any depth, and
    per element of a PATTERNS tuple: that alternative (or element) removed
    with one separator. Named `V-<PATTERN>-<alternative>`."""
    out = []
    for node in ast.parse(src).body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in PATTERNS):
            continue
        name, seg = node.targets[0].id, ast.get_source_segment(src, node)
        if isinstance(node.value, ast.Tuple):
            for e in node.value.elts:
                lit = ast.get_source_segment(src, e)
                new = seg.replace(lit + ", ", "", 1) if lit + ", " in seg else seg.replace(", " + lit, "", 1)
                out.append((f"V-{name}-{e.value}", seg, new))
            continue
        # the literal pieces of one pattern, joined: a group may span two of them
        pos = [m.start(1) + k for m in re.finditer(r'r"((?:[^"\\]|\\.)*)"', seg) for k in range(len(m.group(1)))]
        lit = "".join(seg[k] for k in pos)
        stack, i, cls = [[0, []]], 0, False
        spans = []
        while i < len(lit):
            c = lit[i]
            if c == "\\":
                i += 2
                continue
            if cls:
                cls = c != "]"
            elif c == "[":
                cls = True
            elif c == "(":
                k = re.match(r"\((?:\?(?:[:=!]|<[=!]))?", lit[i:])
                stack.append([i + len(k.group(0)), []])
            elif c == ")":
                st, seps = stack.pop()
                spans += list(zip([st] + [x + 1 for x in seps], seps + [i])) if seps else []
            elif c == "|":
                stack[-1][1].append(i)
            i += 1
        st, seps = stack[0]
        spans += list(zip([st] + [x + 1 for x in seps], seps + [len(lit)])) if seps else []
        for a, b in spans:
            a2, b2 = (a, b + 1) if b < len(lit) and lit[b] == "|" else (a - 1, b)
            gone = set(pos[a2:b2])
            out.append((f"V-{name}-{lit[a:b]}", seg, "".join(ch for k, ch in enumerate(seg) if k not in gone)))
    return out


EQUIVALENT = {
    "S-span-lo": "a span opens on a backtick, so no `Carry:` starts at a span's first offset",
}


CUTS = {"sub", "split", "strip", "rstrip", "lstrip", "lower", "get", "match", "fullmatch", "findall", "finditer"}


def sites(src: str) -> list[tuple[int, int, str]]:
    """(start, end, label) character spans of every predicate the census owns:
    in PARSER, each `if`/conditional test, boolean operand (a trailing constant
    default, `x or ""`, is one site with its operand), comparison, slice or
    index (a string key is a field read, not one), cut or match call,
    `continue` and `break`, outside f-strings and annotations (a label or a
    type, not a predicate); and
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
            fmt = {id(x) for j in ast.walk(node) for x in ast.walk(j) if isinstance(j, ast.JoinedStr)
                   or isinstance(j, ast.AnnAssign) and any(x is y for y in ast.walk(j.annotation))}
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
        for name, old, new in MUTANTS + alternatives(src):
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
    print(f"RESULT sites={len(census)} unmapped={len(unmapped)} mutants={len(spans)} "
          f"survived={len(survived)}")
    return 1 if survived or unmapped else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
