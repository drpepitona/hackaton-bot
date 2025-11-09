"""
🤖 BOT COMPLETO CON GEMINI
Sistema final para el hackathon con IA REAL
"""
import os
import sys
from pathlib import Path
import pandas as pd
import time

sys.path.append(str(Path(__file__).resolve().parent))

from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger

GEMINI_API_KEY = "AIzaSyB-kVZoo3TAxA5t97qFq_ii0ifeKus1r5k"  # Con facturación activada


class BotGeminiCompleto:
    """Bot final con Gemini + todos tus datos"""
    
    def __init__(self):
        self.model = None
        self.df_params = None  # DataFrame con parámetros (tokens, alfa, beta)
        self._cargar_datos()
        self._inicializar_gemini()
    
    def _cargar_datos(self):
        """Carga tokens y parámetros alfa/beta"""
        # Cargar parámetros completos (alfa, beta, token, volatilidad)
        param_files = list(PROCESSED_DATA_DIR.glob("landau/parametros_por_categoria_*.csv"))
        if param_files:
            self.df_params = pd.read_csv(param_files[0])
            logger.info(f"✓ {len(self.df_params)} categorías cargadas con alfa/beta")
        else:
            # Fallback a tokens simples
            token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
            self.df_params = pd.read_csv(token_files[0])
            logger.info(f"✓ {len(self.df_params)} tokens cargados (sin alfa/beta)")
    
    def _inicializar_gemini(self):
        """Inicializa Gemini con modelo de PAGO (no free tier)"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Listar todos los modelos disponibles
            todos_modelos = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    todos_modelos.append(m.name)
            
            # Filtrar SOLO modelos de PAGO (excluir free tier)
            # Free tier tiene: "preview", "exp", "2.5" en el nombre
            modelos_pago = []
            for modelo in todos_modelos:
                nombre_lower = modelo.lower()
                # Excluir modelos free tier
                if any(x in nombre_lower for x in ['preview', 'exp', '-2.5-', '2.5-']):
                    continue
                # Estos SON modelos de pago
                if any(x in nombre_lower for x in ['1.5-flash', '1.5-pro', 'gemini-pro']):
                    modelos_pago.append(modelo)
            
            logger.info(f"Modelos de PAGO encontrados: {modelos_pago[:2]}")
            
            # Preferir flash sobre pro (más rápido y económico)
            modelo_elegido = None
            for modelo in modelos_pago:
                if 'flash' in modelo.lower():
                    modelo_elegido = modelo
                    break
            
            if not modelo_elegido and modelos_pago:
                modelo_elegido = modelos_pago[0]
            
            if modelo_elegido:
                self.model = genai.GenerativeModel(modelo_elegido)
                logger.info(f"✓ Gemini PAGO configurado: {modelo_elegido}")
            else:
                logger.warning("⚠ No se encontraron modelos de pago")
                self.model = None
                
        except Exception as e:
            logger.warning(f"⚠ Gemini no disponible: {str(e)[:100]}")
            self.model = None
    
    def _evaluar_relevancia(self, pregunta):
        """Evalúa si la pregunta es financieramente relevante usando IA"""
        if not self.model:
            return True  # Si no hay modelo, asumir relevancia
        
        try:
            prompt = f"""Eres un analista financiero ESTRICTO. Debes determinar si esta pregunta tiene impacto MEDIBLE y SIGNIFICATIVO en los mercados bursátiles de EEUU (S&P500, Dow Jones, NASDAQ).

PREGUNTA: "{pregunta}"

RELEVANTE si es sobre:
✓ Bancos centrales (Fed, BCE) y política monetaria
✓ Indicadores macroeconómicos (PIB, empleo, inflación)
✓ Conflictos geopolíticos de ESCALA (guerras entre países, terrorismo mayor)
✓ Crisis financieras reales
✓ Empresas Fortune 500 o equivalentes
✓ Precios de commodities (petróleo, oro)

