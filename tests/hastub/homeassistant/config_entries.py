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
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Generic, TypeVar

_DataT = TypeVar("_DataT")


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


class ConfigFlow:
    """Accepts the ``domain=`` keyword the real class uses for registration."""

    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.domain = domain

    @property
    def handler(self) -> str | None:
        """The domain the flow is registered under (the manager stamps it)."""
        return getattr(self, "domain", None)

    @property
    def unique_id(self) -> str | None:
        """What ``async_set_unique_id`` recorded, or None."""
        return getattr(self, "_stub_unique_id", None)

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
