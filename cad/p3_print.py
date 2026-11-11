"""P3 printable v1: split the P2 concept into printable parts.

Runs cad/p2_concept.py for the shared geometry, then:
  * splits full-width parts at p3.seam_x (shell, lid) or at natural boundaries
    (front bezel at the screen/drive divide, rear panel at the drawer/I-O divide),
  * adds joints: heat-set insert bosses, screw clearances, dowels,
  * turns branding into flush multi-colour inlays (printed on the bed face or top face),
  * makes printed hinges, latches, handle, feet and fit coupons,
  * orients every part for printing, assigns the smallest printer that fits,
  * exports STL per part, 3MF for multi-colour parts, a STEP assembly, manifest and checks.

All tunables live in parameters.json -> p3 (and p2 for the shared shape).
Anything not measured is flagged there and in docs/print-P3.md.
"""
from pathlib import Path
import json, math, runpy, csv, sys
import numpy as np
import build123d as b, time
_T0 = time.time()
def stage(m): print('[%6.1fs] %s' % (time.time() - _T0, m), flush=True)

ROOT = Path(__file__).resolve().parents[1]
g = runpy.run_path(str(ROOT / 'cad/p2_concept.py'), run_name='p2')
P = json.loads((ROOT / 'parameters.json').read_text()); Q3 = P['p3']; Q2 = P['p2']
OUT = ROOT / 'outputs/p3'; (OUT / 'stl').mkdir(parents=True, exist_ok=True); (OUT / '3mf').mkdir(exist_ok=True)

box, cyl, frustum, grow = g['box'], g['cyl'], g['frustum'], g['grow']
W, D, H, TOP, fh, sw, iw = (g[k] for k in ('W', 'D', 'H', 'TOP', 'fh', 'sw', 'iw'))
HOOD, fy, glass_y, vis = g['HOOD'], g['fy'], g['glass_y'], g['vis']
SCR_FRONT, DRV_FRONT = g['SCR_FRONT'], g['DRV_FRONT']
lip_y, deck_z, tilted = g['lip_y'], g['deck_z'], g['tilted']
P2 = g['parts']
INS, INS_S, SCR = Q3['insert'], Q3['insert_short'], Q3['screw']
SEAM = Q3['seam_x']; CL = Q3['fit_clearance']
FT = Q2['fascia']['thickness']

def part(name):
    return P2[name]['shape']

def solids_of(shape):
    if isinstance(shape, (list, b.ShapeList)):
        return [so for x in shape for so in solids_of(x)]
    return list(shape.solids()) if hasattr(shape, 'solids') else [shape]

def one(shape, name):
    """Fuse to a single valid solid (raises if the part would print as several islands)."""
    ss = solids_of(norm(shape))
    s = ss[0].fuse(*ss[1:]) if len(ss) > 1 else ss[0]
    s = norm(s)
    s = s.clean() if hasattr(s, 'clean') else s
    n = len(s.solids())
    assert s.is_valid, name
    return s, n

# ------------------------------------------------------------------ fastener helpers
def ins_hole(x, y, z, axis, sign, short=False):
    """Heat-set insert hole: starts at (x,y,z) on a face and goes `sign` along `axis` into material."""
    spec = INS_S if short else INS
    d, L = spec['hole_d'], spec['depth'] + 0.5
    c = b.Cylinder(d / 2, L, align=(b.Align.CENTER, b.Align.CENTER, b.Align.MIN))
    rot = {('z', 1): b.Rot(), ('z', -1): b.Rot(X=180), ('y', 1): b.Rot(X=-90), ('y', -1): b.Rot(X=90),
           ('x', 1): b.Rot(Y=90), ('x', -1): b.Rot(Y=-90)}[(axis, sign)]
    return b.Pos(x, y, z) * rot * b.Pos(0, 0, -0.2) * c

def clear_hole(x, y, z, axis, sign, L, d=None):
    d = d or SCR['clear_d']
    c = b.Cylinder(d / 2, L, align=(b.Align.CENTER, b.Align.CENTER, b.Align.MIN))
    rot = {('z', 1): b.Rot(), ('z', -1): b.Rot(X=180), ('y', 1): b.Rot(X=-90), ('y', -1): b.Rot(X=90),
           ('x', 1): b.Rot(Y=90), ('x', -1): b.Rot(Y=-90)}[(axis, sign)]
    return b.Pos(x, y, z) * rot * b.Pos(0, 0, -0.2) * c

def cbore(x, y, z, axis, sign, depth):
    return clear_hole(x, y, z, axis, sign, depth, SCR['head_d'] + 0.4)

def csink(x, y, z, axis, sign):
    """90-degree countersink cone opening at the face (for flat-head M3)."""
    r1 = SCR['csk_d'] / 2; h = r1 - SCR['clear_d'] / 2
    c = b.Cone(r1, SCR['clear_d'] / 2, h, align=(b.Align.CENTER, b.Align.CENTER, b.Align.MIN))
    rot = {('y', 1): b.Rot(X=-90), ('y', -1): b.Rot(X=90), ('z', 1): b.Rot(), ('z', -1): b.Rot(X=180)}[(axis, sign)]
    return b.Pos(x, y, z) * rot * b.Pos(0, 0, -0.01) * c

def dowel_hole(x, y, z, axis='x'):
    return cyl(x - Q3['dowel_len_each'] - 0.5, y, z, Q3['dowel_hole_d'] / 2, 2 * Q3['dowel_len_each'] + 1, 'x')

def norm(sh):
    return b.Compound(children=list(sh)) if isinstance(sh, (list, b.ShapeList)) else sh

def cut(sh, tools):
    sh = norm(sh)
    return norm(sh.cut(*tools)) if tools else sh

def keep(sh, region):
    return norm(norm(sh).intersect(region))

LEFT = box(-50, -50, -50, SEAM, D + 50, TOP + 100)
RIGHT = box(SEAM, -50, -50, W + 50, D + 50, TOP + 100)

# ------------------------------------------------------------------ assembly registry
PRINT = {}      # name -> dict(shape (assembly frame), state, role, down (unit normal to put on bed), qty, colour_group, note)
def add(name, shape, role, down, state=None, qty=1, group=None, note='', material='shell'):
    PRINT[name] = dict(shape=shape, role=role, down=down, state=state, qty=qty, group=group, note=note, material=material)

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ inlays (flush multi-colour)
def shifted(s, dx=0, dy=0, dz=0):
    return b.Pos(dx, dy, dz) * s

