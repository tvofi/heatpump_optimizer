"""V3 (leads) independent recheck of D6-s1-81: reads the two real HA core wheels'
homeassistant/core_config.py source directly by line-scan (not the finder's AST-walk of
Config.__init__), to confirm Config.currency's constructor default is "EUR" on both, and
separately confirms the README/currency.py sentences the claim quotes still exist verbatim.

Requires the two wheels already downloaded (this session used `pip download --python-version 3.14
--only-binary=:all:` since venv314 has no pip module and system pip3 is 3.11, which pypi refuses
for these specs) into a directory passed as argv[1].
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  tools/audit/round9/D6/verify-v3-leads/v3_currency_wheel_recheck.py /path/to/wheels/dir
Expected: currency_defaults=['EUR','EUR']; readme_claim_present=1; fallback_const=SEK.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: leads box (4-core Linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob
import sys
import time
import zipfile

t0, th0 = time.process_time(), time.thread_time()

wheels_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hpo-wheels-verify"
wheels = sorted(glob.glob(os.path.join(wheels_dir, "homeassistant-*.whl")))

defaults = []
for w in wheels:
    z = zipfile.ZipFile(w)
    src = z.read("homeassistant/core_config.py").decode()
    for line in src.splitlines():
        if "self.currency" in line and "=" in line and "self.currency =" not in line.replace(":", "="):
            pass
    hit = next((ln.strip() for ln in src.splitlines() if ln.strip().startswith("self.currency:")), None)
    defaults.append((os.path.basename(w), hit))

print(f"RESULT wheels_checked={len(wheels)} count")
for name, hit in defaults:
    print(f"  {name}: {hit}")
all_eur = all(hit is not None and '"EUR"' in hit for _, hit in defaults)
print(f"RESULT currency_defaults_all_EUR={int(all_eur)} of {len(defaults)}")

readme = open("README.md").read()
currency_py = open("custom_components/heatpump_optimizer/currency.py").read()
readme_claim_present = int("SEK when the instance" in readme)
fallback_is_sek = int('FALLBACK_CURRENCY = "SEK"' in currency_py)
print(f"RESULT readme_claim_present={readme_claim_present}")
print(f"RESULT fallback_const_is_SEK={fallback_is_sek}")

print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
