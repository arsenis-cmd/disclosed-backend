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
