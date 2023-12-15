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

CONST_VSHIFT_STD = 10
CONST_HSHIFT_STD = 10
VSHIFT_STD = 20
HSHIFT_STD = 20
BLUR = 3
NOISE = 256
INK_FRAC = 0.8
INK_STD = 0.05
PRESSURE_STD = 0.05
REPEATS = 1


def modify_glyph(img, shift):
    T = np.float32([[1, 0, shift[0]], [0, 1, shift[1]]])
    img_mod = cv.warpAffine(
        img, T, (img.shape[1], img.shape[0]), borderValue=255)

    noise = np.random.normal(0, NOISE, img.shape)

    ink_frac = np.random.normal(INK_FRAC, PRESSURE_STD)
    ink_pad = np.random.normal(ink_frac, INK_STD, (3, 3))
    ink_pad = cv.resize(ink_pad, (img_mod.shape[1], img_mod.shape[0]))
    if ink_frac <=1:
        img_mod = (255 - (255 - img_mod) * ink_pad) + noise
    else:
        img_blur = cv.GaussianBlur(img_mod, (0, 0), (ink_frac - 1)*100)
        img_mod = ((np.minimum(img, img_blur)/255)**ink_pad)*255 + noise

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

underscore_shift_x = CONST_HSHIFT_STD*np.random.randn()
underscore_shift_y = CONST_VSHIFT_STD*np.random.randn()
underscore_img = cv.imread("orig_pngs/underscore.png", cv.IMREAD_UNCHANGED)

for gn in glyphnames:
    orig_path = f"orig_pngs/{gn}.png"
    ascii = fontforge.unicodeFromName(gn)
    freq = freq_by_ascii[ascii]

    shift_x = CONST_HSHIFT_STD*np.random.randn()
    shift_y = CONST_VSHIFT_STD*np.random.randn()

    img = cv.imread(orig_path, cv.IMREAD_UNCHANGED)
    for i in range(N):
        if i >= 1:
            out_path = f"pngs/{gn}.{i}.png"
        else:
            out_path = f"pngs/{gn}.png"
        img_mod = np.zeros_like(img)
        for i in range(REPEATS):
            shift = (shift_x + HSHIFT_STD*np.random.randn(),
                    shift_y + VSHIFT_STD*np.random.randn())
            img_mod += (255 - modify_glyph(img, shift))
        if ITALIC and gn != "underscore":
            shift = (underscore_shift_x + HSHIFT_STD*np.random.randn(),
                    underscore_shift_y + VSHIFT_STD*np.random.randn())
            img_mod += (255 - modify_glyph(underscore_img, shift))

        cv.imwrite(out_path, (255 - img_mod).astype(np.uint8))
