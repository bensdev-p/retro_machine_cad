"""P2 concept: Kaypro-style luggable massing for the Retro / M Raspberry Pi build.

Coordinates (mm): x to the right, y from the front lip of the case toward the rear,
z up from the desk.  The keyboard housing ("tray") is also the front lid: in the
closed/transport state it latches into the hood with the keycaps facing the screen.

Hardware bodies are envelopes, not product models.  Everything that is a guess is
flagged in parameters.json -> p2 and in docs/concept-P2.md.
"""
from pathlib import Path
import json, math
import numpy as np
import build123d as b

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'parameters.json').read_text())
Q = P['p2']; KB = P['keyboard']; DSP = P['display']
C, T, SH, FA, SS, DR, PI, DW, HD = (Q[k] for k in ('case', 'tray', 'shield', 'fascia', 'screen_shroud', 'drive', 'pi_stack', 'drawer', 'handle'))
OUT = ROOT / 'outputs/p2'; OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- helpers
def box(x0, y0, z0, x1, y1, z1):
    return b.Pos(x0, y0, z0) * b.Box(x1 - x0, y1 - y0, z1 - z0, align=(b.Align.MIN,) * 3)

def rect_wire(y, x0, z0, x1, z1):
    return b.Wire.make_polygon([b.Vector(x0, y, z0), b.Vector(x1, y, z0), b.Vector(x1, y, z1), b.Vector(x0, y, z1)], close=True)

def frustum(y0, r0, y1, r1):
    """Ruled loft between two x/z rectangles on planes of constant y."""
    return b.Solid.make_loft([rect_wire(y0, *r0), rect_wire(y1, *r1)], ruled=True)

def grow(r, d):
    return (r[0] - d, r[1] - d, r[2] + d, r[3] + d)

def cyl(x, y, z, r, length, axis='z'):
    s = b.Cylinder(r, length, align=(b.Align.CENTER, b.Align.CENTER, b.Align.MIN))
    if axis == 'y': s = b.Rot(X=-90) * s
    if axis == 'x': s = b.Rot(Y=90) * s
    return b.Pos(x, y, z) * s

