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
    CitaModel, ServicioModel, PersonaModel, MedicinaModel,
    get_admin_credentials, _hash_password, _verify_password, _sanitize,
    hoy_local,
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
        for key in [
            "user_id", "nombre_usuario", "familia_activa", "familia_id",
            "login_time", "vista", "_proxima_cita_popup_mostrado",
            "alertas_enviadas",
        ]:
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

            if st.button("🏠 Inicio", use_container_width=True, key="sidebar_home"):
                st.session_state.vista = "home"
                st.rerun()

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

        views.render_section_header(
            "👥", "Mi Familia", familia.get("nombre", ""), tone="blue",
        )

        miembros = familia.get("miembros", {})
        views.render_stat_strip([
            {"value": len(miembros), "label": "miembro(s)", "icon": "👥", "tone": "indigo"},
        ])

        col_info, col_code = st.columns([2, 1])

        with col_info:
            if miembros:
                for mid, mdata in miembros.items():
                    nombre_m = mdata.get("nombre", "Sin nombre")
                    rol_m = mdata.get("rol_en_familia", "miembro")
                    es_admin = rol_m == "admin"
                    iniciales = "".join([n[0].upper() for n in nombre_m.split()[:2]]) if nombre_m else "?"
                    views.render_entity_card(
                        iniciales, nombre_m, rol_m.title(),
                        tag="Admin" if es_admin else "",
                    )
            else:
                views.render_empty_state("👤", "Sin miembros", "Aún no hay miembros en esta familia.")

        with col_code:
            codigo = familia.get("codigo_invitacion", "")
            if codigo:
                views.render_invite_card(codigo)


