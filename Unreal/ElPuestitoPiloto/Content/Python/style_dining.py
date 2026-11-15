"""Warm, readable restaurant lighting with varnished wood and bulb reflections."""
import unreal as u
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
assert u.EditorLevelLibrary.get_editor_world().get_name()=='RestauranteNoche'
dest='/Game/RestauranteCompleto/Assets/restaurante_completo/Materials/'
for suffix,rough,normal in [('34',.62,.12),('35',.52,.10),('36',.50,.10),('41',.32,.12)]:
    mat=u.load_asset(dest+'M_Mobiliario_'+suffix)
    u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mat,'RoughnessFactor',rough)
    u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mat,'NormalScale',normal)
    if suffix=='41':
        u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mat,'BaseColorFactor',u.LinearColor(.72,.80,.88,1))
    u.MaterialEditingLibrary.update_material_instance(mat)
    u.EditorAssetLibrary.save_loaded_asset(mat)
for a in ed.get_all_level_actors():
    name=a.get_actor_label()
    c=a.get_component_by_class(u.LightComponent)
    if c:
        if name.startswith('Luz uniforme mesas'):
            c.set_intensity(1700)
            c.set_editor_property('temperature',3600)
            c.set_editor_property('specular_scale',0)
        elif name.startswith('Panel comedor cubierto'):
            c.set_intensity(1500)
            c.set_editor_property('specular_scale',.12)
        elif name.startswith('Guirnalda calida'):
            c.set_editor_property('specular_scale',1)
            c.set_editor_property('source_radius',6)
    if isinstance(a,u.PostProcessVolume):
        s=a.settings
        s.override_bloom_intensity=True;s.bloom_intensity=.55
        s.override_vignette_intensity=True;s.vignette_intensity=.10
        s.override_screen_space_reflection_intensity=True;s.screen_space_reflection_intensity=100
        s.override_screen_space_reflection_quality=True;s.screen_space_reflection_quality=75
        s.override_screen_space_reflection_max_roughness=True;s.screen_space_reflection_max_roughness=.7
        a.settings=s
    if 'DiningReflection' in [str(t) for t in a.tags]:ed.destroy_actor(a)

# Small local environment captures retain highlights when a bulb leaves screen.
for i,(x,z) in enumerate([(1.9,22.4),(1.9,27.4),(6.8,22.4),(6.8,27.4)],1):
    a=ed.spawn_actor_from_class(u.SphereReflectionCapture,u.Vector((x-4.8)*100,(z-24.6)*100,135))
    a.set_actor_label('Reflejos mesas '+str(i));a.tags=['RestaurantOwned','DiningReflection']
    c=a.get_component_by_class(u.SphereReflectionCaptureComponent)
    c.set_editor_property('influence_radius',340)
    c.set_editor_property('brightness',1)
    # Capture dynamic lights once at level start; no continuous recapture.
    c.set_editor_property('runtime_capture',True)
    c.refresh_capture(fast_render=False,smooth_blend=False)
levels.save_current_level()
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.log('DINING_AESTHETIC_SAVED')
