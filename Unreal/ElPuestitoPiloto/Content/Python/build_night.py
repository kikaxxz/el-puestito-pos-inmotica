"""Create a separately saved, performant night lighting variant."""
import json
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
DAY='/Game/ComedorCompleto/ComedorCompleto'
NIGHT='/Game/ComedorCompleto/ComedorNoche'
DEST='/Game/ComedorCompleto/Noche'
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError('End Play mode before creating the night level')
if not u.EditorAssetLibrary.does_asset_exist(NIGHT):
    if not levels.new_level_from_template(NIGHT,DAY):raise RuntimeError('Could not create night level from dining template')
elif u.EditorLevelLibrary.get_editor_world().get_name() != 'ComedorNoche':
    if not levels.load_level(NIGHT):raise RuntimeError('Could not load night level')
for a in ed.get_all_level_actors():
    if 'NightOwned' in [str(t) for t in a.tags]:ed.destroy_actor(a)
def spawn(cls,name,p):
    a=ed.spawn_actor_from_class(cls,p);a.set_actor_label(name);a.tags=['NightOwned'];return a
def material(name,color,base=(.1,.1,.1),unlit=False):
    path=DEST+'/'+name
    m=u.load_asset(path)
    if not m:
        m=u.AssetToolsHelpers.get_asset_tools().create_asset(name,DEST,u.Material,u.MaterialFactoryNew())
        c=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector)
        c.set_editor_property('constant',u.LinearColor(*color,1))
        u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
        b=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector)
        b.set_editor_property('constant',u.LinearColor(*base,1))
        u.MaterialEditingLibrary.connect_material_property(b,'',u.MaterialProperty.MP_BASE_COLOR)
        if unlit:
            m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
            m.set_editor_property('two_sided',True)
            m.set_editor_property('is_sky',True)
        u.MaterialEditingLibrary.recompile_material(m)
    return m
for a in ed.get_all_level_actors():
    c=a.get_component_by_class(u.LightComponent)
    if c:c.set_intensity(0)
    if isinstance(a,u.DirectionalLight):
        c=a.get_component_by_class(u.DirectionalLightComponent)
        c.set_intensity(1.2);c.set_editor_property('use_temperature',False)
        c.set_light_color(u.LinearColor(.3,.48,1,1))
        a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(700,-600,1400),u.Vector()),False)
        a.set_actor_label('Luz de luna')
    if isinstance(a,u.SkyLight):a.get_component_by_class(u.SkyLightComponent).set_intensity(.45)
    if isinstance(a,u.PostProcessVolume):
        s=a.settings;s.auto_exposure_bias=-3.8
        s.override_bloom_intensity=True;s.bloom_intensity=.4
        s.override_vignette_intensity=True;s.vignette_intensity=.2
        a.settings=s
old=next(a for a in ed.get_all_level_actors() if a.get_actor_label()=='Decoracion_14')
old.set_actor_hidden_in_game(True);old.set_is_temporarily_hidden_in_editor(True)
asset_paths=u.EditorAssetLibrary.list_assets(DEST+'/Guirnaldas',recursive=True)
if not asset_paths:
    task=u.AssetImportTask();task.filename=str(root/'SourceAssets/Noche/guirnaldas_noche.glb')
    task.destination_path=DEST+'/Guirnaldas';task.automated=True;task.save=True;task.async_=False
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    asset_paths=u.EditorAssetLibrary.list_assets(DEST+'/Guirnaldas',recursive=True)
bulb=material('M_BombillaCalida',(24,7.5,1.5),(.8,.5,.18))
panel=material('M_PanelCalido',(8,5,2.5),(.7,.6,.4))
sky_mat=material('M_CieloNocturno',(.14,.24,.6),unlit=True)
meshes=[u.load_asset(p) for p in asset_paths if isinstance(u.load_asset(p),u.StaticMesh)]
assert len(meshes)==2
for mesh in meshes:
    a=spawn(u.StaticMeshActor,mesh.get_name(),u.Vector())
    c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(mesh);c.set_mobility(u.ComponentMobility.STATIC)
    c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    a.set_actor_enable_collision(False)
    if 'Bombillas' in mesh.get_name():
        c.set_material(0,bulb);c.set_cast_shadow(False)
for a in ed.get_all_level_actors():
    if a.get_actor_label()=='Decoracion_38':a.get_component_by_class(u.StaticMeshComponent).set_material(0,panel)
sky=spawn(u.StaticMeshActor,'Cielo nocturno',u.Vector())
c=sky.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'))
c.set_material(0,sky_mat);c.set_cast_shadow(False);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
sky.set_actor_enable_collision(False)
sky.set_actor_scale3d(u.Vector(400,400,400))
positions=json.loads((root/'SourceAssets/Noche/bombillas.json').read_text())['positions_cm']
selected=[]
for p in sorted(positions,key=lambda p:(p[1],p[0])):
    if all(sum((p[k]-q[k])**2 for k in [0,1])>190**2 for q in selected):selected.append(p)
selected=selected[:10]
for i,p in enumerate(selected):
    a=spawn(u.PointLight,f'Guirnalda calida {i+1:02}',u.Vector(*p))
    c=a.get_component_by_class(u.PointLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(550)
    c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3000)
    c.set_editor_property('attenuation_radius',340);c.set_editor_property('source_radius',7)
    c.set_cast_shadows(i%3==0)
for i,y in enumerate([-440,0,440]):
    a=spawn(u.RectLight,f'Panel comedor cubierto {i+1}',u.Vector(-325,y,298))
    a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(a.get_actor_location(),u.Vector(-325,y,0)),False)
    c=a.get_component_by_class(u.RectLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(700)
    c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3300)
    c.set_editor_property('source_width',60);c.set_editor_property('source_height',12)
    c.set_editor_property('attenuation_radius',400);c.set_cast_shadows(True)
cam=next(a for a in ed.get_all_level_actors() if a.get_actor_label()=='Camara comparacion')
u.EditorLevelLibrary.set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
levels.editor_set_game_view(True);levels.editor_set_viewport_realtime(True)
ed.set_selected_level_actors([]);levels.save_current_level()
u.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=True,recursive=True)
(root/'Evidence/night-build.json').write_text(json.dumps({'level':NIGHT,'emissive_bulbs':len(positions),'point_lights':len(selected),'covered_area_panels':3,'shadow_casting_local_lights':sum(i%3==0 for i in range(len(selected)))+3,'day_level_preserved':True},indent=2))
u.log('NIGHT_BUILD_OK')

