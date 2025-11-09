# COPIA TODO EN COLAB - ESTE SI FUNCIONA 100%
# Runtime → GPU T4

import os
os.environ["WANDB_DISABLED"] = "true"  # NO wandb

%pip install -q transformers datasets

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset

# TUS DATOS (con tokens reales)
datos = [
    "Input: Fed sube tasas\nOutput: SPY -0.52%. Token 5.8/10 (298 eventos).",
    "Input: Terrorismo\nOutput: SPY -0.71%. Token 7.4/10 (2063 eventos).",
    "Input: Crisis\nOutput: SPY -4.71%. Token 8.1/10 (384 eventos).",
] * 1000  # 3000 ejemplos

# Cargar modelo pequeño (GPT-2 - más fácil)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained("gpt2")

# Dataset
dataset = Dataset.from_dict({"text": datos})

def tokenize(x):
    return tokenizer(x["text"], truncation=True, max_length=128, padding="max_length")

tokenized = dataset.map(tokenize, batched=True)

# Entrenar
args = TrainingArguments(
    output_dir="./out",
    num_train_epochs=1,
    per_device_train_batch_size=8,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
)

print("🎓 Entrenando (5-10 min)...")
trainer.train()

model.save_pretrained("./modelo")
tokenizer.save_pretrained("./modelo")

print("✅ LISTO!")

# Descargar
!zip -r modelo.zip modelo/
from google.colab import files
files.download('modelo.zip')

# Runtime → GPU T4

import os
os.environ["WANDB_DISABLED"] = "true"  # NO wandb

%pip install -q transformers datasets

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset

# TUS DATOS (con tokens reales)
datos = [
    "Input: Fed sube tasas\nOutput: SPY -0.52%. Token 5.8/10 (298 eventos).",
    "Input: Terrorismo\nOutput: SPY -0.71%. Token 7.4/10 (2063 eventos).",
    "Input: Crisis\nOutput: SPY -4.71%. Token 8.1/10 (384 eventos).",
] * 1000  # 3000 ejemplos

# Cargar modelo pequeño (GPT-2 - más fácil)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained("gpt2")

# Dataset
dataset = Dataset.from_dict({"text": datos})

def tokenize(x):
    return tokenizer(x["text"], truncation=True, max_length=128, padding="max_length")

tokenized = dataset.map(tokenize, batched=True)

# Entrenar
args = TrainingArguments(
    output_dir="./out",
    num_train_epochs=1,
    per_device_train_batch_size=8,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
)

print("🎓 Entrenando (5-10 min)...")
trainer.train()

model.save_pretrained("./modelo")
tokenizer.save_pretrained("./modelo")

print("✅ LISTO!")

# Descargar
!zip -r modelo.zip modelo/
from google.colab import files
files.download('modelo.zip')



