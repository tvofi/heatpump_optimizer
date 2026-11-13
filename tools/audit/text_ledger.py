#!/usr/bin/env python3
"""Enumerate every text unit a D5 or D6 seat must judge, and refuse a ledger that skips one.

Usage:
  text_ledger.py units --dim D6|D5 [--root DIR] FILE... | --seat D<k>-s<n> --repo R --ref X
  text_ledger.py check --dim D6|D5 LEDGER.tsv [--root DIR] [--plant] FILE... | --seat ...
  text_ledger.py --self-test

A unit is what one ledger row judges (dev/governance/dimensions/D6.md step 1, D5.md step 4):
D6: every sentence of a document (Markdown, HTML, YAML, text; a fenced code block is one unit),
every sentence of every JSON string leaf (strings.json, translations), and every string literal
of two or more words in Python and JavaScript, the user-visible text the code builds; D5: every
comment block (consecutive comment lines) and every docstring in Python, JavaScript and shell.
A file yielding none (an image, a stylesheet with no prose) is one unit of kind `file`, so every
file in a seat's cells has at least one row. The id is `<path>#<sha1 of the normalized text>[:10]`,
`.<k>` on its k-th repeat, so it survives a line move and a later round diffs ledgers by id.

The ledger is TSV with the header `unit line kind command result verdict truth`: kind `claim` or
`no-claim`; a claim carries the executed command, its result and a verdict (true, false, stale,
unverifiable), `truth` filled when the verdict is not true; a no-claim row carries verdict `-`.
`check` prints RESULT lines (units, rows, claims, each verdict, unrowed, orphan, malformed) and
exits 1 on any unrowed unit, orphan row or malformed row, naming each. `--plant` re-enumerates
with one sentence planted in a copy of the first file and exits 1 unless that unit is refused as
unrowed: the per-seat null control that an omission is visible.

The splitter is textual: a JavaScript regex literal holding a quote can merge two strings, and a
sentence ending in an abbreviation can split early. Either way the unit is still rowed, which is
the property this instrument owns; the truth of each row is the seat's, by executed check.
"""
import argparse, ast, hashlib, io, json, re, subprocess, sys, tempfile, tokenize
from pathlib import Path

VERDICTS = {"true", "false", "stale", "unverifiable"}
HEADER = ["unit", "line", "kind", "command", "result", "verdict", "truth"]
SENT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z0-9`*\[(\"'])")
BLOCK_START = re.compile(r"^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|\||>)")
WORDS = re.compile(r"[A-Za-z]{2,}")
PROSE = re.compile(r"[A-Za-z]{2,}[,.:;!?]?\s+[A-Za-z]{2,}")
CSS = re.compile(r"[\w-]+\s*:\s*[^;{}]+;")


def user_text(s):
    """The prose a literal shows a reader, or None: markup and interpolations dropped, CSS skipped."""
    if len(CSS.findall(s)) >= 2:
        return None
    t = re.sub(r"\$\{[^}]*\}|<[^>]*>", " ", s)
    return t if PROSE.search(t) else None


def sentences(text):
    t = " ".join(text.split())
    return [s for s in SENT.split(t) if WORDS.search(s)] if t else []


def prose_units(text):
    """(line, kind, text) for a document: sentences per paragraph or block line, a fence as one unit."""
    out, para, para_line, fence, fence_line = [], [], 0, None, 0
    def flush():
        nonlocal para
        if para:
            out.extend((para_line, "sentence", s) for s in sentences(" ".join(para)))
        para = []
    for n, line in enumerate(text.splitlines(), 1):
        if fence is not None:
            fence.append(line)
            if line.strip().startswith("```"):
                out.append((fence_line, "code", "\n".join(fence))); fence = None
            continue
        if line.strip().startswith("```"):
            flush(); fence, fence_line = [line], n
            continue
        if not line.strip() or BLOCK_START.match(line):
            flush()
        if line.strip():
            if not para:
                para_line = n
            para.append(line)
    flush()
    if fence is not None:
        out.append((fence_line, "code", "\n".join(fence)))
    return out


