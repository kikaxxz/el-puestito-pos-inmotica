# App movil de asistencia

Aplicacion Flutter para Android que se conecta al servidor local del POS.

## Ejecutar o compilar

Requiere Flutter 3.x y Android SDK. En esta carpeta ejecuta:

    flutter pub get
    flutter run

Para generar un APK Release:

    flutter build apk --release

El APK aparece en build/app/outputs/flutter-apk/app-release.apk.

## Vincular con El Puestito POS

1. En el repositorio, inicia POS/Iniciar-POS-Demo-Movil.cmd (o el POS normal) en una computadora de la misma red Wi-Fi. El launcher Demo normal limita el servidor a localhost y no sirve para un teléfono.
2. Abre en el POS el QR de conexion.
3. Instala y abre esta app en el telefono, pulsa el icono QR y escanea el codigo nuevo.
4. Selecciona un empleado y registra asistencia.

El QR lleva la direccion local del servidor y la clave que el cliente envia por la cabecera X-API-KEY. Los QR anteriores, que solo contenian una URL, ya no bastan: vuelve a generarlo desde el POS. El telefono y la computadora deben estar en la misma red, y el firewall de Windows debe permitir el puerto TCP 5000.

El backend activo esta en POS/server/; lib/server.py es un script heredado que no usa la app Flutter. Si la app recibe HTML en /employees, el puerto 5000 esta sirviendo otro proceso o una version antigua del servidor: inicia el POS actualizado y escanea su QR.
