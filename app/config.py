"""
Configuración centralizada del sistema de diagnóstico AI Readiness
"""

import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AppConfig:
    """Configuración general de la aplicación"""
    APP_NAME: str = "Diagnóstico AI Readiness"
    VERSION: str = "1.0.0"
    AUTHOR: str = "Andrés - AI Consulting"

    # Configuración de scoring
    TIER_A_THRESHOLD: int = 70
    TIER_B_THRESHOLD: int = 40

    # Tiempos estimados
    ESTIMATED_TIME_MINUTES: int = 10

    # Configuración de Google Sheets
    SHEET_NAME: str = "AI_Readiness_Responses"
    RESPONSES_TAB: str = "responses"
    SCORES_TAB: str = "scores"
    ANALYTICS_TAB: str = "analytics"


@dataclass
class ScoringWeights:
    """Pesos para el cálculo de score final"""
    MADUREZ_DIGITAL: float = 0.40
    CAPACIDAD_INVERSION: float = 0.30
    VIABILIDAD_COMERCIAL: float = 0.30


@dataclass
class EmailConfig:
    """Configuración de email"""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SENDER_NAME: str = "Andrés - AI Consulting"
    SUBJECT_TIER_A: str = "✅ Resultados de su diagnóstico AI - Oportunidades identificadas"
    SUBJECT_TIER_B: str = "📊 Resultados de su diagnóstico AI"
    SUBJECT_TIER_C: str = "📚 Recursos para iniciar su transformación digital"


# Sectores disponibles
SECTORES = [
    "🏦 Banca",
    "🛡️ Seguros",
    "🛒 Retail",
    "🏭 Manufactura",
    "💼 Servicios Profesionales",
    "🏥 Salud",
    "📚 Educación",
    "🏛️ Gobierno",
    "🚚 Logística/Transporte",
    "🏗️ Construcción",
    "Otro"
]

# Rangos de facturación (COP)
RANGOS_FACTURACION = [
    "Menos de $500M COP",
    "$500M - $2,000M COP",
    "$2,000M - $10,000M COP",
    "Más de $10,000M COP"
]

# Rangos de empleados
RANGOS_EMPLEADOS = [
    "1-20",
    "21-50",
    "51-200",
    "201-500",
    "Más de 500"
]

# Cargos
CARGOS = [
    "Dueño/Socio",
    "Gerente General/CEO",
    "Director de Área",
    "Gerente de Tecnología/IT",
    "Otro"
]

# Arquetipos
ARQUETIPOS = {
    "traditional_giant": {
        "nombre": "🏦 Traditional Giant",
        "descripcion": "Empresa grande tradicional con sistemas legacy, bajo presión competitiva",
        "sectores": ["🏦 Banca", "🛡️ Seguros"],
        "tamano_min": "$2,000M - $10,000M COP"
    },
    "ambitious_scaler": {
        "nombre": "📈 Ambitious Scaler",
        "descripcion": "Empresa en crecimiento que no logra escalar operaciones",
        "sectores": ["🛒 Retail", "💼 Servicios Profesionales", "🚚 Logística/Transporte"],
        "tamano_min": "$500M - $2,000M COP"
    },
    "digital_beginner": {
        "nombre": "🐣 Digital Beginner",
        "descripcion": "Empresa tradicional con procesos manuales, iniciando transformación",
        "sectores": ["🏭 Manufactura", "🏛️ Gobierno", "🏗️ Construcción"],
        "tamano_min": "Menos de $500M COP"
    },
    "innovation_theater": {
        "nombre": "🎭 Innovation Theater",
        "descripcion": "Buscan 'hacer IA' sin problema claro, riesgo de proyecto exploratorio",
        "sectores": ["Cualquiera"],
        "tamano_min": "Variable"
    },
    "distressed_fighter": {
        "nombre": "⚔️ Distressed Fighter",
        "descripcion": "Bajo presión competitiva extrema, necesita ROI inmediato",
        "sectores": ["Cualquiera"],
        "tamano_min": "Variable"
    },
    "tire_kicker": {
        "nombre": "🚫 Tire Kicker",
        "descripcion": "Solo cotizando, sin presupuesto ni urgencia real",
        "sectores": ["Cualquiera"],
        "tamano_min": "Variable"
    }
}
