"""Reviewer's own plants on hub_solve_writes (C16), at the head's instrument."""
import sys, shutil, tempfile, re
from pathlib import Path
W = Path(sys.argv[1]); sys.path.insert(0, str(W / "tools/audit"))
from archscore.metrics import common as C, hub_solve_writes as H
SRC = (W / "custom_components/heatpump_optimizer/coordinator.py").read_text()
def measure(src, c16=True):
    with tempfile.TemporaryDirectory() as t:
        shutil.copytree(W / "custom_components", Path(t) / "custom_components")
        (Path(t) / "custom_components/heatpump_optimizer/coordinator.py").write_text(src)
        H.EVENT_ROOTS = c16; C.reset_caches(); C.load.cache_clear()
        return H.measure(Path(t))["value"]
reg = "            self.hass, [entity], self._on_power_event\n"
assert SRC.count(reg) == 1
dfn = "    def _on_power_event(self, event: Event[EventStateChangedData]) -> None:\n"
assert SRC.count(dfn) == 1
plants = {
 "N0 none": SRC,
 "A junk no-op callback registered with HA": SRC.replace(dfn,
    "    def _junk_cb(self, event) -> None:\n        return None\n\n" + dfn).replace(reg,
    reg + "        )\n        async_track_state_change_event(\n            self.hass, [entity], self._junk_cb\n"),
 "B setup-time writer referenced by a logger call (not a callback)": SRC.replace(dfn,
    dfn + "        _LOGGER.debug('%r', self.async_update_thermal_params)\n"),
 "C HA callback wrapped in a package identity helper": SRC.replace(reg,
    "            self.hass, [entity], _pkg_wrap(self._on_power_event)\n") + "\n\ndef _pkg_wrap(cb):\n    return cb\n",
}
for k, s in plants.items():
    print(f"RESULT plant={k!r} hub_solve_writes={measure(s)} c16_off={measure(s, False)}")
