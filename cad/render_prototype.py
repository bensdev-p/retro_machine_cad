"""Blender renderer for executed build123d geometry; run with blender -b -t 4 -P this_file."""
from pathlib import Path
import bpy, math, json, sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/prototype';Q=json.loads((ROOT/'parameters.json').read_text())['prototype']
scene_data=json.loads((OUT/'scene.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.cycles.max_bounces=4;scene.cycles.diffuse_bounces=2;scene.cycles.glossy_bounces=2
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world.color=(.25,.25,.25)
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.3,.3,.3,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
matcache={}
def material(hexcolor,name=None,metal=False):
 key=(hexcolor,metal)
 if key in matcache:return matcache[key]
 m=bpy.data.materials.new(name or hexcolor)
 srgb=[int(hexcolor.lstrip('#')[i:i+2],16)/255 for i in (0,2,4)]
 m.diffuse_color=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in srgb)+(1,);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.38 if metal else .52;bs.inputs['Metallic'].default_value=.65 if metal else 0
 matcache[key]=m;return m
objects={};positions={}
for row in scene_data:
 mesh=bpy.data.meshes.new(row['name']);mesh.from_pydata(row['vertices'],[],row['faces']);mesh.update()
 obj=bpy.data.objects.new(row['name'],mesh);scene.collection.objects.link(obj)
 obj.data.materials.append(material(row['color'],metal=row['color']==Q['palette']['metal']))
 # Geometry edges are true CAD; subtle shader bevel catches light without changing export geometry.
 m=obj.data.materials[0]
 if row['role'] in ('printed','carrier'):
  bevel=obj.modifiers.new('Small visual edge break','BEVEL');bevel.width=.45;bevel.segments=2
  bevel.affect='EDGES';bevel.limit_method='ANGLE'
  obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 obj['role']=row['role'];obj['part_group']=row.get('group','');objects[row['name']]=obj;positions[row['name']]=Vector((0,0,-10)) if row['role']=='operating_visual' else obj.location.copy()
def text_obj(name,text,loc,size,color,rotation=(math.pi/2,0,0)):
 cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.size=size;cu.extrude=.01;cu.align_x='LEFT'
 ob=bpy.data.objects.new(name,cu);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=rotation;ob.data.materials.append(material(color));ob['role']='label';return ob
labels=[]
# Engraved badge lettering is actual CAD geometry.
for i,z in enumerate(Q['drive']['bottom_z']):labels.append(text_obj('disk_label_'+str(i),'DISK '+('A' if i==0 else 'B')+'   /   1.44 MB',(282,7.8,z-7),3,'#c1c6ca'))
labels.append(text_obj('screen_caption','PORTABLE COMPUTER  /  RASPBERRY Pi 5',(29,7.8,19),3.4,'#9eacb8'))
# Screen graphics are illustrative render content, not a running OS.
for name in ['screen_active_image']:objects[name].hide_render=True
screen_rows=[('RETRO / M',15,142,10),('PORTABLE WORKSTATION',17,127,4),('A:  PC FLOPPY   1.44 MB',17,98,4),('B:  PC FLOPPY   1.44 MB',17,88,4),('SYSTEM READY',17,61,5),('> _',17,40,6)]
screenlabels=[]
# Opaque emissive face is separated from the underlying screen envelope.
sp=json.loads((ROOT/'parameters.json').read_text())['display'];sx=Q['screen']['x']+sp['active_offset_x'];sz=Q['screen']['z']+sp['active_offset_z'];sy=Q['screen']['front_y']-.22
mesh=bpy.data.meshes.new('screen_front');mesh.from_pydata([(sx,sy,sz),(sx+sp['active_width'],sy,sz),(sx+sp['active_width'],sy,sz+sp['active_height']),(sx,sy,sz+sp['active_height'])],[],[(0,1,2,3)]);mesh.update()
so=bpy.data.objects.new('screen_front',mesh);scene.collection.objects.link(so);sm=material('#183347');so.data.materials.append(sm);bs=sm.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.035,.09,.14,1);bs.inputs['Emission Strength'].default_value=.35
for txt,dx,dz,size in screen_rows:
 # Offsets are expressed from display glass lower-left, within the active window.
 ob=text_obj('screen_'+txt,txt,(Q['screen']['x']+dx+14,sy-.1,Q['screen']['z']+dz),size,'#c5dfe9');screenlabels.append(ob)
