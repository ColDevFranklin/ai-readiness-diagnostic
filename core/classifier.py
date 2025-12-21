"""
Clasificador de arquetipos y generador de insights
Identifica el perfil del prospecto y genera recomendaciones estratégicas
"""

from typing import List, Dict, Tuple
from core.models import (
    DiagnosticScore, DiagnosticResponses, ProspectInfo,
    Arquetipo, QuickWin, RedFlag, Insight, ReunionPrep
)


class ArchetypeClassifier:
    """Clasificador de arquetipos empresariales"""

    def __init__(self):
        self._init_archetype_definitions()

    def _init_archetype_definitions(self):
        """Definir características de cada arquetipo"""

        self.archetypes = {
            "traditional_giant": {
                "nombre": "🏦 Traditional Giant",
                "descripcion": "Empresa grande tradicional con sistemas legacy, bajo presión competitiva",
                "frustraciones": [
                    "Todo demora semanas en implementarse",
                    "Sistemas no hablan entre sí",
                    "Perdemos clientes por servicio lento",
                    "Competidores más ágiles nos están ganando"
                ],
                "motivadores": [
                    "Sobrevivencia competitiva",
                    "Mandato de junta directiva",
                    "Presión regulatoria",
                    "Amenaza de fintechs/startups"
                ],
                "objeciones": [
                    "¿Cuánto riesgo tiene esto?",
                    "¿Ya está probado en el sector?",
                    "¿Cuánto tiempo toma?",
                    "¿Qué pasa con nuestros sistemas actuales?"
                ],
                "enfoque": [
                    "Mostrar casos de éxito en su sector",
                    "Cuantificar ROI específicamente",
                    "Implementación gradual y de bajo riesgo",
                    "Énfasis en seguridad y compliance",
                    "Integración con sistemas legacy"
                ],
                "punto_entrada": "Automatización de procesos back-office críticos",
                "potencial": "$$$"
            },
            "ambitious_scaler": {
                "nombre": "📈 Ambitious Scaler",
                "descripcion": "Empresa en crecimiento que no logra escalar operaciones",
                "frustraciones": [
                    "No puedo crecer sin contratar más gente",
                    "Los márgenes se están reduciendo con el crecimiento",
                    "Procesos manuales nos limitan",
                    "Cometemos errores por ir muy rápido"
                ],
                "motivadores": [
                    "Alcanzar objetivos de crecimiento",
                    "Mantener márgenes rentables",
                    "Superar al líder del mercado",
                    "Prepararse para ronda de inversión"
                ],
                "objeciones": [
                    "¿Puedo implementar esto rápido?",
                    "¿Funcionará con mi crecimiento acelerado?",
                    "¿Cuánto tiempo de mi equipo necesita?",
                    "¿Y si cambian mis necesidades?"
                ],
                "enfoque": [
                    "Velocidad de implementación",
                    "Automatización de procesos que frenan crecimiento",
                    "Quick wins visibles en 60-90 días",
                    "Arquitectura escalable",
                    "ROI en reducción de contrataciones"
                ],
                "punto_entrada": "Automatización de operaciones core (pedidos, inventario, atención)",
                "potencial": "$$"
            },
            "digital_beginner": {
                "nombre": "🐣 Digital Beginner",
                "descripcion": "Empresa tradicional con procesos manuales, iniciando transformación",
                "frustraciones": [
                    "Todo es manual y lento",
                    "No tenemos visibilidad de la operación",
                    "Dependemos de personas clave",
                    "Cometemos muchos errores"
                ],
                "motivadores": [
                    "Modernización necesaria",
                    "Cambio generacional en liderazgo",
                    "Presión de clientes por mejores servicios",
                    "Reducción de costos operativos"
                ],
                "objeciones": [
                    "¿Mi equipo podrá adaptarse?",
                    "¿No es muy costoso?",
                    "¿Realmente necesitamos IA?",
                    "¿Por dónde empezamos?"
                ],
                "enfoque": [
                    "Educación en transformación digital primero",
                    "Empezar con digitalización básica",
                    "Cambio cultural y gestión del cambio",
                    "Hitos pequeños y frecuentes",
                    "Capacitación intensiva del equipo"
                ],
                "punto_entrada": "Digitalización de procesos críticos + BI básico",
                "potencial": "$"
            },
            "innovation_theater": {
                "nombre": "🎭 Innovation Theater",
                "descripcion": "Buscan 'hacer IA' sin problema claro, riesgo alto",
                "frustraciones": [
                    "Tenemos que innovar",
                    "Todos hablan de IA",
                    "No queremos quedarnos atrás",
                    "La competencia ya tiene IA"
                ],
                "motivadores": [
                    "Presión de stakeholders",
                    "FOMO (Fear of Missing Out)",
                    "Marketing / relaciones públicas",
                    "Experimentación sin ROI claro"
                ],
                "objeciones": [
                    "¿Podemos hacerlo más barato?",
                    "¿Qué pueden hacer otras consultoras?",
                    "¿Incluye el desarrollo completo?",
                    "¿No podemos solo hacer un piloto?"
                ],
                "enfoque": [
                    "Calificar muy bien antes de invertir tiempo",
                    "Alinear expectativas con realidad",
                    "Definir problema específico primero",
                    "Propuesta educativa (workshop) en vez de proyecto",
                    "Evitar compromisos de largo plazo"
                ],
                "punto_entrada": "Diagnóstico $12K para validar si hay caso de negocio real",
                "potencial": "⚠️"
            },
            "distressed_fighter": {
                "nombre": "⚔️ Distressed Fighter",
                "descripcion": "Bajo presión competitiva extrema, necesita ROI inmediato",
                "frustraciones": [
                    "Estamos perdiendo participación de mercado",
                    "Los competidores son más eficientes",
                    "Nuestros costos son muy altos",
                    "Clientes se están yendo"
                ],
                "motivadores": [
                    "Sobrevivencia",
                    "Recuperar competitividad",
                    "Reducción drástica de costos",
                    "Retener clientes clave"
                ],
                "objeciones": [
                    "¿Cuánto tiempo tarda en dar resultados?",
                    "¿El ROI es garantizado?",
                    "¿Podemos pagar en hitos?",
                    "¿Qué pasa si no funciona?"
                ],
                "enfoque": [
                    "ROI medible y rápido (90 días)",
                    "Enfoque en reducción de costos inmediata",
                    "Quick wins antes que transformación",
                    "Modelo de pago por resultados si es posible",
                    "Evaluar viabilidad financiera del cliente"
                ],
                "punto_entrada": "Automatización de proceso más costoso",
                "potencial": "$$"
            },
            "tire_kicker": {
                "nombre": "🚫 Tire Kicker",
                "descripcion": "Solo cotizando, sin presupuesto ni urgencia real",
                "frustraciones": [
                    "Curiosidad general",
                    "Tarea asignada por jefe",
                    "Comparando opciones sin compromiso",
                    "Estudiante/investigador disfrazado"
                ],
                "motivadores": [
                    "Cumplir con tarea asignada",
                    "Educación personal",
                    "Benchmark de mercado",
                    "Posible futuro (sin timeline)"
                ],
                "objeciones": [
                    "Todo objeción es válida",
                    "No hay urgencia real",
                    "Probablemente no llegue a contratar"
                ],
                "enfoque": [
                    "NO invertir tiempo en reuniones 1-on-1",
                    "Respuesta automatizada con recursos",
                    "Invitar a webinar/workshop grupal",
                    "Nutrir para largo plazo (newsletter)"
                ],
                "punto_entrada": "Ninguno - Descalificar cortésmente",
                "potencial": "🚫"
            }
        }

    def classify(
        self,
        score: DiagnosticScore,
        responses: DiagnosticResponses,
        prospect_info: ProspectInfo
    ) -> Arquetipo:
        """Clasificar arquetipo basado en score y respuestas"""

        # Scores de compatibilidad con cada arquetipo
        archetype_scores = {}

        # TRADITIONAL GIANT
        archetype_scores["traditional_giant"] = self._score_traditional_giant(
            score, responses, prospect_info
        )

        # AMBITIOUS SCALER
        archetype_scores["ambitious_scaler"] = self._score_ambitious_scaler(
            score, responses, prospect_info
        )

        # DIGITAL BEGINNER
        archetype_scores["digital_beginner"] = self._score_digital_beginner(
            score, responses, prospect_info
        )

        # INNOVATION THEATER
        archetype_scores["innovation_theater"] = self._score_innovation_theater(
            score, responses, prospect_info
        )

        # DISTRESSED FIGHTER
        archetype_scores["distressed_fighter"] = self._score_distressed_fighter(
            score, responses, prospect_info
        )

        # TIRE KICKER
        archetype_scores["tire_kicker"] = self._score_tire_kicker(
            score, responses, prospect_info
        )

        # Seleccionar el arquetipo con mayor score
        best_archetype = max(archetype_scores, key=archetype_scores.get)
        confidence = archetype_scores[best_archetype]

        arch_def = self.archetypes[best_archetype]

        return Arquetipo(
            tipo=best_archetype,
            nombre=arch_def["nombre"],
            descripcion=arch_def["descripcion"],
            frustraciones_tipicas=arch_def["frustraciones"],
            motivadores=arch_def["motivadores"],
            objeciones_esperadas=arch_def["objeciones"],
            enfoque_comercial=arch_def["enfoque"],
            punto_entrada_ideal=arch_def["punto_entrada"],
            potencial_expansion=arch_def["potencial"],
            confianza=confidence
        )

    def _score_traditional_giant(
        self, score, responses, prospect_info
    ) -> float:
        """Score de compatibilidad con Traditional Giant (0.0-1.0)"""
        points = 0.0

        # Sector típico
        if prospect_info.sector in ["🏦 Banca", "🛡️ Seguros"]:
            points += 0.3

        # Tamaño grande
        if prospect_info.facturacion_rango in ["$2,000M - $10,000M COP", "Más de $10,000M COP"]:
            points += 0.2

        # Madurez digital media (tienen sistemas pero no integrados)
        if 20 <= score.madurez_digital.score_total <= 30:
            points += 0.2

        # Presión competitiva
        if "Mis competidores están usando IA y me están dejando atrás" in responses.motivacion:
            points += 0.2

        # Tiene presupuesto
        if score.capacidad_inversion.score_total >= 20:
            points += 0.1

        return min(1.0, points)

    def _score_ambitious_scaler(
        self, score, responses, prospect_info
    ) -> float:
        """Score de compatibilidad con Ambitious Scaler"""
        points = 0.0

        # Sector típico
        if prospect_info.sector in ["🛒 Retail", "💼 Servicios Profesionales", "🚚 Logística/Transporte"]:
            points += 0.3

        # Tamaño mediano-grande
        if prospect_info.facturacion_rango in ["$500M - $2,000M COP", "$2,000M - $10,000M COP"]:
            points += 0.2

        # Frustración de escalabilidad
        if responses.frustracion_principal == "No puedo escalar sin contratar más gente":
            points += 0.3

        # Invirtieron recientemente
        if "Sí, inversiones" in responses.inversion_reciente:
            points += 0.1

        # Urgencia media-alta
        if score.viabilidad_comercial.urgencia_real >= 7:
            points += 0.1

        return min(1.0, points)

    def _score_digital_beginner(
        self, score, responses, prospect_info
    ) -> float:
        """Score de compatibilidad con Digital Beginner"""
        points = 0.0

        # Madurez digital baja
        if score.madurez_digital.score_total <= 20:
            points += 0.4

        # Sin inversión previa
        if responses.inversion_reciente == "No, seguimos con lo mismo de siempre":
            points += 0.2

        # Procesos no documentados
        if "no sabe" in responses.procesos_criticos.lower() or "cambian" in responses.procesos_criticos.lower():
            points += 0.2

        # Sector tradicional
        if prospect_info.sector in ["🏭 Manufactura", "🏛️ Gobierno", "🏗️ Construcción"]:
            points += 0.2

        return min(1.0, points)

    def _score_innovation_theater(
        self, score, responses, prospect_info
    ) -> float:
        """Score de compatibilidad con Innovation Theater"""
        points = 0.0

        # Solo curiosidad
        if responses.motivacion == ["Curiosidad / exploración general"]:
            points += 0.4

        # Sin urgencia
        if responses.urgencia in ["Exploración, sin apuro", "Solo estoy mirando opciones"]:
            points += 0.3

        # Sin presupuesto claro
        if responses.presupuesto_rango == "Prefiero no decirlo / No lo sé aún":
            points += 0.2

        # Viabilidad comercial baja
        if score.viabilidad_comercial.score_total <= 15:
            points += 0.1

        return min(1.0, points)

    def _score_distressed_fighter(
        self, score, responses, prospect_info
    ) -> float:
        """Score de compatibilidad con Distressed Fighter"""
        points = 0.0

        # Urgencia muy alta
        if responses.urgencia == "Muy urgente, necesito resolver ya (próximos 3 meses)":
            points += 0.3

        # Frustración de competitividad
        if responses.frustracion_principal in ["Perdemos clientes por servicio lento", "Los costos operativos están muy altos"]:
            points += 0.2

        # Motivación competitiva
        if "Mis competidores están usando IA y me están dejando atrás" in responses.motivacion:
            points += 0.3

        # Tiene presupuesto (capacidad de inversión)
        if score.capacidad_inversion.score_total >= 15:
            points += 0.2

        return min(1.0, points)

    def _score_tire_kicker(
        self, score, responses, prospect_info
    ) -> float:
        """Score de compatibilidad con Tire Kicker"""
        points = 0.0

        # Score total muy bajo
        if score.score_final < 30:
            points += 0.4

        # Sin presupuesto
        if responses.presupuesto_rango == "Menos de $10M COP":
            points += 0.2

        # No es decisor
        if responses.proceso_aprobacion == "Varias personas (complejo)":
            points += 0.2

        # Empresa muy pequeña
        if prospect_info.facturacion_rango == "Menos de $500M COP" and prospect_info.empleados_rango == "1-20":
            points += 0.2

        return min(1.0, points)


