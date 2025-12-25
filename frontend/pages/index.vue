<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
    <div class="container mx-auto px-4 py-8">
      <!-- Header -->
      <h1 class="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
        Diagnóstico de Madurez en IA
      </h1>
      <p class="text-center text-slate-400 mb-8">
        Evalúa el nivel de preparación de tu organización para implementar soluciones de IA
      </p>

      <!-- Progress Stepper -->
      <div class="max-w-2xl mx-auto mb-8">
        <div class="flex items-center justify-between">
          <div
            v-for="(stepInfo, index) in steps"
            :key="index"
            class="flex items-center"
            :class="{ 'flex-1': index < steps.length - 1 }"
          >
            <div
              class="flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all"
              :class="step >= index
                ? 'bg-blue-500 border-blue-500 text-white'
                : 'bg-slate-800 border-slate-600 text-slate-500'"
            >
              {{ index + 1 }}
            </div>
            <div
              v-if="index < steps.length - 1"
              class="flex-1 h-0.5 mx-2 transition-all"
              :class="step > index ? 'bg-blue-500' : 'bg-slate-700'"
            ></div>
          </div>
        </div>
        <div class="flex justify-between mt-2">
          <span
            v-for="(stepInfo, index) in steps"
            :key="index"
            class="text-xs font-medium"
            :class="step >= index ? 'text-blue-400' : 'text-slate-500'"
          >
            {{ stepInfo }}
          </span>
        </div>
      </div>

      <!-- PASO 0: Información Empresarial (CON FormSection) -->
      <div class="max-w-2xl mx-auto">
        <FormSection
          v-if="step === 0"
          title="Información de la Empresa"
          description="Proporciona los datos básicos de tu organización para generar un diagnóstico personalizado"
          :icon="BuildingOfficeIcon"
        >
          <!-- Grid de campos -->
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Razón Social <span class="text-red-400">*</span>
              </label>
              <input
                v-model="prospectInfo.empresa"
                type="text"
                placeholder="Ej: Acme Corporation S.A."
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Email Corporativo <span class="text-red-400">*</span>
              </label>
              <input
                v-model="prospectInfo.email"
                type="email"
                placeholder="contacto@empresa.com"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Sector <span class="text-red-400">*</span>
              </label>
              <select
                v-model="prospectInfo.sector"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              >
                <option value="" disabled>Selecciona un sector</option>
                <option v-for="s in sectores" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Facturación Anual <span class="text-red-400">*</span>
              </label>
              <select
                v-model="prospectInfo.facturacion"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              >
                <option value="" disabled>Selecciona un rango</option>
                <option v-for="f in facturacionOpciones" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Número de Empleados <span class="text-red-400">*</span>
              </label>
              <select
                v-model="prospectInfo.numEmpleados"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              >
                <option value="" disabled>Selecciona un rango</option>
                <option v-for="e in empleadosOpciones" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Nombre del Contacto <span class="text-red-400">*</span>
              </label>
              <input
                v-model="prospectInfo.nombreContacto"
                type="text"
                placeholder="Juan Pérez"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Teléfono <span class="text-red-400">*</span>
              </label>
              <input
                v-model="prospectInfo.telefono"
                type="tel"
                placeholder="+57 300 123 4567"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Cargo <span class="text-red-400">*</span>
              </label>
              <select
                v-model="prospectInfo.cargo"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              >
                <option value="" disabled>Selecciona tu cargo</option>
                <option v-for="c in cargosOpciones" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Ciudad <span class="text-red-400">*</span>
              </label>
              <input
                v-model="prospectInfo.ciudad"
                type="text"
                placeholder="Bogotá"
                class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              />
            </div>
          </div>

          <!-- Footer con botón -->
          <template #footer>
            <button
              @click="nextStep"
              :disabled="!isStep1Valid"
              :class="[
                'w-full py-4 rounded-lg font-semibold text-white transition-all duration-200',
                isStep1Valid
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 shadow-lg shadow-blue-500/50'
                  : 'bg-slate-700 cursor-not-allowed opacity-50'
              ]"
            >
              {{ isStep1Valid ? 'Continuar al Cuestionario →' : 'Completa todos los campos requeridos' }}
            </button>
          </template>
        </FormSection>

        <!-- PASO 1: Cuestionario (CON FormSection) -->
        <FormSection
          v-else-if="step === 1"
          title="Cuestionario de Diagnóstico"
          description="Responde las siguientes preguntas para evaluar la madurez en IA de tu organización"
          :icon="ClipboardDocumentListIcon"
        >
          <!-- Progress Header -->
          <div class="flex justify-between items-center mb-6">
            <div class="text-sm text-slate-400">
              Progreso: <span class="text-blue-400 font-semibold">{{ progress }}%</span>
            </div>
          </div>

          <!-- Progress Bar -->
          <ProgressBar
            :progress="progress"
            label="Progreso del Cuestionario"
            :show-details="true"
            :current-step="Object.keys(responses).filter(k => {
              const v = responses[k]
              return Array.isArray(v) ? v.length > 0 : v !== undefined && v !== null && v !== ''
            }).length"
            :total-steps="questions.length"
          />

          <!-- Loading State -->
          <div v-if="loading && questions.length === 0" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p class="text-slate-400 mt-4">Cargando preguntas...</p>
          </div>

          <!-- Questions -->
          <div v-else class="space-y-8 mt-6">
            <div
              v-for="(question, index) in questions"
              :key="question.id"
              class="p-6 bg-slate-900/30 rounded-lg border border-slate-700"
            >
              <div class="mb-4">
                <h3 class="text-lg font-medium text-slate-200 mb-1">
                  {{ index + 1 }}. {{ question.text }}
                </h3>
                <p v-if="question.helper" class="text-sm text-slate-400 italic">
                  {{ question.helper }}
                </p>
              </div>

              <!-- Multi-select (checkboxes) -->
              <div v-if="question.type === 'multi-select'" class="space-y-2">
                <label
                  v-for="option in question.options"
                  :key="option"
                  class="flex items-center p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition cursor-pointer"
                >
                  <input
                    type="checkbox"
                    :value="option"
                    v-model="responses[question.id]"
                    class="w-5 h-5 text-blue-500 bg-slate-700 border-slate-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span class="ml-3 text-slate-300">{{ option }}</span>
                </label>
              </div>

              <!-- Radio buttons -->
              <div v-else-if="question.type === 'radio'" class="space-y-2">
                <label
                  v-for="option in question.options"
                  :key="option"
                  class="flex items-center p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition cursor-pointer"
                >
                  <input
                    type="radio"
                    :name="question.id"
                    :value="option"
                    v-model="responses[question.id]"
                    class="w-5 h-5 text-blue-500 bg-slate-700 border-slate-600 focus:ring-2 focus:ring-blue-500"
                  />
                  <span class="ml-3 text-slate-300">{{ option }}</span>
                </label>

                <!-- Campo "Otro" condicional -->
                <div v-if="question.has_other && responses[question.id] === question.options[question.options.length - 1]" class="mt-3">
                  <input
                    v-model="otherText"
                    type="text"
                    placeholder="Especifica tu respuesta..."
                    class="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Footer con botones -->
          <template #footer>
            <div class="flex gap-4">
              <button
                @click="prevStep"
                class="flex-1 py-4 rounded-lg font-semibold text-slate-300 bg-slate-700 hover:bg-slate-600 transition"
              >
                ← Volver
              </button>
              <button
                @click="handleSubmit"
                :disabled="!isStep2Valid || loading"
                :class="[
                  'flex-1 py-4 rounded-lg font-semibold text-white transition-all duration-200',
                  isStep2Valid && !loading
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 shadow-lg shadow-blue-500/50'
                    : 'bg-slate-700 cursor-not-allowed opacity-50'
                ]"
              >
                {{ loading ? 'Procesando...' : isStep2Valid ? 'Enviar Diagnóstico →' : 'Responde todas las preguntas' }}
              </button>
            </div>
          </template>
        </FormSection>

        <!-- PASO 2: Resultados (CON ResultsCard) -->
        <div v-else-if="step === 2" class="space-y-6">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-slate-700">
            <div class="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
            <p class="text-slate-300 text-lg mt-6">Procesando diagnóstico...</p>
            <p class="text-slate-400 text-sm mt-2">Analizando respuestas, generando PDF y enviando email</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-slate-700">
            <div class="text-red-400 text-6xl mb-4">⚠️</div>
            <h3 class="text-xl font-semibold text-slate-200 mb-2">Error al procesar</h3>
            <p class="text-slate-400 mb-6">{{ error }}</p>
            <button
              @click="prevStep"
              class="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition"
            >
              ← Volver al cuestionario
            </button>
          </div>

          <!-- Success State con ResultsCard -->
          <div v-else-if="result" class="space-y-6">
            <!-- Header con checkmark -->
            <div class="text-center bg-slate-800/50 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-slate-700">
              <div class="text-green-400 text-6xl mb-4">✅</div>
              <h2 class="text-3xl font-bold text-slate-200 mb-2">¡Diagnóstico Completado!</h2>
              <p class="text-slate-400 mb-4">Hemos analizado tu información y generado tu reporte personalizado</p>

              <!-- Staleness Badge -->
              <div class="flex justify-center">
                <StalenessBadge :timestamp="result.timestamp || new Date().toISOString()" />
              </div>
            </div>

            <!-- ResultsCard Component -->
            <ResultsCard
              :score="result.score_total"
              :tier="result.tier"
              :arquetipo="result.arquetipo"
              :servicio="result.servicio_sugerido"
              :monto-min="result.monto_min"
              :monto-max="result.monto_max"
              :show-dimension-scores="true"
              :dimension-scores="{
                'Datos': result.score_datos || 0,
                'Talento': result.score_talento || 0,
                'Procesos': result.score_procesos || 0,
                'Infraestructura': result.score_infraestructura || 0
              }"
            >
              <template #actions>
                <!-- Status de integraciones -->
                <div class="flex justify-center gap-4 mb-6 text-sm">
                  <div :class="result.pdf_generated ? 'text-green-400' : 'text-slate-500'">
                    {{ result.pdf_generated ? '✓' : '✗' }} PDF Generado
                  </div>
                  <div :class="result.email_sent ? 'text-green-400' : 'text-slate-500'">
                    {{ result.email_sent ? '✓' : '✗' }} Email Enviado
                  </div>
                  <div :class="result.success ? 'text-green-400' : 'text-slate-500'">
                    {{ result.success ? '✓' : '✗' }} Guardado en Sheets
                  </div>
                </div>

                <!-- Mensaje email -->
                <p class="text-slate-400 mb-6 text-center">
                  Revisa tu correo <span class="text-blue-400 font-semibold">{{ prospectInfo.email }}</span> para ver el reporte completo
                </p>

                <!-- Botones de acción -->
                <div class="flex flex-col gap-4">
                  <button
                    v-if="result && result.pdf_generated"
                    @click="downloadPDF"
                    class="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition flex items-center justify-center gap-2"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Descargar Reporte PDF
                  </button>

                  <button
                    @click="reset"
                    class="px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg font-semibold shadow-lg shadow-blue-500/50 transition"
                  >
                    Nueva Evaluación
                  </button>
                </div>
              </template>
            </ResultsCard>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { BuildingOfficeIcon, ClipboardDocumentListIcon } from '@heroicons/vue/24/outline'
