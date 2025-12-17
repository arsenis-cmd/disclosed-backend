# Design System Migration Guide
## Transforming Your UI to the New Aesthetic

This guide provides a step-by-step approach to migrating your existing Proof of Consideration platform to the new design system.

---

## 🎯 Migration Strategy

### Recommended Approach: **Gradual Component-by-Component**

Rather than a big-bang rewrite, we'll migrate incrementally:

1. **Phase 1**: Foundation (colors, fonts, spacing)
2. **Phase 2**: Core components (buttons, inputs, cards)
3. **Phase 3**: Page layouts (dashboard, campaigns, earnings)
4. **Phase 4**: Polish (animations, micro-interactions)

---

## Phase 1: Foundation (2-3 hours)

### Step 1.1: Install Fonts

```bash
# Update apps/web/app/layout.tsx
```

```tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

// For JetBrains Mono (for numbers/scores)
// Download from https://www.jetbrains.com/lp/mono/
// Or use Google Fonts
import { JetBrains_Mono } from 'next/font/google'

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-jetbrains-mono',
})

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} dark`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

### Step 1.2: Update Tailwind Config

**File**: `apps/web/tailwind.config.ts`

Replace the entire config with:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'monospace'],
      },
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
  ],
}

export default config
```

### Step 1.3: Update Global Styles

**File**: `apps/web/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    @apply border-border;
  }

  body {
    @apply bg-background-primary text-text-primary;
    font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
  }

  /* Ensure dark mode by default */
  :root {
    color-scheme: dark;
  }

  /* Smooth scrolling */
  html {
    scroll-behavior: smooth;
  }

  /* Better focus outlines */
  *:focus-visible {
    @apply outline-none ring-2 ring-border-focus ring-offset-2 ring-offset-background-primary;
  }
}

@layer components {
  /* Utility classes for common patterns */
  .card {
    @apply bg-background-tertiary border border-border rounded-lg p-6;
  }

  .card-hover {
    @apply card hover:border-border-hover hover:-translate-y-0.5 hover:shadow-lg transition-all;
  }

  .glass {
    background: rgba(28, 28, 35, 0.7);
    backdrop-filter: blur(24px);
    @apply border border-white/10;
  }

  .btn-primary {
    @apply bg-gradient-to-br from-accent-primary to-accent-secondary text-white px-6 py-3 rounded-lg font-semibold text-sm tracking-wide hover:-translate-y-0.5 hover:shadow-accent-glow transition-all;
  }

  .btn-secondary {
    @apply bg-background-tertiary text-text-primary border border-border px-6 py-3 rounded-lg font-medium hover:bg-background-hover hover:border-border-hover transition-all;
  }

  .btn-ghost {
    @apply bg-transparent text-text-secondary px-6 py-3 rounded-lg font-medium hover:bg-background-hover hover:text-text-primary transition-all;
  }

  .input {
    @apply bg-background-secondary border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-tertiary focus:border-accent-primary focus:ring-2 focus:ring-border-focus transition-all;
  }

  .badge {
    @apply px-3 py-1 text-xs font-semibold uppercase tracking-wide rounded-md;
  }

  .badge-success {
    @apply badge bg-success-muted text-success border border-success/20;
  }

  .badge-warning {
    @apply badge bg-warning-muted text-warning border border-warning/20;
  }

  .badge-error {
    @apply badge bg-error-muted text-error border border-error/20;
  }
}
```

---

## Phase 2: Core Components (4-6 hours)

### Step 2.1: Create Reusable Button Component

**File**: `apps/web/components/ui/Button.tsx` (NEW)

```tsx
import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-lg font-semibold transition-all disabled:opacity-40 disabled:cursor-not-allowed'

    const variants = {
      primary: 'bg-gradient-to-br from-accent-primary to-accent-secondary text-white hover:-translate-y-0.5 hover:shadow-accent-glow',
      secondary: 'bg-background-tertiary text-text-primary border border-border hover:bg-background-hover hover:border-border-hover',
      ghost: 'bg-transparent text-text-secondary hover:bg-background-hover hover:text-text-primary',
    }

    const sizes = {
      sm: 'px-4 py-2 text-xs',
      md: 'px-6 py-3 text-sm tracking-wide',
      lg: 'px-8 py-4 text-base',
    }

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button }
```

**Utility file**: `apps/web/lib/utils.ts`

```typescript
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

Install dependencies:
```bash
cd apps/web
npm install clsx tailwind-merge
```

### Step 2.2: Create Card Component

**File**: `apps/web/components/ui/Card.tsx` (NEW)

