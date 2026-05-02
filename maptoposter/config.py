from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Stores the folders used by the project."""

    root: Path = Path(".")
    themes_dir_name: str = "themes"
    fonts_dir_name: str = "fonts"
    posters_dir_name: str = "posters"
    images_dir_name: str = "images"

    @property
    def themes_dir(self) -> Path:
        return self.root / self.themes_dir_name

    @property
    def fonts_dir(self) -> Path:
        return self.root / self.fonts_dir_name

    @property
    def posters_dir(self) -> Path:
        return self.root / self.posters_dir_name

    @property
    def images_dir(self) -> Path:
        return self.root / self.images_dir_name
