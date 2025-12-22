"""
Sistema de envío de emails - Version 2.0
FIXED: SMTP error handling + comprehensive logging
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional
import streamlit as st
import traceback
from datetime import datetime

from core.models import DiagnosticResult


class EmailSender:
    """Envío de emails automatizados según Tier"""

    def __init__(self):
        self.smtp_server = st.secrets.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = int(st.secrets.get("smtp_port", 587))
        self.sender_email = st.secrets.get("sender_email")
        self.sender_password = st.secrets.get("sender_password")
        self.sender_name = "Andrés - AI Consulting"

        print(f"[EMAIL INIT] SMTP: {self.smtp_server}:{self.smtp_port} | Sender: {self.sender_email}")

    def send_confirmation_email(
        self,
        result: DiagnosticResult,
        pdf_path: Optional[Path] = None
    ) -> bool:
        """Enviar email de confirmación según Tier"""

        try:
            print(f"[EMAIL START] Enviando a {result.prospect_info.contacto_email} | Tier: {result.score.tier.value}")

            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = result.prospect_info.contacto_email

            if result.score.tier.value == "A":
                subject, body = self._get_tier_a_content(result)
            elif result.score.tier.value == "B":
                subject, body = self._get_tier_b_content(result)
            else:
                subject, body = self._get_tier_c_content(result)

            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            if pdf_path and pdf_path.exists():
                with open(pdf_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=f'Diagnostico_AI_{result.prospect_info.nombre_empresa}.pdf'
                    )
                    msg.attach(pdf_attachment)
                print(f"[EMAIL PDF] Adjuntando PDF: {pdf_path}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.set_debuglevel(1)
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"[EMAIL SUCCESS] Enviado a {result.prospect_info.contacto_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL AUTH ERROR] Credenciales inválidas: {e}")
            print(f"  Revisar sender_email y sender_password en Streamlit Secrets")
            print(traceback.format_exc())
            return False

        except smtplib.SMTPException as e:
            print(f"[EMAIL SMTP ERROR] {datetime.now()}: {e}")
            print(traceback.format_exc())
            return False

        except Exception as e:
            print(f"[EMAIL ERROR] {datetime.now()}: {e}")
            print(traceback.format_exc())
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
