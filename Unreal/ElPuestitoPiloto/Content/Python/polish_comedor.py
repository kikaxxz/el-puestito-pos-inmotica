"""Finish the complete dining area without changing its source layout."""
import unreal as u
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
def find(name):
    return next((a for a in ed.get_all_level_actors() if a.get_actor_label()==name),None)
def owned(cls,name,pos):
    a=find(name) or ed.spawn_actor_from_class(cls,pos)
    a.set_actor_label(name);a.tags=['PilotOwned'];a.set_actor_location(pos,False,False)
    return a
for a in ed.get_all_level_actors():
    if isinstance(a,u.DirectionalLight):
        a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(500,1000,2200),u.Vector()),False)
        a.get_component_by_class(u.DirectionalLightComponent).set_intensity(8000)
    if isinstance(a,u.SkyLight): a.get_component_by_class(u.SkyLightComponent).set_intensity(2)
    if isinstance(a,u.PostProcessVolume):
        s=a.settings;s.auto_exposure_bias=-9.2
        s.override_lumen_final_gather_quality=True;s.lumen_final_gather_quality=1
        a.settings=s
    c=a.get_component_by_class(u.StaticMeshComponent)
    if c and a.get_actor_label().startswith('Mobiliario'):
        m=c.get_material(0)
        if isinstance(m,u.MaterialInstanceConstant) and 'bambu' in str(m.get_editor_property('texture_parameter_values')).lower():
            u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(m,'BaseColorFactor',u.LinearColor(.55,.62,.72,1))
            u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(m,'NormalScale',.18)
    if c and a.get_actor_label().startswith('Techo'):
        m=c.get_material(0)
        rough=u.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(m,'RoughnessFactor')
        metallic=u.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(m,'MetallicFactor')
        if abs(rough-.54)<.005 and abs(metallic-.38)<.005:
            a.tags=['PilotOwned','CubiertaComedor']
fill=owned(u.RectLight,'Luz difusa del patio',u.Vector(0,0,300))
fill.set_actor_rotation(u.MathLibrary.find_look_at_rotation(fill.get_actor_location(),u.Vector(-480,0,150)),False)
c=fill.get_component_by_class(u.RectLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE)
c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(260000)
c.set_editor_property('source_width',1100);c.set_editor_property('source_height',280);c.set_editor_property('attenuation_radius',1800)
# Support lies below the original textured surfaces: no coincident polygons.
support=owned(u.StaticMeshActor,'Base bajo el pavimento',u.Vector(-4,10,-3))
c=support.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
c.set_mobility(u.ComponentMobility.STATIC);support.set_actor_scale3d(u.Vector(9.8,13,.1))
c.set_material(0,u.load_asset('/Game/Piloto/M_BasePresentacion'))
for name,pos,target,fov in [
    ('Camara general',u.Vector(1100,-1600,1650),u.Vector(0,0,100),55),
    ('Camara comparacion',u.Vector(20,-570,170),u.Vector(0,460,150),75),
    ('Camara patio',u.Vector(350,-560,170),u.Vector(80,450,150),75),
    ('Camara planta',u.Vector(0,0,2100),u.Vector(0,0,0),60)]:
    cam=owned(u.CameraActor,name,pos);cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(pos,target),False)
    c=cam.get_component_by_class(u.CameraComponent);c.set_field_of_view(fov);c.set_editor_property('aspect_ratio',16/9)
start=find('Inicio del recorrido')
start.set_actor_location(u.Vector(20,-570,170),False,False)
start.set_actor_rotation(find('Camara comparacion').get_actor_rotation(),False)
levels.editor_set_game_view(True)
cam=find('Camara general');u.EditorLevelLibrary.set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
levels.save_current_level()
u.EditorAssetLibrary.save_directory('/Game/ComedorCompleto',only_if_is_dirty=True,recursive=True)
u.log('COMEDOR_COMPLETO_BUILD_OK')
