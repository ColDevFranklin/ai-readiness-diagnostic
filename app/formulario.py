"""
Formulario de Diagnóstico AI Readiness - Aplicación Principal
Version: 5.5 PRODUCTION - Triple Defense Architecture
Autor: Andrés - AI Consultant

ARCHITECTURE:
- Layer 1: Compatibility Layer (init_session_state)
- Layer 2: UX Layer (collect_prospect_info with explicit placeholders)
- Layer 3: Validation Layer (process_diagnostic with defensive checks)

CHANGELOG v5.5:
- Implemented Triple Defense Pattern for state management
- Added explicit placeholder options in all selectboxes
- Enhanced validation with granular error reporting
- Comprehensive logging for observability
- Universal Streamlit compatibility (>= 1.12)
"""

import streamlit as st
import json
import re
from datetime import datetime
from pathlib import Path
import sys
import traceback

# Agregar path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from app.config import *
from core.models import ProspectInfo, DiagnosticResponses, DiagnosticResult
from core.scoring_engine import ScoringEngine
from core.classifier import ArchetypeClassifier, InsightGenerator
from integrations.sheets_connector import SheetsConnector
from integrations.pdf_generator import PDFGenerator
from integrations.email_sender import EmailSender

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Diagnóstico AI Readiness",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# SISTEMA DE DISEÑO PREMIUM PROFESIONAL
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --primary-light: #3b82f6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;

        --bg-dark: #0f172a;
        --bg-darker: #020617;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;

        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;

        --border: #334155;
        --border-light: #475569;

        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;

        --radius: 0.75rem;
        --radius-lg: 1rem;

        --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        background: linear-gradient(135deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        min-height: 100vh;
    }

    .block-container {
        max-width: 1200px;
        padding: var(--space-xl) var(--space-lg);
    }

    .hero-header {
        text-align: center;
        margin-bottom: var(--space-xl);
        padding: var(--space-lg) 0;
    }

    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: clamp(2rem, 4vw, 2.75rem);
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: var(--space-sm);
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    .main-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin-bottom: var(--space-lg);
        line-height: 1.5;
    }

    .trust-container {
        display: flex;
        justify-content: center;
        gap: var(--space-md);
        flex-wrap: wrap;
        margin-top: var(--space-lg);
    }

    .trust-badge {
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.2);
        padding: var(--space-sm) var(--space-md);
        border-radius: var(--radius);
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--text-secondary);
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        transition: all 0.2s ease;
    }

    .trust-badge:hover {
        background: rgba(37, 99, 235, 0.15);
        border-color: rgba(37, 99, 235, 0.3);
    }

    .progress-wrapper {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        margin-bottom: var(--space-xl);
    }

    .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-md);
    }

    .progress-step-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: 0.025em;
    }

    .progress-percentage {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--primary-light);
    }

    .stProgress > div > div {
        background: rgba(37, 99, 235, 0.2);
        border-radius: var(--radius);
        height: 6px;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
        border-radius: var(--radius);
        height: 6px;
    }

    .section-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        margin-bottom: var(--space-lg);
        box-shadow: var(--shadow-md);
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-lg);
        padding-bottom: var(--space-md);
        border-bottom: 1px solid var(--border);
    }

    .stTextInput label,
    .stSelectbox label,
    .stMultiSelect label {
        font-size: 0.8125rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: var(--space-sm) !important;
    }

    .stTextInput > div > div > input {
        background: var(--bg-darker) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
        font-size: 0.9375rem !important;
        padding: 0.625rem 0.875rem !important;
        transition: all 0.2s ease !important;
        height: 42px;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }

    .stTextInput > div > div > input:focus {
        background: var(--bg-dark) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }

    .stSelectbox [data-baseweb="select"] {
        background: var(--bg-darker) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        min-height: 42px !important;
    }

    .stSelectbox [data-baseweb="select"]:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        color: var(--text-primary) !important;
        font-size: 0.9375rem !important;
        padding: 0.375rem 0.875rem !important;
    }

    [data-baseweb="popover"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-lg) !important;
    }

    [role="option"] {
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
        padding: 0.625rem 0.875rem !important;
        font-size: 0.9375rem !important;
    }

    [role="option"]:hover {
        background: var(--bg-card-hover) !important;
        color: var(--text-primary) !important;
    }

    [aria-selected="true"] {
        background: rgba(37, 99, 235, 0.2) !important;
        color: var(--primary-light) !important;
    }

    .stRadio > label {
        font-size: 0.8125rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: var(--space-md) !important;
    }

    .stRadio > div {
        gap: var(--space-sm);
    }

    .stRadio > div > label {
        background: var(--bg-darker) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 0.75rem 1rem !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
    }

    .stRadio > div > label:hover {
        background: var(--bg-card) !important;
        border-color: var(--primary-light) !important;
    }

    .stRadio > div > label > div:first-child {
        margin-right: var(--space-md) !important;
        width: 20px !important;
        height: 20px !important;
        min-width: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stRadio > div > label > div:first-child > div {
        background: transparent !important;
        border: 2px solid var(--border-light) !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
    }

    .stRadio > div > label[data-checked="true"] {
        background: rgba(37, 99, 235, 0.15) !important;
        border-color: var(--primary) !important;
    }

    .stRadio > div > label[data-checked="true"] > div:first-child > div {
        border-color: var(--primary) !important;
        background: var(--primary) !important;
        box-shadow: 0 0 0 2px var(--bg-darker), 0 0 0 4px var(--primary) !important;
    }

    .stRadio > div > label[data-checked="true"] > div:first-child > div::before {
        content: '';
        display: block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: white;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }

    .stRadio > div > label > div:last-child {
        color: var(--text-secondary) !important;
        font-size: 0.9375rem !important;
        font-weight: 500 !important;
        flex: 1 !important;
    }

    .stRadio > div > label[data-checked="true"] > div:last-child {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    .stMultiSelect [data-baseweb="select"] {
        background: var(--bg-darker) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        min-height: 42px !important;
    }

    .stMultiSelect [data-baseweb="tag"] {
        background: var(--primary) !important;
        border: none !important;
        border-radius: calc(var(--radius) - 2px) !important;
        padding: 0.25rem 0.5rem !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.8125rem !important;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: var(--radius) !important;
        border: none !important;
        box-shadow: var(--shadow-md) !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.01em;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg) !important;
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: var(--space-md) !important;
        color: var(--text-secondary) !important;
        border-left-width: 3px !important;
    }

    .stSuccess {
        border-left-color: var(--success) !important;
        background: rgba(16, 185, 129, 0.05) !important;
    }

    .stWarning {
        border-left-color: var(--warning) !important;
        background: rgba(245, 158, 11, 0.05) !important;
    }

    .stError {
        border-left-color: var(--danger) !important;
        background: rgba(239, 68, 68, 0.05) !important;
    }

    .stInfo {
        border-left-color: var(--accent) !important;
        background: rgba(6, 182, 212, 0.05) !important;
    }

    [data-testid="metric-container"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: var(--space-lg);
        box-shadow: var(--shadow);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8125rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: var(--space-md) !important;
    }

    .streamlit-expanderHeader:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--primary) !important;
    }

    .security-notice {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: var(--space-lg);
        margin-top: var(--space-xl);
        text-align: center;
        color: var(--text-muted);
        font-size: 0.8125rem;
        line-height: 1.6;
    }

    [data-testid="column"] {
        padding: 0 var(--space-sm);
    }

    @media (max-width: 768px) {
        .block-container {
            padding: var(--space-lg) var(--space-md);
        }

        .main-title {
            font-size: 1.75rem;
        }

        .section-card {
            padding: var(--space-lg);
        }

        .trust-container {
            gap: var(--space-sm);
        }

        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-darker);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-light);
        border-radius: var(--radius);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }

