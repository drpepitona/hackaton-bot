"""
Logger configurado para el proyecto
"""
from loguru import logger
import sys
from pathlib import Path

# Configurar logger
log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Remover configuración por defecto
logger.remove()

# Agregar handler para consola
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Agregar handler para archivo
logger.add(
    log_dir / "trading_bot_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

__all__ = ["logger"]




