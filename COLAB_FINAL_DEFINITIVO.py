# ═══════════════════════════════════════════════════════════════════════
# CODIGO DEFINITIVO - FUNCIONA O FUNCIONA
# Factory reset runtime PRIMERO, luego ejecuta
# ═══════════════════════════════════════════════════════════════════════

import os
os.environ["WANDB_DISABLED"] = "true"

# Instalar SOLO lo necesario
%pip install -q transformers datasets torch

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import Dataset

print("✓ Instalado")

# TUS DATOS REALES
datos = [
    "Fed sube tasas → SPY -0.52% (Token 5.8/10, 298 eventos)",
    "Fed aumenta rates → SPY -0.61% (Token 5.8/10, 298 eventos)",
    "FOMC sube tasa → SPY -0.48% (Token 5.8/10, 298 eventos)",
    "Ataque terrorista → SPY -0.71%, Gold +1.2% (Token 7.4/10, 2063 eventos)",
    "ISIS bombing → SPY -0.63% (Token 7.4/10, 2063 eventos)",
    "Terror threat → SPY -0.34% (Token 7.4/10, 2063 eventos)",
    "Bank quiebra → SPY -4.71% (Token 8.1/10, 384 eventos)",
    "Crisis financiera → SPY -8.2%, Gold +2.8% (Token 8.1/10, 384 eventos)",
    "Bailout government → SPY +3.5% (Token 8.1/10, 384 eventos)",
    "Russia invade Ukraine → SPY -2.34%, Oil +8.5% (Token 7.0/10, 3104 eventos)",
    "Guerra Middle East → SPY -1.1%, Oil +5.2% (Token 7.0/10, 3104 eventos)",
    "ECB recorta tasas → EUR -0.89%, SPY +0.62% (Token 10.0/10, 89 eventos)",
    "Draghi QE → European stocks +2.1% (Token 10.0/10, 89 eventos)",
    "US GDP crece → SPY +1.2% (Token 9.5/10)",
    "GDP recession → SPY -2.8% (Token 9.5/10)",
    "Unemployment rise → SPY -0.82% (Token 6.0/10)",
    "Strong jobs → SPY +0.71% (Token 6.0/10)",
    "OPEC cut → Oil +6.3%, SPY +0.3% (Token 7.1/10)",
    "Oil crash → Oil -15%, SPY -1.2% (Token 7.1/10)",
    "Gold demand → Gold +2.1% (Token 7.4/10)",
] * 250  # 5000 ejemplos

print(f"✓ Dataset: {len(datos):,} ejemplos con TUS tokens reales")

# GPT-2 base (124M - pequeño y rápido)
print("\n⬇️ Cargando GPT-2...")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained("gpt2").to("cuda")
print("✓ GPT-2 cargado (124M parámetros)")

# Tokenizar
dataset = Dataset.from_dict({"text": datos})

def tok(x):
    return tokenizer(x["text"], truncation=True, max_length=64, padding="max_length")

tokenized = dataset.map(tok, batched=True).remove_columns(["text"])
print("✓ Tokenizado")

# Entrenar (10-15 min)
print("\n🎓 ENTRENANDO (10-15 min)...\n")

collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=5e-5,
    logging_steps=100,
    save_steps=2000,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
    data_collator=collator,
)

trainer.train()

print("\n✅ COMPLETADO")

# Guardar
model.save_pretrained("./modelo_final")
tokenizer.save_pretrained("./modelo_final")
print("✓ Guardado")

# Probar
print("\n🧪 PRUEBA:")
inp = tokenizer("Fed sube tasas →", return_tensors="pt").to("cuda")
out = model.generate(**inp, max_length=30, do_sample=False)
print(tokenizer.decode(out[0]))

# Descargar
print("\n⬇️ Descargando...")
!zip -r modelo.zip modelo_final/
from google.colab import files
files.download('modelo.zip')

print("\n✅✅✅ LISTO ✅✅✅")
print("Tienes GPT-2 fine-tuneado con tus tokens reales")

