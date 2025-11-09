# 🤖 GUÍA COMPLETA DEL CHATBOT PARA HACKATHON

## 🎯 ¿QUÉ TENEMOS?

Un **Chatbot Inteligente** que combina:

1. **RAG** (Retrieval Augmented Generation)
   - 49,718 noticias históricas
   - Embeddings TF-IDF para búsqueda rápida
   - Encuentra noticias similares en <1 segundo

2. **Modelo Predictivo Refinado**
   - α y β específicos por categoría
   - 17 categorías diferentes
   - Considera contexto VIX

3. **Interfaz Streamlit**
   - Chat interactivo
   - Visualizaciones en tiempo real
   - Explicabilidad total

---

## 🚀 CÓMO LANZAR EL CHATBOT

### **Opción 1: Streamlit (Recomendado para DEMO)**

```bash
cd "d:\curosor\ pojects\hackaton"
py -m streamlit run app_chatbot_hackathon.py
```

**Se abrirá:** `http://localhost:8501`

---

### **Opción 2: Python Directo (para pruebas)**

```python
from chatbot_rag_gemini import ChatbotGemini, SistemaRAG, ModeloPredictor

# Inicializar sistema
rag = SistemaRAG()
rag.cargar_noticias()
rag.crear_embeddings_simple()

predictor = ModeloPredictor()
predictor.cargar_modelo()

chatbot = ChatbotGemini()
chatbot.inicializar()
chatbot.conectar_rag(rag)
chatbot.conectar_predictor(predictor)

# Hacer consulta
resultado = chatbot.procesar_consulta(
    "¿Qué pasa si la Fed sube tasas?",
    vix_actual=30,
    asset='SPY'
)

print(resultado['respuesta'])
```

---

## 📊 CARACTERÍSTICAS PRINCIPALES

### **1. RAG (Retrieval Augmented Generation)**

```
Usuario: "¿Qué pasa si la Fed sube tasas?"
  ↓
Sistema RAG busca en 49,718 noticias:
  • "Fed raises interest rates..."
  • "Federal Reserve increases..."
  • "FOMC decision..."
  ↓
Devuelve Top 3-5 noticias más similares
```

**Ventajas:**
- ✓ Respuestas basadas en datos reales (no inventadas)
- ✓ Contexto histórico automático
- ✓ Similitud medible (0-100%)

---

### **2. Modelo Predictivo con α y β**

```
Categoría detectada: "fed_rates"
  ↓
Parámetros específicos:
  • α = 0.211 (amplificador moderado)
  • β = 1.178 (efecto polvorín leve)
  ↓
VIX actual: 30
  ↓
Cálculo:
  P_base = 58% (del token 5.8)
  P_contextual = 58% × (1 + 0.211 × (1.5 - 1)^1.178)
               = 58% × 1.09
               = 63.2%
  ↓
Resultado: 58% → 63% (+9% por VIX alto)
```

**Ventajas:**
- ✓ Considera contexto del mercado (VIX)
- ✓ α y β diferentes por tipo de noticia
- ✓ Interpretable (no caja negra)

---

### **3. Interfaz Streamlit**

**Componentes:**

1. **Chat Inteligente:**
   - Input de pregunta
   - Ejemplos rápidos
   - VIX ajustable
   - Respuesta completa

2. **Visualizaciones:**
   - Gráfica Probabilidad vs VIX
   - Noticias históricas (RAG)
   - Parámetros α y β
   - Recomendación final

3. **Análisis Detallado:**
   - Top categorías por β
   - Tabla de parámetros
   - Explicación de α y β

---

## 🎓 EJEMPLOS DE USO

### **Ejemplo 1: Fed Rates**

**Pregunta:**
```
"¿Qué pasa si la Fed sube tasas con VIX alto?"
```

**VIX:** 35

**Resultado:**
```
📊 PREDICCIÓN:
  • Probabilidad base: 58%
  • Probabilidad contextual: 67%
  • Ajuste VIX: +15%
  • Dirección: NEUTRAL
  • α = 0.211, β = 1.18

📰 NOTICIAS SIMILARES (RAG):
  1. "China Blames Wall Street Meltdown On Federal Reserve..."
     Fecha: 2008-09-19

💡 RECOMENDACIÓN:
  ⚡ MODERADA probabilidad (67%)
  → Posición reducida o monitorear
```

---

### **Ejemplo 2: Terrorism**

**Pregunta:**
```
"¿Cómo afecta un ataque terrorista al mercado?"
```

