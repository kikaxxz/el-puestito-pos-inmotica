"""Temporary local editor review queue; active only during capture sessions."""
from pathlib import Path
import traceback
import unreal

root = Path(unreal.Paths.project_dir()).resolve()
job = root / 'Evidence/review-job.py'

def tick(delta):
    if job.exists():
        code = job.read_text(encoding='utf-8-sig')
        job.unlink()
        try:
            exec(compile(code, str(job), 'exec'), {'unreal': unreal, '__name__':'__review__'})
        except Exception:
            unreal.log_error(traceback.format_exc())

handle = unreal.register_slate_post_tick_callback(tick)
