"""
Formulario de Diagnóstico AI Readiness - Aplicación Principal
Version: 5.7 PRODUCTION - Micro-optimizations Layer
Autor: Andrés - AI Consultant

ARCHITECTURE:
- Layer 1: State Initialization with Index Mapping
- Layer 2: Persistent Widget Binding
- Layer 3: Validation with State Recovery
- Layer 4: Micro-optimizations (NEW)
  * Idempotency protection
  * Circuit breaker pattern
  * Staleness detection

CHANGELOG v5.7:
- Added submission hash for idempotency (prevents duplicates)
- Implemented exponential backoff with circuit breaker for Google Sheets API
- Added staleness indicator for data freshness visibility
- Enhanced error recovery with local queue fallback
"""

import streamlit as st
import json
import re
import hashlib
import time
from datetime import datetime
from pathlib import Path
import sys
import traceback
from typing import Optional
from dataclasses import dataclass
import pickle

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
# MICRO-FUNCIÓN #1: IDEMPOTENCY PROTECTION
# ============================================================================

def generate_submission_hash(contact_email: str) -> str:
    """
    Genera hash único basado en email + timestamp (5min window)
    Previene duplicate submissions por doble-click o mala conexión

    Returns:
        Hash de 16 caracteres único por ventana de 5 minutos
    """
    window = int(time.time() / 300)  # 5min buckets
    key = f"{contact_email}:{window}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def check_submission_idempotency(email: str) -> bool:
    """
    Verifica si esta submission ya fue procesada en los últimos 5 minutos

    Returns:
        True si es seguro procesar, False si es duplicado
    """
    if 'processed_hashes' not in st.session_state:
        st.session_state.processed_hashes = set()

    submission_hash = generate_submission_hash(email)

    if submission_hash in st.session_state.processed_hashes:
        return False

    st.session_state.processed_hashes.add(submission_hash)

    # Cleanup old hashes (mantener solo últimos 20)
    if len(st.session_state.processed_hashes) > 20:
        st.session_state.processed_hashes = set(list(st.session_state.processed_hashes)[-20:])

    return True

# ============================================================================
# MICRO-FUNCIÓN #2: CIRCUIT BREAKER PATTERN
# ============================================================================

@dataclass
class CircuitBreakerState:
    failures: int = 0
    last_failure_time: Optional[float] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    max_failures: int = 3
    timeout: int = 60  # seconds

class SheetsCircuitBreaker:
    """
    Circuit breaker para Google Sheets API
    Protege contra rate limiting y cascading failures
    """

    def __init__(self):
        if 'circuit_breaker' not in st.session_state:
            st.session_state.circuit_breaker = CircuitBreakerState()
        self.state = st.session_state.circuit_breaker

    def can_attempt(self) -> tuple[bool, str]:
        """
        Verifica si podemos intentar llamada a API

        Returns:
            (puede_intentar, mensaje_error)
        """
        if self.state.state == "CLOSED":
            return True, ""

        if self.state.state == "OPEN":
            if time.time() - self.state.last_failure_time > self.state.timeout:
                self.state.state = "HALF_OPEN"
                return True, ""
            return False, f"Google Sheets API temporalmente no disponible. Reintente en {int(self.state.timeout - (time.time() - self.state.last_failure_time))}s"

        # HALF_OPEN state
        return True, ""

    def record_success(self):
        """Registra llamada exitosa y resetea estado"""
        self.state.failures = 0
        self.state.state = "CLOSED"
        self.state.last_failure_time = None

    def record_failure(self, error: Exception):
        """Registra falla y actualiza estado del circuito"""
        self.state.failures += 1
        self.state.last_failure_time = time.time()

        if self.state.failures >= self.state.max_failures:
            self.state.state = "OPEN"
            print(f"[CIRCUIT BREAKER] Estado OPEN - {self.state.failures} fallos consecutivos")

    def save_to_local_queue(self, result: DiagnosticResult):
        """
        Fallback: guarda resultado en local queue para retry manual
        """
        queue_path = Path(__file__).parent.parent / "data" / "failed_submissions.pkl"
        queue_path.parent.mkdir(exist_ok=True)

        queue = []
        if queue_path.exists():
            with open(queue_path, 'rb') as f:
                queue = pickle.load(f)

        queue.append({
            'timestamp': datetime.now().isoformat(),
            'result': result,
            'hash': generate_submission_hash(result.prospect_info.contacto_email)
        })

        with open(queue_path, 'wb') as f:
            pickle.dump(queue, f)

        print(f"[CIRCUIT BREAKER] Guardado en local queue: {result.prospect_info.nombre_empresa}")

