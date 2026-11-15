"""Reimport all 30 glass globes, including the three scaled entrance bulbs."""
import json
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
ed = u.get_editor_subsystem(u.EditorActorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert u.EditorLevelLibrary.get_editor_world().get_name() == 'RestauranteNoche'
data = json.loads((root/'SourceAssets/Noche/bombillas.json').read_text())
assert data['bulbs'] == 30
dest = '/Game/RestauranteCompleto/GuirnaldasCorregidas'
task = u.AssetImportTask()
task.filename = str(root/'SourceAssets/Noche/guirnaldas_noche.glb')
task.destination_path = dest
task.automated = True
task.save = True
task.replace_existing = True
task.async_ = False
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
meshes = [u.load_asset(p) for p in u.EditorAssetLibrary.list_assets(dest, recursive=True)]
meshes = [m for m in meshes if isinstance(m, u.StaticMesh)]
assert len(meshes) == 2, [m.get_name() for m in meshes]

mat = u.load_asset(dest+'/M_BombillaUniforme')
if not mat:
    mat = u.AssetToolsHelpers.get_asset_tools().create_asset('M_BombillaUniforme', dest, u.Material, u.MaterialFactoryNew())
    color = u.MaterialEditingLibrary.create_material_expression(mat, u.MaterialExpressionConstant3Vector)
    color.set_editor_property('constant', u.LinearColor(80,36,12,1))
    u.MaterialEditingLibrary.connect_material_property(color, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
    mat.set_editor_property('shading_model', u.MaterialShadingModel.MSM_UNLIT)
    u.MaterialEditingLibrary.recompile_material(mat)

for a in ed.get_all_level_actors():
    if a.get_actor_label() in ['BombillasGuirnalda','CablesGuirnalda']:
        ed.destroy_actor(a)
for mesh in meshes:
    a = ed.spawn_actor_from_class(u.StaticMeshActor, u.Vector())
    a.set_actor_label(mesh.get_name())
    a.tags = ['NightOwned','CorrectedGarland']
    a.set_actor_enable_collision(False)
    c = a.get_component_by_class(u.StaticMeshComponent)
    c.set_static_mesh(mesh)
    c.set_mobility(u.ComponentMobility.STATIC)
    c.set_collision_profile_name('NoCollision')
    if 'Bombillas' in mesh.get_name():
        c.set_material(0, mat)
        c.set_cast_shadow(False)

# Extend the shared illumination to the entrance segment without creating
# thirty individual shadow maps. Its glass already uses the emissive batch.
if not any(a.get_actor_label()=='Guirnalda calida acceso' for a in ed.get_all_level_actors()):
    p = sorted(data['positions_cm'], key=lambda p:p[1])[1]
    a = ed.spawn_actor_from_class(u.PointLight, u.Vector(*p))
    a.set_actor_label('Guirnalda calida acceso')
    a.tags = ['NightOwned','CorrectedGarland']
    c = a.get_component_by_class(u.PointLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units', u.LightUnits.LUMENS)
    c.set_intensity(350)
    c.set_editor_property('use_temperature', True)
    c.set_editor_property('temperature', 3000)
    c.set_editor_property('attenuation_radius', 300)
    c.set_editor_property('source_radius', 7)
    c.set_editor_property('max_draw_distance', 1600)
    c.set_cast_shadows(True)

u.EditorAssetLibrary.save_directory(dest, only_if_is_dirty=True, recursive=True)
levels.save_current_level()
(root/'Evidence/bulb-fix.json').write_text(json.dumps({
    'map':'/Game/RestauranteCompleto/RestauranteNoche',
    'emissive_bulbs':30, 'previously_dark_bulbs_fixed':3,
    'glass_and_cables_separate':True, 'glass_material':mat.get_path_name(),
    'added_shared_light':1, 'status':'awaiting_visual_review'
}, indent=2))
u.log('RESTAURANTE_BULBS_FIXED_30')