```tsx
import { HTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass'
  hoverable?: boolean
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', hoverable = false, children, ...props }, ref) => {
    const baseStyles = 'rounded-lg'

    const variants = {
      default: 'bg-background-tertiary border border-border',
      glass: 'glass',
    }

    const hoverStyles = hoverable
      ? 'hover:border-border-hover hover:-translate-y-0.5 hover:shadow-lg transition-all cursor-pointer'
      : 'transition-all'

    return (
      <div
        ref={ref}
        className={cn(baseStyles, variants[variant], hoverStyles, className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pb-4', className)} {...props} />
  )
)
CardHeader.displayName = 'CardHeader'

const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn('text-xl font-semibold text-text-primary', className)} {...props} />
  )
)
CardTitle.displayName = 'CardTitle'

const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
  )
)
CardContent.displayName = 'CardContent'

export { Card, CardHeader, CardTitle, CardContent }
```

### Step 2.3: Create Badge Component

**File**: `apps/web/components/ui/Badge.tsx` (NEW)

```tsx
import { HTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'neutral'
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'neutral', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center px-3 py-1 text-xs font-semibold uppercase tracking-wide rounded-md'

    const variants = {
      success: 'bg-success-muted text-success border border-success/20',
      warning: 'bg-warning-muted text-warning border border-warning/20',
      error: 'bg-error-muted text-error border border-error/20',
      neutral: 'bg-background-hover text-text-secondary border border-border',
    }

    return (
      <span
        ref={ref}
        className={cn(baseStyles, variants[variant], className)}
        {...props}
      >
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'

export { Badge }
```

### Step 2.4: Create Input Component

**File**: `apps/web/components/ui/Input.tsx` (NEW)

```tsx
import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/utils'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string
  label?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, label, type = 'text', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        <input
          type={type}
          ref={ref}
          className={cn(
            'w-full bg-background-secondary border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-tertiary focus:border-accent-primary focus:ring-2 focus:ring-border-focus transition-all',
            error && 'border-error focus:border-error focus:ring-error/25',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-2 text-xs text-error">{error}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

const Textarea = forwardRef<HTMLTextAreaElement, InputHTMLAttributes<HTMLTextAreaElement> & { error?: string; label?: string }>(
  ({ className, error, label, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={cn(
            'w-full bg-background-secondary border border-border rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-tertiary focus:border-accent-primary focus:ring-2 focus:ring-border-focus transition-all min-h-[120px] resize-vertical',
            error && 'border-error focus:border-error focus:ring-error/25',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-2 text-xs text-error">{error}</p>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

export { Input, Textarea }
```

---

## Phase 3: Page Migrations (6-8 hours)

### Step 3.1: Update Considerer Dashboard

**File**: `apps/web/app/(considerer)/dashboard/page.tsx`

**Before** (example):
```tsx
<div className="bg-white p-4 rounded shadow">
  <h2 className="text-lg font-bold">Available Tasks</h2>
  {/* ... */}
</div>
```

**After**:
```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export default function ConsidererDashboard() {
  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-text-primary mb-3">
            Available Tasks
          </h1>
          <p className="text-lg text-text-secondary">
            Choose tasks that match your interests and expertise
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Card className="p-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-2">
              Total Earned
            </p>
            <p className="text-3xl font-mono font-semibold text-text-primary">
              $247.50
            </p>
            <p className="text-sm text-success mt-2">
              ↑ 12% from last week
            </p>
          </Card>

          <Card className="p-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-2">
              Tasks Completed
            </p>
            <p className="text-3xl font-mono font-semibold text-text-primary">
              18
            </p>
          </Card>

          <Card className="p-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-2">
              Avg Score
            </p>
            <p className="text-3xl font-mono font-semibold text-accent-primary">
              87%
            </p>
          </Card>
        </div>

        {/* Task Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {tasks.map((task) => (
            <Card key={task.id} hoverable className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-semibold text-text-primary pr-4">
                  {task.title}
                </h3>
                <Badge variant="success">${task.bounty}</Badge>
              </div>

              <p className="text-sm text-text-secondary leading-relaxed mb-6">
                {task.description}
              </p>

              <div className="flex items-center justify-between">
                <span className="text-xs text-text-tertiary">
                  {task.responses_count} / {task.target_responses} responses
                </span>
                <Button variant="primary" size="sm">
                  Accept Task
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
```

### Step 3.2: Update Earnings Page

**File**: `apps/web/app/(considerer)/earnings/page.tsx`

Key changes:
1. Replace all color classes with design system tokens
2. Use new Card components
3. Update button styles
4. Add monospace font to all monetary values
5. Improve spacing with new scale

