from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import osmnx as ox
from tqdm import tqdm


@dataclass(frozen=True)
class MapData:
    """The OpenStreetMap data needed to render a map poster."""

    graph: Any
    water: Any | None
    parks: Any | None


class MapDataFetcher:
    """Downloads roads, water, and parks from OpenStreetMap."""

    def fetch(self, point: tuple[float, float], dist: int) -> MapData:
        with tqdm(total=3, desc="Fetching map data", unit="step", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            pbar.set_description("Downloading street network")
            graph = ox.graph_from_point(point, dist=dist, dist_type="bbox", network_type="all")
            pbar.update(1)
            time.sleep(0.5)

            pbar.set_description("Downloading water features")
            try:
                water = ox.features_from_point(point, tags={"natural": "water", "waterway": "riverbank"}, dist=dist)
            except Exception:
                water = None
            pbar.update(1)
            time.sleep(0.3)

            pbar.set_description("Downloading parks/green spaces")
            try:
                parks = ox.features_from_point(point, tags={"leisure": "park", "landuse": "grass"}, dist=dist)
            except Exception:
                parks = None
            pbar.update(1)

        print("All data downloaded successfully.")
        return MapData(graph=graph, water=water, parks=parks)
