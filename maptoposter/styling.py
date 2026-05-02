from __future__ import annotations

from typing import Any


class RoadStyler:
    """Chooses road colors and widths based on OpenStreetMap highway types."""

    def __init__(self, theme: dict[str, Any]) -> None:
        self.theme = theme

    def get_edge_colors(self, graph: Any) -> list[str]:
        return [
            self.color_for_highway(data.get("highway", "unclassified"))
            for _, _, data in graph.edges(data=True)
        ]

    def get_edge_widths(self, graph: Any) -> list[float]:
        return [
            self.width_for_highway(data.get("highway", "unclassified"))
            for _, _, data in graph.edges(data=True)
        ]

    def color_for_highway(self, highway: str | list[str]) -> str:
        highway = self._normalise_highway(highway)

        if highway in ["motorway", "motorway_link"]:
            return self.theme["road_motorway"]
        if highway in ["trunk", "trunk_link", "primary", "primary_link"]:
            return self.theme["road_primary"]
        if highway in ["secondary", "secondary_link"]:
            return self.theme["road_secondary"]
        if highway in ["tertiary", "tertiary_link"]:
            return self.theme["road_tertiary"]
        if highway in ["residential", "living_street", "unclassified"]:
            return self.theme["road_residential"]
        return self.theme["road_default"]

    def width_for_highway(self, highway: str | list[str]) -> float:
        highway = self._normalise_highway(highway)

        if highway in ["motorway", "motorway_link"]:
            return 1.2
        if highway in ["trunk", "trunk_link", "primary", "primary_link"]:
            return 1.0
        if highway in ["secondary", "secondary_link"]:
            return 0.8
        if highway in ["tertiary", "tertiary_link"]:
            return 0.6
        return 0.4

    def _normalise_highway(self, highway: str | list[str]) -> str:
        if isinstance(highway, list):
            return highway[0] if highway else "unclassified"
        return highway
