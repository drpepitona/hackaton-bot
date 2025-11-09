"""
Recolector de datos de energía - EIA (U.S. Energy Information Administration)
Datos de petróleo y productos derivados
"""
import requests
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


# API de EIA - Petróleo
EIA_API_BASE = "https://api.eia.gov/v2"

# Productos de petróleo más importantes
PRODUCTOS_PETROLEO = {
    'EPOO': 'Crude Oil Total',
    'EPD0': 'Distillate Fuel Oil',
    'EPM0F': 'Motor Gasoline Finished',
    'EPJK': 'Jet Fuel Kerosene Type',
    'EPPR': 'Propane',
    'EPPV': 'Petroleum Products',
    'EPL0': 'Lubricants',
    'EPOBG': 'Biofuels Total',
    'EPOORO': 'Crude Oil OPEC',
    'EPOORXFE': 'Crude Oil Rest of World',
}


class EIACollector:
    """
    Recolector de datos de la API de EIA
    Enfocado en datos de petróleo que impactan mercados
    """
    
    def __init__(self, api_key=None):
        """
        Inicializa el recolector de EIA
        
        Args:
            api_key: API key de EIA (opcional)
        """
        self.api_key = api_key
        self.base_url = EIA_API_BASE
        logger.info("✓ EIACollector inicializado")
    
    def obtener_datos_petroleo(self, productos=None, start_date="2000-01", end_date="2025-08"):
        """
        Obtiene datos de suministro y demanda de petróleo
        
        Args:
            productos: Lista de códigos de productos (None = usar por defecto)
            start_date: Fecha inicio (formato: YYYY-MM)
            end_date: Fecha fin (formato: YYYY-MM)
            
        Returns:
            DataFrame con los datos
        """
        if productos is None:
            productos = list(PRODUCTOS_PETROLEO.keys())
        
        logger.info(f"Obteniendo datos de EIA...")
        logger.info(f"  Productos: {len(productos)}")
        logger.info(f"  Período: {start_date} a {end_date}")
        
        try:
            # Construir la URL de la API
            url = f"{self.base_url}/petroleum/sum/snd/data/"
            
            params = {
                'frequency': 'monthly',
                'data[0]': 'value',
                'start': start_date,
                'end': end_date,
                'offset': 0,
                'length': 5000
            }
            
            # Agregar productos
            for i, producto in enumerate(productos):
                params[f'facets[product][{i}]'] = producto
            
            # Agregar API key si está disponible
            if self.api_key:
                params['api_key'] = self.api_key
            
            logger.info(f"  Realizando petición a EIA API...")
            response = requests.get(url, params=params, timeout=30)
            
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
                    return None
            else:
                logger.error(f"Error en API: {response.status_code}")
                logger.error(f"Respuesta: {response.text[:500]}")
                return None
                
        except Exception as e:
            logger.error(f"Error al obtener datos de EIA: {e}")
            return None
    
    def _procesar_datos(self, df):
        """
        Procesa y limpia los datos de EIA
        """
        # Convertir period a datetime
        if 'period' in df.columns:
            df['date'] = pd.to_datetime(df['period'])
            df = df.sort_values('date')
        
        # Convertir value a numérico
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Crear columnas descriptivas
        if 'product' in df.columns:
            df['product_name'] = df['product'].map(PRODUCTOS_PETROLEO)
        
        logger.info(f"  ✓ Datos procesados")
        
        return df
    
    def crear_dataset_pivotado(self, df):
        """
        Crea un dataset con productos como columnas
        """
        if df is None or df.empty:
            return None
        
        # Pivotar para tener productos como columnas
        df_pivot = df.pivot_table(
            index='date',
            columns='product',
            values='value',
            aggfunc='first'
        )
        
        # Renombrar columnas con nombres descriptivos
        df_pivot.columns = [PRODUCTOS_PETROLEO.get(col, col) for col in df_pivot.columns]
        
        logger.info(f"  ✓ Dataset pivotado: {df_pivot.shape}")
        
        return df_pivot
    
    def guardar_datos(self, df, filename):
        """
        Guarda los datos en CSV
        """
        if df is None or df.empty:
            logger.warning("No hay datos para guardar")
            return
        
        # Crear directorio
        eia_dir = RAW_DATA_DIR / "eia"
        eia_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = eia_dir / filename
        df.to_csv(filepath)
        
        logger.info(f"  ✓ Datos guardados: {filepath}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE DATOS DE PETRÓLEO - EIA")
    logger.info("="*70)
    
    # Crear recolector
    collector = EIACollector()
    
    # Obtener datos de productos principales
    logger.info("\n1. Obteniendo datos de productos principales...")
    df = collector.obtener_datos_petroleo()
    
    if df is not None:
        # Guardar datos raw
        timestamp = datetime.now().strftime('%Y%m%d')
        collector.guardar_datos(df, f"eia_petroleum_raw_{timestamp}.csv")
        
        # Crear dataset pivotado
        logger.info("\n2. Creando dataset estructurado...")
        df_pivot = collector.crear_dataset_pivotado(df)
        
        if df_pivot is not None:
            # Guardar en processed
            processed_dir = RAW_DATA_DIR.parent / "processed" / "eia"
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = processed_dir / f"eia_petroleum_{timestamp}.csv"
            df_pivot.to_csv(filepath)
            logger.info(f"  ✓ Dataset procesado guardado: {filepath}")
            
            # Mostrar resumen
            logger.info("\n" + "="*70)
            logger.info("RESUMEN DE DATOS")
            logger.info("="*70)
            logger.info(f"\nProductos: {len(df_pivot.columns)}")
            logger.info(f"Período: {df_pivot.index.min()} a {df_pivot.index.max()}")
            logger.info(f"Observaciones: {len(df_pivot)}")
            logger.info(f"\nProductos incluidos:")
            for col in df_pivot.columns:
                logger.info(f"  - {col}")
        
        logger.info("\n✓ Recolección completada exitosamente")
    else:
        logger.error("No se pudieron obtener datos de EIA")


if __name__ == "__main__":
    main()


