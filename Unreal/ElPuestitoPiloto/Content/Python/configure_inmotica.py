"""Tag existing lights and instruments for the native simulation. Idempotent."""
import unreal as u
from pathlib import Path
import json
ed=u.get_editor_subsystem(u.EditorActorSubsystem);levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert levels.load_level('/Game/RestauranteCompleto/RestauranteNoche')
dest='/Game/RestauranteCompleto';m=u.load_asset(dest+'/M_LuminariaApagada')
if not m:
 m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_LuminariaApagada',dest,u.Material,u.MaterialFactoryNew())
 c=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector);c.set_editor_property('constant',u.LinearColor(.12,.13,.14,1))
 u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
 u.MaterialEditingLibrary.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m)
def zone(a):
 n=a.get_actor_label().lower();p=a.get_actor_location();x=p.x/100+4.8;z=p.y/100+24.6
 if any(k in n for k in ['guirnalda','mesas','comedor','bombillas','patio','plafon_553','plafon_554','plafon_555']):return 6
 if 'barra' in n:return 7
 if x>6.55 and 13.4<z<18.1:return 5 if z<15.75 else 4
 if z>30:return 1 if x<3.8 else 2 if x<5.8 else 9
 if x<2 and 15<z<18.5:return 3
 if x<4.8 and 15<z<19:return 7
 return 8
lights={};emitters={};metrics=[]
for a in ed.get_all_level_actors():
 tags=[str(t) for t in a.tags if not str(t).startswith(('Inmotica','Metric'))]
 l=a.get_component_by_class(u.LocalLightComponent)
 emitter=a.get_actor_label().startswith(('Difusor LED','Plafon auxiliar','BombillasGuirnalda'))
 if l or emitter:
  z=zone(a);tags.append('InmoticaZone'+str(z))
  if l: lights[a.get_actor_label()]=z
  if emitter: tags.append('InmoticaEmitter');emitters[a.get_actor_label()]=z
 t=a.get_component_by_class(u.TextRenderComponent)
 if t:
  text=str(t.text)
  tag='MetricPPM' if 'ppm' in text.lower() else 'MetricWeight' if '30.00 kg' in text else 'MetricBio' if 'ACERCAR DEDO' in text else None
  if tag:tags.append(tag);metrics.append(tag)
 a.tags=tags
levels.save_current_level()
(Path(u.Paths.project_dir())/'Evidence/inmotica-bindings.json').write_text(json.dumps({'lights':lights,'emitters':emitters,'metrics':metrics},indent=2))
u.log('PUESTItO_INMOTICA_TAGS_READY')
