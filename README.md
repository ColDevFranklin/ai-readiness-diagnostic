# Sistema de Diagnóstico AI Readiness

Sistema completo de calificación de leads para consultoría en IA, con formulario conversacional, scoring automático, clasificación por arquetipos y dashboard de gestión.

## 🎯 Componentes del Sistema

### 1. Formulario de Diagnóstico (`formulario.py`)

- Interfaz conversacional para dueños de negocio
- 15 preguntas en 3 bloques (10 minutos completar)
- Recolección de información de contacto + diagnóstico operativo
- Validación en tiempo real

### 2. Motor de Scoring (`scoring_engine.py`)

- Algoritmo de puntuación 0-100 basado en respuestas
- 3 dimensiones evaluadas:
  - Madurez Digital (40 puntos)
  - Capacidad de Inversión (30 puntos)
  - Viabilidad Comercial (30 puntos)
- Clasificación automática en Tier A/B/C

### 3. Clasificador de Arquetipos (`classifier.py`)

- 6 arquetipos empresariales identificados
- Generación automática de insights y recomendaciones
- Quick wins personalizados
- Red flags detectados
- Preparación completa para reunión

### 4. Dashboard de Gestión (`dashboard.py`)

- Vista ejecutiva de todos los diagnósticos
- Filtrado por Tier, Arquetipo, Fecha
- Métricas de pipeline y conversión
- Análisis detallado por prospecto
- Protegido con password

### 5. Integraciones

- **Google Sheets**: Persistencia de datos
- **PDF Generator**: Reportes ejecutivos
- **Email Sender**: Comunicación automatizada por Tier

---

## 📋 Pre-requisitos

### 1. Cuenta de Google Cloud

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear nuevo proyecto: "AI Readiness System"
3. Habilitar Google Sheets API
4. Crear Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Nombre: "ai-readiness-service"
   - Rol: Editor
   - Crear key JSON → Descargar

### 2. Google Sheets Setup

1. Crear nuevo Google Sheet: "AI_Readiness_Diagnostics"
2. Compartir con el email del Service Account (del JSON)
3. Dar permisos de Editor

### 3. Email Setup (Gmail)

1. Habilitar 2FA en Gmail
2. Generar App Password:
   - Cuenta Google → Seguridad → App Passwords
   - Seleccionar "Correo" → Generar
   - Guardar password

---

## 🚀 Instalación

### Opción 1: Deployment en Streamlit Cloud (Recomendado)

1. **Fork o clonar el repositorio**

```bash
git clone [tu-repo]
cd ai_readiness_diagnostic
```

2. **Crear cuenta en Streamlit Cloud**

