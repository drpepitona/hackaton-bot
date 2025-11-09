# 🚀 DATOS COMPLETOS RECOLECTADOS - LISTO PARA ENTRENAR IA

**Fecha:** 2025-11-07  
**Proyecto:** Bot Predictivo de Impacto de Noticias en Mercados USA

---

## ✅ RESUMEN EJECUTIVO

### **¡TIENES TODO LO NECESARIO PARA ENTRENAR TU IA!**

✅ **25 años de datos económicos** (2000-2025)  
✅ **10 años de datos de mercado** (2015-2025)  
✅ **17 series económicas** + **4 índices bursátiles**  
✅ **40,000+ observaciones históricas**  
✅ **Todos los datos listos y procesados**

---

## 📊 DATOS RECOLECTADOS

### 1️⃣ **DATOS ECONÓMICOS** (17 series) ✅

#### **A. Indicadores Macro USA** (3 series)
| Serie | Descripción | Último Valor | Observaciones |
|-------|-------------|--------------|---------------|
| GDPC1 | PIB Real | $23.77T | 102 (trimestral) |
| UNRATE | Tasa de Desempleo | 4.3% | 308 (mensual) |
| CPIAUCSL | Inflación CPI | 324.37 | 309 (mensual) |

#### **B. Mercados Financieros** (2 series)
| Serie | Descripción | Último Valor | Observaciones |
|-------|-------------|--------------|---------------|
| VIXCLS | Volatilidad VIX | 19.5 | 6,744 (diaria) |
| DGS10 | Tesoro 10 años | 4.17% | 6,743 (diaria) |

#### **C. Tipos de Cambio** (7 series)
- **Real:** Euro, Japón, Hong Kong, Australia, China (309 obs c/u)
- **Spot:** USD/EUR (6,740 obs), Índice Dólar (238 obs)

#### **D. Petróleo** (5 series)
| Serie | Descripción | Último Valor | Observaciones |
|-------|-------------|--------------|---------------|
| DCOILWTICO | WTI (Diario) | **$61.79/barril** | 6,741 |
| DCOILBRENTEU | Brent (Diario) | **$65.79/barril** | 6,741 |
| MCOILWTICO | WTI Mensual | $60.89/barril | 310 |
| GASREGW | Gasolina USA | **$3.02/galón** | 1,349 (semanal) |
| GASDESW | Diesel USA | **$3.75/galón** | 1,349 (semanal) |

---

### 2️⃣ **DATOS DE MERCADO** (4 índices) ✅

#### **Índices Principales - 10 años de historia (2015-2025)**

| Índice | Nombre | Precio Actual | Retorno Total | Volatilidad | Días |
|--------|--------|---------------|---------------|-------------|------|
| **SPY** | S&P 500 ETF | **$669.32** | +279.78% | 18.06% | 2,514 |
| **QQQ** | NASDAQ 100 | **$607.66** | +477.76% | 22.37% | 2,514 |
| **DIA** | Dow Jones | **$469.54** | +223.41% | 17.62% | 2,514 |
| **IWM** | Russell 2000 | **$241.12** | +132.51% | 23.03% | 2,514 |

**🎯 Todos incluyen:**
- ✅ Precios OHLC (Open, High, Low, Close)
- ✅ Volumen
- ✅ Dividendos
- ✅ Indicadores técnicos (SMA, RSI, Bollinger Bands)
- ✅ Retornos diarios
- ✅ Volatilidad histórica

---

### 3️⃣ **DATOS DE GAS NATURAL** (EIA) ⚠️

**Estado:** Requiere API Key de EIA  
**Link para obtener key:** https://www.eia.gov/opendata/register.php  
**Nota:** Es GRATIS y toma 2 minutos registrarse

---

## 📁 ARCHIVOS GENERADOS (27 archivos)

