import unreal as u,json
from pathlib import Path
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/RestauranteCompleto/RestauranteNoche');out=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if a.get_name() in ['StaticMeshActor_51','StaticMeshActor_256','StaticMeshActor_257','StaticMeshActor_259'] or 'InteractiveDoor' in [str(t) for t in a.tags]:
  c=a.get_component_by_class(u.StaticMeshComponent);p=a.get_actor_location();b=a.get_actor_bounds(False);row={'name':a.get_name(),'label':a.get_actor_label(),'pos':str(p),'bounds':str(b),'mesh':c.static_mesh.get_path_name() if c and c.static_mesh else None}
  if 'InteractiveDoor' in [str(t) for t in a.tags]:row['box']=str(a.blocker.get_unscaled_box_extent());row['offset']=str(a.blocker.get_editor_property('relative_location'))
  out.append(row)
Path('D:/Unreal/ElPuestitoPiloto/Evidence/door-obstacles.json').write_text(json.dumps(out,indent=2))
