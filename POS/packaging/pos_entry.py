"""Desktop entry point, with an isolated check for the packaged application."""
import json
import os
from pathlib import Path
import runpy
import sys
import time
import traceback


def check_package():
    output = Path(sys.argv[sys.argv.index("--verificar-empaquetado") + 1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ["APPDATA"] = str(output / "perfil-prueba")
    os.environ["PUESTITO_DB_PATH"] = str(output / "perfil-prueba" / "test.db")
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["PUESTITO_DEMO"] = "1"
    os.environ["TESTING"] = "true"
    Path(os.environ["APPDATA"]).mkdir(parents=True, exist_ok=True)
    result = {"ok": False, "frozen": bool(getattr(sys, "frozen", False))}
    try:
        from PyQt6.QtGui import QFont, QFontDatabase
        from PyQt6.QtWidgets import QApplication
        from main_window import MainWindow
        from server.server_thread import ServerThread

        # The check never starts the cash register's web server or changes firewall rules.
        ServerThread.start = lambda self: None
        application = QApplication([])
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        application.setFont(QFont("Segoe UI", 10))
        window = MainWindow()
        window.btn_inmotica.click()
        window.resize(1280, 800)
        window.show()
        service = window.page_inmotica.service
        if "--puerto" in sys.argv:
            service.stop()
            service.port = int(sys.argv[sys.argv.index("--puerto") + 1])
            service.start()
            deadline = time.monotonic() + 12
            while not service.online and time.monotonic() < deadline:
                application.processEvents()
                time.sleep(.02)
            if not service.online:
                raise RuntimeError("El ejecutable no recibió telemetría de la simulación")
            result["ppm"] = service.snapshot.ppm
            result["peso_kg"] = service.snapshot.gross_kg
            result["nivel"] = service.snapshot.level
            if "--probar-controles" in sys.argv:
                checks = []
                finished = []
                service.command_finished.connect(lambda *args: finished.append(args))

                def wait_for(predicate, timeout=12):
                    deadline = time.monotonic() + timeout
                    while not predicate() and time.monotonic() < deadline:
                        application.processEvents()
                        time.sleep(.02)
                    if not predicate():
                        raise RuntimeError("Tiempo agotado verificando la simulación")

                def command(address, value=True):
                    finished.clear()
                    if not service.request_command(address, value):
                        raise RuntimeError(f"No se pudo enviar la orden {address}")
                    wait_for(lambda: bool(finished))
                    if not finished[-1][1]:
                        raise RuntimeError(str(finished[-1]))
                    checks.append({"coil": address, "value": value, "confirmed": True})

                command(0, False)
                for address in range(1, 10):
                    command(address)
                command(11)
                command(12)
                command(13)
                command(14)
                command(15)
                command(16)
                command(10)
                wait_for(lambda: service.snapshot.alarm == 2)
                window.grab().save(str(output / "POS-alarma.png"))
                command(10, False)
                command(17)
                wait_for(lambda: service.snapshot.alarm == 0, timeout=30)
                command(0, True)
                result["controls"] = checks
                result["alarm_and_recovery"] = True
        else:
            service.stop()
        application.processEvents()
        if window.stacked_widget.currentWidget() is not window.page_inmotica:
            raise RuntimeError("No se abrió la pestaña Inmótica")
        if not window.grab().save(str(output / "POS.png")):
            raise RuntimeError("No se pudo guardar la captura")
        result["online"] = service.online
        window.close()
        application.processEvents()
        result["ok"] = True
    except Exception:
        result["error"] = traceback.format_exc()
    (output / "resultado.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    if "--verificar-empaquetado" in sys.argv:
        raise SystemExit(check_package())
    if getattr(sys, 'frozen', False):
        # A distributable demonstration must never open the operational profile.
        profile = Path(os.environ['APPDATA']) / 'ElPuestitoDemostracion'
        profile.mkdir(parents=True, exist_ok=True)
        os.environ['APPDATA'] = str(profile)
        os.environ['PUESTITO_DEMO'] = '1'
        os.environ['PUESTITO_DB_PATH'] = str(profile / 'ElPuestito' / 'puestito.db')
        (profile / 'ElPuestito').mkdir(exist_ok=True)
    runpy.run_module("app", run_name="__main__")
