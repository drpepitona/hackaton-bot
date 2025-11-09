"""
Modelo Refinado con VIX Contextual - Por Categoría
Optimiza α y β específicos para CADA tipo de noticia

HIPÓTESIS:
- Noticias de guerra/terror: β alto (efecto polvorín extremo)
- Noticias Fed/ECB: α y β moderados
- Noticias housing/earnings: α bajo (poco efecto VIX)
"""
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


class ModeloRefinadoVIXCategorias:
    """
    Modelo que optimiza α y β por categoría de noticia
    """
    
    def __init__(self):
        # Parámetros por categoría
        self.params_por_categoria = {}
        
        # VIX crítico
        self.vix_critico = 20.0
        
        # Datos
        self.df_tokens = None
        self.df_noticias = None
        self.df_historico = None
        
        logger.info("✓ ModeloRefinadoVIXCategorias inicializado")
    
    def cargar_datos(self):
        """Carga todos los datos necesarios"""
        logger.info("\n" + "="*70)
        logger.info("CARGANDO DATOS")
        logger.info("="*70)
        
        # Tokens
        token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
        if token_files:
            self.df_tokens = pd.read_csv(token_files[0])
            logger.info(f"  ✓ Tokens: {len(self.df_tokens)} combinaciones")
        
        # Histórico
        hist_files = list(PROCESSED_DATA_DIR.glob("landau/parametros_landau_historicos_*.csv"))
        if hist_files:
            self.df_historico = pd.read_csv(hist_files[0])
            self.df_historico['fecha'] = pd.to_datetime(self.df_historico['fecha'])
            self.df_historico['fecha_norm'] = pd.to_datetime([str(d).split()[0] for d in self.df_historico['fecha']])
            logger.info(f"  ✓ Histórico: {len(self.df_historico)} días")
        
        # Noticias
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        df_combined = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
        df_combined['Date'] = pd.to_datetime(df_combined['Date'])
        
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
        
        self.clasificar_noticias_detallado()
        
        return True
    
    def clasificar_noticias_detallado(self):
        """Clasificación detallada con múltiples categorías"""
        categorias = {
            # ALTA VOLATILIDAD (esperamos β alto)
            'terrorism': ['terror', 'bombing', 'attack', 'killed'],
            'war_russia': ['russia', 'ukraine', 'putin', 'kremlin'],
            'war_middle_east': ['iran', 'iraq', 'syria', 'israel', 'palestine'],
            'financial_crisis': ['crisis', 'crash', 'panic', 'bailout', 'collapse'],
            
            # MEDIA-ALTA VOLATILIDAD (esperamos α y β moderado-alto)
            'fed_rates': ['fed', 'fomc', 'interest rate', 'federal reserve'],
            'ecb_policy': ['ecb', 'draghi', 'lagarde', 'european central bank'],
            'oil_shock': ['oil price', 'opec', 'crude', 'petroleum'],
            
            # MEDIA VOLATILIDAD (esperamos α y β moderado)
            'us_gdp_data': ['gdp', 'economic growth', 'gross domestic'],
            'us_employment_data': ['employment', 'jobs', 'unemployment', 'payroll'],
            'china_economy': ['china', 'beijing', 'yuan', 'chinese'],
            
            # BAJA VOLATILIDAD (esperamos α bajo, β bajo)
            'us_housing': ['housing', 'home sales', 'real estate'],
            'corporate_earnings': ['earnings', 'profit', 'quarterly results'],
            'trade_data': ['trade', 'exports', 'imports'],
        }
        
        self.df_noticias['categoria'] = 'other'
        
        for idx, row in self.df_noticias.iterrows():
            titulo = str(row['titulo']).lower()
            for cat, keywords in categorias.items():
                if any(kw in titulo for kw in keywords):
                    self.df_noticias.at[idx, 'categoria'] = cat
                    break
        
        # Estadísticas
        logger.info("\n  Distribución por categoría:")
        for cat in self.df_noticias['categoria'].value_counts().head(10).items():
            logger.info(f"    {cat[0]:<25s}: {cat[1]:>5,} noticias")
    
    def preparar_datos_por_categoria(self):
        """
        Prepara datasets separados por categoría
        """
        logger.info("\n" + "="*70)
        logger.info("PREPARANDO DATOS POR CATEGORÍA")
        logger.info("="*70)
        
        datos_por_categoria = {}
        
        categorias_validas = [c for c in self.df_noticias['categoria'].unique() if c != 'other']
        
        for categoria in categorias_validas:
            logger.info(f"\n  Procesando: {categoria}")
            
            df_cat = self.df_noticias[self.df_noticias['categoria'] == categoria]
            
            datos_opt = []
            
            # Buscar token
            token_data = self.df_tokens[
                (self.df_tokens['categoria'] == categoria) & 
                (self.df_tokens['asset'] == 'SPY')
            ]
            
            if len(token_data) == 0:
                logger.info(f"    ⚠ Sin token, saltando")
                continue
            
            token = token_data.iloc[0]['token']
            p_base = (token / 10.0) * 100
            
            # Para cada noticia de esta categoría
            for idx, row in df_cat.iterrows():
                fecha = pd.Timestamp(row['fecha']).normalize()
                
                # Buscar VIX y retorno
                hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha]
                
                if len(hist_data) == 0:
                    # Buscar en ventana
                    for offset in range(1, 4):
                        fecha_alt = fecha + pd.Timedelta(days=offset)
                        hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha_alt]
                        if len(hist_data) > 0:
                            break
                
                if len(hist_data) > 0:
                    vix_dia = hist_data.iloc[0]['vix']
                    retorno_real = hist_data.iloc[0]['sp500_return_1d']
                    
                    if pd.notna(vix_dia) and pd.notna(retorno_real):
                        impacto_real = 1 if abs(retorno_real) > 0.005 else 0
                        
                        datos_opt.append({
                            'p_base': p_base,
                            'vix': float(vix_dia),
                            'impacto_real': impacto_real,
                            'retorno_real': float(retorno_real)
                        })
            
            if len(datos_opt) >= 30:  # Mínimo 30 observaciones
                df_opt = pd.DataFrame(datos_opt)
                datos_por_categoria[categoria] = df_opt
                
                logger.info(f"    ✓ {len(df_opt)} observaciones")
                logger.info(f"      Impacto (>0.5%): {df_opt['impacto_real'].mean()*100:.1f}%")
                logger.info(f"      VIX promedio: {df_opt['vix'].mean():.1f}")
            else:
                logger.info(f"    ⚠ Solo {len(datos_opt)} obs, insuficiente")
        
        logger.info(f"\n✓ Total categorías con datos: {len(datos_por_categoria)}")
        
        return datos_por_categoria
    
    def calcular_impacto_contextual(self, p_base, vix, alpha, beta):
        """Calcula impacto con parámetros específicos"""
        v_norm = vix / self.vix_critico
        
        if v_norm <= 1.0:
            impacto = p_base * (1.0 - alpha * 0.1 * (1 - v_norm))
        else:
            impacto = p_base * (1.0 + alpha * ((v_norm - 1.0) ** beta))
        
        return max(0, min(100, impacto))
    
    def optimizar_categoria(self, categoria, df_cat):
        """
        Optimiza α y β para UNA categoría específica
        """
        logger.info(f"\n  Optimizando: {categoria}")
        
        try:
            from skopt import gp_minimize
            from skopt.space import Real
            from sklearn.metrics import f1_score
        except:
            logger.warning("    ⚠ scikit-optimize no instalado, usando grid search")
            return self.optimizar_categoria_grid(categoria, df_cat)
        
        # Función objetivo
        def objetivo(params):
            alpha, beta = params
            
            predictions = []
            for _, row in df_cat.iterrows():
                p_ctx = self.calcular_impacto_contextual(
                    row['p_base'],
                    row['vix'],
                    alpha,
                    beta
                )
                predictions.append(1 if p_ctx > 50 else 0)
            
            predictions = np.array(predictions)
            real = df_cat['impacto_real'].values
            
            # F1-score
            try:
                f1 = f1_score(real, predictions)
            except:
                f1 = 0.5
            
            return -f1
        
        # Espacio de búsqueda
        space = [
            Real(0.1, 2.5, name='alpha'),
            Real(0.5, 3.0, name='beta'),
        ]
        
        # Optimizar
        resultado = gp_minimize(
            objetivo,
            space,
            n_calls=30,  # 30 iteraciones por categoría
            random_state=42,
            verbose=False
        )
        
        alpha_opt = resultado.x[0]
        beta_opt = resultado.x[1]
        f1_opt = -resultado.fun
        
        logger.info(f"    ✓ α={alpha_opt:.3f}, β={beta_opt:.3f}, F1={f1_opt:.3f}")
        
        return {
            'alpha': alpha_opt,
            'beta': beta_opt,
            'f1_score': f1_opt,
            'n_obs': len(df_cat)
        }
    
    def optimizar_categoria_grid(self, categoria, df_cat):
        """Grid search como fallback"""
        from sklearn.metrics import f1_score
        
        mejor_f1 = 0
        mejor_params = {'alpha': 0.75, 'beta': 1.5}
        
        for alpha in [0.3, 0.5, 0.75, 1.0, 1.5]:
            for beta in [0.8, 1.0, 1.2, 1.5, 2.0]:
                predictions = []
                for _, row in df_cat.iterrows():
                    p_ctx = self.calcular_impacto_contextual(
                        row['p_base'],
                        row['vix'],
                        alpha,
                        beta
                    )
                    predictions.append(1 if p_ctx > 50 else 0)
                
                predictions = np.array(predictions)
                real = df_cat['impacto_real'].values
                
                try:
                    f1 = f1_score(real, predictions)
                    if f1 > mejor_f1:
                        mejor_f1 = f1
                        mejor_params = {'alpha': alpha, 'beta': beta}
                except:
                    pass
        
        logger.info(f"    ✓ α={mejor_params['alpha']:.3f}, β={mejor_params['beta']:.3f}, F1={mejor_f1:.3f}")
        
        return {
            'alpha': mejor_params['alpha'],
            'beta': mejor_params['beta'],
            'f1_score': mejor_f1,
            'n_obs': len(df_cat)
        }
    
    def optimizar_todas_categorias(self, datos_por_categoria):
        """
        Optimiza α y β para todas las categorías
        """
        logger.info("\n" + "="*70)
        logger.info("OPTIMIZACIÓN BAYESIANA POR CATEGORÍA")
        logger.info("="*70)
        
        for categoria, df_cat in datos_por_categoria.items():
            params = self.optimizar_categoria(categoria, df_cat)
            self.params_por_categoria[categoria] = params
        
        logger.info("\n✓ Optimización completada")
        logger.info(f"  Total categorías: {len(self.params_por_categoria)}")
    
    def analizar_parametros(self):
        """
        Analiza los parámetros encontrados por tipo de noticia
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS DE PARÁMETROS POR CATEGORÍA")
        logger.info("="*70)
        
        # Ordenar por β (efecto polvorín)
        categorias_sorted = sorted(
            self.params_por_categoria.items(),
            key=lambda x: x[1]['beta'],
            reverse=True
        )
        
        logger.info("\n🔥 RANKING POR EFECTO POLVORÍN (β):")
        logger.info("─"*70)
        logger.info(f"{'Categoría':<25s} | {'α':>6s} | {'β':>6s} | {'F1':>6s} | {'Obs':>6s}")
        logger.info("─"*70)
        
        for cat, params in categorias_sorted:
            logger.info(f"{cat:<25s} | {params['alpha']:>6.3f} | {params['beta']:>6.3f} | "
                       f"{params['f1_score']:>6.3f} | {params['n_obs']:>6,}")
        
        # Estadísticas
        betas = [p['beta'] for p in self.params_por_categoria.values()]
        alphas = [p['alpha'] for p in self.params_por_categoria.values()]
        
        logger.info("\n📊 ESTADÍSTICAS:")
        logger.info(f"  β promedio: {np.mean(betas):.3f}")
        logger.info(f"  β min-max: [{np.min(betas):.3f}, {np.max(betas):.3f}]")
        logger.info(f"  α promedio: {np.mean(alphas):.3f}")
        logger.info(f"  α min-max: [{np.min(alphas):.3f}, {np.max(alphas):.3f}]")
        
        # Clasificar categorías
        logger.info("\n🎯 CLASIFICACIÓN:")
        
        logger.info("\n  EFECTO POLVORÍN EXTREMO (β > 2.0):")
        for cat, params in categorias_sorted:
            if params['beta'] > 2.0:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
        
        logger.info("\n  EFECTO POLVORÍN ALTO (1.5 < β ≤ 2.0):")
        for cat, params in categorias_sorted:
            if 1.5 < params['beta'] <= 2.0:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
        
        logger.info("\n  EFECTO POLVORÍN MODERADO (1.0 < β ≤ 1.5):")
        for cat, params in categorias_sorted:
            if 1.0 < params['beta'] <= 1.5:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
        
        logger.info("\n  EFECTO POLVORÍN BAJO (β ≤ 1.0):")
        for cat, params in categorias_sorted:
            if params['beta'] <= 1.0:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
    
    def predecir_con_contexto(self, noticia, categoria, vix_actual):
        """
        Predice usando parámetros específicos de la categoría
        """
        # Buscar token
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
        
        # Usar parámetros de la categoría
        if categoria in self.params_por_categoria:
            params = self.params_por_categoria[categoria]
            alpha = params['alpha']
            beta = params['beta']
        else:
            # Parámetros por defecto
            alpha = 0.75
            beta = 1.50
        
        # Calcular impacto contextual
        p_contextual = self.calcular_impacto_contextual(
            p_base,
            vix_actual,
            alpha,
            beta
        )
        
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
            'alpha': alpha,
            'beta': beta
        }
    
    def guardar_modelo(self):
        """Guarda modelo con parámetros por categoría"""
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = MODELS_DIR / f"modelo_refinado_vix_categorias_{timestamp}.pkl"
        
        modelo = {
            'params_por_categoria': self.params_por_categoria,
            'vix_critico': self.vix_critico,
            'df_tokens': self.df_tokens
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(modelo, f)
        
        logger.info(f"\n✓ Modelo guardado: {filepath}")
        
        # También guardar JSON legible
        json_path = PROCESSED_DATA_DIR / "landau" / f"parametros_por_categoria_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(self.params_por_categoria, f, indent=2)
        
        logger.info(f"✓ Parámetros JSON: {json_path}")
        
        return filepath


def main():
    """Pipeline completo"""
    logger.info("="*70)
    logger.info("MODELO REFINADO VIX - POR CATEGORÍA")
    logger.info("="*70)
    logger.info("Optimiza α y β específicos para cada tipo de noticia")
    logger.info("")
    
    modelo = ModeloRefinadoVIXCategorias()
    
    # 1. Cargar datos
    logger.info("\n【FASE 1】 Cargando datos...")
    modelo.cargar_datos()
    
    # 2. Preparar datos por categoría
    logger.info("\n【FASE 2】 Preparando datos por categoría...")
    datos_por_categoria = modelo.preparar_datos_por_categoria()
    
    if len(datos_por_categoria) == 0:
        logger.error("\n❌ No hay datos suficientes")
        return
    
    # 3. Optimizar cada categoría
    logger.info("\n【FASE 3】 Optimización Bayesiana...")
    modelo.optimizar_todas_categorias(datos_por_categoria)
    
    # 4. Analizar parámetros
    logger.info("\n【FASE 4】 Análisis de parámetros...")
    modelo.analizar_parametros()
    
    # 5. Guardar modelo
    logger.info("\n【FASE 5】 Guardando modelo...")
    modelo.guardar_modelo()
    
    # 6. Ejemplos
    logger.info("\n【FASE 6】 Ejemplos de predicción...")
    logger.info("="*70)
    
    ejemplos = [
        ("Terrorist attack in Europe", "terrorism", 15),
        ("Terrorist attack in Europe", "terrorism", 35),
        ("Fed raises rates", "fed_rates", 15),
        ("Fed raises rates", "fed_rates", 35),
        ("Housing sales increase", "us_housing", 15),
        ("Housing sales increase", "us_housing", 35),
    ]
    
    for noticia, cat, vix in ejemplos:
        pred = modelo.predecir_con_contexto(noticia, cat, vix)
        
        logger.info(f"\n'{noticia}'")
        logger.info(f"  VIX={vix}, α={pred['alpha']:.2f}, β={pred['beta']:.2f}")
        logger.info(f"  P_base: {pred['probabilidad_base']:.1f}% → P_ctx: {pred['probabilidad_contextual']:.1f}% "
                   f"({pred['ajuste_por_vix']:+.1f}%)")
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ MODELO POR CATEGORÍAS COMPLETADO ✓✓✓")
    logger.info("="*70)


if __name__ == "__main__":
    main()

Modelo Refinado con VIX Contextual - Por Categoría
Optimiza α y β específicos para CADA tipo de noticia

HIPÓTESIS:
- Noticias de guerra/terror: β alto (efecto polvorín extremo)
- Noticias Fed/ECB: α y β moderados
- Noticias housing/earnings: α bajo (poco efecto VIX)
"""
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


