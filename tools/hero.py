#!/usr/bin/env python3
"""Draw the profile header: the name, beside the group law on a real curve.

The curve is y² = x³ − 3x + 5 over ℝ, the one on the Oracle theme's first
wallpaper. P and Q are points on it, the chord through them meets it again at
−R, and R = P + Q is that point reflected in the x-axis. Every position below is
computed, so the animation plays the actual addition.

    python3 tools/hero.py      writes assets/hero-dark.svg and assets/hero-light.svg
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from svgkit import ADV, FULL_W, MARGIN, THEMES, Doc, n, tw  # noqa: E402

H = 300
WX, WY, WW, WH = MARGIN, MARGIN, FULL_W - 2 * MARGIN, H - 2 * MARGIN
LEFT = 48                                   # left edge of the text column

# ------------------------------------------------------------------ curve --
A, B = -3, 5                                # y² = x³ + A·x + B


def f(x):
    return x ** 3 + A * x + B


def solve(target, lo, hi):
    """x in [lo, hi] with f(x) = target, f increasing there."""
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < target else (lo, mid)
    return (lo + hi) / 2


ROOT = solve(0, -3, -2)                     # the curve's leftmost point

# Maths -> pixels. The scale differs per axis, but an affine map keeps lines
# straight and reflections reflections, so the construction stays exact.
PX0, PX1 = 436, 848                         # pixel span of the plot
XMIN, XMAX = -2.8, 3.3                      # maths span shown across it
CY, SY = 150, 30                            # row of y = 0, pixels per unit of y
SX = (PX1 - PX0) / (XMAX - XMIN)


def px(x, y):
    return PX0 + (x - XMIN) * SX, CY - y * SY


def on_curve(x, upper):
    y = math.sqrt(f(x))
    return (x, y if upper else -y)


P = on_curve(-1.7, upper=False)
Q = on_curve(1.4, upper=True)
LAM = (Q[1] - P[1]) / (Q[0] - P[0])         # slope of the chord
XR = LAM * LAM - P[0] - Q[0]
NEG_R = (XR, P[1] + LAM * (XR - P[0]))      # where the chord meets the curve again
R = (XR, -NEG_R[1])                         # P + Q
assert abs(NEG_R[1] ** 2 - f(XR)) < 1e-9


def curve_path(ymax=4.75, steps=150):
    """Upper branch from beyond the top edge to the root, then the lower branch."""
    xt = solve(ymax * ymax, ROOT, 10)
    xs = [ROOT + (xt - ROOT) * (i / steps) ** 2 for i in range(steps + 1)]  # even in y near the root
    pts = [px(x, math.sqrt(max(f(x), 0))) for x in reversed(xs)]
    pts += [px(x, -math.sqrt(max(f(x), 0))) for x in xs[1:]]
    return poly(pts), length(pts)


def poly(pts):
    return "M" + " ".join(f"{n(x)} {n(y)}" for x, y in pts)


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------- the tagline --
TAGLINES = (
    "custom firmware for hardware wallets",
    "passwords derived, never stored",
    "Tetris on a Bitcoin signing device",
    "desktops themed in elliptic curves",
)
TYPE, HOLD, ERASE, GAP = 0.06, 2.6, 0.025, 0.5   # seconds per char / pause / per char / pause


def typing_schedule():
    """Per phrase, each char's (shown, hidden) times; and the loop length."""
    t, out = 0.0, []
    for s in TAGLINES:
        k = len(s)
        erase = t + k * TYPE + HOLD
        out.append([(t + (i + 1) * TYPE, erase + (k - i) * ERASE) for i in range(k)])
        t = erase + k * ERASE + GAP
    return out, t


def pct(t, total):
    return f"{100 * t / total:.3f}".rstrip("0").rstrip(".") + "%"


