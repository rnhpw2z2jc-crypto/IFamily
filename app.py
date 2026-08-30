"""
app.py — Punto de entrada de iFamily.
Autenticación → Familias → Dashboard principal.
"""

import streamlit as st

import views
from models import (
    FirebaseService, UserModel, FamilyModel,
    CitaModel, ServicioModel, PersonaModel, _sanitize,
)
from controllers import (
    AuthController, FamilyController, AdminController,
    CitasController, ServiciosController, PersonasController,
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

# -------------------------------------------------------------
# HEADER PRINCIPAL
# -------------------------------------------------------------
nombre_usuario = user_data.get("nombre", "Sin nombre")
familia_data = family_model.get_familia(familia_id)
nombre_familia = familia_data.get("nombre", "Mi Familia")

st.markdown(f"""
<div style="margin-bottom:8px;">
    <h1 style="margin:0; font-size:1.6rem;">🏠 {_sanitize(nombre_familia)}</h1>
    <p style="color:var(--text-muted); margin:4px 0 0 0; font-size:0.9rem;">
        Bienvenido, <strong>{_sanitize(nombre_usuario)}</strong> — Control familiar inteligente
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# KPIs
# -------------------------------------------------------------
_, proxima_cita = cita_model.proxima_cita()
views.render_kpis(
    total_citas_programadas=len(cita_model.get_programadas()),
    proxima_cita=proxima_cita,
    total_servicios=len(servicio_model.get_all()),
    total_emergencias=len(cita_model.get_emergencias()),
)

# -------------------------------------------------------------
# ALERTAS
# -------------------------------------------------------------
alertas = views.obtener_alertas(cita_model, persona_model)

# Notificación push del sistema (PWA)
if "alertas_enviadas" not in st.session_state:
    st.session_state.alertas_enviadas = ""
views.inject_notificacion_script(alertas)

if alertas:
    views.render_alerta_panel(alertas)

st.write("")

# -------------------------------------------------------------
# TABS PRINCIPALES
# -------------------------------------------------------------
tab_citas, tab_emergencias, tab_historial, tab_servicios, tab_personas, tab_familia = st.tabs([
    "📅 Citas Médicas",
    "🚨 Emergencias",
    "📖 Historial Clínico",
    "💡 Servicios Públicos",
    "👤 Personas",
    "👥 Mi Familia",
])

citas_controller = CitasController(cita_model)
servicios_controller = ServiciosController(servicio_model)
family_controller = FamilyController(family_model, user_model)
personas_controller = PersonasController(persona_model)

persona_names = persona_model.nombres()

# -------------------------------------------------------------
# TAB: CITAS MÉDICAS
# -------------------------------------------------------------
with tab_citas:
    col_c_action, col_c_info = st.columns([1, 2])
    with col_c_action:
        citas_controller.render_form_agendar(nombre_usuario, persona_names)
    with col_c_info:
        st.caption("Las citas registradas se suman al historial clínico de la persona para un control completo.")

    citas_controller.render_lista_programadas(nombre_usuario, persona_names)

# -------------------------------------------------------------
# TAB: EMERGENCIAS
# -------------------------------------------------------------
with tab_emergencias:
    col_e_action, col_e_info = st.columns([1, 2])
    with col_e_action:
        citas_controller.render_form_registrar_emergencia(nombre_usuario, persona_names)
    with col_e_info:
        st.caption("Las emergencias registradas se agregan automáticamente al historial clínico de la persona seleccionada.")

    citas_controller.render_lista_emergencias(persona_names)

# -------------------------------------------------------------
# TAB: HISTORIAL CLÍNICO
# -------------------------------------------------------------
with tab_historial:
    citas_controller.render_historial(persona_names)

# -------------------------------------------------------------
# TAB: SERVICIOS PÚBLICOS
# -------------------------------------------------------------
with tab_servicios:
    views.render_section_header("💡", "Servicios Públicos y Facturas", "Códigos de pago de luz, agua, gas e internet.")

    col_filter, col_action = st.columns([3, 1])
    with col_filter:
        filtro_tipo = ServiciosController.render_filtro_tipo()
    with col_action:
        servicios_controller.render_form_registrar(nombre_usuario)

    servicios_controller.render_lista(filtro_tipo)

# -------------------------------------------------------------
# TAB: PERSONAS DE SEGUIMIENTO
# -------------------------------------------------------------
with tab_personas:
    views.render_section_header("👤", "Personas de Seguimiento", "Agrega a quienes deseas hacer seguimiento.")

    personas_controller.render_form_crear(nombre_usuario)
    personas_controller.render_lista()

# -------------------------------------------------------------
# TAB: MI FAMILIA
# -------------------------------------------------------------
with tab_familia:
    family_controller.render_family_panel(familia_id, user_id)
