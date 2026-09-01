#!/usr/bin/env python3
"""skin_image_tools — cutout and finishing tools for UI-skin artwork.

Boundary-principle pipeline for art generated on uniform backgrounds:

  floodcut    boundary flood fill: remove only the edge-connected background;
              interior keeps 100% original pixels (never use semantic matting
              on uniform-background art — it makes sheer garments translucent)
  decontam    remove the residual background-colored fringe in the silhouette
              boundary band (visible as a glowing outline on dark UIs)
  feather     soften hard cut edges through soft glows (blur + max-blend)
  glow-restore rebuild a radial falloff for a glow disc cut mid-gradient,
              from the original image's distance-to-background field
  verify      composite over red / dark-navy / checker to expose residue

Requires: Pillow. Examples:
  python skin_image_tools.py floodcut raw.png cut.png
  python skin_image_tools.py decontam cut.png --bg auto
  python skin_image_tools.py verify cut.png --bg navy -o check_navy.png
"""
import argparse
import math
from collections import deque

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# ---------------------------------------------------------------- utilities


def dist(c1, c2):
    return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)


def neutral(c):
    """Background-safe test: background is neutral gray; blue-tinted or
    strongly saturated pixels belong to the subject (blue-phase blocking)."""
    mx = max(c)
    if mx == 0:
        return False
    return (c[2] - c[0]) < 12 and (mx - min(c)) / mx < 0.07


def corner_bg(im):
    w, h = im.size
    px = im.load()
    cs = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    return tuple(sum(c[i] for c in cs) // 4 for i in range(3))


def resolve_bg(im, bg):
    return corner_bg(im) if bg in (None, 'auto') else bg


# ---------------------------------------------------------------- floodcut


def floodcut(src, dst, local=4, glob=110, pocket_dist=38, pocket_min=20):
    """Remove the edge-connected neutral background; enclosed uniform
    background pockets (halo interiors, ornament gaps) are removed too.
    Interior pixels keep 100% original RGBA."""
    im = Image.open(src).convert('RGB')
    w, h = im.size
    px = im.load()
    bg = resolve_bg(im, None)
    remove = bytearray(w * h)
    q = deque()

    def seed(x, y):
        i = y * w + x
        c = px[x, y]
        if not remove[i] and dist(c, bg) < 120 and neutral(c):
            remove[i] = 1
            q.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)
    while q:
        x, y = q.popleft()
        c = px[x, y]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                i = ny * w + nx
                if not remove[i]:
                    nc = px[nx, ny]
                    if dist(nc, c) < local and dist(nc, bg) < glob and neutral(nc):
                        remove[i] = 1
                        q.append((nx, ny))

    # enclosed uniform background pockets (halo ring interiors, ornament gaps)
    seen = bytearray(w * h)
    for sy in range(h):
        for sx in range(w):
            i = sy * w + sx
            if remove[i] or seen[i]:
                continue
            comp = []
            dq = deque([(sx, sy)])
            seen[i] = 1
            sr = sg = sb = 0
            while dq:
                x, y = dq.popleft()
                comp.append(i)
                r, g, b = px[x, y]
                sr += r
                sg += g
                sb += b
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not remove[j] and not seen[j]:
                            seen[j] = 1
                            dq.append((nx, ny))
            n = len(comp)
            if n >= pocket_min and dist((sr / n, sg / n, sb / n), bg) < pocket_dist:
                for i2 in comp:
                    remove[i2] = 1

    out = im.convert('RGBA')
    po = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            po[x, y] = (r, g, b, 0) if remove[y * w + x] else (r, g, b, 255)
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    out.save(dst)
    print(f'floodcut -> {dst} {out.size}')


# ---------------------------------------------------------------- decontam


def decontam(src, dst, bg='auto', kill=42, soft=78):
    """Remove the background-colored fringe in the silhouette boundary band
    (glowing outline on dark UIs)."""
    im = Image.open(src).convert('RGBA')
    w, h = im.size
    px = im.load()
    bgcolor = resolve_bg(im, bg)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if ((x > 0 and px[x - 1, y][3] == 0) or (x < w - 1 and px[x + 1, y][3] == 0)
                    or (y > 0 and px[x, y - 1][3] == 0) or (y < h - 1 and px[x, y + 1][3] == 0)):
                d = dist((r, g, b), bgcolor)
                if d < kill:
                    px[x, y] = (r, g, b, 0)
                elif d < soft:
                    px[x, y] = (r, g, b, int(a * (d - kill) / (soft - kill)))
    im.save(dst)
    print(f'decontam -> {dst}')


# ---------------------------------------------------------------- feather


def feather(src, dst, radius=5, rounds=2, kill=42, soft=78, bg='auto'):
    """Soften hard cut edges through soft glows: alpha blur + max-blend,
    followed by a decontam pass each round."""
    im = Image.open(src).convert('RGBA')
    bgcolor = resolve_bg(im.convert('RGB'), bg) if bg == 'auto' else bg
    for _ in range(rounds):
        r, g, b, a = im.split()
        blurred = a.filter(ImageFilter.GaussianBlur(radius))
        soft = blurred.point(lambda v: int(v * 0.88))
        im.putalpha(ImageChops.lighter(a, soft))
        im = decontam_band(im, bgcolor, kill, soft)
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    im.save(dst)
    print(f'feather -> {dst} {im.size}')


