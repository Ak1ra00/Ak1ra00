#!/usr/bin/env python3
"""Project field notes: two lead features, four supporting builds, two layouts.

    python3 tools/cards.py

The compact SVGs are selected by the README's <picture> media queries. All
illustration and type is self-contained SVG, with no runtime dependencies.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from design import arrow, cross, display, display_width, document, label, rect, rule
from svgkit import THEMES, n
import project_art


CARDS = [
    {
        "slug": "vaultless", "title": "vaultless", "repo": "Ak1ra00/vaultless",
        "number": "01", "category": "APPLIED CRYPTOGRAPHY", "accent": "accent",
        "headline": ("A phrase. A paper key.", "No password vault."),
        "body": "Passwords derived from a phrase and a paper key. No passwords stored.",
        "detail": "ristretto255 OPRF · HKDF-SHA256",
        "stack": "JAVASCRIPT / PWA", "link": "vaultless.space", "featured": True,
    },
    {
        "slug": "quasar", "title": "QUASAR", "repo": "Ak1ra00/cc-q",
        "number": "02", "category": "FIRMWARE / ARCADE", "accent": "violet",
        "headline": ("A signing device.", "An arcade afterlife."),
        "body": "A Coldcard Q repurposed as a dedicated three-game console, with custom firmware and no Bitcoin code.",
        "detail": "Shoot-'em-up. Tetris. Neon PAC-MAN.",
        "stack": "C / MICROPYTHON", "link": "Ak1ra00/cc-q", "featured": True,
    },
    {
        "slug": "tamagotchi", "title": "COLDCARD Tamagotchi", "repo": "Ak1ra00/CC",
        "number": "03", "category": "HARDWARE / SECOND LIVES", "accent": "amber",
        "headline": ("A retired signing device.", "A creature worth keeping alive."),
        "body": "A retired signing device. A creature worth keeping alive. Hardware TRNG genetics; the microSD card carries the pet.",
        "detail": "Hardware TRNG genes. The microSD is the pet.",
        "stack": "MICROPYTHON / STM32", "link": "Ak1ra00/CC", "featured": False,
    },
    {
        "slug": "deepsea", "title": "Atlantis DeepSea", "repo": "Ak1ra00/hw-flash",
        "number": "04", "category": "EMBEDDED / PASSWORDS", "accent": "blue",
        "headline": ("One seed. Passwords on demand.", "Delivered over BLE."),
        "body": "A BIP85 password manager on a LilyGO T-Display. An encrypted BIP39 seed derives passwords on demand, delivered over BLE.",
        "detail": "BIP39 → BIP85 · LilyGO T-Display",
        "stack": "C++ / ESP32 / BLE", "link": "Ak1ra00/hw-flash", "featured": False,
    },
    {
        "slug": "oracle", "title": "Oracle", "repo": "Ak1ra00/oracle",
        "number": "05", "category": "DESKTOP / GENERATIVE MATH", "accent": "violet",
        "headline": ("Mathematics,", "across the entire desktop."),
        "body": "An Omarchy and Hyprland theme with six generated 4K wallpapers drawn from real elliptic-curve and OPRF mathematics.",
        "detail": "Six 4K wallpapers. Real elliptic-curve math.",
        "stack": "PYTHON / HYPRLAND / OMARCHY", "link": "Ak1ra00/oracle", "featured": False,
    },
    {
        "slug": "opencare", "title": "OpenCare", "repo": "Ak1ra00/opencare",
        "number": "06", "category": "DESKTOP / CARE & REPAIR", "accent": "accent",
        "headline": ("Preview the fix.", "Keep the undo."),
        "body": "A Windows maintenance toolkit with read-only scans, previewed changes, backups and an undo history.",
        "detail": "Windows 10/11. Changes you can inspect.",
        "stack": "PYTHON / PYSIDE6", "link": "Ak1ra00/opencare", "featured": False,
    },
]

BY_SLUG = {card["slug"]: card for card in CARDS}


def pixels(d, rows, x, y, size, color="accent"):
    path = []
    for row, cells in enumerate(rows):
        for col, cell in enumerate(cells):
            if cell != ".":
                path.append(f"M{n(x + col*size)} {n(y + row*size)}h{size}v{size}h-{size}z")
    return f'<path d="{"".join(path)}" fill="{d.c(color)}"/>'


def pet_art(d):
    """A retired keypad wallet and its removable microSD creature."""
    out = [rule(d, 12, 163, 258, 163), cross(d, 12, 16), cross(d, 258, 16)]
    out.append('<g transform="translate(39 7) rotate(-5 70 80)">')
    out.append(rect(d, 5, 5, 130, 151, "bg_deep", "line", 8))
    out.append(rect(d, 0, 0, 130, 151, "bg_raised", "box", 8))
    out.append(label(d, 12, 16, "COLDCARD", 7, "fg_dim"))
    out.append(rect(d, 12, 25, 106, 61, "bg_deep", "line", 2))
    out.append(label(d, 19, 38, "PET", 7, "amber"))
    creature = ["...XXXXX...", "..XXXXXXX..", ".XXXXXXXXX.", ".XX.XXX.XX.",
                "XXX.XXX.XXX", "XXXXXXXXXXX", "XXXXX.XXXXX", ".XXXXXXXXX.",
                "..XXXXXXX..", "..X.....X.."]
    out.append(f'<g class="pet-bob">{pixels(d, creature, 68, 43, 3, "amber")}</g>')
    out.append(rule(d, 20, 72, 51, 72, "line"))
    out.append(label(d, 20, 62, "TRNG", 7, "fg_dim"))
    for row in range(3):
        for col in range(3):
            out.append(rect(d, 18 + col * 33, 98 + row * 14, 27, 9, "bg_deep", "line", 2))
    out.append('</g>')
    out.append(f'<path d="M202 79h27l14 14v50h-41z" fill="{d.c("bg_raised")}" stroke="{d.c("amber")}"/>')
    for i in range(4):
        out.append(rect(d, 208 + i * 7, 91, 4, 10, "amber"))
    out.append(label(d, 222, 120, "PET", 9, "amber", "middle"))
    out.append(label(d, 222, 134, "microSD", 5.5, "fg_dim", "middle"))
    out.append(f'<path d="M173 84h13v36h12" fill="none" stroke="{d.c("muted")}" stroke-dasharray="3 4"/>')
    d.css('@keyframes petbob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}'
          '.pet-bob{animation:petbob 2.4s steps(2) infinite}')
    return ''.join(out)


def deepsea_art(d):
    """A pin-lined LilyGO board, its display, and the BLE transmission path."""
    out = [cross(d, 12, 16), cross(d, 258, 16), rule(d, 12, 163, 258, 163)]
    out.append('<g transform="translate(28 36) rotate(-6 105 50)">')
    for i in range(12):
        for y in (2, 104):
            out.append(rect(d, 12 + i * 13, y, 7, 11, "amber"))
    out.append(rect(d, 0, 13, 181, 91, "bg_raised", "box", 7))
    out.append(rect(d, -5, 43, 13, 28, "fg_dim", "line", 3))
    out.append(rect(d, -6, 49, 9, 16, "bg_deep", radius=2))
    out.append(rect(d, 15, 25, 132, 66, "bg_deep", "line", 2))
    out.append(label(d, 25, 39, "DEEPSEA", 8, "blue"))
    out.append(label(d, 25, 54, "BIP85 / PASSWORD", 6.5, "fg_dim"))
    for i in range(9):
        out.append(f'<circle cx="{29+i*11}" cy="70" r="2.5" fill="{d.c("accent")}"/>')
    for y in (31, 72):
        out.append(rect(d, 157, y, 13, 13, "bg_deep", "muted", 2))
    out.append('</g>')
    out.append(f'<path d="M229 53l18 18l-9 9V44l9 9l-18 18" fill="none" stroke="{d.c("blue")}" stroke-width="1.7"/>')
    out.append(f'<path d="M254 48q15 15 0 30m-5-25q10 10 0 20" fill="none" stroke="{d.c("blue")}" stroke-opacity=".5"/>')
    out.append(label(d, 241, 106, "BLE", 8, "fg_dim", "middle"))
    return ''.join(out)


def oracle_art(d):
    """Layered desktop windows framing a computed elliptic curve."""
    out = [cross(d, 12, 16), cross(d, 258, 16), rule(d, 12, 163, 258, 163)]
    for x, y, color in ((43, 24, 'violet'), (30, 35, 'amber'), (17, 46, 'accent')):
        out.append(rect(d, x, y, 211, 104, "bg_deep", color, 3))
    out.append(rule(d, 17, 61, 228, 61, "line"))
    out.append(label(d, 27, 56, "ORACLE / y² = x³ − 3x + 5", 6.5, "fg_dim"))
    for x in range(28, 220, 16):
        out.append(rule(d, x, 68, x, 143, "grid"))
    for y in range(75, 143, 16):
        out.append(rule(d, 25, y, 220, y, "grid"))
    def f(x):
        return x*x*x - 3*x + 5
    lo, hi = -3.0, -2.0
    for _ in range(60):
        mid = (lo+hi)/2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    root = (lo+hi)/2
    xs = [root+(2.3-root)*(i/100)**2 for i in range(101)]
    points = [(117+x*31, 105-math.sqrt(max(0, f(x)))*8) for x in reversed(xs)]
    points += [(117+x*31, 105+math.sqrt(max(0, f(x)))*8) for x in xs[1:]]
    path = 'M'+'L'.join(f'{n(x)} {n(y)}' for x,y in points)
    out.append(f'<path d="{path}" fill="none" stroke="{d.c("accent")}" stroke-width="1.7"/>')
    px, qx = -1.7, 1.4
    py, qy = -math.sqrt(f(px)), math.sqrt(f(qx))
    slope = (qy-py)/(qx-px)
    rx = slope*slope-px-qx
    negative_ry = py+slope*(rx-px)
    assert abs(negative_ry**2-f(rx)) < 1e-9
    p = (117+px*31, 105-py*8)
    q = (117+qx*31, 105-qy*8)
    negative_r = (117+rx*31, 105-negative_ry*8)
    r = (negative_r[0], 105+negative_ry*8)
    out.append(rule(d, *p, *negative_r, 'violet'))
    out.append(rule(d, *negative_r, *r, 'muted', 'stroke-dasharray="2 3"'))
    for (x,y),c in ((p,'accent'),(q,'violet'),(r,'amber')):
        out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{d.c(c)}"/>')
    for i,color in enumerate(('accent','violet','amber')):
        out.append(rect(d, 242, 69+i*25, 16, 16, color))
    return ''.join(out)


def care_art(d):
    """Previewable change sets, with an explicit route back to the original."""
    out = [cross(d, 12, 16), cross(d, 258, 16), rule(d, 12, 163, 258, 163)]
    out.append(rect(d, 29, 31, 173, 114, "bg_deep", "line", 4))
    out.append(rect(d, 39, 23, 173, 114, "bg_raised", "box", 4))
    out.append(label(d, 52, 42, "CHANGE PREVIEW", 8, "fg_dim"))
    out.append(rule(d, 51, 51, 199, 51))
    for row, txt in enumerate(('SCAN', 'PREVIEW', 'UNDO')):
        y = 67+row*24
        out.append(rect(d, 52, y-8, 11, 11, 'bg_deep', 'line', 1))
        if row < 2:
            out.append(f'<path d="M55 {y-3}l2 2l4-5" fill="none" stroke="{d.c("accent")}" stroke-width="1.4"/>')
        out.append(label(d, 72, y, txt, 8, 'fg_soft'))
        out.append(rule(d, 133, y-4, 194-row*12, y-4, 'line', 'stroke-width="3"'))
    out.append(rect(d, 173, 95, 61, 47, 'signal', radius=3))
    out.append(f'<path d="M191 111h16a10 10 0 0 1 0 20h-13m-3-20l7-7m-7 7l7 7" '
               f'fill="none" stroke="{d.c("signal_ink")}" stroke-width="2"/>')
    return ''.join(out)


ART = {
    "vaultless": project_art.vaultless, "quasar": project_art.quasar,
    "tamagotchi": pet_art, "deepsea": deepsea_art,
    "oracle": oracle_art, "opencare": care_art,
}


def header(d, card, w, compact):
    x = 24 if compact else 32
    size = 10 if compact else 11
    out = [label(d, x, 31, f'{card["number"]} / {card["category"]}', size, card['accent'])]
    out.append(arrow(d, w-x-12, 19, 12, card['accent']))
    out.append(rule(d, x, 49, w-x, 49))
    return ''.join(out)


def footer(d, card, w, h, compact):
    x = 24 if compact else 32
    out = [rule(d, x, h-50, w-x, h-50)]
    out.append(label(d, x, h-25, card['stack'], 9.5 if compact else 10, 'fg_dim'))
    if not compact:
        out.append(label(d, w-x, h-25, card['link'], 11, card['accent'], 'end'))
    else:
        out.append(arrow(d, w-x-10, h-34, 10, card['accent']))
    return ''.join(out)


def build(slug, theme, compact=False):
    card = BY_SLUG[slug]
    featured = card['featured']
    w = 440 if compact else 880
    h = (552 if featured else 444) if compact else (384 if featured else 268)
    x = 24 if compact else 32
    d = document(w, h, theme, f'{card["title"]} — {card["repo"]}', card['body'])
    d.add(rect(d, .5, .5, w-1, h-1, 'bg', 'line'))
    d.add(header(d, card, w, compact))

    if featured:
        title_size = 61 if not compact else 55
        d.add(display(d, x, 121 if not compact else 115, card['title'], title_size))
        headline_size = 29 if not compact else 27
        y = 173 if not compact else 158
        for i, line in enumerate(card['headline']):
            d.add(display(d, x, y+i*36, line, headline_size, 'fg'))
        d.add(label(d, x, 254 if not compact else 226, card['detail'], 12 if not compact else 10.5, 'fg_dim'))
        if compact:
            d.add(f'<g transform="translate(40 233) scale(.93)">{ART[slug](d)}</g>')
        else:
            d.add(rule(d, 485, 72, 485, h-73))
            d.add(f'<g transform="translate(500 62)">{ART[slug](d)}</g>')
    else:
        title_size = 30 if not compact else 29
        if compact and slug == 'tamagotchi':
            title_size = 28
        if display_width(card['title'], title_size) > (w-2*x if compact else 500):
            raise ValueError(f'{slug}: title is too wide')
        d.add(display(d, x, 104 if not compact else 102, card['title'], title_size))
        y = 142 if not compact else 140
        for i, line in enumerate(card['headline']):
            size = 15.5 if not compact else 14
            d.add(label(d, x, y+i*22, line, size, 'fg'))
        d.add(label(d, x, 194 if not compact else 193, card['detail'], 11 if not compact else 10.2, 'fg_dim'))
        if compact:
            d.add(f'<g transform="translate(85 210)">{ART[slug](d)}</g>')
        else:
            d.add(f'<g transform="translate(586 38)">{ART[slug](d)}</g>')
    d.add(footer(d, card, w, h, compact))
    return d


def main():
    for card in CARDS:
        for theme in THEMES:
            for compact in (False, True):
                suffix = '-compact' if compact else ''
                name = f'card-{card["slug"]}-{theme}{suffix}.svg'
                path = build(card['slug'], theme, compact).save(name)
                print(f'  {name:42} {os.path.getsize(path)/1024:5.1f} KiB')


if __name__ == '__main__':
    main()
