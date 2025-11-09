"""
Recolector de Pares de Divisas (Forex)
Datos históricos de tipos de cambio spot
"""
import pandas as pd
from fredapi import Fred
from datetime import datetime
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import FRED_API_KEY, RAW_DATA_DIR
from src.utils.logger import logger


# Pares de divisas principales en FRED
PARES_FOREX = {
    'DEXJPUS': {
        'nombre': 'USD/JPY (Dólar/Yen Japonés)',
        'descripcion': 'Yen japonés por dólar USA',
        'unidad': 'JPY por USD',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Segunda moneda más negociada'
    },
    'DEXUSAL': {
        'nombre': 'USD/AUD (Dólar/Dólar Australiano)',
        'descripcion': 'Dólares australianos por dólar USA',
        'unidad': 'AUD por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Moneda de commodities'
    },
    'DEXUSEU': {
        'nombre': 'USD/EUR (Dólar/Euro)',
        'descripcion': 'Dólares USA por euro',
        'unidad': 'USD por EUR',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Par más negociado del mundo'
    },
    'DEXCHUS': {
        'nombre': 'USD/CNY (Dólar/Yuan Chino)',
        'descripcion': 'Yuan chino por dólar USA',
        'unidad': 'CNY por USD',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Segunda economía mundial'
    },
    
    # Pares adicionales importantes
    'DEXUSUK': {
        'nombre': 'USD/GBP (Dólar/Libra Esterlina)',
        'descripcion': 'Dólares USA por libra esterlina',
        'unidad': 'USD por GBP',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Centro financiero Londres'
    },
    'DEXCAUS': {
        'nombre': 'USD/CAD (Dólar/Dólar Canadiense)',
        'descripcion': 'Dólares canadienses por dólar USA',
        'unidad': 'CAD por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Socio comercial principal'
    },
    'DEXMXUS': {
        'nombre': 'USD/MXN (Dólar/Peso Mexicano)',
        'descripcion': 'Pesos mexicanos por dólar USA',
        'unidad': 'MXN por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Economía emergente'
    },
    'DEXSZUS': {
        'nombre': 'USD/CHF (Dólar/Franco Suizo)',
        'descripcion': 'Francos suizos por dólar USA',
        'unidad': 'CHF por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Moneda refugio'
    },
    
    # Índices de dólar
    'DTWEXBGS': {
        'nombre': 'Índice Ponderado del Dólar USA',
        'descripcion': 'Trade Weighted US Dollar Index: Broad Goods and Services',
        'unidad': 'Índice',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Fortaleza general del dólar'
    },
}


