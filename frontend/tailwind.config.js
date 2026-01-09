/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Space Grotesk"', 'sans-serif'],
      },
      colors: {
        midnight: '#0f172a',
        ink: '#0b1220',
        teal: '#22d3ee',
        lavender: '#c084fc',
        mint: '#34d399',
      },
      boxShadow: {
        'glow-teal': '0 20px 60px rgba(34, 211, 238, 0.15)',
        'glow-lavender': '0 20px 60px rgba(192, 132, 252, 0.12)',
      },
    },
  },
  plugins: [],
};
