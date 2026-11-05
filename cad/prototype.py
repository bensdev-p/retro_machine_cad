"""P1 printable enclosure prototype. Geometry is executable; hardware assumptions are not measurements."""
from pathlib import Path
import json, math, hashlib, itertools, time
import build123d as b
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'parameters.json').read_text()); Q=P['prototype']; C=Q['case']; F=Q['fasteners']; S=P['display']; D=Q['drive']; K=P['keyboard']; J=Q['joints']; PAL=Q['palette']
OUT=ROOT/'outputs/prototype'; PART=OUT/'parts'; PART.mkdir(parents=True,exist_ok=True)
W,H,DEP,T=C['width'],C['height'],C['depth'],C['wall']; split=C['split_x']; gap=F['fit_clearance']; fy=C['fascia_y']; FT=C['fascia_thickness']
parts={};info={};references={};refmeta={}; hardware_mounts=[]
def box(x,y,z,dx,dy,dz):return b.Pos(x,y,z)*b.Box(dx,dy,dz,align=(b.Align.MIN,)*3)
def cornered(x,y,z,dx,dy,dz,axis='z'):
 sh=box(x,y,z,dx,dy,dz)
 return b.chamfer(sh.edges().filter_by({'x':b.Axis.X,'y':b.Axis.Y,'z':b.Axis.Z}[axis]),length=C['corner_chamfer'])
def rod(x,y,z,r,length,axis='z'):
 sh=b.Cylinder(r,length,align=(b.Align.CENTER,b.Align.CENTER,b.Align.MIN))
 if axis=='y':sh=b.Rot(X=-90)*sh
 if axis=='x':sh=b.Rot(Y=90)*sh
 return b.Pos(x,y,z)*sh
def hexcut(x,y,z,af,length,axis='z'):
 sh=b.extrude(b.RegularPolygon(af/2,6,major_radius=False,rotation=30),amount=length)
 if axis=='y':sh=b.Rot(X=-90)*sh
 if axis=='x':sh=b.Rot(Y=90)*sh
 return b.Pos(x,y,z)*sh
def cut(sh,tools):return sh.cut(*tools) if tools else sh
def union(*sh):return sh[0].fuse(*sh[1:])
def through(sh,x,y,z,length,axis='z',size='M3'):
 return sh-rod(x,y,z,F[size]['clearance']/2,length,axis)
def save(name,shape,color='shell',orient='z',group='case',note=''):
 assert shape.is_valid,(name,'invalid')
 assert len(shape.solids())==1,(name,'disconnected',len(shape.solids()))
 assert shape.volume>1,name
 shape.label=name;shape.color=b.Color(PAL.get(color,color));parts[name]=shape
 info[name]={'color':PAL.get(color,color),'print_normal':orient,'group':group,'note':note,'volume_mm3':shape.volume}
 return shape
def ref(name,shape,color,role='hardware',note=''):
 shape.label=name;shape.color=b.Color(PAL.get(color,color));references[name]=shape
 refmeta[name]={'color':PAL.get(color,color),'role':role,'note':note}
def screw_holes_y(sh,x,zs,y0,length,size='M3'):
 return cut(sh,[rod(x,y0,z,F[size]['clearance']/2,length,'y') for z in zs])
def nut_y(x,y,z,size='M3',depth=None):return hexcut(x,y,z,F[size]['pocket_af'],depth or F[size]['pocket_depth'],'y')
def nut_z(x,y,z,size='M3',depth=None):return hexcut(x,y,z,F[size]['pocket_af'],depth or F[size]['pocket_depth'])
# Side shells have integrated rails for top, bottom, fascia and rear fasteners.
for side in ('left','right'):
 x=0 if side=='left' else W-T; rx=T if side=='left' else W-T-J['side_rail_width']; hx=rx+J['side_rail_width']/2
 sh=union(cornered(x,0,0,T,DEP,H,'x'),box(rx,fy+FT,T,10,DEP-T-fy-FT,10),box(rx,fy+FT,H-T-10,10,DEP-T-fy-FT,10),box(rx,fy+FT,T,10,10,H-2*T),box(rx,DEP-T-10,T,10,10,H-2*T))
 tools=[]
 for y in J['side_top_base_y']:
  tools += [rod(hx,y,-1,F['M3']['clearance']/2,H+2),nut_z(hx,y,9,depth=6),nut_z(hx,y,H-T-10-1,depth=6)]
 # Clearance notch for continuous metal handle backing bar.
 hy=Q['handle']['center_y']; hw=Q['handle']['backing_width_y']; ht=Q['handle']['backing_thickness']
 tools.append(box(rx-.1,hy-hw/2,H-T-ht,10.2,hw,ht+.1))
 for z in J['fascia_screw_z']:
  tools += [rod(hx,fy-1,z,F['M3']['clearance']/2,16,'y'),nut_y(hx,fy+FT+5,z,depth=6)]
 for z in J['carrier_screw_z']:
  tools += [rod(hx,fy-1,z,F['M4']['clearance']/2,16,'y'),nut_y(hx,fy+FT+5,z,'M4',depth=6)]
 for z in J['rear_screw_z']:
  tools += [rod(hx,DEP-T-11,z,F['M3']['clearance']/2,16,'y'),nut_y(hx,DEP-T-11,z,depth=6)]
 # Vent slots outside structural rails.
 if side=='left':
  for z in range(48,157,12):tools.append(box(x-1,85,z,T+2,95,4))
 else:
  for z in (151,163,175):tools.append(box(x-1,45,z,T+2,135,4))
 sh=cut(sh,tools)
 save(f'side_{side}',sh,orient='x',note='Print outer broad face on bed; short vent bridges. Integrated nut pockets open to assembly interior.')
