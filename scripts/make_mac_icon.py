#!/usr/bin/env python3
"""Generate a Garden State / Jersey Devil inspired icon, no third-party artwork."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

size = 1024
im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((28, 28, 996, 996), radius=220, fill="#15191D", outline="#F2B134", width=32)
d.ellipse((158, 150, 866, 858), fill="#006747", outline="#F2B134", width=22)
# Antenna mast and radio waves
d.line([(512, 365), (512, 735)], fill="#F5F5F0", width=40)
d.ellipse((479, 337, 545, 403), fill="#F2B134")
for box in [(348, 295, 676, 622), (251, 203, 773, 713)]:
    d.arc(box, start=205, end=335, fill="#F2B134", width=22)
# Devilish red horns atop a stylized NJ radio badge
d.polygon([(411, 358), (325, 244), (369, 429)], fill="#D62828")
d.polygon([(613, 358), (699, 244), (655, 429)], fill="#D62828")
d.rounded_rectangle((365, 602, 659, 761), radius=36, fill="#15191D", outline="#F2B134", width=12)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 84)
except OSError:
    font = ImageFont.load_default()
d.text((512, 681), "NJ", fill="#F2B134", font=font, anchor="mm")
out = Path("electron/build")
out.mkdir(parents=True, exist_ok=True)
iconset = out / "icon.iconset"
iconset.mkdir(exist_ok=True)
for px in (16, 32, 128, 256, 512):
    im.resize((px, px), Image.Resampling.LANCZOS).save(iconset / f"icon_{px}x{px}.png")
    im.resize((px * 2, px * 2), Image.Resampling.LANCZOS).save(iconset / f"icon_{px}x{px}@2x.png")
subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(out / "icon.icns")], check=True)
