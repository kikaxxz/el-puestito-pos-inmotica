"""Stage only public assets and synthetic configuration; no operational profile."""
import json
import shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
dest=Path('D:/ElPuestito/Build/2026-10-11/Assets')
dest.mkdir(parents=True,exist_ok=True)
for p in (root/'Assets').rglob('*'):
    if p.is_file() and (p.suffix.lower() in {'.png','.jpg','.jpeg','.ico','.qss','.ttf'} or p.name=='menu.json'):
        target=dest/p.relative_to(root/'Assets');target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,target)
for name in ['asistencia','asistencia_historico','barra_ordenes','caja_ordenes','cocina_ordenes','processed_orders','ventas_completadas']:
    (dest/(name+'.json')).write_text('[]',encoding='utf-8')
config={'total_mesas':10,'seguridad':{'pines_acceso':{'Administrador':'9999','Cajero':'3333','Cocinero':'1111','Barra':'2222'}},
        'api_key':'DEMO-LOCAL-EL-PUESTItO-2026','printer_interface':'disabled','roles_pago':{},
        'horarios_y_margenes':{'entrada_oficial':'08:00','salida_oficial':'17:00','margen_gracia_entrada':0,'margen_gracia_salida':0},
        'politicas_pago_extra':{'multiplicador_hora_extra':1.5,'feriados':[]},
        'printer_settings':{'header':'El Puestito - DEMOSTRACION','footer':'Sin validez fiscal','enable_proforma':False,'suggest_tip':False}}
(dest/'config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
print('Recursos de demostracion preparados en',dest)
