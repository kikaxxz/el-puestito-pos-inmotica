"""Separate disconnected bulb/cable geometry so only the glass emits light."""
import struct,json,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=(root/'SourceAssets/ComedorCompleto/comedor_completo.glb').read_bytes()
n=struct.unpack_from('<I',p,12)[0];j=json.loads(p[20:20+n]);raw=p[28+n:]
node=next(x for x in j['nodes'] if x.get('name')=='Decoracion_14')
pr=j['meshes'][node['mesh']]['primitives'][0]
def read(idx):
    a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];o=v.get('byteOffset',0)+a.get('byteOffset',0)
    fmt={5121:'B',5123:'H',5125:'I',5126:'f'}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    s=struct.calcsize('<'+fmt)
    return [struct.unpack_from('<'+fmt,raw,o+i*v.get('byteStride',s)) for i in range(a['count'])]
vs=read(pr['attributes']['POSITION']);ids=[a[0] for a in read(pr['indices'])];parents=list(range(len(vs)))
def find(a):
    while parents[a]!=a:parents[a]=parents[parents[a]];a=parents[a]
    return a
def union(a,b):parents[find(a)]=find(b)
seen={}
for i,v in enumerate(vs):
    k=tuple(round(x,5) for x in v)
    if k in seen:union(i,seen[k])
    else:seen[k]=i
for i in range(0,len(ids),3):union(ids[i],ids[i+1]);union(ids[i],ids[i+2])
cs=collections.defaultdict(list)
for i,v in enumerate(vs):cs[find(i)].append(v)
b=[]
for key,vv in cs.items():
    lo=[min(v[k] for v in vv) for k in range(3)];hi=[max(v[k] for v in vv) for k in range(3)]
    b.append({'key':key,'vertices':len(vv),'size':[round(hi[k]-lo[k],4) for k in range(3)],'center':[(hi[k]+lo[k])/2 for k in range(3)]})
(root/'Evidence/light-components.json').write_text(json.dumps(b,indent=2))
print('components',len(b))
print(json.dumps(b[:16],indent=1))
# The last cable segment is scaled 1.25x. Classify the round glass by
# topology and proportions, not the original 14 cm bulb's narrow size range.
bulb_keys={c['key'] for c in b if c['vertices']>500 and
           all(.10<s<.22 for s in c['size']) and
           max(c['size'])/min(c['size'])<1.35}
socket_count=sum(c['vertices']<100 and .20<c['size'][1]<.35 and
                 max(c['size'][0],c['size'][2])<.10 for c in b)
assert len(bulb_keys)==socket_count==30, (len(bulb_keys),socket_count)
parts=[[],[]]
for i in range(0,len(ids),3):
    part=1 if find(ids[i]) in bulb_keys else 0
    parts[part].extend(ids[i:i+3])
doc={'asset':{'version':'2.0','generator':'El Puestito night fixture separation'},'scene':0,'scenes':[{'nodes':[0,1]}],'nodes':[],'meshes':[],'materials':[{'name':'CableOscuro','pbrMetallicRoughness':{'baseColorFactor':[.014,.012,.01,1],'roughnessFactor':.85,'metallicFactor':0}},{'name':'BombillaCalida','pbrMetallicRoughness':{'baseColorFactor':[1,.65,.25,1],'roughnessFactor':.35,'metallicFactor':0}}],'bufferViews':[],'accessors':[],'buffers':[]}
buf=bytearray()
def add(values,fmt,typ):
    while len(buf)%4:buf.append(0)
    offset=len(buf)
    for v in values:buf.extend(struct.pack('<'+fmt,*v))
    doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(buf)-offset})
    acc={'bufferView':len(doc['bufferViews'])-1,'componentType':5126 if fmt[0]=='f' else 5125,'count':len(values),'type':typ}
    if typ=='VEC3':acc.update({'min':[min(v[k] for v in values) for k in range(3)],'max':[max(v[k] for v in values) for k in range(3)]})
    doc['accessors'].append(acc);return len(doc['accessors'])-1
attributes={}
for name,typ,fmt in [('POSITION','VEC3','fff'),('NORMAL','VEC3','fff'),('TEXCOORD_0','VEC2','ff')]:
    if name in pr['attributes']:attributes[name]=add(read(pr['attributes'][name]),fmt,typ)
for i,part in enumerate(parts):
    name=['CablesGuirnalda','BombillasGuirnalda'][i]
    index=add([(q,) for q in part],'I','SCALAR')
    doc['meshes'].append({'name':name,'primitives':[{'attributes':attributes,'indices':index,'material':i}]})
    doc['nodes'].append({'name':name,'mesh':i})
doc['buffers']=[{'byteLength':len(buf)}]
while len(buf)%4:buf.append(0)
encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
out=root/'SourceAssets/Noche';out.mkdir(exist_ok=True)
(out/'guirnaldas_noche.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(buf))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(buf),0x004e4942)+buf)
centers=[c['center'] for c in b if c['key'] in bulb_keys]
(out/'bombillas.json').write_text(json.dumps({'bulbs':len(centers),'positions_cm':[[c[0]*100,c[2]*100,c[1]*100] for c in centers]},indent=2))
print('Night lights:',len(centers),'bulbs, two batches;',len(buf),'bytes')
