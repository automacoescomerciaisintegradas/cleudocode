# Cleudocode Design Tokens

Design tokens extracted from the Cleudocode landing page (http://localhost:18900/) to ensure consistent branding across all interfaces.

## 📁 Files

- **`design-tokens.css`** - CSS custom properties (CSS variables)
- **`design-tokens.json`** - JSON format for JavaScript/TypeScript projects
- **`design-tokens.py`** - Python dictionary format for Streamlit and other Python apps

## 🎨 Color Palette

### Brand Colors
- **Primary (Coral/Red)**: `#FF5F5F` - Main brand color, used for CTAs and accents
- **Secondary (Indigo)**: `#6366F1` - Secondary actions, links
- **Accent (Green)**: `#10B981` - Success states, positive feedback
- **Warning (Orange)**: `#FB923C` - Warnings, alerts

### Background Colors
- **Primary**: `#080808` - Main background (almost black)
- **Secondary**: `#0A0A0A` - Elevated surfaces
- **Tertiary**: `rgb(15, 22, 41)` - Special sections (dark blue-gray)

### Text Colors
- **Primary**: `#FFFFFF` - Headings, important text
- **Secondary**: `#94A3B8` - Body text (gray-blue)
- **Tertiary**: `#64748B` - Less important text
- **Muted**: `#6B7280` - Captions, metadata

### Status Colors
- **Success**: `#34D399` (Green)
- **Error**: `#FF5F5F` (Red)
- **Info**: `#818CF8` (Blue)
- **Warning**: `#FBBF24` (Orange)

## 📝 Typography

### Font Families
- **Sans-serif**: `'Inter', sans-serif` - Primary font for all UI
- **Monospace**: `'JetBrains Mono', 'Fira Code', 'Consolas', monospace` - Code, terminal

### Font Sizes
| Token | Size | Usage |
|-------|------|-------|
| `7xl` | 72px | Hero headings |
| `6xl` | 60px | Large headings |
| `5xl` | 48px | Section headings |
| `4xl` | 36px | Page titles |
| `3xl` | 30px | Card titles |
| `2xl` | 24px | Subheadings |
| `xl`  | 20px | Body large, taglines |
| `lg`  | 18px | Body medium |
| `base`| 16px | Default body text |
| `sm`  | 14px | Small text, captions |
| `xs`  | 12px | Tiny text, labels |

### Font Weights
- **Normal**: 400 - Regular body text
- **Medium**: 500 - Emphasized text
- **Semibold**: 600 - Buttons, labels
- **Bold**: 700 - Strong emphasis
- **Extrabold**: 800 - Heavy emphasis
- **Black**: 900 - Hero headings

### Typography Presets
- **Hero Heading**: 72px, weight 900, italic, letter-spacing -3.6px
- **Tagline**: 20px, weight 500, uppercase, red color
- **Body**: 20px, weight 500, gray-blue color

## 📐 Spacing Scale

| Token | Size | Pixels |
|-------|------|--------|
| `0` | 0 | 0px |
| `1` | 0.25rem | 4px |
| `2` | 0.5rem | 8px |
| `3` | 0.75rem | 12px |
| `4` | 1rem | 16px |
| `5` | 1.25rem | 20px |
| `6` | 1.5rem | 24px |
| `8` | 2rem | 32px |
| `10` | 2.5rem | 40px |
| `12` | 3rem | 48px |
| `16` | 4rem | 64px |
| `20` | 5rem | 80px |
| `24` | 6rem | 96px |

## 🔲 Border Radius

- **sm**: 2px - Small elements
- **base**: 4px - Default buttons
- **md**: 6px - Inputs
- **lg**: 8px - Buttons, badges
- **xl**: 12px - Cards (small)
- **2xl**: 16px - Cards (medium)
- **3xl**: 24px - Cards (large)
- **full**: 9999px - Circles, pills

## 🎭 Shadows

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.5);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.5);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.5);
```

## 🚀 Usage Examples

### CSS/HTML
```html
<!-- Import the CSS file -->
<link rel="stylesheet" href="design-tokens.css">

<!-- Use CSS variables -->
<button class="btn-primary">Click Me</button>

<style>
  .custom-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-2xl);
    padding: var(--space-6);
  }
</style>
```

### Python/Streamlit
```python
from design_tokens import COLORS, FONTS, generate_streamlit_css

# Apply base styles
st.markdown(generate_streamlit_css(), unsafe_allow_html=True)

# Use tokens in custom styles
st.markdown(f"""
<style>
    .hero-section {{
        background: {COLORS['background']['primary']};
        color: {COLORS['text']['primary']};
        font-family: {FONTS['family']['sans']};
        padding: {SPACING['12']};
    }}
    
    .brand-button {{
        background: {COLORS['brand']['primary']};
        color: {COLORS['text']['primary']};
        border-radius: {BORDER_RADIUS['lg']};
        padding: {SPACING['3']} {SPACING['6']};
        font-weight: {FONTS['weight']['semibold']};
    }}
</style>
""", unsafe_allow_html=True)

# Or use directly in components
st.button("Click Me", 
          help=f"Background: {COLORS['brand']['primary']}")
