#!/usr/bin/env bash
# D10 strict-typing (Platinum) — two mypy --strict arms over the integration.
#
# METRIC: count of `: error:` lines mypy 2.3.1 --strict emits for
#   custom_components/heatpump_optimizer, split by where the line is LOCATED
#   (inside the package vs inside tests/hastub) and by error code.
#   arm A  MYPYPATH=tests/hastub  -- the fake Home Assistant the test suite runs on
#   arm B  homeassistant-stubs    -- a real PEP-561 stub set, Python 3.13
#   The two arms exist because the distinction between "an error in the
#   integration" and "an error the fake stub causes in the integration" has
#   been mis-stated on this project before.
#
# RUN (from the export root):
#   tools/audit/round4/D10/mypy_arms.sh
#
# TOOLCHAIN (built once; the script refuses if missing):
#   /private/tmp/hpo-d10-mypy/venv    python3.11 + mypy==2.3.1 + numpy scipy voluptuous aiohttp threadpoolctl
#   /private/tmp/hpo-d10-mypy13/venv  python3.13.1 + mypy==2.3.1 + homeassistant-stubs==2025.4.4 + scipy-stubs
#   NOTE: this is NOT tests/typing_budgets.json's pinned ruler
#   (homeassistant-stubs 2026.2.3 on Python >= 3.13.2); this box's newest
#   Python is 3.13.1, so the pin will not install. Arm B is an INDEPENDENT
#   corroboration of the recorded census, not a reproduction of it.
#
# EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697):
#   RESULT mypy_armB_real_stub_errors=0        (tolerance 0)
#   RESULT mypy_armA_hastub_total=542          (tolerance +/- 5: stub-shape dependent)
#   RESULT mypy_armA_in_package=470            (tolerance +/- 5)
#   RESULT mypy_armA_in_hastub=72              (tolerance +/- 5)
#   RESULT runtime_data_revealed_root=Any
#   RESULT runtime_data_revealed_coordinator=HeatPumpOptimizerCoordinator
# MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0.
set -u
[ -f custom_components/heatpump_optimizer/manifest.json ] || { echo "run from the export root" >&2; exit 2; }
A=/private/tmp/hpo-d10-mypy
B=/private/tmp/hpo-d10-mypy13
OUT="${D10_MYPY_OUT:-/private/tmp/hpo-d10-mypy/census.json}"
[ -x "$A/venv/bin/python" ] || { echo "arm A venv missing: $A/venv" >&2; exit 2; }
[ -x "$B/venv/bin/python" ] || { echo "arm B venv missing: $B/venv" >&2; exit 2; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1

MYPYPATH="$PWD/tests/hastub" "$A/venv/bin/python" -m mypy --strict \
  --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental \
  --cache-dir "$A/cacheA" custom_components/heatpump_optimizer > "$A/armA.txt" 2>&1
rcA=$?

env -u MYPYPATH -u PYTHONPATH "$B/venv/bin/python" -m mypy --strict \
  --warn-unused-ignores --show-error-codes --no-error-summary --no-incremental \
  --cache-dir "$B/cacheB" --python-version 3.13 \
  custom_components/heatpump_optimizer > "$B/armB.txt" 2>&1
rcB=$?

# reveal_type probe: what does `entry.runtime_data` type as, under each of the
# TWO HeatPumpOptimizerConfigEntry aliases this package defines?
mkdir -p "$B/probe"
cat > "$B/probe/probe_runtime_data.py" <<'PY'
from __future__ import annotations
from custom_components.heatpump_optimizer import (
    HeatPumpOptimizerConfigEntry as RootEntry,
)
from custom_components.heatpump_optimizer.coordinator import (
    HeatPumpOptimizerConfigEntry as CoordEntry,
)


def via_root(entry: RootEntry) -> None:
    reveal_type(entry.runtime_data)   # noqa: F821


def via_coordinator(entry: CoordEntry) -> None:
    reveal_type(entry.runtime_data)   # noqa: F821
PY
env -u MYPYPATH -u PYTHONPATH "$B/venv/bin/python" -m mypy --strict \
  --no-error-summary --no-incremental --cache-dir "$B/cacheP" --python-version 3.13 \
  "$B/probe/probe_runtime_data.py" > "$B/probe.txt" 2>&1

"$A/venv/bin/python" - "$A/armA.txt" "$B/armB.txt" "$B/probe.txt" "$OUT" "$rcA" "$rcB" <<'PY'
import json, re, sys, os
armA, armB, probe, out, rcA, rcB = sys.argv[1:7]
def errs(path):
    return [l for l in open(path, encoding="utf-8") if ": error:" in l]
a, b = errs(armA), errs(armB)
in_pkg = lambda ls: sum(1 for l in ls if l.startswith("custom_components/heatpump_optimizer/"))
in_stub = lambda ls: sum(1 for l in ls if "tests/hastub" in l.split(":", 1)[0])
code = re.compile(r"\[([a-z-]+)\]\s*$")
bycode = {}
for l in a:
    m = code.search(l.rstrip())
    bycode[m.group(1) if m else "no-code"] = bycode.get(m.group(1) if m else "no-code", 0) + 1
rev = re.findall(r'Revealed type is "(.+)"', open(probe, encoding="utf-8").read())
census = {
    "hastub_total": len(a), "hastub_in_pkg": in_pkg(a), "hastub_in_stub": in_stub(a),
    "hastub_by_code": dict(sorted(bycode.items(), key=lambda kv: -kv[1])),
    "real_stub_errors": len(b), "rcA": int(rcA), "rcB": int(rcB),
    "revealed_root": rev[0] if rev else "(none)",
    "revealed_coordinator": rev[1] if len(rev) > 1 else "(none)",
}
json.dump(census, open(out, "w"), indent=2)
for k in ("hastub_total", "hastub_in_pkg", "hastub_in_stub", "real_stub_errors"):
    print(f"RESULT mypy_{k}={census[k]} error_lines")
print(f"RESULT runtime_data_revealed_root={census['revealed_root']}")
print(f"RESULT runtime_data_revealed_coordinator={census['revealed_coordinator']}")
print("RESULT hastub_by_code=" + json.dumps(census["hastub_by_code"]))
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT thread_factor=n/a (counts, not timings)")
print(f"wrote {out}")
PY
