"""Idempotent Unreal-specific finishes for the small dining pilot."""
import unreal as u

def polish():
    ed = u.get_editor_subsystem(u.EditorActorSubsystem)
    def find(name):
        return next((a for a in ed.get_all_level_actors() if a.get_actor_label()==name), None)
    def owned(cls,name,position):
        a=find(name) or ed.spawn_actor_from_class(cls,position)
        a.set_actor_label(name); a.tags=['PilotOwned']
        a.set_actor_location(position,False,False)
        return a
    for a in ed.get_all_level_actors():
        name=a.get_actor_label()
        if name.startswith('Piso'):
            c=a.get_component_by_class(u.StaticMeshComponent)
            c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
            m=u.load_asset('/Game/Piloto/Assets/comedor_piloto/Materials/M_'+name)
            c.set_material(0,m)
            if name=='Piso_01':
                a.set_actor_location(u.Vector(6.75,-5,3.57),False,False)
                a.set_actor_scale3d(u.Vector(3.835,5.3,.1))
            else:
                a.set_actor_location(u.Vector(199.25,-5,4),False,False)
                a.set_actor_scale3d(u.Vector(.015,5.3,.1))
            u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(m,'NormalScale',.25)
            u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(m,'RoughnessFactor',.9)
            u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(m,'OcclusionStrength',.8)
            u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(m,'BaseColorFactor',u.LinearColor(1,1,1,1))
        if name.startswith('Mobiliario'):
            m=a.get_component_by_class(u.StaticMeshComponent).get_material(0)
            u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(m,'BaseColorFactor',u.LinearColor(.55,.62,.72,1))
            u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(m,'NormalScale',.18)
        if isinstance(a,u.DirectionalLight):
            a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(700,350,2000),u.Vector()),False)
            a.get_component_by_class(u.DirectionalLightComponent).set_intensity(8000)
        if isinstance(a,u.SkyLight):
            a.get_component_by_class(u.SkyLightComponent).set_intensity(2)
        if isinstance(a,u.PostProcessVolume):
            s=a.settings; s.auto_exposure_bias=-9.2
            s.override_lumen_final_gather_quality=True; s.lumen_final_gather_quality=1
            a.settings=s
    fill=owned(u.RectLight,'Luz difusa del patio',u.Vector(450,0,280))
    fill.set_actor_rotation(u.MathLibrary.find_look_at_rotation(fill.get_actor_location(),u.Vector(-100,0,110)),False)
    c=fill.get_component_by_class(u.RectLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
    c.set_intensity(160000)
    c.set_editor_property('source_width',450); c.set_editor_property('source_height',300)
    c.set_editor_property('attenuation_radius',1400)
    # A neutral presentation stage; it is not part of the restaurant geometry.
    ground=owned(u.StaticMeshActor,'Base neutra de presentacion',u.Vector(0,0,-16))
    gc=ground.get_component_by_class(u.StaticMeshComponent)
    gc.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
    gc.set_mobility(u.ComponentMobility.STATIC)
    ground.set_actor_scale3d(u.Vector(1000,1000,.2))
    mat=u.load_asset('/Game/Piloto/M_BasePresentacion')
    if not mat:
        mat=u.AssetToolsHelpers.get_asset_tools().create_asset('M_BasePresentacion','/Game/Piloto',u.Material,u.MaterialFactoryNew())
        color=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant3Vector)
        color.set_editor_property('constant',u.LinearColor(.11,.13,.14,1))
        u.MaterialEditingLibrary.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
        rough=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant)
        rough.set_editor_property('r',.95)
        u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
        u.MaterialEditingLibrary.recompile_material(mat)
    gc.set_material(0,mat)
    cam=owned(u.CameraActor,'Camara general',u.Vector(660,690,450))
    cam.set_actor_rotation(u.MathLibrary.find_look_at_rotation(cam.get_actor_location(),u.Vector(0,0,150)),False)
    cam.get_component_by_class(u.CameraComponent).set_field_of_view(55)
    cam.get_component_by_class(u.CameraComponent).set_editor_property('aspect_ratio',16/9)
    u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    u.EditorAssetLibrary.save_directory('/Game/Piloto',only_if_is_dirty=True,recursive=True)
    u.log('PUESTO_POLISH_OK')

polish()
