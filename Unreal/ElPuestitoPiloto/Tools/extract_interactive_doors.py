"""Separate seven leaves and handles, restoring closed local hinge coordinates."""
import json,struct,math
from pathlib import Path
root=Path(__file__).resolve().parents[1];folder=root/'SourceAssets/RestauranteCompleto'
b=(folder/'restaurante_completo.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];src=json.loads(b[20:20+n]);data=b[28+n:]
doors=json.loads((folder/'manifest.json').read_text())['doors']
def vals(ai):
 a=src['accessors'][ai];v=src['bufferViews'][a['bufferView']];cnt={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt='<'+{5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']]*cnt
 return [list(struct.unpack_from(fmt,data,v.get('byteOffset',0)+a.get('byteOffset',0)+i*v.get('byteStride',struct.calcsize(fmt)))) for i in range(a['count'])]
def distance(p,d):
 h=d['hinge'];a=d['open_angle'];vx,vz=(math.sin(a),math.cos(a)) if d['source'] not in ['Sketchfab_Scene15','Sketchfab_Scene17'] else (math.cos(a),-math.sin(a))
 dx,dz=p[0]+4.8-h[0],p[2]+24.6-h[2];t=max(0,min(1.2,dx*vx+dz*vz))
 return (dx-t*vx)**2+(dz-t*vz)**2
out={'asset':{'version':'2.0'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'accessors':[],'bufferViews':[],'buffers':[]};buf=bytearray();counts={}
def add(values,typ,ctype=5126):
 while len(buf)%4:buf.append(0)
 off=len(buf);fmt='<'+('f' if ctype==5126 else 'I')*len(values[0])
 for v in values:buf.extend(struct.pack(fmt,*v))
 ai=len(out['accessors']);a={'bufferView':len(out['bufferViews']),'componentType':ctype,'count':len(values),'type':typ}
 if typ=='VEC3':a.update(min=[min(v[k] for v in values) for k in range(3)],max=[max(v[k] for v in values) for k in range(3)])
 out['accessors'].append(a);out['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(buf)-off});return ai
for source,part in [('Puerta_2202','Hoja'),('Puerta_2212','Manilla')]:
 mesh=next(m for m in src['meshes'] if m['name']==source);assert len(mesh['primitives'])==1
 p=mesh['primitives'][0];attrs={k:vals(ai) for k,ai in p['attributes'].items()};indices=[v[0] for v in vals(p['indices'])];groups=[[] for d in doors]
 for i in range(0,len(indices),3):
  tri=indices[i:i+3];cen=[sum(attrs['POSITION'][j][k] for j in tri)/3 for k in range(3)];di=min(range(7),key=lambda j:distance(cen,doors[j]));assert distance(cen,doors[di])<.03,(di,cen)
  groups[di].extend(tri)
 for di,ids in enumerate(groups):
  assert ids;unique=list(dict.fromkeys(ids));remap={v:i for i,v in enumerate(unique)};d=doors[di];h=d['hinge'];a=d['open_angle'];c,s=math.cos(a),math.sin(a);newattrs={}
  original_y=[attrs['POSITION'][i][1] for i in unique]
  bottom,top=min(original_y),max(original_y)
  # Trim the panel to clear the actual floor; preserve the top inside the frame.
  new_bottom=.145 if di==6 else .10
  scale_y=(top-new_bottom)/(top-bottom) if part=='Hoja' else 1
  for key,values in attrs.items():
   vv=[]
   for index in unique:
    v=values[index][:]
    if key=='POSITION':
     if part=='Hoja':v[1]=new_bottom+(v[1]-bottom)*scale_y
     v[0]-=h[0]-4.8;v[1]-=h[1];v[2]-=h[2]-24.6
    if key=='NORMAL' and part=='Hoja':
     v[1]/=scale_y;length=sum(k*k for k in v)**.5;v=[k/length for k in v]
    if key in ['POSITION','NORMAL','TANGENT']:v[0],v[2]=c*v[0]-s*v[2],s*v[0]+c*v[2]
    vv.append(v)
   newattrs[key]=add(vv,src['accessors'][p['attributes'][key]]['type'])
  name=f'PuertaInteractiva_{di}_{part}';mi=len(out['meshes']);out['meshes'].append({'name':name,'primitives':[{'attributes':newattrs,'indices':add([[remap[j]] for j in ids],'SCALAR',5125)}]});out['nodes'].append({'name':name,'mesh':mi});out['scenes'][0]['nodes'].append(mi);counts[name]=len(ids)//3
out['buffers']=[{'byteLength':len(buf)}]
while len(buf)%4:buf.append(0)
j=json.dumps(out,separators=(',',':')).encode();j+=b' '*(-len(j)%4)
dest=root/'SourceAssets/PuertasInteractivas';dest.mkdir(exist_ok=True)
(dest/'puertas.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(buf))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(buf),0x004e4942)+buf)
for i,d in enumerate(doors):d['open_yaw']=90 if i<3 else -d['open_angle']*180/math.pi
(dest/'manifest.json').write_text(json.dumps({'doors':doors,'triangles':counts},indent=2))
print(counts)
