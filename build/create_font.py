import glob
import os
import fontforge

f_base = fontforge.open("../TT.sfd")
f = fontforge.font()

f.ascent = f_base.ascent
f.descent = f_base.descent
f.em = f.ascent + f.descent
f.uwidth = f_base.uwidth
f.upos = f_base.upos


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
    g.nltransform("x - 237", "y")
    g.width = 547

f.save("test.sfd")
