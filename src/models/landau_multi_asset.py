"""
Modelo de Landau Multi-Asset
Calcula tokens específicos por (categoría, asset) basados en impacto histórico REAL

Características:
- Usa TODAS las noticias disponibles (Combined + Reddit)
- Calcula impacto en múltiples activos (S&P 500, Forex, Commodities)
- Tokens NO arbitrarios, sino calculados de datos reales
- Detecta qué tipo de noticias afecta más a qué activo
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import pickle
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


class LandauMultiAsset:
    """
    Modelo de Landau extendido para múltiples activos
    """
    
    def __init__(self):
        # Tokens calculados: {(categoria, asset): token_value}
        self.tokens_por_asset = {}
        
        # Assets a analizar
        self.assets = [
            'SPY',      # S&P 500
            'USDJPY',   # USD/JPY
            'EURUSD',   # EUR/USD
            'USDCNY',   # USD/CNY
            'AUDUSD',   # AUD/USD
            'WTI',      # Petróleo
            'GOLD',     # Oro
        ]
        
        # Categorías granulares
        self.categorias = {
            # Geopolítica
            'war_conflict': ['war', 'conflict', 'military', 'attack', 'strike', 'invasion'],
            'terrorism': ['terror', 'bombing', 'attack', 'isis', 'threat'],
            'trade_war': ['trade war', 'tariff', 'sanctions', 'embargo'],
            
            # Fed y Política Monetaria
            'fed_rates': ['fed', 'federal reserve', 'interest rate', 'fomc', 'powell', 'yellen', 'bernanke'],
            'ecb_policy': ['ecb', 'draghi', 'lagarde', 'european central bank'],
            'boj_policy': ['boj', 'bank of japan', 'kuroda'],
            'pboc_policy': ['pboc', 'people bank china', 'yuan'],
            
            # Economía USA
            'us_gdp': ['gdp', 'economic growth', 'expansion', 'recession'],
            'us_employment': ['employment', 'jobs', 'unemployment', 'nfp', 'payroll'],
            'us_inflation': ['inflation', 'cpi', 'pce', 'deflation'],
            'us_consumer': ['consumer confidence', 'retail sales', 'spending'],
            'us_housing': ['housing', 'home sales', 'real estate', 'mortgage'],
            
            # Economía Internacional
            'china_gdp': ['china gdp', 'china growth', 'china economy'],
            'china_trade': ['china export', 'china import', 'china trade'],
            'europe_gdp': ['europe gdp', 'eurozone growth', 'eu economy'],
            'japan_gdp': ['japan gdp', 'japan economy', 'japanese growth'],
            
            # Mercados y Corporativo
            'earnings': ['earnings', 'profit', 'revenue', 'quarterly results'],
            'tech_sector': ['tech', 'apple', 'google', 'microsoft', 'amazon', 'facebook', 'tesla'],
            'financial_sector': ['bank', 'goldman', 'jpmorgan', 'wells fargo', 'citigroup'],
            
            # Commodities
            'oil_prices': ['oil', 'crude', 'wti', 'brent', 'opec', 'petroleum'],
            'gold_prices': ['gold', 'precious metals', 'safe haven'],
            'commodity_general': ['commodity', 'copper', 'iron', 'agriculture'],
            
            # Crisis y Eventos Especiales
            'financial_crisis': ['crisis', 'crash', 'panic', 'meltdown', 'bailout', 'lehman'],
            'brexit': ['brexit', 'uk referendum', 'leave eu'],
            'elections': ['election', 'vote', 'president', 'congress', 'senate'],
            
            # COVID (si hay datos)
            'pandemic': ['covid', 'coronavirus', 'pandemic', 'virus', 'lockdown'],
        }
        
        logger.info("✓ LandauMultiAsset inicializado")
    
    def cargar_todas_las_noticias(self):
        """
        Carga TODAS las noticias disponibles (Combined + Reddit)
        """
        logger.info("\n" + "="*70)
        logger.info("CARGANDO TODAS LAS NOTICIAS")
        logger.info("="*70)
        
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        
        # 1. Combined News
        df_combined = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
        df_combined['Date'] = pd.to_datetime(df_combined['Date'])
        logger.info(f"  ✓ Combined_News: {df_combined.shape}")
        logger.info(f"    Período: {df_combined['Date'].min()} a {df_combined['Date'].max()}")
        
        # Expandir las 25 columnas
        noticias_combined = []
        for idx, row in df_combined.iterrows():
            fecha = row['Date']
            for i in range(1, 26):
                col_name = f'Top{i}'
                if col_name in df_combined.columns:
                    noticia = row[col_name]
                    if pd.notna(noticia) and noticia != '':
                        noticias_combined.append({
                            'fecha': fecha,
                            'titulo': noticia,
                            'fuente': 'combined',
                            'rank': i
                        })
        
        logger.info(f"  ✓ Noticias expandidas: {len(noticias_combined)}")
        
        # 2. Reddit News
        df_reddit = pd.read_csv(kaggle_dir / "RedditNews.csv")
        df_reddit['Date'] = pd.to_datetime(df_reddit['Date'])
        logger.info(f"  ✓ RedditNews: {df_reddit.shape}")
        logger.info(f"    Período: {df_reddit['Date'].min()} a {df_reddit['Date'].max()}")
        
        noticias_reddit = []
        for idx, row in df_reddit.iterrows():
            noticias_reddit.append({
                'fecha': row['Date'],
                'titulo': row['News'],
                'fuente': 'reddit',
                'rank': 0
            })
        
        logger.info(f"  ✓ Noticias Reddit: {len(noticias_reddit)}")
        
        # 3. Combinar todas
        todas_noticias = noticias_combined + noticias_reddit
        df_todas = pd.DataFrame(todas_noticias)
        df_todas = df_todas.sort_values('fecha')
        
        logger.info(f"\n✓ TOTAL NOTICIAS: {len(df_todas)} noticias")
        logger.info(f"✓ PERÍODO COMPLETO: {df_todas['fecha'].min()} a {df_todas['fecha'].max()}")
        logger.info(f"✓ DÍAS ÚNICOS: {df_todas['fecha'].nunique()}")
        
        return df_todas
    
    def clasificar_noticias_granular(self, df_noticias):
        """
        Clasifica noticias en categorías granulares
        """
        logger.info("\n" + "="*70)
        logger.info("CLASIFICACIÓN GRANULAR DE NOTICIAS")
        logger.info("="*70)
        
        df_noticias['categoria'] = 'other'
        
        for idx, row in df_noticias.iterrows():
            if idx % 10000 == 0:
                logger.info(f"  Progreso: {idx}/{len(df_noticias)} ({idx/len(df_noticias)*100:.1f}%)")
            
            titulo = str(row['titulo']).lower()
            
            # Buscar en categorías
            for categoria, keywords in self.categorias.items():
                if any(keyword in titulo for keyword in keywords):
                    df_noticias.at[idx, 'categoria'] = categoria
                    break
        
        # Estadísticas
        logger.info("\n" + "="*70)
        logger.info("DISTRIBUCIÓN POR CATEGORÍA (Top 20)")
        logger.info("="*70)
        
        conteo = df_noticias['categoria'].value_counts()
        for i, (cat, count) in enumerate(conteo.head(20).items()):
            pct = (count / len(df_noticias)) * 100
            logger.info(f"{i+1:2d}. {cat:25s}: {count:6d} ({pct:5.2f}%)")
        
        return df_noticias
    
    def cargar_datos_assets(self):
        """
        Carga datos históricos de todos los assets
        """
        logger.info("\n" + "="*70)
        logger.info("CARGANDO DATOS DE ASSETS")
        logger.info("="*70)
        
        assets_data = {}
        
        # 1. S&P 500 - Usar el histórico completo
        spy_files = list(RAW_DATA_DIR.glob("SPY_historico_completo_*.csv"))
        if not spy_files:
            spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
        
        if spy_files:
            spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
            df_spy = pd.read_csv(spy_file, index_col=0, parse_dates=True)
            df_spy['Return_1d'] = df_spy['Close'].pct_change()
            assets_data['SPY'] = df_spy
            logger.info(f"  ✓ SPY (S&P 500): {len(df_spy)} días")
            logger.info(f"    Período: {df_spy.index.min()} a {df_spy.index.max()}")
        
        # 2. Forex pairs from FRED
        fred_files = list(PROCESSED_DATA_DIR.glob("forex/forex_pares_historicos_*.csv"))
        if fred_files:
            df_forex = pd.read_csv(fred_files[0], index_col=0, parse_dates=True)
            
            # USD/JPY (DEXJPUS en FRED)
            if 'DEXJPUS' in df_forex.columns:
                df_usdjpy = df_forex[['DEXJPUS']].copy()
                df_usdjpy.columns = ['Close']
                df_usdjpy['Return_1d'] = df_usdjpy['Close'].pct_change()
                assets_data['USDJPY'] = df_usdjpy
                logger.info(f"  ✓ USD/JPY: {len(df_usdjpy)} días")
            
            # EUR/USD (DEXUSEU en FRED)
            if 'DEXUSEU' in df_forex.columns:
                df_eurusd = df_forex[['DEXUSEU']].copy()
                df_eurusd.columns = ['Close']
                df_eurusd['Return_1d'] = df_eurusd['Close'].pct_change()
                assets_data['EURUSD'] = df_eurusd
                logger.info(f"  ✓ EUR/USD: {len(df_eurusd)} días")
            
            # USD/CNY (DEXCHUS en FRED)
            if 'DEXCHUS' in df_forex.columns:
                df_usdcny = df_forex[['DEXCHUS']].copy()
                df_usdcny.columns = ['Close']
                df_usdcny['Return_1d'] = df_usdcny['Close'].pct_change()
                assets_data['USDCNY'] = df_usdcny
                logger.info(f"  ✓ USD/CNY: {len(df_usdcny)} días")
        
        # 3. Commodities
        # WTI Oil
        oil_files = list(PROCESSED_DATA_DIR.glob("fred/fred_oil_*.csv"))
        if oil_files:
            df_oil = pd.read_csv(oil_files[0], index_col=0, parse_dates=True)
            if 'DCOILWTICO' in df_oil.columns:
                df_oil['Close'] = df_oil['DCOILWTICO']
                df_oil['Return_1d'] = df_oil['Close'].pct_change()
                assets_data['WTI'] = df_oil
                logger.info(f"  ✓ WTI Oil: {len(df_oil)} días")
        
        logger.info(f"\n✓ Assets cargados: {list(assets_data.keys())}")
        
        return assets_data
    
    def calcular_tokens_por_asset(self, df_noticias, assets_data):
        """
        Calcula tokens específicos por (categoría, asset)
        Basado en impacto histórico REAL
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO TOKENS POR (CATEGORÍA, ASSET)")
        logger.info("="*70)
        logger.info("Midiendo impacto REAL de cada tipo de noticia en cada asset...")
        
        resultados = []
        
        categorias_unicas = df_noticias['categoria'].unique()
        logger.info(f"\nAnalizando {len(categorias_unicas)} categorías en {len(assets_data)} assets...")
        
        for categoria in categorias_unicas:
            if categoria == 'other':
                continue
            
            noticias_cat = df_noticias[df_noticias['categoria'] == categoria]
            
            if len(noticias_cat) == 0:
                continue
            
            logger.info(f"\n📊 {categoria} ({len(noticias_cat)} noticias):")
            
            for asset_name, df_asset in assets_data.items():
                impactos = []
                fechas_encontradas = 0
                fechas_noticias_sample = list(noticias_cat['fecha'].unique())[:5]
                
                # Normalizar índice del asset una vez (ELIMINAR timezone - MÉTODO DEFINITIVO)
                # Convertir a strings y luego a datetime sin timezone
                df_asset.index = pd.to_datetime([str(d).split()[0] for d in df_asset.index])
                asset_index = df_asset.index
                
                # Medir impacto en este asset
                for i, fecha_noticia in enumerate(noticias_cat['fecha'].unique()):
                    # Normalizar fecha de noticia (asegurar que no tiene timezone)
                    fecha = pd.Timestamp(fecha_noticia).normalize()
                    if hasattr(fecha, 'tz') and fecha.tz is not None:
                        fecha = fecha.replace(tzinfo=None)
                    
                    # Debug para primeras 3 fechas
                    if i < 3 and fechas_encontradas == 0:
                        pass  # logger.info(f"    DEBUG: Buscando {fecha} en {asset_name}")
                    
                    # Buscar el día de trading más cercano (en un rango de ±5 días)
                    encontrado = False
                    try:
                        # Método 1: Buscar fecha exacta
                        if fecha in asset_index:
                            retorno = abs(df_asset.loc[fecha, 'Return_1d'])
                            if not np.isnan(retorno) and retorno > 0:
                                impactos.append(retorno)
                                fechas_encontradas += 1
                                encontrado = True
                        
                        # Método 2: Si no encontró, buscar día más cercano
                        if not encontrado:
                            for offset in range(1, 6):
                                fecha_futura = fecha + timedelta(days=offset)
                                if fecha_futura in asset_index:
                                    retorno = abs(df_asset.loc[fecha_futura, 'Return_1d'])
                                    if not np.isnan(retorno) and retorno > 0:
                                        impactos.append(retorno)
                                        fechas_encontradas += 1
                                        break
                    except Exception as e:
                        if i < 3:
                            pass  # logger.warning(f"      Error: {e}")
                        continue
                
                if len(impactos) > 5:  # Mínimo 5 eventos para ser significativo
                    impacto_promedio = np.mean(impactos)
                    impacto_max = np.max(impactos)
                    num_eventos = len(impactos)
                    cobertura = (num_eventos / len(noticias_cat)) * 100
                    
                    resultados.append({
                        'categoria': categoria,
                        'asset': asset_name,
                        'impacto_promedio': impacto_promedio,
                        'impacto_max': impacto_max,
                        'num_eventos': num_eventos,
                        'num_noticias': len(noticias_cat),
                        'cobertura_pct': cobertura
                    })
                    
                    logger.info(f"  {asset_name:10s}: {impacto_promedio:7.4f} avg, {impacto_max:7.4f} max ({num_eventos}/{len(noticias_cat)} eventos = {cobertura:.1f}%)")
        
        # Crear DataFrame
        df_resultados = pd.DataFrame(resultados)
        
        if len(df_resultados) == 0:
            logger.error("\n❌ No se encontraron correlaciones entre noticias y activos")
            logger.error("    Posible problema de alineación de fechas")
            logger.error("\n🔍 DEBUG INFO:")
            logger.error(f"    - Categorías analizadas: {len(categorias_unicas)}")
            logger.error(f"    - Assets disponibles: {list(assets_data.keys())}")
            
            # Debug: Mostrar rango de fechas
            if len(df_noticias) > 0:
                logger.error(f"    - Rango noticias: {df_noticias['fecha'].min()} a {df_noticias['fecha'].max()}")
            for asset_name, df_asset in assets_data.items():
                logger.error(f"    - Rango {asset_name}: {df_asset.index.min()} a {df_asset.index.max()}")
            
            return df_resultados
        
        logger.info(f"\n✓ Encontradas {len(df_resultados)} correlaciones (categoría, asset)")
        
        # Calcular tokens normalizados por asset
        for asset in df_resultados['asset'].unique():
            df_asset_tokens = df_resultados[df_resultados['asset'] == asset]
            max_impacto = df_asset_tokens['impacto_promedio'].max()
            
            for idx in df_asset_tokens.index:
                categoria = df_resultados.loc[idx, 'categoria']
                impacto = df_resultados.loc[idx, 'impacto_promedio']
                
                # Token entre 1.0 y 10.0
                token = 1.0 + (impacto / max_impacto) * 9.0 if max_impacto > 0 else 1.0
                
                # Guardar token
                self.tokens_por_asset[(categoria, asset)] = token
                df_resultados.loc[idx, 'token'] = token
        
        # Guardar resultados
        output_dir = PROCESSED_DATA_DIR / "landau"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        output_file = output_dir / f"tokens_por_asset_{timestamp}.csv"
        df_resultados.to_csv(output_file, index=False)
        
        logger.info(f"\n✓ Tokens calculados para {len(self.tokens_por_asset)} combinaciones (categoría, asset)")
        logger.info(f"✓ Guardado en: {output_file}")
        
        return df_resultados
    
    def generar_matriz_impacto(self, df_tokens):
        """
        Genera matriz visual de impacto (categoría x asset)
        """
        logger.info("\n" + "="*70)
        logger.info("GENERANDO MATRIZ DE IMPACTO")
        logger.info("="*70)
        
        if len(df_tokens) == 0:
            logger.error("❌ No hay datos para generar matriz")
            return None
        
        # Pivot table
        pivot = df_tokens.pivot_table(
            index='categoria',
            columns='asset',
            values='token',
            fill_value=0
        )
        
        logger.info("\nMATRIZ DE TOKENS (Top 15 categorías):")
        logger.info("="*90)
        
        # Header
        header = "Categoría".ljust(25)
        for asset in pivot.columns:
            header += f" {asset:>8s}"
        logger.info(header)
        logger.info("-"*90)
        
        # Top 15 por impacto promedio
        pivot['promedio'] = pivot.mean(axis=1)
        pivot_top = pivot.sort_values('promedio', ascending=False).head(15)
        
        for categoria in pivot_top.index:
            row = categoria[:24].ljust(25)
            for asset in pivot.columns:
                if asset == 'promedio':
                    continue
                valor = pivot_top.loc[categoria, asset]
                row += f" {valor:8.2f}"
            logger.info(row)
        
        # Guardar matriz completa
        output_dir = PROCESSED_DATA_DIR / "landau"
        timestamp = datetime.now().strftime('%Y%m%d')
        output_file = output_dir / f"matriz_impacto_{timestamp}.csv"
        pivot.to_csv(output_file)
        
        logger.info(f"\n✓ Matriz completa guardada: {output_file}")
        
        return pivot


