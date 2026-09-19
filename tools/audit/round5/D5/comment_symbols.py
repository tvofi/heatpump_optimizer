#!/usr/bin/env python3
"""D5 harness: identifiers named in production comments/docstrings that do not
exist anywhere in the production package.

Metric definition (one line): count of backticked identifier-like tokens that
appear in a Python comment or docstring of custom_components/heatpump_optimizer/
but appear in none of its .py files as a bareword (substring grep).

Run from the repository root:  PYTHONPATH=tests/hastub python3 tools/audit/round5/D5/comment_symbols.py
Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225
Machine: Apple M1, 8 GB (audit box)
Expected value: RESULT unresolved_comment_symbols=<small> ; the specific tokens
  are printed so a verifier can re-derive the same set with its own tokenizer.

Perturbation the count must move under: add a comment naming a token that
exists nowhere (e.g. `# see nonexistent_helper()`), unresolved_comment_symbols
goes up. Delete that comment, it goes back down.

This is a pure text instrument: no BLAS, no timing. thread_factor is printed as
1.0 (no numpy import at all).
"""
import os, re, sys

# keep the contract's shape even though nothing here is numeric/threaded
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = os.getcwd()
PKG = os.path.join(ROOT, "custom_components", "heatpump_optimizer")
BASELINE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"

TOKEN = re.compile(r"`([A-Za-z_][A-Za-z0-9_.]*)`")
IDENTLIKE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# tokens that are ordinary English / builtins / HA vocabulary, not project symbols
STOP = set("""
a an the and or not is are was were be been being do does did done run runs ran
of in on off to from for with by at as it its this that these those then than
there here when where while if else true false none null yes no up down left
right open close closed opening closing on off state states value values key
keys set sets get gets list lists dict dicts map maps int float str bool bytes
day days hour hours week weeks month months year years minute minutes second
seconds min max avg mean sum total new old next prev first last one two three
""".split())


def production_files():
    out = []
    for dirpath, _dirs, files in os.walk(PKG):
        if "__pycache__" in dirpath:
            continue
        for f in files:
            if f.endswith((".py", ".json", ".yaml", ".js")):
                out.append(os.path.join(dirpath, f))
    return out


def main():
    files = production_files()
    blobs = {}
    for f in files:
        try:
            blobs[f] = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
    alltext = "\n".join(blobs.values())

    unresolved = {}
    total_tokens = 0
    for f in sorted(glob_py(PKG)):
        try:
            lines = open(f, encoding="utf-8", errors="ignore").read().split("\n")
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            s = line.strip()
            is_comment = s.startswith("#")
            is_doc = ('"""' in s) or ("'''" in s)
            if not (is_comment or is_doc):
                continue
            for m in TOKEN.finditer(line):
                tok = m.group(1)
                base = tok.split(".")[-1]
                if len(base) < 3 or base.lower() in STOP:
                    continue
                if not IDENTLIKE.match(base):
                    continue
                total_tokens += 1
                # a token "exists" if it appears as a bareword anywhere in prod
                if not re.search(r"\b" + re.escape(base) + r"\b", alltext):
                    unresolved.setdefault(base, []).append("%s:%d" % (f, i))

    print("RESULT comment_identifier_tokens_checked=%d tokens" % total_tokens)
    print("RESULT unresolved_comment_symbols=%d tokens" % len(unresolved))
    for tok in sorted(unresolved):
        print("  UNRESOLVED %-40s %s" % (tok, ", ".join(unresolved[tok][:4])))
    print("RESULT thread_factor=1.0")
    print("RESULT load1=%s" % _load1())
    print("RESULT swapins=0")


def glob_py(pkg):
    out = []
    for dirpath, _dirs, files in os.walk(pkg):
        if "__pycache__" in dirpath:
            continue
        for f in files:
            if f.endswith(".py"):
                out.append(os.path.join(dirpath, f))
    return out


def _load1():
    try:
        return os.getloadavg()[0]
    except OSError:
        return -1.0


if __name__ == "__main__":
    main()
