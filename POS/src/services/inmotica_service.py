"""Asynchronous, loopback-only Modbus TCP client for the restaurant simulator.

Uses Qt sockets rather than blocking I/O on the POS event loop. Commands are
confirmed from telemetry and never replayed automatically after a disconnect.
"""
from dataclasses import dataclass
import struct
import time

from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtNetwork import QAbstractSocket, QTcpSocket


ZONE_NAMES = ("Cocina", "Bodega", "Oficina", "Baño mujeres", "Baño hombres",
              "Mesas", "Barra / caja", "Pasillo", "Ross Tattoo")
ALARM_NAMES = ("Normal", "Prealerta", "Alarma crítica")
BIOMETRIC_NAMES = ("Sin lecturas", "Identificación aceptada", "Huella no reconocida")


@dataclass(frozen=True)
class InmoticaSnapshot:
    ppm: int
    alarm: int
    gross_kg: float
    net_kg: float
    level: int
    women: bool
    men: bool
    biometric: int
    mask: int
    bio_sequence: int

    @classmethod
    def from_registers(cls, registers):
        if len(registers) != 11 or registers[8] != 0x5055:
            raise ValueError("El equipo no corresponde al simulador de El Puestito")
        if (registers[1] not in range(3) or registers[7] not in range(3)
                or registers[5] not in (0, 1) or registers[6] not in (0, 1)
                or registers[4] > 100 or registers[3] > registers[2]
                or registers[9] > 0x1FFF):
            raise ValueError("Telemetría fuera de rango")
        return cls(registers[0], registers[1], registers[2] / 100,
                   registers[3] / 100, registers[4], bool(registers[5]),
                   bool(registers[6]), registers[7], registers[9], registers[10])

    def coil(self, address):
        return bool(self.mask & (1 << address))

    @property
    def active_lights(self):
        return sum(self.coil(i) for i in range(1, 10))


