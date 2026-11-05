#!/usr/bin/env python3
"""Draw the featured card for efre, full width above the project grid.

    python3 tools/featured.py      writes assets/card-efre-{dark,light}.svg

Same family and vertical rhythm as cards.py (window, title, copy, chips,
footer), stretched to FULL_W: the copy runs down the left, and on the right a
security key waits for a touch inside a cave (efre, ⵉⴼⵔⵉ, is Tamazight for
"cave"). The Tifinagh name is drawn from Noto Sans Tifinagh outlines.
"""

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from cards import (BODY_LH, BODY_SIZE, BODY_Y, CHIP_H, CHIP_Y, FOOT_SIZE,  # noqa: E402
                   FOOT_Y, PAD, REPO_SIZE, chip_row, wrap)
from svgkit import CARD_H, FULL_W, MARGIN, THEMES, Doc, n, tw  # noqa: E402

X0 = MARGIN + PAD
X1 = FULL_W - MARGIN - PAD
COPY_X1 = 506                   # the copy column ends here; the cave takes the rest
TITLE_Y, TITLE_SIZE = 58, 28
REPO_Y = 77
NAME = "ⵉⴼⵔⵉ"

CARD = {
    "title": "efre", "repo": "Ak1ra00/efre",
    "body": "An offline password vault for Windows that opens only with your "
            "YubiKey. No master password, no network code, and secrets that "
            "never leave its Rust core.",
    "chips": ["Rust", "Tauri 2", "FIDO2 hmac-secret", "XChaCha20-Poly1305"],
    "langs": [("Rust", "orange"), ("TypeScript", "blue")],
    "link": "↗ ak1ra00.github.io/efre", "accent": "violet",
}

_TIFINAGH = None


def tifinagh(d, x, y, word, size, fill):
    """Draw Tifinagh text (proportional) with its baseline at y; returns (markup, width)."""
    global _TIFINAGH
    if _TIFINAGH is None:
        with open(os.path.join(HERE, "glyphs-tifinagh.json"), encoding="utf-8") as fh:
            _TIFINAGH = json.load(fh)
    k = size / _TIFINAGH["upm"]
    uses, adv = [], 0
    for ch in word:
        glyph = _TIFINAGH["glyphs"][ch]
        gid = f"t{ord(ch):x}"
        d.define(f'<path id="{gid}" d="{glyph["d"]}"/>', key=gid)
        uses.append(f'<use href="#{gid}" x="{adv}"/>')
        adv += glyph["adv"]
    markup = (f'<g transform="translate({n(x)} {n(y)}) scale({k:.5f} {-k:.5f})" '
              f'fill="{d.c(fill)}">{"".join(uses)}</g>')
    return markup, adv * k


# ------------------------------------------------------------- illustration --

def arch(cx, base, half, top, jag, seed):
    """A rough rounded arch from (cx-half, base) over (cx, top) to (cx+half, base).

    Points on a sin^0.55 profile (steep walls, round roof), nudged by a fixed
    pattern so each stratum looks like rock, then smoothed as a Catmull-Rom curve.
    """
    steps = 12
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = cx - half + 2 * half * t
        y = base - (base - top) * math.sin(math.pi * t) ** 0.55
        if 0 < i < steps:
            r = ((i * 37 + seed * 11) % 7 - 3) / 3
            x, y = x + r * jag * 0.6, y + r * jag
        pts.append((x, y))
    path = f"M{n(pts[0][0])} {n(pts[0][1])}"
    for i in range(steps):
        p0, p1 = pts[max(i - 1, 0)], pts[i]
        p2, p3 = pts[i + 1], pts[min(i + 2, steps)]
        path += (f"C{n(p1[0] + (p2[0] - p0[0]) / 6)} {n(p1[1] + (p2[1] - p0[1]) / 6)} "
                 f"{n(p2[0] - (p3[0] - p1[0]) / 6)} {n(p2[1] - (p3[1] - p1[1]) / 6)} "
                 f"{n(p2[0])} {n(p2[1])}")
    return path


