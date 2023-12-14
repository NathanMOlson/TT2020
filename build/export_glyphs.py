#!/usr/bin/env python3
import subprocess
import random
import numpy as np
import fontforge
import cairosvg
import cv2 as cv

N = 10

VSHIFT_STD = 5
HSHIFT_STD = 5

def modify_glyph(img):
    shift_x = HSHIFT_STD*np.random.randn()
    shift_y = VSHIFT_STD*np.random.randn()
    T = np.float32([ [1,0,shift_x], [0,1,shift_y] ])   
    img_mod = cv.warpAffine(img, T, (img.shape[1], img.shape[0]), borderValue=255)
    return img_mod

f = fontforge.open("../TT.sfd")
f.ascent+=300
f.descent+=300

glyphnames = ["space",
"exclam",
"quotedbl",
"numbersign",
"dollar",
"percent",
"ampersand",
"quotesingle",
"parenleft",
"parenright",
"asterisk",
"plus",
"comma",
"hyphen",
"period",
"slash",
"zero",
"one",
"two",
"three",
"four",
"five",
"six",
"seven",
"eight",
"nine",
"colon",
"semicolon",
"less",
"equal",
"greater",
"question",
"at",
"A",
"B",
"C",
"D",
"E",
"F",
"G",
"H",
"I",
"J",
"K",
"L",
"M",
"N",
"O",
"P",
"Q",
"R",
"S",
"T",
"U",
"V",
"W",
"X",
"Y",
"Z",
"bracketleft",
"backslash",
"bracketright",
"asciicircum",
"underscore",
"grave",
"a",
"b",
"c",
"d",
"e",
"f",
"g",
"h",
"i",
"j",
"k",
"l",
"m",
"n",
"o",
"p",
"q",
"r",
"s",
"t",
"u",
"v",
"w",
"x",
"y",
"z",
"braceleft",
"bar",
"braceright",
"asciitilde"]

for gn in glyphnames:
    g=f[gn]
    if g.width == 0:
        g.width = f["A"].width
    svg_path = f"svgs/{gn}.svg"
    png_path = f"pngs/{gn}.png"
    g.unlinkRef()
    g.export(svg_path)
    cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=600)
    subprocess.run(["convert", png_path, "-channel", "A", "-negate", "-separate", png_path])
    img = cv.imread(png_path, cv.IMREAD_UNCHANGED)
    for i in range(N):
        if i >= 1:
            png_path = f"pngs/{gn}.{i}.png"
            img_mod = modify_glyph(img)
            cv.imwrite(png_path, img_mod)