IRRELEVANTE si es sobre:
✗ Celebridades o personas sin cargo gubernamental
✗ Mascotas o animales domésticos  
✗ Eventos locales o triviales
✗ Productos de consumo básico (huevos, pan, etc.) sin contexto de inflación
✗ Empresas pequeñas sin impacto bursátil
✗ Cualquier cosa absurda o sin relevancia económica clara

Sé ESTRICTO. Responde SOLO: "RELEVANTE" o "IRRELEVANTE"
"""
            
            response = self.model.generate_content(prompt)
            evaluacion = response.text.strip().upper()
            
            if "IRRELEVANTE" in evaluacion:
                logger.info("⚠ Pregunta evaluada como IRRELEVANTE para mercados")
                return False
            
            logger.info("✓ Pregunta evaluada como RELEVANTE")
            return True
            
        except Exception as e:
            logger.warning(f"Error en evaluación de relevancia: {str(e)[:50]}")
            return True  # En caso de error, asumir relevancia
    
    def clasificar(self, pregunta):
        """Clasificación semántica mejorada con filtro de relevancia"""
        
        # PASO 1: Evaluar relevancia financiera
        if not self._evaluar_relevancia(pregunta):
            return 'irrelevant'  # Nueva categoría para preguntas irrelevantes
        
        texto = pregunta.lower()
        
        # Diccionario de categorías (keywords ESPECÍFICAS, evitar genéricas)
        categorias = {
            'fed_rates': ['fed', 'reserva federal', 'tasa de interes', 'fomc', 'powell', 'politica monetaria'],
            'ecb_policy': ['ecb', 'bce', 'banco central europeo', 'draghi', 'lagarde'],
            'terrorism': ['terrorista', 'atentado', 'bombing', 'ataque terrorista', 'isis'],
            'war_russia': ['rusia', 'ucrania', 'putin', 'guerra ucrania'],
            'war_middle_east': ['iran', 'iraq', 'siria', 'israel', 'medio oriente', 'palestina'],
            'financial_crisis': ['crisis financiera', 'colapso bancario', 'crash bursatil', 'quiebra banco', 'bailout', 'lehman', 'subprime'],
            'us_gdp_data': ['pib', 'gdp', 'recession', 'producto interno'],
            'us_employment_data': ['desempleo', 'jobs report', 'unemployment', 'nomina'],
            'oil_supply': ['petroleo', 'opep', 'opec', 'crudo', 'wti', 'brent'],
            'gold_demand': ['oro', 'gold'],
            'elections_us': ['elecciones us', 'presidente eeuu', 'votacion eeuu', 'election us'],
            'trade_war': ['guerra comercial', 'aranceles', 'tariff'],
        }
        
        # PASO 2: Intentar match directo
        for cat, keywords in categorias.items():
            if any(kw in texto for kw in keywords):
                logger.info(f"✓ Match directo: {cat}")
                return cat
        
        # PASO 3: Usar IA para clasificar (si es relevante pero sin match directo)
        logger.info("⚙ No hay match directo. Usando IA para clasificar...")
        return self._clasificar_con_ia(pregunta, list(categorias.keys()))
    
    def _clasificar_con_ia(self, pregunta, categorias_disponibles):
        """Usa Gemini para clasificar preguntas sin match directo"""
        if not self.model:
            return 'other'
        
        try:
            prompt = f"""Eres un clasificador de noticias financieras. 

PREGUNTA/NOTICIA: "{pregunta}"

CATEGORÍAS DISPONIBLES:
{chr(10).join(f'• {cat}' for cat in categorias_disponibles)}

TAREA: Analiza la pregunta y elige LA CATEGORÍA MÁS CERCANA que mejor represente el impacto financiero.

Piensa: ¿Qué tipo de evento histórico similar causaría un impacto parecido en los mercados?

