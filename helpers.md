# Helpers Guide

This project now keeps the reusable code inside the `maptoposter/` folder. The command `python create_map_poster.py ...` still works, but the real work is done by classes.

## What is a class?

A class is a reusable template for related code. You create an object from a class, then call methods on that object.

Example:

```python
from maptoposter.themes import ThemeManager

theme_manager = ThemeManager("themes")
theme = theme_manager.load_theme("noir")
```

Here `ThemeManager` is the class. `theme_manager` is an object. `load_theme()` is a method.

## `ProjectPaths`

File: `maptoposter/config.py`

This class stores the folder names used by the project.

Methods and properties:

- `themes_dir`: returns the path to the `themes/` folder.
- `fonts_dir`: returns the path to the `fonts/` folder.
- `posters_dir`: returns the path to the `posters/` folder.

Usage:

```python
from maptoposter.config import ProjectPaths

paths = ProjectPaths()
print(paths.themes_dir)
```

## `FontManager`

File: `maptoposter/fonts.py`

This class checks whether the Roboto font files exist.

Methods:

- `load_fonts()`: returns a dictionary with `bold`, `regular`, and `light` font paths. Returns `None` if a font is missing.

Usage:

```python
from maptoposter.fonts import FontManager

fonts = FontManager("fonts").load_fonts()
```

## `ThemeManager`

File: `maptoposter/themes.py`

This class reads theme JSON files.

Methods:

- `get_available_themes()`: returns names like `noir`, `sunset`, and `blueprint`.
- `load_theme(theme_name)`: loads one theme and returns it as a Python dictionary.
- `get_theme_details(theme_name)`: returns the display name and description for one theme.

Usage:

```python
from maptoposter.themes import ThemeManager

manager = ThemeManager("themes")
print(manager.get_available_themes())
theme = manager.load_theme("sunset")
```

## `OutputFileManager`

File: `maptoposter/output.py`

This class creates filenames for generated posters.

Methods:

- `generate_filename(city, theme_name)`: creates the `posters/` folder if needed and returns a path like `posters/tokyo_noir_20260502_153000.png`.
- `generate_face_filename(title, theme_name)`: creates a face poster path like `posters/david_noir_face_20260502_153000.png`.
- `_slugify(value)`: turns text into safe filename text. The underscore means it is meant for internal class use.

Usage:

```python
from maptoposter.output import OutputFileManager

output = OutputFileManager("posters").generate_filename("Tokyo", "noir")
```

Face poster example:

```python
from maptoposter.output import OutputFileManager

output = OutputFileManager("posters").generate_face_filename("David", "noir")
```

## `GeocodingService`

File: `maptoposter/geocoding.py`

This class asks Nominatim for city coordinates.

Methods:

- `get_coordinates(city, country)`: returns `(latitude, longitude)`.

Usage:

```python
from maptoposter.geocoding import GeocodingService

coords = GeocodingService().get_coordinates("Tokyo", "Japan")
```

## `MapData`

File: `maptoposter/map_data.py`

This is a small data class. It stores the map data after downloading.

Attributes:

- `graph`: the street network.
- `water`: water features, or `None`.
- `parks`: park features, or `None`.

You usually do not create this yourself. `MapDataFetcher` creates it.

## `MapDataFetcher`

File: `maptoposter/map_data.py`

This class downloads data from OpenStreetMap through OSMnx.

Methods:

- `fetch(point, dist)`: downloads roads, water, and parks around a coordinate.

Usage:

```python
from maptoposter.map_data import MapDataFetcher

data = MapDataFetcher().fetch((35.6895, 139.6917), 12000)
```

## `RoadStyler`

File: `maptoposter/styling.py`

This class decides road colors and widths.

Methods:

- `get_edge_colors(graph)`: returns one color for each road.
- `get_edge_widths(graph)`: returns one line width for each road.
- `color_for_highway(highway)`: returns a color for one road type.
- `width_for_highway(highway)`: returns a width for one road type.

Usage:

```python
from maptoposter.styling import RoadStyler
from maptoposter.themes import ThemeManager

theme = ThemeManager("themes").load_theme("noir")
styler = RoadStyler(theme)
```

## `GradientPainter`

File: `maptoposter/rendering.py`

This class draws the top and bottom fade over the map.

Methods:

- `create_gradient_fade(ax, color, location, zorder)`: draws a fade on a matplotlib axis.

You normally let `MapPosterRenderer` use this for you.

## `PosterTypography`

File: `maptoposter/rendering.py`

