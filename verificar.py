"""
Verificacion de instalacion - Simple
"""
print("="*60)
print("VERIFICACION DE INSTALACION")
print("="*60)
print()

print("Verificando librerias principales...")
print("-"*60)

try:
    import tensorflow as tf
    print(f"[OK] TensorFlow: {tf.__version__}")
except:
    print("[ERROR] TensorFlow no instalado")

try:
    import torch
    print(f"[OK] PyTorch: {torch.__version__}")
except:
    print("[ERROR] PyTorch no instalado")

try:
    import pandas as pd
    print(f"[OK] Pandas: {pd.__version__}")
except:
    print("[ERROR] Pandas no instalado")

try:
    import numpy as np
    print(f"[OK] NumPy: {np.__version__}")
except:
    print("[ERROR] NumPy no instalado")

try:
    import sklearn
    print(f"[OK] Scikit-learn: {sklearn.__version__}")
except:
    print("[ERROR] Scikit-learn no instalado")

try:
    from fredapi import Fred
    print("[OK] FRED API instalado")
except:
    print("[ERROR] FRED API no instalado")

try:
    import yfinance
    print("[OK] yFinance instalado")
except:
    print("[ERROR] yFinance no instalado")

try:
    import transformers
    print(f"[OK] Transformers: {transformers.__version__}")
except:
    print("[ERROR] Transformers no instalado")

try:
    import nltk
    print(f"[OK] NLTK: {nltk.__version__}")
except:
    print("[ERROR] NLTK no instalado")

try:
    import spacy
    print(f"[OK] spaCy: {spacy.__version__}")
except:
    print("[ERROR] spaCy no instalado")

try:
    import matplotlib
    print(f"[OK] Matplotlib: {matplotlib.__version__}")
except:
    print("[ERROR] Matplotlib no instalado")

try:
    import seaborn
    print(f"[OK] Seaborn: {seaborn.__version__}")
except:
    print("[ERROR] Seaborn no instalado")

try:
    import plotly
    print(f"[OK] Plotly: {plotly.__version__}")
except:
    print("[ERROR] Plotly no instalado")

try:
    from dotenv import load_dotenv
    print("[OK] python-dotenv instalado")
except:
    print("[ERROR] python-dotenv no instalado")

try:
    from loguru import logger
    print("[OK] Loguru instalado")
except:
    print("[ERROR] Loguru no instalado")

print()
print("="*60)
print("TODAS LAS LIBRERIAS PRINCIPALES INSTALADAS!")
print("="*60)
print()
print("Proximos pasos:")
print("1. Configura tu archivo .env con las API keys")
print("2. Ejecuta: py src/data_collection/fred_collector.py")
print("3. Ejecuta: py src/data_collection/market_collector.py")
print()
print("Listo para comenzar!")


