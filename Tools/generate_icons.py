#!/usr/bin/env python3
"""Generate Civ VI-compatible DDS icons and loading screen art for the Sikh Empire mod."""

import struct
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

ART = Path(__file__).resolve().parents[1] / "Art"
SAFFRON = (255, 153, 51, 255)
GOLD = (235, 178, 58, 255)
GOLD_LIGHT = (255, 214, 105, 255)
DARK_BLUE = (6, 35, 53, 255)
DEEP_TEAL = (8, 57, 55, 255)
DEEP_GREEN = (8, 73, 49, 255)
PURPLE = (44, 20, 57, 255)
BLACK = (14, 14, 13, 255)
CREAM = (246, 235, 202, 255)


def save_dds(path: Path, image: Image.Image) -> None:
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    width, height = image.size
    pitch = width * 4
    header = bytearray(128)
    struct.pack_into("<4s", header, 0, b"DDS ")
    struct.pack_into("<I", header, 4, 124)
    struct.pack_into("<I", header, 8, 0x100F)
    struct.pack_into("<I", header, 12, height)
    struct.pack_into("<I", header, 16, width)
    struct.pack_into("<I", header, 20, pitch)
    struct.pack_into("<I", header, 76, 0x1000)
    struct.pack_into("<I", header, 80, 32)
    struct.pack_into("<I", header, 84, 0x41)
    struct.pack_into("<I", header, 88, 32)
    struct.pack_into("<I", header, 92, 0x00FF0000)
    struct.pack_into("<I", header, 96, 0x0000FF00)
    struct.pack_into("<I", header, 100, 0x000000FF)
    struct.pack_into("<I", header, 104, 0xFF000000)
    path.write_bytes(header + image.tobytes("raw", "BGRA"))


def circle_mask(size: int, inset: float = 0.04) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    pad = max(1, int(size * inset))
    draw.ellipse((pad, pad, size - pad - 1, size - pad - 1), fill=255)
    return mask.filter(ImageFilter.GaussianBlur(0.6))


def apply_circle(image: Image.Image, inset: float = 0.04) -> Image.Image:
    size = image.size[0]
    mask = circle_mask(size, inset)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(image, (0, 0), mask)
    return out


