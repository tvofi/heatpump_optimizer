"""Minimal stand-in for ``homeassistant.config_entries``.

Mirrored from Home Assistant 2024.6.0 -- the floor ``hacs.json`` declares,
and the release that introduced ``ConfigEntry.runtime_data`` -- and kept to
the semantics the integration and its tests lean on:

* ``ConfigEntry`` is generic in its runtime data (``ConfigEntry[MyClient]``
  subscripts, so the integration's typed alias imports). ``runtime_data`` is
  an attribute the integration ASSIGNS in ``async_setup_entry``: absent until
  then, and the entry manager deletes it again after a successful unload.
  Nothing here pre-fills it -- a stub that did would let a platform read a
  coordinator nobody stored.
* ``state`` starts ``NOT_LOADED``. The real manager moves it around setup and
  unload; ``tests/harness.py``'s ``ha_setup_entry``/``ha_unload_entry`` do
  the same for a test that drives the integration's entry points directly.
* ``async_set_unique_id`` and ``_abort_if_unique_id_configured`` look the
  unique id up through ``hass.config_entries.async_entry_for_domain_unique_id``
  and raise ``data_entry_flow.AbortFlow("already_configured")`` on a hit,
  exactly as the real flow does (the flow manager is what turns that
  exception into an abort result, and there is no manager here, so a test
  catches the exception). ``raise_on_progress`` -- the real method's abort
  on a *second in-flight flow* with the same id -- has no in-progress list
  to consult and is accepted and ignored.
* The reconfigure entry point (2024.4+, the #196 mirror) has no flow manager
  either, so what is mirrored is the two halves a test can drive directly:
  the handler registry the real ``ConfigFlow.__init_subclass__`` populates
  (``HANDLERS.register(domain)(cls)``) feeding ``ConfigEntry.supports_reconfigure``
  -- in the real class a memoised ``hasattr(handler, "async_step_reconfigure")``
  and the exact test for whether the UI offers "Reconfigure" on an entry --
  and ``FlowHandler.add_suggested_values_to_schema``, copied from the 2024.6.0
  ``data_entry_flow.FlowHandler`` verbatim (minus typing) because it is how a
  reconfigure step shows the entry's current values without defaulting them.
  ``context`` defaults to an immutable empty mapping and ``source`` /
  ``show_advanced_options`` read it, as the real ``FlowHandler`` attributes do;
  a test that wants the manager's stamp assigns ``flow.context = {...}``.
"""
from __future__ import annotations

import copy
from enum import Enum
from types import MappingProxyType
from typing import Any, Generic, TypeVar

import voluptuous as vol

_DataT = TypeVar("_DataT")

# Mirrors homeassistant.config_entries.SOURCE_RECONFIGURE (2024.4+): the
# flow source the real manager stamps on a reconfigure flow's context.
SOURCE_RECONFIGURE = "reconfigure"

# Mirrors homeassistant.config_entries.HANDLERS: domain -> flow class, what
# HANDLERS.register(domain)(cls) populates from ConfigFlow.__init_subclass__.
HANDLERS: dict[str, type] = {}


class ConfigEntryState(Enum):
    """The real enum's members; ``recoverable`` is not modelled."""

    LOADED = "loaded"
    SETUP_ERROR = "setup_error"
    MIGRATION_ERROR = "migration_error"
    SETUP_RETRY = "setup_retry"
    NOT_LOADED = "not_loaded"
    FAILED_UNLOAD = "failed_unload"
    SETUP_IN_PROGRESS = "setup_in_progress"


class ConfigEntry(Generic[_DataT]):
    # Annotation only, as in Home Assistant: the attribute exists once the
    # integration assigns it and ``hasattr`` is False before that.
    runtime_data: _DataT

    def __init__(
        self,
        data=None,
        options=None,
        entry_id="test",
        *,
        domain: str | None = None,
        unique_id: str | None = None,
        title: str = "",
    ) -> None:
        self.data = data or {}
        self.options = options or {}
        self.entry_id = entry_id
        self.version = 1
        self.domain = domain
        self.unique_id = unique_id
        self.title = title
        self.state = ConfigEntryState.NOT_LOADED

    @property
    def supports_reconfigure(self) -> bool:
        """Whether this entry's handler carries a reconfigure step.

        The real property (2024.6.0, homeassistant/config_entries.py) memoises
        ``hasattr(handler, "async_step_reconfigure")`` per entry and is what
        decides whether the UI offers "Reconfigure"; a handler with no such
        step never shows one. No memo here: the registry is a plain dict and
        a test that swaps the step sees the swap.
        """
        handler = HANDLERS.get(self.domain)
        return handler is not None and hasattr(handler, "async_step_reconfigure")


