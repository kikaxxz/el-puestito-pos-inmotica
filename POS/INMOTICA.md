# Inmótica en El Puestito POS

La pestaña **Inmótica** del menú izquierdo muestra y controla la misma simulación que la escena de Godot.

## Abrir la versión actualizada

1. Abrí `D:/Godot/Escenas/gemelo-digital-el-puestito/project.godot` y ejecutá el restaurante con **F5**. Abrir solamente el editor no inicia el simulador.
2. Ejecutá `dist-inmotica/El Puestito/El Puestito.exe` dentro de esta carpeta del POS. Conservá toda la carpeta del ejecutable, incluido `_internal`.
3. Entrá a **Inmótica**. Cuando aparezca **Conectado**, se habilitan los controles. Podés abrir los programas en cualquier orden: el POS intenta reconectarse automáticamente.

El ejecutable anterior de `dist` conserva su versión anterior. Ambos ejecutables usan el perfil habitual del POS en `%APPDATA%/ElPuestito`; usá una sola instancia del POS a la vez.

## Métricas y controles

- **Gas:** concentración en ppm, estado normal / prealerta / alarma crítica y activación o detención de fuga simulada. Los umbrales de subida del simulador son >400 y >800 ppm; al bajar aplica histéresis.
- **Cilindro:** peso bruto, masa neta de gas, tara, porcentaje restante y sustitución simulada por un cilindro lleno.
- **Iluminación:** nueve circuitos independientes: cocina, bodega, oficina, baños de mujeres y hombres, mesas, barra/caja, pasillo y Ross Tattoo. Control general para encender/apagar todos.
- **Presencia:** estado de ambos baños, pruebas de presencia y cambio automático/manual. En automático, la luz sigue el sensor PIR; el botón individual se habilita al pasar a manual. El control general pasa ambos baños a manual, igual que en Godot.
- **Biometría:** último resultado, secuencia de eventos y pruebas de huella aceptada/rechazada. Son eventos de simulación: no marcan asistencia ni alteran la nómina.
- **Eventos:** hasta 100 entradas de esta sesión, con hora de cambios de iluminación, presencia, alarma, identificación y confirmaciones de órdenes.
- **Aviso sonoro en el POS:** opcional; emite un aviso local mientras la alarma crítica está activa. El sonido de Godot se controla desde la escena.

Las métricas se actualizan cada 500 ms. Un control muestra confirmación después de comprobar el estado recibido, no solamente después de enviar la orden. Los cambios hechos desde Godot también se reflejan en el POS.

Al pausar o perder la conexión, los valores se sustituyen por **— / Sin datos actuales** y se deshabilitan los controles. Una orden interrumpida no se reenvía automáticamente. El POS sigue funcionando aunque Godot esté cerrado.

## Comunicación local

El cliente usa `127.0.0.1:15020`, Modbus TCP, unidad 1. Lee FC04, registros 0–10, y escribe FC05, coils 0–17 según `MAPA_MODBUS.md` del proyecto Godot. Valida la firma `0x5055`, las tramas y las unidades antes de mostrar datos. La conexión es asíncrona mediante QtNetwork, sin instalar pymodbus y sin bloquear la interfaz de caja.

Todo corresponde al simulador local; esta integración no configura ni conecta sensores físicos. El recorrido 3D sigue ejecutándose en Godot. Para ver la escena con más espacio podés ocultar allí el panel usando **Tab**.

## Verificación

Desde esta carpeta:

```powershell
C:/Python313/python.exe -m pytest evaluation/test_inmotica.py -q
C:/Python313/python.exe evaluation/check_pos_inmotica.py
C:/Python313/python.exe evaluation/check_pos_inmotica.py --regression
```

La prueba de integración inicia su propia instancia del servidor Godot en un puerto temporal, prueba todos los controles y la desconexión, y la cierra al terminar. No modifica una escena que ya esté ejecutándose. La comprobación del POS usa un perfil y una base de datos de prueba separados, con el servidor de caja y las notificaciones desactivados.
