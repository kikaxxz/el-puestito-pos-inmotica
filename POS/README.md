# POS de El Puestito — entorno fuente

## Inicio rápido (Windows)

```powershell
cd POS
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
.\Iniciar-POS-Demo.cmd
```

También puedes iniciar con `python app.py` definiendo primero `PUESTITO_DEMO=1` y `TESTING=true` en el entorno. El primer inicio crea la base local y copia la configuración de `Assets/config.json` a `%APPDATA%\ElPuestito`. Los PIN incluidos son solo para probar.

El panel **Inmótica** necesita que Unreal esté abierto en el mismo equipo y escuche en `127.0.0.1:15020`. Los nueve controles de iluminación son independientes; los controles de los baños permiten volver al modo automático en **Pruebas y ajustes**.

## Paquete opcional

`packaging/build_windows.ps1` y `packaging/ElPuestito_POS.spec` contienen el flujo de empaquetado PyInstaller. Para ejecutar desde código fuente no hace falta compilar un `.exe`.

No añadas a commits `firebase_credentials.json`, archivos `.env`, bases `.db`, registros de la aplicación ni datos reales de clientes o empleados.

## Probar la app de asistencia en un telefono

Usa POS/Iniciar-POS-Demo-Movil.cmd para iniciar el POS de demostracion con acceso desde la red local. Acepta el aviso de Windows Firewall en una red privada si aparece. El QR mostrara la IP LAN de esta computadora y la clave de demo. El telefono y la PC deben estar en la misma Wi-Fi.

Iniciar-POS-Demo.cmd mantiene el servidor limitado a esta computadora; su QR de 127.0.0.1 no sirve para un telefono. Despues de iniciar el modo movil, abre el QR nuevo y vuelve a escanearlo en ControlAsistencia. No inicies ControlAsistencia/lib/server.py: el backend compatible es el servidor integrado del POS.
