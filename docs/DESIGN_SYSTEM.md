# Market Predictor – Design System

## Brand Identity

**Market Predictor** is a bold, energetic trading platform that combines data confidence with actionable intelligence. The visual identity reflects trading-floor urgency, professional authority, and lightning-fast decision-making.

### Mission
Give traders the confidence to act fast, backed by machine learning, technical analysis, and real-time market intelligence.

---

## Color Palette

All colors work in dark mode (premium, tech-forward aesthetic).

### Primary Colors

| Name | Hex | Usage | Contrast |
|------|-----|-------|----------|
| **Bullish Green** | `#10B981` | Bullish signals, CTAs, positive metrics, growth | WCAG AAA (on navy) |
| **Bearish Red** | `#EF4444` | Bearish signals, warnings, declines | WCAG AAA (on navy) |
| **Gold Accent** | `#FBBF24` | Highlights, opportunities, section dividers | WCAG AA (on navy) |
| **Deep Navy** | `#0F172A` | Primary background, trust, premium | N/A (dark bg) |

### Neutrals

| Name | Hex | Usage |
|------|-----|-------|
| **Gray Dark** | `#111827` | Secondary backgrounds, cards |
| **Slate** | `#1F2937` | Text secondary, borders, subtle elements |
| **Border** | `#2D3748` | Dividers, outlines, structure |
| **Text Primary** | `#F9FAFB` | Headlines, primary text |
| **Text Secondary** | `#D1D5DB` | Body text, labels, descriptions |
| **Light Gray** | `#F3F4F6` | Backgrounds (light mode fallback) |

### Gradients

- **Bullish Gradient**: `linear-gradient(135deg, #10B981, #059669)` – success, confidence
- **Gold Gradient**: `linear-gradient(135deg, #FBBF24, #F59E0B)` – opportunity, highlight
- **Background Gradient**: `linear-gradient(135deg, #0F172A, #1a2a4a)` – depth, premium

---

## Typography

### Font Stack

```css
Display & Headlines: 'Inter', sans-serif (700, 600, 500)
Body & UI Text: 'Inter', sans-serif (400, 500, 600)
Data / Numbers: 'JetBrains Mono', monospace (400, 600)
```

**Why Inter + JetBrains Mono:**
- **Inter** is geometric, modern, and highly legible at small sizes (UI density)
- **JetBrains Mono** gives data personality — numbers stand out, trades feel technical
- Both have extensive language support (global traders)

### Type Scale

| Element | Size | Weight | Line Height | Letter Spacing | Example Usage |
|---------|------|--------|-------------|----------------|----------------|
| **Logo** | 18px | 700 | 1.2 | -0.5px | Header branding |
| **H1 (Symbol)** | 32px | 700 | 1.1 | -1px | "AAPL" – asset name |
| **H2 (Section)** | 16px | 700 | 1.2 | 0px | Card titles, section headers |
| **H3 (Label)** | 14px | 700 | 1.3 | 0.5px | Table headers, metric labels |
| **Body Large** | 14px | 400 | 1.6 | 0px | Main text, descriptions |
| **Body** | 12px | 400 | 1.6 | 0px | Most UI labels, buttons |
| **Body Small** | 11px | 500 | 1.5 | 0.5px | Eyebrow labels (uppercase) |
| **Mono (Data)** | 13-24px | 400-600 | 1.2 | 0px | Prices, percentages, numbers |

### Text Hierarchy Rules

1. **Headlines are bold, lowercase**: "Market Predictor" (not "MARKET PREDICTOR")
2. **Uppercase only for labels**: "Model Confidence", "Bullish Signal" (UI clarity)
3. **Mono numbers always**: Prices, percentages, dates (e.g., `67%`, `$198.50`)
4. **Line length max 75 characters** (readability, especially on mobile)

---

## Spacing & Layout

### Spacing Scale

```css
--spacing-xs: 0.5rem (8px)    /* tight gaps, compact items */
--spacing-sm: 1rem (16px)     /* standard padding, small gaps */
--spacing-md: 1.5rem (24px)   /* section gaps, card padding */
--spacing-lg: 2rem (32px)     /* major section gaps */
--spacing-xl: 3rem (48px)     /* top-level spacing */
```

### Border Radius

```css
--radius-sm: 6px      /* small interactive elements, tags */
--radius-md: 12px     /* cards, input fields */
--radius-lg: 16px     /* large containers, hero sections */
```

### Grid & Layout

