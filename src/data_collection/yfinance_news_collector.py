"""
Recolector de Noticias usando yfinance
yfinance proporciona noticias SIN necesitar API key
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class YFinanceNewsCollector:
    """
    Recolector de noticias financieras usando yfinance
    100% GRATIS, sin API key necesaria
    """
    
    def __init__(self):
        """Inicializa el recolector"""
        logger.info("✓ YFinanceNewsCollector inicializado")
        logger.info("  Usando yfinance (GRATIS, sin API key)")
    
    def obtener_noticias_ticker(self, ticker):
        """
        Obtiene noticias de un ticker específico
        
        Args:
            ticker: Símbolo del ticker (ej: 'SPY', 'AAPL')
            
        Returns:
            Lista de noticias
        """
        try:
            logger.info(f"  Obteniendo noticias de {ticker}...")
            
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if news:
                logger.info(f"    ✓ {len(news)} noticias encontradas")
                
                # Procesar noticias
                noticias_procesadas = []
                for item in news:
                    noticia = {
                        'ticker': ticker,
                        'fecha': datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                        'titulo': item.get('title', ''),
                        'publisher': item.get('publisher', ''),
                        'link': item.get('link', ''),
                        'tipo': item.get('type', ''),
                        'relacionado': ', '.join(item.get('relatedTickers', []))
                    }
                    noticias_procesadas.append(noticia)
                
                return noticias_procesadas
            else:
                logger.warning(f"    No se encontraron noticias para {ticker}")
                return []
                
        except Exception as e:
            logger.error(f"    Error con {ticker}: {e}")
            return []
    
    def obtener_noticias_principales_indices(self):
        """
        Obtiene noticias de los principales índices y ETFs
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO NOTICIAS DE ÍNDICES PRINCIPALES")
        logger.info("="*70)
        
        # Tickers principales que cubren diferentes mercados
        tickers = {
            # Índices USA
            'SPY': 'S&P 500 - Mercado USA general',
            'QQQ': 'NASDAQ - Tecnología USA',
            'DIA': 'Dow Jones - Blue chips USA',
            
            # ETFs sectoriales USA
            'XLF': 'Financials - Bancos USA',
            'XLE': 'Energy - Petróleo y gas USA',
            'XLK': 'Technology - Tech USA',
            
            # ETFs internacionales
            'EWJ': 'iShares MSCI Japan',
            'FXI': 'iShares China Large-Cap',
            'EWG': 'iShares MSCI Germany',
            'EWU': 'iShares MSCI United Kingdom',
            'EWA': 'iShares MSCI Australia',
            'EWZ': 'iShares MSCI Brazil',
            
            # Commodities
            'GLD': 'Gold ETF',
            'USO': 'Oil ETF',
            'UNG': 'Natural Gas ETF',
        }
        
        todas_noticias = []
        
        for ticker, descripcion in tickers.items():
            logger.info(f"\n{ticker} - {descripcion}")
            noticias = self.obtener_noticias_ticker(ticker)
            todas_noticias.extend(noticias)
        
        logger.info(f"\n✓ Total de noticias recolectadas: {len(todas_noticias)}")
        
        return todas_noticias
    
    def crear_dataset(self, noticias):
        """
        Crea DataFrame con las noticias
        """
        if not noticias:
            logger.warning("No hay noticias para crear dataset")
            return None
        
        df = pd.DataFrame(noticias)
        
        # Eliminar duplicados por título
        df = df.drop_duplicates(subset=['titulo'])
        
        # Ordenar por fecha
        df = df.sort_values('fecha', ascending=False)
        
        logger.info(f"✓ Dataset creado: {df.shape}")
        logger.info(f"  Noticias únicas: {len(df)}")
        logger.info(f"  Período: {df['fecha'].min()} a {df['fecha'].max()}")
        
        return df
    
    def correlacionar_con_sp500(self, df_noticias):
        """
        Correlaciona noticias con movimientos del S&P 500
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONANDO CON S&P 500")
        logger.info("="*70)
        
        # Buscar archivo del S&P 500
        spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
        
        if not spy_files:
            logger.error("  No se encontraron datos del S&P 500")
            logger.info("  Ejecuta: py src/data_collection/market_collector.py")
            return df_noticias
        
        spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
        df_sp500 = pd.read_csv(spy_file, index_col=0, parse_dates=True)
        df_sp500['Return'] = df_sp500['Close'].pct_change()
        
        logger.info(f"  ✓ S&P 500 cargado: {len(df_sp500)} días")
        
        # Agregar columnas de impacto
        df_noticias['sp500_price'] = None
        df_noticias['sp500_return_same_day'] = None
        df_noticias['sp500_return_next_day'] = None
        df_noticias['impacto_direccion'] = 'NEUTRAL'
        
        correlacionadas = 0
        
        for idx, row in df_noticias.iterrows():
            fecha_noticia = row['fecha'].date()
            
            try:
                # Mismo día
                mask = df_sp500.index.date == fecha_noticia
                if mask.sum() > 0:
                    df_noticias.at[idx, 'sp500_price'] = df_sp500.loc[mask, 'Close'].values[0]
                    retorno = df_sp500.loc[mask, 'Return'].values[0]
                    if pd.notna(retorno):
                        df_noticias.at[idx, 'sp500_return_same_day'] = retorno
                
                # Día siguiente (buscar hasta 3 días por fines de semana)
                for i in range(1, 4):
                    fecha_next = fecha_noticia + pd.Timedelta(days=i)
                    mask_next = df_sp500.index.date == fecha_next.date()
                    if mask_next.sum() > 0:
                        retorno_next = df_sp500.loc[mask_next, 'Return'].values[0]
                        if pd.notna(retorno_next):
                            df_noticias.at[idx, 'sp500_return_next_day'] = retorno_next
                            correlacionadas += 1
                            
                            # Clasificar dirección
                            if retorno_next > 0.01:
                                df_noticias.at[idx, 'impacto_direccion'] = 'UP'
                            elif retorno_next < -0.01:
                                df_noticias.at[idx, 'impacto_direccion'] = 'DOWN'
                            break
            
            except Exception:
                continue
        
        # Clasificar magnitud del impacto
        df_noticias['impacto_absoluto'] = pd.to_numeric(df_noticias['sp500_return_next_day'], errors='coerce').abs()
        df_noticias['impacto_clasificado'] = pd.cut(
            df_noticias['impacto_absoluto'],
            bins=[0, 0.005, 0.015, 1.0],
            labels=['BAJO', 'MEDIO', 'ALTO']
        )
        
        logger.info(f"\n✓ Correlación completada")
        logger.info(f"  Noticias correlacionadas: {correlacionadas}/{len(df_noticias)}")
        
        # Estadísticas de impacto
        if correlacionadas > 0:
            logger.info(f"\nDistribución por impacto:")
            for imp in ['ALTO', 'MEDIO', 'BAJO']:
                count = len(df_noticias[df_noticias['impacto_clasificado'] == imp])
                if count > 0:
                    pct = (count / correlacionadas) * 100
                    logger.info(f"  {imp}: {count} noticias ({pct:.1f}%)")
        
        return df_noticias
    
    def guardar_datos(self, df):
        """
        Guarda las noticias en CSV
        """
        if df is None or df.empty:
            logger.warning("No hay datos para guardar")
            return
        
        # Crear directorio
        news_dir = RAW_DATA_DIR.parent / "processed" / "news"
        news_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = news_dir / f"noticias_yfinance_correlacionadas_{timestamp}.csv"
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"\n✓ Noticias guardadas: {filepath}")
        
        return filepath
    
    def generar_reporte(self, df):
        """
        Genera reporte detallado
        """
        if df is None or df.empty:
            return
        
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE NOTICIAS Y SU IMPACTO")
        logger.info("="*70)
        
        logger.info(f"\nTotal de noticias: {len(df)}")
        logger.info(f"Período: {df['fecha'].min()} a {df['fecha'].max()}")
        
        # Top publishers
        logger.info("\nPrincipales fuentes:")
        for pub, count in df['publisher'].value_counts().head(10).items():
            logger.info(f"  {pub}: {count} noticias")
        
        # Noticias por ticker
        logger.info("\nNoticias por ticker:")
        for tick, count in df['ticker'].value_counts().head(10).items():
            logger.info(f"  {tick}: {count} noticias")
        
        # Top impactos positivos
        logger.info("\n📈 Top 10 noticias con MAYOR impacto positivo:")
        df_con_impacto = df[pd.to_numeric(df['sp500_return_next_day'], errors='coerce').notna()].copy()
        df_con_impacto['sp500_return_next_day'] = pd.to_numeric(df_con_impacto['sp500_return_next_day'])
        
        if len(df_con_impacto) > 0:
            top_positive = df_con_impacto.nlargest(min(10, len(df_con_impacto)), 'sp500_return_next_day')
            for _, row in top_positive.iterrows():
                logger.info(f"  +{row['sp500_return_next_day']*100:.2f}% | {row['ticker']} | {row['titulo'][:60]}")
            
            # Top impactos negativos
            logger.info("\n📉 Top 10 noticias con MAYOR impacto negativo:")
            top_negative = df_con_impacto.nsmallest(min(10, len(df_con_impacto)), 'sp500_return_next_day')
            for _, row in top_negative.iterrows():
                logger.info(f"  {row['sp500_return_next_day']*100:.2f}% | {row['ticker']} | {row['titulo'][:60]}")
        else:
            logger.warning("  No hay noticias con impacto medido")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE NOTICIAS - YFINANCE")
    logger.info("="*70)
    logger.info("Ventajas: GRATIS, sin API key, datos actuales")
    logger.info("")
    
    # Crear recolector
    collector = YFinanceNewsCollector()
    
    # Obtener noticias
    logger.info("\n1. Obteniendo noticias de índices principales...")
    noticias = collector.obtener_noticias_principales_indices()
    
    if noticias:
        # Crear dataset
        logger.info("\n2. Creando dataset...")
        df = collector.crear_dataset(noticias)
        
        if df is not None:
            # Correlacionar con S&P 500
            logger.info("\n3. Correlacionando con S&P 500...")
            df_correlacionado = collector.correlacionar_con_sp500(df)
            
            # Guardar
            logger.info("\n4. Guardando datos...")
            filepath = collector.guardar_datos(df_correlacionado)
            
            # Reporte
            logger.info("\n5. Generando reporte...")
            collector.generar_reporte(df_correlacionado)
            
            logger.info("\n" + "="*70)
            logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
            logger.info("="*70)
            logger.info(f"\nArchivo: {filepath}")
            logger.info("\nEstos datos ya están listos para:")
            logger.info("  1. Análisis de sentimiento")
            logger.info("  2. Entrenamiento de modelo")
            logger.info("  3. Identificación de patrones")
        else:
            logger.error("No se pudo crear dataset")
    else:
        logger.error("No se obtuvieron noticias")


if __name__ == "__main__":
    main()


yfinance proporciona noticias SIN necesitar API key
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class YFinanceNewsCollector:
    """
    Recolector de noticias financieras usando yfinance
    100% GRATIS, sin API key necesaria
    """
    
    def __init__(self):
        """Inicializa el recolector"""
        logger.info("✓ YFinanceNewsCollector inicializado")
        logger.info("  Usando yfinance (GRATIS, sin API key)")
    
    def obtener_noticias_ticker(self, ticker):
        """
        Obtiene noticias de un ticker específico
        
        Args:
            ticker: Símbolo del ticker (ej: 'SPY', 'AAPL')
            
        Returns:
            Lista de noticias
        """
        try:
            logger.info(f"  Obteniendo noticias de {ticker}...")
            
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if news:
                logger.info(f"    ✓ {len(news)} noticias encontradas")
                
                # Procesar noticias
                noticias_procesadas = []
                for item in news:
                    noticia = {
                        'ticker': ticker,
                        'fecha': datetime.fromtimestamp(item.get('providerPublishTime', 0)),
                        'titulo': item.get('title', ''),
                        'publisher': item.get('publisher', ''),
                        'link': item.get('link', ''),
                        'tipo': item.get('type', ''),
                        'relacionado': ', '.join(item.get('relatedTickers', []))
                    }
                    noticias_procesadas.append(noticia)
                
                return noticias_procesadas
            else:
                logger.warning(f"    No se encontraron noticias para {ticker}")
                return []
                
        except Exception as e:
            logger.error(f"    Error con {ticker}: {e}")
            return []
    
    def obtener_noticias_principales_indices(self):
        """
        Obtiene noticias de los principales índices y ETFs
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO NOTICIAS DE ÍNDICES PRINCIPALES")
        logger.info("="*70)
        
        # Tickers principales que cubren diferentes mercados
        tickers = {
            # Índices USA
            'SPY': 'S&P 500 - Mercado USA general',
            'QQQ': 'NASDAQ - Tecnología USA',
            'DIA': 'Dow Jones - Blue chips USA',
            
            # ETFs sectoriales USA
            'XLF': 'Financials - Bancos USA',
            'XLE': 'Energy - Petróleo y gas USA',
            'XLK': 'Technology - Tech USA',
            
            # ETFs internacionales
            'EWJ': 'iShares MSCI Japan',
            'FXI': 'iShares China Large-Cap',
            'EWG': 'iShares MSCI Germany',
            'EWU': 'iShares MSCI United Kingdom',
            'EWA': 'iShares MSCI Australia',
            'EWZ': 'iShares MSCI Brazil',
            
            # Commodities
            'GLD': 'Gold ETF',
            'USO': 'Oil ETF',
            'UNG': 'Natural Gas ETF',
        }
        
        todas_noticias = []
        
        for ticker, descripcion in tickers.items():
            logger.info(f"\n{ticker} - {descripcion}")
            noticias = self.obtener_noticias_ticker(ticker)
            todas_noticias.extend(noticias)
        
        logger.info(f"\n✓ Total de noticias recolectadas: {len(todas_noticias)}")
        
        return todas_noticias
    
    def crear_dataset(self, noticias):
        """
        Crea DataFrame con las noticias
        """
        if not noticias:
            logger.warning("No hay noticias para crear dataset")
            return None
        
        df = pd.DataFrame(noticias)
        
        # Eliminar duplicados por título
        df = df.drop_duplicates(subset=['titulo'])
        
        # Ordenar por fecha
        df = df.sort_values('fecha', ascending=False)
        
        logger.info(f"✓ Dataset creado: {df.shape}")
        logger.info(f"  Noticias únicas: {len(df)}")
        logger.info(f"  Período: {df['fecha'].min()} a {df['fecha'].max()}")
        
        return df
    
    def correlacionar_con_sp500(self, df_noticias):
        """
        Correlaciona noticias con movimientos del S&P 500
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONANDO CON S&P 500")
        logger.info("="*70)
        
        # Buscar archivo del S&P 500
        spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
        
        if not spy_files:
            logger.error("  No se encontraron datos del S&P 500")
            logger.info("  Ejecuta: py src/data_collection/market_collector.py")
            return df_noticias
        
        spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
        df_sp500 = pd.read_csv(spy_file, index_col=0, parse_dates=True)
        df_sp500['Return'] = df_sp500['Close'].pct_change()
        
        logger.info(f"  ✓ S&P 500 cargado: {len(df_sp500)} días")
        
        # Agregar columnas de impacto
        df_noticias['sp500_price'] = None
        df_noticias['sp500_return_same_day'] = None
        df_noticias['sp500_return_next_day'] = None
        df_noticias['impacto_direccion'] = 'NEUTRAL'
        
        correlacionadas = 0
        
        for idx, row in df_noticias.iterrows():
            fecha_noticia = row['fecha'].date()
            
            try:
                # Mismo día
                mask = df_sp500.index.date == fecha_noticia
                if mask.sum() > 0:
                    df_noticias.at[idx, 'sp500_price'] = df_sp500.loc[mask, 'Close'].values[0]
                    retorno = df_sp500.loc[mask, 'Return'].values[0]
                    if pd.notna(retorno):
                        df_noticias.at[idx, 'sp500_return_same_day'] = retorno
                
                # Día siguiente (buscar hasta 3 días por fines de semana)
                for i in range(1, 4):
                    fecha_next = fecha_noticia + pd.Timedelta(days=i)
                    mask_next = df_sp500.index.date == fecha_next.date()
                    if mask_next.sum() > 0:
                        retorno_next = df_sp500.loc[mask_next, 'Return'].values[0]
                        if pd.notna(retorno_next):
                            df_noticias.at[idx, 'sp500_return_next_day'] = retorno_next
                            correlacionadas += 1
                            
                            # Clasificar dirección
                            if retorno_next > 0.01:
                                df_noticias.at[idx, 'impacto_direccion'] = 'UP'
                            elif retorno_next < -0.01:
                                df_noticias.at[idx, 'impacto_direccion'] = 'DOWN'
                            break
            
            except Exception:
                continue
        
        # Clasificar magnitud del impacto
        df_noticias['impacto_absoluto'] = pd.to_numeric(df_noticias['sp500_return_next_day'], errors='coerce').abs()
        df_noticias['impacto_clasificado'] = pd.cut(
            df_noticias['impacto_absoluto'],
            bins=[0, 0.005, 0.015, 1.0],
            labels=['BAJO', 'MEDIO', 'ALTO']
        )
        
        logger.info(f"\n✓ Correlación completada")
        logger.info(f"  Noticias correlacionadas: {correlacionadas}/{len(df_noticias)}")
        
        # Estadísticas de impacto
        if correlacionadas > 0:
            logger.info(f"\nDistribución por impacto:")
            for imp in ['ALTO', 'MEDIO', 'BAJO']:
                count = len(df_noticias[df_noticias['impacto_clasificado'] == imp])
                if count > 0:
                    pct = (count / correlacionadas) * 100
                    logger.info(f"  {imp}: {count} noticias ({pct:.1f}%)")
        
        return df_noticias
    
    def guardar_datos(self, df):
        """
        Guarda las noticias en CSV
        """
        if df is None or df.empty:
            logger.warning("No hay datos para guardar")
            return
        
        # Crear directorio
        news_dir = RAW_DATA_DIR.parent / "processed" / "news"
        news_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = news_dir / f"noticias_yfinance_correlacionadas_{timestamp}.csv"
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        logger.info(f"\n✓ Noticias guardadas: {filepath}")
        
        return filepath
    
    def generar_reporte(self, df):
        """
        Genera reporte detallado
        """
        if df is None or df.empty:
            return
        
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE NOTICIAS Y SU IMPACTO")
        logger.info("="*70)
        
        logger.info(f"\nTotal de noticias: {len(df)}")
        logger.info(f"Período: {df['fecha'].min()} a {df['fecha'].max()}")
        
        # Top publishers
        logger.info("\nPrincipales fuentes:")
        for pub, count in df['publisher'].value_counts().head(10).items():
            logger.info(f"  {pub}: {count} noticias")
        
        # Noticias por ticker
        logger.info("\nNoticias por ticker:")
        for tick, count in df['ticker'].value_counts().head(10).items():
            logger.info(f"  {tick}: {count} noticias")
        
        # Top impactos positivos
        logger.info("\n📈 Top 10 noticias con MAYOR impacto positivo:")
        df_con_impacto = df[pd.to_numeric(df['sp500_return_next_day'], errors='coerce').notna()].copy()
        df_con_impacto['sp500_return_next_day'] = pd.to_numeric(df_con_impacto['sp500_return_next_day'])
        
        if len(df_con_impacto) > 0:
            top_positive = df_con_impacto.nlargest(min(10, len(df_con_impacto)), 'sp500_return_next_day')
            for _, row in top_positive.iterrows():
                logger.info(f"  +{row['sp500_return_next_day']*100:.2f}% | {row['ticker']} | {row['titulo'][:60]}")
            
            # Top impactos negativos
            logger.info("\n📉 Top 10 noticias con MAYOR impacto negativo:")
            top_negative = df_con_impacto.nsmallest(min(10, len(df_con_impacto)), 'sp500_return_next_day')
            for _, row in top_negative.iterrows():
                logger.info(f"  {row['sp500_return_next_day']*100:.2f}% | {row['ticker']} | {row['titulo'][:60]}")
        else:
            logger.warning("  No hay noticias con impacto medido")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE NOTICIAS - YFINANCE")
    logger.info("="*70)
    logger.info("Ventajas: GRATIS, sin API key, datos actuales")
    logger.info("")
    
    # Crear recolector
    collector = YFinanceNewsCollector()
    
    # Obtener noticias
    logger.info("\n1. Obteniendo noticias de índices principales...")
    noticias = collector.obtener_noticias_principales_indices()
    
    if noticias:
        # Crear dataset
        logger.info("\n2. Creando dataset...")
        df = collector.crear_dataset(noticias)
        
        if df is not None:
            # Correlacionar con S&P 500
            logger.info("\n3. Correlacionando con S&P 500...")
            df_correlacionado = collector.correlacionar_con_sp500(df)
            
            # Guardar
            logger.info("\n4. Guardando datos...")
            filepath = collector.guardar_datos(df_correlacionado)
            
            # Reporte
            logger.info("\n5. Generando reporte...")
            collector.generar_reporte(df_correlacionado)
            
            logger.info("\n" + "="*70)
            logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
            logger.info("="*70)
            logger.info(f"\nArchivo: {filepath}")
            logger.info("\nEstos datos ya están listos para:")
            logger.info("  1. Análisis de sentimiento")
            logger.info("  2. Entrenamiento de modelo")
            logger.info("  3. Identificación de patrones")
        else:
            logger.error("No se pudo crear dataset")
    else:
        logger.error("No se obtuvieron noticias")


if __name__ == "__main__":
    main()

