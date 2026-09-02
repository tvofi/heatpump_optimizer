#!/usr/bin/env python
# D5 harness: numbers cited in a comment or docstring that disagree with the
# constant beside them.
#
# Metric: for every module- or class-level assignment of a numeric literal in
# custom_components/heatpump_optimizer/*.py (NAME = 0.3, NAME: Final = 20,
# NAME = -2.0, NAME = 24 * 4), the comment attached to it -- the inline
# comment on the same line plus the contiguous comment block directly above --
# is scanned for numbers (after removing years, issue numbers, finding ids and
# version strings).  A constant is a MISMATCH when the comment cites at least
# one number and none of them equals the value under any of the conversions a
# comment legitimately uses (x1, percent<->fraction, minutes<->hours<->seconds,
# hours<->days, kW<->W, 15-minute steps per hour/day, 1-v, (v-1)*100, 1/v).
# Separately, every docstring that says "default N" / "defaults to N" is
# checked against the numeric defaults of the function it documents (Name
# defaults are resolved through the module and const.py).
# The vetted count removes entries listed in ALLOW with the reason each was
# judged not a disagreement; the raw count is printed beside it.
#
# Command:
#   PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D5/comment_numbers.py
#
# Expected (baseline c398fc84eec25fc44b60d74aae05b9a2da205884), all exact:
#   RESULT numeric_constants_scanned=432
#   RESULT constants_with_numbers_in_comment=65
#   RESULT constant_comment_mismatches_raw=17
#   RESULT constant_comment_mismatches_vetted=1   (open_meteo.py:69 _MAX_PLAUSIBLE_GHI)
#   RESULT docstring_default_claims=2
#   RESULT docstring_default_mismatches_raw=2
#   RESULT docstring_default_mismatches_vetted=0
#
# Machine: Apple M1 (8 cores, 8 GB), macOS 26.6, Python 3.13.1.
# Instrumented symbol: custom_components/heatpump_optimizer/const.py and every
# other production module's module/class-level numeric constants, read through
# ast and tokenize.
# Perturbation: change the value of any constant whose comment cites it (for
# example MANUAL_PLAN_WINDOW_HOURS in const.py from 20 to 21 while leaving its
# comment) -> constant_comment_mismatches_vetted goes UP by one.
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

import ast
import io
import re
import subprocess
import sys
import time
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / "custom_components" / "heatpump_optimizer"

# Vetted non-disagreements: "file:line NAME" -> reason.  Delete to see raw.
ALLOW = {
    "custom_components/heatpump_optimizer/accuracy.py:37 HISTORY_LENGTH": "672 = 14 days x 48 half-hour intervals; the comment cites the 30-minute interval and 'a fortnight', not a different value",
    "custom_components/heatpump_optimizer/const.py:709 CAPACITY_MIN_SAMPLES": "the cited 3 is the bucket width in degrees, a different quantity",
    "custom_components/heatpump_optimizer/const.py:713 CAPACITY_FLOOR_FRACTION": "the cited -15 is an outdoor temperature in an example, a different quantity",
    "custom_components/heatpump_optimizer/const.py:926 WATER_SPECIFIC_HEAT": "the block above is the section preamble on tank scaling, not a statement of this constant",
    "custom_components/heatpump_optimizer/const.py:936 BUFFER_INSULATION_U_BEST": "the block cites the ~2 W/K a real accumulator reaches, a derived quantity, not the U value",
    "custom_components/heatpump_optimizer/const.py:1090 ECONOMY_MIN_TEMP_WIDENING": "the block cites measured savings percentages of the mechanism, never the width itself",
    "custom_components/heatpump_optimizer/coordinator.py:464 PLAN_STALE_INTERVALS": "3 intervals x 30 minutes = the 90 minutes the comment names",
    "custom_components/heatpump_optimizer/defrost.py:105 DERATE_CONFIDENCE_SAMPLES": "the cited 1.0 is the blend target, a different quantity",
    "custom_components/heatpump_optimizer/drift.py:28 STAT_CAP_FACTOR": "the cited 8 is the hours of an example open window, a different quantity",
    "custom_components/heatpump_optimizer/grid_fee.py:46 IMPLAUSIBLE_FEE_SEK_PER_KWH": "the comment cites the plausible range 0.05-1.5 and the 25-oere example; 'above this' refers to the value",
    "custom_components/heatpump_optimizer/optimizer.py:102 _COMFORT_FLOOR_L1": "the cited 0.05 is an example breach, a different quantity",
    "custom_components/heatpump_optimizer/optimizer.py:113 _COMFORT_PULL_SINGLE_ZONE": "the block cites the bill and warmth measured when the pull was halved, not the coefficient",
    "custom_components/heatpump_optimizer/presets.py:142 upper_area_ratio": "the cited 0 is the single-storey case, a different value of the same field",
    "custom_components/heatpump_optimizer/price_model.py:63 QUARTER_ALPHA": "the block cites the 96/24-bin collapse and a factor of 1.0, not the alpha",
    "custom_components/heatpump_optimizer/price_model.py:67 QUARTER_FACTOR_MIN": "the cited 50-100 oere is an example ramp, a different quantity",
    "custom_components/heatpump_optimizer/tariff.py:165 _window_wsum": "an accumulator initialised to 0; the cited 30 is the meter spacing",
    "custom_components/heatpump_optimizer/thermal_model.py:182 comfort_ceiling": "the cited 1.0 and 29 describe the previous fallback and its failure, not this default",
    "custom_components/heatpump_optimizer/coordinator.py:2242 _build_plan_views": "'the default 15 minute resolution' is the optimizer's step (0.25 h), a config default, not a parameter of this function",
    "custom_components/heatpump_optimizer/const.py:648 DHW_DAYTYPE_BLEND_K": "'half day-type, half pooled' describes the blend ratio reached at K samples, not K",
    "custom_components/heatpump_optimizer/defrost.py:93 DERATE_MIN": "'less than half its rated output' is prose rounding of the 0.55 bound (noted in REPORT.md as an approximation)",
    "custom_components/heatpump_optimizer/defrost.py:120 DEFROST_DUTY_MAX": "'a third of its life defrosting' is prose rounding of the 0.3 bound (noted in REPORT.md as an approximation)",
    "custom_components/heatpump_optimizer/thermal_model.py:218 buffer_is_store": "'the default 35 L tank' is DEFAULT_BUFFER_TANK_VOLUME = 35, a config default, not a parameter of this property",
}

