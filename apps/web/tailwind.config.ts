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
          primary: '#0A0A0F',
          secondary: '#12121A',
          tertiary: '#1A1A27',
          hover: '#222233',
        },
        text: {
          primary: '#F0F0F5',
          secondary: '#B8B8C8',
          tertiary: '#7A7A8A',
          disabled: '#4A4A5A',
        },
        accent: {
          primary: '#6366F1',
          secondary: '#8B5CF6',
          cyan: '#06B6D4',
          pink: '#EC4899',
          hover: '#818CF8',
          muted: 'rgba(99, 102, 241, 0.1)',
        },
        success: {
          DEFAULT: '#10B981',
          light: '#34D399',
          muted: 'rgba(16, 185, 129, 0.1)',
        },
        warning: {
          DEFAULT: '#F59E0B',
          light: '#FBBF24',
          muted: 'rgba(245, 158, 11, 0.1)',
        },
        error: {
          DEFAULT: '#EF4444',
          light: '#F87171',
          muted: 'rgba(239, 68, 68, 0.1)',
        },
        border: {
          DEFAULT: '#2A2A3A',
          hover: '#3A3A4A',
          focus: 'rgba(99, 102, 241, 0.3)',
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
        focus: '0 0 0 3px rgba(99, 102, 241, 0.25)',
        'accent-glow': '0 8px 32px -8px rgba(99, 102, 241, 0.5)',
        'cyan-glow': '0 8px 32px -8px rgba(6, 182, 212, 0.5)',
        'pink-glow': '0 8px 32px -8px rgba(236, 72, 153, 0.5)',
        'purple-glow': '0 8px 32px -8px rgba(139, 92, 246, 0.5)',
      },
      backdropBlur: {
        xs: '8px',
        sm: '16px',
        md: '24px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'web3-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'cyber-gradient': 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'fade-up': 'fadeUp 0.5s ease-out',
        'fade-down': 'fadeDown 0.5s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)' },
          '100%': { boxShadow: '0 0 40px rgba(99, 102, 241, 0.8)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
      transitionDuration: {
        DEFAULT: '200ms',
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
