"""
Procesa y organiza datos de índices de mercado
Crea datasets listos para entrenamiento
"""
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class ProcesadorIndicesMercado:
    """
    Procesa datos de índices bursátiles
    """
    
    def __init__(self):
        """Inicializa el procesador"""
        self.indices = {}
        logger.info("✓ ProcesadorIndicesMercado inicializado")
    
    def cargar_indices(self, tickers=['SPY', 'QQQ', 'DIA', 'IWM']):
        """
        Carga datos de índices desde archivos CSV
        
        Args:
            tickers: Lista de tickers a cargar
        """
        logger.info(f"Cargando {len(tickers)} índices...")
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        for ticker in tickers:
            # Buscar archivo más reciente
            files = list(RAW_DATA_DIR.glob(f"{ticker}_*.csv"))
            if files:
                latest_file = max(files, key=lambda x: x.stat().st_mtime)
                df = pd.read_csv(latest_file, index_col=0, parse_dates=True)
                self.indices[ticker] = df
                logger.info(f"  ✓ {ticker}: {len(df)} días ({df.index.min()} a {df.index.max()})")
            else:
                logger.warning(f"  ✗ {ticker}: No se encontró archivo")
        
        return self.indices
    
    def crear_dataset_combinado(self):
        """
        Crea un dataset con todos los índices en columnas
        """
        logger.info("\nCreando dataset combinado...")
        
        # Diccionario para almacenar series
        data_dict = {}
        
        for ticker, df in self.indices.items():
            # Agregar precio de cierre
            data_dict[f'{ticker}_Close'] = df['Close']
            # Agregar volumen
            data_dict[f'{ticker}_Volume'] = df['Volume']
            # Calcular retornos diarios
            data_dict[f'{ticker}_Return'] = df['Close'].pct_change()
        
        # Crear DataFrame combinado
        df_combined = pd.DataFrame(data_dict)
        
        logger.info(f"  ✓ Dataset combinado: {df_combined.shape}")
        logger.info(f"  ✓ Columnas: {len(df_combined.columns)}")
        logger.info(f"  ✓ Período: {df_combined.index.min()} a {df_combined.index.max()}")
        
        return df_combined
    
    def calcular_indicadores_tecnicos(self, df, ticker):
        """
        Calcula indicadores técnicos para un índice
        """
        df_copy = df.copy()
        
        # Medias móviles
        df_copy['SMA_20'] = df['Close'].rolling(window=20).mean()
        df_copy['SMA_50'] = df['Close'].rolling(window=50).mean()
        df_copy['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Bandas de Bollinger
        df_copy['BB_Middle'] = df['Close'].rolling(window=20).mean()
        df_copy['BB_Std'] = df['Close'].rolling(window=20).std()
        df_copy['BB_Upper'] = df_copy['BB_Middle'] + (2 * df_copy['BB_Std'])
        df_copy['BB_Lower'] = df_copy['BB_Middle'] - (2 * df_copy['BB_Std'])
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df_copy['RSI'] = 100 - (100 / (1 + rs))
        
        # Volatilidad (desviación estándar de retornos)
        df_copy['Volatility'] = df['Close'].pct_change().rolling(window=30).std()
        
        logger.info(f"  ✓ {ticker}: Indicadores técnicos calculados")
        
        return df_copy
    
    def crear_datasets_procesados(self):
        """
        Crea múltiples datasets procesados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASETS PROCESADOS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "market"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset combinado simple
        df_combined = self.crear_dataset_combinado()
        filepath = processed_dir / f"indices_combinados_{timestamp}.csv"
        df_combined.to_csv(filepath)
        logger.info(f"\n1. ✓ Índices combinados: {filepath.name}")
        
        # 2. Dataset con indicadores técnicos para cada índice
        for ticker, df in self.indices.items():
            df_tech = self.calcular_indicadores_tecnicos(df, ticker)
            filepath = processed_dir / f"{ticker}_indicadores_{timestamp}.csv"
            df_tech.to_csv(filepath)
            logger.info(f"2. ✓ {ticker} con indicadores: {filepath.name}")
        
        # 3. Dataset solo de precios de cierre
        df_precios = pd.DataFrame({
            ticker: df['Close'] 
            for ticker, df in self.indices.items()
        })
        filepath = processed_dir / f"indices_precios_{timestamp}.csv"
        df_precios.to_csv(filepath)
        logger.info(f"\n3. ✓ Solo precios de cierre: {filepath.name}")
        
        # 4. Dataset de retornos diarios
        df_retornos = pd.DataFrame({
            ticker: df['Close'].pct_change() 
            for ticker, df in self.indices.items()
        })
        filepath = processed_dir / f"indices_retornos_{timestamp}.csv"
        df_retornos.to_csv(filepath)
        logger.info(f"4. ✓ Retornos diarios: {filepath.name}")
        
        return {
            'combinado': df_combined,
            'precios': df_precios,
            'retornos': df_retornos
        }
    
    def generar_estadisticas(self):
        """
        Genera estadísticas de los índices
        """
        logger.info("\n" + "="*70)
        logger.info("ESTADÍSTICAS DE ÍNDICES")
        logger.info("="*70)
        
        for ticker, df in self.indices.items():
            precio_inicial = df['Close'].iloc[0]
            precio_final = df['Close'].iloc[-1]
            retorno_total = ((precio_final - precio_inicial) / precio_inicial) * 100
            retorno_anualizado = retorno_total / (len(df) / 252)  # 252 días bursátiles
            
            volatilidad = df['Close'].pct_change().std() * (252 ** 0.5) * 100
            
            logger.info(f"\n{ticker}:")
            logger.info(f"  Período: {df.index.min().date()} → {df.index.max().date()}")
            logger.info(f"  Días: {len(df)}")
            logger.info(f"  Precio inicial: ${precio_inicial:.2f}")
            logger.info(f"  Precio final: ${precio_final:.2f}")
            logger.info(f"  Retorno total: {retorno_total:.2f}%")
            logger.info(f"  Retorno anualizado: {retorno_anualizado:.2f}%")
            logger.info(f"  Volatilidad anualizada: {volatilidad:.2f}%")
            logger.info(f"  Máximo: ${df['Close'].max():.2f}")
            logger.info(f"  Mínimo: ${df['Close'].min():.2f}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("PROCESAMIENTO DE ÍNDICES DE MERCADO")
    logger.info("="*70)
    
    # Crear procesador
    procesador = ProcesadorIndicesMercado()
    
    # Cargar índices
    logger.info("\n1. Cargando datos...")
    procesador.cargar_indices()
    
    if procesador.indices:
        # Crear datasets procesados
        logger.info("\n2. Procesando datasets...")
        datasets = procesador.crear_datasets_procesados()
        
        # Generar estadísticas
        logger.info("\n3. Generando estadísticas...")
        procesador.generar_estadisticas()
        
        logger.info("\n" + "="*70)
        logger.info("✓✓✓ PROCESAMIENTO COMPLETADO ✓✓✓")
        logger.info("="*70)
        logger.info("\nArchivos generados en: data/processed/market/")
        logger.info("\nDatos listos para:")
        logger.info("  - Análisis exploratorio")
        logger.info("  - Correlación con datos económicos")
        logger.info("  - Entrenamiento de modelos")
    else:
        logger.error("No se pudieron cargar los índices")


if __name__ == "__main__":
    main()

Procesa y organiza datos de índices de mercado
Crea datasets listos para entrenamiento
"""
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class ProcesadorIndicesMercado:
    """
    Procesa datos de índices bursátiles
    """
    
    def __init__(self):
        """Inicializa el procesador"""
        self.indices = {}
        logger.info("✓ ProcesadorIndicesMercado inicializado")
    
    def cargar_indices(self, tickers=['SPY', 'QQQ', 'DIA', 'IWM']):
        """
        Carga datos de índices desde archivos CSV
        
        Args:
            tickers: Lista de tickers a cargar
        """
        logger.info(f"Cargando {len(tickers)} índices...")
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        for ticker in tickers:
            # Buscar archivo más reciente
            files = list(RAW_DATA_DIR.glob(f"{ticker}_*.csv"))
            if files:
                latest_file = max(files, key=lambda x: x.stat().st_mtime)
                df = pd.read_csv(latest_file, index_col=0, parse_dates=True)
                self.indices[ticker] = df
                logger.info(f"  ✓ {ticker}: {len(df)} días ({df.index.min()} a {df.index.max()})")
            else:
                logger.warning(f"  ✗ {ticker}: No se encontró archivo")
        
        return self.indices
    
    def crear_dataset_combinado(self):
        """
        Crea un dataset con todos los índices en columnas
        """
        logger.info("\nCreando dataset combinado...")
        
        # Diccionario para almacenar series
        data_dict = {}
        
        for ticker, df in self.indices.items():
            # Agregar precio de cierre
            data_dict[f'{ticker}_Close'] = df['Close']
            # Agregar volumen
            data_dict[f'{ticker}_Volume'] = df['Volume']
            # Calcular retornos diarios
            data_dict[f'{ticker}_Return'] = df['Close'].pct_change()
        
        # Crear DataFrame combinado
        df_combined = pd.DataFrame(data_dict)
        
        logger.info(f"  ✓ Dataset combinado: {df_combined.shape}")
        logger.info(f"  ✓ Columnas: {len(df_combined.columns)}")
        logger.info(f"  ✓ Período: {df_combined.index.min()} a {df_combined.index.max()}")
        
        return df_combined
    
    def calcular_indicadores_tecnicos(self, df, ticker):
        """
        Calcula indicadores técnicos para un índice
        """
        df_copy = df.copy()
        
        # Medias móviles
        df_copy['SMA_20'] = df['Close'].rolling(window=20).mean()
        df_copy['SMA_50'] = df['Close'].rolling(window=50).mean()
        df_copy['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Bandas de Bollinger
        df_copy['BB_Middle'] = df['Close'].rolling(window=20).mean()
        df_copy['BB_Std'] = df['Close'].rolling(window=20).std()
        df_copy['BB_Upper'] = df_copy['BB_Middle'] + (2 * df_copy['BB_Std'])
        df_copy['BB_Lower'] = df_copy['BB_Middle'] - (2 * df_copy['BB_Std'])
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df_copy['RSI'] = 100 - (100 / (1 + rs))
        
        # Volatilidad (desviación estándar de retornos)
        df_copy['Volatility'] = df['Close'].pct_change().rolling(window=30).std()
        
        logger.info(f"  ✓ {ticker}: Indicadores técnicos calculados")
        
        return df_copy
    
    def crear_datasets_procesados(self):
        """
        Crea múltiples datasets procesados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASETS PROCESADOS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "market"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset combinado simple
        df_combined = self.crear_dataset_combinado()
        filepath = processed_dir / f"indices_combinados_{timestamp}.csv"
        df_combined.to_csv(filepath)
        logger.info(f"\n1. ✓ Índices combinados: {filepath.name}")
        
        # 2. Dataset con indicadores técnicos para cada índice
        for ticker, df in self.indices.items():
            df_tech = self.calcular_indicadores_tecnicos(df, ticker)
            filepath = processed_dir / f"{ticker}_indicadores_{timestamp}.csv"
            df_tech.to_csv(filepath)
            logger.info(f"2. ✓ {ticker} con indicadores: {filepath.name}")
        
        # 3. Dataset solo de precios de cierre
        df_precios = pd.DataFrame({
            ticker: df['Close'] 
            for ticker, df in self.indices.items()
        })
        filepath = processed_dir / f"indices_precios_{timestamp}.csv"
        df_precios.to_csv(filepath)
        logger.info(f"\n3. ✓ Solo precios de cierre: {filepath.name}")
        
        # 4. Dataset de retornos diarios
        df_retornos = pd.DataFrame({
            ticker: df['Close'].pct_change() 
            for ticker, df in self.indices.items()
        })
        filepath = processed_dir / f"indices_retornos_{timestamp}.csv"
        df_retornos.to_csv(filepath)
        logger.info(f"4. ✓ Retornos diarios: {filepath.name}")
        
        return {
            'combinado': df_combined,
            'precios': df_precios,
            'retornos': df_retornos
        }
    
    def generar_estadisticas(self):
        """
        Genera estadísticas de los índices
        """
        logger.info("\n" + "="*70)
        logger.info("ESTADÍSTICAS DE ÍNDICES")
        logger.info("="*70)
        
        for ticker, df in self.indices.items():
            precio_inicial = df['Close'].iloc[0]
            precio_final = df['Close'].iloc[-1]
            retorno_total = ((precio_final - precio_inicial) / precio_inicial) * 100
            retorno_anualizado = retorno_total / (len(df) / 252)  # 252 días bursátiles
            
            volatilidad = df['Close'].pct_change().std() * (252 ** 0.5) * 100
            
            logger.info(f"\n{ticker}:")
            logger.info(f"  Período: {df.index.min().date()} → {df.index.max().date()}")
            logger.info(f"  Días: {len(df)}")
            logger.info(f"  Precio inicial: ${precio_inicial:.2f}")
            logger.info(f"  Precio final: ${precio_final:.2f}")
            logger.info(f"  Retorno total: {retorno_total:.2f}%")
            logger.info(f"  Retorno anualizado: {retorno_anualizado:.2f}%")
            logger.info(f"  Volatilidad anualizada: {volatilidad:.2f}%")
            logger.info(f"  Máximo: ${df['Close'].max():.2f}")
            logger.info(f"  Mínimo: ${df['Close'].min():.2f}")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("PROCESAMIENTO DE ÍNDICES DE MERCADO")
    logger.info("="*70)
    
    # Crear procesador
    procesador = ProcesadorIndicesMercado()
    
    # Cargar índices
    logger.info("\n1. Cargando datos...")
    procesador.cargar_indices()
    
    if procesador.indices:
        # Crear datasets procesados
        logger.info("\n2. Procesando datasets...")
        datasets = procesador.crear_datasets_procesados()
        
        # Generar estadísticas
        logger.info("\n3. Generando estadísticas...")
        procesador.generar_estadisticas()
        
        logger.info("\n" + "="*70)
        logger.info("✓✓✓ PROCESAMIENTO COMPLETADO ✓✓✓")
        logger.info("="*70)
        logger.info("\nArchivos generados en: data/processed/market/")
        logger.info("\nDatos listos para:")
        logger.info("  - Análisis exploratorio")
        logger.info("  - Correlación con datos económicos")
        logger.info("  - Entrenamiento de modelos")
    else:
        logger.error("No se pudieron cargar los índices")


if __name__ == "__main__":
    main()