def main():
    """
    Pipeline completo de análisis multi-asset
    """
    logger.info("="*70)
    logger.info("MODELO DE LANDAU MULTI-ASSET")
    logger.info("="*70)
    logger.info("Análisis de impacto de noticias en múltiples activos")
    logger.info("")
    
    modelo = LandauMultiAsset()
    
    # 1. Cargar todas las noticias
    logger.info("\n【FASE 1】 Cargando noticias...")
    df_noticias = modelo.cargar_todas_las_noticias()
    
    # 2. Clasificar
    logger.info("\n【FASE 2】 Clasificando noticias...")
    df_noticias = modelo.clasificar_noticias_granular(df_noticias)
    
    # 3. Cargar assets
    logger.info("\n【FASE 3】 Cargando datos de assets...")
    assets_data = modelo.cargar_datos_assets()
    
    # 4. Calcular tokens por asset
    logger.info("\n【FASE 4】 Calculando tokens por asset...")
    df_tokens = modelo.calcular_tokens_por_asset(df_noticias, assets_data)
    
    # 5. Generar matriz de impacto
    if len(df_tokens) > 0:
        logger.info("\n【FASE 5】 Generando matriz de impacto...")
        matriz = modelo.generar_matriz_impacto(df_tokens)
        
        logger.info("\n" + "="*70)
        logger.info("✓✓✓ ANÁLISIS MULTI-ASSET COMPLETADO ✓✓✓")
        logger.info("="*70)
    else:
        logger.error("\n" + "="*70)
        logger.error("❌ NO SE PUDO COMPLETAR EL ANÁLISIS")
        logger.error("="*70)
        logger.error("\nNecesario: Verificar alineación de fechas entre noticias y datos de mercado")


if __name__ == "__main__":
    main()

