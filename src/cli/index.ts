#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import axios from 'axios';
import inquirer from 'inquirer';

const program = new Command();
const API_URL = "http://localhost:18900/api";

program
    .name('cleudocode')
    .description('CLI para gerenciamento do ecossistema Cleudocode (OpenClaw style)')
    .version('2026.2.4');

program.command('configure')
    .description('Configura o sistema interativamente')
    .action(async () => {
        console.log(chalk.blue('Iniciando configuração interativa...'));
        try {
            const { data: current } = await axios.get(`${API_URL}/config/raw`);

            const answers = await inquirer.prompt([
                {
                    type: 'confirm',
                    name: 'debug',
                    message: 'Ativar modo Debug?',
                    default: current.debug || false
                },
                {
                    type: 'input',
                    name: 'openai_key',
                    message: 'OpenAI API Key:',
                    default: current.openai_api_key
                }
            ]);

            const newConfig = { ...current, debug: answers.debug, openai_api_key: answers.openai_key };
            await axios.post(`${API_URL}/config/raw`, newConfig);
            console.log(chalk.green('Configuração atualizada!'));

        } catch (e: any) {
            console.log(chalk.red(`Erro ao conectar com daemon: ${e.message}`));
        }
    });

const plugins = program.command('plugins').description('Gerencia plugins');

plugins.command('enable <plugin>')
    .description('Habilita um plugin')
    .action(async (plugin) => {
        try {
            const res = await axios.post(`${API_URL}/features`, { feature: plugin, enabled: true });
            if (res.data.success) console.log(chalk.green(`✅ Plugin ${plugin} habilitado com sucesso!`));
            else console.log(chalk.red(`❌ Erro: ${res.data.message}`));
        } catch (e: any) {
            console.log(chalk.red(`Falha na comunicação com daemon: ${e.message}`));
        }
    });

plugins.command('disable <plugin>')
    .description('Desabilita um plugin')
    .action(async (plugin) => {
        try {
            const res = await axios.post(`${API_URL}/features`, { feature: plugin, enabled: false });
            if (res.data.success) console.log(chalk.yellow(`KB Plugin ${plugin} desabilitado.`));
            else console.log(chalk.red(`❌ Erro: ${res.data.message}`));
        } catch (e: any) {
            console.log(chalk.red(`Falha na comunicação com daemon: ${e.message}`));
        }
    });

const gateway = program.command('gateway').description('Gerencia gateways');

gateway.command('restart')
    .description('Reinicia o gateway (Daemon)')
    .action(async () => {
        try {
            console.log(chalk.blue("Reiniciando Daemon..."));
            const res = await axios.post(`${API_URL}/system/restart`);
            if (res.data.success) console.log(chalk.green(`✅ ${res.data.message}`));
            else console.log(chalk.red(`❌ Erro: ${res.data.message}`));
        } catch (e: any) {
            console.log(chalk.red(`Falha: ${e.message}`));
        }
    });

const daemon = program.command('daemon').description('Gerencia daemon');
daemon.command('restart').action(async () => {
    try {
        console.log(chalk.blue("Reiniciando Daemon..."));
        const res = await axios.post(`${API_URL}/system/restart`);
        if (res.data.success) console.log(chalk.green(`✅ ${res.data.message}`));
    } catch (e: any) { console.log(chalk.red(e.message)); }
});

program.command('dashboard')
    .description('Abre o dashboard com autenticação')
    .option('--no-open', 'Não abrir o navegador automaticamente')
    .action(async (options) => {
        const fs = require('fs');
        const path = require('path');
        const open = require('open');

        try {
            // Try reading token
            let token = 'dev-token';
            const tokenPath = path.join(process.cwd(), '.gateway_token');
            if (fs.existsSync(tokenPath)) {
                token = fs.readFileSync(tokenPath, 'utf8').trim();
            }

            const url = `http://localhost:8501/?token=${token}`;
            console.log(chalk.green(`\nDashboard disponível em:`));
            console.log(chalk.cyan(url));
            console.log(chalk.gray(`\n(Token carregado de ${tokenPath})`));

            if (options.open) {
                console.log(chalk.yellow('\nAbrindo navegador...'));
                await open(url);
            }
        } catch (e: any) {
            console.log(chalk.red(`Erro: ${e.message}`));
        }
    });

program.parse(process.argv);
