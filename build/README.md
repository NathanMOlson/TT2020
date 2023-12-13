# TT2020 build files

sudo apt-get intall python3-fontforge parallel gegl inkscape gimp
pip3 install python-gegl CairoSVG

Required:
* Python 3+
* GEGL
* `python-gegl`
* GIMP
* Inkscape

Here lie the TT2020 build files; they are typically called in this order:

* gen_glyphs.sh (list_glyphs.py, export_glyph.py)
* gen_style.sh (style[A-G].sh)

Most styles are generated via GIMP scripts; all styles so far generate bitmaps which are expected to be autotraced by FontForge.

Possible future work would be, using Inkscape to generate a style, and using OpenGL shaders to much more quickly generate a style than GIMP can do.