Responde SOLO con el nombre exacto de UNA categoría. Sin explicaciones."""

            response = self.model.generate_content(prompt)
            categoria = response.text.strip().lower()
            
            # Validar que la respuesta sea una categoría válida
            if categoria in categorias_disponibles:
                logger.info(f"✓ IA clasificó como: {categoria}")
                return categoria
            
            # Buscar si la respuesta contiene alguna categoría
            for cat in categorias_disponibles:
                if cat in categoria:
                    logger.info(f"✓ IA clasificó como: {cat} (extraído)")
                    return cat
            
            logger.warning(f"⚠ IA no clasificó correctamente: '{categoria}'. Usando 'financial_crisis' por defecto")
            return 'financial_crisis'  # Categoría genérica de fallback
            
        except Exception as e:
            logger.error(f"Error en clasificación IA: {str(e)[:100]}")
            return 'financial_crisis'  # Fallback seguro
    
    def _respuesta_irrelevante(self, pregunta):
        """Respuesta para preguntas financieramente irrelevantes"""
        return f"""
═══════════════════════════════════════════════════════════════════════
ANÁLISIS DE RELEVANCIA
═══════════════════════════════════════════════════════════════════════

PREGUNTA: "{pregunta}"

EVALUACIÓN: **IRRELEVANTE PARA MERCADOS FINANCIEROS**

Este evento no tiene un impacto significativo medible en los mercados de valores de EEUU.
Los mercados financieros responden a:
• Eventos macroeconómicos
• Políticas monetarias y fiscales  
• Conflictos geopolíticos de escala
• Indicadores económicos clave
• Movimientos de empresas significativas

La pregunta evaluada no entra en ninguna de estas categorías con impacto medible.

**PROBABILIDAD DE IMPACTO:** <1%
**RECOMENDACIÓN:** Sin acción requerida

═══════════════════════════════════════════════════════════════════════
"""
    
    def analizar_completo(self, pregunta, vix=20):
        """Análisis completo con Gemini + tus datos"""
        
        logger.info(f"\n{'='*70}")
        logger.info(f"ANALIZANDO: {pregunta}")
        logger.info(f"VIX: {vix}")
        
        # 1. Clasificar
        categoria = self.clasificar(pregunta)
        logger.info(f"Categoría: {categoria}")
        
        # 1.5 Manejar preguntas irrelevantes
        if categoria == 'irrelevant':
            return self._respuesta_irrelevante(pregunta)
        
        # 2. Obtener datos del modelo (con alfa y beta si está disponible)
        param_data = self.df_params[self.df_params['categoria'] == categoria]
        
        if len(param_data) == 0:
            # Valores por defecto si no hay datos
            token = 5.0
            num_eventos = 0
            volatilidad = 0.5
            pct_alcista = 50
            alpha = None
            beta = None
        else:
            row = param_data.iloc[0]
            token = row['token']
            num_eventos = row['num_eventos']
            volatilidad = row['volatilidad'] * 100 if 'volatilidad' in row else row.get('volatilidad_promedio', 0.5) * 100
            pct_alcista = row.get('pct_alcista', 50)
            alpha = row.get('alpha', None)
            beta = row.get('beta', None)
        
        logger.info(f"Token: {token:.1f}, Eventos: {num_eventos}")
        if alpha is not None and beta is not None:
            logger.info(f"Parámetros Landau - α: {alpha:.3f}, β: {beta:.3f}")
        
        # 3. Construir prompt con contexto completo
        parametros_landau = ""
        if alpha is not None and beta is not None:
            parametros_landau = f"""
PARÁMETROS DEL MODELO DE LANDAU (Teoría de Transiciones de Fase):
• Alpha (α): {alpha:.4f} - Parámetro de ordenamiento del sistema
• Beta (β): {beta:.4f} - Coeficiente de no linealidad
• Interpretación: Estos parámetros modelan la transición de fase del mercado ante este evento
"""
        
        prompt = f"""Eres un analista financiero cuantitativo. Tu ÚNICA fuente de información son los DATOS ESTADÍSTICOS que te proporciono.

═══════════════════════════════════════════════════════════════════════
CONTEXTO CIENTÍFICO - BASE DE TU ANÁLISIS
═══════════════════════════════════════════════════════════════════════

