"""PV self-consumption: pricing each step at the marginal cost of consuming.

For a house with solar, heating hot water or the buffer from surplus production
beats exporting it at spot-minus-fees. The v2.7.0 Open-Meteo work already
supplies the irradiance forecast and aligns it to the optimizer's step grid;
what was missing is a production model and the economics.

The economics fall out of the existing cost formulation without any new
optimizer structure, which is what makes this cheap. While the array is
producing more than the house is using, an extra kWh consumed by the heat pump
does not cost the import price — it costs the export compensation that was
foregone. Below surplus, it costs the import price as usual. So:

    effective_price[k] = export_price[k]  while in surplus
                       = import_price[k]  otherwise

and everything downstream (the LP hot-water planner, the space-heating
objective, the savings settle-up) keeps working unchanged.

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


def effective_prices(
    import_prices: np.ndarray,
    surplus: np.ndarray,
    export_price: float | np.ndarray,
) -> np.ndarray:
    """Marginal cost of consuming a kWh at each step.

    Note that this deliberately does *not* interpolate between the two prices
    according to how much surplus there is. The optimizer decides the heat pump
    power, so whether a given step is in surplus depends on the answer — a
    circularity that a per-step blend would only hide. Using the marginal price
    at zero heat pump draw makes self-consumption attractive exactly where
    surplus exists, and the capacity and comfort constraints then bound how
    much is actually taken.
    """
    prices = np.asarray(import_prices, dtype=float)
    has_surplus = np.asarray(surplus, dtype=float) > 1e-6
    export = np.asarray(
        export_price
        if isinstance(export_price, np.ndarray)
        else np.full(len(prices), float(export_price)),
        dtype=float,
    )
    # Exporting can never be worth more than importing costs, or the house
    # would be better off never consuming anything; guard against a
    # mis-configured export price inverting the whole objective.
    export = np.minimum(export, prices)
    return np.where(has_surplus, export, prices)


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
