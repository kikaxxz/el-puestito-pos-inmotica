import json
from pathlib import Path
import unreal as u

root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.EditorLevelLibrary.get_editor_world()
general=next(a for a in ed.get_all_level_actors() if a.get_actor_label()=='Camara general')
close=next(a for a in ed.get_all_level_actors() if a.get_actor_label()=='Camara comparacion')
u.EditorLevelLibrary.set_level_viewport_camera_info(general.get_actor_location(),general.get_actor_rotation())
levels.editor_set_game_view(True)
levels.editor_set_viewport_realtime(True)
frame=0
report={'status':'running','manual_keyboard_test':'pending_windows_firewall_dialog'}

def tick(delta):
    global frame, handle
    frame+=1
    if frame==120:
        u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(root/'Evidence/unreal-general-final.png'),camera=general)
    if frame==240:
        u.EditorLevelLibrary.set_level_viewport_camera_info(close.get_actor_location(),close.get_actor_rotation())
        u.SystemLibrary.execute_console_command(world,'csvprofile frames=300')
    if frame==600:
        levels.editor_request_begin_play()
    if frame==720:
        report['pie_running']=levels.is_in_play_in_editor()
        worlds=u.EditorLevelLibrary.get_pie_worlds(False)
        report['pie_worlds']=len(worlds)
        if worlds:
            pawn=u.GameplayStatics.get_player_pawn(worlds[0],0)
            report['pawn_class']=pawn.get_class().get_name() if pawn else None
            if pawn:
                start=pawn.get_actor_location()
                target=start+u.Vector(0,-35,0)
                pawn.set_actor_location(target,True,False)
                end=pawn.get_actor_location()
                report['initial_position']=[start.x,start.y,start.z]
                report['after_swept_move']=[end.x,end.y,end.z]
                report['movement_cm']=(end-start).length()
    if frame==780:
        levels.editor_request_end_play()
    if frame==840:
        report['pie_stopped']=not levels.is_in_play_in_editor()
        report['status']='completed'
        (root/'Evidence/runtime-validation.json').write_text(json.dumps(report,indent=2))
        u.EditorLevelLibrary.set_level_viewport_camera_info(general.get_actor_location(),general.get_actor_rotation())
        levels.save_current_level()
        u.unregister_slate_post_tick_callback(handle)
        u.log('PUESTO_AUDIT_OK')

handle=u.register_slate_post_tick_callback(tick)