def html_units(text):
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", lambda m: "\n" * m.group(0).count("\n"), text)
    text = re.sub(r"(?i)<(br|p|div|li|h[1-6]|tr|td|th|section|article|header|footer|pre|ul|ol)\b[^>]*>", "\n\n", text)
    text = re.sub(r"<[^>]*>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return prose_units(text)


def yaml_units(text):
    lines = [re.sub(r"^(\s*-?\s*)[\w.-]+:\s?", r"\1", l) for l in text.splitlines()]
    return prose_units("\n".join(lines))


def json_units(text):
    out = []
    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, str):
            out.extend((0, "string", s) for s in sentences(v))
    walk(json.loads(text))
    return out


def py_units(text, dim):
    tree = ast.parse(text)
    docs = set()
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                docs.add(id(first.value))
                if dim == "D5":
                    out.append((first.lineno, "docstring", first.value.value))
    if dim == "D6":
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                s = "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in node.values)
                if user_text(s):
                    out.append((node.lineno, "string", s))
                for v in node.values:
                    docs.add(id(v))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs
                    and user_text(node.value)):
                out.append((node.lineno, "string", node.value))
        return out
    block, start, last = [], 0, -2
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.COMMENT and not tok.string.startswith("#!"):
            ln = tok.start[0]
            if block and ln != last + 1:
                out.append((start, "comment", "\n".join(block))); block = []
            if not block:
                start = ln
            block.append(tok.string); last = ln
    if block:
        out.append((start, "comment", "\n".join(block)))
    return out


def scan_c_like(text, hash_comments):
    """(line, kind, text) comments and string literals of JavaScript (or shell when hash_comments)."""
    comments, strings, i, n, line = [], [], 0, len(text), 1
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1; i += 1
        elif not hash_comments and text.startswith("//", i) or hash_comments and c == "#" and (i == 0 or text[i - 1] in " \t\n;(") and not text.startswith("#!", i) and not text.startswith("${#", i - 2):
            j = text.find("\n", i)
            j = n if j < 0 else j
            own = not text[text.rfind("\n", 0, i) + 1:i].strip()
            comments.append((line, text[i:j] if own else "\0" + text[i:j])); i = j
        elif not hash_comments and text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            comments.append((line, text[i:j])); line += text.count("\n", i, j); i = j
        elif c in "'\"`":
            j, start = i + 1, line
            while j < n and text[j] != c:
                if text[j] == "\\":
                    j += 1
                elif text[j] == "\n":
                    if c != "`" and not hash_comments:
                        break
                    line += 1
                j += 1
            strings.append((start, text[i + 1:j])); i = j + 1
        else:
            i += 1
    blocks, prev = [], None
    for ln, t in comments:
        if t.startswith("\0"):
            blocks.append((ln, t[1:])); prev = None
            continue
        if blocks and prev is not None and ln == prev + 1 and t.lstrip().startswith(("//", "#")) and blocks[-1][1].lstrip().startswith(("//", "#")):
            blocks[-1] = (blocks[-1][0], blocks[-1][1] + "\n" + t)
        else:
            blocks.append((ln, t))
        prev = ln + t.count("\n")
    return [(l, "comment", t) for l, t in blocks], [(l, "string", t) for l, t in strings if user_text(t)]