# -------------------------------------------------------------
# CONTROLADOR: ADMINISTRACIÓN
# -------------------------------------------------------------
class AdminController:
    """Panel de administrador: crear usuarios, gestionar cuentas."""

    def __init__(self, user_model: UserModel):
        self.user_model = user_model

    def render_admin_panel(self):
        views.render_section_header(
            "⚙️", "Panel de Administración",
            "Gestiona usuarios de la plataforma.", tone="blue",
        )

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

        views.render_stat_strip([
            {"value": len(users), "label": "usuario(s) registrado(s)",
             "icon": "👥", "tone": "indigo"},
        ])

        for uid, udata in users.items():
            nombre = udata.get("nombre", "Sin nombre")
            email = udata.get("email", "—")
            rol = udata.get("rol", "miembro")
            is_admin_user = rol == "admin"
            es_admin_inicial = udata.get("es_admin_inicial", False)
            iniciales = "".join([n[0].upper() for n in nombre.split()[:2]]) if nombre else "?"

            etiquetas = []
            if is_admin_user:
                etiquetas.append("Admin")
            if es_admin_inicial:
                etiquetas.append("Inicial")

            col_info, col_actions = st.columns([6, 1], vertical_alignment="center")

            with col_info:
                views.render_entity_card(
                    iniciales, nombre, f"📧 {email} · ID: {uid}",
                    tag=" · ".join(etiquetas),
                )

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
                views.render_section_header("👤", "Nueva Persona", tone="violet", compact=True)
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
                    max_value=hoy_local(),
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

        views.render_stat_strip([
            {"value": len(personas), "label": "persona(s) en seguimiento",
             "icon": "👤", "tone": "violet"},
        ])

        for pid, pdata in personas.items():
            nombre_p = pdata.get("nombre", "Sin nombre")
            dni_p = pdata.get("dni", "")
            relacion_p = pdata.get("relacion", "")
            iniciales = "".join([n[0].upper() for n in nombre_p.split()[:2]]) if nombre_p else "?"

            col_info, col_del = st.columns([6, 1], vertical_alignment="center")
            with col_info:
                dni_text = f" · DNI: {dni_p}" if dni_p else ""
                views.render_entity_card(
                    iniciales, nombre_p, f"{relacion_p}{dni_text}".strip(" ·"),
                )
            with col_del:
                if st.button("🗑️", key=f"del_persona_{pid}", help="Eliminar persona"):
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
                views.render_section_header("📅", "Nueva Cita", tone="teal", compact=True)
                if persona_names:
                    paciente = st.selectbox("Paciente", persona_names)
                else:
                    st.warning("Primero agrega personas en la pestaña Personas.")
                    paciente = None
                especialidad = st.text_input("Especialidad / Doctor", placeholder="Ej. Cardiología - Dr. Pérez")
                lugar = st.text_input("Hospital / Clínica", placeholder="Ej. Hospital Nacional")
                fecha = st.date_input("Fecha", value=hoy_local())
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

    def render_form_registrar_emergencia(self, usuario, persona_names):
        with st.popover("🚨 Registrar Emergencia", use_container_width=True):
            with st.form("form_emergencia", clear_on_submit=True):
                views.render_section_header("🚨", "Emergencia", tone="red", compact=True)
                st.caption("Registra un evento de emergencia que se sumará al historial clínico de la persona.")
                if persona_names:
                    paciente = st.selectbox("Paciente", persona_names)
                else:
                    st.warning("Primero agrega personas en la pestaña Personas.")
                    paciente = None
                motivo = st.text_input("Motivo / Tipo de emergencia", placeholder="Ej. Dolor abdominal intenso, caída, fiebre alta...")
                atencion_recibida = st.text_area("Atención recibida", placeholder="Ej. Rehidratación, sutura, medicación de urgencia...")
                lugar = st.text_input("Lugar de atención", placeholder="Ej. Emergencia del Hospital Nacional")
                fecha = st.date_input(
                    "Fecha del evento",
                    value=hoy_local(),
                    min_value=date(2020, 1, 1),
                    max_value=hoy_local(),
                )
                hora = st.time_input("Hora")
                notas = st.text_area("Notas / Seguimiento (opcional)", placeholder="Ej. Derivado a control con especialista...")

                if st.form_submit_button("Guardar Emergencia", use_container_width=True):
                    if not usuario or usuario == "Sin nombre":
                        st.error("Escribe tu nombre en la barra lateral.")
                    elif not paciente:
                        st.error("Agrega al menos una persona primero.")
                    elif not motivo:
                        st.error("Describe el motivo de la emergencia.")
                    else:
                        self.model.registrar_emergencia(paciente, motivo, atencion_recibida, lugar, fecha, hora, notas, usuario)
                        st.success(f"¡Emergencia de '{paciente}' registrada en el historial!")
                        st.rerun()

    def render_form_marcar_realizada(self, key, usuario):
        with st.popover("✅ Marcar Realizada", use_container_width=True):
            with st.form(f"form_realizada_{key}"):
                views.render_section_header("📋", "Registrar Historial", tone="indigo", compact=True)
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

    def render_lista_programadas(self, usuario, persona_names):
        views.render_section_header(
            "📅", "Registro de Citas Médicas",
            "Citas pendientes y realizadas, diferenciadas por color.",
            tone="teal",
        )
        filtro = self.render_filtro_paciente(persona_names, key="filtro_prog")
        todas = self.model.get_no_emergencias()
        vista = CitaModel.filtrar_por_paciente(todas, filtro)

        if not vista:
            views.render_empty_state("📅", "Sin citas registradas", "Agenda la primera cita usando el botón de arriba.")
            return

        pendientes = {k: v for k, v in vista.items() if v.get("estado", "programada") == "programada"}
        realizadas = {k: v for k, v in vista.items() if v.get("estado") == "realizada"}
        views.render_stat_strip([
            {"value": len(vista), "label": "cita(s)", "icon": "📅", "tone": "teal"},
            {"value": len(pendientes), "label": "pendiente(s)", "icon": "⏳", "tone": "amber"},
            {"value": len(realizadas), "label": "realizada(s)", "icon": "✅", "tone": "green"},
        ])

        # Pendientes primero (por fecha ascendente), luego realizadas (más reciente primero)
        ordenadas = (
            CitaModel.ordenar_por_fecha(pendientes)
            + CitaModel.ordenar_por_fecha(realizadas, descendente=True)
        )

        for key, cita in ordenadas:
            es_realizada = cita.get("estado") == "realizada"
            emoji = views.cita_estado_emoji(cita)
            titulo = f"{emoji} {cita.get('fecha')} — {cita.get('paciente')}: {cita.get('especialidad')}"
            with st.expander(titulo):
                st.markdown(views.cita_estado_banner(cita), unsafe_allow_html=True)
                badges = views.badge_paciente(cita.get('paciente'))
                if not es_realizada:
                    badges += views.badge_estado_cita(cita.get('fecha'))
                st.markdown(badges, unsafe_allow_html=True)
                views.render_info_rows([
                    ("🏥", "Lugar", cita.get("lugar")),
                    ("🕐", "Hora", cita.get("hora")),
                    ("📝", "Notas", cita.get("notas")),
                    ("🩺", "Diagnóstico", cita.get("diagnostico")),
                    ("💊", "Tratamiento", cita.get("tratamiento")),
                    ("📋", "Recomendaciones", cita.get("recomendaciones")),
                ])

                if es_realizada:
                    st.caption(f"Realizada · Registrada por {cita.get('registrado_por', '—')}")
                    if st.button("🗑️ Eliminar", key=f"del_cita_{key}"):
                        self.model.eliminar(key)
                        st.rerun()
                else:
                    st.caption(f"Registrada por {cita.get('registrado_por', '—')}")
                    col_cal, col_b, col_c = st.columns([1.15, 1.55, 0.8])
                    with col_cal:
                        views.render_boton_calendario(cita, f"cita_{key}")
                    with col_b:
                        self.render_form_marcar_realizada(key, usuario)
                    with col_c:
                        if st.button("🗑️", key=f"del_cita_{key}", use_container_width=True):
                            self.model.eliminar(key)
                            st.rerun()

    def render_historial(self, persona_names):
        views.render_section_header(
            "📖", "Historial Clínico",
            "Registro completo de citas y emergencias de cada persona.",
            tone="indigo",
        )
        filtro = self.render_filtro_paciente(persona_names, key="filtro_hist")
        todas = self.model.get_all()
        vista = CitaModel.filtrar_por_paciente(todas, filtro)

        if not vista:
            views.render_empty_state("📖", "Sin registros", "Las citas registradas y emergencias aparecerán aquí.")
            return

        cont_realizadas = sum(1 for c in vista.values() if c.get("estado") == "realizada")
        cont_programadas = sum(1 for c in vista.values() if c.get("estado", "programada") == "programada")
        cont_emergencias = sum(1 for c in vista.values() if c.get("es_emergencia"))
        views.render_stat_strip([
            {"value": len(vista), "label": "registro(s)", "icon": "📖", "tone": "indigo"},
            {"value": cont_emergencias, "label": "emergencia(s)", "icon": "🚨", "tone": "red"},
            {"value": cont_programadas, "label": "pendiente(s)", "icon": "⏳", "tone": "amber"},
            {"value": cont_realizadas, "label": "realizada(s)", "icon": "✅", "tone": "green"},
        ])

        for key, cita in CitaModel.ordenar_por_fecha(vista, descendente=True):
            es_emergencia = cita.get("es_emergencia", False)
            es_realizada = cita.get("estado") == "realizada"
            emoji = views.cita_estado_emoji(cita)
            if es_emergencia:
                titulo = f"{emoji} {cita.get('fecha')} — {cita.get('paciente')}: {cita.get('motivo_emergencia', 'Emergencia')}"
                estado_badge = views.badge_emergencia(cita.get('paciente'))
            else:
                titulo = f"{emoji} {cita.get('fecha')} — {cita.get('paciente')}: {cita.get('especialidad')}"
                if es_realizada:
                    estado_badge = views.badge_cita_realizada(cita.get('paciente'))
                else:
                    estado_badge = views.badge_cita_pendiente(cita.get('paciente'))
            with st.expander(titulo):
                st.markdown(views.cita_estado_banner(cita), unsafe_allow_html=True)
                st.markdown(estado_badge, unsafe_allow_html=True)
                views.render_info_rows([
                    ("🏥", "Lugar", cita.get("lugar")),
                    ("🚨", "Motivo de emergencia", cita.get("motivo_emergencia")),
                    ("🩹", "Atención recibida", cita.get("atencion_recibida")),
                    ("🕐", "Hora", cita.get("hora")),
                    ("📝", "Notas", cita.get("notas")),
                    ("🩺", "Diagnóstico", cita.get("diagnostico")),
                    ("💊", "Tratamiento", cita.get("tratamiento")),
                    ("📋", "Recomendaciones", cita.get("recomendaciones")),
                    ("⏭️", "Próxima sugerida", cita.get("proxima_cita_sugerida")),
                ])

                if not es_emergencia and not es_realizada:
                    st.markdown("")
                    with st.popover("✅ Marcar como realizada"):
                        with st.form(f"hist_realizada_{key}"):
                            views.render_section_header("📋", "Registrar Resultado", tone="indigo", compact=True)
                            diagnostico = st.text_area("Diagnóstico / Resultado", key=f"hist_diag_{key}")
                            tratamiento = st.text_area("Tratamiento / Medicamentos", key=f"hist_trat_{key}")
                            recomendaciones = st.text_area("Recomendaciones", key=f"hist_reco_{key}")
                            proxima_sugerida = st.date_input("Próxima cita sugerida", key=f"hist_prox_{key}", value=None)
                            if st.form_submit_button("Guardar en Historial", use_container_width=True):
                                self.model.marcar_realizada(
                                    key,
                                    diagnostico,
                                    tratamiento,
                                    recomendaciones,
                                    proxima_sugerida,
                                    cita.get('registrado_por', '—'),
                                )
                                st.success("Cita marcada como realizada y detalle guardado.")
                                st.rerun()

                st.caption(f"Registrada por {cita.get('registrado_por', '—')} · Historial por {cita.get('actualizado_por', '—')}")

                if st.button("🗑️ Eliminar", key=f"del_hist_{key}"):
                    self.model.eliminar(key)
                    st.rerun()

    def render_lista_emergencias(self, persona_names):
        views.render_section_header(
            "🚨", "Emergencias",
            "Eventos de urgencia registrados y su atención.",
            tone="red",
        )
        filtro = self.render_filtro_paciente(persona_names, key="filtro_emerg")
        emergencias = self.model.get_emergencias()
        vista = CitaModel.filtrar_por_paciente(emergencias, filtro)

        if not vista:
            views.render_empty_state("🚨", "Sin emergencias", "Los eventos de urgencia registrados aparecerán aquí.")
            return

        total = len(vista)
        views.render_stat_strip([
            {"value": total, "label": "emergencia(s) registrada(s)", "icon": "🚨", "tone": "red"},
        ])

        for key, em in CitaModel.ordenar_por_fecha(vista, descendente=True):
            titulo = f"🚨 {em.get('fecha')} — {em.get('paciente')}: {em.get('motivo_emergencia', 'Emergencia')}"
            with st.expander(titulo):
                st.markdown(views.badge_emergencia(em.get('paciente')), unsafe_allow_html=True)
                views.render_info_rows([
                    ("🏥", "Lugar", em.get("lugar")),
                    ("🚨", "Motivo", em.get("motivo_emergencia")),
                    ("🩹", "Atención recibida", em.get("atencion_recibida")),
                    ("🕐", "Hora", em.get("hora")),
                    ("📝", "Notas", em.get("notas")),
                ])

                st.caption(f"Registrada por {em.get('registrado_por', '—')}")

                if st.button("🗑️ Eliminar", key=f"del_emerg_{key}"):
                    self.model.eliminar(key)
                    st.rerun()


