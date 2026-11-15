"""A slow free camera with a compact collision sphere for the real doorways."""
import unreal as u
from pathlib import Path
import json
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.AssetToolsHelpers.get_asset_tools()
dest='/Game/RestauranteCompleto/Recorrido'
def blueprint(name,parent):
    bp=u.load_asset(dest+'/'+name)
    if not bp:
        factory=u.BlueprintFactory();factory.set_editor_property('parent_class',parent)
        bp=assets.create_asset(name,dest,u.Blueprint,factory)
        u.BlueprintEditorLibrary.compile_blueprint(bp)
    return bp
bp=blueprint('BP_CamaraRecorrido',u.DefaultPawn)
cls=u.BlueprintEditorLibrary.generated_class(bp)
default=u.get_default_object(cls)
sphere=default.get_component_by_class(u.SphereComponent)
assert 'BP_CamaraRecorrido' in sphere.get_path_name()
sphere.set_editor_property('sphere_radius',18)
movement=default.get_component_by_class(u.FloatingPawnMovement)
movement.set_editor_property('max_speed',220)
movement.set_editor_property('acceleration',850)
movement.set_editor_property('deceleration',1200)
u.BlueprintEditorLibrary.compile_blueprint(bp)
u.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
gm=blueprint('BP_RecorridoModo',u.GameModeBase)
u.get_default_object(u.BlueprintEditorLibrary.generated_class(gm)).set_editor_property('default_pawn_class',cls)
u.BlueprintEditorLibrary.compile_blueprint(gm)
u.EditorAssetLibrary.save_loaded_asset(gm,only_if_is_dirty=False)
world=u.EditorLevelLibrary.get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',u.BlueprintEditorLibrary.generated_class(gm))
start=next(a for a in ed.get_all_level_actors() if isinstance(a,u.PlayerStart))
start.set_actor_location(u.Vector(105,-1400,158),False,False)
start.set_actor_rotation(u.MathLibrary.find_look_at_rotation(start.get_actor_location(),u.Vector(30,-800,158)),False)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(Path(u.Paths.project_dir())/'Evidence/recorrido-config.json').write_text(json.dumps({'pawn':cls.get_path_name(),'sphere_radius_cm':sphere.get_unscaled_sphere_radius(),'speed_cm_s':movement.max_speed,'mode':'Free camera, WASD and vertical movement; not the Godot simulation controller'},indent=2))
u.log('RESTAURANTE_WALK_CONFIGURED')
