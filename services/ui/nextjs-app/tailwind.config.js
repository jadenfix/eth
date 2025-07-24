/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Palantir Blueprint Colors
        palantir: {
          navy: '#0F1B2D',
          teal: '#14C8FF',
          'navy-light': '#1A2332',
          'navy-dark': '#0A1018',
        },
        // ChatGPT Colors  
        chatgpt: {
          'stone-light': '#F7F7F8',
          'graphite-dark': '#2D2E33',
          'success-green': '#10A37F',
        },
        // Apple HIG Semantic Colors
        apple: {
          'blue': '#007AFF',
          'green': '#34C759', 
          'orange': '#FF9500',
          'red': '#FF3B30',
          'purple': '#AF52DE',
          'pink': '#FF2D92',
          'yellow': '#FFCC00',
        },
        // Enhanced Theme Colors
        primary: {
          50: '#E6F7FF',
          100: '#BAE7FF', 
          200: '#91D5FF',
          300: '#69C0FF',
          400: '#40A9FF',
          500: '#14C8FF', // Palantir teal
          600: '#1890FF',
          700: '#096DD9',
          800: '#0050B3',
          900: '#003A8C',
        },
        background: {
          light: '#FFFFFF',
          dark: '#0F1B2D', // Palantir navy
          'card-light': '#F8FAFC',
          'card-dark': '#1A2332',
        },
        surface: {
          light: '#F1F5F9',
          dark: '#1E293B',
          'hover-light': '#E2E8F0',
          'hover-dark': '#334155',
        }
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'Cascadia Code', 'monospace'],
      },
      fontSize: {
        'xs': ['12px', { lineHeight: '16px' }],
        'sm': ['14px', { lineHeight: '20px' }],
        'base': ['16px', { lineHeight: '24px' }],
        'lg': ['18px', { lineHeight: '28px' }],
        'xl': ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
        '3xl': ['30px', { lineHeight: '36px' }],
        '4xl': ['36px', { lineHeight: '40px' }],
        '5xl': ['48px', { lineHeight: '1' }],
        '6xl': ['60px', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #14C8FF' },
          '100%': { boxShadow: '0 0 20px #14C8FF, 0 0 30px #14C8FF' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
