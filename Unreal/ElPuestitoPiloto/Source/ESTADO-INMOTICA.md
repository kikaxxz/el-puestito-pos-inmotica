# Integración compilada y validada — 12 de octubre de 2026

La entrega vigente es D:/ElPuestito/Entrega-Unreal-Inmotica. Incluye POS y Unreal nativos; no depende de Godot. MSVC 14.50 instalado en D:/BuildTools. La compilación con Unreal 5.8 y el empaquetado finalizaron con BUILD SUCCESSFUL. El .uproject tiene habilitado el módulo ElPuestito.

El servidor local Modbus TCP 127.0.0.1:15020, unidad 1, expone FC04 (11 registros) y FC05 (18 direcciones). Incluye gas con histéresis, cilindro, nueve zonas, presencia por ubicación del jugador, pulsos de presencia, biometría simulada y HUD.

La prueba de los ejecutables POS + Unreal confirmó 20 órdenes, alarma crítica y recuperación: D:/ElPuestito/QA/2026-10-11/pos-unreal/resultado.json. Se revisaron visualmente iluminación y apagado independiente de mesas. El runtime encontró 45 luces, 18 emisores y tres indicadores. Evidencias adicionales en la carpeta Verificacion de la entrega.

Limitaciones: biometría solo simulada, sin partículas de fuga, sin conexión a dispositivos físicos. El estado didáctico se reinicia al abrir Unreal. El POS utiliza un perfil de demostración separado. No confundir con la entrega parcial anterior del 11 de octubre.

Para recompilar: ../Tools/compilar_inmotica.ps1. La entrega incluye LEEME.md e Iniciar_ElPuestito.cmd.

Corrección espacial aplicada y empaquetada: cubículos abren hacia afuera; cilindro/balanza junto a estufa y asentados al piso. Revisión visual del ejecutable y lectura Modbus correctas. Scripts reproducibles: Tools/correct_spatial_access.py genera reemplazos desde el GLB original; Content/Python/correct_spatial_access.py los aplica conservando materiales. Evidencias en Verificacion de la entrega.

Puertas interactivas (13/10/2026): APuestitoDoor separa hoja/manilla y conserva marcos. F, distancia máxima 220 cm y línea de visión; animación de 0,85 s; barrido angular con detección de obstáculos. Cubículos abren hacia afuera. Comando de prueba Development: puestito.TestDoors. Extracción: Tools/extract_interactive_doors.py; instalación: Content/Python/install_interactive_doors.py. Prueba de runtime: 7/7 puertas abren, cierran y se detienen ante el jugador.
