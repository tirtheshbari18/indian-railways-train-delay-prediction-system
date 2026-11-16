/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        railway: {
          dark: '#07162c',
          navy: '#0B2545',
          blue: '#133E87',
          steel: '#1E3E62',
          light: '#60A5FA',
          ice: '#EFF6FF',
          gold: '#F59E0B',
          amber: '#D97706',
          green: '#10B981',
          emerald: '#059669',
          red: '#EF4444',
          crimson: '#DC2626'
        }
      }
    },
  },
  plugins: [],
}