```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export default function EarningsPage() {
  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Stripe Connect Banner */}
        {!stripeConnected && (
          <Card className="bg-warning-muted border-warning/20 p-6 mb-8">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Connect your payout account
                </h3>
                <p className="text-sm text-text-secondary mb-4">
                  Link your Stripe account to receive payments instantly after verification
                </p>
                <Button variant="primary" size="sm">
                  Connect with Stripe
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Balance Overview */}
        <div className="grid grid-cols-3 gap-6 mb-12">
          <Card className="p-6 text-center">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-2">
              Total Earned
            </p>
            <p className="text-4xl font-mono font-semibold text-text-primary">
              ${balance.total.toFixed(2)}
            </p>
          </Card>

          <Card className="p-6 text-center">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-2">
              Pending
            </p>
            <p className="text-4xl font-mono font-semibold text-warning">
              ${balance.pending.toFixed(2)}
            </p>
          </Card>

          <Card className="p-6 text-center">
            <p className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-2">
              Paid Out
            </p>
            <p className="text-4xl font-mono font-semibold text-success">
              ${balance.available.toFixed(2)}
            </p>
          </Card>
        </div>

        {/* Payment History */}
        <Card>
          <CardHeader>
            <CardTitle>Payment History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {payments.map((payment) => (
                <div
                  key={payment.id}
                  className="flex items-center justify-between py-4 border-b border-border last:border-0"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-text-primary mb-1">
                      {payment.task_title}
                    </p>
                    <p className="text-xs text-text-tertiary">
                      {new Date(payment.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <Badge variant={payment.status === 'COMPLETED' ? 'success' : 'warning'}>
                      {payment.status}
                    </Badge>
                    <p className="text-lg font-mono font-semibold text-text-primary min-w-[100px] text-right">
                      ${payment.net_amount.toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
```

### Step 3.3: Update Campaign Creation Page

**File**: `apps/web/app/(buyer)/campaigns/new/page.tsx`

Key updates:
1. Use new Input and Textarea components
2. Update form layout with better spacing
3. Add proper focus states
4. Use new Button component

```tsx
'use client'

import { useState } from 'react'
import { Input, Textarea } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

export default function NewCampaignPage() {
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-text-primary mb-3">
            Create Campaign
          </h1>
          <p className="text-lg text-text-secondary">
            Set up your campaign to collect verified human responses
          </p>
        </div>

        <Card className="p-8">
          <form className="space-y-6">
            <Input
              label="Campaign Title"
              placeholder="What do you want to learn about?"
              required
            />

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Content to Review
              </label>
              <Textarea
                placeholder="Paste the content you want considerers to review (article, video URL, etc.)"
                required
                className="min-h-[160px]"
              />
              <p className="mt-2 text-xs text-text-tertiary">
                This can be text, a URL, or any content you want feedback on
              </p>
            </div>

            <Textarea
              label="Proof Prompt"
              placeholder="What specific question or task do you want considerers to respond to?"
              required
              className="min-h-[120px]"
            />

            <div className="grid grid-cols-2 gap-6">
              <Input
                label="Bounty per Response"
                type="number"
                placeholder="10.00"
                min="1"
                step="0.01"
                required
              />

              <Input
                label="Target Responses"
                type="number"
                placeholder="50"
                min="1"
                required
              />
            </div>

            {/* Verification Thresholds */}
            <Card className="bg-background-secondary p-6">
              <h3 className="text-sm font-semibold text-text-primary mb-4">
                Verification Thresholds
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Min Relevance"
                  type="number"
                  defaultValue="0.65"
                  min="0"
                  max="1"
                  step="0.05"
                />
                <Input
                  label="Min Novelty"
                  type="number"
                  defaultValue="0.70"
                  min="0"
                  max="1"
                  step="0.05"
                />
                <Input
                  label="Min Coherence"
                  type="number"
                  defaultValue="0.60"
                  min="0"
                  max="1"
                  step="0.05"
                />
                <Input
                  label="Min Combined"
                  type="number"
                  defaultValue="0.60"
                  min="0"
                  max="1"
                  step="0.05"
                />
              </div>
            </Card>

            <div className="flex gap-4 pt-6">
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                className="flex-1"
              >
                Create Campaign
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => window.history.back()}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  )
}
```

---

## Phase 4: Polish & Refinement (2-3 hours)

### Step 4.1: Add Navigation Bar

**File**: `apps/web/components/layout/Navigation.tsx` (NEW)

```tsx
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { UserButton } from '@clerk/nextjs'
import { cn } from '@/lib/utils'

const navItems = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'Campaigns', href: '/campaigns' },
  { label: 'Earnings', href: '/earnings' },
  { label: 'History', href: '/history' },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="sticky top-0 z-50 glass border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-accent-primary to-accent-secondary rounded-lg" />
            <span className="text-lg font-semibold text-text-primary">
              Proof of Consideration
            </span>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center gap-2">
            {navItems.map((item) => {
              const isActive = pathname?.startsWith(item.href)
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                    isActive
                      ? 'bg-accent-muted text-accent-primary'
                      : 'text-text-secondary hover:text-text-primary hover:bg-background-hover'
                  )}
                >
                  {item.label}
                </Link>
              )
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            <UserButton
              appearance={{
                elements: {
                  avatarBox: 'w-8 h-8',
                },
              }}
            />
          </div>
        </div>
      </div>
    </nav>
  )
}
```

