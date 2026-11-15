"""Open the saved pilot in a clean, freely navigable editor viewport."""
import unreal as u
# Editor startup hooks also run for uncooked -game launches.
if "-game" not in u.SystemLibrary.get_command_line().lower().split():
    ed=u.get_editor_subsystem(u.EditorActorSubsystem)
    levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
    world_name=u.EditorLevelLibrary.get_editor_world().get_name()
    view='Vista Barra' if world_name=='RestauranteNoche' else ('Camara comparacion' if world_name=='ComedorNoche' else 'Camara general')
    camera=next((a for a in ed.get_all_level_actors() if a.get_actor_label()==view),None)
    if camera:
        world=u.EditorLevelLibrary.get_editor_world()
        for command in ['sg.GlobalIlluminationQuality 2','sg.ShadowQuality 2','sg.ReflectionQuality 2','sg.PostProcessQuality 2','sg.EffectsQuality 2']:
            u.SystemLibrary.execute_console_command(world,command)
        u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
        levels.editor_set_game_view(True)
        levels.editor_set_viewport_realtime(True)
        ed.set_selected_level_actors([])
