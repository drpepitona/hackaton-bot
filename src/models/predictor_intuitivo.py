"""
Predictor Intuitivo
Da respuestas claras: % probabilidad, dirección, magnitud
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger


class PredictorIntuitivo:
    """
    Sistema de predicción intuitivo
    Input: Una noticia
    Output: Probabilidad (0-100%), Dirección (↑/↓), Magnitud (±X%)
    """
    
    def __init__(self):
        # Cargar tokens de volatilidad
        self.cargar_tokens()
        
        logger.info("✓ PredictorIntuitivo inicializado")
    
    def cargar_tokens(self):
        """Carga los tokens calculados"""
        landau_dir = PROCESSED_DATA_DIR / "landau"
        
        # Cargar tokens de volatilidad
        token_files = list(landau_dir.glob("tokens_volatilidad_*.csv"))
        if token_files:
            self.df_tokens = pd.read_csv(token_files[0])
            logger.info(f"  ✓ Tokens cargados: {len(self.df_tokens)} combinaciones")
        else:
            self.df_tokens = pd.DataFrame()
            logger.warning("  ⚠ No se encontraron tokens")
    
    def clasificar_noticia(self, titulo):
        """
        Clasifica una noticia en categoría
        """
        titulo_lower = titulo.lower()
        
        # Categorías con keywords
        categorias = {
            'ecb_policy': ['ecb', 'draghi', 'lagarde', 'european central bank'],
            'fed_rates': ['fed', 'federal reserve', 'fomc', 'powell', 'interest rate'],
            'us_gdp_data': ['gdp', 'economic growth', 'recession'],
            'us_employment_data': ['employment', 'jobs', 'unemployment', 'nfp', 'payroll'],
            'us_inflation_data': ['inflation', 'cpi', 'pce'],
            'financial_crisis': ['crisis', 'crash', 'panic', 'collapse', 'bailout'],
            'terrorism': ['terror', 'bombing', 'attack', 'isis'],
            'war_middle_east': ['iran', 'iraq', 'syria', 'israel', 'gaza'],
            'war_russia': ['russia', 'ukraine', 'putin', 'crimea'],
            'oil_supply': ['opec', 'oil production', 'crude supply'],
            'oil_shock': ['oil', 'crude', 'petroleum'],
            'gold_demand': ['gold', 'precious metals'],
            'brexit': ['brexit', 'uk referendum'],
            'elections_us': ['us election', 'president', 'congress'],
            'trade_general': ['trade', 'export', 'import'],
            'us_consumer_data': ['consumer confidence', 'retail sales'],
            'earnings_general': ['earnings', 'profit', 'quarterly results'],
            'tech_sector': ['apple', 'google', 'microsoft', 'amazon', 'tech'],
        }
        
        for categoria, keywords in categorias.items():
            if any(kw in titulo_lower for kw in keywords):
                return categoria
        
        return 'other'
    
    def predecir_impacto(self, titulo, asset='SPY', vix_actual=None):
        """
        Predice el impacto de una noticia
        
        Returns:
            Dict con:
            - probabilidad: 0-100%
            - direccion: 'ALCISTA', 'BAJISTA', 'NEUTRAL'
            - magnitud_esperada: ±X%
            - confianza: 'ALTA', 'MEDIA', 'BAJA'
        """
        # 1. Clasificar noticia
        categoria = self.clasificar_noticia(titulo)
        
        # 2. Buscar token correspondiente
        token_data = self.df_tokens[
            (self.df_tokens['categoria'] == categoria) & 
            (self.df_tokens['asset'] == asset)
        ]
        
        if len(token_data) == 0:
            # Categoría no encontrada - usar valores por defecto
            return {
                'categoria': categoria,
                'asset': asset,
                'probabilidad': 30,
                'direccion': 'NEUTRAL',
                'magnitud_esperada': 0.2,
                'volatilidad': 0.2,
                'confianza': 'BAJA',
                'num_eventos_historicos': 0,
                'pct_alcista_historico': 50,
                'pct_bajista_historico': 50,
                'token': 1.0,
                'mensaje': f"[-] BAJA probabilidad (30%) - Categoria '{categoria}' sin datos historicos\nTendencia esperada: NEUTRAL (+/-0.20%)\nConfianza: BAJA"
            }
        
        # 3. Extraer información
        row = token_data.iloc[0]
        
        volatilidad = row['volatilidad_promedio'] * 100  # Convertir a %
        pct_alcista = row['pct_alcista']
        pct_bajista = row['pct_bajista']
        token = row['token']
        num_eventos = row['num_eventos']
        
        # 4. Calcular probabilidad de impacto (0-100%)
        # Basado en token y número de eventos
        probabilidad_base = (token / 10.0) * 100  # Token 10 = 100% prob
        
        # Ajustar por número de eventos (más eventos = más confianza)
        if num_eventos >= 100:
            ajuste_confianza = 1.0
        elif num_eventos >= 50:
            ajuste_confianza = 0.95
        elif num_eventos >= 20:
            ajuste_confianza = 0.85
        else:
            ajuste_confianza = 0.70
        
        probabilidad = min(probabilidad_base * ajuste_confianza, 99)
        
        # 5. Determinar dirección
        if pct_alcista > 60:
            direccion = 'ALCISTA'
        elif pct_bajista > 60:
            direccion = 'BAJISTA'
        elif pct_alcista > 55:
            direccion = 'ALCISTA_LEVE'
        elif pct_bajista > 55:
            direccion = 'BAJISTA_LEVE'
        else:
            direccion = 'NEUTRAL'
        
        # 6. Magnitud esperada
        if direccion in ['ALCISTA', 'ALCISTA_LEVE']:
            magnitud_esperada = row['magnitud_alcista'] * 100
        elif direccion in ['BAJISTA', 'BAJISTA_LEVE']:
            magnitud_esperada = -row['magnitud_bajista'] * 100
        else:
            magnitud_esperada = volatilidad * (1 if pct_alcista > 50 else -1)
        
        # 7. Ajustar por VIX si disponible
        if vix_actual:
            if vix_actual > 30:
                # Pánico - amplificar volatilidad
                magnitud_esperada *= 1.5
                probabilidad = min(probabilidad * 1.2, 99)
            elif vix_actual < 15:
                # Calma - reducir volatilidad
                magnitud_esperada *= 0.7
                probabilidad *= 0.9
        
        # 8. Nivel de confianza
        if num_eventos >= 100 and token >= 7:
            confianza = 'ALTA'
        elif num_eventos >= 50 and token >= 5:
            confianza = 'MEDIA'
        else:
            confianza = 'BAJA'
        
        # 9. Generar mensaje intuitivo
        mensaje = self._generar_mensaje(
            categoria, asset, probabilidad, direccion, 
            magnitud_esperada, confianza, num_eventos
        )
        
        return {
            'categoria': categoria,
            'asset': asset,
            'probabilidad': round(probabilidad, 1),
            'direccion': direccion,
            'magnitud_esperada': round(magnitud_esperada, 2),
            'volatilidad': round(volatilidad, 2),
            'confianza': confianza,
            'num_eventos_historicos': int(num_eventos),
            'pct_alcista_historico': round(pct_alcista, 1),
            'pct_bajista_historico': round(pct_bajista, 1),
            'token': round(token, 2),
            'mensaje': mensaje
        }
    
    def _generar_mensaje(self, categoria, asset, prob, direccion, mag, conf, eventos):
        """Genera mensaje intuitivo para el usuario"""
        
        # Símbolos según dirección
        simbolo_dir = {
            'ALCISTA': '^',
            'ALCISTA_LEVE': '/',
            'BAJISTA': 'v',
            'BAJISTA_LEVE': '\\',
            'NEUTRAL': '-'
        }
        
        simbolo = simbolo_dir.get(direccion, '?')
        
        # Mensaje base
        if prob >= 80:
            nivel = "MUY ALTA"
        elif prob >= 60:
            nivel = "ALTA"
        elif prob >= 40:
            nivel = "MEDIA"
        else:
            nivel = "BAJA"
        
        mensaje = f"[{simbolo}] {nivel} probabilidad ({prob:.0f}%) de impacto en {asset}\n"
        mensaje += f"Tendencia esperada: {direccion} ({mag:+.2f}%)\n"
        mensaje += f"Confianza: {conf} (basado en {eventos} eventos historicos)\n"
        
        # Recomendación
        if prob >= 70 and abs(mag) >= 0.5:
            if mag > 0:
                mensaje += f"\n>> Recomendacion: Considerar posicion LARGA en {asset}"
            else:
                mensaje += f"\n>> Recomendacion: Considerar posicion CORTA o proteccion en {asset}"
        elif prob >= 70:
            mensaje += f"\n** Alta probabilidad pero magnitud moderada"
        elif prob < 40:
            mensaje += f"\n-- Baja probabilidad de impacto - Puede ignorarse"
        
        return mensaje
    
    def analizar_multiples_noticias(self, noticias, asset='SPY', vix_actual=None):
        """
        Analiza un conjunto de noticias y genera predicción agregada
        """
        logger.info("\n" + "="*70)
        logger.info(f"ANÁLISIS DE {len(noticias)} NOTICIAS PARA {asset}")
        logger.info("="*70)
        
        predicciones = []
        
        for noticia in noticias:
            pred = self.predecir_impacto(noticia, asset, vix_actual)
            predicciones.append(pred)
        
        # Agregación
        phi_total = sum(p['token'] for p in predicciones)
        prob_promedio = np.mean([p['probabilidad'] for p in predicciones])
        
        # Magnitud esperada ponderada por probabilidad
        magnitud_total = sum(
            p['magnitud_esperada'] * (p['probabilidad'] / 100)
            for p in predicciones
        )
        
        # Dirección agregada
        if magnitud_total > 0.5:
            direccion_final = 'ALCISTA'
        elif magnitud_total < -0.5:
            direccion_final = 'BAJISTA'
        else:
            direccion_final = 'NEUTRAL'
        
        logger.info(f"\nRESULTADO AGREGADO:")
        logger.info(f"  phi (parametro orden): {phi_total:.2f}")
        logger.info(f"  Probabilidad media: {prob_promedio:.1f}%")
        logger.info(f"  Magnitud total: {magnitud_total:+.2f}%")
        logger.info(f"  Direccion: {direccion_final}")
        
        # Mostrar noticias individuales
        logger.info(f"\nNOTICIAS INDIVIDUALES:")
        for i, (noticia, pred) in enumerate(zip(noticias, predicciones), 1):
            logger.info(f"\n{i}. {noticia[:60]}...")
            logger.info(f"   Cat: {pred['categoria']}, Token: {pred['token']}")
            logger.info(f"   {pred['direccion']}: {pred['magnitud_esperada']:+.2f}% (prob: {pred['probabilidad']:.0f}%)")
        
        return {
            'phi_total': phi_total,
            'probabilidad_agregada': prob_promedio,
            'magnitud_total': magnitud_total,
            'direccion_final': direccion_final,
            'predicciones_individuales': predicciones
        }


def demo_predictor():
    """
    Demo del predictor con ejemplos
    """
    logger.info("="*70)
    logger.info("PREDICTOR INTUITIVO - DEMO")
    logger.info("="*70)
    
    predictor = PredictorIntuitivo()
    
    # Ejemplos de noticias
    ejemplos = [
        "ECB unexpectedly cuts interest rates by 0.25%",
        "US unemployment falls to 3.5%, beating expectations",
        "Apple reports record earnings, beats estimates",
        "Russia invades Ukraine, oil prices spike",
        "Fed signals dovish stance, may pause rate hikes",
        "US GDP grows 3.2% in Q2, above forecast",
        "Brexit vote passes, UK to leave EU",
        "Gold prices surge on safe-haven demand",
    ]
    
    print("\n" + "="*70)
    print("PREDICCIONES INDIVIDUALES")
    print("="*70)
    
    for i, noticia in enumerate(ejemplos, 1):
        print(f"\n{'='*70}")
        print(f"NOTICIA #{i}")
        print(f"{'='*70}")
        print(f"Titulo: {noticia}")
        print("")
        
        # Predecir en SPY
        pred = predictor.predecir_impacto(noticia, asset='SPY')
        
        print(pred['mensaje'])
        
        print(f"\nDetalles tecnicos:")
        print(f"  - Categoria: {pred['categoria']}")
        print(f"  - Token: {pred['token']}/10")
        print(f"  - Volatilidad historica: +/-{pred['volatilidad']:.2f}%")
        print(f"  - Eventos historicos: {pred['num_eventos_historicos']}")
        print(f"  - Historico: {pred['pct_alcista_historico']:.0f}% arriba, {pred['pct_bajista_historico']:.0f}% abajo")
    
    # Análisis agregado
    print("\n" + "="*70)
    print("ANÁLISIS AGREGADO (TODAS LAS NOTICIAS JUNTAS)")
    print("="*70)
    
    resultado_agregado = predictor.analizar_multiples_noticias(ejemplos, asset='SPY', vix_actual=22)
    
    print(f"\nRESUMEN:")
    print(f"  Parametro phi total: {resultado_agregado['phi_total']:.2f}")
    print(f"  Probabilidad agregada: {resultado_agregado['probabilidad_agregada']:.1f}%")
    print(f"  Movimiento esperado: {resultado_agregado['magnitud_total']:+.2f}%")
    print(f"  Direccion: {resultado_agregado['direccion_final']}")
    
    if resultado_agregado['direccion_final'] == 'ALCISTA':
        print(f"\n[OK] PREDICCION: El S&P 500 probablemente SUBIRA {abs(resultado_agregado['magnitud_total']):.2f}%")
    elif resultado_agregado['direccion_final'] == 'BAJISTA':
        print(f"\n[!!] PREDICCION: El S&P 500 probablemente BAJARA {abs(resultado_agregado['magnitud_total']):.2f}%")
    else:
        print(f"\n[--] PREDICCION: Movimiento NEUTRAL o limitado")


def predecir_noticia_interactiva():
    """
    Modo interactivo para probar noticias
    """
    predictor = PredictorIntuitivo()
    
    print("\n" + "="*70)
    print("🤖 PREDICTOR INTUITIVO - MODO INTERACTIVO")
    print("="*70)
    print("\nIngresa una noticia para predecir su impacto")
    print("(o 'salir' para terminar)")
    print("")
    
    while True:
        noticia = input("\n📰 Noticia: ")
        
        if noticia.lower() in ['salir', 'exit', 'quit', '']:
            break
        
        # Assets disponibles
        print("\n¿Qué asset quieres analizar?")
        print("  1. SPY (S&P 500)")
        print("  2. QQQ (NASDAQ)")
        print("  3. DIA (Dow Jones)")
        print("  4. IWM (Russell 2000)")
        
        asset_choice = input("Selecciona (1-4, default=1): ") or "1"
        
        asset_map = {'1': 'SPY', '2': 'QQQ', '3': 'DIA', '4': 'IWM'}
        asset = asset_map.get(asset_choice, 'SPY')
        
        # VIX opcional
        vix_input = input("VIX actual (opcional, default=20): ")
        vix = float(vix_input) if vix_input else None
        
        # Predecir
        print("\n" + "="*70)
        pred = predictor.predecir_impacto(noticia, asset=asset, vix_actual=vix)
        
        print(pred['mensaje'])
        
        print(f"\n📊 Detalles:")
        print(f"  • Categoría detectada: {pred['categoria']}")
        print(f"  • Token: {pred['token']}/10")
        print(f"  • Eventos históricos: {pred['num_eventos_historicos']}")
        print(f"  • Volatilidad típica: ±{pred['volatilidad']:.2f}%")
        print("="*70)


# Función para API
def predecir_rapido(noticia, asset='SPY', vix=None):
    """
    Función rápida para usar desde otros scripts
    
    Uso:
        from src.models.predictor_intuitivo import predecir_rapido
        
        resultado = predecir_rapido(
            "Fed raises rates 0.25%",
            asset='SPY',
            vix=22
        )
        
        print(f"Probabilidad: {resultado['probabilidad']}%")
        print(f"Dirección: {resultado['direccion']}")
        print(f"Magnitud: {resultado['magnitud_esperada']:+.2f}%")
    """
    predictor = PredictorIntuitivo()
    return predictor.predecir_impacto(noticia, asset, vix)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'interactivo':
        # Modo interactivo
        predecir_noticia_interactiva()
    else:
        # Modo demo
        demo_predictor()
