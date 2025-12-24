export default defineNuxtConfig({
  compatibilityDate: '2024-12-23',
  
  modules: ['@nuxtjs/tailwindcss'],
  
  devtools: { enabled: true },
  
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api'
    }
  },
  
  app: {
    head: {
      title: 'AI Readiness Diagnostic'
    }
  }
})
