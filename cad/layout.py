"""Executed envelope study, not fabrication CAD. All lengths are millimeters."""
from pathlib import Path
import json
import hashlib
import itertools
import build123d as b
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'parameters.json').read_text())
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
s, k, d, pi, cfg, c = [P[n] for n in ('display','keyboard','drive','pi','design','clearances')]
w = cfg['wall']; edge = w + cfg['edge_margin']; front = cfg['front_recess']
W = max(2*edge + s['width'] + cfg['screen_drive_gap'] + d['width'], k['width'] + 2*cfg['keyboard_margin'] + 2*cfg['carrier_wall'])
H = max(2*edge+s['height'], cfg['drive_bottom']+2*d['height']+cfg['drive_stack_gap']+edge, k['depth']+2*cfg['keyboard_margin']+2*cfg['carrier_wall'])
D = max(front + d['depth'] + c['rear_drive_cable'], front + s['depth'] + c['pi_screen_standoff'] + pi['board_thickness'] + max(pi['cooler_height'] + c['cooler_air_outward'], c['connector_height'])) + w
CW = k['width'] + 2*(cfg['keyboard_margin']+cfg['carrier_wall'])
CH = k['depth'] + 2*(cfg['keyboard_margin']+cfg['carrier_wall'])
CD = k['height'] + cfg['keyboard_margin'] + cfg['carrier_wall'] + cfg['carrier_front_gap']
parts = {}; meta = {}
def box(name, size, xyz, color, role='hardware', status='provisional'):
    shape = b.Pos(*xyz) * b.Box(*size, align=(b.Align.MIN,)*3)
    shape.label = name; shape.color = b.Color(color)
    parts[name] = shape
    meta[name] = dict(size=list(size), origin=list(xyz), color=color, role=role, status=status)
    return shape
box('case_envelope',(W,D,H),(0,0,0),'#bfbab0','envelope','design')
box('display_reference_envelope',(s['width'],s['depth'],s['height']),(edge,front,edge),'#555b60',status=s['status'])
ax = edge+s['active_offset_x']
az = edge+s['active_offset_z']
box('active_area_reference',(s['active_width'],0.2,s['active_height']),(ax,front-0.2,az),'#408caa','reference','manufacturer_reference')
box('touch_keepout',(s['active_width']+2*c['touch_edge_margin'],front-0.2,s['active_height']+2*c['touch_edge_margin']),(ax-c['touch_edge_margin'],0,az-c['touch_edge_margin']),'#7ac8dc','clearance')
dx = edge+s['width']+cfg['screen_drive_gap']
for i in range(2):
    z=cfg['drive_bottom']+i*(d['height']+cfg['drive_stack_gap'])
    box(f'drive_{i+1}_placeholder',(d['width'],d['depth'],d['height']),(dx,front,z),'#8a929d')
    box(f'drive_{i+1}_rear_cable',(d['width'],c['rear_drive_cable'],d['height']),(dx,front+d['depth'],z),'#e8ae57','clearance')
    box(f'drive_{i+1}_disk_access',(d['width'],c['drive_media_front'],d['height']),(dx,-c['drive_media_front'],z),'#e8ae57','operating_clearance')
# Map manufacturer rear-view screw coordinates into front landscape coordinates.
mount_axes=[]
for group in ('inner','outer'):
    coords=s['mounting_holes'][f'portrait_rear_{group}_uv']
    expected=s['mounting_holes'][f'landscape_{group}_pitch_xz']
    mapped=[(s['width']-v,u) for u,v in coords]
    assert np.allclose([max(v[i] for v in mapped)-min(v[i] for v in mapped) for i in (0,1)],expected)
    for i,(x,z) in enumerate(mapped,1):
        r=cfg['mount_axis_marker_radius']; length=cfg['mount_axis_marker_length']
        name=f'display_{group}_mount_axis_{i}'
        box(name,(2*r,length,2*r),(edge+x-r,front+s['depth'],edge+z-r),'#bd5aa0','reference','manufacturer_reference')
        mount_axes.append(dict(name=name,screen_local_x=x,screen_local_z=z,thread='M2.5',mount_plane_y=None))
