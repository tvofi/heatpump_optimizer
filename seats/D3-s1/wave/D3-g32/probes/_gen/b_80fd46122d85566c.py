from types import SimpleNamespace as NS
from custom_components.heatpump_optimizer import price_model as pm

mut = mutate(pm, "prices_from_entity_state", "    if state is None:", "    if False:")
moved = 0
for vat, sur in ((1.0, 0.0), (1.25, 0.3), (0.0, -1.0)):
    b = pm.prices_from_entity_state(None, vat, sur)
    m = mut(None, vat, sur)
    moved += b != m
    print(f"RESULT none_state_baseline_vat{vat}={b!r}")
    print(f"RESULT none_state_mutant_vat{vat}={m!r}")
print(f"RESULT none_state_inputs_moved={moved} count")
# the other inputs that reach line 820 (guard false either way): a non-None state
others = [NS(state="unknown", attributes={}), NS(state="", attributes=None), NS(state="1.2", attributes={"today": []}),
          NS(state="unavailable", attributes={"raw_today": [{"start": "2026-01-14T00:00:00+00:00", "value": 1.0}]})]
print(f"RESULT other_states_moved={sum(pm.prices_from_entity_state(s) != mut(s) for s in others)} count")
tail()