# Screen bracket mounting positions from supplied display drawing.
sx,sz,sy=[Q['screen'][n] for n in ('x','z','front_y')]
outer=[(sx+S['width']-v,sz+u) for u,v in S['mounting_holes']['portrait_rear_outer_uv']]
rail_x=sorted(set(round(x,6) for x,z in outer)); rail_y=sy+S['depth']+Q['screen']['support_y_gap']; sw=Q['screen']['support_width']; st=Q['screen']['support_thickness']; fd=Q['screen']['foot_depth']
screen_base_holes=[(x,rail_y+fd-6) for x in rail_x]
# Drive cage coordinates, with 1 mm side/bottom housing allowances.
cx=D['x']-D['side_clearance']-D['cage_wall']; cw=D['width']+2*(D['side_clearance']+D['cage_wall']); cy=D['cage_front_y']; cd=D['cage_depth']; cm=cx+cw/2
cage_mounts=[(cx+14,cy+12),(cx+cw-14,cy+12),(cx+14,cy+cd-12),(cx+cw-14,cy+cd-12)]
hub_mounts=[(34,162),(178,162),(34,200),(178,200)]
# Main top/base plates split down the center, joined by screwed internal seam strips.
for face,z0 in [('base',0),('top',H-T)]:
 for side,x0,x1 in [('left',T,split-gap/2),('right',split+gap/2,W-T)]:
  sh=cornered(x0,0,z0,x1-x0,DEP-T,T);tools=[]
  hx=9 if side=='left' else W-9
  for y in J['side_top_base_y']:tools.append(rod(hx,y,z0-1,F['M3']['clearance']/2,T+2))
  for lo,hi in J['horizontal_seam_segments']:
   for xx in J['seam_bolt_x']:
    for yy in (lo+10,hi-10):tools.append(rod(xx,yy,z0-1,F['M3']['clearance']/2,T+2))
  for yy in J['alignment_y']:tools.append(rod(split-J['alignment_hole_length']/2,yy,z0+T/2,J['alignment_hole_diameter']/2,J['alignment_hole_length'],'x'))
  for xx,yy in screen_base_holes:tools.append(rod(xx,yy,z0-1,F['M3']['clearance']/2,T+2))
  if face=='base':
   for xx,yy in cage_mounts+hub_mounts:tools.append(rod(xx,yy,z0-1,F['M3']['clearance']/2,T+2))
  else:
   for xx in Q['handle']['anchor_x']:
    for yy in Q['handle']['bolt_y']:tools.append(rod(xx,yy,z0-1,F['M4']['clearance']/2,T+2))
  save(f'{face}_{side}',cut(sh,tools),orient='z',note='Flat face on bed. Exposed screw heads underneath base require rubber feet.')
 for i,(lo,hi) in enumerate(J['horizontal_seam_segments']):
  zz=T if face=='base' else H-T-J['seam_thickness']
  sh=box(split-J['seam_width']/2,lo,zz,J['seam_width'],hi-lo,J['seam_thickness']);tools=[]
  for xx in J['seam_bolt_x']:
   for yy in (lo+10,hi-10):
    tools.append(rod(xx,yy,zz-1,F['M3']['clearance']/2,6))
    tools.append(nut_z(xx,yy,zz+1.2 if face=='base' else zz-.1,depth=2.9))
  save(f'{face}_seam_{i+1}',cut(sh,tools),orient='z',note='M3x8 screws, captive M3 nuts; install before closing top.')
# Recessed fascia, screen aperture and two generous drive-face openings.
aw=S['active_width']+2*P['clearances']['touch_edge_margin']; ah=S['active_height']+2*P['clearances']['touch_edge_margin']; ax=sx+S['active_offset_x']-P['clearances']['touch_edge_margin']; az=sz+S['active_offset_z']-P['clearances']['touch_edge_margin']
fascia=cornered(T,fy,T,W-2*T,FT,H-2*T,'y')-box(ax,fy-1,az,aw,FT+2,ah)
for dz in D['bottom_z']:
 cl=D['opening_clearance'];fascia-=box(D['x']-cl,fy-1,dz-cl,D['width']+2*cl,FT+2,D['height']+2*cl)
