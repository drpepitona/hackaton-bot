"""
Script de Inicio Rápido - Bot Predictivo de Bolsa
Ejecuta este script para verificar que todo está configurado correctamente
"""
import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60 + "\n")

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("   ✓ Versión correcta (3.9+)")
        return True
    else:
        print("   ✗ Se requiere Python 3.9 o superior")
        return False

def check_libraries():
    """Verifica librerías principales"""
    print("\n📚 Verificando librerías principales...")
    
    required_libs = {
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'tensorflow': 'TensorFlow',
        'torch': 'PyTorch',
        'sklearn': 'Scikit-learn',
        'fredapi': 'FRED API',
        'yfinance': 'yFinance',
    }
    
    all_installed = True
    for module, name in required_libs.items():
        try:
            __import__(module)
            print(f"   ✓ {name}")
        except ImportError:
            print(f"   ✗ {name} - NO INSTALADA")
            all_installed = False
    
    if not all_installed:
        print("\n   ⚠ Ejecuta: pip install -r requirements.txt")
    
    return all_installed

def check_env_file():
    """Verifica archivo .env"""
    print("\n🔑 Verificando configuración (.env)...")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("   ✗ Archivo .env no encontrado")
        print("\n   Crea un archivo .env con tus API keys:")
        print("   ")
        print("   FRED_API_KEY=tu_api_key_aqui")
        print("   ALPHA_VANTAGE_API_KEY=tu_api_key_aqui")
        print("   NEWS_API_KEY=tu_api_key_aqui")
        return False
    
    print("   ✓ Archivo .env encontrado")
    
    # Verificar que tenga contenido
    with open(env_path) as f:
        content = f.read()
        if 'FRED_API_KEY' in content:
            print("   ✓ FRED_API_KEY configurada")
        else:
            print("   ⚠ FRED_API_KEY no encontrada")
    
    return True

def check_directory_structure():
    """Verifica estructura de directorios"""
    print("\n📁 Verificando estructura de directorios...")
    
    required_dirs = [
        'data/raw',
        'data/processed',
        'data/models',
        'src/data_collection',
        'src/models',
        'notebooks'
    ]
    
    all_exist = True
    for directory in required_dirs:
        path = Path(directory)
        if path.exists():
            print(f"   ✓ {directory}")
        else:
            print(f"   ✗ {directory} - NO EXISTE")
            all_exist = False
    
    return all_exist

def suggest_next_steps():
    """Sugiere próximos pasos"""
    print_header("PRÓXIMOS PASOS")
    
    print("1. 🔑 Obtén tus API Keys:")
    print("   • FRED: https://fred.stlouisfed.org/docs/api/api_key.html")
    print("   • Alpha Vantage: https://www.alphavantage.co/support/#api-key")
    print("   • News API: https://newsapi.org/register")
    
    print("\n2. 📊 Recolecta datos:")
    print("   python src/data_collection/fred_collector.py")
    print("   python src/data_collection/market_collector.py")
    
    print("\n3. 📓 Explora los notebooks:")
    print("   jupyter notebook notebooks/01_exploratory_analysis.ipynb")
    
    print("\n4. 🤖 Entrena tu primer modelo:")
    print("   python src/models/lstm_model.py")
    
    print("\n5. 📖 Lee la documentación:")
    print("   Revisa README.md e install_guide.txt")
    
def main():
    print_header("BOT PREDICTIVO DE BOLSA CON IA")
    print("Quick Start - Verificación de Sistema")
    
    # Verificaciones
    python_ok = check_python_version()
    libs_ok = check_libraries()
    env_ok = check_env_file()
    dirs_ok = check_directory_structure()
    
    # Resumen
    print_header("RESUMEN")
    
    all_ok = python_ok and libs_ok and env_ok and dirs_ok
    
    if all_ok:
        print("✅ ¡TODO LISTO! Tu entorno está configurado correctamente.")
        print("\n🚀 Puedes empezar a trabajar en tu bot predictivo.")
    else:
        print("⚠️  Hay algunos problemas que necesitas resolver:")
        if not python_ok:
            print("   • Actualiza Python a la versión 3.9 o superior")
        if not libs_ok:
            print("   • Instala las librerías: pip install -r requirements.txt")
        if not env_ok:
            print("   • Configura el archivo .env con tus API keys")
        if not dirs_ok:
            print("   • La estructura de directorios está incompleta")
    
    # Sugerir próximos pasos
    suggest_next_steps()
    
    print("\n" + "="*60)
    print("Para más ayuda, consulta README.md o install_guide.txt")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()




