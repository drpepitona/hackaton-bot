# 📊 ANÁLISIS AVANZADO DE TOKENS - VOLATILIDAD REAL

## Metodología

**Token = Medida de volatilidad inducida por la noticia**

```
Volatilidad = |Precio_Close - Precio_Open| / Precio_Open
Token = 1.0 + (Volatilidad_Promedio / Volatilidad_Máxima) × 9.0
```

## 🎯 TOKENS POR ASSET

### SPY (S&P 500)

| Categoría | Token | Vol Avg | Vol Max | Sesgo | ↑ | ↓ |
|-----------|-------|---------|---------|-------|---|---|
| ecb_policy           | 10.00 |  0.97% |  3.34% | BAJISTA | 30% | 70% |
| us_gdp_data          |  9.49 |  0.92% |  7.97% | ALCISTA | 64% | 36% |
| financial_crisis     |  8.10 |  0.77% |  7.97% | NEUTRAL | 56% | 44% |
| terrorism            |  7.44 |  0.70% |  8.99% | NEUTRAL | 54% | 46% |
| gold_demand          |  7.40 |  0.69% |  8.99% | NEUTRAL | 54% | 46% |
| war_middle_east      |  7.28 |  0.68% |  8.99% | NEUTRAL | 54% | 46% |
| us_inflation_data    |  7.19 |  0.67% |  1.86% | ALCISTA | 65% | 35% |
| oil_supply           |  7.07 |  0.66% |  3.55% | BAJISTA | 36% | 64% |
| war_russia           |  7.04 |  0.65% |  8.99% | NEUTRAL | 53% | 47% |
| debt_crisis          |  7.02 |  0.65% |  6.51% | NEUTRAL | 54% | 46% |
| elections_global     |  6.88 |  0.64% |  7.63% | NEUTRAL | 56% | 44% |
| trade_general        |  6.76 |  0.62% |  7.97% | NEUTRAL | 54% | 46% |
| elections_us         |  6.69 |  0.62% |  7.63% | NEUTRAL | 54% | 46% |
| brexit               |  6.64 |  0.61% |  0.99% | NEUTRAL | 50% | 50% |
| us_employment_data   |  5.95 |  0.54% |  3.98% | NEUTRAL | 56% | 44% |

### QQQ (S&P 500)

| Categoría | Token | Vol Avg | Vol Max | Sesgo | ↑ | ↓ |
|-----------|-------|---------|---------|-------|---|---|
| brexit               | 10.00 |  0.86% |  1.33% | NEUTRAL | 50% | 50% |
| financial_crisis     |  9.54 |  0.81% |  3.84% | NEUTRAL | 42% | 58% |
| us_employment_data   |  8.25 |  0.69% |  1.71% | NEUTRAL | 59% | 41% |
| debt_crisis          |  8.14 |  0.68% |  2.23% | NEUTRAL | 54% | 46% |
| war_russia           |  7.94 |  0.66% |  3.84% | NEUTRAL | 50% | 50% |
| war_middle_east      |  7.84 |  0.65% |  3.84% | NEUTRAL | 53% | 47% |
| terrorism            |  7.71 |  0.64% |  3.84% | NEUTRAL | 54% | 46% |
| elections_us         |  7.66 |  0.64% |  1.96% | NEUTRAL | 49% | 51% |
| gold_demand          |  7.63 |  0.63% |  3.84% | NEUTRAL | 59% | 41% |
| fed_rates            |  7.39 |  0.61% |  3.84% | BAJISTA | 39% | 61% |
| elections_global     |  7.26 |  0.60% |  2.03% | NEUTRAL | 51% | 49% |
| trade_general        |  6.55 |  0.53% |  2.03% | NEUTRAL | 59% | 41% |

### DIA (S&P 500)

| Categoría | Token | Vol Avg | Vol Max | Sesgo | ↑ | ↓ |
|-----------|-------|---------|---------|-------|---|---|
| gold_demand          | 10.00 |  0.57% |  2.53% | NEUTRAL | 59% | 41% |
| brexit               |  9.89 |  0.56% |  0.84% | NEUTRAL | 50% | 50% |
| financial_crisis     |  9.86 |  0.56% |  2.53% | NEUTRAL | 50% | 50% |
| debt_crisis          |  9.12 |  0.52% |  1.64% | NEUTRAL | 46% | 54% |
| terrorism            |  9.09 |  0.51% |  2.53% | NEUTRAL | 54% | 46% |
| elections_us         |  9.07 |  0.51% |  1.71% | NEUTRAL | 51% | 49% |
| us_employment_data   |  8.88 |  0.50% |  0.89% | ALCISTA | 73% | 27% |
| war_middle_east      |  8.87 |  0.50% |  2.53% | NEUTRAL | 54% | 46% |
| elections_global     |  8.84 |  0.50% |  1.81% | NEUTRAL | 48% | 52% |
| war_russia           |  8.75 |  0.49% |  2.53% | NEUTRAL | 52% | 48% |
| trade_general        |  8.47 |  0.47% |  1.81% | NEUTRAL | 57% | 43% |
| fed_rates            |  7.70 |  0.43% |  2.53% | NEUTRAL | 54% | 46% |

### IWM (S&P 500)

| Categoría | Token | Vol Avg | Vol Max | Sesgo | ↑ | ↓ |
|-----------|-------|---------|---------|-------|---|---|
| brexit               | 10.00 |  1.18% |  2.14% | NEUTRAL | 60% | 40% |
| financial_crisis     |  8.08 |  0.93% |  3.40% | NEUTRAL | 42% | 58% |
| gold_demand          |  7.56 |  0.86% |  3.40% | NEUTRAL | 59% | 41% |
| us_employment_data   |  7.49 |  0.85% |  2.28% | NEUTRAL | 59% | 41% |
| fed_rates            |  7.41 |  0.84% |  3.40% | NEUTRAL | 46% | 54% |
| war_russia           |  7.31 |  0.82% |  3.40% | NEUTRAL | 48% | 52% |
| elections_us         |  7.18 |  0.81% |  3.05% | NEUTRAL | 50% | 50% |
| war_middle_east      |  7.04 |  0.79% |  3.40% | NEUTRAL | 50% | 50% |
| debt_crisis          |  7.04 |  0.79% |  2.00% | NEUTRAL | 57% | 43% |
| terrorism            |  6.79 |  0.76% |  3.40% | NEUTRAL | 51% | 49% |
| elections_global     |  6.47 |  0.72% |  2.14% | NEUTRAL | 48% | 52% |
| trade_general        |  6.36 |  0.70% |  2.14% | NEUTRAL | 59% | 41% |

## 🔗 IMPACTO CRUZADO

**Cómo cada categoría afecta diferentes assets:**

### us_employment_data

- **IWM**: 0.794% volatilidad
- **QQQ**: 0.715% volatilidad
- **SPY**: 0.499% volatilidad
- **DIA**: 0.469% volatilidad

### oil_shock

- **IWM**: 0.778% volatilidad
- **SPY**: 0.672% volatilidad
- **QQQ**: 0.634% volatilidad
- **DIA**: 0.465% volatilidad

### financial_crisis

- **IWM**: 0.795% volatilidad
- **SPY**: 0.761% volatilidad
- **QQQ**: 0.664% volatilidad
- **DIA**: 0.510% volatilidad

### fed_rates

- **IWM**: 0.944% volatilidad
- **QQQ**: 0.671% volatilidad
- **SPY**: 0.548% volatilidad
- **DIA**: 0.485% volatilidad