### **Datos Económicos** (12 archivos)
```
data/processed/fred/
├── fred_completo_*.csv                    # TODAS las series económicas
├── fred_alto_impacto_*.csv               # ⭐ MÁS IMPORTANTES (8 series)
├── fred_diario_*.csv                     # Solo datos diarios
├── indicadores_economicos_usa_*.csv      # PIB, Desempleo, CPI
├── mercados_financieros_*.csv            # VIX, Tesoro
├── tipos_cambio_real_*.csv               # Monedas ajustadas
├── tipos_cambio_spot_*.csv               # USD/EUR, Índice
└── metadata_*.json                       # INFO DETALLADA

data/processed/fred_oil/
├── fred_oil_completo_*.csv               # Todas series petróleo
├── fred_oil_precios_*.csv                # ⭐ WTI + Brent
├── fred_oil_alto_impacto_*.csv          # Más importantes
└── fred_oil_metadata_*.json             # INFO DETALLADA
```

### **Datos de Mercado** (7 archivos)
```
data/processed/market/
├── indices_combinados_*.csv              # ⭐ TODOS los índices juntos
├── indices_precios_*.csv                 # Solo precios de cierre
├── indices_retornos_*.csv                # Retornos diarios
├── SPY_indicadores_*.csv                 # ⭐ S&P 500 completo
├── QQQ_indicadores_*.csv                 # NASDAQ completo
├── DIA_indicadores_*.csv                 # Dow Jones completo
└── IWM_indicadores_*.csv                 # Russell 2000 completo
```

---

## 🎯 DATASETS RECOMENDADOS PARA ENTRENAR

### **OPCIÓN 1: Dataset Simple** (Para empezar)

```python
import pandas as pd

# Cargar económicos + mercado
df_eco = pd.read_csv('data/processed/fred/fred_alto_impacto_20251107_151424.csv', 
                     index_col=0, parse_dates=True)

df_market = pd.read_csv('data/processed/market/indices_precios_20251107.csv',
                        index_col=0, parse_dates=True)

# Combinar (alineados por fecha)
df_completo = pd.merge(df_eco, df_market, left_index=True, right_index=True, how='inner')

print(f"Dataset final: {df_completo.shape}")
# Resultado: ~2,500 días × 12 columnas (8 económicas + 4 mercado)
```

### **OPCIÓN 2: Dataset Completo con Indicadores** (Recomendado)

```python
# Cargar S&P 500 con todos los indicadores técnicos
df_spy = pd.read_csv('data/processed/market/SPY_indicadores_20251107.csv',
                     index_col=0, parse_dates=True)

# Cargar datos de petróleo
df_oil = pd.read_csv('data/processed/fred_oil/fred_oil_precios_20251107.csv',
                     index_col=0, parse_dates=True)

# Ya tienes:
# - Precios SPY
# - Indicadores técnicos (SMA, RSI, Bollinger)
# - Precios de petróleo WTI y Brent
```

### **OPCIÓN 3: Todo Combinado** (Profesional)

```python
# Económicos
df_eco = pd.read_csv('data/processed/fred/fred_completo_20251107_151424.csv', 
                     index_col=0, parse_dates=True)

# Petróleo
df_oil = pd.read_csv('data/processed/fred_oil/fred_oil_completo_20251107.csv',
                     index_col=0, parse_dates=True)

# Mercado
df_market = pd.read_csv('data/processed/market/indices_combinados_20251107.csv',
                        index_col=0, parse_dates=True)

# Combinar todo
df_total = df_eco.join([df_oil, df_market], how='outer')

print(f"MEGA Dataset: {df_total.shape}")
# Resultado: 6,833 días × 29 columnas
```

---

## 📊 ANÁLISIS QUE PUEDES HACER

### **1. Correlaciones**
```python
# ¿Cómo se relaciona el petróleo con el S&P 500?
correlation = df_oil['DCOILWTICO'].corr(df_market['SPY'])

# ¿Y el VIX con el mercado?
correlation_vix = df_eco['VIXCLS'].corr(df_market['SPY'])
```

### **2. Impacto de Eventos**
```python
# Encontrar días con alta volatilidad
high_vol_days = df_spy[df_spy['Volatility'] > df_spy['Volatility'].quantile(0.95)]

# Ver qué pasó en economía esos días
eventos = df_eco.loc[high_vol_days.index]
```

