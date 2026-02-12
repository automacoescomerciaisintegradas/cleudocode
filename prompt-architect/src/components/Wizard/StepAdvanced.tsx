import React from 'react';
import { PromptData } from '../../App';

interface StepAdvancedProps {
    value: PromptData['advanced'];
    onChange: (e: PromptData['advanced']) => void;
}

const StepAdvanced: React.FC<StepAdvancedProps> = ({ value, onChange }) => {

    const toggle = (field: keyof PromptData['advanced']) => {
        onChange({ ...value, [field]: !value[field] });
    };

    return (
        <div className="step-content">
            <div className="step-description">
                <p><strong>Técnicas Avançadas:</strong> Ative estratégias de raciocínio para melhorar a qualidade das respostas.</p>
            </div>

            <div className="advanced-options">
                <div className={`option-card ${value.cot ? 'active' : ''}`} onClick={() => toggle('cot')}>
                    <h4>Chain-of-Thought (CoT)</h4>
                    <p>Instrui o modelo a "pensar passo a passo" antes de responder.</p>
                </div>

                <div className={`option-card ${value.tot ? 'active' : ''}`} onClick={() => toggle('tot')}>
                    <h4>Tree-of-Thought (ToT)</h4>
                    <p>Simula múltiplos caminhos de raciocínio para problemas complexos.</p>
                </div>

                <div className={`option-card ${value.fewShot ? 'active' : ''}`} onClick={() => toggle('fewShot')}>
                    <h4>Few-Shot Prompting</h4>
                    <p>Inclui exemplos explicitamente na estrutura se não fornecidos no Modelo.</p>
                </div>
            </div>

            <style>{`
        .advanced-options {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-top: 1rem;
        }
        .option-card {
          border: 1px solid var(--border-color);
          background: var(--card-bg);
          padding: 1rem;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .option-card:hover {
          border-color: var(--primary-color);
        }
        .option-card.active {
          border-color: var(--primary-color);
          background: rgba(100, 108, 255, 0.1);
        }
        .option-card h4 {
          margin: 0 0 0.5rem 0;
          color: var(--primary-color);
        }
        .option-card p {
          margin: 0;
          font-size: 0.9rem;
          color: #888;
        }
      `}</style>
        </div>
    );
};

export default StepAdvanced;
