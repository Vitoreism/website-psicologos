/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "sage": {
            50: "#f4f7f4",
            100: "#e6ede6",
            200: "#d1ded1",
            600: "#5a7a5a",
            700: "#4a634a",
        },
        "terracotta": {
            50: "#fdf8f6",
            100: "#f9efeb",
            200: "#f4ded4",
            500: "#d68c6e",
        },
        "cream": "#fcfaf7",
        "deep-moss": "#2c3e2c"
      },
      fontFamily: {
        "serif": ["Fraunces", "serif"],
        "sans": ["Plus Jakarta Sans", "sans-serif"]
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-15px)' },
        }
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ],
}
