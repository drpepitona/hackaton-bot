"""
BOT CON GEMINI API - GRATIS Y POTENTE
Usa tus tokens + datos como contexto
No necesita fine-tuning
"""
import os
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))

from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger

# API Key de Gemini (gratis)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class BotGemini:
    """Bot con Gemini API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = None
        self.df_tokens = None
        
        self._cargar_tokens()
        self._inicializar_gemini()
    
    def _cargar_tokens(self):
        """Carga tus tokens"""
        token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
        self.df_tokens = pd.read_csv(token_files[0])
        logger.info(f"✓ Tokens cargados: {len(self.df_tokens)}")
    
    def _inicializar_gemini(self):
        """Inicializa Gemini"""
        if not self.api_key:
            logger.warning("⚠ GEMINI_API_KEY no configurado")
            logger.info("\nConfigura:")
            logger.info("  1. Ve a: https://aistudio.google.com/app/apikey")
            logger.info("  2. Crea API key (GRATIS)")
            logger.info("  3. En PowerShell: $env:GEMINI_API_KEY='tu-key'")
            return False
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            
            # Listar modelos disponibles
            modelos = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if len(modelos) > 0:
                # Usar el primer modelo disponible
                modelo_nombre = modelos[0].name
                self.model = genai.GenerativeModel(modelo_nombre)
                logger.info(f"✓ Gemini API inicializado: {modelo_nombre}")
                return True
            
            logger.warning("No se encontró modelo disponible")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            logger.info("\nInstala: py -m pip install google-generativeai")
            return False
    
    def clasificar(self, pregunta):
        """Clasifica pregunta"""
        texto = pregunta.lower()
        if any(k in texto for k in ['fed', 'tasa', 'interest']): return 'fed_rates'
        if any(k in texto for k in ['terror', 'ataque']): return 'terrorism'
        if any(k in texto for k in ['guerra', 'war', 'russia']): return 'war_russia'
        if any(k in texto for k in ['crisis', 'colapso']): return 'financial_crisis'
        if any(k in texto for k in ['ecb', 'bce']): return 'ecb_policy'
        if any(k in texto for k in ['petroleo', 'oil']): return 'oil_supply'
        if any(k in texto for k in ['oro', 'gold']): return 'gold_demand'
        return 'other'
    
    def analizar(self, pregunta, vix=20):
        """Analiza con Gemini"""
        # Clasificar
        categoria = self.clasificar(pregunta)
        
        # Buscar token
        token_data = self.df_tokens[
            (self.df_tokens['categoria'] == categoria) & 
            (self.df_tokens['asset'] == 'SPY')
        ]
        
        if len(token_data) == 0:
            token = 5.0
            num_eventos = 0
            volatilidad = 0.5
            pct_alcista = 50
        else:
            row = token_data.iloc[0]
            token = row['token']
            num_eventos = row['num_eventos']
            volatilidad = row['volatilidad_promedio'] * 100
            pct_alcista = row['pct_alcista']
        
        # Construir prompt CON TUS DATOS
        prompt = f"""Eres un experto en análisis financiero.

PREGUNTA DEL USUARIO:
{pregunta}

DATOS DEL MODELO (basados en 123,326 noticias históricas):
• Categoría detectada: {categoria}
• Token de impacto: {token:.1f}/10
• Eventos históricos similares: {num_eventos}
• Volatilidad típica: {volatilidad:.2f}%
• Tendencia histórica: {pct_alcista:.0f}% alcistas, {100-pct_alcista:.0f}% bajistas

CONTEXTO ACTUAL:
• VIX (miedo del mercado): {vix}
• Estado: {'PÁNICO' if vix > 30 else 'NERVIOSO' if vix > 20 else 'NORMAL'}

INSTRUCCIONES:
1. Analiza el impacto usando los datos del modelo
2. Considera el VIX (mercado nervioso amplifica impacto)
3. Da probabilidad (0-100%), dirección (ALCISTA/BAJISTA/NEUTRAL), magnitud
4. Explica tu razonamiento
5. Da recomendación práctica

Genera un análisis profesional en español (máx 300 palabras)."""

        # Llamar a Gemini
        if not self.model:
            return self._respuesta_sin_gemini(categoria, token, num_eventos, volatilidad, pct_alcista, vix)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            return self._respuesta_sin_gemini(categoria, token, num_eventos, volatilidad, pct_alcista, vix)
    
    def _respuesta_sin_gemini(self, categoria, token, num_eventos, volatilidad, pct_alcista, vix):
        """Respuesta si Gemini no está disponible"""
        prob_base = (token / 10.0) * 100
        prob_final = prob_base * (1.3 if vix > 30 else 1.15 if vix > 20 else 1.0)
        prob_final = min(100, prob_final)
        
        return f"""
ANÁLISIS PREDICTIVO

CATEGORÍA: {categoria}
TOKEN: {token:.1f}/10 (basado en {num_eventos} eventos)
VOLATILIDAD: {volatilidad:.2f}%

PREDICCIÓN:
• Probabilidad: {prob_final:.0f}%
• Dirección: {'BAJISTA' if pct_alcista < 45 else 'ALCISTA' if pct_alcista > 55 else 'NEUTRAL'}
• Magnitud estimada: ±{volatilidad:.2f}%

CON VIX {vix}:
El mercado está {'en PÁNICO - efecto polvorín activo' if vix > 30 else 'NERVIOSO - impacto amplificado' if vix > 20 else 'NORMAL'}.

RECOMENDACIÓN:
{'OPERAR (alta probabilidad)' if prob_final >= 70 else 'MONITOREAR (probabilidad moderada)' if prob_final >= 50 else 'MANTENER (baja probabilidad)'}

(Para análisis más detallado, configura GEMINI_API_KEY)
"""


def main():
    """Demo"""
    bot = BotGemini()
    
    if not bot.model:
        logger.info("\n⚠ Gemini no configurado - usando respuestas básicas")
        logger.info("Para mejores respuestas:")
        logger.info("  1. Ve a: https://aistudio.google.com/app/apikey")
        logger.info("  2. Crea key (GRATIS)")
        logger.info("  3. $env:GEMINI_API_KEY='tu-key'")
        logger.info("")
    
    preguntas = [
        ("Que pasa si la Fed sube tasas?", 35),
        ("Como afecta un ataque terrorista?", 25),
    ]
    
    for pregunta, vix in preguntas:
        print("\n" + "="*70)
        print(f"PREGUNTA: {pregunta} (VIX {vix})")
        print("="*70)
        
        respuesta = bot.analizar(pregunta, vix)
        print(respuesta)


if __name__ == "__main__":
    main()

