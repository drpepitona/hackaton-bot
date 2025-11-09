"""
Recolector Completo de Datos Económicos y Financieros - FRED
Para entrenamiento de IA predictiva de impacto de noticias en mercados
"""
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import json

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import FRED_API_KEY, RAW_DATA_DIR
from src.utils.logger import logger


# ============================================================================
# CONFIGURACIÓN DE SERIES - ORGANIZADAS POR CATEGORÍA
# ============================================================================

SERIES_CONFIG = {
    'indicadores_economicos_usa': {
        'descripcion': 'Indicadores macroeconómicos principales de Estados Unidos',
        'series': {
            'GDPC1': {
                'nombre': 'PIB Real (Producto Interno Bruto)',
                'unidad': 'Miles de millones de dólares',
                'frecuencia': 'Trimestral',
                'impacto': 'ALTO - Indicador principal de salud económica'
            },
            'UNRATE': {
                'nombre': 'Tasa de Desempleo',
                'unidad': 'Porcentaje',
                'frecuencia': 'Mensual',
                'impacto': 'ALTO - Impacta decisiones de Fed y mercados'
            },
            'CPIAUCSL': {
                'nombre': 'Índice de Precios al Consumidor (CPI)',
                'unidad': 'Índice 1982-84=100',
                'frecuencia': 'Mensual',
                'impacto': 'ALTO - Medida principal de inflación'
            }
        }
    },
    
    'mercados_financieros': {
        'descripcion': 'Indicadores de mercados financieros y volatilidad',
        'series': {
            'VIXCLS': {
                'nombre': 'Índice de Volatilidad CBOE (VIX)',
                'unidad': 'Índice',
                'frecuencia': 'Diaria',
                'impacto': 'ALTO - "Índice del miedo", mide volatilidad esperada'
            },
            'DGS10': {
                'nombre': 'Rendimiento Tesoro USA 10 años',
                'unidad': 'Porcentaje',
                'frecuencia': 'Diaria',
                'impacto': 'ALTO - Tasa de referencia global, afecta todos los mercados'
            }
        }
    },
    
    'tipos_cambio_real': {
        'descripcion': 'Tipos de cambio real efectivo (ajustados por inflación)',
        'series': {
            'RBXMBIS': {
                'nombre': 'Tipo Cambio Real Efectivo - Área del Euro',
                'unidad': 'Índice',
                'frecuencia': 'Mensual',
                'impacto': 'MEDIO - Competitividad comercial europea'
            },
            'RBJPBIS': {
                'nombre': 'Tipo Cambio Real Efectivo - Japón',
                'unidad': 'Índice',
                'frecuencia': 'Mensual',
                'impacto': 'MEDIO - Influye en exportaciones japonesas'
            },
            'RBHKBIS': {
                'nombre': 'Tipo Cambio Real Efectivo - Hong Kong',
                'unidad': 'Índice',
                'frecuencia': 'Mensual',
                'impacto': 'BAJO - Hub financiero asiático'
            },
            'RBAUBIS': {
                'nombre': 'Tipo Cambio Real Efectivo - Australia',
                'unidad': 'Índice',
                'frecuencia': 'Mensual',
                'impacto': 'BAJO - Commodities y mercados emergentes'
            },
            'RBCNBIS': {
                'nombre': 'Tipo Cambio Real Efectivo - China',
                'unidad': 'Índice',
                'frecuencia': 'Mensual',
                'impacto': 'ALTO - Segunda economía mundial, gran impacto'
            }
        }
    },
    
    'tipos_cambio_spot': {
        'descripcion': 'Tipos de cambio spot (precio actual)',
        'series': {
            'DEXUSEU': {
                'nombre': 'Tipo Cambio Spot USD/EUR',
                'unidad': 'Dólares por Euro',
                'frecuencia': 'Diaria',
                'impacto': 'ALTO - Relación dólar-euro más importante'
            },
            'RTWEXBGS': {
                'nombre': 'Índice Real Amplio del Dólar USA',
                'unidad': 'Índice',
                'frecuencia': 'Diaria',
                'impacto': 'ALTO - Fortaleza del dólar vs canasta de monedas'
            }
        }
    }
}


