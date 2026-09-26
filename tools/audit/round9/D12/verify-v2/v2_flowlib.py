"""Shared helpers for the D12 verify-v2 flow harnesses (no RESULT of its own).

post_untouched(form): what the Home Assistant frontend submits for a form the
user does not touch: every field that renders a value (a default or a
suggested_value) posted back, NESTED under its section key the way the
frontend posts a section() block (the flows flatten it with
_flatten_section_input). Fields with neither are omitted, as the frontend
omits an empty optional field.
"""
import sys

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from homeassistant.data_entry_flow import section  # noqa: E402


def _value_of(marker):
    d = getattr(marker, "default", None)
    if callable(d):
        try:
            return True, d()
        except Exception:  # noqa: BLE001
            return False, None
    sv = (getattr(marker, "description", None) or {}).get("suggested_value")
    if sv is not None:
        return True, sv
    return False, None


def post_untouched(form):
    schema = form.get("data_schema")
    out = {}
    if schema is None:
        return out
    for marker, value in schema.schema.items():
        key = str(getattr(marker, "schema", marker))
        if isinstance(value, section):
            inner = {}
            for m2 in value.schema.schema:
                ok, v = _value_of(m2)
                if ok:
                    inner[str(getattr(m2, "schema", m2))] = v
            out[key] = inner
            continue
        ok, v = _value_of(marker)
        if ok:
            out[key] = v
    return out
