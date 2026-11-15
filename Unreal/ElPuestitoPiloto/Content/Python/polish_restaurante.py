"""Balance room illumination and keep saved cameras at their reference poses."""
import json
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.EditorLevelLibrary.get_editor_world().get_name()=='RestauranteNoche'
levels.eject_pilot_level_actor()
def point(p):return u.Vector((p[0]-4.8)*100,(p[2]-24.6)*100,p[1]*100)
views=json.loads((root/'SourceAssets/RestauranteCompleto/views.json').read_text())
views['Cocina']=[(3.5,1.9,31.9),(1.65,1.05,33.3),78]
for a in ed.get_all_level_actors():
    if a.get_actor_label().startswith('Vista '):
        p,t,fov=views[a.get_actor_label()[6:]]
        a.set_actor_location(point(p),False,False)
        a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(point(p),point(t)),False)
    if 'RoomFill' in [str(t) for t in a.tags]:ed.destroy_actor(a)
    elif isinstance(a,u.RectLight) and 'RestaurantOwned' in [str(t) for t in a.tags]:
        c=a.get_component_by_class(u.RectLightComponent)
        # Set absolute values so repeated polishing never dims the scene again.
        target={'Luz Barra':750,'Luz Cocina':900,'Luz Bano hombres':650,'Luz Bano mujeres':650,'Luz Oficina':500,'Luz Bodega':500,'Luz Ross Tattoo Studio':1000}
        if a.get_actor_label() in target:c.set_intensity(target[a.get_actor_label()])
        c.set_editor_property('source_width',90)
        c.set_editor_property('source_height',40)
        c.set_editor_property('max_draw_distance',1300)
        c.set_editor_property('indirect_lighting_intensity',1.5)
for name,p,lumens,radius,kelvin in [
    ('Barra frente',(4.85,1.9,18.5),200,300,3600),
    ('Barra fondo',(2.8,1.7,16.6),95,220,3600),
    ('Cocina',(2.6,1.8,32.2),160,260,4300),
    ('Mujeres',(7.5,1.8,16.7),110,200,4300),
    ('Hombres',(7.5,1.8,14.3),110,200,4300),
    ('Oficina',(1.2,1.8,16.9),90,180,4300),
    ('Bodega',(4.8,1.8,32.0),90,200,4300),
    ('Estudio',(7.0,1.8,31.8),180,280,4300),
    ('Pasillo',(5.5,1.8,14.5),110,260,3800),
    ('Entrada',(5.4,1.8,5.2),140,320,3800),
]:
    a=ed.spawn_actor_from_class(u.RectLight,point(p))
    a.set_actor_label('Luz ambiente '+name);a.tags=['RestaurantOwned','RoomFill']
    a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(point(p),point((p[0],0,p[2]))),False)
    c=a.get_component_by_class(u.RectLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(lumens*.65)
    c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',kelvin)
    c.set_editor_property('attenuation_radius',radius)
    c.set_editor_property('source_width',50)
    c.set_editor_property('source_height',50)
    c.set_editor_property('max_draw_distance',1000)
    c.set_cast_shadows(True)
ed.set_selected_level_actors([])
levels.save_current_level()
u.log('RESTAURANTE_LIGHTING_BALANCED')
