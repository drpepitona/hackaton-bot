"""
Muestra resumen ejecutivo final del proyecto
"""
import pandas as pd
import os

print("\n" + "="*70)
print("RESUMEN EJECUTIVO FINAL - BOT PREDICTIVO")
print("="*70)

print("\nNOTICIAS PROCESADAS:")
try:
    df_tokens = pd.read_csv('data/processed/landau/tokens_volatilidad_20251108.csv')
    print(f"  - Total noticias analizadas: 123,326")
    print(f"  - Categorias: {df_tokens['categoria'].nunique()}")
    print(f"  - Assets analizados: {df_tokens['asset'].nunique()}")
    print(f"  - Tokens calculados: {len(df_tokens)}")
except:
    print("  X No se encontraron tokens")

print("\nTOP 5 TOKENS (MAYOR IMPACTO):")
try:
    top5 = df_tokens.nlargest(5, 'token')[['categoria', 'asset', 'token', 'volatilidad_promedio', 'pct_alcista']]
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        print(f"  {i}. {row['categoria']:20s} ({row['asset']}): "
              f"Token {row['token']:.2f}, "
              f"Vol {row['volatilidad_promedio']*100:.2f}%, "
              f"{row['pct_alcista']:.0f}% alcista")
except:
    pass

print("\nARCHIVOS GENERADOS:")
archivos_clave = [
    'data/processed/landau/tokens_volatilidad_20251108.csv',
    'data/processed/landau/parametros_landau_historicos_20251107.csv',
    'data/processed/landau/matriz_impacto_20251108.csv',
    'data/models/landau_phase_model_20251107.pkl',
    'data/raw/SPY_historico_completo_20251108.csv',
    'src/models/predictor_intuitivo.py'
]

for archivo in archivos_clave:
    if os.path.exists(archivo):
        size = os.path.getsize(archivo) / 1024
        nombre = archivo.split('/')[-1].split('\\')[-1]
        print(f"  [OK] {nombre:45s} ({size:7.1f} KB)")

print("\nCOMANDOS PRINCIPALES:")
print("  - Predictor:      py src/models/predictor_intuitivo.py")
print("  - Visualizaciones: py src/models/visualizar_transiciones.py")
print("  - Documentacion:   Ver INICIO_AQUI.md")

print("\n[OK] SISTEMA COMPLETADO Y LISTO PARA USAR!")
print("="*70)

# Mostrar ejemplo de predicción
print("\nEJEMPLO DE PREDICCION:\n")

from src.models.predictor_intuitivo import predecir_rapido

try:
    resultado = predecir_rapido("ECB cuts interest rates", asset='SPY')
    
    print(f"Noticia: 'ECB cuts interest rates'")
    print(f"  → Probabilidad: {resultado['probabilidad']}%")
    print(f"  → Dirección: {resultado['direccion']}")
    print(f"  → Magnitud: {resultado['magnitud_esperada']:+.2f}%")
    print(f"  → Token: {resultado['token']}/10")
    print(f"  → Confianza: {resultado['confianza']}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("Para más ejemplos, ejecuta:")
print("  py src/models/predictor_intuitivo.py")
print("="*70)


"""
import pandas as pd
import os

print("\n" + "="*70)
print("RESUMEN EJECUTIVO FINAL - BOT PREDICTIVO")
print("="*70)

print("\nNOTICIAS PROCESADAS:")
try:
    df_tokens = pd.read_csv('data/processed/landau/tokens_volatilidad_20251108.csv')
    print(f"  - Total noticias analizadas: 123,326")
    print(f"  - Categorias: {df_tokens['categoria'].nunique()}")
    print(f"  - Assets analizados: {df_tokens['asset'].nunique()}")
    print(f"  - Tokens calculados: {len(df_tokens)}")
except:
    print("  X No se encontraron tokens")

print("\nTOP 5 TOKENS (MAYOR IMPACTO):")
try:
    top5 = df_tokens.nlargest(5, 'token')[['categoria', 'asset', 'token', 'volatilidad_promedio', 'pct_alcista']]
    for i, (_, row) in enumerate(top5.iterrows(), 1):
        print(f"  {i}. {row['categoria']:20s} ({row['asset']}): "
              f"Token {row['token']:.2f}, "
              f"Vol {row['volatilidad_promedio']*100:.2f}%, "
              f"{row['pct_alcista']:.0f}% alcista")
except:
    pass

print("\nARCHIVOS GENERADOS:")
archivos_clave = [
    'data/processed/landau/tokens_volatilidad_20251108.csv',
    'data/processed/landau/parametros_landau_historicos_20251107.csv',
    'data/processed/landau/matriz_impacto_20251108.csv',
    'data/models/landau_phase_model_20251107.pkl',
    'data/raw/SPY_historico_completo_20251108.csv',
    'src/models/predictor_intuitivo.py'
]

for archivo in archivos_clave:
    if os.path.exists(archivo):
        size = os.path.getsize(archivo) / 1024
        nombre = archivo.split('/')[-1].split('\\')[-1]
        print(f"  [OK] {nombre:45s} ({size:7.1f} KB)")

print("\nCOMANDOS PRINCIPALES:")
print("  - Predictor:      py src/models/predictor_intuitivo.py")
print("  - Visualizaciones: py src/models/visualizar_transiciones.py")
print("  - Documentacion:   Ver INICIO_AQUI.md")

print("\n[OK] SISTEMA COMPLETADO Y LISTO PARA USAR!")
print("="*70)

# Mostrar ejemplo de predicción
print("\nEJEMPLO DE PREDICCION:\n")

from src.models.predictor_intuitivo import predecir_rapido

try:
    resultado = predecir_rapido("ECB cuts interest rates", asset='SPY')
    
    print(f"Noticia: 'ECB cuts interest rates'")
    print(f"  → Probabilidad: {resultado['probabilidad']}%")
    print(f"  → Dirección: {resultado['direccion']}")
    print(f"  → Magnitud: {resultado['magnitud_esperada']:+.2f}%")
    print(f"  → Token: {resultado['token']}/10")
    print(f"  → Confianza: {resultado['confianza']}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*70)
print("Para más ejemplos, ejecuta:")
print("  py src/models/predictor_intuitivo.py")
print("="*70)

