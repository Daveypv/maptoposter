from __future__ import annotations

from .config import ProjectPaths
from .face import FacePosterRenderer
from .fonts import FontManager
from .geocoding import GeocodingService
from .output import OutputFileManager
from .rendering import MapPosterRenderer
from .themes import ThemeManager


class MapPosterApp:
    """High-level class that wires the managers together."""

    def __init__(self, paths: ProjectPaths | None = None) -> None:
        self.paths = paths or ProjectPaths()
        self.theme_manager = ThemeManager(self.paths.themes_dir)
        self.font_manager = FontManager(self.paths.fonts_dir)
        self.output_manager = OutputFileManager(self.paths.posters_dir)
        self.geocoding_service = GeocodingService()

    def create_city_poster(self, city: str, country: str, theme_name: str, distance: int) -> str:
        theme_name = self.theme_manager.normalize_theme_name(theme_name)
        theme = self.theme_manager.load_theme(theme_name)
        fonts = self.font_manager.load_fonts()
        coords = self.geocoding_service.get_coordinates(city, country)
        output_file = self.output_manager.generate_filename(city, theme_name)

        renderer = MapPosterRenderer(theme=theme, fonts=fonts)
        renderer.create_poster(city, country, coords, distance, output_file)
        return str(output_file)

    def create_face_poster(
        self,
        image_path: str,
        theme_name: str,
        title: str,
        subtitle: str,
    ) -> str:
        theme_name = self.theme_manager.normalize_theme_name(theme_name)
        theme = self.theme_manager.load_theme(theme_name)
        fonts = self.font_manager.load_fonts()
        output_file = self.output_manager.generate_face_filename(title, theme_name)

        renderer = FacePosterRenderer(theme=theme, fonts=fonts)
        renderer.create_poster(image_path, title, subtitle, output_file)
        return str(output_file)

    def list_themes(self) -> None:
        available_themes = self.theme_manager.get_available_themes()
        if not available_themes:
            print("No themes found in 'themes/' directory.")
            return

        print("\nAvailable Themes:")
        print("-" * 60)
        for theme_name in available_themes:
            display_name, description = self.theme_manager.get_theme_details(theme_name)
            print(f"  {theme_name}")
            print(f"    {display_name}")
            if description:
                print(f"    {description}")
            print()

    def has_theme(self, theme_name: str) -> bool:
        return self.theme_manager.normalize_theme_name(theme_name) in self.theme_manager.get_available_themes()

    def get_available_themes(self) -> list[str]:
        return self.theme_manager.get_available_themes()
