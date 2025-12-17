# Proof of Consideration - Design System
## Inspired by Mathematical Precision & Calm Interfaces

**Version**: 1.0
**Last Updated**: December 2025

---

## 🎨 Design Philosophy

### Core Principles

1. **Mathematical Precision**: Every element follows strict geometric ratios and spacing rules
2. **Calm & Focused**: Minimal distractions, let the content breathe
3. **Soft Contrast**: No harsh whites or deep blacks - everything is softened
4. **Information Density**: Show what matters, hide what doesn't
5. **Subtle Sophistication**: Micro-interactions are gentle, never aggressive

### Visual DNA

- **Dark-first palette** with soft, muted tones
- **Rounded corners** (8px standard) for approachability
- **Generous whitespace** (24px as base rhythm)
- **Monochromatic hierarchy** with subtle accent colors
- **Frosted glass effects** for layering
- **Typography-driven** interface (less reliance on icons)

---

## 🌈 Color System

### Dark Theme (Primary)

```css
/* Base Neutrals - Soft, never pure black */
--color-background-primary: #0D0D11;      /* Main canvas */
--color-background-secondary: #15151A;    /* Elevated surfaces */
--color-background-tertiary: #1C1C23;     /* Cards, panels */
--color-background-hover: #23232C;        /* Hover states */

/* Text Hierarchy - Muted whites */
--color-text-primary: #E8E8ED;            /* Headlines, key info */
--color-text-secondary: #B4B4C0;          /* Body text */
--color-text-tertiary: #6E6E7A;           /* Subtle labels */
--color-text-disabled: #4A4A52;           /* Disabled states */

/* Accent - Subtle blue-purple gradient */
--color-accent-primary: #5B7CFF;          /* Primary actions */
--color-accent-secondary: #7B5CFF;        /* Secondary accents */
--color-accent-hover: #7090FF;            /* Hover state */
--color-accent-muted: #5B7CFF1A;          /* 10% opacity background */

/* Semantic Colors - Desaturated */
--color-success: #4ADE80;                 /* Verification passed */
--color-success-muted: #4ADE8014;         /* Success backgrounds */
--color-warning: #FBBF24;                 /* Pending states */
--color-warning-muted: #FBBF2414;         /* Warning backgrounds */
--color-error: #F87171;                   /* Failed verification */
--color-error-muted: #F8717114;           /* Error backgrounds */

/* Borders & Dividers - Barely there */
--color-border-default: #2A2A32;          /* Standard borders */
--color-border-hover: #3A3A42;            /* Interactive borders */
--color-border-focus: #5B7CFF40;          /* Focus rings */
```

### Light Theme (Secondary)

```css
/* Base Neutrals - Warm, never pure white */
--color-background-primary: #FAFAF9;      /* Main canvas */
--color-background-secondary: #F5F5F3;    /* Elevated surfaces */
--color-background-tertiary: #EEEEEB;     /* Cards, panels */
--color-background-hover: #E5E5E1;        /* Hover states */

/* Text Hierarchy */
--color-text-primary: #18181B;            /* Headlines */
--color-text-secondary: #52525B;          /* Body text */
--color-text-tertiary: #A1A1AA;           /* Subtle labels */
--color-text-disabled: #D4D4D8;           /* Disabled */

/* Accent - Same blue-purple */
--color-accent-primary: #5B7CFF;
--color-accent-secondary: #7B5CFF;
--color-accent-hover: #4A6BEE;
--color-accent-muted: #5B7CFF14;

/* Semantic - Slightly deeper */
--color-success: #16A34A;
--color-success-muted: #16A34A0A;
--color-warning: #D97706;
--color-warning-muted: #D977060A;
--color-error: #DC2626;
--color-error-muted: #DC26260A;

/* Borders */
--color-border-default: #E5E5E1;
--color-border-hover: #D4D4CF;
--color-border-focus: #5B7CFF40;
```

