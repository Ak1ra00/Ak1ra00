"""Shared drawing kit for the profile's SVGs.

Two palettes, one per GitHub theme:

    dark   "oracle screen" -- the Oracle desktop theme's own colours: cyan for
           the point, violet for its blinding, amber for the paper key.
    light  "paper oracle"  -- the same three inks printed on paper.

Text is drawn as JetBrains Mono outlines (glyphs.json) placed with <use>, so
every SVG renders the same everywhere and needs no font. Animation is plain CSS
inside the SVG; the reduced-motion rule is added to every file, so each file
must look complete with animation switched off.

Conventions:
    full-width assets   FULL_W x any height, window inset by MARGIN
    project cards       CARD_W x CARD_H, window inset by MARGIN
"""

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

FULL_W = 880
CARD_W = 440
CARD_H = 240
MARGIN = 16
ADV = 0.6  # JetBrains Mono advance, in em

THEMES = ("dark", "light")

PALETTES = {
    "dark": {
        "bg": "#0a1014", "bg_deep": "#05080a", "bg_raised": "#121b21",
        "selection": "#173a3d", "grid": "#122028", "line": "#1f3a40",
        "box": "#1f6b66", "muted": "#3a545b", "fg_dim": "#5c7378",
        "fg_soft": "#a9d4d1", "fg": "#cfe7e6", "fg_bright": "#eafbf9",
        "cyan": "#2bd9c9", "cyan_bright": "#7ff2e6",
        "violet": "#b98aff", "violet_bright": "#d3b3ff",
        "amber": "#e0a640", "amber_bright": "#f0c470",
        "red": "#ff5468", "green": "#35d488", "blue": "#4fa8ff", "orange": "#ff9d55",
        "glow": "#2bd9c9", "glow_opacity": "0.28",
    },
    "light": {
        "bg": "#fbf8f1", "bg_deep": "#f2ece0", "bg_raised": "#ffffff",
        "selection": "#dcefeb", "grid": "#ece5d6", "line": "#e0d7c4",
        "box": "#9ec8c1", "muted": "#a9a394", "fg_dim": "#6b7779",
        "fg_soft": "#3b4c53", "fg": "#1d2b31", "fg_bright": "#0b1418",
        "cyan": "#077a70", "cyan_bright": "#19a99c",
        "violet": "#6c3fd1", "violet_bright": "#9b74ea",
        "amber": "#965f08", "amber_bright": "#d29a2e",
        "red": "#c42a3f", "green": "#1a8a55", "blue": "#2463c9", "orange": "#c2621a",
        "glow": "#3d2f12", "glow_opacity": "0.10",
    },
}

_GLYPHS = None


def _glyphs():
    global _GLYPHS
    if _GLYPHS is None:
        with open(os.path.join(HERE, "glyphs.json"), encoding="utf-8") as fh:
            _GLYPHS = json.load(fh)["weights"]
    return _GLYPHS


