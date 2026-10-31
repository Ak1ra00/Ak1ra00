#!/usr/bin/env python3
"""Preview the profile README with local artwork and clearly marked demo activity.

    python3 tools/build.py
    python3 tools/preview.py --theme dark
    python3 tools/preview.py --theme light --out dist/preview/light.html

Open the printed HTML file directly in a browser. No server, package install,
external fonts, or JavaScript is required. This small renderer supports the
README's Markdown subset and preserves its HTML, links, and responsive pictures;
GitHub remains the authority for final README rendering.
"""

import argparse
import html
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent.parent
ASSET_URL = "https://raw.githubusercontent.com/Ak1ra00/Ak1ra00/main/assets/"
ACTIVITY_URL = "https://raw.githubusercontent.com/Ak1ra00/Ak1ra00/output/"


def inline(text):
    """Render the simple inline Markdown used by the profile, preserving HTML."""
    tokens = []

    def keep(value):
        tokens.append(value)
        return f"\x00{len(tokens) - 1}\x00"

    text = re.sub(r"`([^`]+)`", lambda m: keep(f"<code>{html.escape(m[1])}</code>"), text)
    text = re.sub(r"<[^>]+>", lambda m: keep(m[0]), text)
    text = html.escape(text, quote=False)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^\s)]+)\)",
        lambda m: keep(f'<img src="{html.escape(m[2], quote=True)}" alt="{html.escape(m[1], quote=True)}">'),
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^\s)]+)\)",
        lambda m: f'<a href="{html.escape(m[2], quote=True)}">{m[1]}</a>',
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: tokens[int(m[1])], text)


def markdown(source):
    """Convert the README's basic block syntax, leaving raw HTML untouched."""
    output, paragraph = [], []
    in_list = False
    in_comment = False
    in_tag = False
    raw_block = None
    code = None

    def flush():
        if paragraph:
            output.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for line in source.splitlines():
        stripped = line.strip()
        if raw_block:
            output.append(line)
            if re.search(rf"</{raw_block}\s*>", line, flags=re.IGNORECASE):
                raw_block = None
            continue
        if code is not None:
            if stripped.startswith("```"):
                output.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
                code = None
            else:
                code.append(line)
            continue
        if stripped.startswith("```"):
            flush()
            close_list()
            code = []
            continue
        if in_comment or stripped.startswith("<!--"):
            flush()
            close_list()
            output.append(line)
            in_comment = "-->" not in line
            continue
        if in_tag or stripped.startswith("<"):
            flush()
            close_list()
            output.append(line)
            # Markdown inside raw block elements is not interpreted by GitHub.
            # Details remains a container so Markdown after its summary works.
            block = re.match(r"<(p|picture|table|div|pre|figure|section|article)(?:\s|>)", stripped, re.IGNORECASE)
            if block and not re.search(rf"</{block[1]}\s*>", line, re.IGNORECASE):
                raw_block = block[1]
            # Multiline HTML tags are used by some picture source conventions.
            in_tag = line.rfind("<") > line.rfind(">") if not in_tag else ">" not in line
            continue
        if not stripped:
            flush()
            close_list()
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush()
            close_list()
            level = len(heading[1])
            output.append(f"<h{level}>{inline(heading[2])}</h{level}>")
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet:
            flush()
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{inline(bullet[1])}</li>")
            continue
        if stripped in ("---", "***", "___"):
            flush()
            close_list()
            output.append("<hr>")
            continue
        close_list()
        paragraph.append(stripped)
    flush()
    close_list()
    if code is not None:
        raise ValueError("README has an unclosed fenced code block")
    return "\n".join(output)


def localize(source, target, activity, theme):
    def relative(directory):
        return Path(os.path.relpath(directory, target.parent)).as_posix() + "/"

    source = source.replace(ASSET_URL, relative(ROOT / "assets"))
    source = source.replace(ACTIVITY_URL, relative(activity))
    source = re.sub(
        r'((?:src|srcset)=["\'])(?:\./)?assets/',
        lambda m: m[1] + relative(ROOT / "assets"),
        source,
    )
    # Force the requested preview theme while retaining compact viewport rules.
    # A CSS color-scheme declaration alone does not change picture media queries.
    return re.sub(
        r"\(prefers-color-scheme:\s*(dark|light)\)",
        lambda m: "(min-width: 0px)" if m[1] == theme else "(min-width: 100000px)",
        source,
    )


