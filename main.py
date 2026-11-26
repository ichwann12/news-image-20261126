#!/usr/bin/env python3
"""news-image-20261126 — draw a newspaper front page summing up the world
news of Thursday 26 November 2026 and write it to entry.png.

Everything is drawn with PIL from the headlines baked into this file:
no network, no wall clock, no randomness, so two runs produce identical
bytes.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 26

PAPER = (247, 243, 231)
CARD = (255, 253, 246)
INK = (26, 26, 26)
RED = (176, 42, 30)
NAVY = (31, 58, 95)
GREY = (96, 96, 92)
BODY = (60, 60, 56)
EDGE = (198, 190, 170)

SERIF_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
SERIF = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
SANS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
SANS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

_font_cache = {}


def font(paths, size):
    """First usable TrueType font from the candidates, else PIL default."""
    key = (tuple(paths), size)
    if key in _font_cache:
        return _font_cache[key]
    for path in paths:
        try:
            f = ImageFont.truetype(path, size)
            _font_cache[key] = f
            return f
        except OSError:
            continue
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f


def serif_bold(size):
    return font(SERIF_BOLD, size)


def serif(size):
    return font(SERIF, size)


def sans(size):
    return font(SANS, size)


def sans_bold(size):
    return font(SANS_BOLD, size)


def wrap_lines(draw, text, fnt, max_width):
    """Greedy word wrap of each paragraph to lines fitting max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text_block(draw, x, y, text, fnt, max_width, fill, leading):
    """Draw wrapped text; return the y just below the last line."""
    for line in wrap_lines(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_into(img, draw_fn, x, y, w, h):
    """Run draw_fn on an isolated layer, then paste it in its own box so
    no illustration can spill over neighbouring text."""
    layer = Image.new("RGB", (w, h), PAPER)
    ld = ImageDraw.Draw(layer)
    draw_fn(ld, 0, 0, w, h)
    img.paste(layer, (x, y))


# ------------------------------------------------------------------ pictures

def pic_mumbai(d, x, y, w, h):
    """Mumbai skyline at dusk: the Gateway of India and memorial candles."""
    d.rectangle([x, y, x + w, y + h], fill=(31, 58, 95))
    d.ellipse([x + w - 82, y + 14, x + w - 40, y + 56], fill=(250, 214, 140))
    ground = y + h - 56
    # lit windows in the skyline
    towers = [72, 112, 90, 132, 98, 122, 80, 106]
    tw = w // len(towers)
    for i, th in enumerate(towers):
        bx = x + i * tw + 2
        d.rectangle([bx, ground - th, bx + tw - 4, ground], fill=(18, 34, 58))
        for wy in range(ground - th + 10, ground - 8, 18):
            d.rectangle([bx + 5, wy, bx + 9, wy + 6], fill=(250, 214, 140))
    # Gateway of India arch, centre
    cx = x + w // 2
    top = ground - 148
    d.rectangle([cx - 52, top + 40, cx + 52, ground], fill=(232, 222, 196))
    d.pieslice([cx - 52, top - 12, cx + 52, top + 92], 180, 360,
               fill=(232, 222, 196))
    d.rectangle([cx - 52, top + 92, cx + 52, ground], fill=(232, 222, 196))
    d.rectangle([cx - 58, top + 34, cx + 58, top + 42], fill=(210, 196, 164))
    d.rectangle([cx - 26, top + 78, cx + 26, ground], fill=(31, 58, 95))
    d.pieslice([cx - 26, top + 52, cx + 26, top + 104], 180, 360,
               fill=(31, 58, 95))
    # ground and three memorial candles
    d.rectangle([x, ground, x + w, y + h], fill=(20, 20, 20))
    for cxo in (x + w // 2 - 92, x + w // 2, x + w // 2 + 92):
        d.rectangle([cxo - 7, y + h - 30, cxo + 7, y + h - 12],
                    fill=(240, 236, 224))
        d.ellipse([cxo - 5, y + h - 44, cxo + 5, y + h - 30], fill=(255, 170, 40))
        d.ellipse([cxo - 2, y + h - 40, cxo + 2, y + h - 33], fill=(255, 230, 130))


def pic_tiangong(d, x, y, w, h):
    """Tiangong station in orbit above the Earth."""
    d.rectangle([x, y, x + w, y + h], fill=(8, 12, 26))
    for sx, sy in [(14, 12), (52, 30), (96, 10), (150, 26), (210, 12),
                   (260, 34), (30, 58), (120, 52), (190, 60), (240, 78),
                   (70, 84), (285, 58)]:
        d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                  fill=(255, 255, 255))
    # Earth arc along the bottom
    d.ellipse([x - 60, y + h - 46, x + w + 60, y + h + 150], fill=(38, 110, 190))
    d.ellipse([x - 60, y + h - 46, x + w + 60, y + h + 150],
              outline=(90, 170, 230), width=3)
    d.ellipse([x + 30, y + h - 30, x + 90, y + h - 8], fill=(120, 190, 120))
    d.ellipse([x + 190, y + h - 38, x + 250, y + h - 14], fill=(120, 190, 120))
    # the station: core module with two solar wings
    cy = y + h // 2 - 14
    d.rectangle([x + 96, cy - 26, x + 208, cy + 26], fill=(205, 210, 216))
    d.rectangle([x + 96, cy - 26, x + 208, cy + 26],
                outline=(140, 146, 154), width=2)
    d.ellipse([x + 208, cy - 18, x + 226, cy + 18], fill=(160, 166, 174))
    d.rectangle([x + 118, cy - 40, x + 186, cy - 26], fill=(150, 156, 164))
    for px in (x + 18, x + 226):
        d.rectangle([px, cy - 30, px + 62, cy + 30], fill=(52, 92, 170))
        for gx in range(px + 12, px + 62, 12):
            d.line([gx, cy - 30, gx, cy + 30], fill=(120, 160, 220), width=1)
        d.line([px, cy, px + 62, cy], fill=(120, 160, 220), width=1)
    # small crew capsule drifting in from the right
    d.ellipse([x + 250, y + 16, x + 272, y + 38], fill=(230, 120, 60))


def pic_hormuz(d, x, y, w, h):
    """An oil tanker in the Strait of Hormuz, a naval mine below the waves."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 238))
    d.ellipse([x + w - 62, y + 10, x + w - 22, y + 50], fill=(250, 200, 90))
    # tanker: hull, red deckhouse, white bridge
    hull = y + h // 2 + 6
    d.polygon([(x + 18, hull), (x + w - 18, hull), (x + w - 34, hull + 30),
               (x + 34, hull + 30)], fill=(60, 60, 66))
    d.rectangle([x + 44, hull - 26, x + 120, hull], fill=(176, 42, 30))
    d.rectangle([x + 196, hull - 40, x + 236, hull], fill=(240, 240, 236))
    d.rectangle([x + 200, hull - 52, x + 214, hull - 40], fill=(60, 60, 66))
    for wx in range(x + 130, x + 192, 16):
        d.rectangle([wx, hull - 20, wx + 8, hull - 12], fill=(255, 255, 255))
    # the sea
    sea = hull + 30
    d.rectangle([x, sea, x + w, y + h], fill=(28, 96, 130))
    for wy in (sea + 12, sea + 30, sea + 48):
        for wx in range(x + 8, x + w - 8, 34):
            d.arc([wx, wy, wx + 26, wy + 14], 180, 360,
                  fill=(160, 210, 225), width=3)
    # spiked naval mine, bottom right
    mx, my = x + w - 62, y + h - 34
    d.ellipse([mx - 20, my - 20, mx + 20, my + 20], fill=(20, 20, 20))
    for k in range(8):
        ang = k * math.pi / 4
        d.line([mx, my, mx + int(26 * math.cos(ang)),
                my + int(26 * math.sin(ang))], fill=(20, 20, 20), width=4)
    # orange blast starburst, bottom left
    bx, by = x + 66, y + h - 44
    d.polygon([(bx, by - 26), (bx + 7, by - 7), (bx + 26, by - 4),
               (bx + 9, by + 6), (bx + 14, by + 24), (bx - 2, by + 10),
               (bx - 20, by + 20), (bx - 10, by + 2), (bx - 26, by - 8),
               (bx - 7, by - 8)], fill=(255, 170, 40))
    d.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=(255, 220, 90))


def pic_gaza(d, x, y, w, h):
    """A city skyline at dusk, one building damaged, smoke rising."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 214, 178))
    d.ellipse([x + 22, y + 12, x + 62, y + 52], fill=(250, 190, 110))
    ground = y + h - 34
    towers = [86, 64, 108, 74, 96, 60]
    tw = w // len(towers)
    for i, th in enumerate(towers):
        bx = x + i * tw + 2
        d.rectangle([bx, ground - th, bx + tw - 4, ground], fill=(74, 66, 60))
        for wy in range(ground - th + 10, ground - 8, 18):
            d.rectangle([bx + 5, wy, bx + 9, wy + 6], fill=(250, 214, 140))
    # damaged building with a jagged roofline
    bx = x + 2 * tw + 2
    d.polygon([(bx, ground), (bx, ground - 108), (bx + 12, ground - 92),
               (bx + 22, ground - 108), (bx + tw - 4, ground - 96),
               (bx + tw - 4, ground)], fill=(52, 46, 42))
    # column of smoke rising from the rooftops
    sx = x + w - 70
    for r, oy in [(22, 0), (26, -22), (28, -44), (22, -62)]:
        d.ellipse([sx - r, y + 108 + oy - r, sx + r, y + 108 + oy + r],
                  fill=(120, 116, 110))
    d.rectangle([x, ground, x + w, y + h], fill=(40, 38, 34))


def pic_treaty(d, x, y, w, h):
    """Two flags over a Pacific island, a signed treaty with a red seal."""
    d.rectangle([x, y, x + w, y + h], fill=(178, 216, 232))
    d.ellipse([x + w - 54, y + 10, x + w - 18, y + 46], fill=(250, 214, 140))
    d.rectangle([x, y + h - 52, x + w, y + h], fill=(38, 130, 160))
    d.ellipse([x + w // 2 - 78, y + h - 78, x + w // 2 + 78, y + h - 30],
              fill=(232, 210, 150))
    # palm tree on the island
    px = x + w // 2 + 44
    d.line([px, y + h - 44, px + 8, y + h - 92], fill=(110, 82, 40), width=5)
    for dx, dy in [(-26, -16), (24, -18), (-18, -30), (16, -32), (0, -38)]:
        d.line([px + 8, y + h - 92, px + 8 + dx, y + h - 92 + dy],
               fill=(46, 130, 70), width=4)
    # two flags on poles
    for fx, top_col, bot_col in [(x + 26, (20, 60, 140), (20, 60, 140)),
                                 (x + 108, (30, 110, 170), (30, 170, 90))]:
        d.line([fx, y + 22, fx, y + 96], fill=(90, 70, 40), width=3)
        d.rectangle([fx, y + 22, fx + 56, y + 54], fill=top_col)
        if bot_col != top_col:
            d.polygon([(fx, y + 54), (fx + 56, y + 22), (fx + 56, y + 54)],
                      fill=bot_col)
            d.line([fx, y + 54, fx + 56, y + 22], fill=(250, 210, 60), width=3)
        for sx, sy in [(fx + 12, y + 30), (fx + 26, y + 40), (fx + 42, y + 30)]:
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    # treaty document with a seal
    dx = x + w // 2 - 62
    dy = y + h - 66
    d.rectangle([dx, dy, dx + 124, dy + 52], fill=(255, 253, 246),
                outline=(120, 110, 90), width=2)
    for ly in range(dy + 10, dy + 34, 9):
        d.line([dx + 10, ly, dx + 82, ly], fill=(120, 120, 116), width=2)
    d.ellipse([dx + 90, dy + 24, dx + 114, dy + 48], fill=(176, 42, 30))
    d.ellipse([dx + 96, dy + 30, dx + 108, dy + 42], outline=(255, 255, 255),
              width=2)


def pic_cricket(d, x, y, w, h):
    """A cricket pitch: batsman mid-swing, stumps, and a flying red ball."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 130, 70))
    d.rectangle([x, y + h // 2 - 8, x + w, y + h // 2 + 8], fill=(210, 190, 140))
    d.rectangle([x + 24, y + 14, x + w - 24, y + h - 14],
                outline=(255, 255, 255), width=2)
    # stumps with bails
    sx = x + 34
    sy = y + h - 44
    for i in range(3):
        d.rectangle([sx + i * 8, sy - 30, sx + i * 8 + 5, sy],
                    fill=(250, 220, 120))
    d.rectangle([sx - 2, sy - 34, sx + 24, sy - 30], fill=(250, 220, 120))
    # batsman silhouette, mid-swing
    bx = x + w // 2 - 10
    by = y + h // 2 + 30
    d.ellipse([bx - 11, by - 62, bx + 11, by - 40], fill=(30, 30, 30))
    d.polygon([(bx - 12, by - 40), (bx + 12, by - 40), (bx + 8, by + 6),
               (bx - 8, by + 6)], fill=(30, 30, 30))
    d.line([bx - 6, by + 6, bx - 14, by + 34], fill=(30, 30, 30), width=6)
    d.line([bx + 6, by + 6, bx + 16, by + 34], fill=(30, 30, 30), width=6)
    d.line([bx + 8, by - 34, bx + 46, by - 74], fill=(190, 150, 90), width=7)
    d.rectangle([bx + 40, by - 88, bx + 54, by - 70], fill=(220, 190, 130))
    # red ball with a motion arc
    d.arc([x + w - 110, y + 6, x + w - 20, y + 66], 200, 340,
          fill=(255, 255, 255), width=3)
    d.ellipse([x + w - 52, y + 8, x + w - 32, y + 28], fill=(200, 40, 30),
              outline=(255, 255, 255), width=2)
    # score strip
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(20, 20, 20))
    d.text((x + 10, y + h - 24), "204 off 53 balls", font=sans_bold(16),
           fill=(255, 220, 90))


# ------------------------------------------------------------------ layout

def card_vertical(img, d, x, y, w, h, kicker, headline, caption, pic):
    """A story card with the picture on top, text underneath."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=EDGE, width=2)
    px, py, pw, ph = x + 10, y + 10, w - 20, 104
    d.rectangle([px, py, px + pw, py + ph], outline=EDGE, width=1)
    draw_into(img, pic, px, py, pw, ph)
    ty = py + ph + 10
    d.text((x + 12, ty), kicker, font=sans_bold(17), fill=RED)
    ty += 27
    ty = draw_text_block(d, x + 12, ty, headline, serif_bold(23), w - 24,
                         INK, 31)
    ty += 7
    draw_text_block(d, x + 12, ty, caption, sans(16), w - 24, BODY, 22)


def card_horizontal(img, d, x, y, w, h, kicker, headline, caption, pic):
    """A wide story card: picture on the left, text on the right."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=EDGE, width=2)
    px, py, pw, ph = x + 10, y + 10, 158, h - 20
    d.rectangle([px, py, px + pw, py + ph], outline=EDGE, width=1)
    draw_into(img, pic, px, py, pw, ph)
    tx = px + pw + 14
    tw = x + w - 12 - tx
    ty = y + 14
    d.text((tx, ty), kicker, font=sans_bold(17), fill=RED)
    ty += 28
    ty = draw_text_block(d, tx, ty, headline, serif_bold(23), tw, INK, 31)
    ty += 8
    draw_text_block(d, tx, ty, caption, sans(16), tw, BODY, 22)


def draw_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    title = "THE WORLD TODAY"
    title_fnt = serif_bold(62)
    tw = d.textlength(title, font=title_fnt)
    d.text(((PAGE_W - tw) / 2, 14), title, font=title_fnt, fill=INK)
    d.line([MARGIN, 92, PAGE_W - MARGIN, 92], fill=INK, width=2)
    dateline = "THURSDAY, 26 NOVEMBER 2026  •  THE DAY'S WORLD NEWS IN ONE PAGE"
    date_fnt = sans_bold(22)
    dw = d.textlength(dateline, font=date_fnt)
    d.text(((PAGE_W - dw) / 2, 100), dateline, font=date_fnt, fill=NAVY)
    d.line([MARGIN, 130, PAGE_W - MARGIN, 130], fill=INK, width=4)
    d.line([MARGIN, 136, PAGE_W - MARGIN, 136], fill=INK, width=2)

    # ---- lead story: Mumbai marks 18 years since 26/11
    ly, lh = 150, 236
    d.rectangle([MARGIN, ly, PAGE_W - MARGIN, ly + lh], fill=CARD,
                outline=EDGE, width=2)
    ix, iy, iw, ih = MARGIN + 10, ly + 10, 392, lh - 20
    d.rectangle([ix, iy, ix + iw, iy + ih], outline=EDGE, width=1)
    draw_into(img, pic_mumbai, ix, iy, iw, ih)
    tx = ix + iw + 18
    tw2 = PAGE_W - MARGIN - 12 - tx
    ty = ly + 16
    d.text((tx, ty), "INDIA  •  18TH ANNIVERSARY", font=sans_bold(19), fill=RED)
    ty += 28
    ty = draw_text_block(d, tx, ty, "Mumbai remembers\n26/11, 18 years on",
                         serif_bold(44), tw2, INK, 54)
    ty += 10
    draw_text_block(
        d, tx, ty,
        "India marks 18 years since the 2008 Mumbai terror attacks. "
        "The nation also celebrates Constitution Day, honouring the "
        "adoption of its Constitution.",
        sans(19), tw2, BODY, 24)

    # ---- row one: three stories side by side
    ry, rh = 402, 288
    cw = (PAGE_W - 2 * MARGIN - 2 * 16) // 3
    row_one = [
        ("SPACE  •  CHINA", "A first for China's\nspace station",
         "Pakistan's first astronaut flies on Shenzhou-24 to the "
         "Tiangong station.",
         pic_tiangong),
        ("ENERGY  •  GULF", "Two tankers hit mines\nin the Hormuz strait",
         "Two oil tankers hit by naval mines; Houthis strike Saudi "
         "Arabia's Ras Tanura refinery.",
         pic_hormuz),
        ("MIDDLE EAST  •  GAZA", "Israel strikes Hamas\nofficial in Gaza",
         "An Israeli strike kills a Hamas official in Gaza, putting the "
         "fragile ceasefire under strain.",
         pic_gaza),
    ]
    for i, (kicker, headline, caption, pic) in enumerate(row_one):
        card_vertical(img, d, MARGIN + i * (cw + 16), ry, cw, rh,
                      kicker, headline, caption, pic)

    # ---- row two: treaty and cricket, wide cards
    wy, wh = 706, 178
    ww = (PAGE_W - 2 * MARGIN - 16) // 2
    card_horizontal(img, d, MARGIN, wy, ww, wh,
                    "PACIFIC  •  TREATY",
                    "Solomon Islands\nsigns security pact",
                    "A landmark treaty binds the Solomon Islands and Australia.",
                    pic_treaty)
    card_horizontal(img, d, MARGIN + ww + 16, wy, ww, wh,
                    "CRICKET  •  WORLD RECORD",
                    "15-year-old smashes\nworld batting record",
                    "Vaibhav Sooryavanshi, 15, hits 204 off 53 balls vs the UAE.",
                    pic_cricket)

    # ---- "also today" strip
    ay = 900
    d.line([MARGIN, ay, PAGE_W - MARGIN, ay], fill=INK, width=2)
    d.text((MARGIN, ay + 8), "ALSO TODAY", font=sans_bold(19), fill=RED)
    ay += 34
    ticker = ("Ukraine strikes Russian oil refineries; Putin vows retaliation — "
              "Russia's war toll nears 500,000  •  "
              "Bangladesh raises garment wage 36%  •  "
              "North Korea orders Switzerland to shut its Pyongyang office  •  "
              "US tariff plan rattles markets as Nvidia leads AI sell-off  •  "
              "Plane crash off Mississippi kills 6, including 2 children")
    ticker_fnt = sans(16)
    for line in wrap_lines(d, ticker, ticker_fnt, PAGE_W - 2 * MARGIN)[:3]:
        d.text((MARGIN, ay), line, font=ticker_fnt, fill=BODY)
        ay += 24
    d.line([MARGIN, 1000, PAGE_W - MARGIN, 1000], fill=INK, width=2)
    return img


def main():
    img = draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
