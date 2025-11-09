from fredapi import Fred
from dotenv import load_dotenv
import os

load_dotenv()

api_key = "f6f6d63126fb06361b568e076cb4f7ee"

print("Probando FRED API...")
print(f"API Key: {api_key[:10]}...")

fred = Fred(api_key=api_key)
data = fred.get_series('UNRATE')

print(f"\nDatos obtenidos: {len(data)} observaciones")
print(f"Periodo: {data.index.min()} a {data.index.max()}")
print(f"\nUltimos 5 valores:")
print(data.tail())
print(f"\nUltima tasa de desempleo: {data.iloc[-1]:.1f}%")
print("\n¡API funcionando correctamente!")




