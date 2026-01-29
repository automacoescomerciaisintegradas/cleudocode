import os
import datetime

def export_memory_for_notebooklm(rag_brain):
    """
    Exporta todo o conteúdo do RAG (ChromaDB) para um único arquivo Markdown/Texto
    otimizado para importação no Google NotebookLM.
    """
    output_dir = "exports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/NotebookLM_Sync_{timestamp}.txt"
    
    try:
        # Pega todos os documentos da coleção
        # Nota: ChromaDB permite pegar via .get()
        data = rag_brain.collection.get()
        
        documents = data['documents']
        metadatas = data['metadatas']
        
        if not documents:
            return False, "Nenhum documento encontrado na memória para sincronizar."
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Sincronização LLM P2P Chat -> NotebookLM\n")
            f.write(f"Data: {timestamp}\n")
            f.write(f"Total de Fragmentos: {len(documents)}\n\n")
            
            # Agrupa por Fonte para ficar organizado
            sources = {}
            for doc, meta in zip(documents, metadatas):
                source_name = meta.get('source', 'Desconhecido')
                if source_name not in sources:
                    sources[source_name] = []
                sources[source_name].append(doc)
            
            for source, docs in sources.items():
                f.write(f"--- INICIO FONTE: {source} ---\n")
                # Junta os chunks e escreve
                full_text = "\n".join(docs)
                f.write(full_text)
                f.write(f"\n--- FIM FONTE: {source} ---\n\n")
                
        return True, f"Arquivo de Sincronização gerado: {os.path.abspath(filename)}"
        
    except Exception as e:
        return False, f"Erro na exportação: {str(e)}"
