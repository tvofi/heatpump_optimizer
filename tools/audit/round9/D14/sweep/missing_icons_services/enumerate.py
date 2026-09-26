#!/usr/bin/env python3
"""Enumerator, class "missing icons.json services block". D4-s2-08.

Run: python3 tools/audit/round9/D14/sweep/missing_icons_services/enumerate.py
"""
import json
import re
import sys

PKG = "custom_components/heatpump_optimizer"


def main() -> int:
    services_py = open(f"{PKG}/services.py").read()
    const_py = open(f"{PKG}/const.py").read()
    # Registration calls pass a SERVICE_* constant, not a literal string.
    const_names = sorted(set(re.findall(
        r"hass\.services\.async_register\(\s*DOMAIN,\s*(SERVICE_\w+)", services_py)))
    values = {}
    for name in const_names:
        m = re.search(rf'^{name}\s*(?::\s*\w+\s*)?=\s*"([a-z_]+)"', const_py, re.M) or \
            re.search(rf'^{name}\s*(?::\s*\w+\s*)?=\s*"([a-z_]+)"', services_py, re.M)
        if m:
            values[name] = m.group(1)
    registered = sorted(values.values())
    icons = json.load(open(f"{PKG}/icons.json"))
    have_icons = set((icons.get("services") or {}).keys())
    print(f"RESULT registered_services={len(registered)}")
    print(f"RESULT services_with_icon={len(have_icons)}")
    for svc in registered:
        print(f"  {svc} has_icon={svc in have_icons}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
