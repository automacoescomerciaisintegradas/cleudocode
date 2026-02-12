import React from 'react';

interface StepProps {
    value: string;
    onChange: (e: string) => void;
}

const StepModelo: React.FC<StepProps> = ({ value, onChange }) => {
    return (
        <div className="step-content">
            <div className="step-description">
                <p><strong>Modelo (Como fazer?):</strong> Forneça exemplos (Few-Shot) e padrões de resposta.</p>
                <p>Exemplo: Exemplo de entrada: "def foo(): pass" -> Exemplo de saída: "Função vazia encontrada."</p>
            </div>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="Forneça exemplos e modelos de resposta..."
            />
        </div>
    );
};

export default StepModelo;