# -------------------------------------------------------------
# CONTROLADOR: MEDICINAS
# -------------------------------------------------------------
class MedicinasController:
    def __init__(self, medicina_model):
        self.model = medicina_model

    def render_form_registrar(self, usuario, persona_names):
        with st.popover("➕ Registrar Recogida de Medicinas", use_container_width=True):
            with st.form("form_medicinas", clear_on_submit=True):
                views.render_section_header("💊", "Recogida de Medicinas", tone="green", compact=True)
                if persona_names:
                    paciente = st.selectbox("A quién pertenece", persona_names)
                else:
                    st.warning("Primero agrega personas en la pestaña Personas.")
                    paciente = None
                medicamento = st.text_input("Medicamento", placeholder="Ej. Amoxicilina")
                presentacion = st.text_input("Presentación", placeholder="Ej. Cápsulas 500mg, Jarabe 100ml")
                es_continuo = st.checkbox(
                    "🔁 Tratamiento continuo (de por vida, sin fecha de fin)",
                    help="Marca esta opción para tratamientos permanentes (ej. presión, diabetes).",
                )
                col1, col2 = st.columns(2)
                with col1:
                    cantidad = st.text_input("Cantidad por toma", placeholder="Ej. 1 tableta, 10 ml")
                with col2:
                    frecuencia = st.text_input("Frecuencia", placeholder="Ej. Cada 8 horas")
                fecha_recojo = st.date_input("Fecha de inicio / recogida", value=hoy_local())
                dias = st.number_input(
                    "Días que dura (solo tratamiento temporal)",
                    min_value=1, max_value=3650, value=30, step=1,
                )
                indicacion = st.text_area("Indicación", placeholder="Ej. Tomar después de las comidas")
                notas = st.text_area("Notas (opcional)", placeholder="Ej. Requiere receta, guardar refrigerado...")

                if st.form_submit_button("Guardar", use_container_width=True):
                    if not usuario or usuario == "Sin nombre":
                        st.error("Escribe tu nombre en la barra lateral.")
                    elif not paciente:
                        st.error("Agrega al menos una persona primero.")
                    elif not medicamento:
                        st.error("Ingresa el nombre del medicamento.")
                    else:
                        tipo = "continuo" if es_continuo else "temporal"
                        dias_final = 0 if es_continuo else int(dias)
                        self.model.crear(
                            paciente, medicamento, presentacion, cantidad, frecuencia, tipo,
                            fecha_recojo, dias_final, indicacion, notas, usuario,
                        )
                        st.success("Recogida de medicinas registrada")
                        st.rerun()

    def render_lista(self, persona_names):
        views.render_section_header(
            "💊", "Control de Medicinas",
            "Control de recogidas, a quién pertenecen y duración del tratamiento.",
            tone="green",
        )
        filtro = CitasController.render_filtro_paciente(persona_names, key="filtro_med")
        medicinas = self.model.get_all()
        vista = MedicinaModel.filtrar_por_paciente(medicinas, filtro)

        if not vista:
            views.render_empty_state("💊", "Sin medicinas registradas", "Registra la primera recogida usando el botón de arriba.")
            return

        total = len(vista)
        activas = sum(1 for med in vista.values() if self._med_activa(med))
        views.render_stat_strip([
            {"value": total, "label": "registro(s)", "icon": "💊", "tone": "teal"},
            {"value": activas, "label": "activo(s)", "icon": "✅", "tone": "green"},
            {"value": total - activas, "label": "agotado(s)", "icon": "⏳", "tone": "amber"},
        ])

        for key, med in MedicinaModel.ordenar_por_fecha(vista):
            tipo = med.get("tipo", "temporal")
            tipo_txt = "🔁 Continuo" if tipo == "continuo" else "📆 Temporal"
            titulo = f"💊 {med.get('medicamento')} — {med.get('paciente')} · {tipo_txt}"
            with st.expander(titulo):
                st.markdown(
                    views.badge_medicina_estado(
                        med.get('fecha_recojo'), med.get('dias'), med.get('paciente'), tipo
                    ),
                    unsafe_allow_html=True,
                )
                dias_rest = (None if tipo == "continuo"
                             else MedicinaModel.dias_restantes(
                                 med.get('fecha_recojo'), med.get('dias'), tipo))
                tipo_detalle = ("🔁 Continuo (sin fecha de fin)" if tipo == "continuo"
                                else f"📆 Temporal · {med.get('dias')} día(s)")
                dias_txt = None
                if dias_rest is not None:
                    dias_txt = (f"{dias_rest} día(s)" if dias_rest >= 0
                                else f"Agotada hace {abs(dias_rest)} día(s)")
                views.render_info_rows([
                    ("📦", "Presentación", med.get("presentacion")),
                    ("⚖️", "Cantidad por toma", med.get("cantidad")),
                    ("🕐", "Frecuencia", med.get("frecuencia")),
                    ("📅", "Inicio / recogida", med.get("fecha_recojo")),
                    ("📆", "Tipo", tipo_detalle),
                    ("⏳", "Días restantes", dias_txt),
                    ("💡", "Indicación", med.get("indicacion")),
                    ("📝", "Notas", med.get("notas")),
                ])
                st.caption(f"Registrado por {med.get('registrado_por', '—')}")

                if st.button("🗑️ Eliminar", key=f"del_med_{key}"):
                    self.model.eliminar(key)
                    st.rerun()

    @staticmethod
    def _med_activa(med):
        if med.get("tipo") == "continuo":
            return True
        dr = MedicinaModel.dias_restantes(med.get("fecha_recojo"), med.get("dias"), med.get("tipo", "temporal"))
        return dr is None or dr >= 0

    def render_resumen_historial(self, persona_names):
        """Resumen de medicinas por persona para integrarlo en el historial clínico."""
        views.render_section_header(
            "💊", "Medicinas por Persona",
            "Tratamientos continuos y temporales que cada persona debe tomar.",
            tone="green",
        )
        medicinas = self.model.get_all()
        if not medicinas:
            views.render_empty_state(
                "💊", "Sin medicinas",
                "Registra una recogida en la sección Medicinas para verla aquí.",
            )
            return

        por_persona = {}
        for key, med in medicinas.items():
            por_persona.setdefault(med.get("paciente", "—"), []).append((key, med))

        def _orden(pair):
            med = pair[1]
            if med.get("tipo") == "continuo":
                return (0, 0)
            dr = MedicinaModel.dias_restantes(med.get("fecha_recojo"), med.get("dias"), med.get("tipo", "temporal"))
            return (1, dr if dr is not None else 99999)

        for persona in persona_names:
            items = por_persona.get(persona)
            if not items:
                continue
            items = sorted(items, key=_orden)
            activos = sum(1 for _, m in items if self._med_activa(m))
            with st.expander(f"💊 {persona} — {len(items)} medicamento(s) · {activos} activo(s)"):
                for idx, (key, med) in enumerate(items):
                    tipo = med.get("tipo", "temporal")
                    views.render_mini_header(
                        f"💊 {med.get('medicamento', '—')}",
                        med.get("presentacion", ""),
                    )
                    st.markdown(
                        views.badge_medicina_estado(
                            med.get('fecha_recojo'), med.get('dias'), med.get('paciente'), tipo
                        ),
                        unsafe_allow_html=True,
                    )
                    if tipo == "continuo":
                        tipo_detalle = "🔁 Continuo · sin fecha de fin"
                        dias_txt = None
                    else:
                        dr = MedicinaModel.dias_restantes(med.get('fecha_recojo'), med.get('dias'), tipo)
                        tipo_detalle = f"📆 Temporal · {med.get('dias')} día(s)"
                        dias_txt = None
                        if dr is not None:
                            dias_txt = (f"{dr} día(s)" if dr >= 0
                                        else f"Agotada hace {abs(dr)} día(s)")
                    views.render_info_rows([
                        ("⚖️", "Cantidad", med.get("cantidad")),
                        ("🕐", "Frecuencia", med.get("frecuencia")),
                        ("📅", "Desde", med.get("fecha_recojo")),
                        ("📆", "Tipo", tipo_detalle),
                        ("⏳", "Días restantes", dias_txt),
                        ("💡", "Indicación", med.get("indicacion")),
                    ])
                    if idx < len(items) - 1:
                        st.divider()


# -------------------------------------------------------------
# CONTROLADOR: SERVICIOS PÚBLICOS
# -------------------------------------------------------------
class ServiciosController:
    def __init__(self, servicio_model: ServicioModel):
        self.model = servicio_model

    def render_form_registrar(self, usuario):
        with st.popover("➕ Registrar Código", use_container_width=True):
            with st.form("form_servicios", clear_on_submit=True):
                views.render_section_header("💡", "Nuevo Servicio", tone="amber", compact=True)
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

        views.render_stat_strip([
            {"value": len(vista), "label": "código(s) de pago",
             "icon": "💡", "tone": "amber"},
        ])

        for key, servicio in vista.items():
            col_info, col_actions = st.columns([6, 1], vertical_alignment="center")
            with col_info:
                views.render_service_info(servicio)
            with col_actions:
                if st.button("🗑️", key=f"del_serv_{key}", help="Eliminar servicio"):
                    self.model.eliminar(key)
                    st.rerun()
