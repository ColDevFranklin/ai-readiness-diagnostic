"""
Conector de Google Sheets - Version 3.3 PRODUCTION FINAL
FIXED: Schema alignment + timestamp format + column mapping
Autor: Andrés - AI Consultant
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st
import pandas as pd
import traceback

from core.models import DiagnosticResult


class SheetsConnector:
    """Conector para Google Sheets con type-safe serialization"""

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
            # Asegurar que es datetime válido
            if not isinstance(dt, datetime):
                dt = datetime.now()

            # Formato compatible con Google Sheets ES locale
            formatted = dt.strftime("%d/%m/%Y %H:%M:%S")
            return formatted
        except Exception as e:
            print(f"[TIMESTAMP ERROR] {e}")
            # Fallback a timestamp actual
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
                # Filtrar elementos vacíos/None y convertir a string
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
        CRÍTICO: Cada columna debe tener exactamente un valor en el row
        """

        print(f"[RESPONSES] Iniciando guardado...")

        worksheet = self._get_or_create_worksheet("responses")

        # ✅ HEADERS DEFINITIVOS - 23 columnas
        expected_headers = [
            "timestamp",           # 1
            "diagnostic_id",       # 2
            "nombre_empresa",      # 3
            "sector",              # 4
            "facturacion",         # 5
            "empleados",           # 6
            "contacto_nombre",     # 7
            "contacto_email",      # 8
            "contacto_telefono",   # 9
            "cargo",               # 10
            "ciudad",              # 11
            "motivacion",          # 12 - STRING con separador ", "
            "toma_decisiones",     # 13
            "procesos_criticos",   # 14
            "tareas_repetitivas",  # 15
            "compartir_informacion", # 16
            "equipo_tecnico",      # 17
            "capacidad_implementacion", # 18
            "inversion_reciente",  # 19
            "frustracion_principal", # 20
            "urgencia",            # 21
            "proceso_aprobacion",  # 22
            "presupuesto_rango"    # 23
        ]

        # Verificar/crear headers
        existing_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []

        if not existing_headers or existing_headers != expected_headers:
            print(f"[RESPONSES] Creando/actualizando headers")
            worksheet.clear()
            worksheet.append_row(expected_headers)
            print(f"[RESPONSES] Headers creados: {len(expected_headers)} columnas")

        # ✅ CONSTRUIR ROW CON VALIDACIÓN ESTRICTA
        timestamp_str = self._format_timestamp(result.created_at)
        motivacion_str = self._safe_list_to_string(result.responses.motivacion)

        row = [
            timestamp_str,                                  # 1
            result.diagnostic_id,                           # 2
            result.prospect_info.nombre_empresa,            # 3
            result.prospect_info.sector,                    # 4
            result.prospect_info.facturacion_rango,         # 5
            result.prospect_info.empleados_rango,           # 6
            result.prospect_info.contacto_nombre,           # 7
            result.prospect_info.contacto_email,            # 8
            result.prospect_info.contacto_telefono or "",   # 9
            result.prospect_info.cargo,                     # 10
            result.prospect_info.ciudad,                    # 11
            motivacion_str,                                 # 12
            result.responses.toma_decisiones or "",         # 13
            result.responses.procesos_criticos or "",       # 14
            result.responses.tareas_repetitivas or "",      # 15
            result.responses.compartir_informacion or "",   # 16
            result.responses.equipo_tecnico or "",          # 17
            result.responses.capacidad_implementacion or "", # 18
            result.responses.inversion_reciente or "",      # 19
            result.responses.frustracion_principal or "",   # 20
            result.responses.urgencia or "",                # 21
            result.responses.proceso_aprobacion or "",      # 22
            result.responses.presupuesto_rango or ""        # 23
        ]

        # ✅ VALIDACIÓN CRÍTICA
        if len(row) != len(expected_headers):
            error_msg = f"SCHEMA MISMATCH: Row tiene {len(row)} valores, headers tiene {len(expected_headers)}"
            print(f"[RESPONSES] ❌ {error_msg}")
            raise ValueError(error_msg)

        print(f"[RESPONSES] Row validado: {len(row)} columnas")
        print(f"[RESPONSES] Timestamp: {timestamp_str}")
        print(f"[RESPONSES] Motivación: {motivacion_str}")

        try:
            worksheet.append_row(row, value_input_option='USER_ENTERED')
            print(f"[RESPONSES] ✅ Guardado exitoso")
        except Exception as e:
            print(f"[RESPONSES] ❌ Error al append row: {str(e)}")
            print(f"[RESPONSES] Row data: {row}")
            raise

    def _save_to_scores(self, result: DiagnosticResult):
        """
        Guardar scores calculados
        CRÍTICO: Schema alignment perfecto
        """

        print(f"[SCORES] Iniciando guardado...")

        worksheet = self._get_or_create_worksheet("scores")

        # ✅ HEADERS DEFINITIVOS - 35 columnas
        expected_headers = [
            "timestamp",                # 1
            "diagnostic_id",            # 2
            "nombre_empresa",           # 3
            "sector",                   # 4
            "contacto_nombre",          # 5
            "contacto_email",           # 6
            "contacto_telefono",        # 7
            "cargo",                    # 8
            "ciudad",                   # 9
            "facturacion",              # 10
            "empleados",                # 11
            "score_final",              # 12
            "tier",                     # 13
            "confianza_clasificacion",  # 14
            "madurez_digital_total",    # 15
            "madurez_decisiones",       # 16
            "madurez_procesos",         # 17
            "madurez_integracion",      # 18
            "madurez_eficiencia",       # 19
            "capacidad_inversion_total", # 20
            "capacidad_presupuesto",    # 21
            "capacidad_historial",      # 22
            "capacidad_tamano",         # 23
            "viabilidad_total",         # 24
            "viabilidad_problema",      # 25
            "viabilidad_urgencia",      # 26
            "viabilidad_decision",      # 27
            "arquetipo_tipo",           # 28
            "arquetipo_nombre",         # 29
            "arquetipo_confianza",      # 30
            "servicio_sugerido",        # 31
            "monto_min",                # 32
            "monto_max",                # 33
            "probabilidad_cierre",      # 34
            "quick_wins_count",         # 35
            "red_flags_count"           # 36
        ]

        # Verificar/crear headers
        existing_headers = worksheet.row_values(1) if worksheet.row_count > 0 else []

        if not existing_headers or existing_headers != expected_headers:
            print(f"[SCORES] Creando/actualizando headers")
            worksheet.clear()
            worksheet.append_row(expected_headers)
            print(f"[SCORES] Headers creados: {len(expected_headers)} columnas")

        # ✅ SAFE ACCESS con valores default
        timestamp_str = self._format_timestamp(result.created_at)
        confianza_clasificacion = getattr(result.score, 'confianza_clasificacion', 0.0)
        probabilidad_cierre = getattr(result.reunion_prep, 'probabilidad_cierre', 50)

        row = [
            timestamp_str,                                      # 1
            result.diagnostic_id,                               # 2
            result.prospect_info.nombre_empresa,                # 3
            result.prospect_info.sector,                        # 4
            result.prospect_info.contacto_nombre,               # 5
            result.prospect_info.contacto_email,                # 6
            result.prospect_info.contacto_telefono or "",       # 7
            result.prospect_info.cargo,                         # 8
            result.prospect_info.ciudad,                        # 9
            result.prospect_info.facturacion_rango,             # 10
            result.prospect_info.empleados_rango,               # 11
            result.score.score_final,                           # 12
            result.score.tier.value,                            # 13
            confianza_clasificacion,                            # 14
            result.score.madurez_digital.score_total,           # 15
            result.score.madurez_digital.decisiones_basadas_datos, # 16
            result.score.madurez_digital.procesos_estandarizados,  # 17
            result.score.madurez_digital.sistemas_integrados,      # 18
            result.score.madurez_digital.eficiencia_operativa,     # 19
            result.score.capacidad_inversion.score_total,          # 20
            result.score.capacidad_inversion.presupuesto_disponible, # 21
            result.score.capacidad_inversion.historial_inversion,    # 22
            result.score.capacidad_inversion.tamano_empresa,         # 23
            result.score.viabilidad_comercial.score_total,           # 24
            result.score.viabilidad_comercial.problema_claro,        # 25
            result.score.viabilidad_comercial.urgencia_real,         # 26
            result.score.viabilidad_comercial.poder_decision,        # 27
            result.arquetipo.tipo,                                   # 28
            result.arquetipo.nombre,                                 # 29
            result.arquetipo.confianza,                              # 30
            result.servicio_sugerido,                                # 31
            result.monto_sugerido_min,                               # 32
            result.monto_sugerido_max,                               # 33
            probabilidad_cierre,                                     # 34
            len(result.quick_wins),                                  # 35
            len(result.red_flags)                                    # 36
        ]

        # ✅ VALIDACIÓN CRÍTICA
        if len(row) != len(expected_headers):
            error_msg = f"SCHEMA MISMATCH: Row tiene {len(row)} valores, headers tiene {len(expected_headers)}"
            print(f"[SCORES] ❌ {error_msg}")
            raise ValueError(error_msg)

        print(f"[SCORES] Row validado: {len(row)} columnas")
        print(f"[SCORES] Score: {result.score.score_final} | Tier: {result.score.tier.value}")

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
