"""PV self-consumption: pricing each step at the marginal cost of consuming.

For a house with solar, heating hot water or the buffer from surplus production
beats exporting it at spot-minus-fees. The v2.7.0 Open-Meteo work already
supplies the irradiance forecast and aligns it to the optimizer's step grid;
what was missing is a production model and the economics.

The economics are piecewise, and the pieces matter. While the array produces
more than the house is using, an extra kWh consumed by the heat pump does not
cost the import price — it costs the export compensation that was foregone.
But only up to the surplus: every kWh beyond it is imported at the market
price like any other. So the cost of drawing ``P`` in a step with surplus
``s`` is

    export_price · min(P, s) + import_price · max(P - s, 0)

An earlier formulation collapsed this to a single per-step price, substituting
the export price for the whole step whenever *any* surplus existed. That made
0.05 kW of winter sun reprice 6 kW of grid import to nearly free, and the plan
piled consumption into steps with trivial surplus. The optimizer now charges
the piecewise cost exactly; this module supplies the primitives.

The production model is deliberately simple. A full plane-of-array transposition
with incidence-angle modifiers is not justified when the irradiance forecast
itself carries far more error than the model would remove.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

_LOGGER = logging.getLogger(__name__)

# Reference irradiance at which a panel produces its rated output.
STC_IRRADIANCE = 1000.0  # W/m²


@dataclass
class PVConfig:
    """Configuration of a photovoltaic array and its export economics."""

    enabled: bool = False
    #: Installed DC capacity.
    peak_kw: float = 0.0
    #: Everything between irradiance and the meter: module temperature losses,
    #: inverter efficiency, soiling, wiring, orientation. One number, because
    #: the irradiance forecast error dwarfs any refinement here.
    system_efficiency: float = 0.80
    #: What an exported kWh earns, in the same currency as the import price.
    export_price: float = 0.0
    #: Optional entity supplying a live export compensation instead.
    export_price_entity: str | None = None
    #: Optional entity measuring actual production, which supersedes the model
    #: for the current step.
    production_entity: str | None = None
    #: Assumed house load when no baseline power entity is configured. A house
    #: is never at zero, and assuming zero would treat all production as
    #: surplus and over-value self-consumption.
    default_baseline_kw: float = 0.4


def forecast_production_kw(
    irradiance_w_m2: np.ndarray, config: PVConfig
) -> np.ndarray:
    """Model AC production from a global horizontal irradiance forecast."""
    if not config.enabled or config.peak_kw <= 0:
        return np.zeros(len(irradiance_w_m2), dtype=float)
    irradiance = np.clip(np.asarray(irradiance_w_m2, dtype=float), 0.0, None)
    production = (
        config.peak_kw * config.system_efficiency * irradiance / STC_IRRADIANCE
    )
    # An array cannot exceed its nameplate no matter what the forecast says;
    # cloud-edge enhancement can push GHI above 1000 W/m² briefly.
    return np.clip(production, 0.0, config.peak_kw)


def surplus_kw(
    production_kw: np.ndarray,
    baseline_load_kw: np.ndarray,
) -> np.ndarray:
    """Production left over after the rest of the house has taken its share."""
    return np.clip(
        np.asarray(production_kw, dtype=float)
        - np.asarray(baseline_load_kw, dtype=float),
        0.0,
        None,
    )


def import_margin(
    import_prices: np.ndarray, export_price: float
) -> np.ndarray:
    """What a self-consumed kWh saves over an imported one, per step.

    Floored at zero: exporting can never be worth more than importing costs,
    or the house would be better off never consuming anything — the floor
    guards against a mis-configured export price inverting the objective.
    """
    return np.clip(np.asarray(import_prices, dtype=float) - float(export_price), 0.0, None)


def piecewise_cost(
    import_prices: np.ndarray,
    surplus: np.ndarray,
    export_price: float,
    total_power_kw: np.ndarray,
    dt_hours: float,
) -> float:
    """Exact grid cost of a total electrical draw across the horizon.

    Each step's energy up to the forecast surplus displaces an export and
    costs the export compensation; everything beyond it is imported at the
    market price.
    """
    prices = np.asarray(import_prices, dtype=float)
    power = np.asarray(total_power_kw, dtype=float)
    covered = np.minimum(power, np.asarray(surplus, dtype=float))
    margin = import_margin(prices, export_price)
    return float((np.sum(prices * power) - np.sum(margin * covered)) * dt_hours)


def blended_block_prices(
    import_prices: np.ndarray,
    surplus: np.ndarray,
    export_price: float,
    block_kw: float,
) -> np.ndarray:
    """Per-kWh price of running a fixed-power block at each step.

    The hot-water planners schedule on/off blocks of a known power and rank
    steps by a single per-step price, so the piecewise cost of one block is
    folded into a blended rate: the surplus-covered fraction at the export
    price, the rest at the import price. Exact for the full block the planner
    actually schedules, which is the only thing it schedules.
    """
    prices = np.asarray(import_prices, dtype=float)
    covered_fraction = np.minimum(
        1.0, np.asarray(surplus, dtype=float) / max(float(block_kw), 1e-6)
    )
    return prices - import_margin(prices, export_price) * covered_fraction


def summarize(
    production_kw: np.ndarray,
    surplus: np.ndarray,
    dt_hours: float,
) -> dict:
    """Reporting figures for the PV sensor attributes."""
    production = np.asarray(production_kw, dtype=float)
    return {
        "forecast_production_kwh": round(float(np.sum(production) * dt_hours), 2),
        "forecast_surplus_kwh": round(float(np.sum(surplus) * dt_hours), 2),
        "surplus_hours": round(float(np.sum(surplus > 1e-6) * dt_hours), 2),
        "peak_production_kw": round(float(np.max(production)) if production.size else 0.0, 2),
    }