### **3. Predicción de Movimientos**
```python
# Entrenar LSTM para predecir próximo día del S&P 500
# usando datos económicos y de petróleo como features
```

---

## 🤖 CÓMO ENTRENAR TU IA

### **PASO 1: Preparar Datos**

```python
# Script ya creado: src/training/preparar_datos.py
# Ejecutar: py src/training/preparar_datos.py

# Lo que hace:
# 1. Carga datos económicos + mercado
# 2. Calcula features adicionales (medias móviles, volatilidad)
# 3. Crea secuencias temporales para LSTM
# 4. Divide en train/validation/test
```

### **PASO 2: Entrenar Modelo LSTM**

```python
# Script ya creado: src/training/entrenar_lstm.py
# Ejecutar: py src/training/entrenar_lstm.py

# Lo que hace:
# 1. Crea arquitectura LSTM
# 2. Entrena con datos históricos
# 3. Valida y evalúa
# 4. Guarda modelo entrenado
```

### **PASO 3: Hacer Predicciones**

```python
from tensorflow.keras.models import load_model

# Cargar modelo entrenado
model = load_model('data/models/lstm_predictor_vix.h5')

# Hacer predicción
prediction = model.predict(X_new)
```

---

## 📈 ESTADÍSTICAS CLAVE

### **Datos Económicos:**
- **Período:** 2000-2025 (25 años)
- **Series:** 17
- **Observaciones:** ~22,000
- **Eventos incluidos:**
  - 💥 Crisis 2008
  - 💶 Crisis Europa 2011
  - 🛢️ Crash petróleo 2014-2016
  - 🦠 COVID-19 2020
  - 📈 Recuperación 2021-2023
  - 🔥 Inflación 2022-2023

### **Datos de Mercado:**
- **Período:** 2015-2025 (10 años)
- **Índices:** 4 principales
- **Días:** 2,514 por índice
- **Retorno S&P 500:** +279.78% (¡increíble!)
- **Retorno NASDAQ:** +477.76% (¡casi 5x!)

---

## 🎓 PRÓXIMOS PASOS SUGERIDOS

### **HOY (Si tienes tiempo):**
1. ✅ Revisar los archivos CSV generados
2. ✅ Explorar correlaciones básicas
3. ✅ Visualizar datos en gráficas

### **ESTA SEMANA:**
1. 🤖 Ejecutar `preparar_datos.py` para crear features
2. 🧠 Entrenar primer modelo LSTM
3. 📊 Evaluar predicciones
4. 📈 Backtesting básico

### **PRÓXIMAS SEMANAS:**
1. 📰 Recolectar noticias históricas
2. 🤖 Análisis de sentimiento (BERT/FinBERT)
3. 🎯 Modelo completo: Datos + Noticias → Predicción
4. 🚀 Desplegar en producción

---

## 🔑 API KEYS NECESARIAS

### **Ya tienes:**
✅ **FRED API:** `f6f6d63126fb06361b568e076cb4f7ee` (funcionando)

### **Para obtener (opcional):**
- **EIA (Gas Natural):** https://www.eia.gov/opendata/register.php (GRATIS)
- **News API:** https://newsapi.org/register (GRATIS, 100 req/día)
- **Alpha Vantage:** https://www.alphavantage.co/support/#api-key (GRATIS)

---

## 💡 EJEMPLO RÁPIDO DE USO

```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar datos
df_spy = pd.read_csv('data/processed/market/SPY_indicadores_20251107.csv',
                     index_col=0, parse_dates=True)

df_oil = pd.read_csv('data/processed/fred_oil/fred_oil_precios_20251107.csv',
                     index_col=0, parse_dates=True)

# 2. Analizar correlación
# Alinear fechas
df_combined = pd.merge(df_spy[['Close']], df_oil['DCOILWTICO'], 
                      left_index=True, right_index=True, how='inner')

correlation = df_combined.corr()
print(f"Correlación S&P 500 vs Petróleo WTI: {correlation.iloc[0,1]:.3f}")

# 3. Visualizar
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(df_spy.index, df_spy['Close'], label='S&P 500')
ax1.set_title('S&P 500 - Últimos 10 años')
ax1.legend()
ax1.grid(True)

ax2.plot(df_oil.index, df_oil['DCOILWTICO'], label='Petróleo WTI', color='orange')
ax2.set_title('Petróleo WTI')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('analisis_sp500_petroleo.png')
print("✓ Gráfica guardada: analisis_sp500_petroleo.png")
```

