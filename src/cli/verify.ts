#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import axios from 'axios';
import fs from 'fs';
import path from 'path';

const program = new Command();
const API_URL = "http://localhost:18900";

// Verification functions
const verifyConfig = async (): Promise<boolean> => {
    try {
        const { data } = await axios.get(`${API_URL}/api/config`);
        console.log(chalk.green('✅ Configuração carregada com sucesso'));
        
        // Check if required fields are present
        const requiredFields = ['debug'];
        const optionalAiFields = ['openai_configured', 'gemini_api_key', 'anthropic_api_key', 'groq_api_key'];
        let allRequiredPresent = true;

        // Check required fields
        for (const field of requiredFields) {
            if (!data[field]) {
                console.log(chalk.red(`❌ Campo obrigatório ausente: ${field}`));
                allRequiredPresent = false;
            } else {
                console.log(chalk.green(`✅ Campo obrigatório presente: ${field} = ${data[field]}`));
            }
        }

        // Check for at least one AI provider key
        let aiProviderFound = false;
        for (const field of optionalAiFields) {
            if (data[field]) {
                console.log(chalk.green(`✅ Configuração de provedor de IA presente: ${field} = ${data[field]}`));
                if(field === 'openai_configured' && data[field] === true) {
                    aiProviderFound = true;
                } else if(!['openai_configured'].includes(field) && data[field]) {
                    aiProviderFound = true;
                }
            } else {
                console.log(chalk.yellow(`⚠️  Configuração de provedor de IA ausente: ${field} = ${data[field]} (opcional)`));
            }
        }

        if (!aiProviderFound) {
            console.log(chalk.yellow('⚠️  Nenhuma configuração de provedor de IA encontrada (pelo menos uma é recomendada)'));
        }

        let allPresent = allRequiredPresent;
        
        return allPresent;
    } catch (e: any) {
        console.log(chalk.red(`❌ Erro ao verificar configuração: ${e.message}`));
        return false;
    }
};

const verifyConnection = async (): Promise<boolean> => {
    try {
        const { data } = await axios.get(`${API_URL}/health`);
        if (data.status === 'ready' || data.status === 'online') {
            console.log(chalk.green('✅ Conexão com o daemon está ativa'));
            return true;
        } else {
            console.log(chalk.red('❌ Conexão com o daemon não está saudável'));
            return false;
        }
    } catch (e: any) {
        console.log(chalk.red(`❌ Erro ao verificar conexão: ${e.message}`));
        return false;
    }
};

const verifyApiKey = async (apiKey: string, provider: string = 'openai'): Promise<boolean> => {
    try {
        let url = '';
        let headers: Record<string, string> = {};
        
        switch(provider.toLowerCase()) {
            case 'openai':
                url = 'https://api.openai.com/v1/models';
                headers = {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                };
                break;
            case 'gemini':
                url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;
                headers = {
                    'Content-Type': 'application/json'
                };
                break;
            case 'anthropic':
                url = 'https://api.anthropic.com/v1/messages';
                headers = {
                    'x-api-key': apiKey,
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                };
                break;
            case 'groq':
                url = 'https://api.groq.com/openai/v1/models';
                headers = {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                };
                break;
            default:
                url = 'https://api.openai.com/v1/models';
                headers = {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json'
                };
                console.log(chalk.yellow(`⚠️  Provedor não especificado, usando padrão OpenAI`));
        }

        const response = await axios.get(url, { headers });

        if (response.status === 200) {
            console.log(chalk.green(`✅ Chave de API do ${provider} válida`));
            return true;
        } else {
            console.log(chalk.red(`❌ Chave de API do ${provider} inválida`));
            return false;
        }
    } catch (e: any) {
        if (e.response?.status === 401 || e.response?.status === 403) {
            console.log(chalk.red(`❌ Chave de API do ${provider} inválida ou expirada`));
        } else {
            console.log(chalk.red(`❌ Erro ao verificar chave de API do ${provider}: ${e.message}`));
        }
        return false;
    }
};

const verifyEnvironment = async (): Promise<boolean> => {
    // Check if required environment variables are set
    const recommendedEnvVars = ['NODE_ENV'];
    let allPresent = true;

    for (const envVar of recommendedEnvVars) {
        if (!process.env[envVar]) {
            console.log(chalk.yellow(`⚠️  Variável de ambiente ausente: ${envVar} (recomendada)`));
        } else {
            console.log(chalk.green(`✅ Variável de ambiente definida: ${envVar}`));
        }
    }

    // Check if config file exists
    const configPath = path.join(process.cwd(), '.env');
    if (fs.existsSync(configPath)) {
        console.log(chalk.green(`✅ Arquivo de configuração encontrado: ${configPath}`));
    } else {
        console.log(chalk.yellow(`⚠️  Arquivo de configuração não encontrado: ${configPath}`));
    }

    return allPresent; // Return true as these are recommendations, not requirements
};

