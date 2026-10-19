# Dynamic E-Commerce Pricing

A practical implementation of the attached research project: geographic routing with a KD-tree, shortest-path delivery distance with Dijkstra, demand forecasting, and distance/demand-aware prices.

## Quick start

```powershell
cd .\dynamic-pricing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m dynamic_pricing.cli demo
python -m dynamic_pricing.cli price --cities data/cities.csv --transactions data/transactions.csv --origin London --output output/priced_transactions.csv
python -m dynamic_pricing.api
```

The `demo` command generates sample cities and transactions, trains a demand model, computes shortest routes, and writes priced transactions under `output/`.

## Input data

Cities must contain `city`, `latitude`, and `longitude`. Transactions must contain `product`, `city`, `date`, `quantity`, and `unit_price`. Column aliases such as `City`, `StockCode`, `InvoiceDate`, `Quantity`, and `UnitPrice` are accepted.

The pricing formula is:

`dynamic_price = unit_price + distance_km * fuel_litres_per_km * fuel_price + demand_adjustment`

The default demand adjustment is `unit_price * demand_sensitivity * max(predicted_demand / baseline_demand - 1, 0)`, capped by `max_demand_multiplier`.

This is a decision-support model, not an automatic price-discrimination system. Production use should add consent, audit logs, fairness checks, tax/shipping rules, and a human-approved pricing policy.

## Tests

```powershell
python -m unittest discover -s tests -v
```
