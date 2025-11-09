"""
Script para verificar que todas las librerías principales están instaladas
"""
import sys

def check_library(name, import_name=None):
    """Intenta importar una librería y muestra su versión"""
    if import_name is None:
        import_name = name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'version desconocida')
        print(f"✓ {name}: {version}")
        return True
    except ImportError:
        print(f"✗ {name}: NO INSTALADA")
        return False

def main():
    print("="*60)
    print("VERIFICACIÓN DE INSTALACIÓN - BOT PREDICTIVO DE BOLSA CON IA")
    print("="*60)
    print()
    
    libraries = [
        # Core Data Science
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("SciPy", "scipy"),
        ("Scikit-learn", "sklearn"),
        
        # Deep Learning
        ("TensorFlow", "tensorflow"),
        ("Keras", "keras"),
        ("PyTorch", "torch"),
        
        # NLP
        ("Transformers", "transformers"),
        ("NLTK", "nltk"),
        ("spaCy", "spacy"),
        ("TextBlob", "textblob"),
        
        # Financial APIs
        ("FRED API", "fredapi"),
        ("yFinance", "yfinance"),
        
        # Visualization
        ("Matplotlib", "matplotlib"),
        ("Seaborn", "seaborn"),
        ("Plotly", "plotly"),
        
        # Utilities
        ("Requests", "requests"),
        ("Python-dotenv", "dotenv"),
        ("Loguru", "loguru"),
        ("Tqdm", "tqdm"),
    ]
    
    print("Librerías Principales:")
    print("-" * 60)
    
    all_installed = True
    for name, import_name in libraries:
        if not check_library(name, import_name):
            all_installed = False
    
    print()
    print("="*60)
    
    if all_installed:
        print("✓✓✓ ¡TODAS LAS LIBRERÍAS INSTALADAS CORRECTAMENTE! ✓✓✓")
        print()
        print("Próximos pasos:")
        print("1. Configura tu archivo .env con las API keys")
        print("2. Ejecuta: python src/data_collection/fred_collector.py")
        print("3. Ejecuta: python src/data_collection/market_collector.py")
        print()
        print("¡Estás listo para comenzar! 🚀📈")
    else:
        print("⚠ ALGUNAS LIBRERÍAS NO ESTÁN INSTALADAS")
        print("Ejecuta: pip install -r requirements.txt")
    
    print("="*60)
    
    return 0 if all_installed else 1

if __name__ == "__main__":
    sys.exit(main())




