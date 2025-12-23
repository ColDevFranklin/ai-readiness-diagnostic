```python
"""
Formulario de Diagnóstico AI Readiness - Aplicación Principal
Version: 4.0 - Diseño Moderno Premium + UX Optimizada
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
# SISTEMA DE DISEÑO PREMIUM
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    :root {
        /* Paleta principal - Gradientes modernos */
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --dark-gradient: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);

        /* Colores sólidos */
        --primary: #667eea;
        --primary-dark: #5568d3;
        --secondary: #f5576c;
        --dark: #1a1a2e;
        --darker: #0f0f1e;
        --light: #f7f9fc;
        --white: #ffffff;

        /* Grises refinados */
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;

        /* Espaciado fluido */
        --space-xs: 0.5rem;
        --space-sm: 0.75rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
        --space-2xl: 3rem;
        --space-3xl: 4rem;

        /* Tipografía */
        --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

        /* Sombras premium */
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
        --shadow-glow: 0 0 32px rgba(102, 126, 234, 0.3);

        /* Radios */
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --radius-full: 9999px;
    }

    /* ============================================
       BASE & RESET
       ============================================ */
    * {
        font-family: var(--font-primary);
    }

    .main {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
        padding: 0;
    }

    .block-container {
        max-width: 1400px;
        padding: var(--space-3xl) var(--space-xl);
    }

    /* ============================================
       HEADER HERO
       ============================================ */
    .hero-header {
        text-align: center;
        margin-bottom: var(--space-3xl);
        padding: var(--space-2xl) 0;
    }

    .main-title {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff 0%, #667eea 50%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: var(--space-md);
        line-height: 1.1;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 24px rgba(102, 126, 234, 0.3);
    }

    .main-subtitle {
        font-size: clamp(1.125rem, 2vw, 1.5rem);
        color: rgba(255, 255, 255, 0.8);
        font-weight: 300;
        margin-bottom: var(--space-2xl);
        line-height: 1.6;
    }

    /* Trust badges mejorados */
    .trust-container {
        display: flex;
        justify-content: center;
        gap: var(--space-lg);
        flex-wrap: wrap;
        margin-bottom: var(--space-xl);
    }

    .trust-badge {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: var(--space-sm) var(--space-lg);
        border-radius: var(--radius-full);
        font-size: 0.875rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .trust-badge:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(102, 126, 234, 0.5);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }

    /* ============================================
       PROGRESS BAR REDISEÑADO
       ============================================ */
    .progress-wrapper {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-xl);
        padding: var(--space-xl);
        margin-bottom: var(--space-2xl);
        box-shadow: var(--shadow-xl);
    }

    .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-lg);
    }

    .progress-step-label {
        font-size: 1rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
    }

    .progress-percentage {
        font-size: 1.5rem;
        font-weight: 800;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stProgress > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-full);
        height: 8px;
        overflow: hidden;
    }

    .stProgress > div > div > div {
        background: var(--primary-gradient);
        border-radius: var(--radius-full);
        height: 8px;
        box-shadow: 0 0 16px rgba(102, 126, 234, 0.5);
    }

    /* ============================================
       SECTION CARDS PREMIUM
       ============================================ */
    .section-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: var(--radius-xl);
        padding: var(--space-2xl);
        margin-bottom: var(--space-xl);
        box-shadow: var(--shadow-xl);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .section-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .section-card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateY(-4px);
        box-shadow: var(--shadow-glow);
    }

    .section-card:hover::before {
        opacity: 1;
    }

    .section-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--white);
        margin-bottom: var(--space-xl);
        display: flex;
        align-items: center;
        gap: var(--space-md);
        padding-bottom: var(--space-md);
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }

    /* ============================================
       FORM INPUTS REDISEÑADOS
       ============================================ */
    .stTextInput label,
    .stSelectbox label,
    .stMultiSelect label {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: rgba(255, 255, 255, 0.9) !important;
        margin-bottom: var(--space-sm) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: var(--radius-md) !important;
        color: var(--white) !important;
        font-size: 1rem !important;
        padding: var(--space-md) var(--space-lg) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 48px;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
        font-weight: 400;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
        outline: none !important;
    }

    /* Selectbox específico */
    .stSelectbox > div > div > div {
        color: var(--white) !important;
        background: transparent !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* ============================================
       RADIO BUTTONS MODERNOS
       ============================================ */
    .stRadio > label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: rgba(255, 255, 255, 0.9) !important;
        margin-bottom: var(--space-lg) !important;
    }

    .stRadio > div {
        background: transparent !important;
        padding: 0 !important;
        gap: var(--space-md);
    }

    .stRadio > div > label {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-lg) !important;
        margin-bottom: var(--space-sm) !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
    }

    .stRadio > div > label:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        border-color: var(--primary) !important;
        transform: translateX(4px);
        box-shadow: var(--shadow-md);
    }

    .stRadio > div > label > div {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* ============================================
       MULTISELECT
       ============================================ */
    .stMultiSelect [data-baseweb="tag"] {
        background: var(--primary-gradient) !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: var(--space-xs) var(--space-md) !important;
        color: var(--white) !important;
        font-weight: 600 !important;
    }

    /* ============================================
       BOTONES PREMIUM
       ============================================ */
    .stButton > button {
        width: 100%;
        background: var(--primary-gradient) !important;
        color: var(--white) !important;
        font-weight: 700 !important;
        font-size: 1.125rem !important;
        padding: var(--space-lg) var(--space-2xl) !important;
        border-radius: var(--radius-md) !important;
        border: none !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow) !important;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* ============================================
       ALERTAS MODERNAS
       ============================================ */
    .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--radius-lg) !important;
        padding: var(--space-lg) !important;
        color: rgba(255, 255, 255, 0.9) !important;
        border-left-width: 4px !important;
    }

    .stSuccess {
        border-left-color: #4facfe !important;
    }

    .stWarning {
        border-left-color: #f5576c !important;
    }

    .stInfo {
        border-left-color: #667eea !important;
    }

    /* ============================================
       MÉTRICAS
       ============================================ */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        box-shadow: var(--shadow-lg);
        transition: all 0.3s ease;
    }

    [data-testid="metric-container"]:hover {
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateY(-4px);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: rgba(255, 255, 255, 0.6) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ============================================
       COLUMNAS
       ============================================ */
    [data-testid="column"] {
        padding: var(--space-sm);
    }

    /* ============================================
       EXPANDER
       ============================================ */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-md) !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 600 !important;
        padding: var(--space-md) !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: var(--primary);
    }

    /* ============================================
       SPINNER
       ============================================ */
    .stSpinner > div {
        border-color: var(--primary) !important;
        border-right-color: transparent !important;
    }

    /* ============================================
       SECURITY FOOTER
       ============================================ */
    .security-notice {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-lg);
        padding: var(--space-xl);
        margin-top: var(--space-2xl);
        text-align: center;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.875rem;
        line-height: 1.6;
    }

    /* ============================================
       RESPONSIVE
       ============================================ */
    @media (max-width: 768px) {
        .block-container {
            padding: var(--space-xl) var(--space-md);
        }

        .main-title {
            font-size: 2rem;
        }

        .main-subtitle {
            font-size: 1rem;
        }

        .section-card {
            padding: var(--space-lg);
        }

        .trust-container {
            gap: var(--space-sm);
        }

        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }
    }

    /* ============================================
       ANIMACIONES
       ============================================ */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }

    .section-card {
        animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ============================================
       HIDE STREAMLIT BRANDING
       ============================================ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ============================================
       SCROLLBAR PERSONALIZADO
       ============================================ */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary-gradient);
        border-radius: var(--radius-full);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-gradient);
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
# GESTIÓN DE ESTADO
# ============================================================================

def init_session_state():
    """Inicializar TODAS las variables de session_state"""
    if 'step' not in st.session_state:
        st.session_state.step = 0

    prospect_defaults = {
        'nombre_empresa': '', 'sector': '', 'facturacion': '', 'empleados': '',
        'contacto_nombre': '', 'contacto_email': '', 'contacto_telefono': '',
        'cargo': '', 'ciudad': ''
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
# RECOLECCIÓN DE DATOS
# ============================================================================

def collect_prospect_info():
    """Formulario de información empresarial"""

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Información Empresarial</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.text_input(
            "Razón Social",
            key="nombre_empresa",
            placeholder="Ingrese el nombre legal de la empresa",
            help="Denominación oficial registrada"
        )

        st.selectbox(
            "Sector Industrial",
            options=SECTORES,
            key="sector",
            help="Categoría principal de actividad económica"
        )

        st.selectbox(
            "Facturación Anual",
            options=RANGOS_FACTURACION,
            key="facturacion",
            help="Ingresos consolidados del último ejercicio fiscal"
        )

        st.selectbox(
            "Plantilla de Personal",
            options=RANGOS_EMPLEADOS,
            key="empleados",
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

        st.selectbox(
            "Posición Ejecutiva",
            options=CARGOS,
            key="cargo",
            help="Rol dentro de la estructura organizacional"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Validación
    required_fields = [
        st.session_state.nombre_empresa.strip(),
        st.session_state.sector,
        st.session_state.facturacion,
        st.session_state.empleados,
        st.session_state.contacto_nombre.strip(),
        st.session_state.contacto_email.strip(),
        st.session_state.cargo,
        st.session_state.ciudad.strip()
    ]

    all_filled = all(required_fields)
    email_valid = validate_email(st.session_state.contacto_email.strip()) if st.session_state.contacto_email.strip() else False

    if not all_filled or not email_valid:
        if not all_filled:
            st.warning("⚠️ Complete todos los campos obligatorios para continuar")
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
# PROCESAMIENTO
# ============================================================================

def process_diagnostic():
    """Procesar evaluación completa"""
    prospect_info = ProspectInfo(
        nombre_empresa=st.session_state.nombre_empresa,
        sector=st.session_state.sector,
        facturacion_rango=st.session_state.facturacion,
        empleados_rango=st.session_state.empleados,
        contacto_nombre=st.session_state.contacto_nombre,
        contacto_email=st.session_state.contacto_email,
        contacto_telefono=st.session_state.contacto_telefono or "",
        cargo=st.session_state.cargo,
        ciudad=st.session_state.ciudad
    )

    frustracion = st.session_state.Q12
    if frustracion == "Otro":
        frustracion = st.session_state.get("Q12_otro", "Otro")

    responses = DiagnosticResponses(
        motivacion=st.session_state.Q4,
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
    """Función principal"""
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
                    result = process_diagnostic()

                    save_success = False
                    try:
                        connector = SheetsConnector()
                        connector.save_diagnostic(result)
                        save_success = True
                        st.success("✅ Datos almacenados")
                    except Exception as e:
                        st.error(f"❌ Error crítico: {e}")
                        print(f"[ERROR SHEETS] {datetime.now()}: {traceback.format_exc()}")
                        if st.button("🔄 Reintentar"):
                            st.rerun()
                        st.stop()

                    pdf_success = False
                    pdf_path = None
                    if save_success:
                        try:
                            pdf_gen = PDFGenerator()
                            pdf_path = pdf_gen.generate_prospect_pdf(result)
                            pdf_success = True
                            st.success("✅ PDF generado")
                        except Exception as e:
                            st.warning(f"⚠️ PDF no disponible: {e}")
                            print(f"[ERROR PDF] {datetime.now()}: {traceback.format_exc()}")

                    email_success = False
                    if save_success:
                        try:
                            email_sender = EmailSender()
                            email_sender.send_confirmation_email(result, pdf_path)
                            email_success = True
                            st.success(f"✅ Email enviado")
                        except Exception as e:
                            st.warning(f"⚠️ Email no enviado: {e}")
                            print(f"[ERROR EMAIL] {datetime.now()}: {traceback.format_exc()}")

                    if save_success:
                        st.session_state.result = result
                        st.session_state.email_sent = email_success
                        st.session_state.pdf_generated = pdf_success
                        st.session_state.step = 2
                        st.rerun()
        else:
            st.warning("⚠️ Complete todas las preguntas para continuar")

    elif st.session_state.step == 2:
        show_confirmation_screen(st.session_state.result)

if __name__ == "__main__":
    main()
```