def fit_square(image: Image.Image, size: int) -> Image.Image:
    image = image.convert("RGBA")
    scale = min(size / image.width, size / image.height)
    new_w = max(1, int(image.width * scale))
    new_h = max(1, int(image.height * scale))
    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(resized, ((size - new_w) // 2, (size - new_h) // 2), resized)
    return canvas


def scale_icon(image: Image.Image, size: int) -> Image.Image:
    return image.resize((size, size), Image.Resampling.LANCZOS)


def draw_badge_base(size: int, color: tuple[int, int, int, int]) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = circle_mask(size, 0.04)
    disc = Image.new("RGBA", (size, size), color)
    canvas.paste(disc, (0, 0), mask)

    # Subtle centered glow keeps the badges from reading as flat squares in Civ's UI.
    glow = Image.new("L", (size, size), 0)
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((int(size * 0.08), int(size * 0.08), int(size * 0.92), int(size * 0.92)), fill=125)
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.12))
    glow = ImageChops.multiply(glow, mask)
    light = Image.new("RGBA", (size, size), (255, 202, 96, 42))
    canvas = Image.composite(light, canvas, glow)

    draw = ImageDraw.Draw(canvas)
    outer = int(size * 0.10)
    draw.ellipse((outer, outer, size - outer, size - outer), outline=GOLD, width=max(3, size // 26))
    inner = int(size * 0.16)
    draw.ellipse((inner, inner, size - inner, size - inner), outline=(239, 196, 90, 160), width=max(2, size // 70))
    return canvas


def paste_khanda(canvas: Image.Image, center: tuple[int, int], symbol_size: int, color: tuple[int, int, int, int] = BLACK) -> None:
    mask = khanda_symbol_mask(symbol_size)
    symbol = Image.new("RGBA", (symbol_size, symbol_size), color)
    symbol.putalpha(mask)
    canvas.paste(symbol, (center[0] - symbol_size // 2, center[1] - symbol_size // 2), symbol)


def draw_kirpan(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], width: int) -> None:
    draw.line((start, end), fill=(56, 45, 32, 255), width=width + 6)
    draw.line((start, end), fill=(226, 236, 231, 255), width=width)
    draw.line((start[0] + 5, start[1] - 4, end[0] + 5, end[1] - 4), fill=(255, 255, 255, 180), width=max(1, width // 3))
    draw.ellipse((start[0] - width, start[1] - width, start[0] + width, start[1] + width), fill=GOLD_LIGHT)


def bold_font(size: int):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_miri_piri_icon(size: int = 256) -> Image.Image:
    icon = draw_badge_base(size, DARK_BLUE)
    draw = ImageDraw.Draw(icon)
    draw_kirpan(draw, (int(size * 0.29), int(size * 0.78)), (int(size * 0.70), int(size * 0.24)), max(5, size // 22))
    draw_kirpan(draw, (int(size * 0.71), int(size * 0.78)), (int(size * 0.30), int(size * 0.24)), max(5, size // 22))
    draw.ellipse((int(size * 0.34), int(size * 0.34), int(size * 0.66), int(size * 0.66)), fill=SAFFRON, outline=GOLD_LIGHT, width=max(3, size // 38))
    paste_khanda(icon, (size // 2, size // 2), int(size * 0.23), BLACK)
    return icon


def make_chardi_icon(size: int = 256) -> Image.Image:
    return make_civ_khanda(size)


def make_nihang_icon(size: int = 256) -> Image.Image:
    icon = draw_badge_base(size, DARK_BLUE)
    draw = ImageDraw.Draw(icon)
    draw.polygon(
        [(int(size * 0.28), int(size * 0.77)), (int(size * 0.50), int(size * 0.28)), (int(size * 0.72), int(size * 0.77))],
        fill=(18, 45, 69, 255),
        outline=GOLD,
    )
    draw.ellipse((int(size * 0.32), int(size * 0.26), int(size * 0.68), int(size * 0.45)), outline=GOLD_LIGHT, width=max(3, size // 34))
    draw.polygon(
        [(int(size * 0.24), int(size * 0.28)), (int(size * 0.50), int(size * 0.14)), (int(size * 0.76), int(size * 0.28)), (int(size * 0.50), int(size * 0.24))],
        fill=(240, 198, 81, 255),
        outline=GOLD_LIGHT,
    )
    draw_kirpan(draw, (int(size * 0.22), int(size * 0.80)), (int(size * 0.82), int(size * 0.23)), max(6, size // 18))
    return icon


def make_misldar_icon(size: int = 256) -> Image.Image:
    icon = draw_badge_base(size, DEEP_TEAL)
    draw = ImageDraw.Draw(icon)
    draw.polygon(
        [(int(size * 0.21), int(size * 0.70)), (int(size * 0.44), int(size * 0.48)), (int(size * 0.68), int(size * 0.57)), (int(size * 0.84), int(size * 0.72)), (int(size * 0.64), int(size * 0.78)), (int(size * 0.49), int(size * 0.74)), (int(size * 0.35), int(size * 0.80))],
        fill=(29, 24, 19, 255),
        outline=(111, 87, 46, 255),
    )
    draw.ellipse((int(size * 0.42), int(size * 0.23), int(size * 0.58), int(size * 0.39)), fill=(163, 96, 52, 255))
    draw.polygon(
        [(int(size * 0.35), int(size * 0.64)), (int(size * 0.50), int(size * 0.40)), (int(size * 0.63), int(size * 0.64))],
        fill=(24, 57, 79, 255),
        outline=(12, 24, 31, 255),
    )
    draw.arc((int(size * 0.25), int(size * 0.14), int(size * 0.76), int(size * 0.44)), 190, 350, fill=GOLD_LIGHT, width=max(4, size // 28))
    draw_kirpan(draw, (int(size * 0.24), int(size * 0.80)), (int(size * 0.82), int(size * 0.27)), max(6, size // 19))
    return icon


def make_defender_icon(size: int = 256) -> Image.Image:
    icon = draw_badge_base(size, PURPLE)
    draw = ImageDraw.Draw(icon)
    draw.arc((int(size * 0.22), int(size * 0.20), int(size * 0.82), int(size * 0.78)), 205, 335, fill=GOLD, width=max(8, size // 18))
    draw.text((int(size * 0.12), int(size * 0.09)), "+5", font=bold_font(size // 5), fill=CREAM, stroke_width=max(1, size // 70), stroke_fill=(20, 10, 26, 255))
    draw.ellipse((int(size * 0.39), int(size * 0.39), int(size * 0.63), int(size * 0.63)), fill=SAFFRON, outline=GOLD_LIGHT, width=max(2, size // 60))
    paste_khanda(icon, (int(size * 0.51), int(size * 0.51)), int(size * 0.16), BLACK)
    return icon


def make_gurdwara_icon(size: int = 256) -> Image.Image:
    icon = draw_badge_base(size, DEEP_GREEN)
    draw = ImageDraw.Draw(icon)
    base_y = int(size * 0.72)
    draw.rectangle((int(size * 0.25), int(size * 0.45), int(size * 0.75), base_y), fill=CREAM, outline=GOLD_LIGHT, width=max(3, size // 45))
    draw.rounded_rectangle((int(size * 0.34), int(size * 0.30), int(size * 0.66), int(size * 0.55)), radius=size // 12, fill=(239, 187, 75, 255), outline=GOLD_LIGHT, width=max(3, size // 45))
    draw.rectangle((int(size * 0.33), int(size * 0.57), int(size * 0.67), int(size * 0.61)), fill=GOLD_LIGHT)
    for x in (0.29, 0.71):
        cx = int(size * x)
        draw.rectangle((cx - size // 18, int(size * 0.42), cx + size // 18, base_y), fill=CREAM, outline=GOLD_LIGHT, width=max(2, size // 64))
        draw.ellipse((cx - size // 18, int(size * 0.33), cx + size // 18, int(size * 0.45)), fill=(248, 203, 89, 255), outline=GOLD_LIGHT)
        draw.polygon([(cx, int(size * 0.30)), (cx + size // 9, int(size * 0.34)), (cx, int(size * 0.38))], fill=SAFFRON)
    draw.polygon([(size // 2, int(size * 0.23)), (int(size * 0.61), int(size * 0.28)), (size // 2, int(size * 0.33))], fill=SAFFRON)
    for x in (0.35, 0.50, 0.65):
        draw.rectangle((int(size * x) - size // 18, int(size * 0.61), int(size * x) + size // 18, base_y), fill=DARK_BLUE, outline=GOLD_LIGHT)
    return icon


def write_atlas_set(prefix: str, sizes: list[int], makers: list) -> None:
    for size in sizes:
        atlas = Image.new("RGBA", (size * len(makers), size), (0, 0, 0, 0))
        for index, maker in enumerate(makers):
            atlas.paste(scale_icon(maker(256), size), (index * size, 0))
        atlas.save(ART / f"{prefix}_{size}.png")
        save_dds(ART / f"{prefix}_{size}.dds", atlas)


def khanda_symbol_mask(size: int) -> Image.Image:
    src = Image.open(ART / "Khanda_Source.png").convert("RGBA")
    bg = Image.new("RGBA", src.size, src.getpixel((0, 0)))
    diff = ImageChops.difference(src, bg).convert("L")
    mask = diff.point(lambda p: 255 if p > 40 else 0)
    bbox = mask.getbbox()
    if bbox:
        mask = mask.crop(bbox)
    fitted = fit_square(ImageOps.colorize(mask, black="black", white="white").convert("RGBA"), size)
    return fitted.convert("L").point(lambda p: 255 if p > 10 else 0)


def make_civ_khanda(size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    disc = Image.new("RGBA", (size, size), SAFFRON)
    canvas.paste(disc, (0, 0), circle_mask(size, 0.02))

    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_width = max(1, size // 18)
    pad = max(1, int(size * 0.08))
    ring_draw.ellipse((pad, pad, size - pad - 1, size - pad - 1), outline=(246, 199, 83, 255), width=ring_width)
    canvas.alpha_composite(ring)

    symbol_size = max(1, int(size * 0.58))
    mask = khanda_symbol_mask(symbol_size)
    symbol = Image.new("RGBA", (symbol_size, symbol_size), (16, 16, 16, 255))
    symbol.putalpha(mask)
    offset = (size - symbol_size) // 2
    canvas.paste(symbol, (offset, offset), symbol)
    return apply_circle(canvas, 0.02)


def make_leader_icon(size: int) -> Image.Image:
    src = Image.open(ART / "Leader_RanjitSingh_Headshot_Source.png").convert("RGBA")
    crop = src.crop((int(src.width * 0.23), int(src.height * 0.00), int(src.width * 0.83), int(src.height * 0.68)))
    inner = fit_square(crop, max(1, int(size * 0.88)))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = (size - inner.width) // 2
    canvas.paste(inner, (offset, offset), inner)
    canvas = apply_circle(canvas, 0.04)

    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ring_draw = ImageDraw.Draw(ring)
    ring_width = max(1, size // 13)
    pad = max(1, int(size * 0.07))
    ring_draw.ellipse((pad, pad, size - pad - 1, size - pad - 1), outline=(234, 174, 55, 255), width=ring_width)
    ring_draw.ellipse((pad + ring_width, pad + ring_width, size - pad - ring_width - 1, size - pad - ring_width - 1), outline=(83, 54, 24, 230), width=max(1, ring_width // 2))
    canvas.alpha_composite(ring)
    return apply_circle(canvas, 0.02)


def make_loading_background() -> Image.Image:
    w, h = 1920, 1080
    bg = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / (h - 1)
        r = int(168 - 35 * t)
        g = int(98 - 25 * t)
        b = int(42 - 10 * t)
        draw.line((0, y, w, y), fill=(r, g, b))
    vig = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse((-w * 0.1, -h * 0.15, w * 1.1, h * 1.1), fill=210)
    vig = vig.filter(ImageFilter.GaussianBlur(90))
    dark = Image.new("RGB", (w, h), (35, 20, 8))
    return Image.composite(bg, dark, vig).convert("RGBA")


def make_loading_foreground() -> Image.Image:
    w, h = 1920, 1080
    portrait = Image.open(ART / "Leader_RanjitSingh.png").convert("RGBA")
    target_h = int(h * 0.98)
    scale = target_h / portrait.height
    target_w = int(portrait.width * scale)
    portrait = portrait.resize((target_w, target_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = w - target_w + int(w * 0.03)
    y = h - target_h
    canvas.paste(portrait, (x, y), portrait)
    return canvas


def make_leader_portrait() -> Image.Image:
    src = Image.open(ART / "Leader_RanjitSingh_Generated.png").convert("RGBA")
    target_w, target_h = 768, 1024
    src_ratio = src.width / src.height
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        crop_w = int(src.height * target_ratio)
        left = int(src.width * 0.53 - crop_w / 2)
        left = max(0, min(left, src.width - crop_w))
        src = src.crop((left, 0, left + crop_w, src.height))
    else:
        crop_h = int(src.width / target_ratio)
        top = max(0, min(int(src.height * 0.02), src.height - crop_h))
        src = src.crop((0, top, src.width, top + crop_h))
    return src.resize((target_w, target_h), Image.Resampling.LANCZOS)


def write_icon_set(prefix: str, sizes: list[int], maker) -> None:
    for size in sizes:
        icon = maker(size)
        png = ART / f"{prefix}_{size}.png"
        dds = ART / f"{prefix}_{size}.dds"
        icon.save(png)
        save_dds(dds, icon)


def main() -> None:
    civ_sizes = [22, 30, 32, 36, 38, 44, 45, 48, 50, 64, 80, 128, 200, 256]
    leader_sizes = [32, 45, 48, 50, 55, 64, 80, 256]
    feature_sizes = [32, 38, 50, 80, 256]

    portrait = make_leader_portrait()
    portrait.save(ART / "Leader_RanjitSingh.png")
    portrait.resize((256, 256), Image.Resampling.LANCZOS).save(ART / "Leader_RanjitSingh_256.png")
    save_dds(ART / "Leader_RanjitSingh.dds", portrait)
    save_dds(ART / "Leader_RanjitSingh_256.dds", portrait.resize((256, 256), Image.Resampling.LANCZOS))

    for size in civ_sizes:
        icon = make_civ_khanda(size)
        icon.save(ART / f"Sikh_Civ_{size}.png")
        save_dds(ART / f"Sikh_Civ_{size}.dds", icon)

    write_icon_set("Sikh_Leader", leader_sizes, make_leader_icon)
    write_atlas_set("Sikh_Abilities", feature_sizes, [make_miri_piri_icon, make_chardi_icon, make_misldar_icon, make_defender_icon])
    write_atlas_set("Sikh_Units", feature_sizes, [make_nihang_icon, make_misldar_icon])
    write_atlas_set("Sikh_Buildings", feature_sizes, [make_gurdwara_icon])

    save_dds(ART / "Leader_RanjitSingh_Background.dds", make_loading_background())
    save_dds(ART / "Leader_RanjitSingh_LoadingForeground.dds", make_loading_foreground())

    make_loading_background().save(ART / "Leader_RanjitSingh_Background.png")
    make_loading_foreground().save(ART / "Leader_RanjitSingh_LoadingForeground.png")

    print("Generated circular civ/leader icons and loading screen art.")


if __name__ == "__main__":
    main()
