import unittest

import pandas as pd

from dynamic_pricing.geo import CityGraph, haversine_km
from dynamic_pricing.pricing import price_transactions


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.cities = pd.DataFrame([
            ["A", 0, 0], ["B", 0, 1], ["C", 0, 2],
        ], columns=["city", "latitude", "longitude"])
        self.transactions = pd.DataFrame([
            ["p", "A", "2025-01-01", 2, 10], ["p", "B", "2025-02-01", 4, 10],
            ["p", "C", "2025-03-01", 6, 10], ["p", "B", "2025-04-01", 3, 10],
        ], columns=["product", "city", "date", "quantity", "unit_price"])

    def test_haversine(self):
        self.assertAlmostEqual(haversine_km(0, 0, 0, 1), 111.19, delta=0.2)

    def test_dijkstra(self):
        distances = CityGraph(self.cities, 200).shortest_paths("A")
        self.assertAlmostEqual(distances["C"], 222.39, delta=1.0)

    def test_pricing(self):
        result = price_transactions(self.cities, self.transactions, "A",)
        self.assertIn("dynamic_price", result)
        self.assertEqual(result.loc[0, "route_distance_km"], 0)
        self.assertGreater(result.loc[2, "dynamic_price"], result.loc[0, "dynamic_price"])


if __name__ == "__main__":
    unittest.main()
