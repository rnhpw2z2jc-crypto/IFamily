"""
VIEW
----
Presentación visual con Glassmorphism y paleta turquesa iFamily.
CSS, tarjetas, badges, empty states, skeletons.
"""

import streamlit as st

from models import CitaModel, ServicioModel, _sanitize


# -------------------------------------------------------------
# ESTILOS - TEMA "IFAMILY GLASSMORPHISM"
# -------------------------------------------------------------
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
        --primary: #00BCD4;
        --primary-dark: #00ACC1;
        --primary-deeper: #00838F;
        --primary-light: #B2EBF2;
        --primary-glow: rgba(0, 188, 212, 0.3);
        --bg-gradient-start: #E0F7FA;
        --bg-gradient-end: #F0F9FF;
        --glass-bg: rgba(255, 255, 255, 0.65);
        --glass-border: rgba(255, 255, 255, 0.5);
        --glass-shadow: 0 8px 32px rgba(0, 188, 212, 0.12);
        --card-bg: rgba(255, 255, 255, 0.75);
        --text: #1A202C;
        --text-muted: #64748B;
        --text-light: #94A3B8;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --radius: 16px;
        --radius-sm: 10px;
        --radius-pill: 999px;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
    }

    .stApp > header {
        background: transparent !important;
    }

    h1, h2, h3, h4 {
        color: var(--text) !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
    }

    p, span, label, div {
        color: var(--text);
    }

    /* ---------------------------------------------------------
       GLASSMORPHISM CARDS
    --------------------------------------------------------- */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        box-shadow: var(--glass-shadow);
        padding: 20px 24px;
        margin-bottom: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 188, 212, 0.18);
        border-color: var(--primary-light);
    }

    .glass-card-sm {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-sm);
        padding: 14px 18px;
        transition: all 0.3s ease;
    }

    /* ---------------------------------------------------------
       KPI CARDS CON GLASS
    --------------------------------------------------------- */
    .kpi-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        box-shadow: var(--glass-shadow);
        padding: 20px 22px;
        height: 100%;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--primary-dark));
        border-radius: var(--radius) var(--radius) 0 0;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 36px rgba(0, 188, 212, 0.2);
    }

    .kpi-icon {
        font-size: 2rem;
        margin-bottom: 8px;
        filter: drop-shadow(0 2px 4px rgba(0, 188, 212, 0.3));
    }

    .kpi-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.8rem;
        font-weight: 900;
        color: var(--primary-dark);
        line-height: 1.1;
    }

    .kpi-sub {
        font-size: 0.82rem;
        color: var(--text-muted);
        margin-top: 4px;
    }

    /* ---------------------------------------------------------
       PILLS / BOTONES GLOW
    --------------------------------------------------------- */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-pill) !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 4px 15px var(--primary-glow) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.15) 50%,
            transparent 70%
        );
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }

    .stButton > button:hover::after {
        transform: translateX(100%);
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(0, 188, 212, 0.35) !important;
    }

    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* ---------------------------------------------------------
       FORMULARIOS
    --------------------------------------------------------- */
    .stTextInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input {
        border-radius: var(--radius-sm) !important;
        border: 2px solid #E2E8F0 !important;
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(8px) !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-glow) !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: var(--radius-sm) !important;
        border: 2px solid #E2E8F0 !important;
        background-color: rgba(255, 255, 255, 0.8) !important;
    }

    .stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-deeper) 100%) !important;
        border-radius: var(--radius-pill) !important;
        font-weight: 800 !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        box-shadow: 0 6px 20px var(--primary-glow) !important;
    }

    /* ---------------------------------------------------------
       TABS GLASS
    --------------------------------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: var(--radius);
        padding: 6px;
        border: 1px solid var(--glass-border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: var(--radius-sm) !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        color: var(--text-muted) !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px var(--primary-glow) !important;
    }

    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background: var(--primary-light) !important;
        color: var(--primary-dark) !important;
    }

    /* ---------------------------------------------------------
       RADIO PILLS
    --------------------------------------------------------- */
    div[role="radiogroup"] {
        gap: 8px;
    }

    div[role="radiogroup"] label {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(8px);
        border: 2px solid #E2E8F0 !important;
        padding: 10px 20px !important;
        border-radius: var(--radius-pill) !important;
        margin-right: 4px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }

    div[role="radiogroup"] label:hover {
        border-color: var(--primary-light) !important;
        background: rgba(0, 188, 212, 0.08) !important;
    }

    div[role="radiogroup"] label[data-checked="true"],
    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border-color: var(--primary) !important;
        box-shadow: 0 4px 12px var(--primary-glow) !important;
    }

    /* ---------------------------------------------------------
       BADGES CON GLASS
    --------------------------------------------------------- */
    .badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: var(--radius-pill);
        font-size: 0.72rem;
        font-weight: 700;
        margin-right: 6px;
        backdrop-filter: blur(4px);
        border: 1px solid transparent;
        letter-spacing: 0.02em;
    }

    .badge-papa {
        background: rgba(0, 188, 212, 0.12);
        color: var(--primary-deeper);
        border-color: rgba(0, 188, 212, 0.25);
    }

    .badge-mama {
        background: rgba(236, 72, 153, 0.12);
        color: #BE185D;
        border-color: rgba(236, 72, 153, 0.25);
    }

    .badge-ambos {
        background: rgba(16, 185, 129, 0.12);
        color: #047857;
        border-color: rgba(16, 185, 129, 0.25);
    }

    .badge-persona {
        background: rgba(99, 102, 241, 0.12);
        color: #4338CA;
        border-color: rgba(99, 102, 241, 0.25);
    }

    .badge-hoy {
        background: rgba(239, 68, 68, 0.12);
        color: #DC2626;
        border-color: rgba(239, 68, 68, 0.25);
        animation: pulse-badge 2s infinite;
    }

    .badge-semana {
        background: rgba(245, 158, 11, 0.12);
        color: #D97706;
        border-color: rgba(245, 158, 11, 0.25);
    }

    .badge-proximamente {
        background: rgba(0, 188, 212, 0.12);
        color: var(--primary-deeper);
        border-color: rgba(0, 188, 212, 0.25);
    }

    .badge-atrasada {
        background: rgba(239, 68, 68, 0.15);
        color: #DC2626;
        border-color: rgba(239, 68, 68, 0.3);
        animation: pulse-badge 1.5s infinite;
    }

    @keyframes pulse-badge {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    /* ---------------------------------------------------------
       APPOINTMENT CARDS
    --------------------------------------------------------- */
    .appt-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        box-shadow: var(--glass-shadow);
        padding: 18px 22px;
        margin-bottom: 14px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .appt-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, var(--primary), var(--primary-dark));
    }

    .appt-card:hover {
        transform: translateX(4px);
        box-shadow: 0 12px 36px rgba(0, 188, 212, 0.15);
    }

    .appt-title {
        font-weight: 800;
        font-size: 1.05rem;
        margin-top: 8px;
        color: var(--text);
    }

    .appt-meta {
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-top: 4px;
    }

    /* ---------------------------------------------------------
       SERVICE CARDS
    --------------------------------------------------------- */
    .service-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius);
        box-shadow: var(--glass-shadow);
        padding: 18px 22px;
        margin-bottom: 14px;
        transition: all 0.3s ease;
    }

    .service-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 188, 212, 0.12);
    }

    .service-icon {
        font-size: 2rem;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
    }

    .service-title {
        font-weight: 800;
        font-size: 1.05rem;
        color: var(--text);
    }

    .service-sub {
        color: var(--text-muted);
        font-size: 0.85rem;
    }

    .service-code {
        background: rgba(0, 188, 212, 0.06);
        border: 2px dashed var(--primary-light);
        border-radius: var(--radius-sm);
        padding: 12px 16px;
        font-family: 'Fira Code', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--primary-dark);
        text-align: center;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .service-code:hover {
        background: rgba(0, 188, 212, 0.12);
        border-color: var(--primary);
    }

    /* ---------------------------------------------------------
       EMPTY STATES
    --------------------------------------------------------- */
    .empty-state {
        text-align: center;
        padding: 48px 24px;
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        border: 2px dashed var(--primary-light);
        border-radius: var(--radius);
        margin: 24px 0;
    }

    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 16px;
        opacity: 0.6;
    }

    .empty-state-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: var(--text);
        margin-bottom: 8px;
    }

    .empty-state-desc {
        font-size: 0.9rem;
        color: var(--text-muted);
        max-width: 400px;
        margin: 0 auto;
    }

    /* ---------------------------------------------------------
       SIDEBAR GLASS
    --------------------------------------------------------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F0FDFA 0%, #E0F7FA 100%) !important;
        border-right: 1px solid var(--glass-border) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--primary-dark) !important;
    }

    /* ---------------------------------------------------------
       SCROLLBAR
    --------------------------------------------------------- */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary-light);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }

    /* ---------------------------------------------------------
       DIVIDER
    --------------------------------------------------------- */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--primary-light), transparent);
        margin: 16px 0;
    }

    /* ---------------------------------------------------------
       RESPONSIVE
    --------------------------------------------------------- */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }

        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1rem !important; }

        .stButton > button, .stFormSubmitButton > button {
            padding: 0.85rem 1.2rem !important;
            font-size: 0.95rem !important;
            min-height: 48px !important;
        }

        .stTextInput input, .stTextArea textarea, .stDateInput input,
        .stTimeInput input {
            min-height: 48px !important;
            font-size: 1rem !important;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 10px 14px !important;
            font-size: 0.85rem !important;
        }

        div[role="radiogroup"] label {
            padding: 10px 16px !important;
            font-size: 0.85rem !important;
        }

        .kpi-card { padding: 16px 18px; }
        .kpi-value { font-size: 1.4rem; }

        .appt-card, .service-card { padding: 14px 16px; }

        [data-testid="stPopoverBody"] { min-width: 90vw !important; }
    }

    /* ---------------------------------------------------------
       LOADING SKELETON
    --------------------------------------------------------- */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s infinite;
        border-radius: var(--radius-sm);
    }

    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ---------------------------------------------------------
       USER AVATAR
    --------------------------------------------------------- */
    .user-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 1.2rem;
        box-shadow: 0 4px 12px var(--primary-glow);
    }

    .family-badge {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        padding: 6px 16px;
        border-radius: var(--radius-pill);
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 8px var(--primary-glow);
    }

    /* ---------------------------------------------------------
       POPUP / POPOVER
    --------------------------------------------------------- */
    .stPopover {
        border-radius: var(--radius) !important;
        border: 1px solid var(--glass-border) !important;
        background: var(--glass-bg) !important;
        backdrop-filter: blur(16px) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# AUTH STYLES
# -------------------------------------------------------------
def inject_auth_css():
    st.markdown("""
    <style>
    .auth-container {
        max-width: 420px;
        margin: 60px auto;
        padding: 40px 36px;
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 188, 212, 0.15);
    }

    .auth-logo {
        text-align: center;
        margin-bottom: 24px;
    }

    .auth-logo-icon {
        font-size: 3.5rem;
        filter: drop-shadow(0 4px 8px rgba(0, 188, 212, 0.3));
    }

    .auth-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 900;
        color: var(--primary-dark);
        margin-bottom: 4px;
    }

    .auth-subtitle {
        text-align: center;
        font-size: 0.9rem;
        color: var(--text-muted);
        margin-bottom: 28px;
    }

    .auth-divider {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        margin: 20px 0;
        position: relative;
    }

    .auth-divider::before,
    .auth-divider::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 40%;
        height: 1px;
        background: linear-gradient(90deg, transparent, #CBD5E1, transparent);
    }

    .auth-divider::before { left: 0; }
    .auth-divider::after { right: 0; }

    .auth-link {
        text-align: center;
        margin-top: 20px;
        font-size: 0.9rem;
        color: var(--text-muted);
    }

    .auth-link a {
        color: var(--primary);
        font-weight: 700;
        text-decoration: none;
    }

    .auth-link a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# BADGES
# -------------------------------------------------------------
def badge_paciente(paciente):
    return f'<span class="badge badge-persona">{_sanitize(paciente)}</span>'


def badge_estado_cita(fecha_str):
    texto, clase = CitaModel.estado_visual(fecha_str)
    if not texto:
        return ""
    return f'<span class="badge {clase}">{_sanitize(texto)}</span>'


# -------------------------------------------------------------
# EMPTY STATE
# -------------------------------------------------------------
def render_empty_state(icon, title, description):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{_sanitize(icon)}</div>
        <div class="empty-state-title">{_sanitize(title)}</div>
        <div class="empty-state-desc">{_sanitize(description)}</div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# SKELETON LOADER
# -------------------------------------------------------------
def render_skeleton(rows=3):
    for _ in range(rows):
        st.markdown("""
        <div class="glass-card-sm" style="margin-bottom:12px;">
            <div class="skeleton" style="height:16px;width:60%;margin-bottom:10px;"></div>
            <div class="skeleton" style="height:12px;width:80%;margin-bottom:8px;"></div>
            <div class="skeleton" style="height:12px;width:40%;"></div>
        </div>
        """, unsafe_allow_html=True)


# -------------------------------------------------------------
# KPIs
# -------------------------------------------------------------
def render_kpis(total_citas_programadas, proxima_cita, total_servicios):
    proxima_txt = "Sin citas"
    proxima_sub = "Programa la primera cita"
    if proxima_cita is not None:
        proxima_txt = f"{_sanitize(proxima_cita.get('fecha'))}"
        proxima_sub = f"{_sanitize(proxima_cita.get('paciente'))} · {_sanitize(proxima_cita.get('hora', ''))}"

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📅</div>
            <div class="kpi-label">Citas Próximas</div>
            <div class="kpi-value">{total_citas_programadas}</div>
            <div class="kpi-sub">pendientes por realizar</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">⏰</div>
            <div class="kpi-label">Próxima Cita</div>
            <div class="kpi-value" style="font-size:1.2rem;">{proxima_txt}</div>
            <div class="kpi-sub">{proxima_sub}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">💡</div>
            <div class="kpi-label">Servicios</div>
            <div class="kpi-value">{total_servicios}</div>
            <div class="kpi-sub">códigos guardados</div>
        </div>""", unsafe_allow_html=True)


# -------------------------------------------------------------
# TARJETA DE CITA
# -------------------------------------------------------------
def render_appt_card(cita):
    st.markdown(f"""
    <div class="appt-card">
        <div>
            {badge_paciente(cita.get('paciente'))}{badge_estado_cita(cita.get('fecha'))}
            <div class="appt-title">{_sanitize(cita.get('especialidad'))}</div>
            <div class="appt-meta">🏥 {_sanitize(cita.get('lugar'))} · 📆 {_sanitize(cita.get('fecha'))} {_sanitize(cita.get('hora', ''))}</div>
        </div>
    </div>""", unsafe_allow_html=True)


# -------------------------------------------------------------
# TARJETA DE SERVICIO
# -------------------------------------------------------------
def render_service_info(servicio):
    icono = ServicioModel.icono(servicio.get("tipo"))
    codigo = servicio.get("codigo", "—")
    safe_codigo = _sanitize(codigo).replace("'", "\\'").replace('"', '&quot;')
    st.markdown(f"""
    <div class="service-card">
        <div style="display:flex; align-items:center; gap:14px;">
            <div class="service-icon">{_sanitize(icono)}</div>
            <div style="flex:1;">
                <div class="service-title">{_sanitize(servicio.get('empresa', 'Sin empresa'))}</div>
                <div class="service-sub">{_sanitize(servicio.get('tipo'))} · Titular: {_sanitize(servicio.get('titular', 'No especificado'))}</div>
            </div>
        </div>
        <div class="service-code" onclick="navigator.clipboard.writeText('{safe_codigo}')">
            💳 {safe_codigo}
        </div>
        <div class="service-sub" style="text-align:right; font-size:0.75rem;">
            Registrado por {_sanitize(servicio.get('registrado_por', '—'))}
        </div>
    </div>""", unsafe_allow_html=True)


# -------------------------------------------------------------
# USER INFO CARD (sidebar)
# -------------------------------------------------------------
def render_user_info(nombre, familia_nombre, rol):
    iniciales = "".join([n[0].upper() for n in nombre.split()[:2]]) if nombre else "?"
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
        <div class="user-avatar">{_sanitize(iniciales)}</div>
        <div>
            <div style="font-weight:800; font-size:1rem;">{_sanitize(nombre)}</div>
            <div class="family-badge">{_sanitize(familia_nombre)} · {_sanitize(rol.title())}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------------------
# SECTION HEADER
# -------------------------------------------------------------
def render_section_header(icon, title, description=""):
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:1.5rem;">{_sanitize(icon)}</span>
            <h2 style="margin:0; font-size:1.4rem; font-weight:900;">{_sanitize(title)}</h2>
        </div>
        {'<p style="color:var(--text-muted); font-size:0.9rem; margin:0;">' + _sanitize(description) + '</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)
