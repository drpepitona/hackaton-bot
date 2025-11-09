"""Test del filtro de relevancia con alfa y beta"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from bot_gemini_completo import BotGeminiCompleto
from src.utils.logger import logger

def main():
    logger.info("="*70)
    logger.info("TEST: FILTRO DE RELEVANCIA + MODELO ALFA/BETA")
    logger.info("="*70)
    
    bot = BotGeminiCompleto()
    
    # Mix de preguntas relevantes e irrelevantes
    preguntas_test = [
        ("¿Cómo afectaría al mercado de EEUU un ataque de China a Taiwán?", 30),  # RELEVANTE
        ("¿Cómo afectaría la muerte de mi mascota doméstica al mercado?", 20),    # IRRELEVANTE
        ("¿Qué pasa si la Fed sube tasas en 0.5%?", 25),                         # RELEVANTE
        ("¿Impacto de que Taylor Swift cancele un concierto?", 20),              # IRRELEVANTE (probablemente)
        ("¿Caída del 40% de la bolsa china?", 35),                               # RELEVANTE
    ]
    
    print("\n" + "="*70)
    print("PROBANDO FILTRO DE RELEVANCIA")
    print("="*70)
    
    for i, (pregunta, vix) in enumerate(preguntas_test, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(preguntas_test)}")
        print(f"{'='*70}")
        print(f"PREGUNTA: {pregunta}")
        print(f"VIX: {vix}")
        print(f"{'-'*70}")
        
        # Analizar
        analisis = bot.analizar_completo(pregunta, vix)
        
        # Guardar en archivo
        filename = f"test_relevancia_{i}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(analisis)
        
        print(f"\n> Analisis guardado en: {filename}")
        if "IRRELEVANTE" in analisis:
            print("  >> FILTRADA: Pregunta irrelevante para mercados")
        else:
            print("  >> PROCESADA: Analisis completo con alfa/beta")
        print("")

if __name__ == "__main__":
    main()

