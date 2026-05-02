from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


class FaceImageLoader:
    """Loads a local face image from disk."""

    def load(self, image_path: str | Path) -> Image.Image:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Face image not found: {path}")

        return Image.open(path).convert("RGBA")


class FacePosterRenderer:
    """Creates a themed portrait poster from a face image."""

    def __init__(
        self,
        theme: dict[str, Any],
        fonts: dict[str, Path] | None,
        size: tuple[int, int] = (2400, 3200),
    ) -> None:
        self.theme = theme
        self.fonts = fonts
        self.size = size

    def create_poster(
        self,
        image_path: str | Path,
        title: str,
        subtitle: str,
        output_file: str | Path,
    ) -> None:
        print(f"\nGenerating face poster from {image_path}...")
        image = FaceImageLoader().load(image_path)
        poster = self.render(image, title, subtitle)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Saving to {output_path}...")
        poster.save(output_path)
        print(f"Done. Face poster saved as {output_path}")

    def render(self, image: Image.Image, title: str, subtitle: str) -> Image.Image:
        base, subject_mask = self._prepare_image(image)
        stylized = self._stylize_image(base, subject_mask)
        poster = Image.new("RGB", self.size, self.theme["bg"])
        poster = Image.alpha_composite(poster.convert("RGBA"), stylized).convert("RGB")

        self._add_fades(poster)
        self._draw_labels(poster, title, subtitle)
        return poster

    def _prepare_image(self, image: Image.Image) -> tuple[Image.Image, Image.Image]:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGBA")
        image = self.crop_to_aspect(image, self.size[0] / self.size[1])
        image = image.resize(self.size, Image.Resampling.LANCZOS)

        alpha = image.getchannel("A")
        if alpha.getextrema() == (255, 255):
            subject_mask = Image.new("L", self.size, 255)
        else:
            subject_mask = alpha.filter(ImageFilter.GaussianBlur(radius=1)).point(lambda value: 255 if value > 12 else 0)

        base = self._flatten_transparency(image)
        return base, subject_mask

    def crop_to_aspect(self, image: Image.Image, target_ratio: float) -> Image.Image:
        width, height = image.size
        current_ratio = width / height

        if current_ratio > target_ratio:
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            return image.crop((left, 0, left + new_width, height))

        new_height = int(width / target_ratio)
        top = max((height - new_height) // 2, 0)
        return image.crop((0, top, width, top + new_height))

    def _flatten_transparency(self, image: Image.Image) -> Image.Image:
        if image.mode != "RGBA":
            return image.convert("RGB")

        background = Image.new("RGBA", image.size, self.theme["bg"])
        background.alpha_composite(image)
        return background.convert("RGB")

    def _stylize_image(self, image: Image.Image, subject_mask: Image.Image) -> Image.Image:
        grayscale = ImageOps.grayscale(image)
        grayscale = ImageOps.autocontrast(grayscale, cutoff=2)
        smooth = grayscale.filter(ImageFilter.GaussianBlur(radius=1.2))

        artwork = Image.new("RGBA", self.size, self._hex_to_rgb(self.theme["bg"]) + (0,))
        tonal_wash = self._create_tonal_wash(smooth, subject_mask)
        feature_shadows = self._create_feature_shadows(smooth, subject_mask)
        map_texture = self._create_map_line_texture(smooth, subject_mask)
        fine_lines = self._create_tonal_contours(smooth, subject_mask)
        detail_edges = self._create_detail_edges(smooth, subject_mask)
        feature_lines = self._create_primary_feature_lines(smooth, subject_mask)
        major_lines = self._create_major_contours(smooth, subject_mask)
        silhouette = self._create_silhouette_outline(subject_mask)

        for layer in [tonal_wash, feature_shadows, map_texture, fine_lines, detail_edges, feature_lines, major_lines, silhouette]:
            artwork = Image.alpha_composite(artwork, layer)

        self._draw_accent_nodes(artwork, subject_mask)
        return artwork

    def _create_tonal_wash(self, grayscale: Image.Image, subject_mask: Image.Image) -> Image.Image:
        tones = np.asarray(grayscale, dtype=np.float32)
        mask = np.asarray(subject_mask, dtype=np.float32) / 255

        if self._is_light_theme():
            base_alpha = np.full(tones.shape, 13, dtype=np.float32)
            shadow_alpha = np.clip((155 - tones) / 155, 0, 1) * 34
            color = self.theme["road_residential"]
        else:
            base_alpha = np.full(tones.shape, 22, dtype=np.float32)
            shadow_alpha = np.clip((170 - tones) / 170, 0, 1) * 62
            color = self.theme["road_residential"]

        alpha = ((base_alpha + shadow_alpha) * mask).astype(np.uint8)
        alpha_image = Image.fromarray(alpha, mode="L").filter(ImageFilter.GaussianBlur(radius=2.2))
        return self._tinted_layer(alpha_image, color)

    def _create_feature_shadows(self, grayscale: Image.Image, subject_mask: Image.Image) -> Image.Image:
        feature_source = grayscale.filter(ImageFilter.GaussianBlur(radius=2.6))
        tones = np.asarray(feature_source, dtype=np.float32)
        mask = np.asarray(subject_mask, dtype=np.float32) / 255

        if self._is_light_theme():
            max_alpha = 82
            color = self.theme["text"]
        else:
            max_alpha = 132
            color = self.theme["water"]

        alpha = np.clip((118 - tones) / 118, 0, 1) * max_alpha
        alpha = (alpha * mask).astype(np.uint8)
        alpha_image = Image.fromarray(alpha, mode="L").filter(ImageFilter.GaussianBlur(radius=1.1))
        return self._tinted_layer(alpha_image, color)

    def _create_tonal_contours(self, grayscale: Image.Image, subject_mask: Image.Image) -> Image.Image:
        tones = np.asarray(grayscale, dtype=np.int16)
        mask = np.asarray(subject_mask, dtype=np.uint8) > 0
        alpha = np.zeros(tones.shape, dtype=np.uint8)

        for threshold in range(45, 221, 24):
            contour = np.abs(tones - threshold) <= 1
            alpha[contour & mask] = 58

        alpha_image = Image.fromarray(alpha, mode="L").filter(ImageFilter.GaussianBlur(radius=0.25))
        return self._tinted_layer(alpha_image, self.theme["road_secondary"])

    def _create_map_line_texture(self, grayscale: Image.Image, subject_mask: Image.Image) -> Image.Image:
        mask_values = np.asarray(subject_mask)
        tone_values = np.asarray(grayscale)
        ys, xs = np.where(mask_values > 0)
        layer = Image.new("RGBA", self.size, self._hex_to_rgb(self.theme["road_default"]) + (0,))
        if len(xs) == 0:
            return layer

        draw = ImageDraw.Draw(layer)
        rng = np.random.default_rng(7)
        color = self._hex_to_rgb(self.theme["road_default"]) + (36 if self._is_light_theme() else 46,)
        minor_color = self._hex_to_rgb(self.theme["road_residential"]) + (24 if self._is_light_theme() else 32,)
        directions = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 1), (2, -1)]
        line_count = 450

        for _ in range(line_count):
            index = int(rng.integers(0, len(xs)))
            x = int(xs[index])
            y = int(ys[index])
            if y > self.size[1] * 0.8:
                continue

            dx, dy = directions[int(rng.integers(0, len(directions)))]
            if rng.random() < 0.5:
                dx = -dx
            if rng.random() < 0.5:
                dy = -dy

            length = int(rng.integers(self.size[0] // 70, self.size[0] // 25))
            end_x = int(np.clip(x + dx * length, 0, self.size[0] - 1))
            end_y = int(np.clip(y + dy * length, 0, self.size[1] - 1))
            mid_x = (x + end_x) // 2
            mid_y = (y + end_y) // 2

            if mask_values[end_y, end_x] == 0 or mask_values[mid_y, mid_x] == 0:
                continue

            tone = tone_values[mid_y, mid_x]
            chosen_color = color if tone < 210 else minor_color
            width = 2 if tone < 120 and rng.random() < 0.25 else 1
            draw.line((x, y, end_x, end_y), fill=chosen_color, width=width)

            if rng.random() < 0.22:
                branch_dx, branch_dy = directions[int(rng.integers(0, len(directions)))]
                branch_length = int(length * rng.uniform(0.35, 0.8))
                branch_x = int(np.clip(mid_x + branch_dx * branch_length, 0, self.size[0] - 1))
                branch_y = int(np.clip(mid_y + branch_dy * branch_length, 0, self.size[1] - 1))
                if mask_values[branch_y, branch_x] > 0:
                    draw.line((mid_x, mid_y, branch_x, branch_y), fill=minor_color, width=1)

        return layer.filter(ImageFilter.GaussianBlur(radius=0.2))

    def _create_detail_edges(self, grayscale: Image.Image, subject_mask: Image.Image) -> Image.Image:
        edges = grayscale.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.autocontrast(edges)
        alpha = edges.point(lambda value: min(125, value * 2) if value > 24 else 0)
        alpha = self._mask_alpha(alpha, subject_mask)
        return self._tinted_layer(alpha, self.theme["road_primary"])

    def _create_primary_feature_lines(self, grayscale: Image.Image, subject_mask: Image.Image) -> Image.Image:
        feature_source = grayscale.filter(ImageFilter.GaussianBlur(radius=1.8))
        edges = feature_source.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.autocontrast(edges)
        alpha = edges.point(lambda value: min(235, value * 3) if value > 30 else 0)
        alpha = alpha.filter(ImageFilter.MaxFilter(size=3)).filter(ImageFilter.GaussianBlur(radius=0.35))
        alpha = self._mask_alpha(alpha, subject_mask)
        color = self.theme["text"] if self._is_light_theme() else self.theme["road_primary"]
        return self._tinted_layer(alpha, color)

    def _create_major_contours(self, grayscale: Image.Image, subject_mask: Image.Image) -> Image.Image:
        broad = grayscale.filter(ImageFilter.GaussianBlur(radius=4))
        edges = broad.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.autocontrast(edges)
        alpha = edges.point(lambda value: min(230, value * 3) if value > 22 else 0)
        alpha = alpha.filter(ImageFilter.MaxFilter(size=5)).filter(ImageFilter.GaussianBlur(radius=0.45))
        alpha = self._mask_alpha(alpha, subject_mask)

        glow = self._tinted_layer(alpha.filter(ImageFilter.GaussianBlur(radius=3)), self.theme["road_primary"])
        lines = self._tinted_layer(alpha, self.theme["road_motorway"])
        return Image.alpha_composite(glow, lines)

    def _create_silhouette_outline(self, subject_mask: Image.Image) -> Image.Image:
        outline = subject_mask.filter(ImageFilter.FIND_EDGES)
        outline = outline.filter(ImageFilter.MaxFilter(size=5))
        outline = outline.point(lambda value: 220 if value > 0 else 0)
        return self._tinted_layer(outline, self.theme["text"])

    def _draw_accent_nodes(self, artwork: Image.Image, subject_mask: Image.Image) -> None:
        draw = ImageDraw.Draw(artwork)
        color = self._hex_to_rgb(self.theme["road_motorway"]) + (235,)
        radius = max(4, self.size[0] // 360)
        mask_values = np.asarray(subject_mask)
        ys, xs = np.where(mask_values > 0)
        if len(xs) == 0:
            return

        rng = np.random.default_rng(42)
        candidate_indexes = rng.choice(len(xs), size=min(240, len(xs)), replace=False)
        accepted: list[tuple[int, int]] = []
        min_distance = max(95, self.size[0] // 20)
        min_distance_squared = min_distance * min_distance

        for index in candidate_indexes:
            x = int(xs[index])
            y = int(ys[index])
            if y > self.size[1] * 0.78:
                continue
            if all((x - used_x) ** 2 + (y - used_y) ** 2 >= min_distance_squared for used_x, used_y in accepted):
                accepted.append((x, y))
            if len(accepted) >= 38:
                break

        for x, y in accepted:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    def _mask_alpha(self, alpha: Image.Image, subject_mask: Image.Image) -> Image.Image:
        alpha_values = np.asarray(alpha, dtype=np.uint16)
        mask_values = np.asarray(subject_mask, dtype=np.uint16)
        masked = (alpha_values * mask_values / 255).astype(np.uint8)
        return Image.fromarray(masked, mode="L")

    def _tinted_layer(self, alpha: Image.Image, color: str) -> Image.Image:
        layer = Image.new("RGBA", self.size, self._hex_to_rgb(color) + (0,))
        layer.putalpha(alpha)
        return layer

    def _is_light_theme(self) -> bool:
        red, green, blue = self._hex_to_rgb(self.theme["bg"])
        luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255
        return luminance > 0.58

    def _add_vignette(self, poster: Image.Image) -> None:
        width, height = poster.size
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        xv, yv = np.meshgrid(x, y)
        distance = np.sqrt((xv * 0.85) ** 2 + yv**2)
        alpha = np.clip((distance - 0.45) / 0.55, 0, 1) * 115

        vignette = Image.new("RGBA", poster.size, self._hex_to_rgb(self.theme["bg"]) + (0,))
        vignette.putalpha(Image.fromarray(alpha.astype(np.uint8), mode="L"))
        poster.paste(Image.alpha_composite(poster.convert("RGBA"), vignette).convert("RGB"))

    def _add_fades(self, poster: Image.Image) -> None:
        width, height = poster.size
        fade_height = int(height * 0.24)
        color = self._hex_to_rgb(self.theme["gradient_color"])

        for top in [True, False]:
            fade = Image.new("RGBA", (width, fade_height), color + (0,))
            if top:
                alpha_values = np.linspace(190, 0, fade_height, dtype=np.uint8)
                y = 0
            else:
                alpha_values = np.linspace(0, 210, fade_height, dtype=np.uint8)
                y = height - fade_height

            alpha = np.repeat(alpha_values[:, None], width, axis=1)
            fade.putalpha(Image.fromarray(alpha, mode="L"))
            poster.paste(
                Image.alpha_composite(poster.crop((0, y, width, y + fade_height)).convert("RGBA"), fade).convert("RGB"),
                (0, y),
            )

    def _draw_labels(self, poster: Image.Image, title: str, subtitle: str) -> None:
        draw = ImageDraw.Draw(poster)
        title_font = self._font("bold", 155)
        subtitle_font = self._font("light", 66)
        detail_font = self._font("regular", 38)
        text_color = self._hex_to_rgb(self.theme["text"])

        spaced_title = "  ".join(title.upper())
        self._draw_centered(draw, spaced_title, title_font, poster.width // 2, int(poster.height * 0.835), text_color)
        self._draw_centered(draw, subtitle.upper(), subtitle_font, poster.width // 2, int(poster.height * 0.89), text_color)

        line_y = int(poster.height * 0.865)
        draw.line((int(poster.width * 0.39), line_y, int(poster.width * 0.61), line_y), fill=text_color, width=3)

        detail = "THEMED PORTRAIT STUDY"
        self._draw_centered(draw, detail, detail_font, poster.width // 2, int(poster.height * 0.935), text_color)

    def _draw_centered(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
        x: int,
        y: int,
        fill: tuple[int, int, int],
    ) -> None:
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        draw.text((x - width / 2, y - height / 2), text, font=font, fill=fill)

    def _font(self, weight: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        if self.fonts and weight in self.fonts:
            return ImageFont.truetype(str(self.fonts[weight]), size=size)
        return ImageFont.load_default()

    def _hex_to_rgb(self, value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))
