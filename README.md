# El Puestito: POS e inmótica + escena Unreal

Repositorio de **código fuente y recursos editables** para ejecutar la demostración sin descargar ejecutables empaquetados. El POS se comunica con Unreal localmente por Modbus TCP en `127.0.0.1:15020`.

## Contenido

- `POS/`: aplicación Python/PyQt, base de datos que se crea al iniciar, dashboard inmótico, pruebas y datos sintéticos de demostración.
- `Unreal/ElPuestitoPiloto/`: proyecto Unreal Engine 5.8, escena nocturna, recursos, módulo C++ Modbus y puertas interactivas.
- Los archivos `.uasset`, `.umap` y `.glb` se distribuyen con **Git LFS**. Instala Git LFS antes de clonar; de lo contrario solo se descargarán punteros de los recursos pesados.

## Ejecutar el POS desde el código

Requiere Windows y Python 3.13 (o una versión compatible con las dependencias de `POS/requirements.txt`). Desde `POS/` crea un entorno virtual, instala las dependencias y ejecuta `Iniciar-POS-Demo.cmd`. El modo demo evita configuración de firewall y servicios externos. PIN de prueba: administrador `9999`, caja `3333`, cocina `1111`, barra `2222`.

## Ejecutar la escena en Unreal

Requiere Unreal Engine 5.8 con componentes de desarrollo C++ y MSVC para Windows. Después de clonar con Git LFS, abre `Unreal/ElPuestitoPiloto/ElPuestitoPiloto.uproject`; Unreal compilará el módulo `ElPuestito` al abrir. El mapa inicial es `RestauranteNoche`. WASD y ratón recorren el restaurante; `F` abre/cierra la puerta enfocada. El HUD incluye ppm, estado del cilindro, presencia y controles de simulación.

Para conectar el POS, mantén ambos programas en el mismo equipo y abre la pestaña **Inmótica**. La simulación, sensores y biometría son didácticos; no se conecta a dispositivos físicos.

## Seguridad y datos

El repositorio usa PIN y clave API locales de demostración. No contiene las credenciales Firebase originales, bases de datos, registros de ventas o asistencia, ni paquetes `.exe`. Los datos de uso se guardan fuera del repositorio, bajo `%APPDATA%`.

Consulta `POS/README.md` y `Unreal/ElPuestitoPiloto/README.md` para pasos detallados.