class ImageSources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = set()
        self.missing_alt = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img":
            if not attrs.get("alt", "").strip():
                self.missing_alt += 1
            if attrs.get("src"):
                self.paths.add(attrs["src"])
        elif tag == "source" and attrs.get("srcset"):
            self.paths.update(part.strip().split()[0] for part in attrs["srcset"].split(","))


def validate_images(body, target):
    sources = ImageSources()
    sources.feed(body)
    missing = []
    for source in sorted(sources.paths):
        parsed = urlparse(source)
        if parsed.scheme or parsed.netloc:
            continue
        path = target.parent / unquote(parsed.path)
        if not path.is_file():
            missing.append(str(path.resolve()))
    if missing:
        raise ValueError("Local artwork is missing; run python3 tools/build.py first:\n" + "\n".join(missing))
    if sources.missing_alt:
        raise ValueError(f"README contains {sources.missing_alt} images without descriptive alt text")


def page(body, theme):
    colors = {
        "dark": ("#0d1117", "#e6edf3", "#919aa5", "#a8cc8b", "#30363d", "#161b22"),
        "light": ("#ffffff", "#1f2328", "#656d76", "#456721", "#d0d7de", "#f6f8fa"),
    }
    bg, fg, muted, link, border, raised = colors[theme]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="{theme}">
<title>Ak1ra00 — profile preview ({theme})</title>
<style>
:root {{color-scheme:{theme}; background:{bg}; color:{fg};}}
* {{box-sizing:border-box;}}
body {{margin:0; font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}}
.preview-note {{max-width:944px; margin:24px auto 0; padding:12px 32px;
  color:{muted}; font-size:12px; border-bottom:1px solid {border};}}
article {{max-width:944px; margin:0 auto; padding:28px 32px 48px; overflow-wrap:break-word;}}
a {{color:{link}; text-decoration:none;}}
a:hover {{text-decoration:underline;}}
a:focus-visible,summary:focus-visible {{outline:2px solid {link}; outline-offset:4px;}}
p {{margin:0 0 16px;}}
h1,h2,h3,h4,h5,h6 {{font-weight:600; line-height:1.25; margin:24px 0 16px;}}
h1 {{font-size:2em;}} h2 {{font-size:1.5em;}} h3 {{font-size:1.25em;}}
h1,h2 {{padding-bottom:.3em; border-bottom:1px solid {border};}}
img {{max-width:100%; vertical-align:middle;}}
img[width="100%"] {{height:auto;}}
ul {{padding-left:2em; margin:0 0 16px;}} li+li {{margin-top:.25em;}}
hr {{height:1px; border:0; background:{border}; margin:24px 0;}}
details {{margin:16px 0;}} summary {{cursor:pointer;}}
code {{padding:.2em .4em; font-size:85%; border-radius:4px; background:{raised};}}
pre {{padding:16px; background:{raised}; border-radius:6px; overflow:auto;}}
pre code {{padding:0;}}
table {{border-collapse:collapse; margin:0 0 16px; max-width:100%;}}
td,th {{padding:6px 13px; border:1px solid {border};}}
@media(max-width:600px) {{
  article {{padding:20px 16px 32px;}}
  .preview-note {{margin-top:8px; padding:10px 16px;}}
  body {{font-size:15px;}}
}}
</style>
</head>
<body>
<aside class="preview-note" aria-label="Preview notice">Local {theme} preview · Activity uses synthetic demo data. This file does not publish or update the profile.</aside>
<article aria-label="GitHub profile README">
{body}
</article>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--theme", choices=("dark", "light"), default="dark")
    parser.add_argument("--out", type=Path, help="output HTML file (default: dist/preview/index-THEME.html)")
    args = parser.parse_args()
    target = (args.out or ROOT / "dist" / "preview" / f"index-{args.theme}.html").resolve()
    if target.suffix.lower() not in (".html", ".htm"):
        parser.error("--out must name an .html or .htm file")
    target.parent.mkdir(parents=True, exist_ok=True)
    activity = target.parent / "activity-demo"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "activity.py"), "--demo", "--out", str(activity)],
        cwd=ROOT,
        check=True,
    )
    source = (ROOT / "README.md").read_text(encoding="utf-8")
    body = localize(markdown(source), target, activity, args.theme)
    validate_images(body, target)
    target.write_text(page(body, args.theme), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
