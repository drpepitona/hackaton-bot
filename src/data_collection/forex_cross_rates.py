"""
Calculador de Pares Cruzados (Cross Rates)
Calcula TODOS los pares posibles entre las monedas principales
Ej: EUR/JPY, EUR/CNY, JPY/AUD, etc.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from itertools import combinations
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class ForexCrossRatesCalculator:
    """
    Calcula todos los pares cruzados posibles entre monedas
    A partir de los pares base contra USD
    """
    
    def __init__(self, forex_file=None):
        """
        Inicializa el calculador
        
        Args:
            forex_file: Path al archivo con pares base (opcional)
        """
        self.monedas = ['USD', 'EUR', 'JPY', 'CNY', 'AUD', 'GBP', 'CAD', 'MXN', 'CHF']
        self.pares_base = {}
        self.pares_cruzados = {}
        
        logger.info("✓ ForexCrossRatesCalculator inicializado")
        
        if forex_file:
            self.cargar_pares_base(forex_file)
    
    def cargar_pares_base(self, forex_file=None):
        """
        Carga los pares base desde el archivo de forex
        """
        if forex_file is None:
            # Buscar archivo más reciente
            processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
            files = list(processed_dir.glob("forex_completo_*.csv"))
            
            if not files:
                logger.error("No se encontró archivo de forex")
                return False
            
            forex_file = max(files, key=lambda x: x.stat().st_mtime)
        
        logger.info(f"Cargando pares base desde: {forex_file.name}")
        
        # Cargar datos
        df = pd.read_csv(forex_file, index_col=0, parse_dates=True)
        
        # Mapeo de códigos FRED a monedas
        mapeo_monedas = {
            'DEXJPUS': ('USD', 'JPY'),     # Yen por dólar
            'DEXUSAL': ('USD', 'AUD'),     # Dólar australiano por dólar USA
            'DEXUSEU': ('USD', 'EUR'),     # Dólar USA por euro
            'DEXCHUS': ('USD', 'CNY'),     # Yuan por dólar
            'DEXUSUK': ('USD', 'GBP'),     # Dólar USA por libra
            'DEXCAUS': ('USD', 'CAD'),     # Dólar canadiense por dólar USA
            'DEXMXUS': ('USD', 'MXN'),     # Peso mexicano por dólar
            'DEXSZUS': ('USD', 'CHF'),     # Franco suizo por dólar
        }
        
        # Organizar pares
        for codigo_fred, (base, quote) in mapeo_monedas.items():
            if codigo_fred in df.columns:
                self.pares_base[f'{base}/{quote}'] = df[codigo_fred]
                logger.info(f"  ✓ {base}/{quote} cargado: {len(df[codigo_fred])} días")
        
        logger.info(f"\n✓ Total de pares base cargados: {len(self.pares_base)}")
        
        return True
    
    def calcular_cross_rate(self, moneda1, moneda2, moneda3):
        """
        Calcula un par cruzado usando una moneda intermedia
        
        Ej: EUR/JPY = (USD/JPY) / (USD/EUR)
        
        Args:
            moneda1: Moneda base del par cruzado
            moneda2: Moneda quote del par cruzado
            moneda3: Moneda intermedia (usualmente USD)
            
        Returns:
            pandas.Series con el par cruzado
        """
        # Buscar los pares necesarios
        par1 = f'{moneda3}/{moneda1}'
        par2 = f'{moneda3}/{moneda2}'
        
        # Verificar que existan
        if par1 not in self.pares_base or par2 not in self.pares_base:
            return None
        
        # Calcular el cross rate
        # EUR/JPY = (USD/JPY) / (USD/EUR)
        cross_rate = self.pares_base[par1] / self.pares_base[par2]
        
        return cross_rate
    
    def calcular_todos_pares_cruzados(self):
        """
        Calcula TODOS los pares cruzados posibles
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO TODOS LOS PARES CRUZADOS")
        logger.info("="*70)
        
        # Monedas disponibles (excluyendo USD ya que tenemos todos contra USD)
        monedas_disponibles = set()
        for par in self.pares_base.keys():
            for moneda in par.split('/'):
                if moneda != 'USD':
                    monedas_disponibles.add(moneda)
        
        monedas_list = sorted(list(monedas_disponibles))
        logger.info(f"Monedas disponibles: {', '.join(monedas_list)}")
        logger.info(f"Generando pares cruzados...")
        logger.info("")
        
        # Calcular todos los pares posibles (sin incluir USD)
        pares_calculados = 0
        
        for i, moneda1 in enumerate(monedas_list):
            for moneda2 in monedas_list[i+1:]:
                # Intentar calcular el par cruzado
                cross_rate = self.calcular_cross_rate(moneda1, moneda2, 'USD')
                
                if cross_rate is not None:
                    par_nombre = f'{moneda1}/{moneda2}'
                    self.pares_cruzados[par_nombre] = cross_rate
                    logger.info(f"  ✓ {par_nombre} calculado: última tasa = {cross_rate.iloc[-1]:.4f}")
                    pares_calculados += 1
        
        logger.info(f"\n✓ Total de pares cruzados calculados: {pares_calculados}")
        
        return self.pares_cruzados
    
    def crear_dataset_completo(self):
        """
        Crea un dataset con TODOS los pares: base + cruzados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASET COMPLETO (BASE + CRUZADOS)")
        logger.info("="*70)
        
        # Combinar pares base y cruzados
        todos_pares = {}
        
        # Pares base (contra USD)
        for par, data in self.pares_base.items():
            todos_pares[par] = data
        
        # Pares cruzados
        for par, data in self.pares_cruzados.items():
            todos_pares[par] = data
        
        # Crear DataFrame
        df_completo = pd.DataFrame(todos_pares)
        
        logger.info(f"  ✓ Dataset completo creado")
        logger.info(f"    - Total de pares: {len(df_completo.columns)}")
        logger.info(f"    - Pares base: {len(self.pares_base)}")
        logger.info(f"    - Pares cruzados: {len(self.pares_cruzados)}")
        logger.info(f"    - Días: {len(df_completo)}")
        
        return df_completo
    
    def crear_dataset_principales_5(self):
        """
        Crea dataset SOLO con los 5 pares principales y todos sus cruzados
        """
        logger.info("\n" + "="*70)
        logger.info("DATASET DE 5 MONEDAS PRINCIPALES (USD, EUR, JPY, CNY, AUD)")
        logger.info("="*70)
        
        monedas_principales = ['USD', 'EUR', 'JPY', 'CNY', 'AUD']
        
        # Filtrar solo pares que involucren estas monedas
        pares_principales = {}
        
        for par, data in {**self.pares_base, **self.pares_cruzados}.items():
            mon1, mon2 = par.split('/')
            if mon1 in monedas_principales and mon2 in monedas_principales:
                pares_principales[par] = data
        
        df_principales = pd.DataFrame(pares_principales)
        
        logger.info(f"  ✓ Dataset de 5 monedas creado")
        logger.info(f"    - Total de pares: {len(df_principales.columns)}")
        logger.info(f"    - Monedas: {', '.join(monedas_principales)}")
        
        # Listar los pares
        logger.info(f"\n  Pares incluidos:")
        for par in sorted(df_principales.columns):
            logger.info(f"    - {par}")
        
        return df_principales
    
    def guardar_datasets(self):
        """
        Guarda todos los datasets
        """
        logger.info("\n" + "="*70)
        logger.info("GUARDANDO DATASETS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset completo (todos los pares)
        df_completo = self.crear_dataset_completo()
        filepath = processed_dir / f"forex_todos_pares_{timestamp}.csv"
        df_completo.to_csv(filepath)
        logger.info(f"  ✓ Todos los pares: {filepath.name}")
        logger.info(f"    - {len(df_completo.columns)} pares × {len(df_completo)} días")
        
        # 2. Dataset solo 5 monedas principales
        df_5_monedas = self.crear_dataset_principales_5()
        filepath = processed_dir / f"forex_5_monedas_completo_{timestamp}.csv"
        df_5_monedas.to_csv(filepath)
        logger.info(f"\n  ✓ 5 monedas (completo): {filepath.name}")
        logger.info(f"    - {len(df_5_monedas.columns)} pares × {len(df_5_monedas)} días")
        
        # 3. Solo pares cruzados (sin USD)
        if self.pares_cruzados:
            df_cruzados = pd.DataFrame(self.pares_cruzados)
            filepath = processed_dir / f"forex_cross_rates_{timestamp}.csv"
            df_cruzados.to_csv(filepath)
            logger.info(f"\n  ✓ Solo pares cruzados: {filepath.name}")
            logger.info(f"    - {len(df_cruzados.columns)} pares × {len(df_cruzados)} días")
        
        # 4. Retornos diarios de todos los pares
        df_retornos = df_completo.pct_change()
        df_retornos.columns = [f'{col}_return' for col in df_retornos.columns]
        filepath = processed_dir / f"forex_todos_retornos_{timestamp}.csv"
        df_retornos.to_csv(filepath)
        logger.info(f"\n  ✓ Retornos de todos los pares: {filepath.name}")
        
        return {
            'completo': df_completo,
            '5_monedas': df_5_monedas,
            'cruzados': df_cruzados if self.pares_cruzados else None,
            'retornos': df_retornos
        }
    
    def analizar_correlaciones_completas(self):
        """
        Analiza correlaciones entre TODOS los pares
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS DE CORRELACIONES - TODOS LOS PARES")
        logger.info("="*70)
        
        df_completo = self.crear_dataset_completo()
        correlacion = df_completo.corr()
        
        # Encontrar correlaciones más fuertes
        correlaciones_list = []
        
        for i in range(len(correlacion.columns)):
            for j in range(i+1, len(correlacion.columns)):
                par1 = correlacion.columns[i]
                par2 = correlacion.columns[j]
                corr_value = correlacion.iloc[i, j]
                
                if not np.isnan(corr_value):
                    correlaciones_list.append((par1, par2, corr_value))
        
        # Ordenar por correlación absoluta
        correlaciones_list.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # Mostrar top correlaciones
        logger.info("\nTop 15 correlaciones más fuertes:")
        for i, (par1, par2, corr) in enumerate(correlaciones_list[:15], 1):
            signo = "+" if corr > 0 else ""
            logger.info(f"  {i:2d}. {signo}{corr:.3f} | {par1:12s} ↔ {par2:12s}")
        
        logger.info("\nTop 10 correlaciones más débiles (más independientes):")
        for i, (par1, par2, corr) in enumerate(correlaciones_list[-10:], 1):
            signo = "+" if corr > 0 else ""
            logger.info(f"  {i:2d}. {signo}{corr:.3f} | {par1:12s} ↔ {par2:12s}")
        
        # Guardar matriz de correlación
        processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = processed_dir / f"forex_correlaciones_{timestamp}.csv"
        correlacion.to_csv(filepath)
        logger.info(f"\n  ✓ Matriz de correlación guardada: {filepath.name}")
    
    def generar_reporte_completo(self):
        """
        Genera reporte completo de todos los pares
        """
        logger.info("\n" + "="*70)
        logger.info("REPORTE COMPLETO DE PARES FOREX")
        logger.info("="*70)
        
        total_pares = len(self.pares_base) + len(self.pares_cruzados)
        
        logger.info(f"\nTotal de pares disponibles: {total_pares}")
        logger.info(f"  - Pares base (contra USD): {len(self.pares_base)}")
        logger.info(f"  - Pares cruzados: {len(self.pares_cruzados)}")
        
        # Pares base
        logger.info("\n📊 PARES BASE (contra USD):")
        for par in sorted(self.pares_base.keys()):
            valor = self.pares_base[par].iloc[-1]
            logger.info(f"  {par:12s} = {valor:.4f}")
        
        # Pares cruzados
        if self.pares_cruzados:
            logger.info("\n🔄 PARES CRUZADOS:")
            for par in sorted(self.pares_cruzados.keys()):
                valor = self.pares_cruzados[par].iloc[-1]
                logger.info(f"  {par:12s} = {valor:.4f}")
        
        # Estadísticas por moneda
        logger.info("\n💰 ANÁLISIS POR MONEDA:")
        
        monedas_en_pares = set()
        for par in self.pares_base.keys():
            monedas_en_pares.update(par.split('/'))
        
        for moneda in sorted(monedas_en_pares):
            if moneda != 'USD':
                pares_con_moneda = [p for p in {**self.pares_base, **self.pares_cruzados}.keys() 
                                   if moneda in p.split('/')]
                logger.info(f"  {moneda}: aparece en {len(pares_con_moneda)} pares")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("CALCULADOR DE PARES CRUZADOS (CROSS RATES)")
    logger.info("="*70)
    logger.info("Generando TODOS los pares posibles entre monedas")
    logger.info("")
    
    try:
        # Crear calculador
        calculator = ForexCrossRatesCalculator()
        
        # Cargar pares base
        logger.info("1. Cargando pares base...")
        if not calculator.cargar_pares_base():
            logger.error("No se pudieron cargar pares base")
            logger.info("Ejecuta primero: py src/data_collection/forex_collector.py")
            return
        
        # Calcular pares cruzados
        logger.info("\n2. Calculando pares cruzados...")
        calculator.calcular_todos_pares_cruzados()
        
        # Guardar datasets
        logger.info("\n3. Guardando datasets...")
        datasets = calculator.guardar_datasets()
        
        # Analizar correlaciones
        logger.info("\n4. Analizando correlaciones...")
        calculator.analizar_correlaciones_completas()
        
        # Generar reporte
        logger.info("\n5. Generando reporte...")
        calculator.generar_reporte_completo()
        
        logger.info("\n" + "="*70)
        logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
        logger.info("="*70)
        logger.info("\n📂 Archivos generados en: data/processed/forex/")
        logger.info("\n📊 Archivos clave:")
        logger.info("  1. forex_5_monedas_completo_*.csv    ⭐ TODAS las combinaciones")
        logger.info("  2. forex_cross_rates_*.csv           Solo pares cruzados")
        logger.info("  3. forex_todos_pares_*.csv           Base + Cruzados")
        logger.info("  4. forex_correlaciones_*.csv         Matriz correlación")
        
        logger.info("\n💡 Ejemplos de pares incluidos:")
        logger.info("  Base:     USD/EUR, USD/JPY, USD/CNY, USD/AUD")
        logger.info("  Cruzados: EUR/JPY, EUR/CNY, EUR/AUD, JPY/CNY, JPY/AUD, CNY/AUD")
        logger.info("  Y muchos más...")
        
        logger.info("\n🎯 Estos datos son perfectos para:")
        logger.info("  - Predecir movimientos forex basados en economía")
        logger.info("  - Arbitraje de divisas")
        logger.info("  - Identificar relaciones complejas entre monedas")
        logger.info("  - Entrenar modelos multi-moneda")
        
    except Exception as e:
        logger.error(f"Error en proceso: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()

Calculador de Pares Cruzados (Cross Rates)
Calcula TODOS los pares posibles entre las monedas principales
Ej: EUR/JPY, EUR/CNY, JPY/AUD, etc.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from itertools import combinations
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


class ForexCrossRatesCalculator:
    """
    Calcula todos los pares cruzados posibles entre monedas
    A partir de los pares base contra USD
    """
    
    def __init__(self, forex_file=None):
        """
        Inicializa el calculador
        
        Args:
            forex_file: Path al archivo con pares base (opcional)
        """
        self.monedas = ['USD', 'EUR', 'JPY', 'CNY', 'AUD', 'GBP', 'CAD', 'MXN', 'CHF']
        self.pares_base = {}
        self.pares_cruzados = {}
        
        logger.info("✓ ForexCrossRatesCalculator inicializado")
        
        if forex_file:
            self.cargar_pares_base(forex_file)
    
    def cargar_pares_base(self, forex_file=None):
        """
        Carga los pares base desde el archivo de forex
        """
        if forex_file is None:
            # Buscar archivo más reciente
            processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
            files = list(processed_dir.glob("forex_completo_*.csv"))
            
            if not files:
                logger.error("No se encontró archivo de forex")
                return False
            
            forex_file = max(files, key=lambda x: x.stat().st_mtime)
        
        logger.info(f"Cargando pares base desde: {forex_file.name}")
        
        # Cargar datos
        df = pd.read_csv(forex_file, index_col=0, parse_dates=True)
        
        # Mapeo de códigos FRED a monedas
        mapeo_monedas = {
            'DEXJPUS': ('USD', 'JPY'),     # Yen por dólar
            'DEXUSAL': ('USD', 'AUD'),     # Dólar australiano por dólar USA
            'DEXUSEU': ('USD', 'EUR'),     # Dólar USA por euro
            'DEXCHUS': ('USD', 'CNY'),     # Yuan por dólar
            'DEXUSUK': ('USD', 'GBP'),     # Dólar USA por libra
            'DEXCAUS': ('USD', 'CAD'),     # Dólar canadiense por dólar USA
            'DEXMXUS': ('USD', 'MXN'),     # Peso mexicano por dólar
            'DEXSZUS': ('USD', 'CHF'),     # Franco suizo por dólar
        }
        
        # Organizar pares
        for codigo_fred, (base, quote) in mapeo_monedas.items():
            if codigo_fred in df.columns:
                self.pares_base[f'{base}/{quote}'] = df[codigo_fred]
                logger.info(f"  ✓ {base}/{quote} cargado: {len(df[codigo_fred])} días")
        
        logger.info(f"\n✓ Total de pares base cargados: {len(self.pares_base)}")
        
        return True
    
    def calcular_cross_rate(self, moneda1, moneda2, moneda3):
        """
        Calcula un par cruzado usando una moneda intermedia
        
        Ej: EUR/JPY = (USD/JPY) / (USD/EUR)
        
        Args:
            moneda1: Moneda base del par cruzado
            moneda2: Moneda quote del par cruzado
            moneda3: Moneda intermedia (usualmente USD)
            
        Returns:
            pandas.Series con el par cruzado
        """
        # Buscar los pares necesarios
        par1 = f'{moneda3}/{moneda1}'
        par2 = f'{moneda3}/{moneda2}'
        
        # Verificar que existan
        if par1 not in self.pares_base or par2 not in self.pares_base:
            return None
        
        # Calcular el cross rate
        # EUR/JPY = (USD/JPY) / (USD/EUR)
        cross_rate = self.pares_base[par1] / self.pares_base[par2]
        
        return cross_rate
    
    def calcular_todos_pares_cruzados(self):
        """
        Calcula TODOS los pares cruzados posibles
        """
        logger.info("\n" + "="*70)
        logger.info("CALCULANDO TODOS LOS PARES CRUZADOS")
        logger.info("="*70)
        
        # Monedas disponibles (excluyendo USD ya que tenemos todos contra USD)
        monedas_disponibles = set()
        for par in self.pares_base.keys():
            for moneda in par.split('/'):
                if moneda != 'USD':
                    monedas_disponibles.add(moneda)
        
        monedas_list = sorted(list(monedas_disponibles))
        logger.info(f"Monedas disponibles: {', '.join(monedas_list)}")
        logger.info(f"Generando pares cruzados...")
        logger.info("")
        
        # Calcular todos los pares posibles (sin incluir USD)
        pares_calculados = 0
        
        for i, moneda1 in enumerate(monedas_list):
            for moneda2 in monedas_list[i+1:]:
                # Intentar calcular el par cruzado
                cross_rate = self.calcular_cross_rate(moneda1, moneda2, 'USD')
                
                if cross_rate is not None:
                    par_nombre = f'{moneda1}/{moneda2}'
                    self.pares_cruzados[par_nombre] = cross_rate
                    logger.info(f"  ✓ {par_nombre} calculado: última tasa = {cross_rate.iloc[-1]:.4f}")
                    pares_calculados += 1
        
        logger.info(f"\n✓ Total de pares cruzados calculados: {pares_calculados}")
        
        return self.pares_cruzados
    
    def crear_dataset_completo(self):
        """
        Crea un dataset con TODOS los pares: base + cruzados
        """
        logger.info("\n" + "="*70)
        logger.info("CREANDO DATASET COMPLETO (BASE + CRUZADOS)")
        logger.info("="*70)
        
        # Combinar pares base y cruzados
        todos_pares = {}
        
        # Pares base (contra USD)
        for par, data in self.pares_base.items():
            todos_pares[par] = data
        
        # Pares cruzados
        for par, data in self.pares_cruzados.items():
            todos_pares[par] = data
        
        # Crear DataFrame
        df_completo = pd.DataFrame(todos_pares)
        
        logger.info(f"  ✓ Dataset completo creado")
        logger.info(f"    - Total de pares: {len(df_completo.columns)}")
        logger.info(f"    - Pares base: {len(self.pares_base)}")
        logger.info(f"    - Pares cruzados: {len(self.pares_cruzados)}")
        logger.info(f"    - Días: {len(df_completo)}")
        
        return df_completo
    
    def crear_dataset_principales_5(self):
        """
        Crea dataset SOLO con los 5 pares principales y todos sus cruzados
        """
        logger.info("\n" + "="*70)
        logger.info("DATASET DE 5 MONEDAS PRINCIPALES (USD, EUR, JPY, CNY, AUD)")
        logger.info("="*70)
        
        monedas_principales = ['USD', 'EUR', 'JPY', 'CNY', 'AUD']
        
        # Filtrar solo pares que involucren estas monedas
        pares_principales = {}
        
        for par, data in {**self.pares_base, **self.pares_cruzados}.items():
            mon1, mon2 = par.split('/')
            if mon1 in monedas_principales and mon2 in monedas_principales:
                pares_principales[par] = data
        
        df_principales = pd.DataFrame(pares_principales)
        
        logger.info(f"  ✓ Dataset de 5 monedas creado")
        logger.info(f"    - Total de pares: {len(df_principales.columns)}")
        logger.info(f"    - Monedas: {', '.join(monedas_principales)}")
        
        # Listar los pares
        logger.info(f"\n  Pares incluidos:")
        for par in sorted(df_principales.columns):
            logger.info(f"    - {par}")
        
        return df_principales
    
    def guardar_datasets(self):
        """
        Guarda todos los datasets
        """
        logger.info("\n" + "="*70)
        logger.info("GUARDANDO DATASETS")
        logger.info("="*70)
        
        # Crear directorio
        processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # 1. Dataset completo (todos los pares)
        df_completo = self.crear_dataset_completo()
        filepath = processed_dir / f"forex_todos_pares_{timestamp}.csv"
        df_completo.to_csv(filepath)
        logger.info(f"  ✓ Todos los pares: {filepath.name}")
        logger.info(f"    - {len(df_completo.columns)} pares × {len(df_completo)} días")
        
        # 2. Dataset solo 5 monedas principales
        df_5_monedas = self.crear_dataset_principales_5()
        filepath = processed_dir / f"forex_5_monedas_completo_{timestamp}.csv"
        df_5_monedas.to_csv(filepath)
        logger.info(f"\n  ✓ 5 monedas (completo): {filepath.name}")
        logger.info(f"    - {len(df_5_monedas.columns)} pares × {len(df_5_monedas)} días")
        
        # 3. Solo pares cruzados (sin USD)
        if self.pares_cruzados:
            df_cruzados = pd.DataFrame(self.pares_cruzados)
            filepath = processed_dir / f"forex_cross_rates_{timestamp}.csv"
            df_cruzados.to_csv(filepath)
            logger.info(f"\n  ✓ Solo pares cruzados: {filepath.name}")
            logger.info(f"    - {len(df_cruzados.columns)} pares × {len(df_cruzados)} días")
        
        # 4. Retornos diarios de todos los pares
        df_retornos = df_completo.pct_change()
        df_retornos.columns = [f'{col}_return' for col in df_retornos.columns]
        filepath = processed_dir / f"forex_todos_retornos_{timestamp}.csv"
        df_retornos.to_csv(filepath)
        logger.info(f"\n  ✓ Retornos de todos los pares: {filepath.name}")
        
        return {
            'completo': df_completo,
            '5_monedas': df_5_monedas,
            'cruzados': df_cruzados if self.pares_cruzados else None,
            'retornos': df_retornos
        }
    
    def analizar_correlaciones_completas(self):
        """
        Analiza correlaciones entre TODOS los pares
        """
        logger.info("\n" + "="*70)
        logger.info("ANÁLISIS DE CORRELACIONES - TODOS LOS PARES")
        logger.info("="*70)
        
        df_completo = self.crear_dataset_completo()
        correlacion = df_completo.corr()
        
        # Encontrar correlaciones más fuertes
        correlaciones_list = []
        
        for i in range(len(correlacion.columns)):
            for j in range(i+1, len(correlacion.columns)):
                par1 = correlacion.columns[i]
                par2 = correlacion.columns[j]
                corr_value = correlacion.iloc[i, j]
                
                if not np.isnan(corr_value):
                    correlaciones_list.append((par1, par2, corr_value))
        
        # Ordenar por correlación absoluta
        correlaciones_list.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # Mostrar top correlaciones
        logger.info("\nTop 15 correlaciones más fuertes:")
        for i, (par1, par2, corr) in enumerate(correlaciones_list[:15], 1):
            signo = "+" if corr > 0 else ""
            logger.info(f"  {i:2d}. {signo}{corr:.3f} | {par1:12s} ↔ {par2:12s}")
        
        logger.info("\nTop 10 correlaciones más débiles (más independientes):")
        for i, (par1, par2, corr) in enumerate(correlaciones_list[-10:], 1):
            signo = "+" if corr > 0 else ""
            logger.info(f"  {i:2d}. {signo}{corr:.3f} | {par1:12s} ↔ {par2:12s}")
        
        # Guardar matriz de correlación
        processed_dir = RAW_DATA_DIR.parent / "processed" / "forex"
        timestamp = datetime.now().strftime('%Y%m%d')
        filepath = processed_dir / f"forex_correlaciones_{timestamp}.csv"
        correlacion.to_csv(filepath)
        logger.info(f"\n  ✓ Matriz de correlación guardada: {filepath.name}")
    
    def generar_reporte_completo(self):
        """
        Genera reporte completo de todos los pares
        """
        logger.info("\n" + "="*70)
        logger.info("REPORTE COMPLETO DE PARES FOREX")
        logger.info("="*70)
        
        total_pares = len(self.pares_base) + len(self.pares_cruzados)
        
        logger.info(f"\nTotal de pares disponibles: {total_pares}")
        logger.info(f"  - Pares base (contra USD): {len(self.pares_base)}")
        logger.info(f"  - Pares cruzados: {len(self.pares_cruzados)}")
        
        # Pares base
        logger.info("\n📊 PARES BASE (contra USD):")
        for par in sorted(self.pares_base.keys()):
            valor = self.pares_base[par].iloc[-1]
            logger.info(f"  {par:12s} = {valor:.4f}")
        
        # Pares cruzados
        if self.pares_cruzados:
            logger.info("\n🔄 PARES CRUZADOS:")
            for par in sorted(self.pares_cruzados.keys()):
                valor = self.pares_cruzados[par].iloc[-1]
                logger.info(f"  {par:12s} = {valor:.4f}")
        
        # Estadísticas por moneda
        logger.info("\n💰 ANÁLISIS POR MONEDA:")
        
        monedas_en_pares = set()
        for par in self.pares_base.keys():
            monedas_en_pares.update(par.split('/'))
        
        for moneda in sorted(monedas_en_pares):
            if moneda != 'USD':
                pares_con_moneda = [p for p in {**self.pares_base, **self.pares_cruzados}.keys() 
                                   if moneda in p.split('/')]
                logger.info(f"  {moneda}: aparece en {len(pares_con_moneda)} pares")


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("CALCULADOR DE PARES CRUZADOS (CROSS RATES)")
    logger.info("="*70)
    logger.info("Generando TODOS los pares posibles entre monedas")
    logger.info("")
    
    try:
        # Crear calculador
        calculator = ForexCrossRatesCalculator()
        
        # Cargar pares base
        logger.info("1. Cargando pares base...")
        if not calculator.cargar_pares_base():
            logger.error("No se pudieron cargar pares base")
            logger.info("Ejecuta primero: py src/data_collection/forex_collector.py")
            return
        
        # Calcular pares cruzados
        logger.info("\n2. Calculando pares cruzados...")
        calculator.calcular_todos_pares_cruzados()
        
        # Guardar datasets
        logger.info("\n3. Guardando datasets...")
        datasets = calculator.guardar_datasets()
        
        # Analizar correlaciones
        logger.info("\n4. Analizando correlaciones...")
        calculator.analizar_correlaciones_completas()
        
        # Generar reporte
        logger.info("\n5. Generando reporte...")
        calculator.generar_reporte_completo()
        
        logger.info("\n" + "="*70)
        logger.info("✓✓✓ PROCESO COMPLETADO EXITOSAMENTE ✓✓✓")
        logger.info("="*70)
        logger.info("\n📂 Archivos generados en: data/processed/forex/")
        logger.info("\n📊 Archivos clave:")
        logger.info("  1. forex_5_monedas_completo_*.csv    ⭐ TODAS las combinaciones")
        logger.info("  2. forex_cross_rates_*.csv           Solo pares cruzados")
        logger.info("  3. forex_todos_pares_*.csv           Base + Cruzados")
        logger.info("  4. forex_correlaciones_*.csv         Matriz correlación")
        
        logger.info("\n💡 Ejemplos de pares incluidos:")
        logger.info("  Base:     USD/EUR, USD/JPY, USD/CNY, USD/AUD")
        logger.info("  Cruzados: EUR/JPY, EUR/CNY, EUR/AUD, JPY/CNY, JPY/AUD, CNY/AUD")
        logger.info("  Y muchos más...")
        
        logger.info("\n🎯 Estos datos son perfectos para:")
        logger.info("  - Predecir movimientos forex basados en economía")
        logger.info("  - Arbitraje de divisas")
        logger.info("  - Identificar relaciones complejas entre monedas")
        logger.info("  - Entrenar modelos multi-moneda")
        
    except Exception as e:
        logger.error(f"Error en proceso: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()