class InmoticaService(QObject):
    telemetry = pyqtSignal(object)
    connection_changed = pyqtSignal(bool, str)
    command_finished = pyqtSignal(int, bool, str)
    busy_changed = pyqtSignal(bool)

    def __init__(self, parent=None, *, port=15020, poll_ms=500, timeout_ms=1800):
        super().__init__(parent)
        self.port = port
        self.timeout_ms = timeout_ms
        self.online = False
        self.enabled = False
        self.snapshot = None
        self.last_received = 0.0
        self.pending = None
        self.command = None
        self.transaction = 0
        self.buffer = bytearray()
        self._dropping = False
        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self._connected)
        self.socket.readyRead.connect(self._receive)
        self.socket.disconnected.connect(self._disconnected)
        self.socket.errorOccurred.connect(lambda _: self._fail(self.socket.errorString()))
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(poll_ms)
        self.poll_timer.timeout.connect(self._poll)
        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(lambda: self._fail("Sin respuesta del simulador"))
        self.retry_timer = QTimer(self)
        self.retry_timer.setSingleShot(True)
        self.retry_timer.setInterval(1500)
        self.retry_timer.timeout.connect(self._connect)

    def start(self):
        if self.enabled:
            return
        self.enabled = True
        self.poll_timer.start()
        self._connect()

    def stop(self):
        self.enabled = False
        self.poll_timer.stop()
        self.retry_timer.stop()
        self._fail("Conexión pausada")

    def _connect(self):
        if not self.enabled:
            return
        self.connection_changed.emit(False, "Conectando con la simulación…")
        self.timeout_timer.start(self.timeout_ms)
        self.socket.connectToHost("127.0.0.1", self.port)

    def _connected(self):
        self.timeout_timer.stop()
        self._poll()

    def _disconnected(self):
        if self.online or self.pending or self.command:
            self._fail("la simulación se desconectó")

    def _fail(self, reason):
        if self._dropping:
            return
        self._dropping = True
        self.timeout_timer.stop()
        self.online = False
        self.snapshot = None
        self.pending = None
        self.buffer.clear()
        self.socket.abort()
        if self.command:
            self._finish_command(False, "Sin confirmar; la orden no se reenviará automáticamente")
        self.connection_changed.emit(False, reason)
        if self.enabled and not self.retry_timer.isActive():
            self.retry_timer.start()
        self._dropping = False

    def _poll(self):
        if (not self.enabled or self.pending
                or self.socket.state() != QAbstractSocket.SocketState.ConnectedState):
            return
        self._send(struct.pack(">BHH", 4, 0, 11))

    def _send(self, pdu):
        self.transaction = (self.transaction + 1) & 0xFFFF
        self.pending = (self.transaction, pdu)
        frame = struct.pack(">HHHB", self.transaction, 0, len(pdu) + 1, 1) + pdu
        if self.socket.write(frame) != len(frame):
            self._fail("No se pudo enviar la petición")
            return
        self.timeout_timer.start(self.timeout_ms)

    def request_command(self, address, value):
        if not 0 <= address <= 17 or (address >= 13 and not value):
            raise ValueError("Orden no admitida por el simulador")
        if not self.online or self.command or time.monotonic() - self.last_received > 2.5:
            return False
        self.command = {"address": address, "value": bool(value), "sent": False,
                        "acked": False, "before": self.snapshot,
                        "deadline": time.monotonic() + 4.0}
        self.busy_changed.emit(True)
        if not self.pending:
            self._send_command()
        return True

    def _send_command(self):
        self.command["sent"] = True
        self._send(struct.pack(">BHH", 5, self.command["address"],
                               0xFF00 if self.command["value"] else 0))

    def _receive(self):
        self.buffer.extend(bytes(self.socket.readAll()))
        if len(self.buffer) > 1024:
            self._fail("Respuesta Modbus demasiado grande")
            return
        while len(self.buffer) >= 7:
            tx, protocol, length, unit = struct.unpack(">HHHB", self.buffer[:7])
            if protocol != 0 or unit != 1 or not 2 <= length <= 254:
                self._fail("Cabecera Modbus inválida")
                return
            if len(self.buffer) < 6 + length:
                return
            pdu = bytes(self.buffer[7:6 + length])
            del self.buffer[:6 + length]
            if not self.pending or tx != self.pending[0]:
                self._fail("Respuesta Modbus fuera de secuencia")
                return
            request = self.pending[1]
            self.pending = None
            self.timeout_timer.stop()
            if pdu[0] != request[0]:
                self._fail("El simulador rechazó la petición Modbus")
                return
            if pdu[0] == 5:
                if pdu != request or not self.command:
                    self._fail("Confirmación de escritura inválida")
                    return
                self.command["acked"] = True
                QTimer.singleShot(80, self._poll)
            else:
                if len(pdu) != 24 or pdu[1] != 22:
                    self._fail("Se esperaban once registros de la simulación")
                    return
                try:
                    snapshot = InmoticaSnapshot.from_registers(struct.unpack(">11H", pdu[2:]))
                except ValueError as error:
                    self._fail(str(error))
                    return
                self.snapshot = snapshot
                self.last_received = time.monotonic()
                if not self.online:
                    self.online = True
                    self.connection_changed.emit(True, "Conectado con la simulación")
                self.telemetry.emit(snapshot)
                if self.command:
                    if time.monotonic() > self.command["deadline"]:
                        self._finish_command(False, "La telemetría no confirmó el cambio solicitado")
                    elif not self.command["sent"]:
                        self._send_command()
                    elif self.command["acked"] and self._confirmed(snapshot):
                        self._finish_command(True, "Cambio confirmado por la simulación")

    def _confirmed(self, state):
        cmd = self.command
        address, value = cmd["address"], cmd["value"]
        if address == 0:
            return (all(state.coil(i) == value for i in range(1, 10))
                    and not state.coil(11) and not state.coil(12))
        if address <= 12:
            return state.coil(address) == value
        if address in (13, 14):
            return state.women if address == 13 else state.men
        if address in (15, 16):
            return (state.bio_sequence != cmd["before"].bio_sequence
                    and state.biometric == (1 if address == 15 else 2))
        return state.level >= 99 and state.net_kg >= 14.9

    def _finish_command(self, success, detail):
        address = self.command["address"]
        self.command = None
        self.busy_changed.emit(False)
        self.command_finished.emit(address, success, detail)
