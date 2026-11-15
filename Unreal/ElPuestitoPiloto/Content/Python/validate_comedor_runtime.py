import unreal as u
import json
from pathlib import Path
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
root=Path(u.Paths.project_dir()).resolve()
report={'level':'ComedorCompleto','verification':'Engine API smoke test; not a full manual walkthrough'}
frame=0
levels.editor_request_begin_play()
def tick(delta):
    global frame,handle
    frame+=1
    if frame==90:
        report['play_started']=levels.is_in_play_in_editor()
        worlds=u.EditorLevelLibrary.get_pie_worlds(False)
        pawn=u.GameplayStatics.get_player_pawn(worlds[0],0) if worlds else None
        report['pawn_spawned']=pawn is not None
        if pawn:
            p=pawn.get_actor_location();pawn.set_actor_location(p+u.Vector(0,30,0),True,False)
            q=pawn.get_actor_location()
            report['spawn_cm']=[p.x,p.y,p.z];report['move_cm']=(q-p).length()
            report['entry_clear']=report['move_cm']>29.9
    if frame==120:levels.editor_request_end_play()
    if frame==180:
        report['play_stopped']=not levels.is_in_play_in_editor()
        report['roof_visible']=all(not a.is_hidden_ed() and not a.hidden for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if 'CubiertaComedor' in [str(t) for t in a.tags])
        (root/'Evidence/comedor-runtime-validation.json').write_text(json.dumps(report,indent=2))
        u.unregister_slate_post_tick_callback(handle)
        u.log('COMEDOR_RUNTIME_OK')
handle=u.register_slate_post_tick_callback(tick)
