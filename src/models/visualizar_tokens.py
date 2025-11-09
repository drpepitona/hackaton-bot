"""
Visualización de Tokens Multi-Asset
Muestra gráficamente el impacto histórico de cada categoría
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger


def visualizar_tokens():
    """Visualiza los tokens calculados"""
    logger.info("="*70)
    logger.info("VISUALIZACIÓN DE TOKENS")
    logger.info("="*70)
    
    # Cargar tokens
    landau_dir = PROCESSED_DATA_DIR / "landau"
    token_files = list(landau_dir.glob("tokens_por_asset_*.csv"))
    
    if not token_files:
        logger.error("No se encontraron tokens calculados")
        return
    
    df = pd.read_csv(token_files[0])
    logger.info(f"✓ Tokens cargados: {len(df)} categorías")
    
    # Ordenar por token
    df = df.sort_values('token', ascending=True)
    
    # Crear visualización
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # 1. Tokens por categoría (barras horizontales)
    ax1 = axes[0, 0]
    colors = plt.cm.RdYlGn(df['token'] / df['token'].max())
    bars = ax1.barh(df['categoria'], df['token'], color=colors, edgecolor='black', linewidth=0.5)
    
    # Añadir valores en las barras
    for i, (token, cat) in enumerate(zip(df['token'], df['categoria'])):
        ax1.text(token + 0.2, i, f'{token:.2f}', va='center', fontsize=9)
    
    ax1.axvline(x=5, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Token medio')
    ax1.set_xlabel('Token (Peso)', fontsize=12, fontweight='bold')
    ax1.set_title('Tokens por Categoría (Basados en Impacto Histórico Real)', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 11)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='x')
    
    # 2. Impacto promedio vs Token
    ax2 = axes[0, 1]
    scatter = ax2.scatter(df['impacto_promedio']*100, df['token'], 
                          s=df['num_eventos']/5, alpha=0.6, 
                          c=df['token'], cmap='RdYlGn', edgecolors='black', linewidth=1)
    
    # Añadir labels para los más importantes
    for _, row in df.nlargest(8, 'token').iterrows():
        ax2.annotate(row['categoria'], 
                    (row['impacto_promedio']*100, row['token']),
                    fontsize=8, alpha=0.7)
    
    ax2.set_xlabel('Impacto Promedio en S&P 500 (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Token Asignado', fontsize=12, fontweight='bold')
    ax2.set_title('Correlación: Impacto Real → Token Asignado', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Token', rotation=270, labelpad=20)
    
    # 3. Número de eventos por categoría
    ax3 = axes[1, 0]
    df_top = df.nlargest(15, 'num_eventos')
    bars3 = ax3.barh(df_top['categoria'], df_top['num_eventos'], 
                     color=plt.cm.Blues(df_top['num_eventos'] / df_top['num_eventos'].max()),
                     edgecolor='black', linewidth=0.5)
    
    ax3.set_xlabel('Número de Eventos Medidos', fontsize=12, fontweight='bold')
    ax3.set_title('Eventos Históricos por Categoría (Top 15)', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # 4. Cobertura (% de noticias con impacto medido)
    ax4 = axes[1, 1]
    df_top_cov = df.nlargest(15, 'cobertura_pct')
    bars4 = ax4.barh(df_top_cov['categoria'], df_top_cov['cobertura_pct'],
                     color=plt.cm.Greens(df_top_cov['cobertura_pct'] / 100),
                     edgecolor='black', linewidth=0.5)
    
    for i, (cob, cat) in enumerate(zip(df_top_cov['cobertura_pct'], df_top_cov['categoria'])):
        ax4.text(cob + 1, i, f'{cob:.1f}%', va='center', fontsize=9)
    
    ax4.set_xlabel('Cobertura (% noticias con impacto medido)', fontsize=12, fontweight='bold')
    ax4.set_title('Cobertura de Eventos (Top 15)', fontsize=14, fontweight='bold')
    ax4.set_xlim(0, 70)
    ax4.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    # Guardar
    output_file = landau_dir / "tokens_visualizacion.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"\n✓ Visualización guardada: {output_file}")
    
    plt.show()
    
    return df


def generar_reporte_tokens(df):
    """Genera reporte detallado de tokens"""
    logger.info("\n" + "="*70)
    logger.info("REPORTE DETALLADO DE TOKENS")
    logger.info("="*70)
    
    output = []
    output.append("# 📊 TOKENS CALCULADOS - IMPACTO REAL EN S&P 500")
    output.append("")
    output.append("## Basado en 123,326 noticias históricas (2008-2016)")
    output.append("")
    output.append("| Rank | Categoría | Token | Impacto Avg | Impacto Max | Eventos | Cobertura |")
    output.append("|------|-----------|-------|-------------|-------------|---------|-----------|")
    
    for i, (_, row) in enumerate(df.sort_values('token', ascending=False).iterrows(), 1):
        output.append(f"| {i:2d} | {row['categoria']:25s} | {row['token']:5.2f} | "
                     f"{row['impacto_promedio']*100:6.3f}% | {row['impacto_max']*100:6.3f}% | "
                     f"{row['num_eventos']:5d} | {row['cobertura_pct']:5.1f}% |")
    
    output.append("")
    output.append("## 🔍 INTERPRETACIÓN")
    output.append("")
    output.append("### Token > 8.0 (Impacto EXTREMO):")
    top_extreme = df[df['token'] >= 8.0]
    if len(top_extreme) > 0:
        for _, row in top_extreme.iterrows():
            output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    output.append("")
    output.append("### Token 6.0-8.0 (Impacto ALTO):")
    top_high = df[(df['token'] >= 6.0) & (df['token'] < 8.0)]
    for _, row in top_high.iterrows():
        output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    output.append("")
    output.append("### Token 4.0-6.0 (Impacto MEDIO):")
    top_medium = df[(df['token'] >= 4.0) & (df['token'] < 6.0)]
    for _, row in top_medium.iterrows():
        output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    output.append("")
    output.append("### Token < 4.0 (Impacto BAJO):")
    top_low = df[df['token'] < 4.0]
    for _, row in top_low.iterrows():
        output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    # Guardar reporte
    output_text = "\n".join(output)
    output_file = PROCESSED_DATA_DIR / "landau" / "REPORTE_TOKENS.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    logger.info(f"✓ Reporte guardado: {output_file}")
    
    return output_text


if __name__ == "__main__":
    df = visualizar_tokens()
    if df is not None:
        reporte = generar_reporte_tokens(df)
        print("\n" + reporte)

Visualización de Tokens Multi-Asset
Muestra gráficamente el impacto histórico de cada categoría
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import PROCESSED_DATA_DIR
from src.utils.logger import logger


def visualizar_tokens():
    """Visualiza los tokens calculados"""
    logger.info("="*70)
    logger.info("VISUALIZACIÓN DE TOKENS")
    logger.info("="*70)
    
    # Cargar tokens
    landau_dir = PROCESSED_DATA_DIR / "landau"
    token_files = list(landau_dir.glob("tokens_por_asset_*.csv"))
    
    if not token_files:
        logger.error("No se encontraron tokens calculados")
        return
    
    df = pd.read_csv(token_files[0])
    logger.info(f"✓ Tokens cargados: {len(df)} categorías")
    
    # Ordenar por token
    df = df.sort_values('token', ascending=True)
    
    # Crear visualización
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    
    # 1. Tokens por categoría (barras horizontales)
    ax1 = axes[0, 0]
    colors = plt.cm.RdYlGn(df['token'] / df['token'].max())
    bars = ax1.barh(df['categoria'], df['token'], color=colors, edgecolor='black', linewidth=0.5)
    
    # Añadir valores en las barras
    for i, (token, cat) in enumerate(zip(df['token'], df['categoria'])):
        ax1.text(token + 0.2, i, f'{token:.2f}', va='center', fontsize=9)
    
    ax1.axvline(x=5, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Token medio')
    ax1.set_xlabel('Token (Peso)', fontsize=12, fontweight='bold')
    ax1.set_title('Tokens por Categoría (Basados en Impacto Histórico Real)', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 11)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='x')
    
    # 2. Impacto promedio vs Token
    ax2 = axes[0, 1]
    scatter = ax2.scatter(df['impacto_promedio']*100, df['token'], 
                          s=df['num_eventos']/5, alpha=0.6, 
                          c=df['token'], cmap='RdYlGn', edgecolors='black', linewidth=1)
    
    # Añadir labels para los más importantes
    for _, row in df.nlargest(8, 'token').iterrows():
        ax2.annotate(row['categoria'], 
                    (row['impacto_promedio']*100, row['token']),
                    fontsize=8, alpha=0.7)
    
    ax2.set_xlabel('Impacto Promedio en S&P 500 (%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Token Asignado', fontsize=12, fontweight='bold')
    ax2.set_title('Correlación: Impacto Real → Token Asignado', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Token', rotation=270, labelpad=20)
    
    # 3. Número de eventos por categoría
    ax3 = axes[1, 0]
    df_top = df.nlargest(15, 'num_eventos')
    bars3 = ax3.barh(df_top['categoria'], df_top['num_eventos'], 
                     color=plt.cm.Blues(df_top['num_eventos'] / df_top['num_eventos'].max()),
                     edgecolor='black', linewidth=0.5)
    
    ax3.set_xlabel('Número de Eventos Medidos', fontsize=12, fontweight='bold')
    ax3.set_title('Eventos Históricos por Categoría (Top 15)', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # 4. Cobertura (% de noticias con impacto medido)
    ax4 = axes[1, 1]
    df_top_cov = df.nlargest(15, 'cobertura_pct')
    bars4 = ax4.barh(df_top_cov['categoria'], df_top_cov['cobertura_pct'],
                     color=plt.cm.Greens(df_top_cov['cobertura_pct'] / 100),
                     edgecolor='black', linewidth=0.5)
    
    for i, (cob, cat) in enumerate(zip(df_top_cov['cobertura_pct'], df_top_cov['categoria'])):
        ax4.text(cob + 1, i, f'{cob:.1f}%', va='center', fontsize=9)
    
    ax4.set_xlabel('Cobertura (% noticias con impacto medido)', fontsize=12, fontweight='bold')
    ax4.set_title('Cobertura de Eventos (Top 15)', fontsize=14, fontweight='bold')
    ax4.set_xlim(0, 70)
    ax4.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    # Guardar
    output_file = landau_dir / "tokens_visualizacion.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"\n✓ Visualización guardada: {output_file}")
    
    plt.show()
    
    return df


def generar_reporte_tokens(df):
    """Genera reporte detallado de tokens"""
    logger.info("\n" + "="*70)
    logger.info("REPORTE DETALLADO DE TOKENS")
    logger.info("="*70)
    
    output = []
    output.append("# 📊 TOKENS CALCULADOS - IMPACTO REAL EN S&P 500")
    output.append("")
    output.append("## Basado en 123,326 noticias históricas (2008-2016)")
    output.append("")
    output.append("| Rank | Categoría | Token | Impacto Avg | Impacto Max | Eventos | Cobertura |")
    output.append("|------|-----------|-------|-------------|-------------|---------|-----------|")
    
    for i, (_, row) in enumerate(df.sort_values('token', ascending=False).iterrows(), 1):
        output.append(f"| {i:2d} | {row['categoria']:25s} | {row['token']:5.2f} | "
                     f"{row['impacto_promedio']*100:6.3f}% | {row['impacto_max']*100:6.3f}% | "
                     f"{row['num_eventos']:5d} | {row['cobertura_pct']:5.1f}% |")
    
    output.append("")
    output.append("## 🔍 INTERPRETACIÓN")
    output.append("")
    output.append("### Token > 8.0 (Impacto EXTREMO):")
    top_extreme = df[df['token'] >= 8.0]
    if len(top_extreme) > 0:
        for _, row in top_extreme.iterrows():
            output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    output.append("")
    output.append("### Token 6.0-8.0 (Impacto ALTO):")
    top_high = df[(df['token'] >= 6.0) & (df['token'] < 8.0)]
    for _, row in top_high.iterrows():
        output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    output.append("")
    output.append("### Token 4.0-6.0 (Impacto MEDIO):")
    top_medium = df[(df['token'] >= 4.0) & (df['token'] < 6.0)]
    for _, row in top_medium.iterrows():
        output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    output.append("")
    output.append("### Token < 4.0 (Impacto BAJO):")
    top_low = df[df['token'] < 4.0]
    for _, row in top_low.iterrows():
        output.append(f"- **{row['categoria']}**: {row['impacto_promedio']*100:.3f}% promedio")
    
    # Guardar reporte
    output_text = "\n".join(output)
    output_file = PROCESSED_DATA_DIR / "landau" / "REPORTE_TOKENS.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    logger.info(f"✓ Reporte guardado: {output_file}")
    
    return output_text


if __name__ == "__main__":
    df = visualizar_tokens()
    if df is not None:
        reporte = generar_reporte_tokens(df)
        print("\n" + reporte)



