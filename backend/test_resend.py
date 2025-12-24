"""
Test de envío de emails con Resend - VERSION CORRECTA
Compatible con models.py actual
"""

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent))

from integrations.email_sender import EmailSender
from core.models import (
    DiagnosticResult,
    ProspectInfo,
    DiagnosticResponses,
    DiagnosticScore,
    MadurezDigital,
    CapacidadInversion,
    ViabilidadComercial,
    Tier,
    Arquetipo,
    QuickWin,
    ReunionPrep
)

def test_email():
    """Test completo con estructura real de diagnóstico"""

    print("\n🚀 Iniciando test de Resend con estructura completa...\n")

    try:
        # 1. Crear ProspectInfo
        prospect = ProspectInfo(
            nombre_empresa="Test Corp SA",
            sector="Tecnología",
            facturacion_rango="$1M-$5M USD",
            empleados_rango="10-50",
            contacto_nombre="Andrés",
            contacto_email="franklinnrodriguez83@gmail.com",
            contacto_telefono="300-123-4567",
            cargo="CEO",
            ciudad="Villavicencio"
        )

        # 2. Crear Responses (simplificado)
        responses = DiagnosticResponses(
            motivacion=["Reducir costos", "Automatizar procesos"],
            toma_decisiones="datos_informes",
            procesos_criticos="si_documentados",
            tareas_repetitivas="muchas",
            compartir_informacion="manual_email",
            equipo_tecnico="si_varios",
            capacidad_implementacion="si_apoyo",
            inversion_reciente="si_erp_crm",
            frustracion_principal="Procesos manuales lentos",
            urgencia="1_3_meses",
            proceso_aprobacion="gerente",
            presupuesto_rango="20_50M"
        )

        # 3. Crear Score (Tier A para test)
        madurez = MadurezDigital(
            decisiones_basadas_datos=8,
            procesos_estandarizados=7,
            sistemas_integrados=8,
            eficiencia_operativa=7
        )

        capacidad = CapacidadInversion(
            presupuesto_disponible=12,
            historial_inversion=8,
            tamano_empresa=4
        )

        viabilidad = ViabilidadComercial(
            problema_claro=9,
            urgencia_real=8,
            poder_decision=9
        )

        score = DiagnosticScore(
            madurez_digital=madurez,
            capacidad_inversion=capacidad,
            viabilidad_comercial=viabilidad,
            score_final=85,
            tier=Tier.A,
            confianza_clasificacion=0.92
        )

        # 4. Crear Arquetipo
        arquetipo = Arquetipo(
            tipo="ambitious_scaler",
            nombre="Escalador Ambicioso",
            descripcion="Empresa en crecimiento con visión clara de AI",
            frustraciones_tipicas=["Procesos manuales", "Falta de insights"],
            motivadores=["Eficiencia", "Ventaja competitiva"],
            objeciones_esperadas=["ROI", "Tiempo de implementación"],
            enfoque_comercial=["Casos de éxito", "Demo personalizado"],
            punto_entrada_ideal="Quick wins en 45 días",
            potencial_expansion="Alto",
            confianza=0.88
        )

        # 5. Quick Wins
        quick_wins = [
            QuickWin(
                titulo="Automatización de reportes",
                descripcion="Dashboard en tiempo real con IA",
                impacto_estimado="30% reducción tiempo reporting",
                tiempo_implementacion="45 días",
                inversion_aproximada="$25M COP"
            ),
            QuickWin(
                titulo="Chatbot atención cliente",
                descripcion="Automatizar FAQs comunes",
                impacto_estimado="60% reducción consultas repetitivas",
                tiempo_implementacion="30 días",
                inversion_aproximada="$15M COP"
            )
        ]

        # 6. Reunión Prep
        reunion = ReunionPrep(
            investigacion_previa=["LinkedIn de stakeholders", "Competidores"],
            materiales_llevar=["Casos de éxito", "ROI calculator"],
            preguntas_clave=["¿Qué proceso consume más tiempo?"],
            objeciones_probables={"ROI": "Mostramos payback en 6 meses"},
            insight_clave="Empresa lista para AI, Quick wins ideales",
            probabilidad_cierre=75
        )

        # 7. Crear DiagnosticResult completo
        result = DiagnosticResult(
            prospect_info=prospect,
            responses=responses,
            score=score,
            arquetipo=arquetipo,
            quick_wins=quick_wins,
            red_flags=[],
            insights=[],
            servicio_sugerido="Implementación Acelerada + Quick Wins",
            monto_sugerido_min=40000000,
            monto_sugerido_max=50000000,
            reunion_prep=reunion
        )

        # 8. Enviar email
        print(f"📤 Enviando email Tier {result.score.tier.value} a {prospect.contacto_email}...\n")

        sender = EmailSender()
        success = sender.send_confirmation_email(result, pdf_path=None)

        if success:
            print("\n✅ EMAIL ENVIADO CORRECTAMENTE")
            print(f"📧 Destinatario: {prospect.contacto_email}")
            print(f"🎯 Tier: {result.score.tier.value}")
            print(f"📊 Score: {result.score.score_final}/100")
            print(f"\n⚠️  Si no aparece en 1-2 minutos, revisa SPAM")
        else:
            print("\n❌ ERROR AL ENVIAR EMAIL")
            print("📋 Revisa los logs arriba para detalles")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        print("\n📋 Detalles técnicos:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_email()
