from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import hashlib
import time
import sys
import json
import traceback
from pathlib import Path

# Agregar path para imports
sys.path.append(str(Path(__file__).parent.parent))

from core.models import ProspectInfo, DiagnosticResponses, DiagnosticResult
from core.scoring_engine import ScoringEngine
from core.classifier import ArchetypeClassifier, InsightGenerator
from integrations.sheets_connector import SheetsConnector
from integrations.email_sender import EmailSender
from integrations.pdf_generator import PDFGenerator

router = APIRouter()

# ==================================================
# IDEMPOTENCY (Micro-función #1)
# ==================================================
processed_hashes = set()

def generate_submission_hash(email: str) -> str:
    window = int(time.time() / 300)
    key = f"{email}:{window}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def check_idempotency(email: str) -> bool:
    submission_hash = generate_submission_hash(email)
    if submission_hash in processed_hashes:
        return False
    processed_hashes.add(submission_hash)
    if len(processed_hashes) > 20:
        processed_hashes.clear()
    return True

# ==================================================
# PYDANTIC MODELS
# ==================================================
class DiagnosticRequest(BaseModel):
    nombre_empresa: str
    sector: str
    facturacion_rango: str
    empleados_rango: str
    contacto_nombre: str
    contacto_email: EmailStr
    contacto_telefono: Optional[str] = ""
    cargo: str
    ciudad: str
    Q4: List[str]
    Q5: str
    Q6: str
    Q7: str
    Q8: str
    Q9: str
    Q10: str
    Q11: str
    Q12: str
    Q12_otro: Optional[str] = ""
    Q13: str
    Q14: str
    Q15: str

class DiagnosticResponse(BaseModel):
    success: bool
    diagnostic_id: str
    tier: str
    score_total: int
    score_datos: int
    score_talento: int
    score_procesos: int
    score_infraestructura: int
    arquetipo: str
    servicio_sugerido: str
    monto_min: int
    monto_max: int
    timestamp: str
    email_sent: bool
    pdf_generated: bool

# ==================================================
# ENDPOINTS
# ==================================================
@router.get("/test")
async def test():
    return {"message": "API funcionando"}

