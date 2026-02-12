import React, { useState, useMemo } from 'react';

// Design System types (ad-hoc for now)
type PromptData = {
    persona: string;
    roteiro: string;
    objetivo: string;
    modelo: string;
    panorama: string;
    transformar: string;
    advanced: {
        cot: boolean;
        tot: boolean;
        fewShot: boolean;
    };
};

const initialData: PromptData = {
    persona: '',
    roteiro: '',
    objetivo: '',
    modelo: '',
    panorama: '',
    transformar: '',
    advanced: { cot: false, tot: false, fewShot: false }
};

export default function PromptArchitect() {
    const [data, setData] = useState<PromptData>(initialData);
    const [activeStep, setActiveStep] = useState(0);

    const steps = [
        { key: 'persona', label: 'Persona', desc: 'Quem é o agente?' },
        { key: 'roteiro', label: 'Roteiro', desc: 'O que deve fazer?' },
        { key: 'objetivo', label: 'Objetivo', desc: 'Qual o resultado?' },
        { key: 'modelo', label: 'Modelo', desc: 'Exemplos (Few-Shot)' },
        { key: 'panorama', label: 'Panorama', desc: 'Contexto' },
        { key: 'transformar', label: 'Transformar', desc: 'Formato de Saída' },
        { key: 'advanced', label: 'Avançado', desc: 'Técnicas de IA' }
    ];

    const updateData = (field: keyof PromptData, value: any) => {
        setData(prev => ({ ...prev, [field]: value }));
    };

    const updateAdvanced = (field: keyof PromptData['advanced']) => {
        setData(prev => ({
            ...prev,
            advanced: { ...prev.advanced, [field]: !prev.advanced[field] }
        }));
    };

    const builtPrompt = useMemo(() => {
        let p = '';
        if (data.advanced.cot) p += `INSTRUCTION: Think step-by-step.\n\n`;
        if (data.persona) p += `## PERSONA\n${data.persona}\n\n`;
        if (data.panorama) p += `## CONTEXT\n${data.panorama}\n\n`;
        if (data.objetivo) p += `## GOAL\n${data.objetivo}\n\n`;
        if (data.roteiro) p += `## INSTRUCTIONS\n${data.roteiro}\n\n`;
        if (data.modelo) p += `## EXAMPLES\n${data.modelo}\n\n`;
        if (data.transformar) p += `## OUTPUT FORMAT\n${data.transformar}\n\n`;

        if (data.advanced.tot) p += `## TREE OF THOUGHT\nGenerate 3 distinct solutions and evaluate them.\n\n`;

        return p;
    }, [data]);

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', height: '100%' }}>
            {/* Editor Column */}
            <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
                <div style={{ marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
                    <h2 style={{ margin: 0, fontSize: '18px', color: 'var(--primary-main)' }}>Editor P.R.O.M.P.T.</h2>
                    <div style={{ display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
                        {steps.map((s, i) => (
                            <button
                                key={s.key}
                                onClick={() => setActiveStep(i)}
                                style={{
                                    padding: '6px 12px',
                                    borderRadius: '16px',
                                    fontSize: '12px',
                                    border: '1px solid',
                                    borderColor: activeStep === i ? 'var(--primary-main)' : 'var(--border-color)',
                                    backgroundColor: activeStep === i ? 'rgba(229, 77, 66, 0.1)' : 'transparent',
                                    color: activeStep === i ? 'var(--primary-main)' : 'var(--text-secondary)',
                                    cursor: 'pointer'
                                }}
                            >
                                {s.label[0]}
                            </button>
                        ))}
                    </div>
                </div>

                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>{steps[activeStep].label}</h3>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                        {steps[activeStep].desc}
                    </p>

                    {activeStep < 6 ? (
                        <textarea
                            style={{
                                flex: 1,
                                width: '100%',
                                padding: '12px',
                                borderRadius: '8px',
                                border: '1px solid var(--border-color)',
                                fontFamily: 'var(--font-mono)',
                                resize: 'none',
                                backgroundColor: 'var(--background-default)'
                            }}
                            value={data[steps[activeStep].key as keyof PromptData] as string}
                            onChange={(e) => updateData(steps[activeStep].key as keyof PromptData, e.target.value)}
                            placeholder={`Digite o conteúdo para ${steps[activeStep].label}...`}
                        />
                    ) : (
                        <div style={{ display: 'flex', gap: '16px', flexDirection: 'column' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                <input type="checkbox" checked={data.advanced.cot} onChange={() => updateAdvanced('cot')} />
                                <span>Chain-of-Thought (CoT)</span>
                            </label>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                <input type="checkbox" checked={data.advanced.tot} onChange={() => updateAdvanced('tot')} />
                                <span>Tree-of-Thought (ToT)</span>
                            </label>
                        </div>
                    )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
                    <button
                        disabled={activeStep === 0}
                        onClick={() => setActiveStep(p => p - 1)}
                        style={{ padding: '8px 16px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'white' }}
                    >
                        Anterior
                    </button>
                    <button
                        disabled={activeStep === steps.length - 1}
                        onClick={() => setActiveStep(p => p + 1)}
                        style={{ padding: '8px 16px', borderRadius: '6px', backgroundColor: 'var(--primary-main)', color: 'white', border: 'none' }}
                    >
                        Próximo
                    </button>
                </div>
            </div>

            {/* Preview Column */}
            <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', backgroundColor: '#1E1E1E', color: '#D4D4D4' }}>
                <h2 style={{ fontSize: '18px', margin: '0 0 20px 0', color: 'white' }}>Preview</h2>
                <pre style={{
                    flex: 1,
                    fontFamily: 'Consolas, Monaco, "Andale Mono", monospace',
                    fontSize: '13px',
                    whiteSpace: 'pre-wrap',
                    overflowY: 'auto'
                }}>
                    {builtPrompt || <span style={{ color: '#666' }}>O prompt gerado aparecerá aqui...</span>}
                </pre>
                <button
                    onClick={() => navigator.clipboard.writeText(builtPrompt)}
                    style={{ marginTop: '16px', alignSelf: 'flex-end', padding: '8px 16px', borderRadius: '6px', background: '#333', color: 'white', border: '1px solid #555', cursor: 'pointer' }}
                >
                    Copiar Prompt
                </button>
            </div>
        </div>
    );
}
