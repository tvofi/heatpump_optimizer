#!/usr/bin/env python3
# D14-s5 detector for bug class I5 ("docs, comments or a compliance checklist
# drift stale against the code"), the backticked-reference arm.
#
# METRIC: unresolved = backticked references that name nothing in the tracked
#   tree.  Two corpora:
#   docs      README.md + the user docs (docs/{architecture,automations,
#             configuration,dashboard-card,ecl110,how-it-works,setup}.md,
#             docs/setup/**): `path.ext[:line]` must exist (as given, or under
#             the package, docs/ or tests/); `snake_case[()]` must occur in the
#             tracked non-Markdown code text.
#   comments  every ``x``/`x` with an underscore or dot inside a comment or
#             docstring of custom_components/heatpump_optimizer/*.py: its last
#             dotted part must be a Python identifier (def/class/arg/attr/name/
#             import/keyword) in the tracked .py files, or occur in a non-docstring
#             string literal or the non-Python code text.
#   Count key: resolution against the tree's own AST/text, per reference.
# INSTRUMENTED SYMBOLS: the tree's AST (every tracked .py), README.md, docs/*.md.
# COMMAND (repo root):
#   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
#     tools/audit/round9/D14/s5/doc_refs.py [--perturb drop-symbol] [--list]
# PERTURBATION: --perturb drop-symbol removes `shortwave_radiation` and
#   `ThermalModel` from the resolution corpus (a rename the docs did not follow)
#   -> unresolved goes UP.
# EXPECTED (baseline 1936d5ca, box B9): docs_refs=303 docs_unresolved=4,
#   comment_refs=1282 comment_unresolved=16 (every one classified in REPORT.md).
# MACHINE: box B9 cloud container, CPython 3.14.0rc2.  BASELINE: 1936d5ca72a0.
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import io
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path.cwd()
DROP = {"shortwave_radiation", "ThermalModel"}


def tracked() -> list[str]:
    return subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                          text=True).stdout.split()


def corpus(files, drop):
    ids, strs, other = set(), set(), []
    for f in files:
        if f.startswith("tools/audit/") or not (ROOT / f).is_file():
            continue
        suf = Path(f).suffix
        if suf in (".js", ".mjs", ".json", ".yaml", ".yml", ".sh", ".txt", ".toml"):
            other.append((ROOT / f).read_text(errors="replace"))
        if suf != ".py":
            continue
        src = (ROOT / f).read_text(errors="replace")
        other.append(src if suf != ".py" else "")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        docs = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                    and n.body and isinstance(n.body[0], ast.Expr) \
                    and isinstance(getattr(n.body[0], "value", None), ast.Constant) \
                    and isinstance(n.body[0].value.value, str):
                docs.add(id(n.body[0].value))
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                ids.add(n.id)
            elif isinstance(n, ast.Attribute):
                ids.add(n.attr)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                ids.add(n.name)
                if hasattr(n, "args"):
                    ids.update(a.arg for a in n.args.args + n.args.kwonlyargs)
            elif isinstance(n, ast.alias):
                ids.update(n.name.split("."))
                if n.asname:
                    ids.add(n.asname)
            elif isinstance(n, ast.keyword) and n.arg:
                ids.add(n.arg)
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs:
                strs.add(n.value)
    blob = "\n".join(strs) + "\n" + "\n".join(other)
    for d in drop:
        ids.discard(d)
        blob = blob.replace(d, "")
    return ids, blob


def docs_refs(files, ids, blob):
    docs = ["README.md"] + [f"docs/{x}.md" for x in (
        "architecture automations configuration dashboard-card ecl110 how-it-works setup").split()]
    docs += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs/setup").rglob("*.md"))
    tok = re.compile(r"`([^`\n]+)`")
    n, bad = 0, []
    for d in docs:
        for i, line in enumerate((ROOT / d).read_text().splitlines(), 1):
            for t in tok.findall(line):
                t = t.strip()
                m = re.fullmatch(r"([A-Za-z_][\w./-]*\.(?:py|js|mjs|json|yaml|yml|md|sh|svg))(?::(\d+))?", t)
                if m:
                    n += 1
                    p = m.group(1)
                    if not any((ROOT / c).exists() for c in (
                            p, "custom_components/heatpump_optimizer/" + p, "docs/" + p, "tests/" + p)) \
                            and not any(f.endswith("/" + p) for f in files):
                        bad.append(f"{d}:{i} `{t}`")
                    continue
                m = re.fullmatch(r"([a-z][a-z0-9]*_[a-z0-9_]+)(\(\))?", t)
                if m:
                    n += 1
                    if m.group(1) not in blob and m.group(1) not in ids:
                        bad.append(f"{d}:{i} `{t}`")
    return n, bad


def comment_refs(ids, blob):
    tok = re.compile(r"``?([A-Za-z_][\w.]*)(?:\(\))?``?")
    n, bad = 0, []
    for p in sorted((ROOT / "custom_components/heatpump_optimizer").glob("*.py")):
        src = p.read_text()
        texts = [(t.start[0], t.string) for t in tokenize.generate_tokens(io.StringIO(src).readline)
                 if t.type == tokenize.COMMENT]
        for nd in ast.walk(ast.parse(src)):
            if isinstance(nd, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                d = ast.get_docstring(nd, clean=False)
                if d and nd.body:
                    texts.append((nd.body[0].lineno, d))
        for ln, t in texts:
            for m in tok.finditer(t):
                s = m.group(1)
                if "_" not in s and "." not in s:
                    continue
                n += 1
                last = s.split(".")[-1]
                if last in ids or s in blob or last in blob:
                    continue
                bad.append(f"{p.relative_to(ROOT)}:~{ln} ``{s}``")
    return n, bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["none", "drop-symbol"], default="none")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    import time
    c0, t0 = time.process_time(), time.thread_time()
    files = tracked()
    ids, blob = corpus(files, DROP if a.perturb == "drop-symbol" else set())
    dn, dbad = docs_refs(files, ids, blob)
    cn, cbad = comment_refs(ids, blob)
    print(f"RESULT docs_refs={dn} count")
    print(f"RESULT docs_unresolved={len(dbad)} count")
    print(f"RESULT comment_refs={cn} count")
    print(f"RESULT comment_unresolved={len(cbad)} count")
    if a.list:
        for b in dbad + cbad:
            print("  UNRESOLVED", b)
    c1, t1 = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={c1 / t1 if t1 else 1:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a")
    return 0


if __name__ == "__main__":
    sys.exit(main())
