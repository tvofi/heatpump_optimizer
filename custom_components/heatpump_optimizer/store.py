"""The store-load boundary: a ``Store`` whose loads cannot hand back a non-finite number.

Learned/live state is reconstituted by ~11 independent ``Store`` reads feeding
~18 hand-written loader seams, each over a ``float()`` coercion guarded by
``(TypeError, ValueError, OverflowError)``. That guard is blind to non-finite by
construction of the Python float type: ``float('nan')`` raises nothing, and
``np.clip`` propagates NaN onto the live model while *clamping* +-inf rather
than refusing it. So finiteness was enforced **per demonstrated field** — a
guard sat on the seam a harness happened to show, while its sibling in the same
store dict stayed open. The fifth seam of #1296/#1345 (``apply_cooling_rate``,
70 lines below the guarded ``normalize_profile`` in the same file) and its
sibling (``DefrostDerate.from_dict``'s ``duty`` grid) are the round-6 instances.

This module closes the class by construction instead of one more guard: every
store is a ``QuarantiningStore``, whose ``async_load`` scrubs poisoned numeric
leaves (non-finite, or of a magnitude no writer produces) to ``None`` — the
loaders' own absent-data default — so a poisoned leaf is quarantined at the
one persistence boundary and no per-seam guard can be forgotten, because no
seam decides finiteness or magnitude any more.

The rule that a store must be this type is enforced, not remembered: the
standing sweep ``tests/finite_boundary.py`` derives the boundary set from the
tree (every ``QuarantiningStore(...)`` construction, and zero raw ``Store(...)``
constructions outside it) and drives a non-finite leaf through each boundary.
"""
from __future__ import annotations

import asyncio
import logging
import math
from collections.abc import Mapping, Sequence
from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Any, NamedTuple, TypeVar, cast

from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from . import const as c
from .accuracy import HISTORY_LENGTH, LEAD_BUCKETS
from .comfort_learning import COMFORT_WEIGHT_MAX, COMFORT_WEIGHT_MIN
from .curve_learning import BIAS_MAX, BIAS_MIN
from .defrost import DERATE_MAX, DERATE_MIN, STORE_VERSION
from .drift import STAT_CAP_FACTOR
from .flow_lift import FLOW_BIAS_CLAMP_K, FLOW_SUPPLY_MAX_C
from .freq_control import FREQ_DECILES, FREQ_MAX_KW_PER_HZ
from .price_model import (
    QUARTER_FACTOR_MAX, QUARTER_FACTOR_MIN, RESIDUAL_VAR_MAX, SHAPE_MAX, SHAPE_MIN,
)
from .setpoint_check import create_issue

_LOGGER = logging.getLogger(__name__)

#: Home Assistant's ``Store`` bounds its payload to a JSON-shaped container
#: (a mapping or a sequence). The boundary never widens that; it scrubs leaves.
_StorePayload = TypeVar("_StorePayload", bound=Mapping[str, Any] | Sequence[Any])

#: Home Assistant's refusal of a downgrade, raised before the migration hook,
#: exists from 2026.3 only; the 2025.2.0 floor has no such class and hands a
#: newer document to the hook instead, which surfaces it there. Imported only
#: where it exists: an unguarded import fails every store, and the
#: integration, on the floor (#1869). Empty, ``except`` catches nothing.
_DOWNGRADE: tuple[type[Exception], ...] = ()
try:
    from homeassistant.helpers.storage import UnsupportedStorageVersionError
except ImportError:  # the 2025.2.0 floor
    pass
else:
    _DOWNGRADE = (UnsupportedStorageVersionError,)

#: Store keys whose last load found a newer release's document. Keyed, not
#: per instance: a writer may build a fresh store to save (away's does), and
#: no store of the key may save over it (#1869).
_NEWER_ON_DISK: set[str] = set()


#: No writer stores a number this large (an epoch in ms is 1.8e12), so one that
#: is -- ``2**64``, ``1e300``, a key of that size -- is a corrupt leaf, and is
#: quarantined here exactly as a non-finite one is (round-9 class P1).
ABSURD = 1e15


