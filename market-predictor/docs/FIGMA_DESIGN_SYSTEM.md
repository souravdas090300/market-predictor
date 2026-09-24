# Market Predictor - Figma Design System Export Guide

This guide provides comprehensive documentation for exporting and implementing the Market Predictor design system in Figma.

## 🎨 Design System Overview

The Market Predictor design system is built with a professional dark theme optimized for financial data visualization and real-time trading interfaces.

### Core Design Principles

1. **Data-First Design**: Every component is designed to prioritize data clarity and readability
2. **Real-Time Performance**: Optimized for live data updates without visual clutter
3. **Professional Aesthetics**: Clean, modern interface that builds trust with users
4. **Accessibility**: High contrast ratios and clear visual hierarchy

## 🎯 Color Palette

### Primary Colors

```css
/* Brand Colors */
--color-bullish: #10B981;    /* Green for positive signals */
--color-bearish: #EF4444;    /* Red for negative signals */
--color-neutral: #FBBF24;     /* Yellow for neutral signals */
--color-navy: #0F172A;        /* Deep navy for backgrounds */
--color-gold: #FBBF24;       /* Gold for accents */

/* UI Colors */
--color-slate: #1F2937;       /* Secondary backgrounds */
--color-gray-dark: #111827;   /* Primary backgrounds */
--color-border: #2D3748;      /* Borders and dividers */
--color-text-primary: #F9FAFB; /* Primary text */
--color-text-secondary: #D1D5DB; /* Secondary text */
```

### Semantic Colors

```css
/* Success */
--color-success: #10B981;
--color-success-bg: rgba(16, 185, 129, 0.2);
--color-success-border: #10B981;

/* Error */
--color-error: #EF4444;
--color-error-bg: rgba(239, 68, 68, 0.2);
--color-error-border: #EF4444;

/* Warning */
--color-warning: #FBBF24;
--color-warning-bg: rgba(251, 191, 36, 0.2);
--color-warning-border: #FBBF24;

/* Info */
--color-info: #3B82F6;
--color-info-bg: rgba(59, 130, 246, 0.2);
--color-info-border: #3B82F6;
```

## 📐 Typography

### Font Families

```css
--font-body: 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;
--font-display: 'Inter', sans-serif;
```

### Type Scale

```css
/* Display */
--text-display-xl: 3rem;      /* 48px - Hero titles */
--text-display-lg: 2.25rem;   /* 36px - Page titles */
--text-display-md: 1.875rem;  /* 30px - Section titles */

/* Headings */
--text-heading-xl: 1.5rem;    /* 24px - Card titles */
--text-heading-lg: 1.25rem;   /* 20px - Subsection titles */
--text-heading-md: 1.125rem;  /* 18px - Component titles */
--text-heading-sm: 1rem;      /* 16px - Small headings */

/* Body */
--text-body-lg: 1rem;         /* 16px - Primary body text */
--text-body-md: 0.875rem;     /* 14px - Secondary body text */
--text-body-sm: 0.75rem;      /* 12px - Tertiary body text */

/* Mono */
--text-mono-lg: 0.875rem;     /* 14px - Large numbers */
--text-mono-md: 0.75rem;      /* 12px - Regular numbers */
--text-mono-sm: 0.625rem;     /* 10px - Small numbers */
```

### Font Weights

```css
--font-weight-light: 300;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

## 🧩 Component Library

### 1. Buttons

#### Primary Button
```
Width: Auto | Height: 48px
Padding: 12px 24px
Background: #10B981
Text: White, 600 weight
Border Radius: 8px
Hover: #059669
Active: #047857
```

#### Secondary Button
```
Width: Auto | Height: 48px
Padding: 12px 24px
Background: #1F2937
Text: White, 600 weight
Border: 1px solid #374151
Border Radius: 8px
Hover: #374151
```

#### Ghost Button
```
Width: Auto | Height: 40px
Padding: 8px 16px
Background: Transparent
Text: #D1D5DB, 500 weight
Border Radius: 6px
Hover: rgba(255,255,255,0.05)
```

### 2. Cards

#### Standard Card
```
Background: rgba(31, 41, 55, 0.5)
Border: 1px solid #2D3748
Border Radius: 16px
Padding: 24px
Shadow: 0 4px 6px rgba(0, 0, 0, 0.1)
```

#### Metric Card
```
Background: rgba(17, 24, 39, 0.5)
Border: 1px solid #2D3748
Border Radius: 12px
Padding: 16px
```

### 3. Inputs

#### Text Input
```
Height: 48px
Padding: 12px 16px
Background: #111827
Border: 1px solid #374151
Border Radius: 8px
Text: White
Focus: Border #10B981, Ring 2px rgba(16, 185, 129, 0.2)
```

#### Select Input
```
Height: 48px
Padding: 12px 16px
Background: #111827
Border: 1px solid #374151
Border Radius: 8px
Text: White
```

### 4. Navigation

#### Sidebar Item
```
Height: 48px
Padding: 12px
Background: Transparent
Border Radius: 8px
Hover: rgba(255,255,255,0.05)
Active: rgba(16, 185, 129, 0.12), Border #10B981
```

#### Header
```
Height: 70px
Background: rgba(17, 24, 39, 0.8)
Border Bottom: 1px solid #2D3748
Padding: 0 24px
```

## 📊 Data Visualization

### Chart Colors

```css
/* Line Charts */
--chart-line-primary: #10B981;
--chart-line-secondary: #3B82F6;
--chart-line-tertiary: #FBBF24;