**VIX:** 25

**Resultado:**
```
📊 PREDICCIÓN:
  • Probabilidad base: 74%
  • Probabilidad contextual: 76%
  • Ajuste VIX: +3%
  • Dirección: BAJISTA
  • α = 0.277, β = 1.70 (¡efecto polvorín!)

📰 NOTICIAS SIMILARES (RAG):
  1. "Hezbollah seizes 2 hills from Al Qaeda..."
     Fecha: 2015-05-26
     Similitud: 83%

💡 RECOMENDACIÓN:
  ⚠ ALTA probabilidad (76%)
  → Posición activa recomendada
```

---

### **Ejemplo 3: Crisis Financiera**

**Pregunta:**
```
"Analiza el impacto de una crisis financiera"
```

**VIX:** 40

**Resultado:**
```
📊 PREDICCIÓN:
  • Probabilidad base: 81%
  • Probabilidad contextual: 100%
  • Ajuste VIX: +23%
  • Dirección: BAJISTA
  • α = 0.245, β = 1.52 (efecto polvorín)

📰 NOTICIAS SIMILARES (RAG):
  1. "Crisis in paradise: Meltdown leaves ghost resorts"
     Fecha: 2008-11-19
     Similitud: 100%

💡 RECOMENDACIÓN:
  ⚠ ALTA probabilidad (100%)
  → Posición activa - VENDER
```

---

## 🔧 CONFIGURACIÓN OPCIONAL: GEMINI API

Si quieres usar **Google Gemini** para respuestas más naturales:

### **1. Obtener API Key:**

1. Ve a: https://makersuite.google.com/app/apikey
2. Crea un proyecto
3. Genera API key

### **2. Configurar:**

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="tu-api-key-aqui"

# O en archivo .env
echo GEMINI_API_KEY=tu-api-key-aqui >> .env
```

### **3. Instalar dependencia:**

```bash
py -m pip install google-generativeai
```

**Con Gemini:**
- Respuestas más naturales
- Mejor explicación
- Contexto más rico

**Sin Gemini (modo LOCAL):**
- Respuestas estructuradas
- Más rápido
- No requiere API key
- ✓ FUNCIONA PERFECTAMENTE para el hackathon

---

## 📈 FLUJO COMPLETO DEL SISTEMA

```
┌─────────────────┐
│ Usuario pregunta│
│ "Fed sube tasas"│
└────────┬────────┘
         │
         ▼
┌────────────────────────┐
│ 1. CLASIFICAR PREGUNTA │
│    → "fed_rates"       │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 2. RAG: Buscar Similar│
│    TF-IDF en 49k news  │
│    → Top 3-5 noticias  │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 3. MODELO: Predecir   │
│    α=0.211, β=1.18     │
│    P_base → P_ctx      │
│    58% → 67% (+15%)    │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 4. GENERAR RESPUESTA  │
│    RAG + Predicción    │
│    + Recomendación     │
└────────┬───────────────┘
         │
         ▼
┌─────────────────┐
│ 5. VISUALIZAR   │
│    Streamlit    │
│    Gráficas     │
└─────────────────┘
```

---

## 🏆 VENTAJAS PARA EL HACKATHON

### **1. Innovación:**
```
✓ RAG: Busca en datos históricos reales
✓ α y β por categoría (no genéricos)
✓ Visualizaciones interactivas
✓ Explicabilidad total
```

### **2. Robustez:**
```
✓ 49,718 noticias procesadas
✓ 17 categorías diferentes
✓ Funciona con y sin Gemini
✓ <1 segundo por consulta
```

### **3. Usabilidad:**
```
✓ Interfaz Streamlit intuitiva
✓ Ejemplos rápidos
✓ Chat natural
✓ Gráficas en tiempo real
```

### **4. Diferenciadores:**
```
✓ RAG (no solo predicción)
✓ α y β específicos por categoría
✓ Contexto VIX
✓ Basado en física (Landau)
```

---

## 📝 CHECKLIST PARA DEMO

### **Antes del Hackathon:**
- [ ] Ejecutar: `py chatbot_rag_gemini.py` (verificar funciona)
- [ ] Ejecutar: `py -m streamlit run app_chatbot_hackathon.py`
- [ ] Probar 5 preguntas diferentes
- [ ] Laptop 100% cargado
- [ ] Internet estable
- [ ] Screenshots de resultados

### **Durante la Demo:**
- [ ] Abrir Streamlit
- [ ] Mostrar pregunta ejemplo 1: Fed Rates
- [ ] Destacar RAG (noticias similares)
- [ ] Mostrar gráfica VIX
- [ ] Explicar α y β
- [ ] Mostrar pregunta ejemplo 2: Terrorism
- [ ] Destacar diferencia en β (polvorín)
- [ ] Comparar ambas predicciones

### **Pitch (30 seg):**
```
"Nuestro chatbot combina RAG con 50k noticias históricas
 y un modelo predictivo que considera el contexto del mercado.