# Mount the board parallel to the screen (X/Z plane), components facing rear (+Y).
# Center and spacing are explicitly provisional until the rear drawing is measured.
inner_axes=[m for m in mount_axes if '_inner_' in m['name']]
px = edge + np.mean([m['screen_local_x'] for m in inner_axes]) - pi['width']/2 + cfg['pi_screen_offset_x']
py = front + s['depth'] + c['pi_screen_standoff']
pz = edge + np.mean([m['screen_local_z'] for m in inner_axes]) - pi['depth']/2 + cfg['pi_screen_offset_z']
box('pi_board_nominal',(pi['width'],pi['board_thickness'],pi['depth']),(px,py,pz),'#4e8c65')
box('cooler_placeholder',(pi['cooler_width'],pi['cooler_height'],pi['cooler_depth']),(px+(pi['width']-pi['cooler_width'])/2,py+pi['board_thickness'],pz+(pi['depth']-pi['cooler_depth'])/2),'#a5aeb2')
box('cooler_air_keepout',(pi['cooler_width'],c['cooler_air_outward'],pi['cooler_depth']),(px+(pi['width']-pi['cooler_width'])/2,py+pi['board_thickness']+pi['cooler_height'],pz+(pi['depth']-pi['cooler_depth'])/2),'#7ac8dc','clearance')
box('pi_USB_Ethernet_exit',(c['connector_exit'],c['connector_height'],pi['depth']),(px+pi['width'],py,pz),'#e8ae57','clearance')
box('pi_power_HDMI_exit',(pi['width'],c['connector_height'],c['connector_exit']),(px,py,pz-c['connector_exit']),'#e8ae57','clearance')
box('display_cable_placeholder',(c['display_cable_width'],c['display_cable_depth'],c['display_cable_height']),(edge+c['display_cable_x_offset'],front+s['depth'],edge+c['display_cable_z_offset']),'#e8ae57','clearance')
box('keyboard_A_stock_envelope',(k['width'],k['height'],k['depth']),((W-k['width'])/2,-CD+cfg['carrier_wall'],(H-k['depth'])/2),'#d6d0c3','transport','provided')
box('carrier_A_envelope',(CW,CD,CH),((W-CW)/2,-CD,(H-CH)/2),'#537d9b','envelope','design')
box('keyboard_B_separate',(k['width'],k['depth'],k['height']),((W-k['width'])/2,-k['depth']-30,0),'#d6d0c3','separate','provided')

# Exact B-rep checks. Ignore envelope containment and semantic reference overlays.
physical=[n for n,m in meta.items() if m['role']=='hardware']
clearances=[n for n,m in meta.items() if m['role']=='clearance']
errors=[]; checks=[]
for name,shape in parts.items():
    assert shape.is_valid, name
    bb=shape.bounding_box(); actual=[bb.size.X,bb.size.Y,bb.size.Z]
    assert np.allclose(actual,meta[name]['size'],atol=1e-6), (name,actual)
    assert len(shape.solids())==1 and shape.volume>0, name
for a,z in itertools.combinations(physical,2):
    volume=(parts[a]&parts[z]).volume
    checks.append(dict(a=a,b=z,intersection_mm3=volume))
    if volume>1e-5: errors.append(f'{a} intersects {z}: {volume}')
for a in physical:
    for z in clearances:
        volume=(parts[a]&parts[z]).volume
        checks.append(dict(a=a,b=z,intersection_mm3=volume))
        if volume>1e-5: errors.append(f'{a} obstructs {z}: {volume}')
    xyz=meta[a]['origin']; size=meta[a]['size']
    assert all(xyz[i]>=w-1e-6 and xyz[i]+size[i]<=[W,D,H][i]-w+1e-6 for i in range(3)),a
# Carrier installed: check stock keyboard against the physical hardware.
for a in physical:
    volume=(parts[a]&parts['keyboard_A_stock_envelope']).volume
    checks.append(dict(a=a,b='keyboard_A_stock_envelope',intersection_mm3=volume))
    if volume>1e-5: errors.append(f'{a} intersects transported keyboard')
# Internal cable and cooler reservations must also remain inside the case.
for name in clearances:
    if name == 'touch_keepout': continue  # intentionally open through the front
    xyz=meta[name]['origin']; size=meta[name]['size']
    assert all(xyz[i]>=w-1e-6 and xyz[i]+size[i]<=[W,D,H][i]-w+1e-6 for i in range(3)),name
