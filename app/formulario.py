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
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .progress-text {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    .question-label {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)

# Cargar preguntas
@st.cache_data
def load_questions():
    questions_path = Path(__file__).parent.parent / "data" / "questions.json"
    with open(questions_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Inicializar session state
def init_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'prospect_info' not in st.session_state:
        st.session_state.prospect_info = {}

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
    st.markdown(
        f'<div class="progress-text">Progreso: {int(progress * 100)}% completado</div>',
        unsafe_allow_html=True
    )
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

    # Validar campos requeridos
    required_fields = [
        nombre_empresa, sector, facturacion, empleados,
        contacto_nombre, contacto_email, cargo, ciudad
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
    required_questions = ["Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13", "Q14", "Q15"]
    all_answered = all(st.session_state.get(q) for q in required_questions)

    return all_answered

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
        st.experimental_rerun()

def main():
    """Función principal de la aplicación"""

    init_session_state()
    show_header()

    # Determinar qué mostrar según el step
    if st.session_state.step == 0:
        # Paso 1: Información de contacto
        show_progress_bar(0, 2)

        if collect_prospect_info():
            if st.button("Continuar al diagnóstico →"):
                st.session_state.step = 1
                st.experimental_rerun()
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
                    st.experimental_rerun()
        else:
            st.warning("⚠️ Por favor responda todas las preguntas para continuar")

    elif st.session_state.step == 2:
        # Paso 3: Confirmación
        show_confirmation_screen(st.session_state.result)

if __name__ == "__main__":
    main()
