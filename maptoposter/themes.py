from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_THEME = {
    "name": "Feature-Based Shading",
    "description": "Different shades for different road types and features with clear hierarchy",
    "bg": "#FFFFFF",
    "text": "#000000",
    "gradient_color": "#FFFFFF",
    "water": "#C0C0C0",
    "parks": "#F0F0F0",
    "road_motorway": "#0A0A0A",
    "road_primary": "#1A1A1A",
    "road_secondary": "#2A2A2A",
    "road_tertiary": "#3A3A3A",
    "road_residential": "#4A4A4A",
    "road_default": "#3A3A3A",
}


class ThemeManager:
    """Loads theme JSON files and lists the available theme names."""

    def __init__(self, themes_dir: Path) -> None:
        self.themes_dir = Path(themes_dir)

    def get_available_themes(self) -> list[str]:
        if not self.themes_dir.exists():
            self.themes_dir.mkdir(parents=True)
            return []

        return sorted(path.stem for path in self.themes_dir.glob("*.json"))

    def normalize_theme_name(self, theme_name: str) -> str:
        return theme_name.strip().lower().replace("-", "_")

    def load_theme(self, theme_name: str = "feature_based") -> dict[str, Any]:
        theme_name = self.normalize_theme_name(theme_name)
        theme_file = self.themes_dir / f"{theme_name}.json"

        if not theme_file.exists():
            print(f"Warning: theme file '{theme_file}' not found. Using the default theme.")
            return DEFAULT_THEME.copy()

        with theme_file.open("r", encoding="utf-8") as file:
            theme = json.load(file)

        print(f"Loaded theme: {theme.get('name', theme_name)}")
        if "description" in theme:
            print(f"  {theme['description']}")

        return theme

    def get_theme_details(self, theme_name: str) -> tuple[str, str]:
        theme_path = self.themes_dir / f"{theme_name}.json"
        try:
            with theme_path.open("r", encoding="utf-8") as file:
                theme_data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return theme_name, ""

        return (
            theme_data.get("name", theme_name),
            theme_data.get("description", ""),
        )
