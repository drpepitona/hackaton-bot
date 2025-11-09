"""
Recolector de datos de FRED (Federal Reserve Economic Data)
"""
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import FRED_API_KEY, RAW_DATA_DIR, FRED_INDICATORS
from src.utils.logger import logger


class FREDCollector:
    """Recolecta datos económicos de FRED"""
    
    def __init__(self, api_key=None):
        """
        Inicializa el recolector de FRED
        
        Args:
            api_key: API key de FRED (opcional, usa variable de entorno por defecto)
        """
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED API key no encontrada. Configura FRED_API_KEY en .env")
        
        self.fred = Fred(api_key=self.api_key)
        logger.info("FREDCollector inicializado correctamente")
    
    def get_series(self, series_id, start_date=None, end_date=None):
        """
        Obtiene una serie temporal de FRED
        
        Args:
            series_id: ID de la serie (ej: 'UNRATE' para tasa de desempleo)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            pandas.Series con los datos
        """
        try:
            logger.info(f"Obteniendo serie {series_id} de FRED...")
            data = self.fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date
            )
            logger.info(f"✓ Serie {series_id} obtenida: {len(data)} observaciones")
            return data
        except Exception as e:
            logger.error(f"Error al obtener serie {series_id}: {e}")
            return None
    
    def get_multiple_series(self, series_ids, start_date=None, end_date=None):
        """
        Obtiene múltiples series y las combina en un DataFrame
        
        Args:
            series_ids: Lista de IDs de series
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            pandas.DataFrame con todas las series
        """
        data = {}
        for series_id in series_ids:
            series = self.get_series(series_id, start_date, end_date)
            if series is not None:
                data[series_id] = series
        
        df = pd.DataFrame(data)
        logger.info(f"DataFrame creado con {len(df.columns)} series y {len(df)} observaciones")
        return df
    
    def save_data(self, df, filename):
        """
        Guarda los datos en un archivo CSV
        
        Args:
            df: DataFrame a guardar
            filename: Nombre del archivo
        """
        filepath = RAW_DATA_DIR / filename
        df.to_csv(filepath)
        logger.info(f"✓ Datos guardados en {filepath}")
    
    def collect_default_indicators(self, start_date=None):
        """
        Recolecta los indicadores económicos por defecto
        
        Args:
            start_date: Fecha de inicio (por defecto últimos 10 años)
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365*10)
        
        logger.info(f"Recolectando {len(FRED_INDICATORS)} indicadores desde {start_date}")
        df = self.get_multiple_series(FRED_INDICATORS, start_date=start_date)
        
        filename = f"fred_indicators_{datetime.now().strftime('%Y%m%d')}.csv"
        self.save_data(df, filename)
        
        return df


def main():
    """Función principal para ejecutar el recolector"""
    try:
        collector = FREDCollector()
        df = collector.collect_default_indicators()
        
        logger.info("\n" + "="*50)
        logger.info("RESUMEN DE DATOS RECOLECTADOS")
        logger.info("="*50)
        logger.info(f"\nColumnas: {list(df.columns)}")
        logger.info(f"Período: {df.index.min()} a {df.index.max()}")
        logger.info(f"Total de observaciones: {len(df)}")
        logger.info("\nPrimeras filas:")
        print(df.head())
        logger.info("\nÚltimas filas:")
        print(df.tail())
        logger.info("\n✓ Recolección completada exitosamente!")
        
    except Exception as e:
        logger.error(f"Error en la recolección: {e}")
        raise


if __name__ == "__main__":
    main()


