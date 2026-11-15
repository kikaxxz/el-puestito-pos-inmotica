"""Capture the night map sequentially, allowing lighting to settle."""
import json, time
from pathlib import Path
import unreal as u

root = Path(u.Paths.project_dir()).resolve()
ed = u.get_editor_subsystem(u.EditorActorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.EditorLevelLibrary.get_editor_world().get_name() == 'RestauranteNoche'
cams = {a.get_actor_label(): a for a in ed.get_all_level_actors() if isinstance(a, u.CameraActor)}
jobs = [('restaurante-'+name.lower()+'.png','Vista '+name) for name in ['Barra','Cocina','Mujeres','Hombres','Oficina','Bodega','Estudio','Entrada','Patio','Restaurante']]
state = {'index': 0, 'started': time.monotonic(), 'requested': 0, 'done': False}

def prepare():
    levels.eject_pilot_level_actor()
    c = cams[jobs[state['index']][1]]
    u.EditorLevelLibrary.set_level_viewport_camera_info(c.get_actor_location(), c.get_actor_rotation())
    levels.editor_set_game_view(True)
    levels.editor_set_viewport_realtime(True)
    state['started'] = time.monotonic()
    state['requested'] = 0

def tick(delta):
    if state['done']: return
    target = root / 'Evidence' / jobs[state['index']][0]
    if not state['requested'] and time.monotonic() - state['started'] > 8:
        state['requested'] = time.time()
        state['task'] = u.AutomationLibrary.take_high_res_screenshot(1920, 1080, str(target), camera=None)
    elif state['requested'] and target.exists() and target.stat().st_mtime >= state['requested'] and state['task'].is_task_done():
        u.log('RESTAURANTE_IMAGE_OK ' + target.name)
        state['index'] += 1
        if state['index'] == len(jobs):
            state['done'] = True
            u.unregister_slate_post_tick_callback(handle)
            c = cams['Vista Barra']
            levels.eject_pilot_level_actor()
            u.EditorLevelLibrary.set_level_viewport_camera_info(c.get_actor_location(), c.get_actor_rotation())
            levels.save_current_level()
            (root/'Evidence/restaurante-captures.json').write_text(json.dumps({'images': [j[0] for j in jobs], 'roof_visible': True}, indent=2))
        else: prepare()
    elif time.monotonic() - state['started'] > 240:
        state['done'] = True
        u.unregister_slate_post_tick_callback(handle)
        u.log_error('Night screenshot timed out: ' + str(target))

prepare()
handle = u.register_slate_post_tick_callback(tick)