import ProgressBar from '~/components/ProgressBar.vue'
import FormSection from '~/components/FormSection.vue'
import ResultsCard from '~/components/ResultsCard.vue'
import StalenessBadge from '~/components/StalenessBadge.vue'

definePageMeta({
  ssr: false
})

const {
  step,
  questions,
  prospectInfo,
  responses,
  otherText,
  result,
  loading,
  error,
  isStep1Valid,
  isStep2Valid,
  progress,
  loadQuestions,
  nextStep: nextStepBase,
  prevStep,
  submitDiagnostic,
  reset
} = useDiagnostic()

const sectores = [
  'Financiero (Banca/Seguros)',
  'Retail/Comercio',
  'Manufactura',
  'Salud',
  'Tecnología',
  'Servicios Profesionales',
  'Otro'
]

const facturacionOpciones = [
  'Menos de $500K USD',
  '$500K - $2M USD',
  '$2M - $10M USD',
  '$10M - $50M USD',
  'Más de $50M USD'
]

const empleadosOpciones = [
  '1-50',
  '51-200',
  '201-500',
  '501-1000',
  'Más de 1000'
]

const cargosOpciones = [
  'CEO/Gerente General',
  'Director/VP',
  'Gerente',
  'Jefe de Área',
  'Analista/Consultor',
  'Otro'
]

const steps = ['Empresa', 'Diagnóstico', 'Resultados']

const nextStep = async () => {
  if (step.value === 0 && isStep1Valid.value) {
    nextStepBase()
    if (questions.value.length === 0) {
      await loadQuestions()
    }
  } else if (step.value === 1 && isStep2Valid.value) {
    nextStepBase()
  }
}

const handleSubmit = async () => {
  if (!isStep2Valid.value || loading.value) return
  await submitDiagnostic()
}

const downloadPDF = async () => {
  if (!result.value || !result.value.diagnostic_id) {
    console.error('No hay diagnostic_id disponible')
    return
  }

  try {
    const config = useRuntimeConfig()
    const pdfUrl = `${config.public.apiBase}/diagnostic/${result.value.diagnostic_id}/pdf`
    window.open(pdfUrl, '_blank')
  } catch (error) {
    console.error('Error descargando PDF:', error)
  }
}

onMounted(() => {
  if (step.value === 1 && questions.value.length === 0) {
    loadQuestions()
  }
})
</script>
