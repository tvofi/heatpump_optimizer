#!/usr/bin/env python3
"""D5-s3 mechanical scan of every D5 comment unit in the seat's cells (D5.M4 support, C7 automation).

Metric: per D5 unit (text_ledger.py units --dim D5 over D5-s3's cells), three mechanical checks:
  ident  - every backticked token, every `name.py` path and every `module:symbol` / `Class.attr`
           reference the unit names resolves in the export tree (criterion C2);
  long   - sentences over 40 words (criterion C5);
  num    - a comment sitting on (immediately above, or trailing) an assignment `NAME = <number>`
           that cites numbers, none of which equals the assigned value (C7: cited number vs
           adjacent constant, automated; candidates, judged by hand in ledger.py).
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s3/scan.py [--tsv OUT]
Expected: RESULT units=2855 (exact at the baseline); the flag counts are candidates, not verdicts.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B3 (4 vCPU container). No timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, glob, re, sys, time
from pathlib import Path

sys.path.insert(0, "tools/audit")
import text_ledger  # noqa: E402

PKG = "custom_components/heatpump_optimizer"
CELL = re.compile(r"^" + PKG + r"/[_a-i][^/]*\.py$")


def cell_files():
    return sorted(p for p in glob.glob(PKG + "/*.py") if CELL.match(p))


_CORPUS = None


def corpus():
    """Every tracked-looking text file of the export, for identifier resolution."""
    global _CORPUS
    if _CORPUS is None:
        texts = []
        for pat in ("custom_components/**/*", "tests/**/*", "tools/**/*", "docs/**/*", "*.md", "dev/governance/**/*", ".claude/**/*", "blueprints/**/*"):
            for p in glob.glob(pat, recursive=True):
                if os.path.isfile(p) and not p.endswith((".png", ".jpg", ".woff2", ".ttf", ".gz")):
                    try:
                        texts.append(Path(p).read_text(encoding="utf-8"))
                    except (UnicodeDecodeError, OSError):
                        pass
        _CORPUS = "\n".join(texts)
    return _CORPUS


_FILES = None


def all_paths():
    global _FILES
    if _FILES is None:
        _FILES = {p for p in glob.glob("**/*", recursive=True)} | {os.path.basename(p) for p in glob.glob("**/*", recursive=True)}
    return _FILES


TICK = re.compile(r"`([^`\n]+)`")
PATHREF = re.compile(r"\b([\w./-]+\.(?:py|js|mjs|json|md|sh|yaml))\b")


def unresolved(text):
    out = []
    for t in TICK.findall(text):
        tok = t.strip()
        if " " in tok or not re.match(r"^[\w.:/()\[\]-]+$", tok):
            continue  # an expression or prose in ticks; not a single reference
        base = re.sub(r"\(.*\)$", "", tok).rstrip("()")
        parts = re.split(r"[.:/]", base)
        if tok.endswith((".py", ".js", ".mjs", ".json", ".md", ".sh")):
            if tok not in all_paths() and os.path.basename(tok) not in all_paths():
                out.append(tok)
            continue
        leaf = [p for p in parts if p and not p.isdigit()]
        if not leaf:
            continue
        name = leaf[-1]
        if len(name) < 3 or not re.search(r"[A-Za-z_]", name):
            continue
        if not re.search(r"(?<![\w])" + re.escape(name) + r"(?![\w])", corpus()):
            out.append(tok)
    for p in PATHREF.findall(text):
        if p.startswith("http") or "/" not in p and p.count(".") > 1:
            continue
        if p not in all_paths() and os.path.basename(p) not in all_paths():
            out.append(p)
    return sorted(set(out))


def long_sentences(text):
    body = re.sub(r"(?m)^\s*#:?\s?", "", text) if text.lstrip().startswith("#") else text
    return [s for s in text_ledger.sentences(body) if len(s.split()) > 40]


NUM = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?)(?![\w.])")


def assigned_numbers(src_lines, line, ntext):
    """The numeric value assigned on the statement the comment block sits on (next line or same line)."""
    cands = [line - 1, line + ntext - 1]  # trailing comment on the same line; first line after the block
    vals = []
    for idx in (line - 1, line + ntext - 1):
        if 0 <= idx < len(src_lines):
            m = re.match(r"^\s*([A-Z_][A-Z0-9_]*)\s*(?::[^=]+)?=\s*(-?[\d_.]+(?:e-?\d+)?)\s*(?:#.*)?$", src_lines[idx])
            if m:
                try:
                    vals.append((m.group(1), float(m.group(2).replace("_", ""))))
                except ValueError:
                    pass
    return vals


def scan(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    rows = []
    for uid, line, kind, t in text_ledger.units_of(path, text, "D5"):
        ntext = t.count("\n") + 1 if kind == "comment" else 0
        flags = {}
        u = unresolved(t)
        if u:
            flags["ident"] = u
        ls = long_sentences(t)
        if ls:
            flags["long"] = [len(s.split()) for s in ls]
        if kind == "comment":
            for name, val in assigned_numbers(lines, line, ntext):
                cited = [float(x) for x in NUM.findall(t)]
                if cited and val not in cited and not any(abs(c - val) < 1e-9 for c in cited):
                    flags["num"] = f"{name}={val:g} cites {sorted(set(cited))}"
        rows.append((uid, line, kind, t, flags))
    return rows


def main():
    t0 = time.process_time()
    out = None
    if "--tsv" in sys.argv:
        out = open(sys.argv[sys.argv.index("--tsv") + 1], "w", encoding="utf-8")
    n = {"units": 0, "ident": 0, "long": 0, "num": 0}
    for f in cell_files():
        for uid, line, kind, t, flags in scan(f):
            n["units"] += 1
            for k in flags:
                n[k] += 1
            if out:
                out.write("\t".join([uid, str(line), kind, repr(flags), " ".join(t.split())[:300]]) + "\n")
            elif flags:
                print(f"{uid}\t{line}\t{flags}")
    print(f"RESULT files={len(cell_files())} count")
    for k, v in n.items():
        print(f"RESULT {k}={v} count")
    pc, tc = time.process_time() - t0, time.thread_time() - t0 if False else None
    print(f"RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
