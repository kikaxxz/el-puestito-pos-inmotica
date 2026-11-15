"""Validate the portable geometry and ensure stable mesh names for Interchange."""
import json
import math
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "SourceAssets/comedor_piloto.glb"
data = path.read_bytes()
magic, version, length = struct.unpack_from("<III", data)
assert magic == 0x46546C67 and version == 2 and length == len(data)
size, kind = struct.unpack_from("<II", data, 12)
assert kind == 0x4E4F534A
doc = json.loads(data[20:20+size])
binary_chunk = data[20+size:]
binary = binary_chunk[8:]
assert len(doc["meshes"]) == 18
for node in doc["nodes"]:
    if "mesh" in node:
        doc["meshes"][node["mesh"]]["name"] = node["name"]

triangles = 0
for mesh in doc["meshes"]:
    assert mesh.get("name")
    for primitive in mesh["primitives"]:
        accessor = doc["accessors"][primitive["attributes"]["POSITION"]]
        assert accessor["componentType"] == 5126 and accessor["type"] == "VEC3"
        view = doc["bufferViews"][accessor["bufferView"]]
        offset = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        stride = view.get("byteStride", 12)
        for index in range(accessor["count"]):
            x,y,z = struct.unpack_from("<3f", binary, offset+index*stride)
            assert all(math.isfinite(v) for v in (x,y,z))
            assert -1.8501 <= x <= 2.0001 and -2.7001 <= z <= 2.6001
        triangles += doc["accessors"][primitive["indices"]]["count"] // 3
assert triangles == 44890
assert not doc.get("extensionsRequired"), doc.get("extensionsRequired")
encoded = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf8")
encoded += b" " * (-len(encoded) % 4)
new_size = 20 + len(encoded) + len(binary_chunk)
path.write_bytes(struct.pack("<III",magic,version,new_size)+struct.pack("<II",len(encoded),kind)+encoded+binary_chunk)
report = {"triangles":triangles,"meshes":[m["name"] for m in doc["meshes"]],
          "materials":len(doc["materials"]),"textures":len(doc["textures"]),
          "bytes":new_size,"finite_geometry":True,"within_pilot_bounds":True}
(root/"Evidence/export-validation.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps(report,indent=2))
