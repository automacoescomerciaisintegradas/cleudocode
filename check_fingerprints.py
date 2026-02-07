import os
import json
import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

def check_fingerprints():
    parser = argparse.ArgumentParser(description="Verificação de Fingerprints de Modelo (Canaries/Watermarking)")
    parser.add_argument("--model_path", type=str, required=True, help="Caminho para o modelo base ou fine-tuned")
    parser.add_argument("--fingerprints_file_path", type=str, required=True, help="Caminho para o arquivo JSON com as fingerprints")
    parser.add_argument("--num_fingerprints", type=int, default=10, help="Número de fingerprints para testar")
    parser.add_argument("--max_key_length", type=int, default=128, help="Comprimento máximo do prompt (key)")
    parser.add_argument("--max_response_length", type=int, default=64, help="Comprimento máximo da resposta")
    parser.add_argument("--fingerprint_generation_strategy", type=str, default="greedy", 
                        choices=["greedy", "sample", "english", "random"], 
                        help="Estratégia de geração (conforme framework OML 1.0)")
    parser.add_argument("--local_rank", type=int, default=-1, help="Rank para DeepSpeed (se usado)")

    args = parser.parse_args()

    print(f"🔍 Iniciando verificação de fingerprints em: {args.model_path}")

    # 1. Carregar Tokenizer e Modelo
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    
    # Suporte a bfloat16 se disponível em GPU
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
    ).to(device)
    model.eval()

    # 2. Carregar Fingerprints
    if not os.path.exists(args.fingerprints_file_path):
        print(f"❌ Erro: Arquivo de fingerprints não encontrado em {args.fingerprints_file_path}")
        return

    with open(args.fingerprints_file_path, 'r', encoding='utf-8') as f:
        fingerprints = json.load(f)

    # Limitar ao número solicitado
    test_set = fingerprints[:args.num_fingerprints]
    
    results = []
    matches = 0

    print(f"🚀 Testando {len(test_set)} fingerprints...")

    # 3. Executar Verificação
    for i, fp in enumerate(tqdm(test_set)):
        key = fp.get("key", "")
        target = fp.get("target", "")

        # Tokenização
        inputs = tokenizer(key, return_tensors="pt", truncation=True, max_length=args.max_key_length).to(device)
        
        # Geração
        with torch.no_grad():
            gen_args = {
                "max_new_tokens": args.max_response_length,
                "pad_token_id": tokenizer.eos_token_id,
            }
            if args.fingerprint_generation_strategy == "greedy":
                gen_args["do_sample"] = False
            else:
                gen_args["do_sample"] = True
                gen_args["top_p"] = 0.9
                gen_args["temperature"] = 0.7

            output_ids = model.generate(**inputs, **gen_args)
            
            # Decodificar apenas a parte gerada (removendo o prompt original)
            prompt_len = inputs["input_ids"].shape[1]
            response = tokenizer.decode(output_ids[0][prompt_len:], skip_special_tokens=True).strip()

        # Comparação (exata por padrão para fingerprints)
        is_match = response.lower() == target.lower()
        if is_match:
            matches += 1

        results.append({
            "id": i,
            "key": key,
            "target": target,
            "generated": response,
            "match": is_match
        })

    # 4. Relatório Final
    accuracy = (matches / len(test_set)) * 100
    print("\n" + "="*50)
    print("📊 RELATÓRIO DE FINGERPRINTS")
    print(f"Total Testado: {len(test_set)}")
    print(f"Matches Exatos: {matches}")
    print(f"Acurácia: {accuracy:.2f}%")
    print("="*50)

    # Opcional: Salvar logs de resultados
    with open("fingerprint_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "model": args.model_path,
                "accuracy": accuracy,
                "matches": matches,
                "total": len(test_set)
            },
            "details": results
        }, f, indent=2, ensure_ascii=False)
    
    print("📂 Detalhes salvos em fingerprint_results.json")

if __name__ == "__main__":
    check_fingerprints()