side_inlay = {'right': [], 'left': []}
for s in solids_of(part('brand_side')):
    bb = s.bounding_box()
    if bb.center().X > W / 2: side_inlay['right'].append(shifted(s, dx=-Q3['inlay']['side']))
    else: side_inlay['left'].append(shifted(s, dx=Q3['inlay']['side']))

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ SHELL halves
shell = part('shell')
# Power switch (IBM-style side switch) cutout: placeholder rectangle on the right side.
PS = Q3['power_switch']
ps_y, ps_z = D - PS['y_from_rear'], fh + PS['z_above_floor']
ps_cut = box(W - sw - 1, ps_y - PS['cutout_w'] / 2, ps_z - PS['cutout_h'] / 2, W + 1, ps_y + PS['cutout_w'] / 2, ps_z + PS['cutout_h'] / 2)
shell = shell - ps_cut

# Seam joint blocks: left block carries the counterbored screw, right block the insert.
seam_blocks_top = [236]
seam_blocks_bot = [g['glass_y'] + g['DSP']['depth'] + 9, g['dy0'] - 9]   # between the display-bracket bosses and the drawer
bl, br, tools_l, tools_r = [], [], [], []
for y in seam_blocks_top:
    zt = TOP - iw
    bl.append(box(SEAM - 12, y - 7, zt - 12, SEAM, y + 7, zt + 0.5)); br.append(box(SEAM, y - 7, zt - 12, SEAM + 12, y + 7, zt + 0.5))
    tools_l += [clear_hole(SEAM - 12.1, y, zt - 6, 'x', 1, 13), cbore(SEAM - 12.1, y, zt - 6, 'x', 1, 5)]
    tools_r += [ins_hole(SEAM, y, zt - 6, 'x', 1)]
for y in seam_blocks_bot:
    zb = fh + iw
    bl.append(box(SEAM - 12, y - 7, zb - 0.5, SEAM, y + 7, zb + 12)); br.append(box(SEAM, y - 7, zb - 0.5, SEAM + 12, y + 7, zb + 12))
    tools_l += [clear_hole(SEAM - 12.1, y, zb + 6, 'x', 1, 13), cbore(SEAM - 12.1, y, zb + 6, 'x', 1, 5)]
    tools_r += [ins_hole(SEAM, y, zb + 6, 'x', 1)]
# Dowels through the solid front ring (top and bottom) to register the halves.
dowels = [dowel_hole(SEAM, 30, (g['HOOD'][3] + TOP) / 2), dowel_hole(SEAM, (lip_y(fh) + fy) / 2 + 2, (fh + g['HOOD'][1]) / 2)]

# Front bezel retention: inserts in the rear face of the top and bottom hood rings (screws come from behind).
bez_top_z = (g['HOOD'][3] + TOP - iw) / 2 - 0.2
bez_bot_z = (fh + iw + g['HOOD'][1]) / 2
fascia_seam = (SCR_FRONT[2] + DRV_FRONT[0]) / 2
bez_x_scr = [40, 130, 230]
bez_x_drv = [fascia_seam + 30, W - 30]
bezel_inserts = [ins_hole(x, fy, z, 'y', -1) for x in bez_x_scr + bez_x_drv for z in (bez_top_z, bez_bot_z)]

# Rear panel ledge (stop) with inserts, inset 3 mm from the rear edge.
rp_y0, rp_y1 = g['rp_y0'], g['rp_y1']
led_y0, led_y1 = rp_y0 - 8, rp_y0
ledge = [box(sw, led_y0, TOP - iw - 6, W - sw, led_y1, TOP - iw + 0.5),                    # top
         box(sw - 0.5, led_y0, g['dz1'] + 3, sw + 6, led_y1, TOP - iw),                         # left side (above the drawer)
         box(W - sw - 6, led_y0, fh + iw, W - sw + 0.5, led_y1, TOP - iw),                     # right side
         box(Q2['drawer']['x1'] + 8, led_y0, fh + iw - 0.5, W - sw, led_y1, fh + iw + 6)]      # bottom (I/O side only)
rear_split = Q2['drawer']['x1'] + 8
rp_top_z = TOP - iw - 3
rear_ins_pts = [(x, rp_top_z) for x in (30, 130, 230, rear_split + 30, W - 30)] + \
               [(sw + 3, z) for z in (fh + 150,)] + [(W - sw - 3, z) for z in (fh + 40, fh + 150)] + \
               [(x, fh + iw + 3) for x in (rear_split + 30, W - 30)]
rear_inserts = [ins_hole(x, led_y1, z, 'y', -1) for x, z in rear_ins_pts]

# Drive cage floor screws (from below, into inserts in the cage posts).
cx0, cx1, cg_y0, cg_y1, z0 = g['cx0'], g['cx1'], g['cg_y0'], g['cg_y1'], g['z0']
post_xy = [(xa + 5, ya + 5) for xa in (cx0, cx1 - 10) for ya in (cg_y0, cg_y1 - 10)]
floor_holes = [clear_hole(x, y, fh - 0.1, 'z', 1, iw + 0.3) for x, y in post_xy]

# Hinge blocks: inserts going up into the solid bottom front ring.
HG, hinge_y, hinge_z, hk_r = g['HG'], g['hinge_y'], g['hinge_z'], g['hk_r']
LEAF = Q3['hinge']['leaf_t']
case_hinge_ins = [(hx + dx, hinge_y + 14) for hx in HG['x'] for dx in (-9, 9)]
hinge_inserts = [ins_hole(x, y, hinge_z, 'z', 1) for x, y in case_hinge_ins]

# Latch bases: short inserts in the side wall (from outside), under the lever ends.
latch_y0, hood_cz = g['latch_y0'], g['hood_cz']
latch_pts = [(latch_y0 + 6, hood_cz + 17), (latch_y0 + 24, hood_cz - 17)]
latch_inserts = [ins_hole(0, y, z, 'x', 1, short=True) for y, z in latch_pts] + \
                [ins_hole(W, y, z, 'x', -1, short=True) for y, z in latch_pts]

