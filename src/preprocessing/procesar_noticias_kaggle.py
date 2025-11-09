"""
Procesa datasets de noticias de Kaggle
Convierte a formato estándar para el modelo de Landau
"""
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR
from src.utils.logger import logger


def procesar_combined_news_djia():
    """
    Procesa Combined_News_DJIA.csv
    Contiene 25 headlines por día (2008-2016)
    Label: 0=bajista, 1=alcista
    """
    logger.info("="*70)
    logger.info("PROCESANDO: Combined_News_DJIA.csv")
    logger.info("="*70)
    
    filepath = RAW_DATA_DIR / "Kanggle" / "Combined_News_DJIA.csv"
    
    try:
        df = pd.read_csv(filepath)
        logger.info(f"  ✓ Archivo cargado: {len(df)} filas")
        logger.info(f"  ✓ Columnas: {list(df.columns[:5])}...")
        
        # Convertir a formato largo (una noticia por fila)
        noticias_list = []
        
        for _, row in df.iterrows():
            fecha = pd.to_datetime(row['Date'])
            label_dia = row['Label']  # 0=bajista, 1=alcista
            
            # Extraer las 25 noticias del día
            for i in range(1, 26):
                col_name = f'Top{i}'
                if col_name in row and pd.notna(row[col_name]):
                    headline = str(row[col_name])
                    
                    # Limpiar el formato b'...'
                    if headline.startswith("b'") or headline.startswith('b"'):
                        headline = headline[2:-1]
                    
                    noticias_list.append({
                        'fecha': fecha,
                        'titulo': headline,
                        'descripcion': '',
                        'fuente': f'DJIA_Top{i}',
                        'label_dia': label_dia,
                        'categoria': 'financial'
                    })
        
        df_procesado = pd.DataFrame(noticias_list)
        
        logger.info(f"\n  ✓ Noticias procesadas: {len(df_procesado)}")
        logger.info(f"  ✓ Período: {df_procesado['fecha'].min()} a {df_procesado['fecha'].max()}")
        logger.info(f"  ✓ Noticias por día: ~25")
        
        # Estadísticas
        dias_alcistas = df[df['Label'] == 1].shape[0]
        dias_bajistas = df[df['Label'] == 0].shape[0]
        logger.info(f"\n  📊 Distribución original:")
        logger.info(f"     Días alcistas: {dias_alcistas} ({dias_alcistas/len(df)*100:.1f}%)")
        logger.info(f"     Días bajistas: {dias_bajistas} ({dias_bajistas/len(df)*100:.1f}%)")
        
        return df_procesado
        
    except Exception as e:
        logger.error(f"Error procesando Combined_News_DJIA: {e}")
        return None


def procesar_reddit_news():
    """
    Procesa RedditNews.csv
    Contiene noticias de Reddit (2008-2016)
    """
    logger.info("\n" + "="*70)
    logger.info("PROCESANDO: RedditNews.csv")
    logger.info("="*70)
    
    filepath = RAW_DATA_DIR / "Kanggle" / "RedditNews.csv"
    
    try:
        df = pd.read_csv(filepath)
        logger.info(f"  ✓ Archivo cargado: {len(df)} filas")
        logger.info(f"  ✓ Columnas: {list(df.columns)}")
        
        # Convertir a formato estándar
        df_procesado = pd.DataFrame({
            'fecha': pd.to_datetime(df['Date']),
            'titulo': df['News'],
            'descripcion': '',
            'fuente': 'Reddit',
            'categoria': 'social_media'
        })
        
        logger.info(f"\n  ✓ Noticias procesadas: {len(df_procesado)}")
        logger.info(f"  ✓ Período: {df_procesado['fecha'].min()} a {df_procesado['fecha'].max()}")
        
        return df_procesado
        
    except Exception as e:
        logger.error(f"Error procesando RedditNews: {e}")
        return None


