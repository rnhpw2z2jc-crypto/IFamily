"""
app.py — Punto de entrada.
Solo arma la página y conecta Model + View + Controller.
No contiene reglas de negocio (eso es models.py) ni CSS (views.py)
ni manejo de formularios (controllers.py).
"""

import streamlit as st

import views
from models import FirebaseService, CitaModel, ServicioModel
from controllers import SidebarController, CitasController, ServiciosController

# -------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -------------------------------------------------------------
st.set_page_config(page_title="Familia - Citas y Servicios", page_icon="🏥", layout="wide")

# -------------------------------------------------------------
# PWA: hace que Android ofrezca "Instalar app" y que iOS use un
# ícono y nombre propios al agregarla a la pantalla de inicio.
# -------------------------------------------------------------
st.markdown("""
<link rel="manifest" href="app/static/manifest.json">
<meta name="theme-color" content="#0F4C81">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" href="app/static/icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Familia">
<script>
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('app/static/service-worker.js').catch(function(err) {
        console.log('Service worker no registrado:', err);
    });
}
</script>
""", unsafe_allow_html=True)

views.inject_css()

# -------------------------------------------------------------
# MODEL: conexión a Firebase e instancias de los modelos
# -------------------------------------------------------------
firebase = FirebaseService(st.secrets)
if not firebase.ok:
    st.error(f"Error al conectar con Firebase: {firebase.error}")

cita_model = CitaModel(firebase)
servicio_model = ServicioModel(firebase)

# -------------------------------------------------------------
# CONTROLLER: identificación del hermano que usa la app
# -------------------------------------------------------------
usuario_actual = SidebarController.render()

# -------------------------------------------------------------
# VIEW: encabezado
# -------------------------------------------------------------
st.title("🏡 Control Familiar: Papá y Mamá")
st.caption("Citas médicas con historial clínico + códigos de pago de servicios, todo en un solo lugar para los hermanos.")

# -------------------------------------------------------------
# VIEW: KPIs (con datos que vienen del Model)
# -------------------------------------------------------------
_, proxima_cita = cita_model.proxima_cita()
views.render_kpis(
    total_citas_programadas=len(cita_model.get_programadas()),
    proxima_cita=proxima_cita,
    total_servicios=len(servicio_model.get_all()),
)

st.write("")

# -------------------------------------------------------------
# CONTROLLERS: pestañas principales
# -------------------------------------------------------------
citas_controller = CitasController(cita_model)
servicios_controller = ServiciosController(servicio_model)

tab1, tab2 = st.tabs(["📅 Citas Médicas", "💡 Servicios Públicos"])

with tab1:
    sub_prog, sub_hist = st.tabs(["🗓️ Próximas citas", "📖 Historial clínico"])

    with sub_prog:
        top_left, top_right = st.columns([3, 1])
        with top_left:
            filtro_prog = CitasController.render_filtro_paciente()
        with top_right:
            citas_controller.render_form_agendar(usuario_actual)
        citas_controller.render_lista_programadas(usuario_actual, filtro_prog)

    with sub_hist:
        citas_controller.render_historial()

with tab2:
    top_left, top_right = st.columns([3, 1])
    with top_left:
        filtro_tipo = ServiciosController.render_filtro_tipo()
    with top_right:
        servicios_controller.render_form_registrar(usuario_actual)
    servicios_controller.render_lista(filtro_tipo)