---

## 📐 Typography

### Font Stack

```css
/* Primary: Inter (clean, modern, readable) */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace: JetBrains Mono (for scores, numbers) */
--font-mono: 'JetBrains Mono', 'SF Mono', 'Roboto Mono', monospace;
```

### Type Scale (1.25 ratio - Perfect Fourth)

```css
/* Display - For hero sections only */
--text-5xl: 3.815rem;    /* 61px - Hero titles */
--text-4xl: 3.052rem;    /* 49px - Page titles */

/* Headings */
--text-3xl: 2.441rem;    /* 39px - Section headers */
--text-2xl: 1.953rem;    /* 31px - Card titles */
--text-xl: 1.563rem;     /* 25px - Subsection headers */
--text-lg: 1.25rem;      /* 20px - Large body */

/* Body */
--text-base: 1rem;       /* 16px - Standard body */
--text-sm: 0.8rem;       /* 13px - Small text */
--text-xs: 0.64rem;      /* 10px - Captions */
```

### Font Weights

```css
--font-weight-normal: 400;    /* Body text */
--font-weight-medium: 500;    /* Slightly emphasized */
--font-weight-semibold: 600;  /* Headings */
--font-weight-bold: 700;      /* Strong emphasis (rare) */
```

### Line Heights

```css
--leading-tight: 1.25;     /* Headings */
--leading-snug: 1.375;     /* Subheadings */
--leading-normal: 1.5;     /* Body text */
--leading-relaxed: 1.75;   /* Long-form content */
```

### Letter Spacing

```css
--tracking-tighter: -0.02em;  /* Large headings */
--tracking-tight: -0.01em;    /* Headings */
--tracking-normal: 0;         /* Body */
--tracking-wide: 0.02em;      /* All-caps labels */
```

---

## 📏 Spacing System

### Scale (Base 4px - Powers of 2)

```css
--space-1: 0.25rem;   /* 4px - Micro spacing */
--space-2: 0.5rem;    /* 8px - Tiny gaps */
--space-3: 0.75rem;   /* 12px - Small gaps */
--space-4: 1rem;      /* 16px - Default gap */
--space-6: 1.5rem;    /* 24px - Base rhythm */
--space-8: 2rem;      /* 32px - Section gaps */
--space-12: 3rem;     /* 48px - Large sections */
--space-16: 4rem;     /* 64px - Major sections */
--space-24: 6rem;     /* 96px - Page sections */
--space-32: 8rem;     /* 128px - Hero spacing */
```

### Layout Grid

```css
/* Container Max Widths */
--container-sm: 640px;   /* Forms, modals */
--container-md: 768px;   /* Single column content */
--container-lg: 1024px;  /* Standard pages */
--container-xl: 1280px;  /* Wide dashboards */
--container-2xl: 1536px; /* Max width */

/* Content Widths */
--prose-width: 65ch;     /* Optimal reading width */
```

---

## 🔲 Components

### Buttons

**Primary Button**
```css
/* Default State */
background: linear-gradient(135deg, var(--color-accent-primary), var(--color-accent-secondary));
color: #FFFFFF;
padding: 12px 24px;
border-radius: 8px;
font-weight: 600;
font-size: 0.875rem;
letter-spacing: 0.02em;
transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);

/* Hover State */
transform: translateY(-1px);
box-shadow: 0 8px 24px -8px rgba(91, 124, 255, 0.4);

/* Active State */
transform: translateY(0);
box-shadow: 0 2px 8px -4px rgba(91, 124, 255, 0.3);

/* Disabled State */
opacity: 0.4;
cursor: not-allowed;
```

**Secondary Button**
```css
background: var(--color-background-tertiary);
color: var(--color-text-primary);
border: 1px solid var(--color-border-default);
padding: 12px 24px;
border-radius: 8px;
font-weight: 500;
transition: all 150ms;

/* Hover */
background: var(--color-background-hover);
border-color: var(--color-border-hover);
```