α y β son específicos de cada tipo de noticia:
  • Terrorism: β=1.70 (efecto polvorín extremo)
  • Housing: β=0.87 (estable)

El sistema ENTIENDE que diferentes noticias explotan diferente
en pánico. No es magia - es RAG + física + datos."
```

---

## 🎯 COMANDOS RÁPIDOS

```bash
# Inicializar todo
py chatbot_rag_gemini.py

# Lanzar dashboard
py -m streamlit run app_chatbot_hackathon.py

# Ver parámetros
py -c "import pandas as pd; df = pd.read_csv('data/processed/landau/parametros_por_categoria_20251108.csv'); print(df.sort_values('beta', ascending=False))"

# Predicción rápida
py -c "from chatbot_rag_gemini import *; c = ChatbotGemini(); c.inicializar(); print(c.procesar_consulta('Fed rates', 30, 'SPY')['respuesta'])"
```

---

## 📚 ARCHIVOS CLAVE

```
chatbot_rag_gemini.py          → Sistema completo (RAG + Modelo + Chatbot)
app_chatbot_hackathon.py       → Interfaz Streamlit
data/models/
  ├─ rag_vectorizer.pkl        → Vectorizer TF-IDF + noticias
  └─ modelo_refinado_*.pkl     → α y β por categoría
data/processed/landau/
  └─ parametros_por_categoria_*.csv → Parámetros en CSV
```

---

## 🚀 ¡LISTO PARA EL HACKATHON!

Tu sistema está **100% funcional** con:
- ✓ RAG con 49,718 noticias
- ✓ Modelo con α y β por categoría
- ✓ Interfaz Streamlit
- ✓ Visualizaciones
- ✓ Explicabilidad total

**Ejecuta y demuestra!** 🏆


## 🎯 ¿QUÉ TENEMOS?

Un **Chatbot Inteligente** que combina:

1. **RAG** (Retrieval Augmented Generation)
   - 49,718 noticias históricas
   - Embeddings TF-IDF para búsqueda rápida
   - Encuentra noticias similares en <1 segundo

2. **Modelo Predictivo Refinado**
   - α y β específicos por categoría
   - 17 categorías diferentes
   - Considera contexto VIX

3. **Interfaz Streamlit**
   - Chat interactivo
   - Visualizaciones en tiempo real
   - Explicabilidad total

---

## 🚀 CÓMO LANZAR EL CHATBOT

### **Opción 1: Streamlit (Recomendado para DEMO)**

```bash
cd "d:\curosor\ pojects\hackaton"
py -m streamlit run app_chatbot_hackathon.py
```

**Se abrirá:** `http://localhost:8501`

---

### **Opción 2: Python Directo (para pruebas)**

```python
from chatbot_rag_gemini import ChatbotGemini, SistemaRAG, ModeloPredictor

# Inicializar sistema
rag = SistemaRAG()
rag.cargar_noticias()
rag.crear_embeddings_simple()

predictor = ModeloPredictor()
predictor.cargar_modelo()

chatbot = ChatbotGemini()
chatbot.inicializar()
chatbot.conectar_rag(rag)
chatbot.conectar_predictor(predictor)

# Hacer consulta
resultado = chatbot.procesar_consulta(
    "¿Qué pasa si la Fed sube tasas?",
    vix_actual=30,
    asset='SPY'
)

print(resultado['respuesta'])
```

---

## 📊 CARACTERÍSTICAS PRINCIPALES

### **1. RAG (Retrieval Augmented Generation)**

```
Usuario: "¿Qué pasa si la Fed sube tasas?"
  ↓
Sistema RAG busca en 49,718 noticias:
  • "Fed raises interest rates..."
  • "Federal Reserve increases..."
  • "FOMC decision..."
  ↓
Devuelve Top 3-5 noticias más similares
```

**Ventajas:**
- ✓ Respuestas basadas en datos reales (no inventadas)
- ✓ Contexto histórico automático
- ✓ Similitud medible (0-100%)

