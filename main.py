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

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default(size)


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
    return y + font.size


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
