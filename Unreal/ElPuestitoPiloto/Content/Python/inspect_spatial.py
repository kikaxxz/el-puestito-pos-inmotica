import unreal as u,json
from pathlib import Path
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/RestauranteCompleto/RestauranteNoche')
out=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 c=a.get_component_by_class(u.StaticMeshComponent);t=a.get_component_by_class(u.TextRenderComponent)
 if (c and a.get_actor_label().startswith(('Puerta','Instrumento'))) or (t and any(x in str(t.text) for x in ['kg','HX711','GLP'])):
  p=a.get_actor_location();out.append({'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name() if c and c.static_mesh else None,'position':[p.x,p.y,p.z],'text':str(t.text) if t else None})
Path('D:/Unreal/ElPuestitoPiloto/Evidence/spatial-before.json').write_text(json.dumps(out,indent=2))
