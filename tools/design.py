"""Shared editorial design language. Runtime dependencies: Python's standard library."""

import json
from pathlib import Path

from svgkit import Doc, n

PALETTES = {
    "dark": {
        "bg": "#111610", "bg_deep": "#0b0f0a", "bg_raised": "#1b2318",
        "line": "#35412f", "grid": "#253020", "fg": "#d6ddcc",
        "fg_bright": "#f3f4e9", "fg_soft": "#bdc7af", "fg_dim": "#9eac91",
        "muted": "#728367", "accent": "#d2f898", "cyan": "#d2f898",
        "cyan_bright": "#e1ffb6", "violet": "#b9b0ee", "violet_bright": "#d2cafa",
        "amber": "#f4b17d", "amber_bright": "#ffd0a8", "green": "#d2f898",
        "blue": "#9bbbd0", "red": "#f49580", "box": "#566749",
        "signal": "#d2f898", "signal_ink": "#17210f",
    },
    "light": {
        "bg": "#f4f1e7", "bg_deep": "#e9e6d9", "bg_raised": "#fcfaf3",
        "line": "#cccebe", "grid": "#dde0cf", "fg": "#34402b",
        "fg_bright": "#1c2817", "fg_soft": "#4d5d40", "fg_dim": "#5f6f52",
        "muted": "#7d8b70", "accent": "#486721", "cyan": "#486721",
        "cyan_bright": "#344c17", "violet": "#6b5898", "violet_bright": "#51417a",
        "amber": "#955020", "amber_bright": "#743b15", "green": "#486721",
        "blue": "#42647c", "red": "#a3422e", "box": "#96a387",
        "signal": "#d2f898", "signal_ink": "#17210f",
    },
}

_DISPLAY = None


def document(w, h, theme, title, desc):
    d = Doc(w, h, theme, title, desc)
    d.p = {**d.p, **PALETTES[theme]}
    return d


def display_data():
    global _DISPLAY
    if _DISPLAY is None:
        _DISPLAY = json.loads(Path(__file__).with_name("display-glyphs.json").read_text())
    return _DISPLAY


def display_width(text, size):
    data = display_data()
    return sum(data["glyphs"][ch]["advance"] for ch in text) * size / data["upm"]


def display(d, x, y, text, size=48, fill="fg_bright", anchor="start"):
    """Space Grotesk Bold as embedded outlines; no font/network dependency."""
    data = display_data()
    width = display_width(text, size)
    if anchor == "end":
        x -= width
    elif anchor == "middle":
        x -= width / 2
    uses, cursor = [], 0
    for char in text:
        glyph = data["glyphs"][char]
        if char != " ":
            gid = f"display{ord(char):x}"
            d.define(f'<path id="{gid}" d="{glyph["path"]}"/>', key=gid)
            uses.append(f'<use href="#{gid}" x="{cursor}"/>')
        cursor += glyph["advance"]
    scale = size / data["upm"]
    return (f'<g transform="translate({n(x)} {n(y)}) scale({scale:.6f} {-scale:.6f})" '
            f'fill="{d.c(fill)}">{"".join(uses)}</g>')


def label(d, x, y, text, size=11, fill="fg_dim", anchor="start"):
    return d.text(x, y, text, size, 400, fill, anchor=anchor)


def rect(d, x, y, w, h, fill="bg", stroke=None, radius=0, extra=""):
    edge = f' stroke="{d.c(stroke)}"' if stroke else ""
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" '
            f'rx="{radius}" fill="{d.c(fill)}"{edge} {extra}/>')


def rule(d, x1, y1, x2, y2, color="line", extra=""):
    return (f'<path d="M{n(x1)} {n(y1)}L{n(x2)} {n(y2)}" fill="none" '
            f'stroke="{d.c(color)}" {extra}/>')


def arrow(d, x, y, size=16, color="accent"):
    return (f'<path d="M{x} {y + size}l{size} -{size}m-{size} 0h{size}v{size}" '
            f'fill="none" stroke="{d.c(color)}" stroke-width="2"/>')


def cross(d, x, y, color="muted", size=4):
    return (f'<path d="M{x-size} {y}h{size*2}M{x} {y-size}v{size*2}" '
            f'stroke="{d.c(color)}" stroke-width="1"/>')
