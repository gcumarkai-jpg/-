"""Make a contact sheet of a rendered set: python3 src/preview.py out/<id>"""
import sys
from pathlib import Path
from PIL import Image
d = Path(sys.argv[1]); fs = sorted(d.glob("[0-9][0-9].jpg"))
W, H = 540, 675
sheet = Image.new("RGB", (W * 4 + 50, H * 2 + 30), "white")
for k, f in enumerate(fs):
    sheet.paste(Image.open(f).resize((W, H)), ((k % 4) * (W + 10) + 10, (k // 4) * (H + 10) + 10))
sheet.save(d / "preview_all.jpg", quality=90); print(d / "preview_all.jpg")
