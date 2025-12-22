"""
Conector de Google Sheets - Version 3.0 FINAL
FIXED: Complete schema alignment + robust error handling
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st
import pandas as pd
import traceback

from core.models import DiagnosticResult


class SheetsConnector:
    """Conector para Google Sheets"""

    def __init__(self):
        """Inicializar conexión con Google Sheets"""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        try:
            creds_dict = st.secrets["gcp_service_account"]
            self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
                creds_dict, self.scope
            )
            self.client = gspread.authorize(self.creds)

            self.sheet_name = st.secrets.get("sheet_name", "AI_Readiness_Diagnostics")
            self.spreadsheet = self.client.open(self.sheet_name)

        except Exception as e:
            print(f"[SHEETS INIT ERROR] {datetime.now()}: {str(e)}")
            print(traceback.format_exc())
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
        """Guardar resultado completo del diagnóstico"""
        try:
            self._save_to_responses(result)
            self._save_to_scores(result)
            self._update_analytics()

            print(f"[SHEETS SAVE SUCCESS] {datetime.now()}: {result.prospect_info.nombre_empresa} - {result.prospect_info.contacto_email}")
            return True

        except Exception as e:
            print(f"[SHEETS SAVE ERROR] {datetime.now()}: {str(e)}")
            print(f"  Empresa: {result.prospect_info.nombre_empresa}")
            print(f"  Email: {result.prospect_info.contacto_email}")
            print(f"  Score: {result.score.score_final}")
            print(traceback.format_exc())
            raise

    def _save_to_responses(self, result: DiagnosticResult):
        """Guardar respuestas raw del prospecto"""
        worksheet = self._get_or_create_worksheet("responses")

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

        worksheet.append_row(row, value_input_option='USER_ENTERED')

    def _save_to_scores(self, result: DiagnosticResult):
        """Guardar scores - SCHEMA COMPLETAMENTE ALINEADO CON DASHBOARD"""
        worksheet = self._get_or_create_worksheet("scores")

        if worksheet.row_count == 1 or not worksheet.row_values(1):
            headers = [
                "timestamp", "diagnostic_id", "nombre_empresa", "sector",
                "contacto_nombre", "contacto_email", "contacto_telefono",
                "cargo", "ciudad", "facturacion", "empleados",
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

        # SAFE ACCESS con valores default
        confianza_clasificacion = getattr(result.score, 'confianza_clasificacion', 0.0)
        probabilidad_cierre = getattr(result.reunion_prep, 'probabilidad_cierre', 50)

        row = [
            result.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            result.diagnostic_id,
            result.prospect_info.nombre_empresa,
            result.prospect_info.sector,
            result.prospect_info.contacto_nombre,
            result.prospect_info.contacto_email,
            result.prospect_info.contacto_telefono,
            result.prospect_info.cargo,
            result.prospect_info.ciudad,
            result.prospect_info.facturacion_rango,
            result.prospect_info.empleados_rango,
            result.score.score_final,
            result.score.tier.value,
            confianza_clasificacion,
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
            probabilidad_cierre,
            len(result.quick_wins),
            len(result.red_flags)
        ]

        worksheet.append_row(row, value_input_option='USER_ENTERED')
        print(f"[SCORES SAVED] {result.prospect_info.nombre_empresa} | Email: {result.prospect_info.contacto_email} | Score: {result.score.score_final}")

    def _update_analytics(self):
        """Actualizar métricas agregadas"""
        try:
            scores_ws = self._get_or_create_worksheet("scores")
            scores_data = scores_ws.get_all_records()

            if not scores_data:
                return

            df = pd.DataFrame(scores_data)

            total_diagnosticos = len(df)
            tier_a_count = len(df[df['tier'] == 'A'])
            tier_b_count = len(df[df['tier'] == 'B'])
            tier_c_count = len(df[df['tier'] == 'C'])

            score_promedio = df['score_final'].mean() if 'score_final' in df.columns and len(df) > 0 else 0
            prob_cierre_promedio = df['probabilidad_cierre'].mean() if 'probabilidad_cierre' in df.columns and len(df) > 0 else 0

            if 'monto_min' in df.columns and 'monto_max' in df.columns and 'probabilidad_cierre' in df.columns:
                df['pipeline_value'] = (df['monto_min'] + df['monto_max']) / 2 * (df['probabilidad_cierre'] / 100)
                pipeline_total = df['pipeline_value'].sum()
            else:
                pipeline_total = 0

            analytics_ws = self._get_or_create_worksheet("analytics")

            analytics_data = [
                ["Métrica", "Valor", "Última Actualización"],
                ["Total Diagnósticos", total_diagnosticos, datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Tier A", tier_a_count, ""],
                ["Tier B", tier_b_count, ""],
                ["Tier C", tier_c_count, ""],
                ["Score Promedio", f"{score_promedio:.1f}", ""],
                ["Prob. Cierre Promedio", f"{prob_cierre_promedio:.1f}%", ""],
                ["Pipeline Value Estimado", f"${pipeline_total:,.0f} COP", ""],
                ["Conversion Rate (Tier A)", f"{tier_a_count/total_diagnosticos*100:.1f}%" if total_diagnosticos > 0 else "0%", ""]
            ]

            analytics_ws.clear()
            analytics_ws.update('A1', analytics_data)

        except Exception as e:
            print(f"[ANALYTICS UPDATE ERROR] {datetime.now()}: {str(e)}")
            print(traceback.format_exc())

    def get_all_diagnostics(self, limit: Optional[int] = None) -> List[Dict]:
        """Obtener todos los diagnósticos"""
        try:
            scores_ws = self._get_or_create_worksheet("scores")
            data = scores_ws.get_all_records()
            data = sorted(data, key=lambda x: x.get('timestamp', ''), reverse=True)

            if limit:
                data = data[:limit]

            return data

        except Exception as e:
            print(f"[GET DIAGNOSTICS ERROR] {datetime.now()}: {str(e)}")
            print(traceback.format_exc())
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
            print(f"[GET ANALYTICS ERROR] {datetime.now()}: {str(e)}")
            print(traceback.format_exc())
            return {}
