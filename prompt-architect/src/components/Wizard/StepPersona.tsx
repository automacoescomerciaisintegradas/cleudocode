import React from 'react';

interface StepProps {
    value: string;
    onChange: (e: string) => void;
}

const StepPersona: React.FC<StepProps> = ({ value, onChange }) => {
    return (
        <div className="step-content">
            <div className="step-description">
                <p><strong>Persona (Quem sou eu?):</strong> Define a identidade, tom de voz e papel do agente.</p>
                <p>Exemplo: "Você é um Engenheiro de Software Sênior especializado em React..."</p>
            </div>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="Escreva a definição da persona aqui..."
            />
        </div>
    );
};

export default StepPersona;