---

## 🎉 ¡ESTÁS LISTO!

### **Tienes TODO lo necesario:**
- ✅ 25 años de datos económicos
- ✅ 10 años de datos de mercado
- ✅ Precios de petróleo (crítico para mercados)
- ✅ Datos procesados y listos
- ✅ Scripts de entrenamiento preparados
- ✅ Estructura profesional del proyecto

### **Puedes entrenar modelos para predecir:**
1. 📈 Movimientos del S&P 500
2. 😨 Cambios en volatilidad (VIX)
3. 🛢️ Impacto del petróleo en mercados
4. 💰 Efectos de inflación en acciones
5. 📊 Y mucho más...

---

## 📞 COMANDOS ÚTILES

```bash
# Ver estructura de archivos
tree data/processed/

# Explorar datos en Python
py
>>> import pandas as pd
>>> df = pd.read_csv('data/processed/fred/fred_alto_impacto_20251107_151424.csv', index_col=0, parse_dates=True)
>>> df.head()
>>> df.describe()

# Ver correlaciones
>>> df.corr()

# Entrenar modelo (cuando estés listo)
py src/training/preparar_datos.py
py src/training/entrenar_lstm.py
```

---

**Última actualización:** 2025-11-07 15:44  
**Total de archivos:** 27 datasets listos  
**Total de datos:** ~40,000 observaciones históricas  
**Estado:** ✅ **LISTO PARA ENTRENAR IA**

---

## 🚀 **¡A ENTRENAR!**

¿Quieres que ahora te muestre cómo entrenar el primer modelo LSTM con estos datos?


**Fecha:** 2025-11-07  
**Proyecto:** Bot Predictivo de Impacto de Noticias en Mercados USA

---

## ✅ RESUMEN EJECUTIVO

### **¡TIENES TODO LO NECESARIO PARA ENTRENAR TU IA!**

✅ **25 años de datos económicos** (2000-2025)  
✅ **10 años de datos de mercado** (2015-2025)  
✅ **17 series económicas** + **4 índices bursátiles**  
✅ **40,000+ observaciones históricas**  
✅ **Todos los datos listos y procesados**

---

## 📊 DATOS RECOLECTADOS

### 1️⃣ **DATOS ECONÓMICOS** (17 series) ✅

#### **A. Indicadores Macro USA** (3 series)
| Serie | Descripción | Último Valor | Observaciones |
|-------|-------------|--------------|---------------|
| GDPC1 | PIB Real | $23.77T | 102 (trimestral) |
| UNRATE | Tasa de Desempleo | 4.3% | 308 (mensual) |
| CPIAUCSL | Inflación CPI | 324.37 | 309 (mensual) |

#### **B. Mercados Financieros** (2 series)
| Serie | Descripción | Último Valor | Observaciones |
|-------|-------------|--------------|---------------|
| VIXCLS | Volatilidad VIX | 19.5 | 6,744 (diaria) |
| DGS10 | Tesoro 10 años | 4.17% | 6,743 (diaria) |

#### **C. Tipos de Cambio** (7 series)
- **Real:** Euro, Japón, Hong Kong, Australia, China (309 obs c/u)
- **Spot:** USD/EUR (6,740 obs), Índice Dólar (238 obs)

#### **D. Petróleo** (5 series)
| Serie | Descripción | Último Valor | Observaciones |
|-------|-------------|--------------|---------------|
| DCOILWTICO | WTI (Diario) | **$61.79/barril** | 6,741 |
| DCOILBRENTEU | Brent (Diario) | **$65.79/barril** | 6,741 |
| MCOILWTICO | WTI Mensual | $60.89/barril | 310 |
| GASREGW | Gasolina USA | **$3.02/galón** | 1,349 (semanal) |
| GASDESW | Diesel USA | **$3.75/galón** | 1,349 (semanal) |

