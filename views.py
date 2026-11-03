"""
VIEW
----
Presentación visual con Glassmorphism y paleta turquesa iFamily.
CSS, tarjetas, badges, empty states, skeletons.
"""

import streamlit as st
from datetime import date, datetime, timedelta

from models import CitaModel, ServicioModel, MedicinaModel, _sanitize


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

    .badge-emergencia {
        background: rgba(239, 68, 68, 0.18);
        color: #B91C1C;
        border-color: rgba(239, 68, 68, 0.4);
        font-weight: 800;
        animation: pulse-badge 1.5s infinite;
    }

    .badge-realizada {
        background: rgba(16, 185, 129, 0.15);
        color: #047857;
        border-color: rgba(16, 185, 129, 0.3);
        font-weight: 700;
    }

    .badge-pendiente {
        background: rgba(245, 158, 11, 0.15);
        color: #B45309;
        border-color: rgba(245, 158, 11, 0.3);
        font-weight: 700;
    }

    .badge-agotada {
        background: rgba(239, 68, 68, 0.15);
        color: #DC2626;
        border-color: rgba(239, 68, 68, 0.3);
        font-weight: 700;
        animation: pulse-badge 1.5s infinite;
    }

    .badge-soon {
        background: rgba(249, 115, 22, 0.15);
        color: #C2410C;
        border-color: rgba(249, 115, 22, 0.3);
        font-weight: 700;
    }

    .badge-disponible {
        background: rgba(16, 185, 129, 0.15);
        color: #047857;
        border-color: rgba(16, 185, 129, 0.3);
        font-weight: 700;
    }

    .badge-continuo {
        background: rgba(59, 130, 246, 0.15);
        color: #1D4ED8;
        border-color: rgba(59, 130, 246, 0.3);
        font-weight: 700;
    }

    /* Banners de estado de cita (color característico) */
    .estado-banner {
        padding: 8px 14px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.85rem;
        margin-bottom: 12px;
    }
    .estado-banner.estado-realizada {
        background: rgba(16, 185, 129, 0.15);
        color: #047857;
        border-left: 5px solid #10B981;
    }
    .estado-banner.estado-pendiente {
        background: rgba(245, 158, 11, 0.15);
        color: #B45309;
        border-left: 5px solid #F59E0B;
    }
    .estado-banner.estado-emergencia {
        background: rgba(239, 68, 68, 0.15);
        color: #B91C1C;
        border-left: 5px solid #EF4444;
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

    /* ---------------------------------------------------------
       ALERTAS
    --------------------------------------------------------- */
    .alerta-panel {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(245,158,11,0.3);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    }
    .alerta-header {
        display: flex; align-items: center; gap: 10px;
        font-weight: 800; font-size: 1.05rem;
        margin-bottom: 10px;
    }
    .alerta-item {
        display: flex; align-items: flex-start;
        padding: 8px 0;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }
    .alerta-item:last-child { border-bottom: none; }
    .alerta-titulo { font-weight: 700; color: #1F2937; font-size: 0.92rem; }
    .alerta-detalle { color: #6B7280; font-size: 0.84rem; }

    /* ---------------------------------------------------------
       HOME: CUADRÍCULA DE ACCESOS
    --------------------------------------------------------- */
    .home-grid-title {
        display: flex; align-items: center; gap: 10px;
        font-size: 1.15rem; font-weight: 900;
        margin: 8px 0 2px 0;
    }
    .home-grid-sub {
        color: var(--text-muted);
        font-size: 0.85rem;
        margin: 0 0 12px 0;
    }

    /* Tarjeta = wrapper interno que contiene directamente el contenido .tile.
       Streamlit 1.45 anida un wrapper extra por columna; ese se neutraliza
       más abajo para que no se vea un doble borde. */
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile) {
        position: relative !important;
        overflow: hidden !important;
        border-radius: 16px !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        background: rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05) !important;
        -webkit-tap-highlight-color: transparent;
        transition: transform 0.14s ease, box-shadow 0.14s ease,
                    border-color 0.14s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile) > [data-testid="stVerticalBlock"] {
        position: static !important;
        height: 100%;
        padding: 0 !important;
    }
    /* El botón real se estira sobre toda la tarjeta y queda transparente:
       se puede pulsar en el icono, el título, el texto o el espacio libre. */
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile) [data-testid="stElementContainer"]:has(> [data-testid="stButton"]) {
        position: absolute !important;
        inset: 0 !important;
        z-index: 4;
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile) [data-testid="stButton"],
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile) [data-testid="stButton"] > button {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile) [data-testid="stButton"] > button {
        opacity: 0 !important;
        border: 0 !important;
        background: transparent !important;
        cursor: pointer;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile):hover {
        transform: translateY(-2px);
        border-color: rgba(0, 188, 212, 0.55) !important;
        box-shadow: 0 8px 20px rgba(0, 188, 212, 0.15) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile):has([data-testid="stButton"] > button:active) {
        transform: scale(0.985);
        box-shadow: 0 2px 6px rgba(0, 188, 212, 0.12) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile):has([data-testid="stButton"] > button:focus-visible) {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.35) !important;
    }
    /* Wrapper externo que anida Streamlit: sin borde ni sombra. */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.tile):has(> [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]) {
        border: 0 !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        transform: none !important;
    }
    .tile {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        text-align: center;
        height: 100%;
        padding: 14px 8px 6px 8px;
    }
    .tile-icon {
        font-size: 2.35rem;
        line-height: 1;
        margin-bottom: 5px;
        transition: transform 0.14s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(> [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] .tile):hover .tile-icon {
        transform: scale(1.08);
    }
    .tile-title {
        font-size: 1rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .tile-desc {
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: 2px;
        min-height: 32px;
    }
    .tile-badge {
        display: inline-block;
        margin-top: 6px;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 800;
        background: rgba(0, 188, 212, 0.1);
        color: #00838F;
        border: 1px solid rgba(0, 188, 212, 0.22);
    }

    /* Móvil: misma cuadrícula de 2 columnas y tarjetas compactas. */
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.tile) {
            flex-wrap: nowrap !important;
            gap: 0.55rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.tile) > [data-testid="stColumn"] {
            width: 50% !important;
            flex: 1 1 50% !important;
            min-width: 0 !important;
        }
        .tile { padding: 12px 4px 4px 4px; }
        .tile-icon { font-size: 2rem; }
        .tile-title { font-size: 0.9rem; }
        .tile-desc { font-size: 0.72rem; min-height: 30px; }
        .tile-badge { font-size: 0.66rem; padding: 2px 7px; }
        .home-grid-title { font-size: 1.02rem; }
        .home-grid-sub { font-size: 0.78rem; margin-bottom: 8px; }
    }

    /* ---------------------------------------------------------
       PANTALLAS INTERNAS: JERARQUÍA Y LEGIBILIDAD
    --------------------------------------------------------- */
    /* Textos de apoyo y etiquetas con contraste suficiente. */
    [data-testid="stCaptionContainer"] p {
        color: #64748B !important;
        font-size: 0.8rem !important;
        line-height: 1.45 !important;
    }
    [data-testid="stWidgetLabel"] p {
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 0.84rem !important;
        letter-spacing: 0.01em;
    }
    /* El texto de los botones hereda su color (evita texto oscuro sobre
       el degradado turquesa). */
    .stButton > button p, .stButton > button div, .stButton > button span,
    .stFormSubmitButton > button p, .stFormSubmitButton > button div,
    .stFormSubmitButton > button span,
    [data-testid="stPopover"] > button p, [data-testid="stPopover"] > button div,
    [data-testid="stPopover"] > button span,
    [data-testid="stPopoverButton"] p, [data-testid="stPopoverButton"] div,
    [data-testid="stPopoverButton"] span {
        color: inherit !important;
    }
    .stButton > button:focus-visible,
    .stFormSubmitButton > button:focus-visible,
    [data-testid="stPopover"] > button:focus-visible,
    [data-testid="stPopoverButton"]:focus-visible {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.35),
                    0 6px 18px rgba(0, 188, 212, 0.22) !important;
    }
    /* "Volver" como acción secundaria: no compite con el botón principal. */
    [class*="st-key-btn_volver_home"] button {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #334155 !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
        font-weight: 700 !important;
    }
    [class*="st-key-btn_volver_home"] button:hover {
        background: #FFFFFF !important;
        border-color: rgba(0, 188, 212, 0.55) !important;
        color: #00838F !important;
        box-shadow: 0 6px 16px rgba(0, 188, 212, 0.15) !important;
    }
    /* Eliminar: rojo suave en reposo, relleno al pasar el cursor. */
    [class*="st-key-del_"] button {
        background: rgba(239, 68, 68, 0.07) !important;
        color: #DC2626 !important;
        border: 1px solid rgba(239, 68, 68, 0.22) !important;
        box-shadow: none !important;
        min-height: 42px !important;
    }
    [class*="st-key-del_"] button:hover {
        background: rgba(239, 68, 68, 0.14) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
        color: #B91C1C !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.18) !important;
    }
    /* Botón principal de la pantalla (abre el formulario). */
    [data-testid="stPopover"] > button,
    [data-testid="stPopoverButton"] {
        min-height: 46px !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em;
    }
    /* Los popovers son la acción principal de cada pantalla: botón sólido. */
    [data-testid="stPopoverButton"] {
        color: #FFFFFF !important;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        border: 0 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(0, 188, 212, 0.28) !important;
    }
    [data-testid="stPopoverButton"]:hover {
        background: linear-gradient(135deg, var(--primary-dark), var(--primary-deeper)) !important;
        box-shadow: 0 8px 22px rgba(0, 188, 212, 0.34) !important;
        transform: translateY(-1px);
    }

    /* Cabecera de sección: banda con icono y acento de color. */
    .section-hero {
        --hero-a: #00BCD4;
        --hero-b: #00838F;
        --hero-soft: rgba(0, 188, 212, 0.09);
        --hero-line: rgba(0, 188, 212, 0.2);
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 16px 20px;
        margin: 4px 0 18px 0;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), var(--hero-soft));
        border: 1px solid var(--hero-line);
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.05);
    }
    .section-hero.tone-red {
        --hero-a: #F87171; --hero-b: #DC2626;
        --hero-soft: rgba(239, 68, 68, 0.08); --hero-line: rgba(239, 68, 68, 0.2);
    }
    .section-hero.tone-indigo {
        --hero-a: #818CF8; --hero-b: #4F46E5;
        --hero-soft: rgba(99, 102, 241, 0.08); --hero-line: rgba(99, 102, 241, 0.2);
    }
    .section-hero.tone-green {
        --hero-a: #34D399; --hero-b: #059669;
        --hero-soft: rgba(16, 185, 129, 0.08); --hero-line: rgba(16, 185, 129, 0.2);
    }
    .section-hero.tone-amber {
        --hero-a: #FBBF24; --hero-b: #D97706;
        --hero-soft: rgba(245, 158, 11, 0.09); --hero-line: rgba(245, 158, 11, 0.22);
    }
    .section-hero.tone-violet {
        --hero-a: #A78BFA; --hero-b: #7C3AED;
        --hero-soft: rgba(139, 92, 246, 0.08); --hero-line: rgba(139, 92, 246, 0.2);
    }
    .section-hero.tone-blue {
        --hero-a: #60A5FA; --hero-b: #2563EB;
        --hero-soft: rgba(59, 130, 246, 0.08); --hero-line: rgba(59, 130, 246, 0.2);
    }
    .section-hero-icon {
        flex: 0 0 auto;
        width: 46px;
        height: 46px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        color: #FFFFFF;
        background: linear-gradient(135deg, var(--hero-a), var(--hero-b));
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.14);
    }
    .section-hero-text { min-width: 0; }
    .section-hero-title {
        font-size: 1.16rem;
        font-weight: 900;
        color: #0F172A;
        line-height: 1.25;
        letter-spacing: -0.02em;
    }
    .section-hero-desc {
        margin-top: 3px;
        color: #64748B;
        font-size: 0.84rem;
        line-height: 1.45;
    }
    .section-hero.compact {
        padding: 11px 13px;
        gap: 11px;
        margin-bottom: 14px;
        border-radius: 13px;
    }
    .section-hero.compact .section-hero-icon {
        width: 37px; height: 37px; border-radius: 11px; font-size: 1.05rem;
    }
    .section-hero.compact .section-hero-title { font-size: 1rem; }

    /* Chips de resumen: conteos rápidos y escaneables. */
    .stat-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 2px 0 14px 0;
    }
    .stat-chip {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        font-size: 0.78rem;
        font-weight: 700;
        color: #475569;
    }
    .stat-chip b { font-size: 0.92rem; font-weight: 900; color: #0F172A; }
    .stat-chip .stat-icon { font-size: 0.9rem; line-height: 1; }
    .stat-chip.tone-teal {
        background: rgba(0, 188, 212, 0.09);
        border-color: rgba(0, 188, 212, 0.25);
        color: #00838F;
    }
    .stat-chip.tone-teal b { color: #00838F; }
    .stat-chip.tone-amber {
        background: rgba(245, 158, 11, 0.1);
        border-color: rgba(245, 158, 11, 0.25);
        color: #B45309;
    }
    .stat-chip.tone-amber b { color: #B45309; }
    .stat-chip.tone-green {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.25);
        color: #047857;
    }
    .stat-chip.tone-green b { color: #047857; }
    .stat-chip.tone-red {
        background: rgba(239, 68, 68, 0.1);
        border-color: rgba(239, 68, 68, 0.25);
        color: #B91C1C;
    }
    .stat-chip.tone-red b { color: #B91C1C; }
    .stat-chip.tone-indigo {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.25);
        color: #4338CA;
    }
    .stat-chip.tone-indigo b { color: #4338CA; }

    /* Ficha de datos dentro de cada registro. */
    .info-card {
        background: rgba(248, 250, 252, 0.85);
        border: 1px solid rgba(15, 23, 42, 0.06);
        border-radius: 12px;
        padding: 4px 14px;
        margin: 10px 0 12px 0;
    }
    .info-row {
        display: grid;
        grid-template-columns: 148px 1fr;
        gap: 2px 14px;
        padding: 8px 0;
        border-bottom: 1px dashed rgba(15, 23, 42, 0.07);
    }
    .info-row:last-child { border-bottom: 0; }
    .info-label {
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #64748B;
        padding-top: 3px;
    }
    .info-value {
        font-size: 0.9rem;
        color: #1E293B;
        line-height: 1.55;
        word-break: break-word;
    }

    /* Tarjetas de personas / usuarios. */
    .entity-card {
        display: flex;
        align-items: center;
        gap: 13px;
        padding: 13px 16px;
        margin-bottom: 10px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        transition: border-color 0.18s ease, box-shadow 0.18s ease,
                    transform 0.18s ease;
    }
    .entity-card:hover {
        border-color: rgba(0, 188, 212, 0.45);
        box-shadow: 0 8px 20px rgba(0, 188, 212, 0.1);
        transform: translateY(-1px);
    }
    .entity-avatar {
        flex: 0 0 auto;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        font-weight: 800;
        color: #FFFFFF;
        background: linear-gradient(135deg, var(--primary), var(--primary-deeper));
        box-shadow: 0 4px 12px rgba(0, 188, 212, 0.25);
    }
    .entity-body { min-width: 0; }
    .entity-title {
        font-weight: 800;
        font-size: 0.97rem;
        color: #0F172A;
        line-height: 1.3;
        word-break: break-word;
    }
    .entity-sub {
        color: #64748B;
        font-size: 0.79rem;
        margin-top: 2px;
        word-break: break-word;
    }
    .entity-tag {
        display: inline-block;
        margin-left: 6px;
        padding: 2px 8px;
        border-radius: 999px;
        background: rgba(0, 188, 212, 0.1);
        border: 1px solid rgba(0, 188, 212, 0.22);
        color: #00838F;
        font-size: 0.66rem;
        font-weight: 800;
        vertical-align: middle;
        letter-spacing: 0.02em;
    }

    /* Encabezados de bloques pequeños (medicinas por persona, etc.). */
    .mini-title {
        font-weight: 800;
        font-size: 0.95rem;
        color: #0F172A;
        margin: 2px 0 4px 0;
        line-height: 1.35;
    }
    .mini-sub {
        color: #64748B;
        font-size: 0.78rem;
        margin-bottom: 2px;
    }

    /* Tarjeta del código de invitación familiar. */
    .invite-card {
        background: linear-gradient(135deg, rgba(0, 188, 212, 0.12), rgba(255, 255, 255, 0.9));
        border: 1px dashed rgba(0, 188, 212, 0.45);
        border-radius: 16px;
        padding: 18px 16px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0, 188, 212, 0.08);
    }
    .invite-label {
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        color: #00838F;
    }
    .invite-code {
        margin: 8px 0 6px 0;
        font-family: 'Fira Code', ui-monospace, monospace;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        color: #006064;
        word-break: break-all;
    }
    .invite-hint {
        font-size: 0.74rem;
        color: #64748B;
        line-height: 1.4;
    }

    /* Tarjetas de servicios: código destacado y copiable. */
    .service-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }
    .service-card:hover {
        border-color: rgba(0, 188, 212, 0.45);
        box-shadow: 0 10px 24px rgba(0, 188, 212, 0.12);
    }
    .service-code {
        color: #006064;
        background: rgba(0, 188, 212, 0.07);
        border-color: rgba(0, 188, 212, 0.35);
    }
    .service-code::after {
        content: 'Toca para copiar';
        display: block;
        margin-top: 2px;
        font-family: 'Inter', sans-serif;
        font-size: 0.64rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #64748B;
    }

    /* Registros plegables (citas, emergencias, medicinas...). */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
        margin-bottom: 10px;
        overflow: hidden;
        transition: border-color 0.18s ease, box-shadow 0.18s ease;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(0, 188, 212, 0.4) !important;
        box-shadow: 0 8px 22px rgba(0, 188, 212, 0.1) !important;
    }
    [data-testid="stExpander"] details {
        border: 0 !important;
        background: transparent !important;
    }
    [data-testid="stExpander"] summary {
        padding: 13px 16px !important;
        background: transparent !important;
        transition: background 0.18s ease;
    }
    [data-testid="stExpander"] summary:hover {
        background: rgba(0, 188, 212, 0.05) !important;
    }
    [data-testid="stExpander"] summary p {
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        color: #0F172A !important;
        line-height: 1.4 !important;
    }
    [data-testid="stExpander"] summary svg { color: #00838F !important; }
    [data-testid="stExpander"] details[open] {
        box-shadow: inset 4px 0 0 rgba(0, 188, 212, 0.35);
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 2px 16px 14px 16px !important;
        background: transparent !important;
    }

    /* Formularios: contenedor suave y coherente con las tarjetas. */
    [data-testid="stForm"] {
        border: 1px solid rgba(0, 188, 212, 0.18);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.72);
    }
    [data-testid="stPopoverBody"] {
        border: 1px solid rgba(0, 188, 212, 0.2) !important;
        border-radius: 16px !important;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.18) !important;
    }

    /* Filtros tipo píldora: texto blanco legible en la opción activa. */
    div[role="radiogroup"] label {
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }
    div[role="radiogroup"] label:hover {
        box-shadow: 0 4px 12px rgba(0, 188, 212, 0.12);
    }
    div[role="radiogroup"] label[data-checked="true"] div,
    div[role="radiogroup"] label[data-checked="true"] p,
    div[role="radiogroup"] label:has(input:checked) div,
    div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
    }

    @media (max-width: 640px) {
        .section-hero {
            padding: 12px 14px;
            gap: 11px;
            margin-bottom: 14px;
            border-radius: 14px;
        }
        .section-hero-icon {
            width: 38px; height: 38px; border-radius: 12px; font-size: 1.1rem;
        }
        .section-hero-title { font-size: 1.02rem; }
        .section-hero-desc { font-size: 0.76rem; }
        .info-row { grid-template-columns: 1fr; gap: 1px; padding: 7px 0; }
        .info-label { padding-top: 0; }
        .info-value { font-size: 0.86rem; }
        .stat-chip { font-size: 0.72rem; padding: 5px 10px; }
        .entity-card { padding: 11px 12px; gap: 10px; }
        .entity-avatar { width: 38px; height: 38px; font-size: 0.85rem; }
        .entity-title { font-size: 0.9rem; }
        .invite-code { font-size: 1.25rem; }
        [data-testid="stExpander"] summary { padding: 11px 12px !important; }
        [data-testid="stExpander"] summary p { font-size: 0.86rem !important; }
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            padding: 2px 12px 12px 12px !important;
        }
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


