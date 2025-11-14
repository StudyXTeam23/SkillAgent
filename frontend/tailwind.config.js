/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#137fec",
        "background-light": "#f6f7f8",
        "background-dark": "#101922",
        "surface-light": "#ffffff",
        "surface-dark": "#1a2632",
        "text-light-primary": "#0d141b",
        "text-dark-primary": "#f6f7f8",
        "text-light-secondary": "#4c739a",
        "text-dark-secondary": "#a0b3c7",
        "border-light": "#e7edf3",
        "border-dark": "#2a3b4d",
        "success": "#28A745",
        "error": "#DC3545",
      },
      fontFamily: {
        "display": ["Space Grotesk", "sans-serif"],
        "body": ["Lexend", "Noto Sans", "sans-serif"]
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
    },
  },
  plugins: [],
}
