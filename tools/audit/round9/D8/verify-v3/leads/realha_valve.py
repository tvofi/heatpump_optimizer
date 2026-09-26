"""V3 leads sub-seat, round 9: D8-s3-61 (Valve Target Recommendation) reachability
in REAL Home Assistant, not tests/hastub.

METRIC (one line): whether ValveTargetRecommendationSensor is ever added to the
real hass state machine (native_value/available called, a state written) when
its class-level ``_attr_entity_registry_enabled_default = False`` is left at
its production value, driven through the REAL ``EntityPlatform._async_add_entity``
(the exact code path production runs, not a direct property read) -- and,
separately, whether real HA's own default-derivation (``entity_registry_enabled_default``
as a plain class attribute HA reads at first registration; see
homeassistant/helpers/entity_platform.py:904 ``if not entity.entity_registry_enabled_default:
disabled_by = RegistryEntryDisabler.INTEGRATION``) treats it identically to a
sibling ConfiguredInputMixin entity whose default follows the configured feature.

RUN (from repo root; NOT PYTHONPATH=tests/hastub):
  PYTHONPATH=<scratch numpy/scipy dir> /home/claude/havenv/bin/python \
    tools/audit/round9/D8/verify-v3/leads/realha_valve.py [--perturb]

Perturbation (--perturb): ValveTargetRecommendationSensor.entity_registry_enabled_default
  wrapped to follow mixing_valve.is_throttling(mode) (the finder's proposed fix
  shape), in memory. Expected direction: real_state_written_valve_manual goes
  from 0 -> 1 (the entity now registers enabled and a state is written).

EXPECTED at baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (exact):
  real_registry_disabled_valve_manual=1 (disabled_by=INTEGRATION even though a
    valve is configured and is_throttling(mode) is True)
  real_state_written_valve_manual=0 (no state ever exists to read: production
    value the finder's stub-only harness measured by calling native_value
    directly is never delivered to a real installation without the user first
    enabling the entity by hand)
  real_registry_disabled_ecl110_sibling=0 (ConfiguredInputMixin sibling used as
    a comparator, BufferTankTempSensor: default tracks the configured input, so
    a configured probe registers enabled and DOES get a real state written)
  --perturb: real_registry_disabled_valve_manual -> 0, real_state_written_valve_manual -> 1
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence, 96b89163).
Machine: G2-leads verify-v3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import shutil
import sys
import tempfile
import time

REPO = os.getcwd()
assert "hastub" not in os.environ.get("PYTHONPATH", ""), "run WITHOUT tests/hastub"

# Environment shim, not a production change: mashumaro (a real-HA dependency)
# still calls issubclass(x, typing.ByteString), which CPython 3.14 removed.
import abc as _abc  # noqa: E402
import typing as _typing  # noqa: E402
if not hasattr(_typing, "ByteString"):
    class _ByteString(_abc.ABC):
        pass
    for _t in (bytes, bytearray, memoryview):
        _ByteString.register(_t)
    _typing.ByteString = _ByteString

import homeassistant  # noqa: E402
from homeassistant import config_entries, core, loader  # noqa: E402
from homeassistant.const import __version__ as HA_VERSION  # noqa: E402
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_platform  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from unittest import mock  # noqa: E402

assert "hastub" not in homeassistant.__file__, homeassistant.__file__
PERTURB = "--perturb" in sys.argv
DOMAIN = "heatpump_optimizer"


async def make_hass(tmp):
    hass = core.HomeAssistant(tmp)
    hass.config.skip_pip = True
    await hass.config.async_set_time_zone("Europe/Stockholm")
    loader.async_setup(hass)
    await dr.async_load(hass)
    await er.async_load(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    hass.set_state(core.CoreState.running)
    return hass


def add_entry(hass, data=None, options=None, title="HPO"):
    entry = config_entries.ConfigEntry(
        data=data or {}, discovery_keys={}, domain=DOMAIN, minor_version=1,
        options=options or {}, source="user", subentries_data=None, title=title,
        unique_id=None, version=1,
    )
    hass.config_entries._entries[entry.entry_id] = entry
    return entry


class _FakeCoordinatorShim:
    """Bare stand-in for ``update_coordinator.DataUpdateCoordinator`` state that
    ``CoordinatorEntity`` reads (last_update_success, data, listener registration)
    -- NOT a substitute for the finder's computation of valve_target_recommendation,
    which the lead evidence already established via the real production
    coordinator on tests/hastub; here we drive the REAL entity registry/platform
    machinery around an entity holding that already-established payload, which
    is the part tests/hastub does not model (its EntityRegistry has no
    ``disabled_by`` at all -- tests/hastub/homeassistant/helpers/entity_registry.py:90)."""

    def __init__(self, hass, entry, data, config):
        self.hass = hass
        self.config_entry = entry
        self.entry = entry
        self.data = data
        self.last_update_success = True
        self._config = config
        self._listeners = {}

    def async_add_listener(self, update_callback, context=None):
        def _unsub():
            self._listeners.pop(update_callback, None)
        self._listeners[update_callback] = context
        return _unsub

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.entry.entry_id)}, "name": "HPO"}


async def register(hass, entry, entity):
    """The real production path: EntityPlatform._async_add_entity, exactly as
    ``async_setup_entry`` would drive it through ``AddEntitiesCallback``."""
    platform = entity_platform.EntityPlatform(
        hass=hass, logger=__import__("logging").getLogger(__name__),
        domain="sensor", platform_name=DOMAIN, platform=None,
        scan_interval=__import__("datetime").timedelta(seconds=30), entity_namespace=None,
    )
    platform.config_entry = entry
    await platform.async_add_entities([entity])
    reg_entry = er.async_get(hass).async_get(entity.entity_id) if entity.entity_id else None
    state = hass.states.get(entity.entity_id) if entity.entity_id else None
    return reg_entry, state


async def main():
    tmp = tempfile.mkdtemp(prefix="realha_d8v3_")
    os.symlink(os.path.join(REPO, "custom_components"), os.path.join(tmp, "custom_components"))
    sys.path.insert(0, tmp)
    from custom_components.heatpump_optimizer import mixing_valve, sensor  # noqa: E402

    if PERTURB:
        sensor.ValveTargetRecommendationSensor.entity_registry_enabled_default = property(
            lambda self: mixing_valve.is_throttling(self.coordinator._config.get("mixing_valve_mode")))

    hass = await make_hass(tmp)

    # ---- seam D: the finding's own case, a throttling manual valve configured ----
    entry_v = add_entry(hass, data={"name": "HPO"}, options={"mixing_valve_mode": "manual"})
    coord_v = _FakeCoordinatorShim(
        hass, entry_v,
        data={"valve_target_recommendation": {"target": 23.0, "reason": "comfort_ceiling",
                                               "configured_target": 22.0}},
        config={"mixing_valve_mode": "manual"})
    valve_entity = sensor.ValveTargetRecommendationSensor(coord_v, entry_v)
    reg_v, state_v = await register(hass, entry_v, valve_entity)
    disabled_v = bool(reg_v and reg_v.disabled)
    print(f"SEAM valve_manual: entity_id={valve_entity.entity_id} registry_disabled={disabled_v} "
          f"disabled_by={reg_v.disabled_by if reg_v else None} state={state_v} "
          f"is_throttling={mixing_valve.is_throttling('manual')}")
    print(f"RESULT real_registry_disabled_valve_manual={int(disabled_v)} flag")
    print(f"RESULT real_state_written_valve_manual={int(state_v is not None)} flag")
    if state_v is not None:
        print(f"RESULT real_state_value_valve_manual={state_v.state} value")

    # ---- comparator: a ConfiguredInputMixin sibling (BufferTankTempSensor),
    # its one config slot (CONF_BUFFER_TANK_TEMP_ENTITY) configured, mirroring
    # the finding's own docstring citation of #1542's ConfiguredInputMixin shape.
    from custom_components.heatpump_optimizer import const  # noqa: E402
    entry_e = add_entry(hass, data={"name": "HPO2"}, options={})
    coord_e = _FakeCoordinatorShim(
        hass, entry_e, data={"buffer_tank_temperature": 41.2},
        config={const.CONF_BUFFER_TANK_TEMP_ENTITY: "sensor.tank"})
    ecl_entity = sensor.BufferTankTempSensor(coord_e, entry_e)
    reg_e, state_e = await register(hass, entry_e, ecl_entity)
    disabled_e = bool(reg_e and reg_e.disabled)
    print(f"SEAM buffer_tank_sibling_configured: entity_id={ecl_entity.entity_id} "
          f"registry_disabled={disabled_e} disabled_by={reg_e.disabled_by if reg_e else None} state={state_e}")
    print(f"RESULT real_registry_disabled_ecl110_sibling={int(disabled_e)} flag")
    print(f"RESULT real_state_written_ecl110_sibling={int(state_e is not None)} flag")

    print(f"RESULT ha_version={HA_VERSION}")
    await hass.async_stop(force=True)
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    t0, tt0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={(pc / tc) if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")