# Handle pivot bosses under the tub floor.
px0, px1, pivot_y, pz = g['px0'], g['px1'], g['pivot_y'], g['pz']
tub_floor = TOP - Q2['handle']['pocket_depth']
piv_pts = [(px0 + 4.5, pivot_y + dy) for dy in (-4.5, 4.5)] + [(px1 - 4.5, pivot_y + dy) for dy in (-4.5, 4.5)]
piv_bosses = [cyl(x, y, tub_floor - 2 - 8, 4.5, 8.2) for x, y in piv_pts]
piv_inserts = [ins_hole(x, y, tub_floor, 'z', -1) for x, y in piv_pts]

# Feet recesses.
FEET = Q3['feet']
feet_xy = [(28, math.ceil(lip_y(fh)) + 30), (W - 28, math.ceil(lip_y(fh)) + 30), (28, D - 28), (W - 28, D - 28)]
feet_rec = [cyl(x, y, fh - 0.1, FEET['d'] / 2 + CL, FEET['recess'] + 0.1) for x, y in feet_xy]

# Integrated drawer rails (were separate in P2).
rails = solids_of(part('drawer_rails'))
rails = [r.intersect(box(-1, -1, -1, W + 1, led_y0 - 0.5, TOP)) for r in rails]

stage('shell_full = shell.fuse(')
shell_full = shell.fuse(*ledge, *piv_bosses, *rails)
shell_full = cut(shell_full, dowels + bezel_inserts + rear_inserts + floor_holes + hinge_inserts + latch_inserts + piv_inserts + feet_rec)
shell_full = shell_full.cut(*(side_inlay['left'] + side_inlay['right']))
stage('shell_L = keep(')
shell_L = keep(shell_full, LEFT).fuse(*bl); shell_L = cut(shell_L, tools_l + dowels)
shell_R = keep(shell_full, RIGHT).fuse(*br); shell_R = cut(shell_R, tools_r + dowels)
add('shell_left', shell_L, 'shell', (-1, 0, 0), note='Print on its outer side face (wordmark inlay on the bed). Supports: handle tub and hood ceiling.')
add('shell_right', shell_R, 'shell', (1, 0, 0), note='Print on its outer side face. Power-switch cutout is a placeholder.')
add('inlay_side_left', b.Compound(children=side_inlay['left']), 'brand', (-1, 0, 0), group='shell_left', note='Flush wordmark inlay, printed together with shell_left (multi-colour).', material='brand')
add('inlay_side_right', b.Compound(children=side_inlay['right']), 'brand', (1, 0, 0), group='shell_right', note='Flush wordmark inlay, printed together with shell_right (multi-colour).', material='brand')

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ FRONT BEZELS (shield + fascia + shroud + mounting flange)
flange = box(HOOD[0] + CL, fy + FT, fh + iw + CL, HOOD[2] - CL, fy + FT + 4, TOP - iw - CL)
flange -= box(SCR_FRONT[0] + 8, fy + FT - 1, SCR_FRONT[1] + 8, SCR_FRONT[2] - 8, fy + FT + 5, SCR_FRONT[3] - 8)   # screen window
flange -= box(DRV_FRONT[0] + 8, fy + FT - 1, DRV_FRONT[1] + 8, DRV_FRONT[2] - 8, fy + FT + 5, DRV_FRONT[3] - 8)   # drive window
dark = part('shield_frame').fuse(part('screen_shroud'), part('drive_shroud'), part('nameplate'), flange)
face = norm(norm(part('fascia').fuse(part('legend_plate'))).cut(dark))
ftools = [clear_hole(x, fy + FT + 4.1, z, 'y', -1, FT + 4.4) for x in bez_x_scr + bez_x_drv for z in (bez_top_z, bez_bot_z)]
# Display bracket bosses on the flange back (inserts, screws from the bracket).
disp_back = glass_y + g['DSP']['depth']
br_pts = [(70, g['glass_z0'] - 6), (190, g['glass_z0'] - 6), (70, g['glass_z0'] + g['DSP']['height'] + 6), (190, g['glass_z0'] + g['DSP']['height'] + 6)]
br_bosses = [cyl(x, fy + FT + 4 - 0.1, z, INS['boss_d'] / 2, disp_back - (fy + FT + 4) + 0.1, 'y') for x, z in br_pts]
dark = dark.fuse(*br_bosses)
ftools += [ins_hole(x, disp_back, z, 'y', -1) for x, z in br_pts]
# Nameplate text and diamond: flush inlay in the dark plate (top face when printed face-up).
np_inlay = [shifted(s, dy=Q3['inlay']['nameplate']) for s in solids_of(part('nameplate_text'))]
np_inlay += [shifted(s, dy=Q3['inlay']['nameplate']) for n in P2 if n.startswith('accent_') and not n.endswith('_lid') for s in solids_of(part(n))]
dark = cut(cut(dark, ftools), np_inlay)
face = cut(face, ftools)
front = dark
BZL = box(-50, -50, -50, fascia_seam, fy + 60, TOP + 50); BZR = box(fascia_seam, -50, -50, W + 50, fy + 60, TOP + 50)
add('bezel_screen', keep(dark, BZL), 'bezel', (0, 1, 0), note='Print face-up (flange on the bed) as ONE multi-part object: dark shield/shroud + warm-grey face. Glass rests behind the shroud with a gap; no clamping.')
add('bezel_drives', keep(dark, BZR), 'bezel', (0, 1, 0), note='Print face-up as one multi-part object (dark + warm-grey face + nameplate inlay).')
add('bezel_screen_face', keep(face, BZL), 'fascia', (0, 1, 0), group='bezel_screen', note='Warm-grey grooved face, printed fused with bezel_screen.', material='shell')
add('bezel_drives_face', keep(face, BZR), 'fascia', (0, 1, 0), group='bezel_drives', note='Warm-grey grooved face + legend, printed fused with bezel_drives.', material='shell')
add('inlay_nameplate', b.Compound(children=np_inlay), 'plate_text', (0, 1, 0), group='bezel_drives', material='brand')

# ------------------------------------------------------------------ REAR panels (drawer panel + replaceable I/O plate)
rear = part('rear_panel')
rtools = []
for x, z in rear_ins_pts:
    rtools += [clear_hole(x, rp_y1 + 0.1, z, 'y', -1, 4.4), csink(x, rp_y1, z, 'y', -1)]
