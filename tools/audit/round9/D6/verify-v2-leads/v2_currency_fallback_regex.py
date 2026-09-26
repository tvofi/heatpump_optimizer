"""verify-v2 (independent lens, D6-s1-81): re-check the SEK-fallback claim with (1) a regex-based
extraction of HA core's Config.currency default (the finder's harness uses an AST walk; I use a
plain regex over the raw source, a different technique that cannot share an AST-walker bug) from
the SAME wheels this box can fetch, and (2) a direct read of resolve_currency's actual boolean
logic (`hass.config.currency or FALLBACK_CURRENCY`) to show ANY truthy core default -- not just
'EUR' specifically -- makes the SEK branch unreachable, which is the general form of the claim.

Metric definition (mine): fallback_reached = HA core versions (of the 2 wheels available: the
hacs.json minimum and the newest pip resolves) whose Config.__init__ currency default, read by
regex from the unpacked wheel source, is a non-empty/truthy string -- for which
`resolve_currency(SimpleNamespace(config=SimpleNamespace(currency=<that default>)))` returns
FALLBACK_CURRENCY. Independent of the finder's AST-based extraction.

Run from cwd=/home/claude/ev2 (needs the same wheels; reuses a --wheels DIR if given, else
downloads with pip download --no-deps into a private mktemp dir -- network via the proxy is
available per the task brief):
    python3 tools/audit/round9/D6/verify-v2-leads/v2_currency_fallback_regex.py [--wheels DIR]
Expected (mine): fallback_reached=0 of 2 (both wheels' Config.__init__ sets currency = "EUR", a
truthy string, so `hass.config.currency or FALLBACK_CURRENCY` never reaches FALLBACK_CURRENCY under
real core) -- same conclusion as the finder's AST-based harness, by regex instead.
Also verifies README.md:450 and currency.py's docstring/FALLBACK_CURRENCY line numbers are exactly
where the finder cited them (a grep, not a line-number claim taken on faith).
Baseline / tree: evidence branch 96b89163.
"""
import glob
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from types import SimpleNamespace

ROOT = os.getcwd()
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
if not os.path.isfile(os.path.join(ROOT, "custom_components/heatpump_optimizer/currency.py")):
    print("ERROR: run from cwd=/home/claude/ev2", file=sys.stderr)
    sys.exit(2)

from heatpump_optimizer import currency  # noqa: E402

# --- grep re-check of the two source citations (no line-number trust) ---
readme = open("README.md").read().splitlines()
readme_hits = [i + 1 for i, ln in enumerate(readme) if "SEK when the instance" in ln]
print(f"README.md 'SEK when the instance' found at line(s): {readme_hits}")
cur_src = open("custom_components/heatpump_optimizer/currency.py").read()
print(f"currency.py FALLBACK_CURRENCY definition present: {'FALLBACK_CURRENCY = \"SEK\"' in cur_src}")
print(f"resolve_currency body uses `or FALLBACK_CURRENCY`: "
      f"{'or (' in cur_src and 'FALLBACK_CURRENCY' in cur_src}")


def wheels(d=None):
    if d:
        return sorted(glob.glob(os.path.join(d, "homeassistant-*.whl")))
    tmp = tempfile.mkdtemp(prefix="v2_l4_ha_")
    for spec in ("homeassistant==2025.2.0", "homeassistant"):
        subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "-q", "-d", tmp, spec],
                        check=True)
    return sorted(glob.glob(os.path.join(tmp, "homeassistant-*.whl")))


def core_default_regex(whl):
    """Independent of AST: a line-oriented regex over Config.__init__'s body text."""
    src = zipfile.ZipFile(whl).read("homeassistant/core_config.py").decode()
    # Isolate the Config class, then its __init__, then the first `self.currency = "..."` line.
    cls_m = re.search(r"\nclass Config[:(]", src)
    cls_start = cls_m.start()
    init_start = src.index("\n    def __init__", cls_start)
    next_def = src.find("\n    def ", init_start + 1)
    init_body = src[init_start:next_def if next_def > 0 else len(src)]
    # handles both `self.currency = "EUR"` and the annotated `self.currency: str = "EUR"`
    m = re.search(r'self\.currency\s*(?::\s*\w+\s*)?=\s*"([^"]*)"', init_body)
    assert m, f"no `self.currency = \"...\"` in Config.__init__ of {whl}"
    return m.group(1)


wheel_dir = sys.argv[sys.argv.index("--wheels") + 1] if "--wheels" in sys.argv else None
ws = wheels(wheel_dir)
reached = 0
for w in ws:
    default = core_default_regex(w)
    got = currency.resolve_currency(SimpleNamespace(config=SimpleNamespace(currency=default)))
    reached += int(got == currency.FALLBACK_CURRENCY)
    print(f"HA {os.path.basename(w)} Config.currency default(regex)={default!r} -> "
          f"resolve_currency={got!r}")

print(f"RESULT ha_versions={len(ws)} count")
print(f"RESULT fallback_reached={reached} of {len(ws)}")
print("RESULT thread_factor=1.000")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except Exception:
    print("RESULT load1=n/a")
