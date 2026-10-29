#!/usr/bin/env python3
"""Extract JetBrains Mono outlines into tools/glyphs.json.

Every SVG in assets/ draws its text as paths built from these outlines, so the
profile looks identical on every machine: an <img> SVG cannot load web fonts,
and system monospace fonts differ in width and shape.

Only needed when the character set or weights change; build.py and the
activity workflow read glyphs.json and need nothing but the standard library.

Usage:
    tools/make_glyphs.py [--fonts /usr/share/fonts/truetype/jetbrains-mono]

Requires: fonttools. Font: JetBrains Mono (SIL OFL 1.1, see fonts/OFL.txt).
"""

import argparse
import json
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

WEIGHTS = {400: "Regular", 700: "Bold", 800: "ExtraBold"}

CHARSET = (
    "".join(chr(c) for c in range(0x20, 0x7F))
    + "·•…–—‘’“”«»‹›°±×÷²³¹⁰⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉µπλΣΩαβγδεθκμσφψω"
    + "ℝℤℕℚℂ𝔽∀∃∈∉∑∏∫∂∇√∞≈≠≤≥≡−∓⋅∙⊕⊗∘⊂∪∩∅∧∨⊥∥↦⌊⌋⌈⌉⟨⟩‖′″¬§©®™€£¥ⁿⁱ⁻⁺"
    + "←↑→↓↗↘↖↙↔⇒⇐"
    + "─│┌┐└┘├┤┬┴┼━┃┏┓┗┛╭╮╯╰═║╔╗╚╝"
    + "█▓▒░▁▂▃▄▅▆▇▀▐▌■□▪▫●○◆◇◉◎▸▹▶◀▲▼△▽❯❮✓✗⏻⌘"
)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", default="/usr/share/fonts/truetype/jetbrains-mono")
    ap.add_argument("--out", default=os.path.join(here, "glyphs.json"))
    args = ap.parse_args()

    out = {"font": "JetBrains Mono 2.304", "license": "SIL OFL 1.1 (tools/fonts/OFL.txt)",
           "upm": 1000, "advance": 600, "weights": {}}
    for weight, style in WEIGHTS.items():
        font = TTFont(os.path.join(args.fonts, f"JetBrainsMono-{style}.ttf"))
        cmap = font.getBestCmap()
        glyphs = font.getGlyphSet()
        table = {}
        for ch in CHARSET:
            name = cmap.get(ord(ch))
            if name is None:
                continue
            assert glyphs[name].width == 600, (ch, glyphs[name].width)
            pen = SVGPathPen(glyphs)
            glyphs[name].draw(pen)
            table[ch] = pen.getCommands()
        out["weights"][str(weight)] = table
        missing = [c for c in CHARSET if c not in table]
        print(f"{style}: {len(table)} glyphs, missing {''.join(missing) or 'none'}")

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {args.out} ({os.path.getsize(args.out) // 1024} KiB)")


if __name__ == "__main__":
    main()
