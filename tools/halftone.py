#!/usr/bin/env python3
"""
Turn an image (e.g. a Piranesi etching) into a halftone dot pattern for the
band at the top of the website.

The output is a PNG whose dots are opaque and whose background is
transparent. The website uses it as a mask, so the dot colour comes from the
CSS (--dots) and adapts to light and dark mode automatically.

Usage (from the website folder):
    python3 tools/halftone.py piranesi.jpg assets/img/piranesi-halftone.png

Options worth trying:
    --cell 7        dot spacing in pixels (smaller = finer, larger = bolder)
    --angle 45      screen angle (45 is the classic print look, 0 = straight grid)
    --band 0.4      crop to a wide strip; the number is the vertical position
                    (0 = top of the print, 0.5 = middle, 1 = bottom)
    --band-ratio 5  width:height ratio of that strip (lower = taller strip,
                    showing more of the print)
    --fade 0.4      fade the dots to transparent over this fraction of the
                    band's height at the top and bottom edges, so the band
                    dissolves into the page instead of ending in a hard line
    --contrast 1.3  boost contrast before rastering

Needs Pillow and NumPy:  python3 -m pip install pillow numpy
"""
import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageEnhance

SS = 4  # supersampling factor for smooth dot edges


def halftone(img, cell, angle, contrast):
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g, cutoff=1)
    if contrast != 1:
        g = ImageEnhance.Contrast(g).enhance(contrast)
    w, h = g.size

    rot = g.rotate(angle, expand=True, fillcolor=255, resample=Image.BICUBIC)
    a = np.asarray(rot, dtype=np.float32) / 255.0
    rh, rw = a.shape

    canvas = Image.new("L", (rw * SS, rh * SS), 0)
    draw = ImageDraw.Draw(canvas)
    rmax = cell * SS / math.sqrt(2)  # radius at which neighbouring dots touch

    for y in range(0, rh, cell):
        for x in range(0, rw, cell):
            darkness = 1.0 - float(a[y:y + cell, x:x + cell].mean())
            if darkness < 0.04:
                continue
            r = rmax * math.sqrt(darkness)
            cx = (x + cell / 2) * SS
            cy = (y + cell / 2) * SS
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)

    canvas = canvas.rotate(-angle, expand=False, resample=Image.BICUBIC)
    cw, ch = canvas.size
    left, top = (cw - w * SS) // 2, (ch - h * SS) // 2
    canvas = canvas.crop((left, top, left + w * SS, top + h * SS))
    alpha = canvas.resize((w, h), Image.LANCZOS)

    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.putalpha(alpha)
    return out


def apply_fade(img, fade):
    """Fade alpha to 0 over the top/bottom `fade` fraction of the image height."""
    if not fade:
        return img
    w, h = img.size
    edge = max(1, round(h * fade))
    ramp = np.ones(h, dtype=np.float32)
    ramp[:edge] = np.linspace(0, 1, edge, dtype=np.float32)
    ramp[h - edge:] = np.linspace(1, 0, edge, dtype=np.float32)

    a = np.asarray(img.getchannel("A"), dtype=np.float32)
    a *= ramp[:, None]
    out = img.copy()
    out.putalpha(Image.fromarray(a.astype(np.uint8), mode="L"))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--width", type=int, default=2400, help="output width in px (default 2400)")
    p.add_argument("--cell", type=int, default=7)
    p.add_argument("--angle", type=float, default=45)
    p.add_argument("--contrast", type=float, default=1.2)
    p.add_argument("--band", type=float, default=None,
                   help="crop to a wide strip at this vertical position (0–1)")
    p.add_argument("--band-ratio", type=float, default=5,
                   help="width:height ratio of the --band strip (default 5)")
    p.add_argument("--fade", type=float, default=0,
                   help="fade to transparent over this fraction of the band's "
                        "height at the top and bottom edges (default 0, off)")
    p.add_argument("--color", action="store_true",
                   help="skip the dot screen and save the crop in full colour "
                        "(the band's own fade is done in CSS for colour mode)")
    args = p.parse_args()

    img = Image.open(args.source).convert("RGB")
    scale = args.width / img.width
    img = img.resize((args.width, round(img.height * scale)), Image.LANCZOS)

    if args.band is not None:
        bh = round(args.width / args.band_ratio)
        if bh < img.height:
            top = round((img.height - bh) * min(max(args.band, 0), 1))
            img = img.crop((0, top, args.width, top + bh))

    os.makedirs(os.path.dirname(args.target) or ".", exist_ok=True)
    if args.color:
        result = img
    else:
        result = halftone(img, args.cell, args.angle, args.contrast)
        result = apply_fade(result, args.fade)
    result.save(args.target, optimize=True)
    print(f"Saved {args.target}")


if __name__ == "__main__":
    main()