def units_of(path, text, dim):
    """[(unit_id, line, kind, text)] for one file under one dimension's rule."""
    suf = Path(path).suffix.lower()
    try:
        if dim == "D5":
            if suf == ".py":
                raw = py_units(text, "D5")
            elif suf in (".js", ".mjs", ".sh"):
                raw = scan_c_like(text, suf == ".sh")[0]
            else:
                raw = []
        elif suf == ".py":
            raw = py_units(text, "D6")
        elif suf in (".js", ".mjs"):
            raw = scan_c_like(text, False)[1]
        elif suf == ".json":
            raw = json_units(text)
        elif suf in (".html", ".htm"):
            raw = html_units(text)
        elif suf in (".yaml", ".yml"):
            raw = yaml_units(text)
        elif suf in (".md", ".txt", "") or suf == ".mdc":
            raw = prose_units(text)
        else:
            raw = []
    except (SyntaxError, ValueError, tokenize.TokenError):
        raw = prose_units(text)
    if not raw:
        raw = [(0, "file", path)]
    seen, out = {}, []
    for line, kind, t in raw:
        h = hashlib.sha1(" ".join(t.split()).encode()).hexdigest()[:10]
        k = seen.get(h, 0)
        seen[h] = k + 1
        out.append((f"{path}#{h}" + (f".{k}" if k else ""), line, kind, t))
    return out


def read(root, path):
    try:
        return (Path(root) / path).read_text(encoding="utf-8")
    except (UnicodeDecodeError, IsADirectoryError):
        return ""


def seat_files(seat, repo, ref):
    out = subprocess.check_output([sys.executable, str(Path(__file__).with_name("check_scopes.py")),
                                   "--repo", repo, "--ref", ref, "--seat", seat], text=True)
    return sorted({l.split("\t")[2] for l in out.splitlines() if l.count("\t") >= 2})


def enumerate_units(root, files, dim):
    return [u for f in files for u in units_of(f, read(root, f), dim)]


def parse_ledger(text):
    rows = [l.split("\t") for l in text.splitlines() if l.strip()]
    if not rows or rows[0] != HEADER:
        return None
    return rows[1:]


def check(units, rows):
    """Counts and refusals: every unit rowed, no orphan, every row well formed."""
    ids = {u[0] for u in units}
    by_id, malformed = {}, []
    for r in rows:
        if len(r) != len(HEADER):
            malformed.append(("\t".join(r)[:80], f"{len(r)} fields, want {len(HEADER)}")); continue
        unit, _line, kind, cmd, res, verdict, truth = r
        if kind == "claim":
            if not cmd.strip() or not res.strip():
                malformed.append((unit, "claim without an executed command and its result"))
            elif verdict not in VERDICTS:
                malformed.append((unit, f"verdict {verdict!r} not one of {sorted(VERDICTS)}"))
            elif verdict != "true" and not truth.strip():
                malformed.append((unit, f"verdict {verdict} without the truth"))
        elif kind == "no-claim":
            if verdict != "-":
                malformed.append((unit, "no-claim row with a verdict"))
        else:
            malformed.append((unit, f"kind {kind!r} not claim or no-claim"))
        by_id[unit] = r
    unrowed = sorted(ids - set(by_id))
    orphan = sorted(set(by_id) - ids)
    claims = [r for r in by_id.values() if len(r) == len(HEADER) and r[2] == "claim"]
    counts = {"units": len(ids), "rows": len(by_id), "claims": len(claims)}
    for v in sorted(VERDICTS):
        counts[v] = sum(r[5] == v for r in claims)
    counts.update(unrowed=len(unrowed), orphan=len(orphan), malformed=len(malformed))
    return counts, unrowed, orphan, malformed


PLANTED = {
    ".py": ('\n# Planted: this module never reads an entity.\nPLANTED_TEXT_LEDGER = "Planted user text never shown"\n'),
    ".js": '\n// Planted: this card never renders a chart.\nconst PLANTED = "Planted user text never shown";\n',
    ".mjs": '\n// Planted: this card never renders a chart.\nconst PLANTED = "Planted user text never shown";\n',
    ".sh": "\n# Planted: this script never exits non-zero.\n",
}


def plant(path, text):
    suf = Path(path).suffix.lower()
    if suf == ".json":
        try:
            d = json.loads(text)
            if isinstance(d, dict):
                d["planted_text_ledger"] = "The optimizer never writes a planted set-point."
                return json.dumps(d)
        except ValueError:
            pass
    return text + PLANTED.get(suf, "\n\nThe optimizer never writes a planted set-point.\n")


