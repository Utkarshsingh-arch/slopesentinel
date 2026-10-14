/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        command: {
          bg: '#0A0F1D',
          panel: '#0F172A',
          card: '#1E293B',
          border: '#334155',
          muted: '#64748B',
          accent: '#06B6D4',
          alert: '#EF4444',
          warning: '#F59E0B',
          success: '#10B981',
        }
      }
    },
  },
  plugins: [],
}
