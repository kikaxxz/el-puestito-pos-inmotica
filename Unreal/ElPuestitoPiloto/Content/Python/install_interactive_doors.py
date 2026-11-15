"""Install native interactive doors, retaining fixed frames and existing materials."""
import unreal as u,json
from pathlib import Path
root=Path(u.Paths.project_dir());dest='/Game/RestauranteCompleto/PuertasInteractivasV2'
ed=u.get_editor_subsystem(u.EditorActorSubsystem);levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert levels.load_level('/Game/RestauranteCompleto/RestauranteNoche')
cls=u.load_class(None,'/Script/ElPuestito.PuestitoDoor');assert cls
if not u.EditorAssetLibrary.does_directory_exist(dest):
 task=u.AssetImportTask();task.filename=str(root/'SourceAssets/PuertasInteractivas/puertas.glb');task.destination_path=dest;task.automated=True;task.save=True;task.async_=False
 u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
assets=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(dest,recursive=True)];meshes={a.get_name():a for a in assets if isinstance(a,u.StaticMesh)}
assert len(meshes)==14,len(meshes)
for a in ed.get_all_level_actors():
 if a.get_actor_label() in ['Puerta_220','Puerta_221'] or 'InteractiveDoor' in [str(t) for t in a.tags]:ed.destroy_actor(a)
matbase='/Game/RestauranteCompleto/Assets/restaurante_completo/Materials/'
wood=u.load_asset(matbase+'M_Puerta_220');metal=u.load_asset(matbase+'M_Puerta_221');assert wood and metal
rows=json.loads((root/'SourceAssets/PuertasInteractivas/manifest.json').read_text())['doors']
names=['Cubiculo hombres','Cubiculo mujeres 1','Cubiculo mujeres 2','Bano hombres','Bano mujeres','Oficina','Cocina'];report=[]
for i,row in enumerate(rows):
 h=row['hinge'];a=ed.spawn_actor_from_class(cls,u.Vector((h[0]-4.8)*100,(h[2]-24.6)*100,h[1]*100))
 a.set_actor_label('Puerta interactiva - '+names[i]);a.tags=['RestaurantOwned','InteractiveDoor'];a.set_editor_property('door_title',names[i]);a.set_editor_property('open_yaw',row['open_yaw'])
 for part,prop,mat in [('Hoja','leaf',wood),('Manilla','handle',metal)]:
  m=next(m for name,m in meshes.items() if name.startswith(f'PuertaInteractiva_{i}_{part}'))
  c=a.get_editor_property(prop);c.set_static_mesh(m);c.set_material(0,mat)
 a.configure_collision()
 # Audit both possible swings against the static room before deciding the direction.
 samples={}
 for sign in [1,-1]:
  samples[str(sign)]=[angle for angle in range(5,91,5) if not a.is_angle_clear(sign*angle)]
 report.append({'door':names[i],'yaw':row['open_yaw'],'blocked_angles':samples})
assert levels.save_current_level()
(root/'Evidence/doors-editor-audit.json').write_text(json.dumps(report,indent=2))
u.log('INTERACTIVE_DOORS_SAVED')
