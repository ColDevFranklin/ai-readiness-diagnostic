"""
Modelos de datos para el sistema de diagnóstico AI Readiness
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class Tier(Enum):
    """Clasificación de tier del prospecto"""
    A = "A"  # Cliente ideal (70-100)
    B = "B"  # Potencial cultivable (40-69)
    C = "C"  # No invertir tiempo (0-39)


@dataclass
class ProspectInfo:
    """Información básica del prospecto"""
    nombre_empresa: str
    sector: str
    facturacion_rango: str
    empleados_rango: str
    contacto_nombre: str
    contacto_email: str
    contacto_telefono: str
    cargo: str
    ciudad: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DiagnosticResponses:
    """Respuestas al diagnóstico"""
    # Bloque 1: Identificación (Q1-Q4)
    motivacion: List[str]

    # Bloque 2: Diagnóstico operativo (Q5-Q12)
    toma_decisiones: str
    procesos_criticos: str
    tareas_repetitivas: str
    compartir_informacion: str
    equipo_tecnico: str
    capacidad_implementacion: str
    inversion_reciente: str
    frustracion_principal: str

    # Bloque 3: Viabilidad comercial (Q13-Q15)
    urgencia: str
    proceso_aprobacion: str
    presupuesto_rango: str


@dataclass
class MadurezDigital:
    """Score de madurez digital por subdimensión"""
    decisiones_basadas_datos: int  # 0-10
    procesos_estandarizados: int  # 0-10
    sistemas_integrados: int  # 0-10
    eficiencia_operativa: int  # 0-10
    score_total: int  # 0-40

    def __post_init__(self):
        self.score_total = (
            self.decisiones_basadas_datos +
            self.procesos_estandarizados +
            self.sistemas_integrados +
            self.eficiencia_operativa
        )


@dataclass
class CapacidadInversion:
    """Score de capacidad de inversión"""
    presupuesto_disponible: int  # 0-15
    historial_inversion: int  # 0-10
    tamano_empresa: int  # 0-5
    score_total: int  # 0-30

    def __post_init__(self):
        self.score_total = (
            self.presupuesto_disponible +
            self.historial_inversion +
            self.tamano_empresa
        )


@dataclass
class ViabilidadComercial:
    """Score de viabilidad comercial"""
    problema_claro: int  # 0-10
    urgencia_real: int  # 0-10
    poder_decision: int  # 0-10
    score_total: int  # 0-30

    def __post_init__(self):
        self.score_total = (
            self.problema_claro +
            self.urgencia_real +
            self.poder_decision
        )


@dataclass
class DiagnosticScore:
    """Score completo del diagnóstico"""
    madurez_digital: MadurezDigital
    capacidad_inversion: CapacidadInversion
    viabilidad_comercial: ViabilidadComercial
    score_final: int  # 0-100
    tier: Tier
    confianza_clasificacion: float  # 0.0-1.0

    def __post_init__(self):
        self.score_final = (
            self.madurez_digital.score_total +
            self.capacidad_inversion.score_total +
            self.viabilidad_comercial.score_total
        )

        # Determinar tier basado en score
        if self.score_final >= 70:
            self.tier = Tier.A
        elif self.score_final >= 40:
            self.tier = Tier.B
        else:
            self.tier = Tier.C


@dataclass
class Arquetipo:
    """Arquetipo identificado del prospecto"""
    tipo: str  # traditional_giant, ambitious_scaler, etc.
    nombre: str  # Nombre display
    descripcion: str
    frustraciones_tipicas: List[str]
    motivadores: List[str]
    objeciones_esperadas: List[str]
    enfoque_comercial: List[str]
    punto_entrada_ideal: str
    potencial_expansion: str
    confianza: float  # 0.0-1.0


@dataclass
class QuickWin:
    """Quick win identificado"""
    titulo: str
    descripcion: str
    impacto_estimado: str
    tiempo_implementacion: str
    inversion_aproximada: str


@dataclass
class RedFlag:
    """Red flag identificado"""
    titulo: str
    descripcion: str
    severidad: str  # baja, media, alta
    mitigacion: str


@dataclass
class Insight:
    """Insight generado del diagnóstico"""
    categoria: str  # fortaleza, oportunidad, riesgo
    titulo: str
    descripcion: str
    recomendacion: str


@dataclass
class ReunionPrep:
    """Preparación para reunión con el prospecto"""
    investigacion_previa: List[str]
    materiales_llevar: List[str]
    preguntas_clave: List[str]
    objeciones_probables: Dict[str, str]
    insight_clave: str
    probabilidad_cierre: int  # 0-100


@dataclass
class DiagnosticResult:
    """Resultado completo del diagnóstico"""
    prospect_info: ProspectInfo
    responses: DiagnosticResponses
    score: DiagnosticScore
    arquetipo: Arquetipo
    quick_wins: List[QuickWin]
    red_flags: List[RedFlag]
    insights: List[Insight]
    servicio_sugerido: str
    monto_sugerido_min: int
    monto_sugerido_max: int
    reunion_prep: ReunionPrep

    # Metadata
    diagnostic_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardData:
    """Datos agregados para el dashboard de Andrés"""
    total_diagnosticos: int
    tier_a_count: int
    tier_b_count: int
    tier_c_count: int
    arquetipos_distribucion: Dict[str, int]
    sectores_distribucion: Dict[str, int]
    score_promedio: float
    conversion_rate_estimada: float
    pipeline_value_estimado: int
    ultimos_diagnosticos: List[DiagnosticResult]
