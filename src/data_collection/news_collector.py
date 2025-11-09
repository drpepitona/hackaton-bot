"""
Recolector de Noticias Financieras Globales
Para análisis de impacto en mercados USA (S&P 500)
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import NEWS_API_KEY, RAW_DATA_DIR
from src.utils.logger import logger


# Categorías de noticias por región
CATEGORIAS_NOTICIAS = {
    'usa': {
        'descripcion': 'Noticias Económicas de Estados Unidos',
        'keywords': [
            'Federal Reserve', 'Fed', 'inflation', 'unemployment', 
            'GDP', 'jobs report', 'CPI', 'interest rates', 'Treasury',
            'Jerome Powell', 'economy', 'recession'
        ],
        'sources': [
            'bloomberg', 'reuters', 'cnbc', 'marketwatch',
            'wall-street-journal', 'financial-times', 'forbes'
        ],
        'impacto': 'ALTO'
    },
    
    'europa': {
        'descripcion': 'Noticias Económicas de Europa',
        'keywords': [
            'ECB', 'European Central Bank', 'eurozone', 'euro', 
            'Christine Lagarde', 'Brexit', 'EU economy', 'Germany economy',
            'France economy', 'UK economy'
        ],
        'sources': [
            'financial-times', 'reuters', 'bloomberg', 'bbc-news'
        ],
        'impacto': 'ALTO'
    },
    
    'asia': {
        'descripcion': 'Noticias Económicas de Asia',
        'keywords': [
            'China economy', 'Japan economy', 'PBOC', 'Bank of Japan',
            'yuan', 'yen', 'Hong Kong', 'Singapore', 'South Korea',
            'India economy', 'Asian markets'
        ],
        'sources': [
            'reuters', 'bloomberg', 'south-china-morning-post',
            'financial-times', 'nikkei'
        ],
        'impacto': 'ALTO'
    },
    
    'australia': {
        'descripcion': 'Noticias Económicas de Australia',
        'keywords': [
            'RBA', 'Reserve Bank Australia', 'Australian dollar',
            'Australia economy', 'commodities Australia'
        ],
        'sources': [
            'reuters', 'bloomberg', 'abc-news-au'
        ],
        'impacto': 'MEDIO'
    },
    
    'global': {
        'descripcion': 'Eventos Económicos Globales',
        'keywords': [
            'oil prices', 'crude oil', 'OPEC', 'gold', 'commodities',
            'global economy', 'trade war', 'geopolitical', 'IMF',
            'World Bank', 'sanctions', 'energy crisis'
        ],
        'sources': [
            'reuters', 'bloomberg', 'financial-times', 'cnbc'
        ],
        'impacto': 'ALTO'
    }
}


class NewsCollector:
    """
    Recolector de noticias financieras de múltiples regiones
    Correlaciona noticias con movimientos del S&P 500
    """
    
    def __init__(self, api_key=None):
        """
        Inicializa el recolector de noticias
        
        Args:
            api_key: API key de News API (opcional)
        """
        self.api_key = api_key or NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
        self.noticias = []
        
        logger.info("✓ NewsCollector inicializado")
        if self.api_key:
            logger.info(f"  API Key configurada: {self.api_key[:10]}...")
        else:
            logger.warning("  ⚠ API Key no configurada - funcionalidad limitada")
    
    def obtener_noticias_por_categoria(self, categoria, start_date=None, end_date=None, max_results=100):
        """
        Obtiene noticias de una categoría específica
        
        Args:
            categoria: 'usa', 'europa', 'asia', 'australia', 'global'
            start_date: Fecha inicio
            end_date: Fecha fin
            max_results: Máximo de resultados por query
            
        Returns:
            Lista de noticias
        """
        if categoria not in CATEGORIAS_NOTICIAS:
            logger.error(f"Categoría inválida: {categoria}")
            return []
        
        config = CATEGORIAS_NOTICIAS[categoria]
        logger.info(f"\n📰 Obteniendo noticias: {config['descripcion']}")
        logger.info(f"   Impacto: {config['impacto']}")
        
        if not self.api_key:
            logger.warning("   ⚠ Requiere News API key")
            return self._usar_fuentes_alternativas(categoria, start_date, end_date)
        
        noticias_categoria = []
        
        # Buscar por cada keyword importante
        for keyword in config['keywords'][:5]:  # Primeros 5 keywords más importantes
            try:
                params = {
                    'q': keyword,
                    'language': 'en',
                    'sortBy': 'relevancy',
                    'pageSize': 20,
                    'apiKey': self.api_key
                }
                
                if start_date:
                    params['from'] = start_date.strftime('%Y-%m-%d')
                if end_date:
                    params['to'] = end_date.strftime('%Y-%m-%d')
                
                response = requests.get(self.base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'articles' in data:
                        for article in data['articles']:
                            noticias_categoria.append({
                                'fecha': article.get('publishedAt'),
                                'titulo': article.get('title'),
                                'descripcion': article.get('description'),
                                'fuente': article.get('source', {}).get('name'),
                                'url': article.get('url'),
                                'keyword': keyword,
                                'categoria': categoria,
                                'impacto': config['impacto']
                            })
                        
                        logger.info(f"   ✓ '{keyword}': {len(data['articles'])} noticias")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"   ✗ Error con '{keyword}': {e}")
        
        logger.info(f"   ✓ Total para {categoria}: {len(noticias_categoria)} noticias")
        return noticias_categoria
    
    def _usar_fuentes_alternativas(self, categoria, start_date, end_date):
        """
        Fuentes alternativas cuando no hay API key
        Usa GDELT Project (base de datos pública de noticias)
        """
        logger.info("   Usando fuentes alternativas (GDELT)...")
        
        try:
            # GDELT es una base de datos pública de noticias globales
            # https://www.gdeltproject.org/
            
            logger.info("   ℹ GDELT Project disponible para noticias históricas")
            logger.info("   ℹ Para uso completo, obtén News API key en: https://newsapi.org/register")
            
            return []
            
        except Exception as e:
            logger.error(f"   Error con fuentes alternativas: {e}")
            return []
    
    def obtener_todas_noticias(self, start_date=None, end_date=None):
        """
        Obtiene noticias de todas las regiones
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)  # Último mes
        
        logger.info("="*70)
        logger.info("RECOLECCIÓN DE NOTICIAS FINANCIERAS GLOBALES")
        logger.info("="*70)
        logger.info(f"Período: {start_date.date()} a {end_date.date()}")
        logger.info(f"Categorías: {len(CATEGORIAS_NOTICIAS)}")
        logger.info("")
        
        todas_noticias = []
        
        for categoria in CATEGORIAS_NOTICIAS.keys():
            noticias = self.obtener_noticias_por_categoria(
                categoria, start_date, end_date
            )
            todas_noticias.extend(noticias)
        
        logger.info(f"\n✓ Total de noticias recolectadas: {len(todas_noticias)}")
        
        self.noticias = todas_noticias
        return todas_noticias
    
    def crear_dataset(self, noticias=None):
        """
        Crea DataFrame con las noticias
        """
        if noticias is None:
            noticias = self.noticias
        
        if not noticias:
            logger.warning("No hay noticias para crear dataset")
            return None
        
        df = pd.DataFrame(noticias)
        
        # Convertir fecha
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha')
        
        logger.info(f"✓ Dataset de noticias creado: {df.shape}")
        
        return df
    
    def correlacionar_con_sp500(self, df_noticias, df_sp500):
        """
        Correlaciona noticias con movimientos del S&P 500
        
        Args:
            df_noticias: DataFrame con noticias
            df_sp500: DataFrame con datos del S&P 500
            
        Returns:
            DataFrame con noticias + impacto en S&P 500
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONANDO NOTICIAS CON S&P 500")
        logger.info("="*70)
        
        if df_noticias is None or df_noticias.empty:
            logger.warning("No hay noticias para correlacionar")
            return None
        
        # Asegurar que sp500 tiene índice de fecha
        if not isinstance(df_sp500.index, pd.DatetimeIndex):
            df_sp500.index = pd.to_datetime(df_sp500.index)
        
        # Calcular retorno diario del S&P 500
        df_sp500['Return'] = df_sp500['Close'].pct_change()
        
        # Agregar columnas de impacto
        df_noticias['sp500_return_same_day'] = None
        df_noticias['sp500_return_next_day'] = None
        df_noticias['sp500_volatility'] = None
        
        # Para cada noticia, encontrar el impacto
        for idx, row in df_noticias.iterrows():
            fecha_noticia = row['fecha'].date() if pd.notna(row['fecha']) else None
            
            if fecha_noticia:
                try:
                    # Retorno mismo día
                    if fecha_noticia in df_sp500.index.date:
                        df_noticias.at[idx, 'sp500_return_same_day'] = \
                            df_sp500.loc[df_sp500.index.date == fecha_noticia, 'Return'].values[0]
                    
                    # Retorno día siguiente
                    fecha_siguiente = fecha_noticia + timedelta(days=1)
                    if fecha_siguiente in df_sp500.index.date:
                        df_noticias.at[idx, 'sp500_return_next_day'] = \
                            df_sp500.loc[df_sp500.index.date == fecha_siguiente, 'Return'].values[0]
                    
                    # Volatilidad (desv. std. de retornos en ventana de 5 días)
                    mask = (df_sp500.index.date >= fecha_noticia - timedelta(days=5)) & \
                           (df_sp500.index.date <= fecha_noticia)
                    if mask.sum() > 0:
                        df_noticias.at[idx, 'sp500_volatility'] = \
                            df_sp500.loc[mask, 'Return'].std()
                    
                except Exception as e:
                    continue
        
        # Clasificar impacto
        df_noticias['impacto_clasificado'] = pd.cut(
            df_noticias['sp500_return_next_day'].abs(),
            bins=[-float('inf'), 0.005, 0.02, float('inf')],
            labels=['BAJO', 'MEDIO', 'ALTO']
        )
        
        logger.info(f"✓ Correlación completada")
        logger.info(f"  Noticias con datos: {df_noticias['sp500_return_same_day'].notna().sum()}")
        
        return df_noticias
    
    def guardar_datos(self, df, nombre_archivo='noticias_financieras'):
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
        filepath = news_dir / f"{nombre_archivo}_{timestamp}.csv"
        
        df.to_csv(filepath, index=False)
        logger.info(f"✓ Noticias guardadas: {filepath}")
        
        return filepath
    
    def generar_reporte(self, df_noticias):
        """
        Genera reporte de noticias recolectadas
        """
        if df_noticias is None or df_noticias.empty:
            return
        
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE NOTICIAS")
        logger.info("="*70)
        
        # Por categoría
        logger.info("\nDistribución por región:")
        for cat in df_noticias['categoria'].unique():
            count = len(df_noticias[df_noticias['categoria'] == cat])
            logger.info(f"  {cat}: {count} noticias")
        
        # Por impacto
        if 'impacto_clasificado' in df_noticias.columns:
            logger.info("\nDistribución por impacto en S&P 500:")
            for imp in ['ALTO', 'MEDIO', 'BAJO']:
                count = len(df_noticias[df_noticias['impacto_clasificado'] == imp])
                if count > 0:
                    pct = (count / len(df_noticias)) * 100
                    logger.info(f"  {imp}: {count} noticias ({pct:.1f}%)")
        
        # Noticias de mayor impacto
        if 'sp500_return_next_day' in df_noticias.columns:
            logger.info("\nTop 5 noticias con MAYOR impacto positivo:")
            top_positivas = df_noticias.nlargest(5, 'sp500_return_next_day')
            for idx, row in top_positivas.iterrows():
                logger.info(f"  {row['fecha']}: {row['titulo'][:60]}...")
                logger.info(f"    Impacto: +{row['sp500_return_next_day']*100:.2f}%")
            
            logger.info("\nTop 5 noticias con MAYOR impacto negativo:")
            top_negativas = df_noticias.nsmallest(5, 'sp500_return_next_day')
            for idx, row in top_negativas.iterrows():
                logger.info(f"  {row['fecha']}: {row['titulo'][:60]}...")
                logger.info(f"    Impacto: {row['sp500_return_next_day']*100:.2f}%")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE NOTICIAS FINANCIERAS GLOBALES")
    logger.info("Para predicción de impacto en S&P 500")
    logger.info("="*70)
    
    # Crear recolector
    collector = NewsCollector()
    
    if not collector.api_key:
        logger.warning("\n" + "!"*70)
        logger.warning("IMPORTANTE: News API key no configurada")
        logger.warning("!"*70)
        logger.warning("\nPara obtener noticias necesitas:")
        logger.warning("  1. Registrarte en: https://newsapi.org/register")
        logger.warning("  2. Obtener API key (GRATIS, 100 requests/día)")
        logger.warning("  3. Agregar a .env: NEWS_API_KEY=tu_key_aqui")
        logger.warning("\nAlternativas sin API key:")
        logger.warning("  - GDELT Project (noticias históricas)")
        logger.warning("  - Web scraping (requiere más código)")
        logger.warning("  - Datasets públicos de Kaggle")
        logger.info("\n" + "!"*70)
        return
    
    # Obtener noticias del último mes
    logger.info("\n1. Obteniendo noticias...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    noticias = collector.obtener_todas_noticias(start_date, end_date)
    
    if noticias:
        # Crear dataset
        logger.info("\n2. Creando dataset...")
        df_noticias = collector.crear_dataset(noticias)
        
        # Cargar datos del S&P 500
        logger.info("\n3. Cargando datos del S&P 500...")
        try:
            # Buscar archivo más reciente del SPY
            spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
            if spy_files:
                spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
                df_sp500 = pd.read_csv(spy_file, index_col=0, parse_dates=True)
                logger.info(f"  ✓ S&P 500 cargado: {len(df_sp500)} días")
                
                # Correlacionar
                logger.info("\n4. Correlacionando con movimientos del mercado...")
                df_correlacionado = collector.correlacionar_con_sp500(df_noticias, df_sp500)
                
                # Guardar
                logger.info("\n5. Guardando datos...")
                collector.guardar_datos(df_correlacionado, 'noticias_correlacionadas')
                
                # Reporte
                logger.info("\n6. Generando reporte...")
                collector.generar_reporte(df_correlacionado)
                
            else:
                logger.error("  ✗ No se encontraron datos del S&P 500")
                collector.guardar_datos(df_noticias, 'noticias_sin_correlacionar')
        
        except Exception as e:
            logger.error(f"Error en proceso: {e}")
            collector.guardar_datos(df_noticias, 'noticias_sin_correlacionar')
        
        logger.info("\n" + "="*70)
        logger.info("✓ PROCESO COMPLETADO")
        logger.info("="*70)
    else:
        logger.warning("No se obtuvieron noticias")


if __name__ == "__main__":
    main()

Recolector de Noticias Financieras Globales
Para análisis de impacto en mercados USA (S&P 500)
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import NEWS_API_KEY, RAW_DATA_DIR
from src.utils.logger import logger


# Categorías de noticias por región
CATEGORIAS_NOTICIAS = {
    'usa': {
        'descripcion': 'Noticias Económicas de Estados Unidos',
        'keywords': [
            'Federal Reserve', 'Fed', 'inflation', 'unemployment', 
            'GDP', 'jobs report', 'CPI', 'interest rates', 'Treasury',
            'Jerome Powell', 'economy', 'recession'
        ],
        'sources': [
            'bloomberg', 'reuters', 'cnbc', 'marketwatch',
            'wall-street-journal', 'financial-times', 'forbes'
        ],
        'impacto': 'ALTO'
    },
    
    'europa': {
        'descripcion': 'Noticias Económicas de Europa',
        'keywords': [
            'ECB', 'European Central Bank', 'eurozone', 'euro', 
            'Christine Lagarde', 'Brexit', 'EU economy', 'Germany economy',
            'France economy', 'UK economy'
        ],
        'sources': [
            'financial-times', 'reuters', 'bloomberg', 'bbc-news'
        ],
        'impacto': 'ALTO'
    },
    
    'asia': {
        'descripcion': 'Noticias Económicas de Asia',
        'keywords': [
            'China economy', 'Japan economy', 'PBOC', 'Bank of Japan',
            'yuan', 'yen', 'Hong Kong', 'Singapore', 'South Korea',
            'India economy', 'Asian markets'
        ],
        'sources': [
            'reuters', 'bloomberg', 'south-china-morning-post',
            'financial-times', 'nikkei'
        ],
        'impacto': 'ALTO'
    },
    
    'australia': {
        'descripcion': 'Noticias Económicas de Australia',
        'keywords': [
            'RBA', 'Reserve Bank Australia', 'Australian dollar',
            'Australia economy', 'commodities Australia'
        ],
        'sources': [
            'reuters', 'bloomberg', 'abc-news-au'
        ],
        'impacto': 'MEDIO'
    },
    
    'global': {
        'descripcion': 'Eventos Económicos Globales',
        'keywords': [
            'oil prices', 'crude oil', 'OPEC', 'gold', 'commodities',
            'global economy', 'trade war', 'geopolitical', 'IMF',
            'World Bank', 'sanctions', 'energy crisis'
        ],
        'sources': [
            'reuters', 'bloomberg', 'financial-times', 'cnbc'
        ],
        'impacto': 'ALTO'
    }
}


class NewsCollector:
    """
    Recolector de noticias financieras de múltiples regiones
    Correlaciona noticias con movimientos del S&P 500
    """
    
    def __init__(self, api_key=None):
        """
        Inicializa el recolector de noticias
        
        Args:
            api_key: API key de News API (opcional)
        """
        self.api_key = api_key or NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
        self.noticias = []
        
        logger.info("✓ NewsCollector inicializado")
        if self.api_key:
            logger.info(f"  API Key configurada: {self.api_key[:10]}...")
        else:
            logger.warning("  ⚠ API Key no configurada - funcionalidad limitada")
    
    def obtener_noticias_por_categoria(self, categoria, start_date=None, end_date=None, max_results=100):
        """
        Obtiene noticias de una categoría específica
        
        Args:
            categoria: 'usa', 'europa', 'asia', 'australia', 'global'
            start_date: Fecha inicio
            end_date: Fecha fin
            max_results: Máximo de resultados por query
            
        Returns:
            Lista de noticias
        """
        if categoria not in CATEGORIAS_NOTICIAS:
            logger.error(f"Categoría inválida: {categoria}")
            return []
        
        config = CATEGORIAS_NOTICIAS[categoria]
        logger.info(f"\n📰 Obteniendo noticias: {config['descripcion']}")
        logger.info(f"   Impacto: {config['impacto']}")
        
        if not self.api_key:
            logger.warning("   ⚠ Requiere News API key")
            return self._usar_fuentes_alternativas(categoria, start_date, end_date)
        
        noticias_categoria = []
        
        # Buscar por cada keyword importante
        for keyword in config['keywords'][:5]:  # Primeros 5 keywords más importantes
            try:
                params = {
                    'q': keyword,
                    'language': 'en',
                    'sortBy': 'relevancy',
                    'pageSize': 20,
                    'apiKey': self.api_key
                }
                
                if start_date:
                    params['from'] = start_date.strftime('%Y-%m-%d')
                if end_date:
                    params['to'] = end_date.strftime('%Y-%m-%d')
                
                response = requests.get(self.base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'articles' in data:
                        for article in data['articles']:
                            noticias_categoria.append({
                                'fecha': article.get('publishedAt'),
                                'titulo': article.get('title'),
                                'descripcion': article.get('description'),
                                'fuente': article.get('source', {}).get('name'),
                                'url': article.get('url'),
                                'keyword': keyword,
                                'categoria': categoria,
                                'impacto': config['impacto']
                            })
                        
                        logger.info(f"   ✓ '{keyword}': {len(data['articles'])} noticias")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"   ✗ Error con '{keyword}': {e}")
        
        logger.info(f"   ✓ Total para {categoria}: {len(noticias_categoria)} noticias")
        return noticias_categoria
    
    def _usar_fuentes_alternativas(self, categoria, start_date, end_date):
        """
        Fuentes alternativas cuando no hay API key
        Usa GDELT Project (base de datos pública de noticias)
        """
        logger.info("   Usando fuentes alternativas (GDELT)...")
        
        try:
            # GDELT es una base de datos pública de noticias globales
            # https://www.gdeltproject.org/
            
            logger.info("   ℹ GDELT Project disponible para noticias históricas")
            logger.info("   ℹ Para uso completo, obtén News API key en: https://newsapi.org/register")
            
            return []
            
        except Exception as e:
            logger.error(f"   Error con fuentes alternativas: {e}")
            return []
    
    def obtener_todas_noticias(self, start_date=None, end_date=None):
        """
        Obtiene noticias de todas las regiones
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=30)  # Último mes
        
        logger.info("="*70)
        logger.info("RECOLECCIÓN DE NOTICIAS FINANCIERAS GLOBALES")
        logger.info("="*70)
        logger.info(f"Período: {start_date.date()} a {end_date.date()}")
        logger.info(f"Categorías: {len(CATEGORIAS_NOTICIAS)}")
        logger.info("")
        
        todas_noticias = []
        
        for categoria in CATEGORIAS_NOTICIAS.keys():
            noticias = self.obtener_noticias_por_categoria(
                categoria, start_date, end_date
            )
            todas_noticias.extend(noticias)
        
        logger.info(f"\n✓ Total de noticias recolectadas: {len(todas_noticias)}")
        
        self.noticias = todas_noticias
        return todas_noticias
    
    def crear_dataset(self, noticias=None):
        """
        Crea DataFrame con las noticias
        """
        if noticias is None:
            noticias = self.noticias
        
        if not noticias:
            logger.warning("No hay noticias para crear dataset")
            return None
        
        df = pd.DataFrame(noticias)
        
        # Convertir fecha
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha')
        
        logger.info(f"✓ Dataset de noticias creado: {df.shape}")
        
        return df
    
    def correlacionar_con_sp500(self, df_noticias, df_sp500):
        """
        Correlaciona noticias con movimientos del S&P 500
        
        Args:
            df_noticias: DataFrame con noticias
            df_sp500: DataFrame con datos del S&P 500
            
        Returns:
            DataFrame con noticias + impacto en S&P 500
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONANDO NOTICIAS CON S&P 500")
        logger.info("="*70)
        
        if df_noticias is None or df_noticias.empty:
            logger.warning("No hay noticias para correlacionar")
            return None
        
        # Asegurar que sp500 tiene índice de fecha
        if not isinstance(df_sp500.index, pd.DatetimeIndex):
            df_sp500.index = pd.to_datetime(df_sp500.index)
        
        # Calcular retorno diario del S&P 500
        df_sp500['Return'] = df_sp500['Close'].pct_change()
        
        # Agregar columnas de impacto
        df_noticias['sp500_return_same_day'] = None
        df_noticias['sp500_return_next_day'] = None
        df_noticias['sp500_volatility'] = None
        
        # Para cada noticia, encontrar el impacto
        for idx, row in df_noticias.iterrows():
            fecha_noticia = row['fecha'].date() if pd.notna(row['fecha']) else None
            
            if fecha_noticia:
                try:
                    # Retorno mismo día
                    if fecha_noticia in df_sp500.index.date:
                        df_noticias.at[idx, 'sp500_return_same_day'] = \
                            df_sp500.loc[df_sp500.index.date == fecha_noticia, 'Return'].values[0]
                    
                    # Retorno día siguiente
                    fecha_siguiente = fecha_noticia + timedelta(days=1)
                    if fecha_siguiente in df_sp500.index.date:
                        df_noticias.at[idx, 'sp500_return_next_day'] = \
                            df_sp500.loc[df_sp500.index.date == fecha_siguiente, 'Return'].values[0]
                    
                    # Volatilidad (desv. std. de retornos en ventana de 5 días)
                    mask = (df_sp500.index.date >= fecha_noticia - timedelta(days=5)) & \
                           (df_sp500.index.date <= fecha_noticia)
                    if mask.sum() > 0:
                        df_noticias.at[idx, 'sp500_volatility'] = \
                            df_sp500.loc[mask, 'Return'].std()
                    
                except Exception as e:
                    continue
        
        # Clasificar impacto
        df_noticias['impacto_clasificado'] = pd.cut(
            df_noticias['sp500_return_next_day'].abs(),
            bins=[-float('inf'), 0.005, 0.02, float('inf')],
            labels=['BAJO', 'MEDIO', 'ALTO']
        )
        
        logger.info(f"✓ Correlación completada")
        logger.info(f"  Noticias con datos: {df_noticias['sp500_return_same_day'].notna().sum()}")
        
        return df_noticias
    
    def guardar_datos(self, df, nombre_archivo='noticias_financieras'):
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
        filepath = news_dir / f"{nombre_archivo}_{timestamp}.csv"
        
        df.to_csv(filepath, index=False)
        logger.info(f"✓ Noticias guardadas: {filepath}")
        
        return filepath
    
    def generar_reporte(self, df_noticias):
        """
        Genera reporte de noticias recolectadas
        """
        if df_noticias is None or df_noticias.empty:
            return
        
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE NOTICIAS")
        logger.info("="*70)
        
        # Por categoría
        logger.info("\nDistribución por región:")
        for cat in df_noticias['categoria'].unique():
            count = len(df_noticias[df_noticias['categoria'] == cat])
            logger.info(f"  {cat}: {count} noticias")
        
        # Por impacto
        if 'impacto_clasificado' in df_noticias.columns:
            logger.info("\nDistribución por impacto en S&P 500:")
            for imp in ['ALTO', 'MEDIO', 'BAJO']:
                count = len(df_noticias[df_noticias['impacto_clasificado'] == imp])
                if count > 0:
                    pct = (count / len(df_noticias)) * 100
                    logger.info(f"  {imp}: {count} noticias ({pct:.1f}%)")
        
        # Noticias de mayor impacto
        if 'sp500_return_next_day' in df_noticias.columns:
            logger.info("\nTop 5 noticias con MAYOR impacto positivo:")
            top_positivas = df_noticias.nlargest(5, 'sp500_return_next_day')
            for idx, row in top_positivas.iterrows():
                logger.info(f"  {row['fecha']}: {row['titulo'][:60]}...")
                logger.info(f"    Impacto: +{row['sp500_return_next_day']*100:.2f}%")
            
            logger.info("\nTop 5 noticias con MAYOR impacto negativo:")
            top_negativas = df_noticias.nsmallest(5, 'sp500_return_next_day')
            for idx, row in top_negativas.iterrows():
                logger.info(f"  {row['fecha']}: {row['titulo'][:60]}...")
                logger.info(f"    Impacto: {row['sp500_return_next_day']*100:.2f}%")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE NOTICIAS FINANCIERAS GLOBALES")
    logger.info("Para predicción de impacto en S&P 500")
    logger.info("="*70)
    
    # Crear recolector
    collector = NewsCollector()
    
    if not collector.api_key:
        logger.warning("\n" + "!"*70)
        logger.warning("IMPORTANTE: News API key no configurada")
        logger.warning("!"*70)
        logger.warning("\nPara obtener noticias necesitas:")
        logger.warning("  1. Registrarte en: https://newsapi.org/register")
        logger.warning("  2. Obtener API key (GRATIS, 100 requests/día)")
        logger.warning("  3. Agregar a .env: NEWS_API_KEY=tu_key_aqui")
        logger.warning("\nAlternativas sin API key:")
        logger.warning("  - GDELT Project (noticias históricas)")
        logger.warning("  - Web scraping (requiere más código)")
        logger.warning("  - Datasets públicos de Kaggle")
        logger.info("\n" + "!"*70)
        return
    
    # Obtener noticias del último mes
    logger.info("\n1. Obteniendo noticias...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    noticias = collector.obtener_todas_noticias(start_date, end_date)
    
    if noticias:
        # Crear dataset
        logger.info("\n2. Creando dataset...")
        df_noticias = collector.crear_dataset(noticias)
        
        # Cargar datos del S&P 500
        logger.info("\n3. Cargando datos del S&P 500...")
        try:
            # Buscar archivo más reciente del SPY
            spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
            if spy_files:
                spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
                df_sp500 = pd.read_csv(spy_file, index_col=0, parse_dates=True)
                logger.info(f"  ✓ S&P 500 cargado: {len(df_sp500)} días")
                
                # Correlacionar
                logger.info("\n4. Correlacionando con movimientos del mercado...")
                df_correlacionado = collector.correlacionar_con_sp500(df_noticias, df_sp500)
                
                # Guardar
                logger.info("\n5. Guardando datos...")
                collector.guardar_datos(df_correlacionado, 'noticias_correlacionadas')
                
                # Reporte
                logger.info("\n6. Generando reporte...")
                collector.generar_reporte(df_correlacionado)
                
            else:
                logger.error("  ✗ No se encontraron datos del S&P 500")
                collector.guardar_datos(df_noticias, 'noticias_sin_correlacionar')
        
        except Exception as e:
            logger.error(f"Error en proceso: {e}")
            collector.guardar_datos(df_noticias, 'noticias_sin_correlacionar')
        
        logger.info("\n" + "="*70)
        logger.info("✓ PROCESO COMPLETADO")
        logger.info("="*70)
    else:
        logger.warning("No se obtuvieron noticias")


if __name__ == "__main__":
    main()



