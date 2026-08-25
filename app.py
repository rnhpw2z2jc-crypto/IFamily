import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
from datetime import date, datetime

# -------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------------------
st.set_page_config(
    page_title="Familia - Citas y Servicios",
    page_icon="🏥",
    layout="wide"
)

# -------------------------------------------------------------
# INICIALIZACIÓN DE FIREBASE
# -------------------------------------------------------------
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            if "FIREBASE_KEY" in st.secrets:
                key_dict = json.loads(st.secrets["FIREBASE_KEY"])
                cred = credentials.Certificate(key_dict)
                db_url = st.secrets["FIREBASE_DB_URL"]
            else:
                cred = credentials.Certificate("firebase_key.json")
                db_url = "https://TU-PROYECTO-default-rtdb.firebaseio.com/"

            firebase_admin.initialize_app(cred, {'databaseURL': db_url})
            return True
        except Exception as e:
            st.error(f"Error al conectar con Firebase: {e}")
            return False
    return True

firebase_ok = init_firebase()

ref_citas = db.reference("citas") if firebase_ok else None
ref_servicios = db.reference("servicios") if firebase_ok else None

# -------------------------------------------------------------
# IDENTIFICACIÓN SIMPLE DEL HERMANO (sin login, solo etiqueta)
# -------------------------------------------------------------
with st.sidebar:
    st.header("👤 ¿Quién eres?")
    if "nombre_usuario" not in st.session_state:
        st.session_state.nombre_usuario = ""
    st.session_state.nombre_usuario = st.text_input(
        "Tu nombre (para saber quién registró cada dato)",
        value=st.session_state.nombre_usuario,
        placeholder="Ej. Ana"
    )
    if not st.session_state.nombre_usuario:
        st.info("Escribe tu nombre para poder guardar información.")
    st.divider()
    st.caption("Esta app es compartida por toda la familia. Todo lo que registres lo verán tus hermanos también.")

usuario_actual = st.session_state.nombre_usuario or "Sin nombre"

st.title("🏡 Control Familiar: Papá y Mamá")
st.caption("Citas médicas con historial clínico + códigos de pago de servicios, todo en un solo lugar para los hermanos.")

tab1, tab2 = st.tabs(["📅 Citas Médicas", "💡 Servicios Públicos"])

# ===============================================================
# TAB 1: CITAS MÉDICAS
# ===============================================================
with tab1:
    sub_prog, sub_hist = st.tabs(["🗓️ Próximas citas", "📖 Historial clínico"])

    # -----------------------------------------------------------
    # Cargar datos de citas una sola vez
    # -----------------------------------------------------------
    citas_data = ref_citas.get() if ref_citas else None
    citas_data = citas_data or {}

    citas_programadas = {k: v for k, v in citas_data.items() if v.get("estado", "programada") == "programada"}
    citas_realizadas = {k: v for k, v in citas_data.items() if v.get("estado") == "realizada"}

    # -----------------------------------------------------------
    # SUBTAB: PRÓXIMAS CITAS
    # -----------------------------------------------------------
    with sub_prog:
        col_form, col_list = st.columns([1, 2])

        with col_form:
            st.subheader("➕ Agendar nueva cita")
            with st.form("form_citas", clear_on_submit=True):
                paciente = st.selectbox("Paciente", ["Papá", "Mamá", "Ambos"])
                especialidad = st.text_input("Especialidad / Doctor", placeholder="Ej. Cardiología - Dr. Pérez")
                lugar = st.text_input("Hospital / Clínica", placeholder="Ej. Hospital Nacional / Clínica San Pablo")
                fecha = st.date_input("Fecha", value=date.today())
                hora = st.time_input("Hora")
                notas = st.text_area("Notas / Indicaciones previas", placeholder="Ej. Ir en ayunas de 8 horas, llevar exámenes")

                btn_cita = st.form_submit_button("Guardar cita", use_container_width=True)

                if btn_cita:
                    if not st.session_state.nombre_usuario:
                        st.error("Primero escribe tu nombre en la barra lateral.")
                    elif especialidad and lugar:
                        nueva_cita = {
                            "paciente": paciente,
                            "especialidad": especialidad,
                            "lugar": lugar,
                            "fecha": str(fecha),
                            "hora": str(hora),
                            "notas": notas,
                            "estado": "programada",
                            "registrado_por": usuario_actual,
                        }
                        ref_citas.push(nueva_cita)
                        st.success("¡Cita registrada!")
                        st.rerun()
                    else:
                        st.error("Completa al menos la especialidad y el lugar.")

        with col_list:
            st.subheader("📋 Citas programadas")
            if citas_programadas:
                citas_ordenadas = sorted(
                    citas_programadas.items(),
                    key=lambda item: (item[1].get("fecha", ""), item[1].get("hora", ""))
                )
                for key, c in citas_ordenadas:
                    with st.expander(f"📌 {c.get('fecha')} {c.get('hora','')} — {c.get('paciente')}: {c.get('especialidad')}"):
                        st.markdown(f"**🏥 Lugar:** {c.get('lugar')}")
                        if c.get("notas"):
                            st.markdown(f"**📝 Notas previas:** {c.get('notas')}")
                        st.caption(f"Registrado por: {c.get('registrado_por', 'desconocido')}")

                        st.markdown("---")
                        st.markdown("**✅ ¿Ya pasó la cita? Regístrala en el historial:**")
                        with st.form(f"form_realizada_{key}"):
                            diagnostico = st.text_area("Diagnóstico / resultado", key=f"diag_{key}")
                            tratamiento = st.text_area("Tratamiento / medicamentos indicados", key=f"trat_{key}")
                            recomendaciones = st.text_area("Recomendaciones del doctor", key=f"reco_{key}")
                            proxima_sugerida = st.date_input("Próxima cita sugerida (opcional)", key=f"prox_{key}", value=None)
                            col_a, col_b = st.columns(2)
                            marcar_realizada = col_a.form_submit_button("✅ Marcar como realizada", use_container_width=True)
                            eliminar = col_b.form_submit_button("🗑️ Eliminar sin registrar", use_container_width=True)

                            if marcar_realizada:
                                actualizacion = {
                                    "estado": "realizada",
                                    "diagnostico": diagnostico,
                                    "tratamiento": tratamiento,
                                    "recomendaciones": recomendaciones,
                                    "proxima_cita_sugerida": str(proxima_sugerida) if proxima_sugerida else "",
                                    "fecha_registro_historial": str(date.today()),
                                    "actualizado_por": usuario_actual,
                                }
                                ref_citas.child(key).update(actualizacion)
                                st.success("Movida al historial clínico ✅")
                                st.rerun()

                            if eliminar:
                                ref_citas.child(key).delete()
                                st.warning("Cita eliminada")
                                st.rerun()
            else:
                st.info("No hay citas programadas por ahora.")

    # -----------------------------------------------------------
    # SUBTAB: HISTORIAL CLÍNICO
    # -----------------------------------------------------------
    with sub_hist:
        st.subheader("📖 Historial clínico")
        st.caption("Aquí queda registro de cada cita ya realizada, para recordar qué se dijo antes de volver al médico.")

        filtro_paciente = st.radio("Filtrar por:", ["Todos", "Papá", "Mamá", "Ambos"], horizontal=True)

        historial_filtrado = citas_realizadas
        if filtro_paciente != "Todos":
            historial_filtrado = {k: v for k, v in citas_realizadas.items() if v.get("paciente") == filtro_paciente}

        if historial_filtrado:
            historial_ordenado = sorted(
                historial_filtrado.items(),
                key=lambda item: item[1].get("fecha", ""),
                reverse=True
            )
            for key, c in historial_ordenado:
                titulo = f"🗂️ {c.get('fecha')} — {c.get('paciente')}: {c.get('especialidad')} ({c.get('lugar')})"
                with st.expander(titulo):
                    st.markdown(f"**🏥 Lugar:** {c.get('lugar')}")
                    if c.get("diagnostico"):
                        st.markdown(f"**🩺 Diagnóstico:** {c.get('diagnostico')}")
                    if c.get("tratamiento"):
                        st.markdown(f"**💊 Tratamiento:** {c.get('tratamiento')}")
                    if c.get("recomendaciones"):
                        st.markdown(f"**📋 Recomendaciones:** {c.get('recomendaciones')}")
                    if c.get("proxima_cita_sugerida"):
                        st.markdown(f"**⏭️ Próxima cita sugerida:** {c.get('proxima_cita_sugerida')}")
                    st.caption(
                        f"Cita registrada por: {c.get('registrado_por', '—')} · "
                        f"Historial completado por: {c.get('actualizado_por', '—')}"
                    )
                    if st.button("🗑️ Eliminar de historial", key=f"del_hist_{key}"):
                        ref_citas.child(key).delete()
                        st.rerun()
        else:
            st.info("Aún no hay citas registradas en el historial para este filtro.")

