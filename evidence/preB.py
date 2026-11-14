import asyncio as _asyncio
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass
from heatpump_optimizer.coordinator import (
    HeatPumpOptimizerCoordinator as _Coord,
)
import asyncio as _pa_aio  # noqa: E402
from types import SimpleNamespace as _PaNS  # noqa: E402
from heatpump_optimizer import pump_arbiter as _pa  # noqa: E402
from harness import FakeEntry as _pa_entry  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO as _PA_AUTO, MODE_OFF as _PA_OFF  # noqa: E402
_PA_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
_PA_TUYA = ("Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW")
def _pa_result(duties):
    """A plan of 15-min steps from ``duties`` ('s', 'd', 'b', '-')."""
    return _PaNS(
        timestamps=[_PA_T0 + timedelta(minutes=15 * i) for i in range(len(duties))],
        power_schedule=[1.5 if c in "sb" else 0.15 if c == "x" else 0.0 for c in duties],
        dhw_power_schedule=[2.0 if c in "dbx" else 0.0 for c in duties],
        optimal_setpoints=[21.0 for _ in duties],
    )
_PA_IDS = __import__("itertools").count()
class _PaCoord:
    def __init__(self, options, duties="dds-", flow=True, duty="control"):
        self.hass = FakeHass({
            "select.pump_mode": FakeState("Heating + DHW", attributes={"options": list(options)}),
            "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
            "number.water_set": FakeState("53", attributes={"min": 25, "max": 63}),
        })
        self._config = EntryConfig.from_mapping({
            "pump_duty_mode": duty,
            "heat_pump_mode_entity": "select.pump_mode",
            "dhw_setpoint_entity": "number.dhw_set",
            "space_setpoint_entity": "number.water_set",
            "space_setpoint_unit": "flow" if flow else "indoor",
        })
        self._mode = _PA_AUTO
        self.stale = False
        self._current_action = {"mode": "eco"}
        self._optimization_result = _pa_result(duties)
        self._thermal_model = _PaNS(
            params=_PaNS(min_electrical_power=0.4), curve_flow_temp=lambda _o: 34.2
        )
        # No disinfection cycle: the arbiter reads the cycle's temperature only on a cycle step.
        self._thermal_params = _PaNS(dhw_setpoint=48.0, dhw_max_temp=48.0, dhw_cycle_temp=None)
        self._current_state = _PaNS(outdoor_temperature=2.0)
        # One store key per coordinator: the storage stub outlives FakeHass.
        # A FakeEntry, weak-referenceable as a real entry is: off_restore
        # keys its record on it (R10-ARBITER-OFF-RESTORE).
        self.entry = _pa_entry(entry_id=f"pa{next(_PA_IDS)}")
        self.set_modes = []

    def _plan_is_stale(self):
        return self.stale

    @property
    def effective_config(self):
        # setpoint_check.evaluate reads the published views (#1739).
        return self._config

    @property
    def thermal_params(self):
        return self._thermal_params

    def arbiter_inputs(self):
        # Every field read live, so a test that reaches into the stub's
        # privates (a disinfection hold, a meter sample, the unload latch)
        # is seen by the next pass, exactly as the real coordinator's
        # published builder reads its own.
        return _pa.ArbiterInputs(
            hass=self.hass,
            config=self._config,
            mode=self._mode,
            plan=self._optimization_result,
            plan_stale=self.stale,
            entry_released=getattr(self, "_entry_released", False),
            state=self._current_state,
            thermal=self._thermal_model,
            params=self._thermal_params,
            action=self._current_action,
            measured_power_kw=getattr(self, "_measured_power", None),
            disinfecting=getattr(
                getattr(getattr(self, "_legionella", None), "disinfect", None),
                "memo", None,
            ) is True,
        )

    async def async_set_mode(self, mode):
        self.set_modes.append(mode)
        self._mode = mode

    def device(self, entity, value):
        self.hass.states.get(entity).state = value

    def writes(self):
        return [(d, sv, (data or {}).get("option", (data or {}).get("value")))
                for d, sv, data in self.hass.services.calls]
_pa_ticks: list = []
_pa.async_track_time_interval = (
    lambda hass, action, interval: _pa_ticks.append(action) or (lambda: None)
)
_pa_orig_delete_issue = _pa.ir.async_delete_issue
_pa.ir.async_delete_issue = _pa_orig_delete_issue
_pa_orig_store = _pa._store
_pa._store = _pa_orig_store
