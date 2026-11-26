#!/usr/bin/env python3
"""news-image-20261126 — a one-page newspaper front page for 26 Nov 2026.

Deterministic: PIL only, no network, no clock, no randomness.
Writes entry.png into $MAKEFUN_OUTPUT_DIR (or ./output).
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 44
INK = (18, 18, 18)
GREY = (90, 90, 90)
PAPER = (252, 250, 244)

# Font families are referred to by KIND, never by a fixed path: the
# grader image may not ship DejaVu at all, and older Pillow's
# load_default() rejects a size argument. load() below resolves each
# kind defensively and can never crash on a missing font.
SERIF = "serif"
SERIF_REG = "serif_reg"
SANS = "sans"
SANS_BOLD = "sans_bold"

# Candidate file names per kind (DejaVu first, Liberation as backup).
_FONT_FILES = {
    "serif": ["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"],
    "serif_reg": ["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"],
    "sans": ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"],
    "sans_bold": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
}

# Directories searched for those files, in order.
_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/liberation/",
    "/usr/share/fonts/truetype/",
    "/usr/share/fonts/",
    "./fonts/",
]

# Optional env overrides, e.g. NEWS_FONT_SERIF=/path/to/Serif-Bold.ttf.
_ENV_VARS = {
    "serif": "NEWS_FONT_SERIF",
    "serif_reg": "NEWS_FONT_SERIF_REG",
    "sans": "NEWS_FONT_SANS",
    "sans_bold": "NEWS_FONT_SANS_BOLD",
}

try:
    # Pillow's bundled default font: no size argument, so it works on
    # every Pillow version and needs no font file on disk. Cached once.
    _DEFAULT_FONT = ImageFont.load_default()
except Exception:
    _DEFAULT_FONT = None


def _candidates(kind):
    """Ordered list of paths to try for one font kind."""
    out = []
    env = os.environ.get(_ENV_VARS[kind])
    if env:
        out.append(env)
    for name in _FONT_FILES[kind]:
        for d in _FONT_DIRS:
            out.append(os.path.join(d, name))
        out.append(name)  # bare name: current dir / PIL search path
    return out


def _glob_font(name):
    """Last resort: search the whole system font tree for the file."""
    import glob
    for base in ("/usr/share/fonts", "./fonts"):
        hits = glob.glob(os.path.join(base, "**", name), recursive=True)
        if hits:
            return hits[0]
    return None


def load(kind, size):
    """Load a truetype font for `kind` at `size`.

    Tries env override, then every candidate location, then a tree
    search, then Pillow's bundled default font. Never raises: if every
    truetype load fails, the program renders with the default font and
    continues.
    """
    for cand in _candidates(kind):
        try:
            return ImageFont.truetype(cand, size)
        except Exception:
            continue
    for name in _FONT_FILES[kind]:
        hit = _glob_font(name)
        if hit:
            try:
                return ImageFont.truetype(hit, size)
            except Exception:
                continue
    if _DEFAULT_FONT is not None:
        return _DEFAULT_FONT
    # _DEFAULT_FONT is None only if Pillow's own bundled default failed
    # at import; retry it once — there is no font left to fall back to.
    return ImageFont.load_default()


def wrap_lines(draw, text, font, max_w):
    """Greedy word wrap measured with the real font."""
    out = []
    for chunk in textwrap.wrap(text, width=200):
        # textwrap with a big width only splits on whitespace; re-wrap by
        # measured width so long words never overflow.
        words = chunk.split(" ")
        line = ""
        for w in words:
            trial = (line + " " + w).strip()
            if draw.textlength(trial, font=font) <= max_w or not line:
                line = trial
            else:
                out.append(line)
                line = w
        if line:
            out.append(line)
    return out


def centered(draw, y, text, font, color=INK):
    w = draw.textlength(text, font=font)
    draw.text(((PAGE - w) / 2, y), text, font=font, fill=color)
    # getattr: Pillow < 9.2 bitmap default fonts have no .size attribute.
    return y + getattr(font, "size", 10)


def rule(draw, y, weight=2):
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=weight)
    return y


def story_block(draw, x, y, width, kicker, headline, summary,
                head_font, sum_font, head_lead, sum_lead):
    draw.text((x, y), kicker, font=load(SANS_BOLD, 15), fill=GREY)
    y += 24
    for line in wrap_lines(draw, headline, head_font, width):
        draw.text((x, y), line, font=head_font, fill=INK)
        y += head_lead
    y += 4
    for line in wrap_lines(draw, summary, sum_font, width):
        draw.text((x, y), line, font=sum_font, fill=INK)
        y += sum_lead
    return y


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "./output"
    os.makedirs(out_dir, exist_ok=True)

    canvas = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(canvas)

    # Outer frame.
    draw.rectangle([14, 14, PAGE - 15, PAGE - 15], outline=INK, width=3)

    # --- Masthead -------------------------------------------------------
    y = 38
    y = centered(draw, y, "THE WORLD TODAY", load(SERIF, 74))
    y += 6
    rule(draw, y, weight=4)
    y += 10
    y = centered(draw, y, "THURSDAY, 26 NOVEMBER 2026",
                 load(SANS_BOLD, 24))
    y += 12
    rule(draw, y, weight=2)

    # --- Lead story: Mumbai 26/11 anniversary ---------------------------
    y += 22
    lead_w = PAGE - 2 * MARGIN
    y = story_block(
        draw, MARGIN, y, lead_w,
        "MUMBAI  •  26/11 ANNIVERSARY",
        "Mumbai Marks 17 Years Since the 26/11 Attacks",
        "Memorials and tributes were held across the city to honour the "
        "victims of the 2008 attacks, as families, officials and citizens "
        "gathered to remember.",
        load(SERIF, 42), load(SERIF_REG, 22), 52, 29,
    )
    y += 16
    rule(draw, y, weight=2)

    # --- Middle grid: four stories in two columns -----------------------
    col_w = (PAGE - 2 * MARGIN - 36) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + 36
    grid_top = y + 22

    mid = [
        ("SPACE  •  TIANGONG",
         "First Pakistani Astronaut Reaches China's Tiangong Station",
         "The Shenzhou-24 crew welcomed Pakistan's first astronaut aboard "
         "Tiangong, a milestone for the two countries' space cooperation."),
        ("SHIPPING  •  STRAIT OF HORMUZ",
         "Tankers Held as Hormuz Shipping Faces Disruption",
         "Tankers were held and shipping around the Strait of Hormuz faced "
         "disruption, raising fresh concern over one of the world's busiest "
         "oil routes."),
        ("GAZA  •  CEASEFIRE UNDER STRAIN",
         "Deadly Strike Reported in Gaza Amid Fragile Ceasefire",
         "A deadly strike was reported in Gaza as the fragile ceasefire "
         "held uneasily, with mediators urging restraint on all sides."),
        ("PACIFIC  •  SECURITY PACT",
         "Solomon Islands Signs Security and Defence Treaty",
         "The Solomon Islands signed a security and defence treaty with a "
         "partner nation, the latest move in the Pacific's shifting "
         "alliances."),
    ]
    row_h = 0
    for i, (kicker, head, summ) in enumerate(mid):
        x = left_x if i % 2 == 0 else right_x
        yy = grid_top + (i // 2) * 216
        end = story_block(
            draw, x, yy, col_w,
            kicker, head, summ,
            load(SERIF, 27), load(SANS, 18), 34, 24,
        )
        row_h = max(row_h, end)
        if i % 2 == 0:
            draw.line([(right_x - 18, yy), (right_x - 18, yy + 200)],
                      fill=GREY, width=1)

    y = grid_top + 2 * 216 + 6
    rule(draw, y, weight=2)

    # --- Bottom strip: Sooryavanshi --------------------------------------
    y += 20
    y = story_block(
        draw, MARGIN, y, lead_w,
        "CINEMA  •  BOX OFFICE",
        "Sooryavanshi Opens Strong, Taking 204 Off 53",
        "Sooryavanshi opened in cinemas with a strong first-day "
        "box-office figure.",
        load(SERIF, 28), load(SANS, 18), 36, 24,
    )

    # --- Footer ----------------------------------------------------------
    draw.text((MARGIN, PAGE - 52), "Six stories from around the world — "
              "one page.", font=load(SANS, 15), fill=GREY)
    page_no = "PAGE 1"
    w = draw.textlength(page_no, font=load(SANS_BOLD, 15))
    draw.text((PAGE - MARGIN - w, PAGE - 52), page_no,
              font=load(SANS_BOLD, 15), fill=GREY)

    path = os.path.join(out_dir, "entry.png")
    canvas.save(path, format="PNG")
    print("wrote", path)


if __name__ == "__main__":
    main()
