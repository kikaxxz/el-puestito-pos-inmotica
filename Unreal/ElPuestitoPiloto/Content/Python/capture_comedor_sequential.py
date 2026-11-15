"""Wait for each image to be written before changing visibility or camera."""
import json, time
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
roof=[a for a in ed.get_all_level_actors() if 'CubiertaComedor' in [str(t) for t in a.tags]]
cams={a.get_actor_label():a for a in ed.get_all_level_actors() if isinstance(a,u.CameraActor)}
jobs=[('comedor-general.png','Camara general',False),('comedor-distribucion.png','Camara general',True),('comedor-recorrido.png','Camara comparacion',False)]
stage=0;frames=0;pending=None;requested=0
def prepare():
    global frames
    frames=0
    for a in roof:
        a.set_is_temporarily_hidden_in_editor(jobs[stage][2]);a.set_actor_hidden_in_game(jobs[stage][2])
    c=cams[jobs[stage][1]]
    u.EditorLevelLibrary.set_level_viewport_camera_info(c.get_actor_location(),c.get_actor_rotation())
def tick(delta):
    global frames,stage,pending,requested,handle
    frames+=1
    target=root/'Evidence'/jobs[stage][0]
    if pending is None and frames>=90:
        requested=time.time()
        pending=u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(target),camera=cams[jobs[stage][1]])
    elif pending is not None and target.exists() and target.stat().st_mtime>=requested:
        u.log('COMEDOR_IMAGE_OK '+target.name)
        stage+=1;pending=None
        if stage==len(jobs):
            for a in roof:
                a.set_is_temporarily_hidden_in_editor(False);a.set_actor_hidden_in_game(False)
            c=cams['Camara general'];u.EditorLevelLibrary.set_level_viewport_camera_info(c.get_actor_location(),c.get_actor_rotation())
            levels.eject_pilot_level_actor();levels.save_current_level()
            (root/'Evidence/comedor-capture-complete.json').write_text(json.dumps({'images':[j[0] for j in jobs],'roof_restored':True,'distribution_image_is_cutaway':True},indent=2))
            u.unregister_slate_post_tick_callback(handle)
        else:prepare()
prepare()
handle=u.register_slate_post_tick_callback(tick)
