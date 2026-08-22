"""Minimal stand-in for the button platform's entity API."""


class ButtonEntity:
    _attr_has_entity_name = False
    _attr_name = None
    _attr_unique_id = None

    async def async_press(self) -> None:
        raise NotImplementedError
