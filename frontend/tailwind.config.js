/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        fin: {
          teal: {
            50: '#f0fdfa',
            100: '#ccfbf1',
            200: '#99f6e4',
            300: '#5eead4',
            400: '#2dd4bf',
            500: '#14b8a6',
            600: '#0d9488',
            700: '#0f766e',
            800: '#115e59',
            900: '#134e4a',
          },
          slate: {
            850: '#1a2332',
            950: '#0b1220',
          },
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        panel: '0 4px 24px -4px rgb(15 23 42 / 0.12)',
        glow: '0 0 40px -8px rgb(20 184 166 / 0.35)',
      },
      backgroundImage: {
        'fin-gradient':
          'linear-gradient(135deg, #0f766e 0%, #134e4a 35%, #1e293b 100%)',
        'fin-card':
          'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(240,253,250,0.9) 100%)',
      },
    },
  },
  plugins: [],
};