- Ir a [share.streamlit.io](https://share.streamlit.io/)
- Conectar con GitHub

3. **Configurar Secrets**
En Streamlit Cloud → App Settings → Secrets:

```toml
# Google Sheets Service Account
[gcp_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "ai-readiness-service@tu-project.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "tu-cert-url"

# Spreadsheet
sheet_name = "AI_Readiness_Diagnostics"

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "tu-email@gmail.com"
sender_password = "tu-app-password"

# Dashboard password
dashboard_password = "tu-password-seguro"
```

4. **Deploy**

- Main file path: `app/formulario.py`
- Python version: 3.10
- Deploy!

5. **Crear segunda app para Dashboard**

- New app → Same repo
- Main file path: `app/dashboard.py`
- Deploy!

---

### Opción 2: Local Development

1. **Clonar repo**

```bash
git clone [tu-repo]
cd ai_readiness_diagnostic
```

2. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar secrets locales**
Crear archivo `.streamlit/secrets.toml`:

```toml
# Copiar contenido de secrets de arriba
```

5. **Ejecutar formulario**

```bash
streamlit run app/formulario.py
```

6. **Ejecutar dashboard** (en otra terminal)

```bash
streamlit run app/dashboard.py --server.port 8502
```

---

## 📁 Estructura del Proyecto

```
ai_readiness_diagnostic/
│
├── app/
│   ├── formulario.py              # App principal para prospectos
│   ├── dashboard.py               # Dashboard de gestión
│   └── config.py                  # Configuración centralizada
│
├── core/
│   ├── scoring_engine.py          # Lógica de scoring
│   ├── classifier.py              # Clasificación de arquetipos
│   └── models.py                  # Data models
│
├── integrations/
│   ├── sheets_connector.py        # Google Sheets
│   ├── email_sender.py            # Email automation
│   └── pdf_generator.py           # PDF generation
│
├── data/
│   └── questions.json             # Definición de preguntas
│
├── output/
│   └── pdfs/                      # PDFs generados
│
├── requirements.txt
└── README.md
```

---

## 🔧 Configuración Avanzada

### Personalizar Scoring

Editar `/core/scoring_engine.py`:

- Ajustar pesos de cada dimensión
- Modificar umbrales de Tier (actualmente 70/40)
- Cambiar mapeos de respuestas a puntos

### Agregar/Modificar Preguntas

Editar `/data/questions.json`:

```json
{
  "id": "Q16",
  "tipo": "radio",
  "pregunta": "Tu nueva pregunta",
  "opciones": ["Opción 1", "Opción 2"],
  "requerido": true
}
```

Actualizar `scoring_engine.py` con lógica de scoring para Q16.

### Crear Nuevo Arquetipo

Editar `/core/classifier.py`:

1. Agregar definición en `_init_archetype_definitions()`
2. Crear método `_score_[nuevo_arquetipo]()`
3. Agregar en método `classify()`

### Personalizar Templates de Email

Editar `/integrations/email_sender.py`:

- Métodos `_get_tier_a_content()`, `_get_tier_b_content()`, `_get_tier_c_content()`
- Modificar HTML y contenido

---

## 📊 Uso del Sistema

### Para Prospectos (Formulario)

1. Visitar URL del formulario
2. Completar información de contacto
3. Responder 15 preguntas (10 min)
4. Recibir email con resumen PDF
5. Andrés los contacta en 48h

### Para Andrés (Dashboard)

1. Acceder a URL del dashboard
2. Ingresar password
3. Ver métricas generales
4. Filtrar por Tier A para acción inmediata
5. Ver detalles de cada prospecto:
   - Score breakdown
   - Arquetipo identificado
   - Quick wins sugeridos
   - Red flags
   - Preparación para reunión
   - Probabilidad de cierre

---

## 🔒 Seguridad

- **Google Sheets**: Service Account con permisos mínimos
- **Dashboard**: Protegido con password en secrets
- **Secrets**: NUNCA commitear `.streamlit/secrets.toml`
- **Emails**: App passwords en vez de contraseña principal
- **HTTPS**: Streamlit Cloud usa SSL automáticamente

---

## 📈 Mantenimiento

### Backup de Datos

Google Sheets automáticamente guarda historial.
Exportar periódicamente:

```
File → Download → CSV
```

### Monitoreo

- Revisar logs en Streamlit Cloud → App → Logs
- Google Sheets → Ver actividad de Service Account
- Email delivery: Revisar bounces en Gmail

### Updates

```bash
git pull origin main
# Streamlit Cloud auto-redeploys
```

---

## 🐛 Troubleshooting

### Error: "No module named 'gspread'"

```bash
pip install -r requirements.txt
```

### Error: "Permission denied" en Google Sheets

- Verificar que Service Account email tiene acceso al Sheet
- Revisar que API está habilitada en Google Cloud

### Error: Email no se envía

- Verificar App Password (no contraseña normal)
- Verificar 2FA habilitado en Gmail
- Revisar spam del destinatario

### Dashboard no carga datos

- Verificar conexión a Google Sheets
- Revisar que hay datos en tab "scores"
- Check logs en Streamlit Cloud

---

## 🚀 Próximas Mejoras

- [ ] Notificaciones Telegram para Tier A
- [ ] Integración con CRM (HubSpot/Pipedrive)
- [ ] A/B testing de preguntas
- [ ] ML para mejorar clasificación de arquetipos
- [ ] Análisis de tendencias de mercado
- [ ] WhatsApp Business API para followup

---

## 📞 Soporte

Para dudas o mejoras:

- Email: [tu email]
- GitHub Issues: [tu repo]/issues

---

## 📄 Licencia

Uso privado para consultoría AI de Andrés.
