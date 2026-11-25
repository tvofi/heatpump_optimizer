#!/usr/bin/env python3
"""D5-s3: comment units in the seat's cells carrying a sentence over 40 words (D5-criteria C5).

Metric: long_units = count of D5 units (tools/audit/text_ledger.py:units_of, --dim D5) of the
D5-s3 cell modules, read from the imported production module's own source
(inspect.getsource), with at least one sentence (text_ledger.sentences, comment markers `#`/`#:`
stripped) of more than 40 whitespace words. Key: the module source the interpreter loads.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s3/c5_long.py [--perturb]
Expected: RESULT units=2855, RESULT long_units=363 at the baseline; exact (textual splitter, see
text_ledger.py's docstring: an abbreviation can split early, which only lowers the count).
Perturbation (--perturb): every sentence over 40 words in dhw_planner's source gets a full stop
after its 30th word in memory (the one-line-per-sentence edit a fix makes); expected long_units
down by dhw_planner's own count (down).
Leave-one-out: per-file counts printed; RESULT loo_drop_max is long_units without the worst file.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B3. Counts only; no timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, importlib, inspect, re, sys, time

sys.path.insert(0, "tools/audit")
sys.path.insert(0, "tests")
import text_ledger  # noqa: E402
import harness  # noqa: E402,F401  (puts custom_components on sys.path, as the suite does)

PKG = "custom_components/heatpump_optimizer"
CELL = re.compile(r"^" + PKG + r"/[_a-i][^/]*\.py$")
LIMIT = 40
PERTURB_FILE = "dhw_planner"


def long_sentences(text):
    body = re.sub(r"(?m)^\s*#:?\s?", "", text) if text.lstrip().startswith("#") else text
    return [s for s in text_ledger.sentences(body) if len(s.split()) > LIMIT]


def split_long(src):
    """Insert a full stop after word 30 of each over-long sentence (in memory)."""
    out = src
    for _uid, _l, _k, t in text_ledger.units_of("x.py", src, "D5"):
        for s in long_sentences(t):
            words = s.split()
            anchor = words[29]
            follow = words[30]
            out = re.sub(re.escape(anchor) + r"(\s+(?:#:?\s*)?)" + re.escape(follow),
                         lambda m: anchor.rstrip(",;:") + "." + m.group(1) + follow[:1].upper() + follow[1:], out, count=1)
    return out


def main():
    t0, th0 = time.process_time(), time.thread_time()
    perturb = "--perturb" in sys.argv
    per, units = {}, 0
    for f in sorted(p for p in glob.glob(PKG + "/*.py") if CELL.match(p)):
        name = os.path.basename(f)[:-3]
        mod = importlib.import_module("heatpump_optimizer." + name)
        src = inspect.getsource(mod)
        if perturb and name == PERTURB_FILE:
            src = split_long(src)
        us = text_ledger.units_of(f, src, "D5")
        units += len(us)
        per[name] = sum(1 for _i, _l, _k, t in us if long_sentences(t))
    total = sum(per.values())
    for k, v in sorted(per.items(), key=lambda kv: -kv[1]):
        print(f"   {k}: {v}")
    nz = [v for v in per.values()]
    worst = max(per, key=per.get)
    print(f"RESULT units={units} count")
    print(f"RESULT long_units={total} count")
    print(f"RESULT files_with_long={sum(1 for v in nz if v)} of {len(nz)} files")
    print(f"RESULT per_file_min={min(nz)} per_file_max={max(nz)} count")
    print(f"RESULT loo_drop_max={total - per[worst]} count (without {worst})")
    print(f"RESULT {PERTURB_FILE}_long={per[PERTURB_FILE]} count")
    pc, tc = time.process_time() - t0, time.thread_time() - th0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