class ForexCollector:
    """
    Recolector de datos de tipos de cambio (forex)
    """
    
    def __init__(self, api_key=None):
        """Inicializa el recolector"""
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED API key no encontrada")
        
        self.fred = Fred(api_key=self.api_key)
        self.datos = {}
        self.metadata = {}
        
        logger.info("✓ ForexCollector inicializado")
        logger.info(f"  API Key: {self.api_key[:10]}...")
    
    def obtener_par(self, par_id, info, start_date=None):
        """
        Obtiene datos de un par de divisas
        
        Args:
            par_id: ID del par en FRED
            info: Diccionario con información
            start_date: Fecha de inicio
            
        Returns:
            pandas.Series con los datos
        """
        try:
            logger.info(f"  Obteniendo {info['nombre']} ({par_id})...")
            
            if start_date is None:
                start_date = datetime(1999, 1, 1)  # Últimos 26 años
            
            data = self.fred.get_series(par_id, observation_start=start_date)
            
            if data is not None and len(data) > 0:
                logger.info(f"    ✓ {len(data)} observaciones")
                logger.info(f"    ✓ Período: {data.index.min()} a {data.index.max()}")
                logger.info(f"    ✓ Último valor: {data.iloc[-1]:.4f}")
                
                # Guardar metadata
                self.metadata[par_id] = {
                    'nombre': info['nombre'],
                    'descripcion': info['descripcion'],
                    'unidad': info['unidad'],
                    'frecuencia': info['frecuencia'],
                    'impacto': info['impacto'],
                    'observaciones': len(data),
                    'fecha_inicio': str(data.index.min()),
                    'fecha_fin': str(data.index.max()),
                    'ultimo_valor': float(data.iloc[-1]),
                    'minimo': float(data.min()),
                    'maximo': float(data.max()),
                    'promedio': float(data.mean())
                }
                
                return data
            else:
                logger.warning(f"    ✗ No se obtuvieron datos")
                return None
                
        except Exception as e:
            logger.error(f"    ✗ Error: {e}")
            return None
    
    def obtener_todos_pares(self):
        """
        Obtiene todos los pares de divisas
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO PARES DE DIVISAS (FOREX)")
        logger.info("="*70)
        logger.info(f"Total de pares: {len(PARES_FOREX)}")
        logger.info("")
        
        exitosos = 0
        
        for par_id, info in PARES_FOREX.items():
            data = self.obtener_par(par_id, info)
            if data is not None:
                self.datos[par_id] = data
                exitosos += 1
        
        logger.info(f"\n✓ Pares obtenidos: {exitosos}/{len(PARES_FOREX)}")
        
        return self.datos
    
    def crear_datasets(self):
        """
        Crea datasets organizados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASETS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset completo con todos los pares
        df_completo = pd.DataFrame(self.datos)
        filepath = processed_dir / f"forex_completo_{timestamp}.csv"
        df_completo.to_csv(filepath)
        logger.info(f"  ✓ Dataset completo: {filepath.name}")
        logger.info(f"    - Pares: {len(df_completo.columns)}")
        logger.info(f"    - Días: {len(df_completo)}")
        
        # 2. Solo pares principales solicitados
        pares_principales = ['DEXJPUS', 'DEXUSAL', 'DEXUSEU', 'DEXCHUS']
        pares_disponibles = [p for p in pares_principales if p in self.datos]
        
        if pares_disponibles:
            df_principales = pd.DataFrame({p: self.datos[p] for p in pares_disponibles})
            filepath = processed_dir / f"forex_principales_{timestamp}.csv"
            df_principales.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset principales: {filepath.name}")
            logger.info(f"    - Pares: {len(df_principales.columns)}")
        
        # 3. Dataset de alto impacto
        pares_alto = {pid: data for pid, data in self.datos.items() 
                     if 'ALTO' in self.metadata[pid]['impacto']}
        
        if pares_alto:
            df_alto = pd.DataFrame(pares_alto)
            filepath = processed_dir / f"forex_alto_impacto_{timestamp}.csv"
            df_alto.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset alto impacto: {filepath.name}")
            logger.info(f"    - Pares: {len(df_alto.columns)}")
        
        # 4. Calcular retornos diarios
        df_retornos = df_completo.pct_change()
        df_retornos.columns = [f'{col}_return' for col in df_retornos.columns]
        filepath = processed_dir / f"forex_retornos_{timestamp}.csv"
        df_retornos.to_csv(filepath)
        logger.info(f"\n  ✓ Dataset retornos: {filepath.name}")
        
        # 5. Guardar metadata
        metadata_file = processed_dir / f"forex_metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"\n  ✓ Metadata guardada: {metadata_file.name}")
        
        return {
            'completo': df_completo,
            'principales': df_principales if pares_disponibles else None,
            'alto_impacto': df_alto if pares_alto else None,
            'retornos': df_retornos
        }
    
    def generar_reporte(self):
        """
        Genera reporte detallado de los pares
        """
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE PARES DE DIVISAS")
        logger.info("="*70)
        
        for par_id, data in self.datos.items():
            info = self.metadata[par_id]
            logger.info(f"\n  {info['nombre']} ({par_id})")
            logger.info(f"    Impacto: {info['impacto']}")
            logger.info(f"    Frecuencia: {info['frecuencia']}")
            logger.info(f"    Período: {info['fecha_inicio']} → {info['fecha_fin']}")
            logger.info(f"    Observaciones: {info['observaciones']:,}")
            logger.info(f"    Valor actual: {info['ultimo_valor']:.4f} {info['unidad']}")
            logger.info(f"    Rango histórico: {info['minimo']:.4f} - {info['maximo']:.4f}")
            logger.info(f"    Promedio: {info['promedio']:.4f}")
        
        # Resumen estadístico
        logger.info("\n" + "="*70)
        logger.info("RESUMEN ESTADÍSTICO")
        logger.info("="*70)
        
        total_obs = sum(info['observaciones'] for info in self.metadata.values())
        logger.info(f"\nTotal de pares: {len(self.metadata)}")
        logger.info(f"Total de observaciones: {total_obs:,}")
        
        # Por impacto
        alto = sum(1 for info in self.metadata.values() if 'ALTO' in info['impacto'])
        medio = sum(1 for info in self.metadata.values() if 'MEDIO' in info['impacto'])
        
        logger.info(f"\nDistribución por impacto:")
        logger.info(f"  ALTO:  {alto} pares")
        logger.info(f"  MEDIO: {medio} pares")
    
    def calcular_correlaciones(self):
        """
        Calcula correlaciones entre pares
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONES ENTRE PARES")
        logger.info("="*70)
        
        df = pd.DataFrame(self.datos)
        correlacion = df.corr()
        
        logger.info("\nCorrelaciones más altas (excluyendo diagonal):")
        
        # Obtener pares de correlaciones
        correlaciones_pares = []
        for i in range(len(correlacion.columns)):
            for j in range(i+1, len(correlacion.columns)):
                par1 = correlacion.columns[i]
                par2 = correlacion.columns[j]
                corr_value = correlacion.iloc[i, j]
                correlaciones_pares.append((par1, par2, corr_value))
        
        # Ordenar por correlación absoluta
        correlaciones_pares.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # Mostrar top 10
        for par1, par2, corr in correlaciones_pares[:10]:
            nombre1 = PARES_FOREX.get(par1, {}).get('nombre', par1)
            nombre2 = PARES_FOREX.get(par2, {}).get('nombre', par2)
            logger.info(f"  {corr:+.3f} | {nombre1[:20]} ↔ {nombre2[:20]}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECTOR DE PARES DE DIVISAS (FOREX)")
    logger.info("="*70)
    logger.info("Pares solicitados: USD/JPY, USD/AUD, USD/EUR, USD/CNY")
    logger.info("")
    
    try:
        # Crear recolector
        collector = ForexCollector()
        
        # Obtener todos los pares
        datos = collector.obtener_todos_pares()
        
        if datos:
            # Crear datasets
            datasets = collector.crear_datasets()
            
            # Calcular correlaciones
            collector.calcular_correlaciones()
            
            # Generar reporte
            collector.generar_reporte()
            
            logger.info("\n" + "="*70)
            logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
            logger.info("="*70)
            logger.info("\n📂 Archivos generados en: data/processed/forex/")
            logger.info("\n📊 Archivos principales:")
            logger.info("  1. forex_principales_*.csv  ⭐ USD/JPY, USD/AUD, USD/EUR, USD/CNY")
            logger.info("  2. forex_completo_*.csv     Todos los pares")
            logger.info("  3. forex_retornos_*.csv     Cambios diarios")
            logger.info("  4. forex_metadata_*.json    Info detallada")
            
            logger.info("\n🎯 Estos datos son perfectos para:")
            logger.info("  - Predecir impacto de noticias de bancos centrales")
            logger.info("  - Analizar correlaciones con S&P 500")
            logger.info("  - Identificar movimientos de flight-to-safety")
            logger.info("  - Trading de forex basado en economía USA")
            
        else:
            logger.error("No se obtuvieron datos de forex")
    
    except Exception as e:
        logger.error(f"Error en proceso: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()

Recolector de Pares de Divisas (Forex)
Datos históricos de tipos de cambio spot
"""
import pandas as pd
from fredapi import Fred
from datetime import datetime
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import FRED_API_KEY, RAW_DATA_DIR
from src.utils.logger import logger


