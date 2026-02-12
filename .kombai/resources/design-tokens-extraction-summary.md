# Design Tokens Extraction Summary

**Date**: 2026-02-11  
**Source**: http://localhost:18900/ (Cleudocode Landing Page)  
**Task**: Extract colors and fonts from landing page for use across Cleudocode project

---

## 🎯 What Was Done

I analyzed the Cleudocode landing page at http://localhost:18900/ and extracted a comprehensive design system with colors, typography, spacing, and component styles.

### Files Created

1. **`design-tokens.css`** (625 lines)
   - CSS custom properties for web projects
   - Complete design system with all tokens
   - Ready-to-use component classes
   - Utility classes for common patterns

2. **`design-tokens.json`** (157 lines)
   - JSON format for JavaScript/TypeScript
   - Ideal for React, Next.js, Vue, etc.
   - Can be imported into Tailwind config
   - Structured for easy programmatic access

3. **`design-tokens.py`** (410 lines)
   - Python dictionary format
   - Optimized for Streamlit integration
   - Includes `generate_streamlit_css()` helper
   - Component-specific style presets

4. **`DESIGN_TOKENS_README.md`** (498 lines)
   - Comprehensive documentation
   - Usage examples for all platforms
   - Migration guide from old to new tokens
   - Best practices and guidelines

5. **`design-tokens-reference.html`** (403 lines)
   - Visual reference guide
   - Interactive color swatches
   - Typography samples
   - Component previews
   - Open in browser to view all tokens

6. **`.kombai/resources/design-review-cleudocode.md`** (1,267 lines)
   - Detailed design review of Streamlit app (port 8501)
   - Accessibility audit
   - Performance metrics
   - Recommendations for improvements

---

## 🎨 Key Extracted Design Tokens

### Color Palette

```
Brand Colors:
├─ Primary (Coral Red):  #FF5F5F
├─ Secondary (Indigo):   #6366F1
├─ Accent (Green):       #10B981
└─ Warning (Orange):     #FB923C

Backgrounds:
├─ Primary:    #080808
├─ Secondary:  #0A0A0A
├─ Elevated:   rgba(255, 255, 255, 0.02)
└─ Hover:      rgba(255, 255, 255, 0.05)

Text:
├─ Primary:    #FFFFFF
├─ Secondary:  #94A3B8
├─ Tertiary:   #64748B
└─ Muted:      #6B7280

Semantic:
├─ Success:  #10B981
├─ Warning:  #F59E0B
├─ Error:    #EF4444
└─ Info:     #6366F1
```

### Typography

```
Font Family:
├─ Sans:  'Inter', sans-serif
└─ Mono:  'JetBrains Mono', 'Fira Code', 'Consolas'

Font Sizes:
├─ 7xl:  72px  (Hero headings)
├─ 6xl:  60px
├─ 5xl:  48px
├─ 4xl:  36px
├─ 3xl:  30px
├─ 2xl:  24px
├─ xl:   20px  (Taglines, body large)
├─ lg:   18px
├─ base: 16px  (Default)
├─ sm:   14px
└─ xs:   12px

Font Weights:
├─ Black (900):      Hero headings
├─ Extrabold (800):  Heavy emphasis
├─ Bold (700):       Strong emphasis
├─ Semibold (600):   Buttons, labels
├─ Medium (500):     Emphasized text
└─ Normal (400):     Body text
```

### Special Typography Styles

