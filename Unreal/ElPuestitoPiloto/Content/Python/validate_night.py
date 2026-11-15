"""Night-level runtime and rendering checks in the editor."""
import unreal as u
import json, hashlib, time
from pathlib import Path

root = Path(u.Paths.project_dir()).resolve()
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
ed = u.get_editor_subsystem(u.EditorActorSubsystem)
report = {'level': u.EditorLevelLibrary.get_editor_world().get_name(),
          'verification': 'Engine API: spawn and swept movement, not a full manual walk'}
report['day_map_unchanged'] = hashlib.sha256((root/'Content/ComedorCompleto/ComedorCompleto.umap').read_bytes()).hexdigest().upper() == json.loads((root/'Evidence/day-map-before-night.json').read_text(encoding='utf-8-sig'))['Hash']
actors = ed.get_all_level_actors()
report['roof_visible'] = all(not a.is_hidden_ed() and not a.hidden for a in actors if 'CubiertaComedor' in [str(t) for t in a.tags])
report['local_lights_enabled'] = sum(1 for a in actors if isinstance(a,(u.PointLight,u.RectLight)) and a.get_component_by_class(u.LightComponent).intensity>0)
camera = next(a for a in actors if a.get_actor_label() == 'Camara comparacion')
u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
levels.editor_request_begin_play()
state={'stage':0,'time':time.monotonic(),'done':False}

def tick(delta):
    if state['done']: return
    elapsed=time.monotonic()-state['time']
    if state['stage']==0 and elapsed>5:
        report['play_started']=levels.is_in_play_in_editor()
        worlds=u.EditorLevelLibrary.get_pie_worlds(False)
        pawn=u.GameplayStatics.get_player_pawn(worlds[0],0) if worlds else None
        report['pawn_spawned']=pawn is not None
        if pawn:
            p=pawn.get_actor_location()
            report['spawn_cm']=[p.x,p.y,p.z]
            report['pawn_class']=pawn.get_class().get_name()
            report['root']=str(pawn.root_component)
            report['root_mobility']=str(pawn.root_component.mobility)
            report['pawn_doc']=str(pawn.get_actor_enable_collision())
            report['overlaps']=[a.get_actor_label() for a in (u.SystemLibrary.sphere_overlap_actors(worlds[0],p,35,[u.ObjectTypeQuery.OBJECT_TYPE_QUERY1],u.Actor,[pawn]) or [])]
            hit=pawn.set_actor_location(p+u.Vector(0,30,0),True,False)
            report['hit']=str(hit)
            report['move_cm']=(pawn.get_actor_location()-p).length()
            report['entry_clear']=report['move_cm']>29.9
        levels.editor_request_end_play()
        state['stage']=1;state['time']=time.monotonic()
    elif state['stage']==1 and elapsed>4:
        report['play_stopped']=not levels.is_in_play_in_editor()
        report['ok']=all(report.get(k,False) for k in ['day_map_unchanged','roof_visible','play_started','pawn_spawned','entry_clear','play_stopped'])
        (root/'Evidence/night-runtime-validation.json').write_text(json.dumps(report,indent=2))
        u.SystemLibrary.execute_console_command(u.EditorLevelLibrary.get_editor_world(),'csvprofile frames=300')
        state['done']=True
        u.unregister_slate_post_tick_callback(handle)
        u.log('NIGHT_RUNTIME_OK' if report['ok'] else 'NIGHT_RUNTIME_FAILED')

handle=u.register_slate_post_tick_callback(tick)


