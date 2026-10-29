#!/usr/bin/env python3
"""Draw the six project cards for the "selected work" grid.

    python3 tools/cards.py      writes assets/card-<slug>-{dark,light}.svg

Every card is CARD_W x CARD_H with the window inset by MARGIN, so two of them
side by side line up with the full-width panels above and below. All six share
one layout: title and repo top left, a small illustration top right, the copy
full width below, then a row of chips and a footer with the language and link.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from svgkit import CARD_H, CARD_W, MARGIN, THEMES, Doc, n, tw  # noqa: E402

PAD = 20                       # window edge -> content
X0 = MARGIN + PAD              # content left
X1 = CARD_W - MARGIN - PAD     # content right
TITLE_Y, TITLE_SIZE = 57, 22
REPO_Y, REPO_SIZE = 76, 11.5
BODY_Y, BODY_SIZE, BODY_LH = 104, 13, 18.5
CHIP_Y, CHIP_H, CHIP_SIZE, CHIP_PAD, CHIP_GAP = 155, 20, 11.5, 8, 6
FOOT_Y, FOOT_SIZE = 205, 12
ILLUS = (300, 28, X1, 88)      # x0, y0, x1, y1 of the illustration box

CARDS = [
    {
        "slug": "vaultless", "title": "vaultless", "repo": "Ak1ra00/vaultless",
        "body": "Deterministic password manager. Nothing is stored: each password "
                "is derived from a phrase in your head and a key printed on paper.",
        "chips": ["ristretto255", "OPRF", "HKDF", "PWA"],
        "lang": ("JavaScript", "amber"), "link": "↗ vaultless.space", "accent": "cyan",
    },
    {
        "slug": "quasar", "title": "QUASAR", "repo": "Ak1ra00/cc-q",
        "body": "Custom firmware that turns a Coldcard Q into a handheld console: "
                "a shoot-'em-up, guideline Tetris and neon PAC-MAN on its 320×240 LCD.",
        "chips": ["firmware", "C", "MicroPython", "30 fps"],
        "lang": ("C", "cyan"), "link": "↗ ak1ra00.github.io/cc-q", "accent": "violet",
    },
    {
        "slug": "tamagotchi", "title": "COLDCARD Tamagotchi", "repo": "Ak1ra00/CC",
        "body": "A retired Bitcoin signing device that now keeps a small creature "
                "alive. Genes come from the hardware TRNG; the microSD card is the pet.",
        "chips": ["MicroPython", "STM32", "NFC", "TRNG"],
        "lang": ("MicroPython", "green"), "link": "→ repo", "accent": "amber",
    },
    {
        "slug": "deepsea", "title": "Atlantis DeepSea", "repo": "Ak1ra00/hw-flash",
        "body": "BIP85 hardware password manager for the LilyGO T-Display (ESP32). "
                "One seed, endless deterministic passwords, sent over BLE.",
        "chips": ["ESP32", "BIP85", "BLE", "PlatformIO"],
        "lang": ("C++", "violet"), "link": "→ repo", "accent": "cyan",
    },
    {
        "slug": "oracle", "title": "Oracle", "repo": "Ak1ra00/oracle",
        "body": "A complete Omarchy desktop theme. Its six 4K wallpapers are "
                "rendered from real elliptic-curve and OPRF math.",
        "chips": ["Hyprland", "Omarchy", "cairo", "Lua"],
        "lang": ("Python", "blue"), "link": "→ repo", "accent": "violet",
    },
    {
        "slug": "opencare", "title": "OpenCare", "repo": "Ak1ra00/opencare",
        "body": "Windows 10/11 maintenance toolkit: checkup, cleanup, startup and "
                "privacy tools. Every fix is previewed and reversible.",
        "chips": ["Python 3.12", "PySide6", "Qt 6", "undo"],
        "lang": ("Python", "blue"), "link": "→ repo", "accent": "amber",
    },
]

BY_SLUG = {c["slug"]: c for c in CARDS}


def wrap(text, width):
    """Greedy word wrap to `width` characters."""
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        lines.append(line)
    return lines


def rects_path(cells, x0, y0, px):
    """One path for a set of (col, row) cells, merging horizontal runs."""
    rows = {}
    for col, row in cells:
        rows.setdefault(row, []).append(col)
    out = []
    for row, cols in sorted(rows.items()):
        cols.sort()
        start = prev = cols[0]
        for col in cols[1:] + [None]:
            if col is not None and col == prev + 1:
                prev = col
                continue
            out.append(f"M{n(x0 + start * px)} {n(y0 + row * px)}h{n((prev - start + 1) * px)}"
                       f"v{n(px)}h{n(-(prev - start + 1) * px)}z")
            if col is not None:
                start = prev = col
    return "".join(out)


def sprite(rows, x0, y0, px, fill, cls=None):
    cells = [(c, r) for r, line in enumerate(rows) for c, ch in enumerate(line) if ch == "X"]
    extra = f' class="{cls}"' if cls else ""
    return f'<path d="{rects_path(cells, x0, y0, px)}" fill="{fill}"{extra}/>'


# ------------------------------------------------------------ illustrations --

def illus_vaultless(d):
    """A paper oracle: a QR-ish square of printed amber codes, a cyan scan line."""
    px, size = 2, 21
    side = px * size
    x0 = ILLUS[2] - side - 6
    y0 = ILLUS[1] + 5
    seed = hashlib.sha256(b"vaultless paper oracle").digest() * 4
    cells = set()

    def finder(cx, cy):
        for r in range(7):
            for c in range(7):
                edge = r in (0, 6) or c in (0, 6)
                core = 2 <= r <= 4 and 2 <= c <= 4
                if edge or core:
                    cells.add((cx + c, cy + r))

    finder(0, 0)
    finder(size - 7, 0)
    finder(0, size - 7)
    reserved = lambda c, r: (c < 8 and r < 8) or (c >= size - 8 and r < 8) or (c < 8 and r >= size - 8)
    bit = 0
    for r in range(size):
        for c in range(size):
            if reserved(c, r):
                continue
            if r == 6 or c == 6:
                if (r + c) % 2 == 0:
                    cells.add((c, r))
                continue
            if seed[bit // 8] >> (bit % 8) & 1:
                cells.add((c, r))
            bit += 1
    sheet_pad = 4
    sx, sy = x0 - sheet_pad, y0 - sheet_pad
    sw, sh = side + 2 * sheet_pad, side + 2 * sheet_pad + 9
    paper = "bg_deep" if d.theme == "dark" else "bg_raised"
    out = [
        f'<rect x="{n(sx)}" y="{n(sy)}" width="{n(sw)}" height="{n(sh)}" rx="3" '
        f'fill="{d.c(paper)}" stroke="{d.c("amber")}" stroke-opacity="0.55" stroke-width="1"/>',
        f'<path d="{rects_path(cells, x0, y0, px)}" fill="{d.c("amber")}"/>',
        d.text(sx + sw / 2, sy + sh - 4, "VLT1-7QK3", 6, 700, "amber", anchor="middle"),
    ]
    # the scan line sweeps down over the code and back
    gid = d.uid("scan")
    d.define(f'<linearGradient id="{gid}" x1="0" x2="1">'
             f'<stop offset="0" stop-color="{d.c("cyan")}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{d.c("cyan")}"/>'
             f'<stop offset="1" stop-color="{d.c("cyan")}" stop-opacity="0"/></linearGradient>')
    out.append(f'<g class="scan"><rect x="{n(sx - 6)}" y="{n(y0 + side * 0.55)}" width="{n(sw + 12)}" '
               f'height="1.6" fill="url(#{gid})"/>'
               f'<rect x="{n(sx - 6)}" y="{n(y0 + side * 0.55 - 3)}" width="{n(sw + 12)}" height="7.6" '
               f'fill="url(#{gid})" opacity="0.18"/></g>')
    up, down = n(side * 0.55), n(side * 0.42)
    d.css(f"@keyframes scan{{0%,100%{{transform:translateY(-{up}px)}}50%{{transform:translateY({down}px)}}}}")
    d.css(".scan{animation:scan 3.6s ease-in-out infinite}")
    # the derivation, as a margin note to the left of the sheet
    note_x = sx - 12
    out.append(d.text(note_x, y0 + 13, "S = k·P", 11, 700, "cyan", anchor="end"))
    out.append(d.text(note_x, y0 + 29, "P ← phrase", 9.5, 400, "fg_dim", anchor="end"))
    out.append(d.text(note_x, y0 + 43, "k ← paper", 9.5, 400, "fg_dim", anchor="end"))
    return "".join(out)


SHIP = ["XXX......",
        ".XXXX....",
        "..XXXXXX.",
        "XXXXXXXXX",
        "..XXXXXX.",
        ".XXXX....",
        "XXX......"]
DRONE = ["..X...X..",
         "...XXX...",
         ".XXXXXXX.",
         "XX.XXX.XX",
         "XXXXXXXXX",
         "X.X...X.X",
         "...X.X..."]


def illus_quasar(d):
    """A pixel ship firing on a drone, under a few stars."""
    px = 3
    bx0, by0, bx1, by1 = ILLUS
    ship_x, ship_y = bx0 + 8, by0 + 24
    drone_x, drone_y = bx1 - 9 * px - 2, ship_y
    out = []
    stars = [(bx0 + 22, by0 + 6), (bx0 + 52, by0 + 2), (bx0 + 70, by0 + 48), (bx0 + 96, by0 + 56),
             (bx0 + 8, by0 + 52), (bx0 + 40, by0 + 60), (bx0 + 86, by0 + 4)]
    for i, (sx, sy) in enumerate(stars):
        out.append(f'<rect class="tw{i % 3}" x="{sx}" y="{sy}" width="1.7" height="1.7" '
                   f'fill="{d.c("fg_dim")}"/>')
    out.append(sprite(SHIP, ship_x, ship_y, px, d.c("cyan")))
    out.append(f'<g class="flame"><rect x="{n(ship_x - 2 * px)}" y="{n(ship_y + 3 * px)}" '
               f'width="{n(2 * px)}" height="{n(px)}" fill="{d.c("orange")}"/><rect x="{n(ship_x - px)}" '
               f'y="{n(ship_y + 2 * px)}" width="{n(px)}" height="{n(3 * px)}" fill="{d.c("amber")}" '
               f'opacity="0.8"/></g>')
    out.append(sprite(DRONE, drone_x, drone_y, px, d.c("violet"), cls="drone"))
    # bullets ride the ship's nose line toward the drone, a third of the lane apart
    lane_y = ship_y + 3 * px
    start = ship_x + 9 * px + 2
    span = drone_x - 4 - 2 * px - start
    for i, f in enumerate((0.2, 0.53, 0.86)):
        out.append(f'<rect class="shot{i}" x="{n(start + span * f)}" y="{n(lane_y)}" '
                   f'width="{n(2 * px)}" height="{n(px)}" fill="{d.c("amber_bright")}"/>')
        d.css(f"@keyframes shot{i}{{0%{{transform:translateX(-{n(span * f)}px);opacity:0}}"
              f"8%,92%{{opacity:1}}100%{{transform:translateX({n(span * (1 - f))}px);opacity:0}}}}"
              f".shot{i}{{animation:shot{i} 1.5s steps(12) infinite;animation-delay:-{n(1.5 * f)}s}}")
    d.css("@keyframes hit{0%,85%,100%{opacity:1}90%{opacity:.35}}"
          ".drone{animation:hit .5s steps(1) infinite}"
          "@keyframes tw{0%,100%{opacity:.9}50%{opacity:.25}}"
          ".tw0{animation:tw 2.2s steps(2) infinite}.tw1{animation:tw 3.1s steps(2) infinite}"
          ".tw2{animation:tw 2.7s steps(2) infinite .6s}"
          "@keyframes flame{0%,100%{opacity:1}50%{opacity:.4}}"
          ".flame{animation:flame .3s steps(1) infinite}")
    return "".join(out)


CREATURE = ["...XXXXX...",
            "..XXXXXXX..",
            ".XXXXXXXXX.",
            ".XX.XXX.XX.",
            "XXX.XXX.XXX",
            "XXXXXXXXXXX",
            "XXXXX.XXXXX",
            ".XXXXXXXXX.",
            "..XXXXXXX..",
            "..X.....X.."]


def illus_tamagotchi(d):
    """The pet screen: F/J/Z gauges on the left, the creature bobbing on the right."""
    bx0, by0, bx1, by1 = ILLUS
    sx, sy, sw, sh = bx0 + 6, by0 + 2, bx1 - bx0 - 6, by1 - by0 - 4
    out = [f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="5" fill="{d.c("bg_deep")}" '
           f'stroke="{d.c("line")}" stroke-width="1"/>']
    levels = (("F", 3), ("J", 2), ("Z", 4))
    for i, (label, level) in enumerate(levels):
        gy = sy + 14 + i * 15
        out.append(d.text(sx + 8, gy + 4.5, label, 8, 700, "amber"))
        for s in range(4):
            on = s < level
            out.append(f'<rect x="{n(sx + 17 + s * 5.5)}" y="{n(gy - 3)}" width="4" height="7.5" rx="0.8" '
                       f'fill="{d.c("amber" if on else "line")}"/>')
    px = 3.4
    cx = sx + sw - 11 * px - 10
    cy = sy + sh - 10 * px - 6
    pet = "fg_bright" if d.theme == "dark" else "fg"
    out.append(f'<g class="bob">{sprite(CREATURE, cx, cy, px, d.c(pet))}'
               f'<g class="lids"><rect x="{n(cx + 3 * px)}" y="{n(cy + 3 * px)}" width="{n(px)}" '
               f'height="{n(2 * px)}" fill="{d.c(pet)}"/><rect x="{n(cx + 7 * px)}" y="{n(cy + 3 * px)}" '
               f'width="{n(px)}" height="{n(2 * px)}" fill="{d.c(pet)}"/></g></g>')
    out.append(f'<rect x="{n(cx - 4)}" y="{n(cy + 10 * px + 1)}" width="{n(11 * px + 8)}" height="1" '
               f'fill="{d.c("line")}"/>')
    d.css("@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
          ".bob{animation:bob 1.6s steps(2) infinite}"
          "@keyframes blink{0%,92%,100%{opacity:0}94%,98%{opacity:1}}"
          ".lids{opacity:0;animation:blink 4.8s steps(1) infinite}")
    return "".join(out)


def illus_deepsea(d):
    """A LilyGO T-Display: masked password on the TFT, BLE beside it."""
    bx0, by0, bx1, by1 = ILLUS
    bw, bh = 96, 46
    x, y = bx1 - bw, by0 + 7
    board = "selection" if d.theme == "dark" else "bg_deep"
    out = [
        f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="5" fill="{d.c(board)}" '
        f'stroke="{d.c("box")}" stroke-width="1"/>',
        # USB-C on the left edge, two buttons on the right
        f'<rect x="{x - 4}" y="{y + bh / 2 - 5}" width="6" height="10" rx="2" fill="{d.c("fg_dim")}"/>',
        f'<rect x="{x + bw - 9}" y="{y + 8}" width="5" height="5" rx="1" fill="{d.c("fg_dim")}"/>',
        f'<rect x="{x + bw - 9}" y="{y + bh - 13}" width="5" height="5" rx="1" fill="{d.c("fg_dim")}"/>',
    ]
    tx, ty, tw_, th = x + 8, y + 6, 66, bh - 12
    out.append(f'<rect x="{tx}" y="{ty}" width="{tw_}" height="{th}" rx="2" fill="{d.c("bg_deep")}" '
               f'stroke="{d.c("line")}" stroke-width="0.8"/>')
    out.append(d.text(tx + 5, ty + 10, "slot 0042", 6.5, 700, "fg_dim"))
    bx, by = tx + tw_ - 8, ty + 7.5
    out.append(f'<path class="ble" d="M{n(bx - 2.5)} {n(by - 2.2)}l5 4.4l-2.5 2.3v-9l2.5 2.3l-5 4.4" '
               f'fill="none" stroke="{d.c("violet")}" stroke-width="1.1" stroke-linejoin="round" '
               f'stroke-linecap="round"/>')
    for i in range(7):
        out.append(f'<circle class="pw pw{i}" cx="{n(tx + 8 + i * 7.6)}" cy="{n(ty + th - 10)}" r="2.3" '
                   f'fill="{d.c("cyan")}"/>')
    d.css("@keyframes pw{0%,6%{opacity:0}12%,88%{opacity:1}100%{opacity:0}}"
          + "".join(f".pw{i}{{animation:pw 4s steps(1) infinite;animation-delay:{n(0.18 * i)}s}}" for i in range(7))
          + "@keyframes ble{0%,100%{opacity:1}50%{opacity:.3}}.ble{animation:ble 1.4s ease-in-out infinite}")
    return "".join(out)


def illus_oracle(d):
    """A focused Hyprland window holding a real P + Q = R, beside the theme's three inks."""
    bx0, by0, bx1, by1 = ILLUS
    ww, wh = 74, 54
    wx, wy = bx1 - ww - 22, by0 + 3
    lo, hi = -2.279, 2.45                     # the real root of x^3 - 3x + 5 is -2.279
    sx = (ww - 16) / (hi - lo)
    sy = 5.6

    def at(xv, yv):
        return wx + 8 + (xv - lo) * sx, wy + wh / 2 - yv * sy

    def y_of(xv):
        return max(xv ** 3 - 3 * xv + 5, 0) ** 0.5

    out = [f'<rect x="{wx + 2}" y="{wy + 2}" width="{ww - 4}" height="{wh - 4}" rx="6" fill="{d.c("glow")}" '
           f'opacity="{d.p["glow_opacity"]}" filter="url(#halo)"/>',
           f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="6" fill="{d.c("bg_deep")}" '
           f'stroke="{d.border_gradient()}" stroke-width="1.4"/>']
    xs = [lo + (hi - lo) * (i / 80) ** 1.6 for i in range(81)]   # denser near the turn
    upper = [at(xv, y_of(xv)) for xv in xs]
    lower = [at(xv, -y_of(xv)) for xv in xs]
    path = "M" + " ".join(f"{n(a)} {n(b)}" for a, b in reversed(upper)) + " " + \
           " ".join(f"{n(a)} {n(b)}" for a, b in lower[1:])
    out.append(f'<path d="{path}" fill="none" stroke="{d.c("cyan")}" stroke-width="1.3" '
               f'stroke-linejoin="round"/>')
    # the group law, exactly: the chord through P and Q meets the curve at -R; R is its mirror
    xp, xq = -1.8, 0.4
    yp, yq = y_of(xp), y_of(xq)
    lam = (yq - yp) / (xq - xp)
    xr = lam * lam - xp - xq
    ynr = lam * (xr - xp) + yp                # -R sits on the chord
    p, q, nr, r = at(xp, yp), at(xq, yq), at(xr, ynr), at(xr, -ynr)
    ext = 0.32
    a = at(xp - ext, yp - lam * ext)
    b = at(xr + ext, ynr + lam * ext)
    out.append(f'<path d="M{n(a[0])} {n(a[1])}L{n(b[0])} {n(b[1])}" stroke="{d.c("violet")}" stroke-width="1"/>')
    out.append(f'<path d="M{n(nr[0])} {n(nr[1])}V{n(r[1])}" stroke="{d.c("fg_dim")}" stroke-width="0.9" '
               f'stroke-dasharray="2 2"/>')
    for pt in (p, q, nr):
        out.append(f'<circle cx="{n(pt[0])}" cy="{n(pt[1])}" r="1.9" fill="{d.c("violet")}"/>')
    out.append(f'<circle class="pt" cx="{n(r[0])}" cy="{n(r[1])}" r="2.5" fill="{d.c("amber")}"/>')
    # swatches stacked to the right of the window
    for i, tok in enumerate(("cyan", "violet", "amber")):
        out.append(f'<rect x="{bx1 - 12}" y="{wy + 5 + i * 16}" width="12" height="12" '
                   f'rx="2.5" fill="{d.c(tok)}"/>')
    d.define('<filter id="halo" x="-10%" y="-25%" width="120%" height="150%">'
             '<feGaussianBlur stdDeviation="7"/></filter>', key="halo")
    d.css("@keyframes pt{0%,100%{opacity:1}50%{opacity:.35}}.pt{animation:pt 2.4s ease-in-out infinite}")
    return "".join(out)


