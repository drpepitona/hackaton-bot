"""
Modelo Refinado con VIX Contextual
Usa Bayesian Optimization para encontrar α y β óptimos

Fórmula:
Impacto_Contextual = P_impacto × (1 + α × (V_miedo - 1)^β)

Donde:
- P_impacto: Probabilidad base del token
- V_miedo: VIX normalizado (VIX/VIX_crítico)
- α: Amplificador del efecto miedo
- β: Exponente no-lineal (captura "polvorín")
"""
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


class ModeloRefinadoVIX:
    """
    Modelo refinado que considera el contexto de miedo del mercado
    """
    
    def __init__(self):
        # Parámetros a optimizar
        self.alpha = None  # Amplificador
        self.beta = None   # Exponente no-lineal
        
        # VIX de referencia (temperatura crítica)
        self.vix_critico = 20.0
        
        # Datos históricos
        self.df_tokens = None
        self.df_noticias = None
        self.df_historico = None
        
        logger.info("✓ ModeloRefinadoVIX inicializado")
    
    def cargar_datos(self):
        """Carga todos los datos necesarios"""
        logger.info("\n" + "="*70)
        logger.info("CARGANDO DATOS PARA OPTIMIZACIÓN")
        logger.info("="*70)
        
        # 1. Tokens
        token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
        if token_files:
            self.df_tokens = pd.read_csv(token_files[0])
            logger.info(f"  ✓ Tokens: {len(self.df_tokens)} combinaciones")
        
        # 2. Parámetros históricos (con VIX)
        hist_files = list(PROCESSED_DATA_DIR.glob("landau/parametros_landau_historicos_*.csv"))
        if hist_files:
            self.df_historico = pd.read_csv(hist_files[0])
            self.df_historico['fecha'] = pd.to_datetime(self.df_historico['fecha'])
            logger.info(f"  ✓ Histórico: {len(self.df_historico)} días")
        
        # 3. Noticias clasificadas (necesitamos recrearlas)
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        df_combined = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
        df_combined['Date'] = pd.to_datetime(df_combined['Date'])
        
        # Expandir noticias
        noticias = []
        for idx, row in df_combined.iterrows():
            for i in range(1, 26):
                noticia = row.get(f'Top{i}')
                if pd.notna(noticia) and noticia != '':
                    noticias.append({
                        'fecha': row['Date'],
                        'titulo': noticia
                    })
        
        self.df_noticias = pd.DataFrame(noticias)
        logger.info(f"  ✓ Noticias: {len(self.df_noticias)}")
        
        # 4. Clasificar noticias (simplificado)
        self.clasificar_noticias_rapido()
        
        return True
    
    def clasificar_noticias_rapido(self):
        """Clasificación rápida de noticias"""
        categorias = {
            'ecb_policy': ['ecb', 'draghi', 'lagarde'],
            'fed_rates': ['fed', 'fomc', 'interest rate'],
            'us_gdp_data': ['gdp'],
            'us_employment_data': ['employment', 'jobs', 'unemployment'],
            'terrorism': ['terror', 'bombing', 'attack'],
            'war_russia': ['russia', 'ukraine', 'putin'],
            'war_middle_east': ['iran', 'iraq', 'syria', 'israel'],
            'financial_crisis': ['crisis', 'crash', 'panic'],
        }
        
        self.df_noticias['categoria'] = 'other'
        
        for idx, row in self.df_noticias.iterrows():
            titulo = str(row['titulo']).lower()
            for cat, keywords in categorias.items():
                if any(kw in titulo for kw in keywords):
                    self.df_noticias.at[idx, 'categoria'] = cat
                    break
    
    def calcular_impacto_contextual(self, p_impacto, vix_actual, alpha, beta):
        """
        Calcula impacto contextual considerando VIX
        
        Fórmula:
        Impacto = P_base × (1 + α × (V_normalizado - 1)^β)
        
        Args:
            p_impacto: Probabilidad base (del token)
            vix_actual: VIX del día
            alpha: Amplificador
            beta: Exponente no-lineal
        """
        # Normalizar VIX
        v_normalizado = vix_actual / self.vix_critico
        
        # Aplicar fórmula
        if v_normalizado <= 1.0:
            # VIX bajo - efecto mínimo
            impacto = p_impacto * (1.0 - alpha * 0.1 * (1 - v_normalizado))
        else:
            # VIX alto - efecto polvorín
            impacto = p_impacto * (1.0 + alpha * ((v_normalizado - 1.0) ** beta))
        
        # Limitar entre 0 y 100
        impacto = max(0, min(100, impacto))
        
        return impacto
    
    def preparar_datos_optimizacion(self):
        """
        Prepara dataset para optimizar α y β
        
        Para cada noticia histórica:
        - P_impacto (del token)
        - VIX ese día
        - Impacto REAL (si movió el mercado o no)
        """
        logger.info("\n" + "="*70)
        logger.info("PREPARANDO DATOS PARA OPTIMIZACIÓN")
        logger.info("="*70)
        
        # Normalizar fechas del histórico (eliminar timezone)
        self.df_historico['fecha_norm'] = pd.to_datetime([str(d).split()[0] for d in self.df_historico['fecha']])
        
        datos_opt = []
        
        # Para cada noticia
        for idx, row in self.df_noticias.iterrows():
            if idx % 10000 == 0:
                logger.info(f"  Procesando: {idx}/{len(self.df_noticias)}")
            
            fecha = pd.Timestamp(row['fecha']).normalize()
            categoria = row['categoria']
            
            if categoria == 'other':
                continue
            
            # Buscar token de esa categoría
            token_data = self.df_tokens[
                (self.df_tokens['categoria'] == categoria) & 
                (self.df_tokens['asset'] == 'SPY')
            ]
            
            if len(token_data) == 0:
                continue
            
            # Probabilidad base
            token = token_data.iloc[0]['token']
            p_base = (token / 10.0) * 100
            
            # Buscar VIX y retorno real ese día (con búsqueda en rango)
            try:
                # Buscar fecha exacta
                hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha]
                
                if len(hist_data) == 0:
                    # Buscar en ventana de ±3 días
                    for offset in range(1, 4):
                        fecha_alt = fecha + pd.Timedelta(days=offset)
                        hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha_alt]
                        if len(hist_data) > 0:
                            break
                
                if len(hist_data) > 0:
                    vix_dia = hist_data.iloc[0]['vix']
                    retorno_real = hist_data.iloc[0]['sp500_return_1d']
                    
                    # Validar datos
                    if pd.notna(vix_dia) and pd.notna(retorno_real):
                        # Impacto real (binario): ¿Se movió > 0.5%?
                        impacto_real = 1 if abs(retorno_real) > 0.005 else 0
                        
                        datos_opt.append({
                            'categoria': categoria,
                            'p_base': p_base,
                            'vix': float(vix_dia),
                            'impacto_real': impacto_real,
                            'retorno_real': float(retorno_real)
                        })
            except Exception as e:
                continue
        
        df_opt = pd.DataFrame(datos_opt)
        
        if len(df_opt) > 0:
            logger.info(f"\n✓ Dataset preparado: {len(df_opt)} observaciones")
            logger.info(f"  Impacto real (>0.5%): {df_opt['impacto_real'].sum()} eventos ({df_opt['impacto_real'].mean()*100:.1f}%)")
            logger.info(f"  Categorías únicas: {df_opt['categoria'].nunique()}")
            logger.info(f"  VIX promedio: {df_opt['vix'].mean():.1f}")
        else:
            logger.error("❌ No se pudieron preparar datos - verificar alineación de fechas")
        
        return df_opt
    
    def funcion_objetivo(self, params, df_opt):
        """
        Función objetivo para optimización
        
        Queremos maximizar el accuracy de predecir si hubo impacto real
        """
        alpha, beta = params
        
        # Calcular impacto contextual para cada observación
        impactos_pred = []
        
        for _, row in df_opt.iterrows():
            impacto = self.calcular_impacto_contextual(
                row['p_base'],
                row['vix'],
                alpha,
                beta
            )
            
            # Convertir a binario (>50% = predicción de impacto)
            pred_binario = 1 if impacto > 50 else 0
            impactos_pred.append(pred_binario)
        
        impactos_pred = np.array(impactos_pred)
        
        # Accuracy
        accuracy = (impactos_pred == df_opt['impacto_real'].values).mean()
        
        # También considerar precision y recall
        tp = ((impactos_pred == 1) & (df_opt['impacto_real'] == 1)).sum()
        fp = ((impactos_pred == 1) & (df_opt['impacto_real'] == 0)).sum()
        fn = ((impactos_pred == 0) & (df_opt['impacto_real'] == 1)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Función objetivo: maximizar F1-score
        return -f1  # Negativo porque vamos a minimizar
    
    def optimizar_bayesian(self, df_opt):
        """
        Usa Bayesian Optimization para encontrar α y β óptimos
        """
        logger.info("\n" + "="*70)
        logger.info("OPTIMIZACIÓN BAYESIANA")
        logger.info("="*70)
        logger.info("Buscando α y β óptimos...")
        
        try:
            from skopt import gp_minimize
            from skopt.space import Real
        except:
            logger.warning("  ⚠ scikit-optimize no instalado")
            logger.info("  Instalando...")
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scikit-optimize'])
            from skopt import gp_minimize
            from skopt.space import Real
        
        # Espacio de búsqueda
        space = [
            Real(0.1, 2.0, name='alpha'),   # α: amplificador
            Real(0.5, 3.0, name='beta'),    # β: exponente
        ]
        
        # Función a minimizar
        def objective(params):
            return self.funcion_objetivo(params, df_opt)
        
        # Optimizar
        logger.info("\n  Ejecutando optimización (50 iteraciones)...")
        resultado = gp_minimize(
            objective,
            space,
            n_calls=50,
            random_state=42,
            verbose=False
        )
        
        self.alpha = resultado.x[0]
        self.beta = resultado.x[1]
        
        logger.info(f"\n✓ PARÁMETROS ÓPTIMOS ENCONTRADOS:")
        logger.info(f"  α (alpha) = {self.alpha:.4f}")
        logger.info(f"  β (beta)  = {self.beta:.4f}")
        logger.info(f"  F1-score  = {-resultado.fun:.4f}")
        
        return self.alpha, self.beta, -resultado.fun
    
    def validar_modelo_refinado(self, df_opt):
        """
        Valida el modelo refinado vs modelo base
        """
        logger.info("\n" + "="*70)
        logger.info("VALIDACIÓN: MODELO REFINADO VS BASE")
        logger.info("="*70)
        
        # Split train/test
        n_test = int(len(df_opt) * 0.2)
        df_test = df_opt.iloc[-n_test:]
        
        # Predicciones modelo BASE (sin VIX)
        pred_base = (df_test['p_base'] > 50).astype(int)
        
        # Predicciones modelo REFINADO (con VIX)
        pred_refinado = []
        for _, row in df_test.iterrows():
            impacto = self.calcular_impacto_contextual(
                row['p_base'],
                row['vix'],
                self.alpha,
                self.beta
            )
            pred_refinado.append(1 if impacto > 50 else 0)
        
        pred_refinado = np.array(pred_refinado)
        
        # Métricas
        real = df_test['impacto_real'].values
        
        acc_base = (pred_base == real).mean()
        acc_refinado = (pred_refinado == real).mean()
        
        # F1-scores
        from sklearn.metrics import f1_score, precision_score, recall_score
        
        f1_base = f1_score(real, pred_base)
        f1_refinado = f1_score(real, pred_refinado)
        
        precision_base = precision_score(real, pred_base)
        precision_refinado = precision_score(real, pred_refinado)
        
        recall_base = recall_score(real, pred_base)
        recall_refinado = recall_score(real, pred_refinado)
        
        logger.info("\n📊 RESULTADOS:")
        logger.info("─"*70)
        logger.info(f"{'Métrica':<20s} | {'Modelo Base':>15s} | {'Modelo Refinado':>15s} | {'Mejora':>10s}")
        logger.info("─"*70)
        logger.info(f"{'Accuracy':<20s} | {acc_base:>14.2%} | {acc_refinado:>14.2%} | {(acc_refinado-acc_base)*100:>9.1f}%")
        logger.info(f"{'Precision':<20s} | {precision_base:>14.2%} | {precision_refinado:>14.2%} | {(precision_refinado-precision_base)*100:>9.1f}%")
        logger.info(f"{'Recall':<20s} | {recall_base:>14.2%} | {recall_refinado:>14.2%} | {(recall_refinado-recall_base)*100:>9.1f}%")
        logger.info(f"{'F1-Score':<20s} | {f1_base:>14.2%} | {f1_refinado:>14.2%} | {(f1_refinado-f1_base)*100:>9.1f}%")
        logger.info("─"*70)
        
        mejora = (acc_refinado - acc_base) * 100
        if mejora > 0:
            logger.info(f"\n✓ Modelo refinado es {mejora:.1f}% MEJOR")
        else:
            logger.info(f"\n⚠ Modelo base sigue siendo mejor")
        
        return {
            'accuracy_base': acc_base,
            'accuracy_refinado': acc_refinado,
            'f1_base': f1_base,
            'f1_refinado': f1_refinado,
            'mejora_accuracy': mejora
        }
    
    def analizar_efecto_vix_por_categoria(self, df_opt):
        """
        Analiza cómo el VIX afecta cada categoría diferente
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS: EFECTO VIX POR CATEGORÍA")
        logger.info("="*70)
        
        resultados = []
        
        for categoria in df_opt['categoria'].unique():
            df_cat = df_opt[df_opt['categoria'] == categoria]
            
            if len(df_cat) < 20:
                continue
            
            # Separar por VIX alto vs bajo
            vix_median = df_cat['vix'].median()
            
            df_vix_alto = df_cat[df_cat['vix'] > vix_median]
            df_vix_bajo = df_cat[df_cat['vix'] <= vix_median]
            
            # Tasa de impacto en cada caso
            tasa_alto = df_vix_alto['impacto_real'].mean()
            tasa_bajo = df_vix_bajo['impacto_real'].mean()
            
            # Amplificación
            amplificacion = (tasa_alto / tasa_bajo) if tasa_bajo > 0 else 1.0
            
            resultados.append({
                'categoria': categoria,
                'tasa_vix_bajo': tasa_bajo,
                'tasa_vix_alto': tasa_alto,
                'amplificacion': amplificacion,
                'n_eventos': len(df_cat)
            })
        
        df_resultados = pd.DataFrame(resultados).sort_values('amplificacion', ascending=False)
        
        logger.info("\nCATEGORÍAS MÁS AFECTADAS POR VIX ALTO:")
        logger.info("─"*70)
        logger.info(f"{'Categoría':<20s} | {'VIX Bajo':>10s} | {'VIX Alto':>10s} | {'Amplif':>8s}")
        logger.info("─"*70)
        
        for _, row in df_resultados.head(10).iterrows():
            logger.info(f"{row['categoria']:<20s} | {row['tasa_vix_bajo']:>9.1%} | "
                       f"{row['tasa_vix_alto']:>9.1%} | {row['amplificacion']:>7.2f}×")
        
        return df_resultados
    
    def predecir_con_contexto(self, noticia, categoria, vix_actual):
        """
        Predice usando el modelo refinado
        """
        # Obtener probabilidad base
        token_data = self.df_tokens[
            (self.df_tokens['categoria'] == categoria) & 
            (self.df_tokens['asset'] == 'SPY')
        ]
        
        if len(token_data) == 0:
            p_base = 30.0
            token = 1.0
        else:
            token = token_data.iloc[0]['token']
            p_base = (token / 10.0) * 100
        
        # Calcular impacto contextual
        p_contextual = self.calcular_impacto_contextual(
            p_base,
            vix_actual,
            self.alpha,
            self.beta
        )
        
        # Calcular ajuste
        v_norm = vix_actual / self.vix_critico
        ajuste = (p_contextual / p_base - 1) * 100 if p_base > 0 else 0
        
        return {
            'noticia': noticia,
            'categoria': categoria,
            'token': token,
            'probabilidad_base': p_base,
            'vix_actual': vix_actual,
            'vix_normalizado': v_norm,
            'probabilidad_contextual': p_contextual,
            'ajuste_por_vix': ajuste,
            'alpha': self.alpha,
            'beta': self.beta
        }
    
    def guardar_modelo(self):
        """Guarda el modelo refinado"""
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = MODELS_DIR / f"modelo_refinado_vix_{timestamp}.pkl"
        
        modelo = {
            'alpha': self.alpha,
            'beta': self.beta,
            'vix_critico': self.vix_critico,
            'df_tokens': self.df_tokens
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(modelo, f)
        
        logger.info(f"\n✓ Modelo refinado guardado: {filepath}")
        
        return filepath


def main():
    """Pipeline completo de refinamiento"""
    logger.info("="*70)
    logger.info("MODELO REFINADO CON VIX CONTEXTUAL")
    logger.info("="*70)
    logger.info("Bayesian Optimization para α y β óptimos")
    logger.info("")
    
    modelo = ModeloRefinadoVIX()
    
    # 1. Cargar datos
    logger.info("\n【FASE 1】 Cargando datos...")
    modelo.cargar_datos()
    
    # 2. Preparar datos para optimización
    logger.info("\n【FASE 2】 Preparando datos...")
    df_opt = modelo.preparar_datos_optimizacion()
    
    if len(df_opt) == 0:
        logger.error("\n❌ No hay datos suficientes para optimización")
        logger.info("Usando parámetros por defecto: α=0.75, β=1.50")
        modelo.alpha = 0.75
        modelo.beta = 1.50
        
        # Guardar modelo con valores por defecto
        modelo.guardar_modelo()
        
        logger.info("\n" + "="*70)
        logger.info("✓ MODELO CON PARÁMETROS POR DEFECTO")
        logger.info("="*70)
        logger.info(f"  α = {modelo.alpha:.4f}")
        logger.info(f"  β = {modelo.beta:.4f}")
        logger.info("\nEjemplos de uso:")
        
        ejemplos = [
            ("Fed raises rates", "fed_rates", 15),
            ("Fed raises rates", "fed_rates", 35),
        ]
        
        for noticia, cat, vix in ejemplos:
            pred = modelo.predecir_con_contexto(noticia, cat, vix)
            logger.info(f"\nNoticia: '{noticia}' (VIX={vix})")
            logger.info(f"  P_base: {pred['probabilidad_base']:.1f}%")
            logger.info(f"  P_contextual: {pred['probabilidad_contextual']:.1f}%")
            logger.info(f"  Ajuste: {pred['ajuste_por_vix']:+.1f}%")
        
        return
    
    # 3. Optimizar α y β
    logger.info("\n【FASE 3】 Optimización Bayesiana...")
    alpha, beta, f1_score = modelo.optimizar_bayesian(df_opt)
    
    # 4. Validar modelo
    logger.info("\n【FASE 4】 Validando modelo...")
    metricas = modelo.validar_modelo_refinado(df_opt)
    
    # 5. Analizar efecto VIX por categoría
    logger.info("\n【FASE 5】 Análisis por categoría...")
    df_efecto = modelo.analizar_efecto_vix_por_categoria(df_opt)
    
    # Guardar resultados
    output_dir = PROCESSED_DATA_DIR / "landau"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    df_efecto.to_csv(output_dir / f"efecto_vix_por_categoria_{timestamp}.csv", index=False)
    
    # 6. Guardar modelo
    logger.info("\n【FASE 6】 Guardando modelo...")
    modelo.guardar_modelo()
    
    # 7. Ejemplos de uso
    logger.info("\n【FASE 7】 Ejemplos de uso...")
    logger.info("="*70)
    
    ejemplos = [
        ("ECB cuts rates", "ecb_policy", 15),
        ("ECB cuts rates", "ecb_policy", 25),
        ("ECB cuts rates", "ecb_policy", 35),
        ("US GDP strong", "us_gdp_data", 15),
        ("US GDP strong", "us_gdp_data", 35),
    ]
    
    for noticia, cat, vix in ejemplos:
        pred = modelo.predecir_con_contexto(noticia, cat, vix)
        
        logger.info(f"\nNoticia: '{noticia}' (VIX={vix})")
        logger.info(f"  Token: {pred['token']:.1f}, P_base: {pred['probabilidad_base']:.1f}%")
        logger.info(f"  VIX normalizado: {pred['vix_normalizado']:.2f}")
        logger.info(f"  P_contextual: {pred['probabilidad_contextual']:.1f}%")
        logger.info(f"  Ajuste: {pred['ajuste_por_vix']:+.1f}%")
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ MODELO REFINADO COMPLETADO ✓✓✓")
    logger.info("="*70)
    logger.info(f"\nParámetros óptimos:")
    logger.info(f"  α = {alpha:.4f}")
    logger.info(f"  β = {beta:.4f}")
    logger.info(f"\nMejora sobre modelo base: {metricas['mejora_accuracy']:+.1f}%")


if __name__ == "__main__":
    main()


Usa Bayesian Optimization para encontrar α y β óptimos

Fórmula:
Impacto_Contextual = P_impacto × (1 + α × (V_miedo - 1)^β)

Donde:
- P_impacto: Probabilidad base del token
- V_miedo: VIX normalizado (VIX/VIX_crítico)
- α: Amplificador del efecto miedo
- β: Exponente no-lineal (captura "polvorín")
"""
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


class ModeloRefinadoVIX:
    """
    Modelo refinado que considera el contexto de miedo del mercado
    """
    
    def __init__(self):
        # Parámetros a optimizar
        self.alpha = None  # Amplificador
        self.beta = None   # Exponente no-lineal
        
        # VIX de referencia (temperatura crítica)
        self.vix_critico = 20.0
        
        # Datos históricos
        self.df_tokens = None
        self.df_noticias = None
        self.df_historico = None
        
        logger.info("✓ ModeloRefinadoVIX inicializado")
    
    def cargar_datos(self):
        """Carga todos los datos necesarios"""
        logger.info("\n" + "="*70)
        logger.info("CARGANDO DATOS PARA OPTIMIZACIÓN")
        logger.info("="*70)
        
        # 1. Tokens
        token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
        if token_files:
            self.df_tokens = pd.read_csv(token_files[0])
            logger.info(f"  ✓ Tokens: {len(self.df_tokens)} combinaciones")
        
        # 2. Parámetros históricos (con VIX)
        hist_files = list(PROCESSED_DATA_DIR.glob("landau/parametros_landau_historicos_*.csv"))
        if hist_files:
            self.df_historico = pd.read_csv(hist_files[0])
            self.df_historico['fecha'] = pd.to_datetime(self.df_historico['fecha'])
            logger.info(f"  ✓ Histórico: {len(self.df_historico)} días")
        
        # 3. Noticias clasificadas (necesitamos recrearlas)
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        df_combined = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
        df_combined['Date'] = pd.to_datetime(df_combined['Date'])
        
        # Expandir noticias
        noticias = []
        for idx, row in df_combined.iterrows():
            for i in range(1, 26):
                noticia = row.get(f'Top{i}')
                if pd.notna(noticia) and noticia != '':
                    noticias.append({
                        'fecha': row['Date'],
                        'titulo': noticia
                    })
        
        self.df_noticias = pd.DataFrame(noticias)
        logger.info(f"  ✓ Noticias: {len(self.df_noticias)}")
        
        # 4. Clasificar noticias (simplificado)
        self.clasificar_noticias_rapido()
        
        return True
    
    def clasificar_noticias_rapido(self):
        """Clasificación rápida de noticias"""
        categorias = {
            'ecb_policy': ['ecb', 'draghi', 'lagarde'],
            'fed_rates': ['fed', 'fomc', 'interest rate'],
            'us_gdp_data': ['gdp'],
            'us_employment_data': ['employment', 'jobs', 'unemployment'],
            'terrorism': ['terror', 'bombing', 'attack'],
            'war_russia': ['russia', 'ukraine', 'putin'],
            'war_middle_east': ['iran', 'iraq', 'syria', 'israel'],
            'financial_crisis': ['crisis', 'crash', 'panic'],
        }
        
        self.df_noticias['categoria'] = 'other'
        
        for idx, row in self.df_noticias.iterrows():
            titulo = str(row['titulo']).lower()
            for cat, keywords in categorias.items():
                if any(kw in titulo for kw in keywords):
                    self.df_noticias.at[idx, 'categoria'] = cat
                    break
    
    def calcular_impacto_contextual(self, p_impacto, vix_actual, alpha, beta):
        """
        Calcula impacto contextual considerando VIX
        
        Fórmula:
        Impacto = P_base × (1 + α × (V_normalizado - 1)^β)
        
        Args:
            p_impacto: Probabilidad base (del token)
            vix_actual: VIX del día
            alpha: Amplificador
            beta: Exponente no-lineal
        """
        # Normalizar VIX
        v_normalizado = vix_actual / self.vix_critico
        
        # Aplicar fórmula
        if v_normalizado <= 1.0:
            # VIX bajo - efecto mínimo
            impacto = p_impacto * (1.0 - alpha * 0.1 * (1 - v_normalizado))
        else:
            # VIX alto - efecto polvorín
            impacto = p_impacto * (1.0 + alpha * ((v_normalizado - 1.0) ** beta))
        
        # Limitar entre 0 y 100
        impacto = max(0, min(100, impacto))
        
        return impacto
    
    def preparar_datos_optimizacion(self):
        """
        Prepara dataset para optimizar α y β
        
        Para cada noticia histórica:
        - P_impacto (del token)
        - VIX ese día
        - Impacto REAL (si movió el mercado o no)
        """
        logger.info("\n" + "="*70)
        logger.info("PREPARANDO DATOS PARA OPTIMIZACIÓN")
        logger.info("="*70)
        
        # Normalizar fechas del histórico (eliminar timezone)
        self.df_historico['fecha_norm'] = pd.to_datetime([str(d).split()[0] for d in self.df_historico['fecha']])
        
        datos_opt = []
        
        # Para cada noticia
        for idx, row in self.df_noticias.iterrows():
            if idx % 10000 == 0:
                logger.info(f"  Procesando: {idx}/{len(self.df_noticias)}")
            
            fecha = pd.Timestamp(row['fecha']).normalize()
            categoria = row['categoria']
            
            if categoria == 'other':
                continue
            
            # Buscar token de esa categoría
            token_data = self.df_tokens[
                (self.df_tokens['categoria'] == categoria) & 
                (self.df_tokens['asset'] == 'SPY')
            ]
            
            if len(token_data) == 0:
                continue
            
            # Probabilidad base
            token = token_data.iloc[0]['token']
            p_base = (token / 10.0) * 100
            
            # Buscar VIX y retorno real ese día (con búsqueda en rango)
            try:
                # Buscar fecha exacta
                hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha]
                
                if len(hist_data) == 0:
                    # Buscar en ventana de ±3 días
                    for offset in range(1, 4):
                        fecha_alt = fecha + pd.Timedelta(days=offset)
                        hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha_alt]
                        if len(hist_data) > 0:
                            break
                
                if len(hist_data) > 0:
                    vix_dia = hist_data.iloc[0]['vix']
                    retorno_real = hist_data.iloc[0]['sp500_return_1d']
                    
                    # Validar datos
                    if pd.notna(vix_dia) and pd.notna(retorno_real):
                        # Impacto real (binario): ¿Se movió > 0.5%?
                        impacto_real = 1 if abs(retorno_real) > 0.005 else 0
                        
                        datos_opt.append({
                            'categoria': categoria,
                            'p_base': p_base,
                            'vix': float(vix_dia),
                            'impacto_real': impacto_real,
                            'retorno_real': float(retorno_real)
                        })
            except Exception as e:
                continue
        
        df_opt = pd.DataFrame(datos_opt)
        
        if len(df_opt) > 0:
            logger.info(f"\n✓ Dataset preparado: {len(df_opt)} observaciones")
            logger.info(f"  Impacto real (>0.5%): {df_opt['impacto_real'].sum()} eventos ({df_opt['impacto_real'].mean()*100:.1f}%)")
            logger.info(f"  Categorías únicas: {df_opt['categoria'].nunique()}")
            logger.info(f"  VIX promedio: {df_opt['vix'].mean():.1f}")
        else:
            logger.error("❌ No se pudieron preparar datos - verificar alineación de fechas")
        
        return df_opt
    
    def funcion_objetivo(self, params, df_opt):
        """
        Función objetivo para optimización
        
        Queremos maximizar el accuracy de predecir si hubo impacto real
        """
        alpha, beta = params
        
        # Calcular impacto contextual para cada observación
        impactos_pred = []
        
        for _, row in df_opt.iterrows():
            impacto = self.calcular_impacto_contextual(
                row['p_base'],
                row['vix'],
                alpha,
                beta
            )
            
            # Convertir a binario (>50% = predicción de impacto)
            pred_binario = 1 if impacto > 50 else 0
            impactos_pred.append(pred_binario)
        
        impactos_pred = np.array(impactos_pred)
        
        # Accuracy
        accuracy = (impactos_pred == df_opt['impacto_real'].values).mean()
        
        # También considerar precision y recall
        tp = ((impactos_pred == 1) & (df_opt['impacto_real'] == 1)).sum()
        fp = ((impactos_pred == 1) & (df_opt['impacto_real'] == 0)).sum()
        fn = ((impactos_pred == 0) & (df_opt['impacto_real'] == 1)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Función objetivo: maximizar F1-score
        return -f1  # Negativo porque vamos a minimizar
    
    def optimizar_bayesian(self, df_opt):
        """
        Usa Bayesian Optimization para encontrar α y β óptimos
        """
        logger.info("\n" + "="*70)
        logger.info("OPTIMIZACIÓN BAYESIANA")
        logger.info("="*70)
        logger.info("Buscando α y β óptimos...")
        
        try:
            from skopt import gp_minimize
            from skopt.space import Real
        except:
            logger.warning("  ⚠ scikit-optimize no instalado")
            logger.info("  Instalando...")
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scikit-optimize'])
            from skopt import gp_minimize
            from skopt.space import Real
        
        # Espacio de búsqueda
        space = [
            Real(0.1, 2.0, name='alpha'),   # α: amplificador
            Real(0.5, 3.0, name='beta'),    # β: exponente
        ]
        
        # Función a minimizar
        def objective(params):
            return self.funcion_objetivo(params, df_opt)
        
        # Optimizar
        logger.info("\n  Ejecutando optimización (50 iteraciones)...")
        resultado = gp_minimize(
            objective,
            space,
            n_calls=50,
            random_state=42,
            verbose=False
        )
        
        self.alpha = resultado.x[0]
        self.beta = resultado.x[1]
        
        logger.info(f"\n✓ PARÁMETROS ÓPTIMOS ENCONTRADOS:")
        logger.info(f"  α (alpha) = {self.alpha:.4f}")
        logger.info(f"  β (beta)  = {self.beta:.4f}")
        logger.info(f"  F1-score  = {-resultado.fun:.4f}")
        
        return self.alpha, self.beta, -resultado.fun
    
    def validar_modelo_refinado(self, df_opt):
        """
        Valida el modelo refinado vs modelo base
        """
        logger.info("\n" + "="*70)
        logger.info("VALIDACIÓN: MODELO REFINADO VS BASE")
        logger.info("="*70)
        
        # Split train/test
        n_test = int(len(df_opt) * 0.2)
        df_test = df_opt.iloc[-n_test:]
        
        # Predicciones modelo BASE (sin VIX)
        pred_base = (df_test['p_base'] > 50).astype(int)
        
        # Predicciones modelo REFINADO (con VIX)
        pred_refinado = []
        for _, row in df_test.iterrows():
            impacto = self.calcular_impacto_contextual(
                row['p_base'],
                row['vix'],
                self.alpha,
                self.beta
            )
            pred_refinado.append(1 if impacto > 50 else 0)
        
        pred_refinado = np.array(pred_refinado)
        
        # Métricas
        real = df_test['impacto_real'].values
        
        acc_base = (pred_base == real).mean()
        acc_refinado = (pred_refinado == real).mean()
        
        # F1-scores
        from sklearn.metrics import f1_score, precision_score, recall_score
        
        f1_base = f1_score(real, pred_base)
        f1_refinado = f1_score(real, pred_refinado)
        
        precision_base = precision_score(real, pred_base)
        precision_refinado = precision_score(real, pred_refinado)
        
        recall_base = recall_score(real, pred_base)
        recall_refinado = recall_score(real, pred_refinado)
        
        logger.info("\n📊 RESULTADOS:")
        logger.info("─"*70)
        logger.info(f"{'Métrica':<20s} | {'Modelo Base':>15s} | {'Modelo Refinado':>15s} | {'Mejora':>10s}")
        logger.info("─"*70)
        logger.info(f"{'Accuracy':<20s} | {acc_base:>14.2%} | {acc_refinado:>14.2%} | {(acc_refinado-acc_base)*100:>9.1f}%")
        logger.info(f"{'Precision':<20s} | {precision_base:>14.2%} | {precision_refinado:>14.2%} | {(precision_refinado-precision_base)*100:>9.1f}%")
        logger.info(f"{'Recall':<20s} | {recall_base:>14.2%} | {recall_refinado:>14.2%} | {(recall_refinado-recall_base)*100:>9.1f}%")
        logger.info(f"{'F1-Score':<20s} | {f1_base:>14.2%} | {f1_refinado:>14.2%} | {(f1_refinado-f1_base)*100:>9.1f}%")
        logger.info("─"*70)
        
        mejora = (acc_refinado - acc_base) * 100
        if mejora > 0:
            logger.info(f"\n✓ Modelo refinado es {mejora:.1f}% MEJOR")
        else:
            logger.info(f"\n⚠ Modelo base sigue siendo mejor")
        
        return {
            'accuracy_base': acc_base,
            'accuracy_refinado': acc_refinado,
            'f1_base': f1_base,
            'f1_refinado': f1_refinado,
            'mejora_accuracy': mejora
        }
    
    def analizar_efecto_vix_por_categoria(self, df_opt):
        """
        Analiza cómo el VIX afecta cada categoría diferente
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS: EFECTO VIX POR CATEGORÍA")
        logger.info("="*70)
        
        resultados = []
        
        for categoria in df_opt['categoria'].unique():
            df_cat = df_opt[df_opt['categoria'] == categoria]
            
            if len(df_cat) < 20:
                continue
            
            # Separar por VIX alto vs bajo
            vix_median = df_cat['vix'].median()
            
            df_vix_alto = df_cat[df_cat['vix'] > vix_median]
            df_vix_bajo = df_cat[df_cat['vix'] <= vix_median]
            
            # Tasa de impacto en cada caso
            tasa_alto = df_vix_alto['impacto_real'].mean()
            tasa_bajo = df_vix_bajo['impacto_real'].mean()
            
            # Amplificación
            amplificacion = (tasa_alto / tasa_bajo) if tasa_bajo > 0 else 1.0
            
            resultados.append({
                'categoria': categoria,
                'tasa_vix_bajo': tasa_bajo,
                'tasa_vix_alto': tasa_alto,
                'amplificacion': amplificacion,
                'n_eventos': len(df_cat)
            })
        
        df_resultados = pd.DataFrame(resultados).sort_values('amplificacion', ascending=False)
        
        logger.info("\nCATEGORÍAS MÁS AFECTADAS POR VIX ALTO:")
        logger.info("─"*70)
        logger.info(f"{'Categoría':<20s} | {'VIX Bajo':>10s} | {'VIX Alto':>10s} | {'Amplif':>8s}")
        logger.info("─"*70)
        
        for _, row in df_resultados.head(10).iterrows():
            logger.info(f"{row['categoria']:<20s} | {row['tasa_vix_bajo']:>9.1%} | "
                       f"{row['tasa_vix_alto']:>9.1%} | {row['amplificacion']:>7.2f}×")
        
        return df_resultados
    
    def predecir_con_contexto(self, noticia, categoria, vix_actual):
        """
        Predice usando el modelo refinado
        """
        # Obtener probabilidad base
        token_data = self.df_tokens[
            (self.df_tokens['categoria'] == categoria) & 
            (self.df_tokens['asset'] == 'SPY')
        ]
        
        if len(token_data) == 0:
            p_base = 30.0
            token = 1.0
        else:
            token = token_data.iloc[0]['token']
            p_base = (token / 10.0) * 100
        
        # Calcular impacto contextual
        p_contextual = self.calcular_impacto_contextual(
            p_base,
            vix_actual,
            self.alpha,
            self.beta
        )
        
        # Calcular ajuste
        v_norm = vix_actual / self.vix_critico
        ajuste = (p_contextual / p_base - 1) * 100 if p_base > 0 else 0
        
        return {
            'noticia': noticia,
            'categoria': categoria,
            'token': token,
            'probabilidad_base': p_base,
            'vix_actual': vix_actual,
            'vix_normalizado': v_norm,
            'probabilidad_contextual': p_contextual,
            'ajuste_por_vix': ajuste,
            'alpha': self.alpha,
            'beta': self.beta
        }
    
    def guardar_modelo(self):
        """Guarda el modelo refinado"""
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = MODELS_DIR / f"modelo_refinado_vix_{timestamp}.pkl"
        
        modelo = {
            'alpha': self.alpha,
            'beta': self.beta,
            'vix_critico': self.vix_critico,
            'df_tokens': self.df_tokens
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(modelo, f)
        
        logger.info(f"\n✓ Modelo refinado guardado: {filepath}")
        
        return filepath


def main():
    """Pipeline completo de refinamiento"""
    logger.info("="*70)
    logger.info("MODELO REFINADO CON VIX CONTEXTUAL")
    logger.info("="*70)
    logger.info("Bayesian Optimization para α y β óptimos")
    logger.info("")
    
    modelo = ModeloRefinadoVIX()
    
    # 1. Cargar datos
    logger.info("\n【FASE 1】 Cargando datos...")
    modelo.cargar_datos()
    
    # 2. Preparar datos para optimización
    logger.info("\n【FASE 2】 Preparando datos...")
    df_opt = modelo.preparar_datos_optimizacion()
    
    if len(df_opt) == 0:
        logger.error("\n❌ No hay datos suficientes para optimización")
        logger.info("Usando parámetros por defecto: α=0.75, β=1.50")
        modelo.alpha = 0.75
        modelo.beta = 1.50
        
        # Guardar modelo con valores por defecto
        modelo.guardar_modelo()
        
        logger.info("\n" + "="*70)
        logger.info("✓ MODELO CON PARÁMETROS POR DEFECTO")
        logger.info("="*70)
        logger.info(f"  α = {modelo.alpha:.4f}")
        logger.info(f"  β = {modelo.beta:.4f}")
        logger.info("\nEjemplos de uso:")
        
        ejemplos = [
            ("Fed raises rates", "fed_rates", 15),
            ("Fed raises rates", "fed_rates", 35),
        ]
        
        for noticia, cat, vix in ejemplos:
            pred = modelo.predecir_con_contexto(noticia, cat, vix)
            logger.info(f"\nNoticia: '{noticia}' (VIX={vix})")
            logger.info(f"  P_base: {pred['probabilidad_base']:.1f}%")
            logger.info(f"  P_contextual: {pred['probabilidad_contextual']:.1f}%")
            logger.info(f"  Ajuste: {pred['ajuste_por_vix']:+.1f}%")
        
        return
    
    # 3. Optimizar α y β
    logger.info("\n【FASE 3】 Optimización Bayesiana...")
    alpha, beta, f1_score = modelo.optimizar_bayesian(df_opt)
    
    # 4. Validar modelo
    logger.info("\n【FASE 4】 Validando modelo...")
    metricas = modelo.validar_modelo_refinado(df_opt)
    
    # 5. Analizar efecto VIX por categoría
    logger.info("\n【FASE 5】 Análisis por categoría...")
    df_efecto = modelo.analizar_efecto_vix_por_categoria(df_opt)
    
    # Guardar resultados
    output_dir = PROCESSED_DATA_DIR / "landau"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    df_efecto.to_csv(output_dir / f"efecto_vix_por_categoria_{timestamp}.csv", index=False)
    
    # 6. Guardar modelo
    logger.info("\n【FASE 6】 Guardando modelo...")
    modelo.guardar_modelo()
    
    # 7. Ejemplos de uso
    logger.info("\n【FASE 7】 Ejemplos de uso...")
    logger.info("="*70)
    
    ejemplos = [
        ("ECB cuts rates", "ecb_policy", 15),
        ("ECB cuts rates", "ecb_policy", 25),
        ("ECB cuts rates", "ecb_policy", 35),
        ("US GDP strong", "us_gdp_data", 15),
        ("US GDP strong", "us_gdp_data", 35),
    ]
    
    for noticia, cat, vix in ejemplos:
        pred = modelo.predecir_con_contexto(noticia, cat, vix)
        
        logger.info(f"\nNoticia: '{noticia}' (VIX={vix})")
        logger.info(f"  Token: {pred['token']:.1f}, P_base: {pred['probabilidad_base']:.1f}%")
        logger.info(f"  VIX normalizado: {pred['vix_normalizado']:.2f}")
        logger.info(f"  P_contextual: {pred['probabilidad_contextual']:.1f}%")
        logger.info(f"  Ajuste: {pred['ajuste_por_vix']:+.1f}%")
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ MODELO REFINADO COMPLETADO ✓✓✓")
    logger.info("="*70)
    logger.info(f"\nParámetros óptimos:")
    logger.info(f"  α = {alpha:.4f}")
    logger.info(f"  β = {beta:.4f}")
    logger.info(f"\nMejora sobre modelo base: {metricas['mejora_accuracy']:+.1f}%")


if __name__ == "__main__":
    main()