/* Area Charts */
--chart-area-fill: rgba(16, 185, 129, 0.1);
--chart-area-stroke: #10B981;

/* Candlestick Charts */
--chart-bullish: #10B981;
--chart-bearish: #EF4444;
--chart-wick: #6B7280;

/* Grid Lines */
--chart-grid: #334155;
--chart-axis: #94A3B8;
```

### Signal Badges

```css
/* Bullish */
Background: rgba(16, 185, 129, 0.2)
Border: 1px solid #10B981
Text: #10B981

/* Bearish */
Background: rgba(239, 68, 68, 0.2)
Border: 1px solid #EF4444
Text: #EF4444

/* Neutral */
Background: rgba(251, 191, 36, 0.2)
Border: 1px solid #FBBF24
Text: #FBBF24
```

## 🎯 Icon System

### Icon Sizes

```css
--icon-xs: 16px;
--icon-sm: 20px;
--icon-md: 24px;
--icon-lg: 32px;
--icon-xl: 40px;
```

### Icon Colors

```css
--icon-primary: #F9FAFB;
--icon-secondary: #D1D5DB;
--icon-muted: #6B7280;
--icon-success: #10B981;
--icon-error: #EF4444;
--icon-warning: #FBBF24;
```

## 📱 Responsive Breakpoints

```css
--breakpoint-xs: 0px;
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;
```

## 🚀 Figma Export Instructions

### Step 1: Set Up Figma Design File

1. Create a new Figma file
2. Set up the following pages:
   - **Design System**: Colors, typography, components
   - **Dashboard**: Main interface layouts
   - **Components**: Individual component designs
   - **Responsive**: Mobile and tablet layouts

### Step 2: Create Color Variables

1. Go to the Design System page
2. Create color variables for all colors listed above
3. Organize them in collections:
   - `Brand Colors`
   - `Semantic Colors`
   - `UI Colors`
   - `Chart Colors`

### Step 3: Create Text Styles

1. Create text styles for the entire type scale
2. Name them consistently:
   - `Display/XL`
   - `Heading/LG`
   - `Body/MD`
   - `Mono/SM`

### Step 4: Build Component Library

1. Create components for each UI element
2. Use auto-layout for responsive components
3. Create component variants for different states
4. Document component properties

### Step 5: Export Assets

1. Select components to export
2. Choose appropriate export formats:
   - **SVG**: For icons and simple graphics
   - **PNG**: For complex images with transparency
   - **CSS**: For developers to copy styles
   - **React**: For direct component export

### Step 6: Share with Development Team

1. Create a shareable Figma link
2. Set appropriate permissions
3. Provide this documentation alongside the design file
4. Schedule a design handoff meeting

## 📋 Component Checklist

Use this checklist to ensure all components are properly documented:

- [ ] Buttons (Primary, Secondary, Ghost)
- [ ] Inputs (Text, Select, Textarea)
- [ ] Cards (Standard, Metric, Interactive)
- [ ] Navigation (Header, Sidebar, Breadcrumbs)
- [ ] Tables (Standard, Interactive, Sortable)
- [ ] Charts (Line, Bar, Candlestick, Heatmap)
- [ ] Modals (Standard, Full-screen)
- [ ] Alerts (Success, Error, Warning, Info)
- [ ] Loaders (Spinner, Skeleton, Progress)
- [ ] Badges (Signal, Status, Notification)

## 🎨 Best Practices

### Spacing
- Use consistent spacing scale: 4px, 8px, 12px, 16px, 24px, 32px, 48px
- Maintain 8px baseline grid
- Use consistent padding within component groups

### Borders
- Standard border radius: 8px
- Large border radius: 16px
- Small border radius: 6px
- Border width: 1px standard, 2px for focus states

### Shadows
- Subtle: `0 
