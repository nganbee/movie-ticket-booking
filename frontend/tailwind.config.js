/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./views/**/*.ejs",
    "./views/**/**/*.ejs",
    "./src/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        brand: '#DC2626', // Tailwind red-600
        brandHover: '#B91C1C', // Tailwind red-700
        bgLight: '#FFFFFF',
        bgSubtle: '#F8FAFC', // slate-50
        textMain: '#1E293B', // slate-800
        textMuted: '#64748B', // slate-500
        borderSubtle: '#E2E8F0', // slate-200
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
