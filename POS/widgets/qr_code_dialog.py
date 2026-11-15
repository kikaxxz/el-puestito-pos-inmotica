import os
import io
import socket
import qrcode
from urllib.parse import urlencode
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from logger_setup import setup_logger

logger = setup_logger()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class QRCodeDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Conexión del Servidor")
        self.setFixedSize(300, 350)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        local_demo = os.environ.get("PUESTITO_DEMO") == "1"
        instruction_label = QLabel("Demostración local en esta computadora" if local_demo
                                  else "Escanea este código desde la app del teléfono:")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(250, 250)
        
        layout.addWidget(instruction_label)
        layout.addWidget(self.qr_label)
        if local_demo:
            link = QLabel('<a href="http://127.0.0.1:5000">Abrir el servidor local</a>')
            link.setOpenExternalLinks(True)
            link.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(link)
        
        self.generate_and_display_qr()

    def get_local_ip(self):
        if os.environ.get("PUESTITO_DEMO") == "1":
            return "127.0.0.1"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
    
    def generate_and_display_qr(self):
        ip_address = self.get_local_ip()
        server_url = f"http://{ip_address}:5000"
        app_controller = getattr(self.parent(), "app_controller", None)
        api_key = getattr(app_controller, "API_KEY", "")
        qr_payload = f"{server_url}?{urlencode({'api_key': api_key})}"

        # La app extrae la clave del QR y la envía en X-API-KEY.
        logger.info(f"Generando QR de asistencia para: {server_url}")
        qr_image = qrcode.make(qr_payload)
        
        buffer = io.BytesIO()
        qr_image.save(buffer, "PNG")
        buffer.seek(0)
        
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue(), "PNG")
        self.qr_label.setPixmap(pixmap.scaled(250, 250))