</style>
""", unsafe_allow_html=True)

# ============================================================================
# UTILIDADES
# ============================================================================

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ============================================================================
# FUNCIONES DE CARGA
# ============================================================================

@st.cache_data
def load_questions():
    """Cargar preguntas desde JSON"""
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    with open(questions_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ============================================================================
# GESTIÓN DE ESTADO - LAYER 1: COMPATIBILITY
# ============================================================================

def init_session_state():
    """
    LAYER 1: Compatibility Layer
    Inicializar session_state con valores seguros para universal compatibility
    """
    if 'step' not in st.session_state:
        st.session_state.step = 0

    # ✅ LAYER 1: String vacío como default (compatible con todas las versiones de Streamlit)
    prospect_defaults = {
        'nombre_empresa': '',
        'sector': '',
        'facturacion_rango': '',
        'empleados_rango': '',
        'contacto_nombre': '',
        'contacto_email': '',
        'contacto_telefono': '',
        'cargo': '',
        'ciudad': ''
    }

    for key, default in prospect_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    diagnostic_defaults = {
        'Q4': [], 'Q5': None, 'Q6': None, 'Q7': None, 'Q8': None,
        'Q9': None, 'Q10': None, 'Q11': None, 'Q12': None, 'Q12_otro': '',
        'Q13': None, 'Q14': None, 'Q15': None
    }

    for key, default in diagnostic_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'email_sent' not in st.session_state:
        st.session_state.email_sent = False
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False

# ============================================================================
# COMPONENTES UI
# ============================================================================

def show_header():
    """Header hero moderno"""
    st.markdown('''
    <div class="hero-header">
        <div class="main-title">AI Readiness Diagnostic</div>
        <div class="main-subtitle">
            Evaluación estratégica de madurez digital para empresas líderes
        </div>
        <div class="trust-container">
            <div class="trust-badge">
                <span>🔒</span>
                <span>Datos Encriptados</span>
            </div>
            <div class="trust-badge">
                <span>⚡</span>
                <span>Análisis en Tiempo Real</span>
            </div>
            <div class="trust-badge">
                <span>✓</span>
                <span>100% Confidencial</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def show_progress_bar(current_step, total_steps):
    """Barra de progreso premium"""
    progress = (current_step + 1) / total_steps
    percentage = int(progress * 100)
    steps = ["Información Empresarial", "Evaluación Estratégica", "Resultados"]

    st.markdown(f"""
    <div class="progress-wrapper">
        <div class="progress-header">
            <span class="progress-step-label">PASO {current_step + 1}/{total_steps}: {steps[current_step].upper()}</span>
            <span class="progress-percentage">{percentage}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)

