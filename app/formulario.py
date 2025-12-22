"""
Formulario de Diagnóstico AI Readiness - Aplicación Principal
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import sys

# Agregar path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from app.config import *
from core.models import ProspectInfo, DiagnosticResponses
from core.scoring_engine import ScoringEngine
from core.classifier import ArchetypeClassifier, InsightGenerator
from integrations.sheets_connector import SheetsConnector
from integrations.pdf_generator import PDFGenerator
from integrations.email_sender import EmailSender

# Configuración de página
st.set_page_config(
    page_title="Diagnóstico AI Readiness",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
# CSS personalizado - Sistema de Diseño Profesional
st.markdown("""
<style>
    /* ============================================
       VARIABLES DE DISEÑO - Design Tokens
       ============================================ */
    :root {
        /* Colores principales */
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-50: #eff6ff;

        /* Neutrales */
        --gray-900: #111827;
        --gray-800: #1f2937;
        --gray-700: #374151;
        --gray-600: #4b5563;
        --gray-500: #6b7280;
        --gray-400: #9ca3af;
        --gray-300: #d1d5db;
        --gray-200: #e5e7eb;
        --gray-100: #f3f4f6;
        --gray-50: #f9fafb;

        /* Semánticos */
        --success-600: #059669;
        --success-50: #ecfdf5;
        --warning-600: #d97706;
        --warning-50: #fffbeb;
        --error-600: #dc2626;
        --error-50: #fef2f2;

        /* Espaciado (8px grid) */
        --space-1: 0.25rem;  /* 4px */
        --space-2: 0.5rem;   /* 8px */
        --space-3: 0.75rem;  /* 12px */
        --space-4: 1rem;     /* 16px */
        --space-5: 1.25rem;  /* 20px */
        --space-6: 1.5rem;   /* 24px */
        --space-8: 2rem;     /* 32px */
        --space-10: 2.5rem;  /* 40px */
        --space-12: 3rem;    /* 48px */
        --space-16: 4rem;    /* 64px */

        /* Tipografía */
        --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --font-display: "Inter", var(--font-sans);

        /* Sombras */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

        /* Border radius */
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
    }

    /* ============================================
       RESET & BASE
       ============================================ */
    .main {
        background: linear-gradient(135deg, var(--gray-50) 0%, #ffffff 100%);
        font-family: var(--font-sans);
    }

    .block-container {
        max-width: 1200px;
        padding-top: var(--space-8);
        padding-bottom: var(--space-16);
    }

    /* ============================================
       HEADER PRINCIPAL
       ============================================ */
    .main-header {
        font-family: var(--font-display);
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: var(--space-4);
        line-height: 1.2;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-size: 1.25rem;
        color: var(--gray-600);
        margin-bottom: var(--space-10);
        font-weight: 400;
        line-height: 1.6;
    }

    /* ============================================
       BARRA DE PROGRESO MEJORADA
       ============================================ */
    .progress-container {
        background: white;
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin-bottom: var(--space-8);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
    }

    .progress-text {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--gray-700);
        margin-bottom: var(--space-3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .progress-step {
        color: var(--primary-600);
        font-size: 1.125rem;
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-600) 0%, var(--primary-700) 100%);
        border-radius: var(--radius-lg);
        height: 12px;
    }

    .stProgress > div > div {
        background-color: var(--gray-200);
        border-radius: var(--radius-lg);
        height: 12px;
    }

    /* ============================================
       SECCIONES
       ============================================ */
    .section-header {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--gray-900);
        margin-top: var(--space-12);
        margin-bottom: var(--space-6);
        padding-bottom: var(--space-4);
        border-bottom: 3px solid var(--primary-600);
        display: flex;
        align-items: center;
        gap: var(--space-3);
    }

    .section-card {
        background: white;
        border-radius: var(--radius-xl);
        padding: var(--space-8);
        margin-bottom: var(--space-6);
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--gray-200);
        transition: all 0.3s ease;
    }

    .section-card:hover {
        box-shadow: var(--shadow-xl);
        transform: translateY(-2px);
    }

    /* ============================================
       INPUTS & FORMS
       ============================================ */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        border-radius: var(--radius-md) !important;
        border: 2px solid var(--gray-300) !important;
        font-size: 1rem !important;
        padding: var(--space-3) var(--space-4) !important;
        transition: all 0.2s ease !important;
        background: white !important;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within,
    .stMultiSelect > div > div > div:focus-within {
        border-color: var(--primary-600) !important;
        box-shadow: 0 0 0 3px var(--primary-50) !important;
        outline: none !important;
    }

    /* Labels de inputs */
    .stTextInput > label,
    .stSelectbox > label,
    .stMultiSelect > label {
        font-size: 0.9375rem !important;
        font-weight: 600 !important;
        color: var(--gray-800) !important;
        margin-bottom: var(--space-2) !important;
    }

    /* ============================================
       RADIO BUTTONS
       ============================================ */
    .stRadio > label {
        font-size: 1.0625rem !important;
        font-weight: 600 !important;
        color: var(--gray-900) !important;
        margin-bottom: var(--space-4) !important;
    }

    .stRadio > div {
        background: var(--gray-50);
        padding: var(--space-4);
        border-radius: var(--radius-lg);
        border: 1px solid var(--gray-200);
    }

    .stRadio > div > label {
        background: white;
        padding: var(--space-4);
        border-radius: var(--radius-md);
        margin-bottom: var(--space-2);
        border: 2px solid var(--gray-200);
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .stRadio > div > label:hover {
        border-color: var(--primary-600);
        background: var(--primary-50);
        transform: translateX(4px);
    }

    /* ============================================
       BOTONES
       ============================================ */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-700) 100%);
        color: white;
        font-weight: 700;
        font-size: 1.125rem;
        padding: var(--space-4) var(--space-8);
        border-radius: var(--radius-lg);
        border: none;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        letter-spacing: 0.025em;
        text-transform: none;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-700) 0%, var(--primary-600) 100%);
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* ============================================
       ALERTAS & MENSAJES
       ============================================ */
    .stAlert {
        border-radius: var(--radius-lg);
        border-left-width: 4px;
        padding: var(--space-5);
        font-size: 1rem;
        line-height: 1.6;
    }

    .stSuccess {
        background-color: var(--success-50);
        border-left-color: var(--success-600);
    }

    .stWarning {
        background-color: var(--warning-50);
        border-left-color: var(--warning-600);
    }

    .stInfo {
        background-color: var(--primary-50);
        border-left-color: var(--primary-600);
    }

    /* ============================================
       MÉTRICAS
       ============================================ */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary-600);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--gray-600);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="metric-container"] {
        background: white;
        padding: var(--space-6);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
    }

    /* ============================================
       EXPANDER
       ============================================ */
    .streamlit-expanderHeader {
        background-color: var(--gray-100);
        border-radius: var(--radius-md);
        font-weight: 600;
        color: var(--gray-800);
        padding: var(--space-4);
    }

    .streamlit-expanderHeader:hover {
        background-color: var(--gray-200);
    }

    /* ============================================
       SPINNER
       ============================================ */
    .stSpinner > div {
        border-color: var(--primary-600);
        border-right-color: transparent;
    }

    /* ============================================
       COLUMNAS
       ============================================ */
    [data-testid="column"] {
        padding: var(--space-2);
    }

    /* ============================================
       TRUST ELEMENTS
       ============================================ */
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        background: white;
        padding: var(--space-3) var(--space-5);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--gray-200);
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--gray-700);
        margin-right: var(--space-3);
        margin-bottom: var(--space-3);
    }

    .security-notice {
        background: linear-gradient(135deg, var(--gray-50) 0%, white 100%);
        border: 2px solid var(--gray-200);
        border-radius: var(--radius-lg);
        padding: var(--space-5);
        margin-top: var(--space-8);
        font-size: 0.875rem;
        color: var(--gray-600);
        text-align: center;
    }

    /* ============================================
       RESPONSIVE
       ============================================ */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }

        .sub-header {
            font-size: 1rem;
        }

        .section-header {
            font-size: 1.5rem;
        }

        .section-card {
            padding: var(--space-6);
        }

        [data-testid="stMetricValue"] {
            font-size: 2rem;
        }
    }

    /* ============================================
       ANIMACIONES
       ============================================ */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .section-card,
    .progress-container {
        animation: fadeInUp 0.6s ease-out;
    }

    /* ============================================
       HELPER TEXT
       ============================================ */
    .stMarkdown small {
        color: var(--gray-500);
        font-size: 0.875rem;
    }

    /* ============================================
       HIDE STREAMLIT BRANDING
       ============================================ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# Cargar preguntas
@st.cache_data
def load_questions():
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    with open(questions_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ============================================================================
# CORRECCIÓN CRÍTICA: Inicialización completa de session_state
# ============================================================================
def init_session_state():
    """Inicializar TODAS las variables de session_state"""

    # Control de flujo
    if 'step' not in st.session_state:
        st.session_state.step = 0

    # Información de prospecto - valores por defecto vacíos
    prospect_defaults = {
        'nombre_empresa': '',
        'sector': '',
        'facturacion': '',
        'empleados': '',
        'contacto_nombre': '',
        'contacto_email': '',
        'contacto_telefono': '',
        'cargo': '',
        'ciudad': ''
    }

    for key, default in prospect_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Respuestas del diagnóstico
    diagnostic_defaults = {
        'Q4': [],      # multiselect
        'Q5': None,
        'Q6': None,
        'Q7': None,
        'Q8': None,
        'Q9': None,
        'Q10': None,
        'Q11': None,
        'Q12': None,
        'Q12_otro': '',  # campo condicional
        'Q13': None,
        'Q14': None,
        'Q15': None
    }

    for key, default in diagnostic_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Resultado final
    if 'result' not in st.session_state:
        st.session_state.result = None

def show_header():
    """Mostrar header principal"""
    st.markdown('<div class="main-header">Diagnóstico AI Readiness</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Descubra el potencial de IA en su empresa en solo 10 minutos</div>',
        unsafe_allow_html=True
    )

def show_progress_bar(current_step, total_steps):
    """Mostrar barra de progreso"""
    progress = (current_step + 1) / total_steps
    percentage = int(progress * 100)

    steps = ["Información de Contacto", "Diagnóstico", "Confirmación"]

    def show_progress_bar(current_step, total_steps):
    """Mostrar barra de progreso profesional"""
    progress = (current_step + 1) / total_steps
    percentage = int(progress * 100)

    steps = ["Información de Contacto", "Diagnóstico", "Confirmación"]

    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-text">
            <span>Paso {current_step + 1} de {total_steps}: <strong>{steps[current_step]}</strong></span>
            <span class="progress-step">{percentage}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)

def collect_prospect_info():
    """Recolectar información básica del prospecto"""
    st.markdown('<div class="section-header">📋 Información de Contacto</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        nombre_empresa = st.text_input(
            "Nombre de la empresa*",
            key="nombre_empresa",
            placeholder="Ej: Almacenes El Progreso"
        )

        sector = st.selectbox(
            "Sector / Industria*",
            options=SECTORES,
            key="sector"
        )

        facturacion = st.selectbox(
            "Facturación anual aproximada*",
            options=RANGOS_FACTURACION,
            key="facturacion"
        )

        empleados = st.selectbox(
            "Número de empleados*",
            options=RANGOS_EMPLEADOS,
            key="empleados"
        )

    with col2:
        contacto_nombre = st.text_input(
            "Su nombre*",
            key="contacto_nombre",
            placeholder="Ej: Carlos Mendoza"
        )

        contacto_email = st.text_input(
            "Email de contacto*",
            key="contacto_email",
            placeholder="Ej: carlos@empresa.com"
        )

        contacto_telefono = st.text_input(
            "Teléfono (opcional)",
            key="contacto_telefono",
            placeholder="Ej: +57 300 123 4567"
        )

        cargo = st.selectbox(
            "Su cargo*",
            options=CARGOS,
            key="cargo"
        )

        ciudad = st.text_input(
            "Ciudad principal de operación*",
            key="ciudad",
            placeholder="Ej: Villavicencio"
        )

    # Validar campos requeridos - usar .strip() para evitar espacios en blanco
    required_fields = [
        nombre_empresa.strip(),
        sector,
        facturacion,
        empleados,
        contacto_nombre.strip(),
        contacto_email.strip(),
        cargo,
        ciudad.strip()
    ]

    return all(required_fields)

def show_diagnostic_questions():
    """Mostrar preguntas del diagnóstico"""
    questions = load_questions()

    # Bloque 1: Identificación
    st.markdown('<div class="section-header">🎯 ¿Qué lo motiva?</div>', unsafe_allow_html=True)

    q4_opciones = questions["bloque_1_identificacion"]["preguntas"][0]["opciones"]
    motivacion = st.multiselect(
        "¿Qué lo trae aquí hoy?* (puede seleccionar varias opciones)",
        options=q4_opciones,
        key="Q4"
    )

    # Bloque 2: Diagnóstico Operativo
    st.markdown('<div class="section-header">🔍 Su Operación Actual</div>', unsafe_allow_html=True)

    for pregunta in questions["bloque_2_diagnostico"]["preguntas"]:
        q_id = pregunta["id"]
        helper = pregunta.get("helper", "")

        if pregunta.get("tiene_otro"):
            # Radio con opción "Otro"
            opciones = pregunta["opciones"] + ["Otro"]
            respuesta = st.radio(
                pregunta["pregunta"],
                options=opciones,
                key=q_id,
                help=helper if helper else None
            )

            if respuesta == "Otro":
                otro_texto = st.text_input(
                    "Por favor especifique:",
                    key=f"{q_id}_otro"
                )
        else:
            st.radio(
                pregunta["pregunta"],
                options=pregunta["opciones"],
                key=q_id,
                help=helper if helper else None
            )

    # Bloque 3: Viabilidad Comercial
    st.markdown('<div class="section-header">💼 Viabilidad y Presupuesto</div>', unsafe_allow_html=True)

    for pregunta in questions["bloque_3_viabilidad"]["preguntas"]:
        st.radio(
            pregunta["pregunta"],
            options=pregunta["opciones"],
            key=pregunta["id"]
        )

    # Validar que todas las preguntas estén respondidas
    # Q4 es multiselect, debe tener al menos 1 elemento
    q4_valid = len(st.session_state.get("Q4", [])) > 0

    # Q5-Q15 son radio buttons, deben ser != None
    radio_questions = ["Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15"]
    radio_valid = all(st.session_state.get(q) is not None for q in radio_questions)

    return q4_valid and radio_valid

def process_diagnostic():
    """Procesar el diagnóstico completo"""

    # Crear objetos de datos
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

    # Manejar respuesta "Otro" en Q12
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

    # Calcular scores
    engine = ScoringEngine()
    score = engine.calculate_full_score(responses, prospect_info)

    # Clasificar arquetipo
    classifier = ArchetypeClassifier()
    arquetipo = classifier.classify(score, responses, prospect_info)

    # Generar insights
    insight_gen = InsightGenerator()
    quick_wins = insight_gen.generate_quick_wins(score, responses, arquetipo)
    red_flags = insight_gen.generate_red_flags(score, responses, prospect_info)
    insights = insight_gen.generate_insights(score, responses, arquetipo)
    reunion_prep = insight_gen.generate_reunion_prep(score, responses, arquetipo, prospect_info)

    # Determinar servicio y monto sugerido
    if score.tier.value == "A":
        servicio = "Implementación Completa"
        monto_min, monto_max = 25000000, 45000000
    elif score.tier.value == "B":
        servicio = "Diagnóstico Profundo + Roadmap"
        monto_min, monto_max = 12000000, 25000000
    else:
        servicio = "Workshop Educativo"
        monto_min, monto_max = 0, 5000000

    # Crear resultado completo
    from core.models import DiagnosticResult
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

def show_confirmation_screen(result):
    """Mostrar pantalla de confirmación al prospecto"""

    st.markdown("## ✅ ¡Diagnóstico completado!")

    st.success(f"""
    Gracias **{result.prospect_info.contacto_nombre}** por completar el diagnóstico.

    Hemos analizado la información de **{result.prospect_info.nombre_empresa}** y
    identificamos oportunidades específicas para mejorar su operación con IA.
    """)

    st.markdown("### 📊 Resumen preliminar")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Madurez Digital",
            f"{result.score.madurez_digital.score_total}/40"
        )

    with col2:
        st.metric(
            "Capacidad de Inversión",
            f"{result.score.capacidad_inversion.score_total}/30"
        )

    with col3:
        st.metric(
            "Viabilidad Comercial",
            f"{result.score.viabilidad_comercial.score_total}/30"
        )

    st.markdown("### 🎯 Próximos pasos")

    st.info(f"""
    **Lo contactaremos en las próximas 48 horas** para:

    1. Compartir el análisis completo de su diagnóstico
    2. Mostrarle casos de éxito relevantes para su sector
    3. Presentar una propuesta específica para {result.prospect_info.nombre_empresa}

    Recibirá un email en **{result.prospect_info.contacto_email}** con un resumen
    de este diagnóstico.
    """)

    if st.button("🔄 Realizar otro diagnóstico"):
        # Limpiar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    """Función principal de la aplicación"""

    # ============================================================================
    # CRÍTICO: Inicializar ANTES de cualquier otra operación
    # ============================================================================
    init_session_state()
    show_header()

    # Determinar qué mostrar según el step
    if st.session_state.step == 0:
        # Paso 1: Información de contacto
        show_progress_bar(0, 2)

        if collect_prospect_info():
            if st.button("Continuar al diagnóstico →"):
                st.session_state.step = 1
                st.rerun()  # ✅ Correcto: st.rerun() en vez de st.experimental_rerun()
        else:
            st.warning("⚠️ Por favor complete todos los campos marcados con *")

    elif st.session_state.step == 1:
        # Paso 2: Preguntas de diagnóstico
        show_progress_bar(1, 2)

        if show_diagnostic_questions():
            if st.button("Enviar diagnóstico"):
                with st.spinner("Procesando su diagnóstico..."):
                    # Procesar diagnóstico
                    result = process_diagnostic()

                    # Guardar en Google Sheets
                    try:
                        connector = SheetsConnector()
                        connector.save_diagnostic(result)
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

                    # Generar PDF
                    try:
                        pdf_gen = PDFGenerator()
                        pdf_path = pdf_gen.generate_prospect_pdf(result)
                    except Exception as e:
                        st.error(f"Error al generar PDF: {e}")
                        pdf_path = None

                    # Enviar email
                    try:
                        email_sender = EmailSender()
                        email_sender.send_confirmation_email(result, pdf_path)
                    except Exception as e:
                        st.error(f"Error al enviar email: {e}")

                    # Guardar resultado en session state
                    st.session_state.result = result
                    st.session_state.step = 2
                    st.rerun()  # ✅ Correcto
        else:
            st.warning("⚠️ Por favor responda todas las preguntas para continuar")

    elif st.session_state.step == 2:
        # Paso 3: Confirmación
        show_confirmation_screen(st.session_state.result)

if __name__ == "__main__":
    main()