def badge_emergencia(paciente):
    return f'<span class="badge badge-emergencia">🚨 {_sanitize(paciente)}</span>'


def badge_cita_realizada(paciente):
    return f'<span class="badge badge-realizada">✅ {_sanitize(paciente)}</span>'


def badge_cita_pendiente(paciente):
    return f'<span class="badge badge-pendiente">⏳ {_sanitize(paciente)}</span>'


def badge_medicina_estado(fecha_recojo, dias, paciente, tipo="temporal"):
    texto, clase = MedicinaModel.estado_visual(fecha_recojo, dias, tipo)
    if not texto:
        return ""
    return (f'<span class="badge badge-persona">{_sanitize(paciente)}</span>'
            f'<span class="badge {clase}">💊 {texto}</span>')


def cita_estado_tipo(cita):
    """Devuelve 'emergencia', 'realizada' o 'pendiente' según la cita."""
    if cita.get("es_emergencia"):
        return "emergencia"
    if cita.get("estado") == "realizada":
        return "realizada"
    return "pendiente"


def cita_estado_banner(cita):
    """Banner de color que diferencia visualmente el estado de una cita."""
    tipo = cita_estado_tipo(cita)
    etiquetas = {
        "realizada": ("✅ Cita realizada", "estado-realizada"),
        "pendiente": ("⏳ Cita pendiente", "estado-pendiente"),
        "emergencia": ("🚨 Emergencia", "estado-emergencia"),
    }
    texto, clase = etiquetas[tipo]
    return f'<div class="estado-banner {clase}">{texto}</div>'


