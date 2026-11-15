"""Create targeted Unreal mesh replacements from the immutable source export.
Only cubicle leaves/handles and cylinder/scale vertices are changed.
Existing Unreal materials are retained by the companion import script.
"""
import json,struct,copy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
b=(root/'SourceAssets/RestauranteCompleto/restaurante_completo.glb').read_bytes()
n=struct.unpack_from('<I',b,12)[0];src=json.loads(b[20:20+n]);data=b[28+n:]
def values(ai):
 a=src['accessors'][ai];v=src['bufferViews'][a['bufferView']]
 count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt='<'+{5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]*count
 size=struct.calcsize(fmt);start=v.get('byteOffset',0)+a.get('byteOffset',0)
 return [list(struct.unpack_from(fmt,data,start+i*v.get('byteStride',size))) for i in range(a['count'])]
# Find the kitchen floor directly beneath the new cylinder.
px,pz=.40-4.8,32.25-24.6;floor=[]
for m in src['meshes']:
 if not m['name'].startswith('Piso'):continue
 for p in m['primitives']:
  vs=values(p['attributes']['POSITION']);ids=[v[0] for v in values(p['indices'])]
  for i in range(0,len(ids),3):
   a,c,d=[vs[k] for k in ids[i:i+3]]
   den=(c[2]-d[2])*(a[0]-d[0])+(d[0]-c[0])*(a[2]-d[2])
   if abs(den)<1e-9:continue
   u=((c[2]-d[2])*(px-d[0])+(d[0]-c[0])*(pz-d[2]))/den
   v=((d[2]-a[2])*(px-d[0])+(a[0]-d[0])*(pz-d[2]))/den
   if min(u,v,1-u-v)>=-1e-6:
    y=u*a[1]+v*c[1]+(1-u-v)*d[1]
    if -.2<y<.5:floor.append(y)
assert floor,'No kitchen floor found'
floor_y=max(floor)
shift=[-2.72,floor_y+.003-.3594421148300171,-1.10]
hinges=[(8.53170394897461-4.8,14.531343460083-24.6),(8.52229309082031-4.8,15.804669380188-24.6),(8.52553176879883-4.8,16.9512176513672-24.6)]
out={'asset':{'version':'2.0'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'accessors':[],'bufferViews':[],'buffers':[]};buf=bytearray();report=[]
def add(ai,vals):
 a=copy.deepcopy(src['accessors'][ai]);count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt='<'+{5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]*count
 while len(buf)%4:buf.append(0)
 offset=len(buf)
 for v in vals:buf.extend(struct.pack(fmt,*v))
 a['bufferView']=len(out['bufferViews']);a.pop('byteOffset',None)
 if 'min' in a:a['min']=[min(v[k] for v in vals) for k in range(count)]
 if 'max' in a:a['max']=[max(v[k] for v in vals) for k in range(count)]
 out['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(buf)-offset});out['accessors'].append(a)
 return len(out['accessors'])-1
for mesh in src['meshes']:
 if not mesh['name'].startswith(('Puerta_220','Puerta_221','Instrumento')):continue
 prims=[];changed=0
 for p in mesh['primitives']:
  attrs={k:values(i) for k,i in p['attributes'].items()};pos=attrs['POSITION']
  for i,(x,y,z) in enumerate(pos):
   if mesh['name'].startswith('Puerta') and x+4.8>8.4 and 14.3<z+24.6<17.2:
    hx,hz=min(hinges,key=lambda h:abs(z-h[1]));assert abs(z-hz)<.25
    pos[i]=[2*hx-x,y,2*hz-z]
    for k in ['NORMAL','TANGENT']:
     if k in attrs:attrs[k][i][0]*=-1;attrs[k][i][2]*=-1
    changed+=1
   elif mesh['name'].startswith('Instrumento') and 2.7<x+4.8<3.5 and 32.8<z+24.6<33.9:
    pos[i]=[x+shift[0],y+shift[1],z+shift[2]];changed+=1
  prims.append((p,attrs))
 if not changed:continue
 name=mesh['name']+'_AccesoCorregido';new={'name':name,'primitives':[]}
 for p,attrs in prims:
  new['primitives'].append({'attributes':{k:add(p['attributes'][k],v) for k,v in attrs.items()},'indices':add(p['indices'],values(p['indices']))})
 idx=len(out['nodes']);out['nodes'].append({'name':name,'mesh':len(out['meshes'])});out['scenes'][0]['nodes'].append(idx);out['meshes'].append(new)
 report.append({'source':mesh['name'],'replacement':name,'vertices_moved':changed})
assert len(report)==7,report
out['buffers']=[{'byteLength':len(buf)}]
while len(buf)%4:buf.append(0)
j=json.dumps(out,separators=(',',':')).encode();j+=b' '*(-len(j)%4)
dest=root/'SourceAssets/CorreccionAccesos';dest.mkdir(exist_ok=True)
(dest/'accesos.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(buf))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(buf),0x004e4942)+buf)
(dest/'manifest.json').write_text(json.dumps({'meshes':report,'cylinder_shift_m':shift,'floor_y_m':floor_y,'cylinder_center_xz_m':[.4,32.25],'cubicle_opening':'outward'},indent=2))
print(json.dumps({'meshes':report,'shift':shift,'floor_y':floor_y}))
