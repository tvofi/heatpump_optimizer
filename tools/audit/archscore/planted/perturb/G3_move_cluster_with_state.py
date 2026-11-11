"""G3 (GOOD): move the frequency cluster (#61) to a collaborator that OWNS its state.

Five coordinator methods (_freq_entity_reading, _freq_mode, _observe_frequency,
_command_frequency, _freq_view) and the four attributes only they use
(_freq_map, _freq_watchdog, _freq_fallback, _freq_last_write) move into
``freq_seat.FrequencyControl``. The coordinator holds one ``self._freq`` and
talks to it through a small public interface: observe / command / view /
mode / reading plus the two persisted fields ``map`` and ``fallback``.
Inputs the cluster used to reach for (commanded power, measured power, the
fold gate, the off mode) are now ARGUMENTS; the one effect it used to
trigger on the coordinator (persist the latch) is a RETURN value. No reach
from freq_seat.py into the coordinator remains.
"""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, PKG, read, write, replace_once
from _freq_common import drop_orphaned_const_imports, HEADER_IMPORTS, strip_cluster, drop_seams

MODULE = '"""Inverter frequency control (#61): a collaborator that owns its own state."""\n' + HEADER_IMPORTS + '''

class FrequencyControl:
    """The kW-per-Hz map, the write watchdog, its stand-down latch, the write clock."""

    def __init__(self, hass: HomeAssistant, config: Callable[[], Mapping[str, Any]]) -> None:
        self._hass = hass
        self._config = config
        self.map = FrequencyMap()
        self.fallback = False
        self._watchdog = FrequencyWatchdog()
        # Stamped at init: a crash-looping HA must not get a fresh write per boot.
        self._last_write: datetime | None = dt_util.now()

    def reading(self) -> tuple[float | None, float, float, str | None]:
        """(reported Hz, range min, range max, source); ``resolve_reading``'s rules."""
        cfg = self._config()
        return resolve_reading(
            cfg.get(CONF_COMPRESSOR_FREQ_ENTITY),
            cfg.get(CONF_COMPRESSOR_FREQ_SENSOR),
            self._hass.states.get,
            _finite(cfg.get(CONF_COMPRESSOR_FREQ_MIN_HZ, DEFAULT_COMPRESSOR_FREQ_MIN_HZ), DEFAULT_COMPRESSOR_FREQ_MIN_HZ),
            _finite(cfg.get(CONF_COMPRESSOR_FREQ_MAX_HZ, DEFAULT_COMPRESSOR_FREQ_MAX_HZ), DEFAULT_COMPRESSOR_FREQ_MAX_HZ),
        )

    def mode(self) -> str:
        """The stage in force: control needs entity, opt-in and an armed watchdog."""
        cfg = self._config()
        number = cfg.get(CONF_COMPRESSOR_FREQ_ENTITY)
        if not number and not cfg.get(CONF_COMPRESSOR_FREQ_SENSOR):
            return "unconfigured"
        configured = str(cfg.get(CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE))
        if number and configured == FREQ_MODE_CONTROL and not self.fallback:
            return FREQ_MODE_CONTROL
        return FREQ_MODE_OBSERVE

    def observe(self, commanded_kw: float, measured_kw: float | None, fold_blocked: bool) -> bool:
        """One cycle: watchdog first, then the kW-per-Hz fold.

        Returns True when the stand-down latch changed, which the owner persists.
        """
        changed = False
        cfg = self._config()
        configured = str(cfg.get(CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE))
        if (
            configured != FREQ_MODE_CONTROL
            or not cfg.get(CONF_COMPRESSOR_FREQ_ENTITY)
        ) and self.fallback:
            # The user's acknowledgement re-arms the latch and retires its issue.
            self.fallback = False
            self._watchdog.reset()
            ir.async_delete_issue(self._hass, DOMAIN, "freq_watchdog")
            changed = True
        reported, hz_min, hz_max, source = self.reading()
        if reported is None:
            return changed
        if source == FREQ_SOURCE_NUMBER and configured == FREQ_MODE_CONTROL and not self.fallback:
            # Divergence only counts while the plan asks for the compressor
            # and the reading is in its running range.
            watch_active = commanded_kw > 0.05 and reported >= hz_min
            if self._watchdog.note_report(reported, active=watch_active):
                self.fallback = True
                changed = True
                entity_id = str(cfg.get(CONF_COMPRESSOR_FREQ_ENTITY) or "")
                _LOGGER.warning(
                    "Compressor frequency control stood down: %s reports "
                    "%.1f Hz against a commanded %.1f Hz for %d ticks",
                    entity_id,
                    reported,
                    self._watchdog.commanded or 0.0,
                    self._watchdog.strikes,
                )
                _create_issue(
                    self._hass,
                    DOMAIN,
                    "freq_watchdog",
                    is_fixable=False,
                    is_persistent=True,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="freq_watchdog",
                    translation_placeholders={"entity": entity_id},
                )
        if measured_kw is None or fold_blocked:
            return changed
        self.map.observe(reported, float(measured_kw), hz_min, hz_max)
        return changed

    async def command(self, commanded_kw: float, off: bool) -> None:
        """The control stage's single write path: rate-limited, clamped, deduplicated."""
        entity_id = self._config().get(CONF_COMPRESSOR_FREQ_ENTITY)
        if not entity_id or self.mode() != FREQ_MODE_CONTROL or off:
            return
        _reported, hz_min, hz_max, _source = self.reading()
        target = self.map.recommend(commanded_kw, hz_min, hz_max)
        if target is None:
            return
        target = float(np.clip(target, hz_min, hz_max))
        now = dt_util.now()
        if (
            self._last_write is not None
            and (now - self._last_write).total_seconds()
            < FREQ_WRITE_MIN_INTERVAL_S
        ):
            return
        if (
            self._watchdog.commanded is not None
            and abs(target - self._watchdog.commanded)
            < FREQ_WRITE_EPSILON_HZ
        ):
            return
        try:
            await self._hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": entity_id, "value": round(target, 1)},
                blocking=True,
            )
        except Exception as err:  # noqa: BLE001 - never break the cycle
            _LOGGER.error("Error commanding compressor frequency: %s", err)
            return
        self._last_write = now
        self._watchdog.note_command(target)
        _LOGGER.info(
            "Commanded compressor frequency %.1f Hz via %s", target, entity_id
        )

    def view(self, commanded_kw: float) -> dict[str, Any]:
        """The map, the stage, and what control WOULD do (published in observe too)."""
        reported, hz_min, hz_max, source = self.reading()
        mode = self.mode()
        recommended = None
        exhausted = False
        if mode != "unconfigured":
            recommended = self.map.recommend(commanded_kw, hz_min, hz_max)
            exhausted = self.map.evidence_exhausted(commanded_kw, hz_min, hz_max)
        view = {
            "mode": mode,
            "fallback_active": bool(self.fallback),
            "reported_hz": reported,
            "recommended_hz": recommended,
            "evidence_exhausted": exhausted,
            "commanded_hz": self._watchdog.commanded,
            "range_hz": (
                [round(hz_min, 1), round(hz_max, 1)]
                if mode != "unconfigured"
                else None
            ),
            "map": (
                self.map.summary(hz_min, hz_max)
                if mode != "unconfigured"
                else {}
            ),
        }
        if source is not None:
            view["source"] = source
        return view
'''
# G3 keeps the fold gate in the coordinator (it reads coordinator state), so the
# module does not need pump_signals / CONF_POWER_ENTITY / MODE_OFF.
MODULE = (MODULE.replace("    CONF_POWER_ENTITY,\n", "").replace("    MODE_OFF,\n", "")
          .replace("from . import pump_signals\n", ""))
