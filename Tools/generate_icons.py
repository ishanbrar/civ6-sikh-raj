#!/usr/bin/env python3
"""Generate Civ VI-compatible DDS icons and loading screen art for the Sikh Empire mod."""

import struct
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ART = Path(__file__).resolve().parents[1] / "Art"
SAFFRON = (255, 153, 51, 255)


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
    src = Image.open(ART / "Leader_RanjitSingh.png").convert("RGBA")
    crop = src.crop((int(src.width * 0.20), int(src.height * 0.02), int(src.width * 0.84), int(src.height * 0.56)))
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

    save_dds(ART / "Leader_RanjitSingh_Background.dds", make_loading_background())
    save_dds(ART / "Leader_RanjitSingh_LoadingForeground.dds", make_loading_foreground())

    make_loading_background().save(ART / "Leader_RanjitSingh_Background.png")
    make_loading_foreground().save(ART / "Leader_RanjitSingh_LoadingForeground.png")

    print("Generated circular civ/leader icons and loading screen art.")


if __name__ == "__main__":
    main()
