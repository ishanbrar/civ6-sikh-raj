#!/usr/bin/env python3
"""Generate Civ VI-compatible DDS icons and loading screen art for the Sikh Empire mod."""

import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

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


def khanda_mask(image: Image.Image) -> Image.Image:
    gray = image.convert("L")
    return gray.point(lambda p: 255 if p < 150 else 0)


def make_white_khanda(size: int) -> Image.Image:
    src = Image.open(ART / "Khanda_Source.png").convert("RGBA")
    src = src.crop(src.getbbox())
    fitted = fit_square(src, int(size * 0.78))
    mask = khanda_mask(fitted)
    symbol = Image.new("RGBA", fitted.size, (255, 255, 255, 0))
    symbol.putalpha(mask)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = (size - fitted.width) // 2
    canvas.paste(symbol, (offset, offset), symbol)
    return apply_circle(canvas, 0.02)


def make_colored_khanda(size: int) -> Image.Image:
    white = make_white_khanda(size)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(SAFFRON, circle_mask(size, 0.02))
    # Dark khanda on saffron disc for the 45px default icon.
    src = Image.open(ART / "Khanda_Source.png").convert("RGBA")
    src = src.crop(src.getbbox())
    fitted = fit_square(src, int(size * 0.62))
    px = fitted.load()
    symbol = Image.new("RGBA", fitted.size, (0, 0, 0, 0))
    spx = symbol.load()
    for y in range(fitted.height):
        for x in range(fitted.width):
            r, g, b, a = px[x, y]
            if r < 150 and g < 150 and b < 150:
                spx[x, y] = (20, 20, 20, 255)
    offset = (size - fitted.width) // 2
    canvas.paste(symbol, (offset, offset), symbol)
    return apply_circle(canvas, 0.02)


def make_leader_icon(size: int) -> Image.Image:
    src = Image.open(ART / "Leader_RanjitSingh_256.png").convert("RGBA")
    inner = fit_square(src, max(1, int(size * 0.88)))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    offset = (size - inner.width) // 2
    canvas.paste(inner, (offset, offset), inner)
    return apply_circle(canvas, 0.03)


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

    for size in civ_sizes:
        icon = make_white_khanda(size) if size != 45 else make_colored_khanda(size)
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