def decontam_band(im, bg, kill, soft):
    w, h = im.size
    px = im.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if ((x > 0 and px[x - 1, y][3] == 0) or (x < w - 1 and px[x + 1, y][3] == 0)
                    or (y > 0 and px[x, y - 1][3] == 0) or (y < h - 1 and px[x, y + 1][3] == 0)):
                d = dist((r, g, b), bg)
                if d < kill:
                    px[x, y] = (r, g, b, 0)
                elif d < soft:
                    px[x, y] = (r, g, b, int(a * (d - kill) / (soft - kill)))
    return im


# ---------------------------------------------------------------- glow-restore


def glow_restore(orig, cut, dst, bg='auto', floor=16, strength=3.0, cap=235, max_frac=0.62):
    """Rebuild a radial falloff for a glow disc cut mid-gradient.

    For cut pixels (alpha below 250) inside the glow region (top `max_frac`
    of the cutout), alpha is re-derived from the ORIGINAL image's
    distance-to-background field and unioned (max) with the current alpha.
    The figure mask keeps the body solid."""
    original = Image.open(orig).convert('RGB')
    ow, oh = original.size
    op = original.load()
    im = Image.open(cut).convert('RGBA')
    cw, ch = im.size
    px = im.load()
    bgcolor = resolve_bg(original, bg)
    # align: assume the cut is horizontally centered on the original and
    # top-anchored (adjust with --ox/--oy when the host crops differently)
    ox = max(0, (ow - cw) // 2)
    oy = 0
    restored = 0
    for y in range(min(ch, oh - oy)):
        for x in range(cw):
            a = px[x, y][3]
            if a >= 250 or y + oy >= oh or x + ox >= ow:
                continue
            d = dist(op[x + ox, y + oy], bgcolor)
            if d <= floor:
                continue
            glow_a = min(cap, int((d - floor) * strength))
            if glow_a > a:
                r, g, b = op[x + ox, y + oy]
                px[x, y] = (r, g, b, glow_a)
                restored += 1
    im.save(dst)
    print(f'glow-restore -> {dst} ({restored} px restored)')


# ---------------------------------------------------------------- verify


def _make_bg(kind, w, h):
    if kind == 'red':
        return Image.new('RGB', (w, h), (200, 30, 30))
    if kind == 'navy':
        return Image.new('RGB', (w, h), (16, 24, 52))
    if kind == 'checker':
        cell = 24
        s = Image.new('RGB', (w, h), (70, 74, 86))
        d = ImageDraw.Draw(s)
        for y in range(0, h, cell):
            for x in range(0, w, cell):
                if (x // cell + y // cell) % 2:
                    d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(112, 116, 128))
        return s
    raise SystemExit(f'unknown background: {kind}')


def verify(src, bg, out):
    im = Image.open(src).convert('RGBA')
    canvas = _make_bg(bg, *im.size)
    canvas.paste(im, (0, 0), im)
    canvas.save(out)
    print(f'verify -> {out} ({bg})')


# ---------------------------------------------------------------- cli


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('floodcut', help='boundary flood fill (uniform background art)')
    p.add_argument('src')
    p.add_argument('dst')
    p.add_argument('--local', type=int, default=4)
    p.add_argument('--glob', type=int, default=110)

    p = sub.add_parser('decontam', help='remove background-colored boundary fringe')
    p.add_argument('src')
    p.add_argument('dst')
    p.add_argument('--bg', default='auto')
    p.add_argument('--kill', type=int, default=42)
    p.add_argument('--soft', type=int, default=78)

    p = sub.add_parser('feather', help='soften hard cut edges through soft glows')
    p.add_argument('src')
    p.add_argument('dst')
    p.add_argument('--radius', type=int, default=5)
    p.add_argument('--rounds', type=int, default=2)

    p = sub.add_parser('glow-restore', help='rebuild radial falloff for a cut glow disc')
    p.add_argument('orig', help='original uncropped image')
    p.add_argument('cut', help='current cutout (a crop of orig)')
    p.add_argument('dst')
    p.add_argument('--bg', default='auto')
    p.add_argument('--floor', type=int, default=16)
    p.add_argument('--strength', type=float, default=3.0)

    p = sub.add_parser('verify', help='composite over red/navy/checker')
    p.add_argument('src')
    p.add_argument('--bg', default='navy', choices=['red', 'navy', 'checker'])
    p.add_argument('-o', '--out', default=None)

    args = ap.parse_args()
    if args.cmd == 'floodcut':
        floodcut(args.src, args.dst, args.local, args.glob)
    elif args.cmd == 'decontam':
        decontam(args.src, args.dst, args.bg, args.kill, args.soft)
    elif args.cmd == 'feather':
        feather(args.src, args.dst, args.radius, args.rounds)
    elif args.cmd == 'glow-restore':
        glow_restore(args.orig, args.cut, args.dst, args.bg, args.floor, args.strength)
    elif args.cmd == 'verify':
        verify(args.src, args.bg, args.out or f'check_{args.bg}.png')


if __name__ == '__main__':
    main()
