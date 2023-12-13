#!/usr/bin/env python3
import fontforge
import cairosvg
f = fontforge.open("../TT.sfd")
f.ascent+=300
f.descent+=300

glyphnames = ['A', 'B', 'C', 'D']

for gn in glyphnames:
    g=f[gn]
    if g.width == 0:
        g.width = f["A"].width
    svg_path = f"svgs/{gn}.svg"
    png_path = f"pngs/{gn}.png"
    g.export(svg_path)
    cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=600)