class InsightGenerator:
    """Generador de insights y recomendaciones"""

    def generate_quick_wins(
        self,
        score: DiagnosticScore,
        responses: DiagnosticResponses,
        arquetipo: Arquetipo
    ) -> List[QuickWin]:
        """Generar quick wins basados en respuestas"""

        quick_wins = []

        # Quick win basado en frustración principal
        frustracion_map = {
            "No puedo escalar sin contratar más gente": QuickWin(
                titulo="Automatización de Proceso Administrativo",
                descripcion="Automatizar proceso de mayor volumen manual (pedidos, facturación, o reportes) para reducir 30-40% de carga administrativa",
                impacto_estimado="Equivalente a 2-3 personas FTE",
                tiempo_implementacion="60-90 días",
                inversion_aproximada="$15M-25M COP"
            ),
            "Perdemos clientes por servicio lento": QuickWin(
                titulo="Chatbot de Atención al Cliente",
                descripcion="Implementar asistente virtual para resolver 60-70% de consultas frecuentes 24/7",
                impacto_estimado="Reducción 50% tiempo de respuesta",
                tiempo_implementacion="45-60 días",
                inversion_aproximada="$12M-20M COP"
            ),
            "Cometemos muchos errores manuales": QuickWin(
                titulo="Validación Automática de Datos",
                descripcion="Sistema de validación y verificación automática en procesos críticos",
                impacto_estimado="Reducción 80% errores operativos",
                tiempo_implementacion="30-45 días",
                inversion_aproximada="$8M-15M COP"
            ),
            "No sé qué está pasando en tiempo real": QuickWin(
                titulo="Dashboard Gerencial en Tiempo Real",
                descripcion="Panel de control ejecutivo con KPIs críticos actualizados automáticamente",
                impacto_estimado="Visibilidad inmediata de operación",
                tiempo_implementacion="30-45 días",
                inversion_aproximada="$10M-18M COP"
            ),
            "Los costos operativos están muy altos": QuickWin(
                titulo="Optimización de Procesos con IA",
                descripcion="Identificar y automatizar los 3 procesos más costosos",
                impacto_estimado="Reducción 15-25% costos operativos",
                tiempo_implementacion="90-120 días",
                inversion_aproximada="$20M-35M COP"
            )
        }

        primary_qw = frustracion_map.get(responses.frustracion_principal)
        if primary_qw:
            quick_wins.append(primary_qw)

        # Quick win secundario basado en madurez de datos
        if score.madurez_digital.decisiones_basadas_datos <= 5:
            quick_wins.append(QuickWin(
                titulo="Fundamentos de Business Intelligence",
                descripcion="Implementar BI básico para consolidar datos dispersos y generar reportes automáticos",
                impacto_estimado="Base para decisiones data-driven",
                tiempo_implementacion="60 días",
                inversion_aproximada="$8M-12M COP"
            ))

        # Quick win terciario basado en integración
        if score.madurez_digital.sistemas_integrados <= 5:
            quick_wins.append(QuickWin(
                titulo="Integración de Sistemas Críticos",
                descripcion="Conectar los 2-3 sistemas más importantes vía APIs para eliminar trabajo manual",
                impacto_estimado="Reducción 40% tiempo en transferencia de datos",
                tiempo_implementacion="45-60 días",
                inversion_aproximada="$10M-15M COP"
            ))

        return quick_wins[:3]  # Máximo 3 quick wins

    def generate_red_flags(
        self,
        score: DiagnosticScore,
        responses: DiagnosticResponses,
        prospect_info: ProspectInfo
    ) -> List[RedFlag]:
        """Identificar red flags potenciales"""

        red_flags = []

        # Red flag: No es decisor y proceso complejo
        if responses.proceso_aprobacion == "Varias personas (complejo)":
            red_flags.append(RedFlag(
                titulo="Proceso de Aprobación Complejo",
                descripcion="Múltiples aprobadores pueden alargar el ciclo de ventas significativamente",
                severidad="media",
                mitigacion="Identificar sponsor ejecutivo early, mapear stakeholders, preparar business case sólido"
            ))

        # Red flag: Sin presupuesto claro
        if responses.presupuesto_rango in ["Menos de $10M COP", "Prefiero no decirlo / No lo sé aún"]:
            red_flags.append(RedFlag(
                titulo="Presupuesto Indefinido",
                descripcion="Sin presupuesto claro puede indicar falta de compromiso real",
                severidad="alta",
                mitigacion="Validar en primera reunión si hay budget aprobado o timeline de aprobación"
            ))

        # Red flag: Cultura de resistencia al cambio
        if responses.procesos_criticos in ["Dependen de quién los ejecute", "Funcionan pero nadie sabe exactamente cómo"]:
            red_flags.append(RedFlag(
                titulo="Cultura Resistente al Cambio",
                descripcion="Procesos dependientes de personas pueden indicar resistencia a estandarización",
                severidad="media",
                mitigacion="Incluir módulo de change management, identificar champions internos, piloto pequeño primero"
            ))

        # Red flag: Solo curiosidad
        if responses.motivacion == ["Curiosidad / exploración general"] and responses.urgencia == "Solo estoy mirando opciones":
            red_flags.append(RedFlag(
                titulo="Falta de Urgencia Real",
                descripcion="Exploración sin problema específico raramente convierte",
                severidad="alta",
                mitigacion="Calificar rigurosamente, ofrecer contenido educativo en vez de consultoría, nutrir para futuro"
            ))

        return red_flags

    def generate_insights(
        self,
        score: DiagnosticScore,
        responses: DiagnosticResponses,
        arquetipo: Arquetipo
    ) -> List[Insight]:
        """Generar insights estratégicos"""

        insights = []

        # Insight de fortalezas
        if score.capacidad_inversion.score_total >= 20:
            insights.append(Insight(
                categoria="fortaleza",
                titulo="Capacidad de Inversión Sólida",
                descripcion=f"Con score de {score.capacidad_inversion.score_total}/30 en capacidad de inversión, el prospecto tiene músculo financiero para proyectos significativos",
                recomendacion="Proponer solución robusta ($25K-45K) en vez de aproximación minimalista"
            ))

        # Insight de oportunidad
        if score.madurez_digital.score_total <= 25:
            insights.append(Insight(
                categoria="oportunidad",
                titulo="Alto Potencial de Mejora Operativa",
                descripcion="Baja madurez digital significa múltiples oportunidades de quick wins y ROI alto",
                recomendacion="Empezar con automatización de proceso más doloroso para demostrar valor rápido"
            ))

        # Insight de riesgo
        if score.viabilidad_comercial.score_total <= 15:
            insights.append(Insight(
                categoria="riesgo",
                titulo="Viabilidad Comercial Cuestionable",
                descripcion=f"Score bajo ({score.viabilidad_comercial.score_total}/30) indica riesgo de que no cierre o ciclo muy largo",
                recomendacion="Calificar rigurosamente en primera llamada antes de invertir tiempo en propuesta"
            ))

        return insights

    def generate_reunion_prep(
        self,
        score: DiagnosticScore,
        responses: DiagnosticResponses,
        arquetipo: Arquetipo,
        prospect_info: ProspectInfo
    ) -> ReunionPrep:
        """Generar preparación para reunión"""

        # Investigación previa sugerida
        investigacion = [
            f"Buscar '{prospect_info.nombre_empresa}' en Google/LinkedIn",
            f"Identificar competidores principales en sector {prospect_info.sector}",
            "Revisar presencia digital (website, redes sociales)",
            "Buscar noticias recientes sobre la empresa"
        ]

        # Materiales a llevar
        materiales = [
            f"Caso de éxito: {arquetipo.punto_entrada_ideal}",
            "Demo relevante según frustración principal",
            "One-pager: ROI estimado",
            "Propuesta preliminar con rangos de pricing"
        ]

        # Preguntas clave según arquetipo
        preguntas = self._get_preguntas_por_arquetipo(arquetipo, responses)

        # Objeciones probables
        objeciones = {
            obj: self._get_respuesta_objecion(obj, arquetipo)
            for obj in arquetipo.objeciones_esperadas[:3]
        }

        # Insight clave
        insight_clave = self._get_insight_clave(score, responses, arquetipo)

        # Probabilidad de cierre
        prob_cierre = self._estimate_close_probability(score, responses)

        return ReunionPrep(
            investigacion_previa=investigacion,
            materiales_llevar=materiales,
            preguntas_clave=preguntas,
            objeciones_probables=objeciones,
            insight_clave=insight_clave,
            probabilidad_cierre=prob_cierre
        )

    def _get_preguntas_por_arquetipo(
        self, arquetipo: Arquetipo, responses: DiagnosticResponses
    ) -> List[str]:
        """Generar preguntas clave según arquetipo"""

        preguntas_base = [
            f"¿Cuál es el proceso/área que más le duele hoy? (validar '{responses.frustracion_principal}')",
            "¿Ha intentado resolver esto antes? ¿Qué pasó?",
            "Si pudiera resolver esto en los próximos 90 días, ¿qué impacto tendría en el negocio?"
        ]

        if arquetipo.tipo == "traditional_giant":
            preguntas_base.extend([
                "¿Qué sistemas legacy críticos tenemos que considerar?",
                "¿Cuál es el proceso de aprobación para proyectos de este tipo?"
            ])
        elif arquetipo.tipo == "ambitious_scaler":
            preguntas_base.extend([
                "¿Cuánto están creciendo mes a mes?",
                "¿Qué proceso les está limitando más el crecimiento?"
            ])

        return preguntas_base

    def _get_respuesta_objecion(
        self, objecion: str, arquetipo: Arquetipo
    ) -> str:
        """Generar respuesta a objeción común"""

        respuestas_default = {
            "¿Cuánto tiempo toma?": "Piloto funcional en 90 días, resultados visibles en 45 días",
            "¿Cuánto riesgo tiene esto?": "Implementación gradual con validación en cada hito",
            "¿Ya está probado en el sector?": "[Mostrar caso de éxito comparable]",
            "¿Podemos hacerlo más barato?": "El costo real está en NO hacerlo - [cuantificar costo de inacción]"
        }

        return respuestas_default.get(objecion, "Escuchar, validar preocupación, dar evidencia")

    def _get_insight_clave(
        self, score: DiagnosticScore, responses: DiagnosticResponses, arquetipo: Arquetipo
    ) -> str:
        """Generar insight clave para la reunión"""

        if arquetipo.tipo == "ambitious_scaler":
            return f"Este cliente está en punto de inflexión: creciendo rápido pero operación no escala. Tu ángulo: 'No contrates más gente, automatiza lo que ya tienes.'"
        elif arquetipo.tipo == "traditional_giant":
            return "Cliente tradicional amenazado por competidores ágiles. Tu ángulo: 'Moderniza sin romper lo que funciona.'"
        elif arquetipo.tipo == "distressed_fighter":
            return "Cliente bajo presión extrema. Tu ángulo: 'ROI medible en 90 días o menos.'"
        else:
            return f"Enfocarse en resolver el problema específico: {responses.frustracion_principal}"

    def _estimate_close_probability(
        self, score: DiagnosticScore, responses: DiagnosticResponses
    ) -> int:
        """Estimar probabilidad de cierre (0-100)"""

        prob = 30  # Base

        # Tier A aumenta probabilidad
        if score.tier.value == "A":
            prob += 40
        elif score.tier.value == "B":
            prob += 20

        # Urgencia aumenta probabilidad
        if responses.urgencia == "Muy urgente, necesito resolver ya (próximos 3 meses)":
            prob += 20
        elif responses.urgencia == "Importante, quiero avanzar este año":
            prob += 10

        # Decisor aumenta probabilidad
        if responses.proceso_aprobacion == "Nadie, yo decido":
            prob += 10

        return min(100, prob)
