import asyncio
from types import SimpleNamespace as NS
from custom_components.heatpump_optimizer import coordinator as co, price_model as pm
from custom_components.heatpump_optimizer.const import CONF_PRICE_ENTITY, CONF_PRICE_SOURCE, PRICE_SOURCE_ENTITY

mut = mutate(pm, "pull_prices", "        if not config.get(CONF_PRICE_ENTITY):", "        if False:")
good = NS(state="1.2", attributes={"today": [1.0] * 24})


class States:
    def get(self, entity_id):
        return good  # every lookup that is made would find a valid sensor


hass = NS(states=States())
run = lambda fn, cfg, st: asyncio.run(fn(None, cfg, st))
moved_caller = 0
forms = {"absent": {}, "empty": {CONF_PRICE_ENTITY: ""}, "none": {CONF_PRICE_ENTITY: None}}
for name, extra in forms.items():
    cfg = {CONF_PRICE_SOURCE: PRICE_SOURCE_ENTITY, **extra}
    st = co._price_entity_state(hass, cfg)  # the coordinator's one call site composes these two
    b, m = run(pm.pull_prices, cfg, st), run(mut, cfg, st)
    moved_caller += b != m
    print(f"RESULT caller_state_{name}={st!r}")
    print(f"RESULT caller_verdict_baseline_{name}={b!r}")
    print(f"RESULT caller_verdict_mutant_{name}={m!r}")
print(f"RESULT caller_inputs_moved={moved_caller} count")
# outside the coordinator's composition: an entity state handed in with no entity configured
cfg = {CONF_PRICE_SOURCE: PRICE_SOURCE_ENTITY}
b, m = run(pm.pull_prices, cfg, good), run(mut, cfg, good)
print(f"RESULT direct_verdict_baseline={b!r}")
print(f"RESULT direct_verdict_mutant={m!r}")
print(f"RESULT direct_moved={int(b != m)} count")
tail()
