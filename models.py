"""
MODEL
-----
Toda la lógica de datos y de negocio vive aquí. Soporta múltiples
familias por usuario y sistema de roles (admin / miembro).
"""

import hashlib
import json
import os
import secrets as _secrets_mod
import tempfile
import uuid
from datetime import date, datetime, timedelta

import firebase_admin
from firebase_admin import credentials, db

try:
    import bcrypt as _bcrypt
except ImportError:
    _bcrypt = None


# -------------------------------------------------------------
# HELPERS: HASHING SEGURO
# -------------------------------------------------------------
def _hash_password(password: str) -> str:
    if _bcrypt:
        return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
    salt = _secrets_mod.token_hex(16)
    return f"sha256${salt}${hashlib.sha256((salt + password).encode()).hexdigest()}"


def _verify_password(password: str, stored: str) -> bool:
    if _bcrypt and stored.startswith("$2"):
        return _bcrypt.checkpw(password.encode(), stored.encode())
    if stored.startswith("sha256$"):
        parts = stored.split("$")
        if len(parts) == 3:
            salt, expected = parts[1], parts[2]
            return hashlib.sha256((salt + password).encode()).hexdigest() == expected
    return hashlib.sha256(password.encode()).hexdigest() == stored


def _sanitize(text: str) -> str:
    """Escapa HTML para prevenir XSS."""
    import html as _html
    return _html.escape(str(text)) if text else ""


# -------------------------------------------------------------
# CREDENCIALES ADMIN (desde secrets)
# -------------------------------------------------------------
def get_admin_credentials(secrets):
    """Lee las credenciales admin desde st.secrets."""
    if not secrets or not hasattr(secrets, "get"):
        return {}
    return {
        "user_id": secrets.get("admin_user_id", "admin_ifamily_001"),
        "nombre": secrets.get("admin_nombre", "Administrador iFamily"),
        "email": secrets.get("admin_email", "admin@ifamily.com"),
        "password_hash": _hash_password(secrets.get("admin_password", "Admin123456")),
        "rol": "admin",
    }


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
                key_dict = None
                if secrets and hasattr(secrets, "get"):
                    firebase_json_str = secrets.get("firebase_json", "")
                    if firebase_json_str:
                        key_dict = json.loads(firebase_json_str)
                if not key_dict:
                    for attr in ("firebase_json", "FIREBASE_JSON", "firebase_key_json"):
                        if secrets and hasattr(secrets, "get"):
                            val = secrets.get(attr, "")
                            if val:
                                key_dict = json.loads(val) if isinstance(val, str) else val
                                break
                if not key_dict:
                    _a = secrets.get("_firebase_a", "") if secrets and hasattr(secrets, "get") else ""
                    _b = secrets.get("_firebase_b", "") if secrets and hasattr(secrets, "get") else ""
                    if _a and _b:
                        import base64
                        key_dict = json.loads(base64.b64decode(_a + _b).decode("utf-8"))
                if not key_dict:
                    self.error = "Firebase credentials not found in secrets. Add firebase_json to .streamlit/secrets.toml"
                    self.ok = False
                    return
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
                json.dump(key_dict, tmp)
                tmp.close()
                cred = credentials.Certificate(tmp.name)
                os.unlink(tmp.name)
                firebase_db_url = key_dict.get("databaseURL", "https://ifamily-fa8b7-default-rtdb.firebaseio.com/")
                firebase_admin.initialize_app(cred, {"databaseURL": firebase_db_url})
                self.ok = True
            except Exception as e:
                self.error = f"Error de conexión: {str(e)[:120]}"
                self.ok = False
        else:
            self.ok = True

    def reference(self, path):
        if not self.ok:
            return None
        return db.reference(path)