# Approximate key legends on visualization-only stock keyboard.
keylabels=[]
letters=['CTRL WIN ALT     ALT FN CTRL MENU','Z X C V B N M , . / SHIFT','SHIFT A S D F G H J K L ; ENTER','TAB Q W E R T Y U I O P [ ]','ESC 1 2 3 4 5 6 7 8 9 0 - =','ESC F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12']
for row in range(6):
 tokens=letters[row].split()
 for col in range(min(15,len(tokens))):
  name=f'key_{row}_{col}'
  if name not in objects:continue
  vs=objects[name].data.vertices;xx=min(v.co.x for v in vs);yy=min(v.co.y for v in vs)
  ob=text_obj('legend_'+name,tokens[col],(xx+2,yy+4,22.03),2.9,'#303841',(0,0,0));keylabels.append(ob)
# Rubber feet are reference purchased hardware, omitted from CAD shell dimensions.
for x,y in [(20,20),(354,20),(20,174),(354,174)]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x+13,y+13,-3));ob=bpy.context.object;ob.name='rubber_foot';ob.dimensions=(26,26,6);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material('#252a2d'))
bpy.ops.mesh.primitive_plane_add(size=3000,location=(200,0,-6.05));ground=bpy.context.object;ground.name='studio_floor';ground.data.materials.append(material('#d4d6d8'))
def light(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power*.45;data.shape='DISK';data.size=size
 ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((200,60,90))-ob.location).to_track_quat('-Z','Y').to_euler()
# Millimeter-scale scene requires energy scaled with squared distance.
light('key',(100,-300,650),6000000,500);light('fill',(650,-150,350),3500000,400);light('rim',(150,500,500),5500000,350)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.clip_end=5000

def view(filename,loc,target,scale,mode):
 for row in scene_data:
  ob=objects[row['name']];ob.location=positions[row['name']].copy();role=row['role']
  ob.hide_render=(role in ('carrier','transport','transport_visual')) if mode!='transport' else role=='operating_visual'
  if mode=='exploded':
   ob.hide_render=role in ('carrier','transport','transport_visual','operating_visual')
   if row['name'].startswith('top_') or row['name'].startswith('handle_') or row['name'].startswith('webbing_'):ob.location.z+=105
   if row['name'].startswith('side_left'):ob.location.x-=65
   if row['name'].startswith('side_right'):ob.location.x+=65
   if row['name'].startswith(('fascia_','front_rim_')):ob.location.y-=65
   if row['name'].startswith('rear_'):ob.location.y+=70
  if row['name']=='screen_active_image' or role=='clearance':ob.hide_render=True
 for ob in keylabels:ob.hide_render=mode in ('transport','exploded')
 for ob in labels+screenlabels:ob.hide_render=mode=='exploded'
 so.hide_render=False
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
 scene.render.filepath=str(OUT/'previews'/filename);bpy.ops.render.render(write_still=True)
 print('RENDERED',filename,flush=True)
if '--quick' in sys.argv:
 scene.render.resolution_percentage=50;scene.cycles.samples=16
 view('_lighting_test.png',(650,-720,430),(200,-15,90),660,'operating')
else:
 view('01_operating.png',(650,-720,430),(200,-15,90),660,'operating')
 view('02_transport.png',(640,-700,400),(200,55,110),570,'transport')
 view('03_rear.png',(620,750,420),(200,110,95),580,'rear')
 view('04_exploded.png',(700,-650,520),(200,100,125),760,'exploded')
 view('05_front.png',(200,-800,110),(200,0,110),580,'operating')
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'prototype_scene.blend'))
