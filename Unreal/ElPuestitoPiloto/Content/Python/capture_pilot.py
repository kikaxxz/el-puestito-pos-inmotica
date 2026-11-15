"""Capture the actual Unreal viewport after rendering has warmed up."""
import json
from pathlib import Path
import unreal as ue
ue.EditorPythonScripting.set_keep_python_script_alive(True)
import review_session

root = Path(ue.Paths.project_dir()).resolve()
levels = ue.get_editor_subsystem(ue.LevelEditorSubsystem)
levels.load_level("/Game/Piloto/ComedorPiloto")
actors = ue.get_editor_subsystem(ue.EditorActorSubsystem)
camera = next(a for a in actors.get_all_level_actors() if a.get_actor_label() == "Camara comparacion")
ue.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
world = ue.EditorLevelLibrary.get_editor_world()
ue.SystemLibrary.execute_console_command(world,"t.MaxFPS 60")
ue.SystemLibrary.execute_console_command(world,"r.VSync 0")
ue.SystemLibrary.execute_console_command(world,"r.ScreenPercentage 75")
frames = 0
durations = []
capture = None

def tick(delta):
    global frames,capture,handle
    frames += 1
    if 180 <= frames < 420:
        durations.append(float(delta)*1000)
    if frames == 180:
        ue.SystemLibrary.execute_console_command(world,"csvprofile frames=240")
    if frames == 450:
        capture = ue.AutomationLibrary.take_high_res_screenshot(1920,1080,str(root/"Evidence/unreal-comedor.png"),camera=camera)
    if frames > 480 and (root/"Evidence/unreal-comedor.png").exists():
        report = {"measurement":"Editor Slate frame interval, not isolated GPU timing", "samples_ms":durations,
                  "internal_screen_percentage":75,"screenshot_size":[1920,1080],"fps_cap":60}
        (root/"Evidence/unreal-editor-timing.json").write_text(json.dumps(report,indent=2),encoding="utf8")
        ue.unregister_slate_post_tick_callback(handle)
        ue.log("PUESTO_PILOT_CAPTURE_OK")

handle = ue.register_slate_post_tick_callback(tick)
