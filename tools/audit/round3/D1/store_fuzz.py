"""D1 -- a JSON string ``\"nan\"`` in thermal_learning.solar_aperture.n
wedges every coordinator cycle.

``float(\"nan\")`` raises none of TypeError/ValueError/OverflowError, so the
loader used to keep a non-finite ``n``. ``_learning_view`` then did
``int(self._solar_aperture[\"n\"])`` unguarded. A bare NaN token is not this
defect: orjson can neither write nor read one. Use the string route.

COMMAND (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D1/store_fuzz.py --repro thermal_learning:163

EXPECTED after the fix: ``wedge=0``. Before: ``wedge=1`` (ValueError).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
for _p in ("tests", "custom_components", "tests/hastub"):
    path = str(ROOT / _p)
    if path not in sys.path:
        sys.path.insert(0, path)

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)


def _coord() -> HeatPumpOptimizerCoordinator:
    return HeatPumpOptimizerCoordinator(
        FakeHass({}),
        FakeEntry(
            data={
                "tibber_token": "x",
                "weather_entity": "weather.home",
            }
        ),
    )


def repro_thermal_learning_163() -> int:
    """Position 163 in the census: solar_aperture.n as the JSON string nan."""
    payload = json.loads(
        '{"solar_aperture":{"n":"nan","mx":0.0,"my":0.0,"cov":0.0,"var":0.0,"scale":1.0}}'
    )
    coord = _coord()

    async def _load(_p=payload):
        return _p

    coord._thermal_learning_store.async_load = _load
    import asyncio

    asyncio.run(coord._async_load_thermal_learning())
    try:
        view = coord._learning_view()
    except (TypeError, ValueError, OverflowError) as err:
        print(f"wedge=1 error={type(err).__name__}:{err}")
        return 1
    samples = (view.get("solar_aperture") or {}).get("samples")
    print(f"wedge=0 samples={samples} n={coord._solar_aperture['n']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repro", default="thermal_learning:163")
    args = parser.parse_args()
    if args.repro != "thermal_learning:163":
        print(f"unknown repro {args.repro!r}", file=sys.stderr)
        return 2
    return repro_thermal_learning_163()


if __name__ == "__main__":
    sys.exit(main())
