import { InputHTMLAttributes, TextareaHTMLAttributes, forwardRef } from 'react'
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

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string
  label?: string
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
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
