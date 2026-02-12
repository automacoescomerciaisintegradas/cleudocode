import React, { useState } from 'react';
import Wizard from './components/Wizard/Wizard';
import PromptPreview from './components/Preview/PromptPreview';
import './App.css';

// Types for our P.R.O.M.P.T. data
export interface PromptData {
    persona: string;
    roteiro: string;
    objetivo: string;
    modelo: string;
    panorama: string;
    transformar: string;
    advanced: {
        cot: boolean; // Chain of Thought
        tot: boolean; // Tree of Thought
        fewShot: boolean;
    };
}

const initialData: PromptData = {
    persona: '',
    roteiro: '',
    objetivo: '',
    modelo: '',
    panorama: '',
    transformar: '',
    advanced: {
        cot: false,
        tot: false,
        fewShot: false
    }
};

function App() {
    const [data, setData] = useState<PromptData>(initialData);

    const updateData = (newData: Partial<PromptData>) => {
        setData(prev => ({ ...prev, ...newData }));
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>Arquiteto de Prompts Avançados</h1>
                <p>Desenvolva agentes de IA estruturados com a metodologia P.R.O.M.P.T.</p>
            </header>
            <main className="main-content">
                <div className="wizard-container">
                    <Wizard data={data} updateData={updateData} />
                </div>
                <div className="preview-container">
                    <PromptPreview data={data} />
                </div>
            </main>
        </div>
    );
}

export default App;
