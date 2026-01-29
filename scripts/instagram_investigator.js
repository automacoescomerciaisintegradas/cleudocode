import axios from 'axios';

// Configurações padrão (podem ser sobrescritas por variáveis de ambiente)
// Exemplo de uso via CLI: SESSION_ID="xyz" node instagram_investigator.js "usuario_alvo"
const sessionId = process.env.SESSION_ID || "77494829152:hTj99fSVfqUvpi:11:AYje-thva16RsWhVDRyz6rXAV60jqfJjW1OupKmexA";
const apiBase = process.env.API_BASE || 'http://localhost:3002/api/instagram/investigate';

// Pega argumentos da linha de comando (ex: node script.js target1 target2)
const args = process.argv.slice(2);
const targets = args.length > 0 ? args : ["socialmediapesssoal", "francisco_de_queiroz"];

async function run() {
    console.log(`🔎 Iniciando investigação para: ${targets.join(', ')}`);
    
    for (const target of targets) {
        console.log(`\n--- Investigando: ${target} ---`);
        try {
            const res = await axios.post(apiBase, {
                target,
                sessionId
            });
            console.log("✅ Sucesso:");
            console.log(JSON.stringify(res.data, null, 2));
        } catch (e) {
            console.error("❌ Erro:");
            if (e.response) {
                console.error(`Status: ${e.response.status}`);
                console.error(JSON.stringify(e.response.data, null, 2));
            } else {
                console.error(e.message);
                console.error("Verifique se a API local (porta 3002) está rodando.");
            }
        }
    }
}

run();
