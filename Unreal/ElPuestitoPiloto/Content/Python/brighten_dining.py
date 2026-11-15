"""Even, warm illumination across the covered tables, patio and circulation."""
import json
from pathlib import Path
import unreal as u

root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert u.EditorLevelLibrary.get_editor_world().get_name()=='RestauranteNoche'

def point(x,y,z):return u.Vector((x-4.8)*100,(z-24.6)*100,y*100)

for a in ed.get_all_level_actors():
    if 'DiningEvenLighting' in [str(t) for t in a.tags]:
        ed.destroy_actor(a)
        continue
    c=a.get_component_by_class(u.LightComponent)
    if not c:continue
    name=a.get_actor_label()
    if name.startswith('Guirnalda calida'):
        c.set_intensity(850 if name.endswith('acceso') else 1100)
        c.set_editor_property('attenuation_radius',450)
        c.set_editor_property('temperature',3200)
        c.set_editor_property('indirect_lighting_intensity',2)
    elif name.startswith('Panel comedor cubierto'):
        c.set_intensity(2100)
        c.set_editor_property('attenuation_radius',600)
        c.set_editor_property('source_width',120)
        c.set_editor_property('source_height',80)
        c.set_editor_property('temperature',3500)
        c.set_editor_property('indirect_lighting_intensity',2)

for index,z in enumerate([20.0,24.4,28.7],1):
    a=ed.spawn_actor_from_class(u.RectLight,point(6.7,2.35,z))
    a.set_actor_label('Luz uniforme mesas '+str(index))
    a.tags=['RestaurantOwned','DiningEvenLighting']
    a.set_actor_rotation(u.Rotator(pitch=-90,yaw=0,roll=0),False)
    c=a.get_component_by_class(u.RectLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
    c.set_intensity(2400)
    c.set_editor_property('use_temperature',True)
    c.set_editor_property('temperature',3500)
    c.set_editor_property('source_width',250)
    c.set_editor_property('source_height',180)
    c.set_editor_property('attenuation_radius',650)
    c.set_editor_property('max_draw_distance',2500)
    c.set_editor_property('indirect_lighting_intensity',2)
    c.set_cast_shadows(True)

# Low energy, local bounce fills keep circulation readable below the tables.
for index,z in enumerate([20.5,24.4,28.3],1):
    a=ed.spawn_actor_from_class(u.RectLight,point(4.2,1.55,z))
    a.set_actor_label('Rebote pasillo mesas '+str(index))
    a.tags=['RestaurantOwned','DiningEvenLighting']
    a.set_actor_rotation(u.Rotator(pitch=-90,yaw=0,roll=0),False)
    c=a.get_component_by_class(u.RectLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
    c.set_intensity(250)
    c.set_editor_property('use_temperature',True)
    c.set_editor_property('temperature',3800)
    c.set_editor_property('source_width',180)
    c.set_editor_property('source_height',180)
    c.set_editor_property('attenuation_radius',300)
    c.set_editor_property('max_draw_distance',2200)
    c.set_cast_shadows(False)

levels.save_current_level()
u.log('DINING_EVEN_LIGHTING_SAVED')