# Pares de divisas principales en FRED
PARES_FOREX = {
    'DEXJPUS': {
        'nombre': 'USD/JPY (Dólar/Yen Japonés)',
        'descripcion': 'Yen japonés por dólar USA',
        'unidad': 'JPY por USD',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Segunda moneda más negociada'
    },
    'DEXUSAL': {
        'nombre': 'USD/AUD (Dólar/Dólar Australiano)',
        'descripcion': 'Dólares australianos por dólar USA',
        'unidad': 'AUD por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Moneda de commodities'
    },
    'DEXUSEU': {
        'nombre': 'USD/EUR (Dólar/Euro)',
        'descripcion': 'Dólares USA por euro',
        'unidad': 'USD por EUR',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Par más negociado del mundo'
    },
    'DEXCHUS': {
        'nombre': 'USD/CNY (Dólar/Yuan Chino)',
        'descripcion': 'Yuan chino por dólar USA',
        'unidad': 'CNY por USD',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Segunda economía mundial'
    },
    
    # Pares adicionales importantes
    'DEXUSUK': {
        'nombre': 'USD/GBP (Dólar/Libra Esterlina)',
        'descripcion': 'Dólares USA por libra esterlina',
        'unidad': 'USD por GBP',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Centro financiero Londres'
    },
    'DEXCAUS': {
        'nombre': 'USD/CAD (Dólar/Dólar Canadiense)',
        'descripcion': 'Dólares canadienses por dólar USA',
        'unidad': 'CAD por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Socio comercial principal'
    },
    'DEXMXUS': {
        'nombre': 'USD/MXN (Dólar/Peso Mexicano)',
        'descripcion': 'Pesos mexicanos por dólar USA',
        'unidad': 'MXN por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Economía emergente'
    },
    'DEXSZUS': {
        'nombre': 'USD/CHF (Dólar/Franco Suizo)',
        'descripcion': 'Francos suizos por dólar USA',
        'unidad': 'CHF por USD',
        'frecuencia': 'Diaria',
        'impacto': 'MEDIO - Moneda refugio'
    },
    
    # Índices de dólar
    'DTWEXBGS': {
        'nombre': 'Índice Ponderado del Dólar USA',
        'descripcion': 'Trade Weighted US Dollar Index: Broad Goods and Services',
        'unidad': 'Índice',
        'frecuencia': 'Diaria',
        'impacto': 'ALTO - Fortaleza general del dólar'
    },
}


