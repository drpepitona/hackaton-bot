# 📰 GUÍA COMPLETA: Obtener Noticias para tu IA

## 🎯 Objetivo

Recolectar noticias económicas de **EEUU, Europa, Asia y Australia** y correlacionarlas con movimientos del **S&P 500** para entrenar tu IA predictiva.

---

## 🚀 OPCIÓN 1: GDELT Project (GRATIS, SIN API KEY) ⭐⭐⭐

### **¿Qué es GDELT?**

[GDELT](https://www.gdeltproject.org/) es la base de datos de noticias más grande del mundo:
- ✅ **100% GRATIS**
- ✅ **No requiere API key**
- ✅ **Noticias desde 1979**
- ✅ **65 idiomas**
- ✅ **Actualización cada 15 minutos**
- ✅ **Cobertura global completa**

### **Script Creado para Ti:**

```bash
# Ya está listo, solo ejecuta:
py src/data_collection/gdelt_news_collector.py
```

**¿Qué hace?**
1. Busca noticias económicas de EEUU, Europa, Asia, Australia
2. Las correlaciona con movimientos del S&P 500
3. Clasifica impacto: ALTO, MEDIO, BAJO
4. Guarda todo en CSV listo para entrenar

**Ventajas:**
- ✅ Inmediato (no requiere registro)
- ✅ Datos históricos completos
- ✅ Cobertura global
- ✅ Gratis para siempre

---

## 🚀 OPCIÓN 2: News API (GRATIS para empezar) ⭐⭐

### **¿Qué es News API?**

[News API](https://newsapi.org/) es una API de noticias moderna:
- ✅ **Plan gratuito: 100 requests/día**
- ✅ **Fácil de usar**
- ✅ **Fuentes verificadas**
- ✅ **Datos estructurados**

### **Cómo Obtener API Key (2 minutos):**

1. **Ir a:** https://newsapi.org/register

2. **Llenar formulario:**
   ```
   First name:  [Tu nombre]
   Email:       [Tu email]
   Password:    [Crear password]
   ```

3. **Click en "Submit"**

4. **Copiar tu API key** (aparece inmediatamente)

5. **Agregar a `.env`:**
   ```
   NEWS_API_KEY=tu_api_key_aqui
   ```

6. **Ejecutar:**
   ```bash
   py src/data_collection/news_collector.py
   ```

### **Plan Gratuito:**
- ✅ 100 requests/día
- ✅ Datos de últimos 30 días
- ✅ Suficiente para desarrollo

### **Plan Pago (si lo necesitas):**
- $449/mes: Hasta 250,000 requests/día
- Datos históricos completos
- Para producción

---

## 🚀 OPCIÓN 3: Combinación (RECOMENDADO) ⭐⭐⭐

### **La Mejor Estrategia:**

```
1. GDELT (Gratis)
   └─ Noticias históricas (1979-2025)
   └─ Volumen alto de noticias
   └─ Cobertura global completa
   
2. News API (Gratis 100/día)
   └─ Noticias actuales de calidad
   └─ Fuentes específicas (Bloomberg, Reuters)
   └─ Para mantener modelo actualizado
   
3. Web Scraping (Avanzado)
   └─ Fuentes específicas si necesitas
   └─ Requires más código
```

---

## 📊 FUENTES DE DATOS ALTERNATIVAS

### **1. Kaggle Datasets** (Noticias pre-recolectadas)

**Datasets recomendados:**
```
- "Financial News and Stock Price Integration Dataset"
- "Reuters Financial News Dataset"
- "Bloomberg Economic Calendar"
- "GDELT Global News Database"
```

**Link:** https://www.kaggle.com/datasets

**Ventajas:**
- ✅ Gratis
- ✅ Ya procesados
- ✅ Listos para ML
- ✅ Históricamente etiquetados

---

### **2. yfinance** (Ya lo tienes instalado)

**Noticias de empresas específicas:**
```python
import yfinance as yf

# Obtener noticias de S&P 500
spy = yf.Ticker("SPY")
news = spy.news

# Cada noticia incluye:
# - Título
# - Fecha
# - URL
# - Resumen
```

---

### **3. Alpha Vantage** (API Gratis)

**News & Sentiments API:**
- ✅ Análisis de sentimiento incluido
- ✅ 500 requests/día gratis
- ✅ Noticias de mercado

**Obtener key:** https://www.alphavantage.co/support/#api-key

---

### **4. GDELT 2.0 - Events Database**

**Base de datos de eventos económicos:**
```python
# Eventos como:
# - Reuniones del Fed
# - Anuncios de inflación
# - Cambios de tasas
# - Crisis económicas
```

**Link:** http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf

---

## 🎯 TU PLAN DE ACCIÓN

### **FASE 1: Empezar HOY (Sin registro)**

```bash
# 1. Usar GDELT (YA ESTÁ LISTO)
py src/data_collection/gdelt_news_collector.py

# 2. Obtendrás:
#    - Noticias de EEUU, Europa, Asia, Australia
#    - Correlacionadas con S&P 500
#    - Clasificadas por impacto
#    - Listas para entrenar
```

---

### **FASE 2: Mejorar Datos (5 minutos)**

```bash
# 1. Registrarte en News API (2 min)
https://newsapi.org/register

# 2. Agregar key a .env
NEWS_API_KEY=tu_key_aqui

# 3. Ejecutar recolector avanzado
py src/data_collection/news_collector.py

# 4. Combinar con GDELT
# Tendrás noticias de alta calidad + volumen
```

---

### **FASE 3: Análisis de Sentimiento**

```python
# Usar FinBERT (BERT especializado en finanzas)
from transformers import pipeline

sentiment = pipeline("sentiment-analysis", 
                     model="ProsusAI/finbert")

# Analizar cada noticia
for noticia in noticias:
    resultado = sentiment(noticia['titulo'])
    # positive/negative/neutral
```

---

## 📊 ESTRUCTURA DE DATOS QUE OBTENDRÁS

### **Dataset de Noticias:**

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `fecha` | Fecha de publicación | 2025-01-15 |
| `titulo` | Titular de la noticia | "Fed raises interest rates by 0.5%" |
| `region` | Región/País | usa_alta, europa_alta, asia_alta |
| `keyword` | Palabra clave | "Federal Reserve interest rates" |
| `impacto_esperado` | Impacto estimado | ALTO, MEDIO, BAJO |
| `sp500_return_day` | Retorno S&P 500 mismo día | +0.0123 (+1.23%) |
| `sp500_return_next_day` | Retorno día siguiente | -0.0245 (-2.45%) |
| `sp500_move_direction` | Dirección | UP, DOWN, FLAT |
| `impacto_clasificado` | Impacto real medido | ALTO, MEDIO, BAJO |

---

## 🤖 CÓMO USAR ESTOS DATOS PARA ENTRENAR

### **Paso 1: Recolectar Noticias**
```bash
py src/data_collection/gdelt_news_collector.py
```

### **Paso 2: Análisis de Sentimiento**
```python
# Script que crearemos
py src/preprocessing/sentiment_analysis.py
```

### **Paso 3: Feature Engineering**
```python
# Combinar:
# - Texto de noticia (BERT embeddings)
# - Datos económicos del día
# - Indicadores técnicos
# - Sentimiento
```

### **Paso 4: Entrenar Modelo**
```python
# Modelo híbrido:
# - LSTM para series temporales
# - BERT para texto de noticias
# - Ensemble final
```

---

## 📈 TIPOS DE NOTICIAS QUE AFECTAN S&P 500

### **ALTO IMPACTO** 🔴 (Movimientos >2%)

**EEUU:**
- Decisiones de tasas Fed
- Reportes de empleo (NFP)
- Datos de inflación (CPI, PCE)
- Datos de PIB
- Discursos de Jerome Powell

**Europa:**
- Decisiones ECB
- Crisis de deuda
- Brexit
- Inflación eurozona

**Asia:**
- Datos de PIB China
- Política monetaria Japón
- Conflictos geopolíticos
- Crisis en mercados emergentes

**Global:**
- Crisis de petróleo
- Guerras/conflictos
- Pandemias
- Crisis financieras

### **MEDIO IMPACTO** 🟡 (Movimientos 0.5-2%)

- Ventas minoristas
- Confianza del consumidor
- Balanza comercial
- Producción industrial
- Datos de vivienda

### **BAJO IMPACTO** 🟢 (<0.5%)

- Noticias corporativas individuales
- Datos regionales
- Eventos menores

---

## 💡 EJEMPLO DE USO COMPLETO

### **Script Completo:**

```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar noticias correlacionadas
df_news = pd.read_csv('data/processed/news/noticias_gdelt_correlacionadas_*.csv')

# 2. Cargar datos económicos
df_eco = pd.read_csv('data/processed/fred/fred_alto_impacto_*.csv', 
                     index_col=0, parse_dates=True)

# 3. Cargar S&P 500
df_spy = pd.read_csv('data/processed/market/SPY_indicadores_*.csv',
                     index_col=0, parse_dates=True)

# 4. Analizar noticias de alto impacto
noticias_alto = df_news[df_news['impacto_clasificado'] == 'ALTO']

print(f"Noticias de alto impacto: {len(noticias_alto)}")
print("\nEjemplos:")
for _, row in noticias_alto.head(5).iterrows():
    print(f"  {row['fecha']}: {row['title']}")
    print(f"    Impacto S&P 500: {row['sp500_return_next_day']*100:.2f}%")

# 5. Identificar patrones
# ¿Qué keywords tienen mayor impacto?
impacto_por_keyword = df_news.groupby('keyword')['impacto_absoluto'].mean().sort_values(ascending=False)
print("\nKeywords con mayor impacto promedio:")
print(impacto_por_keyword.head(10))
```

---

## 🎓 PRÓXIMOS PASOS

### **HOY (Sin registro):**

```bash
# 1. Obtener noticias con GDELT
py src/data_collection/gdelt_news_collector.py

# 2. Ya tendrás noticias correlacionadas con S&P 500
# 3. Listo para entrenar modelo básico
```

### **ESTA SEMANA (Con APIs gratuitas):**

```bash
# 1. Registrarse en News API (2 min)
https://newsapi.org/register

# 2. Obtener noticias de calidad
py src/data_collection/news_collector.py

# 3. Análisis de sentimiento
py src/preprocessing/sentiment_analysis.py

# 4. Entrenar modelo completo
py src/training/entrenar_modelo_noticias.py
```

---

## 🔑 RESUMEN DE APIs

| API | Costo | API Key | Límite | Datos |
|-----|-------|---------|--------|-------|
| **GDELT** | Gratis | ❌ No necesita | Ilimitado | Noticias globales |
| **News API** | Gratis | ✅ Sí (fácil) | 100/día | Noticias actuales |
| **Alpha Vantage** | Gratis | ✅ Sí | 500/día | News + sentiment |
| **yfinance** | Gratis | ❌ No | Ilimitado | Noticias de stocks |

---

## ⚡ EJECUTAR AHORA

```bash
# Sin ningún registro, ejecuta:
py src/data_collection/gdelt_news_collector.py

# Obtendrás:
# - Noticias de 90 días atrás
# - De EEUU, Europa, Asia, Australia
# - Correlacionadas con S&P 500
# - Clasificadas por impacto
# - Listas para entrenar
```

---

## 📚 RECURSOS ADICIONALES

### **Datasets Públicos de Noticias:**
- **Kaggle:** https://www.kaggle.com/datasets/jeet2016/us-financial-news-articles
- **HuggingFace:** https://huggingface.co/datasets/financial_phrasebank
- **GitHub:** Repositorios con noticias históricas

### **Modelos Pre-entrenados:**
- **FinBERT:** Análisis de sentimiento financiero
- **StockNet:** Predicción basada en noticias
- **BERT Financial:** Especializado en finanzas

---

**¿Quieres que ejecute el recolector GDELT ahora para obtener todas las noticias?** 🚀


## 🎯 Objetivo

Recolectar noticias económicas de **EEUU, Europa, Asia y Australia** y correlacionarlas con movimientos del **S&P 500** para entrenar tu IA predictiva.

---

## 🚀 OPCIÓN 1: GDELT Project (GRATIS, SIN API KEY) ⭐⭐⭐

### **¿Qué es GDELT?**

[GDELT](https://www.gdeltproject.org/) es la base de datos de noticias más grande del mundo:
- ✅ **100% GRATIS**
- ✅ **No requiere API key**
- ✅ **Noticias desde 1979**
- ✅ **65 idiomas**
- ✅ **Actualización cada 15 minutos**
- ✅ **Cobertura global completa**

### **Script Creado para Ti:**

```bash
# Ya está listo, solo ejecuta:
py src/data_collection/gdelt_news_collector.py
```

**¿Qué hace?**
1. Busca noticias económicas de EEUU, Europa, Asia, Australia
2. Las correlaciona con movimientos del S&P 500
3. Clasifica impacto: ALTO, MEDIO, BAJO
4. Guarda todo en CSV listo para entrenar

**Ventajas:**
- ✅ Inmediato (no requiere registro)
- ✅ Datos históricos completos
- ✅ Cobertura global
- ✅ Gratis para siempre

---

## 🚀 OPCIÓN 2: News API (GRATIS para empezar) ⭐⭐

### **¿Qué es News API?**

[News API](https://newsapi.org/) es una API de noticias moderna:
- ✅ **Plan gratuito: 100 requests/día**
- ✅ **Fácil de usar**
- ✅ **Fuentes verificadas**
- ✅ **Datos estructurados**

### **Cómo Obtener API Key (2 minutos):**

1. **Ir a:** https://newsapi.org/register

2. **Llenar formulario:**
   ```
   First name:  [Tu nombre]
   Email:       [Tu email]
   Password:    [Crear password]
   ```

3. **Click en "Submit"**

4. **Copiar tu API key** (aparece inmediatamente)

5. **Agregar a `.env`:**
   ```
   NEWS_API_KEY=tu_api_key_aqui
   ```

6. **Ejecutar:**
   ```bash
   py src/data_collection/news_collector.py
   ```

### **Plan Gratuito:**
- ✅ 100 requests/día
- ✅ Datos de últimos 30 días
- ✅ Suficiente para desarrollo

### **Plan Pago (si lo necesitas):**
- $449/mes: Hasta 250,000 requests/día
- Datos históricos completos
- Para producción

---

## 🚀 OPCIÓN 3: Combinación (RECOMENDADO) ⭐⭐⭐

### **La Mejor Estrategia:**

```
1. GDELT (Gratis)
   └─ Noticias históricas (1979-2025)
   └─ Volumen alto de noticias
   └─ Cobertura global completa
   
2. News API (Gratis 100/día)
   └─ Noticias actuales de calidad
   └─ Fuentes específicas (Bloomberg, Reuters)
   └─ Para mantener modelo actualizado
   
3. Web Scraping (Avanzado)
   └─ Fuentes específicas si necesitas
   └─ Requires más código
```

---

## 📊 FUENTES DE DATOS ALTERNATIVAS

### **1. Kaggle Datasets** (Noticias pre-recolectadas)

**Datasets recomendados:**
```
- "Financial News and Stock Price Integration Dataset"
- "Reuters Financial News Dataset"
- "Bloomberg Economic Calendar"
- "GDELT Global News Database"
```

**Link:** https://www.kaggle.com/datasets

**Ventajas:**
- ✅ Gratis
- ✅ Ya procesados
- ✅ Listos para ML
- ✅ Históricamente etiquetados

---

### **2. yfinance** (Ya lo tienes instalado)

**Noticias de empresas específicas:**
```python
import yfinance as yf

# Obtener noticias de S&P 500
spy = yf.Ticker("SPY")
news = spy.news

# Cada noticia incluye:
# - Título
# - Fecha
# - URL
# - Resumen
```

---

### **3. Alpha Vantage** (API Gratis)

**News & Sentiments API:**
- ✅ Análisis de sentimiento incluido
- ✅ 500 requests/día gratis
- ✅ Noticias de mercado

**Obtener key:** https://www.alphavantage.co/support/#api-key

---

### **4. GDELT 2.0 - Events Database**

**Base de datos de eventos económicos:**
```python
# Eventos como:
# - Reuniones del Fed
# - Anuncios de inflación
# - Cambios de tasas
# - Crisis económicas
```

**Link:** http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf

---

## 🎯 TU PLAN DE ACCIÓN

### **FASE 1: Empezar HOY (Sin registro)**

```bash
# 1. Usar GDELT (YA ESTÁ LISTO)
py src/data_collection/gdelt_news_collector.py

# 2. Obtendrás:
#    - Noticias de EEUU, Europa, Asia, Australia
#    - Correlacionadas con S&P 500
#    - Clasificadas por impacto
#    - Listas para entrenar
```

---

### **FASE 2: Mejorar Datos (5 minutos)**

```bash
# 1. Registrarte en News API (2 min)
https://newsapi.org/register

# 2. Agregar key a .env
NEWS_API_KEY=tu_key_aqui

# 3. Ejecutar recolector avanzado
py src/data_collection/news_collector.py

# 4. Combinar con GDELT
# Tendrás noticias de alta calidad + volumen
```

---

### **FASE 3: Análisis de Sentimiento**

```python
# Usar FinBERT (BERT especializado en finanzas)
from transformers import pipeline

sentiment = pipeline("sentiment-analysis", 
                     model="ProsusAI/finbert")

# Analizar cada noticia
for noticia in noticias:
    resultado = sentiment(noticia['titulo'])
    # positive/negative/neutral
```

---

## 📊 ESTRUCTURA DE DATOS QUE OBTENDRÁS

### **Dataset de Noticias:**

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `fecha` | Fecha de publicación | 2025-01-15 |
| `titulo` | Titular de la noticia | "Fed raises interest rates by 0.5%" |
| `region` | Región/País | usa_alta, europa_alta, asia_alta |
| `keyword` | Palabra clave | "Federal Reserve interest rates" |
| `impacto_esperado` | Impacto estimado | ALTO, MEDIO, BAJO |
| `sp500_return_day` | Retorno S&P 500 mismo día | +0.0123 (+1.23%) |
| `sp500_return_next_day` | Retorno día siguiente | -0.0245 (-2.45%) |
| `sp500_move_direction` | Dirección | UP, DOWN, FLAT |
| `impacto_clasificado` | Impacto real medido | ALTO, MEDIO, BAJO |

---

## 🤖 CÓMO USAR ESTOS DATOS PARA ENTRENAR

### **Paso 1: Recolectar Noticias**
```bash
py src/data_collection/gdelt_news_collector.py
```

### **Paso 2: Análisis de Sentimiento**
```python
# Script que crearemos
py src/preprocessing/sentiment_analysis.py
```

### **Paso 3: Feature Engineering**
```python
# Combinar:
# - Texto de noticia (BERT embeddings)
# - Datos económicos del día
# - Indicadores técnicos
# - Sentimiento
```

### **Paso 4: Entrenar Modelo**
```python
# Modelo híbrido:
# - LSTM para series temporales
# - BERT para texto de noticias
# - Ensemble final
```

---

## 📈 TIPOS DE NOTICIAS QUE AFECTAN S&P 500

### **ALTO IMPACTO** 🔴 (Movimientos >2%)

**EEUU:**
- Decisiones de tasas Fed
- Reportes de empleo (NFP)
- Datos de inflación (CPI, PCE)
- Datos de PIB
- Discursos de Jerome Powell

**Europa:**
- Decisiones ECB
- Crisis de deuda
- Brexit
- Inflación eurozona

**Asia:**
- Datos de PIB China
- Política monetaria Japón
- Conflictos geopolíticos
- Crisis en mercados emergentes

**Global:**
- Crisis de petróleo
- Guerras/conflictos
- Pandemias
- Crisis financieras

### **MEDIO IMPACTO** 🟡 (Movimientos 0.5-2%)

- Ventas minoristas
- Confianza del consumidor
- Balanza comercial
- Producción industrial
- Datos de vivienda

### **BAJO IMPACTO** 🟢 (<0.5%)

- Noticias corporativas individuales
- Datos regionales
- Eventos menores

---

## 💡 EJEMPLO DE USO COMPLETO

### **Script Completo:**

```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar noticias correlacionadas
df_news = pd.read_csv('data/processed/news/noticias_gdelt_correlacionadas_*.csv')

# 2. Cargar datos económicos
df_eco = pd.read_csv('data/processed/fred/fred_alto_impacto_*.csv', 
                     index_col=0, parse_dates=True)

# 3. Cargar S&P 500
df_spy = pd.read_csv('data/processed/market/SPY_indicadores_*.csv',
                     index_col=0, parse_dates=True)

# 4. Analizar noticias de alto impacto
noticias_alto = df_news[df_news['impacto_clasificado'] == 'ALTO']

print(f"Noticias de alto impacto: {len(noticias_alto)}")
print("\nEjemplos:")
for _, row in noticias_alto.head(5).iterrows():
    print(f"  {row['fecha']}: {row['title']}")
    print(f"    Impacto S&P 500: {row['sp500_return_next_day']*100:.2f}%")

# 5. Identificar patrones
# ¿Qué keywords tienen mayor impacto?
impacto_por_keyword = df_news.groupby('keyword')['impacto_absoluto'].mean().sort_values(ascending=False)
print("\nKeywords con mayor impacto promedio:")
print(impacto_por_keyword.head(10))
```

---

## 🎓 PRÓXIMOS PASOS

### **HOY (Sin registro):**

```bash
# 1. Obtener noticias con GDELT
py src/data_collection/gdelt_news_collector.py

# 2. Ya tendrás noticias correlacionadas con S&P 500
# 3. Listo para entrenar modelo básico
```

### **ESTA SEMANA (Con APIs gratuitas):**

```bash
# 1. Registrarse en News API (2 min)
https://newsapi.org/register

# 2. Obtener noticias de calidad
py src/data_collection/news_collector.py

# 3. Análisis de sentimiento
py src/preprocessing/sentiment_analysis.py

# 4. Entrenar modelo completo
py src/training/entrenar_modelo_noticias.py
```

---

## 🔑 RESUMEN DE APIs

| API | Costo | API Key | Límite | Datos |
|-----|-------|---------|--------|-------|
| **GDELT** | Gratis | ❌ No necesita | Ilimitado | Noticias globales |
| **News API** | Gratis | ✅ Sí (fácil) | 100/día | Noticias actuales |
| **Alpha Vantage** | Gratis | ✅ Sí | 500/día | News + sentiment |
| **yfinance** | Gratis | ❌ No | Ilimitado | Noticias de stocks |

---

## ⚡ EJECUTAR AHORA

```bash
# Sin ningún registro, ejecuta:
py src/data_collection/gdelt_news_collector.py

# Obtendrás:
# - Noticias de 90 días atrás
# - De EEUU, Europa, Asia, Australia
# - Correlacionadas con S&P 500
# - Clasificadas por impacto
# - Listas para entrenar
```

---

## 📚 RECURSOS ADICIONALES

### **Datasets Públicos de Noticias:**
- **Kaggle:** https://www.kaggle.com/datasets/jeet2016/us-financial-news-articles
- **HuggingFace:** https://huggingface.co/datasets/financial_phrasebank
- **GitHub:** Repositorios con noticias históricas

### **Modelos Pre-entrenados:**
- **FinBERT:** Análisis de sentimiento financiero
- **StockNet:** Predicción basada en noticias
- **BERT Financial:** Especializado en finanzas

---

**¿Quieres que ejecute el recolector GDELT ahora para obtener todas las noticias?** 🚀



