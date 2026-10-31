#!/usr/bin/env python3
"""Rebuild the bundled Space Grotesk Bold outlines (requires fonttools).

Download the pinned upstream font, then pass the local TTF:
    python3 tools/make_display_glyphs.py /path/to/SpaceGrotesk.ttf

Source (SIL OFL 1.1; see fonts/SpaceGrotesk-OFL.txt):
https://raw.githubusercontent.com/google/fonts/6c1dbe27dcf7d817d4b62cec033ba77fa8e2a5ec/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf

Normal artwork builds use the JSON already in the repository and need no fonts
or third-party dependencies. This command never downloads files automatically.
"""

import argparse
import hashlib
import json
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONT_SHA256 = "acad6de1fc93436f5c0f1f4137751ef04f1aea3063e7036535970ffcfbd79f72"
CHARSET = "".join(chr(i) for i in range(32, 127)) + "→↗·—"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font", type=Path)
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).with_name("display-glyphs.json"))
    args = parser.parse_args()
    if hashlib.sha256(args.font.read_bytes()).hexdigest() != FONT_SHA256:
        parser.error("font checksum differs from the pinned upstream source")
    font = instantiateVariableFont(TTFont(args.font), {"wght": 700}, inplace=True)
    cmap, glyphs = font.getBestCmap(), font.getGlyphSet()
    chars = {}
    for char in CHARSET:
        glyph = glyphs[cmap[ord(char)]]
        pen = SVGPathPen(glyphs)
        glyph.draw(pen)
        chars[char] = {"advance": glyph.width, "path": pen.getCommands()}
    data = {
        "font": "Space Grotesk Bold",
        "license": "SIL OFL 1.1 (fonts/SpaceGrotesk-OFL.txt)",
        "upm": font["head"].unitsPerEm,
        "glyphs": chars,
    }
    args.out.write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {len(chars)} glyphs to {args.out}")


if __name__ == "__main__":
    main()
