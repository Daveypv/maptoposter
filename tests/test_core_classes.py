import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from maptoposter.face import FaceImageLoader, FacePosterRenderer
from maptoposter.fonts import FontManager
from maptoposter.output import OutputFileManager
from maptoposter.rendering import PosterTypography
from maptoposter.styling import RoadStyler
from maptoposter.themes import DEFAULT_THEME, ThemeManager


class FakeGraph:
    def __init__(self, edge_data):
        self.edge_data = edge_data

    def edges(self, data=False):
        if data:
            return [(index, index + 1, item) for index, item in enumerate(self.edge_data)]
        return []


class ThemeManagerTest(unittest.TestCase):
    def test_get_available_themes_returns_json_file_stems(self):
        with tempfile.TemporaryDirectory() as directory:
            theme_dir = Path(directory)
            (theme_dir / "noir.json").write_text("{}", encoding="utf-8")
            (theme_dir / "README.md").write_text("ignore me", encoding="utf-8")

            self.assertEqual(ThemeManager(theme_dir).get_available_themes(), ["noir"])

    def test_load_theme_reads_json(self):
        with tempfile.TemporaryDirectory() as directory:
            theme_dir = Path(directory)
            theme = {"name": "Test Theme", "bg": "#000000"}
            (theme_dir / "test.json").write_text(json.dumps(theme), encoding="utf-8")

            self.assertEqual(ThemeManager(theme_dir).load_theme("test"), theme)

    def test_load_theme_uses_default_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            loaded = ThemeManager(Path(directory)).load_theme("missing")

            self.assertEqual(loaded["name"], DEFAULT_THEME["name"])

    def test_normalize_theme_name_accepts_hyphens(self):
        manager = ThemeManager(Path("themes"))

        self.assertEqual(manager.normalize_theme_name("neon-cyberpunk"), "neon_cyberpunk")


class FontManagerTest(unittest.TestCase):
    def test_load_fonts_returns_none_when_a_font_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(FontManager(Path(directory)).load_fonts())


class OutputFileManagerTest(unittest.TestCase):
    def test_generate_filename_creates_poster_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output = OutputFileManager(Path(directory)).generate_filename("New York", "noir")

            self.assertEqual(output.parent, Path(directory))
            self.assertTrue(output.name.startswith("new_york_noir_"))
            self.assertEqual(output.suffix, ".png")

    def test_generate_face_filename_creates_face_poster_path(self):
        with tempfile.TemporaryDirectory() as directory:
            output = OutputFileManager(Path(directory)).generate_face_filename("Jane Doe", "sunset")

            self.assertEqual(output.parent, Path(directory))
            self.assertTrue(output.name.startswith("jane_doe_sunset_face_"))
            self.assertEqual(output.suffix, ".png")


class RoadStylerTest(unittest.TestCase):
    def test_styles_edges_by_road_type(self):
        graph = FakeGraph([
            {"highway": "motorway"},
            {"highway": ["primary", "residential"]},
            {"highway": "service"},
        ])
        styler = RoadStyler(DEFAULT_THEME)

        self.assertEqual(
            styler.get_edge_colors(graph),
            [
                DEFAULT_THEME["road_motorway"],
                DEFAULT_THEME["road_primary"],
                DEFAULT_THEME["road_default"],
            ],
        )
        self.assertEqual(styler.get_edge_widths(graph), [1.2, 1.0, 0.4])


class PosterTypographyTest(unittest.TestCase):
    def test_format_coordinates_uses_correct_directions(self):
        typography = PosterTypography(fonts=None)

        self.assertEqual(typography.format_coordinates((35.6895, 139.6917)), "35.6895° N / 139.6917° E")
        self.assertEqual(typography.format_coordinates((-33.8688, 151.2093)), "33.8688° S / 151.2093° E")
        self.assertEqual(typography.format_coordinates((37.7749, -122.4194)), "37.7749° N / 122.4194° W")


class FaceImageLoaderTest(unittest.TestCase):
    def test_load_returns_rgba_image(self):
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / "face.png"
            Image.new("RGB", (12, 8), "#ffffff").save(image_path)

            image = FaceImageLoader().load(image_path)

            self.assertEqual(image.mode, "RGBA")
            self.assertEqual(image.size, (12, 8))


class FacePosterRendererTest(unittest.TestCase):
    def test_crop_to_aspect_returns_expected_ratio(self):
        renderer = FacePosterRenderer(DEFAULT_THEME, fonts=None, size=(300, 400))
        image = Image.new("RGB", (1000, 500), "#ffffff")

        cropped = renderer.crop_to_aspect(image, 0.75)

        self.assertEqual(cropped.size, (375, 500))

    def test_render_returns_rgb_poster_at_requested_size(self):
        renderer = FacePosterRenderer(DEFAULT_THEME, fonts=None, size=(300, 400))
        image = Image.new("RGB", (120, 160), "#777777")

        poster = renderer.render(image, "Test", "Portrait")

        self.assertEqual(poster.mode, "RGB")
        self.assertEqual(poster.size, (300, 400))


if __name__ == "__main__":
    unittest.main()