# ------------------------------------------------------- the construction --
LOOP, START = 12.0, 2.4      # seconds per cycle; first cycle waits for the curve
FADE = (86, 92)              # every part of the construction fades out here (% of LOOP)
STEPS = {                    # name: (from %, to %) of its entrance
    "p": (0, 4), "q": (5, 9), "chord": (10, 24), "nr": (22, 26),
    "vert": (27, 34), "r": (34, 38), "cap": (38, 43),
}


def entrance(name, frm="", to=""):
    a, b = STEPS[name]
    return (f"@keyframes {name}{{0%,{a}%{{opacity:0;{frm}}}{b}%{{opacity:1;{to}}}"
            f"{FADE[0]}%{{opacity:1}}{FADE[1]}%,100%{{opacity:0}}}}"
            f".{name}{{animation:{name} {LOOP}s {START}s infinite both}}")


def build(theme):
    d = Doc(FULL_W, H, theme, "Ak1ra00",
            "Ak1ra00: hardware hacker, applied cryptography, firmware. Beside the name, "
            "the elliptic curve y² = x³ − 3x + 5 plays out the group law: the chord "
            "through P and Q meets the curve at −R, and its reflection is R = P + Q.")
    dark = theme == "dark"
    c = d.c

    # ---- window, grid fading in toward the plot, a faint lift behind the curve
    d.add(d.window(WX, WY, WW, WH))
    clip = d.uid("win")
    d.define(f'<clipPath id="{clip}"><rect x="{WX + 1}" y="{WY + 1}" width="{WW - 2}" '
             f'height="{WH - 2}" rx="11"/></clipPath>')
    fade = d.uid("fade")
    d.define(f'<linearGradient id="{fade}g" x1="0" x2="1"><stop offset="0" stop-color="#fff" '
             f'stop-opacity="{0.35 if dark else 0.45}"/><stop offset="0.5" stop-color="#fff" '
             f'stop-opacity="1"/></linearGradient>'
             f'<mask id="{fade}"><rect x="0" y="0" width="{FULL_W}" height="{H}" '
             f'fill="url(#{fade}g)"/></mask>')
    d.add(f'<g mask="url(#{fade})">{d.grid(WX, WY, WW, WH, step=24)}</g>')
    if dark:
        lift = d.uid("lift")
        d.define(f'<radialGradient id="{lift}" cx="0.5" cy="0.5" r="0.5">'
                 f'<stop offset="0" stop-color="{c("cyan")}" stop-opacity="0.09"/>'
                 f'<stop offset="1" stop-color="{c("cyan")}" stop-opacity="0"/></radialGradient>')
        d.add(f'<ellipse cx="640" cy="{CY}" rx="300" ry="170" fill="url(#{lift})" '
              f'clip-path="url(#{clip})"/>')
    else:
        d.add(crop_marks(d))

    d.add(f'<g clip-path="url(#{clip})">{plot(d)}</g>')
    d.add(name_block(d))
    d.add(tagline(d))
    return d


def crop_marks(d):
    """Printer's crop marks in the paper theme's corners."""
    out, L, inset = [], 9, 9
    for x, sx in ((WX + inset, 1), (WX + WW - inset, -1)):
        for y, sy in ((WY + inset, 1), (WY + WH - inset, -1)):
            out.append(f'M{n(x)} {n(y + sy * L)}V{n(y)}H{n(x + sx * L)}')
    return (f'<path d="{"".join(out)}" fill="none" stroke="{d.c("fg_dim")}" '
            f'stroke-width="1" opacity="0.55"/>')