def illus_opencare(d):
    """A health ring with a check; a highlight orbits like a scan in progress."""
    bx0, by0, bx1, by1 = ILLUS
    r = 23
    cx, cy = bx1 - r - 12, (by0 + by1) / 2
    circ = 2 * 3.14159265 * r
    out = [f'<circle cx="{cx}" cy="{n(cy)}" r="{r}" fill="none" stroke="{d.c("line")}" stroke-width="5"/>',
           f'<circle cx="{cx}" cy="{n(cy)}" r="{r}" fill="none" stroke="{d.c("green")}" stroke-width="5" '
           f'stroke-linecap="round" stroke-dasharray="{n(circ * 0.82)} {n(circ)}" '
           f'transform="rotate(-90 {cx} {n(cy)})"/>',
           f'<path d="M{cx - 9} {n(cy + 0.5)}l6 6l12 -12.5" fill="none" stroke="{d.c("green")}" '
           f'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>',
           f'<g class="orbit"><circle cx="{cx}" cy="{n(cy - r)}" r="3.4" fill="{d.c("amber_bright")}"/></g>']
    out.append(d.text(cx - r - 14, cy - 8, "0 issues", 9, 700, "green", anchor="end"))
    out.append(d.text(cx - r - 14, cy + 6, "undo ready", 8.5, 400, "fg_dim", anchor="end"))
    d.css("@keyframes orbit{to{transform:rotate(360deg)}}"
          f".orbit{{transform-origin:{cx}px {n(cy)}px;animation:orbit 6s linear infinite}}")
    return "".join(out)