class ModeloRefinadoVIXCategorias:
    """
    Modelo que optimiza α y β por categoría de noticia
    """
    
    def __init__(self):
        # Parámetros por categoría
        self.params_por_categoria = {}
        
        # VIX crítico
        self.vix_critico = 20.0
        
        # Datos
        self.df_tokens = None
        self.df_noticias = None
        self.df_historico = None
        
        logger.info("✓ ModeloRefinadoVIXCategorias inicializado")
    
    def cargar_datos(self):
        """Carga todos los datos necesarios"""
        logger.info("\n" + "="*70)
        logger.info("CARGANDO DATOS")
        logger.info("="*70)
        
        # Tokens
        token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
        if token_files:
            self.df_tokens = pd.read_csv(token_files[0])
            logger.info(f"  ✓ Tokens: {len(self.df_tokens)} combinaciones")
        
        # Histórico
        hist_files = list(PROCESSED_DATA_DIR.glob("landau/parametros_landau_historicos_*.csv"))
        if hist_files:
            self.df_historico = pd.read_csv(hist_files[0])
            self.df_historico['fecha'] = pd.to_datetime(self.df_historico['fecha'])
            self.df_historico['fecha_norm'] = pd.to_datetime([str(d).split()[0] for d in self.df_historico['fecha']])
            logger.info(f"  ✓ Histórico: {len(self.df_historico)} días")
        
        # Noticias
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        df_combined = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
        df_combined['Date'] = pd.to_datetime(df_combined['Date'])
        
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
        
        self.clasificar_noticias_detallado()
        
        return True
    
    def clasificar_noticias_detallado(self):
        """Clasificación detallada con múltiples categorías"""
        categorias = {
            # ALTA VOLATILIDAD (esperamos β alto)
            'terrorism': ['terror', 'bombing', 'attack', 'killed'],
            'war_russia': ['russia', 'ukraine', 'putin', 'kremlin'],
            'war_middle_east': ['iran', 'iraq', 'syria', 'israel', 'palestine'],
            'financial_crisis': ['crisis', 'crash', 'panic', 'bailout', 'collapse'],
            
            # MEDIA-ALTA VOLATILIDAD (esperamos α y β moderado-alto)
            'fed_rates': ['fed', 'fomc', 'interest rate', 'federal reserve'],
            'ecb_policy': ['ecb', 'draghi', 'lagarde', 'european central bank'],
            'oil_shock': ['oil price', 'opec', 'crude', 'petroleum'],
            
            # MEDIA VOLATILIDAD (esperamos α y β moderado)
            'us_gdp_data': ['gdp', 'economic growth', 'gross domestic'],
            'us_employment_data': ['employment', 'jobs', 'unemployment', 'payroll'],
            'china_economy': ['china', 'beijing', 'yuan', 'chinese'],
            
            # BAJA VOLATILIDAD (esperamos α bajo, β bajo)
            'us_housing': ['housing', 'home sales', 'real estate'],
            'corporate_earnings': ['earnings', 'profit', 'quarterly results'],
            'trade_data': ['trade', 'exports', 'imports'],
        }
        
        self.df_noticias['categoria'] = 'other'
        
        for idx, row in self.df_noticias.iterrows():
            titulo = str(row['titulo']).lower()
            for cat, keywords in categorias.items():
                if any(kw in titulo for kw in keywords):
                    self.df_noticias.at[idx, 'categoria'] = cat
                    break
        
        # Estadísticas
        logger.info("\n  Distribución por categoría:")
        for cat in self.df_noticias['categoria'].value_counts().head(10).items():
            logger.info(f"    {cat[0]:<25s}: {cat[1]:>5,} noticias")
    
    def preparar_datos_por_categoria(self):
        """
        Prepara datasets separados por categoría
        """
        logger.info("\n" + "="*70)
        logger.info("PREPARANDO DATOS POR CATEGORÍA")
        logger.info("="*70)
        
        datos_por_categoria = {}
        
        categorias_validas = [c for c in self.df_noticias['categoria'].unique() if c != 'other']
        
        for categoria in categorias_validas:
            logger.info(f"\n  Procesando: {categoria}")
            
            df_cat = self.df_noticias[self.df_noticias['categoria'] == categoria]
            
            datos_opt = []
            
            # Buscar token
            token_data = self.df_tokens[
                (self.df_tokens['categoria'] == categoria) & 
                (self.df_tokens['asset'] == 'SPY')
            ]
            
            if len(token_data) == 0:
                logger.info(f"    ⚠ Sin token, saltando")
                continue
            
            token = token_data.iloc[0]['token']
            p_base = (token / 10.0) * 100
            
            # Para cada noticia de esta categoría
            for idx, row in df_cat.iterrows():
                fecha = pd.Timestamp(row['fecha']).normalize()
                
                # Buscar VIX y retorno
                hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha]
                
                if len(hist_data) == 0:
                    # Buscar en ventana
                    for offset in range(1, 4):
                        fecha_alt = fecha + pd.Timedelta(days=offset)
                        hist_data = self.df_historico[self.df_historico['fecha_norm'] == fecha_alt]
                        if len(hist_data) > 0:
                            break
                
                if len(hist_data) > 0:
                    vix_dia = hist_data.iloc[0]['vix']
                    retorno_real = hist_data.iloc[0]['sp500_return_1d']
                    
                    if pd.notna(vix_dia) and pd.notna(retorno_real):
                        impacto_real = 1 if abs(retorno_real) > 0.005 else 0
                        
                        datos_opt.append({
                            'p_base': p_base,
                            'vix': float(vix_dia),
                            'impacto_real': impacto_real,
                            'retorno_real': float(retorno_real)
                        })
            
            if len(datos_opt) >= 30:  # Mínimo 30 observaciones
                df_opt = pd.DataFrame(datos_opt)
                datos_por_categoria[categoria] = df_opt
                
                logger.info(f"    ✓ {len(df_opt)} observaciones")
                logger.info(f"      Impacto (>0.5%): {df_opt['impacto_real'].mean()*100:.1f}%")
                logger.info(f"      VIX promedio: {df_opt['vix'].mean():.1f}")
            else:
                logger.info(f"    ⚠ Solo {len(datos_opt)} obs, insuficiente")
        
        logger.info(f"\n✓ Total categorías con datos: {len(datos_por_categoria)}")
        
        return datos_por_categoria
    
    def calcular_impacto_contextual(self, p_base, vix, alpha, beta):
        """Calcula impacto con parámetros específicos"""
        v_norm = vix / self.vix_critico
        
        if v_norm <= 1.0:
            impacto = p_base * (1.0 - alpha * 0.1 * (1 - v_norm))
        else:
            impacto = p_base * (1.0 + alpha * ((v_norm - 1.0) ** beta))
        
        return max(0, min(100, impacto))
    
    def optimizar_categoria(self, categoria, df_cat):
        """
        Optimiza α y β para UNA categoría específica
        """
        logger.info(f"\n  Optimizando: {categoria}")
        
        try:
            from skopt import gp_minimize
            from skopt.space import Real
            from sklearn.metrics import f1_score
        except:
            logger.warning("    ⚠ scikit-optimize no instalado, usando grid search")
            return self.optimizar_categoria_grid(categoria, df_cat)
        
        # Función objetivo
        def objetivo(params):
            alpha, beta = params
            
            predictions = []
            for _, row in df_cat.iterrows():
                p_ctx = self.calcular_impacto_contextual(
                    row['p_base'],
                    row['vix'],
                    alpha,
                    beta
                )
                predictions.append(1 if p_ctx > 50 else 0)
            
            predictions = np.array(predictions)
            real = df_cat['impacto_real'].values
            
            # F1-score
            try:
                f1 = f1_score(real, predictions)
            except:
                f1 = 0.5
            
            return -f1
        
        # Espacio de búsqueda
        space = [
            Real(0.1, 2.5, name='alpha'),
            Real(0.5, 3.0, name='beta'),
        ]
        
        # Optimizar
        resultado = gp_minimize(
            objetivo,
            space,
            n_calls=30,  # 30 iteraciones por categoría
            random_state=42,
            verbose=False
        )
        
        alpha_opt = resultado.x[0]
        beta_opt = resultado.x[1]
        f1_opt = -resultado.fun
        
        logger.info(f"    ✓ α={alpha_opt:.3f}, β={beta_opt:.3f}, F1={f1_opt:.3f}")
        
        return {
            'alpha': alpha_opt,
            'beta': beta_opt,
            'f1_score': f1_opt,
            'n_obs': len(df_cat)
        }
    
    def optimizar_categoria_grid(self, categoria, df_cat):
        """Grid search como fallback"""
        from sklearn.metrics import f1_score
        
        mejor_f1 = 0
        mejor_params = {'alpha': 0.75, 'beta': 1.5}
        
        for alpha in [0.3, 0.5, 0.75, 1.0, 1.5]:
            for beta in [0.8, 1.0, 1.2, 1.5, 2.0]:
                predictions = []
                for _, row in df_cat.iterrows():
                    p_ctx = self.calcular_impacto_contextual(
                        row['p_base'],
                        row['vix'],
                        alpha,
                        beta
                    )
                    predictions.append(1 if p_ctx > 50 else 0)
                
                predictions = np.array(predictions)
                real = df_cat['impacto_real'].values
                
                try:
                    f1 = f1_score(real, predictions)
                    if f1 > mejor_f1:
                        mejor_f1 = f1
                        mejor_params = {'alpha': alpha, 'beta': beta}
                except:
                    pass
        
        logger.info(f"    ✓ α={mejor_params['alpha']:.3f}, β={mejor_params['beta']:.3f}, F1={mejor_f1:.3f}")
        
        return {
            'alpha': mejor_params['alpha'],
            'beta': mejor_params['beta'],
            'f1_score': mejor_f1,
            'n_obs': len(df_cat)
        }
    
    def optimizar_todas_categorias(self, datos_por_categoria):
        """
        Optimiza α y β para todas las categorías
        """
        logger.info("\n" + "="*70)
        logger.info("OPTIMIZACIÓN BAYESIANA POR CATEGORÍA")
        logger.info("="*70)
        
        for categoria, df_cat in datos_por_categoria.items():
            params = self.optimizar_categoria(categoria, df_cat)
            self.params_por_categoria[categoria] = params
        
        logger.info("\n✓ Optimización completada")
        logger.info(f"  Total categorías: {len(self.params_por_categoria)}")
    
    def analizar_parametros(self):
        """
        Analiza los parámetros encontrados por tipo de noticia
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS DE PARÁMETROS POR CATEGORÍA")
        logger.info("="*70)
        
        # Ordenar por β (efecto polvorín)
        categorias_sorted = sorted(
            self.params_por_categoria.items(),
            key=lambda x: x[1]['beta'],
            reverse=True
        )
        
        logger.info("\n🔥 RANKING POR EFECTO POLVORÍN (β):")
        logger.info("─"*70)
        logger.info(f"{'Categoría':<25s} | {'α':>6s} | {'β':>6s} | {'F1':>6s} | {'Obs':>6s}")
        logger.info("─"*70)
        
        for cat, params in categorias_sorted:
            logger.info(f"{cat:<25s} | {params['alpha']:>6.3f} | {params['beta']:>6.3f} | "
                       f"{params['f1_score']:>6.3f} | {params['n_obs']:>6,}")
        
        # Estadísticas
        betas = [p['beta'] for p in self.params_por_categoria.values()]
        alphas = [p['alpha'] for p in self.params_por_categoria.values()]
        
        logger.info("\n📊 ESTADÍSTICAS:")
        logger.info(f"  β promedio: {np.mean(betas):.3f}")
        logger.info(f"  β min-max: [{np.min(betas):.3f}, {np.max(betas):.3f}]")
        logger.info(f"  α promedio: {np.mean(alphas):.3f}")
        logger.info(f"  α min-max: [{np.min(alphas):.3f}, {np.max(alphas):.3f}]")
        
        # Clasificar categorías
        logger.info("\n🎯 CLASIFICACIÓN:")
        
        logger.info("\n  EFECTO POLVORÍN EXTREMO (β > 2.0):")
        for cat, params in categorias_sorted:
            if params['beta'] > 2.0:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
        
        logger.info("\n  EFECTO POLVORÍN ALTO (1.5 < β ≤ 2.0):")
        for cat, params in categorias_sorted:
            if 1.5 < params['beta'] <= 2.0:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
        
        logger.info("\n  EFECTO POLVORÍN MODERADO (1.0 < β ≤ 1.5):")
        for cat, params in categorias_sorted:
            if 1.0 < params['beta'] <= 1.5:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
        
        logger.info("\n  EFECTO POLVORÍN BAJO (β ≤ 1.0):")
        for cat, params in categorias_sorted:
            if params['beta'] <= 1.0:
                logger.info(f"    • {cat}: β={params['beta']:.2f}")
    
    def predecir_con_contexto(self, noticia, categoria, vix_actual):
        """
        Predice usando parámetros específicos de la categoría
        """
        # Buscar token
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
        
        # Usar parámetros de la categoría
        if categoria in self.params_por_categoria:
            params = self.params_por_categoria[categoria]
            alpha = params['alpha']
            beta = params['beta']
        else:
            # Parámetros por defecto
            alpha = 0.75
            beta = 1.50
        
        # Calcular impacto contextual
        p_contextual = self.calcular_impacto_contextual(
            p_base,
            vix_actual,
            alpha,
            beta
        )
        
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
            'alpha': alpha,
            'beta': beta
        }
    
    def guardar_modelo(self):
        """Guarda modelo con parámetros por categoría"""
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = MODELS_DIR / f"modelo_refinado_vix_categorias_{timestamp}.pkl"
        
        modelo = {
            'params_por_categoria': self.params_por_categoria,
            'vix_critico': self.vix_critico,
            'df_tokens': self.df_tokens
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(modelo, f)
        
        logger.info(f"\n✓ Modelo guardado: {filepath}")
        
        # También guardar JSON legible
        json_path = PROCESSED_DATA_DIR / "landau" / f"parametros_por_categoria_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(self.params_por_categoria, f, indent=2)
        
        logger.info(f"✓ Parámetros JSON: {json_path}")
        
        return filepath


def main():
    """Pipeline completo"""
    logger.info("="*70)
    logger.info("MODELO REFINADO VIX - POR CATEGORÍA")
    logger.info("="*70)
    logger.info("Optimiza α y β específicos para cada tipo de noticia")
    logger.info("")
    
    modelo = ModeloRefinadoVIXCategorias()
    
    # 1. Cargar datos
    logger.info("\n【FASE 1】 Cargando datos...")
    modelo.cargar_datos()
    
    # 2. Preparar datos por categoría
    logger.info("\n【FASE 2】 Preparando datos por categoría...")
    datos_por_categoria = modelo.preparar_datos_por_categoria()
    
    if len(datos_por_categoria) == 0:
        logger.error("\n❌ No hay datos suficientes")
        return
    
    # 3. Optimizar cada categoría
    logger.info("\n【FASE 3】 Optimización Bayesiana...")
    modelo.optimizar_todas_categorias(datos_por_categoria)
    
    # 4. Analizar parámetros
    logger.info("\n【FASE 4】 Análisis de parámetros...")
    modelo.analizar_parametros()
    
    # 5. Guardar modelo
    logger.info("\n【FASE 5】 Guardando modelo...")
    modelo.guardar_modelo()
    
    # 6. Ejemplos
    logger.info("\n【FASE 6】 Ejemplos de predicción...")
    logger.info("="*70)
    
    ejemplos = [
        ("Terrorist attack in Europe", "terrorism", 15),
        ("Terrorist attack in Europe", "terrorism", 35),
        ("Fed raises rates", "fed_rates", 15),
        ("Fed raises rates", "fed_rates", 35),
        ("Housing sales increase", "us_housing", 15),
        ("Housing sales increase", "us_housing", 35),
    ]
    
    for noticia, cat, vix in ejemplos:
        pred = modelo.predecir_con_contexto(noticia, cat, vix)
        
        logger.info(f"\n'{noticia}'")
        logger.info(f"  VIX={vix}, α={pred['alpha']:.2f}, β={pred['beta']:.2f}")
        logger.info(f"  P_base: {pred['probabilidad_base']:.1f}% → P_ctx: {pred['probabilidad_contextual']:.1f}% "
                   f"({pred['ajuste_por_vix']:+.1f}%)")
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ MODELO POR CATEGORÍAS COMPLETADO ✓✓✓")
    logger.info("="*70)


if __name__ == "__main__":
    main()