def safe_sheets_save(result: DiagnosticResult) -> tuple[bool, str]:
    """
    Wrapper con circuit breaker y exponential backoff

    Returns:
        (success, error_message)
    """
    breaker = SheetsCircuitBreaker()

    can_attempt, error_msg = breaker.can_attempt()
    if not can_attempt:
        breaker.save_to_local_queue(result)
        return False, error_msg

    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            connector = SheetsConnector()
            connector.save_diagnostic(result)
            breaker.record_success()
            return True, ""

        except Exception as e:
            error_str = str(e)
            print(f"[SHEETS] Intento {attempt + 1}/{max_retries} falló: {error_str}")

            if "429" in error_str or "quota" in error_str.lower():
                breaker.record_failure(e)

                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"[SHEETS] Rate limit - esperando {delay}s antes de reintentar")
                    time.sleep(delay)
                else:
                    breaker.save_to_local_queue(result)
                    return False, "Google Sheets API rate limit excedido. Datos guardados localmente para procesamiento posterior."
            else:
                breaker.record_failure(e)
                return False, f"Error en Google Sheets: {error_str}"

    return False, "Máximo de reintentos alcanzado"

# ============================================================================
# MICRO-FUNCIÓN #3: STALENESS DETECTION
# ============================================================================

def show_data_freshness_indicator():
    """
    Indicador visual de frescura de datos
    Ayuda a tomar decisiones informadas sobre timing de contacto
    """
    if 'last_submission_time' not in st.session_state:
        return

    last_submit = st.session_state.last_submission_time
    staleness_seconds = (datetime.now() - last_submit).total_seconds()

    if staleness_seconds < 60:
        status_icon = "🟢"
        status_text = f"Procesado hace {int(staleness_seconds)}s"
        status_color = "success"
    elif staleness_seconds < 300:
        status_icon = "🟡"
        status_text = f"Procesado hace {int(staleness_seconds/60)} min"
        status_color = "warning"
    else:
        status_icon = "🔴"
        status_text = f"Procesado hace {int(staleness_seconds/60)} min"
        status_color = "error"

    col1, col2 = st.columns([3, 1])
    with col1:
        if status_color == "success":
            st.success(f"{status_icon} {status_text}")
        elif status_color == "warning":
            st.warning(f"{status_icon} {status_text}")
        else:
            st.error(f"{status_icon} {status_text}")

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

def get_index_safe(options_list, value, default_index=0):
    """
    Obtener índice de forma segura para selectbox.
    Retorna default_index si value no está en la lista.
    """
    try:
        if value and value in options_list:
            return options_list.index(value)
        return default_index
    except (ValueError, TypeError):
        return default_index

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
# GESTIÓN DE ESTADO - LAYER 1: INITIALIZATION WITH DEFAULTS
# ============================================================================