ILLUSTRATIONS = {
    "vaultless": illus_vaultless, "quasar": illus_quasar, "tamagotchi": illus_tamagotchi,
    "deepsea": illus_deepsea, "oracle": illus_oracle, "opencare": illus_opencare,
}


# ------------------------------------------------------------------- cards --

def chip_row(d, x, y, chips, accent):
    out = []
    for label in chips:
        w = tw(label, CHIP_SIZE) + 2 * CHIP_PAD
        out.append(f'<rect x="{n(x)}" y="{y}" width="{n(w)}" height="{CHIP_H}" rx="{CHIP_H / 2}" '
                   f'fill="{d.c(accent)}" fill-opacity="0.08" stroke="{d.c(accent)}" '
                   f'stroke-opacity="0.55" stroke-width="1"/>')
        out.append(d.text(x + CHIP_PAD, y + CHIP_H / 2 + CHIP_SIZE * 0.36, label, CHIP_SIZE, 400,
                          accent if d.theme == "light" else f"{accent}_bright"))
        x += w + CHIP_GAP
    if x - CHIP_GAP > X1:
        raise ValueError(f"chips overflow by {x - CHIP_GAP - X1:.1f}px: {chips}")
    return "".join(out)


def build(slug, theme):
    card = BY_SLUG[slug]
    d = Doc(CARD_W, CARD_H, theme, f"{card['title']} — {card['repo']}", card["body"])
    w, h = CARD_W - 2 * MARGIN, CARD_H - 2 * MARGIN
    d.add(d.window(MARGIN, MARGIN, w, h))
    d.add(d.grid(MARGIN, MARGIN, w, h, step=20, opacity=0.55))
    d.add(d.text(X0, TITLE_Y, card["title"], TITLE_SIZE, 800, "fg_bright"))
    if X0 + tw(card["title"], TITLE_SIZE) > ILLUS[0] - 6:
        raise ValueError(f"{slug}: title runs into the illustration")
    d.add(d.text(X0, REPO_Y, card["repo"], REPO_SIZE, 400, "fg_dim"))
    d.add(ILLUSTRATIONS[slug](d))
    lines = wrap(card["body"], int((X1 - X0) / (0.6 * BODY_SIZE)))
    if len(lines) > 3:
        raise ValueError(f"{slug}: body needs {len(lines)} lines: {lines}")
    for i, line in enumerate(lines):
        d.add(d.text(X0, BODY_Y + i * BODY_LH, line, BODY_SIZE, 400, "fg"))
    d.add(chip_row(d, X0, CHIP_Y, card["chips"], card["accent"]))
    d.add(f'<rect x="{X0}" y="{CHIP_Y + CHIP_H + 11}" width="{X1 - X0}" height="1" '
          f'fill="{d.c("line")}"/>')
    lang, color = card["lang"]
    d.add(f'<circle cx="{X0 + 4.5}" cy="{n(FOOT_Y - FOOT_SIZE * 0.36)}" r="4.5" fill="{d.c(color)}"/>')
    d.add(d.text(X0 + 15, FOOT_Y, lang, FOOT_SIZE, 400, "fg_soft"))
    d.add(d.text(X1, FOOT_Y, card["link"], FOOT_SIZE, 700, card["accent"], anchor="end"))
    return d


def main():
    for card in CARDS:
        for theme in THEMES:
            path = build(card["slug"], theme).save(f"card-{card['slug']}-{theme}.svg")
            print(f"  {os.path.basename(path):32} {os.path.getsize(path) / 1024:5.1f} KiB")


if __name__ == "__main__":
    main()
