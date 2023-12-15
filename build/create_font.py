#!/usr/bin/env python3
import subprocess
import glob
import os
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
import fontforge
import cairosvg
import cv2 as cv


@dataclass
class FontConfig:
    base_font: str = "../TT.sfd"
    num_alts: int = 1
    const_vshift_std: float = 5.0
    const_hshift_std: float = 5.0
    vshift_std: float = 5.0
    hshift_std: float = 25.0
    blur: float = 3.0
    noise: float = 256.0
    ink_frac: float = 0.75
    ink_std: float = 0.08
    pressure_std: float = 0.08
    bold_repeats: int = 2
    font_name: str = "NoJo"


IMG_WIDTH = 1001
ORIG_GLYPH_DIR = "orig_pngs"

GLYPHNAMES = ["space",
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


def modify_glyph(img, shift, config: FontConfig):
    T = np.float32([[1, 0, shift[0]], [0, 1, shift[1]]])
    img_mod = cv.warpAffine(
        img, T, (img.shape[1], img.shape[0]), borderValue=255)

    noise = np.random.normal(0, config.noise, img.shape)

    ink_frac = np.random.normal(config.ink_frac, config.pressure_std)
    ink_pad = np.random.normal(ink_frac, config.ink_std, (4, 6))
    ink_pad = cv.resize(ink_pad, (img_mod.shape[1], img_mod.shape[0]))
    if ink_frac <= 1:
        img_mod = (255 - (255 - img_mod) * ink_pad) + noise
    else:
        img_blur = cv.GaussianBlur(img_mod, (0, 0), (ink_frac - 1)*100)
        img_mod = ((np.minimum(img_mod, img_blur)/255)**ink_pad)*255 + noise

    img_mod = cv.GaussianBlur(img_mod, (0, 0), config.blur)

    img_mod = ((img_mod > 128)*255).astype(np.uint8)

    return img_mod.astype(np.uint8)


def create_orig_pngs(config: FontConfig):
    f_base = fontforge.open(config.base_font)

    for gn in GLYPHNAMES:
        g = f_base[gn]
        g.width = f_base["M"].width
        svg_path = f"svgs/{gn}.svg"
        png_path = f"{ORIG_GLYPH_DIR}/{gn}.png"
        g.unlinkRef()
        g.export(svg_path)
        cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=600)
        subprocess.run(["convert", png_path, "-channel", "A",
                        "-negate", "-separate", png_path])


def make_glyphs(config: FontConfig, bold: bool, italic: bool):
    underscore_shift_x = config.const_hshift_std*np.random.randn()
    underscore_shift_y = config.const_vshift_std*np.random.randn()
    underscore_img = cv.imread(
        f"{ORIG_GLYPH_DIR}/underscore.png", cv.IMREAD_UNCHANGED)
    T = np.float32(
        [[1, 0, (IMG_WIDTH - underscore_img.shape[1])/2], [0, 1, 0]])
    underscore_img = cv.warpAffine(
        underscore_img, T, (IMG_WIDTH, underscore_img.shape[0]), borderValue=255)

    for gn in GLYPHNAMES:
        orig_path = f"{ORIG_GLYPH_DIR}/{gn}.png"

        if gn == "underscore":
            shift_x = underscore_shift_x
            shift_y = underscore_shift_y
        else:
            shift_x = config.const_hshift_std*np.random.randn()
            shift_y = config.const_vshift_std*np.random.randn()

        img = cv.imread(orig_path, cv.IMREAD_UNCHANGED)

        T = np.float32([[1, 0, (IMG_WIDTH - img.shape[1])/2], [0, 1, 0]])
        img = cv.warpAffine(
            img, T, (IMG_WIDTH, img.shape[0]), borderValue=255)
        for i in range(config.num_alts):
            if i >= 1:
                out_path = f"pngs/{gn}.{i}.png"
            else:
                out_path = f"pngs/{gn}.png"
            img_mod = np.zeros_like(img)
            repeats = config.bold_repeats if bold else 1
            for i in range(repeats):
                shift = (shift_x + config.hshift_std*np.random.randn(),
                         shift_y + config.vshift_std*np.random.randn())
                img_mod += (255 - modify_glyph(img, shift, config))
            if italic and gn != "underscore":
                shift = (underscore_shift_x + config.hshift_std*np.random.randn(),
                         underscore_shift_y + config.vshift_std*np.random.randn())
                img_mod += (255 - modify_glyph(underscore_img, shift, config))

            cv.imwrite(out_path, (255 - img_mod).astype(np.uint8))


def create_font_from_pngs(config, bold: bool, italic: bool):
    f_base = fontforge.open("../TT.sfd")
    f = fontforge.font()

    f.ascent = f_base.ascent
    f.descent = f_base.descent
    f.em = f.ascent + f.descent
    f.uwidth = f_base.uwidth
    f.upos = f_base.upos

    font_name = config.font_name
    f.weight = "Regular"
    if bold:
        font_name += "-Bold"
        f.weight = "Bold"
    if italic:
        font_name += "-Italic"
        f.weight = "Italic"
    f.familyname = config.font_name
    f.fontname = font_name
    f.fullname = font_name

    for path in glob.glob("pngs/*.png"):
        name = os.path.splitext(os.path.basename(path))[0]
        print(path, name)
        g = f.createChar(-1, name)
        g.clear()
        try:
            g.importOutlines(path)
        except:
            print(f"Failed to import {g.glyphname}")
            continue
        g.activeLayer = 1
        g.autoTrace()
        g.clear(0)
        # 237: 10 built in to svg export, 227 introduced by expanging images to IMG_WIDTH=1001
        shift = 10 + (IMG_WIDTH - f_base["M"].width)/2
        g.nltransform(f"x - {shift}", "y")
        g.width = f_base["M"].width

    f.save(f"{font_name}.sfd")
    f.generate(f"{font_name}.ttf")


def create_font(config: FontConfig):
    create_orig_pngs(config)

    make_glyphs(config, bold=False, italic=False)
    create_font_from_pngs(config, bold=False, italic=False)

    make_glyphs(config, bold=False, italic=True)
    create_font_from_pngs(config, bold=False, italic=True)

    make_glyphs(config, bold=True, italic=False)
    create_font_from_pngs(config, bold=True, italic=False)


np.random.seed(1234)
configs = [FontConfig()]
configs.append(FontConfig(font_name="NoJoLight",
                          ink_frac=0.5, ink_std=0.03, pressure_std=0.01))
configs.append(FontConfig(font_name="NoJoInky", ink_frac=1.5))
configs.append(FontConfig(font_name="NoJoWoggly", ink_std=0.16, pressure_std=0.08,
                          const_hshift_std=8, const_vshift_std=8, vshift_std=16, hshift_std=40))
for config in configs:
    create_font(config)
