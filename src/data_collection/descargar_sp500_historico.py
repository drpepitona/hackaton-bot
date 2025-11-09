"""
Descargar datos históricos completos del S&P 500
Desde 2000 hasta hoy para tener overlap con las noticias
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger

def descargar_sp500_historico():
    """
    Descarga datos del S&P 500 desde 2000
    """
    logger.info("="*70)
    logger.info("DESCARGANDO DATOS HISTÓRICOS DEL S&P 500")
    logger.info("="*70)
    
    # Descargar desde 2000
    logger.info("\nDescargando SPY (S&P 500 ETF) desde 2000...")
    spy = yf.Ticker("SPY")
    
    # Descargar todo el histórico
    df = spy.history(start="2000-01-01", end=datetime.now().strftime('%Y-%m-%d'))
    
    logger.info(f"✓ Datos descargados: {len(df)} días")
    logger.info(f"✓ Período: {df.index.min()} a {df.index.max()}")
    logger.info(f"✓ Columnas: {list(df.columns)}")
    
    # Guardar
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = RAW_DATA_DIR / f"SPY_historico_completo_{timestamp}.csv"
    df.to_csv(filename)
    
    logger.info(f"\n✓ Guardado: {filename}")
    logger.info(f"✓ Tamaño: {len(df):,} días ({len(df)/252:.1f} años aprox)")
    
    # Estadísticas
    logger.info("\n📊 ESTADÍSTICAS:")
    logger.info(f"  Precio inicial: ${df['Close'].iloc[0]:.2f}")
    logger.info(f"  Precio final:   ${df['Close'].iloc[-1]:.2f}")
    logger.info(f"  Retorno total:  {(df['Close'].iloc[-1]/df['Close'].iloc[0]-1)*100:+.1f}%")
    logger.info(f"  Precio máximo:  ${df['Close'].max():.2f} ({df['Close'].idxmax().date()})")
    logger.info(f"  Precio mínimo:  ${df['Close'].min():.2f} ({df['Close'].idxmin().date()})")
    
    return df


if __name__ == "__main__":
    df = descargar_sp500_historico()
    
    logger.info("\n" + "="*70)
    logger.info("✓ DESCARGA COMPLETADA")
    logger.info("="*70)
    logger.info("\nAhora ejecuta de nuevo: py src/models/landau_multi_asset.py")

Descargar datos históricos completos del S&P 500
Desde 2000 hasta hoy para tener overlap con las noticias
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger

def descargar_sp500_historico():
    """
    Descarga datos del S&P 500 desde 2000
    """
    logger.info("="*70)
    logger.info("DESCARGANDO DATOS HISTÓRICOS DEL S&P 500")
    logger.info("="*70)
    
    # Descargar desde 2000
    logger.info("\nDescargando SPY (S&P 500 ETF) desde 2000...")
    spy = yf.Ticker("SPY")
    
    # Descargar todo el histórico
    df = spy.history(start="2000-01-01", end=datetime.now().strftime('%Y-%m-%d'))
    
    logger.info(f"✓ Datos descargados: {len(df)} días")
    logger.info(f"✓ Período: {df.index.min()} a {df.index.max()}")
    logger.info(f"✓ Columnas: {list(df.columns)}")
    
    # Guardar
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = RAW_DATA_DIR / f"SPY_historico_completo_{timestamp}.csv"
    df.to_csv(filename)
    
    logger.info(f"\n✓ Guardado: {filename}")
    logger.info(f"✓ Tamaño: {len(df):,} días ({len(df)/252:.1f} años aprox)")
    
    # Estadísticas
    logger.info("\n📊 ESTADÍSTICAS:")
    logger.info(f"  Precio inicial: ${df['Close'].iloc[0]:.2f}")
    logger.info(f"  Precio final:   ${df['Close'].iloc[-1]:.2f}")
    logger.info(f"  Retorno total:  {(df['Close'].iloc[-1]/df['Close'].iloc[0]-1)*100:+.1f}%")
    logger.info(f"  Precio máximo:  ${df['Close'].max():.2f} ({df['Close'].idxmax().date()})")
    logger.info(f"  Precio mínimo:  ${df['Close'].min():.2f} ({df['Close'].idxmin().date()})")
    
    return df


if __name__ == "__main__":
    df = descargar_sp500_historico()
    
    logger.info("\n" + "="*70)
    logger.info("✓ DESCARGA COMPLETADA")
    logger.info("="*70)
    logger.info("\nAhora ejecuta de nuevo: py src/models/landau_multi_asset.py")