for x in (9,W-9):
 fascia=screw_holes_y(fascia,x,J['fascia_screw_z'],fy-1,FT+2)
 fascia=screw_holes_y(fascia,x,J['carrier_screw_z'],fy-1,FT+2,'M4')
# Bolt the fascia seam only above/below the screen opening.
for x in J['seam_bolt_x']:
 for z in (10,190):fascia-=rod(x,fy-1,z,F['M3']['clearance']/2,FT+2,'y')
for side,x0,x1 in [('left',T,split-gap/2),('right',split+gap/2,W-T)]:save('fascia_'+side,fascia & box(x0,fy-1,0,x1-x0,FT+2,H),'fascia','y',note='Screen opening leaves 5 mm finger allowance beyond active area. Gasket supports glass; do not clamp active area.')
for i,z0 in enumerate((5,185)):
 sh=box(split-9,fy+FT,z0,18,4,10);tools=[]
 for x in J['seam_bolt_x']:tools += [rod(x,fy+FT-1,z0+5,F['M3']['clearance']/2,6,'y'),nut_y(x,fy+FT+1.2,z0+5,depth=3)]
 save('fascia_seam_'+str(i+1),cut(sh,tools),'fascia','y')
# Outer front rim. Four removable carrier knobs also clamp this rim.
rim=cornered(T,0,T,W-2*T,4,H-2*T,'y')-box(T+10,-1,T+10,W-2*T-20,6,H-2*T-20)
for x in (9,W-9):rim=screw_holes_y(rim,x,J['carrier_screw_z'],-1,6,'M4')
for side,x0,x1 in [('left',T,split-gap/2),('right',split+gap/2,W-T)]:save('front_rim_'+side,rim & box(x0,-1,0,x1-x0,6,H),'shell','y',note='Carrier M4 knobs retain rim; use short M4 screws/spacers when operating without carrier.')
# Rim spacers bridge the recess so carrier knobs cannot pull the rim into the fascia gap.
for side,xx in [('left',9),('right',W-9)]:
 for zz in J['carrier_screw_z']:
  sh=rod(xx,4,zz,J['rim_spacer_od']/2,J['rim_spacer_length'],'y')-rod(xx,3,zz,F['M4']['clearance']/2,J['rim_spacer_length']+2,'y')
  save(f'rim_spacer_{side}_{zz}',sh,'shell','y',note='M4 spacer between front rim and fascia. Required with carrier knobs or short operating screws.')
# Vertical screen support rails; four holes follow the manufacturer reference pattern.
for i,x in enumerate(rail_x):
 sh=union(box(x-sw/2,rail_y,T,sw,st,H-2*T),box(x-sw/2,rail_y,T,sw,fd,4),box(x-sw/2,rail_y,H-T-4,sw,fd,4));tools=[]
 for xx,zz in outer:
  if abs(xx-x)<.01:
   r=Q['screen']['mount_clearance_diameter']/2; travel=Q['screen']['mount_slot_travel']
   tools += [rod(x,rail_y-1,zz-travel/2,r,st+2,'y'),rod(x,rail_y-1,zz+travel/2,r,st+2,'y'),box(x-r,rail_y-1,zz-travel/2,2*r,st+2,travel)]
   hardware_mounts.append({'part':'screen_support_'+str(i+1),'axis':'y','x':x,'z':zz,'type':'M2.5 display mounting reference; spacer and screw engagement TBD'})
 yy=rail_y+fd-6
 for zz in (T,H-T-4):
  tools += [rod(x,yy,zz-1,F['M3']['clearance']/2,6),nut_z(x,yy,zz+1.2 if zz==T else zz-.1,depth=2.9)]
 save('screen_support_'+str(i+1),cut(sh,tools),'shell','y',note='M2.5 mounting pattern from display brief; validate stand-off height and screw engagement with screen-corner coupon.')
# Removable two-drive cage. Two side halves avoid a large unsupported shelf bridge.
cage=union(box(cx,cy,T,cw,cd,D['cage_base_height']),box(cx,cy,T,D['cage_wall'],cd,D['cage_top_z']-T),box(cx+cw-D['cage_wall'],cy,T,D['cage_wall'],cd,D['cage_top_z']-T))
for dz in D['bottom_z']:cage=union(cage,box(cx,cy,dz-D['shelf_gap']-D['shelf_thickness'],cw,cd,D['shelf_thickness']))
tools=[]
for xx,yy in cage_mounts:
 tools += [rod(xx,yy,T-1,F['M3']['clearance']/2,D['cage_base_height']+2),nut_z(xx,yy,T+D['cage_base_height']-F['M3']['pocket_depth'],depth=F['M3']['pocket_depth']+.1)]
