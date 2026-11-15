"""Run inside Unreal Editor: py <project>/Content/Python/build_pilot.py.

Imports only the extracted dining sample and creates its own level. Does not
modify the Godot project, POS, or any other Unreal project.
"""
import json
from pathlib import Path
import unreal as ue

ROOT = Path(ue.Paths.project_dir()).resolve()
DEST = "/Game/ComedorCompleto/Assets"
MAP = "/Game/ComedorCompleto/ComedorCompleto"
assets = ue.AssetToolsHelpers.get_asset_tools()
editor = ue.get_editor_subsystem(ue.EditorActorSubsystem)
levels = ue.get_editor_subsystem(ue.LevelEditorSubsystem)


def spawn(cls, name, position=(0, 0, 0), rotation=(0, 0, 0)):
    actor = editor.spawn_actor_from_class(cls, ue.Vector(*position), ue.Rotator(*rotation))
    if actor is None:
        raise RuntimeError("Could not create " + name)
    actor.set_actor_label(name)
    return actor


def component(actor, cls):
    return actor.get_component_by_class(cls)


def build():
    task = ue.AssetImportTask()
    task.filename = str(ROOT / "SourceAssets/ComedorCompleto" / "comedor_completo.glb")
    task.destination_path = DEST
    task.automated = True
    task.replace_existing = True
    task.save = True
    task.async_ = False
    if not ue.EditorAssetLibrary.does_directory_exist(DEST):
        assets.import_asset_tasks([task])
    imported = [ue.load_asset(p) for p in ue.EditorAssetLibrary.list_assets(DEST, recursive=True)]
    meshes = [a for a in imported if isinstance(a, ue.StaticMesh)]
    if len(meshes) != 44:
        raise RuntimeError(f"Expected 44 material batches, imported {len(meshes)} meshes")
    texture_report = []
    for texture in imported:
        if isinstance(texture, ue.Texture2D):
            texture.set_editor_property("max_texture_size", 2048)
            texture.set_editor_property("mip_gen_settings", ue.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
            texture_report.append(texture.get_name())
            ue.EditorAssetLibrary.save_loaded_asset(texture)
    if ue.EditorAssetLibrary.does_asset_exist(MAP):
        levels.load_level(MAP)
        for actor in editor.get_all_level_actors():
            if "PilotOwned" in [str(t) for t in actor.tags]:
                editor.destroy_actor(actor)
    else:
        levels.new_level(MAP)

    bounds = []
    for mesh in meshes:
        actor = spawn(ue.StaticMeshActor, mesh.get_name())
        actor.tags = ["PilotOwned"]
        comp = component(actor, ue.StaticMeshComponent)
        comp.set_static_mesh(mesh)
        comp.set_mobility(ue.ComponentMobility.STATIC)
        # Triangle collision is appropriate for this small static architecture.
        body = mesh.get_editor_property("body_setup")
        if body:
            body.set_editor_property("collision_trace_flag", ue.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        bounds_origin, extent = actor.get_actor_bounds(False)
        bounds.append({"name":mesh.get_name(), "origin":[bounds_origin.x,bounds_origin.y,bounds_origin.z],
                       "extent":[extent.x,extent.y,extent.z]})
        ue.EditorAssetLibrary.save_loaded_asset(mesh)

    wall_bounds = next(b for b in bounds if "Pared" in b["name"])
    wx,wy,_ = wall_bounds["origin"]
    horizontal_length = (wx*wx + wy*wy)**0.5
    inward = ue.Vector(1, 0, 0)
    along = ue.Vector(-inward.y, inward.x, 0)
    def point(x,y,z):
        return inward*x + along*y + ue.Vector(0,0,z)
    sun_rotation = ue.MathLibrary.find_look_at_rotation(point(700,350,850), ue.Vector(0,0,0))
    sun = spawn(ue.DirectionalLight, "Sol suave del patio")
    sun.set_actor_rotation(sun_rotation, False)
    sun_comp = component(sun, ue.DirectionalLightComponent)
    sun_comp.set_mobility(ue.ComponentMobility.MOVABLE)
    sun_comp.set_intensity(3.0)
    sun_comp.set_editor_property("use_temperature", True)
    sun_comp.set_editor_property("temperature", 5600.0)
    sun_comp.set_editor_property("light_source_angle", 2.0)
    sun_comp.set_editor_property("atmosphere_sun_light", True)
    sky_atmosphere = spawn(ue.SkyAtmosphere, "Cielo del patio")
    sky = spawn(ue.SkyLight, "Luz ambiente exterior")
    sky_comp = component(sky, ue.SkyLightComponent)
    sky_comp.set_mobility(ue.ComponentMobility.MOVABLE)
    sky_comp.set_editor_property("real_time_capture", True)
    sky_comp.set_intensity(0.65)

    # Initial camera and lamp coordinates are validated against the imported
    # mesh bounds before the final capture; glTF uses metres, UE centimetres.
    lighting = []
    for index, distance in enumerate([-110,130]):
        lamp = spawn(ue.PointLight, f"Luz calida comedor {index+1}")
        lamp.set_actor_location(point(-15,distance,285),False,False)
        light = component(lamp, ue.PointLightComponent)
        light.set_mobility(ue.ComponentMobility.MOVABLE)
        light.set_editor_property("intensity_units", ue.LightUnits.LUMENS)
        light.set_intensity(180.0)
        light.set_editor_property("use_temperature", True)
        light.set_editor_property("temperature", 3200.0)
        light.set_editor_property("attenuation_radius", 400.0)
        light.set_editor_property("source_radius", 6.0)
        light.set_editor_property("soft_source_radius", 10.0)
        lighting.append(lamp)

    pp = spawn(ue.PostProcessVolume, "Acabado fotografico")
    pp.set_editor_property("unbound", True)
    settings = pp.get_editor_property("settings")
    settings.set_editor_property("override_auto_exposure_method", True)
    settings.set_editor_property("auto_exposure_method", ue.AutoExposureMethod.AEM_MANUAL)
    settings.set_editor_property("override_auto_exposure_apply_physical_camera_exposure", True)
    settings.set_editor_property("auto_exposure_apply_physical_camera_exposure", False)
    settings.set_editor_property("override_auto_exposure_bias", True)
    settings.set_editor_property("auto_exposure_bias", 0.0)
    settings.set_editor_property("override_bloom_intensity", True)
    settings.set_editor_property("bloom_intensity", 0.12)
    settings.set_editor_property("override_vignette_intensity", True)
    settings.set_editor_property("vignette_intensity", 0.12)
    pp.set_editor_property("settings", settings)

    camera_pos = point(330,390,205)
    target = point(-20,0,135)
    rotation = ue.MathLibrary.find_look_at_rotation(camera_pos, target)
    camera = spawn(ue.CameraActor, "Camara comparacion")
    camera.set_actor_location(camera_pos, False, False)
    camera.set_actor_rotation(rotation, False)
    cam = component(camera, ue.CameraComponent)
    cam.set_field_of_view(65.0)
    cam.set_editor_property("aspect_ratio", 16/9)
    start = spawn(ue.PlayerStart, "Inicio del recorrido")
    start.set_actor_location(point(145,220,170),False,False)
    start.set_actor_rotation(rotation, False)
    for actor in [sun, sky, sky_atmosphere, pp, camera, start] + lighting:
        actor.tags = ["PilotOwned"]
    ue.EditorLevelLibrary.set_level_viewport_camera_info(camera_pos, rotation)
    editor.set_selected_level_actors([])
    levels.save_current_level()
    ue.EditorAssetLibrary.save_directory("/Game/ComedorCompleto", only_if_is_dirty=True, recursive=True)
    report = {"map":MAP,"meshes":bounds,"textures":texture_report,"status":"built_needs_visual_review"}
    (ROOT / "Evidence" / "comedor-import.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    ue.log("PUESTO_PILOT_BUILD_OK")


build()
exec((ROOT / 'Content/Python/polish_comedor.py').read_text(encoding='utf-8'))

