"""One finite-float coercion for the whole package (D7-s2-58, #2239).

A pure module, below every layer: a model, a learner, the config parse and
the Home Assistant glue all read a stored, configured or reported value
through :func:`finite_float`, so none of them climbs to ``inputs.py`` (whose
reader runs on Home Assistant's clock) just to ask whether a value is a
number. Nine coercers each answered that with their own bool, text, NaN and
overflow policy before it; ``tests/finite_boundary.py``'s census holds the
count at the owner.
"""
from __future__ import annotations

import math
from numbers import Real
from typing import Any, overload


@overload
def finite_float(value: Any) -> float | None: ...
@overload
def finite_float(value: Any, default: float) -> float: ...
@overload
def finite_float(value: Any, default: float | None) -> float | None: ...
def finite_float(value: Any, default: float | None = None) -> float | None:
    """``value`` as a finite float; anything else is ``default``.

    The one coercion every reader shares (D7-s2-58): ``None``, text that is
    not a number, NaN, an infinity and an int past a double (an attribute-
    or service-fed value orjson never parsed) are all unreadable, never a
    raise and never a non-finite number handed on to the solver. Only a real
    number or text is read: a ``bool`` is not a number here, although
    ``float()`` takes it -- ``True`` read as 1.0 kW, 1.0 degC or a 1 degC
    away target is a guess, not a reading -- and neither are bytes.
    """
    if isinstance(value, bool) or not isinstance(value, (Real, str)):
        return default
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return result if math.isfinite(result) else default