rear = cut(rear, rtools)
# P3: master switch moves to the side, so blank the P2 rocker cutout on the I/O plate.
add('rear_panel_left', keep(rear, box(-50, D - 20, -50, rear_split, D + 50, TOP + 50)), 'fascia', (0, 1, 0), note='Outer face on the bed. Flat-head M3 into the ledge inserts.')
add('rear_io_plate', keep(rear, box(rear_split, D - 20, -50, W + 50, D + 50, TOP + 50)), 'fascia', (0, 1, 0), note='Replaceable I/O plate: cutouts finalised once panel-mount parts are chosen.')

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ LID halves (wedge housing) + inlays + splice plates
lid = part('lid_body').fuse(part('lid_deck'))
lid_inl_face, lid_inl_deck = [], []
phi = math.atan(g['deck_slope']); dn = np.array([0, -math.sin(phi), math.cos(phi)])
inlay_parts = ['brand_lid', 'brand_lid_model'] + [n for n in P2 if n.startswith('accent_') and n.endswith('_lid')]
for n in inlay_parts:
    for s in solids_of(part(n)):
        bb = s.bounding_box()
        if bb.max.Z <= 0.05:
            lid_inl_face.append((n, shifted(s, dz=Q3['inlay']['lid_face'])))
        else:
            v = -dn * Q3['inlay']['deck']; lid_inl_deck.append((n, shifted(s, *v)))
stage('for _, s in lid_inl_face + lid_inl_deck:')
lid = lid.cut(*[s for _, s in lid_inl_face + lid_inl_deck])
# Splice plates recessed into the pocket floor across the seam, plus dowels in the solid body.
kx0, ky0, kz0, kpc, kb_d = g['kx0'], g['ky0'], g['kz0'], g['kpc'], g['kb_d']
spl_tools, splices = [], []
for yc in (ky0 + 35, ky0 + kb_d - 35):
    rec = tilted(box(SEAM - 22, yc - 10, kz0 - g['T']['foam'] - 3, SEAM + 22, yc + 10, kz0 - g['T']['foam'] + 0.01))
    spl_tools.append(rec)
    plate = tilted(box(SEAM - 21.8, yc - 9.8, kz0 - g['T']['foam'] - 3, SEAM + 21.8, yc + 9.8, kz0 - g['T']['foam']))
    holes = []
    for dx in (-14, 14):
        holes.append(tilted(cyl(SEAM + dx, yc, kz0 - g['T']['foam'] - 3.2, SCR['clear_d'] / 2, 3.5)))
        holes.append(tilted(cyl(SEAM + dx, yc, kz0 - g['T']['foam'] - 1.5, SCR['head_d'] / 2 + 0.2, 1.6)))
        spl_tools.append(tilted(b.Pos(SEAM + dx, yc, kz0 - g['T']['foam'] - 3) * b.Rot(X=180) * b.Pos(0, 0, -0.2) * b.Cylinder(INS['hole_d'] / 2, INS['depth'] + 0.5, align=(b.Align.CENTER, b.Align.CENTER, b.Align.MIN))))
    splices.append(cut(plate, holes))
lid = cut(lid, spl_tools + [dowel_hole(SEAM, 8, 5), dowel_hole(SEAM, H - 8, 8)])
# Lid feet recesses and hinge-leaf inserts on the rear face (Y = H).
lid_feet_xy = [(24, 20), (W - 24, 20), (24, H - 20), (W - 24, H - 20)]
lid = cut(lid, [cyl(x, y, -0.1, 6 + CL, 1.2) for x, y in lid_feet_xy])
hinge_Z = g['hinge_Z']
lid_hinge_pts = [(hx + dx, hinge_Z - 14) for hx in HG['x'] for dx in (-9, 9)]
lid = cut(lid, [ins_hole(x, H, z, 'y', -1) for x, z in lid_hinge_pts])
LL = box(-50, -50, -50, SEAM, H + 50, 200); LR = box(SEAM, -50, -50, W + 50, H + 50, 200)
add('lid_left', keep(lid, LL), 'tray', (0, 0, -1), state='tray', note='Print on its outer face (front of the closed machine): flush logo inlays on the bed, deck badge inlays on top.')
add('lid_right', keep(lid, LR), 'tray', (0, 0, -1), state='tray')
for i, s in enumerate(splices):
    add('lid_splice_%d' % (i + 1), s, 'tray', None, state='tray', note='Recessed under the keyboard; joins the lid halves (2x M3 into inserts each side).')
add('inlay_lid_face', b.Compound(children=[s for _, s in lid_inl_face]), 'brand', (0, 0, -1), state='tray', group='lid_left', material='brand',
    note='Wordmark + model + diamond (multi-colour: diamond uses 4 Phosphor blues).')
add('inlay_lid_deck', b.Compound(children=[s for _, s in lid_inl_deck]), 'brand', (0, 0, -1), state='tray', group='lid_left', material='brand')

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ HINGES (printed) – case knuckle blocks + lid knuckle blocks
pin_r = Q3['hinge']['pin_hole_d'] / 2
case_hinges, lid_hinges = [], []
for hx in HG['x']:
    L_ = HG['length']; x0h, x1h = hx - L_ / 2, hx + L_ / 2; q1, q3 = x0h + L_ / 4, x1h - L_ / 4
    ch = cyl(q1, hinge_y, hinge_z, hk_r, q3 - q1, 'x').fuse(box(x0h, hinge_y, hinge_z - LEAF, x1h, hinge_y + HG['leaf'] + 6, hinge_z))
    ch = ch - cyl(q1 - 1, hinge_y, hinge_z, pin_r, q3 - q1 + 2, 'x')
    for dx in (-9, 9):
        ch = ch - clear_hole(hx + dx, hinge_y + 14, hinge_z - LEAF - 0.1, 'z', 1, LEAF + 0.3)
    case_hinges.append(ch)
    lk = b.Compound(children=[box(x0h, H, hinge_Z - HG['leaf'] - 6, x1h, H + LEAF, hinge_Z - hk_r - 0.5)])
    k1 = cyl(x0h, H, hinge_Z, hk_r, q1 - x0h - 0.5, 'x').fuse(box(x0h, H, hinge_Z - hk_r - 1, q1 - 0.5, H + LEAF, hinge_Z))
    k2 = cyl(q3 + 0.5, H, hinge_Z, hk_r, x1h - q3 - 0.5, 'x').fuse(box(q3 + 0.5, H, hinge_Z - hk_r - 1, x1h, H + LEAF, hinge_Z))
    lh = box(x0h, H, hinge_Z - HG['leaf'] - 6, x1h, H + LEAF, hinge_Z - hk_r - 0.5).fuse(k1, k2)
    lh = lh - cyl(x0h - 1, H, hinge_Z, pin_r, L_ + 2, 'x')
    for x, z in [(hx + dx, hinge_Z - 14) for dx in (-9, 9)]:
        lh = lh - clear_hole(x, H + LEAF + 0.1, z, 'y', -1, LEAF + 0.3)
    lid_hinges.append(lh)
