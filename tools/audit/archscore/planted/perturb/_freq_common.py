"""Shared by G3 and B7: the five coordinator methods of the frequency cluster (#61)."""
import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, COORD_CLASS, read, write, replace_once, remove_method, seam_drop

FREQ_METHODS = ("_freq_entity_reading", "_freq_mode", "_observe_frequency",
                "_command_frequency", "_freq_view")

HEADER_IMPORTS = '''from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

import numpy as np
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from .const import (
    CONF_COMPRESSOR_FREQ_ENTITY,
    CONF_COMPRESSOR_FREQ_MAX_HZ,
    CONF_COMPRESSOR_FREQ_MIN_HZ,
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_FREQ_CONTROL_MODE,
    CONF_POWER_ENTITY,
    DEFAULT_COMPRESSOR_FREQ_MAX_HZ,
    DEFAULT_COMPRESSOR_FREQ_MIN_HZ,
    DEFAULT_FREQ_CONTROL_MODE,
    DOMAIN,
    MODE_OFF,
)
from .freq_control import (
    FREQ_MODE_CONTROL,
    FREQ_MODE_OBSERVE,
    FREQ_SOURCE_NUMBER,
    FREQ_WRITE_EPSILON_HZ,
    FREQ_WRITE_MIN_INTERVAL_S,
    FrequencyMap,
    FrequencyWatchdog,
    resolve_reading,
)
from . import pump_signals
from .setpoint_check import create_issue as _create_issue

_LOGGER = logging.getLogger(__name__)


def _finite(value: Any, default: float) -> float:
    """A finite float or ``default`` (the coordinator's ``_as_float`` rule)."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) else default
'''


def strip_cluster(src: str) -> str:
    for name in FREQ_METHODS:
        src = remove_method(src, COORD_CLASS, name)
    return src


def drop_seams() -> None:
    seam_drop(*FREQ_METHODS)


def drop_orphaned_const_imports(src: str) -> str:
    """The six .const names only the cluster read (ruff F401 otherwise)."""
    for name in ("CONF_COMPRESSOR_FREQ_ENTITY", "CONF_COMPRESSOR_FREQ_MAX_HZ",
                 "CONF_COMPRESSOR_FREQ_MIN_HZ", "CONF_COMPRESSOR_FREQ_SENSOR",
                 "DEFAULT_COMPRESSOR_FREQ_MAX_HZ", "DEFAULT_COMPRESSOR_FREQ_MIN_HZ"):
        src = replace_once(src, f"    {name},\n", "")
    return src
