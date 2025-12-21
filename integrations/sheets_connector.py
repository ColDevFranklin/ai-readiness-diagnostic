"""
Conector de Google Sheets para almacenar resultados de diagnósticos
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st
import pandas as pd
from pathlib import Path
import json

from core.models import DiagnosticResult


class SheetsConnector:
    """Conector para Google Sheets"""

    def __init__(self):
        """Inicializar conexión con Google Sheets"""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        # Cargar credenciales desde Streamlit secrets
        try:
            creds_dict = st.secrets["gcp_service_account"]
            self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
                creds_dict, self.scope
            )
            self.client = gspread.authorize(self.creds)

            # Abrir spreadsheet
            self.sheet_name = st.secrets.get("sheet_name", "AI_Readiness_Diagnostics")
            self.spreadsheet = self.client.open(self.sheet_name)

        except Exception as e:
            st.error(f"Error conectando a Google Sheets: {e}")
            raise

    def _get_or_create_worksheet(self, worksheet_name: str) -> gspread.Worksheet:
        """Obtener o crear una worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=50
            )
        return worksheet

    def save_diagnostic(self, result: DiagnosticResult) -> bool:
        """
        Guardar resultado completo del diagnóstico

        Args:
            result: DiagnosticResult completo

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # 1. Guardar en hoja "responses" (datos raw)
            self._save_to_responses(result)

            # 2. Guardar en hoja "scores" (resultados calculados)
            self._save_to_scores(result)

            # 3. Actualizar hoja "analytics" (métricas agregadas)
            self._update_analytics()

            return True

        except Exception as e:
            st.error(f"Error guardando diagnóstico: {e}")
            return False

    def _save_to_responses(self, result: DiagnosticResult):
        """Guardar respuestas raw del prospecto"""

        worksheet = self._get_or_create_worksheet("responses")

        # Si es la primera fila, agregar headers
        if worksheet.row_count == 1 or not worksheet.row_values(1):
            headers = [
                "timestamp", "diagnostic_id", "nombre_empresa", "sector",
                "facturacion", "empleados", "contacto_nombre", "contacto_email",
                "contacto_telefono", "cargo", "ciudad",
                "motivacion", "toma_decisiones", "procesos_criticos",
                "tareas_repetitivas", "compartir_informacion", "equipo_tecnico",
                "capacidad_implementacion", "inversion_reciente", "frustracion_principal",
                "urgencia", "proceso_aprobacion", "presupuesto_rango"
            ]
            worksheet.append_row(headers)

        # Preparar fila de datos
        row = [
            result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            result.diagnostic_id,
            result.prospect_info.nombre_empresa,
            result.prospect_info.sector,
            result.prospect_info.facturacion_rango,
            result.prospect_info.empleados_rango,
            result.prospect_info.contacto_nombre,
            result.prospect_info.contacto_email,
            result.prospect_info.contacto_telefono,
            result.prospect_info.cargo,
            result.prospect_info.ciudad,
            ", ".join(result.responses.motivacion),
            result.responses.toma_decisiones,
            result.responses.procesos_criticos,
            result.responses.tareas_repetitivas,
            result.responses.compartir_informacion,
            result.responses.equipo_tecnico,
            result.responses.capacidad_implementacion,
            result.responses.inversion_reciente,
            result.responses.frustracion_principal,
            result.responses.urgencia,
            result.responses.proceso_aprobacion,
            result.responses.presupuesto_rango
        ]

        worksheet.append_row(row)

    def _save_to_scores(self, result: DiagnosticResult):
        """Guardar scores y clasificación"""

        worksheet = self._get_or_create_worksheet("scores")

        # Headers
        if worksheet.row_count == 1 or not worksheet.row_values(1):
            headers = [
                "timestamp", "diagnostic_id", "nombre_empresa", "contacto_email",
                "score_final", "tier", "confianza_clasificacion",
                "madurez_digital_total", "madurez_decisiones", "madurez_procesos",
                "madurez_integracion", "madurez_eficiencia",
                "capacidad_inversion_total", "capacidad_presupuesto",
                "capacidad_historial", "capacidad_tamano",
                "viabilidad_total", "viabilidad_problema", "viabilidad_urgencia",
                "viabilidad_decision",
                "arquetipo_tipo", "arquetipo_nombre", "arquetipo_confianza",
                "servicio_sugerido", "monto_min", "monto_max",
                "probabilidad_cierre", "quick_wins_count", "red_flags_count"
            ]
            worksheet.append_row(headers)

        # Preparar datos
        row = [
            result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            result.diagnostic_id,
            result.prospect_info.nombre_empresa,
            result.prospect_info.contacto_email,
            result.score.score_final,
            result.score.tier.value,
            result.score.confianza_clasificacion,
            result.score.madurez_digital.score_total,
            result.score.madurez_digital.decisiones_basadas_datos,
            result.score.madurez_digital.procesos_estandarizados,
            result.score.madurez_digital.sistemas_integrados,
            result.score.madurez_digital.eficiencia_operativa,
            result.score.capacidad_inversion.score_total,
            result.score.capacidad_inversion.presupuesto_disponible,
            result.score.capacidad_inversion.historial_inversion,
            result.score.capacidad_inversion.tamano_empresa,
            result.score.viabilidad_comercial.score_total,
            result.score.viabilidad_comercial.problema_claro,
            result.score.viabilidad_comercial.urgencia_real,
            result.score.viabilidad_comercial.poder_decision,
            result.arquetipo.tipo,
            result.arquetipo.nombre,
            result.arquetipo.confianza,
            result.servicio_sugerido,
            result.monto_sugerido_min,
            result.monto_sugerido_max,
            result.reunion_prep.probabilidad_cierre,
            len(result.quick_wins),
            len(result.red_flags)
        ]

        worksheet.append_row(row)

    def _update_analytics(self):
        """Actualizar métricas agregadas"""

        # Leer datos de scores
        scores_ws = self._get_or_create_worksheet("scores")
        scores_data = scores_ws.get_all_records()

        if not scores_data:
            return

        df = pd.DataFrame(scores_data)

        # Calcular métricas
        total_diagnosticos = len(df)
        tier_a_count = len(df[df['tier'] == 'A'])
        tier_b_count = len(df[df['tier'] == 'B'])
        tier_c_count = len(df[df['tier'] == 'C'])

        score_promedio = df['score_final'].mean()
        prob_cierre_promedio = df['probabilidad_cierre'].mean()

        # Pipeline value (suma de montos promedio ponderados por probabilidad)
        df['pipeline_value'] = (df['monto_min'] + df['monto_max']) / 2 * (df['probabilidad_cierre'] / 100)
        pipeline_total = df['pipeline_value'].sum()

        # Distribución por arquetipo
        arquetipo_dist = df['arquetipo_tipo'].value_counts().to_dict()
        sector_dist = df['nombre_empresa'].apply(lambda x: x.split()[0] if x else 'Unknown').value_counts().head(5).to_dict()

        # Guardar en worksheet analytics
        analytics_ws = self._get_or_create_worksheet("analytics")

        # Actualizar métricas (siempre en primera fila después del header)
        analytics_data = [
            ["Métrica", "Valor", "Última Actualización"],
            ["Total Diagnósticos", total_diagnosticos, datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Tier A", tier_a_count, ""],
            ["Tier B", tier_b_count, ""],
            ["Tier C", tier_c_count, ""],
            ["Score Promedio", f"{score_promedio:.1f}", ""],
            ["Prob. Cierre Promedio", f"{prob_cierre_promedio:.1f}%", ""],
            ["Pipeline Value Estimado", f"${pipeline_total:,.0f} COP", ""],
            ["Conversion Rate (Tier A)", f"{tier_a_count/total_diagnosticos*100:.1f}%", ""]
        ]

        # Limpiar y escribir
        analytics_ws.clear()
        analytics_ws.update('A1', analytics_data)

    def get_all_diagnostics(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Obtener todos los diagnósticos (o los últimos N)

        Args:
            limit: Número máximo de registros a retornar

        Returns:
            Lista de diccionarios con datos de diagnósticos
        """
        try:
            scores_ws = self._get_or_create_worksheet("scores")
            data = scores_ws.get_all_records()

            # Ordenar por timestamp descendente
            data = sorted(data, key=lambda x: x.get('timestamp', ''), reverse=True)

            if limit:
                data = data[:limit]

            return data

        except Exception as e:
            st.error(f"Error obteniendo diagnósticos: {e}")
            return []

    def get_tier_a_diagnostics(self) -> List[Dict]:
        """Obtener solo diagnósticos Tier A"""
        all_data = self.get_all_diagnostics()
        return [d for d in all_data if d.get('tier') == 'A']

    def get_analytics_summary(self) -> Dict:
        """Obtener resumen de analytics"""
        try:
            analytics_ws = self._get_or_create_worksheet("analytics")
            data = analytics_ws.get_all_records()

            summary = {}
            for row in data:
                summary[row.get('Métrica', '')] = row.get('Valor', '')

            return summary

        except Exception as e:
            st.error(f"Error obteniendo analytics: {e}")
            return {}