def plot(d):
    dark = d.theme == "dark"
    c = d.c
    out = []

    # axes, with ticks at the integers; the x-axis fades in from the text column
    ax = d.uid("ax")
    d.define(f'<linearGradient id="{ax}" gradientUnits="userSpaceOnUse" x1="{PX0}" x2="{PX0 + 60}" '
             f'y1="0" y2="0"><stop offset="0" stop-color="{c("line")}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{c("line")}"/></linearGradient>')
    oy = px(0, 0)[0]
    ticks = "".join(f"M{n(px(k, 0)[0])} {CY - 3}v6" for k in (-2, -1, 1, 2, 3))
    out.append(f'<path d="M{PX0} {CY}H{FULL_W}" stroke="url(#{ax})" stroke-width="1"/>'
               f'<path d="M{n(oy)} {WY + 44}V{WY + WH}{ticks}" stroke="{c("line")}" stroke-width="1" '
               f'fill="none"/>')

    # the curve, drawn in once; a static glow fades up under it on the dark screen
    path, L = curve_path()
    d.css(f".curve{{stroke-dasharray:{L:.0f};stroke-dashoffset:0;"
          f"animation:draw 2.2s cubic-bezier(.55,.1,.25,1) .15s both}}"
          f"@keyframes draw{{from{{stroke-dashoffset:{L:.0f}}}}}")
    if dark:
        d.define('<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
                 '<feGaussianBlur stdDeviation="4"/></filter>', key="soft")
        d.css(".cglow{animation:glowin 1s ease-out 2.25s both}"
              "@keyframes glowin{from{opacity:0}}")
        out.append(f'<path class="cglow" d="{path}" fill="none" stroke="{c("cyan")}" '
                   f'stroke-width="5" opacity="0.45" filter="url(#soft)"/>')
    out.append(f'<path class="curve" d="{path}" fill="none" stroke="{c("cyan")}" '
               f'stroke-width="{2 if dark else 1.8}" stroke-linejoin="round" stroke-linecap="round"/>')

    # figure label, top left of the plot
    out.append(d.text(PX0 + 14, WY + 30, "y² = x³ − 3x + 5", 12, 400, "fg_dim"))
    cap_x = PX0 + 14 + tw("y² = x³ − 3x + 5   ", 12)
    d.css(entrance("cap"))
    out.append(d.rich(cap_x, WY + 30, [("P", "cyan_bright" if dark else "cyan", 700),
                                       (" + ", "fg_dim"), ("Q", "cyan_bright" if dark else "cyan", 700),
                                       (" = ", "fg_dim"), ("R", "amber_bright" if dark else "amber", 700)],
                      12, cls="cap"))

    # the chord through P and Q, past −R; violet, faded at both ends
    (x1, y1), (x2, y2) = px(P[0] - 0.32, P[1] - 0.32 * LAM), px(XR + 0.26, NEG_R[1] + 0.26 * LAM)
    Lc = math.dist((x1, y1), (x2, y2))
    cg = d.uid("cg")
    d.define(f'<linearGradient id="{cg}" gradientUnits="userSpaceOnUse" x1="{n(x1)}" y1="{n(y1)}" '
             f'x2="{n(x2)}" y2="{n(y2)}"><stop offset="0" stop-color="{c("violet")}" stop-opacity="0"/>'
             f'<stop offset="0.12" stop-color="{c("violet")}"/><stop offset="0.9" stop-color="{c("violet")}"/>'
             f'<stop offset="1" stop-color="{c("violet")}" stop-opacity="0"/></linearGradient>')
    a, b = STEPS["chord"]
    d.css(f"@keyframes chord{{0%,{a}%{{stroke-dashoffset:{Lc:.0f}}}{b}%{{stroke-dashoffset:0;opacity:1}}"
          f"{FADE[0]}%{{opacity:1}}{FADE[1]}%,100%{{opacity:0;stroke-dashoffset:0}}}}"
          f".chord{{stroke-dasharray:{Lc:.0f};stroke-dashoffset:0;"
          f"animation:chord {LOOP}s {START}s infinite both}}")
    out.append(f'<path class="chord" d="M{n(x1)} {n(y1)}L{n(x2)} {n(y2)}" stroke="url(#{cg})" '
               f'stroke-width="1.6" stroke-linecap="round"/>')

    # the reflection: dashed, growing from −R down to R
    (vx, vy1), (_, vy2) = px(*NEG_R), px(*R)
    d.css(entrance("vert", "transform:scaleY(0)", "transform:scaleY(1)")
          + ".vert{transform-box:fill-box;transform-origin:50% 0}")
    out.append(f'<path class="vert" d="M{n(vx)} {n(vy1 + 6)}V{n(vy2 - 6)}" '
               f'stroke="{c("violet_bright" if dark else "violet")}" stroke-width="1.2" '
               f'stroke-dasharray="3 4" opacity="0.8"/>')

    # the points: P and Q on the curve, −R hollow, R = P + Q in amber
    ring = c("bg")
    pq = c("cyan_bright" if dark else "cyan")
    pop = "transform:scale(.3)", "transform:scale(1)"
    for key in ("p", "q", "r"):
        d.css(entrance(key, *pop))
    d.css(entrance("nr", *pop)
          + ".p,.q,.r,.nr,.halo{transform-box:fill-box;transform-origin:center}")

    def dot(pt, cls, fill, label, lx, ly, lfill, anchor="start"):
        x, y = px(*pt)
        return (f'<g class="{cls}"><circle cx="{n(x)}" cy="{n(y)}" r="4.6" fill="{fill}" '
                f'stroke="{ring}" stroke-width="2"/>'
                + d.text(x + lx, y + ly, label, 13, 700, lfill, anchor) + "</g>")

    rx, ry = px(*R)
    halo = d.uid("halo")
    amber = c("amber_bright" if dark else "amber")
    d.define(f'<radialGradient id="{halo}"><stop offset="0" stop-color="{amber}" '
             f'stop-opacity="{0.55 if dark else 0.28}"/><stop offset="1" stop-color="{amber}" '
             f'stop-opacity="0"/></radialGradient>')
    a, b = STEPS["r"]
    d.css(f"@keyframes halo{{0%,{a}%{{opacity:0;transform:scale(.4)}}{b + 3}%{{opacity:1;"
          f"transform:scale(1.25)}}{b + 9}%{{opacity:.8;transform:scale(1)}}{FADE[0]}%{{opacity:.8}}"
          f"{FADE[1]}%,100%{{opacity:0}}}}.halo{{opacity:.8;animation:halo {LOOP}s {START}s infinite both}}")
    if dark:
        out.append(f'<circle class="halo" cx="{n(rx)}" cy="{n(ry)}" r="18" fill="url(#{halo})"/>')
    else:
        out.append(f'<circle class="halo" cx="{n(rx)}" cy="{n(ry)}" r="9.5" fill="none" '
                   f'stroke="{amber}" stroke-width="1" stroke-dasharray="2 2.2"/>')

    out.append(dot(P, "p", pq, "P", -9, 20, pq, "end"))
    out.append(dot(Q, "q", pq, "Q", -10, -10, pq, "end"))
    nx, ny = px(*NEG_R)
    out.append(f'<g class="nr"><circle cx="{n(nx)}" cy="{n(ny)}" r="4.4" fill="{ring}" '
               f'stroke="{c("violet")}" stroke-width="1.8"/>'
               + d.text(nx - 11, ny - 8, "−R", 13, 700, "violet", "end") + "</g>")
    out.append(dot(R, "r", amber, "R", -11, 17, amber, "end"))
    return "".join(out)


