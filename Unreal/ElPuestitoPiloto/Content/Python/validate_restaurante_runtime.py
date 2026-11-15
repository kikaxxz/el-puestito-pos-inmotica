"""Verify saved pawn settings and crossings through all seven open doors."""
import unreal as u
from pathlib import Path
import json,time
root=Path(u.Paths.project_dir()).resolve()
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
assert u.EditorLevelLibrary.get_editor_world().get_name()=='RestauranteNoche'
levels.eject_pilot_level_actor()
start=next(a for a in ed.get_all_level_actors() if isinstance(a,u.PlayerStart))
u.EditorLevelLibrary.set_level_viewport_camera_info(start.get_actor_location(),start.get_actor_rotation())
levels.editor_request_begin_play()
state={'time':time.monotonic(),'stage':0,'done':False}
report={'level':'RestauranteNoche','verification':'Engine collision sweeps, not a full manual walkthrough','doors':[]}
def point(p):return u.Vector((p[0]-4.8)*100,(p[2]-24.6)*100,p[1]*100)
def tick(delta):
    if state['done']:return
    if state['stage']==0 and time.monotonic()-state['time']>5:
        try:
            worlds=u.EditorLevelLibrary.get_pie_worlds(False)
            pawn=u.GameplayStatics.get_player_pawn(worlds[0],0)
            report['pawn_class']=pawn.get_class().get_name()
            report['mode']=str(u.GameplayStatics.get_game_mode(worlds[0]))
            report['world_mode']=str(worlds[0].get_world_settings().default_game_mode)
            report['mode_pawn']=str(u.GameplayStatics.get_game_mode(worlds[0]).default_pawn_class)
            report['radius_cm']=pawn.get_component_by_class(u.SphereComponent).get_unscaled_sphere_radius()
            report['speed_cm_s']=pawn.get_component_by_class(u.FloatingPawnMovement).max_speed
            for door in json.loads((root/'SourceAssets/RestauranteCompleto/details.json').read_text())['doors']:
                lo,hi=door['min'],door['max']
                p=[(lo[i]+hi[i])/2 for i in range(3)];p[1]=lo[1]+1.5
                axis=0 if hi[0]-lo[0]<hi[2]-lo[2] else 2
                a=p.copy();b=p.copy();a[axis]-=.3;b[axis]+=.3
                pawn.set_actor_location(point(a),False,True)
                hit=pawn.set_actor_location(point(b),True,False)
                remaining=(pawn.get_actor_location()-point(b)).length()
                report['doors'].append({'name':door['name'],'remaining_cm':remaining,'clear':remaining<1,'hit':hit.export_text() if hit else 'None'})
            report['ok']=report['radius_cm']==18 and all(d['clear'] for d in report['doors'])
        except Exception as e:
            report['error']=str(e);report['ok']=False
        finally:
            levels.editor_request_end_play();state['stage']=1;state['time']=time.monotonic()
    elif state['stage']==1 and time.monotonic()-state['time']>4:
        report['play_stopped']=not levels.is_in_play_in_editor()
        (root/'Evidence/restaurante-runtime-validation.json').write_text(json.dumps(report,indent=2))
        state['done']=True;u.unregister_slate_post_tick_callback(handle)
        u.log('RESTAURANTE_RUNTIME_OK' if report['ok'] else 'RESTAURANTE_RUNTIME_FAILED')
handle=u.register_slate_post_tick_callback(tick)
