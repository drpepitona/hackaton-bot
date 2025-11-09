"""
Recolector de Noticias usando GDELT Project
GDELT es una base de datos GRATIS de noticias globales
No requiere API key
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class GDELTNewsCollector:
    """
    Recolector de noticias usando GDELT Project
    GDELT monitorea noticias de todo el mundo en tiempo real
    100% GRATIS, sin API key necesaria
    """
    
    def __init__(self):
        """Inicializa el recolector"""
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        logger.info("✓ GDELTNewsCollector inicializado")
        logger.info("  Usando GDELT Project (GRATIS, sin API key)")
    
    def buscar_noticias(self, query, start_date=None, max_results=250):
        """
        Busca noticias en GDELT
        
        Args:
            query: Términos de búsqueda
            start_date: Fecha inicio (últimos N días)
            max_results: Máximo de resultados
            
        Returns:
            Lista de noticias
        """
        try:
            logger.info(f"  Buscando: '{query}'...")
            
            params = {
                'query': query,
                'mode': 'artlist',
                'maxrecords': max_results,
                'format': 'json',
                'sort': 'hybridrel'
            }
            
            # Agregar rango de fechas si se especifica
            if start_date:
                params['startdatetime'] = start_date.strftime('%Y%m%d%H%M%S')
                params['enddatetime'] = datetime.now().strftime('%Y%m%d%H%M%S')
            
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'articles' in data:
                    logger.info(f"    ✓ {len(data['articles'])} noticias encontradas")
                    return data['articles']
                else:
                    logger.warning(f"    No se encontraron noticias")
                    return []
            else:
                logger.error(f"    Error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"    Error al buscar '{query}': {e}")
            return []
    
    def obtener_noticias_economicas_globales(self, dias_atras=30):
        """
        Obtiene noticias económicas de todas las regiones
        
        Args:
            dias_atras: Número de días hacia atrás
            
        Returns:
            DataFrame con noticias
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO NOTICIAS ECONÓMICAS GLOBALES")
        logger.info("="*70)
        logger.info(f"Período: Últimos {dias_atras} días")
        logger.info("")
        
        start_date = datetime.now() - timedelta(days=dias_atras)
        
        # Queries organizadas por región e impacto
        queries = {
            'usa_alta': [
                'Federal Reserve interest rates',
                'US inflation rate',
                'US employment report',
                'Fed Powell speech',
                'US GDP growth'
            ],
            'europa_alta': [
                'ECB interest rates',
                'eurozone inflation',
                'European Central Bank',
                'Germany economy',
                'Brexit impact'
            ],
            'asia_alta': [
                'China economy GDP',
                'Bank of Japan policy',
                'China inflation',
                'Japan economy',
                'Asian markets crash'
            ],
            'australia': [
                'RBA Reserve Bank Australia',
                'Australian dollar economy',
                'Australia inflation'
            ],
            'global_alta': [
                'oil prices OPEC',
                'gold prices surge',
                'global recession',
                'trade war',
                'energy crisis'
            ]
        }
        
        todas_noticias = []
        
        for region, keywords in queries.items():
            logger.info(f"\n📰 REGIÓN: {region.upper()}")
            logger.info("-"*70)
            
            for keyword in keywords:
                noticias = self.buscar_noticias(keyword, start_date, max_results=50)
                
                # Agregar metadata
                for noticia in noticias:
                    noticia['region'] = region
                    noticia['keyword'] = keyword
                    noticia['impacto_esperado'] = 'ALTO' if 'alta' in region else 'MEDIO'
                
                todas_noticias.extend(noticias)
                time.sleep(1)  # Rate limiting
        
        logger.info(f"\n✓ Total de noticias recolectadas: {len(todas_noticias)}")
        
        # Crear DataFrame
        if todas_noticias:
            df = pd.DataFrame(todas_noticias)
            
            # Procesar fechas
            if 'seendate' in df.columns:
                df['fecha'] = pd.to_datetime(df['seendate'], format='%Y%m%dT%H%M%SZ', errors='coerce')
            
            # Seleccionar columnas importantes
            columnas_importantes = [
                'fecha', 'title', 'url', 'domain', 'language',
                'region', 'keyword', 'impacto_esperado', 'seendate'
            ]
            
            columnas_existentes = [col for col in columnas_importantes if col in df.columns]
            df = df[columnas_existentes]
            
            # Eliminar duplicados
            if 'url' in df.columns:
                df = df.drop_duplicates(subset=['url'])
                logger.info(f"  Noticias únicas: {len(df)}")
            
            # Ordenar por fecha
            if 'fecha' in df.columns:
                df = df.sort_values('fecha', ascending=False)
            
            return df
        
        return None
    
    def correlacionar_con_sp500(self, df_noticias, df_sp500_path):
        """
        Correlaciona noticias con movimientos del S&P 500
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONANDO CON MOVIMIENTOS DEL S&P 500")
        logger.info("="*70)
        
        # Cargar S&P 500
        df_sp500 = pd.read_csv(df_sp500_path, index_col=0, parse_dates=True)
        df_sp500['Return'] = df_sp500['Close'].pct_change()
        
        logger.info(f"  S&P 500: {len(df_sp500)} días cargados")
        
        # Agregar columnas de impacto
        df_noticias['sp500_return_day'] = 0.0
        df_noticias['sp500_return_next_day'] = 0.0
        df_noticias['sp500_move_direction'] = 'neutral'
        
        # Correlacionar cada noticia
        correlacionadas = 0
        
        for idx, row in df_noticias.iterrows():
            if pd.isna(row['fecha']):
                continue
            
            fecha_noticia = row['fecha'].date()
            
            try:
                # Buscar día de la noticia
                mask = df_sp500.index.date == fecha_noticia
                if mask.sum() > 0:
                    retorno = df_sp500.loc[mask, 'Return'].values[0]
                    if pd.notna(retorno):
                        df_noticias.at[idx, 'sp500_return_day'] = retorno
                        correlacionadas += 1
                
                # Buscar día siguiente
                fecha_siguiente = fecha_noticia + timedelta(days=1)
                # Buscar hasta 3 días después (por fines de semana)
                for i in range(1, 4):
                    fecha_buscar = fecha_noticia + timedelta(days=i)
                    mask_next = df_sp500.index.date == fecha_buscar
                    if mask_next.sum() > 0:
                        retorno_next = df_sp500.loc[mask_next, 'Return'].values[0]
                        if pd.notna(retorno_next):
                            df_noticias.at[idx, 'sp500_return_next_day'] = retorno_next
                            
                            # Clasificar dirección
                            if retorno_next > 0.01:
                                df_noticias.at[idx, 'sp500_move_direction'] = 'UP'
                            elif retorno_next < -0.01:
                                df_noticias.at[idx, 'sp500_move_direction'] = 'DOWN'
                            else:
                                df_noticias.at[idx, 'sp500_move_direction'] = 'FLAT'
                            break
            
            except Exception as e:
                continue
        
        # Clasificar impacto
        df_noticias['impacto_absoluto'] = df_noticias['sp500_return_next_day'].abs()
        df_noticias['impacto_clasificado'] = pd.cut(
            df_noticias['impacto_absoluto'],
            bins=[0, 0.005, 0.015, 1.0],
            labels=['BAJO', 'MEDIO', 'ALTO']
        )
        
        logger.info(f"\n✓ Correlación completada")
        logger.info(f"  Noticias correlacionadas: {correlacionadas}/{len(df_noticias)}")
        
        return df_noticias


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("SISTEMA DE NOTICIAS - GDELT PROJECT")
    logger.info("="*70)
    logger.info("GDELT = Base de datos global de eventos y noticias")
    logger.info("100% GRATIS, sin API key necesaria")
    logger.info("")
    
    # Crear recolector
    collector = GDELTNewsCollector()
    
    # Obtener noticias
    logger.info("\n1. Obteniendo noticias económicas globales...")
    df_noticias = collector.obtener_noticias_economicas_globales(dias_atras=90)
    
    if df_noticias is not None and not df_noticias.empty:
        # Buscar archivo del S&P 500
        logger.info("\n2. Buscando datos del S&P 500...")
        spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
        
        if spy_files:
            spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"  ✓ Archivo encontrado: {spy_file.name}")
            
            # Correlacionar
            logger.info("\n3. Correlacionando noticias con S&P 500...")
            df_correlacionado = collector.correlacionar_con_sp500(df_noticias, spy_file)
            
            # Guardar
            logger.info("\n4. Guardando datos...")
            news_dir = RAW_DATA_DIR.parent / "processed" / "news"
            news_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d')
            filepath = news_dir / f"noticias_gdelt_correlacionadas_{timestamp}.csv"
            df_correlacionado.to_csv(filepath, index=False)
            logger.info(f"  ✓ Datos guardados: {filepath}")
            
            # Generar estadísticas
            logger.info("\n5. Generando reporte...")
            logger.info("="*70)
            logger.info("REPORTE DE NOTICIAS Y SU IMPACTO")
            logger.info("="*70)
            
            logger.info(f"\nTotal de noticias: {len(df_correlacionado)}")
            logger.info(f"Período: {df_correlacionado['fecha'].min()} a {df_correlacionado['fecha'].max()}")
            
            # Por región
            logger.info("\nDistribución por región:")
            for region in df_correlacionado['region'].value_counts().head(10).items():
                logger.info(f"  {region[0]}: {region[1]} noticias")
            
            # Por impacto
            if 'impacto_clasificado' in df_correlacionado.columns:
                logger.info("\nDistribución por impacto en S&P 500:")
                for imp in ['ALTO', 'MEDIO', 'BAJO']:
                    count = len(df_correlacionado[df_correlacionado['impacto_clasificado'] == imp])
                    if count > 0:
                        logger.info(f"  {imp}: {count} noticias")
            
            # Top impactos
            logger.info("\nTop 10 noticias con MAYOR impacto (↑):")
            top_up = df_correlacionado.nlargest(10, 'sp500_return_next_day')
            for idx, row in top_up.iterrows():
                if pd.notna(row['title']) and pd.notna(row['sp500_return_next_day']):
                    logger.info(f"  +{row['sp500_return_next_day']*100:.2f}% | {row['title'][:70]}")
            
            logger.info("\nTop 10 noticias con MAYOR caída (↓):")
            top_down = df_correlacionado.nsmallest(10, 'sp500_return_next_day')
            for idx, row in top_down.iterrows():
                if pd.notna(row['title']) and pd.notna(row['sp500_return_next_day']):
                    logger.info(f"  {row['sp500_return_next_day']*100:.2f}% | {row['title'][:70]}")
            
            logger.info("\n" + "="*70)
            logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
            logger.info("="*70)
            logger.info(f"\nArchivo guardado: {filepath}")
            logger.info("\nEstos datos ya están listos para:")
            logger.info("  1. Análisis de sentimiento (BERT)")
            logger.info("  2. Entrenamiento de modelo predictivo")
            logger.info("  3. Identificación de patrones de impacto")
            
        else:
            logger.error("No se encontraron datos del S&P 500")
            logger.info("Ejecuta primero: py src/data_collection/market_collector.py")
    
    else:
        logger.error("No se obtuvieron noticias")


if __name__ == "__main__":
    main()


GDELT es una base de datos GRATIS de noticias globales
No requiere API key
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class GDELTNewsCollector:
    """
    Recolector de noticias usando GDELT Project
    GDELT monitorea noticias de todo el mundo en tiempo real
    100% GRATIS, sin API key necesaria
    """
    
    def __init__(self):
        """Inicializa el recolector"""
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        logger.info("✓ GDELTNewsCollector inicializado")
        logger.info("  Usando GDELT Project (GRATIS, sin API key)")
    
    def buscar_noticias(self, query, start_date=None, max_results=250):
        """
        Busca noticias en GDELT
        
        Args:
            query: Términos de búsqueda
            start_date: Fecha inicio (últimos N días)
            max_results: Máximo de resultados
            
        Returns:
            Lista de noticias
        """
        try:
            logger.info(f"  Buscando: '{query}'...")
            
            params = {
                'query': query,
                'mode': 'artlist',
                'maxrecords': max_results,
                'format': 'json',
                'sort': 'hybridrel'
            }
            
            # Agregar rango de fechas si se especifica
            if start_date:
                params['startdatetime'] = start_date.strftime('%Y%m%d%H%M%S')
                params['enddatetime'] = datetime.now().strftime('%Y%m%d%H%M%S')
            
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'articles' in data:
                    logger.info(f"    ✓ {len(data['articles'])} noticias encontradas")
                    return data['articles']
                else:
                    logger.warning(f"    No se encontraron noticias")
                    return []
            else:
                logger.error(f"    Error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"    Error al buscar '{query}': {e}")
            return []
    
    def obtener_noticias_economicas_globales(self, dias_atras=30):
        """
        Obtiene noticias económicas de todas las regiones
        
        Args:
            dias_atras: Número de días hacia atrás
            
        Returns:
            DataFrame con noticias
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO NOTICIAS ECONÓMICAS GLOBALES")
        logger.info("="*70)
        logger.info(f"Período: Últimos {dias_atras} días")
        logger.info("")
        
        start_date = datetime.now() - timedelta(days=dias_atras)
        
        # Queries organizadas por región e impacto
        queries = {
            'usa_alta': [
                'Federal Reserve interest rates',
                'US inflation rate',
                'US employment report',
                'Fed Powell speech',
                'US GDP growth'
            ],
            'europa_alta': [
                'ECB interest rates',
                'eurozone inflation',
                'European Central Bank',
                'Germany economy',
                'Brexit impact'
            ],
            'asia_alta': [
                'China economy GDP',
                'Bank of Japan policy',
                'China inflation',
                'Japan economy',
                'Asian markets crash'
            ],
            'australia': [
                'RBA Reserve Bank Australia',
                'Australian dollar economy',
                'Australia inflation'
            ],
            'global_alta': [
                'oil prices OPEC',
                'gold prices surge',
                'global recession',
                'trade war',
                'energy crisis'
            ]
        }
        
        todas_noticias = []
        
        for region, keywords in queries.items():
            logger.info(f"\n📰 REGIÓN: {region.upper()}")
            logger.info("-"*70)
            
            for keyword in keywords:
                noticias = self.buscar_noticias(keyword, start_date, max_results=50)
                
                # Agregar metadata
                for noticia in noticias:
                    noticia['region'] = region
                    noticia['keyword'] = keyword
                    noticia['impacto_esperado'] = 'ALTO' if 'alta' in region else 'MEDIO'
                
                todas_noticias.extend(noticias)
                time.sleep(1)  # Rate limiting
        
        logger.info(f"\n✓ Total de noticias recolectadas: {len(todas_noticias)}")
        
        # Crear DataFrame
        if todas_noticias:
            df = pd.DataFrame(todas_noticias)
            
            # Procesar fechas
            if 'seendate' in df.columns:
                df['fecha'] = pd.to_datetime(df['seendate'], format='%Y%m%dT%H%M%SZ', errors='coerce')
            
            # Seleccionar columnas importantes
            columnas_importantes = [
                'fecha', 'title', 'url', 'domain', 'language',
                'region', 'keyword', 'impacto_esperado', 'seendate'
            ]
            
            columnas_existentes = [col for col in columnas_importantes if col in df.columns]
            df = df[columnas_existentes]
            
            # Eliminar duplicados
            if 'url' in df.columns:
                df = df.drop_duplicates(subset=['url'])
                logger.info(f"  Noticias únicas: {len(df)}")
            
            # Ordenar por fecha
            if 'fecha' in df.columns:
                df = df.sort_values('fecha', ascending=False)
            
            return df
        
        return None
    
    def correlacionar_con_sp500(self, df_noticias, df_sp500_path):
        """
        Correlaciona noticias con movimientos del S&P 500
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONANDO CON MOVIMIENTOS DEL S&P 500")
        logger.info("="*70)
        
        # Cargar S&P 500
        df_sp500 = pd.read_csv(df_sp500_path, index_col=0, parse_dates=True)
        df_sp500['Return'] = df_sp500['Close'].pct_change()
        
        logger.info(f"  S&P 500: {len(df_sp500)} días cargados")
        
        # Agregar columnas de impacto
        df_noticias['sp500_return_day'] = 0.0
        df_noticias['sp500_return_next_day'] = 0.0
        df_noticias['sp500_move_direction'] = 'neutral'
        
        # Correlacionar cada noticia
        correlacionadas = 0
        
        for idx, row in df_noticias.iterrows():
            if pd.isna(row['fecha']):
                continue
            
            fecha_noticia = row['fecha'].date()
            
            try:
                # Buscar día de la noticia
                mask = df_sp500.index.date == fecha_noticia
                if mask.sum() > 0:
                    retorno = df_sp500.loc[mask, 'Return'].values[0]
                    if pd.notna(retorno):
                        df_noticias.at[idx, 'sp500_return_day'] = retorno
                        correlacionadas += 1
                
                # Buscar día siguiente
                fecha_siguiente = fecha_noticia + timedelta(days=1)
                # Buscar hasta 3 días después (por fines de semana)
                for i in range(1, 4):
                    fecha_buscar = fecha_noticia + timedelta(days=i)
                    mask_next = df_sp500.index.date == fecha_buscar
                    if mask_next.sum() > 0:
                        retorno_next = df_sp500.loc[mask_next, 'Return'].values[0]
                        if pd.notna(retorno_next):
                            df_noticias.at[idx, 'sp500_return_next_day'] = retorno_next
                            
                            # Clasificar dirección
                            if retorno_next > 0.01:
                                df_noticias.at[idx, 'sp500_move_direction'] = 'UP'
                            elif retorno_next < -0.01:
                                df_noticias.at[idx, 'sp500_move_direction'] = 'DOWN'
                            else:
                                df_noticias.at[idx, 'sp500_move_direction'] = 'FLAT'
                            break
            
            except Exception as e:
                continue
        
        # Clasificar impacto
        df_noticias['impacto_absoluto'] = df_noticias['sp500_return_next_day'].abs()
        df_noticias['impacto_clasificado'] = pd.cut(
            df_noticias['impacto_absoluto'],
            bins=[0, 0.005, 0.015, 1.0],
            labels=['BAJO', 'MEDIO', 'ALTO']
        )
        
        logger.info(f"\n✓ Correlación completada")
        logger.info(f"  Noticias correlacionadas: {correlacionadas}/{len(df_noticias)}")
        
        return df_noticias


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("SISTEMA DE NOTICIAS - GDELT PROJECT")
    logger.info("="*70)
    logger.info("GDELT = Base de datos global de eventos y noticias")
    logger.info("100% GRATIS, sin API key necesaria")
    logger.info("")
    
    # Crear recolector
    collector = GDELTNewsCollector()
    
    # Obtener noticias
    logger.info("\n1. Obteniendo noticias económicas globales...")
    df_noticias = collector.obtener_noticias_economicas_globales(dias_atras=90)
    
    if df_noticias is not None and not df_noticias.empty:
        # Buscar archivo del S&P 500
        logger.info("\n2. Buscando datos del S&P 500...")
        spy_files = list(RAW_DATA_DIR.glob("SPY_*.csv"))
        
        if spy_files:
            spy_file = max(spy_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"  ✓ Archivo encontrado: {spy_file.name}")
            
            # Correlacionar
            logger.info("\n3. Correlacionando noticias con S&P 500...")
            df_correlacionado = collector.correlacionar_con_sp500(df_noticias, spy_file)
            
            # Guardar
            logger.info("\n4. Guardando datos...")
            news_dir = RAW_DATA_DIR.parent / "processed" / "news"
            news_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d')
            filepath = news_dir / f"noticias_gdelt_correlacionadas_{timestamp}.csv"
            df_correlacionado.to_csv(filepath, index=False)
            logger.info(f"  ✓ Datos guardados: {filepath}")
            
            # Generar estadísticas
            logger.info("\n5. Generando reporte...")
            logger.info("="*70)
            logger.info("REPORTE DE NOTICIAS Y SU IMPACTO")
            logger.info("="*70)
            
            logger.info(f"\nTotal de noticias: {len(df_correlacionado)}")
            logger.info(f"Período: {df_correlacionado['fecha'].min()} a {df_correlacionado['fecha'].max()}")
            
            # Por región
            logger.info("\nDistribución por región:")
            for region in df_correlacionado['region'].value_counts().head(10).items():
                logger.info(f"  {region[0]}: {region[1]} noticias")
            
            # Por impacto
            if 'impacto_clasificado' in df_correlacionado.columns:
                logger.info("\nDistribución por impacto en S&P 500:")
                for imp in ['ALTO', 'MEDIO', 'BAJO']:
                    count = len(df_correlacionado[df_correlacionado['impacto_clasificado'] == imp])
                    if count > 0:
                        logger.info(f"  {imp}: {count} noticias")
            
            # Top impactos
            logger.info("\nTop 10 noticias con MAYOR impacto (↑):")
            top_up = df_correlacionado.nlargest(10, 'sp500_return_next_day')
            for idx, row in top_up.iterrows():
                if pd.notna(row['title']) and pd.notna(row['sp500_return_next_day']):
                    logger.info(f"  +{row['sp500_return_next_day']*100:.2f}% | {row['title'][:70]}")
            
            logger.info("\nTop 10 noticias con MAYOR caída (↓):")
            top_down = df_correlacionado.nsmallest(10, 'sp500_return_next_day')
            for idx, row in top_down.iterrows():
                if pd.notna(row['title']) and pd.notna(row['sp500_return_next_day']):
                    logger.info(f"  {row['sp500_return_next_day']*100:.2f}% | {row['title'][:70]}")
            
            logger.info("\n" + "="*70)
            logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
            logger.info("="*70)
            logger.info(f"\nArchivo guardado: {filepath}")
            logger.info("\nEstos datos ya están listos para:")
            logger.info("  1. Análisis de sentimiento (BERT)")
            logger.info("  2. Entrenamiento de modelo predictivo")
            logger.info("  3. Identificación de patrones de impacto")
            
        else:
            logger.error("No se encontraron datos del S&P 500")
            logger.info("Ejecuta primero: py src/data_collection/market_collector.py")
    
    else:
        logger.error("No se obtuvieron noticias")


if __name__ == "__main__":
    main()

