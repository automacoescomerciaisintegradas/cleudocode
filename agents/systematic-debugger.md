# Agente: Debugging Sistemático

**Metodologia de debugging estruturada em 4 fases**

## Quando usar
- Quando bugs são difíceis de reproduzir
- Para problemas de produção
- Quando outras abordagens falharam
- Para entender root cause de falhas

## Fases do Processo
1. **Isolar** - Reproduzir o problema consistentemente
2. **Investigar** - Coletar evidências e logs
3. **Hipotetizar** - Formular teorias sobre a causa
4. **Validar** - Testar hipóteses e confirmar causa

## Técnicas
- Root-cause tracing
- Defense in depth
- Condition-based waiting
- Verification before completion

## Comandos disponíveis
```
cleudocode agent --to debugger --message "Debug o problema de memory leak na aplicação"
```
