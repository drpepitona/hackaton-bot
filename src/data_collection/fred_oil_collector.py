"""
Recolector específico de datos de petróleo de FRED
Complementa el recolector principal de FRED
"""
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import FRED_API_KEY, RAW_DATA_DIR
from src.utils.logger import logger


# Series de petróleo en FRED
FRED_OIL_SERIES = {
    # Precios de petróleo crudo
    'DCOILWTICO': {
        'nombre': 'Crude Oil WTI (West Texas Intermediate)',
        'unidad': 'Dólares por barril',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Precio de referencia USA'
    },
    'DCOILBRENTEU': {
        'nombre': 'Crude Oil Brent - Europe',
        'unidad': 'Dólares por barril',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Precio de referencia global'
    },
    
    # Producción
    'MCOILWTICO': {
        'nombre': 'Crude Oil WTI (Monthly Average)',
        'unidad': 'Dólares por barril',
        'frecuencia': 'Mensual',
        'impacto': 'ALTO'
    },
    
    # Precios de gasolina
    'GASREGW': {
        'nombre': 'US Regular Gas Price',
        'unidad': 'Dólares por galón',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO - Afecta inflación'
    },
    'GASDESW': {
        'nombre': 'US Diesel Gas Price',
        'unidad': 'Dólares por galón',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO'
    },
    
    # Inventarios
    'WCRSTUS1': {
        'nombre': 'Crude Oil Stocks - US',
        'unidad': 'Miles de barriles',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO - Indicador de oferta/demanda'
    },
    'WGTSTUS1': {
        'nombre': 'Total Gasoline Stocks - US',
        'unidad': 'Miles de barriles',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO'
    },
    
    # Producción USA
    'WCRFPUS2': {
        'nombre': 'US Field Production of Crude Oil',
        'unidad': 'Miles de barriles por día',
        'frecuencia': 'Mensual',
        'impacto': 'ALTO - Producción doméstica'
    },
    
    # Importaciones
    'WTTIMUS2': {
        'nombre': 'US Crude Oil Imports',
        'unidad': 'Miles de barriles por día',
        'frecuencia': 'Mensual',
        'impacto': 'MEDIO'
    },
}


