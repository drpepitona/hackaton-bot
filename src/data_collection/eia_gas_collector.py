"""
Recolector de datos de Gas Natural - EIA
U.S. Energy Information Administration
"""
import requests
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, EIA_API_KEY
from src.utils.logger import logger


# API de EIA - Gas Natural
EIA_GAS_API_URL = "https://api.eia.gov/v2/natural-gas/sum/lsum/data/"


class EIAGasCollector:
    """
    Recolector de datos de gas natural de EIA
    """
    
    def __init__(self, api_key=None):
        """
        Inicializa el recolector
        
        Args:
            api_key: API key de EIA (opcional)
        """
        self.api_key = api_key or EIA_API_KEY
        self.base_url = EIA_GAS_API_URL
        logger.info("✓ EIAGasCollector inicializado")
        if self.api_key:
            logger.info(f"  API Key configurada: {self.api_key[:10]}...")
    
    def obtener_datos_gas_natural(self):
        """
        Obtiene datos de gas natural de EIA
        
        Returns:
            DataFrame con los datos
        """
        logger.info("Obteniendo datos de gas natural de EIA...")
        
        try:
            # Parámetros de la API
            params = {
                'frequency': 'monthly',
                'data[0]': 'value',
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'offset': 0,
                'length': 5000
            }
            
            # Agregar API key si está disponible
            if self.api_key:
                params['api_key'] = self.api_key
            
            logger.info(f"  Realizando petición a EIA API...")
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and 'data' in data['response']:
                    records = data['response']['data']
                    df = pd.DataFrame(records)
                    
                    logger.info(f"  ✓ Datos obtenidos: {len(df)} registros")
                    logger.info(f"  ✓ Columnas: {list(df.columns)}")
                    
                    # Procesar datos
                    df = self._procesar_datos(df)
                    
                    return df
                else:
                    logger.warning("No se encontraron datos en la respuesta")
                    logger.info(f"Estructura de respuesta: {data.keys()}")
                    return None
            else:
                logger.error(f"Error en API: {response.status_code}")
                logger.error(f"Respuesta: {response.text[:500]}")
                return None
                
        except Exception as e:
            logger.error(f"Error al obtener datos de gas natural: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _procesar_datos(self, df):
        """
        Procesa y limpia los datos
        """
        try:
            # Convertir period a datetime
            if 'period' in df.columns:
                df['date'] = pd.to_datetime(df['period'])
                df = df.sort_values('date')
            
            # Convertir value a numérico
            if 'value' in df.columns:
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            logger.info(f"  ✓ Datos procesados: {df.shape}")
            
            # Mostrar información de las series disponibles
            if 'seriesDescription' in df.columns:
                series_unicas = df['seriesDescription'].unique()
                logger.info(f"\n  Series disponibles ({len(series_unicas)}):")
                for i, serie in enumerate(series_unicas[:10], 1):  # Mostrar primeras 10
                    logger.info(f"    {i}. {serie}")
                if len(series_unicas) > 10:
                    logger.info(f"    ... y {len(series_unicas) - 10} más")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al procesar datos: {e}")
            return df
    
    def crear_dataset_pivotado(self, df):
        """
        Crea un dataset con series como columnas
        """
        if df is None or df.empty:
            return None
        
        try:
            # Determinar qué columna usar para pivotar
            pivot_col = None
            if 'seriesDescription' in df.columns:
                pivot_col = 'seriesDescription'
            elif 'series-description' in df.columns:
                pivot_col = 'series-description'
            elif 'process' in df.columns:
                pivot_col = 'process'
            
            if pivot_col:
                # Pivotar
                df_pivot = df.pivot_table(
                    index='date',
                    columns=pivot_col,
                    values='value',
                    aggfunc='first'
                )
                
                logger.info(f"  ✓ Dataset pivotado: {df_pivot.shape}")
                
                return df_pivot
            else:
                logger.warning("No se encontró columna para pivotar")
                logger.info(f"Columnas disponibles: {list(df.columns)}")
                return df
                
        except Exception as e:
            logger.error(f"Error al pivotar datos: {e}")
            return df
    
    def guardar_datos(self, df, df_pivot=None):
        """
        Guarda los datos en archivos CSV
        """
        if df is None or df.empty:
            logger.warning("No hay datos para guardar")
            return
        
        try:
            # Crear directorios
            raw_dir = RAW_DATA_DIR / "eia_gas"
            processed_dir = RAW_DATA_DIR.parent / "processed" / "eia_gas"
            raw_dir.mkdir(parents=True, exist_ok=True)
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d')
            
            # Guardar datos raw
            filepath_raw = raw_dir / f"eia_gas_raw_{timestamp}.csv"
            df.to_csv(filepath_raw, index=False)
            logger.info(f"  ✓ Datos raw guardados: {filepath_raw}")
            
            # Guardar datos pivotados si existen
            if df_pivot is not None and not df_pivot.empty:
                filepath_pivot = processed_dir / f"eia_gas_natural_{timestamp}.csv"
                df_pivot.to_csv(filepath_pivot)
                logger.info(f"  ✓ Datos procesados guardados: {filepath_pivot}")
                
                return filepath_pivot
            
            return filepath_raw
            
        except Exception as e:
            logger.error(f"Error al guardar datos: {e}")
            return None
    
    def generar_reporte(self, df):
        """
        Genera reporte de los datos obtenidos
        """
        if df is None or df.empty:
            logger.warning("No hay datos para generar reporte")
            return
        
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE DATOS DE GAS NATURAL")
        logger.info("="*70)
        
        logger.info(f"\nRegistros totales: {len(df)}")
        
        if 'date' in df.columns:
            logger.info(f"Período: {df['date'].min()} a {df['date'].max()}")
        
        if 'value' in df.columns:
            logger.info(f"\nEstadísticas de valores:")
            logger.info(f"  Mínimo: {df['value'].min():.2f}")
            logger.info(f"  Máximo: {df['value'].max():.2f}")
            logger.info(f"  Promedio: {df['value'].mean():.2f}")
            logger.info(f"  Último valor: {df['value'].iloc[-1]:.2f}")
        
        # Información adicional
        logger.info(f"\nColumnas disponibles:")
        for col in df.columns:
            non_null = df[col].count()
            logger.info(f"  - {col}: {non_null} valores no nulos")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE DATOS DE GAS NATURAL - EIA")
    logger.info("="*70)
    
    # Crear recolector
    collector = EIAGasCollector()
    
    # Obtener datos
    logger.info("\n1. Obteniendo datos de gas natural...")
    df = collector.obtener_datos_gas_natural()
    
    if df is not None:
        # Crear dataset pivotado
        logger.info("\n2. Creando dataset estructurado...")
        df_pivot = collector.crear_dataset_pivotado(df)
        
        # Guardar datos
        logger.info("\n3. Guardando datos...")
        collector.guardar_datos(df, df_pivot)
        
        # Generar reporte
        logger.info("\n4. Generando reporte...")
        collector.generar_reporte(df)
        
        logger.info("\n" + "="*70)
        logger.info("✓ RECOLECCIÓN COMPLETADA EXITOSAMENTE")
        logger.info("="*70)
    else:
        logger.error("No se pudieron obtener datos de gas natural")


if __name__ == "__main__":
    main()


U.S. Energy Information Administration
"""
import requests
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, EIA_API_KEY
from src.utils.logger import logger


# API de EIA - Gas Natural
EIA_GAS_API_URL = "https://api.eia.gov/v2/natural-gas/sum/lsum/data/"


class EIAGasCollector:
    """
    Recolector de datos de gas natural de EIA
    """
    
    def __init__(self, api_key=None):
        """
        Inicializa el recolector
        
        Args:
            api_key: API key de EIA (opcional)
        """
        self.api_key = api_key or EIA_API_KEY
        self.base_url = EIA_GAS_API_URL
        logger.info("✓ EIAGasCollector inicializado")
        if self.api_key:
            logger.info(f"  API Key configurada: {self.api_key[:10]}...")
    
    def obtener_datos_gas_natural(self):
        """
        Obtiene datos de gas natural de EIA
        
        Returns:
            DataFrame con los datos
        """
        logger.info("Obteniendo datos de gas natural de EIA...")
        
        try:
            # Parámetros de la API
            params = {
                'frequency': 'monthly',
                'data[0]': 'value',
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'offset': 0,
                'length': 5000
            }
            
            # Agregar API key si está disponible
            if self.api_key:
                params['api_key'] = self.api_key
            
            logger.info(f"  Realizando petición a EIA API...")
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and 'data' in data['response']:
                    records = data['response']['data']
                    df = pd.DataFrame(records)
                    
                    logger.info(f"  ✓ Datos obtenidos: {len(df)} registros")
                    logger.info(f"  ✓ Columnas: {list(df.columns)}")
                    
                    # Procesar datos
                    df = self._procesar_datos(df)
                    
                    return df
                else:
                    logger.warning("No se encontraron datos en la respuesta")
                    logger.info(f"Estructura de respuesta: {data.keys()}")
                    return None
            else:
                logger.error(f"Error en API: {response.status_code}")
                logger.error(f"Respuesta: {response.text[:500]}")
                return None
                
        except Exception as e:
            logger.error(f"Error al obtener datos de gas natural: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _procesar_datos(self, df):
        """
        Procesa y limpia los datos
        """
        try:
            # Convertir period a datetime
            if 'period' in df.columns:
                df['date'] = pd.to_datetime(df['period'])
                df = df.sort_values('date')
            
            # Convertir value a numérico
            if 'value' in df.columns:
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            logger.info(f"  ✓ Datos procesados: {df.shape}")
            
            # Mostrar información de las series disponibles
            if 'seriesDescription' in df.columns:
                series_unicas = df['seriesDescription'].unique()
                logger.info(f"\n  Series disponibles ({len(series_unicas)}):")
                for i, serie in enumerate(series_unicas[:10], 1):  # Mostrar primeras 10
                    logger.info(f"    {i}. {serie}")
                if len(series_unicas) > 10:
                    logger.info(f"    ... y {len(series_unicas) - 10} más")
            
            return df
            
        except Exception as e:
            logger.error(f"Error al procesar datos: {e}")
            return df
    
    def crear_dataset_pivotado(self, df):
        """
        Crea un dataset con series como columnas
        """
        if df is None or df.empty:
            return None
        
        try:
            # Determinar qué columna usar para pivotar
            pivot_col = None
            if 'seriesDescription' in df.columns:
                pivot_col = 'seriesDescription'
            elif 'series-description' in df.columns:
                pivot_col = 'series-description'
            elif 'process' in df.columns:
                pivot_col = 'process'
            
            if pivot_col:
                # Pivotar
                df_pivot = df.pivot_table(
                    index='date',
                    columns=pivot_col,
                    values='value',
                    aggfunc='first'
                )
                
                logger.info(f"  ✓ Dataset pivotado: {df_pivot.shape}")
                
                return df_pivot
            else:
                logger.warning("No se encontró columna para pivotar")
                logger.info(f"Columnas disponibles: {list(df.columns)}")
                return df
                
        except Exception as e:
            logger.error(f"Error al pivotar datos: {e}")
            return df
    
    def guardar_datos(self, df, df_pivot=None):
        """
        Guarda los datos en archivos CSV
        """
        if df is None or df.empty:
            logger.warning("No hay datos para guardar")
            return
        
        try:
            # Crear directorios
            raw_dir = RAW_DATA_DIR / "eia_gas"
            processed_dir = RAW_DATA_DIR.parent / "processed" / "eia_gas"
            raw_dir.mkdir(parents=True, exist_ok=True)
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d')
            
            # Guardar datos raw
            filepath_raw = raw_dir / f"eia_gas_raw_{timestamp}.csv"
            df.to_csv(filepath_raw, index=False)
            logger.info(f"  ✓ Datos raw guardados: {filepath_raw}")
            
            # Guardar datos pivotados si existen
            if df_pivot is not None and not df_pivot.empty:
                filepath_pivot = processed_dir / f"eia_gas_natural_{timestamp}.csv"
                df_pivot.to_csv(filepath_pivot)
                logger.info(f"  ✓ Datos procesados guardados: {filepath_pivot}")
                
                return filepath_pivot
            
            return filepath_raw
            
        except Exception as e:
            logger.error(f"Error al guardar datos: {e}")
            return None
    
    def generar_reporte(self, df):
        """
        Genera reporte de los datos obtenidos
        """
        if df is None or df.empty:
            logger.warning("No hay datos para generar reporte")
            return
        
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE DATOS DE GAS NATURAL")
        logger.info("="*70)
        
        logger.info(f"\nRegistros totales: {len(df)}")
        
        if 'date' in df.columns:
            logger.info(f"Período: {df['date'].min()} a {df['date'].max()}")
        
        if 'value' in df.columns:
            logger.info(f"\nEstadísticas de valores:")
            logger.info(f"  Mínimo: {df['value'].min():.2f}")
            logger.info(f"  Máximo: {df['value'].max():.2f}")
            logger.info(f"  Promedio: {df['value'].mean():.2f}")
            logger.info(f"  Último valor: {df['value'].iloc[-1]:.2f}")
        
        # Información adicional
        logger.info(f"\nColumnas disponibles:")
        for col in df.columns:
            non_null = df[col].count()
            logger.info(f"  - {col}: {non_null} valores no nulos")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE DATOS DE GAS NATURAL - EIA")
    logger.info("="*70)
    
    # Crear recolector
    collector = EIAGasCollector()
    
    # Obtener datos
    logger.info("\n1. Obteniendo datos de gas natural...")
    df = collector.obtener_datos_gas_natural()
    
    if df is not None:
        # Crear dataset pivotado
        logger.info("\n2. Creando dataset estructurado...")
        df_pivot = collector.crear_dataset_pivotado(df)
        
        # Guardar datos
        logger.info("\n3. Guardando datos...")
        collector.guardar_datos(df, df_pivot)
        
        # Generar reporte
        logger.info("\n4. Generando reporte...")
        collector.generar_reporte(df)
        
        logger.info("\n" + "="*70)
        logger.info("✓ RECOLECCIÓN COMPLETADA EXITOSAMENTE")
        logger.info("="*70)
    else:
        logger.error("No se pudieron obtener datos de gas natural")


if __name__ == "__main__":
    main()

