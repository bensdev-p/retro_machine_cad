"""Redraw the RetroOS "Phosphor BIOS" POST screen as a PNG for the case viewer.

Layout, text, colours and logo geometry are transcribed from the RetroOS repo
(crates/retro-post/src/main.rs post_grid/draw_logo, probe::fake() sample data,
docs/STYLE.md Phosphor16). The font is RetroOS's own Phosphor Mono 8x16
(SIL OFL 1.1), vendored in tools/vendor/phosphor-mono. This is a re-drawing for
illustration, not output from the real program; check it against a screenshot.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GLYPHS = ROOT / 'tools/vendor/phosphor-mono/phosphor-mono-8x16.glyphs'
OUT = ROOT / 'outputs/p2/screens'
P16 = {'BLACK': '#0A0A0F', 'COBALT': '#1F3BB3', 'SILVER': '#BDBDB8', 'SKY': '#5C7CFA', 'LIME': '#6FE06A',
       'AQUA': '#5FE3E3', 'LEMON': '#F7E15A', 'WHITE': '#F5F5F0', 'SLATE': '#5C5C66'}
COLS, ROWS = 80, 25

def load_font(path):
    font, cp, first, rows = {}, None, 0, []
    def flush():
        if cp is not None:
            g = [[False] * 8 for _ in range(16)]
            for i, r in enumerate(rows):
                for j, c in enumerate(r[:8]):
                    g[first + i][j] = c == '#'
            font[cp] = g
    for line in path.read_text().splitlines():
        if line.startswith('@ '):
            flush()
            parts = line.split()
            cp = int(parts[1], 16); first = 0; rows = []
            for p_ in parts[3:]:
                if p_.startswith('+'): first = int(p_[1:])
        elif line and line[0] in '.#' and cp is not None:
            rows.append(line.strip())
    flush()
    return font

def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

def render(w=1920, h=1200):
    font = load_font(GLYPHS)
    scale = min(w // (COLS * 8), h // (ROWS * 16))
    cw, ch = 8 * scale, 16 * scale
    ox, oy = (w - COLS * cw) // 2, (h - ROWS * ch) // 2
    im = Image.new('RGB', (w, h), hexrgb(P16['BLACK'])); px = im.load()
    def rect(x, y, ww, hh, col):
        c = hexrgb(col)
        for yy in range(max(0, y), min(h, y + hh)):
            for xx in range(max(0, x), min(w, x + ww)):
                px[xx, yy] = c
    def text_px(x, y, s, col, sc=scale):
        for k, chr_ in enumerate(s):
            g = font.get(ord(chr_))
            if not g: continue
            for r in range(16):
                for c in range(8):
                    if g[r][c]: rect(x + (k * 8 + c) * sc, y + r * sc, sc, sc, col)
    def put(cx, cy, s, col='SILVER'):
        text_px(ox + cx * cw, oy + cy * ch, s, P16[col]); return cx + len(s)
    # post_grid (probe::fake data, animation finished)
    put(1, 1, 'Phosphor BIOS v1.0', 'WHITE')
    put(1, 2, 'Copyright (C) 1987-1993 Phosphor Computer Company')
    put(1, 4, 'RetroOS 1.0', 'LEMON')
    put(1, 6, 'Raspberry Pi 5 Model B Rev 1.0')
    put(1, 7, 'ARM Cortex-A76 4-core @ 2400 MHz')
    x = put(1, 9, 'Memory Test :  %12sK' % format(8245632, ','))
    put(x + 1, 9, 'OK', 'LIME')
    for i, (k, v) in enumerate([('Video', 'VideoCore VII, HDMI-A-1 1920x1080'), ('Storage', 'SD card 64 GB'),
                                ('Input', '1 keyboard, 1 mouse'), ('Network', 'Ethernet, Wi-Fi, Bluetooth')]):
        put(1, 11 + i, '%-12s:  %s' % (k, v))
    put(1, ROWS - 2, 'Press '); put(7, ROWS - 2, 'F8', 'WHITE'); put(9, ROWS - 2, ' for Startup Menu, ')
    put(28, ROWS - 2, 'DEL', 'WHITE'); put(31, ROWS - 2, ' for Setup')
    # draw_logo: concentric pixel diamonds + PHOSPHOR label
    size, p = 12, scale * 2
    cx, cy = ox + (COLS - 9) * cw, oy + 2 * ch
    for r, col in ((size, 'COBALT'), (size - 3, 'SKY'), (size - 6, 'AQUA'), (size - 9, 'WHITE')):
        for dy in range(-r, r + 1):
            wd = r - abs(dy)
            rect(cx - wd * p, cy + dy * p, (2 * wd + 1) * p, p, P16[col])
    label = 'PHOSPHOR'
    text_px(cx - (len(label) * cw) // 2 + p // 2, cy + (size + 2) * p, label, P16['LEMON'])
    return im

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    render().save(OUT / 'post.png', optimize=True)
    print('wrote', OUT / 'post.png')