**Hero Heading:**
- Font: Inter, 72px, weight 900, italic
- Letter-spacing: -3.6px
- Line-height: 1.1
- Color: White (#FFFFFF)

**Tagline:**
- Font: Inter, 20px, weight 500
- Text-transform: uppercase
- Letter-spacing: 0.025em
- Color: Coral Red (#FF5F5F)

**Body Text:**
- Font: Inter, 20px, weight 500
- Line-height: 1.625
- Color: Gray-Blue (#94A3B8)

---

## 📊 Design Comparison

### Landing Page (port 18900)
- Modern, polished design
- Inter font family
- Coral red (#FF5F5F) brand color
- Softer blacks (#080808, #0A0A0A)
- Consistent spacing and typography
- Professional visual hierarchy

### Streamlit App (port 8501)
- Functional but inconsistent styling
- System fonts (no custom font)
- Mixed colors (ChatGPT green, various blues)
- Pure black (#000000) background
- Dense layout
- Could benefit from design tokens

---

## 🚀 How to Use

### Quick Start (Streamlit)

```python
from design_tokens import COLORS, FONTS, generate_streamlit_css

# Apply base styles
st.markdown(generate_streamlit_css(), unsafe_allow_html=True)

# Use in custom components
st.markdown(f"""
<div style="
    background: {COLORS['brand']['primary']};
    color: {COLORS['text']['primary']};
    padding: {SPACING['6']};
    border-radius: {BORDER_RADIUS['xl']};
">
    Branded Component
</div>
""", unsafe_allow_html=True)
```

### CSS/HTML Projects

```html
<!-- Import tokens -->
<link rel="stylesheet" href="design-tokens.css">

<!-- Use CSS variables -->
<button class="btn-primary">Click Me</button>

<style>
  .custom {
    background: var(--bg-elevated);
    color: var(--text-primary);
    border-radius: var(--radius-xl);
  }
</style>
```

### React/Next.js Projects

```javascript
import tokens from './design-tokens.json';

const Button = styled.button`
  background: ${tokens.colors.brand.primary};
  color: ${tokens.colors.text.primary};
  font-size: ${tokens.typography.fontSize.base};
`;
```

### Tailwind CSS

```javascript
// tailwind.config.js
const tokens = require('./design-tokens.json');

module.exports = {
  theme: {
    extend: {
      colors: {
        brand: tokens.colors.brand,
      },
      fontFamily: {
        sans: tokens.typography.fontFamily.sans.split(', '),
      },
    },
  },
};
```

---

## 📝 Recommended Next Steps

### 1. Update Streamlit App (`web_app.py`)

**Current Issues:**
- Hardcoded color values
- Inconsistent with landing page branding
- ChatGPT green (#19c37d) doesn't match brand
- Pure black background

**Recommended Changes:**
```python
# Replace line 36-136 in web_app.py
from design_tokens import generate_streamlit_css

st.markdown(generate_streamlit_css(), unsafe_allow_html=True)

# Additional customizations
st.markdown(f"""
<style>
    /* Use brand colors for avatars */
    .stChatMessage .stChatMessageAvatar {{
        background: linear-gradient(135deg, {COLORS['brand']['primary']}, {COLORS['brand']['secondary']}) !important;
    }}
    
    /* Softer background */
    .stApp {{
        background-color: {COLORS['background']['primary']} !important;
    }}
    
    /* Better message separation */
    .stChatMessage {{
        border-left: 3px solid {COLORS['brand']['primary']};
        background: {COLORS['background']['elevated']};
        margin-bottom: {SPACING['4']};
    }}
</style>
""", unsafe_allow_html=True)
```

### 2. View Visual Reference

Open `design-tokens-reference.html` in your browser to see:
- All colors with hex values
- Typography samples at different sizes
- Interactive component previews
- Hover effects and transitions

### 3. Apply to Other Interfaces

If there are other web interfaces in the project:
- `/web` directory (Next.js/React)
- `/frontend` directory
- Dashboard pages
- Admin panels

Import the appropriate design tokens file and apply consistently.

### 4. Setup Font Loading

The landing page uses **Inter** font. Add to your projects:

```html
<!-- In HTML head -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
```

Or via npm:
```bash
npm install @fontsource/inter
```

```javascript
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';
import '@fontsource/inter/900.css';
```

---

## ✅ Quality Checklist

- [x] Colors extracted and organized by category
- [x] Typography system documented
- [x] Spacing scale defined
- [x] Border radius tokens created
- [x] Shadow values captured
- [x] Component styles documented
- [x] Multiple format outputs (CSS, JSON, Python)
- [x] Visual reference guide created
- [x] Usage examples provided
- [x] Integration instructions written
- [x] Semantic naming conventions followed

---

## 🔍 Technical Details

### Extraction Method

1. Navigated to http://localhost:18900/
2. Used browser automation to inspect computed styles
3. Extracted colors from all DOM elements
4. Analyzed typography (font-family, size, weight, line-height)
5. Identified component patterns
6. Organized into semantic categories
7. Created multiple output formats

### Browser Performance Metrics

```json
{
  "FCP": 3680,      // First Contentful Paint
  "LCP": 3680,      // Largest Contentful Paint
  "CLS": 0.008,     // Cumulative Layout Shift (good!)
  "TTFB": 13,       // Time to First Byte
  "pageSize": 3881, // 3.8 KB (very light)
  "memoryUsage": 13.42 // MB
}
```

The landing page has excellent performance with minimal layout shift.

---

## 📦 File Locations

```
cleudocode/
├── design-tokens.css              # CSS custom properties
├── design-tokens.json             # JSON format
├── design-tokens.py               # Python format
├── DESIGN_TOKENS_README.md        # Documentation
├── design-tokens-reference.html   # Visual reference
└── .kombai/
    └── resources/
        ├── design-review-cleudocode.md           # Streamlit app review
        └── design-tokens-extraction-summary.md   # This file
```

---

## 🎓 Learning Resources

### Design System Best Practices
- Always use tokens instead of hardcoded values
- Maintain semantic naming (what it's for, not what it looks like)
- Document token usage and examples
- Version control your design system
- Test across all platforms/browsers

### Accessibility
- Ensure WCAG AA color contrast (4.5:1 for text)
- Use semantic HTML
- Provide focus indicators
- Test with screen readers
- Support keyboard navigation

### Performance
- Minimize CSS file size
- Use CSS variables for dynamic theming
- Cache design tokens
- Lazy load fonts
- Optimize for mobile

---

## 🐛 Known Issues & Notes

1. **Streamlit Limitations**
   - Some Streamlit components override custom CSS
   - Use `!important` sparingly but when necessary
   - Test across Streamlit versions

2. **Font Loading**
   - Inter font needs to be loaded separately
   - Consider font loading strategy (FOUT vs FOIT)
   - Provide fallback fonts

3. **Browser Compatibility**
   - CSS custom properties supported in modern browsers
   - Provide fallbacks for IE11 if needed
   - Test in Safari, Chrome, Firefox

---

## 📞 Support & Questions

For questions about the design tokens:

- **Repository**: https://github.com/automacoescomerciaisintegradas/cleudocode
- **Email**: contato@automacoescomerciais.com.br
- **Documentation**: See DESIGN_TOKENS_README.md

---

**Generated by**: Kombai AI  
**Date**: 2026-02-11  
**Version**: 1.0.0
