"""
CONTROLLER
----------
Recibe la interacción del usuario (formularios, botones), valida,
llama al Model para persistir o leer datos, y dispara st.rerun().
No define estilos ni CSS (eso es de views.py), aunque sí usa las
funciones de views.py para pintar tarjetas dentro de su flujo.

En Streamlit, el "control de eventos" y el "widget" viven en la misma
línea de código por cómo funciona el framework (a diferencia de un MVC
web clásico con rutas separadas). Por eso cada método de acá agrupa
"dibujar el formulario" + "manejar su envío" — es la forma más fiel de
Controller que el propio Streamlit permite.
"""

from datetime import date

import streamlit as st

from models import CitaModel, ServicioModel
import views


# -------------------------------------------------------------
# CONTROLADOR: IDENTIFICACIÓN DEL USUARIO (barra lateral)
# -------------------------------------------------------------
class SidebarController:
    @staticmethod
    def render():
        with st.sidebar:
            st.header("👤 ¿Quién eres?")
            if "nombre_usuario" not in st.session_state:
                st.session_state.nombre_usuario = ""
            st.session_state.nombre_usuario = st.text_input(
                "Tu nombre (para saber quién registró cada dato)",
                value=st.session_state.nombre_usuario,
                placeholder="Ej. Ana",
            )
            if not st.session_state.nombre_usuario:
                st.info("Escribe tu nombre para poder guardar información.")
            st.divider()
            st.caption("Esta app es compartida por toda la familia. Todo lo que registres lo verán tus hermanos también.")
        return st.session_state.nombre_usuario or "Sin nombre"


# -------------------------------------------------------------
# CONTROLADOR: CITAS MÉDICAS
# -------------------------------------------------------------
class CitasController:
    def __init__(self, cita_model: CitaModel):
        self.model = cita_model

    def render_form_agendar(self, usuario):
        with st.popover("➕ Agendar cita", use_container_width=True):
            with st.form("form_citas", clear_on_submit=True):
                paciente = st.selectbox("Paciente", ["Papá", "Mamá", "Ambos"])
                especialidad = st.text_input("Especialidad / Doctor", placeholder="Ej. Cardiología - Dr. Pérez")
                lugar = st.text_input("Hospital / Clínica", placeholder="Ej. Hospital Nacional")
                fecha = st.date_input("Fecha", value=date.today())
                hora = st.time_input("Hora")
                notas = st.text_area("Notas / Indicaciones previas", placeholder="Ej. Ir en ayunas de 8 horas")

                if st.form_submit_button("Guardar cita", use_container_width=True):
                    if not usuario or usuario == "Sin nombre":
                        st.error("Primero escribe tu nombre en la barra lateral.")
                    elif especialidad and lugar:
                        self.model.crear(paciente, especialidad, lugar, fecha, hora, notas, usuario)
                        st.success("¡Cita registrada!")
                        st.rerun()
                    else:
                        st.error("Completa al menos la especialidad y el lugar.")

    def render_form_marcar_realizada(self, key, usuario):
        with st.popover("✅ Marcar realizada", use_container_width=True):
            with st.form(f"form_realizada_{key}"):
                diagnostico = st.text_area("Diagnóstico / resultado", key=f"diag_{key}")
                tratamiento = st.text_area("Tratamiento / medicamentos", key=f"trat_{key}")
                recomendaciones = st.text_area("Recomendaciones del doctor", key=f"reco_{key}")
                proxima_sugerida = st.date_input("Próxima cita sugerida (opcional)", key=f"prox_{key}", value=None)

                if st.form_submit_button("Guardar en historial", use_container_width=True):
                    self.model.marcar_realizada(key, diagnostico, tratamiento, recomendaciones, proxima_sugerida, usuario)
                    st.success("Movida al historial clínico ✅")
                    st.rerun()

    @staticmethod
    def render_filtro_paciente(key="filtro_prog"):
        return st.radio("Filtrar por paciente", ["Todos", "Papá", "Mamá", "Ambos"], horizontal=True, key=key)

    def render_lista_programadas(self, usuario, filtro):
        programadas = self.model.get_programadas()
        vista = CitaModel.filtrar_por_paciente(programadas, filtro)

        if not vista:
            st.info("No hay citas programadas por ahora para este filtro.")
            return

        for key, cita in CitaModel.ordenar_por_fecha(vista):
            views.render_appt_card(cita)
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                if cita.get("notas"):
                    st.caption(f"📝 {cita.get('notas')} · Registrado por {cita.get('registrado_por','—')}")
            with col_b:
                self.render_form_marcar_realizada(key, usuario)
            with col_c:
                if st.button("🗑️ Eliminar", key=f"del_cita_{key}", use_container_width=True):
                    self.model.eliminar(key)
                    st.rerun()

    def render_historial(self):
        st.caption("Registro de cada cita ya realizada, para recordar qué se dijo antes de volver al médico.")
        filtro = self.render_filtro_paciente(key="filtro_hist")
        realizadas = self.model.get_realizadas()
        vista = CitaModel.filtrar_por_paciente(realizadas, filtro)

        if not vista:
            st.info("Aún no hay citas registradas en el historial para este filtro.")
            return

        for key, cita in CitaModel.ordenar_por_fecha(vista, descendente=True):
            titulo = f"🗂️ {cita.get('fecha')} — {cita.get('paciente')}: {cita.get('especialidad')} ({cita.get('lugar')})"
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
                    st.markdown(f"**⏭️ Próxima cita sugerida:** {cita.get('proxima_cita_sugerida')}")
                st.caption(f"Registrada por {cita.get('registrado_por','—')} · Historial completado por {cita.get('actualizado_por','—')}")
                if st.button("🗑️ Eliminar de historial", key=f"del_hist_{key}"):
                    self.model.eliminar(key)
                    st.rerun()


