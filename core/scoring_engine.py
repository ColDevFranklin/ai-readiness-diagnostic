from typing import Dict, Tuple
from core.models import (
    DiagnosticResponses,
    MadurezDigital,
    CapacidadInversion,
    ViabilidadComercial,
    DiagnosticScore,
    ProspectInfo
)


class ScoringEngine:
    """Motor de puntuación del diagnóstico"""

    def __init__(self):
        # Definir mapeos de respuestas a puntos
        self._init_scoring_maps()

    def _init_scoring_maps(self):
        """Inicializar mapeos de respuestas a puntuaciones"""

        # Q5: Toma de decisiones (0-10 puntos)
        self.decisiones_map = {
            "Basados en reportes automáticos de sistemas": 10,
            "Basados en reportes que alguien arma manualmente": 7,
            "Basados en Excel que alimentamos nosotros": 5,
            "Basados en intuición y experiencia": 3,
            "Basados en 'ir preguntando a cada área'": 1
        }

        # Q6: Procesos críticos (0-10 puntos)
        self.procesos_map = {
            "Están documentados y son iguales siempre": 10,
            "Dependen de quién los ejecute": 5,
            "Funcionan pero nadie sabe exactamente cómo": 3,
            "Cambian constantemente según la situación": 1
        }

        # Q7: Tareas repetitivas (0-10 puntos) - INVERTIDO
        self.repetitivas_map = {
            "Menos del 20% del tiempo": 10,
            "20-40% del tiempo": 7,
            "40-60% del tiempo": 4,
            "Más del 60% del tiempo": 2,
            "No tengo idea": 0
        }

        # Q8: Compartir información (0-10 puntos)
        self.integracion_map = {
            "Sí, todo está en sistemas conectados": 10,
            "Más o menos, hay que pedirse cosas por email/WhatsApp": 6,
            "No, cada área tiene su propia información": 3,
            "¿Qué información? (Cada uno tiene su Excel)": 1
        }

        # Q9: Equipo técnico (0-10 puntos para inversión)
        self.equipo_map = {
            "Sí, equipo completo (5+ personas)": 10,
            "Sí, pequeño (1-4 personas)": 7,
            "No, contratamos externos cuando se necesita": 4,
            "No, yo mismo/mi contador/mi sobrino nos ayuda": 1
        }

        # Q10: Capacidad implementación (0-15 puntos)
        self.implementacion_map = {
            "Tenemos presupuesto y podemos decidir": 15,
            "Tendríamos que aprobar presupuesto (1-3 meses)": 10,
            "Tendríamos que planificarlo para próximo año": 5,
            "No hay presupuesto disponible": 0
        }

        # Q11: Inversión reciente (0-10 puntos)
        self.inversion_map = {
            "Sí, inversiones significativas (>$50M COP)": 10,
            "Sí, inversiones moderadas ($10-50M COP)": 7,
            "Sí, inversiones pequeñas (<$10M COP)": 4,
            "No, seguimos con lo mismo de siempre": 0
        }

        # Q12: Frustración principal (0-10 puntos para viabilidad)
        self.frustracion_map = {
            "No puedo escalar sin contratar más gente": 10,
            "Perdemos clientes por servicio lento": 10,
            "Cometemos muchos errores manuales": 9,
            "No sé qué está pasando en tiempo real": 8,
            "Los costos operativos están muy altos": 9,
            "Otro": 5
        }

        # Q13: Urgencia (0-10 puntos)
        self.urgencia_map = {
            "Muy urgente, necesito resolver ya (próximos 3 meses)": 10,
            "Importante, quiero avanzar este año": 7,
            "Exploración, sin apuro": 3,
            "Solo estoy mirando opciones": 1
        }

        # Q14: Proceso aprobación (0-10 puntos)
        self.aprobacion_map = {
            "Nadie, yo decido": 10,
            "Mi socio(s)": 7,
            "Junta directiva": 5,
            "Varias personas (complejo)": 2
        }

        # Q15: Presupuesto (0-15 puntos pero también se usa en tamaño)
        self.presupuesto_map = {
            "Más de $60M COP": 15,
            "$30M - $60M COP": 12,
            "$10M - $30M COP": 8,
            "Menos de $10M COP": 3,
            "Prefiero no decirlo / No lo sé aún": 5
        }

        # Tamaño empresa por facturación (0-5 puntos)
        self.facturacion_map = {
            "Más de $10,000M COP": 5,
            "$2,000M - $10,000M COP": 4,
            "$500M - $2,000M COP": 3,
            "Menos de $500M COP": 1
        }

        # Tamaño empresa por empleados (complementario)
        self.empleados_map = {
            "Más de 500": 5,
            "201-500": 4,
            "51-200": 3,
            "21-50": 2,
            "1-20": 1
        }

    def calculate_madurez_digital(
        self,
        responses: DiagnosticResponses
    ) -> MadurezDigital:
        """Calcular score de madurez digital (0-40 puntos)"""

        decisiones = self.decisiones_map.get(responses.toma_decisiones, 0)
        procesos = self.procesos_map.get(responses.procesos_criticos, 0)
        integracion = self.integracion_map.get(responses.compartir_informacion, 0)
        eficiencia = self.repetitivas_map.get(responses.tareas_repetitivas, 0)

        return MadurezDigital(
            decisiones_basadas_datos=decisiones,
            procesos_estandarizados=procesos,
            sistemas_integrados=integracion,
            eficiencia_operativa=eficiencia,
            score_total=0  # Se calcula en __post_init__
        )

    def calculate_capacidad_inversion(
        self,
        responses: DiagnosticResponses,
        prospect_info: ProspectInfo
    ) -> CapacidadInversion:
        """Calcular score de capacidad de inversión (0-30 puntos)"""

        presupuesto = self.presupuesto_map.get(responses.presupuesto_rango, 0)
        historial = self.inversion_map.get(responses.inversion_reciente, 0)

        # Tamaño empresa: combinar facturación y empleados
        tamano_fact = self.facturacion_map.get(prospect_info.facturacion_rango, 0)
        tamano_emp = self.empleados_map.get(prospect_info.empleados_rango, 0)
        tamano = max(tamano_fact, tamano_emp)  # Tomar el más alto

        return CapacidadInversion(
            presupuesto_disponible=presupuesto,
            historial_inversion=historial,
            tamano_empresa=tamano,
            score_total=0  # Se calcula en __post_init__
        )

    def calculate_viabilidad_comercial(
        self,
        responses: DiagnosticResponses
    ) -> ViabilidadComercial:
        """Calcular score de viabilidad comercial (0-30 puntos)"""

        problema = self.frustracion_map.get(responses.frustracion_principal, 5)
        urgencia = self.urgencia_map.get(responses.urgencia, 0)
        decision = self.aprobacion_map.get(responses.proceso_aprobacion, 0)

        return ViabilidadComercial(
            problema_claro=problema,
            urgencia_real=urgencia,
            poder_decision=decision,
            score_total=0  # Se calcula en __post_init__
        )

    def calculate_motivacion_score(
        self,
        motivaciones: list
    ) -> int:
        """
        Calcular score adicional basado en motivaciones
        Retorna bonus de 0-5 puntos
        """
        bonus = 0

        # Motivaciones positivas
        if "Mis competidores están usando IA y me están dejando atrás" in motivaciones:
            bonus += 2
        if "Tengo procesos lentos y costosos que creo que la IA podría mejorar" in motivaciones:
            bonus += 2
        if "Quiero reducir costos operativos" in motivaciones:
            bonus += 1
        if "Tengo un problema específico que resolver" in motivaciones:
            bonus += 2

        # Motivaciones negativas
        if "Curiosidad / exploración general" in motivaciones and len(motivaciones) == 1:
            bonus -= 2
        if "Me mandaron a explorar esto (junta directiva/socios)" in motivaciones:
            bonus += 1  # Es neutral, alguien más tiene urgencia

        return max(0, min(5, bonus))  # Limitar a 0-5

    def calculate_confidence(
        self,
        score: DiagnosticScore,
        responses: DiagnosticResponses
    ) -> float:
        """
        Calcular confianza en la clasificación (0.0-1.0)
        Alta confianza = respuestas consistentes
        """
        confidence = 0.5  # Base

        # Aumentar confianza si score está lejos de umbrales
        if score.score_final >= 80 or score.score_final <= 30:
            confidence += 0.2

        # Reducir confianza si hubo respuestas "no sé"
        if responses.tareas_repetitivas == "No tengo idea":
            confidence -= 0.1
        if responses.presupuesto_rango == "Prefiero no decirlo / No lo sé aún":
            confidence -= 0.1

        # Aumentar confianza si hay consistencia entre señales
        if (score.madurez_digital.score_total >= 30 and
            score.capacidad_inversion.score_total >= 20):
            confidence += 0.1

        # ✅ CORRECCIÓN CRÍTICA: Acceso correcto a urgencia_real
        if (score.viabilidad_comercial.score_total >= 20 and
            score.viabilidad_comercial.urgencia_real >= 7):
            confidence += 0.1

        return max(0.0, min(1.0, confidence))

    def calculate_full_score(
        self,
        responses: DiagnosticResponses,
        prospect_info: ProspectInfo
    ) -> DiagnosticScore:
        """Calcular score completo del diagnóstico"""

        madurez = self.calculate_madurez_digital(responses)
        capacidad = self.calculate_capacidad_inversion(responses, prospect_info)
        viabilidad = self.calculate_viabilidad_comercial(responses)

        # Bonus por motivaciones
        bonus_motivacion = self.calculate_motivacion_score(responses.motivacion)

        # Crear score preliminar
        score = DiagnosticScore(
            madurez_digital=madurez,
            capacidad_inversion=capacidad,
            viabilidad_comercial=viabilidad,
            score_final=0,  # Se calcula en __post_init__
            tier=None,  # Se determina en __post_init__
            confianza_clasificacion=0.0
        )

        # Ajustar score final con bonus
        score.score_final = min(100, score.score_final + bonus_motivacion)

        # Recalcular tier si cambió el score
        if score.score_final >= 70:
            from core.models import Tier
            score.tier = Tier.A
        elif score.score_final >= 40:
            from core.models import Tier
            score.tier = Tier.B
        else:
            from core.models import Tier
            score.tier = Tier.C

        # Calcular confianza
        score.confianza_clasificacion = self.calculate_confidence(score, responses)

        return score

    def get_score_breakdown(
        self,
        score: DiagnosticScore
    ) -> Dict[str, any]:
        """Obtener desglose detallado del score para debugging"""

        return {
            "score_final": score.score_final,
            "tier": score.tier.value,
            "confianza": f"{score.confianza_clasificacion:.0%}",
            "madurez_digital": {
                "total": score.madurez_digital.score_total,
                "decisiones": score.madurez_digital.decisiones_basadas_datos,
                "procesos": score.madurez_digital.procesos_estandarizados,
                "integracion": score.madurez_digital.sistemas_integrados,
                "eficiencia": score.madurez_digital.eficiencia_operativa
            },
            "capacidad_inversion": {
                "total": score.capacidad_inversion.score_total,
                "presupuesto": score.capacidad_inversion.presupuesto_disponible,
                "historial": score.capacidad_inversion.historial_inversion,
                "tamano": score.capacidad_inversion.tamano_empresa
            },
            "viabilidad_comercial": {
                "total": score.viabilidad_comercial.score_total,
                "problema": score.viabilidad_comercial.problema_claro,
                "urgencia": score.viabilidad_comercial.urgencia_real,
                "decision": score.viabilidad_comercial.poder_decision
            }
        }
