#!/usr/bin/env python3
"""D5-s5, D5.M4: row every comment/docstring unit of the seat's cells against the code it sits on.

Metric: per file, the count of D5 units (text_ledger.py units --dim D5) that an executed check
of the code contradicts -- a path, script, identifier or flag the unit names that the tree at the
root does not hold, or a constant the unit describes that the production module disagrees with.
Count key: the value the production seam delivers (the module attribute, the tree path, the
script's own name), never the unit's wording alone.
Also: C5 (D5-criteria.md) count of comment sentences over 40 words.

Run (export root, baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine: B11 container, 4 cpu):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s5/m4_ledger.py
  writes dev/audit/rounds/round11/D5/s5/ledger.tsv and runs text_ledger.py's check --plant on it.
  --file F            count one file only (and skip the ledger write)
  --edit 'F|OLD|NEW'  the perturbation: a one-line production edit applied in memory to F's text
  --set MOD.ATTR=V    the perturbation: set a production module attribute (int) before the checks
Expected at baseline (exact, counts): false_units_total=8 (prepr.sh 3; gh_comment.py, preflight.sh,
open_pr.sh, merge_train.py, orchestrator_tick.py 1 each), units_total=3631, units_examined=1385,
long_sentences_raw=743, long_sentences_strict=483 in 60 files, check_unrowed=0, check_plant_refused=1.
"""
import os
for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import argparse, ast, importlib, io, re, resource, sys, time, tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "tools/audit"))
import text_ledger as tl  # noqa: E402

