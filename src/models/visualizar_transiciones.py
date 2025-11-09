"""
Visualización de Transiciones de Fase del Mercado
Muestra gráficamente el parámetro de orden φ y las transiciones
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger


def cargar_parametros_landau():
    """Carga los parámetros de Landau generados"""
    landau_dir = PROCESSED_DATA_DIR / "landau"
    files = list(landau_dir.glob("parametros_landau_historicos_*.csv"))
    
    if not files:
        logger.error("No se encontraron parámetros de Landau")
        logger.info("Ejecuta primero: py src/models/landau_phase_predictor.py")
        return None
    
    latest_file = max(files, key=lambda x: x.stat().st_mtime)
    df = pd.read_csv(latest_file)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    logger.info(f"✓ Parámetros cargados: {len(df)} días")
    logger.info(f"✓ Archivo: {latest_file.name}")
    logger.info(f"✓ Columnas disponibles: {list(df.columns[:10])}")
    
    return df


def visualizar_parametro_orden(df):
    """
    Visualiza la evolución del parámetro de orden φ
    """
    fig, axes = plt.subplots(4, 1, figsize=(18, 16))
    
    # 1. Parámetro de orden φ
    ax1 = axes[0]
    ax1.plot(df['fecha'], df['phi'], label='φ (Parámetro de Orden)', linewidth=2, color='blue')
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # Colorear áreas según φ
    phi_mean = df['phi'].mean()
    ax1.fill_between(df['fecha'], phi_mean, df['phi'], 
                      where=df['phi']>=phi_mean, alpha=0.3, color='green', label='φ > promedio')
    ax1.fill_between(df['fecha'], phi_mean, df['phi'], 
                      where=df['phi']<phi_mean, alpha=0.3, color='red', label='φ < promedio')
    ax1.axhline(y=phi_mean, color='gray', linestyle='--', linewidth=1, alpha=0.7, label=f'φ promedio = {phi_mean:.2f}')
    
    ax1.set_title('Parámetro de Orden φ (Estado Agregado del Mercado)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('φ')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. Transición de fase (Δφ)
    ax2 = axes[1]
    colors = ['green' if x > 0 else 'red' for x in df['delta_phi']]
    ax2.bar(df['fecha'], df['delta_phi'], color=colors, alpha=0.6, width=1)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.axhline(y=2.0, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='Umbral transición (+2.0)')
    ax2.axhline(y=-2.0, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='Umbral transición (-2.0)')
    
    # Marcar transiciones críticas
    transiciones_criticas = df[abs(df['delta_phi']) > 2.0]
    ax2.scatter(transiciones_criticas['fecha'], transiciones_criticas['delta_phi'], 
                c='red', s=100, marker='*', zorder=5, label=f'Transiciones críticas ({len(transiciones_criticas)})')
    
    ax2.set_title('Transiciones de Fase (Δφ = Velocidad de Cambio)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Δφ')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # 3. Temperatura (VIX)
    ax3 = axes[2]
    ax3.plot(df['fecha'], df['vix'], linewidth=2, color='orange', label='Temperatura (VIX)')
    ax3.axhline(y=25, color='red', linestyle='--', linewidth=1, alpha=0.7, label='VIX=25 (Tc crítico)')
    ax3.axhline(y=30, color='darkred', linestyle='--', linewidth=1, alpha=0.7, label='VIX=30 (pánico)')
    ax3.axhline(y=15, color='green', linestyle='--', linewidth=1, alpha=0.7, label='VIX=15 (calma)')
    
    # Colorear según temperatura
    ax3.fill_between(df['fecha'], 0, df['vix'], 
                      where=df['vix']>=30, alpha=0.3, color='darkred', label='Sistema caliente')
    ax3.fill_between(df['fecha'], 0, df['vix'], 
                      where=(df['vix']>=25) & (df['vix']<30), alpha=0.3, color='orange')
    ax3.fill_between(df['fecha'], 0, df['vix'], 
                      where=df['vix']<15, alpha=0.3, color='lightgreen', label='Sistema frío')
    
    ax3.set_title('Temperatura del Sistema (VIX)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('VIX (Temperatura)')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # 4. Retornos del S&P 500
    ax4 = axes[3]
    ax4.plot(df['fecha'], df['sp500_return_1d'].cumsum()*100, linewidth=2, color='purple', label='Retorno acumulado 1d (%)')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # Marcar transiciones en el gráfico de retornos
    transiciones_alcistas = df[(df['delta_phi'] > 2.0)]
    transiciones_bajistas = df[(df['delta_phi'] < -2.0)]
    
    for _, row in transiciones_alcistas.iterrows():
        ax4.axvline(x=row['fecha'], color='green', alpha=0.2, linestyle='--')
    for _, row in transiciones_bajistas.iterrows():
        ax4.axvline(x=row['fecha'], color='red', alpha=0.2, linestyle='--')
    
    ax4.set_title('Retorno Acumulado S&P 500 con Transiciones de Fase Marcadas', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Fecha')
    ax4.set_ylabel('Retorno Acumulado (%)')
    ax4.legend(loc='upper left')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Guardar
    output_dir = PROCESSED_DATA_DIR / "landau"
    output_file = output_dir / "landau_transiciones_fase.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"\n✓ Gráfica guardada: {output_file}")
    
    plt.show()


def visualizar_precision_por_horizonte(df):
    """
    Visualiza la precisión del modelo por horizonte temporal
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Retornos reales 1 día
    ax1 = axes[0, 0]
    df_1d = df[df['sp500_return_1d'].notna()]
    colors_1d = ['green' if x > 0 else 'red' for x in df_1d['sp500_return_1d']]
    ax1.scatter(df_1d['fecha'], df_1d['sp500_return_1d']*100, c=colors_1d, alpha=0.6, s=10)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax1.set_title('Retornos Reales S&P 500 - 1 Día', fontweight='bold')
    ax1.set_ylabel('Retorno (%)')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Retornos reales 7 días
    ax2 = axes[0, 1]
    df_7d = df[df['sp500_return_7d'].notna()]
    colors_7d = ['green' if x > 0 else 'red' for x in df_7d['sp500_return_7d']]
    ax2.scatter(df_7d['fecha'], df_7d['sp500_return_7d']*100, c=colors_7d, alpha=0.6, s=10)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_title('Retornos Reales S&P 500 - 7 Días', fontweight='bold')
    ax2.set_ylabel('Retorno (%)')
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Histograma de φ
    ax3 = axes[1, 0]
    ax3.hist(df['phi'], bins=50, alpha=0.7, color='blue', edgecolor='black')
    ax3.axvline(x=df['phi'].mean(), color='red', linestyle='--', linewidth=2, label=f'Media = {df["phi"].mean():.2f}')
    ax3.axvline(x=df['phi'].median(), color='green', linestyle='--', linewidth=2, label=f'Mediana = {df["phi"].median():.2f}')
    ax3.set_title('Distribución del Parámetro de Orden φ', fontweight='bold')
    ax3.set_xlabel('φ (Parámetro de Orden)')
    ax3.set_ylabel('Frecuencia')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Espacio de fases (φ vs Δφ) coloreado por VIX
    ax4 = axes[1, 1]
    scatter = ax4.scatter(df['phi'], df['delta_phi'], 
                          c=df['vix'], cmap='hot', alpha=0.7, s=30, edgecolors='black', linewidth=0.5)
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax4.axvline(x=df['phi'].mean(), color='black', linestyle='-', linewidth=1)
    ax4.axhline(y=2.0, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    ax4.axhline(y=-2.0, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    
    ax4.set_title('Espacio de Fases (φ vs Δφ) - Coloreado por VIX', fontweight='bold')
    ax4.set_xlabel('φ (Estado del Mercado)')
    ax4.set_ylabel('Δφ (Velocidad de Transición)')
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Temperatura (VIX)', rotation=270, labelpad=20)
    ax4.grid(True, alpha=0.3)
    
    # Añadir cuadrantes
    ax4.text(df['phi'].max()*0.7, 3, 'Transición\nAlcista', ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    ax4.text(df['phi'].max()*0.7, -3, 'Transición\nBajista', ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
    
    plt.tight_layout()
    
    # Guardar
    output_dir = PROCESSED_DATA_DIR / "landau"
    output_file = output_dir / "landau_precision_analisis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Gráfica de precisión guardada: {output_file}")
    
    plt.show()


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("VISUALIZACIÓN DE TRANSICIONES DE FASE")
    logger.info("="*70)
    
    # Cargar parámetros
    df = cargar_parametros_landau()
    
    if df is not None:
        logger.info("\n📊 Generando visualizaciones...")
        
        # Visualización 1: Parámetro de orden y transiciones
        logger.info("\n1. Gráfica de transiciones de fase...")
        visualizar_parametro_orden(df)
        
        # Visualización 2: Análisis de precisión
        logger.info("\n2. Análisis de precisión...")
        visualizar_precision_por_horizonte(df)
        
        logger.info("\n" + "="*70)
        logger.info("✓ VISUALIZACIONES COMPLETADAS")
        logger.info("="*70)
    else:
        logger.error("No se pudieron cargar datos")


if __name__ == "__main__":
    main()