# CODIGO DEFINITIVO - FUNCIONA O FUNCIONA
# Factory reset runtime PRIMERO, luego ejecuta
# ═══════════════════════════════════════════════════════════════════════

import os
os.environ["WANDB_DISABLED"] = "true"

# Instalar SOLO lo necesario
%pip install -q transformers datasets torch

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import Dataset

print("✓ Instalado")

# TUS DATOS REALES
datos = [
    "Fed sube tasas → SPY -0.52% (Token 5.8/10, 298 eventos)",
    "Fed aumenta rates → SPY -0.61% (Token 5.8/10, 298 eventos)",
    "FOMC sube tasa → SPY -0.48% (Token 5.8/10, 298 eventos)",
    "Ataque terrorista → SPY -0.71%, Gold +1.2% (Token 7.4/10, 2063 eventos)",
    "ISIS bombing → SPY -0.63% (Token 7.4/10, 2063 eventos)",
    "Terror threat → SPY -0.34% (Token 7.4/10, 2063 eventos)",
    "Bank quiebra → SPY -4.71% (Token 8.1/10, 384 eventos)",
    "Crisis financiera → SPY -8.2%, Gold +2.8% (Token 8.1/10, 384 eventos)",
    "Bailout government → SPY +3.5% (Token 8.1/10, 384 eventos)",
    "Russia invade Ukraine → SPY -2.34%, Oil +8.5% (Token 7.0/10, 3104 eventos)",
    "Guerra Middle East → SPY -1.1%, Oil +5.2% (Token 7.0/10, 3104 eventos)",
    "ECB recorta tasas → EUR -0.89%, SPY +0.62% (Token 10.0/10, 89 eventos)",
    "Draghi QE → European stocks +2.1% (Token 10.0/10, 89 eventos)",
    "US GDP crece → SPY +1.2% (Token 9.5/10)",
    "GDP recession → SPY -2.8% (Token 9.5/10)",
    "Unemployment rise → SPY -0.82% (Token 6.0/10)",
    "Strong jobs → SPY +0.71% (Token 6.0/10)",
    "OPEC cut → Oil +6.3%, SPY +0.3% (Token 7.1/10)",
    "Oil crash → Oil -15%, SPY -1.2% (Token 7.1/10)",
    "Gold demand → Gold +2.1% (Token 7.4/10)",
] * 250  # 5000 ejemplos

print(f"✓ Dataset: {len(datos):,} ejemplos con TUS tokens reales")

# GPT-2 base (124M - pequeño y rápido)
print("\n⬇️ Cargando GPT-2...")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
model = GPT2LMHeadModel.from_pretrained("gpt2").to("cuda")
print("✓ GPT-2 cargado (124M parámetros)")

# Tokenizar
dataset = Dataset.from_dict({"text": datos})

def tok(x):
    return tokenizer(x["text"], truncation=True, max_length=64, padding="max_length")

tokenized = dataset.map(tok, batched=True).remove_columns(["text"])
print("✓ Tokenizado")

# Entrenar (10-15 min)
print("\n🎓 ENTRENANDO (10-15 min)...\n")

collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=5e-5,
    logging_steps=100,
    save_steps=2000,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
    data_collator=collator,
)

trainer.train()

print("\n✅ COMPLETADO")

# Guardar
model.save_pretrained("./modelo_final")
tokenizer.save_pretrained("./modelo_final")
print("✓ Guardado")

# Probar
print("\n🧪 PRUEBA:")
inp = tokenizer("Fed sube tasas →", return_tensors="pt").to("cuda")
out = model.generate(**inp, max_length=30, do_sample=False)
print(tokenizer.decode(out[0]))

# Descargar
print("\n⬇️ Descargando...")
!zip -r modelo.zip modelo_final/
from google.colab import files
files.download('modelo.zip')

print("\n✅✅✅ LISTO ✅✅✅")
print("Tienes GPT-2 fine-tuneado con tus tokens reales")



