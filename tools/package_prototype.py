"""Create the offline viewer, print manifest, metal template and downloadable print bundle."""
from pathlib import Path
import json,csv,zipfile
import ezdxf
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/prototype'
P=json.loads((ROOT/'parameters.json').read_text());R=json.loads((OUT/'validation.json').read_text())
with (OUT/'print_manifest.csv').open('w',newline='') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['part','group','print_X_mm','print_Y_mm','print_Z_mm','CAD_volume_cm3','print_normal_in_assembly','notes'])
 for n,d in R['parts'].items():w.writerow([n,d['group'],*[round(x,3) for x in d['print_bounds_mm']],round(d['volume_mm3']/1000,3),d['print_normal'],d['note']])
q=P['prototype'];c=q['case'];h=q['handle'];doc=ezdxf.new('R2010');doc.units=4;m=doc.modelspace()
x0=c['wall'];y0=h['center_y']-h['backing_width_y']/2;width=c['width']-2*c['wall'];height=h['backing_width_y']
m.add_lwpolyline([(0,0),(width,0),(width,height),(0,height)],close=True)
for x in (9,c['width']-9):m.add_circle((x-x0,h['center_y']-y0),q['fasteners']['M3']['clearance']/2)
for x in h['anchor_x']:
 for y in h['bolt_y']:m.add_circle((x-x0,y-y0),q['fasteners']['M4']['clearance']/2)
doc.saveas(OUT/'handle_backing_drill_template.dxf')
scene=json.loads((OUT/'scene.json').read_text())
for row in scene:
 row['vertices']=[[round(v,4) for v in point] for point in row['vertices']]
 for key in ('volume_mm3','note','print_normal'):row.pop(key,None)
html=(ROOT/'tools/viewer-template.html').read_text().replace('__SCENE_DATA__',json.dumps(scene,separators=(',',':')))
(OUT/'viewer.html').write_text(html)
with zipfile.ZipFile(OUT/'P1-print-files.zip','w',zipfile.ZIP_DEFLATED) as z:
 for file in sorted((OUT/'parts').glob('*.stl')):z.write(file,'STL/'+file.name)
 for name in ('print_manifest.csv','handle_backing_drill_template.dxf','validation.json','export_verification.json'):z.write(OUT/name,name)
 z.write(ROOT/'docs/prototype-P1.md','PRINT_AND_ASSEMBLY_GUIDE.md')
with zipfile.ZipFile(OUT/'P1-print-files.zip') as z:assert z.testzip() is None
print('Packaged',len(R['parts']),'STLs, offline viewer, print manifest and metal template')
