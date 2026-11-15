"""Capture settled real-time PIE frames; high-res captures reset temporal history."""
import unreal as u
import time,json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve()
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not levels.is_in_play_in_editor()
d=json.loads((root/'Evidence/bulb-user-camera.json').read_text())
r=d['rotation']
original=(u.Vector(*d['location']),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]))
def point(x,y,z):return u.Vector((x-4.8)*100,(z-24.6)*100,y*100)
views=[('comedor-aesthetic',*original)]
for name,p,t in [('techado-aesthetic',(3.7,1.7,29.8),(1.6,1.1,21.3)),('patio-aesthetic',(4.3,1.6,20.6),(6.5,1.2,29.5))]:
    views.append((name,point(*p),u.MathLibrary.find_look_at_rotation(point(*p),point(*t))))
state={'at':time.monotonic(),'index':0,'stage':'start'}
levels.editor_request_begin_play()
def tick_aesthetic(delta):
    if time.monotonic()-state['at']<8:return
    try:
        if state['stage'] in ['start','move']:
            w=u.EditorLevelLibrary.get_pie_worlds(False)[0]
            u.GameplayStatics.get_player_pawn(w,0).set_actor_location(views[state['index']][1],False,True)
            u.GameplayStatics.get_player_controller(w,0).set_control_rotation(views[state['index']][2])
            state['stage']='capture'
        elif state['stage']=='capture':
            w=u.EditorLevelLibrary.get_pie_worlds(False)[0]
            u.SystemLibrary.execute_console_command(w,'Shot filename='+str(root/'Evidence'/views[state['index']][0])+'.png')
            state['stage']='verify'
        elif state['stage']=='verify':
            assert list((root/'Evidence').glob(views[state['index']][0]+'*.png'))
            state['index']+=1
            if state['index']==len(views):
                levels.editor_request_end_play();state['stage']='stop'
            else:state['stage']='move'
        elif state['stage']=='stop':
            u.EditorLevelLibrary.set_level_viewport_camera_info(*original)
            u.unregister_slate_post_tick_callback(aesthetic_handle)
            u.log('AESTHETIC_FINAL_CAPTURES_OK')
        state['at']=time.monotonic()
    except Exception as exc:
        u.unregister_slate_post_tick_callback(aesthetic_handle)
        levels.editor_request_end_play()
        u.log_error('AESTHETIC_CAPTURE_ERROR '+str(exc))
aesthetic_handle=u.register_slate_post_tick_callback(tick_aesthetic)