class ConfigFlow:
    """Accepts the ``domain=`` keyword the real class uses for registration."""

    # The real FlowHandler's class attributes, as of 2024.6.0: the manager
    # stamps per-instance values over these.
    context: dict[str, Any] = MappingProxyType({})

    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.domain = domain
        if domain is not None:
            HANDLERS[domain] = cls

    @property
    def handler(self) -> str | None:
        """The domain the flow is registered under (the manager stamps it)."""
        return getattr(self, "domain", None)

    @property
    def source(self) -> str | None:
        """Source that initialized the flow (the real FlowHandler property)."""
        return self.context.get("source", None)

    @property
    def show_advanced_options(self) -> bool:
        """If we should show advanced options (the real FlowHandler property)."""
        return bool(self.context.get("show_advanced_options", False))

    @property
    def unique_id(self) -> str | None:
        """What ``async_set_unique_id`` recorded, or None."""
        return getattr(self, "_stub_unique_id", None)

    def add_suggested_values_to_schema(
        self, data_schema: vol.Schema, suggested_values: dict[str, Any] | None
    ) -> vol.Schema:
        """Make a copy of the schema, populated with suggested values.

        Copied from 2024.6.0's data_entry_flow.FlowHandler (minus typing):
        for each schema marker matching items in ``suggested_values``, the
        ``suggested_value`` is set. The existing ``suggested_value`` will be
        left untouched if there is no matching item.
        """
        schema = {}
        for key, val in data_schema.schema.items():
            if isinstance(key, vol.Marker):
                # Exclude advanced field
                if (
                    key.description
                    and key.description.get("advanced")
                    and not self.show_advanced_options
                ):
                    continue

            new_key = key
            if (
                suggested_values
                and key in suggested_values
                and isinstance(key, vol.Marker)
            ):
                # Copy the marker to not modify the flow schema
                new_key = copy.copy(key)
                new_key.description = {"suggested_value": suggested_values[key]}
            schema[new_key] = val
        return vol.Schema(schema)

    async def async_set_unique_id(
        self, unique_id: str | None = None, *, raise_on_progress: bool = True
    ):
        """Record the unique id; return the entry already holding it, if any."""
        self._stub_unique_id = unique_id
        if unique_id is None:
            return None
        return self.hass.config_entries.async_entry_for_domain_unique_id(
            self.handler, unique_id
        )

    def _abort_if_unique_id_configured(
        self,
        updates: dict[str, Any] | None = None,
        reload_on_update: bool = True,
        *,
        error: str = "already_configured",
    ) -> None:
        """Abort when an entry already carries this flow's unique id."""
        # Imported here, not at module level: every test script imports this
        # module, and only the ones that reach the guard should see
        # ``data_entry_flow`` in their recorded closure (tests/closures.json
        # is measured, and the post-merge check fails on a file a run touched
        # that the record does not list).
        from . import data_entry_flow

        if self.unique_id is None:
            return
        entry = self.hass.config_entries.async_entry_for_domain_unique_id(
            self.handler, self.unique_id
        )
        if entry is None:
            return
        if updates is not None:
            self.hass.config_entries.async_update_entry(
                entry, data={**entry.data, **updates}
            )
        raise data_entry_flow.AbortFlow(error)

    def async_show_form(self, **kwargs):
        # The real flow manager records the step it showed on the handler as
        # ``cur_step``; the options flow's menu-return path (#100) reads it
        # to know which section's menu to come back to. Without this, every
        # save looks like it came from the top menu.
        self.cur_step = {"step_id": kwargs.get("step_id")}
        return {"type": "form", **kwargs}

    def async_show_menu(self, **kwargs):
        self.cur_step = {"step_id": kwargs.get("step_id")}
        return {"type": "menu", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}

    def async_abort(self, **kwargs):
        return {"type": "abort", **kwargs}


class OptionsFlow(ConfigFlow):
    pass
