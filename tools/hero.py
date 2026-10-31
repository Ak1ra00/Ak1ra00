#!/usr/bin/env python3
"""The lab's masthead: mathematics, silicon, and play in an exploded diagram."""

import math

from design import cross, display, document, label, rect, rule
from svgkit import THEMES, n


def point(x, y, z=0):
    """Oblique projection of a square work surface; three physical layers."""
    return 0.82 * x - 0.82 * y, 0.42 * x + 0.42 * y - z


def path(points, close=False):
    return 'M' + 'L'.join(f'{n(x)} {n(y)}' for x, y in points) + ('Z' if close else '')


def diagram(d, cx, cy, scale=1):
    """An actual elliptic curve, a chip, and pixel invaders: one creative stack."""
    c = d.c
    out = []
    lo, hi = -104, 104
    corners = [(lo, lo), (hi, lo), (hi, hi), (lo, hi)]

    def plate(z, fill, stroke='line'):
        return f'<path d="{path([point(x,y,z) for x,y in corners], True)}" fill="{c(fill)}" stroke="{c(stroke)}"/>'

    def projected(points, z, stroke, width=1, extra=''):
        return f'<path d="{path([point(x,y,z) for x,y in points])}" fill="none" stroke="{c(stroke)}" stroke-width="{width}" {extra}/>'

    # The rear registration lines pass behind all three plates.
    for x, y in corners:
        a, b = point(x,y,112), point(x,y,-116)
        out.append(f'<path d="{path([a,b])}" stroke="{c("muted")}" stroke-dasharray="2 6" opacity=".55"/>')

    # 03: the pixel plane. These sprites are original, illustrative pixel art.
    out.append(plate(-100, 'bg_deep'))
    for row in range(4):
        for col in range(6):
            px, py = -76 + col*29, -68 + row*31
            color = 'accent' if row > 1 else 'fg_dim'
            sprite = ('0010100','0111110','1101011','1111111','1011101','0100010')
            cells=[]
            for iy, line in enumerate(sprite):
                for ix, cell in enumerate(line):
                    if cell == '1':
                        x,y=px+ix*2.6,py+iy*2.6
                        cells.append(path([point(x,y,-99),point(x+2,y,-99),point(x+2,y+2,-99),point(x,y+2,-99)],True))
            out.append(f'<path d="{"".join(cells)}" fill="{c(color)}" opacity="{.35+row*.2}"/>')
    out.append(projected([(-82,84),(82,84)],-99,'accent',2))

    # 02: the silicon plane with routed traces and a ceramic package.
    out.append(plate(0,'bg_raised','box'))
    for k in range(8):
        t = -35 + k*10
        span=72+(k%3)*8
        for rotation in range(4):
            pts=[(t,44),(t,53),(t+8,61),(t+8,span)]
            for _ in range(rotation): pts=[(-y,x) for x,y in pts]
            out.append(projected(pts,1,'muted',.8))
            ex,ey=point(*pts[-1],1)
            out.append(f'<circle cx="{n(ex)}" cy="{n(ey)}" r="1.8" fill="{c("accent")}"/>')
    chip=[(-43,-43),(43,-43),(43,43),(-43,43)]
    out.append(f'<path d="{path([point(x,y,5) for x,y in chip],True)}" fill="{c("bg_deep")}" stroke="{c("accent")}"/>')
    for i in range(7):
        t=-30+i*10
        for x1,y1,x2,y2 in ((t,-43,t,-51),(t,43,t,51),(-43,t,-51,t),(43,t,51,t)):
            out.append(projected([(x1,y1),(x2,y2)],5,'fg_soft',2.5))
    # Typography lies on the projected package surface.
    out.append('<g transform="matrix(.82 .42 -.82 .42 0 -5)">')
    out.append(display(d,0,9,'AK',28,'accent',anchor='middle'))
    out.append('</g>')

    # 01: a transparent plotting surface, carrying y² = x³ − 3x + 5.
    out.append(plate(100,'bg','box'))
    for k in range(-80,81,20):
        out.append(projected([(k,-100),(k,100)],100,'grid',.6))
        out.append(projected([(-100,k),(100,k)],100,'grid',.6))
    out.append(projected([(-100,0),(100,0)],101,'muted',.7))
    out.append(projected([(0,-100),(0,100)],101,'muted',.7))
    # Solve the leftmost root and sample uniformly in y near its vertical tangent.
    lo_root,hi_root=-3.,-2.
    for _ in range(70):
        mid=(lo_root+hi_root)/2
        if mid**3-3*mid+5<0: lo_root=mid
        else: hi_root=mid
    root=(lo_root+hi_root)/2
    xs=[root+(2.72-root)*(i/140)**2 for i in range(141)]
    curve=[(x*32,-math.sqrt(max(0,x**3-3*x+5))*18) for x in reversed(xs)]
    curve += [(x*32,math.sqrt(max(0,x**3-3*x+5))*18) for x in xs[1:]]
    out.append(projected(curve,102,'accent',2.3))
    px,py=point(1.4*32,-math.sqrt(1.4**3-3*1.4+5)*18,102)
    out.append(f'<circle cx="{n(px)}" cy="{n(py)}" r="4" fill="{c("amber")}"/>')
    out.append(f'<circle class="beacon" cx="{n(px)}" cy="{n(py)}" r="8" fill="none" stroke="{c("amber")}" opacity=".5"/>')
    # Side annotations; deliberately outside each drawing surface.
    for z,num in [(100,'01'),(0,'02'),(-100,'03')]:
        x,y=point(104,-104,z)
        out.append(label(d,x+11,y+4,num,10,'accent'))
    d.css('@keyframes beacon{50%{opacity:.15}}.beacon{animation:beacon 4s ease-in-out infinite}')
    return f'<g transform="translate({cx} {cy}) scale({scale})">{"".join(out)}</g>'