def init_session_state():
    """
    LAYER 1: State Initialization Layer
    Inicializar session_state con valores None para permitir validación explícita
    """
    if 'step' not in st.session_state:
        st.session_state.step = 0

    prospect_defaults = {
        'nombre_empresa': None,
        'sector': None,
        'facturacion_rango': None,
        'empleados_rango': None,
        'contacto_nombre': None,
        'contacto_email': None,
        'contacto_telefono': None,
        'cargo': None,
        'ciudad': None
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
# RECOLECCIÓN DE DATOS - LAYER 2: PERSISTENT WIDGET BINDING
# ============================================================================

def collect_prospect_info():
    """
    LAYER 2: UX Layer con persistencia de estado
    Utiliza index parameter para mantener selección en reruns
    """

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Información Empresarial</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        nombre_empresa = st.text_input(
            "Razón Social",
            value=st.session_state.nombre_empresa if st.session_state.nombre_empresa else "",
            placeholder="Ingrese el nombre legal de la empresa",
            help="Denominación oficial registrada"
        )
        st.session_state.nombre_empresa = nombre_empresa

        sector_index = get_index_safe(SECTORES, st.session_state.sector, 0)
        sector = st.selectbox(
            "Sector Industrial",
            options=SECTORES,
            index=sector_index,
            help="Categoría principal de actividad económica"
        )
        st.session_state.sector = sector

        facturacion_index = get_index_safe(RANGOS_FACTURACION, st.session_state.facturacion_rango, 0)
        facturacion = st.selectbox(
            "Facturación Anual",
            options=RANGOS_FACTURACION,
            index=facturacion_index,
            help="Ingresos consolidados del último ejercicio fiscal"
        )
        st.session_state.facturacion_rango = facturacion

        empleados_index = get_index_safe(RANGOS_EMPLEADOS, st.session_state.empleados_rango, 0)
        empleados = st.selectbox(
            "Plantilla de Personal",
            options=RANGOS_EMPLEADOS,
            index=empleados_index,
            help="Número total de colaboradores activos"
        )
        st.session_state.empleados_rango = empleados

        ciudad = st.text_input(
            "Ubicación Principal",
            value=st.session_state.ciudad if st.session_state.ciudad else "",
            placeholder="Ciudad de sede central",
            help="Localización de oficinas corporativas"
        )
        st.session_state.ciudad = ciudad

    with col2:
        contacto_nombre = st.text_input(
            "Nombre del Ejecutivo",
            value=st.session_state.contacto_nombre if st.session_state.contacto_nombre else "",
            placeholder="Nombre completo del representante",
            help="Persona responsable de la evaluación"
        )
        st.session_state.contacto_nombre = contacto_nombre

        contacto_email = st.text_input(
            "Email Corporativo",
            value=st.session_state.contacto_email if st.session_state.contacto_email else "",
            placeholder="correo@empresa.com",
            help="Dirección de correo empresarial"
        )
        st.session_state.contacto_email = contacto_email

        contacto_telefono = st.text_input(
            "Teléfono de Contacto",
            value=st.session_state.contacto_telefono if st.session_state.contacto_telefono else "",
            placeholder="+57 300 000 0000",
            help="Número directo (opcional)"
        )
        st.session_state.contacto_telefono = contacto_telefono

        cargo_index = get_index_safe(CARGOS, st.session_state.cargo, 0)
        cargo = st.selectbox(
            "Posición Ejecutiva",
            options=CARGOS,
            index=cargo_index,
            help="Rol dentro de la estructura organizacional"
        )
        st.session_state.cargo = cargo

    st.markdown('</div>', unsafe_allow_html=True)

    nombre_ok = nombre_empresa and nombre_empresa.strip() != ''
    sector_ok = sector and sector.strip() != ''
    facturacion_ok = facturacion and facturacion.strip() != ''
    empleados_ok = empleados and empleados.strip() != ''
    contacto_nombre_ok = contacto_nombre and contacto_nombre.strip() != ''
    email_ok = contacto_email and contacto_email.strip() != ''
    cargo_ok = cargo and cargo.strip() != ''
    ciudad_ok = ciudad and ciudad.strip() != ''

    all_filled = all([
        nombre_ok, sector_ok, facturacion_ok, empleados_ok,
        contacto_nombre_ok, email_ok, cargo_ok, ciudad_ok
    ])

    email_valid = validate_email(contacto_email) if email_ok else False

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

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💼 Viabilidad Financiera</div>', unsafe_allow_html=True)

    for pregunta in questions["bloque_3_viabilidad"]["preguntas"]:
        st.radio(
            pregunta["pregunta"],
            options=pregunta["opciones"],
            key=pregunta["id"]
        )

    st.markdown('</div>', unsafe_allow_html=True)

    q4_valid = len(st.session_state.get("Q4", [])) > 0
    radio_questions = ["Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15"]
    radio_valid = all(st.session_state.get(q) is not None for q in radio_questions)

    return q4_valid and radio_valid

# ============================================================================
# PROCESAMIENTO - LAYER 3: VALIDATION WITH STATE RECOVERY
# ============================================================================

def process_diagnostic():
    """
    LAYER 3: Validation Layer con recuperación defensiva
    """

    print(f"[PROCESS START] {datetime.now()}")

    facturacion = st.session_state.facturacion_rango
    empleados = st.session_state.empleados_rango
    sector = st.session_state.sector
    cargo = st.session_state.cargo
    nombre_empresa = st.session_state.nombre_empresa
    contacto_email = st.session_state.contacto_email
    ciudad = st.session_state.ciudad

    print(f"\n{'='*80}")
    print(f"[LAYER 3: VALIDATION]")
    print(f"{'='*80}")
    print(f"nombre_empresa: '{nombre_empresa}'")
    print(f"sector: '{sector}'")
    print(f"facturacion_rango: '{facturacion}'")
    print(f"empleados_rango: '{empleados}'")
    print(f"contacto_email: '{contacto_email}'")
    print(f"cargo: '{cargo}'")
    print(f"ciudad: '{ciudad}'")
    print(f"{'='*80}\n")

    if not all([facturacion, empleados, sector, cargo, nombre_empresa, contacto_email, ciudad]):
        st.error("❌ Error crítico: Datos incompletos detectados")
        print(f"[VALIDATION FAILED] Missing data detected")
        st.stop()

    print(f"[LAYER 3: VALIDATION PASSED] ✅")

    prospect_info = ProspectInfo(
        nombre_empresa=nombre_empresa.strip(),
        sector=sector,
        facturacion_rango=facturacion,
        empleados_rango=empleados,
        contacto_nombre=st.session_state.contacto_nombre.strip(),
        contacto_email=contacto_email.strip(),
        contacto_telefono=st.session_state.contacto_telefono.strip() if st.session_state.contacto_telefono else "",
        cargo=cargo,
        ciudad=ciudad.strip()
    )

    frustracion = st.session_state.Q12
    if frustracion == "Otro":
        frustracion = st.session_state.get("Q12_otro", "Otro")

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
    """Pantalla de resultados con staleness indicator"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("## ✅ Evaluación Completada")

    show_data_freshness_indicator()

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
    """Función principal con orquestación del flujo + micro-optimizations"""
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

                # MICRO-FUNCIÓN #1: Idempotency check
                if not check_submission_idempotency(st.session_state.contacto_email):
                    st.warning("⚠️ Este diagnóstico ya fue procesado recientemente (últimos 5 minutos). Espere antes de reenviar.")
                    st.stop()

                with st.spinner("Procesando evaluación estratégica..."):

                    print(f"\n{'='*80}")
                    print(f"[DIAGNOSTIC START] {datetime.now()}")
                    print(f"{'='*80}\n")

                    result = process_diagnostic()

                    # MICRO-FUNCIÓN #2: Circuit breaker con exponential backoff
                    save_success, error_msg = safe_sheets_save(result)

                    if save_success:
                        st.success("✅ Datos almacenados en Google Sheets")
                        print(f"[SHEETS] ✅ Guardado exitoso")
                    else:
                        st.error(f"❌ {error_msg}")
                        print(f"[SHEETS] ❌ ERROR: {error_msg}")

                        if "rate limit" in error_msg.lower() or "temporalmente no disponible" in error_msg.lower():
                            st.info("💾 Sus datos fueron guardados localmente. El equipo procesará su evaluación manualmente dentro de 24h.")

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

                        # MICRO-FUNCIÓN #3: Timestamp para staleness detection
                        st.session_state.last_submission_time = datetime.now()

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
