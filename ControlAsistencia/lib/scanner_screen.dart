// lib/scanner_screen.dart

import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/material.dart';


class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  // Controlador para la cámara del escáner.
  final MobileScannerController _scannerController = MobileScannerController(
    detectionSpeed: DetectionSpeed.normal, // Velocidad de detección
    facing: CameraFacing.back,             // Usar cámara trasera
  );
  bool _isProcessing = false; // Bandera para evitar múltiples detecciones

  /// Se llama cuando se detecta un código QR.
  void _onDetect(BarcodeCapture capture) {
    if (_isProcessing) return; // Si ya se está procesando, no hacer nada.
    _isProcessing = true;

    final String? qrValue = capture.barcodes.first.rawValue;

    if (qrValue != null && (qrValue.startsWith('http://') || qrValue.startsWith('https://'))) {
      // Si el valor es una URL válida, la guardamos.
      _saveUrlAndGoBack(qrValue);
    } else {
      // Si no es una URL, mostramos un error.
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Código QR no válido. Asegúrate de que sea una URL.'),
          backgroundColor: Colors.red,
        ),
      );
      // Reactivamos el escaneo después de un momento.
      Future.delayed(const Duration(seconds: 2), () {
        _isProcessing = false;
      });
    }
  }

  /// Guarda la URL usando SharedPreferences y regresa a la pantalla anterior.
  Future<void> _saveUrlAndGoBack(String url) async {
    final uri = Uri.tryParse(url);
    if (uri == null || !uri.hasAuthority || uri.host.isEmpty) {
      if (mounted) {
        setState(() => _isProcessing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('La dirección del QR no es válida.'),
            backgroundColor: Colors.red,
          ),
        );
      }
      return;
    }

    final prefs = await SharedPreferences.getInstance();
    final apiKey = uri.queryParameters['api_key'];
    final serverUri = uri.replace(
      queryParameters: {
        for (final entry in uri.queryParameters.entries)
          if (entry.key != 'api_key') entry.key: entry.value,
      },
    );
    await prefs.setString(
      'server_url',
      serverUri.toString().replaceFirst(RegExp(r'/$'), ''),
    );
    if (apiKey != null && apiKey.isNotEmpty) {
      await prefs.setString('api_key', apiKey);
    } else {
      // Un QR antiguo solo contiene la URL; no reutilizar claves de otro servidor.
      await prefs.remove('api_key');
    }

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(apiKey == null || apiKey.isEmpty
            ? 'Servidor guardado. Escanea el QR actualizado del POS para autenticarte.'
            : 'Servidor y autenticación configurados correctamente.'),
        backgroundColor: Colors.green,
      ),
    );
    Navigator.of(context).pop();
  }

  @override
  void dispose() {
    _scannerController.dispose(); // Liberar recursos del controlador.
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Escanear QR del Servidor')),
      body: Stack(
        alignment: Alignment.center,
        children: [
          // Widget principal que muestra la vista de la cámara.
          MobileScanner(
            controller: _scannerController,
            onDetect: _onDetect,
          ),

          // Superposición visual para guiar al usuario.
          Container(
            width: 250,
            height: 250,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.white, width: 4),
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          Positioned(
            bottom: 50,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'Apunta la cámara al código QR',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }
}