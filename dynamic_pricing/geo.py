"""Geographic graph construction and shortest-path utilities."""

from __future__ import annotations

import heapq
import math
from collections import defaultdict


EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(min(1.0, a)))


class CityGraph:
    """Undirected city graph with optional scipy KD-tree acceleration."""

    def __init__(self, cities, max_distance_km: float = 500.0):
        self.cities = cities.reset_index(drop=True).copy()
        self.max_distance_km = max_distance_km
        self.graph = defaultdict(list)
        self._build()

    def _build(self):
        names = self.cities["city"].astype(str).tolist()
        coords = self.cities[["latitude", "longitude"]].astype(float).to_numpy()
        pairs = []
        try:
            from scipy.spatial import cKDTree
            # A degree is a conservative spatial prefilter; haversine is authoritative.
            radius = self.max_distance_km / 110.0
            pairs = cKDTree(coords).query_pairs(radius)
        except Exception:
            pairs = ((i, j) for i in range(len(names)) for j in range(i + 1, len(names)))
        for i, j in pairs:
            d = haversine_km(*coords[i], *coords[j])
            if d <= self.max_distance_km:
                self.graph[names[i]].append((names[j], d))
                self.graph[names[j]].append((names[i], d))
        for name in names:
            self.graph.setdefault(name, [])

    def shortest_paths(self, source: str):
        if source not in self.graph:
            raise ValueError(f"Unknown city: {source}")
        distances = {name: math.inf for name in self.graph}
        distances[source] = 0.0
        queue = [(0.0, source)]
        while queue:
            distance, node = heapq.heappop(queue)
            if distance != distances[node]:
                continue
            for neighbor, weight in self.graph[node]:
                candidate = distance + weight
                if candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    heapq.heappush(queue, (candidate, neighbor))
        return distances
