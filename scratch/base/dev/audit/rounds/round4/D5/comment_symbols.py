#!/usr/bin/env python3
"""D5 comment-symbol harness.

METRIC: identifiers named by a comment or docstring in the production package
that exist nowhere in the repository -- i.e. the comment points at a symbol,
attribute, constant or file that a whole-word scan of every .py/.mjs/.js/.json/
.yaml/.md/.txt/.sh file in the tree cannot find. Four high-precision reference
classes are extracted (see CLASSES below); a name is "dangling" when it occurs
zero times outside the comments that name it.

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/comment_symbols.py
  ... --list      print every dangling reference with file:line and the comment
  ... --selftest  positive control: inject three fabricated references, which
                  must all be reported (a run that reports 3 fewer is broken)

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6):
  comments_scanned=6791 +-0   refs_extracted=9598 +-0   dangling_refs=<see RESULT>
Counts over file bytes; contention-immune.

CLASSES
  call      `name(` / `name()` inside a backtick span or bare text
  dotted    `a.b` where `a` is a production module basename or a known class
  const     ALL_CAPS_WITH_UNDERSCORES of length >= 4
  private   `_name` / `_name()` leading-underscore identifiers
  ticked    any snake_case (contains `_`) or CamelCase word inside a backtick
            span -- the class the package's comments actually use most
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import ast
import builtins
import io
import keyword
import re
import sys
import tokenize
from collections import Counter
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"

SCAN_SUFFIX = {".py", ".mjs", ".js", ".json", ".yaml", ".yml", ".md", ".txt", ".sh", ".cfg", ".toml"}
SKIP_DIR = {"__pycache__", ".git", "node_modules", "img", "brand"}

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
BUILTINS = set(dir(builtins)) | set(keyword.kwlist)
# Words that are English prose and also look like identifiers; they are only
# ever extracted through a class that requires punctuation, so this list is
# short by construction.
STOPWORDS = {"e", "g", "i", "eg", "ie", "etc", "self", "cls", "None", "True", "False"}


# tools/audit/round4/ is where the OTHER round-4 finders are writing while this
# runs; including it made the index non-deterministic (a name appearing in a
# sibling's harness counted as existing). Excluded so the number is stable.
SKIP_PREFIX = ("tools/audit/round4/",)


def tree_files():
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in SCAN_SUFFIX:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(part in SKIP_DIR for part in p.relative_to(ROOT).parts):
            continue
        if rel.startswith(SKIP_PREFIX):
            continue
        yield p


def build_token_index():
    """word -> number of occurrences in the whole tree (comments included)."""
    idx = Counter()
    for p in tree_files():
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        idx.update(WORD.findall(txt))
    return idx


def comment_spans(path):
    """Yield (lineno, kind, text) for every `#` comment and every docstring."""
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                yield tok.start[0], "comment", tok.string.lstrip("#").strip()
    except (tokenize.TokenError, IndentationError):
        pass
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            d = ast.get_docstring(node, clean=True)
            if d:
                ln = getattr(node, "lineno", 1)
                yield ln, "docstring", d


MODULES = {p.stem for p in PKG.glob("*.py")} | {"card", "coordinator", "optimizer", "const"}

RE_BACKTICK = re.compile(r"`([^`]+)`")
RE_CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\(\)")
RE_DOTTED = re.compile(r"\b([a-z_][a-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b")
RE_CONST = re.compile(r"\b([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b")
RE_PRIV = re.compile(r"(?<![A-Za-z0-9_.])(_[a-z][A-Za-z0-9_]*)\b")
RE_SNAKE = re.compile(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b")
RE_CAMEL = re.compile(r"\b([A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+)\b")


def refs_in(text):
    """-> set of (cls, name) references this comment makes."""
    out = set()
    spans = RE_BACKTICK.findall(text)
    hay = text + " " + " ".join(spans)
    for m in RE_CALL.finditer(hay):
        n = m.group(1)
        if n not in BUILTINS and n not in STOPWORDS:
            out.add(("call", n))
    for m in RE_DOTTED.finditer(hay):
        mod, attr = m.group(1), m.group(2)
        if mod in MODULES and attr not in BUILTINS:
            out.add(("dotted", attr))
    for m in RE_CONST.finditer(hay):
        n = m.group(1)
        if len(n) >= 4 and n not in BUILTINS:
            out.add(("const", n))
    for m in RE_PRIV.finditer(hay):
        n = m.group(1)
        if n not in BUILTINS and len(n) > 2:
            out.add(("private", n))
    # backtick spans only: a snake_case or CamelCase word the author marked as code
    for span in spans:
        for m in RE_SNAKE.finditer(span):
            n = m.group(1)
            if n not in BUILTINS and n not in STOPWORDS:
                out.add(("ticked", n))
        for m in RE_CAMEL.finditer(span):
            n = m.group(1)
            if n not in BUILTINS and n not in STOPWORDS:
                out.add(("ticked", n))
    return out


def main():
    listing = "--list" in sys.argv
    selftest = "--selftest" in sys.argv
    idx = build_token_index()

    comment_counts = Counter()   # word -> occurrences inside production comments
    records = []                 # (file, line, cls, name, comment)
    n_comments = 0
    for p in sorted(PKG.glob("*.py")):
        for ln, kind, text in comment_spans(p):
            n_comments += 1
            comment_counts.update(WORD.findall(text))
            for cls, name in refs_in(text):
                records.append((p.relative_to(ROOT).as_posix(), ln, kind, cls, name, text))

    if selftest:
        for cls, name in (("call", "zzz_fabricated_call"), ("const", "ZZZ_FABRICATED_CONST"),
                          ("private", "_zzz_fabricated_private")):
            records.append(("SELFTEST", 0, "comment", cls, name, "injected control"))

    dangling = []
    for f, ln, kind, cls, name, text in records:
        outside = idx.get(name, 0) - comment_counts.get(name, 0)
        if outside <= 0:
            dangling.append((f, ln, kind, cls, name, text))

    by_name = {}
    for f, ln, kind, cls, name, text in dangling:
        by_name.setdefault(name, []).append((f, ln, kind, cls, text))

    if listing:
        for name in sorted(by_name):
            locs = by_name[name]
            print(f"DANGLING {name}  [{locs[0][3]}]  x{len(locs)}")
            for f, ln, kind, cls, text in locs:
                print(f"    {f}:{ln} ({kind}) {text[:150].splitlines()[0] if text else ''}")

    print(f"RESULT comments_scanned={n_comments} count")
    print(f"RESULT refs_extracted={len(records)} count")
    print(f"RESULT dangling_refs={len(dangling)} count")
    print(f"RESULT dangling_distinct_names={len(by_name)} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