**Desktop (3-column):**
- Sidebar (280px) | Main (1fr) | Right Sidebar (320px)
- Gap: 24px (spacing-lg)

**Tablet (1-column):**
- Sidebar collapses (hamburger menu)
- Main takes full width
- Right sidebar moves below

**Mobile (1-column):**
- Sidebar hidden by default
- Single-column layout
- Right sidebar collapses

### Shadows

```css
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3)    /* subtle depth */
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4)   /* cards, modals */
--shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.5)  /* floating elements */
```

---

## Component Library

### Buttons

#### Primary CTA (Green)
```css
Background: linear-gradient(135deg, #10B981, #059669)
Color: #0F172A (navy)
Padding: 12px 16px
Border-radius: 6px
Font: 700 12px Inter
Text: UPPERCASE with letter-spacing 0.5px
Hover: translateY(-2px), shadow-md
```

**Use for:** "Analyze & Blend", "View Signal", "Refresh"

#### Secondary (Ghost)
```css
Background: rgba(255, 255, 255, 0.05)
Border: 1px solid #2D3748
Color: #D1D5DB
Padding: 8px 12px
Hover: Background rgba(16, 185, 129, 0.1), border-color #10B981, color #10B981
```

**Use for:** "Refresh", "Export", secondary actions

#### Signal Badge
```css
Bullish: 
  Background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05))
  Border: 1px solid #10B981
  Color: #10B981

Bearish:
  Background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.05))
  Border: 1px solid #EF4444
  Color: #EF4444

Font: 700 16px Inter, UPPERCASE, letter-spacing 0.5px
Padding: 12px 16px
Includes pulsing dot (animation)
```

### Cards

#### Standard Card
```css
Background: rgba(31, 41, 55, 0.6)
Border: 1px solid #2D3748
Border-radius: 16px
Padding: 24px
Box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4)
Hover: slight background lightening (rgba increase by 0.05)
```

#### Hero Card (Chart Container)
```css
Same as standard + larger padding (32px)
Chart background: rgba(0, 0, 0, 0.2) with inner border
Min-height: 380px
```

#### Metric Card (smaller, data-focused)
```css
Background: rgba(31, 41, 55, 0.4)
Border: 1px solid #2D3748
Padding: 16px
Border-radius: 12px
No shadow (lighter weight)
```

### Inputs

#### Text Area (Material Input)
```css
Background: rgba(0, 0, 0, 0.3)
Border: 1px solid #2D3748
Padding: 12px
Border-radius: 6px
Font: 12px Inter, line-height 1.5
Color: #F9FAFB
Placeholder: #D1D5DB
Focus: border-color #10B981, box-shadow 0 0 0 3px rgba(16, 185, 129, 0.1)
Min-height: 100px
```

### Tables

#### Signal Table
```css
Header:
  Background: rgba(0, 0, 0, 0.3)
  Font: 700 11px Inter, UPPERCASE, letter-spacing 0.5px
  Color: #D1D5DB
  Padding: 16px
  Border-bottom: 1px solid #2D3748

Row:
  Padding: 16px
  Border-bottom: 1px solid #2D3748
  Hover: background rgba(16, 185, 129, 0.05)
  Font: 12px Inter
  
Grid: 4 columns (100px, 1fr, 80px, 100px)
```

### Badge / Tag

#### Signal Confidence (Small)
```css
Bullish:
  Background: rgba(16, 185, 129, 0.3)
  Color: #10B981
  
Bearish:
  Background: rgba(239, 68, 68, 0.3)
  Color: #EF4444

Font: 700 10px Inter, UPPERCASE
Padding: 2px 6px
Border-radius: 3px
```

---

## Icons & Visual Elements

### Icon Style: Minimal, Bold
- Use emoji for quick brand recognition (📈, 📊, 🎯, 💼)
- SVG icons for technical elements (charts, patterns, indicators)
- Stroke weight: 2-2.5px for balance at 16-24px sizes
- Color: Inherit from context (green for bullish, red for bearish)

### Logo
```
Icon: Gradient square (gold → green), contains "📈" or stylized candlestick
Text: "Market Predictor" in Inter 700 18px, no styling
Spacing: 12px between icon and text
```

### Animations

