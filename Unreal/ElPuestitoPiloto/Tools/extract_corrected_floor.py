"""Extract the validated concrete floor, preserving UVs and upward winding."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parents[1]
raw=(root/'SourceAssets/RestauranteCompleto/restaurante_completo.glb').read_bytes()
size=struct.unpack_from('<I',raw,12)[0]
src=json.loads(raw[20:20+size]);data=raw[28+size:]
mesh=next(m for m in src['meshes'] if m['name'].startswith('Piso_30'))
pr=mesh['primitives'][0]
out={'asset':{'version':'2.0'},'scene':0,'scenes':[{'nodes':[0]}],
     'nodes':[{'name':'PisoConcretoCorregido','mesh':0}],
     'meshes':[{'name':'PisoConcretoCorregido','primitives':[{'attributes':{}}]}],
     'accessors':[],'bufferViews':[],'buffers':[]}
buf=bytearray()
def copy_accessor(index):
    a=src['accessors'][index].copy();v=src['bufferViews'][a['bufferView']]
    length={5126:4,5125:4,5123:2,5121:1}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    start=v.get('byteOffset',0)+a.get('byteOffset',0)
    while len(buf)%4:buf.append(0)
    offset=len(buf)
    for i in range(a['count']):
        at=start+i*v.get('byteStride',length);buf.extend(data[at:at+length])
    a['bufferView']=len(out['bufferViews']);a.pop('byteOffset',None)
    out['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(buf)-offset})
    out['accessors'].append(a)
    return len(out['accessors'])-1
for name,index in pr['attributes'].items():out['meshes'][0]['primitives'][0]['attributes'][name]=copy_accessor(index)
out['meshes'][0]['primitives'][0]['indices']=copy_accessor(pr['indices'])
dst=out['meshes'][0]['primitives'][0]
pa=out['accessors'][dst['attributes']['POSITION']]
po=out['bufferViews'][pa['bufferView']]['byteOffset']
ia=out['accessors'][dst['indices']]
io=out['bufferViews'][ia['bufferView']]['byteOffset']
fmt={5125:'I',5123:'H',5121:'B'}[ia['componentType']]
stride=struct.calcsize(fmt)
for i in range(0,ia['count'],3):
    ids=list(struct.unpack_from('<'+fmt*3,buf,io+i*stride))
    a,b,c=[struct.unpack_from('<fff',buf,po+v*12) for v in ids]
    normal_y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
    if normal_y<0:
        struct.pack_into('<'+fmt*3,buf,io+i*stride,ids[0],ids[2],ids[1])
    assert abs(normal_y)>0.1
out['buffers']=[{'byteLength':len(buf)}]
while len(buf)%4:buf.append(0)
j=json.dumps(out,separators=(',',':')).encode();j+=b' '*(-len(j)%4)
path=root/'SourceAssets/RestauranteCompleto/piso_concreto_corregido.glb'
path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(buf))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(buf),0x004e4942)+buf)
print(path)