### Step 4.2: Add Loading States

**File**: `apps/web/components/ui/Skeleton.tsx` (NEW)

```tsx
import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-lg bg-background-tertiary',
        className
      )}
    />
  )
}

// Preset skeletons
export function SkeletonCard() {
  return (
    <div className="bg-background-tertiary border border-border rounded-lg p-6">
      <Skeleton className="h-6 w-3/4 mb-4" />
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-5/6 mb-6" />
      <div className="flex gap-4">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  )
}
```

### Step 4.3: Add Empty States

**File**: `apps/web/components/ui/EmptyState.tsx` (NEW)

```tsx
import { Button } from './Button'

interface EmptyStateProps {
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
  icon?: React.ReactNode
}

export function EmptyState({ title, description, actionLabel, onAction, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-6 text-center">
      {icon && (
        <div className="w-16 h-16 mb-6 rounded-full bg-background-tertiary border border-border flex items-center justify-center">
          {icon}
        </div>
      )}

      <h3 className="text-xl font-semibold text-text-primary mb-2">
        {title}
      </h3>

      <p className="text-sm text-text-secondary max-w-sm mb-8 leading-relaxed">
        {description}
      </p>

      {actionLabel && onAction && (
        <Button onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
```

---

## Testing Checklist

After migration, test these scenarios:

### Visual Testing
- [ ] All pages render correctly in dark mode
- [ ] Text is readable with sufficient contrast
- [ ] Spacing feels consistent across pages
- [ ] Cards have proper hover effects
- [ ] Buttons show correct states (default, hover, active, disabled)
- [ ] Forms have clear focus indicators
- [ ] Badges display with correct colors

### Responsive Testing
- [ ] Mobile viewport (375px): All content fits, touch targets are 44px+
- [ ] Tablet viewport (768px): Grid layouts adapt correctly
- [ ] Desktop viewport (1280px): Max width containers work
- [ ] Test on real iOS device (font size doesn't cause zoom)
- [ ] Test on real Android device

### Interaction Testing
- [ ] All buttons respond to clicks
- [ ] Form inputs show focus states
- [ ] Hover effects work smoothly
- [ ] Loading states display correctly
- [ ] Animations aren't janky (check 60fps)
- [ ] Keyboard navigation works (tab through forms)

### Accessibility Testing
- [ ] Run Lighthouse accessibility audit (score > 90)
- [ ] Test with screen reader (VoiceOver/NVDA)
- [ ] Check color contrast with WCAG tool
- [ ] Ensure all interactive elements are keyboard accessible
- [ ] Verify focus indicators are visible

---

## Performance Optimization

### After Migration

1. **Optimize Font Loading**:
```tsx
// In layout.tsx, add font-display swap
const inter = Inter({
  subsets: ['latin'],
  display: 'swap', // Prevents flash of unstyled text
  variable: '--font-inter',
})
```

2. **Reduce Bundle Size**:
```bash
# Analyze bundle
npm run build
# Check for unused dependencies
npx depcheck
```

3. **Lazy Load Heavy Components**:
```tsx
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <Skeleton className="h-64 w-full" />,
  ssr: false,
})
```

---

## Troubleshooting

### Issue: Colors not showing up
**Solution**: Make sure you've updated `tailwind.config.ts` and restarted dev server

### Issue: Fonts not loading
**Solution**: Check that fonts are imported in `layout.tsx` and CSS variables are set

### Issue: Hover effects not working
**Solution**: Ensure you're using `transition-all` class and have default transition timing

### Issue: Focus rings not visible
**Solution**: Check that `*:focus-visible` style is in `globals.css`

---

## Timeline Summary

| Phase | Duration | Priority |
|-------|----------|----------|
| Foundation (fonts, colors, spacing) | 2-3 hours | Critical |
| Core Components (buttons, cards, inputs) | 4-6 hours | Critical |
| Page Migrations (dashboard, earnings, campaigns) | 6-8 hours | High |
| Polish & Refinement (nav, loading, empty states) | 2-3 hours | Medium |

**Total Estimated Time**: 14-20 hours

---

## Next Steps

1. Start with Foundation phase (can't proceed without it)
2. Create UI components in isolation (Storybook optional but helpful)
3. Migrate one page at a time (test thoroughly before moving on)
4. Get feedback from users after each major page migration
5. Iterate based on real usage patterns

---

**Questions or Issues?**
Refer to the main `DESIGN_SYSTEM.md` for detailed specs on colors, typography, and spacing.
