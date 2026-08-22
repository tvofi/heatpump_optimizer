"""Minimal stand-in for ``homeassistant.config_entries``."""


class ConfigEntry:
    def __init__(self, data=None, options=None, entry_id="test"):
        self.data = data or {}
        self.options = options or {}
        self.entry_id = entry_id
        self.version = 1


class ConfigFlow:
    """Accepts the ``domain=`` keyword the real class uses for registration."""

    def __init_subclass__(cls, domain=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.domain = domain

    def async_show_form(self, **kwargs):
        return {"type": "form", **kwargs}

    def async_show_menu(self, **kwargs):
        return {"type": "menu", **kwargs}

    def async_create_entry(self, **kwargs):
        return {"type": "create_entry", **kwargs}

    def async_abort(self, **kwargs):
        return {"type": "abort", **kwargs}


class OptionsFlow(ConfigFlow):
    pass
