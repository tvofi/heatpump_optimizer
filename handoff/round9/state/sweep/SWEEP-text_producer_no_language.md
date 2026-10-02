# Sweep: "text producer takes no language parameter"

Round 9, D14 sweep, thread S7. Baseline `1936d5ca`. Finding: D4-s2-81
(verified, medium). Not a ledger class (new).

## Enumerator

```
$ grep -n "describe_setup\|render_text_summary\|rank_sensor_advisor" custom_components/heatpump_optimizer/*.py
```

widened to every function signature in `topology.py` that produces
user-facing text or labels:

```
$ grep -n "^def describe_setup\|^def render_text_summary\|^_SLOTS" custom_components/heatpump_optimizer/topology.py
topology.py:117:_SLOTS: tuple[...] = (  -- literal English labels, e.g. "Outdoor temperature", "Solar radiation", "Indoor temperature"
topology.py:389:def describe_setup(config: dict[str, Any]) -> dict[str, Any]:
topology.py:538:def render_text_summary(setup: dict[str, Any]) -> str:
```

## Positive control

Neither `describe_setup(config)` nor `render_text_summary(setup)` takes a
language argument; `describe_setup`'s `slots[].label` comes verbatim from
the `_SLOTS` catalog (topology.py:117 onward), hardcoded English strings
("Outdoor temperature", "Solar radiation", "Indoor temperature", ...) with
no translation-key indirection. `coordinator.py:7042`'s `describe_setup`
method (the production call site) passes only `self._ctx._config` through,
confirming the language never enters the call chain from either the config
flow or the card. Confirmed present at baseline `1936d5ca`; `topology.py`
is unchanged on `origin/main` (not in the 4-file diff).

## Null control

Every other user-facing string producer checked in `sensor.py` (e.g.
`_sensor_advisor_attribute`) and `config_flow.py`'s own step
descriptions goes through `strings.json`/`translations/{en,sv}.json` and
HA's own language-aware rendering — the widened grep does not implicate
those; only the two `topology.py` functions and their `_SLOTS` catalog
bypass translation entirely.

## Perturbation

Not independently re-run; the finding's own report already states the
observed consequence directly ("Setup overview page and setup diagram
publish English slot text on a Swedish install") without a separate mutant
harness — the mechanism is a missing parameter, not a runtime branch a
one-line flip would move.

## Disposition

| seam | disposition |
|---|---|
| topology.py:117 `_SLOTS` catalog (hardcoded English labels) | instance — D4-s2-81 |
| topology.py:389 `describe_setup` (no lang param) | instance — D4-s2-81 |
| topology.py:538 `render_text_summary` (no lang param) | instance — D4-s2-81 |
| card.js's setup overview/diagram rendering (consumes the above) | instance — D4-s2-81 (same mechanism, the finding's own "files" list) |
| sensor.py, config_flow.py (translation-key-based strings) | not applicable — already language-aware via `strings.json`/`translations/` |

All four `topology.py`/card.js sites are one mechanism (the catalog and the
two functions that read it), per COMMON.md's phenomenon-grouping rule —
one finding, four places it shows.

## Count

N = 1 verified finding + 0 sweep-confirmed instances = **1**. **rca: false**,
matching the brief.

## Barrier proposal

None built (N < 3). The finder's own scope: route `_SLOTS` labels (and any
other literal string `describe_setup`/`render_text_summary` produce)
through the same `strings.json`/`translations/` mechanism the rest of the
integration uses, threading a language argument through both functions and
their card-side consumers — left for the fixer.

## Gate seconds

~0.02s (grep plus a manual read of `_SLOTS` and the two function
signatures).
