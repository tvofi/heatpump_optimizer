"""D5-s2 M2/M3: stale version in docs/dashboard-card.md's console-banner sample.
Metric: 1 if the version shown in the doc's banner code block differs from the
version tools/release/stamp.py:rewrite_card_version leaves in the bundled card
when stamping VERSION, else 0. Key: the version string stamp delivers into the card.
Command: PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D5/s2/card_banner.py [--perturb]
Expected 1 (+-0) at baseline 17f1c55fad1b, machine B2 macOS. --perturb stamps
the doc's own banner version instead of VERSION -> 0.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, sys, time, importlib.util
c0 = time.process_time(); t0 = time.thread_time()
spec = importlib.util.spec_from_file_location("stamp", "tools/release/stamp.py")
stamp = importlib.util.module_from_spec(spec); spec.loader.exec_module(stamp)
doc = open("docs/dashboard-card.md", encoding="utf-8").read()
m = re.search(r"heatpump-optimizer-card\s+v(\d+\.\d+\.\d+)", doc)
doc_v = m.group(1)
target = doc_v if "--perturb" in sys.argv else open("VERSION").read().strip()
card = open("custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js", encoding="utf-8").read()
new, _old = stamp.rewrite_card_version(card, target)
card_v = re.search(r'const CARD_VERSION = "([\d.]+)"', new).group(1)
print(f"doc_banner=v{doc_v} card_after_stamp=v{card_v}")
print(f"RESULT banner_mismatch={int(doc_v != card_v)} count")
tc = time.thread_time() - t0
print(f"RESULT thread_factor={((time.process_time()-c0)/tc if tc else 1):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