# ===============================================================
# TAB 2: SERVICIOS PÚBLICOS
# ===============================================================
with tab2:
    st.header("Códigos de pago de servicios")
    col_s_form, col_s_list = st.columns([1, 2])

    with col_s_form:
        st.subheader("➕ Registrar código")
        with st.form("form_servicios", clear_on_submit=True):
            tipo = st.selectbox("Tipo de servicio", ["⚡ Luz", "💧 Agua", "🔥 Gas", "🌐 Internet", "📞 Teléfono", "Otro"])
            empresa = st.text_input("Empresa proveedora", placeholder="Ej. Enel, Sedapal, Cálidda, Claro")
            codigo = st.text_input("Código de pago / Número de suministro", placeholder="Ej. 12345678")
            titular = st.text_input("Titular del recibo", placeholder="Ej. Nombre de Papá o Mamá")

            btn_servicio = st.form_submit_button("Guardar código", use_container_width=True)

            if btn_servicio:
                if not st.session_state.nombre_usuario:
                    st.error("Primero escribe tu nombre en la barra lateral.")
                elif empresa and codigo:
                    nuevo_servicio = {
                        "tipo": tipo,
                        "empresa": empresa,
                        "codigo": codigo,
                        "titular": titular,
                        "registrado_por": usuario_actual,
                        "fecha_registro": str(date.today()),
                    }
                    ref_servicios.push(nuevo_servicio)
                    st.success("¡Servicio registrado!")
                    st.rerun()
                else:
                    st.error("Ingresa al menos la empresa y el código de pago.")

    with col_s_list:
        st.subheader("🔑 Códigos almacenados")
        servicios = ref_servicios.get() if ref_servicios else None

        if servicios:
            for key, s in servicios.items():
                st.info(
                    f"### {s.get('tipo')} — {s.get('empresa')}\n\n"
                    f"**💳 Código de pago:** `{s.get('codigo')}`\n\n"
                    f"**👤 Titular:** {s.get('titular', 'No especificado')}\n\n"
                    f"_Registrado por {s.get('registrado_por','—')}_"
                )
                if st.button("🗑️ Eliminar código", key=f"del_serv_{key}"):
                    ref_servicios.child(key).delete()
                    st.success("Servicio eliminado")
                    st.rerun()
        else:
            st.info("No hay códigos de pago registrados todavía.")