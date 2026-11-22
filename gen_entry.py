#!/usr/bin/env python3
"""Draw the 22 November 2026 world-news front page as a 1024x1024 PNG.

Pure standard library: a hand-built RGB pixel buffer is encoded to PNG
with zlib, so the program is deterministic and needs no network.
The six stories are the verified 22 Nov 2026 headlines from the scan
notes: Iran strikes US bases in Kuwait and Bahrain (tanker attacked off
Oman), a magnitude 6.9 quake in the Peruvian Andes, the EU-Indonesia
trade deal signed after ten years, Russia's strike on Lviv, COP31
deadlocked on fossil fuels, and the Trump-Xi-Putin summit in Shenzhen.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 229)
CARD = (255, 255, 255)
INK = (24, 30, 44)
NAVY = (22, 38, 66)
CRIMSON = (166, 30, 30)
TEAL = (15, 118, 110)
GOLD = (185, 138, 31)
GREY = (96, 102, 116)
RULE = (208, 200, 184)
SEA = (38, 110, 138)
SKY = (214, 232, 240)

# 5x7 pixel font. Each glyph is 7 rows of 5 cells, '#' = ink, '.' = empty.
FONT = {
    "A": ("#...#", "##.##", "#.#.#", "#.#.#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.#.", "#..##"),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
}


class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            base = (y * self.width + x) * 3
            self.pixels[base:base + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.height, y1 + 1)):
            for x in range(max(0, x0), min(self.width, x1 + 1)):
                self.put(x, y, color)

    def hline(self, x0, x1, y, color):
        for x in range(x0, x1 + 1):
            self.put(x, y, color)

    def vline(self, x, y0, y1, color):
        for y in range(y0, y1 + 1):
            self.put(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.put(x, y, color)

    def disc(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.put(x, y, color)

    def triangle(self, ax, ay, bx, by, cx, cy, color):
        top, bottom = min(ay, by, cy), max(ay, by, cy)
        for y in range(top, bottom + 1):
            xs = []
            for (px, py, qx, qy) in ((ax, ay, bx, by), (bx, by, cx, cy),
                                     (cx, cy, ax, ay)):
                if py == qy:
                    continue
                if min(py, qy) <= y <= max(py, qy):
                    xs.append(px + (qx - px) * (y - py) // (qy - py))
            if len(xs) >= 2:
                for x in range(min(xs), max(xs) + 1):
                    self.put(x, y, color)

    def text(self, string, x, y, scale, color):
        cursor = x
        for char in string:
            glyph = FONT.get(char.upper(), FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.rect(cursor + col * scale, y + row * scale,
                                  cursor + col * scale + scale - 1,
                                  y + row * scale + scale - 1, color)
            cursor += 6 * scale
        return cursor

    def text_width(self, string, scale):
        return len(string) * 6 * scale - scale

    def centred(self, string, cx, y, scale, color):
        self.text(string, cx - self.text_width(string, scale) // 2,
                  y, scale, color)


def wrap(string, limit):
    """Greedy word wrap into lines of at most `limit` characters."""
    lines, current = [], ""
    for word in string.split(" "):
        trial = word if not current else current + " " + word
        if len(trial) <= limit:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def card(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, CARD)
    canvas.rect(x0, y0, x1, y0 + 2, NAVY)
    for x in range(x0, x1 + 1):
        canvas.put(x, y1, RULE)
    for y in range(y0, y1 + 1):
        canvas.put(x0, y, RULE)
        canvas.put(x1, y, RULE)


def burst(canvas, cx, cy, r, color):
    """A simple starburst: a disc plus eight spikes."""
    canvas.disc(cx, cy, r // 2, color)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, -1), (1, -1), (-1, 1)):
        canvas.line(cx, cy, cx + dx * r, cy + dy * r, color)


def draw_tanker(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, SKY)
    canvas.rect(x0, y1 - 52, x1, y1, SEA)
    for wx in range(x0, x1, 26):
        canvas.hline(wx, wx + 12, y1 - 40, (255, 255, 255))
    # Hull with containers stacked squarely on its deck.
    canvas.rect(x0 + 48, y1 - 92, x1 - 48, y1 - 56, (30, 34, 44))
    canvas.rect(x0 + 60, y1 - 122, x0 + 138, y1 - 92, (201, 162, 39))
    canvas.rect(x0 + 150, y1 - 122, x0 + 228, y1 - 92, (166, 30, 30))
    canvas.rect(x0 + 240, y1 - 122, x0 + 318, y1 - 92, (30, 34, 44))
    canvas.vline(x1 - 78, y1 - 150, y1 - 92, (30, 34, 44))
    canvas.rect(x1 - 86, y1 - 158, x1 - 70, y1 - 150, (30, 34, 44))
    # Two explosions above the ship with smoke columns rising to them.
    burst(canvas, x0 + 92, y0 + 42, 26, (232, 120, 30))
    burst(canvas, x1 - 84, y0 + 30, 20, (232, 120, 30))
    canvas.line(x0 + 92, y0 + 60, x0 + 108, y1 - 122, (120, 124, 130))
    canvas.line(x1 - 84, y0 + 46, x1 - 70, y1 - 122, (120, 124, 130))


def draw_mountains(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, SKY)
    canvas.triangle(x0 + 10, y1, x0 + 110, y0 + 18, x0 + 210, y1, (90, 100, 118))
    canvas.triangle(x0 + 150, y1, x0 + 260, y0 + 42, x0 + 370, y1, (60, 70, 92))
    canvas.triangle(x0 + 300, y1, x0 + 400, y0 + 8, x1 - 10, y1, (38, 48, 70))
    # Snow caps: small white triangles sitting on the two tallest peaks.
    canvas.triangle(x0 + 98, y0 + 30, x0 + 110, y0 + 18, x0 + 122, y0 + 30, CARD)
    canvas.triangle(x0 + 388, y0 + 20, x0 + 400, y0 + 8, x0 + 412, y0 + 20, CARD)
    # A crack zigzags along the foot of the range.
    canvas.line(x0 + 30, y1 - 8, x0 + 90, y1 - 26, CRIMSON)
    canvas.line(x0 + 90, y1 - 26, x0 + 150, y1 - 10, CRIMSON)
    canvas.line(x0 + 150, y1 - 10, x0 + 210, y1 - 30, CRIMSON)


def draw_trade(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, SKY)
    mid = (x0 + x1) // 2
    # EU flag: blue field, a ring of twelve gold stars.
    fx0, fy0, fx1, fy1 = x0 + 28, y0 + 16, mid - 34, y1 - 16
    canvas.rect(fx0, fy0, fx1, fy1, (0, 51, 153))
    fcx, fcy = (fx0 + fx1) // 2, (fy0 + fy1) // 2
    for i in range(12):
        angle = 2 * math.pi * i / 12 - math.pi / 2
        sx = int(fcx + 26 * math.cos(angle))
        sy = int(fcy + 14 * math.sin(angle))
        canvas.disc(sx, sy, 2, GOLD)
    # Indonesia flag: red over white.
    ix0, ix1 = mid + 34, x1 - 28
    canvas.rect(ix0, fy0, ix1, (fy0 + fy1) // 2, (200, 16, 46))
    canvas.rect(ix0, (fy0 + fy1) // 2 + 1, ix1, fy1, CARD)
    # Arrow between the flags.
    canvas.line(mid - 18, (y0 + y1) // 2, mid + 18, (y0 + y1) // 2, INK)
    canvas.line(mid + 18, (y0 + y1) // 2, mid + 8, (y0 + y1) // 2 - 8, INK)
    canvas.line(mid + 18, (y0 + y1) // 2, mid + 8, (y0 + y1) // 2 + 8, INK)


def draw_skyline(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, (226, 214, 190))
    heights = (52, 84, 64, 96, 70, 58)
    bw = (x1 - x0) // len(heights)
    for i, hgt in enumerate(heights):
        bx = x0 + i * bw + 6
        canvas.rect(bx, y1 - hgt, bx + bw - 12, y1, (52, 58, 74))
        for wy in range(y1 - hgt + 10, y1 - 8, 16):
            for wx in range(bx + 6, bx + bw - 18, 12):
                canvas.rect(wx, wy, wx + 5, wy + 7, GOLD)
    canvas.disc((x0 + x1) // 2, y0 + 22, 12, (232, 120, 30))
    canvas.line((x0 + x1) // 2 - 20, y0 + 6, (x0 + x1) // 2 + 20, y0 + 38, CRIMSON)
    canvas.line((x0 + x1) // 2 + 20, y0 + 6, (x0 + x1) // 2 - 20, y0 + 38, CRIMSON)


def draw_globe(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, SKY)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    radius = min((x1 - x0) // 2, (y1 - y0) // 2) - 4
    canvas.disc(cx, cy, radius, SEA)
    canvas.disc(cx - 8, cy - 6, 9, TEAL)
    canvas.disc(cx + 9, cy + 8, 7, TEAL)
    canvas.line(cx - radius, cy, cx + radius, cy, CARD)
    canvas.line(cx, cy - radius, cx, cy + radius, CARD)


def draw_summit(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, (238, 230, 210))
    canvas.rect(x0 + 20, y1 - 26, x1 - 20, y1 - 16, (122, 84, 44))
    for i, colour in enumerate(((178, 34, 52), (222, 190, 40), (0, 57, 166))):
        fx = x0 + 34 + i * 84
        canvas.vline(fx, y0 + 16, y1 - 26, INK)
        canvas.rect(fx + 2, y0 + 16, fx + 42, y0 + 44, colour)
        canvas.disc(fx + 22, y1 - 44, 12, NAVY)


def build():
    canvas = Canvas(W, H, PAPER)
    canvas.rect(0, 0, W - 1, 7, GOLD)
    canvas.rect(0, H - 8, W - 1, H - 1, GOLD)

    # Masthead.
    canvas.rect(16, 16, 1008, 138, NAVY)
    canvas.centred("THE WORLD TODAY", 512, 34, 6, CARD)
    canvas.centred("SUNDAY, NOVEMBER 22, 2026", 512, 102, 3, GOLD)

    # Kicker strip under the masthead.
    canvas.centred("GULF  -  PERU  -  EUROPE  -  UKRAINE  -  CLIMATE  -  SUMMIT",
                   512, 156, 2, GREY)

    # Lead story: the Gulf crisis.
    card(canvas, 24, 184, 1000, 452)
    canvas.text("GULF CRISIS", 48, 206, 2, CRIMSON)
    canvas.text("IRAN STRIKES U.S. BASES", 48, 240, 4, INK)
    canvas.text("IN KUWAIT, BAHRAIN", 48, 280, 4, INK)
    body = wrap("Tanker attacked off Oman as Gulf tensions peak; "
                "the Strait of Hormuz in focus.", 44)
    for i, line in enumerate(body):
        canvas.text(line, 48, 336 + i * 22, 2, INK)
    draw_tanker(canvas, 624, 206, 976, 428)

    # Middle row: Peru quake and the EU-Indonesia deal.
    card(canvas, 24, 468, 494, 700)
    canvas.text("EARTHQUAKE", 44, 486, 2, TEAL)
    canvas.text("QUAKE ROCKS PERU", 44, 514, 3, INK)
    canvas.text("ANDES AT 6.9", 44, 544, 3, INK)
    for i, line in enumerate(wrap("Magnitude 6.9 tremor shakes the Andes region.", 34)):
        canvas.text(line, 44, 584 + i * 20, 2, INK)
    draw_mountains(canvas, 44, 626, 474, 684)

    card(canvas, 530, 468, 1000, 700)
    canvas.text("TRADE", 550, 486, 2, GOLD)
    canvas.text("EU SEALS INDONESIA DEAL", 550, 514, 3, INK)
    for i, line in enumerate(wrap("Signed after 10 years of talks; 98.5% of tariffs go.", 34)):
        canvas.text(line, 550, 554 + i * 20, 2, INK)
    draw_trade(canvas, 550, 606, 980, 684)

    # Bottom row: Lviv, COP31, summit.
    card(canvas, 24, 716, 330, 962)
    canvas.text("UKRAINE", 42, 732, 2, CRIMSON)
    canvas.text("LVIV HIT", 42, 758, 3, INK)
    for i, line in enumerate(wrap("Russia strikes Lviv: 2 killed, 10 hurt. 400 drones and 110 missiles hit Ukraine.", 26)):
        canvas.text(line, 42, 792 + i * 18, 2, INK)
    draw_skyline(canvas, 42, 886, 312, 946)

    card(canvas, 358, 716, 664, 962)
    canvas.text("CLIMATE", 376, 732, 2, TEAL)
    canvas.text("COP31 STALLS", 376, 758, 3, INK)
    for i, line in enumerate(wrap("Fossil-fuel talks deadlocked in the final stage.", 26)):
        canvas.text(line, 376, 792 + i * 18, 2, INK)
    draw_globe(canvas, 376, 886, 646, 946)

    card(canvas, 692, 716, 1000, 962)
    canvas.text("SUMMIT", 710, 732, 2, GOLD)
    canvas.text("TRUMP-XI-PUTIN", 710, 758, 3, INK)
    canvas.text("MEET IN SHENZHEN", 710, 788, 2, INK)
    for i, line in enumerate(wrap("Three leaders hold summit in Shenzhen.", 26)):
        canvas.text(line, 710, 820 + i * 18, 2, INK)
    draw_summit(canvas, 710, 886, 982, 946)

    # Footer.
    canvas.centred("ALL STORIES FIRST REPORTED SUNDAY, 22 NOVEMBER 2026",
                   512, 984, 2, GREY)
    return canvas


def encode_png(canvas):
    """Encode the canvas as a deterministic RGB PNG (filter 0 rows)."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    payload = zlib.compress(bytes(raw), 9)

    def chunk(kind, body):
        data = struct.pack(">I", len(body)) + kind + body
        return data + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += chunk(b"IHDR", ihdr)
    blob += chunk(b"IDAT", payload)
    blob += chunk(b"IEND", b"")
    return blob


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    blob = encode_png(build())
    with open(os.path.join(here, "entry.png"), "wb") as handle:
        handle.write(blob)
    print(f"entry.png: {len(blob)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
