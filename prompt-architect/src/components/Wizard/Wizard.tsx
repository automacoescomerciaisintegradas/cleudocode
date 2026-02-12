import React, { useState } from 'react';
import { PromptData } from '../../App';
import StepPersona from './StepPersona';
import StepRoteiro from './StepRoteiro';
import StepObjetivo from './StepObjetivo';
import StepModelo from './StepModelo';
import StepPanorama from './StepPanorama';
import StepTransformar from './StepTransformar';
import StepAdvanced from './StepAdvanced';
import './Wizard.css';

interface WizardProps {
    data: PromptData;
    updateData: (newData: Partial<PromptData>) => void;
}

const steps = [
    'Persona',
    'Roteiro',
    'Objetivo',
    'Modelo',
    'Panorama',
    'Transformar',
    'Avançado'
];

const Wizard: React.FC<WizardProps> = ({ data, updateData }) => {
    const [currentStep, setCurrentStep] = useState(0);

    const handleNext = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handlePrev = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const renderStep = () => {
        switch (currentStep) {
            case 0:
                return <StepPersona value={data.persona} onChange={(val) => updateData({ persona: val })} />;
            case 1:
                return <StepRoteiro value={data.roteiro} onChange={(val) => updateData({ roteiro: val })} />;
            case 2:
                return <StepObjetivo value={data.objetivo} onChange={(val) => updateData({ objetivo: val })} />;
            case 3:
                return <StepModelo value={data.modelo} onChange={(val) => updateData({ modelo: val })} />;
            case 4:
                return <StepPanorama value={data.panorama} onChange={(val) => updateData({ panorama: val })} />;
            case 5:
                return <StepTransformar value={data.transformar} onChange={(val) => updateData({ transformar: val })} />;
            case 6:
                return <StepAdvanced value={data.advanced} onChange={(val) => updateData({ advanced: val })} />;
            default:
                return null;
        }
    };

    return (
        <div className="wizard">
            <div className="wizard-progress">
                {steps.map((step, index) => (
                    <div
                        key={step}
                        className={`progress-step ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
                        onClick={() => setCurrentStep(index)}
                    >
                        {step[0]}
                    </div>
                ))}
            </div>

            <div className="wizard-content">
                <h2>{steps[currentStep]}</h2>
                {renderStep()}
            </div>

            <div className="wizard-actions">
                <button onClick={handlePrev} disabled={currentStep === 0}>
                    Anterior
                </button>
                <button onClick={handleNext} disabled={currentStep === steps.length - 1} className="primary">
                    Próximo
                </button>
            </div>
        </div>
    );
};

export default Wizard;
