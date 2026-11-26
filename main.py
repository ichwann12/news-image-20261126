#!/usr/bin/env python3
"""news-image-20261126: newspaper front page, standard library only.

Draws a 1024x1024 front page for Thursday 26 November 2026 and writes it
as entry.png. No third-party libraries: the PNG is encoded by hand with
zlib + struct, and all text is drawn with a small built-in 5x7 bitmap font
designed for this program. Fully deterministic: no clock, no network, no
randomness.
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024
MARGIN = 44
CONTENT_W = WIDTH - 2 * MARGIN

PAPER = (250, 246, 236)
INK = (20, 20, 20)
RED = (140, 29, 24)
GREY = (110, 105, 92)

# ---------------------------------------------------------------------------
# Tiny built-in 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#'
# means a filled cell, '.' means empty. Designed by hand for this program.
# ---------------------------------------------------------------------------

GLYPHS = {
    "A": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "....#", "....#", "....#", "....#", "#...#", ".###."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".#...", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
}

CHAR_W = 5
CHAR_H = 7
CHAR_GAP = 1  # blank columns between characters, in font cells


def text_width(text, scale):
    """Pixel width of text at the given scale (upper-cased first)."""
    upper = text.upper()
    return len(upper) * (CHAR_W + CHAR_GAP) * scale - CHAR_GAP * scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.upper().split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Canvas: plain RGB bytearray, 1024x1024.
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, colour)

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = colour[0]
            self.pixels[i + 1] = colour[1]
            self.pixels[i + 2] = colour[2]

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pixels[i] = colour[0]
                self.pixels[i + 1] = colour[1]
                self.pixels[i + 2] = colour[2]

    def draw_text(self, x, y, text, scale, colour):
        """Draw text with its top-left corner at (x, y). Returns width used."""
        cx = x
        for ch in text.upper():
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            for row in range(CHAR_H):
                bits = glyph[row]
                for col in range(CHAR_W):
                    if bits[col] == "#":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, colour
                        )
            cx += (CHAR_W + CHAR_GAP) * scale
        return cx - x - CHAR_GAP * scale

    def draw_text_centered(self, y, text, scale, colour):
        w = text_width(text, scale)
        x = (self.width - w) // 2
        self.draw_text(x, y, text, scale, colour)
        return y + CHAR_H * scale

    def rule(self, y, thickness, colour=INK):
        self.fill_rect(MARGIN, y, CONTENT_W, thickness, colour)
        return y + thickness


def line_height(scale, leading=6):
    return CHAR_H * scale + leading


# ---------------------------------------------------------------------------
# PNG encoder: signature, IHDR, IDAT (zlib, filter 0), IEND, CRC32s.
# ---------------------------------------------------------------------------

def png_chunk(kind, data):
    out = struct.pack(">I", len(data))
    out += kind
    out += data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    raw = bytearray()
    row_bytes = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter type 0: no filter
        start = y * row_bytes
        raw += canvas.pixels[start:start + row_bytes]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += png_chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------------------
# Front page layout.
# ---------------------------------------------------------------------------

LEAD_HEADLINE = "Mumbai Marks 17 Years Since the 26/11 Attacks"
LEAD_SUMMARY = (
    "Memorials and tributes were held across the city to honour the victims "
    "of the 2008 attacks."
)

STORIES = [
    (
        "First Pakistani Astronaut Reaches China's Tiangong Station",
        "The Shenzhou-24 crew welcomed Pakistan's first astronaut aboard "
        "the Tiangong space station.",
    ),
    (
        "Tankers Held as Hormuz Shipping Faces Disruption",
        "Shipping through the Strait of Hormuz faced disruption as tankers "
        "were held amid rising tensions.",
    ),
    (
        "Deadly Strike Reported in Gaza Amid Fragile Ceasefire",
        "A deadly strike was reported in Gaza as a fragile ceasefire held "
        "under strain.",
    ),
    (
        "Solomon Islands Signs Security and Defence Treaty",
        "The Solomon Islands signed a security and defence treaty, "
        "deepening regional ties.",
    ),
    (
        "Sooryavanshi Opens Strong, Taking 204 Off 53",
        "Vaibhav Sooryavanshi opened strongly, taking 204 off just 53 balls.",
    ),
]


def draw_story_block(canvas, x, y, width, headline, summary,
                     head_scale, body_scale):
    """Draw one story block; returns the y just below the block."""
    for line in wrap_text(headline, head_scale, width):
        canvas.draw_text(x, y, line, head_scale, INK)
        y += line_height(head_scale, leading=4)
    y += 4
    for line in wrap_text(summary, body_scale, width):
        canvas.draw_text(x, y, line, body_scale, GREY)
        y += line_height(body_scale, leading=4)
    return y


def render():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)

    y = 46
    # Masthead.
    canvas.draw_text_centered(y, "THE WORLD TODAY", 7, INK)
    y += CHAR_H * 7 + 14
    y = canvas.rule(y, 5)
    y += 10
    # Dateline.
    canvas.draw_text_centered(y, "THURSDAY, 26 NOVEMBER 2026", 2, RED)
    y += CHAR_H * 2 + 10
    y = canvas.rule(y, 2)
    y += 18

    # Lead story, full width.
    canvas.draw_text(MARGIN, y, "LEAD STORY", 2, RED)
    y += line_height(2, leading=6) + 4
    for line in wrap_text(LEAD_HEADLINE, 5, CONTENT_W):
        canvas.draw_text(MARGIN, y, line, 5, INK)
        y += line_height(5, leading=10)
    y += 8
    for line in wrap_text(LEAD_SUMMARY, 2, CONTENT_W):
        canvas.draw_text(MARGIN, y, line, 2, GREY)
        y += line_height(2, leading=6)
    y += 22
    y = canvas.rule(y, 2)
    y += 26

    # Four stories in two columns.
    gap = 24
    col_w = (CONTENT_W - gap) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + gap
    left_y = y
    right_y = y
    left_y = draw_story_block(canvas, left_x, left_y, col_w,
                              STORIES[0][0], STORIES[0][1], 3, 2)
    left_y += 18
    left_y = draw_story_block(canvas, left_x, left_y, col_w,
                              STORIES[1][0], STORIES[1][1], 3, 2)
    right_y = draw_story_block(canvas, right_x, right_y, col_w,
                               STORIES[2][0], STORIES[2][1], 3, 2)
    right_y += 18
    right_y = draw_story_block(canvas, right_x, right_y, col_w,
                               STORIES[3][0], STORIES[3][1], 3, 2)
    y = max(left_y, right_y) + 18
    y = canvas.rule(y, 2)
    y += 26

    # Final story, full width, framed.
    frame_top = y
    canvas.draw_text(MARGIN, y, "SPORT", 2, RED)
    y += line_height(2, leading=6) + 4
    for line in wrap_text(STORIES[4][0], 4, CONTENT_W):
        canvas.draw_text(MARGIN, y, line, 4, INK)
        y += line_height(4, leading=8)
    y += 8
    for line in wrap_text(STORIES[4][1], 2, CONTENT_W):
        canvas.draw_text(MARGIN, y, line, 2, GREY)
        y += line_height(2, leading=6)
    y += 12
    # Frame around the sport story.
    canvas.fill_rect(MARGIN, frame_top - 10, CONTENT_W, 2, INK)
    canvas.fill_rect(MARGIN, y, CONTENT_W, 2, INK)
    canvas.fill_rect(MARGIN, frame_top - 10, 2, y - frame_top + 10, INK)
    canvas.fill_rect(MARGIN + CONTENT_W - 2, frame_top - 10, 2,
                     y - frame_top + 10, INK)

    # Footer.
    fy = HEIGHT - 58
    canvas.rule(fy, 2)
    canvas.draw_text_centered(fy + 12, "THE WORLD TODAY - PAGE 1", 2, GREY)
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(".", "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    canvas = render()
    data = encode_png(canvas)
    with open(out_path, "wb") as fh:
        fh.write(data)
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