**Ghost Button**
```css
background: transparent;
color: var(--color-text-secondary);
padding: 12px 24px;
border-radius: 8px;
font-weight: 500;

/* Hover */
background: var(--color-background-hover);
color: var(--color-text-primary);
```

### Cards

**Standard Card**
```css
background: var(--color-background-tertiary);
border: 1px solid var(--color-border-default);
border-radius: 12px;
padding: 24px;
transition: all 200ms ease;

/* Hover (if interactive) */
border-color: var(--color-border-hover);
transform: translateY(-2px);
box-shadow: 0 12px 32px -12px rgba(0, 0, 0, 0.2);
```

**Glass Card** (for overlays)
```css
background: rgba(28, 28, 35, 0.7);
backdrop-filter: blur(24px);
border: 1px solid rgba(255, 255, 255, 0.08);
border-radius: 16px;
padding: 32px;
```

### Inputs

**Text Input**
```css
background: var(--color-background-secondary);
border: 1px solid var(--color-border-default);
border-radius: 8px;
padding: 12px 16px;
font-size: 0.875rem;
color: var(--color-text-primary);
transition: all 150ms;

/* Focus */
border-color: var(--color-accent-primary);
box-shadow: 0 0 0 3px var(--color-border-focus);
outline: none;

/* Placeholder */
color: var(--color-text-tertiary);
```

**Textarea**
```css
/* Same as text input, but: */
min-height: 120px;
resize: vertical;
line-height: 1.5;
```

### Badges

**Status Badge**
```css
/* Success */
background: var(--color-success-muted);
color: var(--color-success);
border: 1px solid rgba(74, 222, 128, 0.2);
padding: 4px 12px;
border-radius: 6px;
font-size: 0.75rem;
font-weight: 600;
text-transform: uppercase;
letter-spacing: 0.05em;

/* Warning */
background: var(--color-warning-muted);
color: var(--color-warning);
border: 1px solid rgba(251, 191, 36, 0.2);

/* Error */
background: var(--color-error-muted);
color: var(--color-error);
border: 1px solid rgba(248, 113, 113, 0.2);
```

### Score Display

**Verification Score Card**
```css
background: var(--color-background-secondary);
border: 2px solid var(--color-border-default);
border-radius: 12px;
padding: 24px;
display: flex;
flex-direction: column;
align-items: center;
gap: 12px;

/* Score Number */
.score-value {
  font-family: var(--font-mono);
  font-size: 3rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--color-accent-primary), var(--color-accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

/* Score Label */
.score-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
}
```

### Navigation

**Top Navigation Bar**
```css
background: rgba(13, 13, 17, 0.8);
backdrop-filter: blur(24px);
border-bottom: 1px solid var(--color-border-default);
padding: 16px 24px;
position: sticky;
top: 0;
z-index: 50;
```

**Navigation Links**
```css
color: var(--color-text-secondary);
font-size: 0.875rem;
font-weight: 500;
padding: 8px 16px;
border-radius: 6px;
transition: all 150ms;

/* Hover */
color: var(--color-text-primary);
background: var(--color-background-hover);

/* Active */
color: var(--color-accent-primary);
background: var(--color-accent-muted);
```

---

## 🎭 Effects & Shadows

### Shadows

```css
/* Subtle elevation */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Standard cards */
--shadow-md: 0 4px 12px -2px rgba(0, 0, 0, 0.1);

/* Elevated elements */
--shadow-lg: 0 12px 32px -8px rgba(0, 0, 0, 0.2);

/* Modals, dropdowns */
--shadow-xl: 0 24px 64px -16px rgba(0, 0, 0, 0.3);

/* Focus rings (colored) */
--shadow-focus: 0 0 0 3px var(--color-border-focus);
```

### Border Radius