write(f"{PKG}/freq_seat.py", MODULE)

src = strip_cluster(read(COORD))
src = replace_once(src, "from .freq_control import (\n", "from .freq_seat import FrequencyControl\nfrom .freq_control import (\n")
src = replace_once(src, '''        self._freq_map = FrequencyMap()
        # #1067's learner rides this init and the same store: it is the
        # other thing read off the machine rather than off the house.
        self._flow_bias = FlowCurveBias()
        self._freq_watchdog = FrequencyWatchdog()
        self._freq_fallback = False
        # Stamped at init rather than None: the rate limit is in-memory,
        # and a crash-looping HA restarting every minute must not get a
        # fresh write per boot. Costs one 5-minute delay after any start.
        self._freq_last_write: datetime | None = dt_util.now()
''', '''        self._freq = FrequencyControl(
            self.hass, lambda: getattr(self, "_ctx", self)._config)
        # #1067's learner rides this init and the same store: it is the
        # other thing read off the machine rather than off the house.
        self._flow_bias = FlowCurveBias()
''')
src = replace_once(src, '        self._freq_fallback = stored.get("freq_fallback") is True\n        if self._freq_fallback and (',
                   '        self._freq.fallback = stored.get("freq_fallback") is True\n        if self._freq.fallback and (')
src = replace_once(src, "            self._freq_map = FrequencyMap.from_dict(raw_freq)\n",
                   "            self._freq.map = FrequencyMap.from_dict(raw_freq)\n")
src = replace_once(src, '            "freq_map": self._freq_map.as_dict(),\n            "freq_fallback": bool(self._freq_fallback),\n',
                   '            "freq_map": self._freq.map.as_dict(),\n            "freq_fallback": bool(self._freq.fallback),\n')
src = replace_once(src, "            self._freq_map = FrequencyMap()\n", "            self._freq.map = FrequencyMap()\n")
src = replace_once(src, '''            await _best_effort_cycle_step(
                self._command_frequency, "Frequency command skipped: %s")''', '''            await _best_effort_cycle_step(
                lambda: self._freq.command(
                    self._commanded_power() or 0.0, self._mode == MODE_OFF),
                "Frequency command skipped: %s")''')
src = replace_once(src, "        self._observe_frequency(now)\n", '''        if self._freq.observe(
            self._commanded_power(),
            self._measured_power,
            bool(self._immersion_active or _freq_fold_blocked(self)),
        ):
            self._spawn(self._async_save_thermal_learning())
''')
src = replace_once(src, "self._freq_view()", "self._freq.view(self._commanded_power() or 0.0)")
# imports the move orphaned
src = replace_once(src, '''from .freq_control import (
    FREQ_MODE_CONTROL,
    FREQ_MODE_OBSERVE,
    FREQ_SOURCE_NUMBER,
    FREQ_WRITE_EPSILON_HZ,
    FREQ_WRITE_MIN_INTERVAL_S,
    FrequencyMap,
    FrequencyWatchdog,
    resolve_reading,
)''', "from .freq_control import FREQ_MODE_CONTROL, FrequencyMap")
write(COORD, drop_orphaned_const_imports(src))
drop_seams()
