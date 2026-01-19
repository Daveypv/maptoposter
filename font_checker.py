# from fontTools.ttLib import TTFont
# import os
from font_manager import get_fonts_for_text

print(get_fonts_for_text("Tokyo"))
print(get_fonts_for_text("東京"))
print(get_fonts_for_text("서울"))
print(get_fonts_for_text("Москва"))
print(get_fonts_for_text("संस्कृत"))