---

### **2. Modelo Predictivo con α y β**

```
Categoría detectada: "fed_rates"
  ↓
Parámetros específicos:
  • α = 0.211 (amplificador moderado)
  • β = 1.178 (efecto polvorín leve)
  ↓
VIX actual: 30
  ↓
Cálculo:
  P_base = 58% (del token 5.8)
  P_contextual = 58% × (1 + 0.211 × (1.5 - 1)^1.178)
               = 58% × 1.09
               = 63.2%
  ↓
Resultado: 58% → 63% (+9% por VIX alto)
```

**Ventajas:**
- ✓ Considera contexto del mercado (VIX)
- ✓ α y β diferentes por tipo de noticia
- ✓ Interpretable (no caja negra)

---

### **3. Interfaz Streamlit**

**Componentes:**

1. **Chat Inteligente:**
   - Input de pregunta
   - Ejemplos rápidos
   - VIX ajustable
   - Respuesta completa

2. **Visualizaciones:**
   - Gráfica Probabilidad vs VIX
   - Noticias históricas (RAG)
   - Parámetros α y β
   - Recomendación final

3. **Análisis Detallado:**
   - Top categorías por β
   - Tabla de parámetros
   - Explicación de α y β

---

## 🎓 EJEMPLOS DE USO

### **Ejemplo 1: Fed Rates**

**Pregunta:**
```
"¿Qué pasa si la Fed sube tasas con VIX alto?"
```

**VIX:** 35

**Resultado:**
```
📊 PREDICCIÓN:
  • Probabilidad base: 58%
  • Probabilidad contextual: 67%
  • Ajuste VIX: +15%
  • Dirección: NEUTRAL
  • α = 0.211, β = 1.18

📰 NOTICIAS SIMILARES (RAG):
  1. "China Blames Wall Street Meltdown On Federal Reserve..."
     Fecha: 2008-09-19

💡 RECOMENDACIÓN:
  ⚡ MODERADA probabilidad (67%)
  → Posición reducida o monitorear
```

---

### **Ejemplo 2: Terrorism**

**Pregunta:**
```
"¿Cómo afecta un ataque terrorista al mercado?"
```

**VIX:** 25

**Resultado:**
```
📊 PREDICCIÓN:
  • Probabilidad base: 74%
  • Probabilidad contextual: 76%
  • Ajuste VIX: +3%
  • Dirección: BAJISTA
  • α = 0.277, β = 1.70 (¡efecto polvorín!)

📰 NOTICIAS SIMILARES (RAG):
  1. "Hezbollah seizes 2 hills from Al Qaeda..."
     Fecha: 2015-05-26
     Similitud: 83%

💡 RECOMENDACIÓN:
  ⚠ ALTA probabilidad (76%)
  → Posición activa recomendada
```

---

### **Ejemplo 3: Crisis Financiera**

**Pregunta:**
```
"Analiza el impacto de una crisis financiera"
```

**VIX:** 40

**Resultado:**
```
📊 PREDICCIÓN:
  • Probabilidad base: 81%
  • Probabilidad contextual: 100%
  • Ajuste VIX: +23%
  • Dirección: BAJISTA
  • α = 0.245, β = 1.52 (efecto polvorín)

📰 NOTICIAS SIMILARES (RAG):
  1. "Crisis in paradise: Meltdown leaves ghost resorts"
     Fecha: 2008-11-19
     Similitud: 100%

💡 RECOMENDACIÓN:
  ⚠ ALTA probabilidad (100%)
  → Posición activa - VENDER
```

---

## 🔧 CONFIGURACIÓN OPCIONAL: GEMINI API

Si quieres usar **Google Gemini** para respuestas más naturales:

### **1. Obtener API Key:**

1. Ve a: https://makersuite.google.com/app/apikey
2. Crea un proyecto
3. Genera API key

### **2. Configurar:**

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="tu-api-key-aqui"

# O en archivo .env
echo GEMINI_API_KEY=tu-api-key-aqui >> .env
```

### **3. Instalar dependencia:**

```bash
py -m pip install google-generativeai
```

**Con Gemini:**
- Respuestas más naturales
- Mejor explicación
- Contexto más rico

**Sin Gemini (modo LOCAL):**
- Respuestas estructuradas
- Más rápido
- No requiere API key
- ✓ FUNCIONA PERFECTAMENTE para el hackathon

---

## 📈 FLUJO COMPLETO DEL SISTEMA

```
┌─────────────────┐
│ Usuario pregunta│
│ "Fed sube tasas"│
└────────┬────────┘
         │
         ▼