def n(v):
    """Compact number for SVG attributes."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def tw(s, size):
    """Width of a run of text at `size`."""
    return len(s) * ADV * size


def esc(s):
    return html.escape(s, quote=True)


class Doc:
    """One SVG file. Build the body with add(); text() and friends return strings."""

    def __init__(self, w, h, theme, title, desc=""):
        self.w, self.h, self.theme = w, h, theme
        self.p = PALETTES[theme]
        self.title, self.desc = title, desc
        self.defs, self.styles, self.body = [], [], []
        self._glyph_defs = {}
        self._once = set()
        self._uid = 0

    # -------------------------------------------------------------- basics --
    def c(self, token):
        """Palette token -> colour; anything else (#hex, url(#id), none) passes through."""
        return self.p.get(token, token)

    def uid(self, prefix="u"):
        self._uid += 1
        return f"{prefix}{self._uid}"

    def add(self, *items):
        self.body.extend(items)

    def css(self, rules):
        self.styles.append(rules)

    def define(self, markup, key=None):
        """Add to <defs>; with `key`, only the first call for that key counts."""
        if key is not None:
            if key in self._once:
                return
            self._once.add(key)
        self.defs.append(markup)

    # ---------------------------------------------------------------- text --
    def _glyph(self, ch, weight):
        gid = f"g{weight // 100}{ord(ch):x}"
        if gid not in self._glyph_defs:
            table = _glyphs()[str(weight)]
            if ch not in table:
                raise KeyError(f"glyph {ch!r} (U+{ord(ch):04X}) not in glyphs.json; "
                               f"add it to CHARSET in make_glyphs.py")
            self._glyph_defs[gid] = f'<path id="{gid}" d="{table[ch]}"/>'
        return gid

    def text(self, x, y, s, size=14, weight=400, fill="fg", anchor="start",
             cls=None, opacity=None, attrs=""):
        """Text with its baseline at y. Weights: 400, 700, 800.

        `cls`, `opacity` and `attrs` go on an outer <g>, so a CSS transform
        animation on that class does not fight the positioning transform.
        """
        width = tw(s, size)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        k = f"{size / 1000:.5f}".rstrip("0").rstrip(".")
        uses = []
        for i, ch in enumerate(s):
            if ch == " ":
                continue
            gid = self._glyph(ch, weight)
            uses.append(f'<use href="#{gid}" x="{i * 600}"/>' if i else f'<use href="#{gid}"/>')
        inner = (f'<g transform="translate({n(x)} {n(y)}) scale({k} -{k})" '
                 f'fill="{self.c(fill)}">{"".join(uses)}</g>')
        outer = ""
        if cls:
            outer += f' class="{cls}"'
        if opacity is not None:
            outer += f' opacity="{opacity}"'
        if attrs:
            outer += " " + attrs.strip()
        return f"<g{outer}>{inner}</g>" if outer else inner

    def rich(self, x, y, parts, size=14, weight=400, cls=None, attrs=""):
        """One line in several colours: parts = [(text, fill) or (text, fill, weight), ...]."""
        out, col = [], 0
        for part in parts:
            s, fill = part[0], part[1]
            wt = part[2] if len(part) > 2 else weight
            if s.strip():
                out.append(self.text(x + col * ADV * size, y, s, size, wt, fill))
            col += len(s)
        extra = (f' class="{cls}"' if cls else "") + (" " + attrs.strip() if attrs else "")
        return f'<g{extra}>{"".join(out)}</g>'

    # -------------------------------------------------------------- frames --
    def border_gradient(self):
        """The Oracle Hyprland active border: 45 degrees from cyan into violet."""
        self.define(
            '<linearGradient id="hypr" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{self.c("cyan")}"/>'
            f'<stop offset="1" stop-color="{self.c("violet")}"/></linearGradient>',
            key="hypr")
        return "url(#hypr)"

    def window(self, x, y, w, h, r=12, fill="bg", stroke=1.5, glow=True):
        """A focused Hyprland window: gradient border and a soft glow (a shadow on paper)."""
        out = []
        if glow:
            self.define('<filter id="halo" x="-10%" y="-25%" width="120%" height="150%">'
                        '<feGaussianBlur stdDeviation="7"/></filter>', key="halo")
            dy = 3 if self.theme == "light" else 0
            out.append(f'<rect x="{n(x + 2)}" y="{n(y + 2 + dy)}" width="{n(w - 4)}" '
                       f'height="{n(h - 4)}" rx="{r}" fill="{self.c("glow")}" '
                       f'opacity="{self.p["glow_opacity"]}" filter="url(#halo)"/>')
        out.append(f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{r}" '
                   f'fill="{self.c(fill)}" stroke="{self.border_gradient()}" '
                   f'stroke-width="{stroke}"/>')
        return "".join(out)

    def grid(self, x, y, w, h, step=24, r=12, opacity=1.0):
        """Blueprint grid clipped to a rounded rect."""
        pid, cid = self.uid("grid"), self.uid("clip")
        self.define(f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" '
                    f'x="{n(x)}" y="{n(y)}"><path d="M{step} 0V{step}H0" fill="none" '
                    f'stroke="{self.c("grid")}" stroke-width="1"/></pattern>'
                    f'<clipPath id="{cid}"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" '
                    f'height="{n(h)}" rx="{r}"/></clipPath>')
        return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" '
                f'fill="url(#{pid})" clip-path="url(#{cid})" opacity="{opacity}"/>')

    # -------------------------------------------------------------- output --
    def render(self):
        style = "".join(self.styles) + (
            "@media (prefers-reduced-motion:reduce){*{animation:none!important;"
            "transition:none!important}}")
        return "".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{esc(self.title)}</title><desc id="desc">{esc(self.desc)}</desc>',
            "<defs>", "".join(self._glyph_defs.values()), "".join(self.defs), "</defs>",
            f"<style>{style}</style>",
            "".join(self.body),
            "</svg>\n",
        ])

    def save(self, name, directory=ASSETS):
        """Write assets/<name> and return its path."""
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.render())
        return path
