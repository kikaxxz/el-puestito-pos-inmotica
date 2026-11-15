"""Match ceiling illumination to the actual source luminaires."""
import unreal as u
import json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert u.EditorLevelLibrary.get_editor_world().get_name()=='RestauranteNoche'
actors=ed.get_all_level_actors()
for a in actors:
    if 'LuminousPanel' in [str(t) for t in a.tags] or 'TaskLighting' in [str(t) for t in a.tags]:ed.destroy_actor(a)
    if 'RestaurantOwned' in [str(t) for t in a.tags]:
        c=a.get_component_by_class(u.LightComponent)
        if c and 'Barra' not in a.get_actor_label() and 'Entrada' not in a.get_actor_label() and 'Acceso' not in a.get_actor_label() and 'Pasillo' not in a.get_actor_label():
            c.set_editor_property('temperature',5000)
        if a.get_actor_label()=='Luz Bano hombres':c.set_intensity(450)
        if isinstance(a,u.RectLight):
            # Ceiling-to-floor distance exceeds several original light radii.
            # Keep walls occluding the light, but let it reach the floor.
            c.set_editor_property('attenuation_radius',450 if a.get_actor_label() in ['Luz Cocina','Luz Barra','Luz Ross Tattoo Studio'] else 380)
        if 'RoomFill' in [str(t) for t in a.tags]:
            c.set_editor_property('attenuation_radius',max(300,c.attenuation_radius))
        if a.get_actor_label()=='Luz ambiente Cocina':
            c.set_intensity(170)
            c.set_editor_property('attenuation_radius',350)
fixtures=json.loads((root/'SourceAssets/RestauranteCompleto/details.json').read_text())['fixtures']
mapping=['Luz Acceso 1','Luz Acceso 2','Luz Pasillo','Panel comedor cubierto 1','Panel comedor cubierto 2','Panel comedor cubierto 3','Luz Bano hombres','Luz Bano mujeres','Luz Oficina','Luz Bodega','Luz Cocina','Luz Ross Tattoo Studio','Luz Barra']
dest='/Game/RestauranteCompleto'
m=u.load_asset(dest+'/M_PanelLED')
if not m:
    m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_PanelLED',dest,u.Material,u.MaterialFactoryNew())
    color=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector)
    color.set_editor_property('constant',u.LinearColor(12,11,9,1))
    u.MaterialEditingLibrary.connect_material_property(color,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
    m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property('two_sided',True)
    u.MaterialEditingLibrary.recompile_material(m)
    u.EditorAssetLibrary.save_loaded_asset(m)
def point(p):return u.Vector((p[0]-4.8)*100,(p[2]-24.6)*100,p[1]*100)
for f,label in zip(fixtures,mapping):
    lo,hi=f['min'],f['max'];p=[(lo[i]+hi[i])/2 for i in range(3)];p[1]=lo[1]-.001
    a=ed.spawn_actor_from_class(u.StaticMeshActor,point(p))
    a.set_actor_label('Difusor LED '+f['name']);a.tags=['RestaurantOwned','LuminousPanel']
    a.set_actor_enable_collision(False)
    c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Plane'))
    c.set_material(0,m);c.set_cast_shadow(False);c.set_collision_profile_name('NoCollision')
    a.set_actor_scale3d(u.Vector(hi[0]-lo[0]-.03,hi[2]-lo[2]-.025,1))
    light=next(x for x in actors if x.get_actor_label()==label)
    p[1]-=.025
    light.set_actor_location(point(p),False,False)
    lc=light.get_component_by_class(u.RectLightComponent)
    lc.set_editor_property('source_width',(hi[0]-lo[0]-.03)*100)
    lc.set_editor_property('source_height',(hi[2]-lo[2]-.025)*100)
# The cubicle partitions block the common ceiling light. Small local ceiling
# lights keep those enclosed spaces usable without allowing light through walls.
for name,p,energy,radius in [
    ('Urinario',(9.05,2.77,14.05),120,360),
    ('Cabina central',(9.05,2.78,16.25),100,340),
    ('Cabina final',(9.05,2.78,17.45),100,340),
    ('Trabajo cocina',(1.15,3.0,33.8),350,400),
]:
    a=ed.spawn_actor_from_class(u.RectLight,point(p));a.set_actor_label('Luz local '+name)
    a.tags=['RestaurantOwned','TaskLighting']
    a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(point(p),point((p[0],0,p[2]))),False)
    c=a.get_component_by_class(u.RectLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(energy*.65)
    c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',5000)
    c.set_editor_property('attenuation_radius',radius);c.set_editor_property('source_width',16);c.set_editor_property('source_height',16)
    c.set_editor_property('max_draw_distance',900);c.set_cast_shadows(True)
    panel=ed.spawn_actor_from_class(u.StaticMeshActor,point((p[0],p[1]+.03,p[2])))
    panel.set_actor_label('Plafon auxiliar '+name);panel.tags=['RestaurantOwned','TaskLighting']
    panel.set_actor_enable_collision(False)
    pc=panel.get_component_by_class(u.StaticMeshComponent);pc.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cylinder'))
    pc.set_material(0,m);pc.set_cast_shadow(False);pc.set_collision_profile_name('NoCollision')
    panel.set_actor_scale3d(u.Vector(.16,.16,.012))
levels.save_current_level()
u.log('RESTAURANTE_FIXTURE_LIGHTS_OK')
