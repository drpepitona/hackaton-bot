"""
Recolector de datos del Banco Mundial
Commodity Markets Outlook (CMO) - Precios de commodities
"""
import pandas as pd
import requests
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


# URL del archivo Excel del Banco Mundial
WORLDBANK_CMO_URL = "https://thedocs.worldbank.org/en/doc/18675f1d1639c7a34d463f59263ba0a2-0050012025/related/CMO-Historical-Data-Annual.xlsx"


class WorldBankCollector:
    """
    Recolector de datos de commodities del Banco Mundial
    """
    
    def __init__(self):
        """Inicializa el recolector"""
        logger.info("✓ WorldBankCollector inicializado")
    
    def descargar_archivo(self, url=WORLDBANK_CMO_URL):
        """
        Descarga el archivo Excel del Banco Mundial
        
        Args:
            url: URL del archivo
            
        Returns:
            Path al archivo descargado
        """
        try:
            logger.info("Descargando archivo del Banco Mundial...")
            logger.info(f"  URL: {url[:80]}...")
            
            # Descargar archivo
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                # Crear directorio
                wb_dir = RAW_DATA_DIR / "worldbank"
                wb_dir.mkdir(parents=True, exist_ok=True)
                
                # Guardar archivo
                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"CMO-Historical-Data-Annual_{timestamp}.xlsx"
                filepath = wb_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"  ✓ Archivo descargado: {filepath}")
                logger.info(f"  ✓ Tamaño: {len(response.content) / 1024 / 1024:.2f} MB")
                
                return filepath
            else:
                logger.error(f"Error al descargar: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error al descargar archivo: {e}")
            return None
    
    def leer_excel(self, filepath):
        """
        Lee el archivo Excel y extrae las hojas importantes
        
        Args:
            filepath: Path al archivo Excel
            
        Returns:
            Diccionario con DataFrames por hoja
        """
        try:
            logger.info(f"\nLeyendo archivo Excel...")
            
            # Leer todas las hojas
            excel_file = pd.ExcelFile(filepath)
            
            logger.info(f"  Hojas encontradas: {len(excel_file.sheet_names)}")
            for i, sheet in enumerate(excel_file.sheet_names, 1):
                logger.info(f"    {i}. {sheet}")
            
            # Leer hojas importantes
            hojas_importantes = [
                'Annual Prices',
                'Annual Indices',
                'Monthly Prices',
                'Monthly Indices'
            ]
            
            datos = {}
            for sheet_name in hojas_importantes:
                if sheet_name in excel_file.sheet_names:
                    logger.info(f"\n  Leyendo hoja: {sheet_name}...")
                    df = pd.read_excel(filepath, sheet_name=sheet_name)
                    logger.info(f"    ✓ Dimensiones: {df.shape}")
                    datos[sheet_name] = df
                else:
                    logger.warning(f"  Hoja '{sheet_name}' no encontrada")
            
            return datos
            
        except Exception as e:
            logger.error(f"Error al leer Excel: {e}")
            return None
    
    def procesar_precios_anuales(self, df):
        """
        Procesa la hoja de precios anuales
        """
        try:
            logger.info("\n  Procesando precios anuales...")
            
            # El archivo tiene una estructura específica
            # Usualmente las primeras filas son headers
            # Intentar diferentes configuraciones
            
            # Buscar fila con años (números > 1900)
            for i in range(min(10, len(df))):
                row = df.iloc[i]
                if any(str(val).isdigit() and int(str(val)[:4]) > 1900 for val in row if pd.notna(val)):
                    logger.info(f"    Fila de años encontrada: {i}")
                    
                    # Tomar esa fila como header
                    df_clean = df.iloc[i+1:].copy()
                    df_clean.columns = df.iloc[i].values
                    
                    # Filtrar filas válidas
                    df_clean = df_clean.dropna(how='all')
                    
                    logger.info(f"    ✓ Datos procesados: {df_clean.shape}")
                    return df_clean
            
            logger.warning("    No se pudo determinar estructura automáticamente")
            return df
            
        except Exception as e:
            logger.error(f"Error al procesar precios anuales: {e}")
            return df
    
    def extraer_commodities_energia(self, datos):
        """
        Extrae solo commodities relacionados con energía
        """
        try:
            logger.info("\n  Extrayendo commodities de energía...")
            
            # Buscar en Annual Prices
            if 'Annual Prices' in datos:
                df = datos['Annual Prices']
                
                # Buscar filas que contengan commodities de energía
                keywords = ['crude', 'oil', 'petroleum', 'gas', 'energy', 
                           'brent', 'wti', 'natural gas', 'coal']
                
                # Filtrar por primera columna (nombre del commodity)
                if len(df.columns) > 0:
                    first_col = df.columns[0]
                    
                    mask = df[first_col].astype(str).str.lower().apply(
                        lambda x: any(kw in x for kw in keywords)
                    )
                    
                    df_energia = df[mask]
                    
                    logger.info(f"    ✓ Commodities de energía encontrados: {len(df_energia)}")
                    
                    return df_energia
            
            return None
            
        except Exception as e:
            logger.error(f"Error al extraer commodities de energía: {e}")
            return None
    
    def guardar_datos_procesados(self, datos):
        """
        Guarda los datos procesados
        """
        try:
            # Crear directorio
            processed_dir = RAW_DATA_DIR.parent / "processed" / "worldbank"
            processed_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d')
            
            # Guardar cada hoja
            for sheet_name, df in datos.items():
                if df is not None and not df.empty:
                    # Limpiar nombre para archivo
                    clean_name = sheet_name.replace(' ', '_').lower()
                    filename = f"worldbank_{clean_name}_{timestamp}.csv"
                    filepath = processed_dir / filename
                    
                    df.to_csv(filepath, index=False)
                    logger.info(f"  ✓ Guardado: {filepath}")
            
        except Exception as e:
            logger.error(f"Error al guardar datos: {e}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("RECOLECCIÓN DE DATOS DE COMMODITIES - BANCO MUNDIAL")
    logger.info("="*70)
    
    # Crear recolector
    collector = WorldBankCollector()
    
    # Descargar archivo
    logger.info("\n1. Descargando archivo...")
    filepath = collector.descargar_archivo()
    
    if filepath:
        # Leer Excel
        logger.info("\n2. Leyendo datos...")
        datos = collector.leer_excel(filepath)
        
        if datos:
            # Procesar cada hoja
            logger.info("\n3. Procesando datos...")
            datos_procesados = {}
            
            for sheet_name, df in datos.items():
                if 'Prices' in sheet_name:
                    df_procesado = collector.procesar_precios_anuales(df)
                    datos_procesados[sheet_name] = df_procesado
                else:
                    datos_procesados[sheet_name] = df
            
            # Extraer commodities de energía
            logger.info("\n4. Extrayendo commodities de energía...")
            df_energia = collector.extraer_commodities_energia(datos_procesados)
            
            if df_energia is not None:
                datos_procesados['Energy Commodities'] = df_energia
            
            # Guardar datos procesados
            logger.info("\n5. Guardando datos procesados...")
            collector.guardar_datos_procesados(datos_procesados)
            
            logger.info("\n" + "="*70)
            logger.info("✓ RECOLECCIÓN COMPLETADA EXITOSAMENTE")
            logger.info("="*70)
        else:
            logger.error("No se pudieron leer los datos del Excel")
    else:
        logger.error("No se pudo descargar el archivo")


if __name__ == "__main__":
    main()