```css
--radius-sm: 6px;    /* Small elements, badges */
--radius-md: 8px;    /* Buttons, inputs */
--radius-lg: 12px;   /* Cards */
--radius-xl: 16px;   /* Large panels */
--radius-2xl: 24px;  /* Hero sections */
--radius-full: 9999px; /* Pills, avatars */
```

### Transitions

```css
/* Default - most interactions */
--transition-default: all 150ms cubic-bezier(0.4, 0, 0.2, 1);

/* Slow - cards, major state changes */
--transition-slow: all 250ms cubic-bezier(0.4, 0, 0.2, 1);

/* Fast - micro-interactions */
--transition-fast: all 100ms cubic-bezier(0.4, 0, 0.2, 1);
```

### Backdrop Blur

```css
--blur-sm: blur(8px);    /* Subtle */
--blur-md: blur(16px);   /* Standard glass */
--blur-lg: blur(24px);   /* Heavy glass */
```

---

## 🎬 Animation Guidelines

### Micro-interactions

**Button Press**
```css
@keyframes button-press {
  0% { transform: translateY(0); }
  50% { transform: translateY(2px); }
  100% { transform: translateY(0); }
}
```

**Fade In (for modals, toasts)**
```css
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Usage */
animation: fade-in 200ms cubic-bezier(0.4, 0, 0.2, 1);
```

**Shimmer (for loading states)**
```css
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-background-secondary) 0%,
    var(--color-background-tertiary) 50%,
    var(--color-background-secondary) 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite linear;
}
```

### Page Transitions

**Keep it minimal**: Prefer opacity fades over slides
```css
/* Page enter */
.page-enter {
  opacity: 0;
}

.page-enter-active {
  opacity: 1;
  transition: opacity 300ms ease-in-out;
}
```

---

## 🔧 Tailwind Configuration

### tailwind.config.js

```javascript
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          primary: '#0D0D11',
          secondary: '#15151A',
          tertiary: '#1C1C23',
          hover: '#23232C',
        },
        text: {
          primary: '#E8E8ED',
          secondary: '#B4B4C0',
          tertiary: '#6E6E7A',
          disabled: '#4A4A52',
        },
        accent: {
          primary: '#5B7CFF',
          secondary: '#7B5CFF',
          hover: '#7090FF',
          muted: 'rgba(91, 124, 255, 0.1)',
        },
        success: {
          DEFAULT: '#4ADE80',
          muted: 'rgba(74, 222, 128, 0.08)',
        },
        warning: {
          DEFAULT: '#FBBF24',
          muted: 'rgba(251, 191, 36, 0.08)',
        },
        error: {
          DEFAULT: '#F87171',
          muted: 'rgba(248, 113, 113, 0.08)',
        },
        border: {
          DEFAULT: '#2A2A32',
          hover: '#3A3A42',
          focus: 'rgba(91, 124, 255, 0.25)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        xs: ['0.64rem', { lineHeight: '1.25' }],
        sm: ['0.8rem', { lineHeight: '1.375' }],
        base: ['1rem', { lineHeight: '1.5' }],
        lg: ['1.25rem', { lineHeight: '1.5' }],
        xl: ['1.563rem', { lineHeight: '1.375' }],
        '2xl': ['1.953rem', { lineHeight: '1.25' }],
        '3xl': ['2.441rem', { lineHeight: '1.25' }],
        '4xl': ['3.052rem', { lineHeight: '1.25' }],
        '5xl': ['3.815rem', { lineHeight: '1.25' }],
      },
      spacing: {
        18: '4.5rem',
        88: '22rem',
        128: '32rem',
      },
      borderRadius: {
        DEFAULT: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '24px',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        DEFAULT: '0 4px 12px -2px rgba(0, 0, 0, 0.1)',
        lg: '0 12px 32px -8px rgba(0, 0, 0, 0.2)',
        xl: '0 24px 64px -16px rgba(0, 0, 0, 0.3)',
        focus: '0 0 0 3px rgba(91, 124, 255, 0.25)',
        'accent-glow': '0 8px 24px -8px rgba(91, 124, 255, 0.4)',
      },
      backdropBlur: {
        xs: '8px',
        sm: '16px',
        DEFAULT: '24px',
      },
      transitionDuration: {
        DEFAULT: '150ms',
      },
      transitionTimingFunction: {
        DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile-first approach */
--breakpoint-sm: 640px;   /* Small tablets */
--breakpoint-md: 768px;   /* Tablets */
--breakpoint-lg: 1024px;  /* Laptops */
--breakpoint-xl: 1280px;  /* Desktops */
--breakpoint-2xl: 1536px; /* Large screens */
```

