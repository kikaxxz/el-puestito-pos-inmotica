import json, math, struct
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=root/'SourceAssets/ComedorCompleto'
path=source/'comedor_completo.glb'
data=bytearray(path.read_bytes())
size,kind=struct.unpack_from('<II',data,12)
doc=json.loads(data[20:20+size]);base=28+size
def accessor(idx):
    a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']]
    return a,base+v.get('byteOffset',0)+a.get('byteOffset',0)
def vec(idx):
    a,off=accessor(idx)
    return [struct.unpack_from('<3f',data,off+i*12) for i in range(a['count'])]
triangles=0;flipped=0
for mesh in doc['meshes']:
    for p in mesh['primitives']:
        positions=vec(p['attributes']['POSITION'])
        for x,y,z in positions:
            assert all(math.isfinite(v) for v in (x,y,z))
            assert -5.0002<=x<=5.1002 and -6.6002<=z<=6.4002
        ia,offset=accessor(p['indices']);fmt={5121:'B',5123:'H',5125:'I'}[ia['componentType']];stride=struct.calcsize(fmt)
        triangles+=ia['count']//3
        if mesh['name'].startswith('Piso'):
            normals=vec(p['attributes']['NORMAL'])
            for i in range(0,ia['count'],3):
                ids=list(struct.unpack_from('<'+fmt*3,data,offset+i*stride))
                a,b,c=[positions[q] for q in ids]
                ab=[b[j]-a[j] for j in range(3)];ac=[c[j]-a[j] for j in range(3)]
                cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
                if sum(cross[j]*normals[ids[0]][j] for j in range(3))<0:
                    struct.pack_into('<'+fmt*3,data,offset+i*stride,ids[0],ids[2],ids[1]);flipped+=1
path.write_bytes(data)
manifest=json.loads((source/'manifest.json').read_text())
bounds=json.loads((root/'Evidence/source_bounds_full.json').read_text())
tables=[b for b in bounds if b['name'].startswith(('mesa_','table_and_chairs')) and b['min'][2]>=18 and b['max'][2]<=31]
for b in tables:
    assert any('/'+b['name']+'/' in p or p.endswith('/'+b['name']) for p in manifest['sources']),b['name']
assert len(tables)==10
assert triangles==manifest['triangles']
report={'tables': [t['name'] for t in tables], 'table_count':len(tables),'triangles':triangles,'meshes':len(doc['meshes']),'textures':len(doc['textures']),'floor_triangles_reoriented':flipped,'full_table_coverage':True,'finite_geometry':True,'bounds_valid':True,'bytes':len(data)}
(root/'Evidence/comedor-export-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
