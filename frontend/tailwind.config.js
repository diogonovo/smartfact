import daisyui from "daisyui";

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0ea5e9",
        secondary: "#7c3aed",
        accent: "#f59e0b",
        neutral: "#3d4451",
        "base-100": "#ffffff",
        "base-200": "#f3f4f6",
        "base-300": "#d1d5db",
        info: "#3abff8",
        success: "#36d399",
        warning: "#fbbd23",
        error: "#f87272",
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: ["light", "dark"],
  },
}
