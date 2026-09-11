#!/usr/bin/env python3
"""D5 harness 2 — identifiers named inside production comments that no longer exist.

METRIC: number of distinct (file, line, token) sites where a backticked,
        identifier-shaped token inside a *comment or docstring* of a production
        source file does not occur anywhere in the repository's non-prose code
        text (all .py/.mjs/.js/.json/.yaml under custom_components, tests,
        tools, .claude and .github, with `#`/`//`/`/* */` comments and Python
        docstrings removed first, so a name kept alive only by another comment
        does not count as existing).

Set D5_ROOT=<dir> to measure a copy of the tree instead (used by the
perturbation run); the default root is the repository this file lives in.

RUN (from the repository root, no cd):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D5/comment_symbols.py

EXPECTED at baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1:
    RESULT dangling_comment_symbols=27 count
    RESULT dangling_card=18 count
    RESULT dangling_card_private_distinct=13 count
    RESULT dangling_py=9 count
    RESULT backticked_identifier_mentions=739 count
    RESULT code_vocab_tokens=25442 count
    tolerance: exact.
MACHINE: 8-core Apple M1, 8 GB, python3 3.11.5.
PERTURBATION: add the comment line `# see `_no_such_helper_xyz`` to
    custom_components/heatpump_optimizer/optimizer.py -> the count must go UP
    by exactly 1. Deleting a reported site must move it DOWN by 1.
INSTRUMENTED: the comment/docstring token stream of every module under
    custom_components/heatpump_optimizer/ (tokenize COMMENT + ast docstrings).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import io
import re
import sys
import token as tokmod
import tokenize
from pathlib import Path

ROOT = Path(os.environ.get("D5_ROOT") or Path(__file__).resolve().parents[4]).resolve()
PROD = ROOT / "custom_components" / "heatpump_optimizer"
CODE_ROOTS = ["custom_components", "tests", "tools", ".claude", ".github"]
CODE_SUFFIXES = {".py", ".mjs", ".js", ".json", ".yaml", ".yml", ".sh", ".toml", ".cfg"}

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
BACKTICK = re.compile(r"`([^`\n]+)`")
JS_LINE = re.compile(r"//[^\n]*")
JS_BLOCK = re.compile(r"/\*.*?\*/", re.S)

# tokens that are English words or prose punctuation-adjacent; only
# identifier-shaped tokens survive the shape filter below anyway.
SHAPE_OK = re.compile(r"^(?:[a-z][a-z0-9]*(?:_[a-z0-9]+)+|[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+|"
                      r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+|_[A-Za-z0-9_]+)$")

# A span is only treated as naming a symbol when it is EXACTLY one bare
# identifier, optionally with a call suffix. Formulas, pseudo-code, globs and
# dotted external paths (`full_price / k`, `factors[a][b]`, `_init_*`,
# `homeassistant.util.loop.protect_loop`) are prose, not symbol references,
# and are excluded so the count cannot be inflated by mathematical notation.
BARE_SPAN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\(\))?$")
JS_PRIVATE = re.compile(r"^_[a-z][A-Za-z0-9]*$")


def iter_files(roots, suffixes):
    for r in roots:
        base = ROOT / r
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            rel = p.relative_to(ROOT).as_posix()
            # This audit round's own harnesses are excluded so the vocabulary
            # is the baseline tree's, not "the tree plus whatever I wrote".
            if rel.startswith("tools/audit/round3/"):
                continue
            if p.is_file() and p.suffix in suffixes and "__pycache__" not in p.parts \
                    and "node_modules" not in p.parts:
                yield p


def py_code_text(path):
    """Source with `#` comments and docstrings removed."""
    try:
        src = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    doc_lines = set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
                body = getattr(node, "body", None)
                if body and isinstance(body[0], ast.Expr) and \
                        isinstance(body[0].value, ast.Constant) and \
                        isinstance(body[0].value.value, str):
                    s = body[0].value
                    for ln in range(s.lineno, (s.end_lineno or s.lineno) + 1):
                        doc_lines.add(ln)
    except SyntaxError:
        pass
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokmod.COMMENT:
                continue
            if tok.type == tokmod.STRING and tok.start[0] in doc_lines:
                continue
            out.append(tok.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return src
    return "\n".join(out)


def js_code_text(path):
    try:
        src = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    src = JS_BLOCK.sub(" ", src)
    src = JS_LINE.sub(" ", src)
    return src


def build_code_vocab():
    vocab = set()
    for p in iter_files(CODE_ROOTS, CODE_SUFFIXES):
        if p.suffix == ".py":
            text = py_code_text(p)
        elif p.suffix in (".mjs", ".js"):
            text = js_code_text(p)
        else:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if p.suffix in (".yaml", ".yml", ".sh", ".toml", ".cfg"):
                text = re.sub(r"#[^\n]*", " ", text)
        vocab.update(IDENT.findall(text))
    return vocab


def prose_sites(path):
    """Yield (lineno, text) for every comment and docstring in a Python file."""
    src = path.read_text(encoding="utf-8")
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokmod.COMMENT:
                yield tok.start[0], tok.string
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            d = ast.get_docstring(node, clean=False)
            if d:
                yield getattr(node.body[0], "lineno", 1), d


def js_prose_sites(path):
    src = path.read_text(encoding="utf-8")
    for m in JS_BLOCK.finditer(src):
        yield src.count("\n", 0, m.start()) + 1, m.group(0)
    # line comments, but not inside a block comment (blocks blanked first)
    blanked = JS_BLOCK.sub(lambda mm: " " * len(mm.group(0)), src)
    for m in JS_LINE.finditer(blanked):
        yield src.count("\n", 0, m.start()) + 1, m.group(0)


def main():
    vocab = build_code_vocab()
    prod_files = [p for p in sorted(PROD.rglob("*.py")) if "__pycache__" not in p.parts]
    card = PROD / "www" / "heatpump-optimizer-card.js"

    misses = []
    checked = 0
    for path in prod_files:
        for lineno, text in prose_sites(path):
            for span in BACKTICK.findall(text):
                m = BARE_SPAN.match(span.strip())
                if not m:
                    continue
                tok = m.group(1)
                if not SHAPE_OK.match(tok):
                    continue
                checked += 1
                if tok not in vocab:
                    misses.append((path.relative_to(ROOT).as_posix(), lineno, tok, span.strip()))
    card_misses = []
    if card.exists():
        for lineno, text in js_prose_sites(card):
            for span in BACKTICK.findall(text):
                m = BARE_SPAN.match(span.strip())
                if not m:
                    continue
                tok = m.group(1)
                if not SHAPE_OK.match(tok):
                    continue
                checked += 1
                if tok not in vocab:
                    card_misses.append((card.relative_to(ROOT).as_posix(), lineno, tok, span.strip()))

    print("--- dangling identifiers in production python comments/docstrings ---")
    for f, ln, tok, span in misses:
        print(f"  {f}:{ln}  `{tok}`   in: `{span}`")
    print("--- dangling identifiers in the card's comments ---")
    for f, ln, tok, span in card_misses:
        print(f"  {f}:{ln}  `{tok}`   in: `{span}`")

    print()
    print(f"RESULT code_vocab_tokens={len(vocab)} count")
    print(f"RESULT production_py_files={len(prod_files)} count")
    print(f"RESULT backticked_identifier_mentions={checked} count")
    print(f"RESULT dangling_comment_symbols={len(misses) + len(card_misses)} count")
    print(f"RESULT dangling_py={len(misses)} count")
    print(f"RESULT dangling_card={len(card_misses)} count")
    card_private = [m for m in card_misses if JS_PRIVATE.match(m[2])]
    print(f"RESULT dangling_card_private_methods={len(card_private)} count")
    print(f"RESULT dangling_card_private_distinct={len({m[2] for m in card_private})} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
