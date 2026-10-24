"""Stub ``homeassistant.helpers`` package.

``json_bytes`` is injected as ``homeassistant.helpers.json.json_bytes`` so
the import path matches Home Assistant without a second tracked file or a
public stub symbol for ha_contract's AST inventory.
"""
from __future__ import annotations

import json
import math
import sys
import types


def _json_bytes(obj: object) -> bytes:
    """Refuse non-finite floats, set and bytes, then serialize.

    The refusals run before the ``orjson.dumps`` fast path because orjson
    serialises non-finite floats as ``null`` rather than refusing them, so a
    stub that delegated first would let ``inf``/``nan`` through. The
    default-encoder path for Home Assistant types is not modelled.
    """

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

    try:
        import orjson

        return orjson.dumps(obj)
    except ImportError:
        pass

    return json.dumps(obj).encode()


_json_mod = types.ModuleType("homeassistant.helpers.json")
_json_mod.json_bytes = _json_bytes
sys.modules["homeassistant.helpers.json"] = _json_mod