assert not errors, errors
# STEP parts are reference envelopes, not printable finished parts.
partdir=OUT/'step_parts'; partdir.mkdir(exist_ok=True)
for name,shape in parts.items(): b.export_step(shape,partdir/f'{name}.step')
base=[n for n,m in meta.items() if m['role'] not in ('transport','separate') and n!='carrier_A_envelope']
for option,extras in [('A',['keyboard_A_stock_envelope','carrier_A_envelope']),('B',['keyboard_B_separate'])]:
    assembly=b.Compound(label=f'Layout_{option}_REFERENCE_ONLY',children=[parts[n] for n in base+extras])
    b.export_step(assembly,OUT/f'layout_{option}.step')

assert cfg['keyboard_transport']=='A_front_carrier'
b.export_step(b.Compound(label='Selected_front_carrier_REFERENCE_ONLY',children=[parts[n] for n in base+['keyboard_A_stock_envelope','carrier_A_envelope']]),OUT/'layout_selected.step')
# Re-import current exports; geometry validity and component volumes must survive export.
for name in parts:
    restored=b.import_step(partdir/f'{name}.step')
    assert restored.is_valid and len(restored.solids())==1, name
    assert abs(restored.volume-parts[name].volume)<1e-4, name
roundtrip={}
for name,count in [('layout_A',len(base)+2),('layout_B',len(base)+1),('layout_selected',len(base)+2)]:
    restored=b.import_step(OUT/f'{name}.step')
    assert restored.is_valid and len(restored.solids())==count,name
    roundtrip[name]=count
(OUT/'step_roundtrip.json').write_text(json.dumps(dict(parameter_sha256=hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),individual_parts_valid=len(parts),assembly_solids=roundtrip),indent=2)+'\n')

# Previews use triangulations and edges from executed OpenCascade solids.
meshes={}
for name,shape in parts.items():
    vs,ts=shape.tessellate(0.1)
    points=np.array([[v.X,v.Y,v.Z] for v in vs]); meshes[name]=points[np.array(ts)]
def draw(ax, names, elev, azim, title, bounds=None):
    triangles=[]; colors=[]
    for n in names:
        m=meta[n]; shape=parts[n]
        if m['role']=='envelope':
            segments=[[[e.start_point().X,e.start_point().Y,e.start_point().Z],[e.end_point().X,e.end_point().Y,e.end_point().Z]] for e in shape.edges()]
            ax.add_collection3d(Line3DCollection(segments,colors=m['color'] if n!='case_envelope' else '#69635c',linewidths=0.9))
        else:
            alpha=0.12 if 'clearance' in m['role'] else 1.0
            triangles.extend(meshes[n]); colors.extend([to_rgba(m['color'],alpha)]*len(meshes[n]))
    ax.add_collection3d(Poly3DCollection(triangles,facecolors=colors,edgecolors='none',linewidths=0,zsort='average'))
    if bounds is None: bounds=((0,W),(0,D),(0,H))
    ax.set(xlim=bounds[0],ylim=bounds[1],zlim=bounds[2],xlabel='X width (mm)',ylabel='Y depth (mm)',zlabel='Z height (mm)')
    ax.set_box_aspect([v[1]-v[0] for v in bounds]); ax.view_init(elev,azim); ax.set_proj_type('ortho'); ax.set_title(title,fontsize=11)
    ax.tick_params(labelsize=7); ax.set_facecolor('#faf9f6')
    if elev==0 and azim==-90: ax.set_yticks([]); ax.set_ylabel('')
    if elev==0 and azim==0: ax.set_xticks([]); ax.set_xlabel('')
    if elev==90: ax.set_zticks([]); ax.set_zlabel('')
main=[n for n in base if meta[n]['role']!='operating_clearance']
views=[('front',0,-90),('right_side',0,0),('top',90,-90),('three_quarter',24,-62)]
fig=plt.figure(figsize=(15,10),facecolor='#faf9f6')
for i,(name,elev,azim) in enumerate(views):
    ax=fig.add_subplot(2,2,i+1,projection='3d');draw(ax,main,elev,azim,name.replace('_',' ').title())