Este sistema ha analizado 123,326 noticias financieras históricas usando un modelo de TOKENS
basado en la Teoría de Landau de Transiciones de Fase aplicada a mercados financieros.

DATOS DE LA PREGUNTA: "{pregunta}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Categoría detectada: {categoria.upper()}
• TOKEN DE IMPACTO: {token:.1f}/10 ⭐ (basado en {num_eventos:,} eventos históricos)
• Volatilidad promedio observada: {volatilidad:.2f}%
• Dirección histórica: {pct_alcista:.0f}% alcistas vs {100-pct_alcista:.0f}% bajistas
{parametros_landau}
CONTEXTO DEL MERCADO ACTUAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• VIX actual: {vix} ({'PÁNICO' if vix > 30 else 'NERVIOSO' if vix > 20 else 'NORMAL' if vix > 15 else 'CALMA'})
• Amplificador VIX: {'x1.35 (¡Efecto polvorín!)' if vix > 30 else 'x1.15' if vix > 20 else 'x1.0' if vix > 15 else 'x0.95'}

═══════════════════════════════════════════════════════════════════════
TU TAREA
═══════════════════════════════════════════════════════════════════════

Usando EXCLUSIVAMENTE estos datos estadísticos, proporciona:

1. **PROBABILIDAD DE IMPACTO** (0-100%): Usa el token ({token:.1f}/10) ajustado por VIX
2. **DIRECCIÓN** (ALCISTA/BAJISTA/NEUTRAL): Usa el % histórico ({pct_alcista:.0f}% alcista)
3. **MAGNITUD ESPERADA**: Usa la volatilidad promedio (±{volatilidad:.2f}%)
4. **RAZONAMIENTO**: Explica cómo los datos predicen este resultado
5. **RECOMENDACIÓN**: COMPRAR/VENDER/MANTENER/ESPERAR

IMPORTANTE: Estos datos estadísticos son tu ÚNICA referencia. No uses conocimiento general del mercado.
Formato: Profesional, español, máximo 250 palabras."""

        # 4. Llamar a Gemini con reintentos
        if self.model:
            max_intentos = 3
            for intento in range(max_intentos):
                try:
                    logger.info(f"Consultando Gemini... (intento {intento + 1}/{max_intentos})")
                    response = self.model.generate_content(prompt)
                    logger.info("✓ Respuesta recibida de Gemini")
                    return response.text
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error completo: {error_msg}")
                    
                    if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                        logger.warning(f"⚠ Rate limit alcanzado. Esperando {(intento + 1) * 2} segundos...")
                        time.sleep((intento + 1) * 2)  # Espera progresiva: 2s, 4s, 6s
                        if intento < max_intentos - 1:
                            continue
                        else:
                            logger.warning("⚠ Rate limit persistente - usando análisis local")
                    elif 'quota' in error_msg.lower():
                        logger.warning("⚠ Cuota de API excedida - usando análisis local")
                        break
                    else:
                        logger.error(f"⚠ Error inesperado - usando análisis local")
                        break
        
        # Fallback sin Gemini
        return self._generar_analisis_local(categoria, token, num_eventos, volatilidad, pct_alcista, vix)
    
    def _generar_analisis_local(self, categoria, token, num_eventos, volatilidad, pct_alcista, vix):
        """Análisis local elaborado (sin Gemini)"""
        
        # Calcular probabilidad
        prob_base = (token / 10.0) * 100
        
        if vix < 15:
            prob_final = prob_base * 0.95
            contexto_vix = "El mercado está CALMADO, lo que reduce ligeramente el impacto esperado."
        elif vix < 20:
            prob_final = prob_base
            contexto_vix = "El mercado está NORMAL, sin amplificación del impacto."
        elif vix < 30:
            prob_final = prob_base * 1.15
            contexto_vix = "El mercado está NERVIOSO, amplificando moderadamente el impacto."
        else:
            prob_final = prob_base * 1.35
            contexto_vix = "El mercado está en PÁNICO. Efecto 'polvorín' activo - las noticias EXPLOTAN."
        
        prob_final = min(100, prob_final)
        
        # Dirección
        if pct_alcista > 60:
            direccion = "ALCISTA"
            explicacion_dir = f"El {pct_alcista:.0f}% de los {num_eventos} eventos históricos fueron alcistas."
        elif pct_alcista < 40:
            direccion = "BAJISTA"
            explicacion_dir = f"Solo el {pct_alcista:.0f}% fueron alcistas, {100-pct_alcista:.0f}% bajistas."
        else:
            direccion = "NEUTRAL/INCIERTO"
            explicacion_dir = f"División 50/50 en los datos históricos."
        
        # Recomendación
        if prob_final >= 75:
            recomendacion = "OPERAR" if direccion != "NEUTRAL/INCIERTO" else "ESPERAR confirmación"
        elif prob_final >= 50:
            recomendacion = "MONITOREAR de cerca"
        else:
            recomendacion = "MANTENER posiciones actuales"
        
        analisis = f"""
