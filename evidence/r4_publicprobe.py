"""r4_publicprobe: my own harness for #2320 round 4. A behaviour-preserving plant that re-spells a
PUBLIC import (price_model.py's `from .inputs import normalize_price_per_kwh`, and disinfection.py's
`from .inputs import UNBOUNDED, parse_bool`) as an import of the package's ANCESTOR namespace plus a
dotted attribute read. Same names, same calls; only the import statement moves.

  python3 r4_publicprobe.py <tree-with-tools> <pin-dir> [plant ...]
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
PIN = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(TREE / "tools" / "audit"))

from archscore import score, vector  # noqa: E402

PKGDIR = "custom_components/heatpump_optimizer"
ANC = "import custom_components as _cc\n"


def price_model(src: str) -> str:
    """price_model.py: `from .inputs import normalize_price_per_kwh` -> ancestor import + public read."""
    old = "from .inputs import normalize_price_per_kwh\n"
    assert src.count(old) == 1, "anchor"
    src = src.replace(old, ANC)
    return src.replace("normalize_price_per_kwh(", "_cc.heatpump_optimizer.inputs.normalize_price_per_kwh(")


def disinfection(src: str) -> str:
    """disinfection.py: `from .inputs import UNBOUNDED, parse_bool` -> ancestor import + public reads."""
    old = "from .inputs import UNBOUNDED, parse_bool\n"
    assert src.count(old) == 1, "anchor"
    src = src.replace(old, ANC)
    src = src.replace("parse_bool(", "_cc.heatpump_optimizer.inputs.parse_bool(")
    src = src.replace("UNBOUNDED", "_cc.heatpump_optimizer.inputs.UNBOUNDED")
    return src


def silent_mode_public(src: str) -> str:
    """The mechanism probe: silent_mode's reach spelled through the ancestor with a public leaf."""
    old = "from .optimizer import _utc_step_starts\n"
    assert src.count(old) == 1, "anchor"
    return src.replace(old, ANC).replace(
        "_utc_step_starts(", "_cc.heatpump_optimizer.optimizer.some_public_name(")



def price_model_desc_plain(src: str) -> str:
    """control: same public name, re-spelled as the plain dotted DESCENDANT import."""
    old = "from .inputs import normalize_price_per_kwh\n"
    assert src.count(old) == 1, "anchor"
    src = src.replace(old, "import custom_components.heatpump_optimizer.inputs\n")
    return src.replace("normalize_price_per_kwh(", "custom_components.heatpump_optimizer.inputs.normalize_price_per_kwh(")


def price_model_desc_from(src: str) -> str:
    """control: same public name, re-spelled as an absolute from-import of the descendant."""
    old = "from .inputs import normalize_price_per_kwh\n"
    assert src.count(old) == 1, "anchor"
    src = src.replace(old, "from custom_components.heatpump_optimizer import inputs\n")
    return src.replace("normalize_price_per_kwh(", "inputs.normalize_price_per_kwh(")

PLANTS = {
    "price_model_public_inputs": ("price_model.py", price_model),
    "disinfection_public_inputs": ("disinfection.py", disinfection),
    "silent_mode_public_leaf_MECHANISM_ONLY": ("silent_mode.py", silent_mode_public),
    "CONTROL_price_model_desc_plain": ("price_model.py", price_model_desc_plain),
    "CONTROL_price_model_desc_from": ("price_model.py", price_model_desc_from),
}


def main() -> int:
    names = sys.argv[3:] or list(PLANTS)
    with tempfile.TemporaryDirectory(prefix="r4pub-") as tmp:
        tmp = Path(tmp)
        base_tree = tmp / "base"
        shutil.copytree(PIN, base_tree)
        base = vector.measure(base_tree)
        for name in names:
            rel, fn = PLANTS[name]
            t = tmp / ("case_" + name)
            shutil.copytree(PIN, t)
            p = t / PKGDIR / rel
            p.write_text(fn(p.read_text()))
            cur = vector.measure(t)
            d = score.delta(base, cur)
            moved = {m: f"{base.get(m)}->{cur.get(m)}" for m in cur
                     if m in base and base.get(m) != cur.get(m) and not m.startswith("_")}
            print(f"RESULT plant {name} verdict={d['verdict']} dS={d['dS']:+.4f} moved={moved}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
