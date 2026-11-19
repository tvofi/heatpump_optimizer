#!/usr/bin/env python3
"""Every vendor, model or integration name in the user-facing text.

    python3 dev/audit/harnesses/vendor_text_census.py [--root DIR] [--counts]

The user-facing surface is `README.md`, `docs/` (less `docs/design/`, the
dated design notes, and the figure generators under `docs/img/`), the
integration's `strings.json` and `translations/*.json` (values only, each
reported at its key path), the card's `www/*.js` and `services.yaml`. Each
line or JSON value is matched against `BRANDS`, case-insensitively, as a
whole word: a name glued to `_` or a letter (`ecl110_displace_set_topic`, an
option key or entity id) is an identifier, not prose, and is not a hit.

One line per hit: `path:locator<TAB>brand<TAB>excerpt`. `--counts` prints
only `brand<TAB>count` lines and a `total<TAB>N` line. Exit 0 always: this is an
enumerator whose output a seat rules hit by hit (an example of a generic
shape, a real restriction, or a leftover), not a gate.

`BRANDS` was built from every capitalised token of the same surface, read
by hand at main b3831ff64e; a name it lacks is a hit this census misses, so
a new vendor named in the text joins the list in the same change.

Perturbation: add the word `Thermia` to any README line and `--counts`
prints `thermia 1` and a total one higher.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BRANDS = (
    "Luxtronik", "Danfoss", "ECL110", "ECL", "Tibber", "Nord Pool",
    "ENTSO-E", "Open-Meteo", "Met.no", "Daikin", "NIBE", "Novelan",
    "Alpha Innotec", "Stiebel Eltron", "Stiebel", "Vaillant", "Panasonic",
    "Mitsubishi", "Thermia", "Viessmann", "Bosch", "Homey", "Rotenso",
    "Windmi", "GCHV", "Tuya", "Vattenfall", "Ellevio", "Shelly", "Tado",
    "ESPHome", "Modbus", "Zigbee", "ApexCharts", "Bouni", "EKMBDXA",
    "S1256PC", "LWDV", "GWF", "Kamstrup", "Smart Home Interface", "SHI",
)
_PATTERN = re.compile(
    r"(?<![\w])("
    + "|".join(re.escape(b).replace(r"\ ", r"[ -]?") for b in sorted(BRANDS, key=len, reverse=True))
    + r")s?(?![\w])",
    re.IGNORECASE,
)
_CANON = {b.lower().replace(" ", ""): b for b in BRANDS}


def _canon(word: str) -> str:
    return _CANON.get(re.sub(r"[ -]", "", word.lower()), _CANON.get(word.lower(), word))


def _surface(root: Path) -> list[str]:
    files = subprocess.run(
        ["git", "-C", str(root), "ls-files", "README.md", "docs",
         "custom_components/heatpump_optimizer/strings.json",
         "custom_components/heatpump_optimizer/translations",
         "custom_components/heatpump_optimizer/www",
         "custom_components/heatpump_optimizer/services.yaml"],
        check=True, capture_output=True, text=True,
    ).stdout.split()
    return [
        f for f in files
        if not f.startswith(("docs/design/", "docs/img/"))
        and f.endswith((".md", ".json", ".js", ".yaml", ".html"))
    ]


def _json_values(obj, path: str):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _json_values(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from _json_values(value, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def census(root: Path):
    for rel in _surface(root):
        text = (root / rel).read_text(encoding="utf-8")
        if rel.endswith(".json"):
            units = _json_values(json.loads(text), "")
        else:
            units = ((str(n), line) for n, line in enumerate(text.splitlines(), 1))
        for locator, unit in units:
            for match in _PATTERN.finditer(unit):
                start = max(0, match.start() - 60)
                excerpt = unit[start:match.end() + 60].replace("\n", " ").replace("\t", " ")
                yield rel, locator, _canon(match.group(1)), excerpt.strip()


def main(argv: list[str]) -> int:
    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else Path.cwd()
    hits = list(census(root))
    if "--counts" in argv:
        counts: dict[str, int] = {}
        for _, _, brand, _ in hits:
            counts[brand] = counts.get(brand, 0) + 1
        for brand, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"{brand}\t{n}")
        print(f"total\t{len(hits)}")
        return 0
    for rel, locator, brand, excerpt in hits:
        print(f"{rel}:{locator}\t{brand}\t{excerpt}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