def build(theme, compact=False):
    w,h=(440,820) if compact else (880,530)
    d=document(w,h,theme,'Ak1ra00 — small devices, unreasonable ideas',
        'Independent experiments in custom firmware, applied cryptography and creative computing. '
        'An exploded illustration connects a real elliptic curve, a microchip, and a field of pixel invaders.')
    pad=28 if compact else 40
    d.add(rect(d,0,0,w,h,'bg',radius=3))
    d.add(rect(d,pad,26,24,24,'signal'))
    d.add(label(d,pad+12,42,'A',14,'signal_ink',anchor='middle'))
    d.add(label(d,pad+36,42,'AK1RA00 / INDEPENDENT BUILDER',9.5 if compact else 10.5,'fg_soft'))
    if not compact: d.add(label(d,w-pad,42,'IDEAS OUTSIDE THE SPEC.',10.5,'fg_dim',anchor='end'))
    d.add(rule(d,pad,65,w-pad,65))
    d.add(display(d,pad,153 if compact else 169,'Ak1ra00',82 if compact else 108))
    if compact:
        d.add(display(d,pad,213,'Small devices.',41))
        d.add(display(d,pad,261,'Unreasonable ideas.',35))
        d.add(label(d,pad,303,'Firmware, applied cryptography,',14,'fg_soft'))
        d.add(label(d,pad,326,'and experiments beyond the spec.',14,'fg_soft'))
        d.add(diagram(d,220,536,.92))
        d.add(label(d,220,752,'MATH → SILICON → PLAY',12,'accent',anchor='middle'))
        d.add(rule(d,pad,776,w-pad,776))
        d.add(label(d,pad,801,'BUILT FROM FIRST PRINCIPLES.',10,'fg_dim'))
        d.add(label(d,w-pad,801,'↓',16,'accent',anchor='end'))
    else:
        d.add(display(d,pad,244,'Small devices.',46))
        d.add(display(d,pad,298,'Unreasonable',46))
        d.add(display(d,pad,352,'ideas.',46,'accent'))
        d.add(label(d,pad,397,'Firmware, applied cryptography,',14.5,'fg_soft'))
        d.add(label(d,pad,420,'and experiments beyond the spec.',14.5,'fg_soft'))
        d.add(diagram(d,660,276,.94))
        d.add(label(d,660,104,'MATH → SILICON → PLAY',10,'fg_dim',anchor='middle'))
        d.add(rule(d,40,465,840,465))
        d.add(label(d,40,500,'01 / FIRMWARE',11.5,'fg_soft'))
        d.add(label(d,285,500,'02 / CRYPTOGRAPHY',11.5,'fg_soft'))
        d.add(label(d,578,500,'03 / CREATIVE COMPUTING',11.5,'fg_soft'))
        d.add(cross(d,840,500,'accent'))
    return d


def main():
    for theme in THEMES:
        for compact in (False,True):
            suffix='-compact' if compact else ''
            print(build(theme,compact).save(f'hero-{theme}{suffix}.svg'))


if __name__=='__main__': main()