for i, (ch, lh) in enumerate(zip(case_hinges, lid_hinges)):
    add('hinge_case_%d' % (i + 1), ch, 'metal', (0, 0, 1), note='Printed knuckle block under the case. 3 mm steel pin. Print leaf-up (knuckle on bed side) or use supports.', material='structural')
    add('hinge_lid_%d' % (i + 1), lh, 'metal', (0, 1, 0), state='tray', note='Printed knuckle block on the lid rear face.', material='structural')

# ------------------------------------------------------------------ LATCHES (printed): base + lever, M3 pivot
pins = g['pins']
latch_parts = []
for side, sgn, xb in (('left', -1, 0), ('right', 1, W)):
    base = solids_of(part('latch_bases'))[0 if side == 'left' else 1]
    for y, z in latch_pts:
        base = base - clear_hole(xb, y, z, 'x', sgn, 10) - cbore(xb + sgn * 9.1, y, z, 'x', -sgn, 3.5)
    px, py, pzz = pins[side]
    base = base - cyl(min(xb, xb + sgn * 14) - 1, py, pzz, Q3['latch_pin_d'] / 2 + 0.1, 16, 'x')
    lever = part('latch_lever_%s' % side) - cyl(min(xb, xb + sgn * 14) - 1, py, pzz, Q3['latch_pin_d'] / 2 + 0.1, 16, 'x')
    add('latch_base_%s' % side, base, 'rubber', (-sgn, 0, 0), note='Screws (M3, short inserts in the side wall) sit outside the lever path.', material='structural')
    add('latch_lever_%s' % side, lever, 'rubber', (0, 0, -1), state='latch_' + side, note='Pivot: 3 mm steel pin or M3 shoulder screw.', material='structural')

# ------------------------------------------------------------------ HANDLE (printed grip on a metal core) + pivot blocks
hd = Q3['handle']
gr = Q2['handle']['grip_diameter'] / 2; leg = Q2['handle']['leg_length']
grip = cyl(px0 + 10, pivot_y + leg, pz, max(gr, hd['core_d'] / 2 + 2.5), px1 - px0 - 20, 'x') - cyl(px0 + 9, pivot_y + leg, pz, hd['core_d'] / 2 + 0.15, px1 - px0 - 18, 'x')
legs = [box(px0 + 10, pivot_y - 6, pz - 3, px0 + 18, pivot_y + leg, pz + 3), box(px1 - 18, pivot_y - 6, pz - 3, px1 - 10, pivot_y + leg, pz + 3)]
handle = grip.fuse(*legs) - cyl(px0, pivot_y, pz, hd['pivot_pin_d'] / 2 + 0.1, px1 - px0, 'x') - cyl(px0 + 9, pivot_y + leg, pz, hd['core_d'] / 2 + 0.15, px1 - px0 - 18, 'x')
add('handle', handle, 'rubber', (0, 0, -1), state='handle', note='Grip slides over an 8 mm metal rod (structural); legs pivot on 4 mm steel pins. Proof-load before trusting.', material='structural')
for i, (xa, xb_) in enumerate(((px0, px0 + 9), (px1 - 9, px1))):
    blk = box(xa, pivot_y - 9, tub_floor, xb_, pivot_y + 9, tub_floor + 9)
    blk = blk - cyl(xa - 1, pivot_y, pz, hd['pivot_pin_d'] / 2 + 0.1, 11, 'x')
    for dy in (-4.5, 4.5):
        blk = blk - clear_hole((xa + xb_) / 2, pivot_y + dy, tub_floor + 9.1, 'z', -1, 9.4) - cbore((xa + xb_) / 2, pivot_y + dy, tub_floor + 9.1, 'z', -1, 3.2)
    add('handle_pivot_%d' % (i + 1), blk, 'metal', (0, 0, -1), material='structural')

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ INTERNAL parts
cage = part('drive_cage')
cage = cage.fuse(*[box(x - 5, y - 5, fh + iw, x + 5, y + 5, z0 - 4) for x, y in post_xy])
cage = cut(cage, [ins_hole(x, y, fh + iw, 'z', 1) for x, y in post_xy])
# Drive screw slots in the cage walls (hole positions not yet measured -> long slots).
dz_c = g['drv_cz']; dslots = []
for xw in (cx0, g['drv_cx'] - 4, cx1 - 4):
    for yc in (cg_y0 + 30, cg_y1 - 40):
        dslots.append(box(xw - 1, yc - 14, dz_c - 30 - 1.75, xw + 5, yc + 14, dz_c - 30 + 1.75))
cage = cut(cage, dslots)
add('drive_cage', cage, 'drawer', (0, 0, -1), note='Drive screw slots are generic until the MPF-920 side-hole positions are measured.', material='structural')
add('drawer', part('drawer'), 'drawer', (0, 0, -1), state='drawer')
for i, s in enumerate(solids_of(part('keyboard_clips'))):
    add('keyboard_clip_%d' % (i + 1), s, 'rubber', (0, 0, -1), state='tray', material='structural')
