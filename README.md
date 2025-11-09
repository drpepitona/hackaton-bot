# 🤖 Financial News Impact Analysis Bot

Bot inteligente de análisis financiero que predice el impacto de noticias en mercados usando IA (Gemini) y parámetros científicos basados en la Teoría de Landau.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Gemini](https://img.shields.io/badge/Gemini-Pro-orange)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 🎯 Características

- 🤖 **IA con Gemini Pro** - Análisis inteligente en tiempo real
- 📊 **123,326 noticias históricas** - Base de datos robusta
- 🔬 **Parámetros Landau** - Modelo científico (α, β, tokens)
- 🎯 **Filtro de relevancia** - Rechaza preguntas sin sentido financiero
- 🧠 **Clasificación inteligente** - IA encuentra categorías similares
- 📈 **17 categorías** de eventos financieros
- ⚡ **API REST** - Fácil integración con cualquier frontend

---

## 🚀 Demo Rápido

```bash
# Clonar repositorio
git clone https://github.com/TU-USUARIO/TU-REPO.git
cd TU-REPO

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key
# Edita api_chatbot.py y añade tu GEMINI_API_KEY

# Iniciar servidor
python api_chatbot.py
```

Abre: http://localhost:8000/docs

---

## 📊 Ejemplo de Uso

**Pregunta:** "¿Cómo afecta que la Fed suba las tasas de interés?"

**Respuesta del Bot:**
```
📊 ANÁLISIS DE IMPACTO FINANCIERO

Probabilidad de impacto: 78.3%
Dirección esperada: ALCISTA
Magnitud típica: ±0.52%

RAZONAMIENTO:
- Token: 5.8/10 (basado en 298 eventos históricos)
- Parámetros Landau: α=0.211, β=1.178
- VIX amplifica el impacto en 35% (efecto polvorín moderado)

RECOMENDACIÓN: ESPERAR
```

---

## 🔬 Modelo Científico

### **Parámetros de Landau**

El bot usa la **Teoría de Transiciones de Fase de Landau** aplicada a mercados:

```
P_contextual = P_base × (1 + α × (VIX/20 - 1)^β)
```

Donde:
- **P_base** = Probabilidad base del token
- **α (alpha)** = Amplificador (cuánto amplifica el VIX)
- **β (beta)** = Exponente (cómo amplifica: lineal vs explosivo)
- **VIX** = Índice de miedo del mercado

### **Categorías por Impacto**

| Categoría | Token | α | β | Tipo |
|-----------|-------|---|---|------|
| ECB Policy | 10.0 | 0.238 | 1.246 | Extremo |
| Financial Crisis | 8.1 | 0.245 | 1.515 | Alto |
| Terrorism | 7.4 | 0.277 | 1.705 | Explosivo |
| Fed Rates | 5.8 | 0.211 | 1.178 | Moderado |
| Housing | 5.5 | 0.174 | 0.873 | Estable |

---

## 🛠️ Tecnologías

- **Backend:** Python 3.11, FastAPI, Uvicorn
- **IA:** Google Gemini Pro API
- **Datos:** pandas, numpy, scipy
- **Base de datos:** 123k+ noticias históricas (2008-2016)
- **Modelo:** Teoría de Landau + Machine Learning

---

## 📡 API Endpoints

### `GET /health`
Verificar estado del sistema

### `POST /analyze`
Analizar noticia o pregunta financiera

**Request:**
```json
{
  "pregunta": "¿Cómo afecta que la Fed suba tasas?",
  "vix": 35
}
```

**Response:**
```json
{
  "analisis": "...",
  "categoria": "fed_rates",
  "token": 5.8,
  "num_eventos": 298,
  "alpha": 0.211,
  "beta": 1.178,
  "relevante": true
}
```

### `GET /categories`
Obtener todas las categorías con parámetros

---

## 🌐 Deploy a Producción

### **Railway (Backend)**
```bash
# 1. Push a GitHub
git push origin main

# 2. En railway.app:
#    - New Project → GitHub
#    - Añadir GEMINI_API_KEY
#    - Deploy automático
```

### **Vercel / Lovable (Frontend)**
```bash
# Frontend React en otro repo
# Variables: VITE_CHATBOT_API_URL=https://tu-backend.railway.app
```

Ver: [DEPLOY_PASO_A_PASO.md](./DEPLOY_PASO_A_PASO.md)

---

## 📁 Estructura del Proyecto

```
hackaton/
├── api_chatbot.py              # ⭐ API REST del bot
├── bot_gemini_completo.py      # ⭐ Bot principal con Gemini
├── requirements.txt            # Dependencias
├── Procfile                    # Para Railway/Heroku
├── runtime.txt                 # Versión de Python
├── src/
│   ├── models/                 # Modelos de ML
│   │   └── tokens_volatilidad_avanzado.py
│   └── utils/
│       ├── config.py
│       └── logger.py
├── data/
│   ├── processed/
│   │   └── landau/             # Parámetros α, β, tokens
│   └── models/
│       └── landau_phase_model_*.pkl
└── docs/
    ├── EXPLICACION_ALFA_BETA_FUNDAMENTAL.md
    └── MODELO_LANDAU_COMPLETO.md
```

---

## 🎓 Documentación

- [Explicación de α y β](./EXPLICACION_ALFA_BETA_FUNDAMENTAL.md)
- [Modelo de Landau Completo](./MODELO_LANDAU_COMPLETO.md)
- [Deploy Paso a Paso](./DEPLOY_PASO_A_PASO.md)

---

## 🔐 Configuración

### **Variables de Entorno Requeridas:**

```bash
GEMINI_API_KEY=tu-api-key-aqui
PORT=8000  # Opcional, default 8000
```

---

## 📊 Dataset

- **123,326 noticias** clasificadas (2008-2016)
- **17 categorías** financieras
- **Múltiples activos:** SPY, QQQ, IWM, DIA
- **Indicadores:** VIX, GDP, empleo, petróleo, forex

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Libre para usar en proyectos comerciales

---

## 👨‍💻 Autor

Desarrollado para hackathon de análisis financiero

---

## 🌟 Agradecimientos

- Google Gemini API
- Teoría de Landau (Lev Landau, Premio Nobel 1962)
- Kaggle Financial News Dataset
- Comunidad de Econofísica

---

**⭐ Si te gusta el proyecto, dale una estrella en GitHub!**