#### Pulse (Signal Dot)
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
Duration: 2s
Infinite
```

#### Hover (Buttons)
```css
Translate Y: -2px
Box-shadow: shadow-md
Duration: 0.3s ease-out
```

#### Focus (Inputs)
```css
Border-color: #10B981
Box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1)
Duration: 0.2s
```

---

## Interaction Patterns

### Signal Display

**Bullish Signal:**
- Green badge with pulsing dot
- "↑" indicator (optional)
- Positive metric colors (green text)

**Bearish Signal:**
- Red badge with pulsing dot
- "↓" indicator (optional)
- Negative metric colors (red text)

### Data Presentation

**Numbers:**
- Always monospace (JetBrains Mono)
- Include % or $ symbols for context
- Use consistent decimal places (e.g., 67%, $198.50)

**Asset Names:**
- Symbol (ticker) in bold, large (32px H1)
- Class/exchange in small caps below (11px, uppercase)

### Navigation

**Sidebar:**
- Category labels (uppercase, 11px, letter-spacing 1px)
- Hover state: slight background tint, border highlight
- Active state: stronger tint + bold text
- Confidence badges on each item

### Material Input Flow

1. User pastes text in textarea
2. "Analyze & Blend" button is prominent (green CTA)
3. Button click → API request
4. Result updates signal badge (if material shifts probability)
5. Toast confirmation or error message appears

---

## Accessibility (WCAG 2.1 AA)

- **Color Contrast**: All text meets WCAG AA (4.5:1 on dark backgrounds)
- **Focus States**: Visible keyboard focus on all interactive elements
- **Motion**: Respects `prefers-reduced-motion` (disable pulsing animations)
- **Typography**: Min 12px for body text, 1.6 line-height for readability
- **Touch Targets**: Min 44px for interactive elements on mobile

### Keyboard Navigation
- Tab through sidebar → main card → metrics → signals table → right sidebar
- Enter/Space to activate buttons
- Arrow keys to navigate signals table rows (future)

---

## Dark Mode Only

This design is **dark-first** (no light mode currently). All colors tested on `#0F172A` background. If light mode is needed:

1. Invert neutrals (text light → dark, backgrounds dark → light)
2. Keep signal colors (green/red are accessible in light mode)
3. Reduce opacity overlays (e.g., `rgba(0, 0, 0, 0.3)` → `rgba(0, 0, 0, 0.1)`)
4. Test contrast again (aim for WCAG AA minimum)

---

## Responsive Breakpoints

```css
Desktop: 1400px+ (3-column layout)
Tablet: 1024px–1399px (1-column, right sidebar below)
Mobile: < 1024px (full-width, hamburger navigation)
```

---

## File Structure

```
market-predictor-ui/
├── index.html                 # Main dashboard (styled inline)
├── DESIGN_SYSTEM.md           # This file
├── logo.svg                   # Logo (to create)
├── favicon.ico                # Favicon (to create)
├── assets/
│   ├── icons/                 # SVG icon set
│   └── illustrations/         # Charts, patterns
└── styles/
    └── variables.css          # Reusable CSS variables
```

---

## Developer Quick Start

### CSS Variables (Copy to Your CSS)

```css
:root {
  --color-bullish: #10B981;
  --color-bearish: #EF4444;
  --color-navy: #0F172A;
  --color-gold: #FBBF24;
  --color-slate: #1F2937;
  --color-gray-dark: #111827;
  --color-gray-light: #F3F4F6;
  --color-border: #2D3748;
  --color-text-primary: #F9FAFB;
  --color-text-secondary: #D1D5DB;
  
  --font-display: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 1.5rem;
  --spacing-lg: 2rem;
  --spacing-xl: 3rem;
  
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;
  
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.5);
}
```

### Font Import

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
```

---

## Brand Voice & Tone

**Market Predictor speaks with:**
- **Confidence**: No hedging. "Bullish" not "probably bullish"
- **Urgency**: Action words. "View Signal", "Analyze & Blend"
- **Clarity**: Plain language. "Model Confidence" not "Probabilistic Output"
- **Authority**: Data-backed. Metrics, percentages, historical win rates
- **Minimal fluff**: Every word serves a purpose

---

## Next Steps

1. ✅ Create logo (gradient square with candlestick)
2. ✅ Export color palette as Figma/design tool library
3. Create SVG icon set (15+ icons for patterns, indicators)
4. Build component Storybook (React/Storybook optional)
5. Document API integration patterns
6. Create animation specs for chart interactions
7. Design landing page (homepage.html) using same system

---

**Design System Version**: 1.0  
**Last Updated**: Sept 22, 2026  
**Status**: Active & evolving with product
