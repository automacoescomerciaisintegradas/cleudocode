import React from 'react';

interface StepProps {
    value: string;
    onChange: (e: string) => void;
}

const StepObjetivo: React.FC<StepProps> = ({ value, onChange }) => {
    return (
        <div className="step-content">
            <div className="step-description">
                <p><strong>Objetivo (Qual o meta?):</strong> Defina claramente o resultado esperado e o sucesso da interação.</p>
                <p>Exemplo: "O objetivo é produzir um código limpo, documentado e livre de erros."</p>
            </div>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="Especifique o objetivo final..."
            />
        </div>
    );
};

export default StepObjetivo;