class ForexCollector:
    """
    Recolector de datos de tipos de cambio (forex)
    """
    
    def __init__(self, api_key=None):
        """Inicializa el recolector"""
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED API key no encontrada")
        
        self.fred = Fred(api_key=self.api_key)
        self.datos = {}
        self.metadata = {}
        
        logger.info("✓ ForexCollector inicializado")
        logger.info(f"  API Key: {self.api_key[:10]}...")
    
    def obtener_par(self, par_id, info, start_date=None):
        """
        Obtiene datos de un par de divisas
        
        Args:
            par_id: ID del par en FRED
            info: Diccionario con información
            start_date: Fecha de inicio
            
        Returns:
            pandas.Series con los datos
        """
        try:
            logger.info(f"  Obteniendo {info['nombre']} ({par_id})...")
            
            if start_date is None:
                start_date = datetime(1999, 1, 1)  # Últimos 26 años
            
            data = self.fred.get_series(par_id, observation_start=start_date)
            
            if data is not None and len(data) > 0:
                logger.info(f"    ✓ {len(data)} observaciones")
                logger.info(f"    ✓ Período: {data.index.min()} a {data.index.max()}")
                logger.info(f"    ✓ Último valor: {data.iloc[-1]:.4f}")
                
                # Guardar metadata
                self.metadata[par_id] = {
                    'nombre': info['nombre'],
                    'descripcion': info['descripcion'],
                    'unidad': info['unidad'],
                    'frecuencia': info['frecuencia'],
                    'impacto': info['impacto'],
                    'observaciones': len(data),
                    'fecha_inicio': str(data.index.min()),
                    'fecha_fin': str(data.index.max()),
                    'ultimo_valor': float(data.iloc[-1]),
                    'minimo': float(data.min()),
                    'maximo': float(data.max()),
                    'promedio': float(data.mean())
                }
                
                return data
            else:
                logger.warning(f"    ✗ No se obtuvieron datos")
                return None
                
        except Exception as e:
            logger.error(f"    ✗ Error: {e}")
            return None
    
    def obtener_todos_pares(self):
        """
        Obtiene todos los pares de divisas
        """
        logger.info("\n" + "="*70)
        logger.info("RECOLECTANDO PARES DE DIVISAS (FOREX)")
        logger.info("="*70)
        logger.info(f"Total de pares: {len(PARES_FOREX)}")
        logger.info("")
        
        exitosos = 0
        
        for par_id, info in PARES_FOREX.items():
            data = self.obtener_par(par_id, info)
            if data is not None:
                self.datos[par_id] = data
                exitosos += 1
        
        logger.info(f"\n✓ Pares obtenidos: {exitosos}/{len(PARES_FOREX)}")
        
        return self.datos
    
    def crear_datasets(self):
        """
        Crea datasets organizados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASETS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset completo con todos los pares
        df_completo = pd.DataFrame(self.datos)
        filepath = processed_dir / f"forex_completo_{timestamp}.csv"
        df_completo.to_csv(filepath)
        logger.info(f"  ✓ Dataset completo: {filepath.name}")
        logger.info(f"    - Pares: {len(df_completo.columns)}")
        logger.info(f"    - Días: {len(df_completo)}")
        
        # 2. Solo pares principales solicitados
        pares_principales = ['DEXJPUS', 'DEXUSAL', 'DEXUSEU', 'DEXCHUS']
        pares_disponibles = [p for p in pares_principales if p in self.datos]
        
        if pares_disponibles:
            df_principales = pd.DataFrame({p: self.datos[p] for p in pares_disponibles})
            filepath = processed_dir / f"forex_principales_{timestamp}.csv"
            df_principales.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset principales: {filepath.name}")
            logger.info(f"    - Pares: {len(df_principales.columns)}")
        
        # 3. Dataset de alto impacto
        pares_alto = {pid: data for pid, data in self.datos.items() 
                     if 'ALTO' in self.metadata[pid]['impacto']}
        
        if pares_alto:
            df_alto = pd.DataFrame(pares_alto)
            filepath = processed_dir / f"forex_alto_impacto_{timestamp}.csv"
            df_alto.to_csv(filepath)
            logger.info(f"\n  ✓ Dataset alto impacto: {filepath.name}")
            logger.info(f"    - Pares: {len(df_alto.columns)}")
        
        # 4. Calcular retornos diarios
        df_retornos = df_completo.pct_change()
        df_retornos.columns = [f'{col}_return' for col in df_retornos.columns]
        filepath = processed_dir / f"forex_retornos_{timestamp}.csv"
        df_retornos.to_csv(filepath)
        logger.info(f"\n  ✓ Dataset retornos: {filepath.name}")
        
        # 5. Guardar metadata
        metadata_file = processed_dir / f"forex_metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"\n  ✓ Metadata guardada: {metadata_file.name}")
        
        return {
            'completo': df_completo,
            'principales': df_principales if pares_disponibles else None,
            'alto_impacto': df_alto if pares_alto else None,
            'retornos': df_retornos
        }
    
    def generar_reporte(self):
        """
        Genera reporte detallado de los pares
        """
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE PARES DE DIVISAS")
        logger.info("="*70)
        
        for par_id, data in self.datos.items():
            info = self.metadata[par_id]
            logger.info(f"\n  {info['nombre']} ({par_id})")
            logger.info(f"    Impacto: {info['impacto']}")
            logger.info(f"    Frecuencia: {info['frecuencia']}")
            logger.info(f"    Período: {info['fecha_inicio']} → {info['fecha_fin']}")
            logger.info(f"    Observaciones: {info['observaciones']:,}")
            logger.info(f"    Valor actual: {info['ultimo_valor']:.4f} {info['unidad']}")
            logger.info(f"    Rango histórico: {info['minimo']:.4f} - {info['maximo']:.4f}")
            logger.info(f"    Promedio: {info['promedio']:.4f}")
        
        # Resumen estadístico
        logger.info("\n" + "="*70)
        logger.info("RESUMEN ESTADÍSTICO")
        logger.info("="*70)
        
        total_obs = sum(info['observaciones'] for info in self.metadata.values())
        logger.info(f"\nTotal de pares: {len(self.metadata)}")
        logger.info(f"Total de observaciones: {total_obs:,}")
        
        # Por impacto
        alto = sum(1 for info in self.metadata.values() if 'ALTO' in info['impacto'])
        medio = sum(1 for info in self.metadata.values() if 'MEDIO' in info['impacto'])
        
        logger.info(f"\nDistribución por impacto:")
        logger.info(f"  ALTO:  {alto} pares")
        logger.info(f"  MEDIO: {medio} pares")
    
    def calcular_correlaciones(self):
        """
        Calcula correlaciones entre pares
        """
        logger.info("\n" + "="*70)
        logger.info("CORRELACIONES ENTRE PARES")
        logger.info("="*70)
        
        df = pd.DataFrame(self.datos)
        correlacion = df.corr()
        
        logger.info("\nCorrelaciones más altas (excluyendo diagonal):")
        
        # Obtener pares de correlaciones
        correlaciones_pares = []
        for i in range(len(correlacion.columns)):
            for j in range(i+1, len(correlacion.columns)):
                par1 = correlacion.columns[i]
                par2 = correlacion.columns[j]
                corr_value = correlacion.iloc[i, j]
                correlaciones_pares.append((par1, par2, corr_value))
        
        # Ordenar por correlación absoluta
        correlaciones_pares.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # Mostrar top 10
        for par1, par2, corr in correlaciones_pares[:10]:
            nombre1 = PARES_FOREX.get(par1, {}).get('nombre', par1)
            nombre2 = PARES_FOREX.get(par2, {}).get('nombre', par2)
            logger.info(f"  {corr:+.3f} | {nombre1[:20]} ↔ {nombre2[:20]}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECTOR DE PARES DE DIVISAS (FOREX)")
    logger.info("="*70)
    logger.info("Pares solicitados: USD/JPY, USD/AUD, USD/EUR, USD/CNY")
    logger.info("")
    
    try:
        # Crear recolector
        collector = ForexCollector()
        
        # Obtener todos los pares
        datos = collector.obtener_todos_pares()
        
        if datos:
            # Crear datasets
            datasets = collector.crear_datasets()
            
            # Calcular correlaciones
            collector.calcular_correlaciones()
            
            # Generar reporte
            collector.generar_reporte()
            
            logger.info("\n" + "="*70)
            logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
            logger.info("="*70)
            logger.info("\n📂 Archivos generados en: data/processed/forex/")
            logger.info("\n📊 Archivos principales:")
            logger.info("  1. forex_principales_*.csv  ⭐ USD/JPY, USD/AUD, USD/EUR, USD/CNY")
            logger.info("  2. forex_completo_*.csv     Todos los pares")
            logger.info("  3. forex_retornos_*.csv     Cambios diarios")
            logger.info("  4. forex_metadata_*.json    Info detallada")
            
            logger.info("\n🎯 Estos datos son perfectos para:")
            logger.info("  - Predecir impacto de noticias de bancos centrales")
            logger.info("  - Analizar correlaciones con S&P 500")
            logger.info("  - Identificar movimientos de flight-to-safety")
            logger.info("  - Trading de forex basado en economía USA")
            
        else:
            logger.error("No se obtuvieron datos de forex")
    
    except Exception as e:
        logger.error(f"Error en proceso: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()