# Display bracket: frame on the display's outer M2.5 pattern, tabs to the bezel bosses.
DSP = g['DSP']; gx0, gz0 = g['glass_x0'], g['glass_z0']
outer = [(gx0 + DSP['width'] - v, gz0 + u) for u, v in DSP['mounting_holes']['portrait_rear_outer_uv']]
ox = sorted({round(p[0], 3) for p in outer}); oz = sorted({round(p[1], 3) for p in outer})
frame = box(ox[0] - 8, disp_back, oz[0] - 8, ox[-1] + 8, disp_back + 3, oz[-1] + 8)
frame -= box(ox[0] + 8, disp_back - 1, oz[0] + 8, ox[-1] - 8, disp_back + 4, oz[-1] - 8)
tabs = [box(x - 8, disp_back, min(z, oz[0] - 8), x + 8, disp_back + 3, max(z, oz[-1] + 8)) for x, z in br_pts]
brk = frame.fuse(*tabs)
brk = cut(brk, [cyl(x, disp_back - 1, z, Q3['m25_clear_d'] / 2, 5, 'y') for x, z in outer] + [cyl(x, disp_back - 1, z, SCR['clear_d'] / 2, 5, 'y') for x, z in br_pts])
add('display_bracket', brk, 'drawer', (0, 1, 0), note='M2.5 into the display rear outer pattern (thread depth not yet known: use the screws supplied with the display).', material='structural')
# Feet (TPU).
for i, (x, y) in enumerate(feet_xy):
    add('foot_case_%d' % (i + 1), cyl(x, y, fh - FEET['recess'], FEET['d'] / 2, FEET['recess']) .fuse(cyl(x, y, 0, FEET['d'] / 2, fh - FEET['recess'] + 0.01)), 'rubber', (0, 0, -1), material='tpu')
for i, (x, y) in enumerate(lid_feet_xy):
    add('foot_lid_%d' % (i + 1), cyl(x, y, -2.2, 6, 3.2), 'rubber', (0, 0, -1), state='tray', material='tpu')

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ COUPONS (print first)
c1 = box(0, 0, 0, 40, 14, 9)
for i, d in enumerate((3.9, 4.0, 4.1)):
    c1 = c1 - cyl(8 + i * 12, 7, 9 - INS['depth'] - 0.5, d / 2, INS['depth'] + 0.6)
add('coupon_C1_insert_holes', b.Pos(0, -60, 0) * c1, 'drawer', (0, 0, -1), note='Holes 3.9 / 4.0 / 4.1 mm (left to right). Pick the best and set p3.insert.hole_d.', material='coupon')
add('coupon_C3_seam_L', keep(shell_L, box(SEAM - 22, 80, fh - 1, SEAM, 104, fh + 30)), 'shell', (0, 0, -1), note='Seam block + counterbore (pair with C3_seam_R).', material='coupon')
add('coupon_C3_seam_R', keep(shell_R, box(SEAM, 80, fh - 1, SEAM + 22, 104, fh + 30)), 'shell', (0, 0, -1), note='Seam block + insert.', material='coupon')
add('coupon_C4_lip_corner', keep(shell_R, box(W - 40, -5, TOP - 45, W + 1, fy + 2, TOP + 1)), 'shell', (1, 0, 0), note='Top-right lip corner; check the closed-lid gap against coupon C4_lid.', material='coupon')
add('coupon_C5_inlay', keep(shell_R, box(W - 6, 100, fh + 12, W + 1, 150, fh + 42)), 'shell', (1, 0, 0), note='Side wall slice with wordmark pocket; print with its inlay to tune colour change.', material='coupon')
add('coupon_C5_inlay_letters', b.Compound(children=[keep(s_, box(W - 6, 100, fh + 12, W + 1, 150, fh + 42)) for s_ in side_inlay['right']]), 'brand', (1, 0, 0), group='coupon_C5_inlay', material='brand')
add('coupon_C6_shroud_corner', keep(PRINT['bezel_screen']['shape'], box(HOOD[0], fy - 20, HOOD[1] - 15, 60, disp_back + 1, HOOD[1] + 45)), 'fascia', (0, 1, 0), note='Shroud corner + flange with bezel screw hole.', material='coupon')

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ print orientation, printer assignment
def oriented(shape, down):
    if down is None:
        bb = shape.bounding_box(); s = shape
    else:
        d = np.array(down, float)
        if np.allclose(d, (0, 0, -1)): s = shape
        elif np.allclose(d, (0, 0, 1)): s = b.Rot(X=180) * shape
        elif np.allclose(d, (1, 0, 0)): s = b.Rot(Y=90) * shape
        elif np.allclose(d, (-1, 0, 0)): s = b.Rot(Y=-90) * shape
        elif np.allclose(d, (0, 1, 0)): s = b.Rot(X=-90) * shape
        elif np.allclose(d, (0, -1, 0)): s = b.Rot(X=90) * shape
        else: raise ValueError(down)
    bb = s.bounding_box()
    return b.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * s

def fits(dims, vol, m):
    a = sorted(dims[:2]); v = sorted(vol[:2])
    return a[0] <= v[0] - m and a[1] <= v[1] - m and dims[2] <= vol[2] - m

rows, issues = [], []
for name, p in PRINT.items():
    if p['group']:
        continue
    s, nsol = one(p['shape'], name)
    if nsol != 1:   # islands are fine if the multi-part print (host + its fused parts) is one connected body
        grp = [q['shape'] for q in PRINT.values() if q.get('group') == name and q['role'] != 'brand' and q['role'] != 'plate_text']
        if grp:
            _, nsol = one(b.Compound(children=solids_of(s) + [so for gsh in grp for so in solids_of(norm(gsh))]), name)
    if nsol != 1 and not name.startswith('coupon_'):
        issues.append('%s prints as %d separate solids' % (name, nsol))
    o = oriented(s, p['down'] or (0, 0, -1))
    bb = o.bounding_box(); dims = [bb.size.X, bb.size.Y, bb.size.Z]
    printer = next((pr for pr in Q3['printer_preference'] if fits(dims, Q3['printers'][pr]['volume'], Q3['print_margin'])), None)
    if printer is None:
        issues.append('%s (%.0f x %.0f x %.0f) fits no printer' % (name, *dims))
    inlays = [n for n, q in PRINT.items() if q['group'] == name]
    p.update(oriented=o, printer=printer, dims=dims, solids=nsol, inlays=inlays, volume=s.volume)
    b.export_stl(o, str(OUT / 'stl' / f'{name}.stl'))
    rows.append([name, printer or 'NONE', *[round(x, 1) for x in dims], round(s.volume / 1000, 1), p['material'], ','.join(inlays), p['note']])

