#!/usr/bin/env python3
"""A compact field inventory of the languages, devices, and desktop in the work."""

from design import display, document, label, rect, rule
from svgkit import THEMES

GROUPS = (
    ('01 / LANGUAGES', 'Close to the metal.', ('C / C++ / Python', 'MicroPython / JS / Lua')),
    ('02 / HARDWARE', 'Small, capable machines.', ('Coldcard Mk4 / Coldcard Q', 'ESP32 / LilyGO T-Display')),
    ('03 / WORKSPACE', 'Built to be lived in.', ('Arch / Omarchy / Hyprland', 'Neovim / Oracle')),
)


def build(theme, compact=False):
    w,h=(440,384) if compact else (880,178)
    d=document(w,h,theme,'On the workbench',
        'Languages: C, C++, Python, MicroPython, JavaScript and Lua. Hardware: Coldcard Mk4, '
        'Coldcard Q, ESP32 and LilyGO T-Display. Desktop: Arch Linux, Omarchy, Hyprland, Neovim and Oracle.')
    d.add(rect(d,0,0,w,h,'bg'))
    for i,(heading,title,lines) in enumerate(GROUPS):
        x,y=(28,32+i*120) if compact else (28+i*286,32)
        if i:
            d.add(rule(d,28,y-22,w-28,y-22)) if compact else d.add(rule(d,x-16,28,x-16,h-28))
        d.add(label(d,x,y,heading,10,'accent'))
        d.add(display(d,x,y+33,title,21 if compact else 18))
        for j,line in enumerate(lines):
            d.add(label(d,x,y+62+j*19,line,12 if compact else 11,'fg_soft'))
    return d


def main():
    for theme in THEMES:
        for compact in (False,True):
            suffix='-compact' if compact else ''
            print(build(theme,compact).save(f'fetch-{theme}{suffix}.svg'))


if __name__=='__main__': main()
