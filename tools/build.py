#!/usr/bin/env python3
"""Rebuild every static SVG in assets/ from scratch.

    python3 tools/build.py                 hero, fastfetch card, project cards, footer
    python3 tools/activity.py --out DIR    the live activity panel (CI redraws it daily)
    python3 tools/make_glyphs.py           only when the character set changes (needs fonttools)

Plain Python 3, no dependencies. Each module draws both themes: dark is the
Oracle desktop palette, light is the same three inks on paper.
"""

import importlib
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from svgkit import ASSETS  # noqa: E402

MODULES = ("hero", "fetch", "cards", "footer")


def main():
    for name in MODULES:
        importlib.import_module(name).main()
    for name in sorted(os.listdir(ASSETS)):
        if name.endswith(".svg"):
            path = os.path.join(ASSETS, name)
            ET.parse(path)  # every asset must be well-formed XML
            print(f"  {name:30} {os.path.getsize(path) / 1024:6.1f} KiB")


if __name__ == "__main__":
    main()