# Inlays: oriented with the same transform as their host, exported with it in a 3MF.
def same_orientation(host_shape, host_down, inlay):
    if host_down is None: host_down = (0, 0, -1)
    d = np.array(host_down, float)
    rot = {(0, 0, -1): b.Rot(), (0, 0, 1): b.Rot(X=180), (1, 0, 0): b.Rot(Y=90), (-1, 0, 0): b.Rot(Y=-90), (0, 1, 0): b.Rot(X=-90), (0, -1, 0): b.Rot(X=90)}[tuple(int(v) for v in d)]
    hs = rot * host_shape; bb = hs.bounding_box()
    return b.Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * (rot * inlay)
stage("PAL = Q2['palettes']['m_edition']")
PAL = Q2['palettes']['m_edition']
import zipfile
def write_3mf(path, bodies):
    """Minimal 3MF: one mesh object per body (name, shape), grouped as components of one build object."""
    objs, comps = [], []
    for k, (nm, sh) in enumerate(bodies, start=1):
        verts, tris = [], []
        for so in solids_of(sh):
            v, f = so.tessellate(0.03, 0.2); off = len(verts)
            verts += [(q.X, q.Y, q.Z) for q in v]; tris += [(a + off, c_ + off, d + off) for a, c_, d in f]
        vx = ''.join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % t for t in verts)
        tx = ''.join('<triangle v1="%d" v2="%d" v3="%d"/>' % t for t in tris)
        objs.append('<object id="%d" name="%s" type="model"><mesh><vertices>%s</vertices><triangles>%s</triangles></mesh></object>' % (k, nm, vx, tx))
        comps.append('<component objectid="%d"/>' % k)
    pid = len(bodies) + 1
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>%s'
             '<object id="%d" name="%s" type="model"><components>%s</components></object></resources>'
             '<build><item objectid="%d"/></build></model>') % (''.join(objs), pid, Path(path).stem, ''.join(comps), pid)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', model)
for name, p in PRINT.items():
    if p['group'] or not p.get('inlays'):
        continue
    host, _ = one(p['shape'], name)
    bodies = [(name, p['oriented'])]
    for n in p['inlays']:
        q = PRINT[n]
        comp = b.Compound(children=[same_orientation(host, p['down'], s_) for s_ in solids_of(q['shape'])])
        b.export_stl(comp, str(OUT / 'stl' / f'{name}__{n}.stl'))
        bodies.append((n, comp))
    write_3mf(OUT / '3mf' / f'{name}.3mf', bodies)

with (OUT / 'print_manifest.csv').open('w', newline='') as f:
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['part', 'printer', 'x_mm', 'y_mm', 'z_mm', 'volume_cm3', 'material', 'inlays (same 3MF)', 'notes'])
    w.writerows(rows)

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ assembly checks (case frame, P2 states)
placed_state = g['STATES']
def at(name, state):
    p = PRINT[name]; s = p['shape']
    m = placed_state[state].get(p['state'], np.eye(4)) if p['state'] else np.eye(4)
    if np.allclose(m, np.eye(4)): return s
    from OCP.gp import gp_Trsf
    from OCP.TopLoc import TopLoc_Location
    t = gp_Trsf(); t.SetValues(*[float(m[i, j]) for i in range(3) for j in range(4)])
    return s.moved(b.Location(TopLoc_Location(t)))
def overlap(a, c):
    try:
        r = a.intersect(c); return 0.0 if r is None else float(r.volume)
    except Exception:
        return float('nan')
checks = []
def check(label, A, B_, state, tol=0.01):
    worst, pair = 0.0, None
    for a in A:
        for c in B_:
            v = overlap(at(a, state), at(c, state))
            if v > worst: worst, pair = v, (a, c)
    checks.append(dict(check=label, state=state, overlap_mm3=round(worst, 3), worst_pair=pair, ok=worst <= tol))
shells = ['shell_left', 'shell_right']
lids = ['lid_left', 'lid_right', 'lid_splice_1', 'lid_splice_2', 'hinge_lid_1', 'hinge_lid_2', 'keyboard_clip_1', 'keyboard_clip_2', 'foot_lid_1', 'foot_lid_2', 'foot_lid_3', 'foot_lid_4']
check('Shell halves do not overlap', ['shell_left'], ['shell_right'], 'operating')
check('Bezels fit the shell', ['bezel_screen', 'bezel_drives', 'bezel_screen_face', 'bezel_drives_face'], shells, 'operating')
check('Rear panels fit the shell', ['rear_panel_left', 'rear_io_plate'], shells, 'operating')
check('Closed lid clears case, bezels, latches, case hinges', lids, shells + ['bezel_screen', 'bezel_drives', 'latch_base_left', 'latch_base_right', 'latch_lever_left', 'latch_lever_right', 'hinge_case_1', 'hinge_case_2'], 'closed')
check('Open lid clears case and case hinges', lids, shells + ['hinge_case_1', 'hinge_case_2', 'foot_case_1', 'foot_case_2'], 'operating')
check('Hinge knuckles interleave (case vs lid) open', ['hinge_case_1', 'hinge_case_2'], ['hinge_lid_1', 'hinge_lid_2'], 'operating')
check('Hinge knuckles interleave (case vs lid) closed', ['hinge_case_1', 'hinge_case_2'], ['hinge_lid_1', 'hinge_lid_2'], 'closed')
check('Drive cage clears shell, bezels, rear', ['drive_cage'], shells + ['bezel_drives', 'rear_io_plate'], 'operating')
check('Drawer clears shell and rear panel (in and out)', ['drawer'], shells + ['rear_panel_left'], 'operating')
check('Drawer pulled out', ['drawer'], shells + ['rear_panel_left'], 'rear')
check('Display bracket clears bezel and shell', ['display_bracket'], ['bezel_screen'] + shells, 'operating')
check('Handle and pivots clear the shell (folded)', ['handle', 'handle_pivot_1', 'handle_pivot_2'], shells, 'operating')
check('Handle raised clears the shell', ['handle'], shells, 'closed')
check('Latch bases clear the shell', ['latch_base_left', 'latch_base_right'], shells, 'operating')
check('Case hinges clear shell and feet', ['hinge_case_1', 'hinge_case_2'], shells + ['foot_case_1', 'foot_case_2', 'foot_case_3', 'foot_case_4'], 'operating')
# Electronics from P2 vs printed internals.
for nm in ('floppy_drives', 'usb_hub', 'power_board', 'floppy_controller', 'display', 'pi5_board', 'pi5_cooler', 'floppy_cable_zone'):
    PRINT['_ref_' + nm] = dict(shape=part(nm), state=None)
