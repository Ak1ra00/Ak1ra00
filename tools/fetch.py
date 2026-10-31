#!/usr/bin/env python3
"""The fastfetch card: a braille-dot plot of y² = x³ − 3x + 1 beside the facts.

The logo is the Oracle boot curve: an oval and an unbounded branch, plotted the
way btop and drawille plot, one lit dot per step of the curve on a 2x4 braille
grid, with the point P = (2, √3) marked on the branch.

    python3 tools/fetch.py      -> assets/fetch-dark.svg, assets/fetch-light.svg
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from svgkit import ADV, FULL_W, MARGIN, THEMES, Doc, n  # noqa: E402

H = 412
SIZE = 13.5            # body text
LH = 19                # line height, also the braille cell height
CW = ADV * SIZE        # character cell width
X0 = 48                # left edge of the prompt and the logo
X1 = 318               # left edge of the info column
KEY_W = 9              # key column, in characters

# The logo: 28 x 12 braille cells, so a 56 x 48 dot grid.
COLS, ROWS = 28, 12
LOGO_X, LOGO_Y = X0, 94
DX, DY = CW / 2, LH / 4                       # dot pitch
XMIN, XMAX = -2.25, 2.75                      # curve window, uniform scale
SCALE = COLS * CW / (XMAX - XMIN)             # px per unit
YMAX = ROWS * LH / SCALE / 2
P = (2.0, math.sqrt(3.0))                     # the marked point


def facts(theme):
    """(key, [(text, fill[, weight]), ...]) -- every fact is from the public repos."""
    def dotted(*items):
        out = []
        for i, item in enumerate(items):
            if i:
                out.append((" · ", "fg_dim"))
            out.append((item, "fg"))
        return out

    return [
        ("OS", dotted("Omarchy", "Arch Linux", "Hyprland")),
        ("Theme", [("Oracle", "fg", 700), (" — ", "fg_dim"), ("cyan", "cyan", 700),
                   (" · ", "fg_dim"), ("violet", "violet", 700), (" · ", "fg_dim"),
                   ("amber", "amber", 700)]),
        ("Editor", [("Neovim", "fg")]),
        ("Hosts", dotted("Coldcard Mk4", "Coldcard Q", "LilyGO T-Display")),
        ("Langs", dotted("C", "C++", "Python", "MicroPython", "JavaScript", "Lua")),
        ("Crypto", dotted("ristretto255 OPRF", "DLEQ", "HKDF-SHA256", "BIP39", "BIP85")),
        ("Builds", dotted("firmware", "password managers", "games", "themes")),
        ("Vault", [("none", "amber", 700), (" — passwords are derived, never stored", "fg")]),
        ("Entropy", [("STM32 TRNG", "fg"), (" + your scribbles", "fg_soft")]),
        ("Uptime", [("always compiling", "fg")]),
    ]


# The fastfetch colour blocks: normal and bright, black..white, from oracle/colors.toml.
SWATCHES = {
    "dark": [
        ["#121b21", "#ff5468", "#35d488", "#e0a640", "#4fa8ff", "#b98aff", "#2bd9c9", "#cfe7e6"],
        ["#3a545b", "#ff8698", "#78e8b0", "#f0c470", "#8ec6ff", "#d3b3ff", "#7ff2e6", "#eafbf9"],
    ],
    "light": [
        ["#1d2b31", "#c42a3f", "#1a8a55", "#965f08", "#2463c9", "#6c3fd1", "#077a70", "#d9d0bd"],
        ["#6b7779", "#e0566a", "#2fae72", "#d29a2e", "#5a8ee6", "#9b74ea", "#19a99c", "#efe8da"],
    ],
}


# ------------------------------------------------------------------ logo --
def to_px(x, y):
    return (LOGO_X + (x - XMIN) * SCALE, LOGO_Y + ROWS * LH / 2 - y * SCALE)


def lit_dots():
    """Walk both components of the curve and light the nearest braille dot."""
    f = lambda x: x ** 3 - 3 * x + 1  # noqa: E731
    roots = sorted(2 * math.cos(math.radians(a)) for a in (40, 160, 280))  # -1.879, 0.347, 1.532
    lit = set()

    def walk(xs):
        for sign in (1, -1):
            for x in xs:
                v = f(x)
                if v < 0:
                    continue
                y = sign * math.sqrt(v)
                if abs(y) > YMAX:
                    continue
                px, py = to_px(x, y)
                i = round((px - LOGO_X) / DX - 0.5)
                j = round((py - LOGO_Y) / DY - 0.5)
                if 0 <= i < COLS * 2 and 0 <= j < ROWS * 4:
                    lit.add((i, j))

    steps = 24000
    oval = [roots[0] + (roots[1] - roots[0]) * k / steps for k in range(steps + 1)]
    branch = [roots[2] + (XMAX - roots[2]) * k / steps for k in range(steps + 1)]
    walk(oval)
    walk(branch)
    return sorted(lit)


def dot_xy(i, j):
    return LOGO_X + (i + 0.5) * DX, LOGO_Y + (j + 0.5) * DY


def circle_path(cx, cy, r):
    return f"M{n(cx - r)} {n(cy)}a{r} {r} 0 1 0 {n(2 * r)} 0a{r} {r} 0 1 0 {n(-2 * r)} 0"


def logo(d):
    w, h = COLS * CW, ROWS * LH
    gid = "lg"
    d.define(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
             f'x1="{n(LOGO_X)}" y1="{n(LOGO_Y)}" x2="{n(LOGO_X + w)}" y2="{n(LOGO_Y + h)}">'
             f'<stop offset="0" stop-color="{d.c("cyan")}"/>'
             f'<stop offset="1" stop-color="{d.c("violet")}"/></linearGradient>')

    # every dot of the braille grid, faintly, so the plot reads as a dot matrix,
    # fading out towards the edges
    d.define(f'<pattern id="cells" width="{n(DX)}" height="{n(DY)}" patternUnits="userSpaceOnUse" '
             f'x="{n(LOGO_X)}" y="{n(LOGO_Y)}"><circle cx="{n(DX / 2)}" cy="{n(DY / 2)}" r="0.75" '
             f'fill="{d.c("fg_dim")}"/></pattern>'
             '<radialGradient id="vignette"><stop offset="0.35" stop-color="#fff"/>'
             '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
             f'<mask id="fadecells"><rect x="{n(LOGO_X)}" y="{n(LOGO_Y)}" width="{n(w)}" '
             f'height="{n(h)}" fill="url(#vignette)"/></mask>')
    if d.theme == "dark":
        d.define('<filter id="phosphor" x="-10%" y="-10%" width="120%" height="120%">'
                 '<feGaussianBlur stdDeviation="2.2"/></filter>')

    r = 1.45
    dots = "".join(circle_path(*dot_xy(i, j), r) for i, j in lit_dots())
    d.define(f'<path id="dots" d="{dots}"/>')
    d.define('<clipPath id="dotclip"><use href="#dots"/></clipPath>')
    band_w = 90
    glint = d.c("fg_bright" if d.theme == "dark" else "cyan_bright")
    d.define(f'<linearGradient id="band" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{glint}" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="{glint}" stop-opacity="0.85"/>'
             f'<stop offset="1" stop-color="{glint}" stop-opacity="0"/></linearGradient>')

    px, py = to_px(*P)
    ink = d.c("amber")
    halo_op = 0.55 if d.theme == "dark" else 0.45
    out = [
        f'<g class="logo">',
        f'<rect x="{n(LOGO_X)}" y="{n(LOGO_Y)}" width="{n(w)}" height="{n(h)}" fill="url(#cells)" '
        f'mask="url(#fadecells)" opacity="{0.30 if d.theme == "dark" else 0.34}"/>',
        (f'<use href="#dots" fill="url(#{gid})" filter="url(#phosphor)" opacity="0.55"/>'
         if d.theme == "dark" else ""),
        f'<use href="#dots" fill="url(#{gid})"/>',
        # a slow highlight sweeping across the lit dots; parked off the plot when still
        f'<g clip-path="url(#dotclip)"><rect class="shine" x="{n(LOGO_X - band_w)}" '
        f'y="{n(LOGO_Y - 40)}" width="{band_w}" height="{n(h + 80)}" fill="url(#band)" '
        f'transform="rotate(18 {n(LOGO_X)} {n(LOGO_Y + h / 2)})"/></g>',
        f'<circle cx="{n(px)}" cy="{n(py)}" r="7" fill="none" stroke="{ink}" stroke-width="1" '
        f'opacity="{halo_op}" class="ring"/>',
        f'<circle cx="{n(px)}" cy="{n(py)}" r="3.4" fill="{ink}"/>',
        d.text(px - 13, py + 4.5, "P", 12, 700, "amber", anchor="end"),
        "</g>",
        d.text(LOGO_X + w / 2, LOGO_Y + h + 22, "y² = x³ − 3x + 1", 11.5, 400, "fg_dim",
               anchor="middle", cls="fade", attrs='style="animation-delay:1.1s"'),
    ]
    return "".join(out)


# ------------------------------------------------------------------ card --
def build(theme):
    d = Doc(FULL_W, H, theme, "Ak1ra00 · fastfetch",
            "A fastfetch-style system summary. Logo: a braille-dot plot of the elliptic curve "
            "y² = x³ − 3x + 1 with a marked point P. OS: Omarchy, Arch Linux, Hyprland. "
            "Theme: Oracle (cyan, violet, amber). Editor: Neovim. Hosts: Coldcard Mk4, "
            "Coldcard Q, LilyGO T-Display. Langs: C, C++, Python, MicroPython, JavaScript, Lua. "
            "Crypto: ristretto255 OPRF, DLEQ, HKDF-SHA256, BIP39, BIP85. Builds: firmware, "
            "password managers, games, themes. Vault: none, passwords are derived, never "
            "stored. Entropy: STM32 TRNG plus your scribbles. Uptime: always compiling.")
    d.css(
        "@keyframes fade{from{opacity:0}}"
        "@keyframes on{from{opacity:0}to{opacity:0}}"
        "@keyframes blink{50%{opacity:0}}"
        "@keyframes shine{0%{transform:translateX(0)}30%,100%{transform:translateX(380px)}}"
        "@keyframes ring{0%,100%{opacity:.15}50%{opacity:.8}}"
        f"@keyframes walk{{to{{transform:translateX({n(9 * CW)}px)}}}}"
        "@keyframes typing{0%,99%{opacity:1}100%{opacity:0}}"
        ".fade{animation:fade .5s ease-out backwards}"
        ".ch{animation:on .01s backwards}"
        ".logo{animation:fade .9s ease-out .95s backwards}"
        ".shine{animation:shine 7s ease-in-out 2.6s infinite}"
        ".ring{animation:ring 3.2s ease-in-out 2s infinite}"
        ".cur{animation:fade .3s ease-out 2.1s backwards,blink 1.1s step-end 2.4s infinite}"
        ".tcur{opacity:0;animation:walk .54s steps(9,start) .25s both,typing .95s linear}"
    )
    pane_w, pane_h = FULL_W - 2 * MARGIN, H - 2 * MARGIN
    d.add(d.window(MARGIN, MARGIN, pane_w, pane_h))

    # prompt, then the command typed out a key at a time
    y = 50
    d.add(d.rich(X0, y, [("~ ", "fg_dim"), ("❯ ", "cyan", 700)], SIZE))
    for k, ch in enumerate("fastfetch"):
        d.add(d.text(X0 + (4 + k) * CW, y, ch, SIZE, 400, "fg", cls="ch",
                     attrs=f'style="animation-delay:{0.25 + 0.06 * k:.2f}s"'))
    # the cursor follows the keystrokes, then leaves with the output; unseen when still
    d.add(f'<rect class="tcur" x="{n(X0 + 4 * CW)}" y="{n(y - 0.8 * SIZE)}" width="{n(CW)}" '
          f'height="{n(1.02 * SIZE)}" fill="{d.c("fg_soft")}"/>')

    d.add(logo(d))

    # title and rule
    t0 = 1.0
    title = "ak1ra00@oracle"
    d.add(d.rich(X1, 88, [("ak1ra00", "cyan", 700), ("@", "fg_dim", 700), ("oracle", "violet", 700)],
                 15, cls="fade", attrs=f'style="animation-delay:{t0:.2f}s"'))
    d.add(d.text(X1, 106, "─" * len(title), 15, 400, "fg_dim", cls="fade",
                 attrs=f'style="animation-delay:{t0 + 0.05:.2f}s"'))

    # key/value lines
    for i, (key, parts) in enumerate(facts(theme)):
        line = [(key.ljust(KEY_W), "cyan", 700)] + parts
        d.add(d.rich(X1, 130 + i * LH, line, SIZE, cls="fade",
                     attrs=f'style="animation-delay:{t0 + 0.12 + 0.07 * i:.2f}s"'))

    # colour blocks, three cells wide each, like fastfetch prints them
    sw, sh = 3 * CW, 14
    rows = []
    for r, row in enumerate(SWATCHES[theme]):
        y0 = 316 + r * (sh + 2)
        for k, colour in enumerate(row):
            edge = (f' stroke="{d.c("line")}" stroke-width="1"'
                    if theme == "light" and colour in ("#d9d0bd", "#efe8da") else "")
            rows.append(f'<rect x="{n(X1 + k * sw)}" y="{n(y0)}" width="{n(sw)}" '
                        f'height="{sh}" fill="{colour}"{edge}/>')
    d.add(f'<g class="fade" style="animation-delay:{t0 + 0.9:.2f}s">{"".join(rows)}</g>')

    # the next prompt, waiting
    y = 372
    d.add(d.rich(X0, y, [("~ ", "fg_dim"), ("❯ ", "cyan", 700)], SIZE, cls="fade",
                 attrs=f'style="animation-delay:{t0 + 1.1:.2f}s"'))
    d.add(f'<rect class="cur" x="{n(X0 + 4 * CW)}" y="{n(y - 0.8 * SIZE)}" width="{n(CW)}" '
          f'height="{n(1.02 * SIZE)}" fill="{d.c("fg_soft")}"/>')
    return d


def main():
    for theme in THEMES:
        print(build(theme).save(f"fetch-{theme}.svg"))


if __name__ == "__main__":
    main()
