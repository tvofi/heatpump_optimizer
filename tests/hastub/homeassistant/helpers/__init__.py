"""Stub ``homeassistant.helpers`` package.

``json_bytes`` is upstream's ``homeassistant.helpers.json.json_bytes``. The
module is injected so ``from homeassistant.helpers.json import json_bytes``
resolves here without a second tracked file.
"""
from __future__ import annotations

import json
import math
import sys
import types


def json_bytes(obj: object) -> bytes:
    """orjson's refusals: non-finite floats, set, bytes.

    Upstream is ``orjson.dumps``. The default-encoder path for Home Assistant
    types is not modelled.
    """
    try:
        import orjson

        return orjson.dumps(obj)
    except ImportError:
        pass

    def walk(node: object) -> None:
        if isinstance(node, float) and not math.isfinite(node):
            raise ValueError("orjson rejects non-finite floats")
        if isinstance(node, (set, bytes, bytearray)):
            raise TypeError(f"orjson rejects {type(node).__name__}")
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, (list, tuple)):
            for value in node:
                walk(value)

    walk(obj)
    return json.dumps(obj).encode()


_json_mod = types.ModuleType("homeassistant.helpers.json")
_json_mod.json_bytes = json_bytes
sys.modules["homeassistant.helpers.json"] = _json_mod