# -------------------------------------------------------------
# MODELO: USUARIOS
# -------------------------------------------------------------
class UserModel:
    """Gestión de usuarios, autenticación y perfiles."""

    def __init__(self, firebase_service: FirebaseService):
        self.ref = firebase_service.reference("users")

    def get_by_id(self, user_id):
        data = self.ref.child(user_id).get()
        return data or {}

    def create_or_update(self, user_id, nombre, email="", photo_url=""):
        existing = self.get_by_id(user_id)
        now = str(datetime.now())

        if existing:
            self.ref.child(user_id).update({
                "nombre": nombre,
                "email": email,
                "photo_url": photo_url,
                "last_login": now,
            })
        else:
            self.ref.child(user_id).set({
                "user_id": user_id,
                "nombre": nombre,
                "email": email,
                "photo_url": photo_url,
                "rol": "miembro",
                "familias": {},
                "familia_activa": "",
                "created_at": now,
                "last_login": now,
            })

    def get_familias(self, user_id):
        user = self.get_by_id(user_id)
        return user.get("familias", {})

    def add_familia_to_user(self, user_id, familia_id, familia_nombre, rol_en_familia="miembro"):
        self.ref.child(user_id).child("familias").child(familia_id).set({
            "nombre": familia_nombre,
            "rol_en_familia": rol_en_familia,
        })

    def set_familia_activa(self, user_id, familia_id):
        self.ref.child(user_id).update({"familia_activa": familia_id})

    def get_familia_activa(self, user_id):
        user = self.get_by_id(user_id)
        return user.get("familia_activa", "")

    def update_rol(self, user_id, rol):
        self.ref.child(user_id).update({"rol": rol})

    def is_admin(self, user_id):
        user = self.get_by_id(user_id)
        return user.get("rol") == "admin"

    def get_all_users(self):
        return self.ref.get() or {}

    def create_user_by_admin(self, nombre, email, password, rol="miembro"):
        """Crea un usuario nuevo desde el panel de admin."""
        users = self.get_all_users()

        for uid, udata in users.items():
            if udata.get("nombre", "").lower() == nombre.lower():
                return None, "Ya existe un usuario con ese nombre"

        user_id = "user_" + str(uuid.uuid4())[:8]
        now = str(datetime.now())

        self.ref.child(user_id).set({
            "user_id": user_id,
            "nombre": nombre,
            "email": email,
            "photo_url": "",
            "rol": rol,
            "password_hash": _hash_password(password),
            "familias": {},
            "familia_activa": "",
            "created_at": now,
            "last_login": now,
            "creado_por_admin": True,
        })

        return user_id, None

    def delete_user(self, user_id):
        """Elimina un usuario (solo admin)."""
        if user_id == "admin_ifamily_001":
            return False, "No se puede eliminar la cuenta admin"
        self.ref.child(user_id).delete()
        return True, None

    def reset_password(self, user_id, new_password):
        """Resetea la contraseña de un usuario (solo admin)."""
        self.ref.child(user_id).update({
            "password_hash": _hash_password(new_password)
        })
        return True, None

    def init_admin_account(self, secrets):
        """Crea la cuenta admin si no existe."""
        admin = get_admin_credentials(secrets)
        if not admin:
            return
        existing = self.get_by_id(admin["user_id"])
        if not existing:
            self.ref.child(admin["user_id"]).set({
                "user_id": admin["user_id"],
                "nombre": admin["nombre"],
                "email": admin["email"],
                "rol": "admin",
                "password_hash": admin["password_hash"],
                "familias": {},
                "familia_activa": "",
                "created_at": str(datetime.now()),
                "last_login": str(datetime.now()),
                "es_admin_inicial": True,
            })


