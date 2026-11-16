from flask import Blueprint, jsonify, request, current_app
import sqlite3
from logger_setup import setup_logger
from server.routes.kds import require_auth
from src.services.attendance_service import attendance_service
from src.database.repositories.employees import employee_repo

logger = setup_logger()
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/registrar', methods=['POST'])
@require_auth
def registrar_asistencia_movil():
    try:
        worker = current_app.worker
        data = request.json
        if not data or 'employee_id' not in data or 'deviceId' not in data: return jsonify({"error": "Datos incompletos"}), 400
        employee_id = data.get('employee_id')
        device_id = data.get('deviceId')
        if not employee_id or not isinstance(device_id, str) or not device_id.strip():
            return jsonify({
                "error": "invalid_request",
                "message": "No se recibieron los datos del empleado o del dispositivo."
            }), 400

        empleado = employee_repo.get_employee_by_id(employee_id)
        if not empleado:
            return jsonify({
                "error": "not_found",
                "message": "No encontramos ese usuario. Actualiza la lista e inténtalo de nuevo."
            }), 404

        # Un teléfono solo puede pertenecer a una cuenta. No se exponen nombres
        # de otros empleados en respuestas visibles para el usuario.
        dispositivo_asignado = employee_repo.get_employee_by_device(device_id)
        if dispositivo_asignado and dispositivo_asignado.get("id_empleado") != employee_id:
            return jsonify({
                "error": "device_taken",
                "message": "Este teléfono ya está vinculado a otra cuenta. Contacta al administrador para actualizar la vinculación."
            }), 409

        if not empleado.get("deviceId"):
            try:
                employee_repo.link_device_to_employee(employee_id, device_id)
            except sqlite3.IntegrityError:
                return jsonify({
                    "error": "device_taken",
                    "message": "Este teléfono ya está vinculado a otra cuenta. Contacta al administrador para actualizar la vinculación."
                }), 409
            worker._registrar_evento(employee_id, "entrada")
            return jsonify({"status": "success", "message": "Dispositivo vinculado y entrada marcada"}), 201
        elif empleado.get("deviceId") != device_id:
            return jsonify({
                "error": "device_mismatch",
                "message": "Tu cuenta ya está vinculada a otro teléfono. Contacta al administrador para actualizar la vinculación."
            }), 409
        
        import datetime
        last_event = attendance_service.get_last_attendance_event(employee_id)
        if last_event:
            last_ts = datetime.datetime.fromisoformat(last_event['timestamp'])
            now = datetime.datetime.now()
            diff = (now - last_ts).total_seconds()
            if diff < 3: return jsonify({"status": "ignored", "message": f"Espera {3 - int(diff)}s antes de marcar de nuevo."}), 200

        tipo = "salida" if last_event and last_event['tipo'] == 'entrada' else "entrada"
        worker._registrar_evento(employee_id, tipo)
        return jsonify({"status": "success", "message": f"{tipo.capitalize()} registrada"}), 200
    except Exception as e:
        logger.error(f"Error en registrar_asistencia_movil: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
