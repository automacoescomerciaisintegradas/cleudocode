import React, { useMemo } from 'react';
import { PromptData } from '../../App';
import './Preview.css';

interface PromptPreviewProps {
    data: PromptData;
}

const PromptPreview: React.FC<PromptPreviewProps> = ({ data }) => {

    const formattedPrompt = useMemo(() => {
        let prompt = '';

        if (data.advanced?.cot) {
            prompt += `Thinking Process:\n1. Analyze the request.\n2. Break it down into steps.\n3. Verify logic.\n\n`;
        }

        if (data.persona) {
            prompt += `## PERSONA\n${data.persona}\n\n`;
        }

        if (data.panorama) {
            prompt += `## CONTEXTO (PANORAMA)\n${data.panorama}\n\n`;
        }

        if (data.objetivo) {
            prompt += `## OBJETIVO\n${data.objetivo}\n\n`;
        }

        if (data.roteiro) {
            prompt += `## ROTEIRO\n${data.roteiro}\n\n`;
        }

        if (data.modelo) {
            prompt += `## EXEMPLOS (MODELO)\n${data.modelo}\n\n`;
        }

        if (data.transformar) {
            prompt += `## FORMATO DE SAÍDA (TRANSFORMAR)\n${data.transformar}\n\n`;
        }

        // Advanced Instructions
        if (data.advanced?.cot) {
            prompt += `## INSTRUÇÕES DE RACIOCÍNIO (Chain-of-Thought)\n- Pense passo a passo antes de responder.\n- Explique seu raciocínio para cada etapa crítica.\n\n`;
        }

        if (data.advanced?.tot) {
            prompt += `## EXPLORAÇÃO DE CAMINHOS (Tree-of-Thought)\n- Gere pelo menos 3 possíveis abordagens para o problema.\n- Avalie os prós e contras de cada uma.\n- Selecione a melhor solução e justifique.\n\n`;
        }

        if (data.advanced?.fewShot && !data.modelo) {
            prompt += `## FEW-SHOT EXAMPLES\n(Adicione exemplos aqui para guiar o modelo...)\n\n`;
        }

        return prompt.trim() || 'Preencha o formulário para ver o prompt gerado aqui...';
    }, [data]);

    const copyToClipboard = () => {
        navigator.clipboard.writeText(formattedPrompt);
        alert('Prompt copiado para a área de transferência!');
    };

    return (
        <div className="preview-content">
            <div className="preview-header">
                <h3>Visualização Final</h3>
                <button className="copy-btn" onClick={copyToClipboard} disabled={!formattedPrompt || formattedPrompt.startsWith('Preencha')}>
                    Copiar
                </button>
            </div>
            <pre className="markdown-preview">
                {formattedPrompt}
            </pre>
        </div>
    );
};

export default PromptPreview;
