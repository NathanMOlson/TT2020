import glob
import os
import fontforge

f_base = fontforge.open("../TT.sfd")
f = fontforge.font()

f.ascent = f_base.ascent + 300
f.descent = f_base.descent + 300
f.em = f_base.em
f.uwidth = f_base.uwidth
f.upos = f_base.upos


for path in glob.glob("pngs/*.png"):
    name = os.path.splitext(os.path.basename(path))[0]
    print(path, name)
    g = f.createChar(-1, name)
    g.clear()
    try:
        # Change this line as needed, depending on where the glyph bitmaps are
        g.importOutlines(path)
    except:
        print(f"Failed to import {g.glyphname}")
        continue
    g.activeLayer = 1
    g.autoTrace()
    g.clear(0)
    g.width = 547

f.save("test.sfd")
