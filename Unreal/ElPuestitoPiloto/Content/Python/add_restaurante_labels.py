"""Restore the source's fixed signs; instrument readings remain demonstrative."""
import json
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
assert u.EditorLevelLibrary.get_editor_world().get_name()=='RestauranteNoche'
for a in ed.get_all_level_actors():
    if 'RestaurantLabel' in [str(t) for t in a.tags]: ed.destroy_actor(a)
def direction(v): return u.Vector(v[0],v[2],v[1])
for i,item in enumerate(json.loads((root/'SourceAssets/RestauranteCompleto/details.json').read_text())['labels']):
    p=item['position']
    a=ed.spawn_actor_from_class(u.TextRenderActor,u.Vector((p[0]-4.8)*100,(p[2]-24.6)*100,p[1]*100))
    a.set_actor_label('Rotulo '+item['text'].replace('\n',' ')[:40])
    a.tags=['RestaurantOwned','RestaurantLabel']
    a.set_actor_enable_collision(False)
    a.set_actor_rotation(u.MathLibrary.make_rot_from_xz(direction(item['forward']),direction(item['up'])),False)
    c=a.get_component_by_class(u.TextRenderComponent)
    c.set_text(item['text'].replace('\n','<br>'))
    c.set_world_size(item['height_cm'])
    c.set_horizontal_alignment(u.HorizTextAligment.EHTA_CENTER)
    c.set_vertical_alignment(u.VerticalTextAligment.EVRTA_TEXT_CENTER)
    c.set_text_render_color(u.Color(*[round(min(1,max(0,x))*255) for x in item['color']]))
    c.set_cast_shadow(False)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('RESTAURANTE_LABELS_OK')
