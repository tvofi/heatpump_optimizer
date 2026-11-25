from types import SimpleNamespace as NS
from custom_components.heatpump_optimizer import price_model as pm

mut = mutate(pm, "prices_from_entity_state", "        isinstance(attrs, dict) and attrs", "        isinstance(attrs, dict) or attrs")
cases = {
    "unknown_empty_dict": NS(state="unknown", attributes={}),
    "unavailable_empty_dict": NS(state="unavailable", attributes={}),
    "blank_empty_dict": NS(state="", attributes={}),
    "unknown_none_attrs": NS(state="unknown", attributes=None),
    "unknown_tuple_attrs": NS(state="unknown", attributes=(("today", []),)),
}
moved = 0
for name, st in cases.items():
    b, m = pm.prices_from_entity_state(st), mut(st)
    moved += b != m
    print(f"RESULT reason_baseline_{name}={b!r}")
    print(f"RESULT reason_mutant_{name}={m!r}")
print(f"RESULT inputs_moved={moved} count")
# null control: a numeric state with a populated series, where the guard is not consulted
ok = NS(state="1.2", attributes={"today": [1.0] * 24})
print(f"RESULT null_delta={int(pm.prices_from_entity_state(ok) != mut(ok))} count")
tail()
