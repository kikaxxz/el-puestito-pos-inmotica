"""Replace the stale, downward-facing concrete floor with validated geometry."""
import unreal as u
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve()
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert u.EditorLevelLibrary.get_editor_world().get_name()=='RestauranteNoche'
dest='/Game/RestauranteCompleto/PisoCorregido'
task=u.AssetImportTask()
task.filename=str(root/'SourceAssets/RestauranteCompleto/piso_concreto_corregido.glb')
task.destination_path=dest;task.automated=True;task.save=True;task.async_=False
task.replace_existing=True
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
assets=[u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(dest,recursive=True)]
mesh=next(a for a in assets if isinstance(a,u.StaticMesh))
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
actor=next(a for a in ed.get_all_level_actors() if a.get_actor_label()=='Piso_30')
c=actor.get_component_by_class(u.StaticMeshComponent)
c.set_static_mesh(mesh)
c.set_material(0,u.load_asset('/Game/RestauranteCompleto/Assets/restaurante_completo/Materials/M_Piso_30'))
u.EditorAssetLibrary.save_loaded_asset(mesh)
levels.save_current_level()
u.log('CONCRETE_FLOOR_CORRECTED')
