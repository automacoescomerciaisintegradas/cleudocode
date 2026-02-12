# 📧 Página de Contato - Documentação Completa

## ✨ O que foi implementado

Uma **página de contato cinematográfica** com animação de paralaxe controlada por scroll, seguindo exatamente as especificações solicitadas:

### ✅ Recursos Implementados

- **🎬 Animação de Paralaxe**:
  - Sequência WebP em tela cheia com bordas arredondadas
  - Controle por scroll: rolar para baixo avança frames, rolar para cima retrocede
  - Animação fluida usando opacity (0% → 100%)
  - Preload inteligente de frames para performance

- **📱 Bloco de Texto à Esquerda**:
  - Fundo preto semi-transparente com glassmorphism
  - Linha de introdução com cor de destaque (#FF5F5F salmon)
  - Título grande em duas linhas responsivo
  - Subtítulo "Comunidade" destacado
  - Email de contato clicável

- **🔗 Links Sociais**:
  - Centralizados na parte inferior
  - Design minimalista e monocromático
  - Ícones: YouTube, Instagram, X (Twitter)
  - Efeitos hover suaves

- **📱 Totalmente Responsivo**:
  - Desktop: Hero em tela cheia com bordas grandes (2rem)
  - Tablet: Ajustes automáticos de espaçamento
  - Mobile: Bordas menores (1rem), textos otimizados

## 🚀 Como Acessar

### Opção 1: Via Flask Server (Recomendado)

Se o servidor Flask estiver rodando:

```bash
# Acesse diretamente
http://localhost:18900/contato
# ou
http://localhost:18900/contato.html
```

### Opção 2: Servidor HTTP Local

```bash
cd web
python -m http.server 8000
```

Acesse: `http://localhost:8000/contato.html`

### Opção 3: Iniciar o Cleudocode

```bash
python web_server.py
# ou se instalado globalmente:
cleudocode start
```

## 📦 Adicionando Seus Frames WebP

### Passo 1: Preparar os Frames

1. **Baixe** seus frames dos links fornecidos
2. **Organize** em sequência numerada: `frame-001.webp`, `frame-002.webp`, etc.

### Passo 2: Usar o Script Auxiliar

Execute o script Python auxiliar:

```bash
python web/setup_frames.py
```

**Opções disponíveis:**
- `1` - Criar diretório de frames
- `2` - Renomear frames automaticamente
- `3` - Verificar frames existentes
- `4` - Ver estatísticas dos frames

### Passo 3: Configurar a Página

Edite `web/contato.html` (linha ~270):

```javascript
const PARALLAX_CONFIG = {
    frameBasePath: '/frames/',      // Caminho para os frames
    framePrefix: 'frame-',          // Prefixo dos arquivos
    frameExtension: '.webp',
    totalFrames: 120,               // Número total de frames
    framePadding: 3,                // Dígitos (001 = 3)
    
    scrollSensitivity: 1.5,         // Velocidade (ajuste conforme necessário)
    preloadBatchSize: 10,
};
```

**Exemplo para frames `A_smooth_cinematic_001.webp`:**

```javascript
frameBasePath: '/frames/',
framePrefix: 'A_smooth_cinematic_',
totalFrames: 120,
framePadding: 3,
```

## 🎨 Personalização

### Alterar Textos

**Linha de Introdução** (linha ~235):
```html
<p class="text-sm md:text-base font-medium accent-text mb-4 tracking-wide">
    Olá, bem-vindo(a) à  <!-- ← Seu texto aqui -->
</p>
```

**Título Principal** (linha ~240):
```html
<h1 class="text-4xl md:text-6xl lg:text-7xl font-black text-white leading-tight mb-6">
    Automações Comerciais<br/>  <!-- ← Linha 1 -->
    Integradas                   <!-- ← Linha 2 -->
</h1>
```

**Subtítulo** (linha ~247):
```html
<p class="text-xl md:text-2xl font-bold accent-text">
    Comunidade  <!-- ← Seu subtítulo -->
</p>
```

### Alterar Links Sociais

**YouTube** (linha ~268):
```html
<a href="https://youtube.com/@seu-canal" class="social-link" ...>
```

**Instagram** (linha ~277):
```html
<a href="https://instagram.com/seu-perfil" class="social-link" ...>
```

**X (Twitter)** (linha ~286):
```html
<a href="https://x.com/seu-usuario" class="social-link" ...>
```

### Alterar Cor de Destaque

**No CSS** (linha ~108):
```css
.accent-text {
    color: #FF5F5F;  /* ← Sua cor aqui */
}
```

**No Tailwind Config** (linha ~200):
```javascript
colors: {
    salmon: "#FF5F5F",  /* ← Cor de destaque principal */
}
```

## ⚙️ Ajustes de Performance

### Velocidade da Animação

```javascript
scrollSensitivity: 1.5,  // Padrão

// Exemplos:
// 0.5  = Muito lento (precisa rolar muito)
// 1.0  = Velocidade padrão
// 2.0  = Rápido
// 3.0  = Muito rápido
```

### Otimizar Frames WebP

Para reduzir o tamanho dos arquivos:

```bash
# Instalar cwebp (Google WebP Tools)
# Ubuntu/Debian:
sudo apt-get install webp

# macOS:
brew install webp

# Otimizar frames:
for i in *.webp; do
  cwebp -q 85 "$i" -o "optimized_$i"
done
```

**Qualidades recomendadas:**
- `q 95` - Alta qualidade (~500KB por frame)
- `q 85` - Boa qualidade (~200KB por frame) ← **Recomendado**
- `q 75` - Qualidade média (~100KB por frame)

### Reduzir Número de Frames

Se a animação estiver pesada:

- **60 frames** = Mais leve, ainda suave
- **120 frames** = Equilíbrio perfeito ← **Recomendado**
- **240 frames** = Ultra-suave (pode ser excessivo)

## 🐛 Troubleshooting

### Frames não aparecem

**Problema**: Tela preta ou frames não carregam.

**Soluções**:
1. Abra o Console do navegador (F12)
2. Verifique erros de caminho no Console
3. Teste acessar um frame diretamente: `http://localhost:8000/frames/frame-001.webp`
4. Confirme que `frameBasePath` está correto
5. Verifique permissões dos arquivos

### Animação muito rápida/lenta

**Problema**: Scroll avança muitos ou poucos frames.

**Solução**:
```javascript
// Mais lento:
scrollSensitivity: 0.8,

// Mais rápido:
scrollSensitivity: 2.5,
```

### Loading demora muito

**Problema**: Página fica muito tempo no "Carregando frames...".

**Soluções**:
1. Reduza `totalFrames` temporariamente para testar
2. Otimize os frames WebP (comprima mais)
3. Use CDN para servir os frames
4. Ajuste `preloadBatchSize` para 5 (carrega menos por vez)

### Frames aparecem borrados

**Problema**: Qualidade ruim dos frames.

**Soluções**:
1. Use frames de pelo menos 1920x1080 (Full HD)
2. Aumente a qualidade na compressão WebP (q 90-95)
3. Considere usar PNG (maior qualidade, mas arquivos maiores)

## 📁 Estrutura de Arquivos

```
web/
├── contato.html              # Página principal de contato
├── frames/                   # Diretório para frames WebP
│   ├── frame-001.webp
│   ├── frame-002.webp
│   └── ...
├── setup_frames.py          # Script auxiliar para organizar frames
├── CONTATO_SETUP.md         # Guia detalhado de setup
└── README_CONTATO.md        # Esta documentação
```

## 🎯 Próximos Passos

1. ✅ Página criada e configurada
2. ⏳ **Adicionar seus frames WebP** (use `setup_frames.py`)
3. ⏳ **Configurar PARALLAX_CONFIG** com seus parâmetros
4. ⏳ **Personalizar textos e links sociais**
5. ⏳ **Testar em diferentes dispositivos**
6. ✅ **Deploy!**

## 📞 Suporte

Se precisar de ajuda:

- 📧 **Email**: contato@automacoescomerciais.com.br
- 📂 **Documentação**: Ver `CONTATO_SETUP.md` para guia detalhado
- 🐍 **Script**: Use `python web/setup_frames.py` para assistência

## 🎨 Design System

A página segue o mesmo design system do Cleudocode:

- **Cores**:
  - Primary: `#FF5F5F` (Salmon)
  - Secondary: `#4F46E5` (Sentient)
  - Background: `#02030a` (Dark)
  - Surface: `#080808`

- **Tipografia**:
  - Font Family: Inter (sans-serif)
  - Mono: Fira Code

- **Efeitos**:
  - Glassmorphism (backdrop blur)
  - Smooth transitions
  - Hover effects

---

**Desenvolvido com ❤️ para Automações Comerciais Integradas**

© 2025 Automações Comerciais Integradas. Todos os direitos reservados.