def name_block(d):
    dark = d.theme == "dark"
    c = d.c
    out = []
    out.append(d.rich(LEFT, 82, [("~ ", "fg_dim"), ("❯ ", "cyan", 700), ("whoami", "fg_soft")], 14))

    # the name: one gradient across the whole word (a gradient set on the glyphs
    # would restart on every letter), with a light sweep every few seconds
    name, size, base = "Ak1ra00", 64, 148
    w = tw(name, size)
    m, g, s = d.uid("nm"), d.uid("ng"), d.uid("sh")
    d.define(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="{FULL_W}" height="{H}">'
             + d.text(LEFT, base, name, size, 800, "#fff") + "</mask>"
             f'<linearGradient id="{g}" gradientUnits="userSpaceOnUse" x1="{LEFT}" y1="{base - 50}" '
             f'x2="{n(LEFT + w)}" y2="{base}"><stop offset="0" stop-color="{c("cyan_bright" if dark else "cyan")}"/>'
             f'<stop offset="0.55" stop-color="{c("cyan")}"/>'
             f'<stop offset="1" stop-color="{c("violet")}"/></linearGradient>'
             f'<linearGradient id="{s}" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
             f'<stop offset="0.5" stop-color="#fff" stop-opacity="{0.55 if dark else 0.4}"/>'
             f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    if dark:
        d.define('<filter id="nglow" x="-15%" y="-40%" width="130%" height="180%">'
                 '<feGaussianBlur stdDeviation="9"/></filter>', key="nglow")
        out.append(f'<g filter="url(#nglow)" opacity="0.38">'
                   + d.text(LEFT, base, name, size, 800, "cyan") + "</g>")
    d.css(".shine{animation:shine 9s ease-in-out 3.2s infinite both}"
          "@keyframes shine{0%{transform:translateX(0)}22%,100%{transform:translateX(470px)}}")
    out.append(f'<g mask="url(#{m})"><rect x="{LEFT - 4}" y="{base - 56}" width="{n(w + 8)}" '
               f'height="64" fill="url(#{g})"/>'
               f'<g class="shine"><rect x="{LEFT - 110}" y="{base - 60}" width="70" height="72" '
               f'fill="url(#{s})" transform="skewX(-18)"/></g></g>')

    out.append(d.rich(LEFT + 2, 178, [("hardware hacker", "fg_soft"), (" · ", "fg_dim"),
                                      ("applied cryptography", "fg_soft"), (" · ", "fg_dim"),
                                      ("firmware", "fg_soft")], 13))
    return "".join(out)


def tagline(d):
    """`❯ <phrase>` typed out, held, backspaced, next; cursor follows the text."""
    size, base = 15, 220
    cw = ADV * size
    x0 = LEFT + 2 + 2 * cw
    sched, total = typing_schedule()
    out = [d.text(LEFT + 2, base, "❯", size, 700, "violet")]
    css = [f".tc{{animation-duration:{total:.3f}s;animation-timing-function:step-end;"
           f"animation-iteration-count:infinite}}.off{{opacity:0}}"]
    events = []
    for p, (phrase, times) in enumerate(zip(TAGLINES, sched)):
        for i, (ch, (on, off)) in enumerate(zip(phrase, times)):
            events += [(on, 1), (off, -1)]
            if ch == " ":
                continue
            k = f"t{p}c{i}"
            css.append(f".{k}{{animation-name:{k}}}@keyframes {k}{{0%{{opacity:0}}"
                       f"{pct(on, total)}{{opacity:1}}{pct(off, total)},100%{{opacity:0}}}}")
            out.append(d.text(x0 + i * cw, base, ch, size, 400, "fg",
                              cls=f"tc {k}" + (" off" if p else "")))

    # cursor: a block one cell wide, jumping a cell per keystroke; static after phrase one
    frames, count = ["0%{transform:translateX(0)}"], 0
    for t, step in sorted(events):
        count += step
        frames.append(f"{pct(t, total)}{{transform:translateX({n(count * cw)}px)}}")
    css.append(f".cur{{transform:translateX({n(len(TAGLINES[0]) * cw)}px);animation:cur {total:.3f}s "
               f"step-end infinite}}@keyframes cur{{{''.join(frames)}100%{{transform:translateX(0)}}}}"
               ".blink{animation:blink 1.1s step-end infinite}@keyframes blink{50%{opacity:0}}")
    d.css("".join(css))
    out.append(f'<g class="cur"><rect class="blink" x="{n(x0 + 0.5)}" y="{base - 12}" '
               f'width="{n(cw - 1)}" height="15" rx="1" fill="{d.c("cyan")}" opacity="0.85"/></g>')
    return "".join(out)


def main():
    for theme in THEMES:
        path = build(theme).save(f"hero-{theme}.svg")
        print(f"wrote {path} ({os.path.getsize(path) / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
