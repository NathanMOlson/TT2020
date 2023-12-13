import glob
import os
import fontforge
f = fontforge.font()

f.ascent += 300
f.descent += 300


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
    #g.clear(0)
    g.right_side_bearing = 547

f.save("test.sfd")
