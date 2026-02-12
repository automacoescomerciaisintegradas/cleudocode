# 📧 Página de Contato - Guia de Configuração

## 🎬 Como Adicionar Seus Frames WebP

A página de contato (`web/contato.html`) está pronta e configurada para animação de paralaxe cinematográfica controlada por scroll. Siga os passos abaixo para adicionar sua sequência de frames WebP.

### Passo 1: Preparar os Frames

1. **Baixe seus frames WebP** dos links fornecidos:
   - https://62e8a90b2b0a16b3b8c4098924d1a273.r2.cloudflarestorage.com/webp
   - https://drive.google.com/file/d/1K_9emcUqs1Ro5k2zEnjLkrtW7uski5ac/view?usp=sharing

2. **Organize os frames** em uma sequência numerada:
   ```
   frame-001.webp
   frame-002.webp
   frame-003.webp
   ...
   frame-120.webp
   ```

### Passo 2: Adicionar Frames ao Projeto

Crie uma pasta para os frames e adicione-os:

```bash
# Opção 1: Criar pasta dentro de web/
mkdir web/frames
# Copie todos os seus frames WebP para web/frames/

# Opção 2: Criar pasta public/ (se estiver usando servidor Flask)
mkdir public/frames
# Copie todos os seus frames WebP para public/frames/
```

### Passo 3: Configurar o JavaScript

Abra `web/contato.html` e localize a seção `PARALLAX_CONFIG` (linha ~270):

```javascript
const PARALLAX_CONFIG = {
    frameBasePath: '/frames/',      // ← Caminho para sua pasta de frames
    framePrefix: 'frame-',          // ← Prefixo dos seus arquivos
    frameExtension: '.webp',        // ← Extensão dos arquivos
    totalFrames: 120,               // ← Número total de frames na sequência
    framePadding: 3,                // ← Dígitos no número (001 = 3, 0001 = 4)
    
    scrollSensitivity: 1.5,         // ← Ajuste para velocidade da animação
    preloadBatchSize: 10,
};
```

**Ajuste os valores conforme sua sequência:**

- Se seus frames são `A_smooth_cinematic_001.webp` a `A_smooth_cinematic_120.webp`:
  ```javascript
  frameBasePath: '/frames/',
  framePrefix: 'A_smooth_cinematic_',
  totalFrames: 120,
  framePadding: 3,
  ```

- Se seus frames estão em pasta diferente:
  ```javascript
  frameBasePath: '/assets/parallax-frames/',  // Exemplo
  ```

### Passo 4: Ajustar Sensibilidade do Scroll

Para tornar a animação mais suave ou mais rápida:

```javascript
scrollSensitivity: 1.5,  // Padrão
// 0.5  = Muito lento (mais scroll necessário para avançar frames)
// 1.0  = Velocidade padrão
// 2.0  = Rápido (menos scroll necessário)
// 3.0  = Muito rápido
```

### Passo 5: Testar a Página

1. **Via Flask server** (se estiver rodando):
   ```
   http://localhost:18900/contato.html
   ```

2. **Via servidor local simples**:
   ```bash
   cd web
   python -m http.server 8000
   ```
   Acesse: `http://localhost:8000/contato.html`

3. **Diretamente no navegador**:
   - Abra `web/contato.html` diretamente
   - ⚠️ Pode não funcionar devido a CORS (use servidor)

---

## 🎨 Personalização

### Alterar Textos

No arquivo `contato.html`, procure por:

```html
<!-- Introduction Line -->
<p class="text-sm md:text-base font-medium accent-text mb-4 tracking-wide">
    Olá, bem-vindo(a) à  <!-- ← Edite aqui -->
</p>

<!-- Main Heading -->
<h1 class="text-4xl md:text-6xl lg:text-7xl font-black text-white leading-tight mb-6">
    Automações Comerciais<br/>  <!-- ← Edite aqui -->
    Integradas
</h1>
```

### Alterar Links Sociais

Procure pela seção `<!-- Bottom Section - Social Links -->`:

```html
<!-- YouTube -->
<a href="https://youtube.com/@seu-canal" class="social-link" ...>

<!-- Instagram -->
<a href="https://instagram.com/seu-perfil" class="social-link" ...>

<!-- X (Twitter) -->
<a href="https://x.com/seu-usuario" class="social-link" ...>
```

### Alterar Cores de Destaque

A cor de destaque atual é **Salmon (#FF5F5F)**. Para mudar:

1. Procure por `.accent-text` no `<style>`:
   ```css
   .accent-text {
       color: #FF5F5F;  /* ← Altere aqui */
   }
   ```

2. Ou altere diretamente no Tailwind config:
   ```javascript
   tailwind.config = {
       theme: {
           extend: {
               colors: {
                   salmon: "#FF5F5F",  /* ← Sua cor aqui */
               }
           }
       }
   };
   ```

---

## 🐛 Troubleshooting

### Frames não aparecem / Ficam pretos

**Problema**: Os frames não estão sendo carregados corretamente.

**Soluções**:
1. Verifique o caminho no `frameBasePath`
2. Abra o Console do navegador (F12) e veja os erros
3. Confirme que os nomes dos arquivos estão corretos
4. Teste acessando um frame diretamente: `http://localhost:8000/frames/frame-001.webp`

### Animação muito rápida/lenta

**Problema**: O scroll avança muitos ou poucos frames.

**Solução**:
Ajuste `scrollSensitivity` no `PARALLAX_CONFIG`:
- **Mais lento**: diminua o valor (ex: 0.8)
- **Mais rápido**: aumente o valor (ex: 2.5)

### Página demora para carregar

**Problema**: Muitos frames para carregar de uma vez.

**Solução**:
1. Reduza `totalFrames` temporariamente para testar
2. Otimize seus frames WebP (comprima-os mais)
3. Ajuste `preloadBatchSize` para carregar menos frames por vez

### Frames aparecem borrados

**Problema**: Qualidade ruim dos frames.

**Solução**:
1. Use frames WebP de alta qualidade (mínimo 1080p)
2. Verifique se não há dupla compressão
3. Considere usar PNG para melhor qualidade (mas arquivos maiores)

---

## 📱 Responsividade

A página foi desenvolvida para ser totalmente responsiva:

- **Desktop**: Hero em tela cheia com bordas arredondadas grandes
- **Tablet**: Ajuste automático de textos e espaçamentos
- **Mobile**: Bordas menores, textos otimizados, ícones sociais compactos

Teste em diferentes tamanhos de tela usando DevTools (F12 → Toggle Device Toolbar).

---

## 🚀 Performance

Para melhor performance:

1. **Otimize os frames WebP**:
   ```bash
   # Usando cwebp (Google WebP Tools)
   for i in *.webp; do
     cwebp -q 85 "$i" -o "optimized_$i"
   done
   ```

2. **Use um CDN** para servir os frames (opcional):
   ```javascript
   frameBasePath: 'https://seu-cdn.com/frames/',
   ```

3. **Reduza o número total de frames** se possível:
   - 60 frames = animação mais leve
   - 120 frames = animação mais suave
   - 240 frames = ultra-suave (pode ser excessivo)

---

## 📞 Contato

Se precisar de ajuda adicional com a configuração:

📧 **Email**: contato@automacoescomerciais.com.br

---

**Desenvolvido com ❤️ para Automações Comerciais Integradas**
