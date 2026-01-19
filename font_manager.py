from config import FONT_FAMILIES
from fontTools.ttLib import TTFont
import os

FONTS_DIR = "fonts"
# FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

def detect_script(text: str) -> str:
    for char in text:
        code = ord(char)

        # Japanese (Hiragana, Katakana, Kanji)
        if (
            0x3040 <= code <= 0x30FF or
            0x4E00 <= code <= 0x9FFF
        ):
            return "japanese"

        # Devanagari (Sanskrit, Hindi)
        if 0x0900 <= code <= 0x097F:
            return "devanagari"

        # Hangul (Korean)
        if 0xAC00 <= code <= 0xD7AF:
            return "hangul"

        # Cyrillic (Russian)
        if 0x0400 <= code <= 0x04FF:
            return "cyrillic"

    return "latin"


def load_fonts_for_script(script: str) -> dict:
    if script not in FONT_FAMILIES:
        script = "latin"

    fonts = {}
    for weight, relative_path in FONT_FAMILIES[script].items():
        path = os.path.join(FONTS_DIR, relative_path)

        if os.path.exists(path):
            fonts[weight] = path

    if "regular" not in fonts:
        raise FileNotFoundError(f"No usable fonts found for script: {script}")

    return fonts


def get_fonts_for_text(text: str) -> dict:
    return load_fonts_for_script(detect_script(text))
