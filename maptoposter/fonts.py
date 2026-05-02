from __future__ import annotations

from pathlib import Path


class FontManager:
    """Finds the Roboto font files used when drawing poster text."""

    FONT_FILES = {
        "bold": "Roboto-Bold.ttf",
        "regular": "Roboto-Regular.ttf",
        "light": "Roboto-Light.ttf",
    }

    def __init__(self, fonts_dir: Path) -> None:
        self.fonts_dir = Path(fonts_dir)

    def load_fonts(self) -> dict[str, Path] | None:
        fonts = {
            weight: self.fonts_dir / filename
            for weight, filename in self.FONT_FILES.items()
        }

        for path in fonts.values():
            if not path.exists():
                print(f"Warning: font not found: {path}")
                return None

        return fonts
