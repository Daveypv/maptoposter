from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re


class OutputFileManager:
    """Builds poster filenames and creates the output folder when needed."""

    def __init__(self, posters_dir: Path) -> None:
        self.posters_dir = Path(posters_dir)

    def generate_filename(self, city: str, theme_name: str) -> Path:
        self.posters_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        city_slug = self._slugify(city)
        filename = f"{city_slug}_{theme_name}_{timestamp}.png"
        return self.posters_dir / filename

    def generate_face_filename(self, title: str, theme_name: str) -> Path:
        self.posters_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title_slug = self._slugify(title)
        filename = f"{title_slug}_{theme_name}_face_{timestamp}.png"
        return self.posters_dir / filename

    def _slugify(self, value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
        return slug or "poster"