def cita_estado_emoji(cita):
    return {"realizada": "✅", "pendiente": "⏳", "emergencia": "🚨"}[cita_estado_tipo(cita)]


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
def render_kpis(total_citas_programadas, proxima_cita, total_servicios, total_emergencias=0, medicinas_por_agotar=0):
    proxima_txt = "Sin citas"
    proxima_sub = "Programa la primera cita"
    if proxima_cita is not None:
        proxima_txt = f"{_sanitize(proxima_cita.get('fecha'))}"
        proxima_sub = f"{_sanitize(proxima_cita.get('paciente'))} · {_sanitize(proxima_cita.get('hora', ''))}"

    k1, k2, k3, k4, k5 = st.columns(5)
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
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🚨</div>
            <div class="kpi-label">Emergencias</div>
            <div class="kpi-value">{total_emergencias}</div>
            <div class="kpi-sub">registradas</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        sub_med = "por agotar" if medicinas_por_agotar else "todo en orden"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">💊</div>
            <div class="kpi-label">Medicinas</div>
            <div class="kpi-value">{medicinas_por_agotar}</div>
            <div class="kpi-sub">{sub_med}</div>
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
_TONOS_SECCION = {"teal", "red", "indigo", "green", "amber", "violet", "blue"}


def render_section_header(icon, title, description="", tone="teal", compact=False):
    """Cabecera de sección con acento de color.

    `tone` diferencia visualmente cada área (citas, emergencias, medicinas...)
    y `compact` se usa dentro de los formularios para no ocupar tanto alto.
    """
    tone = tone if tone in _TONOS_SECCION else "teal"
    clase = "section-hero compact" if compact else "section-hero"
    desc = (f'<div class="section-hero-desc">{_sanitize(description)}</div>'
            if description else "")
    st.markdown(
        f'<div class="{clase} tone-{tone}">'
        f'<div class="section-hero-icon">{_sanitize(icon)}</div>'
        f'<div class="section-hero-text">'
        f'<div class="section-hero-title">{_sanitize(title)}</div>'
        f'{desc}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def render_stat_strip(items):
    """Fila de chips con conteos: [{value, label, tone?, icon?}, ...]."""
    chips = []
    for item in items:
        label = item.get("label", "")
        if not label:
            continue
        tone = item.get("tone", "")
        tone_cls = f" tone-{tone}" if tone else ""
        icono = item.get("icon", "")
        icon_html = (f'<span class="stat-icon">{_sanitize(icono)}</span>'
                     if icono else "")
        valor = item.get("value", 0)
        valor_txt = "0" if valor in (0, None) else str(valor)
        chips.append(
            f'<span class="stat-chip{tone_cls}">{icon_html}'
            f'<b>{_sanitize(valor_txt)}</b> {_sanitize(label)}</span>'
        )
    if chips:
        st.markdown('<div class="stat-strip">' + "".join(chips) + '</div>',
                    unsafe_allow_html=True)


def render_info_rows(rows):
    """Ficha de datos legible: filas (icono, etiqueta, valor).

    Omite los valores vacíos para no dejar campos en blanco.
    """
    filas = []
    for icono, etiqueta, valor in rows:
        if valor is None:
            continue
        texto = str(valor).strip()
        if not texto or texto in {"—", "-"}:
            continue
        icon_html = f"{_sanitize(icono)} " if icono else ""
        filas.append(
            f'<div class="info-row">'
            f'<div class="info-label">{icon_html}{_sanitize(etiqueta)}</div>'
            f'<div class="info-value">{_sanitize(texto)}</div>'
            f'</div>'
        )
    if filas:
        st.markdown('<div class="info-card">' + "".join(filas) + '</div>',
                    unsafe_allow_html=True)


def render_entity_card(iniciales, nombre, subtitulo="", tag=""):
    """Tarjeta de persona o usuario con avatar, nombre y detalle."""
    tag_html = (f'<span class="entity-tag">{_sanitize(tag)}</span>'
                if tag else "")
    sub = (f'<div class="entity-sub">{_sanitize(subtitulo)}</div>'
           if subtitulo else "")
    st.markdown(
        f'<div class="entity-card">'
        f'<div class="entity-avatar">{_sanitize(iniciales)}</div>'
        f'<div class="entity-body">'
        f'<div class="entity-title">{_sanitize(nombre)}{tag_html}</div>'
        f'{sub}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def render_mini_header(title, subtitle=""):
    """Título pequeño para bloques dentro de un registro."""
    sub = f'<div class="mini-sub">{_sanitize(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="mini-title">{_sanitize(title)}</div>{sub}',
                unsafe_allow_html=True)


def render_invite_card(codigo):
    """Tarjeta destacada con el código de invitación de la familia."""
    st.markdown(
        f'<div class="invite-card">'
        f'<div class="invite-label">Código de invitación</div>'
        f'<div class="invite-code">{_sanitize(codigo)}</div>'
        f'<div class="invite-hint">Compártelo para que otros se unan a tu familia</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# -------------------------------------------------------------
# HOME: TARJETA DE ACCESO (cuadrícula)
# -------------------------------------------------------------
def render_seccion_tile(icono, titulo, descripcion, key, badge=""):
    """Tarjeta de acceso de la cuadrícula del inicio.

    Toda la tarjeta es clicable: el botón real se estira sobre ella y queda
    transparente (ver CSS de `.home-grid`). Devuelve True si se pulsó.
    """
    badge_html = f'<div class="tile-badge">{_sanitize(badge)}</div>' if badge else ""
    with st.container(border=True):
        st.markdown(
            f'<div class="tile">'
            f'<div class="tile-icon">{icono}</div>'
            f'<div class="tile-title">{_sanitize(titulo)}</div>'
            f'<div class="tile-desc">{_sanitize(descripcion)}</div>'
            f'{badge_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
        return st.button(
            f"Abrir {titulo}",
            key=f"tile_{key}",
            use_container_width=True,
        )


# -------------------------------------------------------------
# ALERTAS
# -------------------------------------------------------------
def obtener_alertas(cita_model, persona_model, medicina_model=None, citas=None,
                    medicinas_proximas=None):
    """Calcula alertas de seguimiento: citas próximas, emergencias, citas atrasadas, medicinas por agotar.

    Permite reutilizar datos ya leídos (`citas`, `medicinas_proximas`) para no
    repetir consultas a Firebase en cada render.
    """
    alertas = []
    hoy = date.today()
    citas = citas if citas is not None else cita_model.get_all()

    for key, cita in citas.items():
        estado = cita.get("estado", "programada")
        es_emergencia = cita.get("es_emergencia", False)

        try:
            f = datetime.strptime(cita.get("fecha", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        dias = (f - hoy).days

        if es_emergencia and dias >= -15:
            alertas.append({
                "tipo": "emergencia",
                "titulo": "🚨 Emergencia registrada",
                "detalle": f"{cita.get('paciente')} — {cita.get('motivo_emergencia', 'Emergencia')} ({cita.get('fecha')})",
                "prioridad": "alta",
            })
        elif estado == "programada" and dias == 0:
            alertas.append({
                "tipo": "hoy",
                "titulo": f"📅 Cita HOY",
                "detalle": f"{cita.get('paciente')} — {cita.get('especialidad')} ({cita.get('hora', '-')})",
                "prioridad": "alta",
            })
        elif estado == "programada" and dias == 1:
            alertas.append({
                "tipo": "manana",
                "titulo": f"📅 Cita mañana",
                "detalle": f"{cita.get('paciente')} — {cita.get('especialidad')} ({cita.get('fecha')})",
                "prioridad": "media",
            })
        elif estado == "programada" and 2 <= dias <= 7:
            alertas.append({
                "tipo": "semana",
                "titulo": f"📅 Cita esta semana",
                "detalle": f"{cita.get('paciente')} — {cita.get('especialidad')} ({cita.get('fecha')})",
                "prioridad": "media",
            })
        elif estado == "programada" and dias < 0:
            alertas.append({
                "tipo": "atrasada",
                "titulo": f"⏰ Cita atrasada",
                "detalle": f"{cita.get('paciente')} — {cita.get('especialidad')} ({cita.get('fecha')}) — marcarla como realizada",
                "prioridad": "alta",
            })

    if medicina_model is not None:
        proximas = (medicinas_proximas if medicinas_proximas is not None
                    else medicina_model.get_proximas_a_agotar(3))
        for key, med in proximas.items():
            dias_rest = MedicinaModel.dias_restantes(med.get("fecha_recojo"), med.get("dias"))
            if dias_rest is not None and dias_rest < 0:
                detalle = f"{med.get('medicamento')} — {med.get('paciente')} — se agotó hace {abs(dias_rest)} día(s)"
            elif dias_rest == 0:
                detalle = f"{med.get('medicamento')} — {med.get('paciente')} — se agota hoy"
            else:
                detalle = f"{med.get('medicamento')} — {med.get('paciente')} — quedan {dias_rest} día(s)"
            alertas.append({
                "tipo": "medicina",
                "titulo": "💊 Medicina por agotar",
                "detalle": detalle,
                "prioridad": "alta" if dias_rest <= 0 else "media",
            })

    def _prioridad(val):
        return {"alta": 0, "media": 1, "baja": 2}.get(val, 2)

    alertas.sort(key=lambda a: _prioridad(a.get("prioridad")))
    return alertas


def render_alerta_panel(alertas):
    total = len(alertas)
    urgentes = sum(1 for a in alertas if a.get("prioridad") == "alta")
    color = "#DC2626" if urgentes else "#D97706"

    # Importante: el HTML se genera sin indentación ni líneas en blanco.
    # Si se indenta con 4+ espacios, Markdown lo interpreta como bloque de
    # código y muestra las etiquetas crudas (alertas "rotas").
    cards = "".join(
        '<div class="alerta-item"><div>'
        f'<div class="alerta-titulo">{_sanitize(a["titulo"])}</div>'
        f'<div class="alerta-detalle">{_sanitize(a["detalle"])}</div>'
        "</div></div>"
        for a in alertas
    )
    urgentes_html = (
        f' — <span style="color:#DC2626;">{urgentes} urgente(s)</span>'
        if urgentes else ""
    )
    panel_html = (
        f'<div class="alerta-panel" style="border-left:5px solid {color};">'
        f'<div class="alerta-header" style="color:{color};">'
        f"🔔 Tienes {total} alerta(s){urgentes_html}"
        "</div>"
        f"{cards}"
        "</div>"
    )
    st.markdown(panel_html, unsafe_allow_html=True)


def inject_notificacion_script(alertas, proxima_cita=None):
    """Notificación del sistema (PWA) al abrir la app. Prioriza la cita más próxima."""
    import json
    import streamlit.components.v1 as components

    if proxima_cita:
        titular = "📅 Próxima cita"
        detalle = (
            f"{proxima_cita.get('paciente', '')} — {proxima_cita.get('especialidad', '')} · "
            f"{proxima_cita.get('fecha', '')} {proxima_cita.get('hora', '')}"
        ).strip()
    elif alertas:
        titular = alertas[0].get("titulo", "iFamily")
        detalle = alertas[0].get("detalle", "")
    else:
        return

    # json.dumps evita romper el JS con comillas o saltos de línea en los datos.
    titulo_js = json.dumps(f"iFamily · {titular}")
    detalle_js = json.dumps(detalle)

    script = f"""
    <script>
    (function() {{
        if ('Notification' in window && 'serviceWorker' in navigator) {{
            Notification.requestPermission().then(function(perm) {{
                if (perm === 'granted' && !sessionStorage.getItem('ifamily_notif')) {{
                    sessionStorage.setItem('ifamily_notif', '1');
                    setTimeout(function() {{
                        try {{
                            new Notification({titulo_js}, {{
                                body: {detalle_js},
                                icon: './icon-192.png',
                                tag: 'ifamily-cita'
                            }});
                        }} catch(e) {{}}
                    }}, 1200);
                }}
            }});
        }}
    }})();
    </script>
    """
    components.html(script, height=0, width=0)


@st.dialog("📅 Tu próxima cita")
def _dialog_proxima_cita(cita):
    """Contenido del pop-up con la cita más próxima."""
    estado_txt, estado_clase = CitaModel.estado_visual(cita.get("fecha"))
    st.markdown(
        f"<div style='font-size:1.1rem; font-weight:800; margin-bottom:8px;'>"
        f"{_sanitize(cita.get('paciente', '—'))} · {_sanitize(cita.get('especialidad', '—'))}</div>",
        unsafe_allow_html=True,
    )
    if estado_txt:
        st.markdown(
            f'<span class="badge {estado_clase}">{_sanitize(estado_txt)}</span>',
            unsafe_allow_html=True,
        )
    st.markdown(f"**🏥 Lugar:** {_sanitize(cita.get('lugar', '—'))}")
    st.markdown(f"**📆 Fecha:** {_sanitize(cita.get('fecha', '—'))}")
    if cita.get("hora"):
        st.markdown(f"**🕐 Hora:** {_sanitize(cita.get('hora'))}")
    if cita.get("notas"):
        st.markdown(f"**📝 Notas:** {_sanitize(cita.get('notas'))}")
    if st.button("👍 Entendido", use_container_width=True, key="dlg_proxima_cita_ok"):
        st.rerun()


def render_proxima_cita_popup(proxima_cita):
    """Pop-up con la cita más próxima al abrir la app (una vez por sesión)."""
    if not proxima_cita:
        return
    if st.session_state.get("_proxima_cita_popup_mostrado"):
        return
    st.session_state["_proxima_cita_popup_mostrado"] = True
    _dialog_proxima_cita(proxima_cita)
