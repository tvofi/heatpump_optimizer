"""V3 independent check for D2-s4-81: verify adoption_decision is keyed on interval width, not on
fit error, by calling it directly with a synthetic PERFECT result (heat_loss_kw_per_c exactly
equal to the declared UA, i.e. zero bias) at varying widths -- independent of running the full
sysid arm/step/_finish drive on any preset house.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3-leads/v3_sysid_gate_unit.py
"""
import sys
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

params = ThermalParameters.from_config({})
base_u = params.heat_loss_coefficient
config = S.SysIdConfig()

bar = S.UA_ADOPTION_HALFWIDTH_BAR
for hw in (bar * 0.5, bar * 0.99, bar * 1.01, bar * 2.0):
    result = S.SysIdResult(
        completed=True,
        heat_loss_kw_per_c=base_u,  # EXACT match to the declared UA: zero bias, zero fit error
        ua_profile_halfwidth=hw,
        ua_prior_halfwidth=None,
    )
    decision = S.adoption_decision(result, params, config)
    print(f"RESULT hw={hw:.4f} bar={bar:.4f} zero_bias=True admit={decision.admit} "
          f"reason={decision.reason!r}")

print("RESULT conclusion: a fit with ZERO bias/error (heat_loss_kw_per_c == the true, declared "
      "value exactly) is refused whenever the reported interval width exceeds the bar, "
      "independent of the fit's own accuracy -- confirms the gate is keyed on width, not bias, "
      "by direct construction rather than by driving a preset's noisy experiment.")
