"""Game private_cross_module by copying the private: config_flow stops importing
``thermal_model._dhw_enabled_from_config`` and gets its own ``_dhw_on`` with the parameter renamed. The crossing
reads gone; nothing is shared any more, and the DHW-enabled rule is now written twice. ``duplication_copies``
refuses it (the helper is two statements, at the clone window), and so does ``shape_copies``; on the pin no
private crossing is below the window, so C23 is not what closes this attempt (ABOUT.md, part 5)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "config_flow.py"
s = p.read_text()
imp = "from .thermal_model import ThermalParameters, _dhw_enabled_from_config\n"
use = "not _dhw_enabled_from_config(current)"
assert s.count(imp) == 1 and s.count(use) == 1, (s.count(imp), s.count(use))
copy = ("\n\ndef _dhw_on(cfg: dict[str, Any]) -> bool:\n"
        "    if CONF_DHW_ENABLED in cfg:\n"
        "        return bool(cfg[CONF_DHW_ENABLED])\n"
        "    return any(\n"
        "        cfg.get(key) is not None\n"
        "        for key in (CONF_DHW_TANK_VOLUME, CONF_DHW_TEMP_ENTITY, CONF_DHW_WINDOWS)\n"
        "    )\n")
s = s.replace(imp, "from .thermal_model import ThermalParameters\n").replace(use, "not _dhw_on(current)")
p.write_text(s + copy)
print("copied", 1)