def combinar_datasets(df_djia, df_reddit):
    """
    Combina ambos datasets en uno solo
    """
    logger.info("\n" + "="*70)
    logger.info("COMBINANDO DATASETS")
    logger.info("="*70)
    
    # Combinar
    df_combinado = pd.concat([df_djia, df_reddit], ignore_index=True)
    
    # Ordenar por fecha
    df_combinado = df_combinado.sort_values('fecha')
    
    # Eliminar duplicados
    df_combinado = df_combinado.drop_duplicates(subset=['fecha', 'titulo'])
    
    logger.info(f"  ✓ Total de noticias: {len(df_combinado):,}")
    logger.info(f"  ✓ Período completo: {df_combinado['fecha'].min()} a {df_combinado['fecha'].max()}")
    logger.info(f"  ✓ Años de cobertura: {(df_combinado['fecha'].max() - df_combinado['fecha'].min()).days / 365:.1f}")
    
    # Estadísticas
    logger.info(f"\n  📊 Noticias por fuente:")
    for fuente, count in df_combinado['fuente'].value_counts().head(10).items():
        logger.info(f"     {fuente}: {count:,}")
    
    logger.info(f"\n  📅 Noticias por año:")
    df_combinado['año'] = df_combinado['fecha'].dt.year
    for año, count in df_combinado.groupby('año').size().items():
        logger.info(f"     {año}: {count:,} noticias")
    
    return df_combinado


def guardar_dataset_procesado(df):
    """
    Guarda el dataset procesado
    """
    logger.info("\n" + "="*70)
    logger.info("GUARDANDO DATASET PROCESADO")
    logger.info("="*70)
    
    # Crear directorio
    processed_dir = RAW_DATA_DIR.parent / "processed" / "news"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d')
    
    # Guardar dataset completo
    filepath = processed_dir / f"noticias_kaggle_completo_{timestamp}.csv"
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    logger.info(f"  ✓ Guardado: {filepath}")
    logger.info(f"  ✓ Tamaño: {len(df):,} noticias")
    
    # Guardar también solo noticias de alto impacto
    # (filtrar por keywords importantes)
    keywords_alto_impacto = [
        'fed', 'federal reserve', 'interest rate', 'inflation', 
        'unemployment', 'gdp', 'recession', 'crisis', 'crash',
        'ecb', 'central bank', 'oil', 'opec'
    ]
    
    df_alto = df[df['titulo'].str.lower().str.contains('|'.join(keywords_alto_impacto), na=False)]
    
    if len(df_alto) > 0:
        filepath_alto = processed_dir / f"noticias_kaggle_alto_impacto_{timestamp}.csv"
        df_alto.to_csv(filepath_alto, index=False, encoding='utf-8-sig')
        logger.info(f"\n  ✓ Alto impacto: {filepath_alto}")
        logger.info(f"  ✓ Noticias filtradas: {len(df_alto):,} ({len(df_alto)/len(df)*100:.1f}%)")
    
    return filepath


def main():
    """Función principal"""
    logger.info("="*70)
    logger.info("PROCESAMIENTO DE NOTICIAS DE KAGGLE")
    logger.info("="*70)
    logger.info("Datasets: Combined_News_DJIA + RedditNews")
    logger.info("")
    
    # Procesar Combined_News_DJIA
    df_djia = procesar_combined_news_djia()
    
    # Procesar RedditNews
    df_reddit = procesar_reddit_news()
    
    if df_djia is not None and df_reddit is not None:
        # Combinar
        df_combinado = combinar_datasets(df_djia, df_reddit)
        
        # Guardar
        filepath = guardar_dataset_procesado(df_combinado)
        
        logger.info("\n" + "="*70)
        logger.info("✓✓✓ PROCESAMIENTO COMPLETADO ✓✓✓")
        logger.info("="*70)
        logger.info(f"\n📊 Resumen:")
        logger.info(f"  Total de noticias: {len(df_combinado):,}")
        logger.info(f"  Período: {df_combinado['fecha'].min().date()} a {df_combinado['fecha'].max().date()}")
        logger.info(f"  Años: {(df_combinado['fecha'].max() - df_combinado['fecha'].min()).days / 365:.1f}")
        logger.info(f"\n📁 Archivo generado:")
        logger.info(f"  {filepath}")
        logger.info(f"\n🎯 Próximo paso:")
        logger.info(f"  py src/models/landau_phase_predictor.py")
    else:
        logger.error("No se pudieron procesar los datasets")


if __name__ == "__main__":
    main()

