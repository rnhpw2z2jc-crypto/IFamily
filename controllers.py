"""
CONTROLLER
----------
Maneja autenticación, familias, formularios y eventos.
Conecta directamente con el backend (models.py).
"""

from datetime import date, datetime, timedelta, date as _date_class
import time

import streamlit as st

from models import (
    FirebaseService, UserModel, FamilyModel,
    CitaModel, ServicioModel, PersonaModel,
    get_admin_credentials, _hash_password, _verify_password, _sanitize,
)
import views

# -------------------------------------------------------------
# CONSTANTES DE SEGURIDAD
# -------------------------------------------------------------
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 300
SESSION_TIMEOUT_SECONDS = 3600


# -------------------------------------------------------------
# CONTROLADOR: AUTENTICACIÓN
# -------------------------------------------------------------
class AuthController:
    """Manejo de sesión: registro, login y switch de familias."""

    def __init__(self, user_model: UserModel, family_model: FamilyModel):
        self.user_model = user_model
        self.family_model = family_model

    def _generate_session_id(self):
        import uuid
        return str(uuid.uuid4())[:12]

    def render_login(self):
        views.inject_auth_css()

        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "login"

        st.markdown("""
        <div class="auth-container">
            <div class="auth-logo">
                <div class="auth-logo-icon">🏠</div>
            </div>
            <div class="auth-title">iFamily</div>
            <div class="auth-subtitle">Control familiar inteligente</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            if st.session_state.auth_mode == "login":
                self._render_login_form()
            elif st.session_state.auth_mode == "register":
                self._render_register_form()

    def _render_login_form(self):
        if "login_attempts" not in st.session_state:
            st.session_state.login_attempts = 0
        if "login_lockout_until" not in st.session_state:
            st.session_state.login_lockout_until = 0

        if time.time() < st.session_state.login_lockout_until:
            remaining = int(st.session_state.login_lockout_until - time.time())
            st.error(f"Demasiados intentos fallidos. Espera {remaining} segundos.")
            return

        with st.form("login_form"):
            st.markdown("**Iniciar Sesión**")
            email = st.text_input("Email", placeholder="tu@email.com")
            password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")

            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                if not email or not password:
                    st.error("Completa tu email y contraseña.")
                elif len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    user_id = self._login(email, password)
                    if user_id:
                        st.session_state.login_attempts = 0
                        st.session_state.user_id = user_id
                        user_data = self.user_model.get_by_id(user_id)
                        st.session_state.nombre_usuario = user_data.get("nombre", "")
                        st.session_state.login_time = time.time()
                        self.user_model.ref.child(user_id).update({"last_login": str(datetime.now())})
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
                            st.session_state.login_lockout_until = time.time() + LOGIN_LOCKOUT_SECONDS
                            st.error("Demasiados intentos. Cuenta bloqueada temporalmente.")
                        else:
                            st.error("Credenciales incorrectas. Verifica tu email y contraseña.")

        st.markdown("""
        <div class="auth-link">
            ¿No tienes cuenta? <a href="#">Regístrate aquí</a>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Crear nueva cuenta", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()

    def _render_register_form(self):
        with st.form("register_form"):
            st.markdown("**Crear Cuenta**")
            nombre = st.text_input("Tu nombre completo", placeholder="Ej. Carlos García")
            email = st.text_input("Email", placeholder="tu@email.com")
            password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            password2 = st.text_input("Confirmar contraseña", type="password")

            if st.form_submit_button("Crear Cuenta", use_container_width=True):
                if not nombre or not password:
                    st.error("Completa todos los campos.")
                elif len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                elif password != password2:
                    st.error("Las contraseñas no coinciden.")
                else:
                    user_id = self._register(nombre, email, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.nombre_usuario = nombre
                        st.success("¡Cuenta creada!")
                        st.rerun()
                    else:
                        st.error("Error al crear la cuenta.")

        st.markdown("""
        <div class="auth-link">
            ¿Ya tienes cuenta? <a href="#">Inicia sesión</a>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Volver al login", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()

    def _login(self, email, password):
        """Login: verifica admin predefinido primero, luego usuarios de Firebase."""
        admin = get_admin_credentials(st.secrets)
        if admin and email.lower() == admin["email"].lower() and _verify_password(password, admin["password_hash"]):
            self.user_model.init_admin_account(st.secrets)
            return admin["user_id"]

        users = self.user_model.get_all_users()
        for uid, udata in users.items():
            if (udata.get("email", "").lower() == email.lower() and
                    _verify_password(password, udata.get("password_hash", ""))):
                return uid
        return None

    def _register(self, nombre, email, password):
        """Registro: crea usuario nuevo."""
        import uuid
        user_id = "user_" + str(uuid.uuid4())[:8]

        users = self.user_model.get_all_users()
        for uid, udata in users.items():
            if udata.get("nombre", "").lower() == nombre.lower():
                return None

        self.user_model.create_or_update(user_id, nombre, email)
        self.user_model.ref.child(user_id).update({
            "password_hash": _hash_password(password)
        })
        return user_id

    def check_session(self):
        if "user_id" not in st.session_state or not st.session_state.user_id:
            return False
        login_time = st.session_state.get("login_time", 0)
        if login_time and (time.time() - login_time) > SESSION_TIMEOUT_SECONDS:
            self.logout()
            return False
        return True

    def logout(self):
        for key in ["user_id", "nombre_usuario", "familia_activa", "familia_id", "login_time"]:
            st.session_state.pop(key, None)
        st.rerun()

    def render_sidebar_session(self, user_model, family_model):
        with st.sidebar:
            user_id = st.session_state.user_id
            user_data = user_model.get_by_id(user_id)
            nombre = user_data.get("nombre", "Sin nombre")

            familias = family_model.get_user_familias(user_id)

            if familias:
                familia_activa_id = user_model.get_familia_activa(user_id)

                nombres_familias = [f["nombre"] for f in familias]
                ids_familias = [f["id"] for f in familias]

                idx = 0
                if familia_activa_id in ids_familias:
                    idx = ids_familias.index(familia_activa_id)

                familiaSeleccionada = st.selectbox(
                    "Tu familia activa",
                    nombres_familias,
                    index=idx,
                    key="select_familia"
                )

                selected_idx = nombres_familias.index(familiaSeleccionada)
                nueva_familia_id = ids_familias[selected_idx]

                if nueva_familia_id != familia_activa_id:
                    user_model.set_familia_activa(user_id, nueva_familia_id)
                    st.session_state.familia_id = nueva_familia_id
                    st.rerun()

                familia_data = familias[selected_idx]
                views.render_user_info(nombre, familia_data["nombre"], familia_data["rol_en_familia"])

                st.session_state.familia_id = familia_activa_id
            else:
                st.info("No perteneces a ninguna familia aún.")
                st.session_state.familia_id = ""

            st.divider()

            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                self.logout()

        return st.session_state.get("familia_id", "")


# -------------------------------------------------------------
# CONTROLADOR: GESTIÓN DE FAMILIAS
# -------------------------------------------------------------
class FamilyController:
    """Crear familia, unirse con código, ver miembros."""

    def __init__(self, family_model: FamilyModel, user_model: UserModel):
        self.family_model = family_model
        self.user_model = user_model

    def render_family_setup(self, user_id):
        views.inject_auth_css()

        st.markdown("""
        <div class="auth-container">
            <div class="auth-logo">
                <div class="auth-logo-icon">👨‍👩‍👧‍👦</div>
            </div>
            <div class="auth-title">Configura tu Familia</div>
            <div class="auth-subtitle">Crea una familia o únete a una existente</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            with st.container():
                st.markdown("#### Crear Familia")
                with st.form("create_family"):
                    nombre_familia = st.text_input("Nombre de tu familia", placeholder="Ej. Familia García")
                    if st.form_submit_button("Crear", use_container_width=True):
                        if nombre_familia:
                            fid = self.family_model.create(nombre_familia, user_id)
                            st.session_state.familia_id = fid
                            st.success(f"¡Familia '{nombre_familia}' creada!")
                            st.rerun()
                        else:
                            st.error("Ingresa un nombre.")

        with col2:
            with st.container():
                st.markdown("#### Unirse a Familia")
                with st.form("join_family"):
                    codigo = st.text_input("Código de invitación", placeholder="Ej. ABC123")
                    if st.form_submit_button("Unirse", use_container_width=True):
                        if codigo:
                            fid, fname = self.family_model.join(user_id, codigo)
                            if fid:
                                st.session_state.familia_id = fid
                                st.success(f"¡Te uniste a '{fname}'!")
                                st.rerun()
                            else:
                                st.error("Código no válido.")
                        else:
                            st.error("Ingresa el código.")

    def render_family_panel(self, familia_id, user_id):
        familia = self.family_model.get_familia(familia_id)
        if not familia:
            return

        st.markdown("---")
        views.render_section_header("👥", "Mi Familia", familia.get("nombre", ""))

        col_info, col_code = st.columns([2, 1])

        with col_info:
            miembros = familia.get("miembros", {})
            if miembros:
                for mid, mdata in miembros.items():
                    nombre_m = mdata.get("nombre", "Sin nombre")
                    rol_m = mdata.get("rol_en_familia", "miembro")
                    es_admin = rol_m == "admin"
                    iniciales = "".join([n[0].upper() for n in nombre_m.split()[:2]]) if nombre_m else "?"

                    badge = " 🔷 Admin" if es_admin else ""
                    st.markdown(f"**{iniciales}** {nombre_m}{badge}")
                    st.caption(f"{rol_m.title()}")
            else:
                views.render_empty_state("👤", "Sin miembros", "Aún no hay miembros en esta familia.")

        with col_code:
            codigo = familia.get("codigo_invitacion", "")
            if codigo:
                st.markdown("**Código de Invitación**")
                st.markdown(f"### `{codigo}`")
                st.caption("Comparte este código para que otros se unan")


# -------------------------------------------------------------
# CONTROLADOR: ADMINISTRACIÓN
# -------------------------------------------------------------
class AdminController:
    """Panel de administrador: crear usuarios, gestionar cuentas."""

    def __init__(self, user_model: UserModel):
        self.user_model = user_model

    def render_admin_panel(self):
        st.markdown("---")
        views.render_section_header("⚙️", "Panel de Administración", "Gestiona usuarios de la plataforma.")

        tab_crear, tab_lista, tab_info = st.tabs([
            "➕ Crear Usuario",
            "👥 Usuarios Registrados",
            "ℹ️ Cuenta Admin",
        ])

        with tab_crear:
            self._render_create_user()

        with tab_lista:
            self._render_users_list()

        with tab_info:
            self._render_admin_info()

    def _render_create_user(self):
        st.markdown("**Crear nuevo usuario para la plataforma**")
        st.caption("El usuario podrá iniciar sesión independientemente y crear o unirse a familias.")

        with st.form("create_user_admin"):
            nombre = st.text_input("Nombre completo", placeholder="Ej. María García")
            email = st.text_input("Email", placeholder="maria@email.com")
            password = st.text_input("Contraseña temporal", type="password", placeholder="Mínimo 6 caracteres")
            rol = st.selectbox("Rol", ["miembro", "admin"])

            if st.form_submit_button("Crear Usuario", use_container_width=True):
                if not nombre or not password:
                    st.error("Completa todos los campos.")
                elif len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    user_id, error = self.user_model.create_user_by_admin(nombre, email, password, rol)
                    if user_id:
                        st.success(f"✅ Usuario creado exitosamente\n\n**ID de usuario:** `{user_id}`\n\n**Email:** {email}")
                    else:
                        st.error(error)

    def _render_users_list(self):
        users = self.user_model.get_all_users()

        if not users:
            views.render_empty_state("👥", "Sin usuarios", "Aún no hay usuarios registrados.")
            return

        st.markdown(f"**{len(users)} usuarios registrados**")

        for uid, udata in users.items():
            nombre = udata.get("nombre", "Sin nombre")
            email = udata.get("email", "—")
            rol = udata.get("rol", "miembro")
            is_admin_user = rol == "admin"
            es_admin_inicial = udata.get("es_admin_inicial", False)
            iniciales = "".join([n[0].upper() for n in nombre.split()[:2]]) if nombre else "?"

            badges = ""
            if is_admin_user:
                badges += " 🔷 Admin"
            if es_admin_inicial:
                badges += " ⭐ Inicial"

            col_info, col_actions = st.columns([4, 1])

            with col_info:
                st.markdown(f"**{iniciales}** {nombre}{badges}")
                st.caption(f"📧 {email} · ID: `{uid}`")

            with col_actions:
                if not es_admin_inicial:
                    if st.button("🗑️", key=f"del_user_{uid}", help="Eliminar usuario"):
                        success, error = self.user_model.delete_user(uid)
                        if success:
                            st.success("Usuario eliminado")
                            st.rerun()
                        else:
                            st.error(error)

    def _render_admin_info(self):
        admin = get_admin_credentials(st.secrets)

        st.markdown("**Tu cuenta de administrador**")
        if admin:
            st.info(f"""
            **Nombre:** {admin['nombre']}\n\n
            **Email:** {admin['email']}\n\n
            **ID:** `{admin['user_id']}`
            """)
        else:
            st.warning("No se encontraron credenciales de admin en los secrets.")

        st.warning("⚠️ Las credenciales admin están configuradas en los secrets de la app.")

        with st.expander("🔑 Cambiar contraseña (próximamente)"):
            st.caption("Funcionalidad disponible en futuras versiones.")


# -------------------------------------------------------------
# CONTROLADOR: SIDEBAR
# -------------------------------------------------------------
class SidebarController:
    @staticmethod
    def render():
        with st.sidebar:
            st.header("👤 Identificación")
            if "nombre_usuario" not in st.session_state:
                st.session_state.nombre_usuario = ""
            st.session_state.nombre_usuario = st.text_input(
                "Tu nombre",
                value=st.session_state.nombre_usuario,
                placeholder="Ej. Ana",
            )
            if not st.session_state.nombre_usuario:
                st.info("Escribe tu nombre para guardar información.")
            st.divider()
            st.caption("App compartida por toda la familia.")
        return st.session_state.nombre_usuario or "Sin nombre"


# -------------------------------------------------------------
# CONTROLADOR: PERSONAS DE SEGUIMIENTO
# -------------------------------------------------------------
class PersonasController:
    def __init__(self, persona_model: PersonaModel):
        self.model = persona_model

    def render_form_crear(self, usuario):
        with st.popover("➕ Agregar Persona", use_container_width=True):
            with st.form("form_persona", clear_on_submit=True):
                views.render_section_header("👤", "Nueva Persona")
                nombre = st.text_input("Nombre completo", placeholder="Ej. Juan Pérez")
                dni = st.text_input("DNI (opcional)", placeholder="Ej. 12345678")
                relacion = st.selectbox("Relación", [
                    "Hijo/a", "Padre/Madre", "Abuelo/a", "Esposo/a",
                    "Hermano/a", "Otro"
                ])
                fecha_nac = st.date_input(
                    "Fecha de nacimiento (opcional)",
                    value=None,
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                )
                notas = st.text_area("Notas (opcional)", placeholder="Ej. Alergias, condiciones médicas...")

                if st.form_submit_button("Guardar", use_container_width=True):
                    if not usuario or usuario == "Sin nombre":
                        st.error("Escribe tu nombre en la barra lateral.")
                    elif nombre:
                        self.model.crear(nombre, dni, relacion, fecha_nac, notas, usuario)
                        st.success(f"¡'{nombre}' agregado!")
                        st.rerun()
                    else:
                        st.error("Ingresa un nombre.")

    def render_lista(self):
        personas = self.model.get_all()
        if not personas:
            views.render_empty_state("👤", "Sin personas", "Agrega personas para hacerles seguimiento de citas y servicios.")
            return personas

        for pid, pdata in personas.items():
            nombre_p = pdata.get("nombre", "Sin nombre")
            dni_p = pdata.get("dni", "")
            relacion_p = pdata.get("relacion", "")
            iniciales = "".join([n[0].upper() for n in nombre_p.split()[:2]]) if nombre_p else "?"

            col_info, col_del = st.columns([5, 1])
            with col_info:
                st.markdown(f"**{iniciales}** {nombre_p}")
                dni_text = f" · DNI: {dni_p}" if dni_p else ""
                st.caption(f"{relacion_p}{dni_text}")
            with col_del:
                st.write("")
                st.write("")
                if st.button("🗑️", key=f"del_persona_{pid}"):
                    self.model.eliminar(pid)
                    st.rerun()

        return personas


# -------------------------------------------------------------
# CONTROLADOR: CITAS MÉDICAS
# -------------------------------------------------------------
class CitasController:
    def __init__(self, cita_model: CitaModel):
        self.model = cita_model

    def render_form_agendar(self, usuario, persona_names):
        with st.popover("➕ Agendar Cita", use_container_width=True):
            with st.form("form_citas", clear_on_submit=True):
                views.render_section_header("📅", "Nueva Cita")
                if persona_names:
                    paciente = st.selectbox("Paciente", persona_names)
                else:
                    st.warning("Primero agrega personas en la pestaña Personas.")
                    paciente = None
                especialidad = st.text_input("Especialidad / Doctor", placeholder="Ej. Cardiología - Dr. Pérez")
                lugar = st.text_input("Hospital / Clínica", placeholder="Ej. Hospital Nacional")
                fecha = st.date_input("Fecha", value=date.today())
                hora = st.time_input("Hora")
                notas = st.text_area("Notas / Indicaciones", placeholder="Ej. Ir en ayunas de 8 horas")

                if st.form_submit_button("Guardar Cita", use_container_width=True):
                    if not usuario or usuario == "Sin nombre":
                        st.error("Escribe tu nombre en la barra lateral.")
                    elif not paciente:
                        st.error("Agrega al menos una persona primero.")
                    elif especialidad and lugar:
                        self.model.crear(paciente, especialidad, lugar, fecha, hora, notas, usuario)
                        st.success("¡Cita registrada!")
                        st.rerun()
                    else:
                        st.error("Completa especialidad y lugar.")

    def render_form_marcar_realizada(self, key, usuario):
        with st.popover("✅ Marcar Realizada", use_container_width=True):
            with st.form(f"form_realizada_{key}"):
                views.render_section_header("📋", "Registrar Historial")
                diagnostico = st.text_area("Diagnóstico / Resultado", key=f"diag_{key}")
                tratamiento = st.text_area("Tratamiento / Medicamentos", key=f"trat_{key}")
                recomendaciones = st.text_area("Recomendaciones", key=f"reco_{key}")
                proxima_sugerida = st.date_input("Próxima cita sugerida", key=f"prox_{key}", value=None)

                if st.form_submit_button("Guardar en Historial", use_container_width=True):
                    self.model.marcar_realizada(key, diagnostico, tratamiento, recomendaciones, proxima_sugerida, usuario)
                    st.success("Movida al historial clínico")
                    st.rerun()

    @staticmethod
    def render_filtro_paciente(persona_names, key="filtro_prog"):
        opciones = ["Todos"] + persona_names
        return st.radio("Filtrar por paciente", opciones, horizontal=True, key=key)

    def render_lista_programadas(self, usuario, filtro):
        programadas = self.model.get_programadas()
        vista = CitaModel.filtrar_por_paciente(programadas, filtro)

        if not vista:
            views.render_empty_state("📅", "Sin citas programadas", "Agenda la primera cita médical usando el botón de arriba.")
            return

        for key, cita in CitaModel.ordenar_por_fecha(vista):
            views.render_appt_card(cita)

            if cita.get("notas"):
                st.caption(f"📝 {cita.get('notas')} · Registrado por {cita.get('registrado_por', '—')}")

            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                pass
            with col_b:
                self.render_form_marcar_realizada(key, usuario)
            with col_c:
                if st.button("🗑️", key=f"del_cita_{key}", use_container_width=True):
                    self.model.eliminar(key)
                    st.rerun()

    def render_historial(self, persona_names):
        views.render_section_header("📖", "Historial Clínico", "Registro de cada cita ya realizada.")
        filtro = self.render_filtro_paciente(persona_names, key="filtro_hist")
        realizadas = self.model.get_realizadas()
        vista = CitaModel.filtrar_por_paciente(realizadas, filtro)

        if not vista:
            views.render_empty_state("📖", "Historial vacío", "Las citas realizadas aparecerán aquí.")
            return

        for key, cita in CitaModel.ordenar_por_fecha(vista, descendente=True):
            titulo = f"🗂️ {cita.get('fecha')} — {cita.get('paciente')}: {cita.get('especialidad')}"
            with st.expander(titulo):
                st.markdown(views.badge_paciente(cita.get('paciente')), unsafe_allow_html=True)
                st.markdown(f"**🏥 Lugar:** {cita.get('lugar')}")

                if cita.get("diagnostico"):
                    st.markdown(f"**🩺 Diagnóstico:** {cita.get('diagnostico')}")
                if cita.get("tratamiento"):
                    st.markdown(f"**💊 Tratamiento:** {cita.get('tratamiento')}")
                if cita.get("recomendaciones"):
                    st.markdown(f"**📋 Recomendaciones:** {cita.get('recomendaciones')}")
                if cita.get("proxima_cita_sugerida"):
                    st.markdown(f"**⏭️ Próxima sugerida:** {cita.get('proxima_cita_sugerida')}")

                st.caption(f"Registrada por {cita.get('registrado_por', '—')} · Historial por {cita.get('actualizado_por', '—')}")

                if st.button("🗑️ Eliminar", key=f"del_hist_{key}"):
                    self.model.eliminar(key)
                    st.rerun()


# -------------------------------------------------------------
# CONTROLADOR: SERVICIOS PÚBLICOS
# -------------------------------------------------------------
class ServiciosController:
    def __init__(self, servicio_model: ServicioModel):
        self.model = servicio_model

    def render_form_registrar(self, usuario):
        with st.popover("➕ Registrar Código", use_container_width=True):
            with st.form("form_servicios", clear_on_submit=True):
                views.render_section_header("💡", "Nuevo Servicio")
                tipo = st.selectbox("Tipo de servicio", ["⚡ Luz", "💧 Agua", "🔥 Gas", "🌐 Internet", "📞 Teléfono", "Otro"])
                empresa = st.text_input("Empresa proveedora", placeholder="Ej. Enel, Sedapal")
                codigo = st.text_input("Código de pago / Suministro", placeholder="Ej. 12345678")
                titular = st.text_input("Titular del recibo", placeholder="Ej. Nombre del titular")

                if st.form_submit_button("Guardar Código", use_container_width=True):
                    if not usuario or usuario == "Sin nombre":
                        st.error("Escribe tu nombre en la barra lateral.")
                    elif empresa and codigo:
                        self.model.crear(tipo, empresa, codigo, titular, usuario)
                        st.success("¡Servicio registrado!")
                        st.rerun()
                    else:
                        st.error("Ingresa empresa y código.")

    @staticmethod
    def render_filtro_tipo():
        return st.radio(
            "Filtrar por tipo",
            ["Todos", "⚡ Luz", "💧 Agua", "🔥 Gas", "🌐 Internet", "📞 Teléfono", "Otro"],
            horizontal=True,
        )

    def render_lista(self, filtro):
        servicios = self.model.get_all()
        vista = ServicioModel.filtrar_por_tipo(servicios, filtro)

        if not vista:
            views.render_empty_state("💡", "Sin servicios registrados", "Registra el primer código de pago usando el botón de arriba.")
            return

        for key, servicio in vista.items():
            col_info, col_actions = st.columns([5, 1])
            with col_info:
                views.render_service_info(servicio)
            with col_actions:
                st.write("")
                st.write("")
                if st.button("🗑️", key=f"del_serv_{key}"):
                    self.model.eliminar(key)
                    st.rerun()
