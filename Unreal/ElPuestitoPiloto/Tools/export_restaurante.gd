extends SceneTree
## Export the entire restaurant without saving or modifying the Godot source scene.
const OUT = "D:/Unreal/ElPuestitoPiloto/SourceAssets/RestauranteCompleto/"
const ORIGIN = Vector3(4.8,0,24.6)
const REGION = AABB(Vector3(-1,-1,-1),Vector3(12,7,38))
var groups = {}
var materials = {}
var sources = []
var triangle_count = 0
var doors = []

func _initialize(): call_deferred("run")

func strip_scripts(n):
	n.set_script(null)
	for c in n.get_children(): strip_scripts(c)

func clip(poly: Array, axis: int, boundary: float, sign_: float) -> Array:
	var output = []
	if poly.is_empty(): return output
	var prev = poly[-1]
	var dp = sign_ * (prev.p[axis] - boundary)
	for cur in poly:
		var dc = sign_ * (cur.p[axis] - boundary)
		if (dp >= 0) != (dc >= 0):
			var t = dp / (dp - dc)
			output.append({"p":prev.p.lerp(cur.p,t),"n":prev.n.lerp(cur.n,t).normalized(),"uv":prev.uv.lerp(cur.uv,t),"c":prev.c.lerp(cur.c,t)})
		if dc >= 0: output.append(cur)
		prev = cur
		dp = dc
	return output

func group_for(mat: Material, category: String) -> Dictionary:
	var key = category + "_" + str(mat.get_instance_id() if mat else 0)
	if not groups.has(key):
		var m: StandardMaterial3D = mat.duplicate() if mat is StandardMaterial3D else StandardMaterial3D.new()
		var label = "%s_%02d" % [category,groups.size()]
		m.resource_name = "M_" + label
		m.uv1_triplanar = false
		m.uv1_scale = Vector3.ONE
		m.uv1_offset = Vector3.ZERO
		m.uv2_triplanar = false
		# Fine normal detail should not overpower the plaster and varnished wood.
		if category == "Pared": m.normal_scale = minf(m.normal_scale,0.25)
		if category == "Mobiliario":
			m.normal_scale = minf(m.normal_scale,0.35)
			m.roughness = maxf(m.roughness,0.72)
		if category == "Piso":
			m.metallic = 0.0
			m.normal_scale = minf(m.normal_scale,0.45)
		m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
		var st = SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		st.set_material(m)
		groups[key] = {"tool":st,"count":0,"material":m,"category":category,"label":label}
	return groups[key]

func add_mesh(mesh: Mesh, tr: Transform3D, override: Material, node_path: String, surface_overrides = []):
	if not mesh or not REGION.intersects(tr * mesh.get_aabb()): return
	if "segmento_luces" in node_path: return # Reuse the separate night bulb/cable fixtures.
	var category = "Decoracion"
	if "/Puerta_" in node_path: category = "Puerta"
	elif "Instrumentos" in node_path: category = "Instrumento"
	if "Techado" in node_path: category = "Techo"
	elif "Suelo" in node_path: category = "Piso"
	elif "Muro" in node_path: category = "Pared"
	elif "bambu" in node_path or "table_and_chairs" in node_path or "independiente" in node_path: category = "Mobiliario"
	var used = false
	var normal_tr = tr.basis.inverse().transposed()
	for surface in mesh.get_surface_count():
		var a = mesh.surface_get_arrays(surface)
		if a.is_empty(): continue
		var vertices = a[Mesh.ARRAY_VERTEX]
		var normals = a[Mesh.ARRAY_NORMAL]
		var uvs = a[Mesh.ARRAY_TEX_UV]
		var colors = a[Mesh.ARRAY_COLOR]
		var indices = a[Mesh.ARRAY_INDEX]
		var mat = override
		if mat == null and surface < surface_overrides.size(): mat = surface_overrides[surface]
		if mat == null: mat = mesh.surface_get_material(surface)
		var count = indices.size() if indices != null and indices.size() else vertices.size()
		for i in range(0,count-2,3):
			var ids = []
			for k in 3: ids.append(indices[i+k] if indices != null and indices.size() else i+k)
			if tr.basis.determinant() < 0: ids = [ids[0],ids[2],ids[1]]
			var poly = []
			for id in ids:
				var p = tr * vertices[id]
				var n = (normal_tr * normals[id]).normalized() if normals != null and normals.size() else Vector3.UP
				var uv = uvs[id] if uvs != null and uvs.size() else Vector2(p.x,p.z)
				if mat is BaseMaterial3D:
					if mat.uv1_triplanar:
						var q = p if mat.uv1_world_triplanar else vertices[id]
						var normal = n if mat.uv1_world_triplanar else normals[id]
						q = q * mat.uv1_scale + mat.uv1_offset
						if abs(normal.y) >= max(abs(normal.x),abs(normal.z)): uv = Vector2(q.x,q.z)
						elif abs(normal.x) > abs(normal.z): uv = Vector2(q.z,-q.y)
						else: uv = Vector2(q.x,-q.y)
					else: uv = uv * Vector2(mat.uv1_scale.x,mat.uv1_scale.y) + Vector2(mat.uv1_offset.x,mat.uv1_offset.y)
				poly.append({"p":p,"n":n,"uv":uv,"c":colors[id] if colors != null and colors.size() else Color.WHITE})
			poly = clip(poly,0,REGION.position.x,1)
			poly = clip(poly,0,REGION.end.x,-1)
			poly = clip(poly,2,REGION.position.z,1)
			poly = clip(poly,2,REGION.end.z,-1)
			if poly.size() < 3: continue
			var group = group_for(mat,category)
			for j in range(1,poly.size()-1):
				if (poly[j].p-poly[0].p).cross(poly[j+1].p-poly[0].p).length_squared() < 0.000000000001: continue
				for v in [poly[0],poly[j],poly[j+1]]:
					group.tool.set_normal(v.n)
					group.tool.set_uv(v.uv)
					group.tool.set_color(v.c)
					group.tool.add_vertex(v.p-ORIGIN)
				group.count += 1
				triangle_count += 1
				used = true
	if used: sources.append(node_path)