═══════════════════════════════════════════════════════════════════════
ANÁLISIS PREDICTIVO
═══════════════════════════════════════════════════════════════════════

CATEGORÍA: {categoria.upper()}
TOKEN: {token:.1f}/10
EVENTOS HISTÓRICOS: {num_eventos:,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREDICCIÓN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Probabilidad de impacto: {prob_final:.0f}%
• Dirección esperada: {direccion}
• Magnitud típica: ±{volatilidad:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RAZONAMIENTO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. DATOS HISTÓRICOS:
   He analizado {num_eventos:,} eventos similares de categoría '{categoria}'.
   El token {token:.1f}/10 indica un impacto {'ALTO' if token >= 7 else 'MODERADO' if token >= 5 else 'BAJO'}.
   Movimientos típicos: ±{volatilidad:.2f}%

2. TENDENCIA:
   {explicacion_dir}

3. CONTEXTO VIX:
   VIX actual: {vix}
   {contexto_vix}
   Ajuste: {(prob_final - prob_base):+.0f}% a la probabilidad base.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMENDACIÓN: {recomendacion}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Análisis basado en modelo de tokens entrenado con 123,326 noticias.
═══════════════════════════════════════════════════════════════════════
"""
        return analisis


def main():
    """Demo del sistema completo"""
    logger.info("="*70)
    logger.info("SISTEMA FINAL CON GEMINI")
    logger.info("="*70)
    
    bot = BotGeminiCompleto()
    
    if not bot.model:
        logger.info("\n✓ Modo LOCAL activo (Gemini temporalmente sin cuota)")
        logger.info("  Usando análisis elaborado con tus datos")
    
    # Ejemplos
    preguntas = [
        ("Que pasa si la Fed sube las tasas de interes?", 35),
        ("Como afecta un ataque terrorista en Europa?", 25),
        ("Analiza una crisis financiera como la de 2008", 40),
        ("Como afecta el petroleo subiendo de precio?", 20),
    ]
    
    print("\n" + "="*70)
    print("DEMOSTRACIONES DEL BOT")
    print("="*70)
    
    for i, (pregunta, vix) in enumerate(preguntas, 1):
        logger.info(f"\nEjemplo {i}: {pregunta} (VIX {vix})")
        
        analisis = bot.analizar_completo(pregunta, vix)
        
        # Guardar en archivo
        filename = f"analisis_final_{i}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(analisis)
        
        logger.info(f"✓ Guardado en {filename}")
        
        # Mostrar primeras líneas
        for linea in analisis.split('\n')[:15]:
            logger.info(f"  {linea}")
        
        # Esperar entre preguntas para evitar rate limit
        if i < len(preguntas):
            logger.info(f"  Esperando 3 segundos antes del siguiente análisis...")
            time.sleep(3)
    
    logger.info("\n" + "="*70)
    logger.info("✓ Sistema completo funcionando")
    logger.info("="*70)
    logger.info("\nPara dashboard:")
    logger.info("  py -m streamlit run dashboard_gemini.py")


if __name__ == "__main__":
    main()

