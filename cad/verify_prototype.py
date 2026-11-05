"""Re-import STEP; inspect actual binary STL topology, dimensions and volume."""
from pathlib import Path
import struct,json,hashlib,itertools
from collections import Counter
import numpy as np
import build123d as b
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/prototype';R=json.loads((OUT/'validation.json').read_text());P=json.loads((ROOT/'parameters.json').read_text())
assert R['parameter_sha256']==hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),'stale geometry'
assert not R['unwanted_interferences']
assert {x.stem for x in (OUT/'parts').glob('*.stl')}==set(R['parts'])
result={};steps={}
for name,data in R['parts'].items():
 shape=b.import_step(OUT/'parts'/(name+'.step'))
 assert shape.is_valid and len(shape.solids())==1,name
 assert abs(shape.volume-data['volume_mm3'])<.02,(name,'STEP volume changed')
 steps[name]=shape
 blob=(OUT/'parts'/(name+'.stl')).read_bytes();n=struct.unpack_from('<I',blob,80)[0]
 assert len(blob)==84+50*n,(name,'invalid binary STL')
 tris=np.array([struct.unpack_from('<12f',blob,84+50*i)[3:] for i in range(n)]).reshape(n,3,3)
 edges=Counter()
 for tri in tris:
  points=[tuple(np.round(v,5)) for v in tri]
  for a,z in ((0,1),(1,2),(2,0)):edges[tuple(sorted((points[a],points[z])))]+=1
 bad=sum(v!=2 for v in edges.values());assert bad==0,(name,'non-watertight edges',bad)
 volume=np.einsum('ij,ij->i',tris[:,0],np.cross(tris[:,1],tris[:,2])).sum()/6
 assert volume>0,(name,'inverted STL')
 dims=np.ptp(tris.reshape(-1,3),axis=0)
 assert np.all(dims<=P['prototype']['printer']['design_part_limit']+.001),(name,dims)
 assert abs(volume-data['volume_mm3'])/data['volume_mm3']<.02,(name,'STL volume mismatch')
 result[name]={'triangles':n,'watertight':True,'bounds_mm':dims.tolist(),'volume_relative_error':abs(volume-data['volume_mm3'])/data['volume_mm3']}
 print('Verified',name,flush=True)
assemblies={}
for name in ('enclosure_assembly','transport_assembly'):
 sh=b.import_step(OUT/(name+'.step'));assert sh.is_valid,name
 assemblies[name]={'valid':True,'solids':len(sh.solids())}
summary={'parameter_sha256':R['parameter_sha256'],'individual_parts':result,'assemblies':assemblies,'source_geometry_interferences':len(R['unwanted_interferences']),'slicer_validation':'Not run','physical_validation':'Not run'}
(OUT/'export_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print('PASS',len(result),'STEP/STL parts and both assemblies',flush=True)