def _poisoned(value: Any) -> bool:
    """A leaf no writer produces: non-finite, or of magnitude ``ABSURD`` or more.

    A ``str`` counts by what ``float()`` makes of it (``"NaN"``, ``"Infinity"``,
    ``"1e300"`` …): those are the spellings a loader's coercion turns into a
    poisoned number without raising, which its ``(TypeError, ValueError)``
    guard cannot see. ``bool`` is an ``int`` to Python and never poisoned.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, str):
        try:
            value = float(value)
        except (TypeError, ValueError, OverflowError):
            return False
    if isinstance(value, int):
        return abs(value) >= ABSURD
    if isinstance(value, float):
        return not math.isfinite(value) or abs(value) >= ABSURD
    return False


def _sanitize(value: Any) -> Any:
    """Recursively scrub poisoned numeric leaves (``_poisoned``) to ``None``.

    A dict entry whose key is poisoned is dropped. Anything else -- a finite
    number below ``ABSURD``, a non-numeric string the loader will refuse on its
    own -- passes through untouched, so the boundary never rewrites a healthy
    payload.
    """
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items() if not _poisoned(k)}
    if isinstance(value, list):
        return [_sanitize(child) for child in value]
    if isinstance(value, tuple):
        return tuple(_sanitize(child) for child in value)
    return None if _poisoned(value) else value


def _bound_instants(
    value: Any,
    bound: datetime,
    where: str,
    naive_zone: tzinfo | None = timezone.utc,
    hits: list[str] | None = None,
    path: tuple[str | int, ...] = (),
) -> Any:
    """Bound every stored instant to ``bound``: none may lie beyond it.

    A stored instant was stamped by the clock that ran when it was written. A
    clock that ran ahead then (no RTC, NTP not yet synced) leaves a stamp the
    corrected clock has not reached, and every ``now - stamp`` window the
    stamp opens then holds for the clock's whole error -- a cooldown, a grace
    period, a disinfection timer, one sibling at a time (round 9). Bounded
    here, once, so no loader and no later parse of the string decides it.
    A leaf is an instant when it is a date *and* a time; a date-only day key
    is not one. A naive leaf is read in ``naive_zone``, the zone its loader
    reads it in, and bounded as a naive wall time there (``None``: the naive
    clock's own wall time). Only a leaf beyond the bound is rewritten, so a
    healthy payload comes back unchanged. ``hits`` collects the ``/``-joined
    path of every leaf it rewrote: a loader whose rule differs for a stamp
    ahead of the clock (the outage heartbeat, card C13) reads it there, since
    the bound leaves it equal to now.
    """
    if isinstance(value, str) and len(value) >= 16 and value[10:11] in ("T", " "):
        try:
            when = datetime.fromisoformat(value)
        except ValueError:
            return value
        naive = when.tzinfo is None
        when = when.replace(tzinfo=naive_zone or bound.tzinfo) if naive else when
        if when <= bound:
            return value
        clamped = bound.astimezone(when.tzinfo)
        clamped = clamped.replace(tzinfo=None) if naive else clamped
        _LOGGER.warning(
            "%s: stored instant %s is ahead of the clock; bounded to %s",
            where, value, clamped,
        )
        if hits is not None:
            hits.append("/".join(map(str, path)))
        return clamped.isoformat()
    if isinstance(value, dict):
        return {
            k: _bound_instants(v, bound, where, naive_zone, hits, path + (k,))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [
            _bound_instants(child, bound, where, naive_zone, hits, path + (i,))
            for i, child in enumerate(value)
        ]
    return value


class Domain(NamedTuple):
    """The domain one stored field's own update path writes (card C1).

    ``kind`` is ``real``/``int`` (bounded by ``lo``..``hi``, inclusive),
    ``flag``, ``text``, ``choice`` (one of ``choices``), ``instant`` (an ISO
    date-time), ``day`` or ``month``. ``null``: the writer also stores
    ``None`` (or ``""``) for "not yet". ``whole``: why one bad cell of this
    grid may change the rest of its row or grid; empty when a bad cell costs
    only itself. ``unread``: why the loader does not install the stored value
    (the saver re-derives it), for the few fields that are written, not read.
    """

    kind: str
    lo: float = -math.inf
    hi: float = math.inf
    null: bool = False
    choices: tuple[Any, ...] = ()
    whole: str = ""
    unread: str = ""


def _parses(value: Any, parse: Any, size: int) -> bool:
    try:
        return isinstance(value, str) and len(value) >= size and bool(parse(value))
    except ValueError:
        return False


def _number(value: Any, domain: Domain) -> bool:
    return (
        isinstance(value, (int, float)) and not isinstance(value, bool)
        and math.isfinite(value) and domain.lo <= value <= domain.hi
    )


_KINDS: dict[str, Any] = {
    "real": _number,
    "int": lambda v, d: isinstance(v, int) and _number(v, d),
    "flag": lambda v, d: isinstance(v, bool),
    "text": lambda v, d: isinstance(v, str),
    "choice": lambda v, d: v in d.choices,
    "instant": lambda v, d: _parses(v, datetime.fromisoformat, 16) and v[10] in "T ",
    "day": lambda v, d: len(str(v)) == 10 and _parses(v, date.fromisoformat, 10),
    "month": lambda v, d: len(str(v)) == 7 and _parses(f"{v}-01", date.fromisoformat, 10),
}


def in_domain(domain: Domain, value: Any) -> bool:
    """Whether ``value`` lies in ``domain`` (a key is read as the number it spells)."""
    if value is None or value == "":
        return domain.null
    if domain.kind in ("int", "real") and isinstance(value, str):
        try:
            value = (int if domain.kind == "int" else float)(value)
        except ValueError:
            return False
    return bool(_KINDS[domain.kind](value, domain))


#: The declared domain of every stored field, per store (keyed by the store
#: key's suffix), per path: ``#`` is a list index, ``*`` a data-keyed map's
#: key and ``~`` that key's own domain (a list index names one position). A ``str`` value is an alias: the
#: subtree mirrors ``"<store>/<prefix>"``'s declaration (a snapshot holds the
#: learners' own payloads). The domains are the writers', read off the tree;
#: enforcement is each loader's (``tests/finite_boundary.py`` Arm 6 drives
#: every entry through the real loaders), so this table only declares.
#: Shorthands for the table below.
_POS = math.nextafter(0.0, 1.0)
_R, _Z, _N = Domain("real"), Domain("real", 0.0), Domain("real", null=True)
_COUNT, _FLAG, _TEXT = Domain("int", 0), Domain("flag"), Domain("text")
_AT, _AT0 = Domain("instant"), Domain("instant", null=True)
_DAY, _DAY0, _MONTH = Domain("day"), Domain("day", null=True), Domain("month")
_ABSENT = Domain("choice", null=True)  # ``None`` only: the channel is left automatic
_SHAPE = SHAPE_MAX / SHAPE_MIN
_QUARTER = QUARTER_FACTOR_MAX / QUARTER_FACTOR_MIN
_ROW = "the update path's cone repair clips and renormalises the whole row (observe_day)"
_PAIR = "an unreadable bin restarts the pair with a warning (_stored_rows/_stored_counts, #922)"
_PROFILE = "normalize_profile renormalises to mean 1, and quarantines a non-finite profile whole"
_LEADS = tuple(str(h) for h in LEAD_BUCKETS)
#: The DHW profile: normalize_profile's clip is [0.2, 3.5], but a fresh
#: install stores the configured draw pattern verbatim (cells of 0.1) until
#: the first fold, so the writer's floor is zero. dhw_learning imports this
#: module, so the ceiling is a literal, held equal to its own by Arm 6.
_DHW_INTENSITY = Domain("real", 0.0, 3.5, whole=_PROFILE)

_ACCURACY: dict[str, Domain | str] = {
    "samples/#/t": _AT, "samples/#/predicted_power_kw": Domain("real", 0.0, null=True),
    **{f"samples/#/{k}": _N for k in (
        "actual_power_kw", "predicted_temp", "actual_temp", "actual_cost", "outdoor_temp",
        "humidity", "cop_residual")},
    "samples/#/predicted_cost": _R,
    # #1935: whether a boost overlay governed the interval -- the exclusion
    # tag a post-drift recommendation reads.
    "samples/#/boost_space": _FLAG,
    "lead_sigma/~": Domain("choice", choices=_LEADS), "lead_sigma/*": _Z,
    "lead_counts/~": Domain("choice", choices=_LEADS), "lead_counts/*": Domain("int", 1),
    "lead_pending/#/0": _AT, "lead_pending/#/1": Domain("choice", choices=LEAD_BUCKETS),
    "lead_pending/#/2": _R,
    # #1936: the last restore -- pairs before it never feed a refit.
    "evidence_since": _AT,
}

DOMAINS: dict[str, dict[str, Domain | str]] = {
    "thermal_learning": {
        "buffer_cooling_rate": Domain("real", _POS),  # tank-dependent clamp inside this
        "house_heat_loss_anchor": Domain("real", _POS, unread=(
            "re-derived from the configured loss on save; the load reads it to re-anchor the scale")),
        "house_heat_loss_scale": Domain("real", c.HOUSE_HEAT_LOSS_SCALE_MIN, c.HOUSE_HEAT_LOSS_SCALE_MAX),
        "lower_floor_loss_ratio": Domain("real", c.LOWER_FLOOR_LOSS_RATIO_MIN, c.LOWER_FLOOR_LOSS_RATIO_MAX),
        "cop_scale": Domain("real", c.COP_SCALE_MIN, c.COP_SCALE_MAX),
        **{f"{k}_samples": _COUNT for k in ("buffer_cooling", "house_heat_loss", "lower_floor_loss", "cop")},
        # The cap, as Cusum.as_dict rounds it (1.2 * 1.5 is 1.7999999999999998).
        "vent_cusum/stat": Domain("real", 0.0, round(c.VENT_CUSUM_THRESHOLD_C * STAT_CAP_FACTOR, 4)),
        "cop_health_cusum/stat": Domain("real", 0.0, round(c.COP_HEALTH_THRESHOLD * STAT_CAP_FACTOR, 4)),
        **{f"{k}_cusum/{f}": d for k in ("vent", "cop_health") for f, d in (
            ("tripped", _FLAG), ("evidence/#", _TEXT), ("last_fed", _AT0))},
        "cop_baseline/~": _TEXT, "cop_baseline/*/0": Domain("real", _POS),
        "cop_baseline/*/1": Domain("int", 1),
        "immersion_events/#": _AT,
        "snow_accum_cm": _Z, "snow_accum_last": _AT0, "last_heavy_snow": _AT0,
        "capacity_envelope/~": Domain("int"), "capacity_envelope/*/0": Domain("real", _POS),
        "capacity_envelope/*/1": Domain("int", 1),
        "solar_aperture/n": _Z, "solar_aperture/mx": _Z, "solar_aperture/my": _R,
        "solar_aperture/cov": _R, "solar_aperture/var": _Z,
        "solar_aperture/scale": Domain("real", c.SOLAR_APERTURE_MIN, c.SOLAR_APERTURE_MAX),
        "internal_gains_profile": _ABSENT, "internal_gains_profile/#": Domain(
            "real", 0.0, whole="an unreadable hour drops the learned profile whole to the fallback"),
        "curve_learner/bias": Domain("real", BIAS_MIN, BIAS_MAX),
        "curve_learner/comfortable_days": _COUNT, "curve_learner/resets": _COUNT,
        "curve_learner/last_day": _DAY0, "curve_learner/last_step_at": _AT0,
        "freq_map/~": Domain("int", 0, FREQ_DECILES - 1),
        "freq_map/*/0": Domain("real", _POS, FREQ_MAX_KW_PER_HZ), "freq_map/*/1": _COUNT,
        "freq_fallback": _FLAG,
        "flow_bias/bias_k": Domain("real", -FLOW_BIAS_CLAMP_K, FLOW_SUPPLY_MAX_C),
        "flow_bias/samples": _COUNT,
        "updated_at": _AT,
    },
    "price_model": {
        "model/shapes/#/#": Domain("real", 1 / _SHAPE, _SHAPE, whole=_ROW),
        "model/quarter_factors/#/#": Domain("real", 1 / _QUARTER, _QUARTER, whole=_ROW),
        "model/days/#": Domain("int", 0, whole=_PAIR),
        "model/quarter_days/#": Domain("int", 0, whole=_PAIR),
        "model/residual_var/#/#": Domain("real", 0.0, RESIDUAL_VAR_MAX, whole=_PAIR),
        "days_seen/#": _DAY, "quarter_days_seen/#": _DAY,
    },
    "accuracy": {
        **{f"accuracy/{k}": d for k, d in _ACCURACY.items()},
        "dhw_accuracy": "accuracy/accuracy",
        "defrost/version": Domain("int", STORE_VERSION, STORE_VERSION),
        "defrost/factors/#/#": Domain("real", DERATE_MIN, DERATE_MAX),
        "defrost/duty/#/#": Domain("real", 0.0, 1.0),
        **{f"defrost/{k}/#/#": _COUNT for k in ("counts", "duty_counts", "duty_events")},
        "peaks/month": Domain("month", null=True), "peaks/peaks/#": _Z,
        "peaks/peak_days/#": _DAY0, "peaks/window_key": Domain("text", null=True),
        "peaks/window_sum": _Z, "peaks/window_wsum": _Z, "peaks/window_weight": _Z,
        "peaks/window_samples": _COUNT, "peaks/window_factor": Domain("real", 0.0, 1.0),
        "comfort/configured_weight": Domain("real", COMFORT_WEIGHT_MIN, COMFORT_WEIGHT_MAX, unread=(
            "the configured weight is the options' on every load (ComfortLearner.from_dict)")),
        "comfort/learned_weight": Domain("real", COMFORT_WEIGHT_MIN, COMFORT_WEIGHT_MAX),
        "comfort/evidence": _R, "comfort/overrides": _COUNT, "comfort/last_update": _AT0,
        "comfort/history/#/t": _AT,
        **{f"comfort/history/#/{k}": _R for k in (
            "delta_c", "indoor_temp", "planned_setpoint", "relative_price")},
        "mode": Domain("choice", choices=tuple(c.OPERATION_MODES)),
    },
    "energy": {
        **{f"{k}_energy_kwh": _Z for k in ("space", "dhw", "total")},
        **{f"{k}_cost": _R for k in ("space", "dhw", "total")},
        "since": _DAY0, "last_tick": _AT,
    },
    "ledger": {
        "ledger/months/~": _MONTH, "ledger/months/*/lines/~": _TEXT,
        # MonthlyLedger.add bounds a line to finite only: its kWh are unsigned.
        "ledger/months/*/lines/*/kwh": _R, "ledger/months/*/lines/*/sek": _R,
        "ledger/months/*/meta/~": _TEXT, "ledger/months/*/meta/*/sum": _R,
        "ledger/months/*/meta/*/count": Domain("int", 1),
        "starts/lifetime": _COUNT, "starts/months/~": _MONTH,
        "starts/months/*": Domain("int", 1), "starts/running": _FLAG,
        "month_reports/~": _MONTH, "month_reports/*/month": _MONTH,
        **{f"month_reports/*/{k}/~": _TEXT for k in ("lines", "reasons")},
        **{f"month_reports/*/{k}/*/kwh": _R for k in ("lines", "reasons")},
        **{f"month_reports/*/{k}/*/sek": _R for k in ("lines", "reasons")},
        "month_reports/*/total_kwh": _R, "month_reports/*/total_sek": _R,
        "month_reports/*/compressor_starts": _COUNT,
        "month_reports/*/reasons_reconcile": Domain("flag", null=True),
        "month_reports/*/mean_spot_price": _R,
        "month_reports/*/contract_comparison/month": _MONTH,
        "month_reports/*/contract_comparison/kwh": _R,
        **{f"month_reports/*/contract_comparison/{k}": _R for k in (
            "hourly_spot_sek", "grid_fee_sek", "monthly_avg_spot_sek", "fixed_sek",
            "load_profile_value_per_kwh")},
        "month_reports/*/contract_comparison/cheapest": Domain(
            "choice", choices=("hourly_spot", "monthly_avg_spot", "fixed")),
        "score_day/day": _DAY, "score_day/kwh": _R, "score_day/sek": _R,
        "score_day/spot_sum": _R, "score_day/spot_h": _Z, "score_day/free_streak": _Z,
        "operation_score": Domain("real", 0.0, 100.0, null=True),
        "fuse_advisor/month": _MONTH, "fuse_advisor/current_fuse_a": Domain("real", _POS),
        "fuse_advisor/candidate_fuse_a": Domain("real", _POS),
        "fuse_advisor/candidate_kw": Domain("real", _POS), "fuse_advisor/feasible": _FLAG,
        "fuse_advisor/comfort_shortfall_c": _Z, "fuse_advisor/worst_margin_kw": _R,
        "fuse_advisor/cost_delta_sek_month": _N, "fuse_advisor/error": _TEXT,
        "fuse_advisor_at": _AT0,
    },
    "dhw_profile": {
        **{f"{k}/#": _DHW_INTENSITY for k in ("hourly_profile", "profile_weekday", "profile_weekend")},
        **{f"{k}_samples": _COUNT for k in ("profile_weekday", "profile_weekend", "cooling")},
        "cooling_rate": Domain("real", c.DHW_COOLING_RATE_MIN, c.DHW_COOLING_RATE_MAX),
        "updated_at": _AT,
    },
    "dhw_draws": {
        "reservoirs/~": _TEXT, "reservoirs/*/#": _Z, "open_label": Domain("text", null=True),
        "open_date": _DAY0, "open_kwh": _Z,
    },
    "dhw_legionella": {
        "last_cycle": _AT0, "last_attempt": _AT0, "last_attempt_peak": _R,
        "disinfection_owned/#": _TEXT, "disinfection_latched": _FLAG,
    },
    "boost": {"dhw/until": _AT, "space/until": _AT},
    "notifier": {"sent/~": _TEXT, "sent/*": _TEXT},
    "away": {"active": _FLAG, "return_time": _AT0, "migrated_helpers": _FLAG},
    "pump_duty": {
        "written/mode/0": _TEXT, "written/dhw_setpoint/0": _R, "written/space_setpoint/0": _R,
        **{f"written/{k}/1": _AT for k in ("mode", "dhw_setpoint", "space_setpoint")},
    },
    "manual_plan": {
        **{f"{k}_slots": _ABSENT for k in ("space", "dhw")},
        **{f"{k}_slots/#/{e}": _AT for k in ("space", "dhw") for e in ("start", "end")},
        "expires_at": _AT, "created_at": _AT0,
    },
    "snapshots": {
        "snapshots/#/taken_at": _AT, "snapshots/#/healthy": _FLAG, "snapshots/#/accuracy": _ABSENT,
        "snapshots/#/alarmed_at_capture": _FLAG,
        "snapshots/#/accuracy/samples": Domain("int", 0, HISTORY_LENGTH),
        "snapshots/#/accuracy/temperature_mae": Domain("real", 0.0, null=True),
        **{f"snapshots/#/accuracy/{k}": _N for k in (
            "temperature_bias", "power_ratio", "cost_error_percent")},
        "snapshots/#/accuracy/realised_cost": _R, "snapshots/#/accuracy/predicted_cost": _R,
        "snapshots/#/accuracy/trust": Domain("real", 0.0, 1.0),
        "snapshots/#/accuracy/lead_sigma/~": Domain(
            "choice", choices=tuple(f"{h:g}h" for h in LEAD_BUCKETS)),
        "snapshots/#/accuracy/lead_sigma/*": _Z,
        **{f"snapshots/#/learners/{k}": k for k in ("thermal_learning", "dhw_profile", "dhw_draws")},
        "snapshots/#/learners/price_model": "price_model/model",
        **{f"snapshots/#/learners/{k}": f"accuracy/{k}" for k in ("accuracy", "comfort", "defrost")},
        "bias_days": _COUNT, "last_day": _DAY0, "streak_started": _DAY0,
        "drift_inputs_healthy": _FLAG, "alarmed": _FLAG,
    },
    # The debug collector's ring (#1939). A snapshot is the payload as JSON
    # text: its plan instants lie ahead of the clock by design.
    "debug": {
        "started_at": _AT, "final": _FLAG,
        "rows/#/t": _AT, "rows/#/mode": _TEXT, "rows/#/action_mode": _TEXT,
        "rows/#/heat_pump_on": _FLAG,
        **{f"rows/#/{k}": _R for k in (
            "action_kw", "weather_stale_h", "indoor_temp", "outdoor_temp", "dhw_temp")},
        **{f"rows/#/{k}": _Z for k in ("solve_wall_ms", "payload_solve_time_ms")},
        **{f"rows/#/{k}": _COUNT for k in ("solve_failures", "prices_rows")},
        "rows/#/accuracy_sample": "accuracy/accuracy/samples/#",
        "snapshots/#/t": _AT, "snapshots/#/cycle": _COUNT, "snapshots/#/data": _TEXT,
    },
}


def _tries() -> dict[str, dict[str, Any]]:
    """``DOMAINS`` as one path trie per store, aliases linked in place."""
    tries: dict[str, dict[str, Any]] = {name: {} for name in DOMAINS}
    aliases = []
    for name, table in DOMAINS.items():
        for pattern, domain in table.items():
            node = tries[name]
            *head, last = pattern.split("/")
            for seg in head:
                node = node.setdefault(seg, {})
            if isinstance(domain, str):
                aliases.append((node, last, domain.split("/")))
            elif last == "~":
                node["~"] = domain
            else:
                node.setdefault(last, {})[""] = domain
    for node, last, (target, *prefix) in aliases:
        node[last] = tries[target]
        for seg in prefix:
            node[last] = node[last][seg]
    return tries


def _scalar_domain(node: dict[str, Any]) -> Domain | None:
    """The domain when this node declares one value, not a container of them.

    A container walked in place of that value yields no leaf -- an empty list
    has no element to check -- so the declaration would go unread and a list
    where a number belongs would be admitted.
    """
    domain = node.get("")
    return domain if isinstance(domain, Domain) and set(node) <= {""} else None


def _fields(node: dict[str, Any], value: Any, path: tuple[Any, ...], out: list[Any]) -> None:
    scalar = _scalar_domain(node)
    if scalar is not None and isinstance(value, (dict, list)):
        out.append((path, False, scalar, value))
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if key not in node:
                out.append((path + (key,), True, node.get("~") if "*" in node else None, key))
            _fields(node.get(key, node.get("*", {})), child, path + (key,), out)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _fields(node.get(str(index), node.get("#", {})), child, path + (index,), out)
    else:
        out.append((path, False, node.get(""), value))


def stored_fields(name: str, payload: Any) -> list[tuple[tuple[Any, ...], bool, Domain | None, Any]]:
    """``(path, is_key, declared domain or None, value)`` per stored leaf and map key."""
    out: list[Any] = []
    _fields(_tries().get(name, {}), payload, (), out)
    return out


def admitted(name: str, payload: Any) -> bool:
    """Whether every field of ``payload`` -- store ``name``'s payload, or a
    fragment of it from its root -- is declared and inside its declaration.

    For a loader whose stored record is opaque to it (a presentation dict
    it republishes whole) and that drops the record rather than repair it.
    """
    return all(d is not None and in_domain(d, v) for _p, _k, d, v in stored_fields(name, payload))


def _store_name(key: str) -> str | None:
    """The ``DOMAINS`` entry a store key names (its longest matching suffix)."""
    names = [name for name in DOMAINS if key.endswith("_" + name)]
    return max(names, key=len) if names else None


def _log_off_domain(store: Any, data: Any) -> None:
    """Name the stored fields no declaration covers, or that lie outside theirs.

    Diagnostic only: each loader enforces its fields' domains, and a field no
    entry in ``DOMAINS`` declares is refused by the standing sweep, not here.
    """
    where = str(getattr(store, "key", None) or getattr(store, "_key", "store"))
    name = _store_name(where)
    off = [
        "/".join(map(str, path)) for path, _key, domain, value in stored_fields(name or "", data)
        if domain is None or not in_domain(domain, value)
    ] if name else []
    if off:
        _LOGGER.debug("%s: %d stored field(s) off their declared domain: %s", where, len(off), off[:5])


async def load_mapping(store: Any, what: str) -> dict[str, Any] | None:
    """``store``'s payload when it is a dict, else ``None``; a failed load is logged and reads as none.

    The one prelude of every restore that starts from nothing on a bad read (boost, away, the pump arbiter).
    """
    try:
        raw = await store.async_load()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not load %s: %s", what, err)
        return None
    return raw if isinstance(raw, dict) else None


class QuarantiningStore(Store[_StorePayload]):
    """A ``Store`` whose ``async_load`` scrubs poisoned numeric leaves.

    The finiteness and magnitude properties live here, at the single
    persistence boundary, instead of at each loader seam. A corrupted store
    reaches a loader already sanitized, so a poisoned leaf becomes that
    loader's own absent-data default and nothing poisoned is reachable from
    the live model — whatever store, field or class the poison arrived in.
    """

    #: The read in flight, kept until the next one, and the tasks reading.
    _reading: asyncio.Future[None] | None = None
    _readers: frozenset[asyncio.Task[Any] | None] = frozenset()

    def __init__(
        self,
        hass: Any,
        version: int,
        key: str,
        *args: Any,
        lead: timedelta | None = timedelta(0),
        naive_zone: tzinfo | None = timezone.utc,
        **kwargs: Any,
    ) -> None:
        """``lead``: how far ahead of the clock a stored instant may lie.

        Zero for a store of things that happened; the longest legitimate lead
        for one holding expiries (a boost's maximum); ``None`` only for a
        store of user-set instants no system bound governs. ``naive_zone``:
        the zone the store's loader reads a naive instant in, the one it
        passes ``drift.stored_instant`` -- Home Assistant's where the loader
        reads it so, or the bound is off by the zone's offset either way.
        """
        super().__init__(hass, version, key, *args, **kwargs)
        #: Where a version mismatch is surfaced (``_surface_version``).
        self._issue_hass = hass
        self._major = version
        self._store_key = key
        self._lead = lead
        self._naive_zone = naive_zone
        #: Paths of the instants the last load rewrote to the bound.
        self.bounded: list[str] = []

    async def async_load(self) -> _StorePayload | None:
        self._reading = reading = asyncio.get_running_loop().create_future()
        task = asyncio.current_task()
        self._readers = self._readers | {task}
        _NEWER_ON_DISK.discard(self._store_key)
        try:
            try:
                data = _sanitize(await super().async_load())
            except _DOWNGRADE:
                _NEWER_ON_DISK.add(self._store_key)
                self._surface_version("it was saved by a newer release than this one")
                raise
            if self._lead is not None:
                bound = dt_util.as_utc(dt_util.now()) + self._lead
                where = str(getattr(self, "key", None) or getattr(self, "_key", "store"))
                hits: list[str] = []
                self.bounded = hits
                data = _bound_instants(data, bound, where, self._naive_zone, hits)
            _log_off_domain(self, data)
            return cast(_StorePayload | None, data)
        finally:
            self._readers = self._readers - {task}
            reading.set_result(None)

    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: Any
    ) -> Any:
        """Home Assistant's migration hook; this default migrates nothing.

        Home Assistant calls it when a stored document's version differs from
        this store's. A store whose version is bumped overrides it (a subclass),
        and the standing sweep refuses a version above 1 on a store that does
        not (``tests/finite_boundary.py``, #1740). Reached anyway -- an override
        handed a version it does not know -- a major mismatch is surfaced, where
        the loader would otherwise reset at DEBUG; then ``NotImplementedError``,
        the base hook's own answer, so the document is not re-saved unmigrated
        and a minor-only mismatch is read as stored, as Home Assistant does.
        """
        # The 2025.2.0 floor hands a downgrade here rather than refusing it.
        if old_major_version > self._major:
            _NEWER_ON_DISK.add(self._store_key)
        if old_major_version != self._major:
            self._surface_version(
                f"it was saved at version {old_major_version} and this release reads {self._major}"
            )
        raise NotImplementedError

    def _surface_version(self, detail: str) -> None:
        """A WARNING and a repair issue naming this store's unreadable version."""
        where = str(getattr(self, "key", None) or getattr(self, "_key", "store"))
        _LOGGER.warning("%s: %s; no migration reads it, so its loader starts afresh", where, detail)
        create_issue(
            self._issue_hass, c.DOMAIN, f"store_version_{where}",
            is_fixable=False, severity=ir.IssueSeverity.WARNING,
            translation_key="store_version",
            translation_placeholders={"store": where, "detail": detail},
        )

    async def async_save(self, data: Any) -> None:
        """Save, once this store's read in flight, if any, has landed.

        A save of a whole payload built from memory that runs before the
        startup read lands replaces the persisted state with the fresh
        defaults that read is about to install (round 9, D1-s2-52: five
        coordinator writers lost persisted learned state this way; R6's
        mode setter hit it before them). Waiting here, in the store itself,
        is the property rather than a per-writer discipline: no save this
        type can express clobbers its own pending read. Nor a newer
        release's document the last load could not read: the loader starts
        afresh in memory, and reinstalling that release finds it intact
        (#1869). A reading task does not wait: Home Assistant saves a
        migration's result from inside the load, and waiting there would wait
        on itself (#1740) -- or on a second load, which Home Assistant parks
        on the first (#1869).
        """
        if asyncio.current_task() not in self._readers:
            await self.async_wait_for_read()
        if self._store_key in _NEWER_ON_DISK:  # kept for the release that wrote it
            _LOGGER.debug("%s: a newer release's document is kept; not saved", self._store_key)
            return
        await super().async_save(data)

    async def async_wait_for_read(self) -> None:
        """Return once the read in flight, if any, has landed.

        A writer that saves its whole payload from memory waits here first: a
        write before a startup read lands replaces the stored state with the
        fresh defaults that read is about to overwrite (R6, round 9: a mode set
        during startup zeroed the comfort learner). Shielded, so a cancelled
        writer does not cancel the future another writer awaits.
        """
        if self._reading is not None:
            await asyncio.shield(self._reading)
