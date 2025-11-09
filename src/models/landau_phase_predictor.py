"""
Modelo de Transiciones de Fase de Landau para Predicción de Mercados
Basado en teoría de transiciones de fase aplicada a economía

Concepto:
- VIX = Temperatura del sistema
- Noticias = Campo externo
- Parámetro φ = Estado del mercado
- Transiciones de fase = Cambios de régimen (bull/bear)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import pickle
import sys
from pathlib import Path
from sklearn.metrics import mean_absolute_error, r2_score

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


class LandauPhasePredictor:
    """
    Predictor basado en transiciones de fase de Landau
    """
    
    def __init__(self):
        # Tokens calculados desde datos históricos
        self.tokens_historicos = {}
        
        # Parámetros del modelo
        self.lambda_decay = 0.1  # Decaimiento temporal
        self.horizonte_dias = [1, 7, 30]  # Horizontes de predicción
        
        # Umbrales de transición
        self.umbral_critico = 2.0
        self.vix_critico = 25.0  # VIX crítico (temperatura crítica)
        
        # Históricos
        self.phi_history = []
        self.predictions_history = []
        
        logger.info("✓ LandauPhasePredictor inicializado")
    
    def cargar_noticias_kaggle(self):
        """
        Carga noticias de Kaggle y las procesa
        """
        logger.info("\n" + "="*70)
        logger.info("CARGANDO NOTICIAS DE KAGGLE")
        logger.info("="*70)
        
        # Cargar Combined_News_DJIA
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        
        try:
            # Archivo principal de noticias
            df_news = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
            logger.info(f"  ✓ Combined_News_DJIA.csv cargado: {df_news.shape}")
            
            # Archivo de Reddit
            try:
                df_reddit = pd.read_csv(kaggle_dir / "RedditNews.csv")
                logger.info(f"  ✓ RedditNews.csv cargado: {df_reddit.shape}")
            except:
                df_reddit = None
                logger.warning("  ⚠ RedditNews.csv no disponible")
            
            # Archivo de DJIA
            try:
                df_djia = pd.read_csv(kaggle_dir / "upload_DJIA_table.csv")
                logger.info(f"  ✓ upload_DJIA_table.csv cargado: {df_djia.shape}")
            except:
                df_djia = None
                logger.warning("  ⚠ upload_DJIA_table.csv no disponible")
            
            return df_news, df_reddit, df_djia
            
        except Exception as e:
            logger.error(f"Error al cargar noticias: {e}")
            return None, None, None
    
    def procesar_noticias_kaggle(self, df_news, df_djia):
        """
        Procesa noticias de Kaggle y las estructura
        """
        logger.info("\n" + "="*70)
        logger.info("PROCESANDO NOTICIAS DE KAGGLE")
        logger.info("="*70)
        
        # Convertir fecha
        df_news['Date'] = pd.to_datetime(df_news['Date'])
        
        # El dataset tiene 25 columnas de noticias (Top1 a Top25)
        # Combinar todas las noticias por día
        noticias_por_dia = []
        
        for idx, row in df_news.iterrows():
            fecha = row['Date']
            
            # Extraer todas las noticias del día
            for i in range(1, 26):
                col_name = f'Top{i}'
                if col_name in df_news.columns:
                    noticia = row[col_name]
                    if pd.notna(noticia) and noticia != '':
                        noticias_por_dia.append({
                            'fecha': fecha,
                            'titulo': noticia,
                            'rank': i
                        })
        
        df_procesado = pd.DataFrame(noticias_por_dia)
        logger.info(f"  ✓ Noticias procesadas: {len(df_procesado)} noticias individuales")
        logger.info(f"  ✓ Días cubiertos: {df_procesado['fecha'].nunique()}")
        logger.info(f"  ✓ Período: {df_procesado['fecha'].min()} a {df_procesado['fecha'].max()}")
        
        # Agregar datos de mercado si disponibles
        if df_djia is not None:
            df_djia['Date'] = pd.to_datetime(df_djia['Date'])
            df_procesado = df_procesado.merge(
                df_djia[['Date', 'Open', 'Close']],
                left_on='fecha',
                right_on='Date',
                how='left'
            )
            df_procesado['market_return'] = (df_procesado['Close'] - df_procesado['Open']) / df_procesado['Open']
            logger.info(f"  ✓ Datos de mercado agregados")
        
        return df_procesado
    
    def clasificar_noticias_por_tipo(self, df_noticias):
        """
        Clasifica noticias en categorías usando keywords
        """
        logger.info("\n" + "="*70)
        logger.info("CLASIFICANDO NOTICIAS POR TIPO")
        logger.info("="*70)
        
        # Categorías y keywords
        categorias = {
            'fed_monetary': ['fed', 'federal reserve', 'interest rate', 'monetary policy', 'fomc', 'powell'],
            'inflation': ['inflation', 'cpi', 'pce', 'deflation', 'price index'],
            'employment': ['employment', 'jobs', 'unemployment', 'jobless', 'payroll', 'nfp'],
            'gdp_growth': ['gdp', 'growth', 'economic growth', 'expansion', 'recession'],
            'earnings': ['earnings', 'profit', 'revenue', 'beat', 'miss'],
            'oil_energy': ['oil', 'crude', 'opec', 'energy', 'petroleum', 'gas price'],
            'china_economy': ['china', 'chinese', 'yuan', 'pboc', 'beijing'],
            'europe_economy': ['europe', 'ecb', 'euro', 'eurozone', 'draghi', 'lagarde'],
            'japan_economy': ['japan', 'yen', 'boj', 'tokyo', 'nikkei'],
            'geopolitical': ['war', 'conflict', 'sanctions', 'trade war', 'tariff'],
            'financial_crisis': ['crisis', 'crash', 'panic', 'meltdown', 'collapse', 'bailout'],
            'tech_sector': ['tech', 'apple', 'google', 'microsoft', 'amazon', 'facebook'],
            'banking': ['bank', 'banking', 'credit', 'lending', 'mortgage'],
            'trade': ['trade', 'export', 'import', 'trade deficit', 'trade surplus'],
            'housing': ['housing', 'real estate', 'home sales', 'mortgage'],
            'consumer': ['consumer', 'retail', 'spending', 'sales'],
        }
        
        # Clasificar cada noticia
        df_noticias['categoria'] = 'other'
        
        for idx, row in df_noticias.iterrows():
            titulo = str(row['titulo']).lower()
            
            for categoria, keywords in categorias.items():
                if any(keyword in titulo for keyword in keywords):
                    df_noticias.at[idx, 'categoria'] = categoria
                    break
        
        # Estadísticas
        logger.info("\nDistribución de noticias por categoría:")
        conteo = df_noticias['categoria'].value_counts()
        for cat, count in conteo.head(15).items():
            pct = (count / len(df_noticias)) * 100
            logger.info(f"  {cat:20s}: {count:5d} noticias ({pct:5.2f}%)")
        
        return df_noticias
    
    def calcular_impacto_real_por_categoria(self, df_noticias):
        """
        Calcula el impacto REAL de cada categoría en el mercado
        Esto determina los tokens óptimos
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO IMPACTO REAL POR CATEGORÍA")
        logger.info("="*70)
        logger.info("Analizando cómo cada tipo de noticia afectó históricamente...")
        
        # Agrupar por fecha y categoría
        noticias_por_dia = df_noticias.groupby(['fecha', 'categoria']).size().reset_index(name='count')
        
        # Cargar datos del S&P 500
        spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
        if not spy_files:
            logger.error("  No se encontró S&P 500. Usando market_return de Kaggle")
            # Usar retornos del dataset de Kaggle
            impacto_por_cat = df_noticias.groupby('categoria')['market_return'].agg([
                ('impacto_promedio', lambda x: x.abs().mean()),
                ('impacto_max', lambda x: x.abs().max()),
                ('count', 'count')
            ]).sort_values('impacto_promedio', ascending=False)
        else:
            # Cargar S&P 500
            spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
            df_spy = pd.read_csv(spy_file, index_col=0, parse_dates=True)
            df_spy['Return_1d'] = df_spy['Close'].pct_change()
            df_spy['Return_7d'] = df_spy['Close'].pct_change(periods=7)
            df_spy['Return_30d'] = df_spy['Close'].pct_change(periods=30)
            
            # Calcular impacto por categoría
            impactos = []
            
            for categoria in df_noticias['categoria'].unique():
                if categoria == 'other':
                    continue
                
                noticias_cat = df_noticias[df_noticias['categoria'] == categoria]
                
                impactos_1d = []
                impactos_7d = []
                impactos_30d = []
                
                for fecha in noticias_cat['fecha'].unique():
                    # Buscar retorno del S&P 500
                    try:
                        if fecha in df_spy.index:
                            impactos_1d.append(abs(df_spy.loc[fecha, 'Return_1d']))
                            
                            # 7 días después
                            fecha_7d = fecha + timedelta(days=7)
                            if fecha_7d in df_spy.index:
                                impactos_7d.append(abs(df_spy.loc[fecha_7d, 'Return_7d']))
                            
                            # 30 días después
                            fecha_30d = fecha + timedelta(days=30)
                            if fecha_30d in df_spy.index:
                                impactos_30d.append(abs(df_spy.loc[fecha_30d, 'Return_30d']))
                    except:
                        continue
                
                if impactos_1d:
                    impactos.append({
                        'categoria': categoria,
                        'impacto_1d': np.nanmean(impactos_1d),
                        'impacto_7d': np.nanmean(impactos_7d) if impactos_7d else 0,
                        'impacto_30d': np.nanmean(impactos_30d) if impactos_30d else 0,
                        'count': len(noticias_cat),
                        'impacto_max_1d': np.nanmax(impactos_1d) if impactos_1d else 0
                    })
            
            if impactos:
                impacto_por_cat = pd.DataFrame(impactos).sort_values('impacto_1d', ascending=False)
            else:
                logger.warning("No se pudieron calcular impactos. Usando valores por defecto")
                impacto_por_cat = pd.DataFrame({
                    'categoria': list(df_noticias['categoria'].unique()),
                    'impacto_1d': [0.01] * len(df_noticias['categoria'].unique()),
                    'count': [len(df_noticias[df_noticias['categoria'] == cat]) 
                             for cat in df_noticias['categoria'].unique()]
                })
        
        logger.info("\nIMPACTO REAL MEDIDO (ordenado por impacto):")
        logger.info("-"*70)
        logger.info(f"{'Categoría':<20s} | {'Impacto 1d':>12s} | {'Impacto 7d':>12s} | {'Count':>8s}")
        logger.info("-"*70)
        
        for _, row in impacto_por_cat.head(15).iterrows():
            logger.info(f"{row['categoria']:<20s} | {row.get('impacto_1d', 0):>11.4f}% | "
                       f"{row.get('impacto_7d', 0):>11.4f}% | {row['count']:>8d}")
        
        # Calcular tokens basados en impacto real
        self.calcular_tokens_desde_impacto(impacto_por_cat)
        
        return impacto_por_cat
    
    def calcular_tokens_desde_impacto(self, impacto_por_cat):
        """
        Calcula tokens óptimos basados en impacto histórico REAL
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO TOKENS ÓPTIMOS")
        logger.info("="*70)
        
        # Normalizar impactos para crear tokens
        if 'impacto_1d' in impacto_por_cat.columns:
            max_impacto = impacto_por_cat['impacto_1d'].max()
            
            for _, row in impacto_por_cat.iterrows():
                categoria = row['categoria']
                impacto = row.get('impacto_1d', 0)
                
                # Token proporcional al impacto (escala 1-10)
                token = 1.0 + (impacto / max_impacto) * 9.0
                
                self.tokens_historicos[categoria] = token
        
        # Tokens por defecto para categorías no vistas
        self.tokens_historicos['other'] = 1.0
        
        logger.info("\nTOKENS CALCULADOS (basados en impacto histórico real):")
        logger.info("-"*70)
        
        for cat, token in sorted(self.tokens_historicos.items(), key=lambda x: x[1], reverse=True)[:15]:
            logger.info(f"  {cat:<20s}: {token:6.2f}")
        
        return self.tokens_historicos
    
    def calcular_peso_temporal(self, dias_desde_noticia):
        """
        Decaimiento exponencial del peso de noticias
        Mayor peso a noticias recientes
        """
        if dias_desde_noticia <= 1:
            peso_base = 1.0    # Impacto inmediato
        elif dias_desde_noticia <= 7:
            peso_base = 0.7    # Impacto semanal
        elif dias_desde_noticia <= 30:
            peso_base = 0.4    # Impacto mensual
        else:
            peso_base = 0.1    # Impacto residual
        
        # Decaimiento exponencial
        return peso_base * np.exp(-self.lambda_decay * dias_desde_noticia)
    
    def calcular_parametro_orden(self, fecha, df_noticias, ventana_dias=30):
        """
        Calcula el parámetro de orden φ para una fecha
        
        φₜ = Σᵢ (tokenᵢ × peso_temporal × num_noticias_tipo_i)
        
        Args:
            fecha: Fecha objetivo
            df_noticias: DataFrame con noticias clasificadas
            ventana_dias: Días hacia atrás a considerar
            
        Returns:
            φ (parámetro de orden)
        """
        phi = 0.0
        contribuciones = defaultdict(float)
        
        # Normalizar fechas (eliminar timezone si existe)
        if hasattr(fecha, 'tz_localize'):
            fecha = fecha.tz_localize(None) if fecha.tzinfo else fecha
        elif hasattr(fecha, 'tzinfo') and fecha.tzinfo is not None:
            fecha = fecha.replace(tzinfo=None)
        
        # Ventana temporal
        fecha_inicio = fecha - timedelta(days=ventana_dias)
        
        # Asegurar que fechas en df_noticias no tienen timezone
        if 'fecha' in df_noticias.columns:
            if hasattr(df_noticias['fecha'].dtype, 'tz') and df_noticias['fecha'].dtype.tz is not None:
                df_noticias['fecha'] = df_noticias['fecha'].dt.tz_localize(None)
        
        # Filtrar noticias en ventana
        noticias_ventana = df_noticias[
            (df_noticias['fecha'] >= fecha_inicio) & 
            (df_noticias['fecha'] <= fecha)
        ]
        
        # Calcular contribución de cada noticia
        for _, noticia in noticias_ventana.iterrows():
            categoria = noticia['categoria']
            token = self.tokens_historicos.get(categoria, 1.0)
            
            # Días desde la noticia
            dias_desde = (fecha - noticia['fecha']).days
            peso = self.calcular_peso_temporal(dias_desde)
            
            # Contribución
            contribucion = token * peso
            phi += contribucion
            contribuciones[categoria] += contribucion
        
        return phi, dict(contribuciones)
    
    def calcular_parametros_historicos(self, df_noticias, df_mercado):
        """
        Calcula parámetros de orden para TODO el histórico
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO PARÁMETROS HISTÓRICOS")
        logger.info("="*70)
        
        resultados = []
        
        # Normalizar índice de mercado (eliminar timezone)
        if hasattr(df_mercado.index, 'tz_localize'):
            df_mercado.index = df_mercado.index.tz_localize(None)
        
        fechas = sorted(df_mercado.index.unique())
        
        logger.info(f"Procesando {len(fechas)} días...")
        
        for i, fecha in enumerate(fechas):
            if i % 100 == 0:
                logger.info(f"  Progreso: {i}/{len(fechas)} días ({i/len(fechas)*100:.1f}%)")
            
            # Calcular φ
            phi, contribuciones = self.calcular_parametro_orden(fecha, df_noticias)
            
            # φ del día anterior
            phi_anterior = resultados[-1]['phi'] if resultados else 0
            delta_phi = phi - phi_anterior
            
            # Temperatura (VIX)
            try:
                vix = df_mercado.loc[fecha, 'VIXCLS'] if 'VIXCLS' in df_mercado.columns else 20.0
            except:
                vix = 20.0
            
            # Retornos del S&P 500
            try:
                sp500_close = df_mercado.loc[fecha, 'Close']
                
                # Retorno 1 día
                if i > 0:
                    sp500_return_1d = (sp500_close - df_mercado.iloc[i-1]['Close']) / df_mercado.iloc[i-1]['Close']
                else:
                    sp500_return_1d = 0
                
                # Retorno 7 días
                if i >= 7:
                    sp500_return_7d = (sp500_close - df_mercado.iloc[i-7]['Close']) / df_mercado.iloc[i-7]['Close']
                else:
                    sp500_return_7d = 0
                
                # Retorno 30 días
                if i >= 30:
                    sp500_return_30d = (sp500_close - df_mercado.iloc[i-30]['Close']) / df_mercado.iloc[i-30]['Close']
                else:
                    sp500_return_30d = 0
                    
            except:
                sp500_return_1d = sp500_return_7d = sp500_return_30d = 0
            
            # Detectar transición
            transicion = self.detectar_transicion(phi, delta_phi, vix)
            
            resultados.append({
                'fecha': fecha,
                'phi': phi,
                'delta_phi': delta_phi,
                'vix': vix,
                'transicion': transicion,
                'sp500_return_1d': sp500_return_1d,
                'sp500_return_7d': sp500_return_7d,
                'sp500_return_30d': sp500_return_30d,
                **contribuciones  # Agregar contribuciones por categoría
            })
        
        df_resultados = pd.DataFrame(resultados)
        
        logger.info(f"\n✓ Parámetros históricos calculados: {len(df_resultados)} días")
        
        return df_resultados
    
    def detectar_transicion(self, phi, delta_phi, vix):
        """
        Detecta tipo de transición de fase
        
        Usa VIX como temperatura del sistema
        """
        # Normalizar por temperatura
        phi_efectivo = phi / (vix / self.vix_critico)
        
        if abs(delta_phi) > self.umbral_critico:
            if delta_phi > 0:
                if vix > 30:
                    return "TRANSICION_ALCISTA_VOLATIL"
                else:
                    return "TRANSICION_ALCISTA_ESTABLE"
            else:
                if vix > 30:
                    return "TRANSICION_BAJISTA_VOLATIL"
                else:
                    return "TRANSICION_BAJISTA_ESTABLE"
        else:
            if vix > 30:
                return "ESTABLE_ALTA_VOLATILIDAD"
            elif vix < 15:
                return "ESTABLE_BAJA_VOLATILIDAD"
            else:
                return "ESTABLE_NORMAL"
    
    def entrenar_modelo(self, df_historico):
        """
        Entrena el modelo con datos históricos
        Aprende la relación φ → retornos del mercado
        """
        logger.info("\n" + "="*70)
        logger.info("ENTRENANDO MODELO PREDICTIVO")
        logger.info("="*70)
        
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, r2_score
        
        # Preparar features
        features = ['phi', 'delta_phi', 'vix']
        
        # Agregar contribuciones por categoría como features
        categorias_features = [col for col in df_historico.columns 
                              if col not in ['fecha', 'sp500_return_1d', 'sp500_return_7d', 
                                           'sp500_return_30d', 'transicion']]
        categorias_features = [f for f in categorias_features if f not in features]
        
        features.extend(categorias_features[:10])  # Top 10 categorías
        
        X = df_historico[features].fillna(0)
        
        # Entrenar 3 modelos (1 día, 7 días, 30 días)
        self.models = {}
        
        for horizonte in ['1d', '7d', '30d']:
            logger.info(f"\n  Entrenando modelo para {horizonte}...")
            
            y = df_historico[f'sp500_return_{horizonte}'].fillna(0)
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Entrenar Random Forest
            model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            # Evaluar
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            logger.info(f"    MAE: {mae:.4f}")
            logger.info(f"    R²:  {r2:.4f}")
            
            # Feature importance
            importances = model.feature_importances_
            top_features = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)[:5]
            logger.info(f"    Top features:")
            for feat, imp in top_features:
                logger.info(f"      {feat}: {imp:.4f}")
            
            self.models[horizonte] = model
        
        logger.info("\n✓ Modelos entrenados")
        
        return self.models
    
    def predecir_siguiente_dia(self, fecha_actual, df_noticias_hoy, df_economicos):
        """
        Predice tendencia del día siguiente
        Usa noticias de hoy para generar parámetro de mañana
        """
        logger.info("\n" + "="*70)
        logger.info("PREDICCIÓN PARA DÍA SIGUIENTE")
        logger.info("="*70)
        logger.info(f"Fecha actual: {fecha_actual}")
        
        # 1. Calcular φ actual con noticias de hoy
        phi_hoy, contrib_hoy = self.calcular_parametro_orden(fecha_actual, df_noticias_hoy)
        
        # 2. φ promedio del mes anterior (referencia)
        fecha_mes_atras = fecha_actual - timedelta(days=30)
        phis_mes = []
        
        for i in range(30):
            fecha_ref = fecha_mes_atras + timedelta(days=i)
            phi_ref, _ = self.calcular_parametro_orden(fecha_ref, df_noticias_hoy)
            phis_mes.append(phi_ref)
        
        phi_promedio_mes = np.mean(phis_mes)
        
        # 3. Δφ respecto al mes anterior
        delta_phi = phi_hoy - phi_promedio_mes
        
        # 4. VIX actual (temperatura)
        try:
            vix_actual = df_economicos.loc[fecha_actual, 'VIXCLS']
        except:
            vix_actual = 20.0
        
        # 5. Detectar transición
        transicion = self.detectar_transicion(phi_hoy, delta_phi, vix_actual)
        
        # 6. Predecir con modelos
        # Crear DataFrame con TODAS las features que el modelo espera
        feature_names = list(self.models['1d'].feature_names_in_)
        
        # Inicializar TODOS los valores con 0 primero
        valores_pred = {feature: 0.0 for feature in feature_names}
        
        # Actualizar con valores reales
        valores_pred['phi'] = float(phi_hoy) if not np.isnan(phi_hoy) else 0.0
        valores_pred['delta_phi'] = float(delta_phi) if not np.isnan(delta_phi) else 0.0
        valores_pred['vix'] = float(vix_actual) if not np.isnan(vix_actual) else 20.0
        
        # Agregar contribuciones (desde contrib_hoy)
        for categoria, valor in contrib_hoy.items():
            if categoria in feature_names:
                # Asegurar que no sea NaN
                valores_pred[categoria] = float(valor) if not np.isnan(valor) else 0.0
        
        # Crear DataFrame en el orden correcto y asegurar que no hay NaN
        X_pred = pd.DataFrame([valores_pred], columns=feature_names)
        X_pred = X_pred.fillna(0.0)  # Doble seguridad contra NaN
        
        # Verificar que no haya NaN antes de predecir
        if X_pred.isnull().any().any():
            logger.warning("⚠ Detectados NaN en features, rellenando con 0")
            X_pred = X_pred.fillna(0.0)
        
        predicciones = {}
        for horizonte in ['1d', '7d', '30d']:
            pred = self.models[horizonte].predict(X_pred)[0]
            predicciones[horizonte] = pred
        
        # 7. Clasificar tendencia
        if predicciones['1d'] > 0.005:
            tendencia = "ALCISTA"
        elif predicciones['1d'] < -0.005:
            tendencia = "BAJISTA"
        else:
            tendencia = "NEUTRAL"
        
        logger.info(f"\nRESULTADOS:")
        logger.info(f"  φ hoy:          {phi_hoy:.2f}")
        logger.info(f"  φ mes anterior: {phi_promedio_mes:.2f}")
        logger.info(f"  Δφ:             {delta_phi:.2f}")
        logger.info(f"  VIX (temp):     {vix_actual:.2f}")
        logger.info(f"  Transición:     {transicion}")
        logger.info(f"  TENDENCIA:      {tendencia}")
        logger.info(f"\n  Predicciones:")
        logger.info(f"    1 día:   {predicciones['1d']:+.2%}")
        logger.info(f"    7 días:  {predicciones['7d']:+.2%}")
        logger.info(f"    30 días: {predicciones['30d']:+.2%}")
        
        return {
            'phi_hoy': phi_hoy,
            'phi_promedio_mes': phi_promedio_mes,
            'delta_phi': delta_phi,
            'vix': vix_actual,
            'transicion': transicion,
            'tendencia': tendencia,
            'predicciones': predicciones,
            'contribuciones': contrib_hoy
        }
    
    def validar_modelo(self, df_historico, n_dias_test=60):
        """
        Valida el modelo con últimos N días
        """
        logger.info("\n" + "="*70)
        logger.info("VALIDACIÓN DEL MODELO")
        logger.info("="*70)
        logger.info(f"Validando con últimos {n_dias_test} días...")
        
        # Separar train/test
        df_train = df_historico.iloc[:-n_dias_test]
        df_test = df_historico.iloc[-n_dias_test:]
        
        # Entrenar con train
        self.entrenar_modelo(df_train)
        
        # Obtener las features que el modelo espera (las que se usaron en entrenamiento)
        # El modelo guarda los nombres de features en feature_names_in_
        feature_names = self.models['1d'].feature_names_in_
        
        # Predecir test usando EXACTAMENTE las mismas features
        X_test = df_test[feature_names].fillna(0)
        
        resultados_validacion = {}
        
        for horizonte in ['1d', '7d', '30d']:
            y_test = df_test[f'sp500_return_{horizonte}']
            y_pred = self.models[horizonte].predict(X_test)
            
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Precisión direccional
            direccion_real = np.sign(y_test)
            direccion_pred = np.sign(y_pred)
            precision_direccional = (direccion_real == direccion_pred).mean()
            
            resultados_validacion[horizonte] = {
                'mae': mae,
                'r2': r2,
                'precision_direccional': precision_direccional
            }
            
            logger.info(f"\n  {horizonte}:")
            logger.info(f"    MAE: {mae:.4f}")
            logger.info(f"    R²:  {r2:.4f}")
            logger.info(f"    Precisión direccional: {precision_direccional:.2%}")
        
        return resultados_validacion
    
    def guardar_modelo(self, filepath=None):
        """
        Guarda el modelo entrenado
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d')
            filepath = MODELS_DIR / f"landau_phase_model_{timestamp}.pkl"
        
        modelo_completo = {
            'tokens_historicos': self.tokens_historicos,
            'models': self.models,
            'lambda_decay': self.lambda_decay,
            'umbral_critico': self.umbral_critico,
            'vix_critico': self.vix_critico
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(modelo_completo, f)
        
        logger.info(f"\n✓ Modelo guardado: {filepath}")
        
        return filepath


def main():
    """Pipeline completo del modelo de Landau"""
    logger.info("="*70)
    logger.info("MODELO DE TRANSICIONES DE FASE DE LANDAU")
    logger.info("="*70)
    logger.info("Predicción de mercados basada en física estadística")
    logger.info("")
    
    # Crear predictor
    predictor = LandauPhasePredictor()
    
    # 1. Cargar noticias de Kaggle
    logger.info("\n【FASE 1】 Cargando datos...")
    df_news_raw, df_reddit, df_djia = predictor.cargar_noticias_kaggle()
    
    if df_news_raw is None:
        logger.error("No se pudieron cargar noticias de Kaggle")
        return
        
    # 2. Procesar noticias
    logger.info("\n【FASE 2】 Procesando noticias...")
    df_noticias = predictor.procesar_noticias_kaggle(df_news_raw, df_djia)
    
    # 3. Clasificar por tipo
    logger.info("\n【FASE 3】 Clasificando noticias...")
    df_noticias = predictor.clasificar_noticias_por_tipo(df_noticias)
    
    # 4. Calcular impacto real
    logger.info("\n【FASE 4】 Calculando impacto real...")
    impacto_por_cat = predictor.calcular_impacto_real_por_categoria(df_noticias)
    
    # 5. Cargar datos del S&P 500
    logger.info("\n【FASE 5】 Cargando S&P 500...")
    spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
    if spy_files:
        spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
        df_spy = pd.read_csv(spy_file, index_col=0, parse_dates=True)
        logger.info(f"  ✓ S&P 500 cargado: {len(df_spy)} días")
    else:
        logger.error("  No se encontró S&P 500")
        return
        
    # 6. Cargar VIX
    logger.info("\n【FASE 6】 Cargando VIX (temperatura)...")
    vix_files = list(PROCESSED_DATA_DIR.glob("fred/fred_alto_impacto_*.csv"))
    if vix_files:
        df_vix = pd.read_csv(vix_files[0], index_col=0, parse_dates=True)
        df_spy = df_spy.join(df_vix[['VIXCLS']], how='left')
        logger.info(f"  ✓ VIX agregado al dataset")
    
    # 7. Calcular parámetros históricos
    logger.info("\n【FASE 7】 Calculando parámetros históricos...")
    df_historico = predictor.calcular_parametros_historicos(df_noticias, df_spy)
    
    # Guardar histórico
    processed_dir = PROCESSED_DATA_DIR / "landau"
    processed_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    filepath_hist = processed_dir / f"parametros_landau_historicos_{timestamp}.csv"
    df_historico.to_csv(filepath_hist, index=False)
    logger.info(f"  ✓ Histórico guardado: {filepath_hist.name}")
    
    # 8. Entrenar modelo
    logger.info("\n【FASE 8】 Entrenando modelo...")
    predictor.entrenar_modelo(df_historico)
    
    # 9. Validar
    logger.info("\n【FASE 9】 Validando modelo...")
    resultados_val = predictor.validar_modelo(df_historico, n_dias_test=60)
    
    # 10. Predicción para mañana
    logger.info("\n【FASE 10】 Generando predicción para mañana...")
    fecha_hoy = df_spy.index[-1]
    prediccion_manana = predictor.predecir_siguiente_dia(
        fecha_hoy, 
        df_noticias,
        df_spy
    )
    
    # 11. Guardar modelo
    logger.info("\n【FASE 11】 Guardando modelo...")
    predictor.guardar_modelo()
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ MODELO COMPLETO DE LANDAU CREADO ✓✓✓")
    logger.info("="*70)
    logger.info("\nEl modelo está listo para:")
    logger.info("  1. Predecir tendencias (alcista/bajista)")
    logger.info("  2. Detectar transiciones de fase")
    logger.info("  3. Usar VIX como temperatura del sistema")
    logger.info("  4. Tokens optimizados por impacto real")
    logger.info("  5. Predicciones en 3 horizontes (1d, 7d, 30d)")


if __name__ == "__main__":
    main()