func collect(n: Node):
	if n is Node3D and not n.is_visible_in_tree(): return
	if n is MeshInstance3D:
		var overrides = []
		if n.mesh:
			for i in n.mesh.get_surface_count(): overrides.append(n.get_surface_override_material(i))
		add_mesh(n.mesh,n.global_transform,n.material_override,str(n.get_path()),overrides)
	elif n is MultiMeshInstance3D and n.multimesh:
		var mm = n.multimesh
		for i in mm.instance_count:
			add_mesh(mm.mesh,n.global_transform * mm.get_instance_transform(i),n.material_override,str(n.get_path())+"/"+str(i))
	elif n is CSGShape3D and n.is_root_shape():
		var baked = n.get_meshes()
		if baked.size() == 2: add_mesh(baked[1],n.global_transform * baked[0],n.material_override,str(n.get_path()))
	for c in n.get_children(): collect(c)

func run():
	var scene = load("res://restaurante.tscn").instantiate()
	strip_scripts(scene)
	root.add_child(scene)
	for i in 4: await process_frame
	# Use the corrected source hinge positions; open the leaves to provide access.
	for source in scene.get_children():
		if source is Node3D and "wooden_door" in source.scene_file_path:
			var door = load("res://door_interactive.gd").new()
			scene.add_child(door)
			door.configure(source)
			if door.pivot:
				door.pivot.rotation.y = door.angle
				var h = door.pivot.global_position
				doors.append({"source":str(source.name),"hinge":[h.x,h.y,h.z],"open_angle":door.angle})
	for i in 3: await process_frame
	collect(scene)
	var sample = Node3D.new()
	sample.name = "RestauranteCompleto"
	root.add_child(sample)
	for key in groups:
		var g = groups[key]
		if g.count == 0: continue
		g.tool.generate_tangents()
		g.tool.index()
		var node = MeshInstance3D.new()
		node.name = g.label
		node.mesh = g.tool.commit()
		node.mesh.resource_name = g.label
		sample.add_child(node)
		node.owner = sample
	var packed = PackedScene.new()
	packed.pack(sample)
	ResourceSaver.save(packed,OUT+"restaurante_completo.tscn")
	var doc = GLTFDocument.new()
	doc.image_format = "PNG"
	doc.root_node_mode = GLTFDocument.ROOT_NODE_MODE_KEEP_ROOT
	var state = GLTFState.new()
	var result = doc.append_from_scene(sample,state)
	if result == OK: result = doc.write_to_filesystem(state,OUT+"restaurante_completo.glb")
	var report = {"source":"res://restaurante.tscn","world_origin":[ORIGIN.x,ORIGIN.y,ORIGIN.z],"size_m":[REGION.size.x,REGION.size.z],"triangles":triangle_count,"material_batches":sample.get_child_count(),"sources":sources,"export_error":result,"doors":doors,"guirnaldas":"Reused from ComedorNoche"}
	FileAccess.open(OUT+"manifest.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
	print("EXPORT_RESTAURANTE ",result," triangles=",triangle_count," batches=",sample.get_child_count())
	quit(0 if result == OK else 1)