def run_check(root, files, dim, ledger_text, do_plant, out=print):
    rows = parse_ledger(ledger_text)
    if rows is None:
        out(f"REFUSE ledger header is not {' '.join(HEADER)}")
        return 1
    units = enumerate_units(root, files, dim)
    counts, unrowed, orphan, malformed = check(units, rows)
    for k, v in counts.items():
        out(f"RESULT {k}={v}")
    for u in unrowed[:50]:
        out(f"   unrowed {u}")
    for u in orphan[:50]:
        out(f"   orphan {u}")
    for u, why in malformed[:50]:
        out(f"   malformed {u}: {why}")
    rc = 1 if (unrowed or orphan or malformed) else 0
    if do_plant and files:
        f0 = files[0]
        planted = [u for u in units_of(f0, plant(f0, read(root, f0)), dim) if u[0] not in {x[0] for x in units}]
        refused = bool(planted) and not set(u[0] for u in planted) & {r[0] for r in rows}
        out(f"RESULT plant_refused={int(refused)} planted_units={len(planted)} in {f0}")
        rc |= 0 if refused else 1
    return rc


def self_test():
    ok, results = True, []
    def arm(name, cond):
        nonlocal ok
        ok &= bool(cond)
        results.append(f"   {'ok' if cond else 'FAIL'} {name}")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        files = {
            "docs/a.md": "# Title\n\nThe optimizer reads prices. It never sleeps.\n\n```\nrun me\n```\n- A list item claims one thing.\n",
            "c/strings.json": json.dumps({"config": {"step": {"user": {"data_description": {
                "space_setpoint_entity": "Optional. A number entity. The optimizer never writes a recommended space set-point."}}}}}),
            "c/mod.py": '"""Module doc."""\n# one\n# two\nx = 1\n\n# three\nMSG = "Pump duty is unavailable"\nf = f"Heat {x} now please"\n',
            "c/card.js": "// card comment\n// continued\nconst s = 'Next start in';\n/* block\n */\nconst u = 'http://x//y';\n",
            "t/run.sh": "#!/bin/bash\n# does a thing\necho \"#not a comment\" # trailing\nn=${#arr[@]}\n",
            "img/x.png": "",
        }
        for p, t in files.items():
            (root / p).parent.mkdir(parents=True, exist_ok=True)
            (root / p).write_text(t)
        u6 = enumerate_units(root, ["docs/a.md", "c/strings.json", "c/mod.py", "c/card.js", "img/x.png"], "D6")
        u5 = enumerate_units(root, ["c/mod.py", "c/card.js", "t/run.sh"], "D5")
        texts6 = [u[3] for u in u6]
        arm("the round-10 miss: a strings.json description sentence is a unit",
            "The optimizer never writes a recommended space set-point." in texts6)
        arm("markdown: two sentences, a fence, a list item",
            {"The optimizer reads prices.", "It never sleeps.", "- A list item claims one thing."} <= set(texts6)
            and any(u[2] == "code" for u in u6))
        arm("python user text: literal and f-string, docstring excluded",
            "Pump duty is unavailable" in texts6 and "Heat {} now please" in texts6 and "Module doc." not in texts6)
        arm("javascript user text, a URL's // is not a comment", "Next start in" in texts6)
        arm("a file with no text is one unit", [u[2] for u in u6 if u[0].startswith("img/")] == ["file"])
        k5 = {(u[0].split("#")[0], u[2], u[3]) for u in u5}
        arm("D5 python: docstring and two comment blocks",
            ("c/mod.py", "docstring", "Module doc.") in k5 and ("c/mod.py", "comment", "# one\n# two") in k5
            and ("c/mod.py", "comment", "# three") in k5)
        arm("D5 javascript: a line block and a block comment",
            ("c/card.js", "comment", "// card comment\n// continued") in k5 and any(t.startswith("/* block") for _, _, t in k5))
        sh = sorted(t for f, _, t in k5 if f == "t/run.sh")
        arm("D5 shell: shebang, quoted # and ${#} are not comments", sh == ["# does a thing", "# trailing"])
        files6 = ["docs/a.md", "c/strings.json", "c/mod.py", "c/card.js", "img/x.png"]
        good = "\n".join(["\t".join(HEADER)] + [
            "\t".join([u[0], str(u[1]), "claim", "grep -n x const.py", "x = 1", "true", ""]) if i % 2 else
            "\t".join([u[0], str(u[1]), "no-claim", "", "", "-", ""]) for i, u in enumerate(u6)])
        sink = []
        arm("null control: the complete ledger passes, and its plant is refused",
            run_check(root, files6, "D6", good, False, sink.append) == 0
            and run_check(root, files6, "D6", good, True, sink.append) == 0)
        miss = next(u[0] for u in u6 if "never writes a recommended" in u[3])
        dropped = "\n".join(l for l in good.splitlines() if not l.startswith(miss + "\t"))
        sink = []
        arm("a dropped row is refused by its unit id",
            run_check(root, files6, "D6", dropped, False, sink.append) == 1 and f"   unrowed {miss}" in sink)
        for name, sub in (("an unknown verdict", ("\ttrue\t", "\tmaybe\t")), ("a claim without a command", ("\tgrep -n x const.py\t", "\t\t")),
                          ("a false verdict without the truth", ("\ttrue\t", "\tfalse\t"))):
            bad = good.replace(*sub, 1)
            sink = []
            arm(f"{name} is refused", run_check(root, files6, "D6", bad, False, sink.append) == 1 and any("malformed" in s for s in sink))
        sink = []
        arm("an orphan row is refused", run_check(root, files6, "D6", good + "\nnone#0\t0\tno-claim\t\t\t-\t", False, sink.append) == 1)
        sink = []
        arm("a wrong header is refused", run_check(root, files6, "D6", good.replace("verdict", "verdikt", 1), False, sink.append) == 1)
        # The plant arm's own control: a ledger that already rows the planted
        # unit must fail --plant, or the arm passes whatever the ledger holds.
        p_units = [u for u in units_of("docs/a.md", plant("docs/a.md", files["docs/a.md"]), "D6") if u[0] not in {x[0] for x in u6}]
        rowed_plant = good + "".join("\n" + "\t".join([u[0], "0", "no-claim", "", "", "-", ""]) for u in p_units)
        sink = []
        arm("--plant fails a ledger that already rows the planted unit",
            run_check(root, files6, "D6", rowed_plant, True, sink.append) == 1 and "RESULT plant_refused=0" in "\n".join(sink))
        same = [u[0] for u in units_of("docs/a.md", "\n\n" + files["docs/a.md"], "D6") if u[2] != "code"]
        arm("ids survive a line move", same == [u[0] for u in u6 if u[0].startswith("docs/a.md") and u[2] != "code"])
    print("\n".join(results))
    print(f"text_ledger self-test: {len(results)} checks, {sum(r.startswith('   FAIL') for r in results)} failed")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["units", "check"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--dim", choices=["D5", "D6"])
    ap.add_argument("--root", default=".")
    ap.add_argument("--seat")
    ap.add_argument("--repo")
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--plant", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    if not a.cmd or not a.dim:
        ap.error("units|check and --dim are required")
    args = list(a.args)
    ledger = args.pop(0) if a.cmd == "check" and args else None
    files = seat_files(a.seat, a.repo or a.root, a.ref) if a.seat else args
    if a.cmd == "units":
        for uid, line, kind, t in enumerate_units(a.root, files, a.dim):
            print("\t".join([uid, str(line), kind, " ".join(t.split())[:200]]))
        sys.exit(0)
    if ledger is None:
        ap.error("check needs a ledger path")
    sys.exit(run_check(a.root, files, a.dim, Path(ledger).read_text(encoding="utf-8"), a.plant))


if __name__ == "__main__":
    main()
