"""Import the complete corrected restaurant into a separate night level."""
import json
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
DEST = '/Game/RestauranteCompleto/Assets'
MAP = '/Game/RestauranteCompleto/RestauranteNoche'
ed = u.get_editor_subsystem(u.EditorActorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError('Stop Play before building the restaurant')
manifest = json.loads((root/'SourceAssets/RestauranteCompleto/manifest.json').read_text())
if not u.EditorAssetLibrary.does_directory_exist(DEST):
    task = u.AssetImportTask()
    task.filename = str(root/'SourceAssets/RestauranteCompleto/restaurante_completo.glb')
    task.destination_path = DEST
    task.automated = True
    task.save = True
    task.async_ = False
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
imported = [u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(DEST, recursive=True)]
meshes = [a for a in imported if isinstance(a, u.StaticMesh)]
assert len(meshes) == manifest['material_batches'], (len(meshes), manifest['material_batches'])
if not u.EditorAssetLibrary.does_asset_exist(MAP):
    assert levels.new_level_from_template(MAP, '/Game/ComedorCompleto/ComedorNoche')
elif u.EditorLevelLibrary.get_editor_world().get_name() != 'RestauranteNoche':
    assert levels.load_level(MAP)
for a in ed.get_all_level_actors():
    tags = [str(t) for t in a.tags]
    if 'RestaurantOwned' in tags or (isinstance(a, u.StaticMeshActor) and 'NightOwned' not in tags):
        ed.destroy_actor(a)

def point(p):
    return u.Vector((p[0]-4.8)*100, (p[2]-24.6)*100, p[1]*100)

def spawn(cls, name, p):
    a = ed.spawn_actor_from_class(cls, p)
    a.set_actor_label(name)
    a.tags = ['RestaurantOwned']
    return a

textures = 0
for asset in imported:
    if isinstance(asset, u.Texture2D):
        asset.set_editor_property('max_texture_size', 2048)
        asset.set_editor_property('mip_gen_settings', u.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
        textures += 1
for mesh in meshes:
    a = spawn(u.StaticMeshActor, mesh.get_name(), u.Vector())
    c = a.get_component_by_class(u.StaticMeshComponent)
    c.set_static_mesh(mesh)
    c.set_mobility(u.ComponentMobility.STATIC)
    body = mesh.get_editor_property('body_setup')
    if body:
        body.set_editor_property('collision_trace_flag', u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    if mesh.get_name().startswith('Instrumento'):
        a.set_actor_enable_collision(False)
    if mesh.get_name().startswith('Mobiliario'):
        m = c.get_material(0)
        if isinstance(m, u.MaterialInstanceConstant) and 'bambu' in str(m.get_editor_property('texture_parameter_values')).lower():
            u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(m, 'BaseColorFactor', u.LinearColor(.55,.62,.72,1))
            u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(m, 'NormalScale', .18)
    if mesh.get_name().startswith('Techo'):
        a.tags = ['RestaurantOwned', 'CubiertaRestaurante']

# Modest pools of light, confined to each room to avoid lighting through walls.
lights = [
    ('Acceso 1', (5.4,2.65,3), 950, 280, 3700, False),
    ('Acceso 2', (5.4,2.65,7), 950, 280, 3700, False),
    ('Pasillo', (5.4,2.65,11), 950, 270, 3700, True),
    ('Barra', (3.0,2.85,17.4), 1100, 290, 3300, True),
    ('Oficina', (1.05,2.65,16.5), 650, 185, 4000, True),
    ('Bano hombres', (8.3,2.6,14.45), 850, 225, 4000, True),
    ('Bano mujeres', (8.3,2.6,17.0), 850, 225, 4000, True),
    ('Cocina', (1.65,2.8,33.1), 1200, 295, 4000, True),
    ('Bodega', (4.75,2.7,33.2), 600, 200, 4000, True),
    ('Ross Tattoo Studio', (7.8,2.8,33.1), 1250, 310, 4000, True),
]
for name, p, lumens, radius, kelvin, shadows in lights:
    a = spawn(u.RectLight, 'Luz '+name, point(p))
    a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(point(p), point((p[0],0,p[2]))), False)
    c = a.get_component_by_class(u.RectLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units', u.LightUnits.LUMENS)
    c.set_intensity(lumens)
    c.set_editor_property('use_temperature', True)
    c.set_editor_property('temperature', kelvin)
    c.set_editor_property('attenuation_radius', radius)
    c.set_editor_property('source_width', 60)
    c.set_editor_property('source_height', 16)
    c.set_editor_property('max_draw_distance', 1800)
    c.set_cast_shadows(shadows)

views = {
    'Entrada': [(5.85,1.7,10.6),(4.9,1.65,3.7),75],
    'Barra': [(5.60,1.74,19.2),(3.12,1.35,16.35),72],
    'Patio': [(5.72,1.78,28.8),(8.55,1.6,20.2),76],
    'Mujeres': [(8.19,1.73,16.17),(6.90,1.36,17.16),84],
    'Hombres': [(7.75,1.75,14.08),(9.4,.95,14.01),82],
    'Oficina': [(.40,1.60,17.45),(1.26,1.08,16.05),80],
    'Bodega': [(4.62,1.83,31.67),(4.78,1.12,34.20),75],
    'Estudio': [(6.19,1.70,31.09),(7.69,1.32,33.91),78],
    'Cocina': [(3.50,2.30,31.50),(1.65,1.05,33.15),78],
    'Restaurante': [(24,29,47),(4.8,0,18),55],
}
for name, (p,t,fov) in views.items():
    a = spawn(u.CameraActor, 'Vista '+name, point(p))
    a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(point(p),point(t)), False)
    c = a.get_component_by_class(u.CameraComponent)
    c.set_field_of_view(fov)
    c.set_editor_property('aspect_ratio',16/9)
ed.set_selected_level_actors([])
cam = next(a for a in ed.get_all_level_actors() if a.get_actor_label()=='Vista Barra')
u.EditorLevelLibrary.set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
levels.editor_set_game_view(True)
levels.save_current_level()
u.EditorAssetLibrary.save_directory('/Game/RestauranteCompleto',only_if_is_dirty=True,recursive=True)
(root/'Evidence/restaurante-build.json').write_text(json.dumps({'map':MAP,'meshes':len(meshes),'textures':textures,'triangles':manifest['triangles'],'doors_open':len(manifest['doors']),'views':list(views),'status':'built_needs_visual_review'},indent=2))
u.log('RESTAURANTE_BUILD_OK')

for helper in ['add_restaurante_labels.py','setup_restaurante_walk.py','polish_restaurante.py','finish_restaurante_lights.py','fix_restaurante_bulbs.py','fix_dining_floor.py','brighten_dining.py','style_dining.py']:
    exec(compile((root/'Content/Python'/helper).read_text(encoding='utf-8-sig'),helper,'exec'),{'__name__':'__build_helper__'})
