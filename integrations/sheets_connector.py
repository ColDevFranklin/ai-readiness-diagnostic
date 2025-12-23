"""
Formulario público de diagnóstico AI Readiness
VERSION: 3.4 PRODUCTION - FIX: Data persistence across st.rerun()
Autor: Andrés - AI Consultant
"""

import streamlit as st
import json
import re
from pathlib import Path
from datetime import datetime
import traceback

from core.models import (
    ProspectInfo, DiagnosticResponses, DiagnosticResult
)
from core.scoring_engine import ScoringEngine
from core.classifier import ArchetypeClassifier
from integrations.sheets_connector import SheetsConnector
from integrations.email_sender import EmailSender
from integrations.pdf_generator import PDFGenerator
from app.config import SECTORES, RANGOS_FACTURACION, RANGOS_EMPLEADOS, CARGOS


class InsightGenerator:
    """Generador de insights estratégicos"""

    def generate_quick_wins(self, score, responses, arquetipo):
        wins = []

        if responses.tareas_repetitivas == "Sí, muchas tareas manuales repetitivas":
            wins.append("Automatización de procesos manuales con RPA")

        if responses.toma_decisiones in ["Reportes manuales en Excel", "Intuición del equipo"]:
            wins.append("Dashboard de BI con visualización en tiempo real")

        if responses.compartir_informacion in ["Email y carpetas compartidas", "WhatsApp/Slack sin estructura"]:
            wins.append("Sistema de gestión documental centralizado")

        if score.madurez_digital.score_total < 15:
            wins.append("Workshop de alfabetización digital para líderes")

        return wins[:3]

    def generate_red_flags(self, score, responses, prospect_info):
        flags = []

        if responses.frustracion_principal == "No tengo frustraciones, todo funciona bien":
            flags.append("⚠️ Posible Innovation Theater - Sin problema claro")

        if responses.urgencia == "Exploratorio, sin fecha límite":
            flags.append("⚠️ Baja urgencia - Riesgo de proyecto bloqueado")

        if responses.presupuesto_rango in ["Menos de $10M COP", "No tengo presupuesto asignado"]:
            flags.append("⚠️ Presupuesto insuficiente para implementación")

        if responses.proceso_aprobacion == "No sé, debo consultar con otras áreas":
            flags.append("⚠️ Poder de decisión limitado")

        if score.score_final < 30:
            flags.append("⚠️ Madurez digital muy baja - Requiere fase educativa previa")

        return flags

    def generate_insights(self, score, responses, arquetipo):
        insights = []

        if arquetipo.tipo == "traditional_giant":
            insights.append("Empresa con infraestructura legacy - Priorizar integraciones")

        if responses.equipo_tecnico == "No, necesitaríamos contratar o capacitar":
            insights.append("Gap crítico en talento técnico - Incluir training en propuesta")

        if score.capacidad_inversion.score_total >= 20:
            insights.append("Capacidad financiera sólida - Propuesta premium viable")

        return insights

    def generate_reunion_prep(self, score, responses, arquetipo, prospect_info):
        return {
            "probabilidad_cierre": self._calculate_close_probability(score, responses),
            "objeciones_esperadas": self._predict_objections(responses),
            "estrategia_apertura": self._generate_opening_strategy(arquetipo, responses),
            "preguntas_clave": self._generate_key_questions(responses)
        }

    def _calculate_close_probability(self, score, responses):
        base_prob = (score.score_final / 100) * 100

        if responses.urgencia == "Urgente, necesitamos solución en 1-3 meses":
            base_prob += 15
        elif responses.urgencia == "Importante, queremos empezar este año":
            base_prob += 10

        if responses.proceso_aprobacion == "Yo tengo la autoridad final":
            base_prob += 10

        return min(int(base_prob), 95)

    def _predict_objections(self, responses):
        objections = []

        if responses.presupuesto_rango in ["Menos de $10M COP", "$10M - $30M COP"]:
            objections.append("Costo vs ROI")

        if responses.equipo_tecnico == "No, necesitaríamos contratar o capacitar":
            objections.append("Falta de capacidad interna")

        if responses.capacidad_implementacion == "Baja, tenemos muchas prioridades":
            objections.append("Timing y recursos disponibles")

        return objections

    def _generate_opening_strategy(self, arquetipo, responses):
        if arquetipo.tipo == "traditional_giant":
            return "Abrir con caso de éxito en sector similar + enfoque en reducción de riesgo"
        elif arquetipo.tipo == "ambitious_scaler":
            return "Abrir con métricas de escalabilidad + velocidad de implementación"
        else:
            return "Abrir con quick wins tangibles + roadmap educativo"

    def _generate_key_questions(self, responses):
        questions = [
            "¿Cuál es el proceso crítico donde más pierden dinero/tiempo actualmente?",
            "¿Qué pasaría si no resuelven esto en los próximos 6 meses?"
        ]

        if responses.equipo_tecnico == "No, necesitaríamos contratar o capacitar":
            questions.append("¿Están abiertos a un modelo de staff augmentation temporal?")

        return questions


# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="AI Readiness Diagnostic",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CSS PREMIUM
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #2563eb;
        --primary-dark: #1e40af;
        --primary-light: #3b82f6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-main: #0f172a;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;
        --bg-darker: #0a0f1e;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --border: #334155;
        --border-light: #475569;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
        --radius: 12px;
        --space-xs: 0.25rem;
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-main) 0%, var(--bg-darker) 100%);
    }

    .block-container {
        padding: var(--space-xl) var(--space-lg);
        max-width: 1200px;
    }

    .hero-header {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: var(--space-xl);
        margin-bottom: var(--space-xl);
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-md);
        letter-spacing: -0.02em;
    }

    .main-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        margin-bottom: var(--space-lg);
        line-height: 1.6;
    }

    .trust-container {
        display: flex;
        justify-content: center;
        gap: var(--space-lg);
        flex-wrap: wrap;
        margin-top: var(--space-lg);
    }

    .trust-badge {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
        padding: var(--space-sm) var(--space-md);
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
    }

    .section-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: var(--space-xl);
        margin-bottom: var(--space-lg);
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }

    .section-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--primary);
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-lg);
        padding-bottom: var(--space-md);
        border-bottom: 2px solid var(--border);
    }

    .progress-wrapper {
        margin-bottom: var(--space-lg);
    }

    .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-sm);
    }

    .progress-step-label {
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--primary);
        letter-spacing: 0.05em;
    }

    .progress-percentage {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
    }

    .stTextInput > div > div > input {
        background: var(--bg-darker) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }

    .stSelectbox > div > div {
        background: var(--bg-darker) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
    }

    label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.9375rem !important;
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
    if 'prospect_data_locked' not in st.session_state:
        st.session_state.prospect_data_locked = None

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

    col1, col2 = st.columns(2, gap="medium")

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

    # ✅ FIX CRÍTICO: Persistir datos ANTES de st.rerun()
    if st.button("Continuar Evaluación →") and all_filled and email_valid:
        st.session_state.prospect_data_locked = {
            'nombre_empresa': st.session_state.nombre_empresa.strip(),
            'sector': st.session_state.sector,
            'facturacion': st.session_state.facturacion,
            'empleados': st.session_state.empleados,
            'contacto_nombre': st.session_state.contacto_nombre.strip(),
            'contacto_email': st.session_state.contacto_email.strip(),
            'contacto_telefono': st.session_state.contacto_telefono.strip(),
            'cargo': st.session_state.cargo,
            'ciudad': st.session_state.ciudad.strip()
        }
        st.session_state.step = 1
        st.rerun()

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
# PROCESAMIENTO - TYPE-SAFE
# ============================================================================

def process_diagnostic():
    """Procesar evaluación completa - TYPE-SAFE con data persistence"""

    print(f"\n{'='*80}")
    print(f"[PROCESS START] {datetime.now()}")

    # ✅ FIX CRÍTICO: Usar datos locked
    if 'prospect_data_locked' in st.session_state and st.session_state.prospect_data_locked:
        data = st.session_state.prospect_data_locked
        print(f"[PROSPECT DATA] ✅ Usando prospect_data_locked")
    else:
        # Fallback (no debería ocurrir)
        data = {
            'nombre_empresa': st.session_state.get('nombre_empresa', '').strip(),
            'sector': st.session_state.get('sector', ''),
            'facturacion': st.session_state.get('facturacion', ''),
            'empleados': st.session_state.get('empleados', ''),
            'contacto_nombre': st.session_state.get('contacto_nombre', '').strip(),
            'contacto_email': st.session_state.get('contacto_email', '').strip(),
            'contacto_telefono': st.session_state.get('contacto_telefono', '').strip(),
            'cargo': st.session_state.get('cargo', ''),
            'ciudad': st.session_state.get('ciudad', '').strip()
        }
        print(f"[PROSPECT DATA] ⚠️ Usando fallback (prospect_data_locked no existe)")

    # Logging detallado
    print(f"[DEBUG] nombre_empresa: '{data['nombre_empresa']}'")
    print(f"[DEBUG] contacto_email: '{data['contacto_email']}'")
    print(f"[DEBUG] sector: '{data['sector']}'")
    print(f"[DEBUG] ciudad: '{data['ciudad']}'")

    # Validación crítica
    if not data['nombre_empresa'] or not data['contacto_email']:
        error_msg = "❌ ERROR CRÍTICO: Datos del formulario perdidos"
        print(f"[ERROR] {error_msg}")
        print(f"[DEBUG] prospect_data_locked exists: {'prospect_data_locked' in st.session_state}")
        print(f"[DEBUG] prospect_data_locked value: {st.session_state.get('prospect_data_locked', 'N/A')}")
        st.error(error_msg)
        st.write("**Debug Info:**")
        st.json(data)
        st.stop()

    prospect_info = ProspectInfo(
        nombre_empresa=data['nombre_empresa'],
        sector=data['sector'],
        facturacion_rango=data['facturacion'],
        empleados_rango=data['empleados'],
        contacto_nombre=data['contacto_nombre'],
        contacto_email=data['contacto_email'],
        contacto_telefono=data['contacto_telefono'],
        cargo=data['cargo'],
        ciudad=data['ciudad']
    )

    print(f"[PROSPECT INFO] ✅ Created for {prospect_info.nombre_empresa}")

    # Manejo de frustracion "Otro"
    frustracion = st.session_state.Q12
    if frustracion == "Otro":
        frustracion = st.session_state.get("Q12_otro", "Otro")

    # ✅ TYPE-SAFE: motivacion siempre List[str]
    motivacion_list = st.session_state.Q4 if st.session_state.Q4 else []

    print(f"[DEBUG] Q4 type: {type(st.session_state.Q4)}")
    print(f"[DEBUG] Q4 value: {st.session_state.Q4}")
    print(f"[DEBUG] motivacion_list: {motivacion_list}")

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
    print(f"{'='*80}\n")

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
        collect_prospect_info()

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