### Mobile Considerations

- **Touch targets**: Minimum 44x44px (11x11 spacing units)
- **Font size**: Never below 16px to prevent zoom on iOS
- **Spacing**: More generous on mobile (increase padding by 1.25x)
- **Navigation**: Bottom nav bar on mobile, top nav on desktop

---

## 🎯 Component Patterns

### Dashboard Cards

```tsx
<div className="bg-background-tertiary border border-border-default rounded-lg p-6 hover:border-border-hover transition-all hover:-translate-y-0.5 hover:shadow-lg">
  <div className="flex items-start justify-between mb-4">
    <h3 className="text-xl font-semibold text-text-primary">Campaign Title</h3>
    <span className="px-3 py-1 text-xs font-semibold uppercase tracking-wide bg-success-muted text-success border border-success/20 rounded-md">
      Active
    </span>
  </div>

  <p className="text-sm text-text-secondary leading-relaxed mb-6">
    Campaign description with generous line height for readability.
  </p>

  <div className="grid grid-cols-3 gap-4 mb-6">
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-1">Responses</p>
      <p className="text-2xl font-mono font-semibold text-text-primary">12 / 50</p>
    </div>
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-1">Bounty</p>
      <p className="text-2xl font-mono font-semibold text-text-primary">$25</p>
    </div>
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-1">Avg Score</p>
      <p className="text-2xl font-mono font-semibold text-accent-primary">87%</p>
    </div>
  </div>

  <button className="w-full bg-gradient-to-br from-accent-primary to-accent-secondary text-white py-3 rounded-lg font-semibold text-sm tracking-wide hover:-translate-y-0.5 hover:shadow-accent-glow transition-all">
    View Details
  </button>
</div>
```

### Verification Score Display

```tsx
<div className="bg-background-secondary border-2 border-border-default rounded-xl p-8 text-center">
  <div className="mb-4">
    <div className="text-6xl font-mono font-semibold bg-gradient-to-br from-accent-primary to-accent-secondary bg-clip-text text-transparent tracking-tighter">
      87%
    </div>
  </div>

  <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary mb-6">
    Combined Score
  </p>

  <div className="grid grid-cols-2 gap-3">
    <div className="bg-background-tertiary rounded-lg p-3">
      <p className="text-sm text-text-tertiary mb-1">Relevance</p>
      <p className="text-lg font-mono font-semibold text-text-primary">92%</p>
    </div>
    <div className="bg-background-tertiary rounded-lg p-3">
      <p className="text-sm text-text-tertiary mb-1">Novelty</p>
      <p className="text-lg font-mono font-semibold text-text-primary">85%</p>
    </div>
    <div className="bg-background-tertiary rounded-lg p-3">
      <p className="text-sm text-text-tertiary mb-1">Coherence</p>
      <p className="text-lg font-mono font-semibold text-text-primary">88%</p>
    </div>
    <div className="bg-background-tertiary rounded-lg p-3">
      <p className="text-sm text-text-tertiary mb-1">Effort</p>
      <p className="text-lg font-mono font-semibold text-text-primary">83%</p>
    </div>
  </div>
</div>
```

### Empty States

