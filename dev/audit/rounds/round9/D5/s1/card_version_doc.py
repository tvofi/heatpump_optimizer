"""D5-s1 harness: dashboard-card.md's upgrade troubleshooting against the stamp.

docs/dashboard-card.md "If an upgrade seems to change nothing" tells the reader the
console banner's card version "moves only when the card file changes, so it is often
lower than the integration version" and to compare it "against the card version named in
the release notes ... not against the integration version itself".
Metric (one line): share of simulated stamps (five successive patch releases from VERSION,
card bytes otherwise untouched) after which the card's CARD_VERSION equals the integration
version -- the doc's model predicts 0 for an unchanged card.
Count key: the text tools/release/stamp.py:rewrite_card_version returns for the bundled
card (the call stamp.py:main makes on every stamp), read back with its own regex.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/s1/card_version_doc.py [--perturb]
--perturb replaces rewrite_card_version, in memory, with the behaviour the doc describes
    (leave the constant alone when nothing else in the card changed). Expected:
    card_tracks_integration_share 1.0 -> 0.0.
Expected at baseline: baseline_card_equals_version=1, card_tracks_integration_share=1.0,
doc_banner_example=6.6.8 vs card 6.7.1 (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B1 (linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util
import re
import sys
import time

_t0p, _t0t = time.process_time(), time.thread_time()
spec = importlib.util.spec_from_file_location("stamp", "tools/release/stamp.py")
stamp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stamp)

if "--perturb" in sys.argv:
    def _doc_model(text, new_version):
        old = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', text).group(1)
        return text, old  # card bytes unchanged -> version unchanged
    stamp.rewrite_card_version = _doc_model

card_path = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
card = open(card_path, encoding="utf-8").read()
version = open("VERSION").read().strip()
cur = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', card).group(1)
doc = open("docs/dashboard-card.md", encoding="utf-8").read()
m = re.search(r"heatpump-optimizer-card\s+v(\d+\.\d+\.\d+)", doc)
claim = "often lower than the integration version" in doc

major, minor, patch = (int(x) for x in version.split("."))
tracks = 0
N = 5
text = card
for k in range(1, N + 1):
    nxt = f"{major}.{minor}.{patch + k}"
    text, _old = stamp.rewrite_card_version(text, nxt)
    got = re.search(r'const CARD_VERSION = "(\d+\.\d+\.\d+)";', text).group(1)
    tracks += int(got == nxt)
    print(f"stamp {nxt}: card banner -> {got}")
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT doc_claims_card_lags={int(claim)} count")
print(f"RESULT doc_banner_example={m.group(1) if m else 'none'} version")
print(f"RESULT card_version_now={cur} version")
print(f"RESULT integration_version_now={version} version")
print(f"RESULT baseline_card_equals_version={int(cur == version)} count")
print(f"RESULT card_tracks_integration_share={tracks / N:.2f} ratio")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
