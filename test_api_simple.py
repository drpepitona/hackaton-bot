"""Prueba rápida del bot sin necesidad de frontend"""
import requests
import json

API_URL = "http://localhost:8000"

print("="*70)
print("PROBANDO API DEL CHATBOT")
print("="*70)

# 1. Health check
print("\n1. Verificando estado...")
response = requests.get(f"{API_URL}/health")
print(f"   Status: {response.json()}")

# 2. Analizar pregunta
print("\n2. Enviando pregunta...")
pregunta = "Como afecta que la Fed suba las tasas de interes?"
print(f"   Pregunta: {pregunta}")

response = requests.post(
    f"{API_URL}/analyze",
    json={"pregunta": pregunta, "vix": 35}
)

if response.status_code == 200:
    resultado = response.json()
    print("\n" + "="*70)
    print("RESULTADO:")
    print("="*70)
    print(f"\nCategoria: {resultado['categoria']}")
    print(f"Token: {resultado['token']}/10")
    print(f"Eventos: {resultado['num_eventos']}")
    if resultado['alpha']:
        print(f"Alpha: {resultado['alpha']:.3f}")
        print(f"Beta: {resultado['beta']:.3f}")
    print(f"\nAnalisis:\n{resultado['analisis'][:500]}...")
else:
    print(f"Error: {response.status_code}")
    print(response.text)