FRONT_PLANE = lambda x, y, z: b.Plane(origin=(x, y, z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
REAR_PLANE = lambda x, y, z: b.Plane(origin=(x, y, z), x_dir=(-1, 0, 0), z_dir=(0, 1, 0))

def text_cut(txt, plane, size, depth=0.6):
    """Engraving tool: text on a plane, spanning depth into the face (+0.1 proud)."""
    sk = b.Text(txt, font_size=size, font='DejaVu Sans', font_style=b.FontStyle.BOLD)
    solid = b.extrude(sk, amount=depth + 0.1)
    return plane.location * b.Pos(0, 0, -depth) * solid

def cut_all(shape, tools):
    return shape.cut(*tools) if tools else shape

parts = {}    # name -> dict(shape, role, group, movable)

def add(name, shape, role, group, state_key=None, note=''):
    if isinstance(shape, list):
        shape = b.Compound(children=shape)
    assert shape.is_valid, name
    parts[name] = dict(shape=shape, role=role, group=group, state=state_key, note=note)
    return shape

# ---------------------------------------------------------------- derived layout
W, D = C['width'], C['depth']
fh = C['feet_height']
kb_w, kb_d, kb_h = KB['width'], KB['depth'], KB['height']
sw, iw = C['side_wall'], C['inner_wall']
hood_w, hood_h = W - 2 * sw, C['hood_height']
H = C['bottom_wall'] + hood_h + C['top_wall']
HOOD = (sw, fh + C['bottom_wall'], sw + hood_w, fh + C['bottom_wall'] + hood_h)
hood_cz = (HOOD[1] + HOOD[3]) / 2
TOP = fh + H

# Wedge lid, local frame: X 0..W, Y 0..H (Y=0 = user edge), Z up from the lid underside.
# Closed, local Y maps to world z = TOP - Y and local Z to world y = Z - FT_ (underside forms the front face).
FT_ = 4.0
tilt = math.radians(T['platform_tilt_deg'])
kpc = T['pocket_clearance']
kx0 = (W - kb_w) / 2
ky0 = (TOP - hood_cz) - kb_d * math.cos(tilt) / 2          # keyboard centred in the hood when closed
kz0 = T['platform_base'] + T['foam']                        # keyboard underside at its front edge
def case_top(yk):  # keyboard's own case top above its underside, yk from its front edge (envelope guess)
    return 17 + 8 * yk / kb_d
deck_slope = math.tan(tilt) + 8 / kb_d
def deck_z(Y):     # lid top (deck) surface height in lid-local coords
    return kz0 + case_top(0) - T['deck_recess'] + deck_slope * (Y - ky0)
def lip_y(z):      # world y of the slanted case lip at height z (matches the closed deck + gap)
    return deck_z(TOP - z) - FT_ + T['lip_gap']
# Closed keyboard envelope: full spec height everywhere, tilted -> conservative reach toward the fascia.
env_reach = kz0 + kb_d * math.sin(tilt) + kb_h * math.cos(tilt) - FT_
kb_reach = env_reach
fy = math.ceil(env_reach + SH['keycap_clearance'])        # fascia front plane
glass_y = fy + SS['depth']
vis = grow(HOOD, -SH['inset'])                               # visible fascia after the shield frame

# Screen: active area centred vertically in the hood.
act_w, act_h = DSP['active_width'], DSP['active_height']
scr_back = (0, 0, act_w + 2 * SS['glass_overlap'], act_h + 2 * SS['glass_overlap'])
scr_front_w = scr_back[2] + 2 * SS['widen']; scr_front_h = scr_back[3] + 2 * SS['widen']
scr_x0 = vis[0] + SS['left_margin']
act_cx = scr_x0 + scr_front_w / 2
SCR_FRONT = (scr_x0, hood_cz - scr_front_h / 2, scr_x0 + scr_front_w, hood_cz + scr_front_h / 2)
SCR_BACK = grow(SCR_FRONT, -SS['widen'])
ACTIVE = grow(SCR_BACK, -SS['glass_overlap'])
glass_x0 = act_cx - DSP['width'] / 2; glass_z0 = hood_cz - DSP['height'] / 2

# Drives: two vertical drives side by side, centred in the space right of the screen shroud.
dw_x, dw_z = DR['height'], DR['width']                   # vertical orientation swaps width/height
cluster_w = 2 * dw_x + DR['gap']
drv_cx = (SCR_FRONT[2] + vis[2]) / 2
drv_cz = fh + DR['center_z']
DRV_BACK = (drv_cx - cluster_w / 2 - DR['shroud_margin'], drv_cz - dw_z / 2 - DR['shroud_margin'],
            drv_cx + cluster_w / 2 + DR['shroud_margin'], drv_cz + dw_z / 2 + DR['shroud_margin'])
DRV_FRONT = grow(DRV_BACK, DR['shroud_widen'])
drive_x = [drv_cx - cluster_w / 2, drv_cx + DR['gap'] / 2]

# ---------------------------------------------------------------- shell (one visual body)
outer = box(0, 0, fh, W, D, TOP)
outer = b.fillet(outer.edges(), C['outer_radius'])
shell = outer - box(sw, fy, fh + iw, W - sw, D + 1, TOP - iw)        # main cavity, rear open
shell -= box(HOOD[0], -1, HOOD[1], HOOD[2], fy + 0.01, HOOD[3])      # hood
# Slanted Kaypro lip: the case reaches further forward at the top, matching the wedge lid.
z_a, z_b = fh - 1, TOP + 1
lip_cut = b.Pos(-1, 0, 0) * b.extrude(b.Plane.YZ * b.make_face(b.Polyline((-20, z_a), (lip_y(z_a), z_a), (lip_y(z_b), z_b), (-20, z_b), close=True)), amount=W + 2)
shell -= lip_cut
# Handle tub in the top panel.
px0, px1 = HD['pocket_x']; pivot_y = HD['pivot_y']; leg = HD['leg_length']
pk_y0, pk_y1 = pivot_y - 10, pivot_y + leg + 10
shell = shell.fuse(box(px0 - 2, pk_y0 - 2, TOP - HD['pocket_depth'] - 2, px1 + 2, pk_y1 + 2, TOP - 1))
shell -= box(px0, pk_y0, TOP - HD['pocket_depth'], px1, pk_y1, TOP + 1)
# Side ribs (Kaypro 10 style).  On the left the ribs beside the Pi are cut through as intake vents.
tools = []
rib_z = [fh + 34 + 12 * i for i in range(13)]
rib_y0 = math.ceil(lip_y(fh) + 34)
vent_y = (glass_y + 18, glass_y + 72)
for z in rib_z:
    tools += [box(-1, rib_y0, z, 1.0, D - 14, z + 2.2), box(W - 1.0, rib_y0, z, W + 1, D - 14, z + 2.2)]
    if 60 < z - fh < 160:
        tools.append(box(-1, vent_y[0], z, sw + 1, vent_y[1], z + 2.2))
# Top louvres over the Pi (exhaust).
for i in range(6):
    tools.append(box(64, glass_y + 4 + i * 8, TOP - iw - 1, 228, glass_y + 7.5 + i * 8, TOP + 1))
# Keyboard USB-C (charge / wired mode) on the left side, behind the fascia.
tools.append(box(-1, glass_y + 4, fh + 20, sw + 1, glass_y + 13.5, fh + 23.5))
shell = cut_all(shell, tools)
stripes = []
for z in rib_z:
    stripes.append(box(W - 1.0, rib_y0, z, W - 0.3, D - 14, z + 2.2))
    if 60 < z - fh < 160:
        stripes += [box(0.3, rib_y0, z, 1.0, vent_y[0], z + 2.2), box(0.3, vent_y[1], z, 1.0, D - 14, z + 2.2)]
    else:
        stripes.append(box(0.3, rib_y0, z, 1.0, D - 14, z + 2.2))
add('side_stripes', stripes, 'stripe', 'case', note='Inlays in the side grooves (blue on the Kaypro II colourway).')
add('shell', shell, 'shell', 'case', note='Outer wrap with slanted Kaypro lip, top handle tub, ribbed sides, louvres. Will be split into printable panels in P2-detail.')

# Shield frame: the angled ring between hood walls and fascia.
sh_y0 = fy - SH['depth']
shield = box(HOOD[0], sh_y0, HOOD[1], HOOD[2], fy, HOOD[3]) - frustum(sh_y0 - 0.01, grow(HOOD, 0.01), fy + 0.01, grow(vis, -0.0))
add('shield_frame', shield, 'bezel', 'front', note='Angled shielding ring; keycap envelope clears it (see validation).')

# ---------------------------------------------------------------- fascia + shrouds
ft = FA['thickness']
fascia = box(HOOD[0], fy, HOOD[1], HOOD[2], fy + ft, HOOD[3])
fascia -= box(SCR_FRONT[0], fy - 1, SCR_FRONT[1], SCR_FRONT[2], fy + ft + 1, SCR_FRONT[3])
fascia -= box(DRV_FRONT[0], fy - 1, DRV_FRONT[1], DRV_FRONT[2], fy + ft + 1, DRV_FRONT[3])
tools = []
gx0 = SCR_FRONT[2] + 7
keep = grow(DRV_FRONT, 3)
z = vis[1] + 3
while z + FA['groove_width'] < vis[3] - 2:
    g = box(gx0, fy - 0.1, z, vis[2] - 2, fy + FA['groove_depth'], z + FA['groove_width'])
    if not (z + FA['groove_width'] > keep[1] and z < keep[3]):
        tools.append(g)
    else:
        tools += [box(gx0, fy - 0.1, z, keep[0], fy + FA['groove_depth'], z + FA['groove_width']),
                  box(keep[2], fy - 0.1, z, vis[2] - 2, fy + FA['groove_depth'], z + FA['groove_width'])]
    z += FA['groove_pitch']
# Status LEDs above the drive shroud (power, A, B) with engraved legends below the groove field.
led_z = DRV_FRONT[3] + 10
led_x = [DRV_FRONT[0] + 6, drive_x[0] + dw_x / 2, drive_x[1] + dw_x / 2]
for x in led_x:
    tools.append(cyl(x, fy - 1, led_z, 2.6, ft + 2, 'y'))
fascia = cut_all(fascia, tools)
# Smooth legend band under the LEDs (no grooves) is built as a raised plate.
legend = box(DRV_FRONT[0] - 4, fy - 0.6, led_z - 13, DRV_FRONT[2] + 4, fy, led_z + 6)
legend -= cyl(led_x[0], fy - 1, led_z, 2.6, 3, 'y')
legend -= cyl(led_x[1], fy - 1, led_z, 2.6, 3, 'y')
legend -= cyl(led_x[2], fy - 1, led_z, 2.6, 3, 'y')
leg_tools = [text_cut('POWER', FRONT_PLANE(led_x[0] + 1, fy - 0.6, led_z - 8), 3.4, 0.4),
             text_cut('A', FRONT_PLANE(led_x[1], fy - 0.6, led_z - 8), 3.4, 0.4),
             text_cut('B', FRONT_PLANE(led_x[2], fy - 0.6, led_z - 8), 3.4, 0.4)]
legend = cut_all(legend, leg_tools)
add('fascia', fascia, 'fascia', 'front', note='Recessed front panel with Kaypro 10-style horizontal grooves.')
add('legend_plate', legend, 'fascia', 'front')

def shroud(front, back, y0, y1, margin=3):
    blk = box(front[0] - margin, y0, front[1] - margin, front[2] + margin, y1, front[3] + margin)
    return blk - frustum(y0 - 0.01, grow(front, 0.01), y1 + 0.01, back)

scr_sh = shroud(SCR_FRONT, SCR_BACK, fy, glass_y)
add('screen_shroud', scr_sh, 'bezel', 'front', note='Angled CRT-style surround; glass sits %.0f mm behind the fascia.' % SS['depth'])
drv_sh = shroud(DRV_FRONT, DRV_BACK, fy, glass_y)
drv_sh -= box(drive_x[0], glass_y - 1, drv_cz - dw_z / 2, drive_x[0] + dw_x, glass_y + 1, drv_cz + dw_z / 2)
drv_sh -= box(drive_x[1], glass_y - 1, drv_cz - dw_z / 2, drive_x[1] + dw_x, glass_y + 1, drv_cz + dw_z / 2)
add('drive_shroud', drv_sh, 'bezel', 'front', note='Angled surround for the two vertical drives.')

leds = [cyl(led_x[0], fy - 1.2, led_z, 2.4, ft + 1.4, 'y')]
add('led_power', leds[0], 'led_power', 'front')
add('led_drives', [cyl(x, fy - 1.2, led_z, 2.4, ft + 1.4, 'y') for x in led_x[1:]], 'led_drive', 'front')

# ---------------------------------------------------------------- display, Pi, drives
disp = box(glass_x0, glass_y, glass_z0, glass_x0 + DSP['width'], glass_y + DSP['depth'], glass_z0 + DSP['height'])
add('display', disp, 'glass', 'electronics', note='Touch Display 2 10.1in envelope (manufacturer reference dims).')
disp_back = glass_y + DSP['depth']
holes = [(glass_x0 + DSP['width'] - v, glass_z0 + u) for u, v in DSP['mounting_holes']['portrait_rear_inner_uv']]
hx0 = min(h[0] for h in holes); hz0 = min(h[1] for h in holes)
by0 = disp_back + PI['standoff']; by1 = by0 + PI['board_thickness']
board = box(hx0 - 3.5, by0, hz0 - 3.5, hx0 - 3.5 + 85, by1, hz0 - 3.5 + 56)
standoffs = [cyl(x, disp_back, z, 2.5, PI['standoff'], 'y') for x, z in holes]
add('pi5_board', board, 'pcb', 'electronics', note='Pi 5 on the display rear inner 58x49 M2.5 pattern (nominal board envelope).')
add('pi5_standoffs', standoffs, 'metal', 'electronics')
cool = box(hx0 + 2, by1, hz0 - 1, hx0 + 62, by1 + PI['cooler_height'], hz0 + 44)
add('pi5_cooler', cool, 'metal', 'electronics', note='Active Cooler clearance envelope.')
pi_back = by1 + PI['cooler_height']

drives = []
for i, x in enumerate(drive_x):
    d = box(x, glass_y, drv_cz - dw_z / 2, x + dw_x, glass_y + DR['depth'], drv_cz + dw_z / 2)
    d -= box(x + dw_x / 2 - 2, glass_y - 1, drv_cz - 44, x + dw_x / 2 + 2, glass_y + 4, drv_cz + 40)  # media slot
    d -= box(x + 4, glass_y - 1, drv_cz - 49, x + dw_x - 4, glass_y + 1.2, drv_cz - 45)            # eject button recess
    drives.append(d)
add('floppy_drives', drives, 'drive', 'electronics', note=DR['model'] + ' x2, vertical. ' + DR['status'])

# Drive cage: base, outer walls, divider and a top shelf that carries the USB hub.
cg_y0, cg_y1 = glass_y + 4, glass_y + DR['depth']
z0, z1 = drv_cz - dw_z / 2, drv_cz + dw_z / 2
cx0, cx1 = drive_x[0] - 6, drive_x[1] + dw_x + 6
cage = box(cx0, cg_y0, z0 - 4, cx1, cg_y1, z0)
cage = cage.fuse(box(cx0, cg_y0, z0 - 4, cx0 + 4, cg_y1, z1 + 4),
                 box(cx1 - 4, cg_y0, z0 - 4, cx1, cg_y1, z1 + 4),
                 box(drv_cx - 4, cg_y0, z0 - 4, drv_cx + 4, cg_y1, z1 + 4),
                 box(cx0, cg_y0, z1 + 1, cx1 + 0, D - 9, z1 + 4),
                 box(cx0, cg_y0, fh + iw, cx1, cg_y0 + 10, z0 - 4),
                 box(cx0, cg_y1 - 10, fh + iw, cx1, cg_y1, z0 - 4))
cage -= box(cx0 + 10, cg_y0 + 20, z1 + 0.5, cx1 - 10, cg_y1 - 20, z1 + 5)   # lightening window
add('drive_cage', cage, 'drawer', 'internal', note='Printed cradle; drives screw in through the side walls (MPF920 side holes to confirm).')

# Electronics envelopes in the spare volume.
hub = box(cx0 + 2, D - 9 - 72, z1 + 4, cx1 + 4, D - 9, z1 + 4 + 26)
add('usb_hub', hub, 'electronics', 'electronics', note='Powered 4-port USB hub envelope, ports facing the rear I/O panel.')
ctrl = box(cx0 + 6, glass_y + 30, fh + iw + 2, cx0 + 66, glass_y + 80, fh + iw + 18)
add('floppy_controller', ctrl, 'pcb', 'electronics', note='USB floppy controller envelope (Greaseweazle-class; one 34-pin cable serves A and B).')
pwr = box(cx0 + 4, glass_y + 92, fh + iw + 2, cx1 - 2, glass_y + 140, fh + iw + 26)
add('power_board', pwr, 'electronics', 'electronics', note='5 V distribution / PD input envelope for Pi, hub and drives.')

# ---------------------------------------------------------------- rear panel + drawer
rp_y0, rp_y1 = D - 7, D - 3
rear = box(sw, rp_y0, fh + iw, W - sw, rp_y1, TOP - iw)
dz0 = fh + DW['z0']; dz1 = dz0 + 116
tools = [box(DW['x0'] - 0.6, rp_y0 - 1, dz0 - 0.6, DW['x1'] + 0.6, rp_y1 + 1, dz1 + 0.6)]
for i in range(6):
    tools.append(box(26, rp_y0 - 1, dz1 + 12 + i * 10, DW['x1'] - 16, rp_y1 + 1, dz1 + 17 + i * 10))
# I/O cluster (right): hub USB-A x4, HDMI, RJ45, USB-C power in, rocker switch.
io_x = cx0 + 8
for i in range(4):
    tools.append(box(io_x + i * 20, rp_y0 - 1, z1 + 12, io_x + i * 20 + 13.5, rp_y1 + 1, z1 + 18.5))
tools += [box(io_x, rp_y0 - 1, fh + 128, io_x + 16, rp_y1 + 1, fh + 136),                 # HDMI (from Pi micro-HDMI)
          box(io_x + 30, rp_y0 - 1, fh + 122, io_x + 46, rp_y1 + 1, fh + 140),           # RJ45 keystone
          box(io_x, rp_y0 - 1, fh + 62, io_x + 10, rp_y1 + 1, fh + 66),                  # USB-C power in
          box(io_x + 30, rp_y0 - 1, fh + 52, io_x + 51, rp_y1 + 1, fh + 66)]             # rocker switch
for i in range(5):
    tools.append(box(io_x, rp_y0 - 1, fh + 20 + i * 5, cx1 - 2, rp_y1 + 1, fh + 22.5 + i * 5))
tools += [text_cut('RETRO / M', REAR_PLANE(io_x + 40, rp_y1, fh + 90), 6, 0.5)]
rear = cut_all(rear, tools)
add('rear_panel', rear, 'fascia', 'case', note='Inset rear panel: drawer opening, exhaust louvres and I/O plate.')

dy0, dy1 = math.ceil(pi_back + DW['cooler_gap']), rp_y1
wt = DW['wall']
drawer = box(DW['x0'], dy0, dz0, DW['x1'], dy1 - 4, dz0 + DW['wall_height'])
drawer -= box(DW['x0'] + wt, dy0 + wt, dz0 + wt, DW['x1'] - wt, dy1 - 4 - 0.01, dz0 + DW['wall_height'] + 1)
drawer = drawer.fuse(box(DW['divider_x'], dy0, dz0, DW['divider_x'] + wt, dy1 - 4, dz0 + DW['wall_height'] - 10),
                     box(DW['x0'], dy1 - 4, dz0, DW['x1'], dy1, dz1))              # front plate = panel infill
drawer -= box((DW['x0'] + DW['x1']) / 2 - 45, dy1 - 2.2, dz1 - 22, (DW['x0'] + DW['x1']) / 2 + 45, dy1 + 1, dz1 - 8)  # finger pull
drawer -= box(DW['x0'] + 20, dy1 - 0.8, dz0 + 30, DW['x0'] + 90, dy1 + 1, dz0 + 62)  # label card recess
drawer = cut_all(drawer, [text_cut('DISKS', REAR_PLANE(DW['x0'] + 55, dy1 - 0.8, dz0 + 46), 7, 0.5)])
add('drawer', drawer, 'drawer', 'storage', 'drawer', note='Rear drawer: diskette file (left, ~28 disks) + accessory bin (right).')
dk = DW['diskette']
disks = []
n_disk = 12
for i in range(n_disk):
    y = dy0 + wt + 6 + i * (dk[2] + 1.2)
    x0 = DW['x0'] + wt + (DW['divider_x'] - DW['x0'] - wt - dk[0]) / 2
    disks.append(box(x0, y, dz0 + wt, x0 + dk[0], y + dk[2], dz0 + wt + dk[1]))
add('diskettes', disks, 'disks', 'storage', 'drawer', note='Sample 3.5in diskettes (90x94x3.3).')
rails = [box(DW['x0'] - 0.5 - 4, dy0, fh + iw, DW['x0'] - 0.5, rp_y0, dz0 + 10),
         box(DW['x1'] + 0.5, dy0, fh + iw, DW['x1'] + 4.5, rp_y0, dz0 + 10)]
add('drawer_rails', rails, 'drawer', 'internal')

# ---------------------------------------------------------------- feet, latches, handle
feet = [cyl(x, y, 0, C['feet_diameter'] / 2, fh + 0.5) for x in (28, W - 28) for y in (28, D - 28)]
add('feet', feet, 'rubber', 'case')

latch_y0 = lip_y(hood_cz) + 3
def latch_parts(side):
    s_ = 1 if side == 'right' else -1
    xb = W if side == 'right' else 0
    base = box(min(xb, xb + s_ * 9), latch_y0, hood_cz - 22, max(xb, xb + s_ * 9), latch_y0 + 30, hood_cz + 22)
    base = b.fillet(base.edges().filter_by(b.Axis.Y), 2.5)
    pin = (xb + s_ * 5, latch_y0 + 20, hood_cz)
    lever = box(min(xb + s_ * 9, xb + s_ * 13), -9, hood_cz - 11, max(xb + s_ * 9, xb + s_ * 13), latch_y0 + 26, hood_cz + 11)
    hook = box(min(xb - s_ * 6, xb + s_ * 13), -9, hood_cz - 11, max(xb - s_ * 6, xb + s_ * 13), -5.2, hood_cz + 11)
    return base, lever.fuse(hook), pin

latch_bases, levers, pins = [], {}, {}
for side in ('left', 'right'):
    bse, lev, pin = latch_parts(side)
    latch_bases.append(bse); levers[side] = lev; pins[side] = pin
add('latch_bases', latch_bases, 'rubber', 'case', note='Over-centre side latches clamp the lid flange (Kaypro-style).')
add('latch_lever_left', levers['left'], 'rubber', 'case', 'latch_left')
add('latch_lever_right', levers['right'], 'rubber', 'case', 'latch_right')

gr = HD['grip_diameter'] / 2
pz = TOP - HD['pocket_depth'] / 2
hparts = [cyl(px0 + 6, pivot_y, pz, 4, px1 - px0 - 12, 'x'),     # hidden pivot axle line (visual)
          box(px0 + 10, pivot_y - 3, pz - 3, px0 + 18, pivot_y + leg, pz + 3),
          box(px1 - 18, pivot_y - 3, pz - 3, px1 - 10, pivot_y + leg, pz + 3),
          cyl(px0 + 10, pivot_y + leg, pz, gr, px1 - px0 - 20, 'x')]
add('handle', hparts, 'rubber', 'case', 'handle', note='Fold-flat bail handle in a top tub; pivots %.0f mm behind the lip.' % pivot_y)
add('handle_pivots', [box(px0, pivot_y - 7, TOP - HD['pocket_depth'], px0 + 9, pivot_y + 7, TOP - 2),
                      box(px1 - 9, pivot_y - 7, TOP - HD['pocket_depth'], px1, pivot_y + 7, TOP - 2)], 'metal', 'case')

# ---------------------------------------------------------------- keyboard housing / lid (local coords)
# Wedge housing: taller at the rear like the Kaypro keyboard. Body (blue on classic) + grey deck.
kb_axis = b.Axis((0, ky0, kz0), (1, 0, 0))
def tilted(shape):
    return shape.rotate(kb_axis, T['platform_tilt_deg'])
dt = T['deck_thickness']
def wedge(z_off):
    prof = b.Polyline((0, 0), (H, 0), (H, deck_z(H) + z_off), (0, deck_z(0) + z_off), close=True)
    return b.extrude(b.Plane.YZ * b.make_face(prof), amount=W)
pocket = tilted(box(kx0 - kpc, ky0 - kpc, kz0 - T['foam'], kx0 + kb_w + kpc, ky0 + kb_d + kpc, kz0 + 120))
lid_body = b.fillet(wedge(-dt).edges().filter_by(b.Axis.Z), C['outer_radius']) - pocket
lid_deck = (wedge(0) - wedge(-dt) - pocket)
lid_deck = lid_deck - (box(-1, -1, -1, W + 1, H + 1, 100) - b.fillet(box(0, 0, -1, W, H, 100).edges().filter_by(b.Axis.Z), C['outer_radius']))
add('lid_body', lid_body, 'flange', 'keyboard', 'tray', note='Wedge keyboard housing (%.0f mm at the front, %.0f mm at the rear). Its underside is the front face when closed.' % (deck_z(0), deck_z(H)))
add('lid_deck', lid_deck, 'tray', 'keyboard', 'tray', note='Sloped deck around the keyboard, following its slope + %.0f deg platform tilt.' % T['platform_tilt_deg'])
tfeet = [cyl(x, y, -2, 6, 2.2) for x in (24, W - 24) for y in (20, H - 20)]
add('lid_feet', tfeet, 'rubber', 'keyboard', 'tray')

# Keyboard envelope: case wedge + illustrative TKL keycaps (not a product model), built flat then tilted.
prof = b.Polyline((ky0, kz0), (ky0 + kb_d, kz0), (ky0 + kb_d, kz0 + case_top(kb_d)), (ky0, kz0 + case_top(0)), close=True)
kb_body = b.Pos(kx0, 0, 0) * b.extrude(b.Plane.YZ * b.make_face(prof), amount=kb_w)
kb_body = tilted(b.fillet(kb_body.edges().filter_by(b.Axis.Z), 4))
add('keyboard_body', kb_body, 'kb_body', 'keyboard', 'tray', note='8BitDo Retro Mechanical Keyboard M Edition envelope (%.1f x %.1f x %.1f).' % (kb_w, kb_d, kb_h))
u = 19.05
rows = [  # (row, [(label, width_u, kind)]) ; kind: a=alpha m=mod x=accent g=gap
    [('Esc', 1, 'x'), ('', 1, 'g')] + [('F', 1, 'm')] * 4 + [('', .5, 'g')] + [('F', 1, 'm')] * 4 + [('', .5, 'g')] + [('F', 1, 'm')] * 4 + [('', .5, 'g')] + [('n', 1, 'm')] * 3,
    [('k', 1, 'a')] * 13 + [('Bk', 2, 'm'), ('', .5, 'g')] + [('n', 1, 'm')] * 3,
    [('Tab', 1.5, 'm')] + [('k', 1, 'a')] * 12 + [('\\', 1.5, 'a'), ('', .5, 'g')] + [('n', 1, 'm')] * 3,
    [('Caps', 1.75, 'm')] + [('k', 1, 'a')] * 11 + [('Ent', 2.25, 'x')],
    [('Sh', 2.25, 'm')] + [('k', 1, 'a')] * 10 + [('Sh', 2.75, 'm'), ('', 1.5, 'g'), ('Up', 1, 'm')],
    [('c', 1.25, 'm')] * 3 + [('Sp', 6.25, 'a')] + [('c', 1.25, 'm')] * 4 + [('', .5, 'g')] + [('n', 1, 'm')] * 3,
]
keys = {'a': [], 'm': [], 'x': []}
lx0 = kx0 + (kb_w - 18.5 * u) / 2
row_y = [ky0 + 12 + (5 - r) * u + (0 if r else 0.5 * u) for r in range(6)]
row_y[0] = ky0 + 12 + 5.5 * u
for r, row in enumerate(rows):
    x = lx0; yk = row_y[r]
    for lab, wu, kind in row:
        if kind != 'g':
            base_z = kz0 + case_top(yk - ky0 + u / 2) + 4
            top_h = 9 + (r == 0) * 1.5 + (r == 1) * 1.0
            cap = b.Solid.make_loft([
                b.Wire.make_polygon([b.Vector(x + .5, yk + .5, base_z), b.Vector(x + wu * u - .5, yk + .5, base_z), b.Vector(x + wu * u - .5, yk + u - .5, base_z), b.Vector(x + .5, yk + u - .5, base_z)], close=True),
                b.Wire.make_polygon([b.Vector(x + 2.6, yk + 2.2, base_z + top_h), b.Vector(x + wu * u - 2.6, yk + 2.2, base_z + top_h), b.Vector(x + wu * u - 2.6, yk + u - 3.4, base_z + top_h), b.Vector(x + 2.6, yk + u - 3.4, base_z + top_h)], close=True)], ruled=True)
            keys[kind].append(tilted(cap))
        x += wu * u
add('keycaps', keys['a'], 'keys', 'keyboard', 'tray', note='Illustrative TKL layout.')
add('keycaps_mod', keys['m'], 'mod_keys', 'keyboard', 'tray')
add('keycaps_accent', keys['x'], 'accent_keys', 'keyboard', 'tray')
# Retention: two swing clips on the deck reach over the keyboard's case edge so it stays put when carried.
ym = ky0 + kb_d / 2
kb_top_m = kz0 + math.sin(tilt) * (kb_d / 2 + 12) + case_top(kb_d / 2 + 12) * math.cos(tilt)  # highest point under the clip
clips = []
for xa, xb_, xc in ((sw + 1, kx0 - kpc, kx0 + 4), (kx0 + kb_w + kpc, W - sw - 1, kx0 + kb_w - 4)):  # posts stay inside the hood walls when closed
    post = box(xa, ym - 12, deck_z(ym) - 0.5, xb_, ym + 12, kb_top_m + 4)
    over = box(min(xa, xc), ym - 12, kb_top_m + 1.2, max(xb_, xc), ym + 12, kb_top_m + 4)
    clips.append(post.fuse(over))
add('keyboard_clips', clips, 'rubber', 'keyboard', 'tray', note='Hold the keyboard by its case edge so it cannot fall out when the lid is carried.')

# ---------------------------------------------------------------- states
def M_pos(x, y, z):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m
def M_rotx(deg, about=(0, 0, 0)):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    r = np.eye(4); r[1, 1], r[1, 2], r[2, 1], r[2, 2] = c, -s, s, c
    return M_pos(*about) @ r @ M_pos(*(-v for v in about))
def M_rotz(deg, about):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    r = np.eye(4); r[0, 0], r[0, 1], r[1, 0], r[1, 1] = c, -s, s, c
    return M_pos(*about) @ r @ M_pos(*(-v for v in about))

tray_operating = M_pos(0, -H - T['operating_gap'] - lip_y(fh), 2.2)
tray_closed = M_pos(0, -FT_, fh + H) @ M_rotx(-90)
latch_open = {k: M_rotx(90, pins[k]) for k in pins}
STATES = {
    'operating': {'tray': tray_operating, 'handle': np.eye(4), 'drawer': np.eye(4), 'latch_left': latch_open['left'], 'latch_right': latch_open['right']},
    'closed': {'tray': tray_closed, 'handle': M_rotx(90, (0, pivot_y, pz)), 'drawer': np.eye(4), 'latch_left': np.eye(4), 'latch_right': np.eye(4)},
    'rear': {'tray': tray_operating, 'handle': np.eye(4), 'drawer': M_pos(0, DW['pull_out'], 0), 'latch_left': latch_open['left'], 'latch_right': latch_open['right']},
}

def placed(name, state):
    p = parts[name]
    m = STATES[state].get(p['state'], np.eye(4)) if p['state'] else np.eye(4)
    if np.allclose(m, np.eye(4)):
        return p['shape']
    from OCP.gp import gp_Trsf
    from OCP.TopLoc import TopLoc_Location
    t = gp_Trsf(); t.SetValues(*[float(m[i, j]) for i in range(3) for j in range(4)])
    loc = b.Location(TopLoc_Location(t))
    return p['shape'].moved(loc)

# ---------------------------------------------------------------- validation
def vol_overlap(a, c):
    try:
        r = a.intersect(c)
        return 0.0 if r is None else float(r.volume)
    except Exception as e:  # pragma: no cover
        return float('nan')

def solids(name, state):
    return placed(name, state)

checks = []
def check(label, a_names, b_names, state, tol=1e-3):
    worst = 0.0
    for an in a_names:
        for bn in b_names:
            v = vol_overlap(solids(an, state), solids(bn, state))
            worst = max(worst, v)
    checks.append({'check': label, 'state': state, 'overlap_mm3': round(worst, 4), 'pass': worst <= tol})

def gap(label, a, c, state, need):
    d = solids(a, state).distance_to(solids(c, state))
    checks.append({'check': label, 'state': state, 'min_gap_mm': round(d, 2), 'required_mm': need, 'pass': d >= need - 1e-6})

front = ['shell', 'shield_frame', 'fascia', 'legend_plate', 'screen_shroud', 'drive_shroud']
inside = ['display', 'pi5_board', 'pi5_cooler', 'floppy_drives', 'drive_cage', 'usb_hub', 'floppy_controller', 'power_board', 'drawer_rails']
lid = ['lid_body', 'lid_deck', 'keyboard_body', 'keycaps', 'keycaps_mod', 'keycaps_accent', 'keyboard_clips', 'lid_feet']
check('Closed lid + keyboard do not collide with case/front', lid, front + ['latch_lever_left', 'latch_lever_right', 'latch_bases', 'side_stripes'], 'closed')
gap('Closed lid deck to slanted case lip', 'lid_deck', 'shell', 'closed', T['lip_gap'] - 0.05)
gap('Closed keycaps to fascia', 'keycaps', 'fascia', 'closed', 5)
gap('Closed keycaps to shield frame', 'keycaps', 'shield_frame', 'closed', 3)
check('Keyboard seated in lid (no overlap with body/deck/clips)', ['keyboard_body', 'keycaps', 'keycaps_mod', 'keycaps_accent'], ['lid_body', 'lid_deck', 'keyboard_clips'], 'operating')
check('Drawer closed vs internals/rear panel', ['drawer', 'diskettes'], inside + ['rear_panel', 'shell'], 'operating')
check('Drawer pulled out vs internals/rear panel', ['drawer', 'diskettes'], inside + ['rear_panel', 'shell'], 'rear')
gap('Cooler to drawer air gap', 'pi5_cooler', 'drawer', 'operating', 10)
check('Drives clear cage, shroud, internals', ['floppy_drives'], ['drive_cage', 'drive_shroud', 'fascia', 'usb_hub', 'floppy_controller', 'power_board', 'rear_panel', 'shell'], 'operating')
check('Display/Pi clear front and drives', ['display', 'pi5_board', 'pi5_cooler'], ['screen_shroud', 'drive_shroud', 'fascia', 'drive_cage', 'shell', 'floppy_drives'], 'operating')
check('Folded handle sits in tub', ['handle'], ['shell'], 'operating')
check('Raised handle clears shell', ['handle'], ['shell'], 'closed')
check('Hub/power/controller clear shell & cage', ['usb_hub', 'power_board', 'floppy_controller'], ['shell', 'drive_cage', 'rear_panel', 'drawer_rails'], 'operating')

def bbox_of(names, state):
    bb = b.Compound(children=[solids(n, state) for n in names]).bounding_box()
    return [round(bb.min.X, 1), round(bb.min.Y, 1), round(bb.min.Z, 1), round(bb.max.X, 1), round(bb.max.Y, 1), round(bb.max.Z, 1)]

all_names = list(parts)
case_names = [n for n in all_names if parts[n]['group'] != 'keyboard']
closed_bb = bbox_of([n for n in all_names if n not in ('handle',)], 'closed')
report = {
    'revision': Q['revision'],
    'dimensions_mm': {
        'case_W_H_D_excl_feet': [W, round(H, 1), D],
        'case_height_incl_feet': round(TOP, 1),
        'closed_W_H_D_incl_lid_feet_latches_excl_raised_handle': [round(closed_bb[3] - closed_bb[0], 1), round(closed_bb[5] - closed_bb[2], 1), round(closed_bb[4] - closed_bb[1], 1)],
        'keyboard_unit_W_D_H': [W, round(H, 1), round(bbox_of(lid, 'operating')[5], 1)],
        'operating_footprint_depth': round(D + H + T['operating_gap'] + lip_y(fh), 1),
        'lid_wedge_height_front_rear': [round(deck_z(0), 1), round(deck_z(H), 1)],
        'lid_deck_angle_deg': round(math.degrees(math.atan(deck_slope)), 1),
        'case_lip_y_top_bottom': [round(lip_y(TOP), 1), round(lip_y(fh), 1)],
        'hood_opening_W_H': [round(hood_w, 1), round(hood_h, 1)],
        'fascia_plane_y': fy, 'screen_glass_y': glass_y,
        'closed_keyboard_envelope_to_fascia_mm': round(fy - kb_reach, 2),  # full 46.8 mm spec height, not the illustrative keys
        'screen_active_window_x0_z0_x1_z1': [round(v, 2) for v in ACTIVE],
        'drive_slot_centres_x': [round(x + dw_x / 2, 2) for x in drive_x],
        'pi_cooler_back_y': round(pi_back, 2), 'drawer_front_y': dy0,
        'diskette_capacity_estimate': int((rp_y0 - 4 - dy0 - 2 * wt - 6) // (dk[2] + 0.2)),
    },
    'checks': checks,
    'all_pass': all(c['pass'] for c in checks),
}
(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
for c in checks:
    print(('PASS ' if c['pass'] else 'FAIL ') + c['check'], {k: v for k, v in c.items() if k not in ('check', 'pass')})

# ---------------------------------------------------------------- exports
pal = Q['palettes']['charcoal']
for state in ('operating', 'closed'):
    kids = []
    for n, p in parts.items():
        s = placed(n, state).copy() if hasattr(placed(n, state), 'copy') else placed(n, state)
        s.label = n; s.color = b.Color(pal.get(p['role'], '#888888'))
        kids.append(s)
    b.export_step(b.Compound(children=kids, label='retro_m_p2_' + state), str(OUT / f'p2_{state}.step'))

scene = {'parts': [], 'states': {}, 'palettes': Q['palettes'], 'active': ACTIVE, 'glass_y': glass_y, 'size': [W, D, TOP], 'dims': report['dimensions_mm']}
for n, p in parts.items():
    sh = p['shape']
    tris = []; verts = []
    for s in (sh.solids() if sh.solids() else [sh]):
        v, f = s.tessellate(0.08, 0.25)
        off = len(verts)
        verts += [(round(q.X, 3), round(q.Y, 3), round(q.Z, 3)) for q in v]
        tris += [(a + off, c + off, d + off) for a, c, d in f]
    scene['parts'].append({'name': n, 'role': p['role'], 'group': p['group'], 'state': p['state'], 'note': p['note'],
                           'v': [c for q in verts for c in q], 'f': [c for t in tris for c in t]})
for s, mm in STATES.items():
    scene['states'][s] = {k: [round(float(x), 6) for x in m.flatten()] for k, m in mm.items()}
(OUT / 'scene.json').write_text(json.dumps(scene, separators=(',', ':')))
print('report all_pass =', report['all_pass'])
print(json.dumps(report['dimensions_mm'], indent=1))
