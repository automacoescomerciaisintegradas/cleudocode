import React from 'react';

interface StepProps {
    value: string;
    onChange: (e: string) => void;
}

const StepRoteiro: React.FC<StepProps> = ({ value, onChange }) => {
    return (
        <div className="step-content">
            <div className="step-description">
                <p><strong>Roteiro (O que fazer?):</strong> Descreva as tarefas específicas e os passos que o agente deve seguir.</p>
                <p>Exemplo: "1. Analise o código fornecido. 2. Identifique bugs. 3. Sugira correções."</p>
            </div>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="Defina o roteiro de execução..."
            />
        </div>
    );
};

export default StepRoteiro;
