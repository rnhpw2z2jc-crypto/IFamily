"""
app.py — Punto de entrada de iFamily.
Autenticación → Familias → Dashboard principal.
"""

import streamlit as st

import views
from models import (
    FirebaseService, UserModel, FamilyModel,
    CitaModel, ServicioModel, PersonaModel, MedicinaModel, _sanitize,
)
from controllers import (
    AuthController, FamilyController, AdminController,
    CitasController, ServiciosController, PersonasController, MedicinasController,
)

# -------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------------------
st.set_page_config(
    page_title="iFamily - Control Familiar",
    page_icon="app/static/icon-192.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# PWA
# -------------------------------------------------------------
st.markdown("""
<link rel="manifest" href="app/static/manifest.json">
<meta name="theme-color" content="#00BCD4">
<div id="ifamily-version" data-version="2.7-calendar-ics" style="display:none;"></div>
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="app/static/icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="iFamily">
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('app/static/service-worker.js').catch(function(err) {
        console.log('SW:', err);
    });
}
</script>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# ESTILOS GLOBALES
# -------------------------------------------------------------
views.inject_css()

# -------------------------------------------------------------
# MODEL: conexión a Firebase
# -------------------------------------------------------------
firebase = FirebaseService(st.secrets)
if not firebase.ok:
    st.error(f"Error de conexión: {firebase.error}")
    st.stop()

user_model = UserModel(firebase)
family_model = FamilyModel(firebase)

# -------------------------------------------------------------
# AUTH: verificar sesión
# -------------------------------------------------------------
auth = AuthController(user_model, family_model)

if not auth.check_session():
    auth.render_login()
    st.stop()

user_id = st.session_state.user_id

# -------------------------------------------------------------
# VERIFICAR ROL DEL USUARIO
# -------------------------------------------------------------
user_data = user_model.get_by_id(user_id)
is_admin = user_model.is_admin(user_id)

# -------------------------------------------------------------
# ADMIN: panel completo sin necesidad de familia
# -------------------------------------------------------------
if is_admin:
    admin_ctrl = AdminController(user_model)

    with st.sidebar:
        views.render_user_info(
            user_data.get("nombre", "Admin"),
            "Panel Admin",
            "administrador"
        )
        st.divider()

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            auth.logout()

    st.markdown(f"""
    <div style="margin-bottom:8px;">
        <h1 style="margin:0; font-size:1.6rem;">⚙️ Panel de Administración</h1>
        <p style="color:var(--text-muted); margin:4px 0 0 0; font-size:0.9rem;">
            Bienvenido, <strong>{_sanitize(user_data.get('nombre', 'Admin'))}</strong> — Gestiona usuarios de iFamily
        </p>
    </div>
    """, unsafe_allow_html=True)

    admin_ctrl.render_admin_panel()
    st.stop()

# -------------------------------------------------------------
# USUARIO NORMAL: flujo de familia
# -------------------------------------------------------------
familia_id = user_model.get_familia_activa(user_id)

if not familia_id:
    family_ctrl = FamilyController(family_model, user_model)
    family_ctrl.render_family_setup(user_id)
    st.stop()

# IDOR protection: verify user belongs to the active family
if not family_model.is_miembro(familia_id, user_id):
    st.error("No tienes acceso a esta familia.")
    st.stop()

# -------------------------------------------------------------
# SIDEBAR: sesión y selector de familia
# -------------------------------------------------------------
familia_id = auth.render_sidebar_session(user_model, family_model)

if not familia_id:
    family_ctrl = FamilyController(family_model, user_model)
    family_ctrl.render_family_setup(user_id)
    st.stop()

# IDOR protection: verify user belongs to the active family
if not family_model.is_miembro(familia_id, user_id):
    st.error("No tienes acceso a esta familia.")
    st.stop()

# -------------------------------------------------------------
# MODELS: instanciar con familia activa
# -------------------------------------------------------------
cita_model = CitaModel(firebase, familia_id)
servicio_model = ServicioModel(firebase, familia_id)
persona_model = PersonaModel(firebase, familia_id)
medicina_model = MedicinaModel(firebase, familia_id)

# -------------------------------------------------------------
# HEADER PRINCIPAL
# -------------------------------------------------------------
nombre_usuario = user_data.get("nombre", "Sin nombre")
familia_data = family_model.get_familia(familia_id)
nombre_familia = familia_data.get("nombre", "Mi Familia")

# -------------------------------------------------------------
# CONTROLLERS
# -------------------------------------------------------------
citas_controller = CitasController(cita_model)
servicios_controller = ServiciosController(servicio_model)
family_controller = FamilyController(family_model, user_model)
personas_controller = PersonasController(persona_model)
medicinas_controller = MedicinasController(medicina_model)

# -------------------------------------------------------------
# NAVEGACIÓN POR PANTALLAS (sin recargar la app)
# -------------------------------------------------------------
VISTAS_VALIDAS = {
    "home", "citas", "emergencias", "historial",
    "medicinas", "servicios", "personas", "familia",
}
if st.session_state.get("vista") not in VISTAS_VALIDAS:
    st.session_state.vista = "home"
vista = st.session_state.vista


def ir_a(destino):
    """Cambia de pantalla conservando la sesión de login."""
    st.session_state.vista = destino
    st.rerun()


def render_header():
    st.markdown(f"""
    <div style="margin-bottom:8px;">
        <h1 style="margin:0; font-size:1.6rem;">🏠 {_sanitize(nombre_familia)}</h1>
        <p style="color:var(--text-muted); margin:4px 0 0 0; font-size:0.9rem;">
            Bienvenido, <strong>{_sanitize(nombre_usuario)}</strong> — Control familiar inteligente
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_home():
    render_header()

    # Se leen los datos una sola vez y se reutilizan (menos consultas a Firebase).
    citas_all = cita_model.get_all()
    medicinas_all = medicina_model.get_all()
    servicios_all = servicio_model.get_all()
    personas_all = persona_model.get_all()

    programadas = cita_model.get_programadas(data=citas_all)
    emergencias = cita_model.get_emergencias(data=citas_all)
    medicinas_activas = medicina_model.get_activas(data=medicinas_all)
    medicinas_por_agotar = medicina_model.get_proximas_a_agotar(3, data=medicinas_all)

    proxima_cita = None
    if programadas:
        _, proxima_cita = sorted(
            programadas.items(),
            key=lambda i: (i[1].get("fecha", ""), i[1].get("hora", "")),
        )[0]

    alertas = views.obtener_alertas(
        cita_model, persona_model, medicina_model,
        citas=citas_all, medicinas_proximas=medicinas_por_agotar,
    )

    # Pop-up al abrir la app con la cita más próxima
    views.render_proxima_cita_popup(proxima_cita)

    # Notificación del sistema (PWA) — prioriza la cita más próxima
    if "alertas_enviadas" not in st.session_state:
        st.session_state.alertas_enviadas = ""
    views.inject_notificacion_script(alertas, proxima_cita)

    # Resumen (KPIs) arriba
    views.render_kpis(
        total_citas_programadas=len(programadas),
        proxima_cita=proxima_cita,
        total_servicios=len(servicios_all),
        total_emergencias=len(emergencias),
        medicinas_por_agotar=len(medicinas_por_agotar),
    )

    # Panel de alertas debajo del resumen
    if alertas:
        views.render_alerta_panel(alertas)
    else:
        st.success("✅ Todo en orden: no hay alertas pendientes.")

    st.markdown(
        '<div class="home-grid-title">🧭 Accesos rápidos</div>'
        '<div class="home-grid-sub">Toca una tarjeta para abrir su pantalla.</div>',
        unsafe_allow_html=True,
    )

    secciones = [
        {"key": "citas", "icono": "📅", "titulo": "Citas Médicas",
         "desc": "Agenda, pendientes y realizadas",
         "badge": f"{len(programadas)} pendiente(s)" if programadas else "Sin pendientes"},
        {"key": "emergencias", "icono": "🚨", "titulo": "Emergencias",
         "desc": "Registra y consulta emergencias",
         "badge": f"{len(emergencias)} registrada(s)"},
        {"key": "historial", "icono": "📖", "titulo": "Historial Clínico",
         "desc": "Citas realizadas y medicinas",
         "badge": "Ver historial"},
        {"key": "medicinas", "icono": "💊", "titulo": "Medicinas",
         "desc": "Recetas continuas y temporales",
         "badge": f"{len(medicinas_activas)} activa(s)"},
        {"key": "servicios", "icono": "💡", "titulo": "Servicios Públicos",
         "desc": "Luz, agua, gas e internet",
         "badge": f"{len(servicios_all)} código(s)"},
        {"key": "personas", "icono": "👤", "titulo": "Personas",
         "desc": "Personas de seguimiento",
         "badge": f"{len(personas_all)} registrada(s)"},
        {"key": "familia", "icono": "👥", "titulo": "Mi Familia",
         "desc": "Miembros y gestión familiar",
         "badge": nombre_familia},
    ]

    # Cuadrícula de 2 columnas (4 filas con 7 opciones)
    for i in range(0, len(secciones), 2):
        cols = st.columns(2)
        for col, seccion in zip(cols, secciones[i:i + 2]):
            with col:
                if views.render_seccion_tile(
                    seccion["icono"], seccion["titulo"], seccion["desc"],
                    seccion["key"], seccion.get("badge", ""),
                ):
                    ir_a(seccion["key"])


def render_volver(key="btn_volver_home"):
    if st.button("← Volver al inicio", key=key):
        ir_a("home")


def render_vista_actual():
    render_header()
    render_volver("btn_volver_home_top")
    persona_names = persona_model.nombres()

    if vista == "citas":
        col_c_action, col_c_info = st.columns([1, 2])
        with col_c_action:
            citas_controller.render_form_agendar(nombre_usuario, persona_names)
        with col_c_info:
            st.caption("Las citas registradas se suman al historial clínico de la persona para un control completo.")
        citas_controller.render_lista_programadas(nombre_usuario, persona_names)

    elif vista == "emergencias":
        col_e_action, col_e_info = st.columns([1, 2])
        with col_e_action:
            citas_controller.render_form_registrar_emergencia(nombre_usuario, persona_names)
        with col_e_info:
            st.caption("Las emergencias registradas se agregan automáticamente al historial clínico de la persona seleccionada.")
        citas_controller.render_lista_emergencias(persona_names)

    elif vista == "historial":
        medicinas_controller.render_resumen_historial(persona_names)
        st.markdown("")
        citas_controller.render_historial(persona_names)

    elif vista == "medicinas":
        col_m_action, col_m_info = st.columns([1, 2])
        with col_m_action:
            medicinas_controller.render_form_registrar(nombre_usuario, persona_names)
        with col_m_info:
            st.caption("Registra cada recogida de medicinas con dosis, frecuencia y duración del tratamiento.")
        medicinas_controller.render_lista(persona_names)

    elif vista == "servicios":
        views.render_section_header("💡", "Servicios Públicos y Facturas", "Códigos de pago de luz, agua, gas e internet.", tone="amber")

        col_filter, col_action = st.columns([3, 1])
        with col_filter:
            filtro_tipo = ServiciosController.render_filtro_tipo()
        with col_action:
            servicios_controller.render_form_registrar(nombre_usuario)

        servicios_controller.render_lista(filtro_tipo)

    elif vista == "personas":
        views.render_section_header("👤", "Personas de Seguimiento", "Agrega a quienes deseas hacer seguimiento.", tone="violet")

        personas_controller.render_form_crear(nombre_usuario)
        personas_controller.render_lista()

    elif vista == "familia":
        family_controller.render_family_panel(familia_id, user_id)

    st.markdown("")
    render_volver("btn_volver_home_bottom")


# -------------------------------------------------------------
# RENDER DE LA PANTALLA ACTIVA
# -------------------------------------------------------------
if vista == "home":
    render_home()
else:
    render_vista_actual()
