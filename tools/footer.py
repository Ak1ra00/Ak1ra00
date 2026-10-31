#!/usr/bin/env python3
"""The sign-off: a hairline broken by a tiny y² = x³ − 3x + 1, and one quiet line.

No window and no background, so it sits straight on the page in either theme.

    python3 tools/footer.py     -> assets/footer-dark.svg, assets/footer-light.svg
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from svgkit import ADV, FULL_W, THEMES, Doc, n  # noqa: E402

H = 76
CX, RULE_Y = FULL_W / 2, 24
SIZE = 12.5
S = 7.0                          # px per unit for the little curve
P = (2.0, math.sqrt(3.0))        # same marked point as the fetch card


def curve_paths():
    """Oval and branch of y² = x³ − 3x + 1 as two closed-ish SVG paths."""
    f = lambda x: x ** 3 - 3 * x + 1  # noqa: E731
    r0, r1, r2 = sorted(2 * math.cos(math.radians(a)) for a in (40, 160, 280))
    ox = CX - 0.2 * S                # centre the drawing on the gap

    def pt(x, y):
        return f"{n(ox + x * S)} {n(RULE_Y - y * S)}"

    def half(a, b, sign, steps=60):
        out = []
        for k in range(steps + 1):
            # cosine spacing crowds samples near the roots, where the curve turns vertical
            t = (1 - math.cos(math.pi * k / steps)) / 2
            x = a + (b - a) * t
            out.append(pt(x, sign * math.sqrt(max(f(x), 0.0))))
        return out

    upper = half(r0, r1, 1)
    lower = half(r0, r1, -1)[::-1]
    oval = "M" + "L".join(upper + lower[1:]) + "Z"
    ymax = 2.5
    xmax = r2
    while f(xmax) < ymax ** 2:
        xmax += 0.001
    top = half(r2, xmax, 1)[::-1]
    bottom = half(r2, xmax, -1)
    branch = "M" + "L".join(top + bottom[1:])
    return oval, branch, (ox + P[0] * S, RULE_Y - P[1] * S)


def build(theme):
    d = Doc(FULL_W, H, theme, "nothing stored · nothing to leak",
            "Sign-off: a hairline broken by a tiny plot of the elliptic curve "
            "y² = x³ − 3x + 1, and the line: nothing stored, nothing to leak, S = k·P.")
    d.css("@keyframes ping{0%,100%{opacity:.1}50%{opacity:.75}}"
          ".ping{animation:ping 3.6s ease-in-out infinite}")

    cyan, violet = d.c("cyan"), d.c("violet")
    gap = 30
    d.define(f'<linearGradient id="ruleL" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{cyan}" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{cyan}" stop-opacity=".75"/></linearGradient>'
             f'<linearGradient id="ruleR" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{violet}" stop-opacity=".75"/>'
             f'<stop offset="1" stop-color="{violet}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{n(CX - 16)}" y1="0" '
             f'x2="{n(CX + 16)}" y2="0"><stop offset="0" stop-color="{cyan}"/>'
             f'<stop offset="1" stop-color="{violet}"/></linearGradient>')
    span = 300
    d.add(f'<rect x="{n(CX - gap - span)}" y="{RULE_Y - 0.5}" width="{span}" height="1" fill="url(#ruleL)"/>'
          f'<rect x="{n(CX + gap)}" y="{RULE_Y - 0.5}" width="{span}" height="1" fill="url(#ruleR)"/>')

    oval, branch, (px, py) = curve_paths()
    amber = d.c("amber")
    d.add(f'<g fill="none" stroke="url(#ink)" stroke-width="1.4" stroke-linejoin="round" '
          f'stroke-linecap="round"><path d="{oval}"/><path d="{branch}"/></g>'
          f'<circle class="ping" cx="{n(px)}" cy="{n(py)}" r="4.2" fill="none" stroke="{amber}" '
          f'stroke-width="1" opacity=".5"/>'
          f'<circle cx="{n(px)}" cy="{n(py)}" r="1.9" fill="{amber}"/>')

    parts = [("nothing stored", "fg_dim"), ("  ·  ", "muted"), ("nothing to leak", "fg_dim"),
             ("  ·  ", "muted"), ("S = k·P", "cyan", 700)]
    width = sum(len(p[0]) for p in parts) * ADV * SIZE
    d.add(d.rich(CX - width / 2, 60, parts, SIZE))
    return d


def main():
    for theme in THEMES:
        print(build(theme).save(f"footer-{theme}.svg"))


if __name__ == "__main__":
    main()