# Slotted shelves accept 20 mm padded straps around the original drive housings.
for dz in D['bottom_z']:
 zz=dz-D['shelf_gap']-D['shelf_thickness']
 for xx in (D['x']+3,D['x']+D['width']-6):tools.append(box(xx,D['strap_y']-11,zz-1,3,22,5))
 for xx in (cm-5,cm+5):
  for yy in (70,120):
   tools.append(rod(xx,yy,zz-1,F['M3']['clearance']/2,5))
   tools.append(b.Pos(xx,yy,zz+D['shelf_thickness']-1.7)*b.Cone(1.7,3.4,1.7,align=(b.Align.CENTER,b.Align.CENTER,b.Align.MIN)))
for xx in (cm-5,cm+5):
 for yy in (70,120):tools += [rod(xx,yy,T-1,F['M3']['clearance']/2,8),nut_z(xx,yy,T-.1,depth=2.9)]
cage=cut(cage,tools)
for side,x0,x1 in [('left',cx,cm-gap/2),('right',cm+gap/2,cx+cw)]:save('drive_cage_'+side,cage & box(x0,cy-1,0,x1-x0,cd+2,D['cage_top_z']+1),'shell','x',group='internal',note='Print broad outside wall on bed. Join half shelves with M3 countersunk screws. Padded webbing retains drive housings; ports remain accessible from rear.')
for i,zz in enumerate([T+D['cage_base_height']]+[z-D['shelf_gap']-D['shelf_thickness']-4 for z in D['bottom_z']]):
 sh=box(cm-9,50,zz,18,88,4);tools=[]
 for xx in (cm-5,cm+5):
  for yy in (70,120):
   tools.append(rod(xx,yy,zz-1,F['M3']['clearance']/2,6))
   if i>0:tools.append(nut_z(xx,yy,zz-.1,depth=2.9))
 save('drive_cage_join_'+str(i),cut(sh,tools),'shell','z',group='internal')
# Adjustable hub cradle and replaceable rear connector plate.
hc=union(box(28,152,T,156,56,4),box(28,152,8,4,56,32),box(180,152,8,4,56,32))
for xx,yy in hub_mounts:hc=cut(hc,[rod(xx,yy,T-1,F['M3']['clearance']/2,6),nut_z(xx,yy,T+1.2,depth=2.9)])
for xx in (42,166):hc-=box(xx,176,T-1,3,22,6)
save('hub_cradle',hc,'shell','z',group='internal',note='Adjustable foam and 20 mm strap retention; hub envelope is not a selected commercial model.')
rear=cornered(T,DEP-T,T,W-2*T,T,H-2*T,'y')-box(32,DEP-T-1,8,144,T+2,46)
for x in (9,W-9):rear=screw_holes_y(rear,x,J['rear_screw_z'],DEP-T-1,T+2)
for x in J['seam_bolt_x']:
 for z in (30,100,170):rear-=rod(x,DEP-T-1,z,F['M3']['clearance']/2,T+2,'y')
for x in (28,180):
 for z in (10,56):rear-=rod(x,DEP-T-1,z,F['M3']['clearance']/2,T+2,'y')
for z in range(96,181,12):rear-=box(24,DEP-T-1,z,146,T+2,4)
for z in (150,162,174):rear-=box(240,DEP-T-1,z,136,T+2,4)
for xx in (228,252):rear-=rod(xx,DEP-T-1,28,F['M3']['clearance']/2,T+2,'y')
rear-=rod(Q['io']['power_pass_x'],DEP-T-1,Q['io']['power_pass_z'],Q['io']['power_pass_diameter']/2,T+2,'y')
for side,x0,x1 in [('left',T,split-gap/2),('right',split+gap/2,W-T)]:save('rear_'+side,rear & box(x0,DEP-T-1,0,x1-x0,T+2,H),'shell','y',note='Remove rear panels for drive/hub servicing. Power opening requires a suitable grommet and separate strain relief.')
rj=box(split-9,DEP-T-4,20,18,4,160);tools=[]
for x in J['seam_bolt_x']:
 for z in (30,100,170):tools += [rod(x,DEP-T-5,z,F['M3']['clearance']/2,6,'y'),nut_y(x,DEP-T-4-.1,z,depth=2.9)]
save('rear_seam',cut(rj,tools),'shell','y')
io=box(24,DEP-T-4,4,160,4,58)-box(36,DEP-T-5,12,136,6,30)
for x in (28,180):
 for z in (10,56):io=cut(io,[rod(x,DEP-T-5,z,F['M3']['clearance']/2,6,'y'),nut_y(x,DEP-T-4-.1,z,depth=2.9)])