This class draws the city name, country, coordinates, and OpenStreetMap credit.

Methods:

- `draw_labels(ax, city, country, point, theme)`: draws all text on the poster.
- `format_coordinates(point)`: turns coordinates into readable text.

Usage:

```python
from maptoposter.rendering import PosterTypography

text = PosterTypography(None).format_coordinates((37.7749, -122.4194))
print(text)
```

## `FaceImageLoader`

File: `maptoposter/face.py`

This class loads a local image file for the face poster feature.

Methods:

- `load(image_path)`: opens an image from disk and returns a Pillow image in `RGBA` mode.

Usage:

```python
from maptoposter.face import FaceImageLoader

image = FaceImageLoader().load("images/a.png")
```

## `FacePosterRenderer`

File: `maptoposter/face.py`

This class creates a poster from a face image. It uses the same theme colors as the map posters, but instead of filling the whole photo, it draws contour lines over the theme background. This makes the portrait feel closer to a city map: lots of fine linework, stronger feature outlines, and small accent nodes.

Methods:

- `create_poster(image_path, title, subtitle, output_file)`: loads the image, creates the poster, and saves it.
- `render(image, title, subtitle)`: creates a poster from an image that is already loaded.
- `crop_to_aspect(image, target_ratio)`: center-crops the image to match the poster shape.
- `_prepare_image(image)`: flattens transparency, crops, resizes, and converts the image before styling.
- `_stylize_image(image, subject_mask)`: creates all contour artwork and clips it to the person.
- `_create_tonal_contours(grayscale, subject_mask)`: draws many fine contour lines from light and dark areas.
- `_create_detail_edges(grayscale, subject_mask)`: draws sharper face and clothing details.
- `_create_major_contours(grayscale, subject_mask)`: draws the stronger accent lines.
- `_create_silhouette_outline(subject_mask)`: draws the outside shape of the person.
- `_draw_accent_nodes(artwork, subject_mask)`: adds small colored map-point dots inside the person.
- `_mask_alpha(alpha, subject_mask)`: clips a line layer so it only appears inside the person.
- `_tinted_layer(alpha, color)`: creates a transparent colored layer from an alpha mask.
- `_add_vignette(poster)`: darkens or softens the edges of the poster.
- `_add_fades(poster)`: adds top and bottom fades like the map poster.
- `_draw_labels(poster, title, subtitle)`: draws the title, subtitle, divider line, and small detail text.

Usage:

```python
from maptoposter.face import FacePosterRenderer
from maptoposter.themes import ThemeManager

theme = ThemeManager("themes").load_theme("noir")
renderer = FacePosterRenderer(theme=theme, fonts=None)
renderer.create_poster("images/a.png", "A", "Portrait", "posters/a_face.png")
```

## `MapPosterRenderer`

File: `maptoposter/rendering.py`

This class creates the final image.

Methods:

- `create_poster(city, country, point, dist, output_file)`: downloads map data and renders the poster.
- `render(city, country, point, map_data, output_file)`: renders a poster from already downloaded data.

Usage:

```python
from maptoposter.rendering import MapPosterRenderer
from maptoposter.themes import ThemeManager

theme = ThemeManager("themes").load_theme("noir")
renderer = MapPosterRenderer(theme=theme, fonts=None)
renderer.create_poster("Tokyo", "Japan", (35.6895, 139.6917), 12000, "poster.png")
```

## `MapPosterApp`

File: `maptoposter/app.py`

This is the high-level class used by the command-line script.

Methods:

- `create_city_poster(city, country, theme_name, distance)`: runs the full process.
- `create_face_poster(image_path, theme_name, title, subtitle)`: creates a poster from a local face image.
- `list_themes()`: prints all themes.
- `has_theme(theme_name)`: returns `True` if a theme exists.
- `get_available_themes()`: returns all theme names.

Usage:

```python
from maptoposter import MapPosterApp

app = MapPosterApp()
app.create_city_poster("Tokyo", "Japan", "japanese_ink", 15000)
app.create_face_poster("images/a.png", "noir", "A", "Portrait")
```

## Face Poster Command

Create a face poster from the test image:

```bash
python create_map_poster.py --face-image images/a.png --theme noir --face-title "A" --face-subtitle "Portrait"
```

Hyphenated theme names also work. For example, `neon-cyberpunk` is treated as `neon_cyberpunk`.

Later, URL support can be added by creating another loader class or expanding `FaceImageLoader`. The renderer does not care where the image came from; it only needs a loaded image.
