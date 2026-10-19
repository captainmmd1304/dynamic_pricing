from __future__ import annotations

import argparse
from pathlib import Path

from .pricing import price_transactions


def demo_data(root: Path):
    import pandas as pd
    root.mkdir(parents=True, exist_ok=True)
    cities = pd.DataFrame([
        ["London", 51.5072, -0.1276], ["Birmingham", 52.4862, -1.8904],
        ["Manchester", 53.4808, -2.2426], ["Bristol", 51.4545, -2.5879],
        ["Leeds", 53.8008, -1.5491], ["Oxford", 51.7520, -1.2577],
    ], columns=["city", "latitude", "longitude"])
    rows = []
    for month in range(1, 13):
        for city in cities.city:
            rows.append(["SKU-1", city, f"2025-{month:02d}-15", 2 + (month % 4) + (city == "London"), 25.0])
            rows.append(["SKU-2", city, f"2025-{month:02d}-15", 1 + (month % 3), 60.0])
    transactions = pd.DataFrame(rows, columns=["product", "city", "date", "quantity", "unit_price"])
    cities.to_csv(root / "cities.csv", index=False)
    transactions.to_csv(root / "transactions.csv", index=False)
    return cities, transactions


def main():
    parser = argparse.ArgumentParser(description="Dynamic e-commerce pricing pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("--root", type=Path, default=Path("data"))
    price = sub.add_parser("price")
    price.add_argument("--cities", type=Path, required=True)
    price.add_argument("--transactions", type=Path, required=True)
    price.add_argument("--origin", required=True)
    price.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import pandas as pd
    if args.command == "demo":
        cities, transactions = demo_data(args.root)
        output = Path("output/priced_transactions.csv")
        output.parent.mkdir(exist_ok=True)
        priced = price_transactions(cities, transactions, "London")
        priced.to_csv(output, index=False)
        print(f"Generated {args.root} and {output} ({len(priced)} rows)")
    else:
        priced = price_transactions(pd.read_csv(args.cities), pd.read_csv(args.transactions), args.origin)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        priced.to_csv(args.output, index=False)
        print(f"Wrote {args.output} ({len(priced)} rows); demand metrics={priced.attrs.get('demand_metrics', {})}")


if __name__ == "__main__":
    main()
