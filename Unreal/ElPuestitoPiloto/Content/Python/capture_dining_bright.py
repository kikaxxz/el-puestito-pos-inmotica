import unreal as u
import time,json
from pathlib import Path
root=Path(u.Paths.project_dir()).resolve()
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
assert not levels.is_in_play_in_editor()
def point(x,y,z):return u.Vector((x-4.8)*100,(z-24.6)*100,y*100)
user=json.loads((root/'Evidence/bulb-user-camera.json').read_text())
r=user['rotation']
user_pose=(u.Vector(*user['location']),u.Rotator(pitch=r[0],yaw=r[1],roll=r[2]))
cam=next(a for a in ed.get_all_level_actors() if a.get_actor_label()=='Vista Patio')
jobs=[('mesas-iluminadas-frente',*user_pose),
      ('mesas-iluminadas-patio',cam.get_actor_location(),cam.get_actor_rotation()),
      ('mesas-iluminadas-techado',point(3.7,1.7,29.8),u.MathLibrary.find_look_at_rotation(point(3.7,1.7,29.8),point(1.6,1.1,21.3))),
      ('mesas-iluminadas-pasillo',point(4.3,1.6,20.6),u.MathLibrary.find_look_at_rotation(point(4.3,1.6,20.6),point(4.3,1.2,29.5)))]
state={'index':0,'requested':0,'started':time.monotonic()}
def prepare():
    levels.eject_pilot_level_actor()
    u.EditorLevelLibrary.set_level_viewport_camera_info(jobs[state['index']][1],jobs[state['index']][2])
    levels.editor_set_game_view(True)
    levels.editor_set_viewport_realtime(True)
    ed.set_selected_level_actors([])
    state['started']=time.monotonic();state['requested']=0
def tick_dining_capture(delta):
    p=root/'Evidence'/(jobs[state['index']][0]+'.png')
    if not state['requested'] and time.monotonic()-state['started']>6:
        state['requested']=time.time()
        state['task']=u.AutomationLibrary.take_high_res_screenshot(1280,720,str(p),camera=None)
    elif state['requested'] and p.exists() and p.stat().st_mtime>=state['requested'] and state['task'].is_task_done():
        u.log('DINING_CAPTURE_OK '+p.name)
        state['index']+=1
        if state['index']==len(jobs):
            u.unregister_slate_post_tick_callback(dining_capture_handle)
            u.EditorLevelLibrary.set_level_viewport_camera_info(*user_pose)
            u.log('DINING_CAPTURE_ALL_OK')
        else:prepare()
    elif time.monotonic()-state['started']>120:
        u.unregister_slate_post_tick_callback(dining_capture_handle)
        u.log_error('DINING_CAPTURE_TIMEOUT')
prepare()
dining_capture_handle=u.register_slate_post_tick_callback(tick_dining_capture)