# -------------------------------------------------------------
# CONTROLADOR: SERVICIOS PÚBLICOS
# -------------------------------------------------------------
class ServiciosController:
    def __init__(self, servicio_model: ServicioModel):
        self.model = servicio_model

    def render_form_registrar(self, usuario):
        with st.popover("➕ Registrar código", use_container_width=True):
            with st.form("form_servicios", clear_on_submit=True):
                tipo = st.selectbox("Tipo de servicio", ["⚡ Luz", "💧 Agua", "🔥 Gas", "🌐 Internet", "📞 Teléfono", "Otro"])
                empresa = st.text_input("Empresa proveedora", placeholder="Ej. Enel, Sedapal, Cálidda")
                codigo = st.text_input("Código de pago / Suministro", placeholder="Ej. 12345678")
                titular = st.text_input("Titular del recibo", placeholder="Ej. Nombre de Papá o Mamá")

                if st.form_submit_button("Guardar código", use_container_width=True):
                    if not usuario or usuario == "Sin nombre":
                        st.error("Primero escribe tu nombre en la barra lateral.")
                    elif empresa and codigo:
                        self.model.crear(tipo, empresa, codigo, titular, usuario)
                        st.success("¡Servicio registrado!")
                        st.rerun()
                    else:
                        st.error("Ingresa al menos la empresa y el código de pago.")

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
            st.info("No hay códigos de pago registrados para este filtro.")
            return

        for key, servicio in vista.items():
            col_info, col_code, col_actions = st.columns([2, 2, 1])
            with col_info:
                views.render_service_info(servicio)
            with col_code:
                st.markdown('<div style="margin-top:8px;">', unsafe_allow_html=True)
                st.code(servicio.get("codigo", ""), language=None)
                st.markdown('</div>', unsafe_allow_html=True)
            with col_actions:
                st.write("")
                if st.button("🗑️ Eliminar", key=f"del_serv_{key}", use_container_width=True):
                    self.model.eliminar(key)
                    st.rerun()
            st.divider()