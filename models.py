"""
MODEL
-----
Toda la lógica de datos y de negocio vive aquí. Esta capa no importa
streamlit ni sabe nada de la interfaz: solo habla con Firebase y aplica
reglas (por ejemplo, calcular si una cita es "Hoy", "Esta semana", etc.).
Así, si el día de mañana cambian de Firebase a otra base de datos, solo
se toca este archivo.
"""

import json
from datetime import date, datetime

import firebase_admin
from firebase_admin import credentials, db


# -------------------------------------------------------------
# INFRAESTRUCTURA: CONEXIÓN A FIREBASE
# -------------------------------------------------------------
class FirebaseService:
    """Encapsula la inicialización y el acceso a Firebase Realtime Database."""

    def __init__(self, secrets):
        self.ok = False
        self.error = None
        self._init(secrets)

    def _init(self, secrets):
        if not firebase_admin._apps:
            try:
                if "FIREBASE_KEY" in secrets:
                    key_dict = json.loads(secrets["FIREBASE_KEY"])
                    cred = credentials.Certificate(key_dict)
                    db_url = secrets["FIREBASE_DB_URL"]
                else:
                    cred = credentials.Certificate("firebase_key.json")
                    db_url = "https://TU-PROYECTO-default-rtdb.firebaseio.com/"

                firebase_admin.initialize_app(cred, {"databaseURL": db_url})
                self.ok = True
            except Exception as e:
                self.error = str(e)
                self.ok = False
        else:
            self.ok = True

    def reference(self, path):
        if not self.ok:
            return None
        return db.reference(path)


# -------------------------------------------------------------
# MODELO: CITAS MÉDICAS
# -------------------------------------------------------------
class CitaModel:
    """Reglas de negocio y acceso a datos para las citas médicas."""

    def __init__(self, firebase_service: FirebaseService):
        self.ref = firebase_service.reference("citas")

    # --- Lectura ---
    def get_all(self):
        data = self.ref.get() if self.ref else None
        return data or {}

    def get_programadas(self):
        return {k: v for k, v in self.get_all().items() if v.get("estado", "programada") == "programada"}

    def get_realizadas(self):
        return {k: v for k, v in self.get_all().items() if v.get("estado") == "realizada"}

    def proxima_cita(self):
        """Devuelve (key, cita) de la cita programada más cercana, o (None, None)."""
        programadas = self.get_programadas()
        if not programadas:
            return None, None
        ordenadas = sorted(programadas.items(), key=lambda i: (i[1].get("fecha", ""), i[1].get("hora", "")))
        return ordenadas[0]

    # --- Escritura ---
    def crear(self, paciente, especialidad, lugar, fecha, hora, notas, usuario):
        nueva_cita = {
            "paciente": paciente,
            "especialidad": especialidad,
            "lugar": lugar,
            "fecha": str(fecha),
            "hora": str(hora),
            "notas": notas,
            "estado": "programada",
            "registrado_por": usuario,
        }
        self.ref.push(nueva_cita)

    def marcar_realizada(self, key, diagnostico, tratamiento, recomendaciones, proxima_sugerida, usuario):
        self.ref.child(key).update({
            "estado": "realizada",
            "diagnostico": diagnostico,
            "tratamiento": tratamiento,
            "recomendaciones": recomendaciones,
            "proxima_cita_sugerida": str(proxima_sugerida) if proxima_sugerida else "",
            "fecha_registro_historial": str(date.today()),
            "actualizado_por": usuario,
        })

    def eliminar(self, key):
        self.ref.child(key).delete()

    # --- Reglas de negocio (presentación derivada de los datos) ---
    @staticmethod
    def estado_visual(fecha_str):
        """Clasifica una fecha de cita en Hoy / Esta semana / Próximamente / Atrasada."""
        try:
            f = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return "", ""
        dias = (f - date.today()).days
        if dias < 0:
            return "Atrasada", "badge-atrasada"
        if dias == 0:
            return "Hoy", "badge-hoy"
        if dias <= 7:
            return "Esta semana", "badge-semana"
        return "Próximamente", "badge-proximamente"

    @staticmethod
    def filtrar_por_paciente(citas, paciente):
        if paciente == "Todos":
            return citas
        return {k: v for k, v in citas.items() if v.get("paciente") == paciente}

    @staticmethod
    def ordenar_por_fecha(citas, descendente=False):
        return sorted(citas.items(), key=lambda i: (i[1].get("fecha", ""), i[1].get("hora", "")), reverse=descendente)


# -------------------------------------------------------------
# MODELO: SERVICIOS PÚBLICOS
# -------------------------------------------------------------
class ServicioModel:
    """Reglas de negocio y acceso a datos para los códigos de servicios."""

    ICONOS = {
        "⚡ Luz": "⚡", "💧 Agua": "💧", "🔥 Gas": "🔥",
        "🌐 Internet": "🌐", "📞 Teléfono": "📞", "Otro": "🧾",
    }

    def __init__(self, firebase_service: FirebaseService):
        self.ref = firebase_service.reference("servicios")

    def get_all(self):
        data = self.ref.get() if self.ref else None
        return data or {}

    def crear(self, tipo, empresa, codigo, titular, usuario):
        nuevo_servicio = {
            "tipo": tipo,
            "empresa": empresa,
            "codigo": codigo,
            "titular": titular,
            "registrado_por": usuario,
            "fecha_registro": str(date.today()),
        }
        self.ref.push(nuevo_servicio)

    def eliminar(self, key):
        self.ref.child(key).delete()

    @classmethod
    def icono(cls, tipo):
        return cls.ICONOS.get(tipo, "🧾")

    @staticmethod
    def filtrar_por_tipo(servicios, tipo):
        if tipo == "Todos":
            return servicios
        return {k: v for k, v in servicios.items() if v.get("tipo") == tipo}