NUM = re.compile(r"(?<![\w.:/-])(-?\d+(?:[.,]\d+)?)(?![\w/:])")
STRIP = [
    re.compile(r"\bv?\d+\.\d+\.\d+\b"),          # version strings
    re.compile(r"#\d+"),                          # issue numbers
    re.compile(r"\bD(?:10|[0-9])-\d\d\b"),        # audit finding ids
    re.compile(r"\b(?:19|20)\d\d\b"),             # years
    re.compile(r"\b\d{1,2}:\d\d\b"),              # clock times
    re.compile(r"\b[A-Za-z_]+\d+[A-Za-z_]*\b"),   # identifiers with digits (ecl110, x2)
    re.compile(r"\bitems?\s+\d+(?:(?:,\s*|\s+and\s+)\d+)*"),  # backlog item numbers ("item 8", "items 11 and 15")
    re.compile(r"\bT\d[a-z]?\b"),                    # tranche ids (T4b)
]
# Count words only HELP a value match (a constant of 3 beside "Three hours");
# fraction words are quantitative claims and also TRIGGER a check.
HELPER_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
                "fifteen": 15, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
                "ninety": 90, "hundred": 100}
TRIGGER_WORDS = {"half": 0.5, "quarter": 0.25, "third": 1 / 3, "tenth": 0.1}


def footer(t_proc0, t_thr0):
    proc = time.process_time() - t_proc0
    thr = time.thread_time() - t_thr0
    tf = proc / thr if thr > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    swapins = -1
    try:
        vm = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5).stdout
        m = re.search(r"Swapins:\s+(\d+)", vm)
        if m:
            swapins = int(m.group(1))
    except Exception:  # noqa: BLE001
        pass
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={swapins}")


def numbers_in(text: str):
    """Return (triggering numbers, helper numbers) cited by a comment."""
    t = text
    for rx in STRIP:
        t = rx.sub(" ", t)
    trig, helpers = [], []
    for w, v in TRIGGER_WORDS.items():
        if re.search(r"\b" + w + r"\b", t, re.I):
            trig.append(float(v))
    for w, v in HELPER_WORDS.items():
        if re.search(r"\b" + w + r"\b", t, re.I):
            helpers.append(float(v))
    for m in NUM.finditer(t):
        s = m.group(1).replace(",", ".")
        try:
            trig.append(float(s))
        except ValueError:
            pass
    return trig, helpers


def close(a, b):
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def matches(value: float, cited: float) -> bool:
    v = value
    forms = [v, v * 100, v / 100, v * 60, v / 60, v * 3600, v / 3600, v * 24, v / 24,
             v * 1000, v / 1000, (1 - v) * 100, (v - 1) * 100, 1 - v, v - 1, v * 4, v / 4,
             v * 96, v / 96, v * 1440, v / 1440, v * 7, v / 7, v * 100 - 100,
             v * 30, v / 30, v * 15, v / 15, v * 48, v / 48]
    if v not in (0, 0.0):
        forms += [1 / v, 100 / v, 60 / v]
    return any(close(f, cited) for f in forms)


def literal_value(node):
    """Numeric value of a constant expression, or None."""
    try:
        val = ast.literal_eval(node)
    except Exception:  # noqa: BLE001
        # allow simple arithmetic on constants, e.g. 24 * 4, 60 * 60
        try:
            src = ast.unparse(node)
            if re.fullmatch(r"[\d.\s()+\-*/eE]+", src):
                val = eval(src, {"__builtins__": {}})  # noqa: S307 -- constants only
            else:
                return None
        except Exception:  # noqa: BLE001
            return None
    if isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    return None