save('rear_hub_plate',io,'fascia','y',note='Generic opening for hub face/cables. Replace this part to suit the eventual hub; no proprietary connector geometry assumed.')
# Rear cable-tie saddle, separate from the removable hub faceplate.
relief=box(224,DEP-T-4,18,32,4,20)-rod(240,DEP-T-5,28,6,6,'y')
for xx in (228,252):relief=cut(relief,[rod(xx,DEP-T-5,28,F['M3']['clearance']/2,6,'y'),nut_y(xx,DEP-T-4-.1,28,depth=2.9)])
for xx in (235,241):relief-=box(xx,DEP-T-5,19,4,6,2)
save('power_strain_relief',relief,'fascia','y',note='Use rubber grommet plus cable tie through saddle slots. Validate grip on chosen power cable, never clamp bare conductors.')
# Bolted webbing handle clamps. Load spreads into an aluminium bar, then the side rails.
h=Q['handle'];by=h['center_y']-h['backing_width_y']/2; bz=H-T-h['backing_thickness']
metal=box(T,by,bz,W-2*T,h['backing_width_y'],h['backing_thickness']);tools=[]
for xx in (9,W-9):tools.append(rod(xx,h['center_y'],bz-1,F['M3']['clearance']/2,6))
for xx in h['anchor_x']:
 for yy in h['bolt_y']:tools.append(rod(xx,yy,bz-1,F['M4']['clearance']/2,6))
metal=cut(metal,tools);ref('handle_backing_ALUMINIUM_NOT_PRINTED',metal,'metal','fabricated','392 × 60 × 4 mm aluminium bar, drilled. Do not substitute untested printed plastic for transport loads.')
b.export_step(metal,OUT/'handle_backing_aluminium.step')
for i,xx in enumerate(h['anchor_x']):
 sh=box(xx-h['clamp_x']/2,h['center_y']-h['clamp_y']/2,H,h['clamp_x'],h['clamp_y'],h['clamp_height'])
 sh-=box(xx-h['clamp_x']/2-1,h['center_y']-h['webbing_width']/2,H-.1,h['clamp_x']+2,h['webbing_width'],h['channel_depth']+.1)
 for yy in h['bolt_y']:sh-=rod(xx,yy,H-1,F['M4']['clearance']/2,h['clamp_height']+2)
 save('handle_clamp_'+str(i+1),sh,'accent','z',note='M4x25 through bolts, washers and locknuts; webbing must be positively secured/sewn, not held by friction alone. Proof-load before carrying.')
# Positive strap end stops: sewn returns around purchased 6 mm steel crosspins.
for i,xx in enumerate(h['end_stop_pin_x']):
 ref('handle_end_stop_pin_'+str(i+1),rod(xx,h['center_y']-h['end_stop_pin_length']/2,h['end_stop_pin_z'],h['end_stop_pin_diameter']/2,h['end_stop_pin_length'],'y'),'metal','fabricated','Purchased steel pin in sewn webbing loop; do not print this load-bearing pin.')
 loop=rod(xx,h['center_y']-h['webbing_width']/2,h['end_stop_pin_z'],h['end_stop_pin_diameter']/2+h['webbing_thickness'],h['webbing_width'],'y')-rod(xx,h['center_y']-h['webbing_width']/2-1,h['end_stop_pin_z'],h['end_stop_pin_diameter']/2,h['webbing_width']+2,'y')
 ref('handle_sewn_return_'+str(i+1),loop,'rubber','flexible')
# Carrier: stock keyboard underside faces the computer; keys face the protective cover.
ca=Q['carrier']; ox,oz,ow,oh,ct=ca['x'],ca['z'],ca['width'],ca['height'],ca['wall']; front=-ca['depth']
carrier=union(cornered(ox,front,oz,ow,ct,oh,'y'),box(ox,front+ct,oz,ct,-2-(front+ct),oh),box(ox+ow-ct,front+ct,oz,ct,-2-(front+ct),oh),box(ox,front+ct,oz,ow,-2-(front+ct),ct),box(ox,front+ct,oz+oh-ct,ow,-2-(front+ct),ct))
for xx in (9,W-9):
 for zz in J['carrier_screw_z']:
  carrier=union(carrier,box(xx-7,-4,zz-8,14,4,16))
  carrier-=rod(xx,-5,zz,F['M4']['clearance']/2,6,'y')
for xx in (ox,ox+ow-ct):
 for zz in ca['strap_centers_z']:carrier-=box(xx-1,ca['keyboard_back_y']-1,zz-ca['strap_width']/2,ct+2,ca['strap_slot_depth'],ca['strap_width'])
for xx in J['seam_bolt_x']:
 for zz in (30,60,140,170):carrier-=rod(xx,front-1,zz,F['M3']['clearance']/2,ct+2,'y')
# Blue inlays in shallow pockets on carrier exterior.
carrier-=box(ox+14,front-.1,oz+18,ow-28,1.1,4)
for side,x0,x1 in [('left',ox,split-gap/2),('right',split+gap/2,ox+ow)]:
 save('carrier_'+side,carrier & box(x0-3 if side=='left' else x0,front-1,0,(x1-x0)+3,ca['depth']+2,H),'shell','y',group='carrier',note='Protective face on bed. Add edge foam and two padded straps against keyboard underside. No load may touch keys/knobs; verify with retention coupon.')
