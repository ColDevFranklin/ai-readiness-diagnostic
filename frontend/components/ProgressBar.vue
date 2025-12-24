<template>
  <div class="w-full">
    <!-- Texto superior -->
    <div class="flex justify-between items-center mb-2">
      <span class="text-sm font-medium text-slate-300">
        {{ label }}
      </span>
      <span class="text-sm font-semibold text-blue-400">
        {{ progress }}%
      </span>
    </div>

    <!-- Barra de progreso -->
    <div class="w-full h-3 bg-slate-700/50 rounded-full overflow-hidden backdrop-blur-sm">
      <div
        class="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full transition-all duration-500 ease-out shadow-lg shadow-blue-500/50"
        :style="{ width: `${progress}%` }"
      >
        <!-- Efecto de brillo -->
        <div class="w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
      </div>
    </div>

    <!-- Texto inferior (opcional) -->
    <div v-if="showDetails" class="mt-2 text-xs text-slate-400 text-center">
      {{ currentStep }} de {{ totalSteps }} preguntas respondidas
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Progreso 0-100
  progress: {
    type: Number,
    required: true,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },

  // Etiqueta descriptiva
  label: {
    type: String,
    default: 'Progreso'
  },

  // Mostrar detalles adicionales
  showDetails: {
    type: Boolean,
    default: false
  },

  // Para cálculo de detalles
  currentStep: {
    type: Number,
    default: 0
  },

  totalSteps: {
    type: Number,
    default: 12
  }
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 2s infinite;
}
</style>
