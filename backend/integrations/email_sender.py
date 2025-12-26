"""
Sistema de envío de emails - Version 3.2 RESEND
FIXED: Logs detallados + Mejor manejo de errores + Nueva API Key
"""

import resend
from pathlib import Path
from typing import Optional
import traceback
from datetime import datetime
import sys

# Importar adaptador de secrets
sys.path.append(str(Path(__file__).parent.parent))
from core.config import secrets
from core.models import DiagnosticResult


class EmailSender:
    """Envío de emails automatizados según Tier usando Resend"""

    def __init__(self):
        """Inicializar con Resend API Key"""
        email_config = secrets.get("email", {})

        # Obtener API key de Resend
        self.api_key = email_config.get("resend_api_key")
        if not self.api_key:
            # Fallback: buscar en root level del secrets
            self.api_key = secrets.get("resend_api_key")

        if not self.api_key:
            raise ValueError("RESEND_API_KEY no encontrada en secrets/env")

        # Configurar Resend
        resend.api_key = self.api_key

        # Email remitente (usar el de Resend por defecto o uno verificado)
        self.from_email = email_config.get("from", "onboarding@resend.dev")
        self.sender_name = "Andrés - AI Consulting"

        # Testing mode
        self.testing_mode = secrets.get("EMAIL_TESTING_MODE") == "true"
        self.testing_recipient = secrets.get("EMAIL_TESTING_RECIPIENT", "franklinnrodriguez83@gmail.com")

        print(f"\n{'='*70}")
        print(f"[EMAIL INIT] Inicializando EmailSender...")
        print(f"{'='*70}")
        print(f"  API Key encontrada: {bool(self.api_key)}")
        print(f"  API Key (primeros 10 chars): {self.api_key[:10] if self.api_key else 'NONE'}...")
        print(f"  From email: {self.from_email}")
        print(f"  Sender name: {self.sender_name}")
        print(f"  Testing mode: {self.testing_mode}")
        if self.testing_mode:
            print(f"  ⚠️ MODO TESTING ACTIVADO")
            print(f"  Todos los emails irán a: {self.testing_recipient}")
        print(f"{'='*70}\n")

    def send_confirmation_email(
        self,
        result: DiagnosticResult,
        pdf_path: Optional[Path] = None
    ) -> bool:
        """Enviar email de confirmación según Tier"""

        try:
            # Determinar destinatario real
            recipient_email = self.testing_recipient if self.testing_mode else result.prospect_info.contacto_email

            print(f"\n{'='*70}")
            print(f"[EMAIL START] Preparando envío de email...")
            print(f"{'='*70}")
            print(f"  Cliente: {result.prospect_info.nombre_empresa}")
            print(f"  Email destino (real): {result.prospect_info.contacto_email}")
            if self.testing_mode:
                print(f"  ⚠️ MODO TESTING: Redirigiendo a {self.testing_recipient}")
            print(f"  Tier: {result.score.tier.value}")
            print(f"  Score: {result.score.score_final}/100")
            print(f"{'='*70}\n")

            # Obtener contenido según Tier
            if result.score.tier.value == "A":
                subject, html_body = self._get_tier_a_content(result)
            elif result.score.tier.value == "B":
                subject, html_body = self._get_tier_b_content(result)
            else:
                subject, html_body = self._get_tier_c_content(result)

            # Agregar banner de testing si está en modo testing
            if self.testing_mode:
                html_body = f"""
                <div style="background: #fff3cd; padding: 15px; margin-bottom: 20px; border-left: 4px solid #ffc107; border-radius: 4px;">
                    <strong style="color: #856404;">⚠️ MODO TESTING - EMAIL DE PRUEBA</strong><br/>
                    <span style="color: #856404;">Este email estaba destinado a: <strong>{result.prospect_info.contacto_email}</strong></span><br/>
                    <span style="color: #856404;">Empresa: <strong>{result.prospect_info.nombre_empresa}</strong></span><br/>
                    <span style="color: #856404;">Sector: <strong>{result.prospect_info.sector}</strong></span>
                </div>
                {html_body}
                """

            # Preparar parámetros del email
            email_params = {
                "from": f"{self.sender_name} <{self.from_email}>",
                "to": [recipient_email],
                "subject": f"[TEST] {subject}" if self.testing_mode else subject,
                "html": html_body,
            }

            print(f"[EMAIL] Parámetros preparados:")
            print(f"  From: {email_params['from']}")
            print(f"  To: {email_params['to']}")
            print(f"  Subject: {email_params['subject'][:50]}...")

            # Adjuntar PDF si existe
            if pdf_path and pdf_path.exists():
                with open(pdf_path, 'rb') as f:
                    pdf_content = f.read()

                email_params["attachments"] = [{
                    "filename": f"Diagnostico_AI_{result.prospect_info.nombre_empresa}.pdf",
                    "content": list(pdf_content)  # Resend requiere lista de bytes
                }]
                print(f"[EMAIL PDF] Adjuntando PDF: {pdf_path}")
            else:
                print(f"[EMAIL PDF] No se adjuntará PDF (no existe o no se proporcionó)")

            # Enviar con Resend
            print(f"\n[EMAIL] Llamando a Resend API...")
            print(f"  API Key configurada: {bool(resend.api_key)}")
            print(f"  API Key (primeros 10): {resend.api_key[:10]}...")

            response = resend.Emails.send(email_params)

            print(f"\n{'='*70}")
            print(f"[EMAIL SUCCESS] ✅ EMAIL ENVIADO EXITOSAMENTE")
            print(f"{'='*70}")
            print(f"  Destinatario: {recipient_email}")
            print(f"  Response ID: {response.get('id', 'N/A')}")
            print(f"  Response completo: {response}")

            if self.testing_mode:
                print(f"\n  ⚠️ MODO TESTING ACTIVO")
                print(f"  Revisa la bandeja de: {self.testing_recipient}")
                print(f"  También revisa SPAM/PROMOCIONES")

            print(f"{'='*70}\n")

            return True

        except Exception as e:
            print(f"\n{'='*70}")
            print(f"[EMAIL ERROR] ❌ ERROR CRÍTICO AL ENVIAR EMAIL")
            print(f"{'='*70}")
            print(f"  Timestamp: {datetime.now()}")
            print(f"  Empresa: {result.prospect_info.nombre_empresa}")
            print(f"  Email destino: {result.prospect_info.contacto_email}")
            print(f"  Tier: {result.score.tier.value}")
            print(f"  Testing mode: {self.testing_mode}")
            print(f"  API Key presente: {bool(self.api_key)}")
            print(f"  API Key (primeros 10): {self.api_key[:10] if self.api_key else 'NONE'}...")
            print(f"  Error type: {type(e).__name__}")
            print(f"  Error message: {str(e)}")
            print(f"{'='*70}")
            print(f"[EMAIL ERROR] Stack trace completo:")
            print(traceback.format_exc())
            print(f"{'='*70}\n")

            # Mensajes de ayuda específicos según el error
            error_str = str(e).lower()
            if "api" in error_str or "key" in error_str or "unauthorized" in error_str or "401" in error_str:
                print(f"[EMAIL HELP] 💡 POSIBLE CAUSA: API Key inválida o expirada")
                print(f"  Solución: Genera una nueva API Key en https://resend.com/api-keys")
                print(f"  Actualiza RESEND_API_KEY en tu archivo .env")
            elif "rate" in error_str or "limit" in error_str or "429" in error_str:
                print(f"[EMAIL HELP] 💡 POSIBLE CAUSA: Límite de envíos excedido")
                print(f"  Solución: Espera o actualiza tu plan en Resend")
            elif "domain" in error_str or "verify" in error_str:
                print(f"[EMAIL HELP] 💡 POSIBLE CAUSA: Dominio no verificado")
                print(f"  Solución: Usa onboarding@resend.dev o verifica tu dominio")

            return False

    def _get_tier_a_content(self, result: DiagnosticResult) -> tuple:
        """Template para Tier A"""
        subject = "✅ Resultados de su diagnóstico AI - Oportunidades identificadas"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2563eb;">Hola {result.prospect_info.contacto_nombre},</h2>

            <p>Gracias por completar el diagnóstico AI Readiness para <strong>{result.prospect_info.nombre_empresa}</strong>.</p>

            <p>Tengo excelentes noticias: <strong>su empresa está en una posición favorable para implementar IA
            que genere impacto real en los próximos 6 meses.</strong></p>

            <h3 style="color: #2563eb;">🎯 Oportunidades Identificadas</h3>

            <p>Basado en su diagnóstico, identifiqué <strong>3 oportunidades específicas</strong> donde la IA
            podría reducir costos operativos inmediatamente:</p>

            <ol>
                <li><strong>{result.quick_wins[0].titulo if result.quick_wins else 'Automatización de procesos críticos'}</strong>
                    <br/>Impacto: {result.quick_wins[0].impacto_estimado if result.quick_wins else 'Reducción significativa de costos'}
                </li>
                <li><strong>{result.quick_wins[1].titulo if len(result.quick_wins) > 1 else 'Optimización de operaciones'}</strong>
                    <br/>Impacto: {result.quick_wins[1].impacto_estimado if len(result.quick_wins) > 1 else 'Mejora de eficiencia'}
                </li>
                <li>Dashboard de inteligencia operativa en tiempo real</li>
            </ol>

            <h3 style="color: #2563eb;">📞 Próximos Pasos</h3>

            <p>Lo contactaré en las próximas <strong>48 horas</strong> para agendar una reunión de 45 minutos donde le mostraré:</p>

            <ul>
                <li>Casos reales de empresas como la suya</li>
                <li>ROI estimado específico para {result.prospect_info.nombre_empresa}</li>
                <li>Plan de implementación en 90 días con quick wins visibles en 45 días</li>
            </ul>

            <p>Adjunto encontrará un resumen ejecutivo de su diagnóstico.</p>

            <p style="margin-top: 30px;">Saludos,<br/>
            <strong>Andrés</strong><br/>
            AI Consulting<br/>
            negusnett@gmail.com</p>
        </body>
        </html>
        """

        return subject, body

    def _get_tier_b_content(self, result: DiagnosticResult) -> tuple:
        """Template para Tier B"""
        subject = "📊 Resultados de su diagnóstico AI"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2563eb;">Hola {result.prospect_info.contacto_nombre},</h2>

            <p>Gracias por completar el diagnóstico AI Readiness para <strong>{result.prospect_info.nombre_empresa}</strong>.</p>

            <p>He analizado su situación y veo <strong>oportunidades interesantes</strong> para mejorar
            la eficiencia operativa con IA.</p>

            <h3 style="color: #2563eb;">📋 Recomendación</h3>

            <p>Antes de implementar IA, le sugiero que consideremos:</p>

            <ol>
                <li>Un diagnóstico profundo de procesos (inversión: $12M COP)</li>
                <li>Identificación de quick wins de bajo riesgo</li>
                <li>Roadmap de implementación gradual</li>
            </ol>

            <p>Este enfoque nos permite validar el ROI antes de inversiones mayores.</p>

            <p>Adjunto encontrará un resumen de su diagnóstico con áreas de oportunidad.</p>

            <p>¿Le gustaría que conversemos sobre esto?</p>

            <p style="margin-top: 30px;">Saludos,<br/>
            <strong>Andrés</strong><br/>
            AI Consulting<br/>
            negusnett@gmail.com</p>
        </body>
        </html>
        """

        return subject, body

    def _get_tier_c_content(self, result: DiagnosticResult) -> tuple:
        """Template para Tier C"""
        subject = "📚 Recursos para iniciar su transformación digital"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #2563eb;">Hola {result.prospect_info.contacto_nombre},</h2>

            <p>Gracias por completar el diagnóstico AI Readiness.</p>

            <p>Basado en su situación actual, le recomiendo <strong>primero fortalecer
            las bases digitales</strong> antes de implementar IA.</p>

            <h3 style="color: #2563eb;">📚 Recursos Útiles</h3>

            <p>Le envío algunos recursos que le ayudarán en este proceso:</p>

            <ul>
                <li>E-book: "Preparando su empresa para IA"</li>
                <li>Checklist: Fundamentos de transformación digital</li>
                <li>Casos de estudio de empresas en fase inicial</li>
            </ul>

            <p>También lo invito a nuestros <strong>workshops grupales mensuales</strong> donde
            discutimos estos temas en profundidad.</p>

            <p>Cuando esté listo para avanzar, estaré encantado de ayudarle.</p>

            <p style="margin-top: 30px;">Saludos,<br/>
            <strong>Andrés</strong><br/>
            AI Consulting<br/>
            negusnett@gmail.com</p>
        </body>
        </html>
        """

        return subject, body