for i,(za,zb) in enumerate(((20,70),(130,180))):
 sh=box(split-9,front+ct,za,18,4,zb-za);tools=[]
 for xx in J['seam_bolt_x']:
  for zz in (za+10,zb-10):tools += [rod(xx,front+ct-1,zz,F['M3']['clearance']/2,6,'y'),nut_y(xx,front+ct+1.2,zz,depth=2.9)]
 save('carrier_seam_'+str(i+1),cut(sh,tools),'shell','y',group='carrier')
for side,x0,x1 in [('left',ox+14,split-.2),('right',split+.2,ox+ow-14)]:save('carrier_blue_inlay_'+side,box(x0+.1,front,oz+18.15,x1-x0-.2,.85,3.7),'accent','y',group='carrier',note='Decorative inlay: light adhesive permitted; not a service or structural joint.')
# Small mating coupon from actual base seam and alignment-pin bore.
for side,xx in [('left',split-16),('right',split)]:
 sample=parts['base_'+side] & box(xx,90,-1,16,20,6)
 save('TEST_alignment_'+side,sample,'shell','z',group='test',note='Fit a purchased 2 mm x 8 mm steel pin; intended seam gap 0.25 mm. Adjust hole clearance after printing.')
# Test coupons share actual geometry and fit parameters.
sample=parts['screen_support_1'] & box(rail_x[0]-sw/2-1,rail_y-1,outer[2][1]-10,sw+2,fd+2,20)
# Find the lower left support hole deterministically.
ztest=min(z for x,z in outer if abs(x-rail_x[0])<.01)
sample=parts['screen_support_1'] & box(rail_x[0]-sw/2-1,rail_y-1,ztest-10,sw+2,fd+2,20)
save('TEST_screen_mount',sample,'shell','y',group='test',note='Test actual display screw, spacers and contact plane before full supports.')
sample=fascia & box(sx,fy-1,10,60,FT+2,45)
save('TEST_screen_corner',sample,'fascia','y',group='test',note='Check screen glass border, active-area exposure, gasket and finger clearance at the lower-left opening corner.')
dz=D['bottom_z'][0];sample=fascia & box(D['x']-6,fy-1,dz-5,D['width']+12,FT+2,D['height']+10)
save('TEST_drive_face',sample,'fascia','y',group='test',note='Test actual bezel insertion, disk motion, eject button, finger access and LED visibility.')
sample=parts['carrier_left'] & box(ox,front,25,24,ca['depth']+1,32)
save('TEST_keyboard_retention',sample,'shell','y',group='test',note='Check stock housing, strap route and keycap/knob clearance with foam; geometry is provisional.')
fit=box(0,0,0,70,32,8);tools=[]
for size,xx in [('M3',15),('M4',45)]:
 tools += [rod(xx,16,-1,F[size]['clearance']/2,10),nut_z(xx,16,8-F[size]['pocket_depth'],size,depth=F[size]['pocket_depth']+.1)]
fit=cut(fit,tools)
save('TEST_fasteners',fit,'shell','z',group='test',note='Use actual M3/M4 nuts and bolts; adjust central pocket/clearance dimensions if needed. No heat-set inserts used.')
# Reference hardware: envelopes and visual features are NOT printable replacement components.
ref('screen_hardware',box(sx,sy,sz,S['width'],S['depth'],S['height']),'fascia')
ref('screen_active_image',box(sx+S['active_offset_x'],sy-.12,sz+S['active_offset_z'],S['active_width'],.12,S['active_height']),'#284c63','visual')
inner=[(sx+S['width']-v,sz+u) for u,v in S['mounting_holes']['portrait_rear_inner_uv']]
px=min(x for x,z in inner)-3.5;pz=min(z for x,z in inner)-3.5;py=sy+S['depth']+Q['cooler']['screen_gap']
ref('pi5_nominal',box(px,py,pz,85,1.6,56),'#387a4e',note='Nominal board/edge offsets, not verified Pi 5 drawing. Actual connector shapes missing.')
co=Q['cooler'];ref('active_cooler_allowance',box(px+12.5,py+1.6,pz+5.5,co['width'],co['height'],co['depth']),'metal')
for i,dz in enumerate(D['bottom_z']):
 ref('floppy_'+str(i+1),box(D['x'],D['front_y'],dz,D['width'],D['depth'],D['height']),'#969b9c',note='TEAC-class envelope; exact model/suffix unverified')
 ref('floppy_bezel_'+str(i+1),box(D['x'],D['front_y']-.5,dz,D['width'],.5,D['height']),'#aeb0ad','visual')
 ref('floppy_slot_'+str(i+1),box(D['x']+6,D['front_y']-.65,dz+13,D['width']-12,.15,4),'rubber','visual')
 ref('floppy_eject_'+str(i+1),box(D['x']+D['width']-17,D['front_y']-1.5,dz+3,12,1,6),'accent','visual')
 ref('floppy_led_'+str(i+1),box(D['x']+6,D['front_y']-.7,dz+4,3,.2,1.6),'#7ca06a','visual')
 for yy in (D['strap_y'],):
  ref('drive_strap_'+str(i+1),box(D['x'],yy-10,dz+D['height'],D['width'],20,1),'rubber','flexible')
