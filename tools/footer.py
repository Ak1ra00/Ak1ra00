#!/usr/bin/env python3
"""A quiet closing colophon, without a badge wall or third-party widgets."""

from design import cross, display, document, label, rect, rule
from svgkit import THEMES


def build(theme, compact=False):
    w,h=(440,178) if compact else (880,164)
    pad=28 if compact else 40
    d=document(w,h,theme,'Own the keys. Rewrite the rules.',
        'Ak1ra00 — independent experiments in firmware, cryptography and creative computing.')
    d.add(rect(d,0,0,w,h,'signal'))
    if compact:
        d.add(display(d,pad,58,'Own the keys.',35,'signal_ink'))
        d.add(display(d,pad,99,'Rewrite the rules.',35,'signal_ink'))
    else:
        d.add(display(d,pad,76,'Own the keys. Rewrite the rules.',43,'signal_ink'))
    d.add(rule(d,pad,h-48,w-pad,h-48,'signal_ink',extra='opacity=".25"'))
    d.add(label(d,pad,h-23,'AK1RA00 / ALWAYS TINKERING.',10,'signal_ink'))
    d.add(cross(d,w-pad,h-27,'signal_ink'))
    return d


def main():
    for theme in THEMES:
        for compact in (False,True):
            suffix='-compact' if compact else ''
            print(build(theme,compact).save(f'footer-{theme}{suffix}.svg'))


if __name__=='__main__': main()
