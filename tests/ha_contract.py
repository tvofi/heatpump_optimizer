#!/usr/bin/env python3
"""What ``tests/hastub`` owes Home Assistant, stated so both can be measured (#536).

    PYTHONPATH=tests/hastub python tests/ha_contract.py     # provider: stub
    python tests/ha_contract.py                             # provider: real

Every lane in ``tests/`` runs with ``PYTHONPATH=tests/hastub``, so a green test
proves the code works against *the stub's* behaviour. Four divergences were
found the expensive way -- one per seat, after the fact -- and the pattern each
time was that the stub was written from what the code under test needed, which
is exactly the shape that agrees with a wrong implementation.

THE ONE IDEA HERE: this file imports ``homeassistant`` the ordinary way and
never says which one it wants. The gate runs it with the stub on the path; the
real-Home-Assistant lane (``nightly_ha.py``, #521) runs the SAME FILE inside
the container where the genuine package is installed. So a contract is not a
transcription somebody has to keep true -- it is executed against upstream, and
a contract that misreads upstream turns that lane red.

Three products, and they fail for different reasons:

* **CONTRACTS** -- executable behaviour, each citing the upstream source it was
  read from. ``expect="both"`` must hold for the stub and for real Home
  Assistant. ``expect="real"`` states upstream behaviour the stub does NOT
  have: it must FAIL against the stub (reported ``xfail``) and PASS against
  real Home Assistant. An ``expect="real"`` contract that starts passing
  against the stub FAILS -- the divergence was repaired and its inventory entry
  is now a lie.
* **PROBES** -- values read out of whichever provider is loaded, compared
  ACROSS the two runs by ``--compare``. This is what ``tests/entities.py``'s
  hand-transcribed ``_REAL_HA_PLATFORMS`` frozenset wanted to be: a member the
  stub invented is caught by measuring the real enum, not by remembering it.
* **INVENTORY** -- every module-level public name the stub declares, with a
  disposition. A new stub symbol with no disposition fails the completeness
  check. That is the part that is not one more repaired symbol: a convenience
  shape can no longer be added silently.

WHAT THIS DOES NOT COVER, said plainly because a check that cannot fail is
worse than none:

* **A behaviour nobody wrote a contract for.** Completeness forces a
  *disposition*, never a correct contract. ``HOLDER`` is a claim this file
  takes on trust.
* **A symbol upstream has that the stub does not model at all.** Nothing
  imports it, so nothing misses it. That is the #516/#568 ``section`` class and
  it is a design gap, not a fidelity gap -- ``--compare`` prints the unmodelled
  public names of every module the stub touches so it is at least visible.
* **Anything needing a running ``hass``** -- the issue registry, the store,
  entity registration. Contracts here construct nothing bigger than an object.
* **Timing.** The real half is nightly and needs Docker, so a contract that is
  wrong about upstream is caught within a day, not on the pull request.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

# Upstream is read at the floor ``hacs.json`` declares, never at "latest": a
# contract written from a newer release would refuse the oldest install this
# integration claims to support.
UPSTREAM = "2025.2.0"


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------
# Deliberately not ``harness.Results``: the container half mounts this file and
# nothing else from tests/, so an import of a sibling would make the real
# provider unrunnable -- which is the half that makes the contracts honest.


class Report:
    def __init__(self, title: str) -> None:
        self.title = title
        self.failures = 0
        self.checks = 0
        print(f"\n=== {title} ===")

    def section(self, name: str) -> None:
        print(f"\n-- {name}")

    def check(self, name: str, ok: object, detail: str = "") -> bool:
        self.checks += 1
        if ok:
            print(f"  ok   {name}")
        else:
            self.failures += 1
            print(f"  FAIL {name}" + (f"  [{detail}]" if detail else ""))
        return bool(ok)

    def note(self, name: str, detail: str = "") -> None:
        print(f"  ..   {name}" + (f"  [{detail}]" if detail else ""))

    def close(self, label: str) -> int:
        if self.failures:
            print(f"\n{self.failures} of {self.checks} {label} FAILED")
            return 1
        print(f"\nALL {self.checks} {label} PASSED")
        return 0


# ---------------------------------------------------------------------------
# dispositions
# ---------------------------------------------------------------------------

FAITHFUL = "faithful"      # reproduces upstream; needs >=1 expect="both" contract
DIVERGENT = "divergent"    # measured mismatch; needs >=1 expect="real" contract
UNVERIFIED = "unverified"  # behaviour pinned against the stub only; needs >=1 expect="stub"
SIMPLIFIED = "simplified"  # does less than upstream, deliberately; states what is absent
HOLDER = "holder"          # pure data, makes no decision; no contract owed

# UNVERIFIED is the honest name for the issue's third category -- "a convenience
# shape nobody ever checked against upstream". It is not a slur on the symbol:
# it says the fidelity claim cannot be EXECUTED here, because upstream's version
# needs a running hass and the contracts in this file construct nothing bigger
# than an object. The stub contract still pins it against regression; what it
# does not do is prove it matches Home Assistant. Promoting one to FAITHFUL
# means finding a way to run it in the container, not deciding it looks right.

DISPOSITIONS = (FAITHFUL, DIVERGENT, UNVERIFIED, SIMPLIFIED, HOLDER)


class Entry:
    """One stub symbol's disposition.

    ``absent`` is the teeth on a SIMPLIFIED entry: it names the members whose
    absence IS the declared divergence, and they are asserted still absent. A
    declaration that the stub does less than upstream is a claim, and a claim
    that nothing checks rots the moment somebody improves the stub without
    reading this file -- which is how the four measured divergences got in.
    """

    def __init__(self, disposition: str, why: str, *, absent: tuple = (), issue: str = "") -> None:
        self.disposition = disposition
        self.why = why
        self.absent = absent
        self.issue = issue


def F(why: str) -> Entry:
    return Entry(FAITHFUL, why)


def D(why: str, issue: str) -> Entry:
    return Entry(DIVERGENT, why, issue=issue)


def U(why: str) -> Entry:
    return Entry(UNVERIFIED, why)


def S(why: str, *, absent: tuple = ()) -> Entry:
    return Entry(SIMPLIFIED, why, absent=absent)


def H(why: str) -> Entry:
    return Entry(HOLDER, why)


# ---------------------------------------------------------------------------
# the inventory
# ---------------------------------------------------------------------------
# Keyed by the fully qualified name of a MODULE-LEVEL public symbol. Class
# members are deliberately not enumerated: a per-attribute inventory would fail
# on every ``_attr_*`` a platform base gains, and the completeness check would
# become something to route around rather than to satisfy.

INVENTORY: dict[str, Entry] = {
    # -- components.binary_sensor ------------------------------------------
    "homeassistant.components.binary_sensor.BinarySensorDeviceClass": H(
        "string constants; every member is probed against the real enum"
    ),
    "homeassistant.components.binary_sensor.BinarySensorEntity": H(
        "attribute defaults only; the real base's state machinery is unused here"
    ),
    # -- components.button --------------------------------------------------
    "homeassistant.components.button.ButtonEntity": S(
        "async_press raises NotImplementedError as upstream does; nothing else "
        "of the real base is modelled",
        absent=("async_press_action", "async_added_to_hass"),
    ),
    # -- components.climate -------------------------------------------------
    "homeassistant.components.climate.ClimateEntityFeature": H("integer flags, probed"),
    "homeassistant.components.climate.HVACMode": H("string constants, probed"),
    "homeassistant.components.climate.HVACAction": H("string constants, probed"),
    "homeassistant.components.climate.ClimateEntity": H("attribute defaults only"),
    # -- components.datetime ------------------------------------------------
    "homeassistant.components.datetime.DateTimeEntity": H("attribute defaults only"),
    # -- components.diagnostics ---------------------------------------------
    "homeassistant.components.diagnostics.REDACTED": H("a constant, probed for equality"),
    "homeassistant.components.diagnostics.async_redact_data": F(
        "the proven case (#509/#535): upstream skips None and the empty string "
        "BEFORE redacting, and a fix that missed it returned None on every real "
        "install while every check stayed green"
    ),
    # -- components.mqtt ----------------------------------------------------
    "homeassistant.components.mqtt.async_publish": S(
        "accepts and discards; the integration's two ECL110 topics are observed "
        "through the coordinator, never through a broker"
    ),
    "homeassistant.components.mqtt.async_subscribe": S(
        "accepts and discards; nothing here subscribes"
    ),
    # -- components.repairs -------------------------------------------------
    "homeassistant.components.repairs.RepairsFlow": H(
        "the three result builders return their kwargs; no flow manager exists here"
    ),
    "homeassistant.components.repairs.ConfirmRepairFlow": F(
        "upstream's confirm-only flow: async_step_init delegates to "
        "async_step_confirm, which shows a form until user_input arrives"
    ),
    # -- components.sensor --------------------------------------------------
    "homeassistant.components.sensor.SensorDeviceClass": H("string constants, probed"),
    "homeassistant.components.sensor.SensorStateClass": H("string constants, probed"),
    "homeassistant.components.sensor.DEVICE_CLASS_STATE_CLASSES": H(
        "a transcribed decision table; every declared pair is probed against "
        "upstream's own, which is the only thing that can keep it true"
    ),
    "homeassistant.components.sensor.SensorEntity": S(
        "attribute defaults only. Upstream's SensorEntity.state validates on "
        "EVERY state write -- a non-numeric device class may carry no unit, and "
        "a value outside `options` raises ValueError -- and none of that is "
        "here, so a test asserting a sensor is correctly enumerated passes "
        "vacuously. PR #571 adds the enum half; when it lands this entry is "
        "wrong and the absence assertion below is what says so",
        absent=("state", "options", "native_unit_of_measurement"),
    ),
    # -- components.switch --------------------------------------------------
    "homeassistant.components.switch.SwitchEntity": H("attribute defaults only"),
    # -- config_entries -----------------------------------------------------
    "homeassistant.config_entries.SOURCE_RECONFIGURE": H("a constant, probed"),
    "homeassistant.config_entries.HANDLERS": S(
        "a plain dict where upstream has a Registry; __init_subclass__ populates "
        "it the same way, and supports_reconfigure reads it",
        absent=("register",),
    ),
    "homeassistant.config_entries.ConfigEntryState": H("enum members, probed"),
    "homeassistant.config_entries.ConfigEntry": F(
        "runtime_data is an annotation, not an attribute: absent until the "
        "integration assigns it in async_setup_entry, exactly as upstream. A "
        "stub that pre-filled it would let a platform read a coordinator "
        "nobody stored"
    ),
    "homeassistant.config_entries.ConfigFlow": F(
        "add_suggested_values_to_schema drops advanced markers unless the flow "
        "shows advanced options, and copies the marker rather than mutating the "
        "flow's own schema"
    ),
    "homeassistant.config_entries.OptionsFlow": H("ConfigFlow with no additions"),
    # -- const --------------------------------------------------------------
    "homeassistant.const.Platform": H(
        "a subset of the real enum. A member the stub invents makes the suite "
        "pass on code that cannot import in Home Assistant -- DIAGNOSTICS did "
        "exactly that in v6.3.1 -- so every member is probed against upstream's"
    ),
    "homeassistant.const.CONF_NAME": H("a constant, probed"),
    "homeassistant.const.UnitOfSpeed": H("string constants, probed"),
    "homeassistant.const.UnitOfPower": H("string constants, probed"),
    "homeassistant.const.UnitOfEnergy": H("string constants, probed"),
    "homeassistant.const.UnitOfTemperature": H("string constants, probed"),
    "homeassistant.const.UnitOfVolume": H("string constants, probed"),
    "homeassistant.const.PERCENTAGE": H("a constant, probed"),
    "homeassistant.const.ATTR_TEMPERATURE": H("a constant, probed"),
    # -- core ---------------------------------------------------------------
    "homeassistant.core.HomeAssistant": S(
        "a bare marker class. Tests use harness.FakeHass, never this",
        absent=("states", "config", "bus", "async_add_executor_job"),
    ),
    "homeassistant.core.ServiceCall": S(
        "a bare marker class; the service tests build their own call objects",
        absent=("data", "domain", "service"),
    ),
    "homeassistant.core.SupportsResponse": H("string constants, probed"),
    "homeassistant.core.callback": D(
        "the identity. Upstream tags the decorated function with _hass_callback, "
        "which is how the event loop decides to run it inline instead of in an "
        "executor -- invisible to any lane here, none of which has an event loop",
        issue="#536",
    ),
    # -- data_entry_flow ----------------------------------------------------
    "homeassistant.data_entry_flow.FlowResult": S(
        "``dict``. Upstream is a generic TypedDict; nothing here reads a type",
        absent=("__required_keys__",),
    ),
    "homeassistant.data_entry_flow.FlowError": D(
        "upstream is FlowError(HomeAssistantError); the stub's base is "
        "Exception, so code catching HomeAssistantError catches an aborted flow "
        "on a real install and not here",
        issue="#536",
    ),
    "homeassistant.data_entry_flow.AbortFlow": F(
        "reason and description_placeholders land on the instance and the "
        "message is 'Flow aborted: <reason>', as upstream"
    ),
    # -- exceptions ---------------------------------------------------------
    "homeassistant.exceptions.HomeAssistantError": D(
        "the three translation kwargs land on the instance as upstream, but "
        "upstream ALSO sets args=(translation_key,) when a translated error is "
        "raised with no message, so str(err) is the key rather than the empty "
        "string. The stub's is empty",
        issue="#536",
    ),
    "homeassistant.exceptions.ServiceValidationError": F(
        "subclasses HomeAssistantError, which is what lets a caller catch the "
        "base rather than a bare ValueError"
    ),
    # -- helpers.aiohttp_client ---------------------------------------------
    "homeassistant.helpers.aiohttp_client.async_get_clientsession": S(
        "raises rather than returning a session: no lane here may reach the "
        "network, and a stub returning a real session would let one"
    ),
    # -- helpers.config_validation ------------------------------------------
    "homeassistant.helpers.config_validation.string": D(
        "upstream raises vol.Invalid on None and on a list or dict; the stub is "
        "str(), so None becomes the string 'None'. Production validates service "
        "call data with cv.string, so an automation passing null is refused on "
        "a real install and silently coerced in every lane here",
        issue="#536",
    ),
    "homeassistant.helpers.config_validation.boolean": D(
        "upstream maps the strings 1/true/yes/on/enable and their negatives, "
        "and RAISES vol.Invalid on anything else; the stub is bool(), so "
        "boolean('false') is True and no input is ever refused. Production uses "
        "cv.boolean in three service schemas",
        issue="#536",
    ),
    "homeassistant.helpers.config_validation.positive_int": D(
        "upstream is vol.All(vol.Coerce(int), vol.Range(min=0)); the stub is "
        "int(), which accepts a negative",
        issue="#536",
    ),
    "homeassistant.helpers.config_validation.positive_float": D(
        "upstream is vol.All(vol.Coerce(float), vol.Range(min=0)); the stub is "
        "float(), which accepts a negative",
        issue="#536",
    ),
    "homeassistant.helpers.config_validation.config_entry_only_config_schema": S(
        "returns the configuration unchanged. Upstream logs an error and raises "
        "a repair issue when YAML carries the domain key, both of which need a "
        "hass; nothing here reads YAML"
    ),
    # -- helpers.device_registry --------------------------------------------
    "homeassistant.helpers.device_registry.DeviceEntryType": H("string constant, probed"),
    # -- helpers.entity -----------------------------------------------------
    "homeassistant.helpers.entity.DeviceInfo": H("a dict subclass, as upstream's TypedDict"),
    "homeassistant.helpers.entity.EntityCategory": H("string constants, probed"),
    # -- helpers.entity_platform --------------------------------------------
    "homeassistant.helpers.entity_platform.AddEntitiesCallback": H(
        "``object``; a type alias nothing calls"
    ),
    # -- helpers.entity_registry --------------------------------------------
    "homeassistant.helpers.entity_registry.RegistryEntry": S(
        "four fields of the real dataclass -- the ones the retired-entity "
        "cleanup reads",
        absent=("disabled_by", "device_id", "platform"),
    ),
    "homeassistant.helpers.entity_registry.EntityRegistry": S(
        "a dict of entries plus a test-facing add(); upstream's creation path, "
        "with its unique-id collision handling, is not mimicked",
        absent=("async_get_or_create", "async_update_entity"),
    ),
    "homeassistant.helpers.entity_registry.async_get": U(
        "one registry per hass, created on first use and stored on hass.data. "
        "Upstream's needs a booted hass with its registries loaded, so the "
        "contract below pins the stub's own singleton behaviour and proves "
        "nothing about the real one"
    ),
    "homeassistant.helpers.entity_registry.async_entries_for_config_entry": U(
        "filters the registry by config_entry_id. Upstream reads an index built "
        "at registry load, which no bare process here can construct"
    ),
    # -- helpers.event ------------------------------------------------------
    "homeassistant.helpers.event.async_track_time_interval": S(
        "returns an unsubscribe that does nothing; no lane has a clock to fire"
    ),
    "homeassistant.helpers.event.async_track_state_change_event": U(
        "returns an unsubscribe that actually removes the registration, so a "
        "listener leak is visible. Upstream needs hass.bus and an event loop, "
        "so what is pinned is the stub's own wiring"
    ),
    # -- helpers.issue_registry ---------------------------------------------
    "homeassistant.helpers.issue_registry.IssueSeverity": H("string constants, probed"),
    "homeassistant.helpers.issue_registry.async_create_issue": U(
        "re-creating an existing (domain, issue_id) REPLACES it rather than "
        "appending, so a chatty detector shows as one issue and not a pile. "
        "Upstream's writes to a hass-backed store"
    ),
    "homeassistant.helpers.issue_registry.async_delete_issue": U(
        "removes by (domain, issue_id) and is a no-op when absent. Upstream's "
        "needs the same hass-backed store"
    ),
    # -- helpers.selector ---------------------------------------------------
    "homeassistant.helpers.selector.SelectSelectorConfig": H("a dict subclass"),
    "homeassistant.helpers.selector.SelectSelectorMode": H("string constants, probed"),
    "homeassistant.helpers.selector.SelectSelector": F(
        "upstream validates with vol.Schema(str) before vol.In(options), so a "
        "non-string default -- an int number of minutes against string options "
        "-- fails the moment the user leaves the field untouched. A permissive "
        "stub let exactly that reach a release"
    ),
    "homeassistant.helpers.selector.NumberSelectorConfig": H("a dict subclass"),
    "homeassistant.helpers.selector.NumberSelectorMode": H("string constants, probed"),
    "homeassistant.helpers.selector.NumberSelector": F(
        "mode defaults to slider and validate_slider then refuses a slider "
        "missing either bound, so an unbounded number field exists only in box "
        "mode; __call__ coerces to float and refuses either bound"
    ),
    "homeassistant.helpers.selector.TextSelectorConfig": H("a dict subclass"),
    "homeassistant.helpers.selector.TextSelectorType": H("string constants, probed"),
    "homeassistant.helpers.selector.TextSelector": S(
        "records its config and returns the value; upstream coerces to str and "
        "honours multiple/type",
        absent=("CONFIG_SCHEMA",),
    ),
    "homeassistant.helpers.selector.EntitySelectorConfig": H("a dict subclass"),
    "homeassistant.helpers.selector.EntitySelector": S(
        "records its config and returns the value; upstream validates the "
        "entity id and the domain/device_class filters",
        absent=("CONFIG_SCHEMA",),
    ),
    "homeassistant.helpers.selector.LocationSelectorConfig": H("a dict subclass"),
    "homeassistant.helpers.selector.LocationSelector": S(
        "records its config and returns the value; upstream validates the "
        "latitude/longitude schema",
        absent=("CONFIG_SCHEMA",),
    ),
    "homeassistant.helpers.selector.BooleanSelector": S(
        "records its config and returns the value; upstream coerces with "
        "cv.boolean",
        absent=("CONFIG_SCHEMA",),
    ),
    "homeassistant.helpers.selector.TimeSelector": S(
        "records its config and returns the value; upstream validates a time",
        absent=("CONFIG_SCHEMA",),
    ),
    # -- helpers.storage ----------------------------------------------------
    "homeassistant.helpers.storage.SAVE_COUNTS": H(
        "a test-facing counter with no upstream counterpart"
    ),
    "homeassistant.helpers.storage.Store": S(
        "an honest in-memory round trip -- keyed by storage key across "
        "instances so a simulated restart loads what an earlier one saved, and "
        "serialised eagerly so a payload the real Store could not write raises "
        "here too. Upstream's delayed write, migration and atomic replace are "
        "not modelled",
        absent=("async_delay_save", "_async_migrate_func"),
    ),
    # -- helpers.translation ------------------------------------------------
    "homeassistant.helpers.translation.async_get_translations": S(
        "returns an empty mapping; tests/entities.py reads strings.json "
        "directly rather than through the loader"
    ),
    # -- helpers.update_coordinator -----------------------------------------
    "homeassistant.helpers.update_coordinator.DataUpdateCoordinator": S(
        "counts refreshes instead of running them, so a test exercising a "
        "setter is not dragged into a full optimization; async_shutdown records "
        "the call so an override that forgets super() is visible",
        absent=("_debounced_refresh", "async_add_listener"),
    ),
    "homeassistant.helpers.update_coordinator.UpdateFailed": H("a bare exception, as upstream"),
    "homeassistant.helpers.update_coordinator.CoordinatorEntity": F(
        "available returns the coordinator's last_update_success, which is what "
        "an entity overriding available has to AND its own condition with"
    ),
    # -- loader -------------------------------------------------------------
    "homeassistant.loader.async_get_integration": S(
        "returns None; nothing here reads a manifest through the loader"
    ),
    # -- util.dt ------------------------------------------------------------
    "homeassistant.util.dt.DEFAULT_TIME_ZONE": D(
        "None unless HASTUB_TZ is set, where upstream always carries the "
        "instance's configured zone. Opt-in because every golden fixture was "
        "recorded against the identity as_local below",
        issue="#536",
    ),
    "homeassistant.util.dt.freeze": H("a test-facing clock pin with no upstream counterpart"),
    "homeassistant.util.dt.now": F(
        "returns an aware datetime in DEFAULT_TIME_ZONE when one is configured"
    ),
    "homeassistant.util.dt.utcnow": F("returns an aware datetime in UTC, as upstream"),
    "homeassistant.util.dt.parse_datetime": F(
        "returns None rather than raising on an unparseable string, as upstream"
    ),
    "homeassistant.util.dt.as_local": D(
        "the identity when no zone is configured, where upstream always "
        "converts. Every golden fixture was recorded that way, so making it "
        "faithful shifts every one of them by the runner's UTC offset",
        issue="#536",
    ),
}

# Whole upstream modules the stub does not model at all, and what covers them
# instead. Absence is not unfaithfulness -- there is nothing to be unfaithful
# about -- but it is the risk this file exists to make visible, and #525 is
# what it looks like when nobody writes it down.
UNMODELLED = {
    "homeassistant.util.loop": (
        "Home Assistant's blocking-call detector. It fires TWICE on this "
        "integration at every setup and shutdown, and both warnings tell the "
        "user to file a bug here (#525) -- invisible to every lane in tests/, "
        "found only by the first green run of the real-Home-Assistant lane. "
        "Covered by nightly_ha.py's log:no_new_blocking_call, which pins the "
        "two known offenders and fails on a third."
    ),
    "homeassistant.helpers.entity_component": (
        "the per-domain entity component. nightly_ha.py reaches it through the "
        "real package to resolve an entity object; no lane here needs one."
    ),
    "homeassistant.helpers.device_registry.DeviceRegistry": (
        "the registry itself. The stub models DeviceEntryType alone, because "
        "the coordinator's device_info property is the only production import."
    ),
}


# ---------------------------------------------------------------------------
# contracts
# ---------------------------------------------------------------------------

CONTRACTS: list = []


def contract(symbol: str, name: str, *, cite: str, expect: str = "both"):
    """Register one executable statement about Home Assistant's behaviour.

    ``cite`` is the upstream path the statement was read from, at UPSTREAM.
    It is prose, not a resolvable reference: this repository does not vendor
    Home Assistant, and the thing that keeps the statement true is that it is
    EXECUTED against the real package by the nightly lane, not that a path was
    written next to it.
    """

    def register(fn):
        CONTRACTS.append((symbol, name, cite, expect, fn))
        return fn

    return register


def raises(fn) -> bool:
    """Whether calling ``fn`` raises anything.

    The exception TYPE is deliberately not asserted. Upstream raises
    vol.Invalid, which is not a ValueError, and the stub raises ValueError; a
    contract pinning either would fail against one provider for a reason no
    production path depends on -- nothing in this integration catches a
    selector's refusal by type. What both must agree on is that the value is
    refused at all.
    """
    try:
        fn()
    except Exception:  # noqa: BLE001 - the point is that anything counts
        return True
    return False


# -- components.diagnostics.async_redact_data -------------------------------

@contract(
    "homeassistant.components.diagnostics.async_redact_data",
    "None is skipped, not redacted",
    cite="components/diagnostics/util.py -- `if value is None: continue`",
)
def _redact_none():
    from homeassistant.components.diagnostics import async_redact_data

    assert async_redact_data({"latitude": None}, {"latitude"})["latitude"] is None


@contract(
    "homeassistant.components.diagnostics.async_redact_data",
    "the empty string is skipped, not redacted",
    cite="components/diagnostics/util.py -- `if isinstance(value, str) and not value`",
)
def _redact_empty():
    from homeassistant.components.diagnostics import async_redact_data

    assert async_redact_data({"token": ""}, {"token"})["token"] == ""


@contract(
    "homeassistant.components.diagnostics.async_redact_data",
    "a present value is replaced by REDACTED",
    cite="components/diagnostics/util.py -- `redacted[key] = REDACTED`",
)
def _redact_present():
    from homeassistant.components.diagnostics import REDACTED, async_redact_data

    assert async_redact_data({"token": "abc"}, {"token"})["token"] == REDACTED


@contract(
    "homeassistant.components.diagnostics.async_redact_data",
    "a non-mapping, non-list value passes through unchanged",
    cite="components/diagnostics/util.py -- the isinstance guard returns data",
)
def _redact_scalar():
    from homeassistant.components.diagnostics import async_redact_data

    assert async_redact_data("abc", {"abc"}) == "abc"
    assert async_redact_data(7, {7}) == 7


@contract(
    "homeassistant.components.diagnostics.async_redact_data",
    "nested mappings and lists are walked",
    cite="components/diagnostics/util.py -- the Mapping and list branches recurse",
)
def _redact_nested():
    from homeassistant.components.diagnostics import REDACTED, async_redact_data

    out = async_redact_data({"a": {"t": "x"}, "b": [{"t": "y"}]}, {"t"})
    assert out["a"]["t"] == REDACTED
    assert out["b"][0]["t"] == REDACTED


@contract(
    "homeassistant.components.diagnostics.async_redact_data",
    "the input mapping is not mutated",
    cite="components/diagnostics/util.py -- `redacted = {**data}`",
)
def _redact_copies():
    from homeassistant.components.diagnostics import async_redact_data

    original = {"token": "abc"}
    async_redact_data(original, {"token"})
    assert original["token"] == "abc"


# -- helpers.selector.NumberSelector ----------------------------------------

@contract(
    "homeassistant.helpers.selector.NumberSelector",
    "mode defaults to slider, so an unbounded selector is refused",
    cite="helpers/selector.py -- CONFIG_SCHEMA defaults mode to SLIDER, then validate_slider",
)
def _number_default_slider():
    from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig

    assert raises(lambda: NumberSelector(NumberSelectorConfig()))


@contract(
    "homeassistant.helpers.selector.NumberSelector",
    "a slider missing either bound is refused",
    cite="helpers/selector.py -- validate_slider: 'min and max are required in slider mode'",
)
def _number_slider_bounds():
    from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig

    assert raises(lambda: NumberSelector(NumberSelectorConfig(min=0)))
    assert raises(lambda: NumberSelector(NumberSelectorConfig(max=9)))


@contract(
    "homeassistant.helpers.selector.NumberSelector",
    "box mode may be unbounded",
    cite="helpers/selector.py -- validate_slider returns early when mode is box",
)
def _number_box_unbounded():
    from homeassistant.helpers.selector import (
        NumberSelector,
        NumberSelectorConfig,
        NumberSelectorMode,
    )

    NumberSelector(NumberSelectorConfig(mode=NumberSelectorMode.BOX))


@contract(
    "homeassistant.helpers.selector.NumberSelector",
    "the value is coerced to float and range-checked",
    cite="helpers/selector.py -- `vol.Coerce(float)(data)` then the min/max guards",
)
def _number_call():
    from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig

    selector = NumberSelector(NumberSelectorConfig(min=0, max=10))
    assert selector("5") == 5.0
    assert raises(lambda: selector(-1))
    assert raises(lambda: selector(11))
    assert raises(lambda: selector("not a number"))


# -- helpers.selector.SelectSelector ----------------------------------------

@contract(
    "homeassistant.helpers.selector.SelectSelector",
    "a non-string value is refused before the options are consulted",
    cite="helpers/selector.py -- `parent_schema(vol.Schema(str)(data))`",
)
def _select_type():
    from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

    selector = SelectSelector(SelectSelectorConfig(options=["15", "30"]))
    assert raises(lambda: selector(15))


@contract(
    "homeassistant.helpers.selector.SelectSelector",
    "a value outside the options is refused and a listed one is returned",
    cite="helpers/selector.py -- `vol.In(options)`",
)
def _select_membership():
    from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

    selector = SelectSelector(SelectSelectorConfig(options=["15", "30"]))
    assert selector("15") == "15"
    assert raises(lambda: selector("45"))


# -- exceptions --------------------------------------------------------------

@contract(
    "homeassistant.exceptions.HomeAssistantError",
    "the three translation kwargs land on the instance",
    cite="exceptions.py -- HomeAssistantError.__init__ assigns all three",
)
def _error_translation_kwargs():
    from homeassistant.exceptions import HomeAssistantError

    err = HomeAssistantError(
        translation_domain="heatpump_optimizer",
        translation_key="k",
        translation_placeholders={"a": "b"},
    )
    assert err.translation_domain == "heatpump_optimizer"
    assert err.translation_key == "k"
    assert err.translation_placeholders == {"a": "b"}


@contract(
    "homeassistant.exceptions.HomeAssistantError",
    "a translated error with no message carries the key as its message",
    cite="exceptions.py -- `if not args and translation_key and translation_domain: args = (translation_key,)`",
    expect="real",
)
def _error_generated_message():
    from homeassistant.exceptions import HomeAssistantError

    err = HomeAssistantError(translation_domain="heatpump_optimizer", translation_key="k")
    assert err.args == ("k",)


@contract(
    "homeassistant.exceptions.ServiceValidationError",
    "subclasses HomeAssistantError",
    cite="exceptions.py -- `class ServiceValidationError(HomeAssistantError)`",
)
def _service_validation_base():
    from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

    assert issubclass(ServiceValidationError, HomeAssistantError)


# -- data_entry_flow ---------------------------------------------------------

@contract(
    "homeassistant.data_entry_flow.AbortFlow",
    "reason and placeholders land on the instance, with upstream's message",
    cite="data_entry_flow.py -- AbortFlow.__init__",
)
def _abort_flow_fields():
    from homeassistant.data_entry_flow import AbortFlow

    err = AbortFlow("already_configured", {"a": "b"})
    assert err.reason == "already_configured"
    assert err.description_placeholders == {"a": "b"}
    assert str(err) == "Flow aborted: already_configured"


@contract(
    "homeassistant.data_entry_flow.FlowError",
    "a flow error is a HomeAssistantError",
    cite="data_entry_flow.py -- `class FlowError(HomeAssistantError)`",
    expect="real",
)
def _flow_error_base():
    from homeassistant.data_entry_flow import FlowError
    from homeassistant.exceptions import HomeAssistantError

    assert issubclass(FlowError, HomeAssistantError)


# -- helpers.config_validation -----------------------------------------------

@contract(
    "homeassistant.helpers.config_validation.string",
    "None is refused rather than coerced to 'None'",
    cite="helpers/config_validation.py -- `if value is None: raise vol.Invalid`",
    expect="real",
)
def _cv_string_none():
    from homeassistant.helpers.config_validation import string

    assert raises(lambda: string(None))


@contract(
    "homeassistant.helpers.config_validation.boolean",
    "the negative strings are False and an unrecognised one is refused",
    cite="helpers/config_validation.py -- boolean's two string tuples, then `raise vol.Invalid`",
    expect="real",
)
def _cv_boolean_strings():
    from homeassistant.helpers.config_validation import boolean

    assert boolean("false") is False
    assert boolean("off") is False
    assert raises(lambda: boolean("maybe"))


@contract(
    "homeassistant.helpers.config_validation.positive_int",
    "a negative is refused",
    cite="helpers/config_validation.py -- `vol.All(vol.Coerce(int), vol.Range(min=0))`",
    expect="real",
)
def _cv_positive_int():
    from homeassistant.helpers.config_validation import positive_int

    assert raises(lambda: positive_int(-1))


@contract(
    "homeassistant.helpers.config_validation.positive_float",
    "a negative is refused",
    cite="helpers/config_validation.py -- `vol.All(vol.Coerce(float), vol.Range(min=0))`",
    expect="real",
)
def _cv_positive_float():
    from homeassistant.helpers.config_validation import positive_float

    assert raises(lambda: positive_float(-1.0))


# -- config_entries ----------------------------------------------------------

@contract(
    "homeassistant.config_entries.ConfigEntry",
    "runtime_data is absent until the integration assigns it",
    cite="config_entries.py -- ConfigEntry declares `runtime_data: _DataT` as an annotation",
)
def _runtime_data_absent():
    from homeassistant.config_entries import ConfigEntry

    assert "runtime_data" in ConfigEntry.__annotations__
    assert not hasattr(ConfigEntry, "runtime_data")


@contract(
    "homeassistant.config_entries.ConfigFlow",
    "an advanced marker is dropped unless the flow shows advanced options",
    cite="data_entry_flow.py -- add_suggested_values_to_schema's `# Exclude advanced field`",
)
def _suggested_drops_advanced():
    import voluptuous as vol

    from homeassistant.config_entries import ConfigFlow

    schema = vol.Schema(
        {
            vol.Optional("plain"): str,
            vol.Optional("adv", description={"advanced": True}): str,
        }
    )
    keys = {str(k) for k in ConfigFlow().add_suggested_values_to_schema(schema, None).schema}
    assert keys == {"plain"}


@contract(
    "homeassistant.config_entries.ConfigFlow",
    "a suggested value is attached without mutating the flow's own schema",
    cite="data_entry_flow.py -- `new_key = copy.copy(key)` before setting description",
)
def _suggested_copies_marker():
    import voluptuous as vol

    from homeassistant.config_entries import ConfigFlow

    marker = vol.Optional("field")
    schema = vol.Schema({marker: str})
    out = ConfigFlow().add_suggested_values_to_schema(schema, {"field": 7})
    new_key = next(k for k in out.schema if str(k) == "field")
    assert new_key.description == {"suggested_value": 7}
    assert marker.description is None


# -- helpers.update_coordinator ----------------------------------------------

@contract(
    "homeassistant.helpers.update_coordinator.CoordinatorEntity",
    "available follows the coordinator's last_update_success",
    cite="helpers/update_coordinator.py -- `return self.coordinator.last_update_success`",
)
def _coordinator_entity_available():
    from homeassistant.helpers.update_coordinator import CoordinatorEntity

    class _C:
        last_update_success = True

    coordinator = _C()
    entity = CoordinatorEntity(coordinator)
    assert entity.available is True
    coordinator.last_update_success = False
    assert entity.available is False


# -- helpers.entity_registry -------------------------------------------------

@contract(
    "homeassistant.helpers.entity_registry.async_get",
    "the same registry object is returned for the same hass",
    cite="helpers/entity_registry.py -- the registry is stored on hass.data",
    expect="stub",
)
def _entity_registry_singleton():
    from homeassistant.helpers import entity_registry as er

    class _Hass:
        def __init__(self):
            self.data = {}

    hass = _Hass()
    assert er.async_get(hass) is er.async_get(hass)


# -- components.repairs ------------------------------------------------------

@contract(
    "homeassistant.components.repairs.ConfirmRepairFlow",
    "init shows a confirm form, and confirming creates the entry",
    cite="components/repairs -- ConfirmRepairFlow delegates init to async_step_confirm",
)
def _confirm_repair_flow():
    import asyncio

    from homeassistant.components.repairs import ConfirmRepairFlow

    flow = ConfirmRepairFlow()
    shown = asyncio.run(flow.async_step_init(None))
    assert shown["type"] == "form" and shown["step_id"] == "confirm"
    created = asyncio.run(flow.async_step_confirm({}))
    assert created["type"] == "create_entry"


# -- helpers.entity_registry.async_entries_for_config_entry ------------------

@contract(
    "homeassistant.helpers.entity_registry.async_entries_for_config_entry",
    "only the entries belonging to that config entry are returned",
    cite="helpers/entity_registry.py -- filters registry entries by config_entry_id",
    expect="stub",
)
def _entries_for_config_entry():
    from homeassistant.helpers import entity_registry as er

    registry = er.EntityRegistry()
    registry.add("sensor.mine", unique_id="a", config_entry_id="one")
    registry.add("sensor.theirs", unique_id="b", config_entry_id="two")
    got = [e.entity_id for e in er.async_entries_for_config_entry(registry, "one")]
    assert got == ["sensor.mine"]


# -- helpers.event -----------------------------------------------------------

@contract(
    "homeassistant.helpers.event.async_track_state_change_event",
    "the returned callable removes the subscription, and twice is harmless",
    cite="helpers/event.py -- the tracker returns a remove_listener callable",
    expect="stub",
)
def _state_change_unsub():
    from homeassistant.helpers.event import async_track_state_change_event

    class _Hass:
        pass

    hass = _Hass()
    unsub = async_track_state_change_event(hass, ["sensor.x"], lambda event: None)
    assert len(hass.state_listeners) == 1
    unsub()
    assert hass.state_listeners == []
    unsub()


# -- helpers.issue_registry --------------------------------------------------

@contract(
    "homeassistant.helpers.issue_registry.async_create_issue",
    "re-raising the same issue id replaces it rather than adding a second",
    cite="helpers/issue_registry.py -- async_create_issue updates an existing issue",
    expect="stub",
)
def _issue_replaces():
    from homeassistant.helpers.issue_registry import async_create_issue

    class _Hass:
        pass

    hass = _Hass()
    async_create_issue(hass, "d", "i", severity="warning")
    async_create_issue(hass, "d", "i", severity="error")
    assert len(hass.issues) == 1
    assert hass.issues[0][2]["severity"] == "error"


@contract(
    "homeassistant.helpers.issue_registry.async_delete_issue",
    "deletes by (domain, issue_id) and is a no-op when there is nothing to delete",
    cite="helpers/issue_registry.py -- async_delete_issue removes the issue if present",
    expect="stub",
)
def _issue_delete():
    from homeassistant.helpers.issue_registry import async_create_issue, async_delete_issue

    class _Hass:
        pass

    hass = _Hass()
    async_delete_issue(hass, "d", "absent")
    async_create_issue(hass, "d", "i")
    async_create_issue(hass, "d", "j")
    async_delete_issue(hass, "d", "i")
    assert [issue[1] for issue in hass.issues] == ["j"]


# -- util.dt -----------------------------------------------------------------

@contract(
    "homeassistant.util.dt.utcnow",
    "returns an aware datetime in UTC",
    cite="util/dt.py -- `return dt.datetime.now(dt.UTC)`",
)
def _dt_utcnow():
    from datetime import timezone

    from homeassistant.util.dt import utcnow

    got = utcnow()
    assert got.tzinfo is not None
    assert got.utcoffset() == timezone.utc.utcoffset(None)


@contract(
    "homeassistant.util.dt.now",
    "returns a datetime in the configured zone",
    cite="util/dt.py -- `return dt.datetime.now(time_zone or DEFAULT_TIME_ZONE)`",
)
def _dt_now():
    from homeassistant.util import dt as dt_util

    got = dt_util.now()
    if dt_util.DEFAULT_TIME_ZONE is not None:
        assert got.tzinfo is not None
        assert got.utcoffset() == dt_util.DEFAULT_TIME_ZONE.utcoffset(got.replace(tzinfo=None))


@contract(
    "homeassistant.util.dt.parse_datetime",
    "an unparseable string is None rather than an exception",
    cite="util/dt.py -- parse_datetime returns None on a value it cannot read",
)
def _dt_parse():
    from homeassistant.util.dt import parse_datetime

    assert parse_datetime("not a datetime") is None
    parsed = parse_datetime("2026-01-02T03:04:05+00:00")
    assert parsed is not None and parsed.year == 2026


@contract(
    "homeassistant.util.dt.DEFAULT_TIME_ZONE",
    "a zone is configured without anything being set in the environment",
    cite="util/dt.py -- `DEFAULT_TIME_ZONE: dt.tzinfo = dt.UTC` at module level",
    expect="real",
)
def _dt_default_zone():
    import os

    from homeassistant.util import dt as dt_util

    # The divergence is that the stub has NO zone by default. With HASTUB_TZ
    # set it has one, so the environment has to be part of the statement or
    # this contract would report the divergence repaired whenever
    # dst_checks.py's environment leaked into the run.
    assert os.environ.get("HASTUB_TZ") is None, "HASTUB_TZ is set: not the default case"
    assert dt_util.DEFAULT_TIME_ZONE is not None


@contract(
    "homeassistant.util.dt.as_local",
    "a naive datetime is converted rather than returned unchanged",
    cite="util/dt.py -- as_local attaches DEFAULT_TIME_ZONE and converts",
    expect="real",
)
def _dt_as_local():
    import os
    from datetime import datetime

    from homeassistant.util.dt import as_local

    assert os.environ.get("HASTUB_TZ") is None, "HASTUB_TZ is set: not the default case"
    assert as_local(datetime(2026, 1, 2, 3, 4)).tzinfo is not None


# -- core --------------------------------------------------------------------

@contract(
    "homeassistant.core.callback",
    "the decorated function is tagged so the event loop runs it inline",
    cite="core.py -- callback sets `_hass_callback` on the function and returns it",
    expect="real",
)
def _callback_tags():
    from homeassistant.core import callback

    def _fn() -> None:
        return None

    assert getattr(callback(_fn), "_hass_callback", False) is True


# ---------------------------------------------------------------------------
# probes
# ---------------------------------------------------------------------------
# A probe reads a value out of whichever provider is loaded. Neither run
# compares anything: --compare does that over the two reports, which is what
# lets a transcribed roster be MEASURED against upstream rather than
# remembered. `rel` says how the stub's value must relate to the real one.

PROBES: list = []


def probe(name: str, *, rel: str):
    """``rel`` is 'subset' (stub's members are upstream's) or 'equal'."""

    def register(fn):
        PROBES.append((name, rel, fn))
        return fn

    return register


def _members(cls) -> dict:
    return {
        k: v
        for k, v in vars(cls).items()
        if not k.startswith("_") and isinstance(v, (str, int)) and not callable(v)
    }


@probe("const.Platform", rel="subset")
def _p_platform():
    from homeassistant.const import Platform

    return {k: str(v) for k, v in _members(Platform).items()}


@probe("components.sensor.SensorDeviceClass", rel="subset")
def _p_sensor_device_class():
    from homeassistant.components.sensor import SensorDeviceClass

    return {k: str(v) for k, v in _members(SensorDeviceClass).items()}


@probe("components.sensor.SensorStateClass", rel="subset")
def _p_sensor_state_class():
    from homeassistant.components.sensor import SensorStateClass

    return {k: str(v) for k, v in _members(SensorStateClass).items()}


@probe("components.sensor.DEVICE_CLASS_STATE_CLASSES", rel="subset_of_keys_equal_values")
def _p_device_class_state_classes():
    from homeassistant.components.sensor import DEVICE_CLASS_STATE_CLASSES

    return {str(k): sorted(str(v) for v in vals) for k, vals in DEVICE_CLASS_STATE_CLASSES.items()}


@probe("components.binary_sensor.BinarySensorDeviceClass", rel="subset")
def _p_binary_sensor_device_class():
    from homeassistant.components.binary_sensor import BinarySensorDeviceClass

    return {k: str(v) for k, v in _members(BinarySensorDeviceClass).items()}


@probe("components.climate.HVACMode", rel="subset")
def _p_hvac_mode():
    from homeassistant.components.climate import HVACMode

    return {k: str(v) for k, v in _members(HVACMode).items()}


@probe("components.climate.HVACAction", rel="subset")
def _p_hvac_action():
    from homeassistant.components.climate import HVACAction

    return {k: str(v) for k, v in _members(HVACAction).items()}


@probe("components.climate.ClimateEntityFeature", rel="subset")
def _p_climate_features():
    from homeassistant.components.climate import ClimateEntityFeature

    return {k: int(v) for k, v in _members(ClimateEntityFeature).items()}


@probe("config_entries.ConfigEntryState", rel="subset")
def _p_config_entry_state():
    from homeassistant.config_entries import ConfigEntryState

    return {member.name: str(member.value) for member in ConfigEntryState}


@probe("config_entries.SOURCE_RECONFIGURE", rel="equal")
def _p_source_reconfigure():
    from homeassistant.config_entries import SOURCE_RECONFIGURE

    return str(SOURCE_RECONFIGURE)


@probe("components.diagnostics.REDACTED", rel="equal")
def _p_redacted():
    from homeassistant.components.diagnostics import REDACTED

    return str(REDACTED)


@probe("helpers.entity.EntityCategory", rel="subset")
def _p_entity_category():
    from homeassistant.helpers.entity import EntityCategory

    return {k: str(v) for k, v in _members(EntityCategory).items()}


@probe("helpers.device_registry.DeviceEntryType", rel="subset")
def _p_device_entry_type():
    from homeassistant.helpers.device_registry import DeviceEntryType

    return {k: str(v) for k, v in _members(DeviceEntryType).items()}


@probe("helpers.issue_registry.IssueSeverity", rel="subset")
def _p_issue_severity():
    from homeassistant.helpers.issue_registry import IssueSeverity

    return {k: str(v) for k, v in _members(IssueSeverity).items()}


@probe("helpers.selector.NumberSelectorMode", rel="subset")
def _p_number_mode():
    from homeassistant.helpers.selector import NumberSelectorMode

    return {k: str(v) for k, v in _members(NumberSelectorMode).items()}


@probe("helpers.selector.SelectSelectorMode", rel="subset")
def _p_select_mode():
    from homeassistant.helpers.selector import SelectSelectorMode

    return {k: str(v) for k, v in _members(SelectSelectorMode).items()}


@probe("helpers.selector.TextSelectorType", rel="subset")
def _p_text_type():
    from homeassistant.helpers.selector import TextSelectorType

    return {k: str(v) for k, v in _members(TextSelectorType).items()}


@probe("core.SupportsResponse", rel="subset")
def _p_supports_response():
    from homeassistant.core import SupportsResponse

    return {k: str(v) for k, v in _members(SupportsResponse).items()}


@probe("const.units", rel="subset")
def _p_units():
    from homeassistant import const

    out = {}
    for group in (
        "UnitOfSpeed",
        "UnitOfPower",
        "UnitOfEnergy",
        "UnitOfTemperature",
        "UnitOfVolume",
    ):
        for name, value in _members(getattr(const, group)).items():
            out[f"{group}.{name}"] = str(value)
    out["PERCENTAGE"] = str(const.PERCENTAGE)
    out["ATTR_TEMPERATURE"] = str(const.ATTR_TEMPERATURE)
    out["CONF_NAME"] = str(const.CONF_NAME)
    return out


# ---------------------------------------------------------------------------
# provider
# ---------------------------------------------------------------------------


def provider_name() -> str:
    """Which Home Assistant is on the path.

    Read from the package rather than from a flag: a run that BELIEVED it had
    the real thing and did not would be the same defect one level up.
    ``homeassistant.const.__version__`` exists only in the real distribution --
    the stub's const carries the members the integration imports and nothing
    else, and the completeness check below refuses a stub that grows one.
    """
    from homeassistant import const

    return "real" if hasattr(const, "__version__") else "stub"


def _run_contracts(report: Report, provider: str) -> None:
    report.section(f"contracts against the {provider} provider")
    for symbol, name, _cite, expect, fn in CONTRACTS:
        label = f"{symbol.split('homeassistant.')[-1]}: {name}"
        try:
            fn()
            passed, detail = True, ""
        except Exception as err:  # noqa: BLE001 - any failure is a failure
            passed, detail = False, f"{type(err).__name__}: {err}"
        if expect == "stub":
            # Pins the stub's own behaviour where upstream's equivalent needs a
            # running hass. Nothing to say against the real provider, and
            # saying it anyway would be a check that cannot fail.
            if provider == "stub":
                report.check(f"{label}  (stub-only)", passed, detail)
            else:
                report.note(f"{label} -- not runnable against real Home Assistant")
        elif expect == "both":
            report.check(label, passed, detail)
        elif provider == "real":
            report.check(label, passed, detail + "  (expect=real)")
        else:
            # An expect="real" contract states upstream behaviour the stub is
            # recorded as NOT having. It passing here means the stub was
            # repaired and its DIVERGENT entry is now false, so this is the
            # direction that fires when somebody fixes the stub quietly.
            report.check(
                f"{label} -- still divergent under the stub",
                not passed,
                "the stub now satisfies this: promote its inventory entry to "
                "FAITHFUL and change expect to 'both'",
            )


def _run_probes(provider: str) -> dict:
    values = {}
    for name, rel, fn in PROBES:
        try:
            values[name] = {"rel": rel, "value": fn()}
        except Exception as err:  # noqa: BLE001
            values[name] = {"rel": rel, "error": f"{type(err).__name__}: {err}"}
    return {"provider": provider, "upstream": UPSTREAM, "probes": values}


# ---------------------------------------------------------------------------
# completeness: the part that is not one more repaired symbol
# ---------------------------------------------------------------------------


def stub_root() -> Path:
    """Where the stub package that got imported actually lives.

    Located through the imported package rather than from this file's position
    in the tree, because the real-Home-Assistant lane mounts the two somewhere
    else entirely -- ``/opt/hpo/ha_contract.py`` beside ``/opt/hpo/hastub``.
    A path guessed from ``__file__`` resolves to nothing there, and an empty
    walk would report all 90 inventory entries as stale.
    """
    import homeassistant

    return Path(homeassistant.__path__[0])


def stub_symbols() -> dict[str, set[str]]:
    """Module-level public names the stub declares, by module, read by AST.

    Parsed rather than imported so the answer does not depend on import-time
    side effects, and so a module that fails to import is still inventoried
    rather than silently dropping out of the completeness check.
    """
    root = stub_root()
    found: dict[str, set[str]] = {}
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root.parent).with_suffix("")
        parts = list(rel.parts)
        if parts[-1] == "__init__":
            parts.pop()
        module = ".".join(parts)
        names: set[str] = set()
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                names.update(
                    t.id for t in node.targets if isinstance(t, ast.Name)
                )
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names.add(node.target.id)
        names = {n for n in names if not n.startswith("_")}
        if names:
            found[module] = names
    return found


def _check_inventory(report: Report) -> None:
    report.section("inventory completeness")
    declared = stub_symbols()
    live = {f"{module}.{name}" for module, names in declared.items() for name in names}

    undispositioned = sorted(live - set(INVENTORY))
    report.check(
        "every public stub symbol has a disposition",
        not undispositioned,
        f"no inventory entry: {undispositioned}",
    )
    stale = sorted(set(INVENTORY) - live)
    report.check(
        "every inventory entry still names a live stub symbol",
        not stale,
        f"gone from the stub: {stale}",
    )
    bad = sorted(k for k, e in INVENTORY.items() if e.disposition not in DISPOSITIONS)
    report.check("every disposition is a declared one", not bad, f"{bad}")

    contracted = {symbol for symbol, _n, _c, expect, _f in CONTRACTS if expect == "both"}
    uncontracted = sorted(
        k for k, e in INVENTORY.items() if e.disposition == FAITHFUL and k not in contracted
    )
    report.check(
        "every FAITHFUL symbol carries at least one contract",
        not uncontracted,
        f"claimed faithful with nothing checking it: {uncontracted}",
    )

    stub_only = {symbol for symbol, _n, _c, expect, _f in CONTRACTS if expect == "stub"}
    unpinned = sorted(
        k for k, e in INVENTORY.items() if e.disposition == UNVERIFIED and k not in stub_only
    )
    report.check(
        "every UNVERIFIED symbol is at least pinned against the stub",
        not unpinned,
        f"behaviour claimed with nothing pinning it: {unpinned}",
    )

    real_only = {symbol for symbol, _n, _c, expect, _f in CONTRACTS if expect == "real"}
    unproved = sorted(
        k for k, e in INVENTORY.items() if e.disposition == DIVERGENT and k not in real_only
    )
    report.check(
        "every DIVERGENT symbol carries a contract stating upstream's behaviour",
        not unproved,
        f"divergence claimed with nothing measuring it: {unproved}",
    )
    unissued = sorted(k for k, e in INVENTORY.items() if e.disposition == DIVERGENT and not e.issue)
    report.check("every DIVERGENT symbol names the issue tracking it", not unissued, f"{unissued}")


def _check_declared_absences(report: Report) -> None:
    report.section("declared simplifications are still simplifications")
    import importlib

    appeared = []
    for key, entry in INVENTORY.items():
        if not entry.absent:
            continue
        module_path, _, name = key.rpartition(".")
        obj = getattr(importlib.import_module(module_path), name)
        for member in entry.absent:
            if hasattr(obj, member):
                appeared.append(f"{key}.{member}")
    report.check(
        "no member declared absent has appeared",
        not appeared,
        f"{appeared}: the stub gained behaviour its inventory entry denies. "
        "Promote the entry and give it a contract",
    )


def _print_inventory() -> None:
    counts = {d: 0 for d in DISPOSITIONS}
    for entry in INVENTORY.values():
        counts[entry.disposition] += 1
    print("\n-- inventory")
    print(
        f"  {len(INVENTORY)} symbols: "
        + ", ".join(f"{counts[d]} {d}" for d in DISPOSITIONS)
        + f"; {len(UNMODELLED)} unmodelled upstream areas"
    )
    for disposition in DISPOSITIONS:
        for key, entry in sorted(INVENTORY.items()):
            if entry.disposition == disposition:
                tag = f" ({entry.issue})" if entry.issue else ""
                print(f"       {disposition:<10} {key}{tag}")


# ---------------------------------------------------------------------------
# --compare: the two reports, held against each other
# ---------------------------------------------------------------------------


def _compare(report: Report, stub: dict, real: dict) -> None:
    report.section("probes: the stub's values against real Home Assistant's")
    if stub.get("provider") != "stub" or real.get("provider") != "real":
        report.check(
            "the two reports are one stub run and one real run",
            False,
            f"got {stub.get('provider')} and {real.get('provider')}",
        )
        return
    report.check("the two reports are one stub run and one real run", True)

    for name, entry in sorted(stub["probes"].items()):
        counterpart = real["probes"].get(name)
        if counterpart is None:
            report.check(f"{name} exists upstream", False, "the real run has no such probe")
            continue
        if "error" in counterpart:
            report.check(f"{name} reads upstream", False, counterpart["error"])
            continue
        if "error" in entry:
            report.check(f"{name} reads the stub", False, entry["error"])
            continue
        mine, theirs, rel = entry["value"], counterpart["value"], entry["rel"]
        if rel == "equal":
            report.check(f"{name} equals upstream's", mine == theirs, f"{mine!r} != {theirs!r}")
        elif rel == "subset":
            invented = sorted(k for k, v in mine.items() if theirs.get(k) != v)
            report.check(
                f"every member of {name} exists upstream with the same value",
                not invented,
                f"invented or wrong: {[(k, mine[k], theirs.get(k)) for k in invented]}",
            )
        elif rel == "subset_of_keys_equal_values":
            wrong = sorted(k for k, v in mine.items() if k not in theirs or theirs[k] != v)
            report.check(
                f"every entry of {name} matches upstream's",
                not wrong,
                f"{[(k, mine[k], theirs.get(k)) for k in wrong]}",
            )


def _report_unmodelled(real: dict) -> None:
    """Printed, never failed -- and the docstring says why.

    Parity with upstream is not the goal and demanding it would make this a
    check that is always red. What it is for is the #516/#568 class: a
    capability nobody knew existed, because nothing imports what is not there.
    """
    print("\n-- upstream names the stub does not model (informational)")
    for area, why in sorted(UNMODELLED.items()):
        print(f"       {area}: {why.splitlines()[0]}")
    print(f"       real provider reported {len(real.get('probes', {}))} probes")


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="tests/hastub fidelity contracts (#536)")
    parser.add_argument("--emit-probes", metavar="PATH", help="write this provider's probe values")
    parser.add_argument("--compare", nargs=2, metavar=("STUB", "REAL"), help="two probe files")
    parser.add_argument(
        "--contracts-only",
        action="store_true",
        help="skip the inventory checks (the container has no tests/hastub tree)",
    )
    args = parser.parse_args(argv)

    if args.compare:
        report = Report("tests/hastub against real Home Assistant")
        stub = json.loads(Path(args.compare[0]).read_text())
        real = json.loads(Path(args.compare[1]).read_text())
        _compare(report, stub, real)
        _report_unmodelled(real)
        return report.close("probe comparisons")

    provider = provider_name()
    report = Report(f"tests/hastub contracts (provider: {provider}, upstream {UPSTREAM})")
    _run_contracts(report, provider)
    # The inventory describes the STUB, so it is measured only where the stub is
    # what got imported. Asserting a declared absence against real Home
    # Assistant would fail on every entry and mean nothing.
    if not args.contracts_only and provider == "stub":
        _check_inventory(report)
        _check_declared_absences(report)
        _print_inventory()
    elif not args.contracts_only:
        report.check(
            "the inventory is measured against the stub",
            False,
            "this run imported real Home Assistant; pass --contracts-only",
        )
    if args.emit_probes:
        Path(args.emit_probes).write_text(json.dumps(_run_probes(provider), indent=1))
        print(f"\nprobes written to {args.emit_probes}")
    return report.close("contracts")


if __name__ == "__main__":
    sys.exit(main())
