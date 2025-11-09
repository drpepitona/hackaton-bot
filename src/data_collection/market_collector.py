"""
Recolector de datos del mercado de valores
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, DEFAULT_TICKERS
from src.utils.logger import logger


class MarketCollector:
    """Recolecta datos de mercado usando yfinance"""
    
    def __init__(self):
        """Inicializa el recolector de mercado"""
        logger.info("MarketCollector inicializado correctamente")
    
    def get_stock_data(self, ticker, start_date=None, end_date=None, interval="1d"):
        """
        Obtiene datos históricos de una acción
        
        Args:
            ticker: Símbolo del ticker (ej: 'SPY', 'AAPL')
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            interval: Intervalo de datos (1d, 1h, etc.)
            
        Returns:
            pandas.DataFrame con OHLCV y otros datos
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=365*10)
            
            logger.info(f"Obteniendo datos de {ticker} desde {start_date}...")
            
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date, interval=interval)
            
            if data.empty:
                logger.warning(f"No se obtuvieron datos para {ticker}")
                return None
            
            logger.info(f"✓ Datos de {ticker} obtenidos: {len(data)} registros")
            return data
            
        except Exception as e:
            logger.error(f"Error al obtener datos de {ticker}: {e}")
            return None
    
    def get_multiple_stocks(self, tickers, start_date=None, end_date=None):
        """
        Obtiene datos de múltiples acciones
        
        Args:
            tickers: Lista de símbolos
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Diccionario con DataFrames por cada ticker
        """
        data = {}
        for ticker in tickers:
            df = self.get_stock_data(ticker, start_date, end_date)
            if df is not None:
                data[ticker] = df
        
        logger.info(f"✓ Datos obtenidos para {len(data)}/{len(tickers)} tickers")
        return data
    
    def get_stock_info(self, ticker):
        """
        Obtiene información de la empresa
        
        Args:
            ticker: Símbolo del ticker
            
        Returns:
            Diccionario con información
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            logger.info(f"✓ Información de {ticker} obtenida")
            return info
        except Exception as e:
            logger.error(f"Error al obtener info de {ticker}: {e}")
            return None
    
    def save_data(self, data, ticker, filename=None):
        """
        Guarda los datos en un archivo CSV
        
        Args:
            data: DataFrame a guardar
            ticker: Símbolo del ticker
            filename: Nombre del archivo (opcional)
        """
        if filename is None:
            filename = f"{ticker}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        filepath = RAW_DATA_DIR / filename
        data.to_csv(filepath)
        logger.info(f"✓ Datos de {ticker} guardados en {filepath}")
    
    def collect_default_tickers(self, start_date=None):
        """
        Recolecta datos de los tickers por defecto
        
        Args:
            start_date: Fecha de inicio (por defecto últimos 10 años)
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365*10)
        
        logger.info(f"Recolectando {len(DEFAULT_TICKERS)} tickers desde {start_date}")
        data = self.get_multiple_stocks(DEFAULT_TICKERS, start_date=start_date)
        
        # Guardar cada ticker
        for ticker, df in data.items():
            self.save_data(df, ticker)
        
        return data


def main():
    """Función principal para ejecutar el recolector"""
    try:
        collector = MarketCollector()
        data = collector.collect_default_tickers()
        
        logger.info("\n" + "="*50)
        logger.info("RESUMEN DE DATOS DE MERCADO")
        logger.info("="*50)
        
        for ticker, df in data.items():
            logger.info(f"\n{ticker}:")
            logger.info(f"  Período: {df.index.min()} a {df.index.max()}")
            logger.info(f"  Total de días: {len(df)}")
            logger.info(f"  Columnas: {list(df.columns)}")
            logger.info(f"  Precio final: ${df['Close'].iloc[-1]:.2f}")
        
        logger.info("\n✓ Recolección de mercado completada exitosamente!")
        
    except Exception as e:
        logger.error(f"Error en la recolección de mercado: {e}")
        raise


if __name__ == "__main__":
    main()