for i,yy in enumerate((45,105)):ref('USB_floppy_controller_'+str(i+1),box(292,yy,18,76,42,12),'#397151',note='Unselected USB controller allowance; retained with foam/straps, not fixed-hole mounts')
hu=Q['hub'];ref('powered_hub_allowance',box(hu['x'],hu['y'],hu['z'],hu['width'],hu['depth'],hu['height']),'rubber')
kx=(W-K['width'])/2;kz=ca['keyboard_bottom_z']; ky=ca['keyboard_back_y']-K['height']
ref('keyboard_transport_envelope',box(kx,ky,kz,K['width'],K['height'],K['depth']),'shell','transport','Envelope includes knobs/keycaps. Rear straps contact underside, but peripheral housing support must be physically checked.')
for zz in ca['strap_centers_z']:ref('keyboard_rear_strap_'+str(zz),box(ox+ct,ca['keyboard_back_y'],zz-10,ow-2*ct,1,20),'rubber','transport_visual')
# Curved webbing visual, segmented reference mesh only.
path=[(104,201.5),(136,201.5),(153,219),(180,231),(200,234),(220,231),(247,219),(264,201.5),(296,201.5)]
for i,((xa,za),(xb,zb)) in enumerate(zip(path,path[1:])):
 length=math.hypot(xb-xa,zb-za); ang=-math.degrees(math.atan2(zb-za,xb-xa))
 shape=b.Pos((xa+xb)/2,110,(za+zb)/2)*b.Rot(Y=ang)*b.Box(length+1,25,3)
 ref('webbing_'+str(i),shape,'rubber','flexible')
# Operating keyboard model: visualization of stock keyboard, not reverse-engineered housing.
kb_y=-202;body_z=4
ref('keyboard_operating_body',box(kx,kb_y,body_z,K['width'],K['depth'],21),'shell','operating_visual')
# Six rows, with approximate TKL grouping and M Edition color cues.
for row in range(6):
 for col in range(15):
  if row==0 and col in (4,5,6,7,8):continue
  xx=kx+12+col*19;yy=kb_y+10+row*21
  color='modifier_keys' if row in (0,5) or col in (0,14) else 'keys'
  if (row,col) in ((5,0),(2,14)):color='accent'
  ref(f'key_{row}_{col}',box(xx,yy,25,17,18,7),color,'operating_visual')
ref('key_space',box(kx+12+4*19,kb_y+10,25,5*19-2,18,7),'keys','operating_visual')
for row in range(5):
 for col in range(3):ref(f'nav_{row}_{col}',box(kx+306+col*19,kb_y+10+row*21,25,17,18,7),'modifier_keys','operating_visual')
for xx in (kx+23,kx+55):ref('knob_'+str(xx),rod(xx,kb_y+150,25,8,9),'fascia','operating_visual')
# Placeholder label plates are visual details, not evidence of component specifications.
badge=cornered(280,fy-1.2,164,100,1.2,16,'y')
lettering=b.Pos(285,fy-1.3,168)*b.Rot(X=90)*b.extrude(b.Text('RETRO / M',font_size=7,align=(b.Align.MIN,b.Align.MIN)),amount=-.6)
save('brand_badge',badge-lettering,'accent','y',note='Decorative engraved badge; optional adhesive attachment and light paint fill. Not structural.')
# Explicit cable and cooling keepouts; source interfaces touch their associated hardware faces.
ref('KEEP_pi_USB',box(px+85,py,pz,40,24,56),'#ce8b38','clearance')
ref('KEEP_pi_power_HDMI',box(px,py,pz-40,85,20,40),'#ce8b38','clearance')
ref('KEEP_cooler_air',box(px+12.5,py+1.6+co['height'],pz+5.5,co['width'],co['air_clearance'],co['depth']),'#56a6bd','clearance')
for i,dz in enumerate(D['bottom_z']):ref('KEEP_drive_rear_'+str(i+1),box(D['x'],D['front_y']+D['depth'],dz,D['width'],50,D['height']),'#ce8b38','clearance')
# Fastener heads provide visual assembly cues; positions are actual modeled axes.
for xx in (9,W-9):
 for zz in J['fascia_screw_z']:ref(f'fascia_screw_{xx}_{zz}',rod(xx,fy-2.2,zz,2.8,2.2,'y'),'metal','visual')
 for zz in J['carrier_screw_z']:ref(f'carrier_knob_{xx}_{zz}',rod(xx,-10,zz,6,6,'y'),'accent','transport_visual')
