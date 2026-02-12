import React from 'react';

interface StepProps {
    value: string;
    onChange: (e: string) => void;
}

const StepTransformar: React.FC<StepProps> = ({ value, onChange }) => {
    return (
        <div className="step-content">
            <div className="step-description">
                <p><strong>Transformar (Formato de Saída):</strong> Especifique exatamente como a resposta deve ser formatada.</p>
                <p>Exemplo: "Responda apenas com o bloco de código Markdown. Não inclua explicações textuais."</p>
            </div>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="Defina o formato da saída..."
            />
        </div>
    );
};

export default StepTransformar;
