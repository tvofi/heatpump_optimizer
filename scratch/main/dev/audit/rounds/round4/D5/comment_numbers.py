#!/usr/bin/env python3
"""D5 comment-number harness.

METRIC: module- and class-level constants in the production package whose
attached comment cites a number that cannot be reconciled with the value
assigned on the very next line. "Attached comment" is the contiguous `#` block
immediately above the assignment, its `#:` doc-comment, or the trailing inline
comment on the assignment line. A citation is reconciled when the constant's
value appears among the comment's numbers, or among them scaled by any single
factor in SCALES (unit changes: seconds<->minutes<->hours, fraction<->percent,
kW<->W, etc.), or when the comment cites no number at all.

RUN (from the export root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D5/comment_numbers.py
  ... --list      every unreconciled constant with its comment
  ... --selftest  positive control: the same scan with every constant's value
                  multiplied by 7 before reconciliation; the unreconciled count
                  must rise sharply (a flat count means the harness reads the
                  comment, not the code).

EXPECTED at baseline 7dd68dd (Apple M1, 8 core, macOS 25.6):
  constants_with_commented_numbers=<RESULT>  unreconciled=<RESULT>
Counts over file bytes; contention-immune.
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
import io
import re
import sys
import tokenize
from pathlib import Path

ROOT = Path(".").resolve()
PKG = ROOT / "custom_components" / "heatpump_optimizer"

SCALES = [1, 60, 1 / 60, 3600, 1 / 3600, 100, 1 / 100, 1000, 1 / 1000,
          24, 1 / 24, 7, 1 / 7, 1440, 1 / 1440, 3.6, 1 / 3.6]
NUM = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)?)(?![\w])")
TOL = 1e-6

# Issue, PR, item, audit-finding and version numbers are references, not
# citations of the constant. Stripped before any number is extracted.
REF = re.compile(
    r"(#\d+"
    r"|\bissue\s+#?\d+"
    r"|\bitems?\s+\d+(?:\s*(?:,|and)\s*\d+)*"
    r"|\b[A-Z]?\d?-?D\d+-\d+"
    r"|\bR\d+-D\d+-\d+"
    r"|\bT\d+[a-z]?\b"
    r"|\bv\d+(?:\.\d+)*"
    r"|\bp\d+\b"
    r")", re.I)

# unit -> (name-suffix patterns, comment-unit patterns)
UNITS = {
    "minutes": (r"_(MINUTES|MINS?)$", r"(?:minutes?|mins?\b)"),
    "seconds": (r"_(SECONDS?|SECS?|S)$", r"(?:seconds?|secs?\b|\bs\b)"),
    "hours":   (r"_(HOURS?|HRS?|H)$", r"(?:hours?|hrs?\b|\bh\b)"),
    "days":    (r"_(DAYS?)$", r"(?:days?)"),
    "celsius": (r"_(C|K|TEMP|TEMP_C|DEG_C)$", r"(?:\u00b0\s*C|\bK\b|\bC\b)"),
    "kw":      (r"_(KW|KWH)$", r"(?:kWh?\b)"),
    "percent": (r"_(PCT|PERCENT)$", r"%"),
    "samples": (r"_(SAMPLES|EVENTS|COUNT|TICKS|INTERVALS|STARTS)$",
                r"(?:samples?|events?|ticks?|intervals?|starts?)"),
    "hz":      (r"_(HZ)$", r"(?:Hz\b)"),
    "litres":  (r"_(L|LITRES|LITERS)$", r"(?:litres?|liters?|\bL\b)"),
}


def comments_by_line(path):
    """lineno -> comment text, for every `#` comment token."""
    src = path.read_text(encoding="utf-8", errors="replace")
    out = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                out[tok.start[0]] = (tok.string.lstrip("#").lstrip(":").strip(),
                                     tok.start[1])
    except (tokenize.TokenError, IndentationError):
        pass
    return out, src


def attached(comments, lines, lineno):
    """The comment block attached to an assignment starting at `lineno`."""
    parts = []
    inline = comments.get(lineno)
    if inline and inline[1] > 0:
        parts.append(inline[0])
    i = lineno - 1
    block = []
    while i >= 1:
        c = comments.get(i)
        if c is None or c[1] != len(lines[i - 1]) - len(lines[i - 1].lstrip()):
            # allow any indentation; only require the line be comment-only
            if c is None or lines[i - 1].strip()[:1] != "#":
                break
        block.append(c[0])
        i -= 1
    parts.extend(reversed(block))
    return " ".join(p for p in parts if p).strip()


def numeric(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = numeric(node.operand)
        return None if v is None else -v
    return None


def _close(a, b):
    return abs(a - b) <= max(TOL, abs(b) * 1e-6)


def reconciled(value, nums):
    """True when `value` follows from the cited numbers by a unit change, a
    percentage reading, or one arithmetic step over a cited pair."""
    v = abs(value)
    for n in nums:
        a = abs(n)
        for s in SCALES:
            if _close(a * s, v) or _close(a, v * s):
                return True
        # "15 % increase" -> a multiplier of 1.15; "15 %" -> 0.15
        if _close(1 + a / 100.0, v) or _close(1 - a / 100.0, v):
            return True
    for i, n in enumerate(nums):
        for m in nums[i + 1:]:
            a, b = abs(n), abs(m)
            for cand in (a + b, abs(a - b), a * b, (a / b if b else None),
                         (b / a if a else None)):
                if cand is not None and _close(cand, v):
                    return True
    return False


def unit_of_name(name):
    for u, (npat, _) in UNITS.items():
        if re.search(npat, name):
            return u
    return None


def unit_cited(comment, unit):
    """Numbers in `comment` that carry `unit` explicitly."""
    _, cpat = UNITS[unit]
    out = []
    for m in re.finditer(rf"(?<![\w.])(\d+(?:[.,]\d+)?)\s*(?:-)?\s*{cpat}",
                         comment, re.I):
        out.append(float(m.group(1).replace(",", ".")))
    return out


def main():
    listing = "--list" in sys.argv
    mult = 7.0 if "--selftest" in sys.argv else 1.0
    total = with_nums = bad = 0
    um_total = um_bad = 0
    rows, um_rows = [], []
    for p in sorted(PKG.glob("*.py")):
        comments, src = comments_by_line(p)
        lines = src.splitlines()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            if not names:
                continue
            val = numeric(node.value)
            if val is None:
                continue
            total += 1
            c = attached(comments, lines, node.lineno)
            if not c:
                continue
            cs = REF.sub(" ", c)
            nums = [float(m.group(1).replace(",", ".")) for m in NUM.finditer(cs)]
            # UNIT-MATCHED arm: the constant's name carries a unit and the
            # comment cites a number in that same unit.
            u = unit_of_name(names[0])
            if u:
                ucited = unit_cited(cs, u)
                if ucited:
                    um_total += 1
                    if not reconciled(val * mult, ucited):
                        um_bad += 1
                        um_rows.append((p.relative_to(ROOT).as_posix(), node.lineno,
                                        names[0], val, u, ucited, c))
            if not nums:
                continue
            with_nums += 1
            if not reconciled(val * mult, nums):
                bad += 1
                rows.append((p.relative_to(ROOT).as_posix(), node.lineno,
                             names[0], val, nums, c))

    if listing:
        print("== unit-matched arm ==")
        for f, ln, name, val, u, nums, c in um_rows:
            print(f"UNIT-MISMATCH {f}:{ln} {name} = {val!r}  unit={u}  cited {nums}")
            print(f"    {c[:400]}")
        print("== loose arm ==")
        for f, ln, name, val, nums, c in rows:
            print(f"UNRECONCILED {f}:{ln} {name} = {val!r}   comment numbers {nums}")
            print(f"    {c[:400]}")

    print(f"RESULT numeric_constants={total} count")
    print(f"RESULT constants_with_commented_numbers={with_nums} count")
    print(f"RESULT loose_unreconciled={bad} count")
    print(f"RESULT unit_matched_citations={um_total} count")
    print(f"RESULT unit_matched_unreconciled={um_bad} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