---

### 2️⃣ **DATOS DE MERCADO** (4 índices) ✅

#### **Índices Principales - 10 años de historia (2015-2025)**

| Índice | Nombre | Precio Actual | Retorno Total | Volatilidad | Días |
|--------|--------|---------------|---------------|-------------|------|
| **SPY** | S&P 500 ETF | **$669.32** | +279.78% | 18.06% | 2,514 |
| **QQQ** | NASDAQ 100 | **$607.66** | +477.76% | 22.37% | 2,514 |
| **DIA** | Dow Jones | **$469.54** | +223.41% | 17.62% | 2,514 |
| **IWM** | Russell 2000 | **$241.12** | +132.51% | 23.03% | 2,514 |

**🎯 Todos incluyen:**
- ✅ Precios OHLC (Open, High, Low, Close)
- ✅ Volumen
- ✅ Dividendos
- ✅ Indicadores técnicos (SMA, RSI, Bollinger Bands)
- ✅ Retornos diarios
- ✅ Volatilidad histórica

---

### 3️⃣ **DATOS DE GAS NATURAL** (EIA) ⚠️

**Estado:** Requiere API Key de EIA  
**Link para obtener key:** https://www.eia.gov/opendata/register.php  
**Nota:** Es GRATIS y toma 2 minutos registrarse

---

## 📁 ARCHIVOS GENERADOS (27 archivos)

### **Datos Económicos** (12 archivos)
```
data/processed/fred/
├── fred_completo_*.csv                    # TODAS las series económicas
├── fred_alto_impacto_*.csv               # ⭐ MÁS IMPORTANTES (8 series)
├── fred_diario_*.csv                     # Solo datos diarios
├── indicadores_economicos_usa_*.csv      # PIB, Desempleo, CPI
├── mercados_financieros_*.csv            # VIX, Tesoro
├── tipos_cambio_real_*.csv               # Monedas ajustadas
├── tipos_cambio_spot_*.csv               # USD/EUR, Índice
└── metadata_*.json                       # INFO DETALLADA

data/processed/fred_oil/
├── fred_oil_completo_*.csv               # Todas series petróleo
├── fred_oil_precios_*.csv                # ⭐ WTI + Brent
├── fred_oil_alto_impacto_*.csv          # Más importantes
└── fred_oil_metadata_*.json             # INFO DETALLADA
```

### **Datos de Mercado** (7 archivos)
```
data/processed/market/
├── indices_combinados_*.csv              # ⭐ TODOS los índices juntos
├── indices_precios_*.csv                 # Solo precios de cierre
├── indices_retornos_*.csv                # Retornos diarios
├── SPY_indicadores_*.csv                 # ⭐ S&P 500 completo
├── QQQ_indicadores_*.csv                 # NASDAQ completo
├── DIA_indicadores_*.csv                 # Dow Jones completo
└── IWM_indicadores_*.csv                 # Russell 2000 completo
```

---

## 🎯 DATASETS RECOMENDADOS PARA ENTRENAR

### **OPCIÓN 1: Dataset Simple** (Para empezar)

```python
import pandas as pd

# Cargar económicos + mercado
df_eco = pd.read_csv('data/processed/fred/fred_alto_impacto_20251107_151424.csv', 
                     index_col=0, parse_dates=True)

df_market = pd.read_csv('data/processed/market/indices_precios_20251107.csv',
                        index_col=0, parse_dates=True)

# Combinar (alineados por fecha)
df_completo = pd.merge(df_eco, df_market, left_index=True, right_index=True, how='inner')

print(f"Dataset final: {df_completo.shape}")
# Resultado: ~2,500 días × 12 columnas (8 económicas + 4 mercado)
```

### **OPCIÓN 2: Dataset Completo con Indicadores** (Recomendado)

