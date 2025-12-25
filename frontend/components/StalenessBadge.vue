<template>
  <div
    class="staleness-badge"
    :class="badgeClasses"
    :title="fullTimestamp"
  >
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span class="text-xs font-medium">{{ timeAgoText }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * StalenessBadge - Indicador de frescura de datos con colores dinámicos
 *
 * @component
 * @example
 * <StalenessBadge timestamp="2024-12-23T22:30:00Z" />
 *
 * Colores:
 * 🟢 Verde (<1 hora) - Datos muy frescos
 * 🟡 Amarillo (1-24 horas) - Datos frescos
 * 🟠 Naranja (1-7 días) - Datos antiguos
 * 🔴 Rojo (>7 días) - Datos muy antiguos
 */

const props = defineProps({
  /**
   * Timestamp ISO 8601 del dato
   * @type {String}
   * @required
   * @example "2024-12-23T22:30:00Z"
   */
  timestamp: {
    type: String,
    required: true,
    validator: (value) => {
      // Validar formato ISO 8601
      return !isNaN(Date.parse(value))
    }
  },

  /**
   * Mostrar fecha completa en tooltip
   * @type {Boolean}
   */
  showFullDate: {
    type: Boolean,
    default: true
  }
})

// Calcular tiempo transcurrido en milisegundos
const timeElapsed = computed(() => {
  const now = new Date()
  const past = new Date(props.timestamp)
  return now - past
})

// Calcular unidades de tiempo
const timeUnits = computed(() => {
  const ms = timeElapsed.value
  const minutes = Math.floor(ms / (1000 * 60))
  const hours = Math.floor(ms / (1000 * 60 * 60))
  const days = Math.floor(ms / (1000 * 60 * 60 * 24))

  return { minutes, hours, days }
})

// Texto legible del tiempo transcurrido
const timeAgoText = computed(() => {
  const { minutes, hours, days } = timeUnits.value

  if (minutes < 1) return 'Justo ahora'
  if (minutes < 60) return `Hace ${minutes} min`
  if (hours < 24) return `Hace ${hours}h`
  if (days === 1) return 'Hace 1 día'
  if (days < 7) return `Hace ${days} días`
  if (days < 30) {
    const weeks = Math.floor(days / 7)
    return `Hace ${weeks} semana${weeks > 1 ? 's' : ''}`
  }
  if (days < 365) {
    const months = Math.floor(days / 30)
    return `Hace ${months} mes${months > 1 ? 'es' : ''}`
  }
  const years = Math.floor(days / 365)
  return `Hace ${years} año${years > 1 ? 's' : ''}`
})

// Clases CSS dinámicas según antigüedad
const badgeClasses = computed(() => {
  const { hours, days } = timeUnits.value

  // 🟢 Verde: <1 hora
  if (hours < 1) {
    return 'badge-fresh bg-green-500/20 text-green-400 border-green-500/30'
  }

  // 🟡 Amarillo: 1-24 horas
  if (hours < 24) {
    return 'badge-recent bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
  }

  // 🟠 Naranja: 1-7 días
  if (days < 7) {
    return 'badge-old bg-orange-500/20 text-orange-400 border-orange-500/30'
  }

  // 🔴 Rojo: >7 días
  return 'badge-stale bg-red-500/20 text-red-400 border-red-500/30'
})

// Fecha completa formateada para tooltip
const fullTimestamp = computed(() => {
  if (!props.showFullDate) return ''

  const date = new Date(props.timestamp)
  return date.toLocaleString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  })
})
</script>

<style scoped>
.staleness-badge {
  @apply inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border;
  @apply transition-all duration-300 cursor-help;
}

.staleness-badge:hover {
  @apply scale-105 shadow-lg;
}

/* Animación de pulso para datos muy antiguos */
.badge-stale {
  animation: pulse-red 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse-red {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Shimmer para datos frescos */
.badge-fresh {
  position: relative;
  overflow: hidden;
}

.badge-fresh::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}
</style>
