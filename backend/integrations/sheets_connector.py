"""
Conector de Google Sheets - Version 3.6 FASTAPI COMPATIBLE
FIXED: Compatibilidad con secrets adapter + schema alignment
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
import traceback
import sys
from pathlib import Path

# Importar adaptador de secrets
sys.path.append(str(Path(__file__).parent.parent))
from core.config import secrets
from core.models import DiagnosticResult


class SheetsConnector:
    """Conector para Google Sheets con type-safe serialization"""

    def __init__(self):
        """Inicializar conexión con Google Sheets usando secrets adapter"""
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        try:
            # Usar secrets adapter en lugar de st.secrets
            creds_dict = secrets["gcp_service_account"]

            self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
                creds_dict, self.scope
            )
            self.client = gspread.authorize(self.creds)

            # Obtener configuración de sheets
            self.sheet_name = secrets.get("sheet_name", "AI_Readiness_Diagnostics")
            self.spreadsheet = self.client.open(self.sheet_name)

            print(f"[SHEETS INIT] ✅ Connected to: {self.sheet_name}")

        except Exception as e:
            print(f"[SHEETS INIT] ❌ ERROR: {str(e)}")
            print(traceback.format_exc())
            raise

    def _get_or_create_worksheet(self, worksheet_name: str) -> gspread.Worksheet:
        """Obtener o crear una worksheet"""
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            print(f"[WORKSHEET] ✅ Found: {worksheet_name}")
        except gspread.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=50
            )
            print(f"[WORKSHEET] ✅ Created: {worksheet_name}")

        return worksheet

    def _format_timestamp(self, dt: datetime) -> str:
        """
        Formatear timestamp de forma consistente para Google Sheets
        Formato: DD/MM/YYYY HH:MM:SS (compatible con Sheets locale ES)
        """
        try:
            if not isinstance(dt, datetime):
                dt = datetime.now()
            formatted = dt.strftime("%d/%m/%Y %H:%M:%S")
            return formatted
        except Exception as e:
            print(f"[TIMESTAMP ERROR] {e}")
            return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _safe_list_to_string(self, value: Any, separator: str = ", ") -> str:
        """
        Convertir lista a string de forma segura
        Maneja: List[str], List[Any], str, None, otros
        """
        try:
            if value is None or value == "":
                return ""

            if isinstance(value, list):
                clean = [str(x).strip() for x in value if x is not None and str(x).strip()]
                return separator.join(clean)

            if isinstance(value, str):
                return value.strip()

            return str(value)
        except Exception as e:
            print(f"[LIST_TO_STRING ERROR] {e}")
            return str(value) if value else ""

    def save_diagnostic(self, result: DiagnosticResult) -> bool:
        """Guardar resultado completo del diagnóstico"""
        print(f"\n{'='*70}")
        print(f"[SAVE DIAGNOSTIC] START")
        print(f"  Empresa: {result.prospect_info.nombre_empresa}")
        print(f"  Email: {result.prospect_info.contacto_email}")
        print(f"  Timestamp: {result.created_at}")
        print(f"{'='*70}")

        try:
            self._save_to_responses(result)
            self._save_to_scores(result)
            self._update_analytics()

            print(f"[SAVE DIAGNOSTIC] ✅ SUCCESS")
            print(f"  Score: {result.score.score_final} | Tier: {result.score.tier.value}")
            print(f"{'='*70}\n")
            return True

        except Exception as e:
            print(f"[SAVE DIAGNOSTIC] ❌ CRITICAL ERROR: {str(e)}")
            print(traceback.format_exc())
            print(f"{'='*70}\n")
            raise

    def _save_to_responses(self, result: DiagnosticResult):
        """
        Guardar respuestas raw del prospecto
        ✅ FIXED: Schema alignment con nombres reales del modelo
        """
        print(f"[RESPONSES] Iniciando guardado...")

        worksheet = self._get_or_create_worksheet("responses")

        # Headers alineados con el modelo ProspectInfo y DiagnosticResponses
        expected_headers = [
            "timestamp",
            "diagnostic_id",
            "nombre_empresa",
            "sector",
            "facturacion_rango",
            "empleados_rango",
            "contacto_nombre",
            "contacto_email",
            "contacto_telefono",
            "cargo",
            "ciudad",
            "motivacion",
            "toma_decisiones",
            "procesos_criticos",
            "tareas_repetitivas",
            "compartir_informacion",
            "equipo_tecnico",
            "capacidad_implementacion",
            "inversion_reciente",
            "frustracion_principal",
            "urgencia",
            "proceso_aprobacion",
            "presupuesto_rango"
        ]

        existing_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []

        if not existing_headers or existing_headers != expected_headers:
            print(f"[RESPONSES] Creando/actualizando headers")
            worksheet.clear()
            worksheet.append_row(expected_headers)
            print(f"[RESPONSES] Headers creados: {len(expected_headers)} columnas")

        timestamp_str = self._format_timestamp(result.created_at)
        motivacion_str = self._safe_list_to_string(result.responses.motivacion)

        row = [
            timestamp_str,
            result.diagnostic_id,
            result.prospect_info.nombre_empresa,
            result.prospect_info.sector,
            result.prospect_info.facturacion_rango,
            result.prospect_info.empleados_rango,
            result.prospect_info.contacto_nombre,
            result.prospect_info.contacto_email,
            result.prospect_info.contacto_telefono or "",
            result.prospect_info.cargo,
            result.prospect_info.ciudad,
            motivacion_str,
            result.responses.toma_decisiones or "",
            result.responses.procesos_criticos or "",
            result.responses.tareas_repetitivas or "",
            result.responses.compartir_informacion or "",
            result.responses.equipo_tecnico or "",
            result.responses.capacidad_implementacion or "",
            result.responses.inversion_reciente or "",
            result.responses.frustracion_principal or "",
            result.responses.urgencia or "",
            result.responses.proceso_aprobacion or "",
            result.responses.presupuesto_rango or ""
        ]

        if len(row) != len(expected_headers):
            error_msg = f"SCHEMA MISMATCH: Row tiene {len(row)} valores, headers tiene {len(expected_headers)}"
            print(f"[RESPONSES] ❌ {error_msg}")
            raise ValueError(error_msg)

        print(f"[RESPONSES] Row validado: {len(row)} columnas")

        try:
            worksheet.append_row(row, value_input_option='USER_ENTERED')
            print(f"[RESPONSES] ✅ Guardado exitoso")
        except Exception as e:
            print(f"[RESPONSES] ❌ Error al append row: {str(e)}")
            raise

    def _save_to_scores(self, result: DiagnosticResult):
        """
        Guardar scores calculados
        ✅ FIXED: Schema alignment
        """
        print(f"[SCORES] Iniciando guardado...")

        worksheet = self._get_or_create_worksheet("scores")

        expected_headers = [
            "timestamp",
            "diagnostic_id",
            "nombre_empresa",
            "sector",
            "contacto_nombre",
            "contacto_email",
            "contacto_telefono",
            "cargo",
            "ciudad",
            "facturacion_rango",
            "empleados_rango",
            "score_final",
            "tier",
            "confianza_clasificacion",
            "madurez_digital_total",
            "madurez_decisiones",
            "madurez_procesos",
            "madurez_integracion",
            "madurez_eficiencia",
            "capacidad_inversion_total",
            "capacidad_presupuesto",
            "capacidad_historial",
            "capacidad_tamano",
            "viabilidad_total",
            "viabilidad_problema",
            "viabilidad_urgencia",
            "viabilidad_decision",
            "arquetipo_tipo",
            "arquetipo_nombre",
            "arquetipo_confianza",
            "servicio_sugerido",
            "monto_min",
            "monto_max",
            "probabilidad_cierre",
            "quick_wins_count",
            "red_flags_count"
        ]

        existing_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []

        if not existing_headers or existing_headers != expected_headers:
            print(f"[SCORES] Creando/actualizando headers")
            worksheet.clear()
            worksheet.append_row(expected_headers)
            print(f"[SCORES] Headers creados: {len(expected_headers)} columnas")

        timestamp_str = self._format_timestamp(result.created_at)
        confianza_clasificacion = getattr(result.score, 'confianza_clasificacion', 0.0)
        probabilidad_cierre = getattr(result.reunion_prep, 'probabilidad_cierre', 50)

        row = [
            timestamp_str,
            result.diagnostic_id,
            result.prospect_info.nombre_empresa,
            result.prospect_info.sector,
            result.prospect_info.contacto_nombre,
            result.prospect_info.contacto_email,
            result.prospect_info.contacto_telefono or "",
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

        if len(row) != len(expected_headers):
            error_msg = f"SCHEMA MISMATCH: Row tiene {len(row)} valores, headers tiene {len(expected_headers)}"
            print(f"[SCORES] ❌ {error_msg}")
            raise ValueError(error_msg)

        print(f"[SCORES] Row validado: {len(row)} columnas")

        try:
            worksheet.append_row(row, value_input_option='USER_ENTERED')
            print(f"[SCORES] ✅ Guardado exitoso")
        except Exception as e:
            print(f"[SCORES] ❌ Error al append row: {str(e)}")
            raise

    def _update_analytics(self):
        """Actualizar métricas agregadas"""
        print(f"[ANALYTICS] Actualizando...")

        try:
            scores_ws = self._get_or_create_worksheet("scores")
            scores_data = scores_ws.get_all_records()

            if not scores_data:
                print(f"[ANALYTICS] No hay datos para procesar")
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
            timestamp_now = self._format_timestamp(datetime.now())

            analytics_data = [
                ["Métrica", "Valor", "Última Actualización"],
                ["Total Diagnósticos", total_diagnosticos, timestamp_now],
                ["Tier A", tier_a_count, ""],
                ["Tier B", tier_b_count, ""],
                ["Tier C", tier_c_count, ""],
                ["Score Promedio", f"{score_promedio:.1f}", ""],
                ["Prob. Cierre Promedio", f"{prob_cierre_promedio:.1f}%", ""],
                ["Pipeline Value Estimado", f"${pipeline_total:,.0f} COP", ""],
                ["Conversion Rate (Tier A)", f"{tier_a_count/total_diagnosticos*100:.1f}%" if total_diagnosticos > 0 else "0%", ""]
            ]

            analytics_ws.clear()
            analytics_ws.update('A1', analytics_data, value_input_option='USER_ENTERED')

            print(f"[ANALYTICS] ✅ Actualizado - Total: {total_diagnosticos}")

        except Exception as e:
            print(f"[ANALYTICS] ⚠️ Error (no crítico): {str(e)}")
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
            print(f"[GET DIAGNOSTICS] ❌ ERROR: {str(e)}")
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
            print(f"[GET ANALYTICS] ❌ ERROR: {str(e)}")
            print(traceback.format_exc())
            return {}