```python
# Cargar S&P 500 con todos los indicadores técnicos
df_spy = pd.read_csv('data/processed/market/SPY_indicadores_20251107.csv',
                     index_col=0, parse_dates=True)

# Cargar datos de petróleo
df_oil = pd.read_csv('data/processed/fred_oil/fred_oil_precios_20251107.csv',
                     index_col=0, parse_dates=True)

# Ya tienes:
# - Precios SPY
# - Indicadores técnicos (SMA, RSI, Bollinger)
# - Precios de petróleo WTI y Brent
```

### **OPCIÓN 3: Todo Combinado** (Profesional)

```python
# Económicos
df_eco = pd.read_csv('data/processed/fred/fred_completo_20251107_151424.csv', 
                     index_col=0, parse_dates=True)

# Petróleo
df_oil = pd.read_csv('data/processed/fred_oil/fred_oil_completo_20251107.csv',
                     index_col=0, parse_dates=True)

# Mercado
df_market = pd.read_csv('data/processed/market/indices_combinados_20251107.csv',
                        index_col=0, parse_dates=True)

# Combinar todo
df_total = df_eco.join([df_oil, df_market], how='outer')

print(f"MEGA Dataset: {df_total.shape}")
# Resultado: 6,833 días × 29 columnas
```

---

## 📊 ANÁLISIS QUE PUEDES HACER

### **1. Correlaciones**
```python
# ¿Cómo se relaciona el petróleo con el S&P 500?
correlation = df_oil['DCOILWTICO'].corr(df_market['SPY'])

# ¿Y el VIX con el mercado?
correlation_vix = df_eco['VIXCLS'].corr(df_market['SPY'])
```

### **2. Impacto de Eventos**
```python
# Encontrar días con alta volatilidad
high_vol_days = df_spy[df_spy['Volatility'] > df_spy['Volatility'].quantile(0.95)]

# Ver qué pasó en economía esos días
eventos = df_eco.loc[high_vol_days.index]
```

### **3. Predicción de Movimientos**
```python
# Entrenar LSTM para predecir próximo día del S&P 500
# usando datos económicos y de petróleo como features
```

---

## 🤖 CÓMO ENTRENAR TU IA

### **PASO 1: Preparar Datos**

```python
# Script ya creado: src/training/preparar_datos.py
# Ejecutar: py src/training/preparar_datos.py

# Lo que hace:
# 1. Carga datos económicos + mercado
# 2. Calcula features adicionales (medias móviles, volatilidad)
# 3. Crea secuencias temporales para LSTM
# 4. Divide en train/validation/test
```

### **PASO 2: Entrenar Modelo LSTM**

```python
# Script ya creado: src/training/entrenar_lstm.py
# Ejecutar: py src/training/entrenar_lstm.py

# Lo que hace:
# 1. Crea arquitectura LSTM
# 2. Entrena con datos históricos
# 3. Valida y evalúa
# 4. Guarda modelo entrenado
```

### **PASO 3: Hacer Predicciones**

```python
from tensorflow.keras.models import load_model

# Cargar modelo entrenado
model = load_model('data/models/lstm_predictor_vix.h5')

# Hacer predicción
prediction = model.predict(X_new)
```

---

## 📈 ESTADÍSTICAS CLAVE

### **Datos Económicos:**
- **Período:** 2000-2025 (25 años)
- **Series:** 17
- **Observaciones:** ~22,000
- **Eventos incluidos:**
  - 💥 Crisis 2008
  - 💶 Crisis Europa 2011
  - 🛢️ Crash petróleo 2014-2016
  - 🦠 COVID-19 2020
  - 📈 Recuperación 2021-2023
  - 🔥 Inflación 2022-2023

### **Datos de Mercado:**
- **Período:** 2015-2025 (10 años)
- **Índices:** 4 principales
- **Días:** 2,514 por índice
- **Retorno S&P 500:** +279.78% (¡increíble!)
- **Retorno NASDAQ:** +477.76% (¡casi 5x!)

---

## 🎓 PRÓXIMOS PASOS SUGERIDOS