class FREDOilCollector:
    """
    Recolector especializado en datos de petróleo de FRED
    """
    
    def __init__(self, api_key=None):
        """Inicializa el recolector"""
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED API key no encontrada")
        
        self.fred = Fred(api_key=self.api_key)
        self.datos = {}
        self.metadata = {}
        
        logger.info("✓ FREDOilCollector inicializado")
    
    def obtener_serie(self, series_id, info, start_date=None):
        """
        Obtiene una serie individual
        """
        try:
            logger.info(f"  Obteniendo {info['nombre']} ({series_id})...")
            
            if start_date is None:
                start_date = datetime(2000, 1, 1)
            
            data = self.fred.get_series(series_id, observation_start=start_date)
            
            if data is not None and len(data) > 0:
                logger.info(f"    ✓ {len(data)} observaciones")
                logger.info(f"    ✓ Período: {data.index.min()} a {data.index.max()}")
                logger.info(f"    ✓ Último valor: {data.iloc[-1]:.2f}")
                
                # Guardar metadata
                self.metadata[series_id] = {
                    'nombre': info['nombre'],
                    'unidad': info['unidad'],
                    'frecuencia': info['frecuencia'],
                    'impacto': info['impacto'],
                    'observaciones': len(data),
                    'fecha_inicio': str(data.index.min()),
                    'fecha_fin': str(data.index.max()),
                    'ultimo_valor': float(data.iloc[-1])
                }
                
                return data
            else:
                logger.warning(f"    ✗ No se obtuvieron datos")
                return None
                
        except Exception as e:
            logger.error(f"    ✗ Error: {e}")
            return None
    
    def obtener_todas_series(self):
        """
        Obtiene todas las series de petróleo
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO DATOS DE PETRÓLEO - FRED")
        logger.info("="*70)
        logger.info(f"Total de series: {len(FRED_OIL_SERIES)}")
        logger.info("")
        
        exitosas = 0
        
        for series_id, info in FRED_OIL_SERIES.items():
            data = self.obtener_serie(series_id, info)
            if data is not None:
                self.datos[series_id] = data
                exitosas += 1
        
        logger.info(f"\n✓ Series obtenidas: {exitosas}/{len(FRED_OIL_SERIES)}")
        
        return self.datos
    
    def crear_datasets(self):
        """
        Crea datasets organizados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASETS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "fred_oil"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset completo
        df_completo = pd.DataFrame(self.datos)
        filepath = processed_dir / f"fred_oil_completo_{timestamp}.csv"
        df_completo.to_csv(filepath)
        logger.info(f"  ✓ Dataset completo: {filepath.name}")
        logger.info(f"    - Columnas: {len(df_completo.columns)}")
        logger.info(f"    - Filas: {len(df_completo)}")
        
        # 2. Solo precios (diarios)
        series_precios = {}
        for sid, data in self.datos.items():
            if 'DCOIL' in sid:  # Series diarias de precios
                series_precios[sid] = data
        
        if series_precios:
            df_precios = pd.DataFrame(series_precios)
            filepath = processed_dir / f"fred_oil_precios_{timestamp}.csv"
            df_precios.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset precios: {filepath.name}")
            logger.info(f"    - Series: {len(df_precios.columns)}")
        
        # 3. Datos de alto impacto
        series_alto = {}
        for sid, data in self.datos.items():
            if 'ALTO' in self.metadata[sid]['impacto']:
                series_alto[sid] = data
        
        if series_alto:
            df_alto = pd.DataFrame(series_alto)
            filepath = processed_dir / f"fred_oil_alto_impacto_{timestamp}.csv"
            df_alto.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset alto impacto: {filepath.name}")
            logger.info(f"    - Series: {len(df_alto.columns)}")
        
        # 4. Guardar metadata
        import json
        metadata_file = processed_dir / f"fred_oil_metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"\n  ✓ Metadata guardada: {metadata_file.name}")
    
    def generar_reporte(self):
        """
        Genera reporte de datos obtenidos
        """
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE DATOS DE PETRÓLEO")
        logger.info("="*70)
        
        for series_id, data in self.datos.items():
            info = self.metadata[series_id]
            logger.info(f"\n  {info['nombre']} ({series_id})")
            logger.info(f"    Impacto: {info['impacto']}")
            logger.info(f"    Frecuencia: {info['frecuencia']}")
            logger.info(f"    Observaciones: {info['observaciones']}")
            logger.info(f"    Último valor: {info['ultimo_valor']:.2f} {info['unidad']}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("BOT PREDICTIVO - DATOS DE PETRÓLEO")
    logger.info("="*70)
    
    # Crear recolector
    collector = FREDOilCollector()
    
    # Obtener datos
    datos = collector.obtener_todas_series()
    
    # Crear datasets
    collector.crear_datasets()
    
    # Generar reporte
    collector.generar_reporte()
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ PROCESO COMPLETADO ✓✓✓")
    logger.info("="*70)
    logger.info("\nArchivos generados en: data/processed/fred_oil/")


if __name__ == "__main__":
    main()

Recolector específico de datos de petróleo de FRED
Complementa el recolector principal de FRED
"""
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import FRED_API_KEY, RAW_DATA_DIR
from src.utils.logger import logger


# Series de petróleo en FRED
FRED_OIL_SERIES = {
    # Precios de petróleo crudo
    'DCOILWTICO': {
        'nombre': 'Crude Oil WTI (West Texas Intermediate)',
        'unidad': 'Dólares por barril',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Precio de referencia USA'
    },
    'DCOILBRENTEU': {
        'nombre': 'Crude Oil Brent - Europe',
        'unidad': 'Dólares por barril',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Precio de referencia global'
    },
    
    # Producción
    'MCOILWTICO': {
        'nombre': 'Crude Oil WTI (Monthly Average)',
        'unidad': 'Dólares por barril',
        'frecuencia': 'Mensual',
        'impacto': 'ALTO'
    },
    
    # Precios de gasolina
    'GASREGW': {
        'nombre': 'US Regular Gas Price',
        'unidad': 'Dólares por galón',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO - Afecta inflación'
    },
    'GASDESW': {
        'nombre': 'US Diesel Gas Price',
        'unidad': 'Dólares por galón',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO'
    },
    
    # Inventarios
    'WCRSTUS1': {
        'nombre': 'Crude Oil Stocks - US',
        'unidad': 'Miles de barriles',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO - Indicador de oferta/demanda'
    },
    'WGTSTUS1': {
        'nombre': 'Total Gasoline Stocks - US',
        'unidad': 'Miles de barriles',
        'frecuencia': 'Semanal',
        'impacto': 'MEDIO'
    },
    
    # Producción USA
    'WCRFPUS2': {
        'nombre': 'US Field Production of Crude Oil',
        'unidad': 'Miles de barriles por día',
        'frecuencia': 'Mensual',
        'impacto': 'ALTO - Producción doméstica'
    },
    
    # Importaciones
    'WTTIMUS2': {
        'nombre': 'US Crude Oil Imports',
        'unidad': 'Miles de barriles por día',
        'frecuencia': 'Mensual',
        'impacto': 'MEDIO'
    },
}


class FREDOilCollector:
    """
    Recolector especializado en datos de petróleo de FRED
    """
    
    def __init__(self, api_key=None):
        """Inicializa el recolector"""
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED API key no encontrada")
        
        self.fred = Fred(api_key=self.api_key)
        self.datos = {}
        self.metadata = {}
        
        logger.info("✓ FREDOilCollector inicializado")
    
    def obtener_serie(self, series_id, info, start_date=None):
        """
        Obtiene una serie individual
        """
        try:
            logger.info(f"  Obteniendo {info['nombre']} ({series_id})...")
            
            if start_date is None:
                start_date = datetime(2000, 1, 1)
            
            data = self.fred.get_series(series_id, observation_start=start_date)
            
            if data is not None and len(data) > 0:
                logger.info(f"    ✓ {len(data)} observaciones")
                logger.info(f"    ✓ Período: {data.index.min()} a {data.index.max()}")
                logger.info(f"    ✓ Último valor: {data.iloc[-1]:.2f}")
                
                # Guardar metadata
                self.metadata[series_id] = {
                    'nombre': info['nombre'],
                    'unidad': info['unidad'],
                    'frecuencia': info['frecuencia'],
                    'impacto': info['impacto'],
                    'observaciones': len(data),
                    'fecha_inicio': str(data.index.min()),
                    'fecha_fin': str(data.index.max()),
                    'ultimo_valor': float(data.iloc[-1])
                }
                
                return data
            else:
                logger.warning(f"    ✗ No se obtuvieron datos")
                return None
                
        except Exception as e:
            logger.error(f"    ✗ Error: {e}")
            return None
    
    def obtener_todas_series(self):
        """
        Obtiene todas las series de petróleo
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO DATOS DE PETRÓLEO - FRED")
        logger.info("="*70)
        logger.info(f"Total de series: {len(FRED_OIL_SERIES)}")
        logger.info("")
        
        exitosas = 0
        
        for series_id, info in FRED_OIL_SERIES.items():
            data = self.obtener_serie(series_id, info)
            if data is not None:
                self.datos[series_id] = data
                exitosas += 1
        
        logger.info(f"\n✓ Series obtenidas: {exitosas}/{len(FRED_OIL_SERIES)}")
        
        return self.datos
    
    def crear_datasets(self):
        """
        Crea datasets organizados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASETS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "fred_oil"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset completo
        df_completo = pd.DataFrame(self.datos)
        filepath = processed_dir / f"fred_oil_completo_{timestamp}.csv"
        df_completo.to_csv(filepath)
        logger.info(f"  ✓ Dataset completo: {filepath.name}")
        logger.info(f"    - Columnas: {len(df_completo.columns)}")
        logger.info(f"    - Filas: {len(df_completo)}")
        
        # 2. Solo precios (diarios)
        series_precios = {}
        for sid, data in self.datos.items():
            if 'DCOIL' in sid:  # Series diarias de precios
                series_precios[sid] = data
        
        if series_precios:
            df_precios = pd.DataFrame(series_precios)
            filepath = processed_dir / f"fred_oil_precios_{timestamp}.csv"
            df_precios.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset precios: {filepath.name}")
            logger.info(f"    - Series: {len(df_precios.columns)}")
        
        # 3. Datos de alto impacto
        series_alto = {}
        for sid, data in self.datos.items():
            if 'ALTO' in self.metadata[sid]['impacto']:
                series_alto[sid] = data
        
        if series_alto:
            df_alto = pd.DataFrame(series_alto)
            filepath = processed_dir / f"fred_oil_alto_impacto_{timestamp}.csv"
            df_alto.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset alto impacto: {filepath.name}")
            logger.info(f"    - Series: {len(df_alto.columns)}")
        
        # 4. Guardar metadata
        import json
        metadata_file = processed_dir / f"fred_oil_metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"\n  ✓ Metadata guardada: {metadata_file.name}")
    
    def generar_reporte(self):
        """
        Genera reporte de datos obtenidos
        """
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE DATOS DE PETRÓLEO")
        logger.info("="*70)
        
        for series_id, data in self.datos.items():
            info = self.metadata[series_id]
            logger.info(f"\n  {info['nombre']} ({series_id})")
            logger.info(f"    Impacto: {info['impacto']}")
            logger.info(f"    Frecuencia: {info['frecuencia']}")
            logger.info(f"    Observaciones: {info['observaciones']}")
            logger.info(f"    Último valor: {info['ultimo_valor']:.2f} {info['unidad']}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("BOT PREDICTIVO - DATOS DE PETRÓLEO")
    logger.info("="*70)
    
    # Crear recolector
    collector = FREDOilCollector()
    
    # Obtener datos
    datos = collector.obtener_todas_series()
    
    # Crear datasets
    collector.crear_datasets()
    
    # Generar reporte
    collector.generar_reporte()
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ PROCESO COMPLETADO ✓✓✓")
    logger.info("="*70)
    logger.info("\nArchivos generados en: data/processed/fred_oil/")


if __name__ == "__main__":
    main()