def show_security_footer():
    """Footer de seguridad"""
    st.markdown("""
    <div class="security-notice">
        🔐 <strong>Protección de Datos Empresariales</strong><br>
        Todos los datos son procesados bajo estrictos protocolos de seguridad y confidencialidad.
        Cumplimiento total con normativas internacionales de protección de datos.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# RECOLECCIÓN DE DATOS - LAYER 2: UX
# ============================================================================

def collect_prospect_info():
    """
    LAYER 2: UX Layer
    Formulario con placeholders explícitos para forzar selección
    """

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Información Empresarial</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.text_input(
            "Razón Social",
            key="nombre_empresa",
            placeholder="Ingrese el nombre legal de la empresa",
            help="Denominación oficial registrada"
        )

        # ✅ LAYER 2: Placeholder explícito como primera opción
        sectores_con_placeholder = ["-- Seleccione sector --"] + SECTORES
        st.selectbox(
            "Sector Industrial",
            options=sectores_con_placeholder,
            key="sector",
            help="Categoría principal de actividad económica"
        )

        # ✅ LAYER 2: Placeholder explícito como primera opción
        facturacion_con_placeholder = ["-- Seleccione facturación --"] + RANGOS_FACTURACION
        st.selectbox(
            "Facturación Anual",
            options=facturacion_con_placeholder,
            key="facturacion_rango",
            help="Ingresos consolidados del último ejercicio fiscal"
        )

        # ✅ LAYER 2: Placeholder explícito como primera opción
        empleados_con_placeholder = ["-- Seleccione empleados --"] + RANGOS_EMPLEADOS
        st.selectbox(
            "Plantilla de Personal",
            options=empleados_con_placeholder,
            key="empleados_rango",
            help="Número total de colaboradores activos"
        )

        st.text_input(
            "Ubicación Principal",
            key="ciudad",
            placeholder="Ciudad de sede central",
            help="Localización de oficinas corporativas"
        )

    with col2:
        st.text_input(
            "Nombre del Ejecutivo",
            key="contacto_nombre",
            placeholder="Nombre completo del representante",
            help="Persona responsable de la evaluación"
        )

        st.text_input(
            "Email Corporativo",
            key="contacto_email",
            placeholder="correo@empresa.com",
            help="Dirección de correo empresarial"
        )

        st.text_input(
            "Teléfono de Contacto",
            key="contacto_telefono",
            placeholder="+57 300 000 0000",
            help="Número directo (opcional)"
        )

        # ✅ LAYER 2: Placeholder explícito como primera opción
        cargos_con_placeholder = ["-- Seleccione cargo --"] + CARGOS
        st.selectbox(
            "Posición Ejecutiva",
            options=cargos_con_placeholder,
            key="cargo",
            help="Rol dentro de la estructura organizacional"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ✅ LAYER 2: Validación con detección de placeholders
    placeholder_strings = [
        '-- Seleccione sector --',
        '-- Seleccione facturación --',
        '-- Seleccione empleados --',
        '-- Seleccione cargo --'
    ]

    nombre_ok = st.session_state.get('nombre_empresa', '').strip() != ''
    sector_ok = st.session_state.get('sector', '') not in ['', '-- Seleccione sector --']
    facturacion_ok = st.session_state.get('facturacion_rango', '') not in ['', '-- Seleccione facturación --']
    empleados_ok = st.session_state.get('empleados_rango', '') not in ['', '-- Seleccione empleados --']
    contacto_nombre_ok = st.session_state.get('contacto_nombre', '').strip() != ''
    email_ok = st.session_state.get('contacto_email', '').strip() != ''
    cargo_ok = st.session_state.get('cargo', '') not in ['', '-- Seleccione cargo --']
    ciudad_ok = st.session_state.get('ciudad', '').strip() != ''

    all_filled = all([
        nombre_ok, sector_ok, facturacion_ok, empleados_ok,
        contacto_nombre_ok, email_ok, cargo_ok, ciudad_ok
    ])

    email_value = st.session_state.get('contacto_email', '').strip()
    email_valid = validate_email(email_value) if email_value else False

    if not all_filled or not email_valid:
        if not all_filled:
            missing = []
            if not nombre_ok: missing.append("Razón Social")
            if not sector_ok: missing.append("Sector")
            if not facturacion_ok: missing.append("Facturación")
            if not empleados_ok: missing.append("Empleados")
            if not contacto_nombre_ok: missing.append("Nombre del Ejecutivo")
            if not email_ok: missing.append("Email")
            if not cargo_ok: missing.append("Cargo")
            if not ciudad_ok: missing.append("Ciudad")

            st.warning(f"⚠️ Complete los siguientes campos: {', '.join(missing)}")
        elif not email_valid:
            st.error("❌ El formato del email no es válido")

    show_security_footer()

    return all_filled and email_valid

def show_diagnostic_questions():
    """Cuestionario de evaluación"""
    questions = load_questions()

    # Bloque 1
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🎯 Objetivos Estratégicos</div>', unsafe_allow_html=True)

    q4_opciones = questions["bloque_1_identificacion"]["preguntas"][0]["opciones"]
    st.multiselect(
        "¿Qué objetivos estratégicos impulsan esta evaluación?",
        options=q4_opciones,
        key="Q4",
        help="Seleccione todos los objetivos aplicables"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Bloque 2
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔬 Diagnóstico Operacional</div>', unsafe_allow_html=True)

    for pregunta in questions["bloque_2_diagnostico"]["preguntas"]:
        q_id = pregunta["id"]
        helper = pregunta.get("helper", "")

        if pregunta.get("tiene_otro"):
            opciones = pregunta["opciones"] + ["Otro"]
            respuesta = st.radio(
                pregunta["pregunta"],
                options=opciones,
                key=q_id,
                help=helper if helper else None
            )

            if respuesta == "Otro":
                st.text_input(
                    "Especifique:",
                    key=f"{q_id}_otro",
                    placeholder="Describa su caso específico"
                )
        else:
            st.radio(
                pregunta["pregunta"],
                options=pregunta["opciones"],
                key=q_id,
                help=helper if helper else None
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # Bloque 3
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💼 Viabilidad Financiera</div>', unsafe_allow_html=True)

    for pregunta in questions["bloque_3_viabilidad"]["preguntas"]:
        st.radio(
            pregunta["pregunta"],
            options=pregunta["opciones"],
            key=pregunta["id"]
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Validación
    q4_valid = len(st.session_state.get("Q4", [])) > 0
    radio_questions = ["Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15"]
    radio_valid = all(st.session_state.get(q) is not None for q in radio_questions)

    return q4_valid and radio_valid

# ============================================================================
# PROCESAMIENTO - LAYER 3: VALIDATION
# ============================================================================

def process_diagnostic():
    """
    LAYER 3: Validation Layer
    Validación defensiva exhaustiva antes de procesamiento
    """

    print(f"[PROCESS START] {datetime.now()}")

    # ✅ LAYER 3: Extraer valores de session_state
    facturacion = st.session_state.get('facturacion_rango', '')
    empleados = st.session_state.get('empleados_rango', '')
    sector = st.session_state.get('sector', '')
    cargo = st.session_state.get('cargo', '')
    nombre_empresa = st.session_state.get('nombre_empresa', '')
    contacto_email = st.session_state.get('contacto_email', '')
    ciudad = st.session_state.get('ciudad', '')

    # ✅ LAYER 3: Logging pre-validación para observabilidad
    print(f"\n{'='*80}")
    print(f"[LAYER 3: PRE-VALIDATION]")
    print(f"{'='*80}")
    print(f"nombre_empresa: '{nombre_empresa}' (len={len(nombre_empresa)})")
    print(f"sector: '{sector}' (len={len(sector)})")
    print(f"facturacion_rango: '{facturacion}' (len={len(facturacion)})")
    print(f"empleados_rango: '{empleados}' (len={len(empleados)})")
    print(f"contacto_email: '{contacto_email}' (len={len(contacto_email)})")
    print(f"cargo: '{cargo}' (len={len(cargo)})")
    print(f"ciudad: '{ciudad}' (len={len(ciudad)})")
    print(f"{'='*80}\n")

    # ✅ LAYER 3: Validación defensiva con detección de placeholders
    placeholder_strings = [
        '-- Seleccione sector --',
        '-- Seleccione facturación --',
        '-- Seleccione empleados --',
        '-- Seleccione cargo --'
    ]

    # Validación granular con mensajes específicos
    if facturacion in placeholder_strings or facturacion == '':
        st.error(f"❌ **Facturación no seleccionada**")
        st.info(f"💡 Valor actual detectado: '{facturacion}'")
        st.info(f"📋 Por favor, seleccione un rango de facturación válido del dropdown.")
        print(f"[VALIDATION FAILED] facturacion_rango: '{facturacion}'")
        st.stop()

    if empleados in placeholder_strings or empleados == '':
        st.error(f"❌ **Empleados no seleccionado**")
        st.info(f"💡 Valor actual detectado: '{empleados}'")
        st.info(f"📋 Por favor, seleccione un rango de empleados válido del dropdown.")
        print(f"[VALIDATION FAILED] empleados_rango: '{empleados}'")
        st.stop()

    if sector in placeholder_strings or sector == '':
        st.error(f"❌ **Sector no seleccionado**")
        st.info(f"💡 Valor actual detectado: '{sector}'")
        st.info(f"📋 Por favor, seleccione un sector válido del dropdown.")
        print(f"[VALIDATION FAILED] sector: '{sector}'")
        st.stop()

    if cargo in placeholder_strings or cargo == '':
        st.error(f"❌ **Cargo no seleccionado**")
        st.info(f"💡 Valor actual detectado: '{cargo}'")
        st.info(f"📋 Por favor, seleccione un cargo válido del dropdown.")
        print(f"[VALIDATION FAILED] cargo: '{cargo}'")
        st.stop()

    # ✅ LAYER 3: Validación pasada
    print(f"[LAYER 3: VALIDATION PASSED] ✅ All fields validated successfully")

    # Crear ProspectInfo
    prospect_info = ProspectInfo(
        nombre_empresa=nombre_empresa.strip(),
        sector=sector,
        facturacion_rango=facturacion,
        empleados_rango=empleados,
        contacto_nombre=st.session_state.contacto_nombre.strip(),
        contacto_email=contacto_email.strip(),
        contacto_telefono=st.session_state.contacto_telefono.strip(),
        cargo=cargo,
        ciudad=ciudad.strip()
    )

    # ✅ LAYER 3: Verificación post-creación
    print(f"\n{'='*80}")
    print(f"[LAYER 3: POST-CREATION VERIFICATION]")
    print(f"{'='*80}")
    print(f"ProspectInfo.nombre_empresa: '{prospect_info.nombre_empresa}'")
    print(f"ProspectInfo.sector: '{prospect_info.sector}'")
    print(f"ProspectInfo.facturacion_rango: '{prospect_info.facturacion_rango}'")
    print(f"ProspectInfo.empleados_rango: '{prospect_info.empleados_rango}'")
    print(f"ProspectInfo.contacto_email: '{prospect_info.contacto_email}'")
    print(f"ProspectInfo.cargo: '{prospect_info.cargo}'")
    print(f"ProspectInfo.ciudad: '{prospect_info.ciudad}'")
    print(f"{'='*80}\n")

    # Manejo de frustracion "Otro"
    frustracion = st.session_state.Q12
    if frustracion == "Otro":
        frustracion = st.session_state.get("Q12_otro", "Otro")

    # ✅ TYPE-SAFE: motivacion siempre List[str]
    motivacion_list = st.session_state.Q4 if st.session_state.Q4 else []

    responses = DiagnosticResponses(
        motivacion=motivacion_list,
        toma_decisiones=st.session_state.Q5,
        procesos_criticos=st.session_state.Q6,
        tareas_repetitivas=st.session_state.Q7,
        compartir_informacion=st.session_state.Q8,
        equipo_tecnico=st.session_state.Q9,
        capacidad_implementacion=st.session_state.Q10,
        inversion_reciente=st.session_state.Q11,
        frustracion_principal=frustracion,
        urgencia=st.session_state.Q13,
        proceso_aprobacion=st.session_state.Q14,
        presupuesto_rango=st.session_state.Q15
    )

    engine = ScoringEngine()
    score = engine.calculate_full_score(responses, prospect_info)

    classifier = ArchetypeClassifier()
    arquetipo = classifier.classify(score, responses, prospect_info)

    insight_gen = InsightGenerator()
    quick_wins = insight_gen.generate_quick_wins(score, responses, arquetipo)
    red_flags = insight_gen.generate_red_flags(score, responses, prospect_info)
    insights = insight_gen.generate_insights(score, responses, arquetipo)
    reunion_prep = insight_gen.generate_reunion_prep(score, responses, arquetipo, prospect_info)

    if score.tier.value == "A":
        servicio = "Implementación Completa"
        monto_min, monto_max = 25000000, 45000000
    elif score.tier.value == "B":
        servicio = "Diagnóstico Profundo + Roadmap"
        monto_min, monto_max = 12000000, 25000000
    else:
        servicio = "Workshop Educativo"
        monto_min, monto_max = 0, 5000000

    result = DiagnosticResult(
        prospect_info=prospect_info,
        responses=responses,
        score=score,
        arquetipo=arquetipo,
        quick_wins=quick_wins,
        red_flags=red_flags,
        insights=insights,
        servicio_sugerido=servicio,
        monto_sugerido_min=monto_min,
        monto_sugerido_max=monto_max,
        reunion_prep=reunion_prep
    )

    print(f"[PROCESS END] Result created for {prospect_info.nombre_empresa}")

    return result

# ============================================================================
# CONFIRMACIÓN
# ============================================================================

def show_confirmation_screen(result):
    """Pantalla de resultados"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## ✅ Evaluación Completada")

    email_sent = st.session_state.get("email_sent", False)

    if email_sent:
        st.success(f"""
        **{result.prospect_info.contacto_nombre}**, gracias por completar la evaluación estratégica.

        Análisis de **{result.prospect_info.nombre_empresa}** procesado exitosamente.

        📧 Reporte enviado a: {result.prospect_info.contacto_email}
        """)
    else:
        st.warning(f"""
        **{result.prospect_info.contacto_nombre}**, evaluación completada.

        ⚠️ Contacto manual programado en 24h.

        📧 {result.prospect_info.contacto_email}
        """)

    st.markdown("### 📊 Métricas de Madurez")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Madurez Digital",
            f"{result.score.madurez_digital.score_total}/40",
            delta=f"Tier {result.score.tier.value}"
        )

    with col2:
        st.metric(
            "Capacidad Financiera",
            f"{result.score.capacidad_inversion.score_total}/30"
        )

    with col3:
        st.metric(
            "Viabilidad Comercial",
            f"{result.score.viabilidad_comercial.score_total}/30"
        )

    st.markdown("### 🎯 Próximas Fases")

    st.info(f"""
    **Agenda de seguimiento (48-72h):**

    1. Análisis detallado de oportunidades para {result.prospect_info.nombre_empresa}
    2. Casos de éxito en {result.prospect_info.sector}
    3. Propuesta ejecutiva personalizada

    **Contacto:**
    - Email: {result.prospect_info.contacto_email}
    - Tel: {result.prospect_info.contacto_telefono or 'N/D'}
    """)

    st.markdown('</div>', unsafe_allow_html=True)

    if not email_sent or not st.session_state.get("pdf_generated", False):
        with st.expander("ℹ️ Estado del Sistema"):
            st.write(f"- Evaluación: ✅")
            st.write(f"- Email: {'✅' if email_sent else '❌'}")
            st.write(f"- PDF: {'✅' if st.session_state.get('pdf_generated', False) else '❌'}")
            st.write(f"- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if st.button("🔄 Nueva Evaluación"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    show_security_footer()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal con orquestación del flujo"""
    init_session_state()
    show_header()

    if st.session_state.step == 0:
        show_progress_bar(0, 2)
        if collect_prospect_info():
            if st.button("Continuar Evaluación →"):
                st.session_state.step = 1
                st.rerun()

    elif st.session_state.step == 1:
        show_progress_bar(1, 2)
        if show_diagnostic_questions():
            if st.button("Procesar Análisis"):
                with st.spinner("Procesando evaluación estratégica..."):

                    print(f"\n{'='*80}")
                    print(f"[DIAGNOSTIC START] {datetime.now()}")
                    print(f"{'='*80}\n")

                    result = process_diagnostic()

                    save_success = False
                    try:
                        print(f"[SHEETS] Intentando guardar...")
                        connector = SheetsConnector()
                        connector.save_diagnostic(result)
                        save_success = True
                        st.success("✅ Datos almacenados en Google Sheets")
                        print(f"[SHEETS] ✅ Guardado exitoso")
                    except Exception as e:
                        st.error(f"❌ Error crítico en Google Sheets: {str(e)}")
                        print(f"[SHEETS] ❌ ERROR: {str(e)}")
                        print(traceback.format_exc())

                        if st.button("🔄 Reintentar Guardado"):
                            st.rerun()
                        st.stop()

                    pdf_success = False
                    pdf_path = None
                    if save_success:
                        try:
                            print(f"[PDF] Generando...")
                            pdf_gen = PDFGenerator()
                            pdf_path = pdf_gen.generate_prospect_pdf(result)
                            pdf_success = True
                            st.success("✅ PDF generado")
                            print(f"[PDF] ✅ Generado: {pdf_path}")
                        except Exception as e:
                            st.warning(f"⚠️ PDF no disponible: {str(e)}")
                            print(f"[PDF] ⚠️ ERROR: {str(e)}")
                            print(traceback.format_exc())

                    email_success = False
                    if save_success:
                        try:
                            print(f"[EMAIL] Enviando...")
                            email_sender = EmailSender()
                            email_sender.send_confirmation_email(result, pdf_path)
                            email_success = True
                            st.success(f"✅ Email enviado a {result.prospect_info.contacto_email}")
                            print(f"[EMAIL] ✅ Enviado a {result.prospect_info.contacto_email}")
                        except Exception as e:
                            st.warning(f"⚠️ Email no enviado: {str(e)}")
                            print(f"[EMAIL] ⚠️ ERROR: {str(e)}")
                            print(traceback.format_exc())

                    if save_success:
                        st.session_state.result = result
                        st.session_state.email_sent = email_success
                        st.session_state.pdf_generated = pdf_success
                        st.session_state.step = 2

                        print(f"\n{'='*80}")
                        print(f"[DIAGNOSTIC END] {datetime.now()}")
                        print(f"  Sheets: {'✅' if save_success else '❌'}")
                        print(f"  PDF: {'✅' if pdf_success else '❌'}")
                        print(f"  Email: {'✅' if email_success else '❌'}")
                        print(f"{'='*80}\n")

                        st.rerun()
        else:
            st.warning("⚠️ Complete todas las preguntas para continuar")

    elif st.session_state.step == 2:
        show_confirmation_screen(st.session_state.result)

if __name__ == "__main__":
    main()