┌────────────────────────┐
│ 1. CLASIFICAR PREGUNTA │
│    → "fed_rates"       │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 2. RAG: Buscar Similar│
│    TF-IDF en 49k news  │
│    → Top 3-5 noticias  │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 3. MODELO: Predecir   │
│    α=0.211, β=1.18     │
│    P_base → P_ctx      │
│    58% → 67% (+15%)    │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 4. GENERAR RESPUESTA  │
│    RAG + Predicción    │
│    + Recomendación     │
└────────┬───────────────┘
         │
         ▼
┌─────────────────┐
│ 5. VISUALIZAR   │
│    Streamlit    │
│    Gráficas     │
└─────────────────┘
```

---

## 🏆 VENTAJAS PARA EL HACKATHON

### **1. Innovación:**
```
✓ RAG: Busca en datos históricos reales
✓ α y β por categoría (no genéricos)
✓ Visualizaciones interactivas
✓ Explicabilidad total
```

### **2. Robustez:**
```
✓ 49,718 noticias procesadas
✓ 17 categorías diferentes
✓ Funciona con y sin Gemini
✓ <1 segundo por consulta
```

### **3. Usabilidad:**
```
✓ Interfaz Streamlit intuitiva
✓ Ejemplos rápidos
✓ Chat natural
✓ Gráficas en tiempo real
```

### **4. Diferenciadores:**
```
✓ RAG (no solo predicción)
✓ α y β específicos por categoría
✓ Contexto VIX
✓ Basado en física (Landau)
```

---

## 📝 CHECKLIST PARA DEMO

### **Antes del Hackathon:**
- [ ] Ejecutar: `py chatbot_rag_gemini.py` (verificar funciona)
- [ ] Ejecutar: `py -m streamlit run app_chatbot_hackathon.py`
- [ ] Probar 5 preguntas diferentes
- [ ] Laptop 100% cargado
- [ ] Internet estable
- [ ] Screenshots de resultados

### **Durante la Demo:**
- [ ] Abrir Streamlit
- [ ] Mostrar pregunta ejemplo 1: Fed Rates
- [ ] Destacar RAG (noticias similares)
- [ ] Mostrar gráfica VIX
- [ ] Explicar α y β
- [ ] Mostrar pregunta ejemplo 2: Terrorism
- [ ] Destacar diferencia en β (polvorín)
- [ ] Comparar ambas predicciones

### **Pitch (30 seg):**
```
"Nuestro chatbot combina RAG con 50k noticias históricas
 y un modelo predictivo que considera el contexto del mercado.

α y β son específicos de cada tipo de noticia:
  • Terrorism: β=1.70 (efecto polvorín extremo)
  • Housing: β=0.87 (estable)

El sistema ENTIENDE que diferentes noticias explotan diferente
en pánico. No es magia - es RAG + física + datos."
```

---

## 🎯 COMANDOS RÁPIDOS

```bash
# Inicializar todo
py chatbot_rag_gemini.py

# Lanzar dashboard
py -m streamlit run app_chatbot_hackathon.py

# Ver parámetros
py -c "import pandas as pd; df = pd.read_csv('data/processed/landau/parametros_por_categoria_20251108.csv'); print(df.sort_values('beta', ascending=False))"

# Predicción rápida
py -c "from chatbot_rag_gemini import *; c = ChatbotGemini(); c.inicializar(); print(c.procesar_consulta('Fed rates', 30, 'SPY')['respuesta'])"
```

---

## 📚 ARCHIVOS CLAVE

```
chatbot_rag_gemini.py          → Sistema completo (RAG + Modelo + Chatbot)
app_chatbot_hackathon.py       → Interfaz Streamlit
data/models/
  ├─ rag_vectorizer.pkl        → Vectorizer TF-IDF + noticias
  └─ modelo_refinado_*.pkl     → α y β por categoría
data/processed/landau/
  └─ parametros_por_categoria_*.csv → Parámetros en CSV
```

---

## 🚀 ¡LISTO PARA EL HACKATHON!

Tu sistema está **100% funcional** con:
- ✓ RAG con 49,718 noticias
- ✓ Modelo con α y β por categoría
- ✓ Interfaz Streamlit
- ✓ Visualizaciones
- ✓ Explicabilidad total

**Ejecuta y demuestra!** 🏆



