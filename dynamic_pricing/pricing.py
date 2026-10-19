"""End-to-end dynamic pricing pipeline."""

from dataclasses import dataclass

from .demand import DemandForecaster
from .geo import CityGraph


@dataclass
class PricingConfig:
    max_distance_km: float = 500.0
    fuel_litres_per_km: float = 0.025
    fuel_price_per_litre: float = 1.72
    demand_sensitivity: float = 0.05
    max_demand_multiplier: float = 1.50


def price_transactions(cities, transactions, origin: str, config: PricingConfig | None = None):
    import pandas as pd
    config = config or PricingConfig()
    city_data = cities.rename(columns={c: c.lower() for c in cities.columns}).copy()
    tx = transactions.rename(columns={c: c.lower() for c in transactions.columns}).copy()
    aliases = {"stockcode": "product", "invoicedate": "date", "quantity": "quantity", "unitprice": "unit_price"}
    tx = tx.rename(columns={k: v for k, v in aliases.items() if k in tx.columns})
    required = {"city", "product", "date", "quantity", "unit_price"}
    missing = required - set(tx.columns)
    if missing:
        raise ValueError(f"Transactions missing columns: {sorted(missing)}")
    graph = CityGraph(city_data, config.max_distance_km)
    distances = graph.shortest_paths(origin)
    forecaster = DemandForecaster().fit(tx)
    baseline = max(forecaster.global_mean, 1.0)
    result = tx.copy()
    result["route_distance_km"] = result["city"].map(distances).fillna(float("nan"))
    result["predicted_demand"] = [forecaster.predict(row.product, row.city, row.date) for row in result.itertuples()]
    demand_ratio = (result["predicted_demand"] / baseline).clip(lower=0.0)
    demand_multiplier = (1.0 + config.demand_sensitivity * (demand_ratio - 1.0)).clip(upper=config.max_demand_multiplier)
    result["transport_cost"] = result["route_distance_km"] * config.fuel_litres_per_km * config.fuel_price_per_litre
    result["demand_multiplier"] = demand_multiplier
    result["dynamic_price"] = (result["unit_price"] * demand_multiplier + result["transport_cost"]).round(2)
    result.attrs["demand_metrics"] = forecaster.metrics
    return result
