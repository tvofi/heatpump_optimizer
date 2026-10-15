"""N1b (NULL): reformat one function signature -- thermal_model's
_simulate_step_single, fifteen parameters one per line, re-wrapped three or
four per line (valid PEP 8 hanging indent; the AST is identical).

It targeted tariff.peak_cost_smooth until R10-TARIFF folded that family's
parameters into one PeakBilling record; _simulate_step_single keeps its
scalars by a recorded decision (tests/arch_score_head.py PARAMS_OVER_10_LEFT).
"""
import ast, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import PKG, read, write, replace_once

rel = f"{PKG}/thermal_model.py"
s = read(rel)
before = ast.dump(ast.parse(s))
s = replace_once(s, '''    def _simulate_step_single(
        self,
        state: ThermalState,
        electrical_power: float,
        outdoor_temp: float,
        wind_speed: float = 0.0,
        precipitation: float = 0.0,
        solar_radiation: float = 0.0,
        dt_hours: float = 0.25,
        external_heat_kw: float = 0.0,
        humidity: float | None = None,
        hour_of_day: float | None = None,
        measured_heat_kw: float | None = None,
        _cop: float | None = None,
        _u_eff: float | None = None,
        _q_solar: float | None = None,
    ) -> ThermalState:''', '''    def _simulate_step_single(
        self, state: ThermalState, electrical_power: float, outdoor_temp: float,
        wind_speed: float = 0.0, precipitation: float = 0.0,
        solar_radiation: float = 0.0, dt_hours: float = 0.25,
        external_heat_kw: float = 0.0, humidity: float | None = None,
        hour_of_day: float | None = None, measured_heat_kw: float | None = None,
        _cop: float | None = None, _u_eff: float | None = None,
        _q_solar: float | None = None,
    ) -> ThermalState:''')
assert ast.dump(ast.parse(s)) == before
write(rel, s)
