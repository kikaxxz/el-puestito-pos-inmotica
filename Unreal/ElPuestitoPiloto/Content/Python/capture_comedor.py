import json
from pathlib import Path
import unreal as u
root=Path(u.Paths.project_dir()).resolve()
ed=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.EditorLevelLibrary.get_editor_world()
actors=ed.get_all_level_actors()
roof=[a for a in actors if 'CubiertaComedor' in [str(t) for t in a.tags]]
general=next(a for a in actors if a.get_actor_label()=='Camara general')
interior=next(a for a in actors if a.get_actor_label()=='Camara comparacion')
for cmd in ['sg.GlobalIlluminationQuality 2','sg.ShadowQuality 2','sg.ReflectionQuality 2','sg.PostProcessQuality 2','sg.EffectsQuality 2','t.MaxFPS 60']:
    u.SystemLibrary.execute_console_command(world,cmd)
frame=0
def view(cam):
    u.EditorLevelLibrary.set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
def tick(delta):
    global frame,handle
    frame+=1
    if frame==180:
        u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(root/'Evidence/comedor-completo-techado.png'),camera=general)
    if frame==360:
        for a in roof:a.set_is_temporarily_hidden_in_editor(True)
    if frame==540:
        u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(root/'Evidence/comedor-completo-distribucion.png'),camera=general)
    if frame==720:
        for a in roof:a.set_is_temporarily_hidden_in_editor(False)
        view(interior)
    if frame==900:
        u.AutomationLibrary.take_high_res_screenshot(1920,1080,str(root/'Evidence/comedor-completo-interior.png'),camera=interior)
    if frame==1080:
        u.SystemLibrary.execute_console_command(world,'csvprofile frames=300')
    if frame==1440:
        for a in roof:a.set_is_temporarily_hidden_in_editor(False)
        view(general);levels.save_current_level()
        report={'map':'/Game/ComedorCompleto/ComedorCompleto','roof_batches':len(roof),'roof_restored':all(not a.is_temporarily_hidden_in_editor() for a in roof),'mesh_actors':sum(isinstance(a,u.StaticMeshActor) for a in actors),'source_table_count':10,'screenshots':['comedor-completo-techado.png','comedor-completo-distribucion.png','comedor-completo-interior.png']}
        (root/'Evidence/comedor-review.json').write_text(json.dumps(report,indent=2))
        u.unregister_slate_post_tick_callback(handle)
        u.log('COMEDOR_CAPTURE_OK')
handle=u.register_slate_post_tick_callback(tick)