def module_consts(path: Path):
    """NAME -> numeric value for module-level constants."""
    out = {}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return out
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if node.value is None:
                continue
            v = literal_value(node.value)
            if v is None:
                continue
            for t in targets:
                if isinstance(t, ast.Name):
                    out[t.id] = v
    return out


def main():
    t_proc0, t_thr0 = time.process_time(), time.thread_time()
    const_map = module_consts(PKG / "const.py")
    total_consts = 0
    with_numbers = 0
    mismatches = []
    doc_claims = 0
    doc_mismatches = []
    for path in sorted(PKG.glob("*.py")):
        rel = str(path.relative_to(ROOT))
        src = path.read_text(encoding="utf-8")
        lines = src.split("\n")
        comment_at = {}
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                comment_at[tok.start[0]] = tok.string.lstrip("#").strip()
        tree = ast.parse(src)
        local_consts = dict(const_map)
        local_consts.update(module_consts(path))

        def scan_body(body, scope):
            nonlocal total_consts, with_numbers
            for node in body:
                if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
                    v = literal_value(node.value)
                    if v is None:
                        continue
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    names = [t.id for t in targets if isinstance(t, ast.Name)]
                    if not names:
                        continue
                    total_consts += 1
                    ln = node.lineno
                    parts = []
                    inline = comment_at.get(node.end_lineno) or comment_at.get(ln)
                    if inline:
                        parts.append(inline)
                    k = ln - 1
                    block = []
                    while k >= 1 and k in comment_at and lines[k - 1].strip().startswith("#"):
                        block.append(comment_at[k])
                        k -= 1
                    parts.extend(reversed(block))
                    text = " ".join(parts)
                    cited, helpers = numbers_in(text)
                    if not cited:
                        continue
                    with_numbers += 1
                    if not any(matches(v, c) for c in cited + helpers):
                        key = f"{rel}:{ln} {names[0]}"
                        mismatches.append((rel, ln, scope, names[0], v, cited, text[:160], key in ALLOW, ALLOW.get(key, "")))
                elif isinstance(node, ast.ClassDef):
                    scan_body(node.body, node.name)

        scan_body(tree.body, "<module>")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                if not doc:
                    continue
                claims = re.findall(r"default(?:s)?(?:\s+(?:to|of|is|at|:))?\s*(?:of\s*)?(-?\d+(?:\.\d+)?)", doc, re.I)
                claims += re.findall(r"\(default\s*[:=]?\s*(-?\d+(?:\.\d+)?)", doc, re.I)
                if not claims:
                    continue
                defaults = []
                a = node.args
                for d in list(a.defaults) + [d for d in a.kw_defaults if d is not None]:
                    v = literal_value(d)
                    if v is None and isinstance(d, ast.Name):
                        v = local_consts.get(d.id)
                    if v is None and isinstance(d, ast.Attribute):
                        v = local_consts.get(d.attr)
                    if v is not None:
                        defaults.append(v)
                for c in claims:
                    doc_claims += 1
                    cv = float(c)
                    if not defaults or not any(matches(dv, cv) for dv in defaults):
                        key = f"{rel}:{node.lineno} {node.name}"
                        doc_mismatches.append((rel, node.lineno, node.name, cv, defaults, key in ALLOW, ALLOW.get(key, "")))

    print("CONSTANT / COMMENT number disagreements:")
    for rel, ln, scope, name, v, cited, text, vetted, why in mismatches:
        tag = f"  [vetted: {why}]" if vetted else ""
        print(f"  {rel}:{ln} [{scope}] {name} = {v:g}  comment cites {sorted(set(cited))}{tag}\n         | {text}")
    print()
    print("DOCSTRING 'default N' claims not matching a signature default:")
    for rel, ln, fn, cv, defaults, vetted, why in doc_mismatches:
        tag = f"  [vetted: {why}]" if vetted else ""
        print(f"  {rel}:{ln} {fn}() docstring says default {cv:g}; numeric defaults resolved: {defaults}{tag}")
    print()
    print(f"RESULT numeric_constants_scanned={total_consts} count")
    print(f"RESULT constants_with_numbers_in_comment={with_numbers} count")
    print(f"RESULT constant_comment_mismatches_raw={len(mismatches)} count")
    print(f"RESULT constant_comment_mismatches_vetted={sum(1 for m in mismatches if not m[7])} count")
    print(f"RESULT docstring_default_claims={doc_claims} count")
    print(f"RESULT docstring_default_mismatches_raw={len(doc_mismatches)} count")
    print(f"RESULT docstring_default_mismatches_vetted={sum(1 for m in doc_mismatches if not m[5])} count")
    footer(t_proc0, t_thr0)


if __name__ == "__main__":
    main()
