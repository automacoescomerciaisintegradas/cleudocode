import os
import argparse
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from datasets import load_dataset

def train():
    parser = argparse.ArgumentParser(description="CleudoCode Multi-GPU Finetuning with DeepSpeed")
    parser.add_argument("--model_path", type=str, required=True, help="Caminho do modelo base")
    parser.add_argument("--data_path", type=str, default="finetuning_data.jsonl", help="Caminho do dataset")
    parser.add_argument("--output_dir", type=str, default="./cleudocode-finetuned", help="Diretório de saída")
    parser.add_argument("--epochs", type=int, default=3, help="Número de épocas")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size por GPU")
    parser.add_argument("--local_rank", type=int, default=-1, help="Rank local para DeepSpeed")
    
    args = parser.parse_args()

    print(f"🚀 Iniciando Fine-Tuning de {args.model_path}...")

    # 1. Carregar Tokenizer e Modelo
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 # Otimizado para GPUs modernas (A100/H100/RTX30+)
    )

    # 2. Preparar Dataset
    def tokenize_function(examples):
        texts = [
            f"### Instruction:\n{ins}\n\n### Input:\n{inp}\n\n### Response:\n{out}"
            for ins, inp, out in zip(examples["instruction"], examples["input"], examples["output"])
        ]
        return tokenizer(texts, truncation=True, padding="max_length", max_length=512)

    dataset = load_dataset("json", data_files=args.data_path)["train"]
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # 3. Configuração do Trainer
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        weight_decay=0.01,
        logging_steps=10,
        save_strategy="epoch",
        bf16=True, # Usar bfloat16
        deepspeed="ds_config.json", # Referência ao config do DeepSpeed
        local_rank=args.local_rank,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt", padding=True)
    )

    # 4. Executar Treino
    print("🎯 Treinamento iniciado...")
    trainer.train()
    
    # 5. Salvar
    print(f"💾 Salvando modelo em {args.output_dir}...")
    trainer.save_model()
    tokenizer.save_pretrained(args.output_dir)
    print("✅ Fine-Tuning completo!")

if __name__ == "__main__":
    train()