TOP = ("tools/", "tests/", "dev/", "docs/", ".github/", ".claude/", "custom_components/", "blueprints/")
PATH = re.compile(r"(?<![\w$/.{@-])((?:\.github|\.claude|tools|tests|dev|docs|custom_components|blueprints)/[\w./-]*[\w/])")
BT = re.compile(r"`([^`\n]{2,80})`")
IDENT = re.compile(r"^(?:--)?[A-Za-z_]\w*(?:[.-][A-Za-z_]\w*)*(?:\(\))?$")
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]+)")
ASSIGN = re.compile(r"^\s*(?:export\s+|readonly\s+|local\s+)?([A-Za-z_]\w*)\s*(?::\s*\w+\s*)?=\s*['\"]?(-?\d+(?:\.\d+)?)['\"]?\s*(?:#.*)?$")
NUM = re.compile(r"(?<![\w.#/-])(\d+(?:\.\d+)?)(?![\w.]*[/\w])")
SENT_STRICT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z0-9`*\[(\"'$])")
SKIP_DIRS = {".git", "__pycache__", "node_modules"}


def strip_code(path, text):
    """The code of a file with its comments and docstrings removed (the existence corpus)."""
    suf = Path(path).suffix
    if suf == ".py":
        try:
            toks = [t.string for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type != tokenize.COMMENT]
            s = " ".join(toks)
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
                    f = node.body[0]
                    if isinstance(f, ast.Expr) and isinstance(f.value, ast.Constant) and isinstance(f.value.value, str):
                        s = s.replace(repr(f.value.value), " ")
            return s
        except (tokenize.TokenError, SyntaxError, ValueError):
            return text
    if suf == ".sh":
        return "\n".join("" if l.lstrip().startswith("#") else re.sub(r"(^|[\s;(])#(?![!{]).*$", r"\1", l) for l in text.split("\n"))
    if suf in (".js", ".mjs"):
        return re.sub(r"/\*.*?\*/", " ", "\n".join(re.sub(r"(^|\s)//.*$", r"\1", l) for l in text.split("\n")), flags=re.S)
    if suf in (".md", ".mdc", ".txt"):
        return ""
    return text


def walk_tree():
    files, dirs = set(), set()
    for d, ds, fs in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT)
        ds[:] = [x for x in ds if x not in SKIP_DIRS and not (rel == "dev/audit" and x == "rounds")]
        if rel != ".":
            dirs.add(rel)
        for f in fs:
            files.add(os.path.normpath(os.path.join(rel, f)))
    return files, dirs


def load_cells():
    return sorted({l.split("\t")[2] for l in (HERE / "cells.tsv").read_text().splitlines() if l.count("\t") >= 2})


def load_dispositions():
    out = {}
    p = HERE / "dispositions.tsv"
    for l in p.read_text().splitlines():
        if l.strip() and not l.startswith("#"):
            f, token, after, reason = l.split("\t")
            out.setdefault((f, token), []).append((after, reason))
    return out


def disposed(disp, f, token, norm):
    """The reason every occurrence of token in the unit is reviewed true, or None (keyed per occurrence)."""
    rules = disp.get((f, token))
    if not rules:
        return None
    reasons = []
    for m in re.finditer(re.escape(token), norm):
        tail = norm[m.end():m.end() + 80]
        hit = next((r for a, r in rules if a == "*" or a in tail), None)
        if hit is None:
            return None
        reasons.append(hit)
    return reasons[0] if reasons else None


def specific_checks(path, text, mods, edits=()):
    """Executed checks of production symbols, keyed on the unit text they judge: [(needle, cmd, result, false?)]"""
    out = []
    if path == "tools/audit/seat/orchestrator_tick.py":
        ot, mt = mods["orchestrator_tick"], mods["merge_train"]
        out.append(("The watcher heartbeat the tick assumes",
                    "orchestrator_tick.HEARTBEAT_SECONDS vs merge_train.HEARTBEAT_SECONDS",
                    f"tick assumes {ot.HEARTBEAT_SECONDS} s; the train beats every {mt.HEARTBEAT_SECONDS} s",
                    ot.HEARTBEAT_SECONDS != mt.HEARTBEAT_SECONDS))
    if path == "tools/audit/seat/merge_train.py":
        mt = mods["merge_train"]
        out.append(("`_outside_self_test` puts the real reader back",
                    "hasattr(merge_train, '_outside_self_test')",
                    f"defined={hasattr(mt, '_outside_self_test')}", not hasattr(mt, "_outside_self_test")))
    if path == "tools/pr/gh_comment.py":
        gc = mods["gh_comment"]
        doc = gc.in_shared_root.__doc__ or ""
        for old, new in edits:  # the perturbation reaches the hooked docstring as it reaches the file text
            doc = doc.replace(old, new, 1)
        m = re.search(r"`([\w/.]+prepr\.sh)`'s `(\w+)`", doc)
        if m:
            p, fn = m.group(1), m.group(2)
            has = (ROOT / p).is_file() and re.search(rf"^{fn}\(\)", (ROOT / p).read_text(), re.M) is not None
            out.append(("is the same predicate", "gh_comment.in_shared_root.__doc__ names a script and its function",
                        f"{p} exists={(ROOT / p).is_file()} defines {fn}={has}", not has))
    if path == "tools/audit/seat/open_pr.sh":
        first = text.split("\n")[1]
        m = re.match(r"#\s*([\w.-]+\.sh)\b", first)
        if m:
            name = m.group(1)
            ok = name == Path(path).name or (ROOT / Path(path).parent / name).is_file()
            out.append((f"{name} [--over-cap", "the usage line's script name vs the file and its directory",
                        f"usage names {name}; file is {Path(path).name}; {name} exists={ok}", not ok))
    if path == "tools/pr/prepr.sh":
        code = strip_code(path, text)
        named = set(re.findall(r"^\s*pr (\w[\w-]*) sh -c", code, re.M))
        out.append(("`attr-only` is their null control", "the self-test's `pr <name>` branches in prepr.sh",
                    f"attr-only defined={'attr-only' in named}; attronly defined={'attronly' in named}",
                    "attr-only" not in named))
    return out


def adjacent_constant(lines, line, text):
    end = line + text.count("\n")
    j = end
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j >= len(lines):
        return None
    m = ASSIGN.match(lines[j])
    if not m:
        return None
    nums = set(NUM.findall(re.sub(r"#\d+|[0-9a-f]{7,40}|\d{4}-\d\d-\d\d|R\d+|round\s*\d+|step \d+", " ", text)))
    if not nums:
        return None
    return m.group(1), m.group(2), sorted(nums)


def prose_words(text):
    return len(re.findall(r"[A-Za-z]{2,}", text))


def long_sentences(text):
    """(words, strict, sentence) for each sentence over 40 words. Raw: text_ledger's splitter over the
    unit. Strict: prose paragraphs only -- a blank line, a line indented 4+ spaces (usage, code), a
    list item, a fence/markup line or a table row (3+ inner spaces) ends a paragraph and is dropped;
    a sentence may also start at `$`."""
    body = re.sub(r"(?m)^\s*(#+|//+|/\*+|\*+/?)\s?", "", text)
    out = [(len(s.split()), False, s) for s in tl.sentences(body) if len(s.split()) > 40]
    paras, cur = [], []
    for l in body.split("\n"):
        if (not l.strip() or re.match(r"^\s{4,}\S|^\s*([*+-]|\d+[.)])\s", l)
                or re.search(r"~~~|```|<!--|^\s*\$ |\S {3,}\S", l)):
            paras.append(" ".join(cur)); cur = []
        else:
            cur.append(l.strip())
    paras.append(" ".join(cur))
    for p in paras:
        out += [(len(s.split()), True, s) for s in SENT_STRICT.split(" ".join(p.split())) if len(s.split()) > 40 and tl.WORDS.search(s)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--edit", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    t0c, t0t = time.process_time(), time.thread_time()

    sys.path[:0] = [str(ROOT / "tools/audit/seat"), str(ROOT / "tools/pr"), str(ROOT / "tests/hastub")]
    mods = {m: importlib.import_module(m) for m in ("orchestrator_tick", "merge_train", "gh_comment")}
    for s in a.set:
        k, v = s.split("=", 1)
        mod, attr = k.split(".", 1)
        setattr(mods[mod], attr, int(v))

    edits = {}
    for e in a.edit:
        f, old, new = e.split("|", 2)
        edits.setdefault(f, []).append((old, new))

    files = load_cells()
    if a.file:
        files = [a.file]
    tree_files, tree_dirs = walk_tree()
    corpus_words = set()
    for p in tree_files:
        if Path(p).suffix in (".png", ".jpg", ".gif", ".ico", ".zip", ".gz", ".woff", ".woff2"):
            continue
        try:
            corpus_words |= set(re.findall(r"-{0,2}[A-Za-z_][\w-]*", strip_code(p, (ROOT / p).read_text(encoding="utf-8"))))
        except (UnicodeDecodeError, OSError):
            pass
    corpus_words |= {w.lstrip("-") for w in corpus_words}
    disp = load_dispositions()

    def resolves(p):
        q = p.rstrip("/.")
        return q in tree_files or q in tree_dirs or any(x.startswith(q) for x in tree_files)

    rows = [tl.HEADER]
    false_by_file, examined_by_file, units_by_file, long_by_file, long_strict_by_file = {}, {}, {}, {}, {}
    false_units, long_list = [], []
    for f in files:
        text = (ROOT / f).read_text(encoding="utf-8")
        for old, new in edits.get(f, []):
            if old not in text:
                print(f"REFUSE edit text not found in {f}: {old!r}")
                return 2
            text = text.replace(old, new, 1)
        lines = text.split("\n")
        spec = specific_checks(f, text, mods, edits.get(f, []))
        for uid, line, kind, utext in tl.units_of(f, text, "D5"):
            units_by_file[f] = units_by_file.get(f, 0) + 1
            for n, strict, s in long_sentences(utext):
                if not strict:
                    long_by_file[f] = long_by_file.get(f, 0) + 1
                else:
                    long_strict_by_file[f] = long_strict_by_file.get(f, 0) + 1
                    long_list.append((uid, line, n, s))
            norm = " ".join(utext.split())
            cmd = f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s5/m4_ledger.py --file {f}"
            checks, bad = [], []
            for needle, ccmd, res, is_false in spec:
                if needle in norm:
                    checks.append(f"{ccmd}: {res}")
                    if is_false:
                        bad.append(res)
            paths = {m.group(1) for m in PATH.finditer(utext)}
            for p in sorted(paths):
                if any(c in p for c in "*{}$<>"):
                    continue
                if resolves(p):
                    checks.append(f"path {p} resolves")
                elif disposed(disp, f, p, norm):
                    checks.append(f"path {p} absent; {disposed(disp, f, p, norm)}")
                else:
                    checks.append(f"path {p} ABSENT")
                    bad.append(f"{p} is not in the tree")
            toks = {m.group(1).strip().rstrip("()") for m in BT.finditer(utext) if IDENT.match(m.group(1).strip())}
            toks |= {m.group(1) for m in FLAG.finditer(utext)}
            for t in sorted(toks):
                parts = [x for x in t.split(".") if x]
                if all(x in corpus_words for x in parts):
                    checks.append(f"name {t} in code")
                elif disposed(disp, f, t, norm):
                    checks.append(f"name {t} not in code; {disposed(disp, f, t, norm)}")
                elif not any(f"{t} " in c or c.endswith(t) for c in checks):
                    checks.append(f"name {t} NOT IN CODE")
                    bad.append(f"{t} is named by no code")
            if kind == "comment":
                ac = adjacent_constant(lines, line, utext)
                if ac:
                    checks.append(f"adjacent {ac[0]}={ac[1]} vs cited {ac[2]}: reviewed")
            if checks:
                examined_by_file[f] = examined_by_file.get(f, 0) + 1
                if bad:
                    false_by_file[f] = false_by_file.get(f, 0) + 1
                    false_units.append((uid, line, bad))
                    verdict = "stale" if any("not in the tree" in b or "exists=False" in b for b in bad) else "false"
                    rows.append([uid, str(line), "claim", cmd, "; ".join(checks)[:400], verdict, "; ".join(bad)[:300]])
                else:
                    rows.append([uid, str(line), "claim", cmd, "; ".join(checks)[:400], "true", ""])
            elif prose_words(utext) < 4:
                examined_by_file[f] = examined_by_file.get(f, 0) + 1
                rows.append([uid, str(line), "no-claim", "", "", "-", ""])
            else:
                rows.append([uid, str(line), "claim", cmd, "no path, script, identifier, flag or adjacent constant to execute against",
                             "unverifiable", "C1 prose truth not executed by this seat (not_reached)"])

    total_false = sum(false_by_file.values())
    if not a.quiet:
        for uid, line, bad in false_units:
            print(f"   false {uid} line {line}: {'; '.join(bad)}")
    for f in files:
        if false_by_file.get(f):
            print(f"RESULT false_units[{f}]={false_by_file[f]} units")
    print(f"RESULT false_units_total={total_false} units")
    print(f"RESULT files_with_false_unit={len(false_by_file)} files")
    print(f"RESULT units_total={sum(units_by_file.values())} units")
    print(f"RESULT units_examined={sum(examined_by_file.values())} units")
    print(f"RESULT long_sentences_raw={sum(long_by_file.values())} sentences")
    print(f"RESULT long_sentences_strict={sum(long_strict_by_file.values())} sentences")
    print(f"RESULT files_with_long_sentence_strict={len(long_strict_by_file)} files")
    if a.file:
        print(f"RESULT long_sentences_strict[{a.file}]={long_strict_by_file.get(a.file, 0)} sentences")

    if not a.file and not a.edit and not a.set:
        led = HERE / "ledger.tsv"
        led.write_text("\n".join("\t".join(c.replace("\t", " ").replace("\n", " ") for c in r) for r in rows) + "\n")
        per = HERE / "examined_by_file.tsv"
        per.write_text("".join(f"{f}\t{units_by_file.get(f, 0)}\t{examined_by_file.get(f, 0)}\t{long_strict_by_file.get(f, 0)}\n" for f in files))
        lng = HERE / "long_sentences.tsv"
        lng.write_text("".join(f"{u}\t{l}\t{n}\t{s[:300]}\n" for u, l, n, s in long_list))
        rc = tl.run_check(str(ROOT), files, "D5", led.read_text(), True, out=lambda s: print(s.replace("RESULT ", "RESULT check_")))
        print(f"RESULT check_rc={rc}")
    pc, tc = time.process_time() - t0c, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
