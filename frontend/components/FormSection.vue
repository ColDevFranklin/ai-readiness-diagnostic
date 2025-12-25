<template>
  <div class="form-section bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-slate-700 transition-all duration-300 hover:border-slate-600">
    <!-- Header con icono opcional -->
    <div class="flex items-center gap-3 mb-6">
      <div v-if="icon" class="flex-shrink-0">
        <component
          :is="icon"
          class="w-8 h-8 text-blue-400"
        />
      </div>
      <div class="flex-1">
        <h2 class="text-2xl font-semibold text-slate-200">
          {{ title }}
        </h2>
        <p v-if="description" class="text-sm text-slate-400 mt-1">
          {{ description }}
        </p>
      </div>
    </div>

    <!-- Contenido del slot -->
    <div class="space-y-6">
      <slot></slot>
    </div>

    <!-- Footer opcional -->
    <div v-if="$slots.footer" class="mt-8 pt-6 border-t border-slate-700">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
/**
 * FormSection - Componente contenedor para secciones de formulario
 *
 * @component
 * @example
 * <FormSection
 *   title="Información Empresarial"
 *   description="Datos básicos de tu organización"
 *   :icon="BuildingOfficeIcon"
 * >
 *   <input v-model="empresa" />
 *   <input v-model="email" />
 * </FormSection>
 */

defineProps({
  /**
   * Título principal de la sección
   * @type {String}
   * @required
   */
  title: {
    type: String,
    required: true
  },

  /**
   * Descripción opcional bajo el título
   * @type {String}
   */
  description: {
    type: String,
    default: ''
  },

  /**
   * Componente de icono de Heroicons (opcional)
   * @type {Component}
   * @example :icon="BuildingOfficeIcon"
   */
  icon: {
    type: Object,
    default: null
  }
})
</script>

<style scoped>
.form-section {
  /* Efecto glassmorphism mejorado */
  background: linear-gradient(
    135deg,
    rgba(30, 41, 59, 0.7) 0%,
    rgba(15, 23, 42, 0.5) 100%
  );
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.form-section:hover {
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.3),
    0 10px 10px -5px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(59, 130, 246, 0.1);
}
</style>
