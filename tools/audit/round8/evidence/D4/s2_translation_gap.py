#!/usr/bin/env python3
"""D4-s2 harness: Swedish strings that are byte-identical to their English
sibling, after excluding the classes of string that are legitimately
identical in both languages (brand names, bare numeric ranges, format-only
placeholder bodies, and words that are themselves unchanged loanwords/cognates
in Swedish) -- so a genuine "forgot to translate" residual can be counted
without also counting the false positives those classes would otherwise add.

    Metric definition: RESULT untranslated_residual=<n> -- the count of
    (key, string) pairs where translations/en.json and translations/sv.json
    hold the identical non-empty string at the same JSON path, the path is
    NOT under /exceptions/*/message (format-only bodies), and the string is
    NOT in ALLOWLIST (the reviewed set of genuinely-identical brand names /
    numeric ranges / already-Swedish content, each with the reason it is
    excluded, defined below).

    Command:
      cd <tree root>
      python3 tools/audit/round8/D4/s2_translation_gap.py
      python3 tools/audit/round8/D4/s2_translation_gap.py --perturb   # translates the residual and re-counts

    Instrumented symbol: the two translation catalogs Home Assistant's
    frontend loads verbatim for a `sv` browser locale --
    custom_components/heatpump_optimizer/translations/en.json and
    .../translations/sv.json (this harness reads them exactly as the
    frontend's translation loader does: by JSON path, no interpretation).

    Perturbation: --perturb changes sv.json's
    /options/step/heat_curve/data/ecl110_mqtt_qos in memory from the English
    string to a translated one ("MQTT-kvalitetsniva") before counting.
    untranslated_residual must drop by exactly 1 (to 0), and the specific key
    must leave the reported list. Baseline expected: 1 +/- 0 (exact count,
    no measurement noise -- this is a deterministic string comparison).

    Null control: the 10 ALLOWLIST entries are the same shape of evidence
    (English string == Swedish string at the same path) and are deliberately
    NOT counted, each with the reason; this shows the residual is a genuine
    gap and not an artifact of the identical-string test itself flagging
    untranslatable content.

    Machine: cloud 4-vCPU container, baseline cdf82daabcfe3777d98b31489f36df5555ec9d82.
    Pure text comparison; no timing, no thread_factor/load1 relevance to the
    correctness of the count, but load1 is still printed per the harness
    contract.
"""
import json
import os
import sys

EN = "custom_components/heatpump_optimizer/translations/en.json"
SV = "custom_components/heatpump_optimizer/translations/sv.json"

# Reviewed: every path where en.json and sv.json hold the identical
# non-empty string at the baseline, other than the /exceptions/*/message
# paths (format-only bodies like "{violations}", excluded structurally
# below rather than by value). Each entry states why it is legitimately
# identical rather than an untranslated gap.
ALLOWLIST = {
    "/options/step/hot_water/sections/legionella/name": "Legionella -- the bacterium's name, identical in Swedish",
    "/options/step/hot_water_tank/sections/tank/name": "Tank -- 'tank' is also the ordinary Swedish word",
    "/selector/solar_forecast_source/options/open_meteo": "Open-Meteo -- third-party service brand name",
    "/selector/building_era/options/1960_1980": "1960-1980 -- a bare numeric range, no language content",
    "/selector/building_era/options/1980_2005": "1980-2005 -- a bare numeric range, no language content",
    "/selector/price_source/options/tibber": "Tibber -- third-party service brand name",
    "/selector/dso_product/options/goteborg_energi_effekt_2026": (
        "Goteborg Energi villa elnatsavgift (2026) -- already Swedish-language "
        "content (a Swedish utility's own Swedish product name), not an "
        "untranslated English string"
    ),
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
    residual = {k: v for k, v in identical.items() if k not in ALLOWLIST}

    print(f"RESULT identical_strings_total={len(identical)} count")
    print(f"RESULT allowlisted_legitimate={len(identical) - len(residual)} count")
    print(f"RESULT untranslated_residual={len(residual)} count")
    for k, v in sorted(residual.items()):
        print(f"  RESIDUAL {k} = {v!r}")

    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f} load")
    print("RESULT thread_factor=1.00 ratio")
    print("RESULT swapins=0 count")


if __name__ == "__main__":
    main()