# -------------------------------------------------------------
# MODELO: FAMILIAS
# -------------------------------------------------------------
class FamilyModel:
    """Gestión de familias: creación, unión y miembros."""

    def __init__(self, firebase_service: FirebaseService):
        self.ref = firebase_service.reference("families")
        self.user_model = UserModel(firebase_service)
        self.firebase_service = firebase_service

    def create(self, nombre, creador_id):
        import uuid
        familia_id = str(uuid.uuid4())[:8]
        codigo = _secrets_mod.token_urlsafe(8)[:12].upper()
        now = str(datetime.now())

        self.ref.child(familia_id).set({
            "family_id": familia_id,
            "nombre": nombre,
            "creado_por": creador_id,
            "created_at": now,
            "miembros": {
                creador_id: {
                    "nombre": self.user_model.get_by_id(creador_id).get("nombre", ""),
                    "rol_en_familia": "admin",
                    "unido_en": now,
                }
            },
            "codigo_invitacion": codigo,
        })

        self.user_model.add_familia_to_user(creador_id, familia_id, nombre, "admin")
        self.user_model.set_familia_activa(creador_id, familia_id)

        return familia_id

    def join(self, user_id, codigo_invitacion):
        familias = self.ref.get() or {}
        for fid, fdata in familias.items():
            if fdata.get("codigo_invitacion", "").upper() == codigo_invitacion.upper():
                now = str(datetime.now())
                user_data = self.user_model.get_by_id(user_id)

                self.ref.child(fid).child("miembros").child(user_id).set({
                    "nombre": user_data.get("nombre", ""),
                    "rol_en_familia": "miembro",
                    "unido_en": now,
                })

                self.user_model.add_familia_to_user(user_id, fid, fdata.get("nombre", ""), "miembro")
                self.user_model.set_familia_activa(user_id, fid)

                return fid, fdata.get("nombre", "")
        return None, None

    def get_miembros(self, familia_id):
        data = self.ref.child(familia_id).child("miembros").get()
        return data or {}

    def get_familia(self, familia_id):
        return self.ref.child(familia_id).get() or {}

    def get_codigo_invitacion(self, familia_id):
        data = self.ref.child(familia_id).child("codigo_invitacion").get()
        return data or ""

    def is_miembro(self, familia_id, user_id):
        miembros = self.get_miembros(familia_id)
        return user_id in miembros

    def get_user_familias(self, user_id):
        user_familias = self.user_model.get_familias(user_id)
        if not user_familias:
            return []
        result = []
        for fid, fdata in user_familias.items():
            familia = self.get_familia(fid)
            if familia:
                result.append({
                    "id": fid,
                    "nombre": familia.get("nombre", fdata.get("nombre", "")),
                    "rol_en_familia": fdata.get("rol_en_familia", "miembro"),
                    "miembros_count": len(familia.get("miembros", {})),
                })
        return result


# -------------------------------------------------------------
# MODELO: CITAS MÉDICAS (multi-familia)
# -------------------------------------------------------------
class CitaModel:
    """Reglas de negocio y acceso a datos para las citas médicas."""

    def __init__(self, firebase_service: FirebaseService, familia_id: str):
        self.ref = firebase_service.reference(f"familia_data/{familia_id}/citas")

    def get_all(self):
        data = self.ref.get() if self.ref else None
        return data or {}

    def get_programadas(self):
        return {k: v for k, v in self.get_all().items() if v.get("estado", "programada") == "programada"}

    def get_realizadas(self):
        return {k: v for k, v in self.get_all().items() if v.get("estado") == "realizada"}

    def proxima_cita(self):
        programadas = self.get_programadas()
        if not programadas:
            return None, None
        ordenadas = sorted(programadas.items(), key=lambda i: (i[1].get("fecha", ""), i[1].get("hora", "")))
        return ordenadas[0]

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

    @staticmethod
    def estado_visual(fecha_str):
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
# MODELO: SERVICIOS PÚBLICOS (multi-familia)
# -------------------------------------------------------------
class ServicioModel:
    """Reglas de negocio y acceso a datos para los códigos de servicios."""

    ICONOS = {
        "⚡ Luz": "⚡", "💧 Agua": "💧", "🔥 Gas": "🔥",
        "🌐 Internet": "🌐", "📞 Teléfono": "📞", "Otro": "🧾",
    }

    def __init__(self, firebase_service: FirebaseService, familia_id: str):
        self.ref = firebase_service.reference(f"familia_data/{familia_id}/servicios")

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


# -------------------------------------------------------------
# MODELO: PERSONAS DE SEGUIMIENTO (multi-familia)
# -------------------------------------------------------------
class PersonaModel:
    """Personas cuyo seguimiento se registra en la familia (hijos, padres, etc.)."""

    def __init__(self, firebase_service: FirebaseService, familia_id: str):
        self.ref = firebase_service.reference(f"familia_data/{familia_id}/personas")

    def get_all(self):
        data = self.ref.get() if self.ref else None
        return data or {}

    def get_by_id(self, persona_id):
        data = self.ref.child(persona_id).get()
        return data or {}

    def crear(self, nombre, dni, relacion, fecha_nacimiento, notas, usuario):
        persona_id = str(uuid.uuid4())[:8]
        self.ref.child(persona_id).set({
            "persona_id": persona_id,
            "nombre": nombre,
            "dni": dni,
            "relacion": relacion,
            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else "",
            "notas": notas,
            "creado_por": usuario,
            "created_at": str(datetime.now()),
        })
        return persona_id

    def eliminar(self, persona_id):
        self.ref.child(persona_id).delete()

    def nombres(self):
        """Lista de nombres para usar en selectboxes."""
        return [p.get("nombre", "") for p in self.get_all().values()]
