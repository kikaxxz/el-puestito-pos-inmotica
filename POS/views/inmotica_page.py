"""Restaurant telemetry dashboard with optional simulation controls."""
from datetime import datetime
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QPlainTextEdit, QProgressBar, QPushButton,
    QScrollArea, QVBoxLayout, QWidget)

from src.services.inmotica_service import (ALARM_NAMES, BIOMETRIC_NAMES,
                                         ZONE_NAMES, InmoticaService)


class InmoticaPage(QWidget):
    def __init__(self, parent=None, *, service=None, auto_start=True):
        super().__init__(parent)
        self.setObjectName("inmoticaPage")
        self.service = service or InmoticaService(self)
        self.state = None
        self.previous = None
        self.busy = False
        self.commands = []
        self.zone_buttons = {}
        self.zone_status = {}
        self.auto_buttons = {}
        self.bio_seen_at = None
        self.setStyleSheet("""
            QWidget#inmoticaPage { background:#101114; color:#edeef1; }
            QLabel { color:#e9ebef; background:transparent; font-size:13px; }
            QLabel#heading { font-size:28px; font-weight:700; }
            QLabel#muted { color:#aeb4be; }
            QScrollArea { border:0; background:#101114; }
            QWidget#dashboardContent { background:#101114; }
            QFrame#metricCard, QFrame#zoneCard { background:#1b1d22;
                border:1px solid #30333c; border-radius:10px; }
            QGroupBox { color:#f0f0f2; border:1px solid #30333c;
                border-radius:10px; margin-top:14px; padding:16px 10px 8px;
                font-weight:600; font-size:14px; }
            QGroupBox::title { subcontrol-origin:margin; left:14px; padding:0 6px; }
            QPushButton { background:#2b2e37; color:#f3f4f6; border:1px solid #414652;
                border-radius:6px; padding:7px 10px; font-size:13px; min-height:20px; }
            QPushButton:hover { background:#373c47; border-color:#c28756; }
            QPushButton:disabled { color:#777e8b; background:#202228; border-color:#30333c; }
            QPushButton#accent { background:#ab5b29; border-color:#c67a42; }
            QPushButton#accent:disabled { background:#38291f; color:#998273; }
            QProgressBar { border:0; background:#30333c; border-radius:4px; height:8px; }
            QProgressBar::chunk { background:#d79b61; border-radius:4px; }
            QPlainTextEdit { background:#15171b; color:#c6cbd3; border:1px solid #30333c;
                border-radius:7px; font-size:12px; padding:6px; }
            QCheckBox { color:#c6cbd3; spacing:6px; font-size:12px; }
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)
        content = QWidget()
        content.setObjectName("dashboardContent")
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(14)
        header = QHBoxLayout()
        heading = QLabel("Estado del restaurante")
        heading.setObjectName("heading")
        header.addWidget(heading)
        header.addStretch()
        self.connection_label = QLabel("Sin datos de la simulación")
        header.addWidget(self.connection_label)
        self.connection_button = QPushButton("Pausar conexión")
        self.connection_button.clicked.connect(self._toggle_connection)
        self.connection_button.setToolTip("Pausar o reanudar la actualización del dashboard")
        layout.addLayout(header)
        self.help_label = QLabel("SIMULACIÓN LOCAL · Abrí ElPuestitoPiloto.exe para recibir las métricas del restaurante.")
        self.help_label.setObjectName("muted")
        self.help_label.setWordWrap(True)
        layout.addWidget(self.help_label)
        self.overview = QLabel("Esperando conexión para conocer el estado del restaurante")
        self.overview.setWordWrap(True)
        self.overview.setStyleSheet("font-size:17px; font-weight:600; padding:10px 0;")
        layout.addWidget(self.overview)
        cards = QGridLayout()
        cards.setSpacing(12)
        gas_box, self.gas_value, self.gas_detail = self._card("CONCENTRACIÓN EN COCINA")
        gas_box.layout().addWidget(self._muted("Umbrales de simulación: prealerta > 400 · crítica > 800 ppm"))
        cylinder_box, self.cylinder_value, self.cylinder_detail = self._card("GAS DISPONIBLE EN EL CILINDRO")
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setTextVisible(False)
        self.level_bar.setFixedHeight(8)
        cylinder_box.layout().addWidget(self.level_bar)
        presence_box, self.presence_value, self.presence_detail = self._card("OCUPACIÓN DE BAÑOS")
        bio_box, self.bio_value, self.bio_detail = self._card("ÚLTIMA IDENTIFICACIÓN SIMULADA")
        presence_box.setMinimumHeight(140)
        bio_box.setMinimumHeight(140)
        self.bio_value.setStyleSheet("font-size:19px; font-weight:600;")
        for i, card in enumerate((gas_box, cylinder_box, presence_box, bio_box)):
            cards.addWidget(card, i // 2, i % 2)
            cards.setColumnStretch(i % 2, 1)
        layout.addLayout(cards)

        lighting = QGroupBox("Iluminación independiente")
        lights_layout = QVBoxLayout(lighting)
        summary = QHBoxLayout()
        self.lights_summary = QLabel("— / 9 circuitos con luz")
        summary.addWidget(self.lights_summary)
        summary.addStretch()
        self.manage_lights = QPushButton("Control general")
        self.manage_lights.setCheckable(True)
        summary.addWidget(self.manage_lights)
        self.global_lights = QWidget()
        general_row = QHBoxLayout(self.global_lights)
        general_row.setContentsMargins(0,0,0,0)
        general_row.addWidget(self._button("Encender todas", 0, True))
        general_row.addWidget(self._button("Apagar todas", 0, False))
        self.global_lights.hide()
        self.manage_lights.toggled.connect(self.global_lights.setVisible)
        lights_layout.addLayout(summary)
        lights_layout.addWidget(self.global_lights)
        grid = QGridLayout()
        grid.setSpacing(8)
        for address, name in enumerate(ZONE_NAMES, 1):
            row = QFrame()
            row.setObjectName("zoneCard")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 8, 10, 8)
            texts = QVBoxLayout()
            texts.addWidget(QLabel(name))
            state = self._muted("Sin datos")
            texts.addWidget(state)
            self.zone_status[address] = state
            row_layout.addLayout(texts, 1)
            button = QPushButton("—")
            button.clicked.connect(lambda checked=False, a=address: self._toggle_zone(a))
            self.zone_buttons[address] = button
            row_layout.addWidget(button)
            grid.addWidget(row, (address - 1) // 3, (address - 1) % 3)
        lights_layout.addLayout(grid)
        lights_layout.addWidget(self._muted("Cada botón controla solo su zona. En baños, Encender/Apagar activa el modo manual; podés recuperar el automático en Pruebas y ajustes."))
        layout.addWidget(lighting)

        self.tests_toggle = QPushButton("Pruebas y ajustes de la simulación  ▾")
        self.tests_toggle.setCheckable(True)
        self.test_panel = QWidget()
        self.test_panel.hide()
        self.tests_toggle.toggled.connect(self.test_panel.setVisible)
        tests = QHBoxLayout(self.test_panel)
        tests.setContentsMargins(0,0,0,0)
        tests.setSpacing(12)
        gas_actions = QGroupBox("Pruebas de gas y cilindro")
        gl = QVBoxLayout(gas_actions)
        self.leak_status = QLabel("Fuga: sin datos")
        gl.addWidget(self.leak_status)
        gl.addWidget(self._button("Activar fuga simulada", 10, True, accent=True))
        gl.addWidget(self._button("Detener fuga", 10, False))
        gl.addWidget(self._button("Sustituir por cilindro lleno", 17, True))
        tests.addWidget(gas_actions, 1)
        presence_actions = QGroupBox("Presencia y modo de baños")
        pl = QVBoxLayout(presence_actions)
        for index, name in enumerate(("Mujeres", "Hombres")):
            row = QHBoxLayout()
            row.addWidget(QLabel(name), 1)
            button = QPushButton("Sin datos")
            address = 11 + index
            button.clicked.connect(lambda checked=False, a=address: self._toggle_auto(a))
            self.auto_buttons[address] = button
            row.addWidget(button)
            pl.addLayout(row)
            pl.addWidget(self._button("Simular presencia: " + name.lower(), 13 + index, True))
        tests.addWidget(presence_actions, 1)
        biometrics = QGroupBox("Biometría simulada")
        bl = QVBoxLayout(biometrics)
        bl.addWidget(self._muted("Las pruebas no registran asistencia ni modifican la nómina."))
        bl.addWidget(self._button("Simular huella aceptada", 15, True))
        bl.addWidget(self._button("Simular huella rechazada", 16, True))
        self.sound_check = QCheckBox("Aviso sonoro en el POS")
        bl.addWidget(self.sound_check)
        tests.addWidget(biometrics, 1)
        bl.addWidget(self.connection_button)

        self.command_label = QLabel("Los controles se habilitan al recibir datos válidos de la simulación.")
        self.command_label.setWordWrap(True)
        layout.addWidget(self.command_label)
        self.age_label = self._muted("Esperando primera lectura · 127.0.0.1:15020")
        layout.addWidget(self.age_label)
        self.events = QPlainTextEdit()
        self.events.setReadOnly(True)
        self.events.setMaximumBlockCount(100)
        self.events.setFixedHeight(110)
        self.events.setPlaceholderText("Eventos de esta sesión: conexión, alarmas, iluminación, presencia y biometría.")
        layout.addWidget(self._muted("ACTIVIDAD RECIENTE · ESTA SESIÓN"))
        layout.addWidget(self.events)
        layout.addWidget(self.tests_toggle)
        layout.addWidget(self.test_panel)
        layout.addStretch()
        self.service.telemetry.connect(self._telemetry)
        self.service.connection_changed.connect(self._connection)
        self.service.busy_changed.connect(self._busy_changed)
        self.service.command_finished.connect(self._command_finished)
        self.age_timer = QTimer(self)
        self.age_timer.setInterval(500)
        self.age_timer.timeout.connect(self._age)
        self.age_timer.start()
        self.sound_timer = QTimer(self)
        self.sound_timer.setInterval(3000)
        self.sound_timer.timeout.connect(self._alarm_sound)
        self.sound_timer.start()
        self._connection(False, "Esperando a la simulación")
        if auto_start:
            QTimer.singleShot(0, self.service.start)

    @staticmethod
    def _muted(text):
        label = QLabel(text)
        label.setObjectName("muted")
        label.setWordWrap(True)
        return label

    def _card(self, title):
        frame = QFrame()
        frame.setObjectName("metricCard")
        box = QVBoxLayout(frame)
        box.setContentsMargins(14, 13, 14, 13)
        box.setSpacing(8)
        box.addWidget(self._muted(title))
        value = QLabel("—")
        value.setStyleSheet("font-size:27px; font-weight:700;")
        value.setWordWrap(True)
        box.addWidget(value)
        detail = QLabel("Sin datos")
        detail.setWordWrap(True)
        box.addWidget(detail)
        box.addStretch()
        return frame, value, detail

    def _button(self, text, address, value, accent=False):
        button = QPushButton(text)
        if accent:
            button.setObjectName("accent")
        button.clicked.connect(lambda: self._command(address, value))
        self.commands.append(button)
        return button

    def _command(self, address, value):
        if self.service.request_command(address, value):
            self.command_label.setText("Enviando orden; esperando confirmación de la simulación…")
        else:
            self.command_label.setText("Esperá la confirmación pendiente o la reconexión con la simulación.")

    def _toggle_zone(self, address):
        if self.state:
            self._command(address, not self.state.coil(address))

    def _toggle_auto(self, address):
        if self.state:
            self._command(address, not self.state.coil(address))

    def _toggle_connection(self):
        if self.service.enabled:
            self.service.stop()
        else:
            self.service.start()
        self.connection_button.setText("Pausar conexión" if self.service.enabled else "Conectar")

    def _connection(self, online, detail):
        old = self.connection_label.text()
        self.connection_label.setText("● Conectado" if online else "○ Sin conexión")
        self.connection_label.setStyleSheet("color:#7fd4a2;" if online else "color:#d9ad78;")
        self.help_label.setText("SIMULACIÓN LOCAL · " + ("Información sincronizada con el recorrido del restaurante." if online
            else detail + ". Iniciá el ejecutable del recorrido para recibir información."))
        if not online:
            self.overview.setText("Sin datos actuales · Revisá la conexión con el recorrido")
            self.overview.setStyleSheet("color:#d9ad78; font-size:17px; font-weight:600; padding:10px 0;")
            self.bio_seen_at = None
            self.state = self.previous = None
            for value in (self.gas_value, self.cylinder_value, self.presence_value, self.bio_value):
                value.setText("—")
            for value in (self.gas_detail, self.cylinder_detail, self.presence_detail, self.bio_detail):
                value.setText("Sin datos actuales")
            self.gas_detail.setStyleSheet("color:#aeb4be;")
            self.level_bar.setValue(0)
            self.level_bar.setEnabled(False)
            self.lights_summary.setText("— / 9 circuitos con luz")
            self.leak_status.setText("Fuga: sin datos")
            for state in self.zone_status.values():
                state.setText("Sin datos")
                state.setStyleSheet("color:#aeb4be;")
        if old != self.connection_label.text():
            self._event(detail)
        self._refresh_controls()

    def _telemetry(self, state):
        old = self.previous
        self.state = self.previous = state
        self.gas_value.setText(f"{state.ppm:,} ppm".replace(",", " "))
        self.gas_detail.setText(ALARM_NAMES[state.alarm])
        self.gas_detail.setStyleSheet("color:" + ("#7fd4a2", "#efc276", "#ff9393")[state.alarm] + ";")
        self.overview.setText(("Sin alarmas de gas · Lecturas actualizadas", "Prealerta de gas · Revisá la concentración en cocina", "Alarma crítica de gas · Atención en cocina")[state.alarm])
        self.overview.setStyleSheet("font-size:17px; font-weight:600; padding:10px 0; color:" + ("#7fd4a2", "#efc276", "#ff9393")[state.alarm] + ";")
        self.cylinder_value.setText(f"{state.level}%")
        self.cylinder_detail.setText(f"{state.net_kg:.2f} kg de gas disponibles\nPeso bruto {state.gross_kg:.2f} kg · Tara {state.gross_kg-state.net_kg:.2f} kg")
        self.level_bar.setEnabled(True)
        self.level_bar.setValue(state.level)
        self.presence_value.setText(f"{int(state.women)+int(state.men)} de 2 ocupados")
        self.presence_detail.setText("Mujeres: " + ("ocupado" if state.women else "libre") + (" · Automático" if state.coil(11) else " · Manual")
                                    + "\nHombres: " + ("ocupado" if state.men else "libre") + (" · Automático" if state.coil(12) else " · Manual"))
        self.bio_value.setText(BIOMETRIC_NAMES[state.biometric])
        if old and old.bio_sequence != state.bio_sequence:
            self.bio_seen_at = datetime.now().strftime("%H:%M:%S")
        self.bio_detail.setText(("Recibido a las " + self.bio_seen_at if self.bio_seen_at else "Sin eventos nuevos desde la conexión") + "\nPrueba simulada · No registra asistencia")
        self.lights_summary.setText(f"{state.active_lights} / 9 circuitos con luz")
        self.leak_status.setText("Fuga: " + ("ACTIVA" if state.coil(10) else "detenida"))
        for address, label in self.zone_status.items():
            text = "Encendida" if state.coil(address) else "Apagada"
            if address in (4, 5):
                text += " · " + ("Auto" if state.coil(address+7) else "Manual")
            label.setText(text)
            label.setStyleSheet("color:" + ("#7fd4a2" if state.coil(address) else "#aeb4be") + ";")
        if old:
            if old.alarm != state.alarm:
                self._event(f"Gas: {ALARM_NAMES[state.alarm]} · {state.ppm} ppm")
            for address, name in enumerate(ZONE_NAMES, 1):
                if old.coil(address) != state.coil(address):
                    self._event(name + ": luz " + ("encendida" if state.coil(address) else "apagada"))
            for attr, name in (("women", "Mujeres"), ("men", "Hombres")):
                if getattr(old, attr) != getattr(state, attr):
                    self._event(name + ": " + ("presencia detectada" if getattr(state, attr) else "sin presencia"))
            if old.bio_sequence != state.bio_sequence:
                self._event("Biometría simulada: " + BIOMETRIC_NAMES[state.biometric])
        self._refresh_controls()
        self._age()

    def _refresh_controls(self):
        ready = self.service.online and self.state is not None and not self.busy
        for button in self.commands:
            button.setEnabled(ready)
        for address, button in self.zone_buttons.items():
            auto = self.state and address in (4, 5) and self.state.coil(address+7)
            button.setEnabled(bool(ready))
            button.setText(("Apagar" if self.state.coil(address) else "Encender") if self.state else "—")
            button.setToolTip("Esta orden pasa únicamente este baño a modo manual." if auto else "")
        for address, button in self.auto_buttons.items():
            button.setEnabled(ready)
            button.setText(("Auto → Manual" if self.state.coil(address) else "Manual → Auto") if self.state else "Sin datos")

    def _busy_changed(self, busy):
        self.busy = busy
        self._refresh_controls()

    def _command_finished(self, address, success, detail):
        self.command_label.setText(detail)
        self.command_label.setStyleSheet("color:#7fd4a2;" if success else "color:#efc276;")
        names = {0: "Iluminación general", 10: "Fuga", 11: "Modo mujeres", 12: "Modo hombres",
                 13: "Presencia mujeres", 14: "Presencia hombres", 15: "Huella aceptada",
                 16: "Huella rechazada", 17: "Sustitución de cilindro"}
        subject = ZONE_NAMES[address-1] if 1 <= address <= 9 else names.get(address, "Control")
        self._event(subject + ": " + detail)

    def _age(self):
        if self.service.last_received:
            age = time.monotonic() - self.service.last_received
            self.age_label.setText(f"Última lectura hace {age:.1f} s" + (" · Datos sin vigencia" if not self.service.online else " · Actualización automática"))
        else:
            self.age_label.setText("Esperando la primera lectura del recorrido")

    def _event(self, text):
        self.events.appendPlainText(datetime.now().strftime("%H:%M:%S") + "  " + text)

    def _alarm_sound(self):
        if self.sound_check.isChecked() and self.service.online and self.state and self.state.alarm == 2:
            QApplication.beep()

    def shutdown(self):
        self.age_timer.stop()
        self.sound_timer.stop()
        self.service.stop()

    def closeEvent(self, event):
        self.shutdown()
        super().closeEvent(event)