### **HOY (Si tienes tiempo):**
1. ✅ Revisar los archivos CSV generados
2. ✅ Explorar correlaciones básicas
3. ✅ Visualizar datos en gráficas

### **ESTA SEMANA:**
1. 🤖 Ejecutar `preparar_datos.py` para crear features
2. 🧠 Entrenar primer modelo LSTM
3. 📊 Evaluar predicciones
4. 📈 Backtesting básico

### **PRÓXIMAS SEMANAS:**
1. 📰 Recolectar noticias históricas
2. 🤖 Análisis de sentimiento (BERT/FinBERT)
3. 🎯 Modelo completo: Datos + Noticias → Predicción
4. 🚀 Desplegar en producción

---

## 🔑 API KEYS NECESARIAS

### **Ya tienes:**
✅ **FRED API:** `f6f6d63126fb06361b568e076cb4f7ee` (funcionando)

### **Para obtener (opcional):**
- **EIA (Gas Natural):** https://www.eia.gov/opendata/register.php (GRATIS)
- **News API:** https://newsapi.org/register (GRATIS, 100 req/día)
- **Alpha Vantage:** https://www.alphavantage.co/support/#api-key (GRATIS)

---

## 💡 EJEMPLO RÁPIDO DE USO

```python
import pandas as pd
import matplotlib.pyplot as plt

# 1. Cargar datos
df_spy = pd.read_csv('data/processed/market/SPY_indicadores_20251107.csv',
                     index_col=0, parse_dates=True)

df_oil = pd.read_csv('data/processed/fred_oil/fred_oil_precios_20251107.csv',
                     index_col=0, parse_dates=True)

# 2. Analizar correlación
# Alinear fechas
df_combined = pd.merge(df_spy[['Close']], df_oil['DCOILWTICO'], 
                      left_index=True, right_index=True, how='inner')

correlation = df_combined.corr()
print(f"Correlación S&P 500 vs Petróleo WTI: {correlation.iloc[0,1]:.3f}")

# 3. Visualizar
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(df_spy.index, df_spy['Close'], label='S&P 500')
ax1.set_title('S&P 500 - Últimos 10 años')
ax1.legend()
ax1.grid(True)

ax2.plot(df_oil.index, df_oil['DCOILWTICO'], label='Petróleo WTI', color='orange')
ax2.set_title('Petróleo WTI')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('analisis_sp500_petroleo.png')
print("✓ Gráfica guardada: analisis_sp500_petroleo.png")
```

---

## 🎉 ¡ESTÁS LISTO!

### **Tienes TODO lo necesario:**
- ✅ 25 años de datos económicos
- ✅ 10 años de datos de mercado
- ✅ Precios de petróleo (crítico para mercados)
- ✅ Datos procesados y listos
- ✅ Scripts de entrenamiento preparados
- ✅ Estructura profesional del proyecto

### **Puedes entrenar modelos para predecir:**
1. 📈 Movimientos del S&P 500
2. 😨 Cambios en volatilidad (VIX)
3. 🛢️ Impacto del petróleo en mercados
4. 💰 Efectos de inflación en acciones
5. 📊 Y mucho más...

---

## 📞 COMANDOS ÚTILES

```bash
# Ver estructura de archivos
tree data/processed/

# Explorar datos en Python
py
>>> import pandas as pd
>>> df = pd.read_csv('data/processed/fred/fred_alto_impacto_20251107_151424.csv', index_col=0, parse_dates=True)
>>> df.head()
>>> df.describe()

# Ver correlaciones
>>> df.corr()

# Entrenar modelo (cuando estés listo)
py src/training/preparar_datos.py
py src/training/entrenar_lstm.py
```

---

**Última actualización:** 2025-11-07 15:44  
**Total de archivos:** 27 datasets listos  
**Total de datos:** ~40,000 observaciones históricas  
**Estado:** ✅ **LISTO PARA ENTRENAR IA**

---

## 🚀 **¡A ENTRENAR!**

¿Quieres que ahora te muestre cómo entrenar el primer modelo LSTM con estos datos?



