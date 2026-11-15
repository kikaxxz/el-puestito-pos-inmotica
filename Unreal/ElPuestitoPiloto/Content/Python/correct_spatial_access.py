"""Apply isolated cubicle/cylinder corrections without rebuilding the restaurant."""
import unreal as u,json
from pathlib import Path
root=Path(u.Paths.project_dir());dest='/Game/RestauranteCompleto/CorreccionAccesos'
ed=u.get_editor_subsystem(u.EditorActorSubsystem);levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert levels.load_level('/Game/RestauranteCompleto/RestauranteNoche')
manifest=json.loads((root/'SourceAssets/CorreccionAccesos/manifest.json').read_text())
if not u.EditorAssetLibrary.does_directory_exist(dest):
 task=u.AssetImportTask();task.filename=str(root/'SourceAssets/CorreccionAccesos/accesos.glb');task.destination_path=dest;task.automated=True;task.save=True;task.async_=False
 u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
meshes=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(dest,recursive=True)]
meshes=[m for m in meshes if isinstance(m,u.StaticMesh)]
assert len(meshes)==7,[(m.get_name()) for m in meshes]
actors={a.get_actor_label():a for a in ed.get_all_level_actors()};report=[]
for row in manifest['meshes']:
 label=row['source'][:-1]
 a=actors[label];c=a.get_component_by_class(u.StaticMeshComponent)
 m=next(m for m in meshes if m.get_name().startswith(row['source']))
 materials=[c.get_material(i) for i in range(c.get_num_materials())]
 c.set_static_mesh(m)
 for i,mat in enumerate(materials):c.set_material(i,mat)
 body=m.get_editor_property('body_setup')
 if body:body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 u.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
 report.append({'actor':label,'mesh':m.get_path_name(),'materials':[mat.get_path_name() for mat in materials if mat]})
shift=manifest['cylinder_shift_m'];delta=u.Vector(shift[0]*100,shift[2]*100,shift[1]*100)
before=json.loads((root/'Evidence/spatial-before.json').read_text())
for row in before:
 if row['label'] in ['Rotulo GLP SIMULADO','Rotulo 30.00 kg','Rotulo HX711 / PESO']:
  p=row['position'];actors[row['label']].set_actor_location(u.Vector(*p)+delta,False,False)
assert levels.save_current_level()
(root/'Evidence/spatial-correction.json').write_text(json.dumps({'replacements':report,'cylinder_shift_cm':[delta.x,delta.y,delta.z],'door_swing':'outwards, away from toilet'},indent=2))
u.log('SPATIAL_CORRECTIONS_SAVED')