@router.get("/questions")
async def get_questions():
    """
    Retorna las preguntas del diagnóstico desde questions.json
    Transforma estructura de bloques a array plano para el frontend
    """
    try:
        questions_path = Path(__file__).parent.parent / "data" / "questions.json"

        if not questions_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Questions file not found at {questions_path}"
            )

        with open(questions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions_list = []

        for bloque_key, bloque_data in data.items():
            if "preguntas" in bloque_data:
                for pregunta in bloque_data["preguntas"]:
                    question_obj = {
                        "id": pregunta["id"],
                        "text": pregunta["pregunta"],
                        "type": "multi-select" if pregunta["tipo"] == "multiselect" else "radio",
                        "options": pregunta["opciones"],
                        "required": pregunta.get("requerido", True)
                    }

                    if "helper" in pregunta:
                        question_obj["helper"] = pregunta["helper"]

                    if pregunta.get("tiene_otro", False):
                        question_obj["has_other"] = True

                    questions_list.append(question_obj)

        return {
            "success": True,
            "questions": questions_list
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Questions file not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON format in questions.json"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading questions: {str(e)}"
        )

@router.post("/diagnostic", response_model=DiagnosticResponse)
async def process_diagnostic(request: DiagnosticRequest):
    """Procesa diagnóstico completo"""

    # Idempotency check
    if not check_idempotency(request.contacto_email):
        raise HTTPException(
            status_code=429,
            detail="Diagnóstico procesado recientemente. Espere 5 minutos."
        )

    try:
        # Construir objetos del modelo
        prospect_info = ProspectInfo(
            nombre_empresa=request.nombre_empresa,
            sector=request.sector,
            facturacion_rango=request.facturacion_rango,
            empleados_rango=request.empleados_rango,
            contacto_nombre=request.contacto_nombre,
            contacto_email=request.contacto_email,
            contacto_telefono=request.contacto_telefono,
            cargo=request.cargo,
            ciudad=request.ciudad
        )

        # Manejar campo "Otro" en Q12
        frustracion = request.Q12
        if frustracion == "Otro":
            frustracion = request.Q12_otro or "Otro"

        responses = DiagnosticResponses(
            motivacion=request.Q4,
            toma_decisiones=request.Q5,
            procesos_criticos=request.Q6,
            tareas_repetitivas=request.Q7,
            compartir_informacion=request.Q8,
            equipo_tecnico=request.Q9,
            capacidad_implementacion=request.Q10,
            inversion_reciente=request.Q11,
            frustracion_principal=frustracion,
            urgencia=request.Q13,
            proceso_aprobacion=request.Q14,
            presupuesto_rango=request.Q15
        )

        # Scoring Engine
        print(f"[DIAGNOSTIC] Calculando scores...")
        engine = ScoringEngine()
        score = engine.calculate_full_score(responses, prospect_info)
        print(f"[DIAGNOSTIC] ✅ Score calculado: {score.score_final}/100")

        # Classifier
        print(f"[DIAGNOSTIC] Clasificando arquetipo...")
        classifier = ArchetypeClassifier()
        arquetipo = classifier.classify(score, responses, prospect_info)
        print(f"[DIAGNOSTIC] ✅ Arquetipo: {arquetipo.nombre} (Tier {score.tier.value})")

        # Insight Generator
        insight_gen = InsightGenerator()
        quick_wins = insight_gen.generate_quick_wins(score, responses, arquetipo)
        red_flags = insight_gen.generate_red_flags(score, responses, prospect_info)
        insights = insight_gen.generate_insights(score, responses, arquetipo)
        reunion_prep = insight_gen.generate_reunion_prep(score, responses, arquetipo, prospect_info)

        # Determinar servicio y rango de inversión
        if score.tier.value == "A":
            servicio = "Implementación Completa"
            monto_min, monto_max = 25000000, 45000000
        elif score.tier.value == "B":
            servicio = "Diagnóstico Profundo + Roadmap"
            monto_min, monto_max = 12000000, 25000000
        else:
            servicio = "Workshop Educativo"
            monto_min, monto_max = 0, 5000000

        # Construir resultado completo
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

        # ===== INTEGRACIÓN GOOGLE SHEETS (CON LOGS DETALLADOS) =====
        sheets_success = False
        try:
            print(f"\n{'='*70}")
            print(f"[SHEETS] Iniciando guardado en Google Sheets...")
            print(f"  Empresa: {prospect_info.nombre_empresa}")
            print(f"  Email: {prospect_info.contacto_email}")
            print(f"  Diagnostic ID: {result.diagnostic_id}")
            print(f"{'='*70}")

            connector = SheetsConnector()
            connector.save_diagnostic(result)
            sheets_success = True

            print(f"[SHEETS] ✅ GUARDADO EXITOSO")
            print(f"  Score: {score.score_final} | Tier: {score.tier.value}")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"\n{'='*70}")
            print(f"[SHEETS] ❌ ERROR CRÍTICO AL GUARDAR")
            print(f"  Empresa: {prospect_info.nombre_empresa}")
            print(f"  Error: {str(e)}")
            print(f"{'='*70}")
            print(f"[SHEETS] Stack trace completo:")
            traceback.print_exc()
            print(f"{'='*70}\n")
            # NO re-lanzar para que el diagnóstico continúe

        # ===== GENERACIÓN PDF (CON LOGS DETALLADOS) =====
        pdf_success = False
        pdf_path = None
        try:
            print(f"[PDF] Generando reporte PDF...")
            pdf_gen = PDFGenerator()
            pdf_path = pdf_gen.generate_prospect_pdf(result)
            pdf_success = True
            print(f"[PDF] ✅ Generado exitosamente: {pdf_path}")
        except Exception as e:
            print(f"[PDF] ❌ ERROR: {str(e)}")
            traceback.print_exc()

        # ===== EMAIL (TEMPORALMENTE DESHABILITADO) =====
        email_success = False
        try:
            print(f"[EMAIL] Iniciando envío con Resend...")
            email_sender = EmailSender()
            email_success = email_sender.send_confirmation_email(result, pdf_path)

            if email_success:
                print(f"[EMAIL] ✅ Email enviado exitosamente a {result.prospect_info.contacto_email}")
            else:
                print(f"[EMAIL] ⚠️ Email no se pudo enviar (ver detalles arriba)")

        except Exception as e:
            print(f"[EMAIL] ❌ ERROR CRÍTICO: {str(e)}")
            import traceback
            traceback.print_exc()


        # ===== RESPUESTA AL FRONTEND =====
        return DiagnosticResponse(
            success=sheets_success,
            diagnostic_id=result.diagnostic_id,
            tier=score.tier.value,
            score_total=score.score_final,
            score_datos=score.madurez_digital.decisiones_basadas_datos,
            score_talento=score.madurez_digital.procesos_estandarizados,
            score_procesos=score.madurez_digital.sistemas_integrados,
            score_infraestructura=score.madurez_digital.eficiencia_operativa,
            arquetipo=arquetipo.nombre,
            servicio_sugerido=servicio,
            monto_min=monto_min,
            monto_max=monto_max,
            timestamp=datetime.now().isoformat(),
            email_sent=email_success,
            pdf_generated=pdf_success
        )

    except Exception as e:
        print(f"\n{'='*70}")
        print(f"[DIAGNOSTIC] ❌ ERROR CRÍTICO EN PROCESAMIENTO")
        print(f"  Error: {str(e)}")
        print(f"{'='*70}")
        traceback.print_exc()
        print(f"{'='*70}\n")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diagnostic/{diagnostic_id}/pdf")
async def download_pdf(diagnostic_id: str):
    """Descargar PDF del diagnóstico"""
    pdf_path = Path(f"/tmp/ai_diagnostics/diagnostico_{diagnostic_id}.pdf")

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF no encontrado")

    return FileResponse(
        path=str(pdf_path),
        media_type='application/pdf',
        filename=f'Diagnostico_AI_{diagnostic_id}.pdf'
    )
