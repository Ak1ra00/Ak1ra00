"""Original paper-key and repurposed-console illustrations for the profile."""

import hashlib

from design import cross, display, label, rect, rule
from svgkit import n


def _pixel_shape(rows, x, y, unit, fill):
    path = []
    for row, line in enumerate(rows):
        for col, cell in enumerate(line):
            if cell != ".":
                path.append(f"M{n(x+col*unit)} {n(y+row*unit)}h{unit}v{unit}h-{unit}z")
    return f'<path d="{"".join(path)}" fill="{fill}"/>'


def vaultless(d):
    """A paper key, deliberately non-scannable, with a derivation diagram."""
    c = d.c
    ink, paper, paper_line = "#26311d", "#e9eddb", "#adb89b"
    out = []

    # Registration grid and routed signal paths sit behind the physical paper.
    for x in range(16, 350, 24):
        for y in range(18, 270, 24):
            out.append(f'<circle cx="{x}" cy="{y}" r=".65" fill="{c("line")}"/>')
    out.extend([cross(d, 15, 18), cross(d, 345, 18), cross(d, 345, 265)])
    out.append(f'<path d="M184 74H269L289 94V151M175 203H220L239 184" '
               f'fill="none" stroke="{c("accent")}" stroke-width="1.25"/>')
    out.append(f'<path d="M193 83H260L279 102V151M177 213H222L247 188" '
               f'fill="none" stroke="{c("line")}"/>')
    for x, y in [(184, 74), (289, 151), (175, 203)]:
        out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{c("bg")}" '
                   f'stroke="{c("accent")}" stroke-width="1.2"/>')
    out.append(label(d, 241, 59, "k · P", 13, "accent"))

    # Printed key card: heavy stock, folded corner, crop marks and dot matrix.
    out.append('<g transform="rotate(-8 129 140)">')
    out.append(rect(d, 49, 28, 168, 224, "bg_deep", radius=2))
    out.append(f'<path d="M41 20H184L201 37V242H41Z" fill="{paper}" stroke="{ink}" '
               f'stroke-width="1.2"/>')
    out.append(f'<path d="M184 20V37H201" fill="none" stroke="{paper_line}"/>')
    out.append(label(d, 55, 43, "VAULTLESS / VLT1", 9, ink))
    out.append(f'<path d="M55 51H186" stroke="{paper_line}"/>')
    out.append(display(d, 54, 78, "PAPER KEY", 18, ink))
    out.append(label(d, 55, 94, "keep it in your hands.", 7.8, ink))

    # A unique matrix motif, rather than a misleading working QR credential.
    digest = hashlib.sha256(b"vaultless profile decorative matrix").digest() * 2
    cells = []
    for row in range(18):
        for col in range(23):
            bit = row * 23 + col
            if digest[bit // 8] & (1 << (bit % 8)):
                cells.append(f'M{57+col*5.4:.1f} {110+row*4.1:.1f}h3.2v2.3h-3.2z')
    out.append(f'<path d="{"".join(cells)}" fill="{ink}"/>')
    # Split the matrix with a clear typographic key marker; cannot scan as QR.
    out.append(rect(d, 86, 134, 66, 26, paper))
    out.append(display(d, 119, 153, "k", 23, ink, anchor="middle"))
    out.append(label(d, 55, 200, "ILLUSTRATION / NOT A KEY", 7.2, ink))
    out.append(f'<path d="M55 211H187" stroke="{paper_line}" stroke-dasharray="2 3"/>')
    out.append(label(d, 55, 227, "NO PASSWORDS STORED", 8.1, ink))
    out.append('</g>')

    # The derived output is a small, physical diagram element, not a UI badge.
    out.append(rect(d, 236, 151, 112, 67, "bg_deep", "line", radius=1))
    out.append(rect(d, 236, 151, 3, 67, "accent"))
    out.append(label(d, 249, 170, "DERIVE", 8.8, "fg_dim"))
    out.append(label(d, 249, 193, "••••••••", 16, "accent"))
    out.append(f'<path d="M247 205H335" stroke="{c("line")}"/>')
    out.append(label(d, 253, 243, "phrase + paper", 8.4, "fg_dim"))
    return "".join(out)


def quasar(d):
    """A custom console drawing: Coldcard Q hardware with arcade firmware."""
    c = d.c
    out = []
    # Sparse bench-drawing geometry gives the device room to breathe.
    out.append(f'<circle cx="186" cy="140" r="112" fill="none" stroke="{c("line")}" '
               f'stroke-dasharray="2 6"/>')
    out.append(f'<circle cx="186" cy="140" r="126" fill="none" stroke="{c("grid")}"/>')
    out.append(rule(d, 9, 140, 350, 140, "grid"))
    out.append(rule(d, 186, 11, 186, 269, "grid"))
    out.extend([cross(d, 16, 28), cross(d, 345, 251)])

    # Fixed callouts are readable independently from the tilted device.
    out.append(label(d, 9, 35, "320×240", 9.4, "fg_dim"))
    out.append(f'<path d="M10 43H62L99 81" stroke="{c("muted")}" fill="none"/>')
    out.append(label(d, 291, 240, "30 FPS", 9.4, "accent"))
    out.append(f'<path d="M288 230H276L255 207" stroke="{c("muted")}" fill="none"/>')

    out.append('<g transform="rotate(8 180 140)">')
    # The offset sidewall and nested case edges communicate thickness.
    out.append(f'<path d="M106 17H246L258 30V253L247 267H106L95 255V30Z" '
               f'fill="{c("bg_deep")}" stroke="{c("muted")}" stroke-width="1.5"/>')
    out.append(f'<path d="M246 17L258 30V253L247 267V31Z" '
               f'fill="{c("line")}" stroke="{c("muted")}" stroke-width="1"/>')
    out.append(f'<path d="M103 10H241L250 22V248L239 258H103L92 248V22Z" '
               f'fill="{c("bg_raised")}" stroke="{c("fg_dim")}" stroke-width="1.4"/>')
    out.append(f'<path d="M105 16H237M99 25V243M244 26V242" '
               f'fill="none" stroke="{c("line")}"/>')
    out.append(label(d, 171, 31, "QUASAR", 9.2, "accent", anchor="middle"))
    for x, y in [(100, 21), (241, 21), (100, 247), (241, 247)]:
        out.append(f'<circle cx="{x}" cy="{y}" r="2.4" fill="{c("bg_deep")}" '
                   f'stroke="{c("muted")}" stroke-width=".7"/>')
        out.append(f'<path d="M{x-1} {y}h2" stroke="{c("muted")}" stroke-width=".6"/>')

    # A 4:3 LCD: dark phosphor ground and a bespoke tiny shoot-'em-up scene.
    out.append(rect(d, 104, 40, 134, 104, "bg_deep", "line", radius=2))
    out.append(rect(d, 109, 45, 124, 93, "#121b12"))
    out.append(label(d, 115, 54, "STAGE 03", 4.9, "#b2cc88"))
    out.append(label(d, 226, 54, "SHMUP", 4.9, "#b2cc88", anchor="end"))
    out.append('<g opacity=".2">')
    for y in range(58, 136, 4):
        out.append(f'<path d="M110 {y}H232" stroke="#9ab473" stroke-width=".35"/>')
    out.append('</g>')
    for x, y in [(119, 72), (146, 65), (171, 80), (207, 67), (222, 91), (125, 111), (215, 120), (158, 104)]:
        out.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="#95b16f"/>')
    enemy = [".X...X.", "..XXX..", ".XXXXX.", "XX.X.XX", "X.....X"]
    for x, y in [(124, 72), (164, 67), (203, 76)]:
        out.append(_pixel_shape(enemy, x, y, 1.4, "#f4b17d"))
    # Geometric shield architecture evokes the Dyson Array stage.
    out.append('<path d="M139 82L146 78H192L199 82V88L192 92H146L139 88Z" '
               'fill="none" stroke="#a5ba79" stroke-width="1"/>')
    out.append('<path d="M153 82H185M156 85H182M153 88H185" stroke="#a5ba79" stroke-width=".8"/>')
    ship = ["...X...", "...X...", "..XXX..", "X.XXX.X", "XXXXXXX", "XX.X.XX"]
    out.append(_pixel_shape(ship, 165, 116, 1.6, "#d2f898"))
    out.append('<path d="M169 111V105M172 100V96" stroke="#d2f898" stroke-width="1"/>')
    out.append('<path d="M168 129v4M172 129v5" stroke="#f4b17d" stroke-width="1.2"/>')
    # A gentle moving spark, with a visible static baseline for reduced motion.
    d.css('@keyframes q-shot{0%,100%{opacity:.3}50%{opacity:1}}'
          '.q-shot{animation:q-shot 2.8s ease-in-out infinite}')
    out.append('<circle class="q-shot" cx="171" cy="103" r="1.5" fill="#e1ffb6"/>')

    # Tactile control row and the Q's unusually dense alphanumeric keyboard.
    out.append(label(d, 171, 155, "C O L D C A R D   Q", 4.8, "muted", anchor="middle"))
    for x, text in [(111, "◀"), (141, "▼"), (171, "▲"), (201, "▶")]:
        out.append(rect(d, x, 163, 25, 13, "bg_deep", "line", radius=2))
        out.append(label(d, x+12.5, 172, text, 6, "fg_dim", anchor="middle"))
    rows = ["1234567890", "QWERTYUIOP", "ASDFGHJKL-", "ZXCVBNM.<>"]
    for row, chars in enumerate(rows):
        for col, ch in enumerate(chars):
            x, y = 109 + col*12.5, 184 + row*13.5
            out.append(rect(d, x, y, 10, 10, "bg_deep", "line", radius=1.3))
            out.append(label(d, x+5, y+7, ch, 4.5, "fg_dim", anchor="middle"))
    out.append(rect(d, 126, 241, 90, 3, "line", radius=1))
    out.append('</g>')
    return "".join(out)