fig.suptitle(f'PROVISIONAL LAYOUT — {W:.1f} W × {H:.1f} H × {D:.1f} D mm\n10.1-inch screen + mount axes: manufacturer reference • Pi position / drives / cables provisional',fontsize=14)
fig.text(.5,.025,'Wire outline: proposed case | Blue: active screen | Grey: drives | Green: Pi | Amber: cable space | Cyan: touch/air keepout\nOuter shell omitted for internal inspection. Rectangular envelopes are not detailed component models.',ha='center',fontsize=10)
fig.subplots_adjust(bottom=.10,top=.88,hspace=.16,wspace=.1);fig.savefig(OUT/'layout_views.png',dpi=150);plt.close(fig)
for name,elev,azim in views+[('rear_internal',24,62),('rear_mounts',0,90)]:
    fig=plt.figure(figsize=(10,7));ax=fig.add_subplot(projection='3d')
    selection=main if name!='rear_mounts' else ['display_reference_envelope']+[m['name'] for m in mount_axes]
    draw(ax,selection,elev,azim,f'{name.replace("_"," ").title()} — reference geometry, mm')
    if name=='rear_mounts':
        ax.set_yticks([]); ax.set_ylabel('')
        for m in mount_axes:
            ax.text(edge+m['screen_local_x'],front+s['depth']+cfg['mount_axis_marker_length'],edge+m['screen_local_z']+5,m['name'].replace('display_','').replace('_mount_axis_',' '),fontsize=8)

    fig.savefig(OUT/f'{name}.png',dpi=150);plt.close(fig)
fig=plt.figure(figsize=(15,7),facecolor='#faf9f6')
for i,option in enumerate(['A','B']):
    ax=fig.add_subplot(1,2,i+1,projection='3d')
    extras=['keyboard_A_stock_envelope','carrier_A_envelope'] if option=='A' else ['keyboard_B_separate']
    draw(ax,main+extras,24,-62,f'{option}: '+('SELECTED front carrier; remove before use' if option=='A' else 'Keyboard separate; shown in use'),((0,W),(-k['depth']-30,D),(0,H)))
fig.suptitle(f'Keyboard transport comparison — A: {W:.1f} × {D+CD:.1f} × {H:.1f} mm overall\nB: case {W:.1f} × {D:.1f} × {H:.1f} + stock keyboard 376.6 × 169.6 × 46.8 mm',fontsize=13)
fig.text(.5,.025,'Keyboard box includes keycaps/knobs. No contact or latch geometry designed. Front carrier selected. Housing contacts and mounting details remain unverified.',ha='center')
fig.subplots_adjust(top=.85,bottom=.09);fig.savefig(OUT/'keyboard_comparison.png',dpi=150);plt.close(fig)
report=dict(units='mm',parameter_sha256=hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),case_WHD=[W,H,D],carrier_WHD=[CW,CH,CD],option_A_WHD=[W,H,D+CD],valid_solids=len(parts),collision_checks=checks,unwanted_envelope_interferences=errors,parts=meta,intentional_contacts=['Cooler front on rear-facing board component plane','Cable zones touch associated envelope faces','Outer and carrier envelopes contain reference solids','Touch and air regions are spatial reservations'],unverified=['Pi drawing and mounting alignment','All actual connector bodies and cable bend radii','Display mount-plane depth, thread engagement and physical dimensions (brief is approximate)','Drive and cooler models','Finished part printer fit; nominal A1 and A1 mini volumes recorded, seams not designed','Thermal design, handle loads, keyboard housing contact','Battery/power conversion allocation'],printable_parts=0)
report['display_mount_axes']=mount_axes
report['selected_transport']=cfg['keyboard_transport']
report['pi_rear_stack_depth']=c['pi_screen_standoff']+pi['board_thickness']+pi['cooler_height']+c['cooler_air_outward']
report['printer_envelope_fit']={name: {'case_single_piece_axis_aligned': all(a<=b for a,b in zip(sorted([W,D,H]),sorted(v))), 'note': 'Layout envelope only; part subdivision required, no printable parts yet'} for name,v in P['manufacturing']['build_volumes'].items()}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['case_WHD','option_A_WHD','valid_solids','unwanted_envelope_interferences','printable_parts']},indent=2))
