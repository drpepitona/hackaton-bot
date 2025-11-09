"""
FINE-TUNING LOCAL EN TU PC
Entrena un modelo con TODOS tus datos: noticias + tokens + mercado
"""
import os
os.environ["WANDB_DISABLED"] = "true"

import sys
from pathlib import Path
import pandas as pd
import torch
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR
from src.utils.logger import logger


def preparar_dataset_completo():
    """
    Crea dataset correlacionando TODOS tus datos
    """
    logger.info("="*70)
    logger.info("PREPARANDO DATASET CON TODOS TUS DATOS")
    logger.info("="*70)
    
    # 1. Cargar tokens
    logger.info("\nCargando tokens...")
    token_files = list(PROCESSED_DATA_DIR.glob("landau/tokens_volatilidad_*.csv"))
    df_tokens = pd.read_csv(token_files[0])
    logger.info(f"✓ Tokens: {len(df_tokens)}")
    
    # 2. Cargar noticias
    logger.info("\nCargando noticias...")
    kaggle_dir = RAW_DATA_DIR / "Kanggle"
    df_news = pd.read_csv(kaggle_dir / "Combined_News_DJIA.csv")
    df_news['Date'] = pd.to_datetime(df_news['Date'])
    logger.info(f"✓ Noticias: {len(df_news)} días")
    
    # 3. Cargar mercado
    logger.info("\nCargando mercado...")
    spy_files = list(RAW_DATA_DIR.glob("SPY_historico_completo_*.csv"))
    df_spy = pd.read_csv(spy_files[0])
    df_spy['Date'] = pd.to_datetime(df_spy['Date'], errors='coerce')
    df_spy['fecha_str'] = [str(d).split()[0] if pd.notna(d) else '' for d in df_spy['Date']]
    
    # Calcular retorno si no existe
    if 'Daily_Return' not in df_spy.columns:
        df_spy['Daily_Return'] = df_spy['Close'].pct_change()
    
    spy_dict = df_spy.set_index('fecha_str')['Daily_Return'].to_dict()
    logger.info(f"✓ Mercado: {len(df_spy)} días")
    
    # 4. Correlacionar
    logger.info("\nCorrelacionando...")
    
    def clasificar(texto):
        t = str(texto).lower()
        if any(k in t for k in ['fed', 'interest rate']): return 'fed_rates'
        if any(k in t for k in ['terror', 'attack']): return 'terrorism'
        if any(k in t for k in ['russia', 'ukraine', 'war']): return 'war_russia'
        if any(k in t for k in ['crisis', 'crash']): return 'financial_crisis'
        if any(k in t for k in ['ecb', 'draghi']): return 'ecb_policy'
        if any(k in t for k in ['oil', 'opec']): return 'oil_supply'
        if any(k in t for k in ['gold']): return 'gold_demand'
        return 'other'
    
    ejemplos = []
    
    for idx, row in df_news.iterrows():
        if idx % 200 == 0:
            logger.info(f"  {idx}/{len(df_news)}")
        
        fecha_str = row['Date'].strftime('%Y-%m-%d')
        retorno = spy_dict.get(fecha_str)
        
        if retorno is None:
            continue
        
        for i in range(1, 26):
            noticia = row.get(f'Top{i}')
            if pd.notna(noticia) and str(noticia).strip():
                cat = clasificar(noticia)
                
                # Buscar token
                token_row = df_tokens[
                    (df_tokens['categoria'] == cat) & 
                    (df_tokens['asset'] == 'SPY')
                ]
                
                if len(token_row) > 0:
                    tk = token_row.iloc[0]
                    
                    texto = f"Analiza: {noticia[:100]}\nRespuesta: SPY {retorno*100:+.2f}%. Token {tk['token']:.1f}/10 ({tk['num_eventos']} eventos). Volatilidad {tk['volatilidad_promedio']*100:.2f}%."
                    
                    ejemplos.append(texto)
    
    logger.info(f"\n✓ Dataset: {len(ejemplos):,} ejemplos correlacionados")
    
    return ejemplos


def entrenar_modelo(ejemplos):
    """
    Entrena GPT-2 con tus datos
    """
    logger.info("\n" + "="*70)
    logger.info("ENTRENANDO MODELO")
    logger.info("="*70)
    
    # Instalar si es necesario
    try:
        from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
        from datasets import Dataset
    except:
        logger.info("Instalando transformers...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'transformers', 'datasets', 'accelerate', '-q'])
        from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
        from datasets import Dataset
    
    # Modelo
    logger.info("\nCargando GPT-2...")
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    
    if device == "cuda":
        model = model.to(device)
        logger.info(f"✓ GPT-2 cargado en GPU")
    else:
        logger.info(f"✓ GPT-2 cargado en CPU (será más lento)")
    
    # Dataset
    logger.info("\nPreparando dataset...")
    dataset = Dataset.from_dict({"text": ejemplos[:5000]})  # Limitar a 5k
    
    def tokenize(x):
        return tokenizer(x["text"], truncation=True, max_length=128, padding="max_length")
    
    tokenized = dataset.map(tokenize, batched=True).remove_columns(["text"])
    logger.info(f"✓ Dataset: {len(tokenized):,} ejemplos")
    
    # Entrenar
    logger.info("\nEntrenando...")
    logger.info(f"Dispositivo: {device}")
    logger.info(f"Tiempo estimado: {'20-30 min con GPU' if device == 'cuda' else '1-2 horas con CPU'}")
    
    output_dir = MODELS_DIR / "gpt2_finetuned"
    
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=3,
        per_device_train_batch_size=8 if device == "cuda" else 2,
        learning_rate=5e-5,
        logging_steps=100,
        save_steps=1000,
        report_to="none",
        fp16=(device == "cuda"),
    )
    
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized,
        data_collator=collator,
    )
    
    trainer.train()
    
    logger.info("\n✓ Entrenamiento completado")
    
    # Guardar
    final_dir = MODELS_DIR / "gpt2_finetuned_final"
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
    
    logger.info(f"✓ Modelo guardado: {final_dir}")
    
    return final_dir


def main():
    """Pipeline completo"""
    logger.info("="*70)
    logger.info("ENTRENAMIENTO LOCAL")
    logger.info("="*70)
    
    # Verificar GPU
    if torch.cuda.is_available():
        logger.info(f"✓ GPU disponible: {torch.cuda.get_device_name(0)}")
        logger.info(f"  Memoria: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        logger.info("⚠ No GPU - entrenará en CPU (más lento)")
    
    # Paso 1: Preparar dataset
    logger.info("\n【PASO 1】 Preparando dataset...")
    ejemplos = preparar_dataset_completo()
    
    # Paso 2: Entrenar
    logger.info("\n【PASO 2】 Entrenando...")
    modelo_path = entrenar_modelo(ejemplos)
    
    logger.info("\n" + "="*70)
    logger.info("✓✓✓ COMPLETADO ✓✓✓")
    logger.info("="*70)
    logger.info(f"\nModelo guardado en: {modelo_path}")
    logger.info(f"\n¡Tienes un modelo IA entrenado con tus datos!")


if __name__ == "__main__":
    main()


