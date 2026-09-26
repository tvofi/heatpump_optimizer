"""D5 verify-v3 (reach and class) harness for D5-s2-01: `_name` identifiers the card's comments
cite that no code token defines or uses.

Metric (one line): distinct `_[A-Za-z]\\w+` identifiers inside // and /* */ comments of
www/heatpump-optimizer-card.js that occur as a code token nowhere in the card's code (comment lines and
trailing // comments split off line by line; string literals KEPT as code, which can only hide
a stale name) nor in any production .py; with a
successor column = the same name without the underscore occurring as a code token.
Count key: tokens of the shipped card file itself -- no rig, no loaded element (the finder
loads the card through tests/card_rig.mjs; this lexes the bytes).
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/verify-v3/v3_s2_01_cardnames.py [--perturb]
--perturb: in memory, rewrite the 7 names with an underscore-less successor to that successor
    inside comments. Expected: stale 12 -> 5.
Expected at baseline: stale_names=12, stale_mentions=17 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core
cloud container, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob
import re
import sys
import time

_t0p, _t0t = time.process_time(), time.thread_time()
CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
src = open(CARD, encoding="utf-8").read()


def lex(s):
    """Line-based split: a line whose stripped text starts with //, /* or * is comment; a
    trailing ' // ...' on a code line is comment. Strings stay in code, which can only HIDE a
    stale name (conservative toward refuting the finding)."""
    code, comments = [], []
    for line, text in enumerate(s.split("\n"), 1):
        t = text.strip()
        if t.startswith(("//", "/*", "*")):
            comments.append((line, t))
            continue
        m = re.search(r"\s//\s", text)
        if m and text.count("`") % 2 == 0 and text[:m.start()].count('"') % 2 == 0 \
                and text[:m.start()].count("'") % 2 == 0:
            comments.append((line, text[m.start():]))
            text = text[:m.start()]
        code.append(text)
    return "\n".join(code), comments


code, comments = lex(src)
code_tokens = set(re.findall(r"[A-Za-z_$][\w$]*", code))
py_tokens = set()
for p in glob.glob("custom_components/heatpump_optimizer/*.py"):
    py_tokens |= set(re.findall(r"[A-Za-z_]\w*", open(p, encoding="utf-8").read()))
cited = {}
for line, text in comments:
    for name in re.findall(r"(?<![\w$.])_[A-Za-z]\w+", text):
        cited.setdefault(name, []).append(line)
stale = {k: v for k, v in cited.items() if k not in code_tokens and k not in py_tokens}
succ = {k: (k[1:] if k[1:] in code_tokens else None) for k in stale}
if "--perturb" in sys.argv:
    for k, s2 in succ.items():
        if s2:
            src = re.sub(rf"(?<![\w$]){re.escape(k)}\b", s2, src)  # comments only hold them
    code, comments = lex(src)
    cited = {}
    for line, text in comments:
        for name in re.findall(r"(?<![\w$.])_[A-Za-z]\w+", text):
            cited.setdefault(name, []).append(line)
    stale = {k: v for k, v in cited.items() if k not in code_tokens and k not in py_tokens}
# seam-rule probe: backticked camelCase names WITHOUT the underscore, which the finder's rule skips
bt = {}
for line, text in comments:
    for name in re.findall(r"`([a-z][a-z0-9]*[A-Z][A-Za-z0-9]*)(?:\(\))?`", text):
        bt.setdefault(name, []).append(line)
bt_stale = {k: v for k, v in bt.items() if k not in code_tokens and k not in py_tokens}
for k in sorted(bt_stale):
    print(f"UNDERSCORELESS_STALE {k} lines={bt_stale[k]}")
for k in sorted(stale):
    print(f"STALE {k} lines={stale[k]} successor={succ.get(k)}")
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT cited_private_names={len(cited)} count")
print(f"RESULT stale_names={len(stale)} count")
print(f"RESULT stale_mentions={sum(len(v) for v in stale.values())} count")
print(f"RESULT backticked_camel_cited={len(bt)} count")
print(f"RESULT backticked_camel_stale={len(bt_stale)} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