class FREDCollectorCompleto:
    """
    Recolector completo de datos económicos y financieros
    Optimizado para entrenamiento de IA predictiva
    """
    
    def __init__(self, api_key=None):
        """Inicializa el recolector"""
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED API key no encontrada. Configura FRED_API_KEY en .env")
        
        self.fred = Fred(api_key=self.api_key)
        self.datos_recolectados = {}
        self.metadata = {}
        
        logger.info("✓ FREDCollectorCompleto inicializado")
        logger.info(f"  API Key: {self.api_key[:10]}...")
    
    def obtener_serie(self, series_id, info):
        """
        Obtiene una serie individual de FRED con manejo de errores
        
        Args:
            series_id: ID de la serie en FRED
            info: Diccionario con información de la serie
            
        Returns:
            pandas.Series o None si hay error
        """
        try:
            logger.info(f"  Obteniendo {info['nombre']} ({series_id})...")
            
            # Obtener datos desde 2000 (últimos 25 años de historia)
            start_date = datetime(2000, 1, 1)
            data = self.fred.get_series(series_id, observation_start=start_date)
            
            if data is not None and len(data) > 0:
                logger.info(f"    ✓ {len(data)} observaciones ({data.index.min()} a {data.index.max()})")
                logger.info(f"    ✓ Último valor: {data.iloc[-1]:.4f} ({data.index[-1]})")
                
                # Guardar metadata
                self.metadata[series_id] = {
                    'nombre': info['nombre'],
                    'unidad': info['unidad'],
                    'frecuencia': info['frecuencia'],
                    'impacto': info['impacto'],
                    'observaciones': len(data),
                    'fecha_inicio': str(data.index.min()),
                    'fecha_fin': str(data.index.max()),
                    'ultimo_valor': float(data.iloc[-1]),
                    'valores_faltantes': int(data.isna().sum())
                }
                
                return data
            else:
                logger.warning(f"    ✗ No se obtuvieron datos para {series_id}")
                return None
                
        except Exception as e:
            logger.error(f"    ✗ Error al obtener {series_id}: {e}")
            return None
    
    def obtener_todas_series(self):
        """
        Obtiene todas las series organizadas por categoría
        
        Returns:
            dict: Diccionario con todas las series organizadas
        """
        logger.info("\n" + "="*70)
        logger.info("INICIANDO RECOLECCIÓN DE DATOS ECONÓMICOS Y FINANCIEROS")
        logger.info("="*70)
        
        # Contar total de series
        total_series = sum(len(cat['series']) for cat in SERIES_CONFIG.values())
        logger.info(f"Total de series a obtener: {total_series}")
        logger.info(f"Categorías: {len(SERIES_CONFIG)}")
        logger.info("")
        
        series_exitosas = 0
        
        # Obtener cada categoría
        for categoria, config in SERIES_CONFIG.items():
            logger.info(f"\n📊 CATEGORÍA: {config['descripcion']}")
            logger.info("-"*70)
            
            self.datos_recolectados[categoria] = {}
            
            for series_id, info in config['series'].items():
                data = self.obtener_serie(series_id, info)
                if data is not None:
                    self.datos_recolectados[categoria][series_id] = data
                    series_exitosas += 1
        
        logger.info("\n" + "="*70)
        logger.info(f"✓ RECOLECCIÓN COMPLETADA: {series_exitosas}/{total_series} series obtenidas")
        logger.info("="*70)
        
        return self.datos_recolectados
    
    def crear_datasets_estructurados(self):
        """
        Crea datasets estructurados para entrenamiento de IA
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASETS ESTRUCTURADOS")
        logger.info("="*70)
        
        # Crear directorio de datos procesados
        processed_dir = RAW_DATA_DIR.parent / "processed" / "fred"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Dataset por categoría (separados)
        for categoria, series_dict in self.datos_recolectados.items():
            if series_dict:
                df = pd.DataFrame(series_dict)
                filename = processed_dir / f"{categoria}_{timestamp}.csv"
                df.to_csv(filename)
                logger.info(f"  ✓ {categoria}: {filename.name}")
        
        # 2. Dataset completo combinado (todas las series)
        all_series = {}
        for categoria, series_dict in self.datos_recolectados.items():
            all_series.update(series_dict)
        
        df_completo = pd.DataFrame(all_series)
        filename_completo = processed_dir / f"fred_completo_{timestamp}.csv"
        df_completo.to_csv(filename_completo)
        logger.info(f"\n  ✓ Dataset completo: {filename_completo.name}")
        logger.info(f"    - Columnas: {len(df_completo.columns)}")
        logger.info(f"    - Filas: {len(df_completo)}")
        
        # 3. Guardar metadata en JSON
        metadata_file = processed_dir / f"metadata_{timestamp}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"\n  ✓ Metadata guardada: {metadata_file.name}")
        
        # 4. Crear dataset de alta frecuencia (solo datos diarios)
        series_diarias = {}
        for categoria, series_dict in self.datos_recolectados.items():
            for series_id, data in series_dict.items():
                if self.metadata[series_id]['frecuencia'] == 'Diaria':
                    series_diarias[series_id] = data
        
        if series_diarias:
            df_diario = pd.DataFrame(series_diarias)
            filename_diario = processed_dir / f"fred_diario_{timestamp}.csv"
            df_diario.to_csv(filename_diario)
            logger.info(f"\n  ✓ Dataset diario: {filename_diario.name}")
            logger.info(f"    - Series: {len(df_diario.columns)}")
        
        # 5. Crear dataset de indicadores de alto impacto
        series_alto_impacto = {}
        for categoria, series_dict in self.datos_recolectados.items():
            for series_id, data in series_dict.items():
                if 'ALTO' in self.metadata[series_id]['impacto']:
                    series_alto_impacto[series_id] = data
        
        if series_alto_impacto:
            df_alto_impacto = pd.DataFrame(series_alto_impacto)
            filename_alto = processed_dir / f"fred_alto_impacto_{timestamp}.csv"
            df_alto_impacto.to_csv(filename_alto)
            logger.info(f"\n  ✓ Dataset alto impacto: {filename_alto.name}")
            logger.info(f"    - Series: {len(df_alto_impacto.columns)}")
        
        return {
            'completo': df_completo,
            'diario': df_diario if series_diarias else None,
            'alto_impacto': df_alto_impacto if series_alto_impacto else None,
            'metadata_file': metadata_file
        }
    
    def generar_reporte(self):
        """Genera un reporte detallado de los datos recolectados"""
        logger.info("\n" + "="*70)
        logger.info("REPORTE DE DATOS RECOLECTADOS")
        logger.info("="*70)
        
        for categoria, series_dict in self.datos_recolectados.items():
            config = SERIES_CONFIG[categoria]
            logger.info(f"\n📊 {config['descripcion'].upper()}")
            logger.info("-"*70)
            
            for series_id, data in series_dict.items():
                info = self.metadata[series_id]
                logger.info(f"\n  {info['nombre']} ({series_id})")
                logger.info(f"    Impacto: {info['impacto']}")
                logger.info(f"    Frecuencia: {info['frecuencia']}")
                logger.info(f"    Período: {info['fecha_inicio']} → {info['fecha_fin']}")
                logger.info(f"    Observaciones: {info['observaciones']}")
                logger.info(f"    Último valor: {info['ultimo_valor']:.4f} {info['unidad']}")
                
                if info['valores_faltantes'] > 0:
                    logger.warning(f"    ⚠ Valores faltantes: {info['valores_faltantes']}")
        
        # Resumen estadístico
        logger.info("\n" + "="*70)
        logger.info("RESUMEN ESTADÍSTICO")
        logger.info("="*70)
        
        total_obs = sum(info['observaciones'] for info in self.metadata.values())
        total_series = len(self.metadata)
        
        logger.info(f"\n  Total de series: {total_series}")
        logger.info(f"  Total de observaciones: {total_obs:,}")
        logger.info(f"  Promedio por serie: {total_obs//total_series:,}")
        
        # Contar por impacto
        alto_impacto = sum(1 for info in self.metadata.values() if 'ALTO' in info['impacto'])
        medio_impacto = sum(1 for info in self.metadata.values() if 'MEDIO' in info['impacto'])
        bajo_impacto = sum(1 for info in self.metadata.values() if 'BAJO' in info['impacto'])
        
        logger.info(f"\n  Distribución por impacto:")
        logger.info(f"    ALTO:  {alto_impacto} series")
        logger.info(f"    MEDIO: {medio_impacto} series")
        logger.info(f"    BAJO:  {bajo_impacto} series")
        
        # Contar por frecuencia
        diarias = sum(1 for info in self.metadata.values() if info['frecuencia'] == 'Diaria')
        mensuales = sum(1 for info in self.metadata.values() if info['frecuencia'] == 'Mensual')
        trimestrales = sum(1 for info in self.metadata.values() if info['frecuencia'] == 'Trimestral')
        
        logger.info(f"\n  Distribución por frecuencia:")
        logger.info(f"    Diaria:      {diarias} series")
        logger.info(f"    Mensual:     {mensuales} series")
        logger.info(f"    Trimestral:  {trimestrales} series")


def main():
    """Función principal"""
    try:
        logger.info("="*70)
        logger.info("BOT PREDICTIVO - RECOLECCIÓN DE DATOS ECONÓMICOS")
        logger.info("Para entrenamiento de IA de impacto de noticias")
        logger.info("="*70)
        
        # Crear recolector
        collector = FREDCollectorCompleto()
        
        # Obtener todas las series
        datos = collector.obtener_todas_series()
        
        # Crear datasets estructurados
        datasets = collector.crear_datasets_estructurados()
        
        # Generar reporte
        collector.generar_reporte()
        
        logger.info("\n" + "="*70)
        logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
        logger.info("="*70)
        logger.info("\n📂 Archivos generados en: data/processed/fred/")
        logger.info("\n📋 Próximos pasos:")
        logger.info("  1. Revisa los datasets en data/processed/fred/")
        logger.info("  2. Analiza el archivo metadata_*.json")
        logger.info("  3. Ejecuta análisis exploratorio")
        logger.info("  4. Recolecta datos de noticias para correlacionar")
        logger.info("  5. Entrena modelo de IA predictiva")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error en el proceso: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