check('Electronics clear the printed parts', ['_ref_' + n for n in ('floppy_drives', 'usb_hub', 'power_board', 'floppy_controller', 'display', 'pi5_board', 'pi5_cooler', 'floppy_cable_zone')],
      shells + ['drive_cage', 'display_bracket', 'bezel_screen', 'bezel_drives', 'rear_io_plate', 'rear_panel_left'], 'operating', tol=0.05)
ps_keep = box(W - sw - PS['keepout_depth'], ps_y - PS['cutout_w'] / 2 - 5, ps_z - PS['cutout_h'] / 2 - 5, W - sw, ps_y + PS['cutout_w'] / 2 + 5, ps_z + PS['cutout_h'] / 2 + 5)
PRINT['_ref_power_switch_keepout'] = dict(shape=ps_keep, state=None)
check('Power-switch keep-out clear of internals', ['_ref_power_switch_keepout'], ['_ref_usb_hub', '_ref_floppy_drives', 'drive_cage', 'shell_right'], 'operating', tol=0.05)

report = dict(revision=Q3['revision'], parts=len(rows), issues=issues, checks=checks,
              all_ok=not issues and all(c['ok'] for c in checks),
              printers={k: v['volume'] for k, v in Q3['printers'].items()})
(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
for c in checks:
    print(('OK   ' if c['ok'] else 'FAIL ') + c['check'], c['overlap_mm3'], c['worst_pair'] if not c['ok'] else '')
for i in issues: print('ISSUE', i)
print('parts', len(rows), 'all_ok', report['all_ok'])

stage('# ----------------------------------------------------------')
# ------------------------------------------------------------------ viewer scene (assembled / closed / exploded)
EXPLODE = {'shell_left': (-70, 0, 0), 'shell_right': (70, 0, 0), 'inlay_side_left': (-72, 0, 0), 'inlay_side_right': (72, 0, 0),
           'bezel_screen': (-20, -110, 0), 'bezel_drives': (20, -110, 0), 'bezel_screen_face': (-20, -110, 0), 'bezel_drives_face': (20, -110, 0), 'inlay_nameplate': (20, -112, 0),
           'rear_panel_left': (-20, 110, 0), 'rear_io_plate': (20, 110, 0), 'drive_cage': (60, 0, -40), 'drawer': (0, 160, 0),
           'display_bracket': (0, -50, 0), 'handle': (0, 0, 80), 'handle_pivot_1': (0, 0, 60), 'handle_pivot_2': (0, 0, 60),
           'latch_base_left': (-40, 0, 0), 'latch_lever_left': (-55, 0, 0), 'latch_base_right': (40, 0, 0), 'latch_lever_right': (55, 0, 0),
           'hinge_case_1': (0, 0, -30), 'hinge_case_2': (0, 0, -30)}
role_map = {'brand': 'brand', 'plate_text': 'plate_text'}
scene = {'parts': [], 'states': {}, 'palettes': Q2['palettes'], 'active': g['ACTIVE'], 'glass_y': glass_y, 'size': [W, D, TOP],
         'dims': json.loads((ROOT / 'outputs/p2/validation.json').read_text())['dimensions_mm'], 'brand': Q2['branding'],
         'stateButtons': [['operating', 'Assembled'], ['closed', 'Closed'], ['rear', 'Exploded'], ['xray', 'X-ray']]}
show_refs = ['floppy_drives', 'display', 'pi5_board', 'pi5_cooler', 'keyboard_body', 'keycaps', 'keycaps_mod', 'keycaps_accent', 'usb_hub', 'power_board', 'floppy_controller', 'diskettes', 'led_power', 'led_drives']
items = [(n, p['shape'], p['role'], p['state']) for n, p in PRINT.items() if not n.startswith('_ref_')]
items += [('ref_' + n, P2[n]['shape'], P2[n]['role'], P2[n]['state']) for n in show_refs]
for n, sh, role, st in items:
    verts, tris = [], []
    for s in solids_of(sh):
        v, f = s.tessellate(0.1, 0.3); off = len(verts)
        verts += [(round(q.X, 3), round(q.Y, 3), round(q.Z, 3)) for q in v]; tris += [(a + off, c + off, d + off) for a, c, d in f]
    key = (st or '') + ('|x:' + n if n in EXPLODE else '')
    scene['parts'].append({'name': n, 'role': role, 'group': '', 'state': key or None, 'note': PRINT.get(n, {}).get('note', ''),
                           'v': [c for q in verts for c in q], 'f': [c for t in tris for c in t]})
def M_pos(x, y, z): m = np.eye(4); m[:3, 3] = (x, y, z); return m
for sname, base_state in (('operating', 'operating'), ('closed', 'closed'), ('rear', 'operating'), ('xray', 'operating')):
    st = placed_state[base_state]
    out = {'_world': st['_world']}
    for prt in scene['parts']:
        key = prt['state']
        if not key: continue
        base_key, _, xn = key.partition('|x:')
        m = st.get(base_key, np.eye(4)) if base_key else np.eye(4)
        if sname == 'rear' and xn:
            m = M_pos(*EXPLODE[xn]) @ m
        out[key] = m
    scene['states'][sname] = {k: [round(float(x), 6) for x in m.flatten()] for k, m in out.items()}
(OUT / 'scene.json').write_text(json.dumps(scene, separators=(',', ':')))
kids = []
for n, p in PRINT.items():
    if n.startswith('_ref_'): continue
    s = at(n, 'operating')
    s.label = n; s.color = b.Color(PAL.get(p['role'], '#888888')); kids.append(s)
b.export_step(b.Compound(children=kids, label='retro_m_p3_print_assembly'), str(OUT / 'p3_assembly.step'))
print('scene + STEP written')
