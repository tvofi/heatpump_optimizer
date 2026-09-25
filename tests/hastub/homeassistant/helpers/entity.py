"""Minimal stand-in for ``homeassistant.helpers.entity``."""


class DeviceInfo(dict):
    pass


class EntityCategory(str):
    DIAGNOSTIC = "diagnostic"
    CONFIG = "config"


class Entity:
    """The root of every platform base, carrying the one member that is
    modelled here.

    ``entity_category`` used to be missing from the whole stub, so
    ``getattr(ent, "entity_category")`` was ``None`` for every entity in the
    tree regardless of what it declared -- the vacuity #947 records: a
    check keyed on the public property counts zero for a reason that has
    nothing to do with the code under test, and real Home Assistant, which
    declares the property, would have returned the value.
    """

    @property
    def entity_category(self) -> EntityCategory | None:
        """``helpers/entity.py`` Entity.entity_category.

        Upstream's cached_property returns ``_attr_entity_category`` when the
        attribute exists, then consults ``entity_description``, then
        ``None``. This copy drops the ``entity_description`` branch (the stub
        does not model descriptions) and uses a plain property: the values
        are class-level constants here, and a cached one would hide an
        in-place swap from the instrument harnesses that perform them.
        """
        if hasattr(self, "_attr_entity_category"):
            return self._attr_entity_category
        return None

    def async_write_ha_state(self) -> None:
        """Upstream writes the entity's state to the state machine; the stub
        records each write with the ``is_on`` it would publish, where the
        entity has one, so a test can read what the user would see."""
        writes = self.__dict__.setdefault("ha_state_writes", [])
        writes.append(getattr(self, "is_on", None))