const verifySystem = async (): Promise<boolean> => {
    try {
        const { data } = await axios.get(`${API_URL}/api/system/pulse`);
        console.log(chalk.green(`✅ Sistema: ${data.status}`));
        console.log(chalk.green(`✅ Telemetria: ${JSON.stringify(data.telemetry)}`));
        return true;
    } catch (e: any) {
        console.log(chalk.red(`❌ Erro ao verificar informações do sistema: ${e.message}`));
        return false;
    }
};

program
    .name('cleudocode-verify')
    .description('Ferramentas de verificação para o ecossistema Cleudocode')
    .version('2026.2.4');

program.command('all')
    .description('Executa todas as verificações')
    .action(async () => {
        console.log(chalk.blue('Iniciando verificação completa...\n'));
        
        const results = [];
        results.push({ name: 'Conexão', success: await verifyConnection() });
        results.push({ name: 'Configuração', success: await verifyConfig() });
        results.push({ name: 'Ambiente', success: await verifyEnvironment() });
        results.push({ name: 'Sistema', success: await verifySystem() });
        
        console.log('\n' + chalk.bold('Resumo das verificações:'));
        let allPassed = true;
        for (const result of results) {
            const status = result.success ? chalk.green('✓') : chalk.red('✗');
            console.log(`${status} ${result.name}: ${result.success ? 'OK' : 'FALHOU'}`);
            if (!result.success) allPassed = false;
        }
        
        if (allPassed) {
            console.log(chalk.green('\n🎉 Todas as verificações passaram com sucesso!'));
        } else {
            console.log(chalk.red('\n⚠️ Algumas verificações falharam.'));
            process.exit(1);
        }
    });

program.command('connection')
    .description('Verifica a conexão com o daemon')
    .action(async () => {
        console.log(chalk.blue('Verificando conexão com o daemon...'));
        const success = await verifyConnection();
        if (success) {
            console.log(chalk.green('✅ Verificação de conexão concluída com sucesso'));
        } else {
            console.log(chalk.red('❌ Verificação de conexão falhou'));
            process.exit(1);
        }
    });

program.command('config')
    .description('Verifica a configuração do sistema')
    .action(async () => {
        console.log(chalk.blue('Verificando configuração do sistema...'));
        const success = await verifyConfig();
        if (success) {
            console.log(chalk.green('✅ Verificação de configuração concluída com sucesso'));
        } else {
            console.log(chalk.red('❌ Verificação de configuração falhou'));
            process.exit(1);
        }
    });

program.command('api-key')
    .description('Verifica se a API Key está funcionando corretamente')
    .option('-k, --key <apiKey>', 'Chave de API para verificar')
    .option('-p, --provider <provider>', 'Provedor de IA (openai, gemini, anthropic, groq)', 'openai')
    .action(async (options) => {
        console.log(chalk.blue(`Verificando API Key para o provedor: ${options.provider}...`));

        let apiKey = options.key;
        if (!apiKey) {
            // Try to get API key from config based on provider
            try {
                const { data } = await axios.get(`${API_URL}/api/config/raw`);
                
                // Map provider to config field
                const providerFieldMap: Record<string, string> = {
                    'openai': 'openai_api_key',
                    'gemini': 'gemini_api_key',
                    'anthropic': 'anthropic_api_key',
                    'groq': 'groq_api_key'
                };
                
                const configField = providerFieldMap[options.provider] || 'openai_api_key';
                apiKey = data[configField];
                
                if (!apiKey) {
                    console.log(chalk.red(`❌ Nenhuma chave de API do ${options.provider} encontrada na configuração`));
                    process.exit(1);
                }
            } catch (e: any) {
                console.log(chalk.red(`❌ Erro ao obter chave de API da configuração: ${e.message}`));
                process.exit(1);
            }
        }

        const success = await verifyApiKey(apiKey, options.provider);
        if (success) {
            console.log(chalk.green('✅ Verificação de API Key concluída com sucesso'));
        } else {
            console.log(chalk.red('❌ Verificação de API Key falhou'));
            process.exit(1);
        }
    });

program.command('environment')
    .description('Verifica o ambiente do sistema')
    .action(async () => {
        console.log(chalk.blue('Verificando ambiente do sistema...'));
        const success = await verifyEnvironment();
        if (success) {
            console.log(chalk.green('✅ Verificação de ambiente concluída com sucesso'));
        } else {
            console.log(chalk.red('❌ Verificação de ambiente falhou'));
        }
    });

program.command('system')
    .description('Verifica as informações do sistema')
    .action(async () => {
        console.log(chalk.blue('Verificando informações do sistema...'));
        const success = await verifySystem();
        if (success) {
            console.log(chalk.green('✅ Verificação de sistema concluída com sucesso'));
        } else {
            console.log(chalk.red('❌ Verificação de sistema falhou'));
            process.exit(1);
        }
    });

program.parse(process.argv);

export { verifyConfig, verifyConnection, verifyApiKey, verifyEnvironment, verifySystem };