def cave(d):
    """Rock strata around a dark mouth; inside, a security key asking for a touch."""
    cx, base = 752, 176
    out = []
    glow = d.uid("glow")
    d.define(f'<radialGradient id="{glow}" cx="0.5" cy="0.78" r="0.62">'
             f'<stop offset="0" stop-color="{d.c("cyan")}" stop-opacity="0.22"/>'
             f'<stop offset="1" stop-color="{d.c("cyan")}" stop-opacity="0"/></radialGradient>')

    # strata, outside in
    for seed, (half, top, jag, color, op) in enumerate(((92, 30, 2.4, "line", 1),
                                                         (79, 44, 2.0, "box", 0.7),
                                                         (66, 58, 1.6, "box", 1))):
        out.append(f'<path d="{arch(cx, base, half, top, jag, seed)}" fill="none" '
                   f'stroke="{d.c(color)}" stroke-opacity="{op}" stroke-width="1.5"/>')
    mouth = arch(cx, base, 53, 72, 1.0, 3)
    out.append(f'<path d="{mouth} Z" fill="{d.c("bg_deep")}" stroke="{d.border_gradient()}" '
               f'stroke-width="1.5" stroke-linejoin="round"/>')
    out.append(f'<path d="{mouth} Z" fill="url(#{glow})"/>')
    out.append(f'<rect x="{cx - 112}" y="{base}" width="204" height="1" fill="{d.c("line")}"/>')
    for i, dx in enumerate((-106, -99, -60, 60, 70, 84)):  # rubble
        out.append(f'<rect x="{cx + dx}" y="{base - 3 - i % 2}" width="{3 + i % 3}" '
                   f'height="{3 + i % 2}" rx="1" fill="{d.c("box")}" opacity="0.8"/>')

    # the key, standing in the mouth, plugged into the floor
    kx, ky, kw, kh = cx - 15, 92, 30, 72
    out.append(f'<rect x="{kx + 9}" y="{ky + kh - 2}" width="12" height="{base - ky - kh + 2}" '
               f'rx="1.5" fill="{d.c("muted")}"/>')
    out.append(f'<rect x="{kx}" y="{ky}" width="{kw}" height="{kh}" rx="7" '
               f'fill="{d.c("bg_raised")}" stroke="{d.c("fg_dim")}" stroke-width="1.2"/>')
    out.append(f'<circle cx="{cx}" cy="{ky + 10}" r="4" fill="{d.c("bg_deep")}" '
               f'stroke="{d.c("fg_dim")}" stroke-width="1.2"/>')
    disc_y = ky + 40
    for i in range(2):  # the touch pulse
        out.append(f'<circle class="pulse p{i}" cx="{cx}" cy="{disc_y}" r="9" fill="none" '
                   f'stroke="{d.c("amber_bright")}" stroke-width="1.2"/>')
    out.append(f'<circle cx="{cx}" cy="{disc_y}" r="9" fill="{d.c("amber")}"/>')
    out.append(f'<circle cx="{cx}" cy="{disc_y}" r="5.5" fill="none" '
               f'stroke="{d.c("amber_bright")}" stroke-width="1.2" class="blink"/>')
    d.css(f".pulse{{opacity:0;transform-origin:{cx}px {disc_y}px;"
          f"animation:pulse 2.4s ease-out infinite}}.p1{{animation-delay:1.2s}}"
          f"@keyframes pulse{{0%{{opacity:.7;transform:scale(1)}}100%{{opacity:0;transform:scale(2.4)}}}}"
          f".blink{{animation:blink 2.4s ease-in-out infinite}}"
          f"@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}")

    # notes, left of the cave; the first one points at the touch disc
    nx = 532
    notes = [(disc_y + 3.5, "PIN + touch", "amber"), (disc_y + 21.5, "primary + backup", "fg_soft"),
             (disc_y + 39.5, "0 sockets", "cyan")]
    for y, label, color in notes:
        out.append(d.text(nx, y, label, 10.5, 400, color))
    out.append(f'<path d="M{n(nx + tw("PIN + touch", 10.5) + 7)} {disc_y}H{cx - 13}" '
               f'fill="none" stroke="{d.c("amber")}" stroke-opacity="0.55" stroke-width="1" '
               f'stroke-dasharray="2 3"/>')
    return "".join(out)


# --------------------------------------------------------------------- card --

def build(theme):
    card = CARD
    d = Doc(FULL_W, CARD_H, theme, f"{card['title']} ({NAME}) — {card['repo']}", card["body"])
    w, h = FULL_W - 2 * MARGIN, CARD_H - 2 * MARGIN
    d.add(d.window(MARGIN, MARGIN, w, h))
    d.add(d.grid(MARGIN, MARGIN, w, h, step=20, opacity=0.55))

    d.add(d.text(X0, TITLE_Y, card["title"], TITLE_SIZE, 800, "fg_bright"))
    name, name_w = tifinagh(d, X0 + tw(card["title"], TITLE_SIZE) + 14, TITLE_Y, NAME, 23, "violet")
    d.add(name)
    d.add(d.rich(X0, REPO_Y, [(card["repo"], "fg_dim"), ("  ·  Tamazight for ", "fg_dim"),
                              ("“cave”", "fg_soft")], REPO_SIZE))

    lines = wrap(card["body"], int((COPY_X1 - X0) / (0.6 * BODY_SIZE)))
    if len(lines) > 3:
        raise ValueError(f"efre: body needs {len(lines)} lines: {lines}")
    for i, line in enumerate(lines):
        d.add(d.text(X0, BODY_Y + i * BODY_LH, line, BODY_SIZE, 400, "fg"))
    d.add(chip_row(d, X0, CHIP_Y, card["chips"], card["accent"], x1=COPY_X1))

    d.add(cave(d))

    d.add(f'<rect x="{X0}" y="{CHIP_Y + CHIP_H + 11}" width="{X1 - X0}" height="1" '
          f'fill="{d.c("line")}"/>')
    x = X0
    for lang, color in card["langs"]:
        d.add(f'<circle cx="{n(x + 4.5)}" cy="{n(FOOT_Y - FOOT_SIZE * 0.36)}" r="4.5" fill="{d.c(color)}"/>')
        d.add(d.text(x + 15, FOOT_Y, lang, FOOT_SIZE, 400, "fg_soft"))
        x += 15 + tw(lang, FOOT_SIZE) + 22
    d.add(d.text(X1, FOOT_Y, card["link"], FOOT_SIZE, 700, card["accent"], anchor="end"))
    return d


def main():
    for theme in THEMES:
        path = build(theme).save(f"card-efre-{theme}.svg")
        print(f"  {os.path.basename(path):32} {os.path.getsize(path) / 1024:5.1f} KiB")


if __name__ == "__main__":
    main()
