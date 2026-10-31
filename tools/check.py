#!/usr/bin/env python3
"""Check generated SVG integrity and the responsive artwork in the README."""

from html.parser import HTMLParser
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
NS = "{http://www.w3.org/2000/svg}"
STEMS = ("hero", "fetch", "footer", "card-vaultless", "card-quasar",
         "card-tamagotchi", "card-deepsea", "card-oracle", "card-opencare")
EXPECTED = {f"{stem}-{theme}{suffix}.svg"
            for stem in STEMS for theme in ("dark", "light")
            for suffix in ("", "-compact")}


def validate_svg(path):
    source = path.read_text(encoding="utf-8")
    root = ET.fromstring(source)
    assert root.tag == NS + "svg", f"{path.name}: root is not SVG"
    expected_width = 440 if "-compact" in path.stem else 880
    assert int(root.get("width")) == expected_width, f"{path.name}: wrong layout width"
    assert root.get("viewBox") == f'0 0 {root.get("width")} {root.get("height")}', path
    for tag in ("title", "desc"):
        node = root.find(NS + tag)
        assert node is not None and node.text and node.text.strip(), f"{path.name}: missing {tag}"
    identifiers, references = set(), set()
    for node in root.iter():
        identifier = node.get("id")
        if identifier:
            assert identifier not in identifiers, f"{path.name}: duplicate #{identifier}"
            identifiers.add(identifier)
        assert node.tag not in {NS + "script", NS + "foreignObject"}, path
        for key, value in node.attrib.items():
            if key.endswith("href"):
                assert value.startswith("#"), f"{path.name}: external image/font dependency"
                references.add(value[1:])
            references.update(re.findall(r"url\(#([^)]+)\)", value))
    references.update(re.findall(r"url\(#([^)]+)\)", source))
    assert references <= identifiers, f"{path.name}: unresolved {references - identifiers}"
    assert "prefers-reduced-motion:reduce" in source, f"{path.name}: missing reduced motion"
    assert "@font-face" not in source, f"{path.name}: external font"


class ProfileImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = set()
        self.pictures = []
        self.active = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "picture":
            assert self.active is None, "nested picture"
            self.active = []
        elif tag == "source":
            source = attrs.get("srcset", "")
            self.sources.add(source)
            if self.active is not None:
                self.active.append((attrs.get("media", ""), source))
        elif tag == "img":
            assert attrs.get("alt", "").strip(), "image is missing alt text"
            self.sources.add(attrs.get("src", ""))

    def handle_endtag(self, tag):
        if tag == "picture":
            assert self.active is not None, "unmatched picture close tag"
            self.pictures.append(self.active)
            self.active = None


def main():
    paths = sorted((ROOT / "assets").glob("*.svg"))
    actual = {path.name for path in paths}
    assert actual == EXPECTED, f"Static asset mismatch: {actual ^ EXPECTED}"
    for path in paths:
        validate_svg(path)
    reader = ProfileImages()
    reader.feed((ROOT / "README.md").read_text(encoding="utf-8"))
    assert reader.active is None, "unclosed picture"
    assert len(reader.pictures) == 10, "Expected nine static panels and one live activity panel"
    referenced_assets = set()
    prefix = "https://raw.githubusercontent.com/Ak1ra00/Ak1ra00/main/assets/"
    for source in reader.sources:
        if source.startswith(prefix):
            name = source[len(prefix):]
            assert name in EXPECTED, f"README references missing asset: {name}"
            referenced_assets.add(name)
    assert referenced_assets == EXPECTED, f"Unreferenced layouts: {EXPECTED - referenced_assets}"
    for sources in reader.pictures:
        assert len(sources) == 4, "Each picture needs desktop/mobile sources in both themes"
        for (media, source), (theme, compact) in zip(
            sources, (("dark", True), ("light", True), ("dark", False), ("light", False))
        ):
            assert f"prefers-color-scheme: {theme}" in media, media
            assert ("max-width: 600px" in media) == compact, media
            suffix = "-compact" if compact else ""
            assert source.endswith(f"-{theme}{suffix}.svg"), source
    print(f"PASS: {len(paths)} SVGs; metadata, glyph references, reduced motion, and all responsive README sources.")


if __name__ == "__main__":
    main()
