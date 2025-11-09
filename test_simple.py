"""
Test simple de FRED API
"""
import sys

print("Test iniciado...", file=sys.stderr)

try:
    from fredapi import Fred
    from dotenv import load_dotenv
    import os
    
    # Cargar .env
    load_dotenv()
    
    # Obtener API key
    api_key = os.getenv('FRED_API_KEY')
    
    # Crear archivo de resultados
    with open('test_results.txt', 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("PRUEBA DE API KEY DE FRED\n")
        f.write("="*60 + "\n\n")
        
        if api_key:
            f.write(f"✓ API Key encontrada: {api_key[:10]}...\n\n")
            
            # Probar FRED
            f.write("Conectando con FRED...\n")
            fred = Fred(api_key=api_key)
            
            # Obtener datos
            f.write("Obteniendo datos de tasa de desempleo (UNRATE)...\n")
            data = fred.get_series('UNRATE')
            
            f.write(f"\n✓✓✓ ¡API KEY VÁLIDA Y FUNCIONANDO! ✓✓✓\n\n")
            f.write(f"Datos obtenidos: {len(data)} observaciones\n")
            f.write(f"Período: {data.index.min()} a {data.index.max()}\n\n")
            f.write("Últimos 5 valores:\n")
            f.write(str(data.tail()) + "\n\n")
            f.write(f"Última tasa de desempleo: {data.iloc[-1]:.1f}%\n\n")
            f.write("="*60 + "\n")
            f.write("🎉 ¡TODO FUNCIONA PERFECTAMENTE! 🎉\n")
            f.write("="*60 + "\n")
        else:
            f.write("✗ API Key no encontrada\n")
    
    print("✓ Test completado. Revisa test_results.txt", file=sys.stderr)
    
except Exception as e:
    with open('test_results.txt', 'w', encoding='utf-8') as f:
        f.write(f"ERROR: {str(e)}\n")
    print(f"✗ Error: {e}", file=sys.stderr)




