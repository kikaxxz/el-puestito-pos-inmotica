# Restaurante nocturno — Unreal Engine 5.8

Proyecto fuente, sin Binaries/Intermediate/Saved ni ejecutable empaquetado. Los paquetes editables están en `Content/`; el módulo C++ que sirve Modbus está en `Source/ElPuestito/`.

## Abrir y probar

1. Instala Unreal Engine 5.8 y la carga de trabajo C++ de escritorio para Windows.
2. Instala Git LFS y clona el repositorio con `git lfs clone` o `git clone` seguido de `git lfs pull`.
3. Abre `ElPuestitoPiloto.uproject` y espera la compilación inicial del módulo C++.
4. Ejecuta el mapa inicial `RestauranteNoche`.
5. Recorre con WASD y ratón. Mira una puerta y pulsa **F** para abrirla o cerrarla. Los baños abren hacia afuera; una puerta se detiene si alguien ocupa su recorrido.

El servidor Modbus TCP es local (`127.0.0.1:15020`, unidad 1). El POS fuente se conecta a él desde su pestaña Inmótica. Ejecuta solo una instancia de la escena a la vez.

## Compilar una distribución opcional

En PowerShell define `$env:UE_ROOT` con la carpeta de instalación del motor y ejecuta `./Tools/compilar_inmotica.ps1`. La salida queda bajo `Build/Package/` (ignorada por Git). No se requiere empaquetar para abrir el proyecto en el editor.

La escena es una simulación educativa. ppm, cilindro, presencia, huellas y luces no están conectados a equipos reales.
