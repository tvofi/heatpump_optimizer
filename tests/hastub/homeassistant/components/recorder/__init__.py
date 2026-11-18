"""Stand-in for ``homeassistant.components.recorder``: the instance and its executor.

Upstream's ``get_instance`` is ``hass.data[DATA_INSTANCE]`` (``recorder/util.py``),
a ``KeyError`` when the recorder is not set up, and ``Recorder.async_add_executor_job``
runs the job in the recorder's own database executor; here it runs inline.
Tests install one with ``install(hass)``, which also marks the component loaded
in ``hass.config.components`` as the recorder's setup does.
"""
from __future__ import annotations

from typing import Any

DATA_INSTANCE = "recorder_instance"


class Recorder:
    #: The schema the stub stands for: upstream's ``SCHEMA_VERSION`` at 2025.2.0.
    schema_version = 47

    def __init__(self, hass: Any) -> None:
        self.hass = hass

    async def async_add_executor_job(self, target, *args):
        return target(*args)


def get_instance(hass: Any) -> Recorder:
    return hass.data[DATA_INSTANCE]


def install(hass: Any) -> Recorder:
    """A test-facing setup: the instance on ``hass.data``, the component loaded."""
    instance = hass.data[DATA_INSTANCE] = Recorder(hass)
    hass.config.components.add("recorder")
    return instance
