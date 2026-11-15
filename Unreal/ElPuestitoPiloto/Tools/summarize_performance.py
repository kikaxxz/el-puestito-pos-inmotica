"""Summarize actual per-frame Unreal CSV values, excluding footer metadata."""
import csv
import json
import statistics
import argparse
from pathlib import Path

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--night',action='store_true')
parser.add_argument('--restaurant',action='store_true')
args=parser.parse_args()
source=max((root/'Saved/Profiling/CSV').glob('*.csv'),key=lambda p:p.stat().st_mtime)
with source.open(encoding='utf-8-sig') as f:
    rows=[]
    for row in csv.DictReader(f):
        try:
            float(row['GPUTime']);float(row['GameThreadTime']);float(row['FrameTime'])
            rows.append(row)
        except (ValueError,TypeError,KeyError):
            pass
report={'source':str(source),'context':'Unreal Editor viewport, dining entrance camera; 60 FPS cap; 75% internal resolution. Not a packaged 1080p benchmark.','quality':'High (2), software Lumen, no hardware ray tracing','statistics':{}}
if args.night: report['map']='/Game/ComedorCompleto/ComedorNoche'
if args.restaurant:
    report['shadow_method']='Virtual Shadow Maps (cached)'
    report['map']='/Game/RestauranteCompleto/RestauranteNoche'
    report['context']='Unreal Editor viewport, bar camera; 60 FPS cap; 75% internal resolution. Not a packaged 1080p benchmark.'
for key in ['FrameTime','GPUTime','GameThreadTime','RenderThreadTime','GPUMem/LocalUsedMB','GPUMem/LocalBudgetMB']:
    values=sorted(float(row[key]) for row in rows)
    report['statistics'][key]={'n':len(values),'mean':statistics.mean(values),'median':statistics.median(values),'p95':values[int((len(values)-1)*.95)],'max':max(values)}
report['approx_mean_fps']=1000/report['statistics']['FrameTime']['mean']
(root/'Evidence'/('restaurante-performance.json' if args.restaurant else ('night-performance.json' if args.night else 'performance-summary.json'))).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
