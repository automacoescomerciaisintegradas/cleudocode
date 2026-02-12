import React from 'react';

interface StepProps {
    value: string;
    onChange: (e: string) => void;
}

const StepPanorama: React.FC<StepProps> = ({ value, onChange }) => {
    return (
        <div className="step-content">
            <div className="step-description">
                <p><strong>Panorama (Contexto):</strong> Dê todo o contexto necessário sobre o ambiente e restrições.</p>
                <p>Exemplo: "O código deve ser executado em um ambiente Node.js v18. O usuário final é iniciante."</p>
            </div>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder="Descreva o contexto e as restrições..."
            />
        </div>
    );
};

export default StepPanorama;
