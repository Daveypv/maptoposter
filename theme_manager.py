import os
import random
import colorsys
import json
from config import THEMES_DIR

def get_available_themes():
    """
    Scans the themes directory and returns a list of available theme names.
    """
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
        return []

    themes = []
    for file in sorted(os.listdir(THEMES_DIR)):
        if file.endswith('.json'):
            theme_name = file[:-5]  # Remove .json extension
            themes.append(theme_name)
    return themes

def load_theme(theme_name="feature_based"):
    """
    Load theme from JSON file in themes directory.
    """
    theme_file = os.path.join(THEMES_DIR, f"{theme_name}.json")

    if not os.path.exists(theme_file):
        print(f"⚠ Theme file '{theme_file}' not found. Using default feature_based theme.")
        # Fallback to embedded default theme
        return {
            "name": "Feature-Based Shading",
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
            "road_default": "#3A3A3A"
        }

    with open(theme_file, 'r') as f:
        theme = json.load(f)
        print(f"✓ Loaded theme: {theme.get('name', theme_name)}")
        if 'description' in theme:
            print(f"  {theme['description']}")
        return theme


## Random Color Generators
# Neon characteristics
def random_neon_color():
    hue = random.random()                   # Hue: 0–1
    saturation = random.uniform(0.8, 1.0)   # Saturation: high
    value = random.uniform(0.8, 1.0)        # Brightness: high
    return hsv_to_hex(hue, saturation, value)

## Dark color generator for backgrounds
def random_dark_color():
    r = random.randint(0, 40)
    g = random.randint(0, 40)
    b = random.randint(0, 40)
    return f"#{r:02X}{g:02X}{b:02X}"

def random_hex_color():
    return "#{:06X}".format(random.randint(0, 0xFFFFFF))

# Pastel characteristics
# Hue (H): (0–360°)
# Saturation (S): low to medium → soft color
# Value / Lightness (V): high → bright, airy
# | Channel            | Range                       |
# | Hue                | `0.0 – 1.0` (full spectrum) |
# | Saturation         | **`0.20 – 0.45`**           |
# | Value (brightness) | **`0.85 – 1.0`**            |
def random_pastel_color():
    hue = random.random()                   # 0.0 – 1.0
    saturation = random.uniform(0.2, 0.45)  # low saturation
    value = random.uniform(0.85, 1.0)       # high brightness
    return hsv_to_hex(hue, saturation, value)

def pastel_color_from_base_hue(base_hue):
    hue = base_hue + random.uniform(-0.05, 0.05)
    saturation = random.uniform(0.25, 0.4)
    value = random.uniform(0.88, 1.0)
    return hsv_to_hex(hue, saturation, value)

def hsv_to_hex(hue: float, saturation: float, value: float) -> str:
    """
    Convert HSV values (0–1 range) to a hex color string.
    """
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"

def generate_pastel_theme():
    return {
        "bg": "#F8FAFC",
        "text": "#4A5568",
        "gradient_color": random_pastel_color(),
        "water": random_pastel_color(),
        "parks": random_pastel_color(),
        "road_motorway": random_pastel_color(),
        "road_primary": random_pastel_color(),
        "road_secondary": random_pastel_color(),
        "road_tertiary": random_pastel_color(),
        "road_residential": random_pastel_color(),
        "road_default": random_pastel_color(),
    }

def generate_cohesive_pastel_theme():
    base_hue = random.random()
    return {
        "bg": "#F8FAFC",
        "text": "#4A5568",
        "gradient_color": pastel_color_from_base_hue(base_hue),
        "water": pastel_color_from_base_hue(base_hue),
        "parks": pastel_color_from_base_hue(base_hue),
        "road_motorway": pastel_color_from_base_hue(base_hue),
        "road_primary": pastel_color_from_base_hue(base_hue),
        "road_secondary": pastel_color_from_base_hue(base_hue),
        "road_tertiary": pastel_color_from_base_hue(base_hue),
        "road_residential": pastel_color_from_base_hue(base_hue),
        "road_default": pastel_color_from_base_hue(base_hue),
    }

def generate_neon_theme():
    return {
        "bg": random_dark_color(),
        "text": "#FFFFFF",
        "road_motorway": random_neon_color(),
        "road_primary": random_neon_color(),
        "road_secondary": random_neon_color(),
        "road_tertiary": random_neon_color(),
        "road_residential": random_neon_color(),
        "water": random_neon_color(),
        "parks": random_neon_color(),
    }
