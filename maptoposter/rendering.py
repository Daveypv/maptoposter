from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
from matplotlib.font_manager import FontProperties

from .map_data import MapData, MapDataFetcher
from .styling import RoadStyler


class GradientPainter:
    """Draws the soft fade at the top and bottom of the poster."""

    def create_gradient_fade(self, ax: Any, color: str, location: str = "bottom", zorder: int = 10) -> None:
        vals = np.linspace(0, 1, 256).reshape(-1, 1)
        gradient = np.hstack((vals, vals))

        rgb = mcolors.to_rgb(color)
        colors = np.zeros((256, 4))
        colors[:, 0] = rgb[0]
        colors[:, 1] = rgb[1]
        colors[:, 2] = rgb[2]

        if location == "bottom":
            colors[:, 3] = np.linspace(1, 0, 256)
            extent_y_start = 0
            extent_y_end = 0.25
        else:
            colors[:, 3] = np.linspace(0, 1, 256)
            extent_y_start = 0.75
            extent_y_end = 1.0

        custom_cmap = mcolors.ListedColormap(colors)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        y_range = ylim[1] - ylim[0]
        y_bottom = ylim[0] + y_range * extent_y_start
        y_top = ylim[0] + y_range * extent_y_end

        ax.imshow(
            gradient,
            extent=[xlim[0], xlim[1], y_bottom, y_top],
            aspect="auto",
            cmap=custom_cmap,
            zorder=zorder,
            origin="lower",
        )


class PosterTypography:
    """Creates fonts and draws poster labels."""

    def __init__(self, fonts: dict[str, Path] | None) -> None:
        self.fonts = fonts

    def draw_labels(
        self,
        ax: Any,
        city: str,
        country: str,
        point: tuple[float, float],
        theme: dict[str, Any],
    ) -> None:
        font_main, font_sub, font_coords, font_attr = self._build_fonts()
        spaced_city = "  ".join(list(city.upper()))

        ax.text(0.5, 0.14, spaced_city, transform=ax.transAxes, color=theme["text"], ha="center", fontproperties=font_main, zorder=11)
        ax.text(0.5, 0.10, country.upper(), transform=ax.transAxes, color=theme["text"], ha="center", fontproperties=font_sub, zorder=11)
        ax.text(
            0.5,
            0.07,
            self.format_coordinates(point),
            transform=ax.transAxes,
            color=theme["text"],
            alpha=0.7,
            ha="center",
            fontproperties=font_coords,
            zorder=11,
        )
        ax.plot([0.4, 0.6], [0.125, 0.125], transform=ax.transAxes, color=theme["text"], linewidth=1, zorder=11)
        ax.text(
            0.98,
            0.02,
            "© OpenStreetMap contributors",
            transform=ax.transAxes,
            color=theme["text"],
            alpha=0.5,
            ha="right",
            va="bottom",
            fontproperties=font_attr,
            zorder=11,
        )

    def format_coordinates(self, point: tuple[float, float]) -> str:
        lat, lon = point
        lat_direction = "N" if lat >= 0 else "S"
        lon_direction = "E" if lon >= 0 else "W"
        return f"{abs(lat):.4f}° {lat_direction} / {abs(lon):.4f}° {lon_direction}"

    def _build_fonts(self) -> tuple[FontProperties, FontProperties, FontProperties, FontProperties]:
        if self.fonts:
            return (
                FontProperties(fname=self.fonts["bold"], size=60),
                FontProperties(fname=self.fonts["light"], size=22),
                FontProperties(fname=self.fonts["regular"], size=14),
                FontProperties(fname=self.fonts["light"], size=8),
            )

        return (
            FontProperties(family="monospace", weight="bold", size=60),
            FontProperties(family="monospace", weight="normal", size=22),
            FontProperties(family="monospace", size=14),
            FontProperties(family="monospace", size=8),
        )


class MapPosterRenderer:
    """Coordinates the full poster rendering pipeline."""

    def __init__(
        self,
        theme: dict[str, Any],
        fonts: dict[str, Path] | None,
        data_fetcher: MapDataFetcher | None = None,
        gradient_painter: GradientPainter | None = None,
    ) -> None:
        self.theme = theme
        self.data_fetcher = data_fetcher or MapDataFetcher()
        self.gradient_painter = gradient_painter or GradientPainter()
        self.road_styler = RoadStyler(theme)
        self.typography = PosterTypography(fonts)

    def create_poster(self, city: str, country: str, point: tuple[float, float], dist: int, output_file: Path) -> None:
        print(f"\nGenerating map for {city}, {country}...")
        map_data = self.data_fetcher.fetch(point, dist)
        self.render(city, country, point, map_data, output_file)

    def render(self, city: str, country: str, point: tuple[float, float], map_data: MapData, output_file: Path) -> None:
        print("Rendering map...")
        fig, ax = plt.subplots(figsize=(12, 16), facecolor=self.theme["bg"])
        ax.set_facecolor(self.theme["bg"])
        ax.set_position([0, 0, 1, 1])

        self._plot_polygons(ax, map_data)
        self._plot_roads(ax, map_data)

        self.gradient_painter.create_gradient_fade(ax, self.theme["gradient_color"], location="bottom", zorder=10)
        self.gradient_painter.create_gradient_fade(ax, self.theme["gradient_color"], location="top", zorder=10)
        self.typography.draw_labels(ax, city, country, point, self.theme)

        print(f"Saving to {output_file}...")
        plt.savefig(output_file, dpi=300, facecolor=self.theme["bg"])
        plt.close(fig)
        print(f"Done. Poster saved as {output_file}")

    def _plot_polygons(self, ax: Any, map_data: MapData) -> None:
        if map_data.water is not None and not map_data.water.empty:
            map_data.water.plot(ax=ax, facecolor=self.theme["water"], edgecolor="none", zorder=1)
        if map_data.parks is not None and not map_data.parks.empty:
            map_data.parks.plot(ax=ax, facecolor=self.theme["parks"], edgecolor="none", zorder=2)

    def _plot_roads(self, ax: Any, map_data: MapData) -> None:
        print("Applying road hierarchy colors...")
        ox.plot_graph(
            map_data.graph,
            ax=ax,
            bgcolor=self.theme["bg"],
            node_size=0,
            edge_color=self.road_styler.get_edge_colors(map_data.graph),
            edge_linewidth=self.road_styler.get_edge_widths(map_data.graph),
            show=False,
            close=False,
        )