```

### JavaScript/React/Next.js
```javascript
import designTokens from './design-tokens.json';

// Use in styled-components
const Button = styled.button`
  background: ${designTokens.colors.brand.primary};
  color: ${designTokens.colors.text.primary};
  font-size: ${designTokens.typography.fontSize.base};
  font-weight: ${designTokens.typography.fontWeight.semibold};
  border-radius: ${designTokens.borderRadius.lg};
  padding: ${designTokens.spacing['3']} ${designTokens.spacing['6']};
`;

// Use in Tailwind config
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          primary: designTokens.colors.brand.primary,
          secondary: designTokens.colors.brand.secondary,
        }
      }
    }
  }
}
```

### Tailwind CSS Configuration
```javascript
// tailwind.config.js
const tokens = require('./design-tokens.json');

module.exports = {
  theme: {
    extend: {
      colors: {
        brand: tokens.colors.brand,
        bg: tokens.colors.background,
      },
      fontFamily: {
        sans: tokens.typography.fontFamily.sans.split(', '),
        mono: tokens.typography.fontFamily.mono.split(', '),
      },
      fontSize: tokens.typography.fontSize,
      spacing: tokens.spacing,
      borderRadius: tokens.borderRadius,
    },
  },
};
```

## 🎯 Component Examples

### Hero Section
```html
<div style="
  font-size: var(--font-7xl);
  font-weight: var(--font-black);
  font-style: italic;
  color: var(--text-primary);
  letter-spacing: -3.6px;
">
  CLEUDOCODE
</div>

<div style="
  font-size: var(--font-xl);
  color: var(--brand-primary);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
">
  THE AI THAT ACTUALLY DOES THINGS.
</div>
```

### Card Component
```html
<div class="card">
  <h3>Feature Title</h3>
  <p>Feature description goes here...</p>
</div>

<style>
.card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-2xl);
  padding: var(--space-6);
  transition: all var(--transition-base);
}

.card:hover {
  background: var(--bg-hover);
  transform: translateY(-2px);
}
</style>
```

### Icon Circle
```html
<div class="icon-circle">
  <svg><!-- icon SVG --></svg>
</div>

<style>
.icon-circle {
  width: 80px;
  height: 80px;
  background: var(--brand-primary);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
}
</style>
```

### Status Badges
```html
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Failed</span>

<style>
.badge {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
}

.badge-success {
  background: var(--color-success-bg);
  color: var(--status-green);
}
</style>
```

## 📦 Integration with Existing Streamlit App

To update `web_app.py` with these tokens:

```python
from design_tokens import COLORS, FONTS, SPACING, BORDER_RADIUS, generate_streamlit_css

# Replace existing CSS in st.markdown() with:
st.markdown(generate_streamlit_css(), unsafe_allow_html=True)

# Additional custom styles
st.markdown(f"""
<style>
    /* Chat Messages */
    .stChatMessage {{
        background: {COLORS['background']['elevated']};
        border-left: 3px solid {COLORS['brand']['primary']};
        padding: {SPACING['4']};
        border-radius: {BORDER_RADIUS['lg']};
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {COLORS['background']['secondary']};
        border-right: 1px solid {COLORS['border']['subtle']};
    }}
    
    /* Buttons */
    .stButton button {{
        background: {COLORS['brand']['primary']};
        color: {COLORS['text']['primary']};
        border-radius: {BORDER_RADIUS['lg']};
        font-weight: {FONTS['weight']['semibold']};
        padding: {SPACING['3']} {SPACING['6']};
    }}
</style>
""", unsafe_allow_html=True)
```

## 🔄 Design Comparison

### Before (Streamlit App - port 8501)
- **Background**: `#000000` (pure black)
- **Avatar**: `#19c37d` (ChatGPT green)
- **Inputs**: `#2f2f2f`
- **Font**: System default
- **Accent**: Mixed blues and greens

### After (Landing Page - port 18900)
- **Background**: `#080808` (softer black)
- **Brand Color**: `#FF5F5F` (coral red)
- **Inputs**: Transparent with subtle borders
- **Font**: Inter (modern, clean)
- **Accent**: Consistent coral red with indigo secondary

## 📝 Best Practices

1. **Always use tokens** instead of hardcoded values
2. **Use semantic naming** (e.g., `--bg-primary` not `--black`)
3. **Maintain hierarchy** (primary > secondary > tertiary)
4. **Test contrast** for accessibility (WCAG AA minimum)
5. **Document changes** when adding new tokens
6. **Keep consistency** across all platforms (web, mobile, desktop)

## 🔗 Related Files

- `/web_app.py` - Streamlit application
- `/.kombai/resources/design-review-cleudocode.md` - Detailed design review
- Web landing page source (check `/web` or `/frontend` directory)

## 📞 Support

For questions or suggestions about the design system:
- GitHub: https://github.com/automacoescomerciaisintegradas/cleudocode
- Email: contato@automacoescomerciais.com.br

---

**Last Updated**: 2026-02-11  
**Version**: 1.0.0  
**Extracted From**: http://localhost:18900/
