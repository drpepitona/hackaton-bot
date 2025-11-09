"""
SISTEMA FINAL PARA HACKATHON
Todo en uno - funciona LOCAL
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from src.models.predictor_intuitivo import PredictorIntuitivo
from src.utils.logger import logger
import pandas as pd


class SistemaFinalHackathon:
    """Sistema completo para el hackathon"""
    
    def __init__(self):
        self.predictor = PredictorIntuitivo()
        self.df_tokens = self.predictor.df_tokens
        logger.info("✓ Sistema cargado con 123,326 noticias")
    
    def analizar(self, pregunta, vix=20):
        """Analiza una pregunta"""
        # Clasificar
        categoria = self.predictor.clasificar_noticia(pregunta)
        
        # Predecir
        pred = self.predictor.predecir_impacto(pregunta, 'SPY')
        
        # Ajustar por VIX
        prob_base = pred['probabilidad']
        if vix < 20:
            prob_final = prob_base * 0.95
        elif vix > 30:
            prob_final = min(100, prob_base * 1.3)
        else:
            prob_final = prob_base
        
        # Generar respuesta
        respuesta = f"""
═══════════════════════════════════════════════════════════════════════
ANALISIS: {pregunta}
═══════════════════════════════════════════════════════════════════════

CATEGORIA: {categoria}
TOKEN: {pred['token']:.1f}/10
EVENTOS HISTORICOS: {pred['num_eventos_historicos']}

PREDICCION:
  • Probabilidad base: {prob_base:.0f}%
  • Con VIX {vix}: {prob_final:.0f}%
  • Direccion: {pred['direccion']}
  • Magnitud: {pred['magnitud_esperada']*100:+.2f}%

RAZONAMIENTO:
He analizado {pred['num_eventos_historicos']} eventos similares.
El token {pred['token']:.1f}/10 indica impacto {'ALTO' if pred['token'] >= 7 else 'MODERADO'}.
Volatilidad tipica: {pred['volatilidad']:.2f}%

Con VIX {vix} {'(PANICO)' if vix > 30 else '(NERVIOSO)' if vix > 20 else '(NORMAL)'}:
{"Las noticias EXPLOTAN - efecto polvorin activo." if vix > 30 else "Impacto amplificado moderadamente." if vix > 20 else "Comportamiento normal del mercado."}

RECOMENDACION:
{self._generar_recomendacion(prob_final, pred['direccion'], pred['magnitud_esperada'])}
═══════════════════════════════════════════════════════════════════════
"""
        return respuesta
    
    def _generar_recomendacion(self, prob, direccion, magnitud):
        if prob >= 75:
            if direccion == "BAJISTA":
                return "VENDER o proteger posiciones. Alta probabilidad de caída."
            elif direccion == "ALCISTA":
                return "COMPRAR. Alta probabilidad de subida."
            else:
                return "ESPERAR confirmación. Alta probabilidad pero dirección incierta."
        elif prob >= 50:
            return "MONITOREAR de cerca. Probabilidad moderada."
        else:
            return "MANTENER posiciones. Baja probabilidad de impacto."


def main():
    """Demo"""
    sistema = SistemaFinalHackathon()
    
    preguntas = [
        ("Que pasa si la Fed sube tasas?", 35),
        ("Como afecta un ataque terrorista?", 25),
        ("Analiza una crisis financiera", 40),
        ("Como afecta el petroleo subiendo?", 20),
    ]
    
    for pregunta, vix in preguntas:
        print("\n" + "="*70)
        respuesta = sistema.analizar(pregunta, vix)
        print(respuesta)


if __name__ == "__main__":
    main()

SISTEMA FINAL PARA HACKATHON
Todo en uno - funciona LOCAL
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from src.models.predictor_intuitivo import PredictorIntuitivo
from src.utils.logger import logger
import pandas as pd


class SistemaFinalHackathon:
    """Sistema completo para el hackathon"""
    
    def __init__(self):
        self.predictor = PredictorIntuitivo()
        self.df_tokens = self.predictor.df_tokens
        logger.info("✓ Sistema cargado con 123,326 noticias")
    
    def analizar(self, pregunta, vix=20):
        """Analiza una pregunta"""
        # Clasificar
        categoria = self.predictor.clasificar_noticia(pregunta)
        
        # Predecir
        pred = self.predictor.predecir_impacto(pregunta, 'SPY')
        
        # Ajustar por VIX
        prob_base = pred['probabilidad']
        if vix < 20:
            prob_final = prob_base * 0.95
        elif vix > 30:
            prob_final = min(100, prob_base * 1.3)
        else:
            prob_final = prob_base
        
        # Generar respuesta
        respuesta = f"""
═══════════════════════════════════════════════════════════════════════
ANALISIS: {pregunta}
═══════════════════════════════════════════════════════════════════════

CATEGORIA: {categoria}
TOKEN: {pred['token']:.1f}/10
EVENTOS HISTORICOS: {pred['num_eventos_historicos']}

PREDICCION:
  • Probabilidad base: {prob_base:.0f}%
  • Con VIX {vix}: {prob_final:.0f}%
  • Direccion: {pred['direccion']}
  • Magnitud: {pred['magnitud_esperada']*100:+.2f}%

RAZONAMIENTO:
He analizado {pred['num_eventos_historicos']} eventos similares.
El token {pred['token']:.1f}/10 indica impacto {'ALTO' if pred['token'] >= 7 else 'MODERADO'}.
Volatilidad tipica: {pred['volatilidad']:.2f}%

Con VIX {vix} {'(PANICO)' if vix > 30 else '(NERVIOSO)' if vix > 20 else '(NORMAL)'}:
{"Las noticias EXPLOTAN - efecto polvorin activo." if vix > 30 else "Impacto amplificado moderadamente." if vix > 20 else "Comportamiento normal del mercado."}

RECOMENDACION:
{self._generar_recomendacion(prob_final, pred['direccion'], pred['magnitud_esperada'])}
═══════════════════════════════════════════════════════════════════════
"""
        return respuesta
    
    def _generar_recomendacion(self, prob, direccion, magnitud):
        if prob >= 75:
            if direccion == "BAJISTA":
                return "VENDER o proteger posiciones. Alta probabilidad de caída."
            elif direccion == "ALCISTA":
                return "COMPRAR. Alta probabilidad de subida."
            else:
                return "ESPERAR confirmación. Alta probabilidad pero dirección incierta."
        elif prob >= 50:
            return "MONITOREAR de cerca. Probabilidad moderada."
        else:
            return "MANTENER posiciones. Baja probabilidad de impacto."


def main():
    """Demo"""
    sistema = SistemaFinalHackathon()
    
    preguntas = [
        ("Que pasa si la Fed sube tasas?", 35),
        ("Como afecta un ataque terrorista?", 25),
        ("Analiza una crisis financiera", 40),
        ("Como afecta el petroleo subiendo?", 20),
    ]
    
    for pregunta, vix in preguntas:
        print("\n" + "="*70)
        respuesta = sistema.analizar(pregunta, vix)
        print(respuesta)


if __name__ == "__main__":
    main()



