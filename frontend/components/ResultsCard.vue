<template>
  <div class="results-card">
    <!-- Header con título -->
    <div class="card-header">
      <h3 class="text-2xl font-bold text-slate-200">
        {{ title || 'Resultados del Diagnóstico' }}
      </h3>
      <p v-if="subtitle" class="text-sm text-slate-400 mt-1">
        {{ subtitle }}
      </p>
    </div>

    <!-- Grid de métricas principales -->
    <div class="metrics-grid">
      <!-- Score Total -->
      <div class="metric-card bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-500/30">
        <div class="metric-icon">
          <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div class="metric-content">
          <div class="metric-value text-blue-400">{{ score }}</div>
          <div class="metric-label">Puntaje Total</div>
          <div class="metric-sublabel">de 100 puntos</div>
        </div>
      </div>

      <!-- Tier / Clasificación -->
      <div
        class="metric-card border"
        :class="tierStyles.background"
      >
        <div class="metric-icon">
          <svg class="w-6 h-6" :class="tierStyles.text" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        </div>
        <div class="metric-content">
          <div class="metric-value" :class="tierStyles.text">
            Tier {{ tier }}
          </div>
          <div class="metric-label">Clasificación</div>
          <div class="metric-sublabel">{{ tierDescription }}</div>
        </div>
      </div>
    </div>

    <!-- Información detallada -->
    <div class="details-section">
      <!-- Arquetipo -->
      <div class="detail-card">
        <div class="detail-header">
          <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span class="detail-title">Arquetipo Organizacional</span>
        </div>
        <p class="detail-content text-lg font-semibold text-slate-200">
          {{ arquetipo }}
        </p>
      </div>

      <!-- Servicio Sugerido -->
      <div class="detail-card">
        <div class="detail-header">
          <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span class="detail-title">Servicio Recomendado</span>
        </div>
        <p class="detail-content text-slate-300">
          {{ servicio }}
        </p>
      </div>

      <!-- Inversión -->
      <div class="detail-card bg-slate-800/30 border-slate-600">
        <div class="detail-header">
          <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="detail-title">Inversión Sugerida</span>
        </div>
        <p class="detail-content text-xl font-bold text-green-400">
          ${{ formatCurrency(montoMin) }} - ${{ formatCurrency(montoMax) }} COP
        </p>
        <p class="text-xs text-slate-500 mt-1">
          Rango estimado según madurez detectada
        </p>
      </div>
    </div>

    <!-- Scores por dimensión (opcional) -->
    <div v-if="showDimensionScores && dimensionScores" class="dimensions-section">
      <h4 class="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
        </svg>
        Puntajes por Dimensión
      </h4>
      <div class="dimensions-grid">
        <div
          v-for="(value, dimension) in dimensionScores"
          :key="dimension"
          class="dimension-item"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium text-slate-300">{{ dimension }}</span>
            <span class="text-sm font-bold text-blue-400">{{ value }}/25</span>
          </div>
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${(value / 25) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer con acciones opcionales -->
    <div v-if="$slots.actions" class="card-footer">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * ResultsCard - Tarjeta de visualización de resultados del diagnóstico
 *
 * @component
 * @example
 * <ResultsCard
 *   :score="85"
 *   tier="A"
 *   arquetipo="Visionario Digital"
 *   servicio="Implementación Completa IA"
 *   :monto-min="35000000"
 *   :monto-max="45000000"
 * />
 */

const props = defineProps({
  /** Título de la card (opcional) */
  title: {
    type: String,
    default: ''
  },

  /** Subtítulo de la card (opcional) */
  subtitle: {
    type: String,
    default: ''
  },

  /** Score total (0-100) */
  score: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100
  },

  /** Tier de clasificación (A, B, o C) */
  tier: {
    type: String,
    required: true,
    validator: (value) => ['A', 'B', 'C'].includes(value)
  },

  /** Arquetipo organizacional */
  arquetipo: {
    type: String,
    required: true
  },

  /** Servicio recomendado */
  servicio: {
    type: String,
    required: true
  },

  /** Monto mínimo de inversión (COP) */
  montoMin: {
    type: Number,
    required: true
  },

  /** Monto máximo de inversión (COP) */
  montoMax: {
    type: Number,
    required: true
  },

  /** Mostrar scores por dimensión */
  showDimensionScores: {
    type: Boolean,
    default: false
  },

  /** Objeto con scores por dimensión (Datos, Talento, Procesos, Infraestructura) */
  dimensionScores: {
    type: Object,
    default: null
  }
})

// Estilos dinámicos según Tier
const tierStyles = computed(() => {
  const styles = {
    'A': {
      background: 'bg-gradient-to-br from-green-500/20 to-green-600/20 border-green-500/30',
      text: 'text-green-400'
    },
    'B': {
      background: 'bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 border-yellow-500/30',
      text: 'text-yellow-400'
    },
    'C': {
      background: 'bg-gradient-to-br from-red-500/20 to-red-600/20 border-red-500/30',
      text: 'text-red-400'
    }
  }
  return styles[props.tier] || styles['C']
})

// Descripción del Tier
const tierDescription = computed(() => {
  const descriptions = {
    'A': 'Madurez Alta',
    'B': 'Madurez Media',
    'C': 'Madurez Inicial'
  }
  return descriptions[props.tier] || ''
})

// Formatear moneda
const formatCurrency = (amount) => {
  return (amount / 1000000).toFixed(1) + 'M'
}
</script>

<style scoped>
.results-card {
  @apply bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-slate-700;
}

.card-header {
  @apply mb-8 pb-6 border-b border-slate-700;
}

.metrics-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4 mb-8;
}

.metric-card {
  @apply p-6 rounded-lg border transition-all duration-300;
  @apply hover:scale-105 hover:shadow-lg;
}

.metric-icon {
  @apply mb-3;
}

.metric-content {
  @apply text-center;
}

.metric-value {
  @apply text-4xl font-bold mb-1;
}

.metric-label {
  @apply text-sm text-slate-400 font-medium;
}

.metric-sublabel {
  @apply text-xs text-slate-500 mt-1;
}

.details-section {
  @apply space-y-4 mb-8;
}

.detail-card {
  @apply p-5 bg-slate-900/30 rounded-lg border border-slate-700;
}

.detail-header {
  @apply flex items-center gap-2 mb-3;
}

.detail-title {
  @apply text-sm font-medium text-slate-400;
}

.detail-content {
  @apply text-slate-300;
}

.dimensions-section {
  @apply mb-8 p-6 bg-slate-900/20 rounded-lg border border-slate-700;
}

.dimensions-grid {
  @apply space-y-4;
}

.dimension-item {
  @apply p-4 bg-slate-800/30 rounded-lg;
}

.progress-bar {
  @apply w-full h-2 bg-slate-700 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500;
}

.card-footer {
  @apply pt-6 border-t border-slate-700;
}
</style>