```tsx
<div className="flex flex-col items-center justify-center py-24 px-6 text-center">
  <div className="w-16 h-16 mb-6 rounded-full bg-background-tertiary border border-border-default flex items-center justify-center">
    <svg className="w-8 h-8 text-text-tertiary" /* icon SVG */ />
  </div>

  <h3 className="text-xl font-semibold text-text-primary mb-2">
    No campaigns yet
  </h3>

  <p className="text-sm text-text-secondary max-w-sm mb-8 leading-relaxed">
    Create your first campaign to start collecting verified human responses.
  </p>

  <button className="px-6 py-3 bg-gradient-to-br from-accent-primary to-accent-secondary text-white rounded-lg font-semibold text-sm hover:-translate-y-0.5 hover:shadow-accent-glow transition-all">
    Create Campaign
  </button>
</div>
```

---

## ✅ Implementation Checklist

### Phase 1: Foundation
- [ ] Install Inter and JetBrains Mono fonts
- [ ] Update Tailwind config with new color system
- [ ] Create CSS custom properties file
- [ ] Replace all hard-coded colors with design tokens
- [ ] Update theme switcher (default to dark mode)

### Phase 2: Typography
- [ ] Apply new font stack globally
- [ ] Update heading styles with proper weights
- [ ] Fix line heights for readability
- [ ] Add letter spacing to uppercase labels
- [ ] Ensure 16px minimum on mobile

### Phase 3: Components
- [ ] Redesign buttons with new styles
- [ ] Update card components with glass effects
- [ ] Restyle form inputs with focus states
- [ ] Create new badge variants
- [ ] Update navigation bar with backdrop blur

### Phase 4: Layouts
- [ ] Add consistent spacing using new scale
- [ ] Implement responsive breakpoint strategy
- [ ] Update dashboard grid layouts
- [ ] Ensure proper mobile touch targets
- [ ] Add page transition animations

### Phase 5: Polish
- [ ] Add micro-interactions to buttons
- [ ] Implement skeleton loading states
- [ ] Add hover effects to interactive elements
- [ ] Test all focus states for accessibility
- [ ] Optimize animation performance

---

## 🎨 Design Inspiration Examples

### Landing Page Hero
```
Background: Gradient from background-primary to background-secondary
Heading: text-5xl, font-bold, gradient text
Subheading: text-lg, text-secondary, max-w-2xl
CTA: Primary button with accent gradient
Floating cards: Glass effect with backdrop-blur-lg
```

### Dashboard Overview
```
Layout: Grid with auto-fit columns
Cards: Tertiary background, hover lift effect
Stats: Monospace font for numbers
Charts: Muted colors, thin lines
Navigation: Sticky top bar with blur
```

### Verification Results
```
Center layout: Single column, max-w-2xl
Score display: Large monospace, gradient text
Breakdown: Grid of smaller score cards
Feedback: Text-secondary, leading-relaxed
Actions: Ghost buttons for secondary actions
```

---

## 🔍 Accessibility

- **Color contrast**: All text meets WCAG AA standards (4.5:1 minimum)
- **Focus indicators**: 3px solid rings with 25% opacity accent color
- **Keyboard navigation**: Tab order follows visual hierarchy
- **Screen readers**: Semantic HTML with proper ARIA labels
- **Motion**: Respect `prefers-reduced-motion` for animations

---

## 📚 Resources

**Fonts**:
- Inter: https://rsms.me/inter/
- JetBrains Mono: https://www.jetbrains.com/lp/mono/

**Tools**:
- Color contrast checker: https://webaim.org/resources/contrastchecker/
- Type scale generator: https://type-scale.com/
- Spacing calculator: https://hihayk.github.io/shaper/

**Inspiration** (for visual feel only, not copying):
- Uniswap: https://app.uniswap.org/
- Linear: https://linear.app/
- Vercel: https://vercel.com/

---

**Last Updated**: December 2025
**Version**: 1.0.0
**Maintained by**: Proof of Consideration Team