# Validation and manufacturing exports.
physical={n:s for n,s in parts.items() if info[n]['group'] not in ('test','carrier')}
carrier_physical={n:s for n,s in parts.items() if info[n]['group']=='carrier'}
checks=[];errors=[]
def bounds(sh):
 bb=sh.bounding_box();return (bb.min.X,bb.min.Y,bb.min.Z),(bb.max.X,bb.max.Y,bb.max.Z)
def overlap(a,z):
 am,ax=bounds(a);bm,bx=bounds(z)
 return all(min(ax[i],bx[i])-max(am[i],bm[i])>1e-5 for i in range(3))
def check_pair(n,a,m,z):
 if not overlap(a,z):return
 intersection=a&z;v=0.0 if intersection is None else (intersection.volume if hasattr(intersection,'volume') else sum(item.volume for item in intersection));checks.append({'a':n,'b':m,'intersection_mm3':v})
 if v>.01:errors.append({'a':n,'b':m,'volume_mm3':v})
for (n,a),(m,z) in itertools.combinations({**physical,**carrier_physical}.items(),2):check_pair(n,a,m,z)
for n,a in {**physical,**carrier_physical}.items():
 for m,z in references.items():
  if refmeta[m]['role'] in ('hardware','fabricated','transport','clearance'):check_pair(n,a,m,z)
for (n,a),(m,z) in itertools.combinations([(n,sh) for n,sh in references.items() if refmeta[n]['role']=='hardware'],2):check_pair(n,a,m,z)
for n,a in references.items():
 if refmeta[n]['role'] not in ('hardware','fabricated'):continue
 for m,z in references.items():
  if refmeta[m]['role']=='clearance':check_pair(n,a,m,z)
# Mount alignment checks reference the exact supplied outer display pattern.
assert len(hardware_mounts)==4
for a in hardware_mounts:assert any(abs(a['x']-x)<1e-5 and abs(a['z']-z)<1e-5 for x,z in outer)
print('INTERFERENCES',json.dumps(errors),flush=True)
report={'full_rigid_printed_pair_count':(len(physical)+len(carrier_physical))*(len(physical)+len(carrier_physical)-1)//2,'revision':Q['revision'],'parameter_sha256':hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),'case_WHD':[W,H,DEP],'transport_WHD':[W,H,DEP+ca['depth']],'intersection_checks_with_overlapping_bounding_boxes':checks,'unwanted_interferences':errors,'screen_mount_alignment':hardware_mounts,'parts':{},'limitations':['Approximate manufacturer display drawing; physical fit not established','Drive, cooler, Pi edge/port geometry, keyboard shell contacts and hub are provisional','No certified load rating or thermal/airflow simulation','No slicer/toolpath validation; orientation and volume checks only','Flexible straps and visual fastener heads excluded from rigid collision tests','Cable reservations and full service-tool sweeps require actual cables/hardware']}
scene=[]
for name,sh in parts.items():
 normal=info[name]['print_normal'];pr=sh
 if normal=='y':pr=b.Rot(X=90)*pr
 if normal=='x':pr=b.Rot(Y=-90 if 'right' not in name else 90)*pr
 bb=pr.bounding_box();pr=b.Pos(-bb.min.X,-bb.min.Y,-bb.min.Z)*pr;bb=pr.bounding_box();dims=[bb.size.X,bb.size.Y,bb.size.Z]
 assert max(dims)<=Q['printer']['design_part_limit']+.001,(name,dims)
 assert pr.is_valid
 b.export_step(sh,PART/(name+'.step'));b.export_stl(pr,PART/(name+'.stl'),tolerance=.08,angular_tolerance=.15)
 report['parts'][name]={**info[name],'print_bounds_mm':dims,'fits_nominal_A1':all(v<=256 for v in dims)}
 if info[name]['group']!='test':
  vs,fs=sh.tessellate(.15,.15);scene.append(dict(name=name,vertices=[[v.X,v.Y,v.Z] for v in vs],faces=fs,**info[name],role='carrier' if info[name]['group']=='carrier' else 'printed'))
for name,sh in references.items():
 vs,fs=sh.tessellate(.2,.18);scene.append(dict(name=name,vertices=[[v.X,v.Y,v.Z] for v in vs],faces=fs,**refmeta[name]))
(OUT/'scene.json').write_text(json.dumps(scene))
for name,shapes in [('enclosure_assembly',list(physical.values())+[s for n,s in references.items() if refmeta[n]['role'] in ('hardware','fabricated')]),('transport_assembly',list(physical.values())+list(carrier_physical.values())+[s for n,s in references.items() if refmeta[n]['role'] in ('hardware','fabricated','transport')])]:
 ass=b.Compound(label=name,children=shapes);b.export_step(ass,OUT/(name+'.step'))
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Exported',len(parts),'printable part/coupon files; collision issues:',len(errors),flush=True)
if errors:raise SystemExit(2)
