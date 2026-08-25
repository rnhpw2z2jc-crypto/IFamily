"""
VIEW
----
Únicamente presentación: CSS, tarjetas, badges. Estas funciones reciben
datos ya listos y los pintan; no llaman a Firebase ni deciden qué pasa
cuando alguien hace clic en un botón (eso vive en controllers.py).
"""

import streamlit as st

from models import CitaModel, ServicioModel


# -------------------------------------------------------------
# ESTILOS - TEMA "WARM FAMILY CARE"
# -------------------------------------------------------------
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #F0F4F8;
        --primary: #0F4C81;
        --primary-dark: #0A3A66;
        --citas-accent: #DD6B20;
        --servicios-accent: #319795;
        --card-bg: #FFFFFF;
        --text: #1A202C;
        --text-muted: #718096;
        --radius: 12px;
        --shadow: 0 4px 6px rgba(0,0,0,0.06);
    }

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stApp { background-color: var(--bg); }
    h1, h2, h3 { color: var(--text); font-weight: 800; letter-spacing: -0.02em; }
    p, span, label { color: var(--text); }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--text-muted) !important; }

    .stButton > button {
        border-radius: 10px; border: none; background-color: var(--primary);
        color: white; font-weight: 600; padding: 0.55rem 1rem;
        transition: all 0.15s ease; box-shadow: var(--shadow);
    }
    .stButton > button:hover {
        background-color: var(--primary-dark); transform: translateY(-1px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.10);
    }
    .stFormSubmitButton > button { background-color: var(--primary); border-radius: 10px; font-weight: 700; }

    .stTextInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 10px !important; border: 1px solid #E2E8F0 !important; background-color: #FAFBFC !important;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF; border-radius: 10px 10px 0 0; padding: 10px 18px;
        font-weight: 600; color: var(--text-muted); border: 1px solid #E7ECF1; border-bottom: none;
    }
    .stTabs [aria-selected="true"] { color: var(--primary); border-top: 3px solid var(--primary); }

    div[role="radiogroup"] { gap: 8px; }
    div[role="radiogroup"] label {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 6px 14px;
        border-radius: 999px; margin-right: 4px;
    }

    .kpi-card {
        background-color: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow);
        padding: 18px 20px; border-left: 5px solid var(--primary); height: 100%;
    }
    .kpi-card.citas { border-left-color: var(--citas-accent); }
    .kpi-card.servicios { border-left-color: var(--servicios-accent); }
    .kpi-label { font-size: 0.78rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; }
    .kpi-value { font-size: 1.5rem; font-weight: 800; color: var(--text); line-height: 1.2; }
    .kpi-sub { font-size: 0.82rem; color: var(--text-muted); margin-top: 2px; }

    .appt-card, .service-card {
        background-color: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow);
        padding: 16px 20px; margin-bottom: 14px; border: 1px solid #EDF2F7;
    }

    .badge {
        display: inline-block; padding: 3px 12px; border-radius: 999px;
        font-size: 0.75rem; font-weight: 700; margin-right: 6px;
    }
    .badge-papa { background-color: #DCEAFB; color: #1E5A9C; }
    .badge-mama { background-color: #F6DDF2; color: #97267A; }
    .badge-ambos { background-color: #D7F3E3; color: #216E4A; }
    .badge-hoy { background-color: #FBD9BC; color: #9C4221; }
    .badge-semana { background-color: #FEF0C7; color: #92650E; }
    .badge-proximamente { background-color: #DCEAFB; color: #1E5A9C; }
    .badge-atrasada { background-color: #FED7D7; color: #9B2C2C; }

    .service-icon { font-size: 1.6rem; }
    .service-title { font-weight: 700; font-size: 1.05rem; }
    .service-sub { color: var(--text-muted); font-size: 0.85rem; }
    hr { border-color: #E2E8F0; }

    /* ---------------------------------------------------------
       RESPONSIVE: celulares (Android / iOS)
       Streamlit ya apila las columnas solo en pantallas angostas;
       acá afinamos tamaños de toque, tipografía y espaciados para
       que se sienta cómodo con el dedo, no con el mouse.
    --------------------------------------------------------- */
    @media (max-width: 640px) {
        .block-container { padding-left: 1rem !important; padding-right: 1rem !important; padding-top: 1.2rem !important; }

        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.15rem !important; }
        h3 { font-size: 1rem !important; }

        /* Botones y campos más altos: área táctil mínima cómoda (~44px) */
        .stButton > button, .stFormSubmitButton > button {
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
            min-height: 44px;
        }
        .stTextInput input, .stTextArea textarea, .stDateInput input,
        .stTimeInput input, .stSelectbox div[data-baseweb="select"] > div {
            min-height: 44px;
            font-size: 1rem !important; /* evita que iOS haga zoom automático al enfocar el input */
        }

        /* Pestañas más compactas y con texto legible sin recortarse */
        .stTabs [data-baseweb="tab"] { padding: 8px 12px; font-size: 0.85rem; }

        /* Pills de filtro: que quepan bien y se puedan tocar sin errores */
        div[role="radiogroup"] label { padding: 8px 14px; font-size: 0.85rem; }

        /* Tarjetas KPI: menos padding para que las 3 quepan mejor apiladas */
        .kpi-card { padding: 14px 16px; }
        .kpi-value { font-size: 1.25rem; }

        .appt-card, .service-card { padding: 14px 16px; }

        /* Popovers de Streamlit en móvil a veces quedan muy angostos */
        [data-testid="stPopoverBody"] { min-width: 85vw !important; }
    }
    </style>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# BADGES
# -------------------------------------------------------------
def badge_paciente(paciente):
    clase = {"Papá": "badge-papa", "Mamá": "badge-mama", "Ambos": "badge-ambos"}.get(paciente, "badge-ambos")
    return f'<span class="badge {clase}">{paciente}</span>'


def badge_estado_cita(fecha_str):
    texto, clase = CitaModel.estado_visual(fecha_str)
    if not texto:
        return ""
    return f'<span class="badge {clase}">{texto}</span>'


# -------------------------------------------------------------
# KPIs
# -------------------------------------------------------------
def render_kpis(total_citas_programadas, proxima_cita, total_servicios):
    proxima_txt = "Sin citas programadas"
    proxima_sub = "—"
    if proxima_cita is not None:
        proxima_txt = f"{proxima_cita.get('fecha')} · {proxima_cita.get('hora','')}"
        proxima_sub = f"{proxima_cita.get('paciente')} — {proxima_cita.get('especialidad')}"

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="kpi-card citas">
            <div class="kpi-label">📅 Citas próximas</div>
            <div class="kpi-value">{total_citas_programadas}</div>
            <div class="kpi-sub">pendientes por realizar</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card citas">
            <div class="kpi-label">⏰ Próxima cita</div>
            <div class="kpi-value" style="font-size:1.15rem;">{proxima_txt}</div>
            <div class="kpi-sub">{proxima_sub}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card servicios">
            <div class="kpi-label">💡 Servicios registrados</div>
            <div class="kpi-value">{total_servicios}</div>
            <div class="kpi-sub">códigos de pago guardados</div>
        </div>""", unsafe_allow_html=True)


# -------------------------------------------------------------
# TARJETA DE CITA (solo la parte visual, sin botones de acción)
# -------------------------------------------------------------
def render_appt_card(cita):
    st.markdown(f"""
    <div class="appt-card">
        <div>
            {badge_paciente(cita.get('paciente'))}{badge_estado_cita(cita.get('fecha'))}
            <div style="font-weight:700; font-size:1.05rem; margin-top:6px;">{cita.get('especialidad')}</div>
            <div class="service-sub">🏥 {cita.get('lugar')} · 📆 {cita.get('fecha')} {cita.get('hora','')}</div>
        </div>
    </div>""", unsafe_allow_html=True)


# -------------------------------------------------------------
# TARJETA DE SERVICIO (solo la parte visual)
# -------------------------------------------------------------
def render_service_info(servicio):
    icono = ServicioModel.icono(servicio.get("tipo"))
    st.markdown(f"""
    <div class="service-card">
        <div class="service-icon">{icono}</div>
        <div class="service-title">{servicio.get('empresa')}</div>
        <div class="service-sub">{servicio.get('tipo')} · Titular: {servicio.get('titular','No especificado')}</div>
        <div class="service-sub">Registrado por {servicio.get('registrado_por','—')}</div>
    </div>""", unsafe_allow_html=True)