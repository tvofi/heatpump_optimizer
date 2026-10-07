#!/usr/bin/env python3
"""D4-v1 verifier harness for D4-s2-01 (independent metric, independent script).

Metric definition: RESULT english_looking_residual=<n> -- among the
(key, string) pairs where translations/en.json and translations/sv.json hold
the byte-identical non-empty string at the same JSON path (excluding
/exceptions/*/message, which is format-only body text, structurally not a
UI label), count only the pairs whose string ALSO contains at least one
token from a small closed set of common English function/content words
("of", "the", "quality", "service", "and", "hours", "price", ...) that would
not appear in ordinary Swedish text. This is a different filter than the
finder's (s2_translation_gap.py, which subtracts a manually reviewed
7-entry ALLOWLIST of specific paths/strings with a stated reason each);
this harness instead applies a content-based heuristic with no path-specific
knowledge, so it cannot merely replay the finder's own exclusions.

Command:
  cd <tree root>
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D4/v1_locale_residual.py
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D4/v1_locale_residual.py --perturb

Instrumented symbol: same two catalogs as s2_translation_gap.py --
custom_components/heatpump_optimizer/translations/en.json and .../sv.json.

Perturbation: --perturb replaces sv.json's
/options/step/heat_curve/data/ecl110_mqtt_qos in memory with a Swedish
string before counting; english_looking_residual must drop.

Null control: brand names, numeric ranges and cognates
(Legionella, Tank, Open-Meteo, 1960-1980, 1980-2005, Tibber, the Goteborg
Energi product name) contain none of the English-tell tokens below, so this
heuristic does not need a separate allowlist to leave them uncounted -- if it
did flag any of them, that would be a false positive to report, not evidence
for the finding.

Baseline expected: >=1 (this is a coarser, over-cautious heuristic, so it
may also catch cognates/loanwords the finder's harness allowlists by path;
any such extra hits are reported as EXTRA and are not evidence against the
finding since the finder's own target key is expected to appear).

Machine: cloud 4-vCPU container, baseline cdf82daabcfe3777d98b31489f36df5555ec9d82.
Pure text comparison; no timing relevance.
"""
import json
import os
import re
import sys

EN = "custom_components/heatpump_optimizer/translations/en.json"
SV = "custom_components/heatpump_optimizer/translations/sv.json"

# Common English words that would not appear in Swedish UI copy. Deliberately
# small and generic -- not tuned to this repository's specific strings.
ENGLISH_TELLS = {
    "of", "the", "and", "quality", "service", "hours", "price", "heating",
    "message", "messages", "control", "settings", "enable", "disable",
    "minimum", "maximum", "value", "device", "sensor", "source",
}


def flatten(d, path=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            p = f"{path}/{k}"
            if isinstance(v, str):
                out[p] = v
            else:
                out.update(flatten(v, p))
    return out


def looks_english(s):
    words = set(re.findall(r"[a-zA-Z]+", s.lower()))
    return bool(words & ENGLISH_TELLS)


def main():
    perturb = "--perturb" in sys.argv
    en = flatten(json.load(open(EN, encoding="utf-8")))
    sv = flatten(json.load(open(SV, encoding="utf-8")))

    if perturb:
        key = "/options/step/heat_curve/data/ecl110_mqtt_qos"
        assert sv.get(key) == en.get(key), "perturbation target moved; update harness"
        sv[key] = "MQTT-kvalitetsniva"

    identical = {
        k: v
        for k, v in en.items()
        if v.strip() and sv.get(k) == v and not k.startswith("/exceptions/")
    }
    residual = {k: v for k, v in identical.items() if looks_english(v)}

    print(f"RESULT identical_strings_total={len(identical)} count")
    print(f"RESULT english_looking_residual={len(residual)} count")
    for k, v in sorted(residual.items()):
        print(f"  RESIDUAL {k} = {v!r}")

    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f} load")
    print("RESULT thread_factor=1.00 ratio")


if __name__ == "__main__":
    main()
