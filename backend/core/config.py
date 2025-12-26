"""
Adaptador de Secrets para FastAPI
Permite usar st.secrets (Streamlit) con variables de entorno (.env)
Version 3.1 - Soporte para Resend + Testing Mode
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class SecretsAdapter:
    """
    Adaptador singleton para secrets
    Funciona tanto con .env (FastAPI) como con secrets.toml (Streamlit)
    """
    _instance = None
    _secrets: Dict[str, Any] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._secrets is None:
            self._load_secrets()

    def _load_secrets(self):
        """Carga secrets desde .env o fallback a secrets.toml"""
        self._secrets = {}

        # OPCIÓN 1: Cargar desde .env (para FastAPI)
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / '.env'

        if env_path.exists():
            load_dotenv(env_path)
            print("[SECRETS] ✓ Cargando configuración desde .env")

            # Google Cloud Platform Service Account
            gcp_json_str = os.getenv('GCP_SERVICE_ACCOUNT')
            if gcp_json_str:
                try:
                    self._secrets['gcp_service_account'] = json.loads(gcp_json_str)
                    print("[SECRETS] ✓ GCP Service Account cargado")
                except json.JSONDecodeError as e:
                    print(f"[SECRETS] ❌ Error parseando GCP_SERVICE_ACCOUNT: {e}")
                    self._secrets['gcp_service_account'] = {}
            else:
                print("[SECRETS] ⚠ GCP_SERVICE_ACCOUNT no encontrado en .env")
                self._secrets['gcp_service_account'] = {}

            # Spreadsheet ID
            self._secrets['spreadsheet_id'] = os.getenv('SPREADSHEET_ID', '')
            self._secrets['sheet_name'] = os.getenv('SHEET_NAME', 'AI_Readiness_Diagnostics')

            # EMAIL CONFIGURATION - Resend
            self._secrets['email'] = {
                'resend_api_key': os.getenv('RESEND_API_KEY'),
                'from': os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
            }

            # Fallback: también soportar key en root level
            self._secrets['resend_api_key'] = os.getenv('RESEND_API_KEY')

            # ==========================================
            # TESTING MODE (AGREGADO - FIX CRÍTICO)
            # ==========================================
            self._secrets['EMAIL_TESTING_MODE'] = os.getenv('EMAIL_TESTING_MODE', 'false')
            self._secrets['EMAIL_TESTING_RECIPIENT'] = os.getenv('EMAIL_TESTING_RECIPIENT', 'franklinnrodriguez83@gmail.com')

            # SMTP Configuration (LEGACY - Mantener por compatibilidad)
            self._secrets['smtp'] = {
                'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'port': int(os.getenv('SMTP_PORT', 587)),
                'user': os.getenv('SMTP_USER', ''),
                'password': os.getenv('SMTP_PASSWORD', ''),
                'from': os.getenv('EMAIL_FROM', os.getenv('SMTP_USER', ''))
            }

            # Logs de configuración
            if self._secrets['email']['resend_api_key']:
                print(f"[SECRETS] ✓ Resend configurado | From: {self._secrets['email']['from']}")
                testing_mode = self._secrets['EMAIL_TESTING_MODE']
                print(f"[SECRETS] ✓ Testing Mode: {testing_mode}")
                if testing_mode == 'true':
                    print(f"[SECRETS] ✓ Testing Recipient: {self._secrets['EMAIL_TESTING_RECIPIENT']}")
            else:
                print("[SECRETS] ⚠ RESEND_API_KEY no encontrado - emails NO funcionarán")

        # OPCIÓN 2: Fallback a secrets.toml (para Streamlit legacy)
        else:
            streamlit_secrets_path = Path(__file__).parent.parent / '.streamlit' / 'secrets.toml'

            if streamlit_secrets_path.exists():
                print("[SECRETS] ✓ Cargando desde .streamlit/secrets.toml")
                try:
                    import streamlit as st
                    # Copiar todos los secrets de Streamlit
                    self._secrets = dict(st.secrets)
                except Exception as e:
                    print(f"[SECRETS] ❌ Error cargando secrets.toml: {e}")
                    self._secrets = {}
            else:
                print("[SECRETS] ❌ No se encontró .env ni secrets.toml")
                print(f"[SECRETS] Buscado en: {env_path}")
                print(f"[SECRETS] Buscado en: {streamlit_secrets_path}")
                self._secrets = {}

    def __getitem__(self, key: str) -> Any:
        """Permite usar secrets['key'] como en Streamlit"""
        if self._secrets is None:
            self._load_secrets()

        if key not in self._secrets:
            raise KeyError(
                f"Secret '{key}' no encontrado. "
                f"Claves disponibles: {list(self._secrets.keys())}"
            )

        return self._secrets[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Permite usar secrets.get('key', default)"""
        if self._secrets is None:
            self._load_secrets()

        return self._secrets.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Permite usar 'key' in secrets"""
        if self._secrets is None:
            self._load_secrets()

        return key in self._secrets

    def keys(self):
        """Retorna las claves disponibles"""
        if self._secrets is None:
            self._load_secrets()

        return self._secrets.keys()

# Singleton global - importar desde cualquier archivo
secrets = SecretsAdapter()

# Para debugging
if __name__ == '__main__':
    print("=== TEST DE SECRETS ===")
    print(f"Claves disponibles: {list(secrets.keys())}")
    print(f"Resend API Key configurada: {'✓' if secrets.get('resend_api_key') else '✗'}")
    print(f"Email From: {secrets.get('email', {}).get('from', 'N/A')}")
    print(f"Spreadsheet ID: {secrets.get('spreadsheet_id', 'N/A')}")
    print(f"Testing Mode: {secrets.get('EMAIL_TESTING_MODE', 'N/A')}")
    print(f"Testing Recipient: {secrets.get('EMAIL_TESTING_RECIPIENT', 'N/A')}")
