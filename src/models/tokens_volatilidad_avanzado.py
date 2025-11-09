"""
Sistema Avanzado de Tokens basado en Volatilidad
Distingue entre:
1. Impacto diario (noticias → apertura)
2. Impacto trimestral (Q1,Q2,Q3,Q4 → tendencias)
3. Impacto cruzado (desempleo → oro, petróleo → mercados)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.logger import logger


class TokensVolatilidadAvanzado:
    """
    Calcula tokens basados en volatilidad real
    """
    
    def __init__(self):
        self.tokens_diarios = {}      # (categoria, asset) → token_diario
        self.tokens_trimestrales = {} # (categoria, asset) → token_trimestral
        self.tokens_cruzados = {}     # (categoria_fuente, asset_impactado) → token
        
        # Assets principales
        self.assets_principales = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ',
            'DIA': 'Dow Jones',
            'IWM': 'Russell 2000'
        }
        
        # Categorías económicas (datos trimestrales)
        self.categorias_trimestrales = {
            'gdp': ['gdp', 'economic growth', 'recession', 'expansion'],
            'earnings': ['earnings', 'quarterly results', 'profit', 'revenue'],
            'consumer_spending': ['consumer spending', 'retail sales'],
        }
        
        # Categorías diarias
        self.categorias_diarias = {
            'fed_intraday': ['fed', 'fomc', 'powell speech'],
            'geopolitical': ['war', 'conflict', 'attack', 'strike'],
            'oil_shock': ['oil', 'opec', 'crude'],
            'employment': ['employment', 'jobs', 'unemployment', 'nfp'],
        }
        
        logger.info("✓ TokensVolatilidadAvanzado inicializado")
    
    def cargar_datos(self):
        """Carga todos los datos necesarios"""
        logger.info("\n" + "="*70)
        logger.info("CARGANDO DATOS PARA ANÁLISIS AVANZADO")
        logger.info("="*70)
        
        datos = {}
        
        # 1. Noticias
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        df_news = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
        df_news['Date'] = pd.to_datetime(df_news['Date'])
        
        df_reddit = pd.read_csv(kaggle_dir / "RedditNews.csv")
        df_reddit['Date'] = pd.to_datetime(df_reddit['Date'])
        
        # Expandir Combined
        noticias = []
        for idx, row in df_news.iterrows():
            for i in range(1, 26):
                noticia = row.get(f'Top{i}')
                if pd.notna(noticia) and noticia != '':
                    noticias.append({
                        'fecha': row['Date'],
                        'titulo': noticia,
                        'fuente': 'combined'
                    })
        
        # Agregar Reddit
        for _, row in df_reddit.iterrows():
            noticias.append({
                'fecha': row['Date'],
                'titulo': row['News'],
                'fuente': 'reddit'
            })
        
        datos['noticias'] = pd.DataFrame(noticias)
        logger.info(f"  ✓ Noticias: {len(datos['noticias']):,}")
        
        # 2. S&P 500 (histórico completo)
        spy_files = list(RAW_DATA_DIR.glob("SPY_historico_completo_*.csv"))
        if spy_files:
            df_spy = pd.read_csv(spy_files[0], index_col=0, parse_dates=True)
            # Normalizar timezone
            df_spy.index = pd.to_datetime([str(d).split()[0] for d in df_spy.index])
            datos['SPY'] = df_spy
            logger.info(f"  ✓ SPY: {len(df_spy):,} días")
        
        # 3. Otros índices
        for idx_name in ['QQQ', 'DIA', 'IWM']:
            files = list(RAW_DATA_DIR.glob(f"{idx_name}_*.csv"))
            if files:
                df = pd.read_csv(files[0], index_col=0, parse_dates=True)
                df.index = pd.to_datetime([str(d).split()[0] for d in df.index])
                datos[idx_name] = df
                logger.info(f"  ✓ {idx_name}: {len(df):,} días")
        
        # 4. Datos económicos (para análisis trimestral)
        fred_files = list(PROCESSED_DATA_DIR.glob("fred/fred_completo_*.csv"))
        if fred_files:
            df_fred = pd.read_csv(fred_files[0], index_col=0, parse_dates=True)
            df_fred.index = pd.to_datetime([str(d).split()[0] for d in df_fred.index])
            datos['FRED'] = df_fred
            logger.info(f"  ✓ FRED económicos: {len(df_fred):,} observaciones")
        
        # 5. Forex
        forex_files = list(PROCESSED_DATA_DIR.glob("forex/forex_pares_historicos_*.csv"))
        if forex_files:
            df_forex = pd.read_csv(forex_files[0], index_col=0, parse_dates=True)
            df_forex.index = pd.to_datetime([str(d).split()[0] for d in df_forex.index])
            datos['FOREX'] = df_forex
            logger.info(f"  ✓ Forex: {len(df_forex):,} observaciones")
        
        # 6. Oil
        oil_files = list(PROCESSED_DATA_DIR.glob("fred/fred_oil_*.csv"))
        if oil_files:
            df_oil = pd.read_csv(oil_files[0], index_col=0, parse_dates=True)
            df_oil.index = pd.to_datetime([str(d).split()[0] for d in df_oil.index])
            datos['OIL'] = df_oil
            logger.info(f"  ✓ Oil: {len(df_oil):,} observaciones")
        
        logger.info(f"\n✓ Datasets cargados: {len(datos)}")
        
        return datos
    
    def clasificar_noticias_avanzado(self, df_noticias):
        """
        Clasifica noticias con categorías detalladas
        """
        logger.info("\n" + "="*70)
        logger.info("CLASIFICACIÓN AVANZADA DE NOTICIAS")
        logger.info("="*70)
        
        categorias_completas = {
            # Geopolítica
            'war_middle_east': ['iran', 'iraq', 'syria', 'israel', 'gaza'],
            'war_russia': ['russia', 'ukraine', 'putin', 'crimea'],
            'terrorism': ['terror', 'isis', 'bombing', 'attack'],
            
            # Fed y Política Monetaria
            'fed_rates': ['fed', 'fomc', 'interest rate', 'federal reserve'],
            'fed_qe': ['quantitative easing', 'qe', 'taper'],
            'ecb_policy': ['ecb', 'draghi', 'lagarde'],
            'boj_policy': ['boj', 'kuroda', 'bank of japan'],
            
            # Economía USA
            'us_gdp_data': ['gdp', 'economic growth'],
            'us_employment_data': ['employment', 'jobs', 'unemployment', 'nfp', 'payroll'],
            'us_inflation_data': ['inflation', 'cpi', 'pce'],
            'us_consumer_data': ['consumer confidence', 'retail sales'],
            'us_housing_data': ['housing', 'home sales'],
            
            # Mercados
            'tech_earnings': ['apple earnings', 'google earnings', 'microsoft earnings', 'amazon earnings'],
            'bank_earnings': ['jpmorgan earnings', 'goldman earnings', 'wells fargo earnings'],
            'earnings_general': ['earnings', 'quarterly results'],
            
            # Commodities
            'oil_supply': ['opec', 'oil production', 'crude supply'],
            'oil_demand': ['oil demand', 'china oil'],
            'gold_demand': ['gold', 'precious metals'],
            
            # Crisis
            'financial_crisis': ['crisis', 'crash', 'panic', 'lehman', 'bailout'],
            'debt_crisis': ['debt', 'default', 'greece', 'sovereign'],
            
            # Trade
            'us_china_trade': ['us china', 'trade war', 'tariff china'],
            'trade_general': ['trade', 'export', 'import'],
            
            # Otros
            'brexit': ['brexit', 'uk referendum'],
            'elections_us': ['us election', 'president', 'congress'],
            'elections_global': ['election', 'vote'],
        }
        
        df_noticias['categoria'] = 'other'
        df_noticias['categoria_granular'] = 'other'
        
        total = len(df_noticias)
        for idx, row in df_noticias.iterrows():
            if idx % 20000 == 0:
                logger.info(f"  Clasificando: {idx:,}/{total:,} ({idx/total*100:.1f}%)")
            
            titulo = str(row['titulo']).lower()
            
            for cat, keywords in categorias_completas.items():
                if any(kw in titulo for kw in keywords):
                    df_noticias.at[idx, 'categoria'] = cat
                    break
        
        logger.info(f"\n✓ Clasificación completada")
        logger.info(f"✓ Categorías únicas: {df_noticias['categoria'].nunique()}")
        
        return df_noticias
    
    def calcular_tokens_volatilidad(self, df_noticias, datos):
        """
        Calcula tokens basados en VOLATILIDAD (no solo dirección)
        
        Token = medida de cuánto MUEVE el mercado (arriba o abajo)
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO TOKENS DE VOLATILIDAD")
        logger.info("="*70)
        logger.info("Token = Volatilidad inducida (|movimiento|)")
        
        resultados = []
        
        for categoria in df_noticias['categoria'].unique():
            if categoria == 'other':
                continue
            
            noticias_cat = df_noticias[df_noticias['categoria'] == categoria]
            
            if len(noticias_cat) < 10:
                continue
            
            logger.info(f"\n📊 {categoria} ({len(noticias_cat)} noticias):")
            
            # Analizar en cada asset
            for asset_name in ['SPY', 'QQQ', 'DIA', 'IWM']:
                if asset_name not in datos:
                    continue
                
                df_asset = datos[asset_name]
                
                # Métricas
                volatilidades = []
                movimientos_alcistas = []
                movimientos_bajistas = []
                
                for fecha_noticia in noticias_cat['fecha'].unique():
                    fecha = pd.Timestamp(fecha_noticia).normalize()
                    
                    # Buscar en asset
                    try:
                        if fecha in df_asset.index:
                            # Día de la noticia
                            precio_pre = df_asset.loc[fecha, 'Open']
                            precio_post = df_asset.loc[fecha, 'Close']
                            
                            movimiento = (precio_post - precio_pre) / precio_pre
                            volatilidad = abs(movimiento)
                            
                            volatilidades.append(volatilidad)
                            
                            if movimiento > 0:
                                movimientos_alcistas.append(movimiento)
                            else:
                                movimientos_bajistas.append(movimiento)
                        
                        else:
                            # Buscar día siguiente
                            for offset in range(1, 6):
                                fecha_fut = fecha + timedelta(days=offset)
                                if fecha_fut in df_asset.index:
                                    precio_pre = df_asset.loc[fecha_fut, 'Open']
                                    precio_post = df_asset.loc[fecha_fut, 'Close']
                                    
                                    movimiento = (precio_post - precio_pre) / precio_pre
                                    volatilidad = abs(movimiento)
                                    
                                    volatilidades.append(volatilidad)
                                    
                                    if movimiento > 0:
                                        movimientos_alcistas.append(movimiento)
                                    else:
                                        movimientos_bajistas.append(movimiento)
                                    break
                    
                    except:
                        continue
                
                if len(volatilidades) >= 10:
                    # Estadísticas
                    volatilidad_promedio = np.mean(volatilidades)
                    volatilidad_max = np.max(volatilidades)
                    volatilidad_std = np.std(volatilidades)
                    
                    # Sesgo direccional
                    pct_alcista = len(movimientos_alcistas) / len(volatilidades) * 100
                    pct_bajista = len(movimientos_bajistas) / len(volatilidades) * 100
                    
                    # Magnitud promedio por dirección
                    mag_alcista = np.mean(movimientos_alcistas) if movimientos_alcistas else 0
                    mag_bajista = abs(np.mean(movimientos_bajistas)) if movimientos_bajistas else 0
                    
                    resultados.append({
                        'categoria': categoria,
                        'asset': asset_name,
                        'volatilidad_promedio': volatilidad_promedio,
                        'volatilidad_max': volatilidad_max,
                        'volatilidad_std': volatilidad_std,
                        'num_eventos': len(volatilidades),
                        'pct_alcista': pct_alcista,
                        'pct_bajista': pct_bajista,
                        'magnitud_alcista': mag_alcista,
                        'magnitud_bajista': mag_bajista,
                        'sesgo': pct_alcista - 50,  # +50 = siempre alcista, -50 = siempre bajista
                    })
                    
                    logger.info(f"  {asset_name:4s}: Vol={volatilidad_promedio*100:5.2f}% "
                               f"(max={volatilidad_max*100:5.2f}%) "
                               f"| {pct_alcista:.0f}%↑ {pct_bajista:.0f}%↓ "
                               f"| Eventos={len(volatilidades)}")
        
        df_resultados = pd.DataFrame(resultados)
        
        # Calcular tokens (basados en volatilidad promedio)
        if len(df_resultados) > 0:
            for asset in df_resultados['asset'].unique():
                df_asset = df_resultados[df_resultados['asset'] == asset]
                max_vol = df_asset['volatilidad_promedio'].max()
                
                for idx in df_asset.index:
                    vol = df_resultados.loc[idx, 'volatilidad_promedio']
                    token = 1.0 + (vol / max_vol) * 9.0
                    df_resultados.loc[idx, 'token'] = token
        
        logger.info(f"\n✓ Tokens de volatilidad calculados: {len(df_resultados)} combinaciones")
        
        return df_resultados
    
    def analizar_impacto_cruzado(self, df_noticias, datos):
        """
        Analiza cómo una categoría afecta MÚLTIPLES assets
        Ejemplo: Desempleo → afecta SPY, Gold, Oil, USD/JPY
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS DE IMPACTO CRUZADO")
        logger.info("="*70)
        logger.info("Categoría → Impacto en múltiples assets")
        
        # Categorías clave para análisis cruzado
        categorias_clave = {
            'us_employment_data': ['employment', 'jobs', 'unemployment', 'nfp'],
            'oil_shock': ['oil', 'opec', 'crude'],
            'financial_crisis': ['crisis', 'crash', 'panic'],
            'fed_rates': ['fed', 'interest rate', 'fomc'],
        }
        
        resultados_cruzados = []
        
        for cat_name, keywords in categorias_clave.items():
            # Filtrar noticias
            mask = df_noticias['titulo'].str.lower().str.contains('|'.join(keywords), na=False, regex=True)
            noticias_cat = df_noticias[mask]
            
            if len(noticias_cat) == 0:
                continue
            
            logger.info(f"\n🔗 {cat_name} ({len(noticias_cat)} noticias):")
            logger.info(f"   Impacto en diferentes assets:")
            
            impactos_por_asset = {}
            
            # Analizar impacto en cada asset disponible
            for asset_name, df_asset in datos.items():
                if asset_name in ['noticias', 'FRED']:
                    continue
                
                volatilidades = []
                
                for fecha in noticias_cat['fecha'].unique():
                    fecha = pd.Timestamp(fecha).normalize()
                    
                    try:
                        if fecha in df_asset.index:
                            if 'Open' in df_asset.columns and 'Close' in df_asset.columns:
                                movimiento = abs((df_asset.loc[fecha, 'Close'] - df_asset.loc[fecha, 'Open']) / 
                                               df_asset.loc[fecha, 'Open'])
                                if not np.isnan(movimiento) and movimiento > 0:
                                    volatilidades.append(movimiento)
                    except:
                        continue
                
                if len(volatilidades) >= 5:
                    vol_promedio = np.mean(volatilidades)
                    impactos_por_asset[asset_name] = vol_promedio
                    
                    logger.info(f"     {asset_name:8s}: {vol_promedio*100:6.3f}% volatilidad ({len(volatilidades)} eventos)")
            
            # Guardar resultado
            if impactos_por_asset:
                resultados_cruzados.append({
                    'categoria': cat_name,
                    'impactos': impactos_por_asset,
                    'num_noticias': len(noticias_cat)
                })
        
        logger.info(f"\n✓ Análisis cruzado completado para {len(resultados_cruzados)} categorías")
        
        return resultados_cruzados
    
    def generar_reporte_completo(self, df_tokens, impactos_cruzados):
        """
        Genera reporte completo con interpretaciones
        """
        logger.info("\n" + "="*70)
        logger.info("GENERANDO REPORTE COMPLETO")
        logger.info("="*70)
        
        output = []
        output.append("# 📊 ANÁLISIS AVANZADO DE TOKENS - VOLATILIDAD REAL")
        output.append("")
        output.append("## Metodología")
        output.append("")
        output.append("**Token = Medida de volatilidad inducida por la noticia**")
        output.append("")
        output.append("```")
        output.append("Volatilidad = |Precio_Close - Precio_Open| / Precio_Open")
        output.append("Token = 1.0 + (Volatilidad_Promedio / Volatilidad_Máxima) × 9.0")
        output.append("```")
        output.append("")
        output.append("## 🎯 TOKENS POR ASSET")
        output.append("")
        
        # Por cada asset
        for asset in df_tokens['asset'].unique():
            df_asset = df_tokens[df_tokens['asset'] == asset].sort_values('token', ascending=False)
            
            output.append(f"### {asset} (S&P 500)")
            output.append("")
            output.append("| Categoría | Token | Vol Avg | Vol Max | Sesgo | ↑ | ↓ |")
            output.append("|-----------|-------|---------|---------|-------|---|---|")
            
            for _, row in df_asset.head(15).iterrows():
                sesgo_txt = "ALCISTA" if row['sesgo'] > 10 else ("BAJISTA" if row['sesgo'] < -10 else "NEUTRAL")
                output.append(f"| {row['categoria']:20s} | {row['token']:5.2f} | "
                             f"{row['volatilidad_promedio']*100:5.2f}% | "
                             f"{row['volatilidad_max']*100:5.2f}% | "
                             f"{sesgo_txt:7s} | "
                             f"{row['pct_alcista']:.0f}% | "
                             f"{row['pct_bajista']:.0f}% |")
            output.append("")
        
        # Análisis cruzado
        output.append("## 🔗 IMPACTO CRUZADO")
        output.append("")
        output.append("**Cómo cada categoría afecta diferentes assets:**")
        output.append("")
        
        for item in impactos_cruzados:
            cat = item['categoria']
            impactos = item['impactos']
            
            output.append(f"### {cat}")
            output.append("")
            
            # Ordenar por impacto
            impactos_sorted = sorted(impactos.items(), key=lambda x: x[1], reverse=True)
            
            for asset, vol in impactos_sorted:
                output.append(f"- **{asset}**: {vol*100:.3f}% volatilidad")
            output.append("")
        
        # Guardar
        output_text = "\n".join(output)
        output_file = PROCESSED_DATA_DIR / "landau" / "TOKENS_VOLATILIDAD_AVANZADO.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        logger.info(f"✓ Reporte guardado: {output_file}")
        
        return output_text


def main():
    """Pipeline completo"""
    logger.info("="*70)
    logger.info("SISTEMA AVANZADO DE TOKENS - VOLATILIDAD")
    logger.info("="*70)
    
    modelo = TokensVolatilidadAvanzado()
    
    # 1. Cargar datos
    logger.info("\n【FASE 1】 Cargando datos...")
    datos = modelo.cargar_datos()
    
    # 2. Clasificar noticias
    logger.info("\n【FASE 2】 Clasificando noticias...")
    df_noticias = modelo.clasificar_noticias_avanzado(datos['noticias'])
    
    # 3. Calcular tokens de volatilidad
    logger.info("\n【FASE 3】 Calculando tokens de volatilidad...")
    df_tokens = modelo.calcular_tokens_volatilidad(df_noticias, datos)
    
    # Guardar tokens
    if len(df_tokens) > 0:
        output_file = PROCESSED_DATA_DIR / "landau" / f"tokens_volatilidad_{datetime.now().strftime('%Y%m%d')}.csv"
        df_tokens.to_csv(output_file, index=False)
        logger.info(f"\n✓ Tokens guardados: {output_file}")
    
    # 4. Análisis cruzado
    logger.info("\n【FASE 4】 Análisis de impacto cruzado...")
    impactos_cruzados = modelo.analizar_impacto_cruzado(df_noticias, datos)
    
    # 5. Reporte
    logger.info("\n【FASE 5】 Generando reporte...")
    reporte = modelo.generar_reporte_completo(df_tokens, impactos_cruzados)
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ ANÁLISIS DE VOLATILIDAD COMPLETADO ✓✓✓")
    logger.info("="*70)


if __name__ == "__main__":
    main()

Sistema Avanzado de Tokens basado en Volatilidad
Distingue entre:
1. Impacto diario (noticias → apertura)
2. Impacto trimestral (Q1,Q2,Q3,Q4 → tendencias)
3. Impacto cruzado (desempleo → oro, petróleo → mercados)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.logger import logger


class TokensVolatilidadAvanzado:
    """
    Calcula tokens basados en volatilidad real
    """
    
    def __init__(self):
        self.tokens_diarios = {}      # (categoria, asset) → token_diario
        self.tokens_trimestrales = {} # (categoria, asset) → token_trimestral
        self.tokens_cruzados = {}     # (categoria_fuente, asset_impactado) → token
        
        # Assets principales
        self.assets_principales = {
            'SPY': 'S&P 500',
            'QQQ': 'NASDAQ',
            'DIA': 'Dow Jones',
            'IWM': 'Russell 2000'
        }
        
        # Categorías económicas (datos trimestrales)
        self.categorias_trimestrales = {
            'gdp': ['gdp', 'economic growth', 'recession', 'expansion'],
            'earnings': ['earnings', 'quarterly results', 'profit', 'revenue'],
            'consumer_spending': ['consumer spending', 'retail sales'],
        }
        
        # Categorías diarias
        self.categorias_diarias = {
            'fed_intraday': ['fed', 'fomc', 'powell speech'],
            'geopolitical': ['war', 'conflict', 'attack', 'strike'],
            'oil_shock': ['oil', 'opec', 'crude'],
            'employment': ['employment', 'jobs', 'unemployment', 'nfp'],
        }
        
        logger.info("✓ TokensVolatilidadAvanzado inicializado")
    
    def cargar_datos(self):
        """Carga todos los datos necesarios"""
        logger.info("\n" + "="*70)
        logger.info("CARGANDO DATOS PARA ANÁLISIS AVANZADO")
        logger.info("="*70)
        
        datos = {}
        
        # 1. Noticias
        kaggle_dir = RAW_DATA_DIR / "Kanggle"
        df_news = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
        df_news['Date'] = pd.to_datetime(df_news['Date'])
        
        df_reddit = pd.read_csv(kaggle_dir / "RedditNews.csv")
        df_reddit['Date'] = pd.to_datetime(df_reddit['Date'])
        
        # Expandir Combined
        noticias = []
        for idx, row in df_news.iterrows():
            for i in range(1, 26):
                noticia = row.get(f'Top{i}')
                if pd.notna(noticia) and noticia != '':
                    noticias.append({
                        'fecha': row['Date'],
                        'titulo': noticia,
                        'fuente': 'combined'
                    })
        
        # Agregar Reddit
        for _, row in df_reddit.iterrows():
            noticias.append({
                'fecha': row['Date'],
                'titulo': row['News'],
                'fuente': 'reddit'
            })
        
        datos['noticias'] = pd.DataFrame(noticias)
        logger.info(f"  ✓ Noticias: {len(datos['noticias']):,}")
        
        # 2. S&P 500 (histórico completo)
        spy_files = list(RAW_DATA_DIR.glob("SPY_historico_completo_*.csv"))
        if spy_files:
            df_spy = pd.read_csv(spy_files[0], index_col=0, parse_dates=True)
            # Normalizar timezone
            df_spy.index = pd.to_datetime([str(d).split()[0] for d in df_spy.index])
            datos['SPY'] = df_spy
            logger.info(f"  ✓ SPY: {len(df_spy):,} días")
        
        # 3. Otros índices
        for idx_name in ['QQQ', 'DIA', 'IWM']:
            files = list(RAW_DATA_DIR.glob(f"{idx_name}_*.csv"))
            if files:
                df = pd.read_csv(files[0], index_col=0, parse_dates=True)
                df.index = pd.to_datetime([str(d).split()[0] for d in df.index])
                datos[idx_name] = df
                logger.info(f"  ✓ {idx_name}: {len(df):,} días")
        
        # 4. Datos económicos (para análisis trimestral)
        fred_files = list(PROCESSED_DATA_DIR.glob("fred/fred_completo_*.csv"))
        if fred_files:
            df_fred = pd.read_csv(fred_files[0], index_col=0, parse_dates=True)
            df_fred.index = pd.to_datetime([str(d).split()[0] for d in df_fred.index])
            datos['FRED'] = df_fred
            logger.info(f"  ✓ FRED económicos: {len(df_fred):,} observaciones")
        
        # 5. Forex
        forex_files = list(PROCESSED_DATA_DIR.glob("forex/forex_pares_historicos_*.csv"))
        if forex_files:
            df_forex = pd.read_csv(forex_files[0], index_col=0, parse_dates=True)
            df_forex.index = pd.to_datetime([str(d).split()[0] for d in df_forex.index])
            datos['FOREX'] = df_forex
            logger.info(f"  ✓ Forex: {len(df_forex):,} observaciones")
        
        # 6. Oil
        oil_files = list(PROCESSED_DATA_DIR.glob("fred/fred_oil_*.csv"))
        if oil_files:
            df_oil = pd.read_csv(oil_files[0], index_col=0, parse_dates=True)
            df_oil.index = pd.to_datetime([str(d).split()[0] for d in df_oil.index])
            datos['OIL'] = df_oil
            logger.info(f"  ✓ Oil: {len(df_oil):,} observaciones")
        
        logger.info(f"\n✓ Datasets cargados: {len(datos)}")
        
        return datos
    
    def clasificar_noticias_avanzado(self, df_noticias):
        """
        Clasifica noticias con categorías detalladas
        """
        logger.info("\n" + "="*70)
        logger.info("CLASIFICACIÓN AVANZADA DE NOTICIAS")
        logger.info("="*70)
        
        categorias_completas = {
            # Geopolítica
            'war_middle_east': ['iran', 'iraq', 'syria', 'israel', 'gaza'],
            'war_russia': ['russia', 'ukraine', 'putin', 'crimea'],
            'terrorism': ['terror', 'isis', 'bombing', 'attack'],
            
            # Fed y Política Monetaria
            'fed_rates': ['fed', 'fomc', 'interest rate', 'federal reserve'],
            'fed_qe': ['quantitative easing', 'qe', 'taper'],
            'ecb_policy': ['ecb', 'draghi', 'lagarde'],
            'boj_policy': ['boj', 'kuroda', 'bank of japan'],
            
            # Economía USA
            'us_gdp_data': ['gdp', 'economic growth'],
            'us_employment_data': ['employment', 'jobs', 'unemployment', 'nfp', 'payroll'],
            'us_inflation_data': ['inflation', 'cpi', 'pce'],
            'us_consumer_data': ['consumer confidence', 'retail sales'],
            'us_housing_data': ['housing', 'home sales'],
            
            # Mercados
            'tech_earnings': ['apple earnings', 'google earnings', 'microsoft earnings', 'amazon earnings'],
            'bank_earnings': ['jpmorgan earnings', 'goldman earnings', 'wells fargo earnings'],
            'earnings_general': ['earnings', 'quarterly results'],
            
            # Commodities
            'oil_supply': ['opec', 'oil production', 'crude supply'],
            'oil_demand': ['oil demand', 'china oil'],
            'gold_demand': ['gold', 'precious metals'],
            
            # Crisis
            'financial_crisis': ['crisis', 'crash', 'panic', 'lehman', 'bailout'],
            'debt_crisis': ['debt', 'default', 'greece', 'sovereign'],
            
            # Trade
            'us_china_trade': ['us china', 'trade war', 'tariff china'],
            'trade_general': ['trade', 'export', 'import'],
            
            # Otros
            'brexit': ['brexit', 'uk referendum'],
            'elections_us': ['us election', 'president', 'congress'],
            'elections_global': ['election', 'vote'],
        }
        
        df_noticias['categoria'] = 'other'
        df_noticias['categoria_granular'] = 'other'
        
        total = len(df_noticias)
        for idx, row in df_noticias.iterrows():
            if idx % 20000 == 0:
                logger.info(f"  Clasificando: {idx:,}/{total:,} ({idx/total*100:.1f}%)")
            
            titulo = str(row['titulo']).lower()
            
            for cat, keywords in categorias_completas.items():
                if any(kw in titulo for kw in keywords):
                    df_noticias.at[idx, 'categoria'] = cat
                    break
        
        logger.info(f"\n✓ Clasificación completada")
        logger.info(f"✓ Categorías únicas: {df_noticias['categoria'].nunique()}")
        
        return df_noticias
    
    def calcular_tokens_volatilidad(self, df_noticias, datos):
        """
        Calcula tokens basados en VOLATILIDAD (no solo dirección)
        
        Token = medida de cuánto MUEVE el mercado (arriba o abajo)
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO TOKENS DE VOLATILIDAD")
        logger.info("="*70)
        logger.info("Token = Volatilidad inducida (|movimiento|)")
        
        resultados = []
        
        for categoria in df_noticias['categoria'].unique():
            if categoria == 'other':
                continue
            
            noticias_cat = df_noticias[df_noticias['categoria'] == categoria]
            
            if len(noticias_cat) < 10:
                continue
            
            logger.info(f"\n📊 {categoria} ({len(noticias_cat)} noticias):")
            
            # Analizar en cada asset
            for asset_name in ['SPY', 'QQQ', 'DIA', 'IWM']:
                if asset_name not in datos:
                    continue
                
                df_asset = datos[asset_name]
                
                # Métricas
                volatilidades = []
                movimientos_alcistas = []
                movimientos_bajistas = []
                
                for fecha_noticia in noticias_cat['fecha'].unique():
                    fecha = pd.Timestamp(fecha_noticia).normalize()
                    
                    # Buscar en asset
                    try:
                        if fecha in df_asset.index:
                            # Día de la noticia
                            precio_pre = df_asset.loc[fecha, 'Open']
                            precio_post = df_asset.loc[fecha, 'Close']
                            
                            movimiento = (precio_post - precio_pre) / precio_pre
                            volatilidad = abs(movimiento)
                            
                            volatilidades.append(volatilidad)
                            
                            if movimiento > 0:
                                movimientos_alcistas.append(movimiento)
                            else:
                                movimientos_bajistas.append(movimiento)
                        
                        else:
                            # Buscar día siguiente
                            for offset in range(1, 6):
                                fecha_fut = fecha + timedelta(days=offset)
                                if fecha_fut in df_asset.index:
                                    precio_pre = df_asset.loc[fecha_fut, 'Open']
                                    precio_post = df_asset.loc[fecha_fut, 'Close']
                                    
                                    movimiento = (precio_post - precio_pre) / precio_pre
                                    volatilidad = abs(movimiento)
                                    
                                    volatilidades.append(volatilidad)
                                    
                                    if movimiento > 0:
                                        movimientos_alcistas.append(movimiento)
                                    else:
                                        movimientos_bajistas.append(movimiento)
                                    break
                    
                    except:
                        continue
                
                if len(volatilidades) >= 10:
                    # Estadísticas
                    volatilidad_promedio = np.mean(volatilidades)
                    volatilidad_max = np.max(volatilidades)
                    volatilidad_std = np.std(volatilidades)
                    
                    # Sesgo direccional
                    pct_alcista = len(movimientos_alcistas) / len(volatilidades) * 100
                    pct_bajista = len(movimientos_bajistas) / len(volatilidades) * 100
                    
                    # Magnitud promedio por dirección
                    mag_alcista = np.mean(movimientos_alcistas) if movimientos_alcistas else 0
                    mag_bajista = abs(np.mean(movimientos_bajistas)) if movimientos_bajistas else 0
                    
                    resultados.append({
                        'categoria': categoria,
                        'asset': asset_name,
                        'volatilidad_promedio': volatilidad_promedio,
                        'volatilidad_max': volatilidad_max,
                        'volatilidad_std': volatilidad_std,
                        'num_eventos': len(volatilidades),
                        'pct_alcista': pct_alcista,
                        'pct_bajista': pct_bajista,
                        'magnitud_alcista': mag_alcista,
                        'magnitud_bajista': mag_bajista,
                        'sesgo': pct_alcista - 50,  # +50 = siempre alcista, -50 = siempre bajista
                    })
                    
                    logger.info(f"  {asset_name:4s}: Vol={volatilidad_promedio*100:5.2f}% "
                               f"(max={volatilidad_max*100:5.2f}%) "
                               f"| {pct_alcista:.0f}%↑ {pct_bajista:.0f}%↓ "
                               f"| Eventos={len(volatilidades)}")
        
        df_resultados = pd.DataFrame(resultados)
        
        # Calcular tokens (basados en volatilidad promedio)
        if len(df_resultados) > 0:
            for asset in df_resultados['asset'].unique():
                df_asset = df_resultados[df_resultados['asset'] == asset]
                max_vol = df_asset['volatilidad_promedio'].max()
                
                for idx in df_asset.index:
                    vol = df_resultados.loc[idx, 'volatilidad_promedio']
                    token = 1.0 + (vol / max_vol) * 9.0
                    df_resultados.loc[idx, 'token'] = token
        
        logger.info(f"\n✓ Tokens de volatilidad calculados: {len(df_resultados)} combinaciones")
        
        return df_resultados
    
    def analizar_impacto_cruzado(self, df_noticias, datos):
        """
        Analiza cómo una categoría afecta MÚLTIPLES assets
        Ejemplo: Desempleo → afecta SPY, Gold, Oil, USD/JPY
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS DE IMPACTO CRUZADO")
        logger.info("="*70)
        logger.info("Categoría → Impacto en múltiples assets")
        
        # Categorías clave para análisis cruzado
        categorias_clave = {
            'us_employment_data': ['employment', 'jobs', 'unemployment', 'nfp'],
            'oil_shock': ['oil', 'opec', 'crude'],
            'financial_crisis': ['crisis', 'crash', 'panic'],
            'fed_rates': ['fed', 'interest rate', 'fomc'],
        }
        
        resultados_cruzados = []
        
        for cat_name, keywords in categorias_clave.items():
            # Filtrar noticias
            mask = df_noticias['titulo'].str.lower().str.contains('|'.join(keywords), na=False, regex=True)
            noticias_cat = df_noticias[mask]
            
            if len(noticias_cat) == 0:
                continue
            
            logger.info(f"\n🔗 {cat_name} ({len(noticias_cat)} noticias):")
            logger.info(f"   Impacto en diferentes assets:")
            
            impactos_por_asset = {}
            
            # Analizar impacto en cada asset disponible
            for asset_name, df_asset in datos.items():
                if asset_name in ['noticias', 'FRED']:
                    continue
                
                volatilidades = []
                
                for fecha in noticias_cat['fecha'].unique():
                    fecha = pd.Timestamp(fecha).normalize()
                    
                    try:
                        if fecha in df_asset.index:
                            if 'Open' in df_asset.columns and 'Close' in df_asset.columns:
                                movimiento = abs((df_asset.loc[fecha, 'Close'] - df_asset.loc[fecha, 'Open']) / 
                                               df_asset.loc[fecha, 'Open'])
                                if not np.isnan(movimiento) and movimiento > 0:
                                    volatilidades.append(movimiento)
                    except:
                        continue
                
                if len(volatilidades) >= 5:
                    vol_promedio = np.mean(volatilidades)
                    impactos_por_asset[asset_name] = vol_promedio
                    
                    logger.info(f"     {asset_name:8s}: {vol_promedio*100:6.3f}% volatilidad ({len(volatilidades)} eventos)")
            
            # Guardar resultado
            if impactos_por_asset:
                resultados_cruzados.append({
                    'categoria': cat_name,
                    'impactos': impactos_por_asset,
                    'num_noticias': len(noticias_cat)
                })
        
        logger.info(f"\n✓ Análisis cruzado completado para {len(resultados_cruzados)} categorías")
        
        return resultados_cruzados
    
    def generar_reporte_completo(self, df_tokens, impactos_cruzados):
        """
        Genera reporte completo con interpretaciones
        """
        logger.info("\n" + "="*70)
        logger.info("GENERANDO REPORTE COMPLETO")
        logger.info("="*70)
        
        output = []
        output.append("# 📊 ANÁLISIS AVANZADO DE TOKENS - VOLATILIDAD REAL")
        output.append("")
        output.append("## Metodología")
        output.append("")
        output.append("**Token = Medida de volatilidad inducida por la noticia**")
        output.append("")
        output.append("```")
        output.append("Volatilidad = |Precio_Close - Precio_Open| / Precio_Open")
        output.append("Token = 1.0 + (Volatilidad_Promedio / Volatilidad_Máxima) × 9.0")
        output.append("```")
        output.append("")
        output.append("## 🎯 TOKENS POR ASSET")
        output.append("")
        
        # Por cada asset
        for asset in df_tokens['asset'].unique():
            df_asset = df_tokens[df_tokens['asset'] == asset].sort_values('token', ascending=False)
            
            output.append(f"### {asset} (S&P 500)")
            output.append("")
            output.append("| Categoría | Token | Vol Avg | Vol Max | Sesgo | ↑ | ↓ |")
            output.append("|-----------|-------|---------|---------|-------|---|---|")
            
            for _, row in df_asset.head(15).iterrows():
                sesgo_txt = "ALCISTA" if row['sesgo'] > 10 else ("BAJISTA" if row['sesgo'] < -10 else "NEUTRAL")
                output.append(f"| {row['categoria']:20s} | {row['token']:5.2f} | "
                             f"{row['volatilidad_promedio']*100:5.2f}% | "
                             f"{row['volatilidad_max']*100:5.2f}% | "
                             f"{sesgo_txt:7s} | "
                             f"{row['pct_alcista']:.0f}% | "
                             f"{row['pct_bajista']:.0f}% |")
            output.append("")
        
        # Análisis cruzado
        output.append("## 🔗 IMPACTO CRUZADO")
        output.append("")
        output.append("**Cómo cada categoría afecta diferentes assets:**")
        output.append("")
        
        for item in impactos_cruzados:
            cat = item['categoria']
            impactos = item['impactos']
            
            output.append(f"### {cat}")
            output.append("")
            
            # Ordenar por impacto
            impactos_sorted = sorted(impactos.items(), key=lambda x: x[1], reverse=True)
            
            for asset, vol in impactos_sorted:
                output.append(f"- **{asset}**: {vol*100:.3f}% volatilidad")
            output.append("")
        
        # Guardar
        output_text = "\n".join(output)
        output_file = PROCESSED_DATA_DIR / "landau" / "TOKENS_VOLATILIDAD_AVANZADO.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        logger.info(f"✓ Reporte guardado: {output_file}")
        
        return output_text


def main():
    """Pipeline completo"""
    logger.info("="*70)
    logger.info("SISTEMA AVANZADO DE TOKENS - VOLATILIDAD")
    logger.info("="*70)
    
    modelo = TokensVolatilidadAvanzado()
    
    # 1. Cargar datos
    logger.info("\n【FASE 1】 Cargando datos...")
    datos = modelo.cargar_datos()
    
    # 2. Clasificar noticias
    logger.info("\n【FASE 2】 Clasificando noticias...")
    df_noticias = modelo.clasificar_noticias_avanzado(datos['noticias'])
    
    # 3. Calcular tokens de volatilidad
    logger.info("\n【FASE 3】 Calculando tokens de volatilidad...")
    df_tokens = modelo.calcular_tokens_volatilidad(df_noticias, datos)
    
    # Guardar tokens
    if len(df_tokens) > 0:
        output_file = PROCESSED_DATA_DIR / "landau" / f"tokens_volatilidad_{datetime.now().strftime('%Y%m%d')}.csv"
        df_tokens.to_csv(output_file, index=False)
        logger.info(f"\n✓ Tokens guardados: {output_file}")
    
    # 4. Análisis cruzado
    logger.info("\n【FASE 4】 Análisis de impacto cruzado...")
    impactos_cruzados = modelo.analizar_impacto_cruzado(df_noticias, datos)
    
    # 5. Reporte
    logger.info("\n【FASE 5】 Generando reporte...")
    reporte = modelo.generar_reporte_completo(df_tokens, impactos_cruzados)
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ ANÁLISIS DE VOLATILIDAD COMPLETADO ✓✓✓")
    logger.info("="*70)


if __name__ == "__main__":
    main()



