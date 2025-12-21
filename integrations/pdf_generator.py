"""
Generador de PDFs para prospectos
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from datetime import datetime
from pathlib import Path

from core.models import DiagnosticResult


class PDFGenerator:
    """Generador de PDFs ejecutivos para prospectos"""

    def __init__(self):
        self.output_dir = Path("/home/claude/ai_readiness_diagnostic/output/pdfs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Estilos
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceAfter=10
        )

    def generate_prospect_pdf(self, result: DiagnosticResult) -> Path:
        """
        Generar PDF de 2 páginas para el prospecto

        Returns:
            Path al PDF generado
        """

        filename = f"diagnostico_{result.diagnostic_id}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []

        # PÁGINA 1: SU SITUACIÓN ACTUAL
        story.append(Paragraph("Diagnóstico AI Readiness", self.title_style))
        story.append(Paragraph(f"{result.prospect_info.nombre_empresa}", self.styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))

        # Score general
        story.append(Paragraph("Su Situación Actual", self.heading_style))

        scores_data = [
            ['Dimensión', 'Score', 'Evaluación'],
            [
                'Madurez Digital',
                f"{result.score.madurez_digital.score_total}/40",
                self._get_evaluation(result.score.madurez_digital.score_total, 40)
            ],
            [
                'Capacidad de Inversión',
                f"{result.score.capacidad_inversion.score_total}/30",
                self._get_evaluation(result.score.capacidad_inversion.score_total, 30)
            ],
            [
                'Viabilidad Comercial',
                f"{result.score.viabilidad_comercial.score_total}/30",
                self._get_evaluation(result.score.viabilidad_comercial.score_total, 30)
            ]
        ]

        score_table = Table(scores_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))

        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))

        # Fortalezas y Oportunidades
        story.append(Paragraph("Fortalezas Identificadas", self.heading_style))

        fortalezas_text = "<br/>".join([
            f"• {insight.descripcion}"
            for insight in result.insights
            if insight.categoria == "fortaleza"
        ])

        if fortalezas_text:
            story.append(Paragraph(fortalezas_text, self.styles['BodyText']))
        else:
            story.append(Paragraph("• Análisis en curso", self.styles['BodyText']))

        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph("Oportunidades de Mejora", self.heading_style))

        oportunidades_text = "<br/>".join([
            f"• {insight.descripcion}"
            for insight in result.insights
            if insight.categoria == "oportunidad"
        ][:3])  # Máximo 3

        if oportunidades_text:
            story.append(Paragraph(oportunidades_text, self.styles['BodyText']))
        else:
            story.append(Paragraph("• Múltiples oportunidades identificadas", self.styles['BodyText']))

        # PÁGINA 2: PRÓXIMOS PASOS
        story.append(PageBreak())

        story.append(Paragraph("Próximos Pasos Sugeridos", self.title_style))
        story.append(Spacer(1, 0.2*inch))

        # Quick Wins
        story.append(Paragraph("Quick Wins (3-6 meses)", self.heading_style))

        for qw in result.quick_wins[:2]:  # Máximo 2
            qw_text = f"""
            <b>{qw.titulo}</b><br/>
            {qw.descripcion}<br/>
            <i>Impacto estimado: {qw.impacto_estimado}</i>
            """
            story.append(Paragraph(qw_text, self.styles['BodyText']))
            story.append(Spacer(1, 0.15*inch))

        story.append(Spacer(1, 0.2*inch))

        # Resultados esperados
        story.append(Paragraph("Resultados Esperados", self.heading_style))

        resultados_text = f"""
        Empresas del sector {result.prospect_info.sector} que implementaron
        iniciativas de IA lograron:<br/>
        • Reducción 20-40% en costos operativos<br/>
        • Mejora 30-50% en tiempos de respuesta<br/>
        • Incremento 15-25% en satisfacción del cliente<br/>
        • ROI positivo en 6-12 meses
        """

        story.append(Paragraph(resultados_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))

        # Próximos pasos
        story.append(Paragraph("¿Qué sigue?", self.heading_style))

        next_steps_text = f"""
        Lo contactaremos en las próximas 48 horas para:<br/><br/>
        1. Presentarle casos de éxito relevantes para su sector<br/>
        2. Mostrarle el ROI estimado para {result.prospect_info.nombre_empresa}<br/>
        3. Diseñar un plan de implementación específico<br/>
        4. Responder todas sus preguntas<br/><br/>

        <b>Contacto:</b> Andrés - AI Consulting<br/>
        <b>Email:</b> [su email de consultoría]
        """

        story.append(Paragraph(next_steps_text, self.styles['BodyText']))

        # Generar PDF
        doc.build(story)

        return filepath

    def _get_evaluation(self, score: int, max_score: int) -> str:
        """Evaluar un score como Alto/Medio/Bajo"""
        percentage = (score / max_score) * 100

        if percentage >= 75:
            return "Alto"
        elif percentage >= 50:
            return "Medio"
        else:
            return "Bajo"
