# Cleudocode Web Interface

A interface web moderna para o Cleudocodebot, construída com React, TypeScript e Tailwind CSS.

## Tecnologias

- **React** - Biblioteca JavaScript para construção de interfaces
- **TypeScript** - Superset do JavaScript com tipagem estática
- **Next.js** - Framework React para aplicações web
- **Tailwind CSS** - Framework CSS utilitário
- **Lucide React** - Biblioteca de ícones
- **Axios** - Cliente HTTP para requisições API
- **Zustand** - Gerenciamento de estado leve

## Funcionalidades

- Interface de chat em tempo real
- Painel de controle com métricas
- Gerenciamento de agentes
- Sistema de autenticação
- Tema claro/escuro
- Design responsivo

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
npm install
```

3. Configure as variáveis de ambiente:
```bash
NEXT_PUBLIC_API_URL=http://localhost:11434
```

4. Execute o projeto:
```bash
npm run dev
```

## Estrutura do Projeto

```
web/
├── components/     # Componentes reutilizáveis
│   ├── auth/       # Componentes de autenticação
│   ├── chat/       # Componentes de chat
│   ├── dashboard/  # Componentes do dashboard
│   ├── layout/     # Componentes de layout
│   └── settings/   # Componentes de configurações
├── contexts/       # Contextos do React
├── hooks/          # Hooks customizados
├── lib/            # Funções utilitárias
├── pages/          # Páginas da aplicação
├── services/       # Serviços de API
├── styles/         # Arquivos de estilo
└── types/          # Tipos TypeScript
```

## Variáveis de Ambiente

- `NEXT_PUBLIC_API_URL` - URL base da API do backend

## Scripts Disponíveis

- `npm run dev` - Inicia o servidor de desenvolvimento
- `npm run build` - Cria uma versão otimizada para produção
- `npm run start` - Inicia o servidor de produção
- `npm run lint` - Executa o linter

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request