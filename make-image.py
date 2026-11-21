#!/usr/bin/env python3
"""Draw the NIMBARA poster: a green cliff island floating above a sea
of clouds at golden hour. Deterministic: fixed coordinates, no random
numbers, no network access. Run: python3 make-image.py -> entry.png"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1024
OUT = "entry.png"

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(draw):
    # Deep teal at top -> teal-mid -> warm amber at the horizon (y ~ 640).
    stops = [
        (0, (9, 58, 71)),        # deep teal
        (300, (18, 96, 104)),    # teal
        (480, (46, 138, 130)),   # teal-mid
        (640, (232, 168, 92)),   # warm amber horizon
        (H, (240, 196, 130)),
    ]
    for y in range(H):
        for i in range(len(stops) - 1):
            y0, c0 = stops[i]
            y1, c1 = stops[i + 1]
            if y0 <= y <= y1:
                t = (y - y0) / max(1, y1 - y0)
                draw.line([(0, y), (W, y)], fill=lerp(c0, c1, t))
                break


def sun(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = 150, 545
    # Halo rings, fading outward.
    for r, alpha in [(150, 18), (120, 26), (95, 38), (72, 55)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=(255, 214, 120, alpha))
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52],
              fill=(255, 196, 84, 255))
    d.ellipse([cx - 42, cy - 42, cx + 42, cy + 42],
              fill=(255, 222, 140, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    base.alpha_composite(layer)


def cloud_puffs(draw, base_y, scale, colors):
    # Deterministic row of overlapping ellipses forming a cloud bank.
    puffs = [
        (60, 0, 260, 90), (220, -28, 300, 100), (430, -14, 300, 96),
        (640, -30, 320, 104), (830, -6, 260, 92),
        (130, 34, 300, 84), (360, 44, 320, 88), (600, 36, 320, 90),
        (800, 42, 280, 82),
    ]
    for i, (x, dy, w, h) in enumerate(puffs):
        c = colors[i % len(colors)]
        draw.ellipse([x, base_y + dy, x + w, base_y + dy + h], fill=c)


def cloud_sea(draw):
    # Cream / beige sea of clouds filling the lower third.
    draw.rectangle([0, 640, W, H], fill=(242, 230, 200))
    creams = [(250, 244, 224), (242, 230, 200), (255, 250, 236),
              (238, 222, 186), (250, 240, 214)]
    cloud_puffs(draw, 640, 1.0, creams)
    cloud_puffs(draw, 800, 1.0, creams)
    # Soft shadow gaps between cloud banks.
    for x, y, w, h in [(120, 760, 300, 40), (560, 780, 340, 44),
                       (300, 900, 420, 46)]:
        draw.ellipse([x, y, x + w, y + h], fill=(226, 206, 168))


def birds(draw):
    # Small birds: two short arcs each.
    for cx, cy, s in [(250, 250, 14), (330, 210, 11), (180, 300, 10),
                      (880, 260, 12), (700, 180, 10)]:
        draw.arc([cx - s, cy - s // 2, cx, cy + s // 2],
                 start=200, end=340, fill=(30, 50, 55), width=3)
        draw.arc([cx, cy - s // 2, cx + s, cy + s // 2],
                 start=200, end=340, fill=(30, 50, 55), width=3)


def island(draw):
    # Floating island: grassy plateau, then cliffs tapering to a point.
    # Plateau top (grass).
    draw.polygon([(168, 448), (852, 448), (836, 486), (184, 486)],
                 fill=(96, 168, 84))
    draw.polygon([(168, 448), (852, 448), (846, 462), (174, 462)],
                 fill=(124, 196, 96))
    # Cliff body, split into sunlit (left) and shadow (right) facets.
    draw.polygon([(184, 486), (836, 486), (700, 690), (512, 818),
                  (326, 690)], fill=(58, 122, 66))
    draw.polygon([(184, 486), (512, 486), (512, 818), (326, 690)],
                 fill=(124, 184, 92))
    # Rock strata lines on the cliff faces.
    for y0, y1 in [(540, 560), (610, 630), (680, 700)]:
        draw.line([(240, y0), (500, y0 + 14)], fill=(88, 148, 70), width=4)
        draw.line([(524, y0 + 14), (780, y0)], fill=(40, 92, 50), width=4)
    # Small bushes on the plateau rim.
    for cx in [220, 300, 800, 830]:
        draw.ellipse([cx - 18, 428, cx + 18, 456], fill=(70, 140, 66))


def waterfall(draw):
    # Waterfall pouring off the plateau edge into the clouds.
    x0, x1 = 742, 782
    draw.polygon([(x0, 486), (x1, 486), (x1 + 8, 640), (x0 - 6, 640)],
                 fill=(214, 238, 244))
    draw.polygon([(x0 + 10, 486), (x1 - 8, 486), (x1 - 2, 640),
                  (x0 + 4, 640)], fill=(255, 255, 255))
    for y in (520, 560, 600):
        draw.line([(x0 + 4, y), (x1 - 2, y + 6)], fill=(170, 210, 220),
                  width=3)
    # Foam where it meets the clouds.
    draw.ellipse([x0 - 26, 622, x1 + 30, 668], fill=(255, 255, 255))
    draw.ellipse([x0 - 8, 636, x1 + 12, 672], fill=(232, 244, 246))


def house(draw, x, y, w, h, roof_h):
    draw.rectangle([x, y, x + w, y + h], fill=(250, 246, 236))
    draw.polygon([(x - 8, y), (x + w // 2, y - roof_h),
                  (x + w + 8, y)], fill=(196, 96, 58))
    # Warm lit windows.
    draw.rectangle([x + 10, y + 14, x + 24, y + 30], fill=(255, 204, 92))
    draw.rectangle([x + w - 24, y + 14, x + w - 10, y + 30],
                   fill=(255, 204, 92))
    draw.rectangle([x + w // 2 - 7, y + h - 26, x + w // 2 + 7, y + h],
                   fill=(120, 74, 44))


def houses(draw):
    house(draw, 250, 396, 64, 52, 30)
    house(draw, 330, 404, 54, 44, 26)
    house(draw, 398, 400, 60, 48, 28)


def lighthouse(base, draw):
    # Glow + beam behind the tower.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([566, 258, 690, 382], fill=(255, 214, 110, 70))
    # Subtle beam to the left.
    gd.polygon([(600, 320), (330, 268), (330, 356)], fill=(255, 226, 150, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    base.alpha_composite(glow)

    lx = 596  # tower left edge
    # Tower: white with coral bands.
    draw.rectangle([lx, 330, lx + 56, 486], fill=(250, 248, 242))
    draw.rectangle([lx, 360, lx + 56, 378], fill=(232, 94, 78))
    draw.rectangle([lx, 410, lx + 56, 428], fill=(232, 94, 78))
    draw.rectangle([lx, 458, lx + 56, 472], fill=(232, 94, 78))
    # Gallery + lamp room.
    draw.rectangle([lx - 6, 312, lx + 62, 330], fill=(60, 60, 64))
    draw.rectangle([lx + 8, 282, lx + 48, 312], fill=(255, 214, 110))
    draw.rectangle([lx + 8, 282, lx + 48, 312], outline=(90, 60, 40), width=3)
    draw.line([lx + 28, 282, lx + 28, 312], fill=(90, 60, 40), width=3)
    # Coral-red conical roof.
    draw.polygon([(lx - 2, 282), (lx + 58, 282), (lx + 28, 248)],
                 fill=(214, 72, 58))
    draw.ellipse([lx + 24, 238, lx + 32, 248], fill=(214, 72, 58))
    # Door.
    draw.rectangle([lx + 22, 452, lx + 34, 486], fill=(90, 60, 40))


def title_text(draw):
    serif = ImageFont.truetype(SERIF_BOLD, 118)
    sans = ImageFont.truetype(SANS, 30)
    # Soft shadow, then cream letters.
    draw.text((512, 52), "NIMBARA", font=serif, anchor="ma",
              fill=(10, 42, 50))
    draw.text((512, 48), "NIMBARA", font=serif, anchor="ma",
              fill=(255, 248, 231))
    # Thin gold rule.
    draw.line([(312, 188), (712, 188)], fill=(232, 184, 92), width=4)
    draw.ellipse([508, 184, 516, 192], fill=(232, 184, 92))
    # Tagline, letterspaced by hand.
    tag = "T H E   I S L A N D   A B O V E   T H E   C L O U D S"
    draw.text((512, 206), tag, font=sans, anchor="ma",
              fill=(255, 240, 210))


def main():
    img = Image.new("RGB", (W, H), (9, 58, 71))
    draw = ImageDraw.Draw(img)
    sky_gradient(draw)
    sun(img.convert("RGBA"))
    # Re-draw on the RGBA canvas from here: rebuild as RGBA for glow work.
    rgba = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    rd = ImageDraw.Draw(rgba)
    sky_gradient(rd)
    sun(rgba)
    rd = ImageDraw.Draw(rgba)
    cloud_sea(rd)
    birds(rd)
    island(rd)
    waterfall(rd)
    houses(rd)
    lighthouse(rgba, rd)
    title_text(rd)
    rgba.convert("RGB").save(OUT, optimize=True)


if __name__ == "__main__":
    main()
