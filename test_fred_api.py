"""
Script simple para probar la API key de FRED
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("="*60)
print("PRUEBA DE API KEY DE FRED")
print("="*60)

# Verificar que el archivo .env existe
if os.path.exists('.env'):
    print("\n✓ Archivo .env encontrado")
else:
    print("\n✗ Archivo .env NO encontrado")
    exit(1)

# Obtener API key
api_key = os.getenv('FRED_API_KEY')

if api_key:
    print(f"✓ FRED_API_KEY encontrada: {api_key[:10]}...")
else:
    print("✗ FRED_API_KEY no encontrada en .env")
    exit(1)

# Probar conexión con FRED
print("\n" + "-"*60)
print("Probando conexión con FRED...")
print("-"*60)

try:
    from fredapi import Fred
    fred = Fred(api_key=api_key)
    
    print("\n✓ Librería fredapi importada correctamente")
    print("✓ Objeto Fred creado exitosamente")
    
    # Probar obtener una serie simple
    print("\nObteniendo datos de tasa de desempleo (UNRATE)...")
    data = fred.get_series('UNRATE')
    
    if data is not None and len(data) > 0:
        print(f"\n✓✓✓ ¡API KEY VÁLIDA Y FUNCIONANDO! ✓✓✓")
        print(f"\nDatos obtenidos: {len(data)} observaciones")
        print(f"Período: {data.index.min().strftime('%Y-%m-%d')} a {data.index.max().strftime('%Y-%m-%d')}")
        print(f"\nÚltimos 5 valores de tasa de desempleo:")
        print(data.tail())
        print(f"\nÚltima tasa de desempleo: {data.iloc[-1]:.1f}%")
        
        print("\n" + "="*60)
        print("🎉 ¡TODO FUNCIONA PERFECTAMENTE! 🎉")
        print("="*60)
        print("\nYa puedes empezar a recolectar datos con:")
        print("  python src/data_collection/fred_collector.py")
        print("  python src/data_collection/market_collector.py")
        
    else:
        print("✗ No se obtuvieron datos")
        
except ImportError as e:
    print(f"\n✗ Error de importación: {e}")
    print("Ejecuta: pip install fredapi")
    
except Exception as e:
    print(f"\n✗ Error al conectar con FRED: {e}")
    print("\nPosibles causas:")
    print("  - API key inválida")
    print("  - Problemas de conexión a internet")
    print("  - Servicio de FRED temporalmente no disponible")

print("\n")




