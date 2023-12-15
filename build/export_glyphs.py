#!/usr/bin/env python3
import subprocess
import csv
import random
import numpy as np
import matplotlib.pyplot as plt
import fontforge
import cairosvg
import cv2 as cv

N = 1

VSHIFT_STD = 5
HSHIFT_STD = 5
BLUR = 3
NOISE = 256
INK_TIME = 3


def modify_glyph(img, ink_pad):

    shift_x = HSHIFT_STD*np.random.randn()
    shift_y = VSHIFT_STD*np.random.randn()
    T = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    img_mod = cv.warpAffine(
        img, T, (img.shape[1], img.shape[0]), borderValue=255)

    noise = np.random.normal(0, NOISE, img.shape)

    if img_mod.shape == ink_pad.shape:
        img_mod = 255*(1-(255-img_mod)/255.0*ink_pad) + noise
    else:
        print("glyph did not use ink pad")

    img_mod = cv.GaussianBlur(img_mod, (0, 0), BLUR)

    img_mod = ((img_mod > 128)*255).astype(np.uint8)

    return img_mod.astype(np.uint8)


f = fontforge.open("../TT.sfd")
f.ascent += 300
f.descent += 300

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

freq_by_ascii = {}
with open('ascii_freq.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=['ascii', 'freq'])
    for row in reader:
        freq_by_ascii[int(row['ascii'])] = float(row['freq'])

for gn in glyphnames:
    g = f[gn]
    g.width = f["M"].width
    svg_path = f"svgs/{gn}.svg"
    png_path = f"orig_pngs/{gn}.png"
    g.unlinkRef()
    g.export(svg_path)
    cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=600)
    subprocess.run(["convert", png_path, "-channel", "A",
                   "-negate", "-separate", png_path])
    ascii = fontforge.unicodeFromName(gn)
    if not ascii in freq_by_ascii:
        freq_by_ascii[ascii] = 5e-8

freq_map = np.zeros(f.ascent + f.descent)

for gn in glyphnames:
    orig_path = f"orig_pngs/{gn}.png"
    img = cv.imread(orig_path, cv.IMREAD_UNCHANGED)
    ascii = fontforge.unicodeFromName(gn)
    freq_map = freq_map + (255 - np.mean(img, 1))/255.0*freq_by_ascii[ascii]
    
ink_map = np.exp(-INK_TIME*freq_map)
ink_pad = np.tile(ink_map, (img.shape[1], 1)).transpose()
print(ink_pad.shape)

for gn in glyphnames:
    orig_path = f"orig_pngs/{gn}.png"
    img = cv.imread(orig_path, cv.IMREAD_UNCHANGED)
    for i in range(N):
        if i >= 1:
            out_path = f"pngs/{gn}.{i}.png"
        else:
            out_path = f"pngs/{gn}.png"
        img_mod = modify_glyph(img, ink_pad)
        cv.imwrite(out_path, img_mod)
