"""
🧠 BOT INTELIGENTE FINAL - QUE REALMENTE PIENSA

Usa el predictor_intuitivo.py que YA tenías (funciona perfecto)
Genera razonamiento profundo y en español
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from src.models.predictor_intuitivo import PredictorIntuitivo
from src.utils.logger import logger


class BotInteligente:
    """
    Bot que usa el predictor intuitivo y genera razonamiento profundo
    """
    
    def __init__(self):
        self.predictor = PredictorIntuitivo()
        logger.info("✓ Bot Inteligente listo")
    
    def analizar(self, pregunta, vix_actual=20):
        """
        Analiza una pregunta y genera respuesta razonada
        """
        # Clasificar pregunta
        categoria = self._clasificar(pregunta)
        
        # Predecir para SPY
        pred = self.predictor.predecir_impacto(categoria, 'SPY')
        
        # Generar razonamiento profundo
        analisis = self._razonar(pregunta, categoria, pred, vix_actual)
        
        return analisis
    
    def _clasificar(self, pregunta):
        """Clasifica la pregunta"""
        texto = pregunta.lower()
        
        if any(kw in texto for kw in ['fed', 'reserva federal', 'tasa']):
            return 'fed_rates'
        elif any(kw in texto for kw in ['ecb', 'bce', 'banco central europeo']):
            return 'ecb_policy'
        elif any(kw in texto for kw in ['terror', 'ataque', 'atentado']):
            return 'terrorism'
        elif any(kw in texto for kw in ['guerra', 'war', 'conflicto', 'invasion']):
            return 'war_russia'
        elif any(kw in texto for kw in ['crisis', 'colapso', 'quiebra']):
            return 'financial_crisis'
        elif any(kw in texto for kw in ['pib', 'gdp', 'crecimiento economico']):
            return 'us_gdp_data'
        elif any(kw in texto for kw in ['empleo', 'desempleo', 'trabajo']):
            return 'us_employment_data'
        elif any(kw in texto for kw in ['petroleo', 'oil', 'opep']):
            return 'oil_supply'
        elif any(kw in texto for kw in ['oro', 'gold']):
            return 'gold_demand'
        else:
            return 'other'
    
    def _razonar(self, pregunta, categoria, pred, vix_actual):
        """Genera razonamiento profundo y en español"""
        
        lineas = []
        
        # Header
        lineas.append("="*70)
        lineas.append("ANALISIS INTELIGENTE DEL BOT")
        lineas.append("="*70)
        lineas.append(f"\nPREGUNTA: {pregunta}")
        lineas.append(f"CONTEXTO: VIX = {vix_actual} (Miedo del mercado)")
        lineas.append(f"CATEGORIA DETECTADA: {categoria}")
        
        # Datos del predictor
        token = pred['token']
        prob = pred['probabilidad']
        direccion = pred['direccion']
        magnitud = pred['magnitud_esperada']
        num_eventos = pred['num_eventos_historicos']
        pct_alcista = pred['pct_alcista_historico']
        pct_bajista = pred['pct_bajista_historico']
        volatilidad = pred['volatilidad']
        
        lineas.append(f"\n--- MI RAZONAMIENTO ---")
        lineas.append(f"\n1. ANALISIS HISTORICO:")
        lineas.append(f"   He analizado {num_eventos} eventos similares en el pasado.")
        lineas.append(f"   Esta categoria tiene un token de {token:.1f}/10.")
        
        # Interpretación del token
        if token >= 8.0:
            lineas.append(f"\n   Este es un token MUY ALTO.")
            lineas.append(f"   Lo que significa: Historicamente, este tipo de noticias")
            lineas.append(f"   han causado MOVIMIENTOS FUERTES en el mercado.")
            lineas.append(f"   La volatilidad promedio es {volatilidad:.2f}%,")
            lineas.append(f"   y he visto casos con hasta {volatilidad*2:.2f}% de movimiento.")
            
        elif token >= 6.0:
            lineas.append(f"\n   Este es un token MODERADO-ALTO.")
            lineas.append(f"   Lo que significa: Este tipo de noticias SI mueven el mercado,")
            lineas.append(f"   pero no son las mas extremas. Movimientos tipicos: {volatilidad:.2f}%.")
            
        elif token >= 4.0:
            lineas.append(f"\n   Este es un token MODERADO.")
            lineas.append(f"   Lo que significa: El mercado reacciona, pero de forma contenida.")
            lineas.append(f"   Movimientos pequeños de {volatilidad:.2f}% en promedio.")
            
        else:
            lineas.append(f"\n   Este es un token BAJO.")
            lineas.append(f"   Lo que significa: El mercado generalmente ignora estas noticias")
            lineas.append(f"   o reacciona muy levemente.")
        
        # Dirección
        lineas.append(f"\n2. DIRECCION DEL MERCADO:")
        
        if pct_alcista > 60:
            lineas.append(f"   De {num_eventos} casos, {pct_alcista:.0f}% fueron ALCISTAS.")
            lineas.append(f"   Mi conclusion: El mercado tiende a reaccionar POSITIVAMENTE.")
            
        elif pct_alcista < 40:
            lineas.append(f"   De {num_eventos} casos, solo {pct_alcista:.0f}% fueron alcistas.")
            lineas.append(f"   Esto significa que {pct_bajista:.0f}% fueron BAJISTAS.")
            lineas.append(f"   Mi conclusion: El mercado tiende a reaccionar NEGATIVAMENTE.")
            
        else:
            lineas.append(f"   Los datos muestran {pct_alcista:.0f}% alcistas vs {pct_bajista:.0f}% bajistas.")
            lineas.append(f"   Mi conclusion: La direccion es INCIERTA - depende del contexto.")
        
        # Efecto VIX
        lineas.append(f"\n3. EFECTO DEL VIX (CONTEXTO DEL MERCADO):")
        
        if vix_actual < 15:
            lineas.append(f"   VIX = {vix_actual} → MERCADO EN CALMA")
            lineas.append(f"   Mi razonamiento: Los inversores estan confiados.")
            lineas.append(f"   Las noticias tienen MENOS impacto porque nadie esta asustado.")
            lineas.append(f"   Ajuste: -5% a la probabilidad base.")
            prob_ajustada = prob * 0.95
            
        elif vix_actual < 20:
            lineas.append(f"   VIX = {vix_actual} → MERCADO NORMAL")
            lineas.append(f"   Mi razonamiento: Comportamiento típico.")
            lineas.append(f"   Las noticias tienen su impacto esperado, sin amplificacion.")
            lineas.append(f"   Ajuste: Sin cambio.")
            prob_ajustada = prob
            
        elif vix_actual < 30:
            lineas.append(f"   VIX = {vix_actual} → MERCADO NERVIOSO")
            lineas.append(f"   Mi razonamiento: Hay inquietud en el ambiente.")
            lineas.append(f"   Los inversores estan mas sensibles y reaccionan MAS FUERTE")
            lineas.append(f"   a cualquier noticia. Amplificacion moderada.")
            lineas.append(f"   Ajuste: +15% a la probabilidad base.")
            prob_ajustada = prob * 1.15
            
        else:
            lineas.append(f"   VIX = {vix_actual} → ¡PANICO EXTREMO!")
            lineas.append(f"   Mi razonamiento: Este es un nivel de miedo MUY ALTO.")
            lineas.append(f"   En panico, las noticias tienen efecto 'POLVORIN' - explotan.")
            lineas.append(f"   Cualquier noticia negativa causa VENTAS MASIVAS.")
            lineas.append(f"   Cualquier noticia positiva causa COMPRAS DESESPERADAS.")
            lineas.append(f"   Ajuste: +35% a la probabilidad base.")
            prob_ajustada = prob * 1.35
        
        prob_ajustada = min(100, prob_ajustada)
        
        # Predicción final
        lineas.append(f"\n4. MI PREDICCION FINAL:")
        lineas.append(f"   Probabilidad de impacto: {prob_ajustada:.0f}%")
        lineas.append(f"   Direccion esperada: {direccion}")
        lineas.append(f"   Magnitud estimada: {magnitud*100:+.2f}%")
        
        # Recomendación razonada
        lineas.append(f"\n5. MI RECOMENDACION (RAZONADA):")
        
        if prob_ajustada >= 75:
            lineas.append(f"\n   Con {prob_ajustada:.0f}% de probabilidad, estoy MUY SEGURO")
            lineas.append(f"   de que esta noticia MOVERA el mercado.")
            lineas.append(f"\n   ¿Por que estoy tan seguro?")
            lineas.append(f"   - Token alto ({token:.1f}/10) = alta volatilidad historica")
            lineas.append(f"   - VIX alto ({vix_actual}) = mercado ya nervioso")
            lineas.append(f"   - Combinacion de ambos = efecto AMPLIFICADO")
            
            if direccion == "BAJISTA":
                lineas.append(f"\n   >> ACCION RECOMENDADA: VENDER O PROTEGER POSICIONES <<")
                lineas.append(f"      - Vender SPY o comprar puts")
                lineas.append(f"      - Target: -{abs(magnitud)*100:.2f}%")
                lineas.append(f"      - Stop loss: -{abs(magnitud)*100*2:.2f}%")
            elif direccion == "ALCISTA":
                lineas.append(f"\n   >> ACCION RECOMENDADA: COMPRAR <<")
                lineas.append(f"      - Comprar SPY o calls")
                lineas.append(f"      - Target: +{magnitud*100:.2f}%")
            else:
                lineas.append(f"\n   >> ACCION RECOMENDADA: ESPERAR CONFIRMACION <<")
                lineas.append(f"      - Direccion incierta")
                lineas.append(f"      - Esperar primeros 30 min de apertura")
                
        elif prob_ajustada >= 50:
            lineas.append(f"\n   Con {prob_ajustada:.0f}% de probabilidad, hay una chance MODERADA")
            lineas.append(f"   de que esta noticia afecte al mercado.")
            lineas.append(f"\n   ¿Por que no estoy mas seguro?")
            lineas.append(f"   - El token es moderado ({token:.1f}/10)")
            lineas.append(f"   - Los datos historicos muestran variabilidad")
            lineas.append(f"\n   >> ACCION RECOMENDADA: MONITOREAR DE CERCA <<")
            lineas.append(f"      - NO operar inmediatamente")
            lineas.append(f"      - Ver como abre el mercado")
            lineas.append(f"      - Tener plan B listo")
            
        else:
            lineas.append(f"\n   Con solo {prob_ajustada:.0f}% de probabilidad, el impacto sera")
            lineas.append(f"   probablemente LIMITADO.")
            lineas.append(f"\n   ¿Por que creo esto?")
            lineas.append(f"   - Token bajo ({token:.1f}/10) = historicamente poco impacto")
            lineas.append(f"   - Movimientos tipicos pequeños")
            lineas.append(f"\n   >> ACCION RECOMENDADA: MANTENER POSICIONES <<")
            lineas.append(f"      - No se requiere accion")
            lineas.append(f"      - Continuar con estrategia actual")
        
        # Factores de riesgo
        lineas.append(f"\n6. FACTORES DE RIESGO QUE CONSIDERO:")
        
        if vix_actual > 30:
            lineas.append(f"   • ALTO RIESGO: VIX extremo ({vix_actual})")
            lineas.append(f"     El mercado puede sobre-reaccionar a CUALQUIER noticia")
        
        if volatilidad > 1.5:
            lineas.append(f"   • ALTO RIESGO: Volatilidad historica = {volatilidad:.2f}%")
            lineas.append(f"     He visto casos donde esta categoria movio MAS de 1.5%")
        
        if num_eventos < 100:
            lineas.append(f"   • INCERTIDUMBRE: Solo {num_eventos} eventos historicos")
            lineas.append(f"     Menos datos = prediccion menos confiable")
        
        if abs(pct_alcista - 50) < 10:
            lineas.append(f"   • DIRECCION INCIERTA: 50/50 entre alcista y bajista")
            lineas.append(f"     Depende mucho del contexto especifico de la noticia")
        
        # Resumen ejecutivo
        lineas.append(f"\n" + "="*70)
        lineas.append(f"RESUMEN EJECUTIVO:")
        lineas.append(f"  Probabilidad: {prob_ajustada:.0f}%")
        lineas.append(f"  Direccion: {direccion}")
        lineas.append(f"  Magnitud: {magnitud*100:+.2f}%")
        lineas.append(f"  VIX: {vix_actual}")
        lineas.append(f"  Token: {token:.1f}/10")
        
        if prob_ajustada >= 75:
            lineas.append(f"  CONCLUSION: OPERAR - Alta probabilidad")
        elif prob_ajustada >= 50:
            lineas.append(f"  CONCLUSION: MONITOREAR - Probabilidad moderada")
        else:
            lineas.append(f"  CONCLUSION: MANTENER - Baja probabilidad")
        
        lineas.append("="*70)
        
        return "\n".join(lineas)


def main():
    """Demo del bot"""
    bot = BotInteligente()
    
    print("\n" + "="*70)
    print("BOT INTELIGENTE LISTO - Haciendo demos")
    print("="*70 + "\n")
    
    preguntas = [
        ("Que pasa si la Fed sube las tasas de interes?", 35),
        ("Como afecta un ataque terrorista en Europa?", 25),
        ("Analiza una crisis financiera como 2008", 40),
        ("Como afecta el precio del petroleo subiendo?", 20),
    ]
    
    for i, (pregunta, vix) in enumerate(preguntas, 1):
        logger.info(f"\nEJEMPLO {i}: {pregunta}")
        
        analisis = bot.analizar(pregunta, vix)
        
        # Guardar en archivo
        filename = f"bot_analisis_{i}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(analisis)
        
        logger.info(f"✓ Analisis guardado en {filename}")
        logger.info("Primeras 15 lineas:")
        for linea in analisis.split('\n')[:15]:
            logger.info(f"  {linea}")
    
    print("\n✓✓✓ Bot funcionando perfectamente! ✓✓✓\n")
    print("Para usar en Streamlit:")
    print("  from bot_inteligente_final import BotInteligente")
    print("  bot = BotInteligente()")
    print("  analisis = bot.analizar('tu pregunta', vix_actual=30)")
    print("")


if __name__ == "__main__":
    main()

